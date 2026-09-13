"""Correct solvent identity and scope of the unvalidated selectivity discussion."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil

BOOK = Path(__file__).resolve().parents[1]
QA = BOOK / 'verification/pdf_final'
path = BOOK / 'chapters/ch12_gas_processing/chapter.md'
before = path.read_text(encoding='utf-8')
old = '''MDEA typically achieves selectivity factors of 5–15, depending on:
- Absorber height (fewer trays = more selective)
- TEG circulation rate (lower rate = more selective)
- Temperature (lower temperature = more selective)
- CO$_2$/H$_2$S ratio in the feed'''
new = '''MDEA is an acid-gas solvent used for selective H$_2$S removal ([Dow technical description](https://www.dow.com/en-us/pdp.methyldiethanolamine-mdea-high-purity-gt-grade.85613z.html)). Circulation here means the aqueous-MDEA solvent flow; TEG circulation belongs to the separate dehydration system. Evaluate the ratio above on a consistent wet/dry composition basis with finite outlet fractions. The prescribed-removal example in this chapter does not predict kinetic selectivity or establish a general range. Solvent composition, circulation, contacting conditions and feed must be specified before evaluating a particular process; the book does not establish universal temperature or tray-count trends.'''
assert before.count(old) == 1
after = before.replace(old, new)
pattern = r'^```(?:python|java)[^\n]*\n(.*?)^```'
assert re.findall(pattern, before, re.M | re.S) == re.findall(pattern, after, re.M | re.S)
backup = BOOK / '.build/rejected_visual_review_9c2791ae'
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(path, backup / 'ch12_before_mdea_prose.md')
path.write_text(after, encoding='utf-8')
report = {
    'status': 'passed', 'code_unchanged': True,
    'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'chapter': str(path.relative_to(BOOK)),
    'before_sha256': hashlib.sha256(before.encode()).hexdigest(),
    'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    'correction': 'MDEA acid-gas solvent circulation replaces the erroneous TEG reference; unsupported blanket selectivity range and monotonic process trends removed. Calculation scope explicitly limited to prescribed removal.',
    'primary_reference': {
        'title': 'METHYLDIETHANOLAMINE (MDEA), HIGH PURITY GT GRADE | Dow Inc.',
        'url': 'https://www.dow.com/en-us/pdp.methyldiethanolamine-mdea-high-purity-gt-grade.85613z.html',
        'retrieval': 'Read through the web search tool on 2026-09-12 UTC.',
        'short_quote': 'A gas removal solvent often used for selective H2S removal.',
        'scope': 'Solvent identity and stated use only; no operating selectivity range inferred.',
    },
    'corroborating_primary_abstract': {
        'title': 'Selective absorption of H2S from gas streams containing H2S and CO2 into aqueous solutions of N-methyldiethanolamine and 2-amino-2-methyl-1-propanol',
        'doi': '10.1016/S1383-5866(03)00139-4',
        'publication': 'Separation and Purification Technology35(3),191–202,2004',
        'scope': 'Search-readable primary abstract describes specific wetted-wall experiments. Full publisher page returned403; no full-text access or plant-wide trend validation claimed.',
    },
}
(QA / 'mdea_scientific_prose_fix.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('PASS: MDEA prose corrected with primary solvent identification; all code preserved.')
