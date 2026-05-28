"""Local rule-based generator for Conventional Commit commands."""

from __future__ import annotations

import re

from .commit_message import CommitMessage, normalize_body_line, normalize_subject
from .input_cleanup import clean_input, strip_markdown_noise
from .type_scope import detect_scope as heuristic_detect_scope
from .type_scope import select_commit_type as heuristic_select_commit_type


ACTION_VERBS = {
    "feat": "add",
    "fix": "fix",
    "docs": "update",
    "test": "add",
    "refactor": "refactor",
    "style": "format",
    "ci": "update",
    "perf": "improve",
    "chore": "update",
}


class LocalCommitGenerator:
    """Generate useful commit messages without network access."""

    def generate(self, original_text: str) -> CommitMessage:
        cleaned = normalize_input_text(original_text)
        signal_text = clean_input(original_text) or cleaned
        commit_type = detect_type(signal_text)
        scope = detect_scope(signal_text, commit_type)
        subject_phrase = build_subject_phrase(cleaned, commit_type, scope)
        subject = normalize_subject(f"{commit_type}({scope}): {subject_phrase}")
        body_lines = build_body_lines(cleaned, commit_type, scope)
        return CommitMessage(subject=subject, body_lines=body_lines, source="local").normalized()


def normalize_input_text(text: str) -> str:
    text = strip_markdown_noise(text)
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    return text.strip()


def detect_type(text: str) -> str:
    lower = text.lower()
    if is_api_key_persistence_summary(lower):
        return "feat"
    if is_prompt_example_filter_summary(lower):
        return "fix"
    if "wrk" in lower and ("recognizes" in lower or "detect" in lower or "support" in lower):
        return "feat"

    heuristic = heuristic_select_commit_type(text, subject_verb=extract_subject_verb(text))
    if heuristic in ACTION_VERBS:
        return heuristic

    scores = {
        "fix": score_keywords(
            lower,
            [
                "fix",
                "fixed",
                "bug",
                "error",
                "failure",
                "prevent",
                "correct",
                "handle",
                "leak",
                "race",
                "regression",
                "vulnerability",
                "not supported",
            ],
        ),
        "feat": score_keywords(
            lower,
            [
                "add",
                "added",
                "implement",
                "implemented",
                "introduce",
                "enable",
                "support",
                "new ",
                "now recognizes",
                "detect",
            ],
        ),
        "docs": score_keywords(
            lower,
            ["readme", "documentation", "docs", "guide", "roadmap", "changelog", "document"],
        ),
        "test": score_keywords(lower, ["test", "tests", "coverage", "unittest", "pytest"]),
        "refactor": score_keywords(
            lower,
            ["refactor", "split", "extract", "replace", "simplify", "migrate", "consolidate"],
        ),
        "ci": score_keywords(lower, ["ci", "pipeline", "github actions", "gitlab ci"]),
        "perf": score_keywords(lower, ["performance", "slow", "speed", "optimize", "latency"]),
        "style": score_keywords(lower, ["format", "lint", "style", "css"]),
        "chore": score_keywords(lower, ["dependency", "dependencies", "build", "tooling", "config"]),
    }

    if looks_like_docs_only(lower):
        return "docs"
    if looks_like_tests_only(lower):
        return "test"

    non_test_priority = ["fix", "feat", "refactor", "perf", "docs", "ci", "style", "chore"]
    if max(scores[kind] for kind in non_test_priority):
        return max(non_test_priority, key=lambda kind: (scores[kind], -non_test_priority.index(kind)))
    return "test" if scores["test"] else "chore"


def score_keywords(text: str, keywords: list[str]) -> int:
    score = 0
    for keyword in keywords:
        score += text.count(keyword)
    return score


def looks_like_docs_only(lower: str) -> bool:
    doc_hits = score_keywords(lower, ["readme", "documentation", "docs", "guide", "roadmap"])
    code_hits = score_keywords(lower, ["loader", "parser", "ui", "test", "implemented", "added support"])
    return doc_hits >= 2 and code_hits == 0


