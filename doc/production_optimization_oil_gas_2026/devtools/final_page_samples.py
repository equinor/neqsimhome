"""Render final contents, equipment, advanced code and backmatter samples."""
from pathlib import Path
import sys
import re
import json
import hashlib

BOOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / '.build/python_packages'))
import pymupdf

doc = pymupdf.open(BOOK / '.build/release_candidate/submission/book.pdf')
selected = set(range(1, min(20, len(doc)) + 1))
geometry = json.loads((BOOK / 'verification/pdf_final/geometry_report.json').read_text(encoding='utf-8'))
assert geometry['sha256'] == hashlib.sha256((BOOK / '.build/release_candidate/submission/book.pdf').read_bytes()).hexdigest()
selected.update(geometry.get('layout_review_required_pages', []))
structure = json.loads((BOOK / 'verification/publication_structure_check.json').read_text(encoding='utf-8'))
assert structure['pdf_sha256'] == geometry['sha256']
for row in structure.get('repaired_inline_math', []):
    selected.update(row['pdf_pages'])
selected.update(range(max(1,len(doc)-4),len(doc)+1))
for level, title, page in doc.get_toc():
    if title.strip().casefold() == 'glossary':
        selected.update(range(max(1, page - 1), len(doc) + 1))
    if level == 1 and any(needle in title for needle in ['Gas Compression Systems', 'Onshore', 'Glossary', 'Case Studies']):
        selected.add(page)
        selected.add(page + 1)
needles = ['NIST reference', 'Horner', 'Brayton', 'Pareto', 'saturation envelope',
           'first-stage separator', 'RIGOROUS_CONVERGED', 'fixed-composition',
           'collection of synthetic', 'resource-depletion', 'time-step',
           '350000', '5.3 Natural Gas Processing', 'Conditional rate changes from three',
           'outside template map', '171.167', 'LP allocation',
           'Diagnostic VFP', 'total standard liquid',
           'The incomplete plotted trace alone', 'The contour curvature is prescribed',
           'No speed lines or constant', 'For a common time interval']
math_fixes = json.loads((BOOK / 'verification/pdf_final/renderer_math_reference_fix.json').read_text(encoding='utf-8'))
needles.extend(row['anchor'] for row in math_fixes['actual_affected_prose_checks'])
needles.extend(['Circulation here means', 'The prescribed-removal example'])
found = {}
chapter_figure_samples = {}
for i, page in enumerate(doc):
    content = page.get_text()
    for block in page.get_text('blocks'):
        match=re.match(r'Figure\s+(\d+)\.(\d+):',block[4].strip())
        if match:
            chapter=int(match[1])
            if chapter not in chapter_figure_samples or chapter in (10,11,14,15,17,18,19,21,22,24,28,30,32,33,34):
                selected.add(i+1)
                chapter_figure_samples.setdefault(chapter,[]).append(i+1)
    for needle in needles:
        if needle not in found and needle.casefold() in re.sub(r'\s+', ' ', content).casefold():
            found[needle] = i + 1
            selected.add(i + 1)
            if i + 1 < len(doc):
                selected.add(i + 2)
for page in sorted(selected):
    doc[page - 1].get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).save(BOOK / f'verification/pdf_final/sample_{page:04d}.png')
print(sorted(selected))
(BOOK / 'verification/pdf_final/scientific_sample_manifest.json').write_text(
    json.dumps({'pdf_sha256': hashlib.sha256((BOOK / '.build/release_candidate/submission/book.pdf').read_bytes()).hexdigest(),
                'selected_pages': sorted(selected), 'matched_terms': found,
                'chapter_figure_samples':chapter_figure_samples,
                'rendered_images': [{'page':page,'path':str(BOOK / f'verification/pdf_final/sample_{page:04d}.png'),
                                    'sha256':hashlib.sha256((BOOK / f'verification/pdf_final/sample_{page:04d}.png').read_bytes()).hexdigest()}
                                    for page in sorted(selected)]}, indent=2), encoding='utf-8')
