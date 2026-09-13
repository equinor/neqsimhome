"""Root applies after source freeze: prose-only placement, exact code invariant."""
from pathlib import Path
import hashlib,json,re
B=Path(__file__).resolve().parents[1]
P=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
report=json.loads((B/'verification/scientific_revision/additional_scientific_literal_figure_review.json').read_text(encoding='utf-8'))
assert report['status']=='passed'
for r in report['images']:
 p=B/'chapters'/r['chapter']/'chapter.md';text=p.read_text(encoding='utf-8-sig');old=[m[3] for m in P.finditer(text)]
 marker='<!-- additional-scientific-literal-figure:'+r['chapter']+' -->'
 if marker in text:
  duplicate='\n\n**Figure '+r['chapter'][2:4]+'.90. '+r['caption']+'**'
  updated=text.replace(duplicate,'')
  assert [v[3] for v in P.finditer(updated)]==old
  if updated!=text:p.write_text(updated,encoding='utf-8')
  continue
 m=list(P.finditer(text))[r['fence']-1]
 assert hashlib.sha256(m[3].encode()).hexdigest()==r['code_sha256']
 figure=Path(r['path']);assert hashlib.sha256(figure.read_bytes()).hexdigest()==r['sha256']
 number=r['chapter'][2:4]
 addition='\n\n'+marker+'\n\n!['+r['caption']+'](figures/'+figure.name+')\n\n**Discussion.** '+r['discussion']+'\n'
 updated=text[:m.end()]+addition+text[m.end():]
 assert [v[3] for v in P.finditer(updated)]==old
 p.write_text(updated,encoding='utf-8')
 print(r['chapter'],'added reviewed literal figure; executable code byte-identical')
