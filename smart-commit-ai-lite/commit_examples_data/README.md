# Commit Examples Data

This folder contains structured data extracted from `COMMIT_GENERATION_EXAMPLES.md`.

Files:

- `parse_commit_examples.py`: parser script to regenerate the data.
- `examples.json`: consolidated list of examples.
- `examples.db`: SQLite database with parsed examples.
- `entries/`: one JSON file per example entry.

Usage:

```bash
python3 commit_examples_data/parse_commit_examples.py
```

Then inspect:

- `commit_examples_data/examples.json`
- `commit_examples_data/examples.db`
- individual entry files in `commit_examples_data/entries/`
