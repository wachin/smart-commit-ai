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
from smart_commit_ai.local_generator import LocalCommitGenerator


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
