"""Add retained bibliographic responses to the existing primary-source archive."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

OUT = Path(__file__).resolve().parents[1] / 'verification/scientific_revision'
REF = OUT / 'references'
manifest_path = REF / 'collection_manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
known = {row['file'].replace('\\', '/') for row in manifest}
for path in sorted((REF / 'crossref').glob('*.json')):
    local = path.relative_to(OUT).as_posix()
    if local in known:
        continue
    response = json.loads(path.read_text(encoding='utf-8'))
    record = response.get('message', response)
    if 'items' in record:
        expected={'peng1976':'10.1021/i160057a011','beggs1973':'10.2118/4007-pa','rachford1952':'10.2118/952327-g'}[path.stem]
        record=next(r for r in record['items'] if r.get('DOI','').lower()==expected)
    doi = record.get('DOI', '')
    manifest.append(dict(source='Crossref publisher-deposited bibliographic metadata',
                         url='https://api.crossref.org/works/' + doi,
                         file=local, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         retrieved_utc=datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                         retrieval_time_basis='retained file modification timestamp',
                         data_type='Bibliographic identity metadata; not a numerical validation dataset',
                         purpose='Check author/title/journal/DOI identity. Full-text scientific claims require separate evidence.'))
for row in manifest:
    path = OUT / row['file'].replace('\\', '/')
    assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
path = REF / 'SOURCES.md'
source = re.sub(r'\n<!-- bibliography-metadata:start -->.*?<!-- bibliography-metadata:end -->\n?', '', path.read_text(encoding='utf-8'), flags=re.S)
lines = ['<!-- bibliography-metadata:start -->', '## Bibliographic response archive', '',
         'Successful publisher-deposited metadata responses are retained separately from numerical reference data. Other Crossref attempts returned HTTP 429; the metadata audit retains those failures. See [bibliographic review](../bibliographic_review.md) for publisher and official-source checks used separately.', '']
for row in manifest:
    if '/crossref/' in row['file'].replace('\\', '/'):
        rel = row['file'].replace('\\', '/').removeprefix('references/')
        lines.append(f"- [{Path(rel).name}]({rel}): [source metadata]({row['url']}); SHA-256 `{row['sha256']}`. {row['purpose']}")
lines += ['', '<!-- bibliography-metadata:end -->']
path.write_text(source.rstrip() + '\n\n' + '\n'.join(lines) + '\n', encoding='utf-8')
print(f'Indexed and hash-checked {len(manifest)} source files.')
