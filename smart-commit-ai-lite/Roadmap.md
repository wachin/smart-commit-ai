# Roadmap: NLTK + Lightweight ML Git Commit Generator

This roadmap tracks the progress of the NLTK-based smart commit generator, now extended with a mandatory classic scikit-learn ML engine. The goal is to improve Conventional Commit prediction without turning the project into a heavy AI application: everything should stay local, lightweight, explainable, maintainable, and Debian 12 friendly.

## Project Contract

### Philosophy
- [x] Keep the project lightweight, offline-first, open source, Linux friendly, Debian 12 friendly, and low-resource friendly.
- [x] Prioritize stability, offline compatibility, Debian compatibility, low memory usage, and then accuracy.
- [x] Keep `smart_commit_nltk.py` functional as the existing heuristic engine.
- [x] Extend the current architecture instead of replacing it.
- [x] Avoid unnecessary complexity and heavy dependencies.

### Technical Boundaries
- [x] Do not use transformers, torch, tensorflow, spaCy, Hugging Face, neural networks, cloud APIs, LLM frameworks, online inference, or telemetry.
- [x] Use dependencies available in Debian 12 repositories: `python3-nltk`, `python3-sklearn`, `python3-joblib`, `python3-langdetect`, and `python3-regex`.
- [x] Keep `python3-gensim` optional, not required.
- [x] Do not depend on heavy pip-only packages for the main path.
- [x] Keep the application fully usable without internet access once local NLTK data and, if used, the local model are present.

### Engine Responsibilities
- [x] NLTK and local utilities: normalization, cleanup, tokenization, stemming, stopword removal, and preprocessing.
- [x] scikit-learn: TF-IDF vectorization, ML classification, and commit type prediction.
- [x] `smart_commit_nltk.py`: orchestrator for NLTK preprocessing -> sklearn classification -> NLTK/heuristic subject and body generation.
- [x] Existing heuristics: scope detection, subject/body generation, and compatibility with the current UI behavior.
- [x] `python3-langdetect`: support language detection when useful, with deterministic behavior.
- [x] `python3-regex`: improve regular-expression handling where useful.

### ML Objective
- [x] Predict Conventional Commit types from user text.
- [x] Support these types: `feat`, `fix`, `docs`, `refactor`, `test`, and `chore`.
- [x] Use `TfidfVectorizer` and `LinearSVC`.
- [x] Save the model locally with `joblib`.
- [x] Save the vectorizer separately.
- [x] Load quickly from the distributed local model artifacts.
- [x] Avoid online inference and external services.

## Current State

The program is already usable for daily work: it accepts pasted English or Spanish text, removes Markdown/command noise, detects language, proposes `type(scope)`, generates a localized subject and body, lets the user manually correct language/type/scope, and copies the command without a modal dialog.

The current improvement track is not Git integration. It is better semantic quality from pasted text. The ML layer is mandatory, classic, and local; `smart_commit_nltk.py` orchestrates the hybrid flow instead of being replaced by it.

### Latest Important Progress
- [x] Removed the separate subject/body preview because it did not improve the workflow.
- [x] Added word-boundary-aware subject truncation.
- [x] Fixed prioritization so semantic changes are not hidden by secondary test or documentation mentions.
- [x] Added detection for indirect validation phrases such as `Result: 20 tests OK`, `full suite passes`, `py_compile`, `compileall`, `unittest`, and `pytest`.
- [x] Added file mention detection to classify code, tests, documentation, reports, and configuration.
- [x] Expanded the body from 5 to 7 bullets to preserve important details.
- [x] Added bullet ranking so main changes come first, tests/docs/reports follow, and validation stays last.
- [x] Added a hybrid ML architecture with scikit-learn, TF-IDF, LinearSVC, and NLTK/heuristic orchestration.
- [x] Current suite: 71 registered tests, all passing in this Debian apt sklearn environment.

### ML Prompt Compliance Status
- [x] `smart_commit_nltk.py` remains present and functional.
- [x] The sklearn engine is modular and part of the standard architecture.
- [x] Add startup validation for the distributed `ml/commit_model.pkl` and `ml/vectorizer.pkl` artifacts.
- [x] Validate `ml/model_metadata.json` format, required fields, supported labels, and label counts before treating the distributed model as ready.
- [x] Training reuses `commit_examples_data/examples.json`, `commit_examples_data/examples.db`, and `commit_examples_data/entries/`.
- [x] The predictor returns a type and approximate confidence when the model supports it.
- [x] The system supports English and Spanish input.
- [x] The project includes `ml/`, `utils/`, and dedicated tests for the new architecture.
- [x] Product decision: distribute a pre-trained model while keeping local retraining available for users who need it.
- [x] Validate real training with `python3-sklearn` installed from Debian repositories.
- [x] Validate real predictions with the distributed pre-trained model artifacts.
- [x] Distribute a pre-trained model, vectorizer, and metadata file; document how users can retrain locally as needed.

