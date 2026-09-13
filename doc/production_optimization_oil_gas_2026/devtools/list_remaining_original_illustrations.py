from pathlib import Path
import json,re,hashlib
B=Path(__file__).resolve().parents[1];O=B/'verification/scientific_revision'
initial=json.loads((O/'manuscript_figures/inventory.json').read_text(encoding='utf-8'))
decisions=json.loads((O/'manuscript_figure_review.json').read_text(encoding='utf-8'))['changes']
covered={(r['chapter'],r['file']) for r in decisions}
rows=[]
for r in initial:
 p=Path(r['path']);ch=p.parent.parent;txt=(ch/'chapter.md').read_text(encoding='utf-8')
 if '](figures/'+p.name+')' not in txt or (r['chapter'],p.name) in covered:continue
 if hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:continue
 rows.append(r)
(O/'unchanged_original_illustrations_to_confirm.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps([{'chapter':r['chapter'],'file':Path(r['path']).name,'caption':r['caption']} for r in rows],indent=2))
