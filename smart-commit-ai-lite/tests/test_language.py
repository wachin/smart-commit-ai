import unittest

from utils.language import LANGUAGE_MARKERS, detect_language, language_signal_text, score_language_markers


class LanguageTests(unittest.TestCase):
    def test_language_markers_are_grouped_by_supported_language(self):
        self.assertEqual(set(LANGUAGE_MARKERS), {"en", "es"})
        self.assertIn(" created", LANGUAGE_MARKERS["en"])
        self.assertIn(" creado", LANGUAGE_MARKERS["es"])

    def test_detect_language_handles_english_and_spanish(self):
        self.assertEqual(detect_language("Created bilingual support for English input."), "en")
        self.assertEqual(detect_language("He creado soporte bilingüe para español."), "es")

    def test_score_language_markers_includes_spanish_diacritics(self):
        scores = score_language_markers("Añadimos soporte para documentación.")

        self.assertGreater(scores["es"], scores["en"])

    def test_language_signal_text_ignores_code_fences_and_embedded_commits(self):
        text = """Continued development with expanded Spanish verb support.

```text
Arreglé el fallo al abrir archivos de audio.
Añadimos soporte para karaoke MIDI.
```

```bash
git commit -m "fix(app): corrige fallo al abrir archivos de audio"
```

I updated smart_commit_nltk.py with the new Spanish conjugations.
"""

        signal = language_signal_text(text)

        self.assertIn("Continued development", signal)
        self.assertIn("I updated smart_commit_nltk.py", signal)
        self.assertNotIn("Arreglé el fallo", signal)
        self.assertNotIn("git commit -m", signal)
        self.assertEqual(detect_language(text), "en")


if __name__ == "__main__":
    unittest.main()
