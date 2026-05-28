"""Versioned policy for local and distributed ML artifacts."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_POLICY_VERSION = 1

OFFICIAL_MODEL_PATH = ROOT / "ml" / "commit_model.pkl"
OFFICIAL_VECTORIZER_PATH = ROOT / "ml" / "vectorizer.pkl"
OFFICIAL_METADATA_PATH = ROOT / "ml" / "model_metadata.json"

OFFICIAL_ARTIFACTS = (
    OFFICIAL_MODEL_PATH,
    OFFICIAL_VECTORIZER_PATH,
    OFFICIAL_METADATA_PATH,
)

LOCAL_EXPERIMENT_GLOB = "ml/*.pkl"


def official_artifact_paths() -> tuple[Path, ...]:
    return OFFICIAL_ARTIFACTS


def is_official_artifact(path: Path | str) -> bool:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve() in {artifact.resolve() for artifact in OFFICIAL_ARTIFACTS}
