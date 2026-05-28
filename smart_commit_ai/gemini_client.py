"""Optional Google Gemini API support."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from urllib import parse
from urllib import error, request

from .commit_message import CommitMessage, parse_git_commit_command
from .config import DEFAULT_GEMINI_MODEL, load_gemini_model
from .examples import ExampleStore
from .local_generator import LocalCommitGenerator


FALLBACK_GEMINI_MODELS = (DEFAULT_GEMINI_MODEL, "gemini-flash-latest", "gemini-2.0-flash", "gemini-3.5-flash")
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GEMINI_MODELS_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_CHECK_PROMPT = "Reply with exactly: OK"
GEMINI_COMMIT_PROMPT = """Act as a Senior Software Engineer and Git Expert. I will provide you with a summary of recent development work, including code changes, bug fixes, feature additions, and test results.

Your task is to generate a single, professional Git commit message that strictly adheres to the Conventional Commits specification and standard Git formatting limits.

Formatting Rules:
1. Header: type(scope): subject
   - Must be 50 characters or fewer.
   - Use lowercase for the type and scope.
   - Common types: feat, fix, docs, style, refactor, test, chore, ci, perf.
2. Body:
   - Each line must be 72 characters or fewer.
   - Use bullet points (-) for clarity.
   - Focus on what changed and why it matters (architecture, UX, stability).
   - Do not include conversational filler, process noise, or "I did this" statements.
   - Highlight key technical details (e.g., specific algorithms, UI components, test counts).
3. Footer: Optional, only if there are breaking changes or specific issue references.

Output Format:
Provide ONLY the raw git commit command in a bash code block, like this:

```bash
git commit -m "type(scope): concise subject line" \\
  -m "- Bullet point 1" \\
  -m "- Bullet point 2" \\
  -m "- Bullet point 3"
```

Do not split one body bullet across multiple -m arguments.
Do not return JSON, explanations, analysis, or alternate options.
Preserve the language of the input summary when writing the body.

Minimum quality requirements:
- Never return a subject-only commit.
- Include 4 to 7 body bullets for normal development summaries.
- Preserve concrete filenames, modules, APIs, settings, and test counts.
- Include a Validation bullet when tests or compile checks are mentioned.
- If the summary is terse, infer a focused commit from its concrete terms.
- Use specific technical verbs; avoid vague subjects like "update changes",
  "restrict saved", "add gui changes", or "improve app".

Commit selection rules:
- Choose the scope from the primary changed module or behavior, not from the
  word "app" or a generic UI mention.
- If smart_commit_ai/service.py is the primary changed file, prefer
  scope "service".
- If gemini_client.py is the primary changed file, prefer scope "gemini".
- If gui.py is the primary changed file, prefer scope "ui".
- If tests are only mentioned as verification or coverage, do not use
  type "test"; keep the type tied to the production behavior.
