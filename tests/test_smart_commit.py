from pathlib import Path
import tempfile
import unittest

from smart_commit_ai.config import load_api_key, save_api_key
from smart_commit_ai.commit_message import (
    MAX_BODY_LINE_LENGTH,
    MAX_HEADER_LENGTH,
    CommitMessage,
    format_git_commit_command,
    parse_git_commit_command,
)
from smart_commit_ai.examples import ExampleStore
from smart_commit_ai.gemini_client import GeminiError
from smart_commit_ai.gemini_client import parse_model_response
from smart_commit_ai.local_generator import LocalCommitGenerator
from smart_commit_ai.service import SmartCommitService


WRK_SUMMARY = """We kept the development moving and took the first real WRK step.

In [file.py](/home/wachin/Dev/dmidiplayer/drumstick/drumstick_py/file.py), the loader now deliberately recognizes Cakewalk WRK input and raises a specific error:

`Cakewalk WRK files are not supported yet`

So `.wrk` files no longer fall through as generic "not a Standard MIDI File" failures. It is a small change, but it gives the app a much clearer contract and sets up the real parser work later.

I added coverage in [test_smf_parser.py](/home/wachin/Dev/dmidiplayer/tests/test_smf_parser.py) for a WRK-like header and marked the roadmap skeleton item complete in [Roadmap.md](/home/wachin/Dev/dmidiplayer/Roadmap.md).

Verification is clean:
- focused parser suite passed: `19 tests OK`
- full test suite passed: `208 tests OK`
- `compileall` passed

A strong next move is the actual WRK minimum event model.
"""


API_KEY_SUMMARY = """I updated it so the Gemini key is saved locally in .env.local, and .env.local is explicitly
ignored in .gitignore:29.

I also wired the app to:

- load the saved key when the window opens
- save the key when you press Create Commit
- store only GEMINI_API_KEY=... in .env.local
- set the file permissions to 600 when possible

Relevant files:

- smart_commit_ai/config.py:1
- smart_commit_ai/gui.py:8
- README.md:22

I verified:

- git check-ignore -v .env.local confirms it is ignored
- .env.local is not tracked by git
- tests pass: 4 tests OK
- compile check passes
"""


class CommitFormattingTests(unittest.TestCase):
    def test_format_and_parse_command(self):
        command = format_git_commit_command(
            'feat(parser): detect "WRK" files',
            ["- Recognize $WRK input", "- Validation: compileall OK"],
        )

        self.assertIn('\\"WRK\\"', command)
        self.assertIn("\\$WRK", command)
        parsed = parse_git_commit_command(command)

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.subject, 'feat(parser): detect "WRK" files')
        self.assertEqual(parsed.body_lines[0], "- Recognize $WRK input")


class LocalGeneratorTests(unittest.TestCase):
    def test_generates_wrk_commit_from_codex_summary(self):
        message = LocalCommitGenerator().generate(WRK_SUMMARY)

        self.assertEqual(message.subject, "feat(parser): detect Cakewalk WRK files")
        self.assertLessEqual(len(message.subject), MAX_HEADER_LENGTH)
        self.assertIn("- Add WRK-like header test coverage", message.body_lines)
        self.assertIn("- Update Roadmap.md to mark WRK skeleton item complete", message.body_lines)
        self.assertTrue(any("208 full tests pass" in line for line in message.body_lines))
        self.assertTrue(all(len(line) <= MAX_BODY_LINE_LENGTH for line in message.body_lines))

    def test_generates_api_key_persistence_commit_from_summary(self):
        message = LocalCommitGenerator().generate(API_KEY_SUMMARY)

        self.assertEqual(message.subject, "feat(config): persist Gemini API key")
        self.assertLessEqual(len(message.subject), MAX_HEADER_LENGTH)
        self.assertIn("- Save GEMINI_API_KEY to ignored .env.local", message.body_lines)
        self.assertIn("- Load saved Gemini key when the app window opens", message.body_lines)
        self.assertIn("- Add .env.local ignore coverage to prevent key commits", message.body_lines)
        self.assertTrue(any("4 tests pass" in line for line in message.body_lines))
        self.assertTrue(any("compileall OK" in line for line in message.body_lines))
        self.assertTrue(all(len(line) <= MAX_BODY_LINE_LENGTH for line in message.body_lines))


