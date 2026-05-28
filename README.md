# Smart Commit AI

Smart Commit AI turns a pasted Codex development summary into a Conventional
Commit command.

## Run

```bash
python3 smart_commit_ai.py
```

Paste the Codex summary, choose a provider, then press **Create Commit**.
Use **Copy** to copy the generated `git commit` command.

## Providers

- `auto`: use Gemini when an API key is available, otherwise use the local
  generator.
- `gemini`: require Google Gemini API access.
- `local`: use the built-in offline generator.

Gemini uses the REST `generateContent` API with `gemini-3.5-flash` by default.
When you paste a Gemini key in the app, Smart Commit AI saves it locally in:

```text
.env.local
```

That file is ignored by `.gitignore`, so it will not be added to normal commits
or pushed to GitHub. You can also export a key before launching:

```bash
export GEMINI_API_KEY="your-key"
python3 smart_commit_ai.py
```

To use a different model:

```bash
export SMART_COMMIT_AI_GEMINI_MODEL="gemini-3.5-flash"
```

## Training Data

Generated input/output pairs are saved to:

```text
commit_examples_data/entries
```

Each saved JSON entry contains:

- `original_text`
- `expected_subject`
- `expected_body_lines`
- `expected_command`

Those examples are also used as few-shot context for Gemini and as retrieval
data for future local training work.

Only unchanged Gemini-generated commit messages are saved as training examples.
Local fallback output can be copied and used, but it is not written to
`commit_examples_data/entries`. The manual **Save Example** button follows the
same rule.

## Verify

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall smart_commit_ai tests
```
