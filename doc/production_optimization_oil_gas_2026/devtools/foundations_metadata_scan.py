from pathlib import Path
import re,json,sys
BOOK=Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')
keys={}
for p in sorted((BOOK/'chapters').glob('ch*/chapter.md'))[:18]:
 t=p.read_text(encoding='utf-8')
 for x in re.findall(r'\\cite\w*\{([^}]+)\}',t):
  for k in x.split(','):keys.setdefault(k.strip(),[]).append(p.parent.name[:4])
 control=[(i,ord(c)) for i,c in enumerate(t) if ord(c)<32 and c not in '\n\t\r']
 if control:print('CONTROL',p.parent.name,control[:10])
bibs=list(BOOK.rglob('*.bib'))
master=BOOK/'refs.bib'
masterkeys=set(re.findall(r'@\w+\s*\{\s*([^,]+)',master.read_text(encoding='utf-8')))
extra=BOOK/'verification/scientific_revision/foundations_refs.bib'
extra_keys=set(re.findall(r'@\w+\s*\{\s*([^,]+)',extra.read_text(encoding='utf-8')))
print('MASTER',master)
print('MISSING',json.dumps({k:v for k,v in keys.items() if k not in masterkeys|extra_keys},indent=2))
print('NEW KEYS',sorted(set(keys)-masterkeys))
print('ISSUES',len(json.loads((BOOK/'verification/scientific_revision/foundations_text_changes.json').read_text())))
