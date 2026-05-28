import sys

with open('smart_commit_nltk.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False

# Add import at the top
for i, line in enumerate(lines):
    if line.startswith('from utils.type_scope import'):
        new_lines.append(line)
        continue
    if 'select_commit_type as select_conventional_commit_type,' in line:
        new_lines.append(line)
        continue
    if line.strip() == ')' and 'select_conventional_commit_type' in lines[i-1]:
        new_lines.append(line)
        new_lines.append("from utils.nlp_heuristics import NLPEngine\n")
        continue

    # Add initialization in __init__
    if 'self.ml_predictor = SklearnCommitPredictor() if SklearnCommitPredictor else None' in line:
        new_lines.append(line)
        new_lines.append("        self.nlp_engine = NLPEngine()\n")
        continue

    # Skip the extracted methods
    if line.startswith('    def clean_summary_text(self, text):'):
        skip = True
    if line.startswith('    def generate_commit(self):'):
        skip = False

    # Replacements in the remaining code
    if not skip:
        # replace internal calls with self.nlp_engine calls
        mod_line = line
        mod_line = mod_line.replace('self.update_noise_warning(text)', 'self.update_noise_warning(text)') # wait, update_noise_warning is kept
        mod_line = mod_line.replace('self.detect_input_noise_warnings(text)', 'self.nlp_engine.detect_input_noise_warnings(text)')
        mod_line = mod_line.replace('self.analyze_with_nltk(text, forced_language)', 'self.nlp_engine.analyze_with_nltk(text, forced_language)')
        mod_line = mod_line.replace('self.detect_scope(text)', 'self.nlp_engine.detect_scope(text)')
        mod_line = mod_line.replace('self.format_subject(verb, obj, language)', 'self.nlp_engine.format_subject(verb, obj, language)')
        mod_line = mod_line.replace('self.truncate_subject(subject)', 'self.nlp_engine.truncate_subject(subject)')
        mod_line = mod_line.replace('self.predict_commit_type(text, verb, obj, language)', 'self.nlp_engine.predict_commit_type(text, verb, obj, language)')
        mod_line = mod_line.replace('self.generate_body_lines(self.clean_input(text), language)', 'self.nlp_engine.generate_body_lines(self.nlp_engine.clean_input(text), language)')
        
        new_lines.append(mod_line)

with open('smart_commit_nltk.py', 'w') as f:
    f.writelines(new_lines)

print("Patch applied.")
