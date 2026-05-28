import unittest

from utils.input_cleanup import clean_input, detect_input_noise_warnings, strip_markdown_noise


class InputCleanupTests(unittest.TestCase):
    def test_strip_markdown_noise_removes_embedded_commit_but_keeps_validation(self):
        text = """Useful summary.

```bash
git commit -m "docs(repo): embedded"
python3 -m py_compile smart_commit_nltk.py
```

Added language detection.
"""

        cleaned = strip_markdown_noise(text)

        self.assertNotIn("git commit -m", cleaned)
        self.assertIn("Verifiqué con python3 -m py_compile smart_commit_nltk.py.", cleaned)
        self.assertIn("Added language detection.", cleaned)

    def test_clean_input_filters_terminal_noise(self):
        text = """Read smart_commit_nltk.py
python3 -m unittest discover -s tests -v
Updated smart_commit_nltk.py with cleanup handling.
"""

        cleaned = clean_input(text)

        self.assertEqual(cleaned, "Updated smart_commit_nltk.py with cleanup handling.")

    def test_detect_input_noise_warnings_reports_code_and_embedded_commits(self):
        text = """Updated cleanup handling.

```bash
git commit -m "bad"
```
"""

        warnings = detect_input_noise_warnings(text)

        self.assertIn("1 bloque(s) de código", warnings)
        self.assertIn("commits pegados", warnings)


if __name__ == "__main__":
    unittest.main()
