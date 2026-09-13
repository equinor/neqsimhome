from pathlib import Path
import sys,json
BOOK=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BOOK/'.build/python_packages'))
sys.stdout.reconfigure(encoding='utf-8')
if len(sys.argv)>1 and sys.argv[1]=='pdf':
 import fitz
 p=BOOK/'verification/scientific_revision/references/emerson/control_valve_handbook.pdf'
 with fitz.open(p) as d:
  for i,page in enumerate(d):
   t=page.get_text()
   if any(k.lower() in t.lower() for k in sys.argv[2:]):print('PAGE',i+1,t[:8000])
else:
 for p in sorted((BOOK/'verification/scientific_revision').glob('ch??_manuscript_physics.json')):
  d=json.loads(p.read_text());fails=[x for x in d['physical_checks'] if not x['pass']]
  print(p.name,'blocks',len(d['literal_blocks']),'units',len(d['physical_checks']),'fail',len(fails))
  for x in fails:print(json.dumps({k:x[k] for k in ['block','equipment','class']},ensure_ascii=False),x.get('error') or [(c['name'],c['error']) for c in x['checks'] if not c['pass']])
