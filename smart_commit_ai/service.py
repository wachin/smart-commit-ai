"""Application service layer used by both GUI and tests."""

from __future__ import annotations

from dataclasses import dataclass

from .commit_message import CommitMessage
from .examples import ExampleStore
from .gemini_client import GeminiCommitGenerator, GeminiError
from .local_generator import LocalCommitGenerator


@dataclass(frozen=True)
class GenerationResult:
    message: CommitMessage
    command: str
    saved_path: str | None
    warning: str | None = None


class SmartCommitService:
    def __init__(self, store: ExampleStore | None = None) -> None:
        self.store = store or ExampleStore()
        self.local = LocalCommitGenerator()
        self.gemini = GeminiCommitGenerator(self.store)

    def generate(
        self,
        original_text: str,
        *,
        provider: str = "auto",
        api_key: str | None = None,
        save: bool = True,
    ) -> GenerationResult:
        if not original_text.strip():
            raise ValueError("Paste a Codex summary before creating a commit message.")

        warning = None
        if provider == "local":
            message = self.local.generate(original_text)
        elif provider == "gemini":
            message = self.gemini.generate(original_text, api_key=api_key)
        else:
            try:
                message = self.gemini.generate(original_text, api_key=api_key)
            except GeminiError as exc:
                warning = f"Gemini unavailable; used local generator. {exc}"
                message = self.local.generate(original_text)

        saved_path = None
        if save and message.source == "gemini":
            path = self.store.save(
                original_text,
                message,
                source=message.source,
                model=message.model,
            )
            saved_path = str(path)

        return GenerationResult(
            message=message,
            command=message.command(),
            saved_path=saved_path,
            warning=warning,
        )
