from pathlib import Path
import re,json,hashlib,sys
BOOK=Path(__file__).resolve().parents[1];sys.stdout.reconfigure(encoding='utf-8')
for path in sorted((BOOK/'chapters').glob('ch*/chapter.md'))[:18]:
 text=path.read_text(encoding='utf-8');d=json.loads((BOOK/'verification/scientific_revision'/(path.parent.name[:4]+'_manuscript_physics.json')).read_text())
 checked={r['block'] for r in d['physical_checks']};print('\n',path.parent.name)
 for i,m in enumerate(re.finditer(r'^```(?:python|java)\s*\n(.*?)^```',text,re.M|re.S),1):
  # Physical executor indices count all fences, including text diagrams.
  fullidx=1+len(list(re.finditer(r'^```\w*\s*\n.*?^```',text[:m.start()],re.M|re.S)))
  if '```python' in m[0] and fullidx not in checked:
   code=m[1]
   print(i,'fullidx',fullidx,'NOAUTO',code[:130].replace('\n',' / '),'calls',re.findall(r'\w+\.(?:run|\w*flash|\w*Flash|\w*Envelope|\w*Factor|calculate\w*|fit\w*|solve\w*)\([^\n]*',code)[-5:])
   print('LAST',code[-200:].replace('\n',' / '))