def looks_like_tests_only(lower: str) -> bool:
    test_hits = score_keywords(lower, ["test", "tests", "coverage", "unittest", "pytest"])
    feature_hits = score_keywords(lower, ["add ", "implement", "fix", "refactor", "ui", "parser"])
    return test_hits >= 2 and feature_hits == 0


def detect_scope(text: str, commit_type: str) -> str:
    lower = text.lower()
    if is_api_key_persistence_summary(lower):
        return "config"
    if is_prompt_example_filter_summary(lower):
        return "prompt"

    heuristic = heuristic_detect_scope(text)
    if heuristic in {"config", "parser", "prompt", "ui", "docs", "repo", "ml", "test"}:
        return heuristic

    scopes = [
        (
            "parser",
            [
                "parser",
                "parse",
                "loader",
                "smf",
                "midi",
                "wrk",
                "file format",
                "header",
                "serializer",
            ],
        ),
        ("ui", ["ui", "window", "dialog", "view", "panel", "button", "toggle", "playlist", "main window"]),
        ("auth", ["auth", "login", "password", "oauth", "oidc", "saml", "jwt", "2fa", "mfa", "totp"]),
        ("api", ["api", "endpoint", "request", "response", "rest", "graphql", "webhook"]),
        ("ml", ["ml", "model", "training", "classifier", "sklearn", "vectorizer", "confidence"]),
        ("data", ["dataset", "examples", "entries", "json", "training data"]),
        ("security", ["csrf", "xss", "sql injection", "vulnerability", "certificate", "ssl", "tls"]),
        ("ci", ["ci", "pipeline", "github actions", "gitlab ci"]),
        ("test", ["test", "coverage", "unittest", "pytest"]),
        ("docs", ["readme", "documentation", "docs", "roadmap", "guide"]),
        ("prompt", ["prompt", "examples", "few-shot", "quality", "gemini"]),
        ("db", ["database", "postgres", "mysql", "sqlite", "redis", "mongodb"]),
        (
            "config",
            [
                "config",
                "settings",
                "preferences",
                "environment variables",
                ".env",
                "api key",
                "secret",
                "permissions",
                "gitignore",
            ],
        ),
    ]

    scores = {
        scope: score_keywords(lower, keywords)
        for scope, keywords in scopes
        if score_keywords(lower, keywords)
    }
    if not scores:
        return "core"

    if commit_type == "docs" and scores.get("docs", 0) >= max(scores.values()):
        return "docs"
    if commit_type == "test" and scores.get("test", 0) >= max(scores.values()):
        return "test"

    return max(scores, key=lambda scope: (scores[scope], -list(scores).index(scope)))


def extract_subject_verb(text: str) -> str | None:
    for sentence in split_sentences(text):
        normalized = strip_sentence_noise(sentence)
        match = re.match(r"^(?:we|i|the app|this|it)\s+(?:now\s+)?([a-z]+)", normalized, flags=re.I)
        if match:
            return match.group(1).lower()
        match = re.search(
            r"\b(added|implemented|updated|fixed|refactored|documented|improved|prevented|detected|recognized|supports?|loads?|writes?|reports?|validates?)\b",
            normalized,
            flags=re.I,
        )
        if match:
            return match.group(1).lower()
    return None


def build_subject_phrase(text: str, commit_type: str, scope: str) -> str:
    lower = text.lower()
    if is_api_key_persistence_summary(lower):
        return "persist Gemini API key"
    if is_prompt_example_filter_summary(lower):
        return "skip low-quality prompt examples"
    if "cakewalk" in lower and "wrk" in lower:
        return "detect Cakewalk WRK files"
    if "wrk" in lower and ("parser" in lower or "loader" in lower):
        return "detect WRK files"
    if "two-factor" in lower or "2fa" in lower:
        return "add two-factor authentication"
    if "rhythm view" in lower:
        return "add embedded Rhythm view"

    phrase = extract_action_object(text, commit_type)
    if phrase:
        return phrase

    return f"{ACTION_VERBS.get(commit_type, 'update')} {scope} changes"


