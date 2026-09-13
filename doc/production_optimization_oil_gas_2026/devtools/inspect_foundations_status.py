from pathlib import Path
import json
import sys
BOOK=Path(__file__).resolve().parents[1]
for p in sorted((BOOK/'verification').glob('ch*_*.json')):
    if not p.name.endswith(('_python.json','_java.json')): continue
    if len(sys.argv)>1 and not any(p.name.startswith(v) for v in sys.argv[1:]): continue
    data=json.loads(p.read_text(encoding='utf-8'))
    rows=data.get('blocks',[])
    print(p.name,[(r['index'],r['status']) for r in rows])
    for r in rows:
        if r['status']=='fail': print(r['index'],r.get('traceback',r.get('output',''))[-1600:])
        if len(sys.argv)>1 and r['status']=='pass' and r.get('output'): print(r['index'],r['output'][-1000:])
