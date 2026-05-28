import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

ROOT = Path(__file__).resolve().parents[1]
TESTS_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(TESTS_ROOT))

from PyQt6.QtWidgets import QApplication

from smart_commit_nltk import NLPCommitGenerator
from ml.predictor import PredictionResult
from fixtures import (
    ML_METADATA_SUMMARY,
    ML_PIPELINE_SUMMARY,
    README_ARCHITECTURE_SUMMARY,
    SPANISH_BILINGUAL_SUMMARY,
    SPANISH_VERB_EXPANSION_SUMMARY,
)


APP = QApplication.instance() or QApplication([])


class StubLowConfidencePredictor:
    def predict(self, _text, language=None):
        return PredictionResult('chore', confidence=0.2, language=language or 'en')


class SmartCommitGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = NLPCommitGenerator()

    def setUp(self):
        self.generator.input_text.clear()
        self.generator.output_text.clear()
        self.generator.copy_btn.setEnabled(False)
        self.generator.copy_btn.setText('Copiar al Portapapeles')
        self.generator.noise_warning_label.setText('')
        self.generator.noise_warning_label.setVisible(False)
        self.generator.language_override_combo.setCurrentIndex(0)
        self.generator.type_override_combo.setCurrentIndex(0)
        self.generator.scope_override_combo.setCurrentIndex(0)
        self.generator.language_status_label.setText('Idioma detectado: pendiente')
        self.generator.detected_commit_type = None
        self.generator.detected_scope = None
        self.generator.current_subject = ''
        self.generator.current_body_lines = []

    def render_command(self, text):
        self.generator.input_text.setPlainText(text)
        self.generator.generate_commit()
        return self.generator.output_text.toPlainText()

    def test_strip_markdown_noise_removes_embedded_commits(self):
        text = """Resumen útil.

```bash
git commit -m "docs(repo): bad embedded subject" \\
  -m "- Bad embedded body"
python3 -m py_compile smart_commit_nltk.py
```

Ahora detecta idioma y genera commits mejores.
"""
        cleaned = self.generator.nlp_engine.strip_markdown_noise(text)

        self.assertNotIn('git commit -m', cleaned)
        self.assertNotIn('-m "- Bad embedded body"', cleaned)
        self.assertIn('Verifiqué con python3 -m py_compile smart_commit_nltk.py.', cleaned)

    def test_detect_language_spanish_and_english(self):
        spanish = 'He creado soporte bilingüe para detectar español e inglés.'
        english = 'Created bilingual support to detect Spanish and English input.'

        self.assertEqual(self.generator.nlp_engine.detect_language(spanish), 'es')
        self.assertEqual(self.generator.nlp_engine.detect_language(english), 'en')

    def test_spanish_bilingual_summary_generates_feat_nlp(self):
        command = self.render_command(SPANISH_BILINGUAL_SUMMARY)

        self.assertIn('git commit -m "feat(nlp): agrega soporte bilingüe y corrige tipo ci"', command)
        self.assertIn('-m "- Detecta el idioma de entrada para tokenización localizada"', command)
        self.assertIn('-m "- Corrige falsos positivos de ci dentro de palabras comunes"', command)
        self.assertIn('-m "- Valida la sintaxis con py_compile"', command)
        self.assertNotIn('docs(repo): agrega roadmap', command)

    def test_roadmap_creation_in_spanish_generates_docs_repo(self):
        text = """He creado el archivo Roadmap.md en la raíz del proyecto.
Este documento resume el progreso realizado, marca funcionalidades completadas
y deja pendientes las mejoras futuras para Git, ML, UI, testing y multilenguaje.
"""
        command = self.render_command(text)

        self.assertIn('git commit -m "docs(repo): agrega roadmap con seguimiento de progreso"', command)
        self.assertIn('-m "- Documenta funcionalidades completadas y progreso del proyecto"', command)

    def test_ci_detection_uses_whole_word_matching(self):
        text = 'He creado funcionalidades y secciones nuevas en Roadmap.md.'
        verb, obj, _language = self.generator.nlp_engine.analyze_with_nltk(text)

        self.assertEqual(self.generator.nlp_engine.select_commit_type(text, verb, obj), 'docs')

    def test_select_commit_type_handles_core_change_categories(self):
        cases = [
            ('Fixed crash when opening audio files.', 'fix', 'audio files', 'fix'),
            ('Updated README.md with installation instructions.', 'update', 'README.md', 'docs'),
            ('Refactored parser cleanup and simplified token handling.', 'refactor', 'parser', 'refactor'),
            ('Added regression tests for language detection.', 'add', 'regression tests', 'test'),
        ]

        for text, verb, obj, expected_type in cases:
            with self.subTest(text=text):
                self.assertEqual(self.generator.nlp_engine.select_commit_type(text, verb, obj), expected_type)

    def test_low_confidence_ml_prediction_does_not_override_heuristic_type(self):
        original_predictor = self.generator.ml_predictor
        self.generator.ml_predictor = StubLowConfidencePredictor()
        try:
            commit_type = self.generator.predict_commit_type(
                'Updated README.md with installation instructions.',
                'update',
                'README.md',
                'en',
            )
        finally:
            self.generator.ml_predictor = original_predictor

        self.assertEqual(commit_type, 'docs')

    def test_prompt_examples_generate_expected_commit_types(self):
        cases = [
            ('fixed crash when opening audio files', 'fix(app): fix crash', 'fix'),
            ('added MIDI karaoke support', 'feat(app): add midi karaoke support', 'feat'),
            ('updated installation instructions', 'docs(docs): update installation instructions', 'docs'),
            ('cleaned deprecated code', 'refactor(app): refactor deprecated code', 'refactor'),
        ]

        for text, expected_subject, rejected_type in cases:
            with self.subTest(text=text):
                command = self.render_command(text)

                self.assertIn(f'git commit -m "{expected_subject}"', command)
                if rejected_type != 'feat':
                    self.assertNotIn(f'git commit -m "feat(', command)

    def test_detect_scope_handles_common_project_areas(self):
        cases = [
            ('Updated smart_commit_nltk.py tokenization rules.', 'nlp'),
            ('Added checkbox and button behavior to the dialog UI.', 'ui'),
            ('Updated README.md with usage instructions.', 'docs'),
            ('Changed converter tool for dictionary exports.', 'dict'),
            ('Added .gitignore and comparison_report.json baseline data.', 'repo'),
        ]

        for text, expected_scope in cases:
            with self.subTest(text=text):
                self.assertEqual(self.generator.nlp_engine.detect_scope(text), expected_scope)

    def test_extract_action_phrase_es_handles_common_verbs(self):
        cases = [
            ('He corregido el error de apertura de archivos.', 'fix', 'error de apertura de archivos'),
            ('Hemos documentado las opciones de instalación.', 'doc', 'opciones de instalación'),
            ('He mejorado el ranking de bullets.', 'improve', 'ranking de bullets'),
            ('Arreglé el fallo al abrir archivos de audio.', 'fix', 'fallo al abrir archivos de audio'),
            ('Añadimos soporte para karaoke MIDI.', 'add', 'soporte para karaoke midi'),
            ('Documentamos las instrucciones de instalación.', 'doc', 'instrucciones de instalación'),
        ]

        for sentence, expected_action, expected_obj in cases:
            with self.subTest(sentence=sentence):
                action, obj = self.generator.nlp_engine.extract_action_phrase_es(sentence)

                self.assertEqual(action, expected_action)
                self.assertEqual(obj, expected_obj)

    def test_spanish_conjugated_summaries_generate_specific_commits(self):
        cases = [
            ('Arreglé el fallo al abrir archivos de audio.', 'fix(app): corrige fallo al abrir archivos de audio'),
            ('Añadimos soporte para karaoke MIDI.', 'feat(app): agrega soporte para karaoke midi'),
            ('Mejoramos la detección de idioma mixto.', 'feat(nlp): mejora detección de idioma en textos mixtos'),
            ('Documentamos las instrucciones de instalación.', 'docs(docs): documenta instrucciones de instalación'),
        ]

        for text, expected_subject in cases:
            with self.subTest(text=text):
                command = self.render_command(text)

                self.assertIn(f'git commit -m "{expected_subject}"', command)
                self.assertNotIn('actualiza proyecto', command)

    def test_colloquial_spanish_summaries_generate_specific_commits(self):
        cases = [
            ('Le metí soporte para karaoke MIDI.', 'feat(app): agrega soporte para karaoke midi'),
            ('Le puse tests al predictor de commits.', 'test(test): agrega tests para predictor de commits'),
            ('Se arregló el fallo al abrir archivos de audio.', 'fix(app): corrige fallo al abrir archivos de audio'),
            ('Quedó documentada la instalación en README.md.', 'docs(docs): documenta instalación'),
        ]

        for text, expected_subject in cases:
            with self.subTest(text=text):
                command = self.render_command(text)

                self.assertIn(f'git commit -m "{expected_subject}"', command)
                self.assertNotIn('actualiza proyecto', command)
                self.assertNotIn('feat(dict):', command)

    def test_clear_input_button_resets_input_output_and_copy_state(self):
        self.generator.input_text.setPlainText('He creado Roadmap.md.')
        self.generator.output_text.setPlainText('git commit -m "docs(repo): test"')
        self.generator.copy_btn.setEnabled(True)
        self.generator.language_status_label.setText('Idioma detectado: Español')
        self.generator.ml_status_label.setText('ML model: stale')
        self.generator.noise_warning_label.setText('Aviso: ruido.')
        self.generator.noise_warning_label.setVisible(True)

        self.generator.clear_input_text()

        self.assertEqual(self.generator.input_text.toPlainText(), '')
        self.assertEqual(self.generator.output_text.toPlainText(), '')
        self.assertFalse(self.generator.copy_btn.isEnabled())
        self.assertEqual(self.generator.copy_btn.text(), 'Copiar al Portapapeles')
        self.assertFalse(self.generator.noise_warning_label.isVisible())
        self.assertEqual(self.generator.language_status_label.text(), 'Idioma detectado: pendiente')
        self.assertEqual(self.generator.ml_status_label.text(), self.generator.model_status_text())
        self.assertEqual(self.generator.type_override_combo.currentData(), 'auto')
        self.assertEqual(self.generator.scope_override_combo.currentData(), 'auto')

    def test_default_window_geometry_starts_compact_and_resizable(self):
        x, y, width, height = self.generator.DEFAULT_WINDOW_GEOMETRY
        min_width, min_height = self.generator.MINIMUM_WINDOW_SIZE
        geometry = self.generator.geometry()
        minimum_size = self.generator.minimumSize()

        self.assertEqual((geometry.x(), geometry.y(), geometry.width(), geometry.height()), (x, y, width, height))
        self.assertEqual((minimum_size.width(), minimum_size.height()), (min_width, min_height))
        self.assertLessEqual(width, 700)
        self.assertLessEqual(height, 700)

    def test_model_status_text_reports_artifact_state(self):
        status = self.generator.model_status_text()

        self.assertIn('ML model:', status)
        self.assertTrue('ready' in status or 'ml.train_model' in status)

    def test_language_status_updates_after_generating_commit(self):
        self.render_command('He creado Roadmap.md con tareas completadas.')
        self.assertEqual(self.generator.language_status_label.text(), 'Idioma detectado: Español')

        self.render_command('Created Roadmap.md with completed tasks.')
        self.assertEqual(self.generator.language_status_label.text(), 'Idioma detectado: Inglés')

    def test_manual_language_override_controls_generation_language(self):
        self.generator.language_override_combo.setCurrentIndex(
            self.generator.language_override_combo.findData('en')
        )

        command = self.render_command('Updated Roadmap.md con tareas completadas.')

        self.assertEqual(self.generator.language_status_label.text(), 'Idioma detectado: Inglés (manual)')
        self.assertIn('git commit -m "docs(docs): update project roadmap"', command)

    def test_manual_type_and_scope_override_updates_generated_command(self):
        command = self.render_command('He creado Roadmap.md con tareas completadas.')
        self.assertIn('docs(repo): agrega roadmap con seguimiento de progreso', command)

        self.generator.type_override_combo.setCurrentIndex(
            self.generator.type_override_combo.findData('feat')
        )
        self.generator.scope_override_combo.setCurrentIndex(
            self.generator.scope_override_combo.findData('ui')
        )

        updated = self.generator.output_text.toPlainText()
        self.assertIn('git commit -m "feat(ui): agrega roadmap con seguimiento de progreso"', updated)
        self.assertIn('-m "- Documenta funcionalidades completadas y progreso del proyecto"', updated)

    def test_truncate_subject_preserves_word_boundaries(self):
        subject = 'agrega soporte bilingüe y corrige detección de tipo demasiado larga'
        truncated = self.generator.nlp_engine.truncate_subject(subject, limit=50)

        self.assertLessEqual(len(truncated), 50)
        self.assertEqual(truncated, 'agrega soporte bilingüe y corrige detección...')
        self.assertNotIn('tip...', truncated)

    def test_preview_removal_and_truncation_summary_takes_priority_over_tests(self):
        text = """Listo. Eliminé la vista previa del programa y del Roadmap.

También continué con una mejora útil del Roadmap: ahora el `subject` se trunca
respetando límites de palabra, en vez de cortar brutalmente con `subject[:47]`.

Cambios principales:
- Quitada la vista previa de smart_commit_nltk.py.
- Añadido `truncate_subject()` en smart_commit_nltk.py.
- Actualizados tests en tests/test_smart_commit_nltk.py.
- Limpiado Roadmap.md para quitar la vista previa y marcar el truncado como hecho.
- Ajustado README.md.

Verificación:
QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests -v
Resultado: 17 tests OK.
"""
        command = self.render_command(text)

        self.assertIn('git commit -m "refactor(nlp): mejora truncado de subject y elimina vista previa"', command)
        self.assertIn('-m "- Reemplaza el corte fijo de caracteres con truncate_subject()"', command)
        self.assertIn('-m "- Elimina componentes legacy de vista previa de la interfaz"', command)
        self.assertIn('-m "- Actualiza tests para validar truncado en límites de palabra"', command)
        self.assertIn('-m "- Validación: unittest OK, 17 tests pass"', command)
        self.assertNotIn('test(repo): agrega truncate_subject', command)

    def test_type_scope_summary_takes_priority_over_testing_and_roadmap(self):
        text = """Continué con la mejora del Roadmap: ya puedes editar manualmente `type` y `scope` desde la UI antes de copiar.

Añadí dos selectores:

- **Tipo:** `Automático`, `feat`, `fix`, `docs`, `test`, `build`, `ci`, `style`, `refactor`, `perf`
- **Scope:** `Automático`, `app`, `ui`, `docs`, `repo`, `dict`, `tools`, `nlp`, `test`

El programa propone `type/scope`, y si quieres corregirlo manualmente el comando se regenera
al instante manteniendo el subject y los bullets.

Actualicé Roadmap.md, README.md y tests/test_smart_commit_nltk.py.
Resultado: **13 tests OK**.
"""
        command = self.render_command(text)

        self.assertIn('git commit -m "feat(ui): agrega selectores manuales de type y scope"', command)
        self.assertIn('-m "- Regenera el comando en tiempo real al cambiar type/scope"', command)
        self.assertIn('-m "- Conserva subject y body al aplicar ajustes manuales"', command)
        self.assertIn('-m "- Validación: 13 tests pass"', command)
        self.assertNotIn('test(repo): agrega suite', command)

    def test_indirect_validation_phrases_are_included_in_body(self):
        text = """Mejoré el ranking de bullets para ordenar primero los cambios principales
y dejar las verificaciones como soporte del commit.

La suite completa pasa: 18 tests OK.
También verifiqué con py_compile.
"""
        command = self.render_command(text)

        self.assertIn('-m "- Validación: py_compile OK, 18 tests pass"', command)
        self.assertNotIn('git commit -m "test(', command)

    def test_file_mentions_generate_code_test_docs_and_report_bullets(self):
        text = """Mejoré la detección de menciones de archivos dentro del texto pegado.

Cambios:
- Actualicé smart_commit_nltk.py con clasificación de archivos mencionados.
- Actualicé tests/test_smart_commit_nltk.py con una regresión nueva.
- Actualicé README.md y Roadmap.md para documentar el comportamiento.
- Recalculé commit_examples_data/comparison_report.json.

Resultado: 19 tests OK.
"""
        command = self.render_command(text)

        self.assertIn('git commit -m "feat(nlp): mejora detección de menciones de archivos"', command)
        self.assertIn('-m "- Actualiza lógica de código mencionada en el resumen"', command)
        self.assertIn('-m "- Cubre cambios con tests de regresión"', command)
        self.assertIn('-m "- Actualiza documentación mencionada en el resumen"', command)
        self.assertIn('-m "- Actualiza datos o reportes de evaluación"', command)
        self.assertIn('-m "- Validación: 19 tests pass"', command)
        self.assertNotIn('-m "- Actualiza documentación del proyecto"', command)
        self.assertNotIn('-m "- Actualiza Roadmap.md para marcar elementos completados"', command)
        self.assertLess(
            command.index('-m "- Actualiza lógica de código mencionada en el resumen"'),
            command.index('-m "- Validación: 19 tests pass"')
        )

    def test_readme_architecture_summary_generates_rich_docs_commit(self):
        command = self.render_command(README_ARCHITECTURE_SUMMARY)

        self.assertIn('git commit -m "docs(readme): expand project principles and architecture"', command)
        self.assertIn('-m "- Clarify lightweight ML layer and core design constraints"', command)
        self.assertIn('-m "- Document responsibility split between NLTK, utils, and sklearn"', command)
        self.assertIn('-m "- List supported ML labels and local joblib artifact behavior"', command)
        self.assertIn('-m "- Add Debian validation notes and contribution guidelines"', command)
        self.assertIn('-m "- Emphasize do-not-use list for heavy dependencies and APIs"', command)
        self.assertNotIn('refactor(nlp): update readme.md', command)

    def test_ml_metadata_summary_generates_feat_ml_commit(self):
        command = self.render_command(ML_METADATA_SUMMARY)

        self.assertIn('git commit -m "feat(ml): add strict metadata validation in predictor"', command)
        self.assertIn('-m "- Validate model metadata fields before reporting model ready"', command)
        self.assertIn('-m "- Check metadata format version in ml/predictor.py"', command)
        self.assertIn('-m "- Add tests for valid and invalid metadata scenarios"', command)
        self.assertIn('-m "- Update Roadmap.md with progress and suite count"', command)
        self.assertIn('-m "- Validation: 31/32 tests pass, 1 skipped"', command)
        self.assertNotIn('style(dict): add stricter model metadata validation', command)
        self.assertNotIn('-m "- Outline future work for Git, ML, UI, tests, and multilingual support"', command)

    def test_copy_button_confirms_without_modal_text_change(self):
        self.render_command('He creado Roadmap.md con tareas completadas.')
        self.assertEqual(self.generator.copy_btn.text(), 'Copiar al Portapapeles')

        self.generator.copy_to_clipboard()

        self.assertEqual(self.generator.copy_btn.text(), 'Comando copiado al Portapapeles')
        self.assertIn('git commit -m', QApplication.clipboard().text())

    def test_noise_warning_detects_fenced_code_and_embedded_commits(self):
        text = """He creado Roadmap.md.

```bash
git commit -m "docs(repo): embedded" \\
  -m "- Embedded body"
```
"""
        warnings = self.generator.nlp_engine.detect_input_noise_warnings(text)
        self.assertIn('1 bloque(s) de código', warnings)
        self.assertIn('mucho ruido filtrado', warnings)

        self.render_command(text)
        self.assertFalse(self.generator.noise_warning_label.isHidden())
        self.assertIn('bloque(s) de código', self.generator.noise_warning_label.text())

    def test_clear_input_summary_takes_priority_over_tests_and_roadmap(self):
        text = """Listo, implementé el botón **“Limpiar entrada”** en [smart_commit_nltk.py](/tmp/smart_commit_nltk.py).

Al pulsarlo:

- borra el texto de entrada
- borra el commit generado anterior
- desactiva el botón de copiar
- devuelve el foco al cuadro de entrada

También añadí un test en [tests/test_smart_commit_nltk.py](/tmp/tests/test_smart_commit_nltk.py)
y actualicé [Roadmap.md](/tmp/Roadmap.md) marcando la mejora como completada.

Resultado: **8 tests OK**.
"""
        command = self.render_command(text)

        self.assertIn('git commit -m "feat(ui): agrega botón Limpiar entrada en la interfaz"', command)
        self.assertIn('-m "- Implementa lógica para limpiar entrada y commit generado"', command)
        self.assertIn('-m "- Desactiva el botón de copiar al limpiar la entrada"', command)
        self.assertIn('-m "- Validación: 8 tests pass"', command)
        self.assertNotIn('test(repo): agrega suite', command)

    def test_language_status_summary_takes_priority_over_roadmap(self):
        text = """Hecho. Quité el enfoque de “integración con Git” del Roadmap.
También continué con una mejora del programa: añadí en la interfaz una etiqueta de estado
que muestra el idioma detectado:

- `Idioma detectado: pendiente`
- `Idioma detectado: Español`
- `Idioma detectado: Inglés`

Al generar el commit se actualiza automáticamente, y al usar **Limpiar entrada** vuelve a `pendiente`.
Actualicé [Roadmap.md](/tmp/Roadmap.md) marcando como hecho el idioma detectado.
También añadí test de regresión.
Resultado: **10 tests OK**.
"""
        command = self.render_command(text)

        self.assertIn('git commit -m "feat(ui): agrega indicador de idioma detectado"', command)
        self.assertIn('-m "- Presenta estados Pendiente, Español e Inglés"', command)
        self.assertIn('-m "- Enfoca el roadmap en calidad semántica sin integración Git"', command)
        self.assertIn('-m "- Validación: 10 tests pass"', command)
        self.assertNotIn('actualiza roadmap del proyecto', command)

    def test_testing_evaluation_summary_takes_priority_over_bilingual_terms(self):
        text = """Continué con las mejoras del Roadmap y dejé una primera base de testing/evaluación.

- Añadí [tests/test_smart_commit_nltk.py](/tmp/tests/test_smart_commit_nltk.py) con 6 regresiones.
- Actualicé [commit_examples_data/compare_generator.py](/tmp/compare_generator.py) para la nueva firma bilingüe.
- Recalculé [comparison_report.json](/tmp/comparison_report.json).
- Añadí [.gitignore](/tmp/.gitignore) para `__pycache__/`.
- Actualicé [README.md](/tmp/README.md) con comandos de testing/evaluación.
- Actualicé [Roadmap.md](/tmp/Roadmap.md) marcando estas tareas completadas.
- Afiné `clean_input()` para no perder frases en inglés con `detects`, `supports`, `fixes`, `validated`.

La línea base actual quedó: 45 ejemplos, subject similarity `0.446`, body ratio `0.000`.
"""
        command = self.render_command(text)

        self.assertIn('git commit -m "test(repo): agrega suite de regresión y baseline de evaluación"', command)
        self.assertIn('-m "- Añade test_smart_commit_nltk.py con 6 regresiones principales"', command)
        self.assertIn('-m "- Actualiza compare_generator.py para la firma bilingüe"', command)
        self.assertIn('-m "- Establece baseline: 0.446 de similitud de subject"', command)
        self.assertNotIn('feat(nlp): agrega', command)


if __name__ == '__main__':
    unittest.main()
