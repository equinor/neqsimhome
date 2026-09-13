"""Promote the exact reviewed primary artifacts, without silently rebuilding them."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil

BOOK = Path(__file__).resolve().parents[1]
VERIFY = BOOK / 'verification'
STAGE = BOOK / '.build/release_candidate/submission'

def read(name):
    return json.loads((VERIFY / name).read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

manifest = read('render_manifest.json')
geometry = read('pdf_final/geometry_report.json')
visual = read('pdf_final/visual_review.json')
html = read('full_book_html_check.json')
structure = read('publication_structure_check.json')
notebooks = read('notebook_release_audit.json')
foundations = read('foundations_release_audit.json')
optimization = read('optimization_chapters_audit_summary.json')
scientific = read('scientific_revision/engineering_release_gate.json')
assert not manifest['changed_during_render']
assert not manifest['renderers_changed_during_render']
for name, expected in manifest['renderer_sha256'].items():
    assert sha(Path(name)) == expected, 'Renderer changed after rendering: ' + name
for name, expected in manifest['source_sha256'].items():
    assert sha(BOOK / name) == expected, 'Source changed after rendering: ' + name
for artifact in manifest['artifacts']:
    assert sha(Path(artifact['path'])) == artifact['sha256'], 'Artifact changed after rendering'
pdf_sha = sha(STAGE / 'book.pdf')
assert geometry['sha256'] == pdf_sha == visual['pdf_sha256'] == structure['pdf_sha256']
assert not geometry['text_outside_page'] and not geometry['empty_pages']
assert visual['passed'] and structure['passed']
assert set(geometry.get('layout_review_required_pages', [])).issubset(
    set(visual.get('layout_diagnostic_pages_reviewed', []))), 'Layout diagnostics require visual disposition'
assert visual.get('unresolved_material_findings') == 0
assert html['passed'] and html['sha256'] == sha(STAGE / 'book.html')
assert notebooks['status'] == 'passed' and notebooks['passed_notebooks'] == 35
assert set(foundations['counts']) == {'pass'} and foundations['counts']['pass'] > 0
assert not foundations['exclusions']
assert optimization['all_runnable_fences_passed'] and not optimization['stale_or_missing']
assert scientific['status'] == 'passed_with_declared_model_scope'
assert scientific['reviewed_chapters'] == 35 and not scientific['unresolved_release_errors']
for name, expected in scientific['evidence_sha256'].items():
    assert sha(BOOK / name) == expected, 'Scientific evidence changed after review: ' + name
assert '0 error(s)' in (VERIFY / 'book_check_final.log').read_text(encoding='utf-8-sig')

destination = BOOK / 'submission'
backup = BOOK / '.build/pre_scientific_publication'
destination.mkdir(exist_ok=True)
backup.mkdir(parents=True, exist_ok=True)
primary_names = ['book.pdf', 'book.html', 'book_standalone.html']
for name in primary_names:
    old = destination / name
    if old.exists() and not (backup / name).exists():
        shutil.copy2(old, backup / name)
for source in STAGE.iterdir():
    if source.is_dir():
        shutil.copytree(source, destination / source.name, dirs_exist_ok=True)
    elif source.name in primary_names or source.suffix.lower() in ('.png', '.jpg', '.jpeg', '.svg', '.css', '.js'):
        shutil.copy2(source, destination / source.name)
artifacts = []
for name in primary_names:
    assert sha(destination / name) == sha(STAGE / name)
    artifacts.append({'path': str(destination / name), 'sha256': sha(destination / name),
                      'bytes': (destination / name).stat().st_size})
renderer_names = ['book_builder.py', 'book_render_pdf.py', 'book_render_html.py', 'katex_head.py']
report = {'promoted_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'status': 'released', 'artifacts': artifacts, 'previous_publication': str(backup),
          'renderer_sha256': {name: sha(BOOK.parents[1] / 'tools' / name) for name in renderer_names},
          'pages': geometry['pages'], 'chapters': len(structure['numbered_chapters']),
          'numbered_figures': structure['pdf_caption_count'],
          'executed_notebooks': notebooks['passed_notebooks'],
          'executed_notebook_code_cells': notebooks['executed_code_cells'],
          'fresh_notebook_figures': notebooks['fresh_figures'],
          'executed_manuscript_fences': scientific['executed_manuscript_fences'],
          'integration_patterns_not_executed': scientific['integration_patterns_not_executed'],
          'benchmark_comparisons': scientific['benchmark_comparisons'],
          'independent_reference_eos_comparisons': scientific['independent_reference_eos_comparisons'],
          'scientific_review': 'verification/scientific_revision/SCIENTIFIC_REVIEW.md',
          'source_git_revision': notebooks['source_revisions'][0]}
(VERIFY / 'publication_release.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