### Current Quality Example

Input summary:

```text
Ip mp ovlntfiltim etxdctetx
 utma_comt_ltk.pyt/tst_smr_com_lk.y,READMEm,
Romp.d,comm_exmp_ata/aiso_rp.jsn
19OK
 utma_comt_ltk.pyts/tt_sma_com_lpy,README.m,
Romp.d,comm_exmp_ata/aiso_rp.jsn
19OK
I updated smart_commit_nltk.py, tests/test_smart_commit_nltk.py, README.md,
Roadmap.md, and commit_examples_data/comparison_report.json.
Result: 19 tests OK.
```

Current expected output:

```bash
git commit -m "feat(nlp): improve file mention detection" \
  -m "- Update code paths mentioned in the summary" \
  -m "- Cover changes with regression tests" \
  -m "- Update documentation mentioned in the summary" \
  -m "- Update evaluation data or reports" \
  -m "- Validation: 19 tests pass"
```

### Useful Commands

Install Debian dependencies:

```bash
sudo apt install \
    python3-pyqt6 \
    python3-nltk \
    python3-sklearn \
    python3-joblib \
    python3-langdetect \
    python3-regex
```

Optional dependency:

```bash
sudo apt install python3-gensim
```

Train or retrain the local ML model:

```bash
python3 -m ml.train_model
```

Run the regression suite:

```bash
QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests -v
```

Recalculate the comparison report:

```bash
QT_QPA_PLATFORM=offscreen python3 commit_examples_data/compare_generator.py
```

Note: `__pycache__/smart_commit_nltk.cpython-311.pyc` may appear modified because it is already tracked by Git. `.gitignore` prevents new generated artifacts, but removing that tracked bytecode from the index remains pending.

## Completed Features

### [x] Initial Project Setup
- [x] Created the repository and basic structure.
- [x] Installed the main dependencies: NLTK and PyQt6.
- [x] Added startup checks for required NLTK data.
- [x] Added first-run download support for missing NLTK packages.
- [x] Documented Debian packages required for the hybrid ML engine.
- [x] Documented `python3-gensim` as an optional dependency.

### [x] Desktop Interface
- [x] Main PyQt6 window for pasting change summaries.
- [x] Button for generating commits with NLTK.
- [x] Button for clearing user input.
- [x] Detected-language indicator: pending, Spanish, or English.
- [x] Manual language selector: Automatic, Spanish, or English.
- [x] Manual selectors for type and scope before copying.
- [x] Non-intrusive warning when input contains heavy noise or code blocks.
- [x] Output area with multiline `git commit` command.
- [x] Button for copying the command to the clipboard.
- [x] Copy confirmation in the button itself, without a modal message.

### [x] Base NLTK Generator
- [x] Tokenization and POS tagging for English text.
- [x] Initial verb/object extraction for subject construction.
- [x] Sentence scoring to choose the most representative phrase.
- [x] Conventional Commit format: `type(scope): subject`.
- [x] Length limits for subjects and body lines.

### [x] Commit Example Dataset
- [x] Created `COMMIT_GENERATION_EXAMPLES.md` with real cases.
- [x] Created `parse_commit_examples.py` to parse examples.
- [x] Exported examples to JSON and SQLite.
- [x] Validated 45 processed entries.

### [x] Comparison and Evaluation System
- [x] Created `compare_generator.py`.
- [x] Compared generated commits against expected commits.
- [x] Produced a JSON report with similarity metrics.
- [x] Improved label balance from 12.25 to 1.04 with 593 diverse examples
- [x] Improved subject similarity to 0.509.
- [x] Updated `compare_generator.py` for the current bilingual signature.
- [x] Recalculated `comparison_report.json` after bilingual improvements.
- [x] Recorded current baseline: 45 examples, subject similarity 0.444, subject text similarity 0.395, 7 type matches, and 26 scope matches.

