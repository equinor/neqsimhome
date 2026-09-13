from pathlib import Path
import sys,re,json,itertools
sys.stdout.reconfigure(encoding='utf-8')
B=Path(__file__).resolve().parents[1]
if sys.argv[1]=='outputs':
 for ch in sys.argv[2:]:
  data=json.loads((B/'verification/scientific_revision'/(ch+'_manuscript_physics.json')).read_text())
  for row in data['literal_blocks']:print(ch,row['index'],row['output'][-4000:])
elif sys.argv[1]=='json':
 for path in sys.argv[2:]:
  rows=json.loads((B/path).read_text())
  for row in rows:print({k:v for k,v in row.items() if k not in ['code','diagnostics']})
else:
 c=sys.argv[1];s=next((B/'chapters').glob(c+'*/chapter.md')).read_text(encoding='utf-8');lines=s.splitlines()
 for arg in sys.argv[2:]:
  if ':' in arg and all(x.isdigit() for x in arg.split(':')):
   a,z=map(int,arg.split(':'));print('\n'.join(f'{i+1}: {lines[i]}' for i in range(a-1,min(z,len(lines)))))
  else:
   print('\nPATTERN',arg)
   for m in itertools.islice(re.finditer(arg,s,re.I),3):print(s[max(0,m.start()-250):m.end()+500].replace('```python','[code python]'))
