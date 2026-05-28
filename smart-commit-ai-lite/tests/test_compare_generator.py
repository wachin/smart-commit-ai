import unittest

from commit_examples_data.compare_generator import MAX_BODY_LINES, compare_entry, parse_commit_header


class StubGenerator:
    def __init__(self):
        self.nlp_engine = self

    def analyze_with_nltk(self, _text):
        return "add", "feature", "en"

    def detect_scope(self, _text):
        return "app"

    def select_commit_type(self, _text, _verb, _obj):
        return "feat"

    def format_subject(self, verb, obj, _language):
        return f"{verb} {obj}"

    def clean_input(self, text):
        return text

    def generate_body_lines(self, _text, _language):
        return [f"- Body {index}" for index in range(1, MAX_BODY_LINES + 1)]


class CompareGeneratorTests(unittest.TestCase):
    def test_parse_commit_header_extracts_type_scope_and_subject(self):
        commit_type, scope, subject = parse_commit_header("feat(app): add feature")

        self.assertEqual(commit_type, "feat")
        self.assertEqual(scope, "app")
        self.assertEqual(subject, "add feature")

    def test_compare_entry_reports_capped_body_metrics(self):
        expected_body = [f"- Body {index}" for index in range(1, 10)]
        entry = {
            "title": "Long body example",
            "original_text": "Added feature with many body lines.",
            "expected_subject": "feat(app): add feature",
            "expected_body_lines": expected_body,
        }

        result = compare_entry(entry, StubGenerator())

        self.assertFalse(result["body_count_match"])
        self.assertTrue(result["type_match"])
        self.assertTrue(result["scope_match"])
        self.assertEqual(result["subject_text_similarity"], 1.0)
        self.assertTrue(result["capped_body_count_match"])
        self.assertEqual(result["expected_body_count"], 9)
        self.assertEqual(result["capped_expected_body_count"], MAX_BODY_LINES)
        self.assertEqual(result["generated_body_count"], MAX_BODY_LINES)
        self.assertEqual(result["capped_body_line_ratio"], 1.0)
        self.assertEqual(result["capped_body_coverage"], 1.0)


if __name__ == "__main__":
    unittest.main()
