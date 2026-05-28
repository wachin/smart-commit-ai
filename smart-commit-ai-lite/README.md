# Smart Commit AI Lite

A lightweight desktop app built with **PyQt6**, **NLTK**, and classic **scikit-learn** that turns pasted change summaries into ready-to-run Conventional Commit commands.

The project is intentionally local-first: no API keys, no cloud model, and no network dependency after the initial NLTK data download and local model setup. It uses a mandatory hybrid architecture: NLTK prepares language-aware text features, scikit-learn classifies the commit type, and `smart_commit_nltk.py` orchestrates the UI, scope detection, subject generation, and body generation.

![](vx_images/smart_commit_ai_generator.png)

## Project Principles

- Lightweight, offline-first, open source, Linux friendly, Debian 12 friendly, and low-resource friendly.
- `smart_commit_nltk.py` remains functional and acts as the orchestrator for the hybrid workflow.
- The sklearn engine extends the existing NLTK workflow instead of replacing it.
- Stability, offline compatibility, Debian compatibility, and low memory usage take priority over raw accuracy.
- No transformers, torch, tensorflow, spaCy, Hugging Face tooling, neural networks, cloud APIs, LLM frameworks, online inference, telemetry, or heavy pip-only dependencies.

## Features

- **Bilingual input support**: Detects Spanish or English summaries and keeps the generated subject/body in the same language.
- **Language-aware tokenization**: Uses NLTK Punkt tokenizers for English and Spanish sentence splitting.
- **Spanish action extraction**: Understands common Spanish development phrases such as `he creado`, `actualizado`, `incluye`, `resume`, `corrige`, and `mejora`.
- **Conventional Commits format**: Generates `type(scope): subject` commands with scopes such as `nlp`, `ml`, `repo`, `docs`, `ui`, `app`, `dict`, and `tools`.
- **Markdown noise filtering**: Ignores pasted fenced code blocks, embedded `git commit -m` examples, Markdown links, and quoted command output that would otherwise pollute the result.
- **Smarter type detection**: Avoids false positives such as classifying a commit as `ci` just because the letters `ci` appear inside Spanish words like `funcionalidades` or `secciones`.
- **Sklearn classifier**: Uses a local TF-IDF + LinearSVC model for `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, and related Conventional Commit type prediction.
- **Distributed model**: Ships with `ml/commit_model.pkl`, `ml/vectorizer.pkl`, and `ml/model_metadata.json`, with local retraining available when needed.
- **Conservative ML orchestration**: Low-confidence ML predictions do not override stronger heuristic decisions. Confidence gate set to 0.4 to allow ML to contribute with expanded dataset.
- **Structured body generation**: Builds up to seven high-signal bullet lines for roadmap work, bilingual NLP changes, UI work, validation, docs, and common project patterns.
- **Clipboard workflow**: Shows a multiline `git commit` command ready to copy and paste into a terminal.

## Model Training

The distributed model is trained with 593 diverse examples covering web development, mobile, ML, DevOps, security, testing, refactoring, and documentation. To retrain the model with new examples:

```bash
python3 -m ml.train_model
```

This will regenerate `ml/commit_model.pkl`, `ml/vectorizer.pkl`, and `ml/model_metadata.json` from the examples in `commit_examples_data/entries/`.

## Installation

### Debian 12 / Ubuntu / Linux Mint

```bash
sudo apt update
sudo apt install \
    python3-pyqt6 \
    python3-nltk \
    python3-sklearn \
    python3-joblib \
    python3-langdetect \
    python3-regex
```

Optional:

```bash
sudo apt install python3-gensim
```

The sklearn packages are part of the standard Debian 12 installation path for this project. The distributed model lives in `ml/commit_model.pkl`, its TF-IDF vectorizer lives in `ml/vectorizer.pkl`, and metadata lives in `ml/model_metadata.json`. The current model is trained with 593 diverse examples covering web development, mobile, ML, DevOps, security, and more.

This project is designed for Debian repository packages and offline use. Avoid heavy AI stacks such as transformers, torch, tensorflow, spaCy, Hugging Face tooling, cloud APIs, or online inference services.

On first run, the app checks for required NLTK data and downloads missing packages:

- `punkt`
- `averaged_perceptron_tagger`

The Spanish tokenizer is included in the Punkt data package.

Optional pre-download:

```bash
python3 -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

