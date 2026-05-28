"""Lightweight offline sklearn Conventional Commit predictor package."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ml.predictor import PredictionResult, SklearnCommitPredictor, predict_commit_type

__all__ = [
    "PredictionResult",
    "SklearnCommitPredictor",
    "predict_commit_type",
]


def __getattr__(name: str):
    if name in __all__:
        from ml import predictor

        return getattr(predictor, name)
    raise AttributeError(f"module 'ml' has no attribute {name!r}")
