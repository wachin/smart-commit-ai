"""Local configuration helpers for secrets and user preferences."""

from __future__ import annotations

import json
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_ENV_PATH = PROJECT_ROOT / ".env.local"
API_KEY_NAME = "GEMINI_API_KEY"
APP_CONFIG_DIRNAME = "smartcommitai"
SETTINGS_NAME = "settings.json"
SECRETS_NAME = "secrets.env"
VALID_PROVIDERS = {"local", "gemini", "auto"}
DEFAULT_PROVIDER = "local"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


def config_dir() -> Path:
    """Return the per-user Smart Commit AI config directory."""

    root = os.environ.get("XDG_CONFIG_HOME")
    if root:
        return Path(root) / APP_CONFIG_DIRNAME
    return Path.home() / ".config" / APP_CONFIG_DIRNAME


CONFIG_DIR = config_dir()
SETTINGS_PATH = CONFIG_DIR / SETTINGS_NAME
USER_ENV_PATH = CONFIG_DIR / SECRETS_NAME


def load_api_key(
    path: Path | str = USER_ENV_PATH,
    *,
    include_environment: bool = True,
) -> str:
    """Load the Gemini API key from env vars or the local user config."""

    if include_environment:
        value = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if value:
            return value

    for env_path in api_key_paths(path):
        value = load_api_key_from_file(env_path)
        if value:
            return value
    return ""


def load_api_key_from_file(path: Path | str) -> str:
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


def api_key_paths(path: Path | str) -> list[Path]:
    primary = Path(path)
    paths = [primary]
    if primary != LOCAL_ENV_PATH:
        paths.append(LOCAL_ENV_PATH)
    return paths


def save_api_key(api_key: str, path: Path | str = USER_ENV_PATH) -> Path:
    """Save the Gemini API key to the local user config directory."""

    clean_key = api_key.strip()
    if not clean_key:
        raise ValueError("API key cannot be empty.")

    env_path = Path(path)
    env_path.parent.mkdir(parents=True, exist_ok=True)
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


def load_settings(path: Path | str = SETTINGS_PATH) -> dict:
    settings_path = Path(path)
    if not settings_path.exists():
        return {}
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(settings: dict, path: Path | str = SETTINGS_PATH) -> Path:
    settings_path = Path(path)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        settings_path.chmod(0o600)
    except OSError:
        pass
    return settings_path


def load_provider(path: Path | str = SETTINGS_PATH) -> str:
    value = str(load_settings(path).get("provider", "")).strip().lower()
    return value if value in VALID_PROVIDERS else DEFAULT_PROVIDER


def save_provider(provider: str, path: Path | str = SETTINGS_PATH) -> Path:
    normalized = provider.strip().lower()
    if normalized not in VALID_PROVIDERS:
        normalized = DEFAULT_PROVIDER
    settings = load_settings(path)
    settings["provider"] = normalized
    return save_settings(settings, path)


def load_gemini_model(path: Path | str = SETTINGS_PATH) -> str:
    value = str(load_settings(path).get("gemini_model", "")).strip()
    return value or DEFAULT_GEMINI_MODEL


def save_gemini_model(model: str, path: Path | str = SETTINGS_PATH) -> Path:
    settings = load_settings(path)
    clean_model = model.strip() or DEFAULT_GEMINI_MODEL
    settings["gemini_model"] = clean_model
    return save_settings(settings, path)


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