### [x] Noise Filtering
- [x] Removed terminal commands and irrelevant conversational phrases.
- [x] Cleaned lines generated by tools or assistants.
- [x] Filtered Markdown triple-backtick blocks.
- [x] Ignored pasted `git commit -m` commands inside summaries.
- [x] Ignored embedded `-m` lines to avoid polluting the body.
- [x] Cleaned Markdown links while preserving visible link text.
- [x] Preserved useful validations such as `py_compile` when they appear inside code blocks.

### [x] Bilingual English/Spanish Support
- [x] Simple input language detection (`es` / `en`).
- [x] Language-specific tokenization using English or Spanish Punkt.
- [x] Subject and body generation in the same language as the summary.
- [x] Support for common Spanish verbs: `creado`, `actualizado`, `incluye`, `resume`, `corrige`, and `mejora`.
- [x] Spanish object extraction through local linguistic rules.
- [x] Specific cases for roadmap summaries in English and Spanish.
- [x] Specific cases for bilingual/NLP improvements.

### [x] Type and Scope Detection
- [x] Automatic type detection: `feat`, `fix`, `docs`, `test`, `build`, `ci`, `style`, `refactor`, `perf`.
- [x] Automatic scope detection: `app`, `ui`, `docs`, `repo`, `dict`, `tools`, `nlp`, `ml`.
- [x] Fixed false-positive `ci` detection inside words such as `funcionalidades` and `secciones`.
- [x] Prioritized NLP/bilingual changes as `feat(nlp)`.
- [x] Classified newly created roadmaps as `docs(repo)`.

### [x] Lightweight Hybrid ML Engine
- [x] Created `ml/dataset_loader.py` to reuse `examples.json`, `examples.db`, and `commit_examples_data/entries/`.
- [x] Created `ml/train_model.py` with `TfidfVectorizer` and `LinearSVC`.
- [x] Saved `commit_model.pkl` and `vectorizer.pkl` locally with `joblib`.
- [x] Added `model_metadata.json` generation for model format, label counts, and artifact paths.
- [x] Created `ml/predictor.py` with fast local model loading.
- [x] Added `python3 -m ml.predictor` for direct offline CLI predictions and model status checks.
- [x] Added explicit model artifact status reporting for model/vectorizer presence and loadability.
- [x] Added metadata validation for required fields and model format version.
- [x] Added metadata validation for supported labels and label counts matching the training total.
- [x] Added offline seed examples to cover `feat`, `fix`, `docs`, `refactor`, `test`, and `chore`.
- [x] Added shared utilities in `utils/` for NLTK preprocessing, language detection, and `python3-regex`.
- [x] Documented Debian installation and local training.
- [x] Started separating NLTK/preprocessing responsibilities from sklearn/classification responsibilities.
- [x] Surface missing official model artifacts in the UI with a retraining command hint.
- [x] Generated official local model artifacts with 593 examples: `ml/commit_model.pkl`, `ml/vectorizer.pkl`, and `ml/model_metadata.json`.
- [x] Added 90+ user-supplied training examples covering web, mobile, ML, DevOps, security, and more.
- [x] Added entry-file validation for required training fields and supported commit types.
- [x] Added duplicate title/text validation for training entry files.
- [x] Made `python3 -m ml.train_model` stop before writing artifacts when entry validation fails.
- [x] Added a confidence gate so low-confidence ML predictions do not override stronger heuristic decisions.
- [x] Updated README and ML README for distributed artifacts, confidence-gated ML use, and current Debian sklearn validation.

### [x] Offline and Extensible Architecture
- [x] Kept the existing heuristic engine as the subject/body and scope orchestration layer.
- [x] Added the sklearn engine without breaking the current UI flow.
- [x] Prepared the structure around the hybrid engines: NLTK/utils, sklearn classifier, and heuristic subject/body generation.
- [x] Avoided any dependency on network access, external APIs, telemetry, or online inference.
- [x] Kept model artifacts as local files generated by `joblib`.

### [x] Body Line Generation
- [x] Generated up to 7 relevant bullets.
- [x] Localized bullets in English or Spanish according to the input text.
- [x] Specific bullets for roadmap progress tracking.
- [x] Specific bullets for bilingual/NLP support.
- [x] Validation bullets for `compileall`, tests, and `py_compile`.
- [x] Basic deduplication to avoid repeated bullets.

### [x] Documentation
- [x] Updated README with current capabilities.
- [x] Added output examples in English and Spanish.
- [x] Updated Roadmap with completed and pending features.
- [x] Updated README with testing and evaluation commands.

