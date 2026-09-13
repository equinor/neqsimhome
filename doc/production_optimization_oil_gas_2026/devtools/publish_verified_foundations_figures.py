"""Publish only explicitly referenced figures from a matching successful code fence."""
from pathlib import Path
import hashlib
import json
import re
import shutil
BOOK=Path(__file__).resolve().parents[1]
reports=[]
for p in (BOOK/'verification').glob('ch*_python*.json'):
    data=json.loads(p.read_text(encoding='utf-8'))
    reports.extend((data.get('chapter'),r,str(p.relative_to(BOOK))) for r in data.get('blocks',[]))
manifest=[]
for chapter in sorted((BOOK/'chapters').glob('*/chapter.md'))[:18]:
    text=chapter.read_text(encoding='utf-8')
    references=set(re.findall(r'!\[[^\]]*\]\((figures/[^)]+)\)',text))
    for index,m in enumerate(re.finditer(r'^```(python|java)\s*\n(.*?)^```',text,re.M|re.S),1):
        if m[1]!='python':continue
        for rel in re.findall(r'\.savefig\(["\'](figures/[^"\']+)["\']',m[2]):
            if rel not in references:continue
            evidence=[(r,p) for ch,r,p in reports if ch==chapter.parent.name and r.get('code')==m[2] and r.get('status')=='pass']
            if not evidence:raise RuntimeError(f'No current passing producer for {chapter.parent.name}/{rel}')
            generated=(BOOK/'.build/fenced_examples'/chapter.parent.name/rel).resolve()
            target=(chapter.parent/rel).resolve()
            assert target.is_relative_to((chapter.parent/'figures').resolve())
            if not generated.is_file():raise FileNotFoundError(generated)
            oldhash=hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None
            backup=BOOK/'.build/foundations_original_figures'/chapter.parent.name/Path(rel).name
            if target.exists() and not backup.exists():
                backup.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(target,backup)
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(generated,target)
            manifest.append({'chapter':chapter.parent.name,'block':index,'figure':rel,
                             'producer_code_sha256':hashlib.sha256(m[2].encode()).hexdigest(),
                             'image_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                             'previous_image_sha256':oldhash,'execution_report':evidence[-1][1]})
(BOOK/'verification/foundations_published_figures.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Published',len(manifest),'referenced figures from verified fenced examples')
for row in manifest:print(row['chapter'],row['figure'])
