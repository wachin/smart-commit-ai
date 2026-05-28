import sys
import time
import threading
import contextlib
import io
import os
import nltk
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QTextEdit, QPushButton, QLabel, QMessageBox,
                             QHBoxLayout, QGroupBox, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QClipboard, QIcon

try:
    import regex as re
except ImportError:  # pragma: no cover - Debian package is recommended, stdlib keeps app usable
    import re

try:
    from ml.predictor import SklearnCommitPredictor
except Exception:  # pragma: no cover - ML is intentionally optional
    SklearnCommitPredictor = None

from utils.input_cleanup import (
    clean_input as clean_pasted_input,
    clean_summary_text as clean_summary_snippet,
    detect_input_noise_warnings as detect_pasted_input_noise_warnings,
    strip_markdown_noise as strip_pasted_markdown_noise,
)
from utils.language import (
    detect_language as detect_input_language,
    language_signal_text as get_language_signal_text,
)
from utils.type_scope import (
    COMMIT_TYPE_OPTIONS,
    DetectionContext,
    SCOPE_OPTIONS,
    detect_scope as detect_commit_scope,
    select_commit_type as select_conventional_commit_type,
)
from utils.nlp_heuristics import NLPEngine

# ==========================================
# 🔄 MEJORA: Descarga con Spinner y Feedback
# ==========================================
def ensure_nltk_data():
    required_packages = [
        ('punkt', 'tokenizers/punkt'),
        ('averaged_perceptron_tagger', 'taggers/averaged_perceptron_tagger')
    ]

    missing = []
    for pkg, path in required_packages:
        try:
            nltk.data.find(path)
        except LookupError:
            missing.append(pkg)

    if not missing:
        return

    print("\n📦 First-time setup: Downloading NLTK language models (~57 MB)...")
    print("⏳ This is a one-time process. Depending on your connection, it may take 2-10 minutes.")
    print("🔄 The terminal may appear idle, but the download is running in the background...\n")

    # Spinner animation thread
    stop_spinner = threading.Event()
    def spinner():
        symbols = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        idx = 0
        while not stop_spinner.is_set():
            sys.stdout.write(f"\r  {symbols[idx % len(symbols)]} Downloading and extracting data...")
            sys.stdout.flush()
            time.sleep(0.15)
            idx += 1
        sys.stdout.write("\r  ✅ Download complete! Launching application...\n")
        sys.stdout.flush()

    spinner_thread = threading.Thread(target=spinner)
    spinner_thread.start()

    # Download thread (suppresses NLTK's own print statements)
    download_done = threading.Event()
    def download_task():
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                for pkg in missing:
                    nltk.download(pkg, quiet=True)
        except Exception as e:
            print(f"\n❌ Error downloading NLTK data: {e}")
            sys.exit(1)
        download_done.set()

    download_thread = threading.Thread(target=download_task)
    download_thread.start()
    download_thread.join()

    stop_spinner.set()
    spinner_thread.join()

# Ejecutar verificación antes de iniciar la GUI
ensure_nltk_data()

