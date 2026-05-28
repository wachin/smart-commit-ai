"""Load local Conventional Commit examples for offline sklearn training."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from utils.regex_utils import regex


SUPPORTED_TYPES = {"feat", "fix", "docs", "refactor", "test", "chore"}
ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class TrainingExample:
    text: str
    label: str
    source: str


@dataclass(frozen=True)
class EntryValidationError:
    path: Path
    message: str


SEED_EXAMPLES = [
    ("added MIDI karaoke support", "feat"),
    ("implemented language detection for Spanish summaries", "feat"),
    ("fixed crash when opening audio files", "fix"),
    ("corrige error al abrir archivos de audio", "fix"),
    ("updated installation instructions", "docs"),
    ("documenta nuevas opciones de instalacion", "docs"),
    ("cleaned deprecated code paths", "refactor"),
    ("refactoriza el parser para separar responsabilidades", "refactor"),
    ("added regression tests for commit prediction", "test"),
    ("añade pruebas para el predictor de commits", "test"),
    ("updated build scripts and dependency notes", "chore"),
    ("actualiza tareas de mantenimiento del repositorio", "chore"),
]


def label_from_subject(subject: str) -> str | None:
    match = regex.match(r"\s*([a-z]+)(?:\(|:)", subject or "")
    if not match:
        return None
    label = match.group(1).lower()
    return label if label in SUPPORTED_TYPES else None


def _entry_to_example(entry: dict, source: str) -> TrainingExample | None:
    label = label_from_subject(entry.get("expected_subject", ""))
    text = (entry.get("original_text") or "").strip()
    if not label or not text:
        return None
    return TrainingExample(text=text, label=label, source=source)


def validate_entry(entry: dict, path: Path) -> list[EntryValidationError]:
    errors: list[EntryValidationError] = []
    required_fields = {
        "title": str,
        "original_text": str,
        "expected_subject": str,
        "expected_body_lines": list,
    }
    for field, expected_type in required_fields.items():
        value = entry.get(field)
        if not isinstance(value, expected_type) or (isinstance(value, str) and not value.strip()):
            errors.append(EntryValidationError(path, f"missing or invalid {field}"))

    label = label_from_subject(entry.get("expected_subject", ""))
    if not label:
        errors.append(EntryValidationError(path, "expected_subject must use a supported Conventional Commit type"))

    body_lines = entry.get("expected_body_lines", [])
    if isinstance(body_lines, list):
        for index, line in enumerate(body_lines, start=1):
            if not isinstance(line, str) or not line.strip():
                errors.append(EntryValidationError(path, f"expected_body_lines[{index}] must be non-empty text"))

    return errors


def validate_entry_files(path: Path | None = None) -> list[EntryValidationError]:
    path = path or ROOT / "commit_examples_data" / "entries"
    if not path.exists():
        return [EntryValidationError(path, "entries directory does not exist")]

    errors: list[EntryValidationError] = []
    seen_titles: dict[str, Path] = {}
    seen_texts: dict[str, Path] = {}
    for entry_path in sorted(path.glob("*.json")):
        try:
            entry = json.loads(entry_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(EntryValidationError(entry_path, f"invalid JSON: {exc}"))
            continue
        if not isinstance(entry, dict):
            errors.append(EntryValidationError(entry_path, "entry must be a JSON object"))
            continue
        errors.extend(validate_entry(entry, entry_path))

        title_key = regex.sub(r"\s+", " ", str(entry.get("title", "")).lower()).strip()
        if title_key:
            if title_key in seen_titles:
                errors.append(EntryValidationError(entry_path, f"duplicate title also used by {seen_titles[title_key]}"))
            else:
                seen_titles[title_key] = entry_path

        text_key = regex.sub(r"\s+", " ", str(entry.get("original_text", "")).lower()).strip()
        if text_key:
            if text_key in seen_texts:
                errors.append(EntryValidationError(entry_path, f"duplicate original_text also used by {seen_texts[text_key]}"))
            else:
                seen_texts[text_key] = entry_path
    return errors


def load_examples_json(path: Path | None = None) -> list[TrainingExample]:
    path = path or ROOT / "commit_examples_data" / "examples.json"
    if not path.exists():
        return []
    entries = json.loads(path.read_text(encoding="utf-8"))
    return [ex for entry in entries if (ex := _entry_to_example(entry, str(path)))]


def load_examples_db(path: Path | None = None) -> list[TrainingExample]:
    path = path or ROOT / "commit_examples_data" / "examples.db"
    if not path.exists():
        return []
    examples: list[TrainingExample] = []
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        for row in conn.execute("SELECT original_text, expected_subject FROM examples"):
            entry = dict(row)
            if ex := _entry_to_example(entry, str(path)):
                examples.append(ex)
    return examples


def load_entry_files(path: Path | None = None) -> list[TrainingExample]:
    path = path or ROOT / "commit_examples_data" / "entries"
    if not path.exists():
        return []
    examples = []
    for entry_path in sorted(path.glob("*.json")):
        entry = json.loads(entry_path.read_text(encoding="utf-8"))
        if ex := _entry_to_example(entry, str(entry_path)):
            examples.append(ex)
    return examples


def load_seed_examples() -> list[TrainingExample]:
    return [TrainingExample(text=text, label=label, source="built-in-seed") for text, label in SEED_EXAMPLES]


def load_training_examples(include_seed: bool = True) -> list[TrainingExample]:
    """Load and de-duplicate all offline training examples."""
    candidates = []
    candidates.extend(load_examples_json())
    candidates.extend(load_examples_db())
    candidates.extend(load_entry_files())
    if include_seed:
        candidates.extend(load_seed_examples())

    unique: list[TrainingExample] = []
    seen = set()
    for example in candidates:
        key = (regex.sub(r"\s+", " ", example.text.lower()).strip(), example.label)
        if key not in seen:
            unique.append(example)
            seen.add(key)
    return unique


def as_training_arrays(examples: list[TrainingExample]) -> tuple[list[str], list[str]]:
    return [example.text for example in examples], [example.label for example in examples]


def label_counts(examples: list[TrainingExample]) -> dict[str, int]:
    counts = Counter(example.label for example in examples)
    return {label: counts.get(label, 0) for label in sorted(SUPPORTED_TYPES)}


def summarize_label_balance(examples: list[TrainingExample]) -> dict:
    counts = label_counts(examples)
    nonzero_counts = [count for count in counts.values() if count > 0]
    total = sum(counts.values())
    largest_label = max(counts, key=counts.get) if counts else None
    smallest_label = min(counts, key=counts.get) if counts else None
    max_count = counts.get(largest_label, 0) if largest_label else 0
    min_nonzero = min(nonzero_counts) if nonzero_counts else 0

    return {
        "total": total,
        "counts": counts,
        "largest_label": largest_label,
        "largest_count": max_count,
        "smallest_label": smallest_label,
        "smallest_count": counts.get(smallest_label, 0) if smallest_label else 0,
        "imbalance_ratio": round(max_count / min_nonzero, 2) if min_nonzero else None,
    }
