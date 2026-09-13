"""Retrieve primary publisher-deposited Crossref metadata; never auto-substitute titles."""
from pathlib import Path
import re, json, urllib.request, urllib.parse, concurrent.futures, difflib
BOOK = Path(__file__).resolve().parents[1]
OUT = BOOK / 'verification/scientific_revision/references/crossref'
OUT.mkdir(parents=True, exist_ok=True)
source = (BOOK / 'refs.bib').read_text(encoding='utf-8')
def entries(text):
    for start in re.finditer(r'@(\w+)\s*\{([^,]+),', text):
        pos, level = start.end(), 1
        while pos < len(text) and level:
            level += (text[pos] == '{')-(text[pos] == '}')
            pos += 1
        yield start[1], start[2], text[start.end():pos-1]
def field(block, name):
    match = re.search(r'\b'+name+r'\s*=\s*\{', block)
    if not match:
        return ''
    pos, begin, depth = match.end(), match.end(), 1
    while pos < len(block) and depth:
        depth += (block[pos] == '{')-(block[pos] == '}')
        pos += 1
    return block[begin:pos-1]
def normalize(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())
def fetch(entry):
    kind, key, block = entry
    title = field(block, 'title')
    rawpath = OUT / (key+'.json')
    try:
        if rawpath.exists():
            raw = json.loads(rawpath.read_text(encoding='utf-8'))
        else:
            url = 'https://api.crossref.org/works?'+urllib.parse.urlencode({'query.title': title, 'rows': 3})
            req = urllib.request.Request(url, headers={'User-Agent': 'NeqSim-PaperLab-bibliographic-review/1.0'})
            with urllib.request.urlopen(req, timeout=30) as response:
                raw = json.load(response)
            rawpath.write_text(json.dumps(raw, indent=2), encoding='utf-8')
        hits=[]
        for item in raw['message']['items']:
            actual = item.get('title',[''])[0]
            hits.append(dict(title=actual, similarity=difflib.SequenceMatcher(None, normalize(title), normalize(actual)).ratio(),
                doi=item.get('DOI'), authors=item.get('author'), year=item.get('published'),
                journal=item.get('container-title'), volume=item.get('volume'),
                issue=item.get('issue'), pages=item.get('page'), article_number=item.get('article-number')))
        return dict(key=key, original_title=title, original_year=field(block,'year'),
            original_journal=field(block,'journal'), original_pages=field(block,'pages'),
            candidates=sorted(hits,key=lambda x:x['similarity'],reverse=True), status='retrieved')
    except Exception as exc:
        return dict(key=key, original_title=title, status='unresolved', reason=str(exc))
selected = [entry for entry in entries(source) if entry[0] in ('article','inproceedings') or field(entry[2], 'journal')]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(fetch, selected))
(OUT.parent.parent / 'bibliographic_metadata_audit.json').write_text(json.dumps(results, indent=2),encoding='utf-8')
for row in results:
    best=(row.get('candidates') or [{}])[0]
    print(row['key'], best.get('similarity'), best.get('doi'), best.get('year'), best.get('journal'), best.get('volume'), best.get('pages'))
