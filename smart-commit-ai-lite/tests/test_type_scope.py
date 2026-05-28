import unittest

from utils.type_scope import (
    COMMIT_TYPE_OPTIONS,
    SCOPE_OPTIONS,
    DetectionContext,
    detect_scope,
    select_commit_type,
)


class TypeScopeTests(unittest.TestCase):
    def test_ui_option_constants_include_supported_values(self):
        self.assertEqual(COMMIT_TYPE_OPTIONS[:4], ("feat", "fix", "docs", "test"))
        self.assertIn("refactor", COMMIT_TYPE_OPTIONS)
        self.assertIn("nlp", SCOPE_OPTIONS)
        self.assertIn("ml", SCOPE_OPTIONS)

    def test_select_commit_type_handles_core_categories(self):
        cases = [
            ("Fixed crash when opening audio files.", "fix", "fix"),
            ("Updated README.md with installation instructions.", "update", "docs"),
            ("Refactored parser cleanup and simplified token handling.", "refactor", "refactor"),
            ("Added regression tests for language detection.", "add", "test"),
        ]

        for text, verb, expected_type in cases:
            with self.subTest(text=text):
                self.assertEqual(select_commit_type(text, verb), expected_type)

    def test_detect_scope_handles_common_project_areas(self):
        cases = [
            ("Updated smart_commit_nltk.py tokenization rules.", "nlp"),
            ("Added checkbox and button behavior to the dialog UI.", "ui"),
            ("Updated README.md with usage instructions.", "docs"),
            ("Changed converter tool for dictionary exports.", "dict"),
            ("Added .gitignore and comparison_report.json baseline data.", "repo"),
        ]

        for text, expected_scope in cases:
            with self.subTest(text=text):
                self.assertEqual(detect_scope(text), expected_scope)

    def test_special_summary_context_can_override_generic_keywords(self):
        text = "Updated README.md with ML principles, joblib artifacts, and Debian validation."
        context = DetectionContext(readme_architecture_docs=True)

        self.assertEqual(select_commit_type(text, "update", context=context), "docs")
        self.assertEqual(detect_scope(text, context), "readme")


if __name__ == "__main__":
    unittest.main()
