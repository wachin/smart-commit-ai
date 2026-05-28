import sys
from PyQt6.QtWidgets import QApplication
from utils.nlp_heuristics import NLPEngine

text = """
We kept the development moving and took the first real WRK step.

In [file.py](/home/wachin/Dev/dmidiplayer/drumstick/drumstick_py/file.py), the loader now deliberately recognizes Cakewalk WRK input and raises a specific error:

`Cakewalk WRK files are not supported yet`

So `.wrk` files no longer fall through as generic “not a Standard MIDI File” failures. It’s a small change, but it gives the app a much clearer contract and sets up the real parser work later.

I added coverage in [test_smf_parser.py](/home/wachin/Dev/dmidiplayer/tests/test_smf_parser.py) for a WRK-like header and marked the roadmap skeleton item complete in [Roadmap.md](/home/wachin/Dev/dmidiplayer/Roadmap.md).

Verification is clean:
- focused parser suite passed: `19 tests OK`
- full test suite passed: `208 tests OK`
- `compileall` passed

A strong next move is the actual WRK minimum event model, or we can swing back to the UI and keep surfacing more metadata in places like the playlist and main window.
"""

engine = NLPEngine()
verb, obj, language = engine.analyze_with_nltk(text)
scope = engine.detect_scope(text)
commit_type = engine.select_commit_type(text, verb, obj)
subject_text = engine.format_subject(verb, obj, language)
subject = f'{commit_type}({scope}): {subject_text}'

body_lines = engine.generate_body_lines(engine.clean_input(text), language)

print("SUBJECT:", subject)
for b in body_lines:
    print("BODY:", b)
