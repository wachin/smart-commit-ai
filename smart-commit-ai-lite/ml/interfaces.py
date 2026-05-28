"""Shared lightweight interfaces for commit prediction engines."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class CommitPrediction(Protocol):
    """Result shape needed by callers that consume predicted commit types."""

    commit_type: str


@runtime_checkable
class CommitTypePredictor(Protocol):
    """Minimal interface shared by sklearn and future local predictors."""

    def predict(self, text: str, language: str | None = None) -> CommitPrediction | None:
        ...
