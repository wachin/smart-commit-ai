"""Load and save Smart Commit AI training examples."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from .commit_message import CommitMessage, format_git_commit_command


DEFAULT_ENTRIES_DIR = Path(__file__).resolve().parents[1] / "commit_examples_data" / "entries"


@dataclass(frozen=True)
class ExampleEntry:
    path: Path
    title: str
    original_text: str
    expected_subject: str
    expected_body_lines: list[str]
    expected_command: str

    @property
    def message(self) -> CommitMessage:
        return CommitMessage(subject=self.expected_subject, body_lines=self.expected_body_lines).normalized()


class ExampleStore:
    """Small JSONL-like store, one example per JSON file."""

    def __init__(self, entries_dir: Path | str = DEFAULT_ENTRIES_DIR) -> None:
        self.entries_dir = Path(entries_dir)

    def load(self) -> list[ExampleEntry]:
        entries: list[ExampleEntry] = []
        if not self.entries_dir.exists():
            return entries

        for path in sorted(self.entries_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue

            original_text = str(data.get("original_text", "")).strip()
            expected_subject = str(data.get("expected_subject", "")).strip()
            if not original_text or not expected_subject:
                continue

            body = data.get("expected_body_lines", [])
            if not isinstance(body, list):
                body = []

            entries.append(
                ExampleEntry(
                    path=path,
                    title=str(data.get("title", path.stem)),
                    original_text=original_text,
                    expected_subject=expected_subject,
                    expected_body_lines=[str(line) for line in body],
                    expected_command=str(data.get("expected_command", "")),
                )
            )
        return entries

    def find_similar(self, text: str, limit: int = 4) -> list[ExampleEntry]:
        query_tokens = set(tokenize(text))
        if not query_tokens:
            return []

        scored: list[tuple[float, ExampleEntry]] = []
        for entry in self.load():
            entry_tokens = set(tokenize(entry.original_text + " " + entry.expected_subject))
            if not entry_tokens:
                continue
            overlap = len(query_tokens & entry_tokens)
            if not overlap:
                continue
            score = overlap / ((len(query_tokens) * len(entry_tokens)) ** 0.5)
            scored.append((score, entry))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [entry for _, entry in scored[:limit]]

    def save(
        self,
        original_text: str,
        message: CommitMessage,
        *,
        source: str = "local",
        model: str | None = None,
    ) -> Path:
        self.entries_dir.mkdir(parents=True, exist_ok=True)
        normalized = message.normalized()

        existing = self._find_duplicate(original_text, normalized.subject)
        if existing is not None:
            return existing

        prefix = self._next_numeric_prefix()
        slug = slugify(normalized.subject)
        path = self.entries_dir / f"{prefix}-{slug}.json"
        while path.exists():
            prefix += 1
            path = self.entries_dir / f"{prefix}-{slug}.json"

        payload = {
            "title": title_from_subject(normalized.subject),
            "original_text": original_text.strip(),
            "expected_subject": normalized.subject,
            "expected_body_lines": normalized.body_lines,
            "expected_command": format_git_commit_command(normalized.subject, normalized.body_lines),
            "source": source,
            "model": model,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "content_hash": content_hash(original_text, normalized.subject, normalized.body_lines),
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return path

    def _find_duplicate(self, original_text: str, subject: str) -> Path | None:
        original_normalized = normalize_for_hash(original_text)
        subject_normalized = normalize_for_hash(subject)
        for entry in self.load():
            if (
                normalize_for_hash(entry.original_text) == original_normalized
                and normalize_for_hash(entry.expected_subject) == subject_normalized
            ):
                return entry.path
        return None

    def _next_numeric_prefix(self) -> int:
        max_value = 0
        if self.entries_dir.exists():
            for path in self.entries_dir.glob("*.json"):
                match = re.match(r"^(\d+)", path.stem)
                if match:
                    max_value = max(max_value, int(match.group(1)))
        return max_value + 1


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def slugify(value: str) -> str:
    value = re.sub(r"^[a-z]+\(([^)]+)\):\s*", r"\1 ", value.lower())
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:70].strip("-") or "commit-message"


def title_from_subject(subject: str) -> str:
    match = re.match(r"^([a-z]+)\(([^)]+)\):\s*(.+)$", subject)
    if not match:
        return subject
    commit_type, scope, description = match.groups()
    return f"{commit_type}: {scope} - {description}".title()


def normalize_for_hash(text: str) -> str:
    return " ".join(text.strip().split()).lower()


def content_hash(original_text: str, subject: str, body_lines: list[str]) -> str:
    value = "\n".join([normalize_for_hash(original_text), subject, *body_lines])
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

