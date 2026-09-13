"""Refresh only Chapter 10's current ledger entry after a label-only replay."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

OUT=Path(__file__).resolve().parent; BOOK=OUT.parents[1]
BACKUP=BOOK/'.build/backups/ch10_final_separator_label_correction'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
write=lambda p,d:p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
chapter='ch10_separation_technology'
rp=BOOK/'verification/notebooks'/f'{chapter}.json'; r=read(rp)
old=read(BACKUP/rp.relative_to(BOOK)); nb=BOOK/r['notebook']
assert r['status']=='passed' and r['numeric_results']==old['numeric_results'], 'Label repair changed a numerical result'
before=read(BACKUP/'before_hashes.json')
for name,digest in before.items():
    if name!=r['notebook']:assert sha(BOOK/name)==digest, 'An unrelated notebook changed: '+name
evidence_path=OUT/'notebooks'/f'{chapter}.json'; e=read(evidence_path)
assert e['status']=='passed'
r['scientific_validation']={**old['scientific_validation'],
    'post_execution_edit':'Reran only Chapter 10 after final-separator label/comment correction; numeric arrays unchanged. Replaced discussion prose with corrected pressure/temperature basis.',
    'previous_notebook_sha256':old['notebook_sha256']}
write(rp,r)
ledger_path=OUT/'notebook_physics_review.json'; ledger=read(ledger_path)
item=next(x for x in ledger['ledger'] if x['chapter']==chapter)
assert item['distinct_check_labels']==len(e['checks'])
assert item['evaluations']==sum(x['evaluations'] for x in e['checks'])
item.update(notebook_sha256=sha(nb),code_cell_sha256=[x['sha256'] for x in r['cell_runs']],
            physics_report_sha256=sha(evidence_path),runtime_seconds=r['runtime_seconds'],
            figure_coverage=[{'path':x['path'],'sha256':x['sha256'],'series':len(x['series']),
                             'nonfinite_plotted_values':sum(z['n_nonfinite'] for z in x['series'])} for x in r['figures']])
correction={'date':datetime.now(timezone.utc).isoformat(),'chapter':chapter,
            'scope':'Corrected final-separator oil labels: 1.5 bara, calculated flash temperature, no subsequent reference flash.',
            'numerical_arrays_unchanged':True,'other_34_notebooks_unchanged':True,
            'previous_notebook_sha256':old['notebook_sha256'],'notebook_sha256':sha(nb)}
ledger.setdefault('subsequent_scoped_revisions',[]).append(correction)
write(ledger_path,ledger)
mp=OUT/'notebook_physics_review.md'
mp.write_text(mp.read_text(encoding='utf-8')+'\n## Chapter 10 label correction\n\nOnly Chapter 10 was rerun after its oil-rate labels were corrected to the final separator at 1.5 bara and calculated flash temperature. All numerical arrays and scoped physics-check counts are unchanged; the other 34 notebook files are unchanged. The current machine-readable ledger binds the refreshed artifacts.\n',encoding='utf-8')
correction.update(physics_report_sha256=sha(evidence_path),physical_evaluations=item['evaluations'],
                  figures=[{'path':x['path'],'sha256':x['sha256']} for x in r['figures']],
                  discussion_section=str((BOOK/'verification/figure_sections/ch10.md').relative_to(BOOK)))
write(OUT/'ch10_label_correction.json',correction)
print(json.dumps(correction,indent=2))
