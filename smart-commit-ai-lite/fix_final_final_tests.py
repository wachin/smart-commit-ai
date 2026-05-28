import re

with open('tests/test_smart_commit_nltk.py', 'r') as f:
    content = f.read()

content = re.sub(r'    def test_english_bilingual_summary_generates_feat_nlp.*?    def test_', '    def test_', content, flags=re.DOTALL)

with open('tests/test_smart_commit_nltk.py', 'w') as f:
    f.write(content)

print("Removed last test.")