### [x] Initial Evaluation and Testing
- [x] Created a `unittest` regression suite.
- [x] Tests for `strip_markdown_noise()`.
- [x] Tests for language detection.
- [x] Tests for bilingual `feat(nlp)` generation in Spanish and English.
- [x] Test for Spanish roadmap input as `docs(repo)`.
- [x] Test to avoid false-positive `ci` inside common words.
- [x] Test to prioritize testing/evaluation summaries over bilingual terms.
- [x] Test for clearing input, output, and copy button state.
- [x] Test to prioritize Clear Input summaries over test/Roadmap mentions.
- [x] Test to show and reset detected language in the interface.
- [x] Test to prioritize detected-language summaries over Roadmap mentions.
- [x] Test to manually force the generation language.
- [x] Test to manually edit type/scope and regenerate the command.
- [x] Test for compact startup window geometry.
- [x] Test to prioritize type/scope summaries over test/Roadmap mentions.
- [x] Test to confirm copy state in the button without a modal message.
- [x] Test for noise warnings from code blocks and pasted commits.
- [x] Test for subject truncation without cutting words.
- [x] Test to prioritize preview removal and truncation summaries over test mentions.
- [x] Test to detect indirect validations such as `full suite passes: 18 tests OK`.
- [x] Test to detect code, test, documentation, and report mentions.
- [x] Test to rank bullets by importance and remove duplicate generic documentation.
- [x] Tests for dataset loading and local predictor artifact handling.
- [x] Unit tests for common Spanish action extraction.
- [x] Tests for Spanish first-person and team conjugations such as `arreglé`, `añadimos`, `mejoramos`, and `documentamos`.
- [x] Direct tests for `select_commit_type()` with core categories.
- [x] Direct tests for `detect_scope()` with common project areas.
- [x] Regression for rich README architecture summaries compared against an AI-generated commit.
- [x] Regression for ML metadata validation summaries compared against an AI-generated commit.
- [x] Regression for original prompt examples: crash/audio, MIDI karaoke, installation instructions, and deprecated code.
- [x] Regression for mixed English/Spanish NLP summaries.
- [x] Regression for several modified files in the offline ML pipeline.
- [x] Regression for English summaries that contain Spanish examples or commit snippets.
- [x] Regression for colloquial Spanish phrases such as `le metí`, `le puse`, `se arregló`, and `quedó documentada`.
- [x] Tests for model artifact status reporting and UI model status text.
- [x] Tests for model metadata generation without requiring sklearn at runtime.
- [x] Tests for valid metadata, invalid metadata status, unsupported labels, and mismatched label counts.
- [x] Tests for dataset label-balance summaries without requiring sklearn at runtime.
- [x] Tests for optional built-in seed examples in local training.
- [x] Tests that user-supplied training examples are loaded from entry files.
- [x] Tests that all entry files are valid for training use.
- [x] Tests that duplicate entry titles and original texts are rejected before training.
- [x] Test that training stops before model writes when entry files are invalid.
- [x] Tests for capped body comparison metrics that respect the 7-bullet limit.
- [x] Tests for type/scope/text breakdown in the historical comparison report.
- [x] Dataset-only ML examples now cover all supported labels without requiring seed examples.
- [x] Tests for offline ML predictor accuracy evaluation without requiring sklearn at runtime.
- [x] Tests for ML evaluation misclassification reporting.
- [x] Tests for the shared lightweight predictor interface.
- [x] Tests for distributed artifact path and policy versioning.
- [x] Tests for distributed model predictions on core prompt examples.
- [x] Tests for public `ml` package predictor exports.
- [x] Tests for predictor JSON CLI output and empty prediction payloads.
- [x] Tests for the dedicated input cleanup module.
- [x] Reusable fixtures for real AI-comparison summaries used in regressions.
- [x] Direct tests for the dedicated type/scope detection module.
- [x] Centralized UI type/scope option lists in the type/scope detection module.
- [x] Tests for shared language detection and signal-text cleanup.
- [x] Tests for structured English/Spanish language marker scoring.
- [x] Test for repository bytecode ignore rules.
- [x] Per-label ML evaluation metrics for targeting weak commit-type classes.
- [x] Type/scope/text metrics in `comparison_report.json` for easier historical analysis.
- [x] Regression for low-confidence ML predictions preserving heuristic commit types.
- [x] Documentation reflects the shipped model artifacts, predictor CLI, and Debian apt validation.
- [x] Successful suite run: 71 tests pass with `python3-sklearn` installed from apt.

### [x] Generated Artifact Hygiene
- [x] Created `.gitignore` entries for `__pycache__/` and `*.py[cod]`.