## Usage

1. Run the app:

   ```bash
   python3 smart_commit_nltk.py
   ```

2. Paste a summary from your own notes, an assistant response, or a changelog-style paragraph.
3. Leave the language mode on automatic, or choose Spanish / English manually if the text is mixed.
4. Click the NLTK commit generation button.
5. Review the generated command, detected language status, and any non-blocking noise warning.
6. Adjust **Tipo** or **Scope** if the automatic choice needs a manual correction.
7. Copy it to the clipboard and run it in your repository. The copy button confirms the action in-place, without opening a popup.

## Startup Window Size

The default startup position and size are defined near the top of `smart_commit_nltk.py` in `NLPCommitGenerator`:

```python
DEFAULT_WINDOW_GEOMETRY = (90, 30, 660, 690)
MINIMUM_WINDOW_SIZE = (620, 620)
```

`DEFAULT_WINDOW_GEOMETRY` uses this order:

```text
(x position, y position, width, height)
```

For example, to open the app wider and slightly lower:

```python
DEFAULT_WINDOW_GEOMETRY = (120, 80, 820, 720)
```

Adjust `MINIMUM_WINDOW_SIZE` only if you want to allow the window to be resized smaller or force it to stay larger.

## Hybrid Architecture

The machine-learning engine predicts the Conventional Commit type. Supported ML labels include:

- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `chore`

Responsibility split:

- **NLTK/utils**: normalization, cleanup, tokenization, stemming, stopword removal, language detection, and language-aware preprocessing.
- **scikit-learn**: TF-IDF vectorization and ML classification of commit types.
- **`smart_commit_nltk.py` orchestrator**: coordinates the flow: NLTK preprocessing -> sklearn classification -> NLTK/heuristic subject and body generation. It also handles scope detection, confidence-gated ML overrides, and the UI workflow.

## Model Training

Train or retrain the local model after installing `python3-sklearn`:

```bash
python3 -m ml.train_model
```

The trainer reads local examples from:

- `commit_examples_data/examples.json`
- `commit_examples_data/examples.db`
- `commit_examples_data/entries/`

It writes:

- `ml/commit_model.pkl`
- `ml/vectorizer.pkl`
- `ml/model_metadata.json`

The project distributes a pre-trained model for these default filenames. The current official artifacts were trained locally with Debian-packaged sklearn/joblib from 68 offline examples. Users can retrain locally and replace them as needed.

The model and vectorizer are trained and loaded locally with `joblib`. The metadata file records the training example count, label balance, artifact paths, model format version, and artifact policy version. At startup the predictor validates the metadata format, supported labels, and label counts before reporting the model as ready. No network access, online inference, or external services are used.

Use the default training command for official artifacts. For dataset-only experiments without built-in seed examples:

```bash
python3 -m ml.train_model --no-seed
```

Regenerate the model, vectorizer, and metadata after adding balanced examples, changing preprocessing, changing supported labels, or preparing a Debian validation release.

Training entry files are validated by the test suite and by `python3 -m ml.train_model` before model artifacts are written. Each JSON entry under `commit_examples_data/entries/` should include a non-empty `title`, `original_text`, `expected_subject`, and `expected_body_lines`, and the subject must use a supported Conventional Commit type. Duplicate titles or duplicate original texts are reported as validation errors.

The official distributed artifact paths are versioned in `ml/artifact_policy.py`. Local experimental `.pkl` files should use different names; `.gitignore` keeps them out of the repository while allowing the official artifacts to be tracked.

The UI shows the local model status at startup. If the distributed artifacts or metadata are not present yet, it points users to `python3 -m ml.train_model`.

Evaluate the local predictor against offline examples:

```bash
python3 -m ml.evaluate_model
```

With the distributed artifacts present, the evaluator reports accuracy, per-label metrics, and any misclassified examples for all local examples. If model artifacts are missing, it reports skipped examples instead of contacting any external service.

Predict a commit type directly from the distributed model:

```bash
python3 -m ml.predictor "fixed crash when opening audio files"
python3 -m ml.predictor --json "added MIDI karaoke support"
python3 -m ml.predictor --status
```

