"""NLTK-centered preprocessing shared by the heuristic and sklearn engines."""

from __future__ import annotations

from functools import lru_cache

import nltk
from nltk.stem.snowball import SnowballStemmer

from utils.language import detect_language
from utils.regex_utils import regex


ENGLISH_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "have", "in", "is", "it", "of", "on", "or", "that", "the", "this",
    "to", "was", "were", "with", "we", "i",
}

SPANISH_STOPWORDS = {
    "a", "al", "con", "de", "del", "el", "en", "es", "esta", "este",
    "la", "las", "lo", "los", "para", "por", "que", "se", "un", "una",
    "y", "he", "hemos",
}


@lru_cache(maxsize=2)
def _stemmer(language: str) -> SnowballStemmer:
    return SnowballStemmer("spanish" if language == "es" else "english")


def normalize_text(text: str) -> str:
    """Remove common Markdown/code noise before vectorization."""
    text = text or ""
    text = regex.sub(r"```.*?```", " ", text, flags=regex.S)
    text = regex.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = regex.sub(r"`([^`]+)`", r"\1", text)
    text = regex.sub(r"(?m)^\s*(git\s+commit\b|-m\s+[\"']).*$", " ", text)
    text = regex.sub(r"\s+", " ", text)
    return text.strip().lower()


def preprocess_text(text: str, language: str | None = None) -> str:
    """Tokenize, remove stopwords, and stem using lightweight NLTK pieces."""
    language = language if language in {"en", "es"} else detect_language(text)
    normalized = normalize_text(text)
    tokens = nltk.wordpunct_tokenize(normalized)
    stopwords = SPANISH_STOPWORDS if language == "es" else ENGLISH_STOPWORDS
    stemmer = _stemmer(language)

    processed = []
    for token in tokens:
        if not regex.match(r"^[\w-]+$", token, flags=regex.UNICODE):
            continue
        if len(token) <= 1 or token in stopwords:
            continue
        processed.append(stemmer.stem(token))

    return " ".join(processed)
