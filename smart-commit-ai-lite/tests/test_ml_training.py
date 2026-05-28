import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from ml.artifact_policy import ARTIFACT_POLICY_VERSION, is_official_artifact, official_artifact_paths
from ml.dataset_loader import (
    SUPPORTED_TYPES,
    TrainingExample,
    label_from_subject,
    load_training_examples,
    summarize_label_balance,
    validate_entry_files,
)
from ml.train_model import MODEL_FORMAT_VERSION, build_metadata, train


class MLTrainingTests(unittest.TestCase):
    def test_dataset_loader_reuses_local_examples_and_seed_labels(self):
        examples = load_training_examples(include_seed=True)
        labels = {example.label for example in examples}
        dataset_only_labels = {example.label for example in load_training_examples(include_seed=False)}

        self.assertGreaterEqual(len(examples), 12)
        self.assertTrue(SUPPORTED_TYPES.issubset(labels))
        self.assertTrue(SUPPORTED_TYPES.issubset(dataset_only_labels))
        self.assertEqual(label_from_subject("feat(ui): add control"), "feat")
        self.assertEqual(label_from_subject("docs: update readme"), "docs")

    def test_build_metadata_describes_training_artifacts(self):
        metadata = build_metadata(
            example_count=12,
            label_counts={"feat": 8, "fix": 4},
            model_path=Path("ml/commit_model.pkl"),
            vectorizer_path=Path("ml/vectorizer.pkl"),
            label_balance={"largest_label": "feat", "imbalance_ratio": 2.0},
            seed_examples_included=False,
        )

        self.assertEqual(metadata["format_version"], MODEL_FORMAT_VERSION)
        self.assertEqual(metadata["artifact_policy_version"], ARTIFACT_POLICY_VERSION)
        self.assertEqual(metadata["training_examples"], 12)
        self.assertEqual(metadata["labels"], {"feat": 8, "fix": 4})
        self.assertEqual(metadata["label_balance"]["largest_label"], "feat")
        self.assertEqual(metadata["label_balance"]["imbalance_ratio"], 2.0)
        self.assertFalse(metadata["seed_examples_included"])
        self.assertEqual(metadata["model_path"], "ml/commit_model.pkl")
        self.assertEqual(metadata["vectorizer_path"], "ml/vectorizer.pkl")
        self.assertIn("LinearSVC", metadata["trainer"])

    def test_summarize_label_balance_reports_dataset_skew(self):
        examples = [
            TrainingExample("add feature", "feat", "test"),
            TrainingExample("add another feature", "feat", "test"),
            TrainingExample("fix crash", "fix", "test"),
            TrainingExample("update docs", "docs", "test"),
        ]

        summary = summarize_label_balance(examples)

        self.assertEqual(summary["total"], 4)
        self.assertEqual(summary["counts"]["feat"], 2)
        self.assertEqual(summary["counts"]["fix"], 1)
        self.assertEqual(summary["counts"]["chore"], 0)
        self.assertEqual(summary["largest_label"], "feat")
        self.assertEqual(summary["imbalance_ratio"], 2.0)

    def test_seed_examples_are_optional_training_support(self):
        without_seed = load_training_examples(include_seed=False)
        with_seed = load_training_examples(include_seed=True)

        self.assertGreaterEqual(len(with_seed), len(without_seed))
        self.assertFalse(any(example.source == "built-in-seed" for example in without_seed))
        self.assertTrue(any(example.source == "built-in-seed" for example in with_seed))

    def test_user_supplied_training_examples_are_loaded(self):
        examples = load_training_examples(include_seed=False)
        texts = [example.text.lower() for example in examples]
        labels = {example.label for example in examples}

        self.assertTrue(any("dropzonewidget" in text for text in texts))
        self.assertTrue(any("confidence gate" in text for text in texts))
        self.assertTrue(any("gtk-platformtheme" in text or "gtk theme" in text for text in texts))
        self.assertTrue({"feat", "docs", "test"}.issubset(labels))

    def test_entry_files_validate_for_training_use(self):
        errors = validate_entry_files()

        self.assertEqual(errors, [])

    def test_entry_file_validation_rejects_duplicate_titles(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            entry = {
                "title": "Duplicate title",
                "original_text": "Added a useful feature.",
                "expected_subject": "feat(app): add useful feature",
                "expected_body_lines": ["- Add useful feature"],
            }
            (path / "one.json").write_text(json.dumps(entry), encoding="utf-8")
            (path / "two.json").write_text(
                json.dumps(entry | {"original_text": "Added another useful feature."}),
                encoding="utf-8",
            )

            errors = validate_entry_files(path)

        self.assertTrue(any("duplicate title" in error.message for error in errors))

    def test_entry_file_validation_rejects_duplicate_original_texts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            entry = {
                "title": "First title",
                "original_text": "Added a useful feature.",
                "expected_subject": "feat(app): add useful feature",
                "expected_body_lines": ["- Add useful feature"],
            }
            (path / "one.json").write_text(json.dumps(entry), encoding="utf-8")
            (path / "two.json").write_text(
                json.dumps(entry | {"title": "Second title"}),
                encoding="utf-8",
            )

            errors = validate_entry_files(path)

        self.assertTrue(any("duplicate original_text" in error.message for error in errors))

    def test_training_stops_before_model_write_when_entries_are_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "broken.json").write_text(
                json.dumps(
                    {
                        "title": "Broken training entry",
                        "original_text": "",
                        "expected_subject": "feature(app): invalid type",
                        "expected_body_lines": ["- Broken entry"],
                    }
                ),
                encoding="utf-8",
            )
            model_path = path / "commit_model.pkl"

            with self.assertRaisesRegex(RuntimeError, "Training entry validation failed"):
                train(
                    model_path=model_path,
                    vectorizer_path=path / "vectorizer.pkl",
                    metadata_path=path / "model_metadata.json",
                    entries_path=path,
                )

            self.assertFalse(model_path.exists())

    def test_official_artifact_policy_tracks_distributed_files(self):
        paths = official_artifact_paths()

        self.assertEqual(len(paths), 3)
        self.assertTrue(is_official_artifact("ml/commit_model.pkl"))
        self.assertTrue(is_official_artifact("ml/vectorizer.pkl"))
        self.assertTrue(is_official_artifact("ml/model_metadata.json"))
        self.assertFalse(is_official_artifact("ml/local_experiment.pkl"))

    @unittest.skipUnless(importlib.util.find_spec("sklearn"), "python3-sklearn is not installed")
    def test_training_writes_model_and_vectorizer(self):
        with tempfile.TemporaryDirectory() as tmp:
            model_path = Path(tmp) / "commit_model.pkl"
            vectorizer_path = Path(tmp) / "vectorizer.pkl"
            metadata_path = Path(tmp) / "model_metadata.json"
            stats = train(
                model_path=model_path,
                vectorizer_path=vectorizer_path,
                metadata_path=metadata_path,
            )

            self.assertTrue(model_path.exists())
            self.assertTrue(vectorizer_path.exists())
            self.assertTrue(metadata_path.exists())
            self.assertGreaterEqual(stats["training_examples"], 12)


if __name__ == "__main__":
    unittest.main()
