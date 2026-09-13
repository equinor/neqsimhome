"""Recover the complete shared reference index from unchanged archived files."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,urllib.parse
OUT=Path(__file__).resolve().parents[1]/'verification/scientific_revision'
REF=OUT/'references'
prior=json.loads((REF/'collection_manifest.json').read_text(encoding='utf-8')) if (REF/'collection_manifest.json').exists() else []
records=[]
def add(file,source,url,purpose,data_type):
    path=REF/file
    assert path.is_file(),path
    records.append({'source':source,'url':url,'file':str(path.relative_to(OUT)),
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'retrieved_utc':datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
        'retrieval_time_basis':'retained file modification time; index reconstructed without downloading or modifying the reference',
        'data_type':data_type,'purpose':purpose,'review_status':'reviewed for stated scope'})
for p in (1.0,50.0,100.0):
    params={'Action':'Data','Wide':'on','ID':'C74828','Type':'IsoBar','Digits':'8','P':p,
            'TLow':300,'THigh':400,'TInc':50,'TUnit':'K','PUnit':'bar','DUnit':'kg/m3',
            'HUnit':'kJ/kg','WUnit':'m/s','VisUnit':'uPa*s','STUnit':'N/m','RefState':'DEF'}
    add(f'nist/methane_{p:g}bar_300_400K.tsv','NIST Chemistry WebBook SRD69',
        'https://webbook.nist.gov/cgi/fluid.cgi?'+urllib.parse.urlencode(params),
        'Independent methane density comparison at 300, 350 and 400 K and the stated absolute pressure.',
        'Independent reference-EOS calculated values; not new experimental measurements')
for folder,name,url,source,purpose in [
 ('nasa','compressor_thermodynamics.html','https://www.grc.nasa.gov/www/k-12/airplane/compth.html','NASA Glenn','Constant-cp ideal compressor equation and shaft first law; the benchmark distinguishes reversible isentropic reference from irreversible adiabatic compression.'),
 ('nasa','hydrostatic_pressure.html','https://www.grc.nasa.gov/www/k-12/WindTunnel/Activities/fluid_pressure.html','NASA Glenn','Hydrostatic rho*g*h; absolute versus gauge pressure.'),
 ('nist','codata_constants.txt','https://physics.nist.gov/cuu/Constants/Table/allascii.txt','NIST CODATA','Molar gas constant and standard gravity for analytical limits.'),
 ('nist','reference_properties_method.html','https://www.nist.gov/publications/thermophysical-properties-fluids','NIST','Reference-fluid property tables are calculated; they are distinct from raw experiments.')]:
    add(folder+'/'+name,source,url,purpose,'Primary equation, constant or method context')
for path in sorted((REF/'crossref').glob('*.json')):
    raw=json.loads(path.read_text(encoding='utf-8'));metadata=raw.get('message',raw)
    expected_doi={'peng1976':'10.1021/i160057a011','beggs1973':'10.2118/4007-pa','rachford1952':'10.2118/952327-g'}[path.stem]
    metadata=next(r for r in metadata.get('items',[metadata]) if r.get('DOI','').lower()==expected_doi)
    add(path.relative_to(REF).as_posix(),'Crossref publisher-deposited metadata',
        'https://api.crossref.org/works/'+metadata['DOI'],
        'Bibliographic author/title/journal/DOI identity; not full-text or numerical validation.',
        'Bibliographic identity metadata')
add('emerson/control_valve_handbook.pdf','Emerson Control Valve Handbook',
    'https://www.emerson.com/documents/automation/control-valve-handbook-en-3661206.pdf',
    'Manufacturer flow-sizing constants and unit conventions; not a qualified valve selection.',
    'Primary manufacturer handbook')
if (REF/'nasa/mass_flow_rate_equations.html').is_file():
    provenance=json.loads((REF/'nasa/provenance.json').read_text(encoding='utf-8'))
    add('nasa/mass_flow_rate_equations.html',provenance['title'],provenance['url'],provenance['scope'],'Primary ideal-gas sonic-flow equation')
    assert records[-1]['sha256']==provenance['sha256']
known={r['file'].replace('\\','/') for r in records}
for row in prior:
    local=row.get('file','').replace('\\','/')
    if local and local not in known:
        p=OUT/local
        assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
        records.append(row);known.add(local)
assert len(records)>=11
(REF/'collection_manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
lines=['# Shared scientific reference archive','',
       f'All {len(records)} archived sources are indexed together. Reconstructing this index did not alter or retrieve any data file. NIST fluid values are independent reference-EOS calculations, not new experimental measurements.','']
for row in records:
    rel=Path(row['file']).relative_to('references').as_posix()
    lines += [f"- [{Path(rel).name}]({rel}) — [{row['source']}]({row['url']}). {row['purpose']}",
              f"  - Retrieved-file timestamp: {row['retrieved_utc']}; SHA256 `{row['sha256']}`; {row['review_status']}."]
lines += ['', 'Data gaps: no independent mixture PVT, hydrate/MEG/TEG, field hydraulics, vendor compressor maps, facility dynamics, production history or cost dataset was supplied. The available checks do not establish calibration in those domains.', '',
          'Most other Crossref requests returned HTTP429. Those attempts remain failures in the metadata audit; primary publisher/author/official sources used separately are documented in the bibliographic and chapter reviews.', '',
          'Shared-index rule: read and merge the existing manifest and preserve other reviewers’ records when adding references.']
(REF/'SOURCES.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'Reconstructed and hash-checked {len(records)} archived sources; data files unchanged.')
