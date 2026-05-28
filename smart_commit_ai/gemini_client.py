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
- Return only valid JSON with keys "subject" and "body_lines".
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
    cleaned = re.sub(r"^```(?:json|bash)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        parsed_command = parse_git_commit_command(cleaned)
        if parsed_command is None:
            raise GeminiError("Gemini response was not valid JSON or a git commit command.")
        return parsed_command.normalized()

    subject = str(data.get("subject", "")).strip()
    body = data.get("body_lines", [])
    if not subject or not isinstance(body, list):
        raise GeminiError("Gemini JSON must contain subject and body_lines.")

    return CommitMessage(subject=subject, body_lines=[str(line) for line in body]).normalized()
