"""Retain the rejected candidate and exact reviewed page images before rebuilding."""
from pathlib import Path
import hashlib
import json
import shutil

BOOK = Path(__file__).resolve().parents[1]
QA = BOOK / 'verification/pdf_final'
target = BOOK / '.build/rejected_visual_review_9c2791ae'
target.mkdir(parents=True, exist_ok=True)
expected = '9c2791ae11117d355b91bc6af5dce294225d0b5cf9fc1cc05a2e5644d00e24d8'
pdf = BOOK / '.build/release_candidate/submission/book.pdf'
assert hashlib.sha256(pdf.read_bytes()).hexdigest() == expected
shutil.copy2(pdf, target / 'book.pdf')
names = ['scientific_sample_manifest.json', 'scientific_contacts.json', 'geometry_report.json']
names += ['final_visual_' + who + '.json' for who in ('root', 'foundations', 'notebooks', 'optimization')]
for name in names:
    shutil.copy2(QA / name, target / name)
shutil.copy2(BOOK / 'verification/render_manifest.json', target / 'render_manifest.json')
samples = json.loads((QA / names[0]).read_text(encoding='utf-8'))
contacts = json.loads((QA / names[1]).read_text(encoding='utf-8'))
assert samples['pdf_sha256'] == contacts['pdf_sha256'] == expected
images = target / 'reviewed_images'
images.mkdir(exist_ok=True)
rows = []
for row in samples['rendered_images'] + contacts['sheets']:
    src = Path(row['path'])
    assert hashlib.sha256(src.read_bytes()).hexdigest() == row['sha256']
    dest = images / src.name
    shutil.copy2(src, dest)
    rows.append({'source': str(src), 'archive': str(dest), 'sha256': row['sha256']})
(target / 'archive_manifest.json').write_text(json.dumps({'pdf_sha256': expected, 'images': rows}, indent=2), encoding='utf-8')
print('Archived candidate, all current review reports and', len(rows), 'exact current page/contact images.')
