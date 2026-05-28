"""Local configuration helpers for secrets and user preferences."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_ENV_PATH = PROJECT_ROOT / ".env.local"
API_KEY_NAME = "GEMINI_API_KEY"


def load_api_key(
    path: Path | str = LOCAL_ENV_PATH,
    *,
    include_environment: bool = True,
) -> str:
    """Load the Gemini API key from env vars or the ignored local env file."""

    if include_environment:
        value = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if value:
            return value

    env_path = Path(path)
    if not env_path.exists():
        return ""

    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""

    for line in lines:
        key, separator, value = line.partition("=")
        if separator and key.strip() == API_KEY_NAME:
            return decode_env_value(value.strip())
    return ""


def save_api_key(api_key: str, path: Path | str = LOCAL_ENV_PATH) -> Path:
    """Save the Gemini API key to a git-ignored local env file."""

    clean_key = api_key.strip()
    if not clean_key:
        raise ValueError("API key cannot be empty.")

    env_path = Path(path)
    lines = read_existing_lines(env_path)
    encoded_line = f"{API_KEY_NAME}={encode_env_value(clean_key)}"
    replaced = False
    updated_lines: list[str] = []

    for line in lines:
        key, separator, _ = line.partition("=")
        if separator and key.strip() == API_KEY_NAME:
            if not replaced:
                updated_lines.append(encoded_line)
                replaced = True
            continue
        updated_lines.append(line)

    if not replaced:
        if updated_lines and updated_lines[-1].strip():
            updated_lines.append("")
        if not updated_lines:
            updated_lines.append("# Local Smart Commit AI secrets. Ignored by git.")
        updated_lines.append(encoded_line)

    env_path.write_text("\n".join(updated_lines).rstrip() + "\n", encoding="utf-8")
    try:
        env_path.chmod(0o600)
    except OSError:
        pass
    return env_path


def read_existing_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []


def encode_env_value(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def decode_env_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value