class GeminiParserTests(unittest.TestCase):
    def test_parses_json_wrapped_in_markdown(self):
        message = parse_model_response(
            """Here is the result:

```json
{
  "subject": "feat(config): persist Gemini API key",
  "body_lines": [
    "- Save GEMINI_API_KEY to ignored .env.local",
    "- Validation: 4 tests pass, compileall OK"
  ]
}
```
"""
        )

        self.assertEqual(message.subject, "feat(config): persist Gemini API key")
        self.assertEqual(message.body_lines[0], "- Save GEMINI_API_KEY to ignored .env.local")

    def test_parses_raw_git_commit_command(self):
        message = parse_model_response(
            """```bash
git commit -m "feat(config): persist Gemini API key" \\
  -m "- Save GEMINI_API_KEY to ignored .env.local" \\
  -m "- Validation: 4 tests pass, compileall OK"
```"""
        )

        self.assertEqual(message.subject, "feat(config): persist Gemini API key")
        self.assertEqual(message.body_lines[-1], "- Validation: 4 tests pass, compileall OK")


class FakeGenerator:
    def __init__(self, message: CommitMessage | None = None, error: Exception | None = None):
        self.message = message
        self.error = error

    def generate(self, original_text, api_key=None):
        if self.error:
            raise self.error
        return self.message


class ServiceSavePolicyTests(unittest.TestCase):
    def test_saves_only_gemini_generated_messages(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ExampleStore(Path(directory))
            service = SmartCommitService(store)
            service.gemini = FakeGenerator(
                CommitMessage(
                    subject="feat(config): persist Gemini API key",
                    body_lines=["- Save GEMINI_API_KEY to ignored .env.local"],
                    source="gemini",
                    model="gemini-test",
                )
            )

            result = service.generate("summary", provider="gemini", api_key="test", save=True)

            self.assertIsNotNone(result.saved_path)
            self.assertEqual(len(store.load()), 1)

    def test_does_not_save_local_generated_messages(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ExampleStore(Path(directory))
            service = SmartCommitService(store)
            service.local = FakeGenerator(
                CommitMessage(
                    subject="feat(config): persist Gemini API key",
                    body_lines=["- Save GEMINI_API_KEY to ignored .env.local"],
                    source="local",
                )
            )

            result = service.generate("summary", provider="local", save=True)

            self.assertIsNone(result.saved_path)
            self.assertEqual(store.load(), [])

    def test_does_not_save_auto_local_fallback_messages(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ExampleStore(Path(directory))
            service = SmartCommitService(store)
            service.gemini = FakeGenerator(error=GeminiError("offline"))
            service.local = FakeGenerator(
                CommitMessage(
                    subject="feat(config): persist Gemini API key",
                    body_lines=["- Save GEMINI_API_KEY to ignored .env.local"],
                    source="local",
                )
            )

            result = service.generate("summary", provider="auto", save=True)

            self.assertIsNone(result.saved_path)
            self.assertEqual(store.load(), [])


class ExampleStoreTests(unittest.TestCase):
    def test_saves_training_example_with_incrementing_slug(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ExampleStore(Path(directory))
            message = CommitMessage(
                subject="feat(parser): detect Cakewalk WRK files",
                body_lines=["- Add WRK-like header test coverage"],
            )

            path = store.save("summary", message, source="test")
            self.assertEqual(path.name, "1-parser-detect-cakewalk-wrk-files.json")

            duplicate = store.save("summary", message, source="test")
            self.assertEqual(duplicate, path)

            entries = store.load()
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].expected_subject, message.subject)


class ConfigTests(unittest.TestCase):
    def test_saves_and_loads_local_api_key(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.local"

            saved_path = save_api_key('abc-123_"key"', path)

            self.assertEqual(saved_path, path)
            self.assertEqual(load_api_key(path, include_environment=False), 'abc-123_"key"')
            self.assertIn("GEMINI_API_KEY=", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
