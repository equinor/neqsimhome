"""Prove final illustration/prose integration leaves all reviewed code unchanged."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import datetime

BOOK=Path(__file__).resolve().parents[1]
OUT=BOOK/'verification/scientific_revision'
parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['before','after']);args=parser.parse_args()
pattern=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
snapshot={}
for path in sorted((BOOK/'chapters').glob('*/chapter.md')):
    text=path.read_text(encoding='utf-8')
    snapshot[path.parent.name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                              'code_sha256':[hashlib.sha256(m[3].encode()).hexdigest() for m in pattern.finditer(text)]}
if args.phase=='before':
    (OUT/'pre_integration_source.json').write_text(json.dumps(snapshot,indent=2),encoding='utf-8')
else:
    before=json.loads((OUT/'pre_integration_source.json').read_text(encoding='utf-8'))
    assert before.keys()==snapshot.keys()
    for name,row in snapshot.items():
        assert before[name]['code_sha256']==row['code_sha256'],f'Code changed during integration: {name}'
        row['reviewed_before_integration_sha256']=before[name]['sha256']
        row['final_sha256']=row.pop('sha256')
    report={'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'all_executable_code_unchanged':True,
            'scope':'After specialist full-text freeze: integration of104 reviewed notebook results, calculated/specified manuscript figures and captions, removal of unsupported legacy placements, and adjacent prose reconciliation. Full chapter sources and exact Python/Java code hashes retained.',
            'chapters':snapshot}
    report['verified_scientific_amendments']=[
        {'path':str(p.relative_to(BOOK)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in sorted(OUT.glob('*_integration_scientific_amendment.json'))]
    (OUT/'final_source_review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(f'{args.phase}: captured {len(snapshot)} chapters.')