class NLPCommitGenerator(QMainWindow):
    # Geometry order: x position, y position, width, height.
    DEFAULT_WINDOW_GEOMETRY = (90, 30, 660, 690)
    MINIMUM_WINDOW_SIZE = (620, 620)
    MIN_ML_TYPE_CONFIDENCE = 0.4

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Commits - NLTK Enhanced")
        self.setGeometry(*self.DEFAULT_WINDOW_GEOMETRY)
        self.setMinimumSize(*self.MINIMUM_WINDOW_SIZE)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "icons", "smart-commit-icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.detected_commit_type = None
        self.detected_scope = None
        self.current_subject = ""
        self.current_body_lines = []
        self.ml_predictor = SklearnCommitPredictor() if SklearnCommitPredictor else None
        self.nlp_engine = NLPEngine()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        instr_label = QLabel("Pega aquí el resumen. El sistema usará NLTK para analizar la gramática:")
        instr_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(instr_label)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Ejemplo: We pushed the Pianola work into real interaction...")
        self.input_text.setFont(QFont("Courier New", 9))
        layout.addWidget(self.input_text)

        self.noise_warning_label = QLabel("")
        self.noise_warning_label.setFont(QFont("Arial", 9))
        self.noise_warning_label.setStyleSheet("color: #B26A00; padding: 4px 0;")
        self.noise_warning_label.setVisible(False)
        layout.addWidget(self.noise_warning_label)

        self.language_status_label = QLabel("Idioma detectado: pendiente")
        self.language_status_label.setFont(QFont("Arial", 9))
        self.language_status_label.setStyleSheet("color: #555; padding: 4px 0;")

        language_layout = QHBoxLayout()
        language_layout.addWidget(self.language_status_label)

        language_mode_label = QLabel("Modo de idioma:")
        language_mode_label.setFont(QFont("Arial", 9))
        language_layout.addWidget(language_mode_label)

        self.language_override_combo = QComboBox()
        self.language_override_combo.addItem("Automático", "auto")
        self.language_override_combo.addItem("Español", "es")
        self.language_override_combo.addItem("Inglés", "en")
        self.language_override_combo.setFont(QFont("Arial", 9))
        language_layout.addWidget(self.language_override_combo)
        layout.addLayout(language_layout)

        self.ml_status_label = QLabel(self.model_status_text())
        self.ml_status_label.setFont(QFont("Arial", 9))
        self.ml_status_label.setStyleSheet("color: #555; padding: 4px 0;")
        layout.addWidget(self.ml_status_label)

        commit_meta_layout = QHBoxLayout()

        type_label = QLabel("Tipo:")
        type_label.setFont(QFont("Arial", 9))
        commit_meta_layout.addWidget(type_label)

        self.type_override_combo = QComboBox()
        self.type_override_combo.addItem("Automático", "auto")
        for commit_type in COMMIT_TYPE_OPTIONS:
            self.type_override_combo.addItem(commit_type, commit_type)
        self.type_override_combo.setFont(QFont("Arial", 9))
        self.type_override_combo.currentIndexChanged.connect(self.refresh_commit_command_from_controls)
        commit_meta_layout.addWidget(self.type_override_combo)

        scope_label = QLabel("Scope:")
        scope_label.setFont(QFont("Arial", 9))
        commit_meta_layout.addWidget(scope_label)

        self.scope_override_combo = QComboBox()
        self.scope_override_combo.addItem("Automático", "auto")
        for scope in SCOPE_OPTIONS:
            self.scope_override_combo.addItem(scope, scope)
        self.scope_override_combo.setFont(QFont("Arial", 9))
        self.scope_override_combo.currentIndexChanged.connect(self.refresh_commit_command_from_controls)
        commit_meta_layout.addWidget(self.scope_override_combo)
        layout.addLayout(commit_meta_layout)

        action_btn_layout = QHBoxLayout()

        self.generate_btn = QPushButton("Generar Commit con NLTK")
        self.generate_btn.clicked.connect(self.generate_commit)
        self.generate_btn.setStyleSheet(
            "QPushButton { background-color: #673AB7; color: white; padding: 12px; font-weight: bold; font-size: 14px; }"
            "QPushButton:hover { background-color: #512DA8; }"
        )
        action_btn_layout.addWidget(self.generate_btn)

        self.clear_input_btn = QPushButton("Limpiar entrada")
        self.clear_input_btn.clicked.connect(self.clear_input_text)
        self.clear_input_btn.setStyleSheet(
            "QPushButton { background-color: #607D8B; color: white; padding: 12px; font-weight: bold; font-size: 14px; }"
            "QPushButton:hover { background-color: #455A64; }"
        )
        action_btn_layout.addWidget(self.clear_input_btn)
        layout.addLayout(action_btn_layout)

        output_group = QGroupBox("Comando Git Generado:")
        output_layout = QVBoxLayout()

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier New", 10))
        self.output_text.setStyleSheet("background-color: #2b2b2b; color: #f8f8f2;")
        output_layout.addWidget(self.output_text)

        btn_layout = QHBoxLayout()
        self.copy_btn = QPushButton("Copiar al Portapapeles")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setEnabled(False)
        self.copy_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; padding: 8px; font-weight: bold; }"
        )
        btn_layout.addWidget(self.copy_btn)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        layout.addLayout(btn_layout)



    def update_noise_warning(self, text):
        warnings = self.nlp_engine.detect_input_noise_warnings(text)
        if warnings:
            self.noise_warning_label.setText("Aviso: se detectó " + ", ".join(warnings) + ".")
            self.noise_warning_label.setVisible(True)
        else:
            self.noise_warning_label.setText("")
            self.noise_warning_label.setVisible(False)

    def update_language_status(self, language, manual=False):
        labels = {
            'es': 'Idioma detectado: Español',
            'en': 'Idioma detectado: Inglés'
        }
        text = labels.get(language, 'Idioma detectado: pendiente')
        if manual and language in {'es', 'en'}:
            text += ' (manual)'
        self.language_status_label.setText(text)

    def selected_commit_type(self):
        selected = self.type_override_combo.currentData()
        if selected and selected != 'auto':
            return selected
        return self.detected_commit_type

    def selected_scope(self):
        selected = self.scope_override_combo.currentData()
        if selected and selected != 'auto':
            return selected
        return self.detected_scope

    def build_commit_command(self):
        commit_type = self.selected_commit_type()
        scope = self.selected_scope()
        if not commit_type or not scope or not self.current_subject:
            return ""

        cmd_parts = [f'git commit -m "{commit_type}({scope}): {self.current_subject}"']
        for line in self.current_body_lines:
            if len(line) > 72:
                line = line[:69] + "..."
            cmd_parts.append(f'  -m "{line}"')
        return " \
".join(cmd_parts)

    def refresh_commit_command_from_controls(self):
        command = self.build_commit_command()
        if command:
            self.output_text.setText(command)
            self.copy_btn.setText("Copiar al Portapapeles")
            self.copy_btn.setEnabled(True)

    def selected_language_override(self):
        selected = self.language_override_combo.currentData()
        return selected if selected in {'es', 'en'} else None

    def model_status_text(self):
        if not self.ml_predictor:
            return "ML model: sklearn predictor unavailable"

        status = self.ml_predictor.status(try_load=False)
        if status.ready:
            return "ML model: ready"
        return f"ML model: {status.message}; run python3 -m ml.train_model"

    def predict_commit_type(self, text, subject_verb, subject_obj, language=None):
        heuristic_type = self.nlp_engine.select_commit_type(text, subject_verb, subject_obj)
        if self.ml_predictor:
            prediction = self.ml_predictor.predict(text, language)
            if (
                prediction
                and prediction.commit_type
                and prediction.confidence is not None
                and prediction.confidence >= self.MIN_ML_TYPE_CONFIDENCE
            ):
                return prediction.commit_type
        return heuristic_type
    def generate_commit(self):
        text = self.input_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Advertencia", "Por favor pega el texto primero.")
            return

        try:
            self.update_noise_warning(text)
            forced_language = self.selected_language_override()
            verb, obj, language = self.nlp_engine.analyze_with_nltk(text, forced_language)
            self.update_language_status(language, manual=forced_language is not None)
            scope = self.nlp_engine.detect_scope(text)
            subject = self.nlp_engine.format_subject(verb, obj, language)
            subject = self.nlp_engine.truncate_subject(subject)

            commit_type = self.predict_commit_type(text, verb, obj, language)
            body_lines = self.nlp_engine.generate_body_lines(self.nlp_engine.clean_input(text), language)
            self.detected_commit_type = commit_type
            self.detected_scope = scope
            self.current_subject = subject
            self.current_body_lines = body_lines
            self.refresh_commit_command_from_controls()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error analizando con NLTK: {str(e)}")

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_text.toPlainText())
        self.copy_btn.setText("Comando copiado al Portapapeles")

    def clear_input_text(self):
        self.input_text.clear()
        self.output_text.clear()
        self.copy_btn.setEnabled(False)
        self.copy_btn.setText("Copiar al Portapapeles")
        self.noise_warning_label.setText("")
        self.noise_warning_label.setVisible(False)
        self.detected_commit_type = None
        self.detected_scope = None
        self.current_subject = ""
        self.current_body_lines = []
        self.language_override_combo.setCurrentIndex(0)
        self.type_override_combo.setCurrentIndex(0)
        self.scope_override_combo.setCurrentIndex(0)
        self.language_status_label.setText("Idioma detectado: pendiente")
        self.ml_status_label.setText(self.model_status_text())
        self.input_text.setFocus()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NLPCommitGenerator()
    window.show()
    sys.exit(app.exec())