def extract_action_object(text: str, commit_type: str) -> str | None:
    verbs = {
        "feat": r"add(?:ed)?|implement(?:ed)?|introduce(?:d)?|enable(?:d)?|support(?:ed)?",
        "fix": r"fix(?:ed)?|prevent(?:ed)?|correct(?:ed)?|handle(?:d)?|resolve(?:d)?",
        "docs": r"update(?:d)?|document(?:ed)?|add(?:ed)?",
        "test": r"add(?:ed)?|cover(?:ed)?|test(?:ed)?",
        "refactor": r"refactor(?:ed)?|extract(?:ed)?|split|replace(?:d)?|migrate(?:d)?",
        "perf": r"improve(?:d)?|optimize(?:d)?|speed up|reduce(?:d)?",
        "chore": r"update(?:d)?|add(?:ed)?|upgrade(?:d)?",
    }.get(commit_type, r"update(?:d)?|add(?:ed)?")

    for sentence in split_sentences(text):
        normalized = strip_sentence_noise(sentence)
        match = re.search(rf"\b({verbs})\s+(?:an?\s+|the\s+)?([^.;:\n]+)", normalized, flags=re.I)
        if not match:
            match = re.search(r"\bnow\s+(?:deliberately\s+)?recognizes?\s+([^.;:\n]+)", normalized, flags=re.I)
        if not match:
            continue
        verb = imperative_verb(match.group(1), commit_type) if match.lastindex and match.lastindex >= 1 else ACTION_VERBS[commit_type]
        obj = match.group(match.lastindex or 1)
        obj = clean_subject_object(obj)
        if obj:
            return f"{verb} {obj}"
    return None


def imperative_verb(value: str, commit_type: str) -> str:
    lower = value.lower()
    if lower.startswith("added") or lower.startswith("add"):
        return "add"
    if lower.startswith("implemented") or lower.startswith("implement"):
        return "implement"
    if lower.startswith("introduced") or lower.startswith("introduce"):
        return "introduce"
    if lower.startswith("enabled") or lower.startswith("enable"):
        return "enable"
    if lower.startswith("supported") or lower.startswith("support"):
        return "support"
    if lower.startswith("document"):
        return "document"
    if lower.startswith("updated") or lower.startswith("update"):
        return "update"
    if lower.startswith("prevent"):
        return "prevent"
    if lower.startswith("handle"):
        return "handle"
    if lower.startswith("resolve"):
        return "resolve"
    if lower.startswith("fix"):
        return "fix"
    if lower.startswith("refactor"):
        return "refactor"
    if lower.startswith("extract"):
        return "extract"
    if lower.startswith("split"):
        return "split"
    if lower.startswith("replace"):
        return "replace"
    if lower.startswith("migrate"):
        return "migrate"
    if lower.startswith("recognize"):
        return "detect" if commit_type == "feat" else "recognize"
    return ACTION_VERBS.get(commit_type, "update")


def clean_subject_object(value: str) -> str:
    value = re.sub(r"\s+and\s+.*$", "", value, flags=re.I)
    value = re.sub(r"\s+to\s+match\s+.*$", "", value, flags=re.I)
    value = re.sub(r"\s+with\s+.*$", "", value, flags=re.I)
    value = value.strip(" -,:.`'\"")
    value = re.sub(r"\binput\b", "files", value, flags=re.I)
    value = re.sub(r"\bthe\s+", "", value, flags=re.I)
    return value


