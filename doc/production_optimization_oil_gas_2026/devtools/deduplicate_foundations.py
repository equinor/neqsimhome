from pathlib import Path
import re
import json
BOOK=Path(__file__).resolve().parents[1]
report=[]
for chapter in (1,3,4,7,11):
    p=next((BOOK/'chapters').glob('ch%02d*/chapter.md'%chapter))
    text=p.read_text(encoding='utf-8')
    title=text.splitlines()[0]
    duplicate=text.find('\n'+title+'\n')
    if duplicate<0:continue
    primary=text[:duplicate].rstrip()
    secondary=text[duplicate:]
    backup=BOOK/'.build/foundations_originals'/(p.parent.name+'_secondary_reviewed.md')
    backup.write_text(secondary,encoding='utf-8')
    gallery=re.search(r'^## Figures\s*$',secondary,re.M)
    suffix=secondary[gallery.start():] if gallery else ''
    retained=[]
    if chapter==4:
        unique=re.search(r'^### 4\.7\.2 Well Stream Setup\n(.*?)(?=^### 4\.7\.3)',secondary,re.M|re.S)
        if unique:
            new='### 4.10.5 Well Stream Setup\n'+unique[1]+'\n'
            pos=primary.index('## 4.11 ')
            primary=primary[:pos]+new+primary[pos:]
            retained.append('Well Stream Setup, renumbered 4.10.5')
    # Preserve unique figure placements in the chapter gallery.
    refs=re.findall(r'!\[[^\]]*\]\([^\)]+\)',secondary)
    missing=[ref for ref in refs if ref not in primary and ref not in suffix]
    if missing:
        suffix+='\n\n'+ '\n\n'.join(missing)
    revised=primary+'\n\n'+suffix.strip()+'\n'
    report.append({'chapter':p.parent.name,'words_before':len(text.split()),'words_after':len(revised.split()),
                   'blocks_removed':len(re.findall(r'^```(?:python|java)\s*$',text,re.M))-len(re.findall(r'^```(?:python|java)\s*$',revised,re.M)),
                   'unique_material_retained':retained,'basis':'First version contains the expanded topic coverage; second version repeats the same chapter with older section numbering. Figure gallery retained; full reviewed duplicate backed up.'})
    p.write_text(revised,encoding='utf-8')
(BOOK/'verification/foundations_deduplication.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