## Testing and Evaluation

Run the regression tests:

```bash
QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests -v
```

Recalculate the example-dataset comparison report:

```bash
QT_QPA_PLATFORM=offscreen python3 commit_examples_data/compare_generator.py
```

The comparison report is written to `commit_examples_data/comparison_report.json`. The current heuristics intentionally cap generated bodies at seven bullets, so the report includes type/scope/text diagnostics and cap-aware body metrics:

- `exact_type_matches`
- `exact_scope_matches`
- `average_subject_text_similarity`
- `capped_body_count_matches`
- `average_capped_body_line_ratio`
- `average_capped_body_coverage`

These metrics compare generated bodies against the first seven expected lines instead of penalizing the generator for not reproducing older, longer bodies.

## Examples

English input about bilingual NLP improvements can produce:

```bash
git commit -m "feat(nlp): add bilingual support and fix type detection" \
  -m "- Detect input language for localized tokenization" \
  -m "- Support Spanish verbs like creado, actualizado, and incluye" \
  -m "- Generate commit subject and body in the source language" \
  -m "- Fix false-positive ci detection inside common words" \
  -m "- Validate syntax with py_compile"
```

Input about roadmap work can produce:

```bash
git commit -m "docs(repo): add roadmap with progress tracking" \
  -m "- Document completed features and project progress" \
  -m "- Outline future work for Git, ML, UI, tests, and multilingual support" \
  -m "- Organize the roadmap with clear status sections" \
  -m "- Include documentation, community, and testing areas" \
  -m "- Use checkbox format for completed and pending tasks"
```

Short change summaries map to Conventional Commit types:

```text
fixed crash when opening audio files -> fix
added MIDI karaoke support -> feat
updated installation instructions -> docs
cleaned deprecated code -> refactor
```

## How It Works

1. **Noise cleanup**: Removes Markdown fences, embedded commit commands, copied `-m` lines, Markdown link targets, and other assistant/terminal noise.
2. **Language detection**: Scores Spanish and English markers to choose `es` or `en`.
3. **Sentence splitting**: Uses NLTK sentence tokenization with the detected language.
4. **Action extraction**: Applies English POS tagging and rule-based Spanish patterns to find the main action and object.
5. **Type/scope selection**: Classifies the change into Conventional Commit type/scope using whole-word matching and project-aware keywords.
6. **ML prediction**: The local TF-IDF + LinearSVC classifier predicts the commit type.
7. **Body generation**: Adds concise, localized bullets for detected change categories.
8. **Formatting**: Keeps the subject short and emits a shell-ready multiline `git commit` command.

## Project Structure

```text
├── smart_commit_nltk.py          # Main PyQt6 application
├── Roadmap.md                    # Current progress and planned improvements
├── COMMIT_GENERATION_EXAMPLES.md # Real-world examples and expected outputs
├── commit_examples_data/         # Parsed JSON/SQLite examples and comparison tools
├── ml/                           # Sklearn training, model, vectorizer, and prediction modules
├── utils/                        # Shared preprocessing, language, and regex helpers
├── tests/                        # Regression tests for NLP heuristics
└── README.md                     # Project documentation
```

## Current Limitations

- Spanish grammar support is rule-based. NLTK Punkt can split Spanish sentences, but this project does not currently use a full Spanish POS tagger.
- The generator is hybrid NLTK + classic ML, not a large language model. It improves through specific patterns, examples, and evaluation data.
- The current dataset is small and mostly feature-oriented, so the ML classifier uses a small offline seed set to represent all six supported types.
- Keep distributed model artifacts validated on a Debian 12 system with the required apt packages installed.
- It works best with summaries that describe concrete changes, files, features, validation, and user-visible behavior.

## Contributing

Good contributions include:

- Adding more Spanish and English phrase patterns.
- Expanding `commit_examples_data` with real summaries and expected commits.
- Adding balanced examples for `fix`, `docs`, `refactor`, `test`, and `chore`.
- Improving comparison metrics.
- Adding tests for language detection, Markdown cleanup, type/scope selection, ML prediction, and body generation.

## License

This project is open-source and available under GPL 3.
