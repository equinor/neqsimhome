"""Read-only source-caption and dangling prose inventory for final book pass."""
from pathlib import Path
import re,json,hashlib,collections
B=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
FIG=re.compile(r'!\[([^\n]*)\]\(([^\n]+)\)')
records=[];captions={};refs=[];duplicates=[]
for p in sorted((B/'chapters').glob('ch*/chapter.md')):
 n=int(p.parent.name[2:4]);raw=p.read_text(encoding='utf-8-sig');text=re.sub(r'^```[^\n]*\n.*?^```',lambda m:'\n'*m[0].count('\n'),raw,flags=re.M|re.S)
 images=[]
 for i,m in enumerate(FIG.finditer(text),1):
  label,path=m.groups();target=(p.parent/path).resolve();number=re.search(r'^Figure (\d+\.\d+):',label)
  key=number[1] if number else None
  if key:captions.setdefault(key,[]).append({'chapter':n,'path':path,'caption':label})
  images.append({'line':text.count('\n',0,m.start())+1,'label':key,'caption':label,'path':path,'exists':target.exists(),'expected_label':f'{n}.{i}'})
 for line_no,line in enumerate(text.splitlines(),1):
  if line.lstrip().startswith('!['):continue
  for match in re.finditer(r'\b(?:Figure|Fig\.)\s+(\d+\.\d+)\b',line):refs.append({'chapter':n,'line':line_no,'label':match[1],'text':line})
 paragraphs=re.split(r'\n\s*\n',text)
 seen={}
 for paragraph in paragraphs:
  norm=' '.join(paragraph.split())
  if len(norm)>120 and not norm.startswith('![') and norm in seen:duplicates.append({'chapter':n,'text':norm})
  seen[norm]=True
 records.append({'chapter':n,'source':str(p.relative_to(B)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'figures':images})
for row in refs:row['target_exists']=row['label'] in captions
d={'chapters':records,'prose_figure_refs':refs,'duplicate_paragraphs':duplicates,'caption_label_duplicates':{k:v for k,v in captions.items() if len(v)>1},'missing_paths':[{'chapter':r['chapter'],**im} for r in records for im in r['figures'] if not im['exists']],'label_order_mismatches':[{'chapter':r['chapter'],**im} for r in records for im in r['figures'] if im['label']!=im['expected_label']]}
(OUT/'final_figure_editorial_inventory.json').write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'figures':sum(len(r['figures']) for r in records),'missing_paths':d['missing_paths'],'label_mismatches':d['label_order_mismatches'],'duplicate_paragraphs':duplicates,'prose_refs_19_35':[r for r in refs if r['chapter']>=19]},indent=2,ensure_ascii=False))