- Do not let a weak local draft override concrete filenames and behavior in
  the new summary."""


class GeminiError(RuntimeError):
    """Raised when the Gemini API cannot return a valid commit message."""


class GeminiHTTPError(GeminiError):
    """Gemini HTTP error with status code for model fallback decisions."""

    def __init__(self, status_code: int, detail: str, model: str) -> None:
        super().__init__(f"Gemini API error {status_code} for {model}: {detail}")
        self.status_code = status_code
        self.detail = detail
        self.model = model


@dataclass(frozen=True)
class GeminiApiStatus:
    ok: bool
    model: str | None
    available_models: list[str]
    detail: str


class GeminiCommitGenerator:
    """Generate commit messages with Gemini, using local examples as few-shot context."""

    def __init__(self, store: ExampleStore | None = None, model: str | None = None) -> None:
        self.store = store or ExampleStore()
        self.model = model or os.environ.get("SMART_COMMIT_AI_GEMINI_MODEL") or load_gemini_model()
        self.local = LocalCommitGenerator()

    def check_api(self, api_key: str | None = None, *, verify_generation: bool = True) -> GeminiApiStatus:
        api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return GeminiApiStatus(
                ok=False,
                model=None,
                available_models=[],
                detail="Missing Gemini API key.",
            )

        try:
            response_data = self._list_models(api_key)
        except GeminiError as exc:
            return GeminiApiStatus(
                ok=False,
                model=None,
                available_models=[],
                detail=str(exc),
            )

        available_models = extract_generate_content_models(response_data)
        selected_model = select_available_model(self.model, available_models)
        if not selected_model:
            return GeminiApiStatus(
                ok=False,
                model=None,
                available_models=available_models,
                detail=(
                    "Gemini API key is valid, but none of the configured Flash "
                    "models support generateContent for this key."
                ),
            )

        self.model = selected_model
        detail = f"Gemini API is active. Using {selected_model}."
        if verify_generation:
            try:
                smoke_text = self._request_model(GEMINI_CHECK_PROMPT, api_key, selected_model)
            except GeminiError as exc:
                return GeminiApiStatus(
                    ok=False,
                    model=selected_model,
                    available_models=available_models,
                    detail=(
                        "Gemini models.list succeeded, but generateContent failed "
                        f"for {selected_model}: {exc}"
                    ),
                )
            detail = f"{detail} generateContent test returned: {response_excerpt(smoke_text, 80)}"

        return GeminiApiStatus(
            ok=True,
            model=selected_model,
            available_models=available_models,
            detail=detail,
        )

    def generate(self, original_text: str, api_key: str | None = None) -> CommitMessage:
        api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise GeminiError("Missing Gemini API key.")

        local_draft = self.local.generate(original_text)
        prompt = self._build_prompt(original_text, local_draft)
        text = self._request(prompt, api_key)
        try:
            message = parse_model_response(text)
        except GeminiError as exc:
            repair_prompt = self._build_repair_prompt(
                original_text,
                local_draft,
                text,
                ["response was not a raw git commit command"],
            )
            repaired_text = self._request(repair_prompt, api_key)
            try:
                message = parse_model_response(repaired_text)
            except GeminiError as repair_exc:
                raise GeminiError(
                    "Gemini returned an invalid response after repair. "
                    f"First response excerpt: {response_excerpt(text)}. "
                    f"Repair response excerpt: {response_excerpt(repaired_text)}"
                ) from repair_exc
            text = repaired_text

        issues = quality_issues(message, original_text)
        if issues:
            repair_prompt = self._build_repair_prompt(original_text, local_draft, text, issues)
            text = self._request(repair_prompt, api_key)
            message = parse_model_response(text)
            issues = quality_issues(message, original_text)
            if issues:
                raise GeminiError(
                    "Gemini returned a low-quality commit message after repair: "
                    f"{'; '.join(issues)}. Raw response excerpt: {response_excerpt(text)}"
                )

        normalized = message.normalized()
        return CommitMessage(
            subject=normalized.subject,
            body_lines=normalized.body_lines,
            source="gemini",
            model=self.model,
        )

    def _request(self, prompt: str, api_key: str) -> str:
        errors: list[GeminiHTTPError] = []
        for model in request_model_candidates(self.model):
            try:
                text = self._request_model(prompt, api_key, model)
            except GeminiHTTPError as exc:
                errors.append(exc)
                if not http_error_is_model_unavailable(exc):
                    raise
                continue
            self.model = model
            return text

        if errors:
            tried = ", ".join(error.model for error in errors)
            raise GeminiError(
                "Gemini model unavailable for this API key. "
                f"Tried: {tried}. Last error: {errors[-1]}"
            ) from errors[-1]
        raise GeminiError("Gemini request failed before a model was tried.")

    def _request_model(self, prompt: str, api_key: str, model: str) -> str:
        endpoint = GEMINI_ENDPOINT.format(model=model)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 700,
                "temperature": 0.1,
            },
        }
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=45) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GeminiHTTPError(exc.code, detail, model) from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise GeminiError(f"Gemini request failed: {exc}") from exc

        text = extract_response_text(response_data)
        return text

    def _list_models(self, api_key: str) -> dict:
        query = parse.urlencode({"key": api_key, "pageSize": "1000"})
        http_request = request.Request(
            f"{GEMINI_MODELS_ENDPOINT}?{query}",
            headers={"Accept": "application/json"},
            method="GET",
        )

        try:
            with request.urlopen(http_request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GeminiError(f"Gemini API check failed {exc.code}: {detail}") from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise GeminiError(f"Gemini API check failed: {exc}") from exc

    def _build_prompt(self, original_text: str, local_draft: CommitMessage | None = None) -> str:
        examples = self.store.find_similar(original_text, limit=3)
        example_blocks = []
        for entry in examples:
            if quality_issues(entry.message, entry.original_text):
                continue
            expected_command = entry.expected_command or entry.message.command()
            example_blocks.append(
                "\n".join(
                    [
                        "Input:",
                        entry.original_text,
                        "Output:",
                        "```bash",
                        expected_command,
                        "```",
                    ]
                )
            )

        examples_text = "\n\n".join(example_blocks) if example_blocks else "No examples available."
        local_draft_text = local_draft.command() if local_draft else "No local draft available."
        return f"""{GEMINI_COMMIT_PROMPT}

