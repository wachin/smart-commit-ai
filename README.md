# Smart Commit AI

Smart Commit AI turns a pasted Codex development summary into a Conventional
Commit command.

## Run

```bash
python3 smart_commit_ai.py
```

Paste the Codex summary, choose a mode, then press **Create Commit**.
Use **Copy** to copy the generated `git commit` command.

## Modes

- `auto`: use Gemini when an API key is available, otherwise use the local
  generator.
- `gemini`: require Google Gemini API access.
- `local`: use the built-in offline generator.

Gemini uses the REST `generateContent` API with `gemini-2.5-flash` by default.
If that model is unavailable for your API key, the app tries compatible Flash
fallback models before using the local generator.
When you paste a Gemini key in the app, Smart Commit AI saves it locally in:

```text
~/.config/smartcommitai/secrets.env
```

User preferences, including the last selected mode, are saved in:

```text
~/.config/smartcommitai/settings.json
```

Those files live outside the repository, so they will not be added to normal
commits or pushed to GitHub. You can also export a key before launching:

```bash
export GEMINI_API_KEY="your-key"
python3 smart_commit_ai.py
```

To use a different model:

```bash
export SMART_COMMIT_AI_GEMINI_MODEL="gemini-3.5-flash"
```

If Gemini fails, Smart Commit AI still returns a local commit command. Use the
**Details** button to view and copy the Gemini diagnostic.

Use **Check API** to validate the saved Gemini key and confirm which
`generateContent` model the app will use. This calls Gemini `models.list` and
runs a tiny `generateContent` smoke test, so it checks both model availability
and actual text generation before saving the selected model.

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

The local generator can also learn lightweight rules from the saved examples
without NLTK, sklearn, or an LLM. Train or refresh those rules with:

```bash
python3 -m smart_commit_ai.rule_training
```

This writes:

```text
commit_examples_data/smart_commit_rules.json
```

When present, the local generator uses that file to improve `type`, `scope`,
subject reuse from similar examples, and matching body bullets before falling
back to fixed heuristics.

## Verify

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall smart_commit_ai tests
```
