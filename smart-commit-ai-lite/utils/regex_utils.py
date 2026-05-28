"""Small wrapper around the optional Debian `python3-regex` package."""

try:
    import regex as _regex
except ImportError:  # pragma: no cover - stdlib fallback for minimal installs
    import re as _regex


regex = _regex

