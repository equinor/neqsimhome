from pathlib import Path
import json,re
B=Path(__file__).resolve().parents[1]
d=json.loads((B/'verification/scientific_revision/optimization_review.json').read_text(encoding='utf-8'))
out=[]
for c in d['chapters']:
 rows=[e for e in c['entries'] if e['classification']=='executed_numerical_or_api_demonstration_unqualified']
 if not rows:continue
 print(c['number'],[(e['number'],e['heading']) for e in rows])
 t=(B/'chapters'/c['chapter']/'chapter.md').read_text(encoding='utf-8-sig')
 blocks=list(re.finditer(r'^```(?:python|java)[^\n]*\n(.*?)^```',t,re.M|re.S))
 for row in rows:
  out.append({'chapter':c['number'],'folder':c['chapter'],**row,'code':blocks[row['number']-1].group(1)})
(B/'verification/scientific_revision/remaining_numerical_cases.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
