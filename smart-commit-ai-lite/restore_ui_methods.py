import sys

with open('smart_commit_nltk.py', 'r') as f:
    smart_lines = f.readlines()

ui_methods = """
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
        return " \\\n".join(cmd_parts)

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

"""

out_lines = []
for line in smart_lines:
    if line.startswith('    def predict_commit_type('):
        out_lines.append(ui_methods)
    out_lines.append(line)

with open('smart_commit_nltk.py', 'w') as f:
    f.writelines(out_lines)

# Also remove from utils/nlp_heuristics.py
with open('utils/nlp_heuristics.py', 'r') as f:
    nlp_lines = f.readlines()

out_lines = []
skip = False
for line in nlp_lines:
    if line.startswith('    def update_noise_warning(self, text):'):
        skip = True
    elif skip and line.startswith('    def detect_language(self, text):'):
        skip = False
    
    if line.startswith('    def selected_language_override(self):'):
        skip = True
    elif skip and line.startswith('    def analyze_with_nltk(self, text, forced_language=None):'):
        skip = False
        
    if line.startswith('    def update_language_status(self, language, manual=False):'):
        skip = True
    elif skip and line.startswith('    def detection_context(self, text_lower):'):
        skip = False

    if not skip:
        out_lines.append(line)

with open('utils/nlp_heuristics.py', 'w') as f:
    f.writelines(out_lines)

print("Restored UI methods to NLPCommitGenerator and removed from NLPEngine.")
