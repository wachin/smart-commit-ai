import sys
import re

with open('utils/nlp_heuristics.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False

for i, line in enumerate(lines):
    # Remove colloquialisms from extract_action_phrase
    if "r'\\bwe\\s+got\\s+(.+?)\\s+over the line'" in line:
        continue
    if "r'\\bwe\\s+landed\\s+(.+?)(?:\\s+with|\\s+\\.|$)'" in line:
        continue
    if "r'\\bwe\\s+carried\\s+(.+?)\\s+one step further'" in line:
        continue
    if "r'\\bwe\\s+kept\\s+(.+?)\\s+moving'" in line:
        continue
    if "r'\\bwe\\s+made\\s+(.+?)\\s+much nicer to use'" in line:
        continue

    # Removing the massive hardcoded body rules in generate_body_lines
    if "if 'utils/preprocessing.py' in text_lower or 'vectorization' in text_lower or 'vectorizer' in text_lower:" in line:
        skip = True
    elif skip and "add_validation_bullet()" in line and "return bullets" in lines[i+1]:
        skip = False
        continue

    if "if self.is_spanish_verb_expansion_summary(text_lower):" in line:
        skip = True
    elif skip and "add_validation_bullet()" in line and "return bullets" in lines[i+1]:
        skip = False
        continue
        
    if "if self.is_mixed_language_nlp_summary(text_lower):" in line:
        skip = True
    elif skip and "add_validation_bullet()" in line and "return bullets" in lines[i+1]:
        skip = False
        continue
        
    if "has_bilingual_nlp = any(k in text_lower for k in ['bilingual', 'spanish', 'english', 'tokenization', 'spanish verbs'])" in line:
        skip = True
    elif skip and "if 'track-aware' in text_lower or 'source track' in text_lower:" in line:
        # Stop skipping after the track-aware block
        pass
    elif skip and "add_bullet('- Add track-aware filtering for lyrics events')" in line:
        skip = False
        continue

    if not skip:
        new_lines.append(line)

# Let's write back
with open('utils/nlp_heuristics.py', 'w') as f:
    f.writelines(new_lines)

print("Patching complete.")
