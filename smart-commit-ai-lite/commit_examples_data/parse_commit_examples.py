import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MD_PATH = ROOT.parent / 'COMMIT_GENERATION_EXAMPLES.md'
JSON_PATH = ROOT / 'examples.json'
DB_PATH = ROOT / 'examples.db'
ENTRIES_DIR = ROOT / 'entries'

ENTRY_SEPARATOR = r'^---$'


def slugify(text: str) -> str:
    slug = re.sub(r'[^0-9a-z]+', '-', text.lower()).strip('-')
    return slug[:80]


def parse_markdown(text: str):
    sections = re.split(r'(?m)^---\s*$', text)
    entries = []

    for sec in sections:
        title_match = re.search(r'^##\s+(.*?)\s*$', sec, re.MULTILINE)
        if not title_match:
            continue

        title = title_match.group(1).strip()
        orig_match = re.search(r'\*\*Texto Original:\*\*\n((?:>.*\n)+)', sec)
        cmd_match = re.search(r'\*\*Comando Generado:\*\*\n```bash\n(.*?)```', sec, re.S)
        if not orig_match or not cmd_match:
            continue

        orig_lines = [line[2:].strip() for line in orig_match.group(1).splitlines() if line.startswith('>')]
        original_text = ' '.join(orig_lines)

        raw_command = cmd_match.group(1).strip()
        subject_match = re.search(r'git commit -m "([^"]+)"', raw_command)
        expected_subject = subject_match.group(1).strip() if subject_match else ''
        expected_bodies = re.findall(r'-m "(.*)"', raw_command)
        expected_body_lines = expected_bodies[1:] if len(expected_bodies) > 1 else []

        entries.append({
            'title': title,
            'original_text': original_text,
            'expected_subject': expected_subject,
            'expected_body_lines': expected_body_lines,
            'expected_command': raw_command,
        })

    return entries


def save_json(entries):
    with JSON_PATH.open('w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def save_sqlite(entries):
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        '''
        CREATE TABLE examples (
            id INTEGER PRIMARY KEY,
            title TEXT,
            original_text TEXT,
            expected_subject TEXT,
            expected_body_count INTEGER,
            expected_body_lines TEXT,
            expected_command TEXT
        )
        '''
    )
    conn.execute('CREATE INDEX idx_title ON examples(title)')

    for index, entry in enumerate(entries, start=1):
        conn.execute(
            '''INSERT INTO examples
               (title, original_text, expected_subject, expected_body_count, expected_body_lines, expected_command)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (
                entry['title'],
                entry['original_text'],
                entry['expected_subject'],
                len(entry['expected_body_lines']),
                json.dumps(entry['expected_body_lines'], ensure_ascii=False),
                entry['expected_command'],
            )
        )

    conn.commit()
    conn.close()


def save_entries(entries):
    ENTRIES_DIR.mkdir(parents=True, exist_ok=True)
    for index, entry in enumerate(entries, start=1):
        slug = slugify(entry['title']) or f'entry-{index:02d}'
        path = ENTRIES_DIR / f'{index:02d}-{slug}.json'
        with path.open('w', encoding='utf-8') as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    md_text = MD_PATH.read_text(encoding='utf-8')
    entries = parse_markdown(md_text)
    print(f'Parsed {len(entries)} entries from {MD_PATH.name}')
    save_json(entries)
    save_sqlite(entries)
    save_entries(entries)
    print(f'Wrote {JSON_PATH.name}, {DB_PATH.name}, and {len(entries)} entry files to {ENTRIES_DIR}')
