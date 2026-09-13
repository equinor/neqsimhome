from pathlib import Path
import json
import re
import sys

BOOK = Path(__file__).resolve().parents[1]
FENCES = re.compile(r'^```(python|java)\s*\n(.*?)^```', re.M | re.S)
blocks = []
for chapter in sorted((BOOK / 'chapters').glob('*/chapter.md'))[:18]:
    text = chapter.read_text(encoding='utf-8')
    found = list(FENCES.finditer(text))
    print(chapter.parent.name, len(found), {language: sum(m[1] == language for m in found) for language in ('python', 'java')})
    for index, match in enumerate(found, 1):
        blocks.append({'chapter': chapter.parent.name, 'index': index, 'line': text[:match.start()].count('\n') + 1, 'language': match[1], 'code': match[2]})
(BOOK / 'verification').mkdir(exist_ok=True)
(BOOK / 'verification' / 'foundations_blocks.json').write_text(json.dumps(blocks, indent=2), encoding='utf-8')
if len(sys.argv) > 1:
    for block in blocks:
        if block['chapter'].startswith(sys.argv[1]):
            print('\nBLOCK', block['index'], 'LINE', block['line'], block['language'])
            print(block['code'])