Reference examples. Follow their style and level of detail, but do not copy
their content unless it is present in the new summary:
{examples_text}

Local fallback draft. Use it only as a minimum detail checklist. You must
correct its type, scope, subject, and bullets when the new summary provides
better evidence:
```bash
{local_draft_text}
```

New development summary:
{original_text}
"""

    def _build_repair_prompt(
        self,
        original_text: str,
        local_draft: CommitMessage,
        bad_response: str,
        issues: list[str],
    ) -> str:
        return f"""{GEMINI_COMMIT_PROMPT}

Your previous answer was rejected for these quality problems:
- {'; '.join(issues)}

Previous rejected answer:
{bad_response}

Local quality floor. The replacement must be at least this detailed:
```bash
{local_draft.command()}
```

Rewrite the commit command from this development summary:
{original_text}
"""


def extract_response_text(response_data: dict) -> str:
    try:
        candidates = response_data["candidates"]
        parts = candidates[0]["content"]["parts"]
        text = "\n".join(str(part.get("text", "")) for part in parts).strip()
        if text:
            return text
    except (KeyError, IndexError, TypeError) as exc:
        raise GeminiError(response_text_missing_message(response_data)) from exc

    raise GeminiError(response_text_missing_message(response_data))


def response_text_missing_message(response_data: dict) -> str:
    details: list[str] = []
    prompt_feedback = response_data.get("promptFeedback")
    if isinstance(prompt_feedback, dict) and prompt_feedback.get("blockReason"):
        details.append(f"blockReason={prompt_feedback.get('blockReason')}")

    candidates = response_data.get("candidates")
    if isinstance(candidates, list) and candidates:
        candidate = candidates[0]
        if isinstance(candidate, dict) and candidate.get("finishReason"):
            details.append(f"finishReason={candidate.get('finishReason')}")

    suffix = f" ({', '.join(details)})" if details else ""
    return f"Gemini response did not include text{suffix}."


def request_model_candidates(model: str) -> list[str]:
    candidates = [model, *FALLBACK_GEMINI_MODELS]
    unique: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def extract_generate_content_models(response_data: dict) -> list[str]:
    models = response_data.get("models", [])
    if not isinstance(models, list):
        return []

    available: list[str] = []
    for item in models:
        if not isinstance(item, dict):
            continue
        methods = item.get("supportedGenerationMethods", item.get("supportedActions", []))
        if isinstance(methods, list) and "generateContent" not in methods:
            continue

        for name in model_names_from_item(item):
            if name and name not in available:
                available.append(name)

    return available


def model_names_from_item(item: dict) -> list[str]:
    names: list[str] = []
    for key in ("baseModelId", "name"):
        value = item.get(key)
        if not isinstance(value, str) or not value:
            continue
        if value.startswith("models/"):
            value = value.split("/", 1)[1]
        names.append(value)
    return names


def select_available_model(preferred_model: str, available_models: list[str]) -> str | None:
    available = set(available_models)
    for candidate in request_model_candidates(preferred_model):
        if candidate in available:
            return candidate
    return None


def http_error_is_model_unavailable(exc: GeminiHTTPError) -> bool:
    detail = exc.detail.lower()
    return exc.status_code in {400, 404} and (
        "not found" in detail
        or "not supported" in detail
        or "not available" in detail
        or "not enabled" in detail
    )


def parse_model_response(text: str) -> CommitMessage:
    cleaned = text.strip()
    data = parse_json_from_text(cleaned)
    if isinstance(data, dict):
        message = commit_message_from_mapping(data)
        if message is not None:
            return message.normalized()

    parsed_command = parse_git_commit_command(cleaned)
    if parsed_command is not None:
        return parsed_command.normalized()

    markdown_message = parse_markdown_commit_message(cleaned)
    if markdown_message is not None:
        return markdown_message.normalized()

    raise GeminiError(
        "Gemini response was not valid JSON or a git commit command. "
        f"Raw response excerpt: {response_excerpt(cleaned)}"
    )


def response_excerpt(text: str, limit: int = 240) -> str:
    value = " ".join(text.strip().split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def parse_json_from_text(text: str) -> object | None:
    for candidate in json_candidates(text):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None


def json_candidates(text: str) -> list[str]:
    candidates = [text.strip()]
    for match in re.finditer(r"```(?:json)?\s*(.*?)```", text, flags=re.I | re.S):
        candidates.append(match.group(1).strip())

    balanced = first_balanced_json_object(text)
    if balanced:
        candidates.append(balanced)

    unique: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def first_balanced_json_object(text: str) -> str | None:
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(text[start:], start=start):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def commit_message_from_mapping(data: dict) -> CommitMessage | None:
    command = first_string(data, "command", "expected_command", "git_commit_command")
    if command:
        parsed_command = parse_git_commit_command(command)
        if parsed_command is not None:
            return parsed_command

    subject = first_string(data, "subject", "expected_subject", "header", "title")
    body = data.get("body_lines", data.get("expected_body_lines", data.get("body", [])))
    if isinstance(body, str):
        body_lines = [line.strip() for line in body.splitlines() if line.strip()]
    elif isinstance(body, list):
        body_lines = [str(line) for line in body]
    else:
        body_lines = []

    if not subject:
        return None
    return CommitMessage(subject=subject, body_lines=body_lines)


def quality_issues(message: CommitMessage, original_text: str) -> list[str]:
    normalized = message.normalized()
    issues: list[str] = []

    if len(normalized.body_lines) < 3:
        issues.append("body must include at least 3 bullet lines")

    if subject_is_too_generic(normalized.subject):
        issues.append("subject is too vague or too short")

    weak_lines = [line for line in normalized.body_lines if body_line_is_too_generic(line)]
    if weak_lines:
        issues.append("body contains vague bullet lines")

    if summary_mentions_validation(original_text) and not message_mentions_validation(normalized):
        issues.append("validation/test result from summary is missing")

    return issues


def subject_is_too_generic(subject: str) -> bool:
    match = re.match(r"^[a-z]+(?:\([^)]+\))?:\s*(.+)$", subject.strip())
    if not match:
        return True

    description = match.group(1).strip().lower()
    words = re.findall(r"[a-z0-9_.-]+", description)
    if len(words) < 3:
        return True

    generic_phrases = {
        "update changes",
        "update it",
        "improve app",
        "restrict saved",
        "add support",
        "fix issue",
    }
    return description in generic_phrases


def body_line_is_too_generic(line: str) -> bool:
    value = line.strip().lower()
    if value.startswith("- validation:"):
        return False
    words = re.findall(r"[a-z0-9_.-]+", value)
    if len(words) < 4:
        return True
    generic_lines = {
        "- update it",
        "- update changes",
        "- improve behavior",
        "- fix issue",
        "- add support",
    }
    return value in generic_lines


def summary_mentions_validation(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in [
            "verification",
            "tests ok",
            "tests pass",
            "tests passed",
            "compileall",
            "compile check",
            "git diff --check",
        ]
    )


def message_mentions_validation(message: CommitMessage) -> bool:
    combined = " ".join(message.body_lines).lower()
    return any(marker in combined for marker in ["validation:", "tests pass", "tests ok", "compileall"])


def first_string(data: dict, *keys: str) -> str:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def parse_markdown_commit_message(text: str) -> CommitMessage | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    subject = ""
    body_lines: list[str] = []
    subject_pattern = re.compile(
        r"((?:feat|fix|docs|style|refactor|test|chore|ci|perf)"
        r"(?:\([a-z0-9._-]+\))?:\s+[^\n]+)",
        flags=re.I,
    )

    for index, line in enumerate(lines):
        match = subject_pattern.search(line)
        if not match:
            continue
        subject = match.group(1).strip(" `\"'")
        for body_line in lines[index + 1 :]:
            if body_line.startswith("- "):
                body_lines.append(body_line)
        break

    if not subject:
        return None
    return CommitMessage(subject=subject, body_lines=body_lines)
