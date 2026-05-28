"""Commit message data model and shell command formatting."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
import shlex
import textwrap


MAX_HEADER_LENGTH = 50
MAX_BODY_LINE_LENGTH = 72
CONVENTIONAL_TYPES = {
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "test",
    "chore",
    "ci",
    "perf",
}


@dataclass(frozen=True)
class CommitMessage:
    """A Conventional Commit message with shell-command rendering."""

    subject: str
    body_lines: list[str] = field(default_factory=list)
    source: str = "local"
    model: str | None = None

    def normalized(self) -> "CommitMessage":
        subject = normalize_subject(self.subject)
        body_lines = [normalize_body_line(line) for line in self.body_lines if line.strip()]
        return CommitMessage(subject=subject, body_lines=body_lines, source=self.source, model=self.model)

    def command(self) -> str:
        return format_git_commit_command(self.subject, self.body_lines)


def normalize_subject(subject: str) -> str:
    """Normalize a generated subject while preserving Conventional Commit shape."""

    value = " ".join(subject.strip().split())
    if not value:
        return "chore(commit): update project changes"

    match = re.match(r"^([a-z]+)(?:\(([a-z0-9._-]+)\))?:\s*(.+)$", value)
    if not match:
        value = f"chore(commit): {value[0].lower()}{value[1:]}"
        match = re.match(r"^([a-z]+)(?:\(([a-z0-9._-]+)\))?:\s*(.+)$", value)

    if not match:
        return trim_to_limit(value, MAX_HEADER_LENGTH)

    commit_type, scope, description = match.groups()
    commit_type = commit_type if commit_type in CONVENTIONAL_TYPES else "chore"
    scope = clean_scope(scope or "commit")
    description = lowercase_first(description.strip().rstrip("."))
    description = compact_subject_words(description)

    prefix = f"{commit_type}({scope}): "
    available = MAX_HEADER_LENGTH - len(prefix)
    if available < 12:
        scope = "core"
        prefix = f"{commit_type}({scope}): "
        available = MAX_HEADER_LENGTH - len(prefix)

    return prefix + trim_to_limit(description, available)


def normalize_body_line(line: str) -> str:
    value = " ".join(line.strip().split())
    if not value:
        return value
    if not value.startswith("- "):
        value = f"- {value.lstrip('-').strip()}"
    value = compact_body_words(value)
    return trim_to_limit(value, MAX_BODY_LINE_LENGTH)


def clean_scope(scope: str) -> str:
    value = re.sub(r"[^a-z0-9._-]+", "-", scope.lower()).strip("-")
    return value or "commit"


def lowercase_first(value: str) -> str:
    if not value:
        return value
    return value[0].lower() + value[1:]


def trim_to_limit(value: str, limit: int) -> str:
    value = " ".join(value.strip().split())
    if len(value) <= limit:
        return value
    truncated = textwrap.shorten(value, width=limit, placeholder="")
    return truncated.strip(" -,:;")


def compact_subject_words(value: str) -> str:
    replacements = {
        "authentication": "auth",
        "authorization": "authz",
        "documentation": "docs",
        "configuration": "config",
        "implementation": "impl",
        "internationalization": "i18n",
        "accessibility": "a11y",
        "performance": "perf",
        "application": "app",
        "database": "db",
        "synchronization": "sync",
        "Standard MIDI File": "SMF",
        "standard MIDI file": "SMF",
        "not supported": "unsupported",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def compact_body_words(value: str) -> str:
    replacements = {
        "Standard MIDI File": "SMF",
        "standard MIDI file": "SMF",
        "not supported": "unsupported",
        "documentation": "docs",
        "configuration": "config",
        "synchronization": "sync",
        "application": "app",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def shell_double_quote(value: str) -> str:
    """Return a shell-safe double-quoted string for git -m arguments."""

    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("$", "\\$")
        .replace("`", "\\`")
    )
    return f'"{escaped}"'


def format_git_commit_command(subject: str, body_lines: list[str] | tuple[str, ...]) -> str:
    message = CommitMessage(subject=subject, body_lines=list(body_lines)).normalized()
    command_lines = [f"git commit -m {shell_double_quote(message.subject)}"]
    for body_line in message.body_lines:
        command_lines.append(f"  -m {shell_double_quote(body_line)}")
    return " \\\n".join(command_lines)


def parse_git_commit_command(command: str) -> CommitMessage | None:
    """Best-effort parser for existing dataset commands."""

    for candidate in command_candidates(command):
        message = parse_git_commit_args(candidate)
        if message is not None:
            return message.normalized()

    matches = quoted_message_matches(command)
    if not matches:
        return None

    decoded = [decode_shell_quoted(item) for item in matches]
    return CommitMessage(subject=decoded[0], body_lines=decoded[1:]).normalized()


def command_candidates(command: str) -> list[str]:
    normalized = normalize_shell_command_text(command)
    candidates = [normalized]

    for match in re.finditer(r"```(?:bash|sh|shell)?\s*(.*?)```", command, flags=re.I | re.S):
        candidates.append(normalize_shell_command_text(match.group(1)))

    git_commit_index = normalized.find("git commit")
    if git_commit_index != -1:
        candidates.append(normalized[git_commit_index:])

    unique: list[str] = []
    for candidate in candidates:
        candidate = candidate.strip("` \n\t")
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def normalize_shell_command_text(command: str) -> str:
    value = command.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    value = re.sub(r"```(?:bash|sh|shell)?", "", value, flags=re.I)
    value = value.replace("```", "")
    value = re.sub(r"\\\s*\n\s*", " ", value)
    return value.strip()


def parse_git_commit_args(command: str) -> CommitMessage | None:
    try:
        args = shlex.split(command, posix=True)
    except ValueError:
        return None

    if len(args) < 4:
        return None

    try:
        git_index = next(
            index
            for index in range(len(args) - 1)
            if args[index] == "git" and args[index + 1] == "commit"
        )
    except StopIteration:
        return None

    messages: list[str] = []
    index = git_index + 2
    while index < len(args):
        arg = args[index]
        if arg in {"-m", "--message"} and index + 1 < len(args):
            messages.append(decode_shell_quoted(args[index + 1]))
            index += 2
            continue
        if arg.startswith("--message="):
            messages.append(decode_shell_quoted(arg.split("=", 1)[1]))
        index += 1

    if not messages:
        return None
    return CommitMessage(subject=messages[0], body_lines=messages[1:])


def quoted_message_matches(command: str) -> list[str]:
    normalized = normalize_shell_command_text(command)
    patterns = [
        r"-m\s+\"((?:[^\"\\]|\\.)*)\"",
        r"-m\s+'((?:[^'\\]|\\.)*)'",
    ]
    matches: list[str] = []
    for pattern in patterns:
        matches.extend(re.findall(pattern, normalized))
    return matches


def decode_shell_quoted(value: str) -> str:
    return decode_shell_double_quoted(value)


def decode_shell_double_quoted(value: str) -> str:
    chars: list[str] = []
    index = 0
    while index < len(value):
        char = value[index]
        if char == "\\" and index + 1 < len(value):
            next_char = value[index + 1]
            if next_char in {'"', "\\", "$", "`"}:
                chars.append(next_char)
                index += 2
                continue
        chars.append(char)
        index += 1
    return "".join(chars)