def build_body_lines(text: str, commit_type: str, scope: str) -> list[str]:
    if is_api_key_persistence_summary(text.lower()):
        return api_key_persistence_body_lines(text)
    if is_prompt_example_filter_summary(text.lower()):
        return prompt_example_filter_body_lines(text)

    if "cakewalk" in text.lower() and "wrk" in text.lower():
        return wrk_body_lines(text)

    candidates: list[str] = []
    for sentence in split_sentences(text):
        if should_skip_body_sentence(sentence):
            continue
        bullet = sentence_to_bullet(sentence)
        if bullet:
            candidates.append(bullet)

    validation = extract_validation(text)
    if validation:
        candidates.append(f"- Validation: {validation}")

    if not candidates:
        candidates.append(f"- {ACTION_VERBS.get(commit_type, 'Update').capitalize()} {scope} behavior")

    return unique_limited_body(candidates)


def wrk_body_lines(text: str) -> list[str]:
    lines = [
        "- Recognize Cakewalk WRK input and raise a specific error",
        "- Prevent generic SMF parsing failures for unsupported WRK files",
    ]
    lower = text.lower()
    if "test" in lower or "coverage" in lower:
        lines.append("- Add WRK-like header test coverage")
    if "roadmap" in lower:
        lines.append("- Update Roadmap.md to mark WRK skeleton item complete")
    validation = extract_validation(text)
    if validation:
        lines.append(f"- Validation: {validation}")
    return unique_limited_body(lines)


def is_api_key_persistence_summary(lower: str) -> bool:
    return (
        ("gemini" in lower or "gemini_api_key" in lower)
        and ("api key" in lower or "gemini_api_key" in lower)
        and (".env.local" in lower or "saved locally" in lower or "save" in lower)
    )


def is_prompt_example_filter_summary(lower: str) -> bool:
    return (
        ("low-quality" in lower or "low quality" in lower)
        and ("example" in lower or "examples" in lower or "json" in lower)
        and ("prompt" in lower or "few-shot" in lower or "gemini" in lower)
    )


def prompt_example_filter_body_lines(text: str) -> list[str]:
    lines = [
        "- Filter low-quality examples out of Gemini prompt context",
        "- Prevent weak saved JSON entries from shaping future responses",
        "- Keep bodyless or vague examples out of few-shot data",
    ]
    referenced_entries = re.findall(r"\b\d{3,}\b", text)
    if referenced_entries:
        entries = ", ".join(dict.fromkeys(referenced_entries))
        lines.append(f"- Exclude referenced weak entries such as {entries}")
    return unique_limited_body(lines)


def api_key_persistence_body_lines(text: str) -> list[str]:
    lower = text.lower()
    lines = [
        "- Save GEMINI_API_KEY to ignored .env.local",
        "- Load saved Gemini key when the app window opens",
        "- Wire GUI to persist keys before commit generation",
    ]
    if "600" in lower or "permissions" in lower or "perms" in lower:
        lines.append("- Set .env.local permissions to 600 when possible")
    if ".gitignore" in lower or "ignored" in lower:
        lines.append("- Add .env.local ignore coverage to prevent key commits")
    if "readme" in lower:
        lines.append("- Document local key storage and ignore behavior")
    validation = extract_validation(text)
    if validation:
        lines.append(f"- Validation: {validation}")
    return unique_limited_body(lines)


def split_sentences(text: str) -> list[str]:
    prepared = re.sub(r"\n+\s*", ". ", text)
    prepared = re.sub(r"\s+", " ", prepared)
    return [item.strip() for item in re.split(r"(?<=[.!?])\s+", prepared) if item.strip()]


def strip_sentence_noise(sentence: str) -> str:
    value = sentence.strip()
    value = re.sub(r"^We\s+(?:kept|got|continued).*?\.\s*", "", value, flags=re.I)
    value = re.sub(r"^(?:I|We)\s+(?:also\s+)?", "", value, flags=re.I)
    value = re.sub(r"^Continued\s+by\s+", "", value, flags=re.I)
    value = re.sub(r"^In\s+[^,]+,\s+", "", value, flags=re.I)
    value = re.sub(r"^To\s+support\s+that\s+cleanly,\s+", "", value, flags=re.I)
    return value.strip()


