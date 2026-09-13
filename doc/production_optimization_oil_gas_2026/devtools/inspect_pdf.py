"""Audit complete PDF text bounds and render representative pages for visual review."""
from pathlib import Path
import json
import hashlib
import sys
import argparse
import re

BOOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / '.build' / 'python_packages'))
sys.stdout.reconfigure(encoding='utf-8')
import pymupdf

def layout_diagnostics(page, page_number, intentional_sparse_pages):
    """Surface sparse pages and intersecting text lines for visual review.

    The central7%-92% vertical band excludes typical running furniture. These
    heuristics do not recognize all valid typography or certify page quality.
    """
    top, bottom = 0.07 * page.rect.height, 0.92 * page.rect.height
    body, furniture, collision_lines = [], [], []
    data = page.get_text('dict', flags=pymupdf.TEXTFLAGS_DICT & ~pymupdf.TEXT_PRESERVE_IMAGES)
    for block in data['blocks']:
        for line in block.get('lines', []):
            text = ''.join(span['text'] for span in line['spans']).strip()
            if text:
                record = {'text': text, 'bbox': list(line['bbox'])}
                midpoint = (line['bbox'][1] + line['bbox'][3]) / 2
                (body if top <= midpoint <= bottom else furniture).append(record)
                # A broken table can collapse into the footer area. Keep such
                # text in the collision scan; discard only isolated page labels.
                page_label = midpoint > bottom and re.fullmatch(r'\d+|[ivxlcdm]+', text, re.I)
                if midpoint >= top and not page_label:
                    collision_lines.append(record)
    images = len(page.get_images())
    characters = sum(len(line['text']) for line in body)
    sparse = None
    if not body or (len(body) <= 3 and characters <= 160 and not images):
        if body:
            kind = 'heading-or-short-text-only-body'
        elif images:
            kind = 'visual-only-body'
        elif furniture and all(line['bbox'][1] > bottom for line in furniture):
            kind = 'footer-only-body-empty'
        else:
            kind = 'running-furniture-only-body-empty' if furniture else 'empty-body'
        reason = intentional_sparse_pages.get(page_number)
        sparse = {'page': page_number, 'classification': kind,
                  'body_line_count': len(body), 'body_character_count': characters,
                  'image_count': images, 'body_text_sample': ' '.join(line['text'] for line in body)[:220],
                  'furniture_text': [line['text'] for line in furniture],
                  'intentional_exception': reason, 'review_required': not bool(reason)}
    # Separate table cells on one baseline do not collide unless their horizontal
    # extents intersect too. Ignore small superscript/descender overlaps.
    ordered = sorted(enumerate(collision_lines), key=lambda item: item[1]['bbox'][1])
    affected, examples = set(), []
    pair_count = 0
    for position, (left_id, left) in enumerate(ordered):
        a = left['bbox']
        for right_id, right in ordered[position + 1:]:
            b = right['bbox']
            if b[1] >= a[3]:
                break
            min_height = min(a[3] - a[1], b[3] - b[1])
            min_width = min(a[2] - a[0], b[2] - b[0])
            overlap_y = min(a[3], b[3]) - max(a[1], b[1])
            overlap_x = min(a[2], b[2]) - max(a[0], b[0])
            if min_height > 0 and min_width > 0 and overlap_y >= .30 * min_height and overlap_x >= .25 * min_width:
                pair_count += 1
                affected.update((left_id, right_id))
                if len(examples) < 8:
                    examples.append({'first': left, 'second': right,
                                     'vertical_overlap_fraction': overlap_y / min_height,
                                     'horizontal_overlap_fraction': overlap_x / min_width})
    fraction = len(affected) / max(len(collision_lines), 1)
    dense = None
    if pair_count >= 10 and fraction >= .12:
        dense = {'page': page_number, 'classification': 'suspicious-dense-overlapping-body-text',
                 'body_line_count': len(body), 'collision_scan_line_count': len(collision_lines),
                 'scan_scope': 'Body text including intrusion into footer space; isolated numeric page labels excluded',
                 'overlapping_line_pairs': pair_count,
                 'affected_line_count': len(affected), 'affected_line_fraction': fraction,
                 'examples': examples, 'review_required': True}
    return sparse, dense


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('pdf', nargs='?', type=Path, default=BOOK / '.build/print_preview/submission/book.pdf')
parser.add_argument('--out', type=Path)
parser.add_argument('--no-render', action='store_true')
parser.add_argument('--intentional-sparse-page', action='append', default=[], metavar='PAGE=REASON')
args = parser.parse_args()
exceptions = {}
for value in args.intentional_sparse_page:
    number, separator, reason = value.partition('=')
    if not separator or not number.isdigit() or int(number) < 1 or not reason.strip():
        parser.error('--intentional-sparse-page needs a positive PAGE and explicit REASON')
    exceptions[int(number)] = reason.strip()
