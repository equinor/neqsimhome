"""Reuse actual exact-literal hook executions; never promote stale/failed sources."""
from pathlib import Path
import argparse,hashlib,json,re
B=Path(__file__).resolve().parents[1]
P=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
ap=argparse.ArgumentParser();ap.add_argument('--chapters',required=True);args=ap.parse_args()
for n in map(int,args.chapters.split(',')):
 chapter=next((B/'chapters').glob(f'ch{n:02d}_*'));proof_path=B/f'verification/scientific_revision/ch{n:02d}_solution_checks.json'
 proof=json.loads(proof_path.read_text(encoding='utf-8'))
 assert proof['all_targeted_checks_passed'],proof_path
 literal=list(P.finditer((chapter/'chapter.md').read_text(encoding='utf-8-sig')))
 for r in proof['prerequisite_fences']:
  m=literal[r['number']-1]
  assert r['status']=='passed' and hashlib.sha256(m.group(3).encode()).hexdigest()==r['sha256'],r
 path=B/'verification'/(chapter.name+'_fences.json');report=json.loads(path.read_text(encoding='utf-8'))
 backup=B/'verification/scientific_revision/prior_execution_records';backup.mkdir(exist_ok=True)
 data=path.read_bytes();digest=hashlib.sha256(data).hexdigest();(backup/(digest+'.json')).write_bytes(data)
 details={r['number']:r for r in proof['entries']};actual={r['number']:r for r in proof['prerequisite_fences']}
 text=(chapter/'chapter.md').read_text(encoding='utf-8-sig')
 for row in report['examples']:
  i=row['number'];m=literal[i-1]
  if i not in actual:continue
  old_hash=row['sha256'];row.update(sha256=actual[i]['sha256'],status='passed',line=text.count('\n',0,m.start())+1,
    execution_evidence=str(proof_path.relative_to(B)),execution_evidence_sha256=hashlib.sha256(proof_path.read_bytes()).hexdigest(),
    prior_execution_record=str((backup/(digest+'.json')).relative_to(B)))
  for stale in ('error','traceback'):row.pop(stale,None)
  if i in details:
   row['seconds']=details[i]['seconds'];row['output']=details[i].get('output','')
  elif old_hash!=row['sha256']:
   row['output']='Exact literal executed as a prerequisite in the linked solution-check report; no stdout retained for this prerequisite.'
   row.pop('seconds',None)
 report['execution_model']='Sequential literal Python in a fresh JVM; ordinary executions supplemented by exact-source hook runs. Per-example evidence links identify reused executions.'
 path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
 print(n,len(actual),'actual current executions rebound')
