"""Bounded chapter-by-chapter literal execution and engineering gates."""
from pathlib import Path
import subprocess,sys,json,time,os
BOOK=Path(__file__).resolve().parents[1]
rows=[]
for n in range(1,19):
 ch=f'ch{n:02d}';t=time.monotonic()
 try:
  p=subprocess.run([sys.executable,str(BOOK/'devtools/foundations_manuscript_physics.py'),'--chapter',ch,'--probe'],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=420)
  row={'chapter':ch,'returncode':p.returncode,'seconds':time.monotonic()-t,'output':p.stdout,'stderr':p.stderr}
 except subprocess.TimeoutExpired:
  row={'chapter':ch,'returncode':'timeout','seconds':time.monotonic()-t}
 rows.append(row)
 (BOOK/'verification/scientific_revision/foundations_physics_run.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
 print(ch,row['returncode'],round(row['seconds'],1),flush=True)
