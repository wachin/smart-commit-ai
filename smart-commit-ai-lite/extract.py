import sys

with open('smart_commit_nltk.py', 'r') as f:
    lines = f.readlines()

# We need everything from `def clean_summary_text` to just before `def generate_commit`
start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.startswith('    def clean_summary_text(self, text):'):
        start_idx = i
    if line.startswith('    def generate_commit(self):'):
        end_idx = i

if start_idx != -1 and end_idx != -1:
    with open('utils/nlp_heuristics.py', 'w') as out:
        out.write("import nltk\n")
        out.write("try:\n")
        out.write("    import regex as re\n")
        out.write("except ImportError:\n")
        out.write("    import re\n\n")
        out.write("from utils.input_cleanup import (\n")
        out.write("    clean_input as clean_pasted_input,\n")
        out.write("    clean_summary_text as clean_summary_snippet,\n")
        out.write("    detect_input_noise_warnings as detect_pasted_input_noise_warnings,\n")
        out.write("    strip_markdown_noise as strip_pasted_markdown_noise,\n")
        out.write(")\n")
        out.write("from utils.language import (\n")
        out.write("    detect_language as detect_input_language,\n")
        out.write("    language_signal_text as get_language_signal_text,\n")
        out.write(")\n")
        out.write("from utils.type_scope import (\n")
        out.write("    DetectionContext,\n")
        out.write("    detect_scope as detect_commit_scope,\n")
        out.write("    select_commit_type as select_conventional_commit_type,\n")
        out.write(")\n\n\n")
        out.write("class NLPEngine:\n")
        for line in lines[start_idx:end_idx]:
            out.write(line)

print("Extraction complete.")
