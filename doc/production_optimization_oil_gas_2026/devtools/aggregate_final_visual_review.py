"""Bind completed specialist visual reviews to the exact current PDF and samples."""
from pathlib import Path
import datetime
import hashlib
import json

BOOK = Path(__file__).resolve().parents[1]
QA = BOOK / 'verification/pdf_final'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

pdf = BOOK / '.build/release_candidate/submission/book.pdf'
digest = sha(pdf)
contacts = read(QA / 'scientific_contacts.json')
samples = read(QA / 'scientific_sample_manifest.json')
assert contacts['pdf_sha256'] == samples['pdf_sha256'] == digest
expected = {Path(row['path']).resolve(): row for row in contacts['sheets']}
covered = set()
selected = set()
full_size = set()
reports = []
findings = []
dispositions = []
for name in ('root', 'foundations', 'notebooks', 'optimization'):
    path = QA / ('final_visual_' + name + '.json')
    review = read(path)
    assert review['pdf_sha256'] == digest, 'Stale review: ' + name
    assert review['passed'] is True and not review.get('unresolved'), 'Unresolved review: ' + name
    for item in review['contact_sheets']:
        sheet = Path(item['path']).resolve()
        assert sheet in expected, 'Unexpected contact sheet'
        assert sha(sheet) == item['sha256'] == expected[sheet]['sha256'], 'Contact sheet changed'
        assert item['pages'] == expected[sheet]['pages']
        covered.add(sheet)
        selected.update(item['pages'])
    selected.update(review['selected_pages'])
    for item in review.get('full_size_pages', []):
        if isinstance(item, int):
            full_size.add(item)
        else:
            full_size.add(item['page'])
            if item.get('path') and item.get('sha256'):
                assert sha(Path(item['path'])) == item['sha256'], 'Full-size page changed'
    for item in review.get('full_size_page_artifacts', []):
        assert sha(Path(item['path'])) == item['sha256'], 'Full-size page artifact changed'
    reports.append({'reviewer': name, 'path': str(path), 'sha256': sha(path)})
    findings.extend(review.get('findings', []))
    dispositions.extend({'reviewer': name, **row} for row in review.get('diagnostic_dispositions', []))
assert covered == set(expected), 'Not every current contact sheet was reviewed'
assert set(samples['selected_pages']).issubset(selected)
geometry = read(QA / 'geometry_report.json')
assert geometry['sha256'] == digest
required = set(geometry.get('layout_review_required_pages', []))
assert required.issubset(selected | full_size), 'A layout diagnostic lacks visual review'
assert required.issubset({row['page'] for row in dispositions}), 'A layout diagnostic lacks an explicit disposition'
assert not any(row.get('unresolved_layout_issue') for row in dispositions)
report = {
    'passed': True, 'pdf': str(pdf), 'pdf_sha256': digest,
    'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'method': 'Actual AI-agent visual inspection of all current contact sheets, with full-size enlargement of dense or uncertain pages. This is sampled publication QA, not external human peer review or visual inspection of every book page.',
    'contact_sheets_reviewed': len(covered),
    'selected_pages': sorted(selected), 'full_size_pages': sorted(full_size),
    'distinct_pages_reviewed': len(selected | full_size),
    'layout_diagnostic_pages_reviewed': sorted(required),
    'layout_diagnostic_dispositions': dispositions,
    'reviewer_reports': reports, 'findings': findings,
    'unresolved_material_findings': 0,
}
(QA / 'visual_review.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k not in ('selected_pages', 'full_size_pages', 'reviewer_reports')}, indent=2))
