"""Conventional Commit type and scope detection helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .language import detect_language


COMMIT_TYPE_OPTIONS = ("feat", "fix", "docs", "test", "build", "ci", "style", "refactor", "perf", "chore")
SCOPE_OPTIONS = ("config", "parser", "prompt", "ui", "docs", "repo", "ml", "test", "core")


@dataclass(frozen=True)
class DetectionContext:
    """Shared summary flags computed by the heuristic orchestrator."""

    readme_architecture_docs: bool = False
    ml_metadata_validation: bool = False
    mixed_language_nlp: bool = False
    ml_pipeline: bool = False
    spanish_verb_expansion: bool = False


DOCS_KEYWORDS = [
    "readme", "roadmap", "docs", "documentation", "documentación",
    "documentacion", ".md", ".rst", "guide", "guía", "guia", "help",
    "instructions", "installation instructions", "instrucciones",
    "instalación", "instalacion", "docstring", "comment",
]
TEST_KEYWORDS = ["test", "tests", "unittest", "pytest", "coverage", "qa", "spec", "mock", "prueba", "pruebas"]
CI_KEYWORDS = [
    "ci", "continuous integration", "github action", "workflow", "pipeline",
    "circleci", "travis", "jenkins", "gitlab-ci", "azure-pipelines",
]
BUILD_KEYWORDS = [
    "build", "docker", "dockerfile", "dependency", "dependencies", "npm",
    "package.json", "yarn.lock", "pip", "requirements", "maven", "gradle",
    "pom.xml", "pyproject.toml",
]
PERF_KEYWORDS = ["perf", "performance", "speed", "latency", "memory", "optimiz", "cache", "caching", "rendimiento"]
STYLE_KEYWORDS = ["style", "format", "formatted", "lint", "whitespace", "indent", "prettier", "eslint", "formato"]
REFACTOR_KEYWORDS = [
    "refactor", "cleanup", "cleaned", "restructure", "rename", "split",
    "extract", "simplify", "refactoriza", "limpia",
]
FIX_KEYWORDS = [
    "fix", "fixed", "correct", "corrected", "resolve", "resolved", "bug",
    "crash", "error", "fallo", "corrige", "corregido", "corregí",
    "arregla", "arreglado", "arreglé",
]


def has_any(text_lower: str, markers: list[str]) -> bool:
    return any(marker in text_lower for marker in markers)


def detect_scope(text: str, context: DetectionContext | None = None) -> str:
    context = context or DetectionContext()
    text_lower = text.lower()

    if context.ml_metadata_validation:
        return "ml"
    if context.mixed_language_nlp:
        return "prompt"
    if context.readme_architecture_docs:
        return "docs"
    if context.ml_pipeline:
        return "ml"
    if context.spanish_verb_expansion:
        return "prompt"

    if has_any(text_lower, ["parser", "parse", "loader", "smf", "midi", "wrk", "file format", "header", "serializer"]):
        return "parser"
    if has_any(text_lower, ["config", "settings", "preferences", "environment variables", ".env", "api key", "secret", "permissions", "gitignore"]):
        return "config"
    if has_any(text_lower, ["prompt", "examples", "few-shot", "quality", "gemini"]):
        return "prompt"
    if has_any(text_lower, ["ui", "window", "dialog", "view", "panel", "button", "toggle", "playlist", "main window", "copy", "clipboard"]):
        return "ui"
    if regex_search_test_scope(text_lower):
        return "test"
    if has_any(text_lower, ["test_smart_commit.py", "comparison_report.json", ".gitignore", "baseline", "línea base", "linea base"]):
        return "repo"
    if has_any(text_lower, ["ml", "model", "training", "classifier", "sklearn", "vectorizer", "confidence"]):
        return "ml"
    if has_any(text_lower, DOCS_KEYWORDS):
        return "docs"
    if "repo" in text_lower or ".gitignore" in text_lower or "clone" in text_lower or "repository" in text_lower:
        return "repo"

    return "core"


def regex_search_test_scope(text_lower: str) -> bool:
    import re

    return re.search(r"\b(tests?|pruebas?)\b", text_lower) is not None


def select_commit_type(
    text: str,
    subject_verb: str | None,
    subject_obj: str | None = None,
    context: DetectionContext | None = None,
) -> str:
    del subject_obj
    context = context or DetectionContext()
    text_lower = text.lower()
    subject_verb = (subject_verb or "").lower()
    language = detect_language(text)

    if context.ml_metadata_validation:
        return "feat"
    if context.mixed_language_nlp:
        return "feat"
    if context.readme_architecture_docs:
        return "docs"
    if context.ml_pipeline:
        return "feat"
    if context.spanish_verb_expansion:
        return "feat"

    if has_any(text_lower, ["ci", "continuous integration", "workflow", "pipeline"]):
        return "ci"
    if has_any(text_lower, BUILD_KEYWORDS):
        return "build"
    if has_any(text_lower, ["skip low-quality", "skip", "filter", "discard", "exclude", "reject"]) and has_any(text_lower, ["example", "examples", "prompt", "json", "data"]):
        return "fix"
    if has_any(text_lower, TEST_KEYWORDS) and has_any(text_lower, ["regression", "regresión", "regresion", "suite", "validation", "verificación", "verificacion"]):
        return "test"
    if has_any(text_lower, PERF_KEYWORDS) or subject_verb in {"perf", "optimize", "improve", "speed"}:
        return "perf"
    if has_any(text_lower, STYLE_KEYWORDS) or subject_verb in {"style", "format", "lint"}:
        return "style"
    if has_any(text_lower, REFACTOR_KEYWORDS) or subject_verb in {"refactor", "cleanup", "clean", "rename", "restructure", "simplify"}:
        return "refactor"
    if has_any(text_lower, DOCS_KEYWORDS) and subject_verb not in {"fix", "perf", "refactor", "test", "build", "ci", "style"}:
        return "docs"
    if has_any(text_lower, FIX_KEYWORDS) or subject_verb in {"fix", "correct", "resolve"}:
        return "fix"
    if subject_verb in {"skip", "filter", "discard", "exclude", "reject"} and has_any(text_lower, ["example", "examples", "prompt", "json", "data"]):
        return "fix"

    if language == "es" and has_any(text_lower, ["añad", "agreg", "implement", "actualiz", "mejor", "crea", "genera"]):
        return "feat"
    return "feat"