path = args.pdf
out = args.out or BOOK / 'verification' / ('pdf_final' if 'print_preview' not in str(path) else 'pdf_preview')
out.mkdir(parents=True, exist_ok=True)
doc = pymupdf.open(path)
overflow = []
empty = []
sparse_pages, dense_pages = [], []
selected = {0, 1, 4, 7, len(doc) - 1}
targets = {'separator': 'Conceptual AI-generated', 'evidence': 'From candidate to defensible',
           'code': 'import jpype', 'software': 'Software Basis and Reproducibility',
           'table': 'Selected numerical ranges', 'preface': 'What Changed in This Revision',
           'flow_figure': 'Volumetric equipment load at 50',
           'pareto': 'Thirty full NeqSim compressor candidates',
           'seasonal': 'Seasonal operation: process and utility comparison',
           'ngl': 'NGL recovery and compression-power response',
           'calibration': 'observations.put(', 'glossary': 'Abandonment Pressure'}
matches = {}
for idx, page in enumerate(doc):
    text = page.get_text()
    if not text.strip() and len(page.get_images()) == 0:
        empty.append(idx + 1)
    sparse, dense = layout_diagnostics(page, idx + 1, exceptions)
    if sparse:
        sparse_pages.append(sparse)
    if dense:
        dense_pages.append(dense)
    if any(item and item['review_required'] for item in (sparse, dense)):
        selected.add(idx)
    for key, needle in targets.items():
        if key not in matches and needle in text:
            matches[key] = idx + 1
            selected.add(idx)
    for block in page.get_text('dict', flags=pymupdf.TEXTFLAGS_DICT & ~pymupdf.TEXT_PRESERVE_IMAGES)['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                x0, y0, x1, y1 = span['bbox']
                if span['text'].strip() and (x0 < -0.5 or y0 < -0.5 or x1 > page.rect.width + .5 or y1 > page.rect.height + .5):
                    overflow.append({'page': idx + 1, 'text': span['text'][:180], 'bbox': span['bbox']})
for idx in sorted(selected):
    if not args.no_render and 0 <= idx < len(doc):
        doc[idx].get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).save(out / f'page_{idx + 1:04d}.png')
report = {'pdf': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    'pages': len(doc), 'page_size_mm':
    [round(float(doc[0].rect.width) * 25.4 / 72, 2), round(float(doc[0].rect.height) * 25.4 / 72, 2)],
    'text_outside_page': overflow, 'empty_pages': empty, 'selected_pages': [i + 1 for i in sorted(selected)],
    'matched_sections': matches,
    'body_empty_pages': [item for item in sparse_pages if item['body_line_count'] == 0],
    'sparse_body_pages': [item for item in sparse_pages if item['body_line_count'] > 0],
    'dense_overlapping_body_text': dense_pages,
    'intentional_sparse_page_exceptions': [
        {'page': page, 'reason': reason, 'diagnostic_detected': any(item['page'] == page for item in sparse_pages)}
        for page, reason in sorted(exceptions.items())],
    'layout_review_required_pages': sorted({item['page'] for item in sparse_pages + dense_pages if item['review_required']}),
    'diagnostic_policy': {
        'auto_certifies_layout': False,
        'body_vertical_band_fraction': [0.07, 0.92],
        'collision_scan': 'Includes text below the body band to detect overprinted content intruding into the footer; only isolated numeric page labels are excluded.',
        'sparse_threshold': 'At most3 body text lines and160 characters without images; image-only pages are separately identified.',
        'overlap_threshold': 'At least10 pairs, each overlapping30% of the smaller line height and25% of its width, affecting at least12% of body lines.',
        'limitations': 'Review diagnostics only. Intentional title/frontmatter pages and some equations may be flagged; other defects may be missed. Explicit sparse-page exceptions never suppress dense-overlap diagnostics. Zero findings does not replace visual review.'}}
(out / 'geometry_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k not in ['text_outside_page', 'empty_pages', 'body_empty_pages', 'sparse_body_pages', 'dense_overlapping_body_text']}, indent=2))
print('Text spans outside page:', len(overflow), '; empty pages:', len(empty))
print('Body-empty/visual-only pages:', len(report['body_empty_pages']),
      '; sparse body pages:', len(report['sparse_body_pages']),
      '; dense overlapping body pages:', len(dense_pages),
      '; automatic layout certification: disabled')
print('First overflows:', json.dumps(overflow[:12], ensure_ascii=False))
