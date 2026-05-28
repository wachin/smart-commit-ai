import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import patch

import ml
from ml.predictor import SklearnCommitPredictor, main, prediction_payload
from ml.train_model import MODEL_FORMAT_VERSION


class SklearnPredictorTests(unittest.TestCase):
    def test_package_exports_common_predictor_api(self):
        self.assertIs(ml.SklearnCommitPredictor, SklearnCommitPredictor)
        self.assertTrue(callable(ml.predict_commit_type))

    def test_prediction_payload_handles_missing_prediction(self):
        self.assertEqual(
            prediction_payload(None),
            {
                "commit_type": None,
                "confidence": None,
                "language": None,
                "engine": "sklearn",
            },
        )

    def test_distributed_model_predicts_core_prompt_examples(self):
        predictor = SklearnCommitPredictor()
        status = predictor.status(try_load=True)

        self.assertTrue(status.ready, status.message)
        cases = [
            ("fixed crash when opening audio files", "fix"),
            ("added MIDI karaoke support", "feat"),
            ("updated installation instructions", "docs"),
            ("cleaned deprecated code", "refactor"),
            ("added regression tests for predictor", "test"),
            ("generated official local ML model artifacts", "feat"),
        ]

        for text, expected_type in cases:
            with self.subTest(text=text):
                prediction = predictor.predict(text)

                self.assertIsNotNone(prediction)
                self.assertEqual(prediction.commit_type, expected_type)

    def test_predictor_cli_prints_json_prediction(self):
        with patch("sys.argv", ["ml.predictor", "--json", "fixed crash when opening audio files"]):
            with patch("builtins.print") as mocked_print:
                exit_code = main()

        self.assertEqual(exit_code, 0)
        payload = json.loads(mocked_print.call_args.args[0])
        self.assertEqual(payload["commit_type"], "fix")
        self.assertEqual(payload["engine"], "sklearn")

    def test_missing_model_returns_none_instead_of_failing(self):
        with tempfile.TemporaryDirectory() as tmp:
            predictor = SklearnCommitPredictor(
                model_path=Path(tmp) / "missing-model.pkl",
                vectorizer_path=Path(tmp) / "missing-vectorizer.pkl",
                metadata_path=Path(tmp) / "missing-metadata.json",
            )

            self.assertFalse(predictor.available)
            self.assertIsNone(predictor.predict("fixed crash when opening audio files"))

    def test_status_reports_missing_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            predictor = SklearnCommitPredictor(
                model_path=Path(tmp) / "missing-model.pkl",
                vectorizer_path=Path(tmp) / "missing-vectorizer.pkl",
                metadata_path=Path(tmp) / "missing-metadata.json",
            )

            status = predictor.status()

            self.assertFalse(status.ready)
            self.assertFalse(status.model_exists)
            self.assertFalse(status.vectorizer_exists)
            self.assertFalse(status.metadata_exists)
            self.assertIsNone(status.metadata)
            self.assertEqual(status.message, "missing model and vectorizer artifacts")

    def test_load_metadata_accepts_current_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata_path = Path(tmp) / "model_metadata.json"
            metadata_path.write_text(
                json.dumps(
                    {
                        "format_version": MODEL_FORMAT_VERSION,
                        "training_examples": 12,
                        "labels": {"feat": 8, "fix": 4},
                        "model_path": "ml/commit_model.pkl",
                        "vectorizer_path": "ml/vectorizer.pkl",
                        "trainer": "test trainer",
                    }
                ),
                encoding="utf-8",
            )
            predictor = SklearnCommitPredictor(metadata_path=metadata_path)

            metadata = predictor.load_metadata()

            self.assertIsNotNone(metadata)
            self.assertEqual(metadata["training_examples"], 12)

    def test_load_metadata_rejects_invalid_label_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata_path = Path(tmp) / "model_metadata.json"
            metadata_path.write_text(
                json.dumps(
                    {
                        "format_version": MODEL_FORMAT_VERSION,
                        "training_examples": 12,
                        "labels": {"feat": 8, "feature": 4},
                        "model_path": "ml/commit_model.pkl",
                        "vectorizer_path": "ml/vectorizer.pkl",
                        "trainer": "test trainer",
                    }
                ),
                encoding="utf-8",
            )
            predictor = SklearnCommitPredictor(metadata_path=metadata_path)

            metadata = predictor.load_metadata()

            self.assertIsNone(metadata)
            self.assertIn("unsupported type", predictor._metadata_error)

    def test_load_metadata_rejects_mismatched_training_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata_path = Path(tmp) / "model_metadata.json"
            metadata_path.write_text(
                json.dumps(
                    {
                        "format_version": MODEL_FORMAT_VERSION,
                        "training_examples": 12,
                        "labels": {"feat": 8, "fix": 3},
                        "model_path": "ml/commit_model.pkl",
                        "vectorizer_path": "ml/vectorizer.pkl",
                        "trainer": "test trainer",
                    }
                ),
                encoding="utf-8",
            )
            predictor = SklearnCommitPredictor(metadata_path=metadata_path)

            metadata = predictor.load_metadata()

            self.assertIsNone(metadata)
            self.assertIn("label counts", predictor._metadata_error)

    def test_status_reports_invalid_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            model_path = Path(tmp) / "commit_model.pkl"
            vectorizer_path = Path(tmp) / "vectorizer.pkl"
            metadata_path = Path(tmp) / "model_metadata.json"
            model_path.write_text("placeholder", encoding="utf-8")
            vectorizer_path.write_text("placeholder", encoding="utf-8")
            metadata_path.write_text("{}", encoding="utf-8")
            predictor = SklearnCommitPredictor(
                model_path=model_path,
                vectorizer_path=vectorizer_path,
                metadata_path=metadata_path,
            )

            status = predictor.status()

            self.assertFalse(status.ready)
            self.assertTrue(status.metadata_exists)
            self.assertIsNone(status.metadata)
            self.assertIn("model metadata is invalid", status.message)


if __name__ == "__main__":
    unittest.main()
