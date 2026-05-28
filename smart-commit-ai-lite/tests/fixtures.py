"""Reusable real-world summaries for regression tests."""

SPANISH_BILINGUAL_SUMMARY = """Listo, le metí una mejora fuerte a [smart_commit_nltk.py](/tmp/smart_commit_nltk.py).
Ahora detecta si el texto está en español o inglés, usa tokenización por idioma,
entiende verbos españoles como `he creado`, `actualizado`, `incluye`, `resume`,
y genera el subject/body en el mismo idioma del texto de entrada.

```bash
git commit -m "docs(repo): agrega roadmap con seguimiento de progreso" \\
  -m "- Documenta funcionalidades completadas"
python3 -m py_compile smart_commit_nltk.py
```

También corregí el bug que hacía que saliera `ci(docs)` por encontrar las letras
`ci` dentro de palabras como “funcionalidades” o “secciones”.
"""


README_ARCHITECTURE_SUMMARY = """Updated [README.md](/home/wachin/Dev/smart-commit-ai-lite/README.md) where it was still a bit thin.

Added:
- clearer project title with the lightweight ML layer
- explicit project principles and “do not use” constraints
- supported ML labels
- NLTK/utils vs scikit-learn vs heuristic responsibility split
- local `joblib` artifact behavior
- Debian validation note
- contribution guidance for balanced ML examples and ML prediction tests

No tests needed; documentation-only change.
"""


ML_METADATA_SUMMARY = """Continued development on the ML layer.

I added stricter model metadata validation in [ml/predictor.py](/home/wachin/Dev/smart-commit-ai-lite/ml/predictor.py:33): the predictor now checks `model_metadata.json` for required fields and the supported format version before reporting the distributed ML model as ready.

I also added predictor tests in [tests/test_predictor.py](/home/wachin/Dev/smart-commit-ai-lite/tests/test_predictor.py:39) for valid metadata and invalid metadata, then updated [Roadmap.md](/home/wachin/Dev/smart-commit-ai-lite/Roadmap.md:53) with the new progress and current suite count.

Verification passed:

```bash
QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests -v
```

Result: `32` tests ran, `31` passed, `1` skipped because `python3-sklearn` is not installed in this environment.
"""


SPANISH_VERB_EXPANSION_SUMMARY = """Continued development with expanded Spanish verb support.

I fixed common Spanish summaries that were falling back to `actualiza proyecto`, including:

```text
Arreglé el fallo al abrir archivos de audio.
Añadimos soporte para karaoke MIDI.
Mejoramos la detección de idioma mixto.
Documentamos las instrucciones de instalación.
```

These now produce specific Conventional Commits such as:

```bash
git commit -m "fix(app): corrige fallo al abrir archivos de audio"
git commit -m "feat(app): agrega soporte para karaoke midi"
git commit -m "docs(docs): documenta instrucciones de instalación"
```

I updated [smart_commit_nltk.py](/home/wachin/Dev/smart-commit-ai-lite/smart_commit_nltk.py:314) with the new Spanish conjugations, fixed `ci` scope matching so it no longer fires inside `instrucciones`, and added regressions in [tests/test_smart_commit_nltk.py](/home/wachin/Dev/smart-commit-ai-lite/tests/test_smart_commit_nltk.py:173). [Roadmap.md](/home/wachin/Dev/smart-commit-ai-lite/Roadmap.md:53) now marks Spanish verb expansion complete.

Verification passed:

```bash
QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests -v
```

Result: `37` tests ran, `36` passed, `1` skipped because `python3-sklearn` is not installed here.
"""


ML_PIPELINE_SUMMARY = """Improved the offline ML training pipeline across several files.

Changed:
- ml/dataset_loader.py loads examples from JSON, SQLite, and entries.
- ml/train_model.py writes joblib artifacts and metadata.
- ml/predictor.py reports artifact readiness.
- utils/preprocessing.py normalizes text before vectorization.
- tests/test_ml_training.py and tests/test_predictor.py cover training and predictor behavior.
- README.md and Roadmap.md document the workflow.

Result: 35 tests OK.
"""
