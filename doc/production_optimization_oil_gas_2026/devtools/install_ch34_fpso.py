"""Replace only the two allocated fences, preserving concurrent prose edits."""
from pathlib import Path
import hashlib,json,re
BOOK=Path(__file__).resolve().parents[1]
chapter=BOOK/'chapters/ch34_case_studies/chapter.md'
source=chapter.read_text(encoding='utf-8')
pattern=re.compile(r'^```python[^\n]*\n(.*?)^```',re.M|re.S)
edits=[]
for match in pattern.finditer(source):
    if 'def build_fpso_model(' in match[1]:
        replacement=(BOOK/'devtools/ch34_fpso_verified.py').read_text(encoding='utf-8')
    elif 'water_cuts = np.linspace(' in match[1] and 'build_fpso_model(' in match[1]:
        replacement=(BOOK/'devtools/ch34_fpso_sweep.py').read_text(encoding='utf-8')
    else: continue
    edits.append((match.start(1),match.end(1),replacement,hashlib.sha256(match[1].encode()).hexdigest()))
assert len(edits)==2
for start,end,replacement,_ in reversed(edits):source=source[:start]+replacement+source[end:]
chapter.write_text(source,encoding='utf-8')
(BOOK/'verification/scientific_revision/ch34_fence_replacement.json').write_text(json.dumps([
    dict(old_sha256=old,new_sha256=hashlib.sha256(code.encode()).hexdigest()) for _,_,code,old in edits],indent=2),encoding='utf-8')
print('Replaced exactly two FPSO fences; other manuscript content preserved.')
