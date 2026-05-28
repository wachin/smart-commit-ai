import unittest

from ml.dataset_loader import TrainingExample
from ml.evaluate_model import evaluate_predictor
from ml.interfaces import CommitTypePredictor
from ml.predictor import PredictionResult


class StubPredictor:
    def __init__(self, labels):
        self.labels = labels

    def predict(self, _text, language=None):
        if not self.labels:
            return None
        label = self.labels.pop(0)
        if label is None:
            return None
        return PredictionResult(label, confidence=0.9, language=language or "en")


class MLEvaluationTests(unittest.TestCase):
    def test_evaluate_predictor_reports_accuracy_and_skips(self):
        examples = [
            TrainingExample("add feature", "feat", "test"),
            TrainingExample("fix crash", "fix", "test"),
            TrainingExample("update docs", "docs", "test"),
        ]
        predictor = StubPredictor(["feat", "docs", None])

        self.assertIsInstance(predictor, CommitTypePredictor)
        result = evaluate_predictor(examples, predictor)

        self.assertEqual(result.total_examples, 3)
        self.assertEqual(result.evaluated_examples, 2)
        self.assertEqual(result.skipped_examples, 1)
        self.assertEqual(result.correct_predictions, 1)
        self.assertEqual(result.accuracy, 0.5)
        self.assertEqual(result.expected_labels, {"docs": 1, "feat": 1, "fix": 1})
        self.assertEqual(result.predicted_labels, {"docs": 1, "feat": 1})
        self.assertEqual(
            result.misclassifications,
            [
                {
                    "source": "test",
                    "text": "fix crash",
                    "expected": "fix",
                    "predicted": "docs",
                    "confidence": 0.9,
                }
            ],
        )
        self.assertEqual(
            result.label_metrics,
            {
                "docs": {"expected": 1, "evaluated": 0, "skipped": 1, "correct": 0, "accuracy": None},
                "feat": {"expected": 1, "evaluated": 1, "skipped": 0, "correct": 1, "accuracy": 1.0},
                "fix": {"expected": 1, "evaluated": 1, "skipped": 0, "correct": 0, "accuracy": 0.0},
            },
        )

    def test_evaluate_predictor_reports_empty_misclassifications_when_all_correct(self):
        examples = [
            TrainingExample("add feature", "feat", "test"),
            TrainingExample("fix crash", "fix", "test"),
        ]
        predictor = StubPredictor(["feat", "fix"])

        result = evaluate_predictor(examples, predictor)

        self.assertEqual(result.accuracy, 1.0)
        self.assertEqual(result.misclassifications, [])


if __name__ == "__main__":
    unittest.main()
