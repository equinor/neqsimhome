"""Merge reviewed references without duplicating keys; preserve rejected entries."""
from pathlib import Path
import re, json
BOOK = Path(__file__).resolve().parents[1]
OUT = BOOK / 'verification/scientific_revision'
path = BOOK / 'refs.bib'
text = path.read_text(encoding='utf-8')
rejected = []
chapters = '\n'.join(p.read_text(encoding='utf-8') for p in (BOOK/'chapters').glob('*/chapter.md'))
cited = {k.strip() for group in re.findall(r'\\cite\{([^}]+)\}', chapters) for k in group.split(',')}
for key, reason in {
    'dimoplon1978': 'Listed book title/year/publisher could not be substantiated; no manuscript citation uses this entry.',
    'dale2013': 'The listed NTNU publication could not be substantiated; no manuscript citation uses this entry.',
    'norsok_p001': 'Listed sixth edition/2016 could not be substantiated; no manuscript citation uses this entry. Use verified current P-002 metadata and appropriate clause evidence.'
}.items():
    pattern = re.compile(r'^@\w+\{'+re.escape(key)+r',.*?(?=^@\w+\{|\Z)',re.M|re.S)
    match = pattern.search(text)
    if match:
        assert key not in cited, f'Review new use of quarantined reference {key}'
        rejected.append((key, reason, match[0]))
        text = text[:match.start()]+text[match.end():]
if rejected:
    (OUT/'unverified_unused_references.bib').write_text('\n\n'.join('% '+r+'\n'+b for k,r,b in rejected),encoding='utf-8')
existing = set(re.findall(r'^@\w+\{([^,]+),', text, re.M))
added=[]
for filename in ('onshore_refs.bib','foundations_refs.bib','optimization_refs.bib','benchmark_refs.bib'):
    source = OUT/filename
    if not source.exists():
        continue
    for match in re.finditer(r'^@\w+\{([^,]+),.*?(?=^@\w+\{|\Z)',source.read_text(encoding='utf-8-sig'),re.M|re.S):
        if match[1]=='foundationMichelsen1982':
            assert match[1] not in cited
            continue
        if match[1] not in existing:
            text += '\n'+match[0].strip()+'\n'
            existing.add(match[1]); added.append(match[1])
assert 'foundationMichelsen1982' not in cited
text=re.sub(r'^@\w+\{foundationMichelsen1982,.*?(?=^@\w+\{|\Z)','',text,flags=re.M|re.S)
path.write_text(text,encoding='utf-8')
print('Added reference keys:', added)
print('Unresolved citation keys:', sorted(cited-existing))