## Future Improvements

### Recommended Next Session
- [x] Test the program with the latest Codex-generated summary and compare it against the commit a richer AI would produce.
- [x] Added a regression for ML metadata validation summaries so they generate `feat(ml)` instead of generic style/docs output.
- [x] Expanded training dataset to 182 examples with diverse real-world scenarios.
- [x] Lowered ML confidence gate to 0.4 to improve ML contribution.
- [x] If the subject is too generic, add a specific subject rule before touching the body.
- [x] If the body has good bullets but poor ordering, adjust `rank_body_lines()`.
- [x] If useful information is lost from pasted text, inspect `clean_input()` first.
- [x] After each improvement, add or adjust a regression test in `tests/test_smart_commit_nltk.py`.
- [x] Always run `QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests -v`.

### [ ] Evaluation and Testing
- [x] Add more unit tests for Spanish action extraction.
- [x] Add more unit tests for `select_commit_type()` and `detect_scope()`.
- [x] Add ML prediction tests with the distributed trained model in a Debian apt environment.
- [x] Test local training with `python3-sklearn` and `python3-joblib` installed from apt.
- [x] Test distributed model prediction with `python3-sklearn`, `python3-joblib`, `python3-langdetect`, and `python3-regex` installed from apt.
- [x] Verify prompt examples: crash/audio -> `fix`, MIDI karaoke -> `feat`, instructions -> `docs`, deprecated code -> `refactor`.
- [x] Add regression cases for mixed English/Spanish texts.
- [x] Add regression cases for summaries with several modified files..
- [x] Expanded dataset to 593 examples with diverse real-world scenarios
- [x] Define new metrics that do not penalize the current 7-bullet limit.
- [x] Improve historical dataset diagnostics without losing recent bilingual cases.
- [x] Improve historical dataset scores without losing recent bilingual cases.

### [ ] ML Engine and Data
- [x] Evaluate dataset balance: the historical examples currently favor `feat`.
- [x] Add more real examples for `fix`, `docs`, `refactor`, `test`, and `chore`.
- [x] Measure local model accuracy without increasing weight or complexity.
- [x] Report per-label evaluation metrics so weak classes can be improved without heavy tooling.
- [x] Report misclassified examples during ML evaluation so weak examples can be inspected directly.
- [x] Document when to regenerate `commit_model.pkl`, `vectorizer.pkl`, and `model_metadata.json`.
- [x] Keep offline seed examples only as support while the real dataset grows.

### [ ] Language Support
- [x] Expand Spanish verbs and patterns.
- [x] Improve language detection for mixed-language texts.
- [x] Share language detection cleanup between the GUI and ML preprocessing path.
- [x] Separate language-specific rules into more maintainable structures.
- [x] Evaluate a Spanish POS tagger if more grammatical precision is desired.
- [x] Support regional variants and more colloquial phrases.

### [ ] Architecture and Maintainability
- [x] Add external modules for preprocessing, language, and ML without rewriting `smart_commit_nltk.py`.
- [x] Fully separate heuristic NLP logic from the PyQt6 interface.
- [x] Create a dedicated class or module for input cleanup.
- [x] Create a dedicated module for type/scope detection.
- [x] Create reusable fixtures with real examples.
- [x] Define the packaging/versioning policy for the distributed pre-trained model, vectorizer, metadata, and locally retrained artifacts.
- [x] Define a common internal interface for the hybrid NLTK/utils, sklearn, and heuristic components.
- [x] Remove any already-tracked `__pycache__` files from the Git index.

### [ ] User Interface
- [x] Allow manual language override.
- [x] Allow editing type/scope from the UI before copying.
- [x] Show warnings when input contains heavy noise or many code blocks.
- [x] Start the window at a compact, top-left geometry that fits above the desktop panel.

### [ ] Commit Quality
- [x] Improve bullet ranking by importance.
- [x] Detect validations and tests even when they appear in indirect phrases.
- [x] Detect documentation, test, and code mentions inside pasted text.
- [x] Improve subject truncation so it does not cut words.
- [x] Expand the body up to 7 bullets to preserve relevant changes and validation.
- [x] Prioritize combined semantic improvements over secondary test/documentation mentions.

---

**Last updated:** May 12, 2026  
**Status:** Functional for basic use and daily iteration. It now has initial regressions, dataset evaluation, and a documented mandatory offline NLTK + sklearn architecture. The next priority is improving semantic quality from pasted text without losing lightness or Debian compatibility.
