import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryHygieneTests(unittest.TestCase):
    def test_gitignore_covers_python_bytecode(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn("__pycache__/", gitignore)
        self.assertIn("*.py[cod]", gitignore)


if __name__ == "__main__":
    unittest.main()
