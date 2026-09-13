"""Record root's actual inspection of the current frontmatter images."""
from pathlib import Path
import datetime
import hashlib
import json

BOOK = Path(__file__).resolve().parents[1]
QA = BOOK / 'verification/pdf_final'
contacts = json.loads((QA / 'scientific_contacts.json').read_text(encoding='utf-8'))
samples = json.loads((QA / 'scientific_sample_manifest.json').read_text(encoding='utf-8'))
expected = 'c051766714aa5083d29804877c28d906ded31967f52afe551d459e4a797ad6b9'
pdf = BOOK / '.build/release_candidate/submission/book.pdf'
assert hashlib.sha256(pdf.read_bytes()).hexdigest() == contacts['pdf_sha256'] == samples['pdf_sha256'] == expected
sheets = contacts['sheets'][:2]
full = [row for row in samples['rendered_images'] if row['page'] in (9, 10)]
prior = json.loads((BOOK / '.build/rejected_visual_review_9c2791ae/scientific_sample_manifest.json').read_text(encoding='utf-8'))
prior_images = {row['page']: row['sha256'] for row in prior['rendered_images']}
for row in full:
    assert prior_images[row['page']] == row['sha256']
    row['method'] = 'Fresh current contact-sheet inspection; full-size pixels are exactly identical to the individually viewed previous image.'
    row['prior_full_size_review_pdf_sha256'] = prior['pdf_sha256']
for row in sheets + full:
    assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest() == row['sha256']
report = {
    'passed': True, 'pdf_sha256': expected,
    'reviewed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'Fresh actual tool image inspection of current contact sheets01–02 (pages1–12); full-size current pages9–10 additionally verified pixel-identical to their prior individual inspection.',
    'contact_sheets': sheets, 'selected_pages': list(range(1, 13)),
    'full_size_pages': full,
    'checks': [
        'Cover, half-title, title, copyright, dedication, preface and contents hierarchy are legible with no clipping or overprint.',
        'Book-organization and validation-basis tables paginate with repeated headings and readable rows.',
        'Pages9–10 clearly distinguish execution, solution verification and independent comparison; 35notebooks/300cells/89comparisons and18NIST comparisons are correctly scoped.',
        'Recorded source build, current capability table, synthetic-data limitations and conceptual-artwork provenance remain visible.',
    ],
    'diagnostic_dispositions': [
        {'page': 1, 'disposition': 'Intentional full-page illustrated cover; raster artwork contains the title and author.', 'passed': True},
        {'page': 2, 'disposition': 'Intentional half-title page with centered book title and designed white space.', 'passed': True},
        {'page': 5, 'disposition': 'Intentional dedication page with a short centered dedication.', 'passed': True},
    ],
    'findings': [], 'unresolved': [],
}
(QA / 'final_visual_root.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('Recorded actual final frontmatter review:12pages,2 enlarged pages; PASS.')
