import sys
import glob

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Replacements for test files
    methods = [
        'extract_action_phrase',
        'extract_action_phrase_es',
        'clean_input',
        'strip_markdown_noise',
        'truncate_subject',
        'analyze_with_nltk',
        'extract_file_mentions',
        'generate_body_lines',
        'detect_language',
        'language_signal_text',
        'detect_scope',
        'select_commit_type'
    ]

    for method in methods:
        content = content.replace(f'self.generator.{method}', f'self.generator.nlp_engine.{method}')
        content = content.replace(f'generator.{method}', f'generator.nlp_engine.{method}')

    with open(filepath, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    for filepath in glob.glob('tests/*.py'):
        patch_file(filepath)
    patch_file('commit_examples_data/compare_generator.py')
    print("Test files patched successfully.")
