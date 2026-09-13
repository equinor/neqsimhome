"""Cross-check rendered chapter and figure structure across PDF and HTML."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import sys

BOOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / '.build/python_packages'))
import pymupdf
import yaml
from bs4 import BeautifulSoup

stage = BOOK / '.build/release_candidate/submission'
cfg = yaml.safe_load((BOOK / 'book.yaml').read_text(encoding='utf-8'))
source_chapters = [ch for part in cfg['parts'] for ch in part['chapters']]
expected_labels = []
expected_prerequisites = 0
for number, chapter in enumerate(source_chapters, 1):
    source = (BOOK / 'chapters' / chapter['dir'] / 'chapter.md').read_text(encoding='utf-8')
    expected_prerequisites += len(re.findall(r'^```(?:python|java)[^\n]*\bpattern\b[^\n]*$', source, re.M))
    prose = re.sub(r'^```[^\n]*\n.*?^```[^\n]*(?:\n|$)', '', source, flags=re.M | re.S)
    for index, _ in enumerate(re.finditer(r'!\[[^\]]*\]\([^)]+\)', prose), 1):
        expected_labels.append(f'{number}.{index}')
typst = (stage / 'book.typ').read_text(encoding='utf-8')
chapters = re.findall(r'^= (.+)$', typst, flags=re.M)
soup = BeautifulSoup((stage / 'book.html').read_text(encoding='utf-8'), 'html.parser')
html_labels = []
for caption in soup.select('figcaption'):
    match = re.search(r'Figure\s+(\d+\.\d+)', caption.get_text(' ', strip=True))
    if match:
        html_labels.append(match[1])
with pymupdf.open(stage / 'book.pdf') as doc:
    page_texts = [page.get_text() for page in doc]
    text = '\n'.join(page_texts)
    # Captions begin their own text block; code strings and prose references
    # also contain "Figure 24.2:" and must not count as placed illustrations.
    pdf_labels = []
    for page in doc:
        for block in page.get_text('blocks'):
            match = re.match(r'Figure\s+(\d+\.\d+):', block[4].strip())
            if match:
                pdf_labels.append(match[1])
math_fixes = json.loads((BOOK / 'verification/pdf_final/renderer_math_reference_fix.json').read_text(encoding='utf-8'))
math_checks = []
def searchable_prose(value):
    # PDF font maps may expose a curly apostrophe as a replacement character.
    # Match the unchanged words; the Typst check still uses the exact anchor.
    return ' '.join(re.sub(r'[^\w\s]', '', value).split()).casefold()

for fix in math_fixes['actual_affected_prose_checks']:
    anchor = fix['anchor'].casefold()
    lines = [line for line in typst.splitlines() if anchor in line.casefold()]
    pages = [i + 1 for i, page in enumerate(page_texts) if searchable_prose(anchor) in searchable_prose(page)]
    math_checks.append({'anchor': fix['anchor'], 'pdf_pages': pages,
                        'passed': bool(lines) and bool(pages) and all('\\$' not in line for line in lines)})
residue = [token for token in ('{.unnumbered', '{.unlisted') if token in text or token in soup.get_text()]
report = {'pdf_sha256': hashlib.sha256((stage / 'book.pdf').read_bytes()).hexdigest(),
          'numbered_chapters': chapters, 'numbered_chapter_count': len(chapters),
          'pdf_caption_count': len(pdf_labels), 'html_caption_count': len(html_labels),
          'expected_source_caption_count': len(expected_labels),
          'expected_prerequisite_notes': expected_prerequisites,
          'source_only_labels': list((Counter(expected_labels) - Counter(pdf_labels)).elements()),
          'unexpected_rendered_labels': list((Counter(pdf_labels) - Counter(expected_labels)).elements()),
          'pdf_only_labels': list((Counter(pdf_labels) - Counter(html_labels)).elements()),
          'html_only_labels': list((Counter(html_labels) - Counter(pdf_labels)).elements()),
          'invalid_figure_chapters': [x for x in pdf_labels if not 1 <= int(x.split('.')[0]) <= 35],
          'rendered_prerequisite_notes': text.count('Integration pattern prerequisites:'),
          'orphan_heading_attributes': residue, 'repaired_inline_math': math_checks}
report['passed'] = (len(chapters) == len(source_chapters) == 35 and Counter(pdf_labels) == Counter(expected_labels)
    and Counter(pdf_labels) == Counter(html_labels) and not report['invalid_figure_chapters']
    and report['rendered_prerequisite_notes'] == expected_prerequisites
    and not residue and all(row['passed'] for row in math_checks))
(BOOK / 'verification/publication_structure_check.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
raise SystemExit(0 if report['passed'] else 1)
