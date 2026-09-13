"""Focused regression: the rejected glossary and a normally spaced text page."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

BOOK = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / 'inspection_diagnostic_regression'
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(BOOK / '.build/python_packages'))
import pymupdf

helper = BOOK / 'devtools/inspect_pdf.py'
archive = BOOK / '.build/rejected_visual_review_2cd8b9f/book.pdf'
expected_sha = '2cd8b9f074cd5291b613e24505e0d2910ed9a842c3d86e856faeaf2bbc5af7e7'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(archive) == expected_sha

normal_path = OUT / 'normal_page.pdf'
normal = pymupdf.open()
page = normal.new_page(width=170 * 72 / 25.4, height=244 * 72 / 25.4)
page.insert_text((60, 75), 'A normally spaced technical page', fontsize=13)
for index in range(28):
    page.insert_text((60, 110 + 15 * index),
                     f'Line {index + 1:02d}: Independent pressure and temperature checks.', fontsize=9)
page.insert_text((235, 658), '1', fontsize=9)
normal.save(normal_path)
normal.close()


def run_case(name, path, exceptions=()):
    directory = OUT / name
    command = [sys.executable, str(helper), str(path), '--out', str(directory), '--no-render']
    for exception in exceptions:
        command.extend(['--intentional-sparse-page', exception])
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=90)
    (OUT / (name + '.log')).write_text(result.stdout + result.stderr, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    return json.loads((directory / 'geometry_report.json').read_text(encoding='utf-8'))


rejected = run_case('rejected_archive', archive,
                    ('1=Intentional illustrated cover, visually reviewed',
                     '2=Intentional half-title frontmatter, visually reviewed',
                     '3=Intentional title page, visually reviewed'))
accepted = run_case('normal', normal_path)
body_empty = {item['page']: item for item in rejected['body_empty_pages']}
sparse = {item['page']: item for item in rejected['sparse_body_pages']}
dense = {item['page']: item for item in rejected['dense_overlapping_body_text']}
assert rejected['empty_pages'] == [], 'The original empty-page check is preserved.'
assert rejected['text_outside_page'] == [], 'The physical-page overflow check is preserved.'
for number in (1385, 1387):
    assert body_empty[number]['classification'] == 'footer-only-body-empty'
    assert body_empty[number]['review_required']
assert sparse[1386]['classification'] == 'heading-or-short-text-only-body'
assert dense[1388]['review_required'] and dense[1388]['overlapping_line_pairs'] >= 10
assert body_empty[1]['classification'] == 'visual-only-body'
assert body_empty[1]['intentional_exception'] and not body_empty[1]['review_required']
assert sparse[2]['intentional_exception'] and not sparse[2]['review_required']
assert len(rejected['intentional_sparse_page_exceptions']) == 3
assert not accepted['body_empty_pages'] and not accepted['sparse_body_pages']
assert not accepted['dense_overlapping_body_text'] and not accepted['text_outside_page']
assert rejected['diagnostic_policy']['auto_certifies_layout'] is False
assert accepted['diagnostic_policy']['auto_certifies_layout'] is False

report = {
    'status': 'passed', 'passed': True,
    'tested_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'helper': str(helper), 'helper_sha256': sha(helper),
    'python': sys.executable,
    'test_script': str(Path(__file__)), 'test_sha256': sha(Path(__file__)),
    'archived_pdf': str(archive), 'archived_pdf_sha256': expected_sha,
    'preserved_old_gates': {'text_outside_page': 0, 'empty_pages': 0},
    'detected_footer_only_pages': [1385, 1387],
    'detected_heading_only_page': 1386,
    'detected_glossary_overlap': dense[1388],
    'explicit_frontmatter_exceptions': rejected['intentional_sparse_page_exceptions'],
    'normal_page': {'path': str(normal_path), 'sha256': sha(normal_path),
                    'body_empty': 0, 'sparse_body': 0, 'overlapping_body': 0, 'overflow': 0},
    'archived_review_required_pages': rejected['layout_review_required_pages'],
    'scope': 'Heuristic diagnostic regression against a known rejected publication and a normal text fixture. It does not certify the next PDF or alter any manuscript, renderer, numerical result or scientific ledger.',
    'auto_certifies_layout': False,
    'reports': [str(OUT / name / 'geometry_report.json') for name in ('rejected_archive', 'normal')],
    'unresolved': [],
}
(OUT.parent / 'inspect_pdf_diagnostics_review.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'passed': True, 'footer_only': [1385, 1387], 'heading_only': 1386,
                  'glossary_overlap_pairs': dense[1388]['overlapping_line_pairs'],
                  'affected_glossary_lines': dense[1388]['affected_line_count'],
                  'normal_page_findings': 0,
                  'other_review_required_pages': rejected['layout_review_required_pages']}))
