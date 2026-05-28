import sys

# 1. Read smart_commit_nltk.py and insert predict_commit_type
with open('smart_commit_nltk.py', 'r') as f:
    lines = f.readlines()

predict_method = """
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
"""

# Insert before generate_commit
out_lines = []
for line in lines:
    if line.startswith('    def generate_commit(self):'):
        out_lines.append(predict_method)
    if 'self.nlp_engine.predict_commit_type' in line:
        line = line.replace('self.nlp_engine.predict_commit_type', 'self.predict_commit_type')
    out_lines.append(line)

with open('smart_commit_nltk.py', 'w') as f:
    f.writelines(out_lines)

# 2. Remove predict_commit_type from utils/nlp_heuristics.py
with open('utils/nlp_heuristics.py', 'r') as f:
    lines = f.readlines()

out_lines = []
skip = False
for line in lines:
    if line.startswith('    def predict_commit_type(self, text, subject_verb, subject_obj, language=None):'):
        skip = True
    elif skip and line.startswith('    def extract_validation_bullet(self, text, language=\'en\'):'):
        skip = False
    
    if not skip:
        out_lines.append(line)

with open('utils/nlp_heuristics.py', 'w') as f:
    f.writelines(out_lines)

print("Fix applied.")