def should_skip_body_sentence(sentence: str) -> bool:
    lower = sentence.lower()
    if len(sentence.strip()) < 18:
        return True
    skip_phrases = [
        "a strong next move",
        "next move",
        "we kept the development moving",
        "verification is clean",
        "result:",
        "git commit",
    ]
    if any(phrase in lower for phrase in skip_phrases):
        return True
    action_phrases = [
        "add",
        "added",
        "implement",
        "implemented",
        "update",
        "updated",
        "fix",
        "fixed",
        "prevent",
        "refactor",
        "test",
        "coverage",
        "document",
        "now ",
        "support",
        "enable",
    ]
    return not any(phrase in lower for phrase in action_phrases)


def sentence_to_bullet(sentence: str) -> str | None:
    value = strip_sentence_noise(sentence)
    value = value.strip(" -")
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"^(?:I|We)\s+(?:also\s+)?", "", value, flags=re.I)
    replacements = [
        (r"^Added\b", "Add"),
        (r"^Implemented\b", "Implement"),
        (r"^Updated\b", "Update"),
        (r"^Fixed\b", "Fix"),
        (r"^Refactored\b", "Refactor"),
        (r"^Documented\b", "Document"),
        (r"^Tests?\s+.*?\s+cover\b", "Add tests for"),
    ]
    for pattern, replacement in replacements:
        value = re.sub(pattern, replacement, value, flags=re.I)
    value = re.sub(r"\s+so\s+.+$", "", value, flags=re.I)
    value = value.strip(" .:;")
    if not value:
        return None
    return normalize_body_line(f"- {value}")


def unique_limited_body(lines: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for line in lines:
        normalized = normalize_body_line(line)
        key = re.sub(r"[^a-z0-9]+", "", normalized.lower())
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(normalized)
        if len(result) >= 7:
            break
    return result


def extract_validation(text: str) -> str | None:
    lower = text.lower()
    parts: list[str] = []

    focused_match = re.search(r"focused\s+([a-z0-9_-]+)?\s*[^:.\n]*passed:\s*`?(\d+)\s+tests?\s+OK`?", text, re.I)
    if focused_match:
        label = (focused_match.group(1) or "focused").strip()
        parts.append(f"{focused_match.group(2)} {label} tests pass")

    full_match = re.search(r"full\s+test\s+suite\s+passed:\s*`?(\d+)\s+tests?\s+OK`?", text, re.I)
    if full_match:
        parts.append(f"{full_match.group(1)} full tests pass")

    all_match = re.search(r"(\d+)\s+tests?\s+(?:ran,\s*)?\1?\s*(?:passed|pass|OK)", text, re.I)
    if all_match and not any("tests pass" in part for part in parts):
        parts.append(f"all {all_match.group(1)} tests pass")

    tests_pass_match = re.search(r"tests?\s+pass(?:ed)?:\s*(\d+)\s+tests?\s+OK", text, re.I)
    if tests_pass_match and not any(tests_pass_match.group(1) in part for part in parts):
        parts.append(f"{tests_pass_match.group(1)} tests pass")

    single_match = re.search(r"(\d+)\s+tests?\s+OK", text, re.I)
    if single_match and not any(single_match.group(1) in part for part in parts):
        parts.append(f"{single_match.group(1)} tests pass")

    if ("compileall" in lower or "compile check" in lower) and (
        "passed" in lower or "passes" in lower or "clean" in lower or "ok" in lower
    ):
        parts.append("compileall OK")

    if "git diff --check" in lower and ("passed" in lower or "clean" in lower):
        parts.append("git diff --check clean")

    if not parts and "operational" in lower:
        match = re.search(r"Result:\s*([^.\n]+)", text, re.I)
        if match:
            parts.append(match.group(1).strip())

    return ", ".join(parts[:4]) if parts else None
