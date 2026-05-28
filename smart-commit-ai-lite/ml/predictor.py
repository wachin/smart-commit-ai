"""Local sklearn predictor and artifact validation."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib

from ml.dataset_loader import SUPPORTED_TYPES
from ml.train_model import MODEL_FORMAT_VERSION
from utils.language import detect_language
from utils.preprocessing import preprocess_text


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = ROOT / "ml" / "commit_model.pkl"
DEFAULT_VECTORIZER_PATH = ROOT / "ml" / "vectorizer.pkl"
DEFAULT_METADATA_PATH = ROOT / "ml" / "model_metadata.json"


@dataclass(frozen=True)
class PredictionResult:
    commit_type: str
    confidence: float | None
    language: str
    engine: str = "sklearn"


@dataclass(frozen=True)
class ModelStatus:
    model_path: Path
    vectorizer_path: Path
    metadata_path: Path
    model_exists: bool
    vectorizer_exists: bool
    metadata_exists: bool
    metadata: dict[str, Any] | None
    loadable: bool
    message: str

    @property
    def ready(self) -> bool:
        return (
            self.model_exists
            and self.vectorizer_exists
            and self.metadata_exists
            and self.metadata is not None
            and self.loadable
        )


class SklearnCommitPredictor:
    """Load local joblib artifacts and predict Conventional Commit types."""

    def __init__(
        self,
        model_path: Path | str = DEFAULT_MODEL_PATH,
        vectorizer_path: Path | str = DEFAULT_VECTORIZER_PATH,
        metadata_path: Path | str = DEFAULT_METADATA_PATH,
    ) -> None:
        self.model_path = Path(model_path)
        self.vectorizer_path = Path(vectorizer_path)
        self.metadata_path = Path(metadata_path)
        self._model: Any | None = None
        self._vectorizer: Any | None = None
        self._load_error: str | None = None
        self._metadata_error: str | None = None

    @property
    def available(self) -> bool:
        return self.model_path.exists() and self.vectorizer_path.exists()

    def load(self) -> bool:
        if self._model is not None and self._vectorizer is not None:
            return True
        if not self.available:
            self._load_error = "model or vectorizer artifact is missing"
            return False
        try:
            self._model = joblib.load(self.model_path)
            self._vectorizer = joblib.load(self.vectorizer_path)
            self._load_error = None
            return True
        except Exception as exc:
            self._model = None
            self._vectorizer = None
            self._load_error = str(exc)
            return False

    def load_metadata(self) -> dict[str, Any] | None:
        if not self.metadata_path.exists():
            self._metadata_error = "metadata artifact is missing"
            return None
        try:
            metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        except Exception as exc:
            self._metadata_error = str(exc)
            return None

        required_fields = {
            "format_version",
            "training_examples",
            "labels",
            "model_path",
            "vectorizer_path",
            "trainer",
        }
        missing_fields = sorted(required_fields - set(metadata))
        if missing_fields:
            self._metadata_error = "metadata missing fields: " + ", ".join(missing_fields)
            return None
        if metadata.get("format_version") != MODEL_FORMAT_VERSION:
            self._metadata_error = (
                f"unsupported metadata format version: {metadata.get('format_version')}"
            )
            return None
        label_error = self._validate_metadata_labels(metadata)
        if label_error:
            self._metadata_error = label_error
            return None

        self._metadata_error = None
        return metadata

    def _validate_metadata_labels(self, metadata: dict[str, Any]) -> str | None:
        labels = metadata.get("labels")
        training_examples = metadata.get("training_examples")
        if not isinstance(labels, dict) or not labels:
            return "metadata labels must be a non-empty object"
        if not isinstance(training_examples, int) or training_examples <= 0:
            return "metadata training_examples must be a positive integer"

        for label, count in labels.items():
            if label not in SUPPORTED_TYPES:
                return f"metadata labels include unsupported type: {label}"
            if not isinstance(count, int) or count < 0:
                return f"metadata label count must be a non-negative integer: {label}"

        if sum(labels.values()) != training_examples:
            return "metadata label counts must match training_examples"
        return None

    def status(self, try_load: bool = False) -> ModelStatus:
        model_exists = self.model_path.exists()
        vectorizer_exists = self.vectorizer_path.exists()
        metadata_exists = self.metadata_path.exists()
        metadata = self.load_metadata() if metadata_exists else None
        loadable = False

        if model_exists and vectorizer_exists:
            loadable = self.load() if try_load else True

        if not model_exists and not vectorizer_exists:
            message = "missing model and vectorizer artifacts"
        elif not model_exists:
            message = "missing model artifact"
        elif not vectorizer_exists:
            message = "missing vectorizer artifact"
        elif not metadata_exists:
            message = "model artifacts are ready; metadata is missing"
        elif metadata is None:
            message = f"model metadata is invalid: {self._metadata_error or 'unknown error'}"
        elif loadable:
            message = "model artifacts are ready"
        else:
            message = f"model artifacts could not be loaded: {self._load_error or 'unknown error'}"

        return ModelStatus(
            model_path=self.model_path,
            vectorizer_path=self.vectorizer_path,
            metadata_path=self.metadata_path,
            model_exists=model_exists,
            vectorizer_exists=vectorizer_exists,
            metadata_exists=metadata_exists,
            metadata=metadata,
            loadable=loadable,
            message=message,
        )

    def predict(self, text: str, language: str | None = None) -> PredictionResult | None:
        if not text or not text.strip() or not self.load():
            return None

        language = language if language in {"en", "es"} else detect_language(text)
        processed = preprocess_text(text, language)
        if not processed:
            return None

        try:
            features = self._vectorizer.transform([processed])
            label = str(self._model.predict(features)[0])
            if label not in SUPPORTED_TYPES:
                return None
            return PredictionResult(label, self._confidence(features, label), language)
        except Exception:
            return None

    def _confidence(self, features: Any, label: str) -> float | None:
        """Approximate confidence for LinearSVC using normalized margins."""
        if self._model is None or not hasattr(self._model, "decision_function"):
            return None
        try:
            scores = self._model.decision_function(features)
            classes = list(getattr(self._model, "classes_", []))
            if not classes:
                return None
            if len(classes) == 2 and not hasattr(scores[0], "__iter__"):
                score = float(scores[0])
                raw = score if classes[1] == label else -score
                return round(1.0 / (1.0 + math.exp(-raw)), 3)
            row = [float(value) for value in scores[0]]
            max_score = max(row)
            exps = [math.exp(min(50.0, value - max_score)) for value in row]
            total = sum(exps)
            if total <= 0:
                return None
            index = classes.index(label)
            return round(exps[index] / total, 3)
        except Exception:
            return None


def predict_commit_type(text: str, language: str | None = None) -> PredictionResult | None:
    return SklearnCommitPredictor().predict(text, language)


def prediction_payload(prediction: PredictionResult | None) -> dict[str, Any]:
    if prediction is None:
        return {
            "commit_type": None,
            "confidence": None,
            "language": None,
            "engine": "sklearn",
        }
    return {
        "commit_type": prediction.commit_type,
        "confidence": prediction.confidence,
        "language": prediction.language,
        "engine": prediction.engine,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Predict a Conventional Commit type offline.")
    parser.add_argument("text", nargs="*", help="Change summary text to classify.")
    parser.add_argument("--language", choices=("en", "es"), help="Force input language.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--status", action="store_true", help="Print model artifact status and exit.")
    args = parser.parse_args()

    predictor = SklearnCommitPredictor()
    if args.status:
        status = predictor.status(try_load=True)
        if args.json:
            print(json.dumps({"ready": status.ready, "message": status.message}, indent=2, sort_keys=True))
        else:
            print(f"Ready: {status.ready}")
            print(f"Status: {status.message}")
        return 0 if status.ready else 1

    text = " ".join(args.text).strip()
    prediction = predictor.predict(text, args.language)
    if args.json:
        print(json.dumps(prediction_payload(prediction), indent=2, sort_keys=True))
    elif prediction is None:
        print("No prediction")
        return 1
    else:
        confidence = "n/a" if prediction.confidence is None else prediction.confidence
        print(f"{prediction.commit_type} (confidence={confidence}, language={prediction.language})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
