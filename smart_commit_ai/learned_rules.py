"""Learn lightweight local rules from saved commit examples."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from math import sqrt
from pathlib import Path
import re
from typing import Iterable

from .commit_message import clean_scope, normalize_body_line
from .examples import DEFAULT_ENTRIES_DIR, ExampleEntry, ExampleStore


DEFAULT_RULES_PATH = DEFAULT_ENTRIES_DIR.parent / "smart_commit_rules.json"
RULES_VERSION = 1
MAX_TOKEN_SCORES_PER_LABEL = 220

GENERIC_SUBJECT_MARKERS = {
    "update changes",
    "update prompt changes",
    "restrict saved",
    "improve app",
    "update project changes",
}

STOPWORDS = {
    "a",
    "all",
    "also",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "being",
    "both",
    "by",
    "can",
    "change",
    "changes",
    "cleanly",
    "continued",
    "coverage",
    "de",
    "del",
    "do",
    "each",
    "el",
    "en",
    "file",
    "files",
    "finished",
    "first",
    "for",
    "from",
    "good",
    "got",
    "has",
    "i",
    "in",
    "is",
    "it",
    "its",
    "kept",
    "la",
    "las",
    "line",
    "lines",
    "lo",
    "los",
    "me",
    "moved",
    "moving",
    "my",
    "now",
    "of",
    "on",
    "one",
    "or",
    "our",
    "para",
    "per",
    "por",
    "que",
    "result",
    "results",
    "se",
    "so",
    "small",
    "test",
    "tests",
    "that",
    "the",
    "their",
    "there",
    "these",
    "this",
    "those",
    "to",
    "un",
    "una",
    "using",
    "was",
    "we",
    "were",
    "with",
    "without",
    "you",
    "your",
    "verification",
    "verified",
    "verificacion",
    "verificación",
    "validation",
    "clean",
    "passed",
    "pass",
    "ok",
    "full",
    "suite",
    "compileall",
}


@dataclass(frozen=True)
class ParsedSubject:
    commit_type: str
    scope: str
    description: str


@dataclass(frozen=True)
class LearnedExample:
    subject: str
    commit_type: str
    scope: str
    description: str
    body_lines: list[str]
    tokens: list[str]


@dataclass(frozen=True)
class SimilarExample:
    score: float
    example: LearnedExample


@dataclass(frozen=True)
class LearnedPrediction:
    commit_type: str | None = None
    scope: str | None = None
    subject_phrase: str | None = None
    body_lines: list[str] | None = None
    nearest_score: float = 0.0


class LearnedRuleSet:
    """In-memory rule set trained from saved input/output examples."""

    def __init__(
        self,
        *,
        example_count: int = 0,
        type_token_scores: dict[str, dict[str, float]] | None = None,
        scope_token_scores: dict[str, dict[str, float]] | None = None,
        file_scope_scores: dict[str, dict[str, float]] | None = None,
        examples: list[LearnedExample] | None = None,
    ) -> None:
        self.example_count = example_count
        self.type_token_scores = type_token_scores or {}
        self.scope_token_scores = scope_token_scores or {}
        self.file_scope_scores = file_scope_scores or {}
        self.examples = examples or []

    @classmethod
    def empty(cls) -> "LearnedRuleSet":
        return cls()

    @classmethod
    def load_default(cls) -> "LearnedRuleSet":
        if DEFAULT_RULES_PATH.exists():
            try:
                return cls.load(DEFAULT_RULES_PATH)
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                pass
        return train_from_entries(ExampleStore().load())

    @classmethod
    def load(cls, path: Path | str) -> "LearnedRuleSet":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        examples = [
            LearnedExample(
                subject=str(item["subject"]),
                commit_type=str(item["type"]),
                scope=str(item["scope"]),
                description=str(item["description"]),
                body_lines=[str(line) for line in item.get("body_lines", [])],
                tokens=[str(token) for token in item.get("tokens", [])],
            )
            for item in data.get("examples", [])
        ]
        return cls(
            example_count=int(data.get("example_count", len(examples))),
            type_token_scores=score_mapping(data.get("type_token_scores", {})),
            scope_token_scores=score_mapping(data.get("scope_token_scores", {})),
            file_scope_scores=score_mapping(data.get("file_scope_scores", {})),
            examples=examples,
        )

    def save(self, path: Path | str = DEFAULT_RULES_PATH) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": RULES_VERSION,
            "example_count": self.example_count,
            "type_token_scores": self.type_token_scores,
            "scope_token_scores": self.scope_token_scores,
            "file_scope_scores": self.file_scope_scores,
            "examples": [
                {
                    "subject": example.subject,
                    "type": example.commit_type,
                    "scope": example.scope,
                    "description": example.description,
                    "body_lines": example.body_lines,
                    "tokens": example.tokens,
                }
                for example in self.examples
            ],
        }
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return output_path

    def predict(self, text: str) -> LearnedPrediction:
        tokens = feature_tokens(text)
        if not tokens:
            return LearnedPrediction()

        similar = self.similar_examples(text, limit=3)
        commit_type = best_label(self._label_scores(tokens, self.type_token_scores, similar, "type"))
        scope = best_label(self._label_scores(tokens, self.scope_token_scores, similar, "scope"))
        file_scope = best_label(file_scope_scores(extract_file_tokens(text), self.file_scope_scores))
        scope = file_scope or scope

        nearest = similar[0] if similar else None
        subject_phrase = None
        body_lines: list[str] = []
        if nearest and nearest.score >= 0.28:
            example = nearest.example
            if (commit_type in {None, example.commit_type}) and (scope in {None, example.scope}):
                subject_phrase = example.description
            body_lines = matching_body_lines(text, example.body_lines)

        return LearnedPrediction(
            commit_type=commit_type,
            scope=scope,
            subject_phrase=subject_phrase,
            body_lines=body_lines,
            nearest_score=nearest.score if nearest else 0.0,
        )

    def similar_examples(self, text: str, limit: int = 4) -> list[SimilarExample]:
        query_tokens = set(feature_tokens(text))
        if not query_tokens:
            return []

        scored: list[SimilarExample] = []
        for example in self.examples:
            example_tokens = set(example.tokens)
            if not example_tokens:
                continue
            overlap = len(query_tokens & example_tokens)
            if not overlap:
                continue
            score = overlap / sqrt(len(query_tokens) * len(example_tokens))
            if score >= 0.12:
                scored.append(SimilarExample(score=score, example=example))

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:limit]

    def _label_scores(
        self,
        tokens: list[str],
        token_scores: dict[str, dict[str, float]],
        similar: list[SimilarExample],
        label_kind: str,
    ) -> dict[str, float]:
        scores: dict[str, float] = defaultdict(float)
        for label, weights in token_scores.items():
            for token in tokens:
                scores[label] += weights.get(token, 0.0)

        for item in similar:
            label = item.example.commit_type if label_kind == "type" else item.example.scope
            scores[label] += item.score * 30.0

        return dict(scores)


def train_from_entries(entries: Iterable[ExampleEntry]) -> LearnedRuleSet:
    learned_examples: list[LearnedExample] = []
    type_counts: Counter[str] = Counter()
    scope_counts: Counter[str] = Counter()
    token_by_type: dict[str, Counter[str]] = defaultdict(Counter)
    token_by_scope: dict[str, Counter[str]] = defaultdict(Counter)
    scope_by_file: dict[str, Counter[str]] = defaultdict(Counter)
    global_token_counts: Counter[str] = Counter()

    for entry in entries:
        parsed = parse_subject(entry.expected_subject)
        if parsed is None or is_low_quality_example(entry, parsed):
            continue

        tokens = feature_tokens(entry.original_text)
        if not tokens:
            continue

        token_set = set(tokens)
        type_counts[parsed.commit_type] += 1
        scope_counts[parsed.scope] += 1
        global_token_counts.update(token_set)
        token_by_type[parsed.commit_type].update(token_set)
        token_by_scope[parsed.scope].update(token_set)

        for file_token in extract_file_tokens(entry.original_text):
            scope_by_file[file_token][parsed.scope] += 1

        learned_examples.append(
            LearnedExample(
                subject=entry.expected_subject,
                commit_type=parsed.commit_type,
                scope=parsed.scope,
                description=parsed.description,
                body_lines=[normalize_body_line(line) for line in entry.expected_body_lines],
                tokens=sorted(token_set),
            )
        )

    return LearnedRuleSet(
        example_count=len(learned_examples),
        type_token_scores=build_token_scores(token_by_type, type_counts, global_token_counts),
        scope_token_scores=build_token_scores(token_by_scope, scope_counts, global_token_counts),
        file_scope_scores=build_file_scores(scope_by_file),
        examples=learned_examples,
    )


def parse_subject(subject: str) -> ParsedSubject | None:
    match = re.match(r"^([a-z]+)\(([a-z0-9._-]+)\):\s*(.+)$", subject.strip())
    if not match:
        return None
    commit_type, scope, description = match.groups()
    return ParsedSubject(commit_type=commit_type, scope=clean_scope(scope), description=description.strip())


def is_low_quality_example(entry: ExampleEntry, parsed: ParsedSubject) -> bool:
    description = parsed.description.lower().strip()
    if not entry.expected_body_lines:
        return True
    if description in GENERIC_SUBJECT_MARKERS:
        return True
    if len(description.split()) < 3:
        return True
    return False


def build_token_scores(
    label_token_counts: dict[str, Counter[str]],
    label_counts: Counter[str],
    global_token_counts: Counter[str],
) -> dict[str, dict[str, float]]:
    total_examples = sum(label_counts.values())
    scores: dict[str, dict[str, float]] = {}
    for label, token_counts in label_token_counts.items():
        label_total = label_counts[label]
        label_scores: dict[str, float] = {}
        for token, count in token_counts.items():
            other_total = max(1, total_examples - label_total)
            other_count = global_token_counts[token] - count
            label_freq = count / max(1, label_total)
            other_freq = other_count / other_total
            weight = max(0.0, label_freq - other_freq) * 100.0
            if weight >= 4.0:
                label_scores[token] = round(weight, 3)
        if label_scores:
            strongest = sorted(label_scores.items(), key=lambda item: (-item[1], item[0]))
            scores[label] = dict(sorted(strongest[:MAX_TOKEN_SCORES_PER_LABEL]))
    return scores


def build_file_scores(scope_by_file: dict[str, Counter[str]]) -> dict[str, dict[str, float]]:
    scores: dict[str, dict[str, float]] = {}
    for file_token, counts in scope_by_file.items():
        total = sum(counts.values())
        if total < 1:
            continue
        scores[file_token] = {
            scope: round((count / total) * 100.0, 3)
            for scope, count in sorted(counts.items())
            if count
        }
    return scores


def best_label(scores: dict[str, float]) -> str | None:
    if not scores:
        return None
    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best, best_score = ordered[0]
    second_score = ordered[1][1] if len(ordered) > 1 else 0.0
    if best_score < 8.0:
        return None
    if best_score - second_score < 2.0:
        return None
    return best


def file_scope_scores(file_tokens: list[str], score_map: dict[str, dict[str, float]]) -> dict[str, float]:
    scores: dict[str, float] = defaultdict(float)
    for file_token in file_tokens:
        for scope, score in score_map.get(file_token, {}).items():
            scores[scope] += score
    return dict(scores)


def matching_body_lines(text: str, body_lines: list[str]) -> list[str]:
    input_tokens = set(feature_tokens(text))
    matched: list[str] = []
    for line in body_lines:
        if line.lower().startswith("- validation:"):
            continue
        line_tokens = set(feature_tokens(line))
        if len(input_tokens & line_tokens) >= 2:
            matched.append(normalize_body_line(line))
    return matched[:4]


def feature_tokens(text: str) -> list[str]:
    raw_tokens = re.findall(r"[a-z0-9][a-z0-9._-]*", text.lower())
    tokens: set[str] = set()
    for raw_token in raw_tokens:
        for token in expand_token(raw_token):
            if token in STOPWORDS or token.isdigit() or len(token) < 2:
                continue
            tokens.add(token)
    return sorted(tokens)


def expand_token(raw_token: str) -> set[str]:
    token = raw_token.strip("._-")
    if not token:
        return set()
    values = {token}
    if "." in token:
        values.add(token.rsplit(".", 1)[0])
    values.update(part for part in re.split(r"[._/-]+", token) if part)
    return values


def extract_file_tokens(text: str) -> list[str]:
    candidates = re.findall(r"[a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+", text)
    tokens: set[str] = set()
    for candidate in candidates:
        path = Path(candidate.strip(".,:;()[]{}<>`'\""))
        name = path.name.lower()
        if not name:
            continue
        tokens.add(name)
        tokens.add(name.rsplit(".", 1)[0])
    return sorted(tokens)


def score_mapping(data: object) -> dict[str, dict[str, float]]:
    if not isinstance(data, dict):
        return {}
    result: dict[str, dict[str, float]] = {}
    for label, values in data.items():
        if not isinstance(values, dict):
            continue
        result[str(label)] = {str(token): float(score) for token, score in values.items()}
    return result


def train_default_rules(output_path: Path | str = DEFAULT_RULES_PATH) -> Path:
    rules = train_from_entries(ExampleStore().load())
    return rules.save(output_path)
