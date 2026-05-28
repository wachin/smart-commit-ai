"""Optional Google Gemini API support."""

from __future__ import annotations

import json
import os
import re
from urllib import error, request

from .commit_message import CommitMessage, parse_git_commit_command
from .examples import ExampleStore


DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiError(RuntimeError):
    """Raised when the Gemini API cannot return a valid commit message."""


class GeminiCommitGenerator:
    """Generate commit messages with Gemini, using local examples as few-shot context."""

    def __init__(self, store: ExampleStore | None = None, model: str | None = None) -> None:
        self.store = store or ExampleStore()
        self.model = model or os.environ.get("SMART_COMMIT_AI_GEMINI_MODEL") or DEFAULT_GEMINI_MODEL

    def generate(self, original_text: str, api_key: str | None = None) -> CommitMessage:
        api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise GeminiError("Missing Gemini API key.")

        prompt = self._build_prompt(original_text)
        endpoint = GEMINI_ENDPOINT.format(model=self.model)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "object",
                    "properties": {
                        "subject": {"type": "string"},
                        "body_lines": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["subject", "body_lines"],
                    "propertyOrdering": ["subject", "body_lines"],
                },
                "maxOutputTokens": 700,
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
            raise GeminiError(f"Gemini API error {exc.code}: {detail}") from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise GeminiError(f"Gemini request failed: {exc}") from exc

        text = extract_response_text(response_data)
        message = parse_model_response(text)
        return CommitMessage(
            subject=message.subject,
            body_lines=message.body_lines,
            source="gemini",
            model=self.model,
        ).normalized()

    def _build_prompt(self, original_text: str) -> str:
        examples = self.store.find_similar(original_text, limit=3)
        example_blocks = []
        for entry in examples:
            example_blocks.append(
                "\n".join(
                    [
                        "Input:",
                        entry.original_text,
                        "Output JSON:",
                        json.dumps(
                            {
                                "subject": entry.expected_subject,
                                "body_lines": entry.expected_body_lines,
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
            )

        examples_text = "\n\n".join(example_blocks) if example_blocks else "No examples available."
        return f"""Act as a Senior Software Engineer and Git Expert.

Generate one professional Conventional Commit message from the development
summary.

Rules:
- Return only one valid JSON object with keys "subject" and "body_lines".
- Do not return markdown fences, prose, comments, or a bash command.
- subject must be: type(scope): subject
- subject must be 50 characters or fewer.
- type and scope must be lowercase.
- body_lines must be an array of bullet strings that start with "- ".
- each body line must be 72 characters or fewer.
- focus on what changed and why it matters.
- remove conversational filler and next-step suggestions.
- include validation/test results when present.

Similar examples:
{examples_text}

Development summary:
{original_text}
"""


def extract_response_text(response_data: dict) -> str:
    try:
        candidates = response_data["candidates"]
        parts = candidates[0]["content"]["parts"]
        return "\n".join(str(part.get("text", "")) for part in parts).strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise GeminiError("Gemini response did not include text.") from exc


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

    raise GeminiError("Gemini response was not valid JSON or a git commit command.")


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
