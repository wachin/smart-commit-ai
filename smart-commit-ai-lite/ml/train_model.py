"""Train the optional offline sklearn Conventional Commit classifier."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import joblib

from ml.artifact_policy import (
    ARTIFACT_POLICY_VERSION,
    OFFICIAL_METADATA_PATH,
    OFFICIAL_MODEL_PATH,
    OFFICIAL_VECTORIZER_PATH,
)
from ml.dataset_loader import (
    EntryValidationError,
    as_training_arrays,
    load_training_examples,
    summarize_label_balance,
    validate_entry_files,
)
from utils.language import detect_language
from utils.preprocessing import preprocess_text


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = OFFICIAL_MODEL_PATH
DEFAULT_VECTORIZER_PATH = OFFICIAL_VECTORIZER_PATH
DEFAULT_METADATA_PATH = OFFICIAL_METADATA_PATH
MODEL_FORMAT_VERSION = 1


def format_entry_validation_errors(errors: list[EntryValidationError]) -> str:
    lines = ["Training entry validation failed:"]
    for error in errors[:10]:
        lines.append(f"- {error.path}: {error.message}")
    if len(errors) > 10:
        lines.append(f"- ... and {len(errors) - 10} more error(s)")
    return "\n".join(lines)


def build_metadata(
    example_count: int,
    label_counts: dict[str, int],
    model_path: Path,
    vectorizer_path: Path,
    label_balance: dict | None = None,
    seed_examples_included: bool = True,
) -> dict:
    return {
        "format_version": MODEL_FORMAT_VERSION,
        "artifact_policy_version": ARTIFACT_POLICY_VERSION,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "training_examples": example_count,
        "labels": dict(sorted(label_counts.items())),
        "label_balance": label_balance or {},
        "seed_examples_included": seed_examples_included,
        "model_path": str(model_path),
        "vectorizer_path": str(vectorizer_path),
        "trainer": "TfidfVectorizer(ngram_range=(1, 2)) + LinearSVC(class_weight='balanced')",
    }


def train(
    model_path: Path = DEFAULT_MODEL_PATH,
    vectorizer_path: Path = DEFAULT_VECTORIZER_PATH,
    metadata_path: Path = DEFAULT_METADATA_PATH,
    include_seed: bool = True,
    entries_path: Path | None = None,
) -> dict:
    entry_errors = validate_entry_files(entries_path)
    if entry_errors:
        raise RuntimeError(format_entry_validation_errors(entry_errors))

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.svm import LinearSVC
    except ImportError as exc:
        raise RuntimeError("Install Debian package python3-sklearn to train the ML model.") from exc

    examples = load_training_examples(include_seed=include_seed)
    texts, labels = as_training_arrays(examples)
    processed = [preprocess_text(text, detect_language(text)) for text in texts]
    pairs = [(text, label) for text, label in zip(processed, labels) if text]
    if len(pairs) < 6:
        raise RuntimeError("Not enough training examples to train the classifier.")

    processed, labels = zip(*pairs)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, lowercase=False)
    features = vectorizer.fit_transform(processed)
    model = LinearSVC(class_weight="balanced", random_state=0)
    model.fit(features, labels)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    counts = Counter(labels)
    metadata = build_metadata(
        len(labels),
        dict(counts),
        model_path,
        vectorizer_path,
        summarize_label_balance(examples),
        seed_examples_included=include_seed,
    )
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return metadata | {"metadata_path": str(metadata_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Train the offline sklearn commit type classifier.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--vectorizer", type=Path, default=DEFAULT_VECTORIZER_PATH)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA_PATH)
    parser.add_argument(
        "--no-seed",
        action="store_true",
        help="Train only from repository datasets, without built-in seed examples.",
    )
    args = parser.parse_args()

    stats = train(args.model, args.vectorizer, args.metadata, include_seed=not args.no_seed)
    print(f"Trained commit model with {stats['training_examples']} examples")
    print(f"Labels: {stats['labels']}")
    print(f"Seed examples included: {stats['seed_examples_included']}")
    if stats.get("label_balance"):
        print(f"Label balance: {stats['label_balance']}")
    print(f"Model: {stats['model_path']}")
    print(f"Vectorizer: {stats['vectorizer_path']}")
    print(f"Metadata: {stats['metadata_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
