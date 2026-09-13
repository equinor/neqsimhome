"""Archive primary reference-fluid data separately from simulation results."""
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'references/nist'
DEST.mkdir(parents=True, exist_ok=True)
entries = []
expected = []
for pressure in (1.0, 50.0, 100.0):
    params = {'Action': 'Data', 'Wide': 'on', 'ID': 'C74828', 'Type': 'IsoBar', 'Digits': '8',
              'P': pressure, 'TLow': 300, 'THigh': 400, 'TInc': 50,
              'TUnit': 'K', 'PUnit': 'bar', 'DUnit': 'kg/m3', 'HUnit': 'kJ/kg',
              'WUnit': 'm/s', 'VisUnit': 'uPa*s', 'STUnit': 'N/m', 'RefState': 'DEF'}
    url = 'https://webbook.nist.gov/cgi/fluid.cgi?' + urllib.parse.urlencode(params)
    path = DEST / f'methane_{pressure:g}bar_300_400K.tsv'
    response = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=40)
    data = response.read()
    path.write_bytes(data)
    text = data.decode('utf-8')
    rows = list(csv.DictReader(io.StringIO(text), delimiter='\t'))
    if not rows or not any('Density' in key for key in rows[0]):
        raise RuntimeError('NIST response was not the requested tabular data: ' + text[:250])
    for row in rows:
        normalized = {key.replace(' ', '').lower(): value for key, value in row.items()}
        def value(prefix):
            return float(next(v for k, v in normalized.items() if k.startswith(prefix)))
        T, P, rho = value('temperature'), value('pressure'), value('density')
        if T not in (300.0, 350.0, 400.0) or abs(P - pressure) > 1e-9:
            continue
        record = {'fluid': 'methane', 'T_K': T, 'P_bara': P, 'density_kg_m3': rho,
                  'phase': normalized.get('phase', ''), 'source_file': str(path.relative_to(ROOT))}
        # The NIST response may repeat a phase-labelled state; reject conflicting data.
        prior = [r for r in expected if r['T_K'] == T and r['P_bara'] == P]
        if prior:
            if abs(prior[0]['density_kg_m3'] - rho) > 1e-8:
                raise ValueError('Conflicting NIST phase duplicate')
        else:
            expected.append(record)
    entries.append({'source': 'NIST Chemistry WebBook SRD 69', 'url': url,
                    'file': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(data).hexdigest(),
                    'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                    'data_type': 'Reference-equation calculated properties, not new experimental measurements',
                    'purpose': 'Independent reference-fluid density comparison for cubic EOS at nine gas/supercritical states.'})
    print(path.name, len(rows), 'raw rows', flush=True)
assert len(expected) == 9
(ROOT / 'reference_expected.json').write_text(json.dumps({'source_kind': 'NIST independent reference EOS', 'states': expected}, indent=2), encoding='utf-8')
(ROOT / 'references/collection_manifest.json').write_text(json.dumps(entries, indent=2), encoding='utf-8')
lines = ['# Primary reference archive', '', 'NIST WebBook values are calculated reference-fluid properties, not experimental measurements obtained for this book.', '']
for entry in entries:
    lines.extend([f"- [{Path(entry['file']).name}]({entry['url']})", f"  - Retrieved: {entry['retrieved_utc']}; SHA-256: `{entry['sha256']}`.",
                  f"  - Local file: `{entry['file']}`. Scope: pure methane density, 300–400 K, 1–100 bara."])
lines.extend(['', 'Method and interpretation: [NIST thermophysical property tables](https://www.nist.gov/publications/thermophysical-properties-fluids).',
              '', 'Reference-data gaps: no independent facility-specific PVT, compressor vendor map, hydraulic field survey, hydrate equilibrium, TEG-contacting, control transient, cost, or production-history data were supplied. Those domains must not be described as calibrated or field-validated.'])
(ROOT / 'references/SOURCES.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
