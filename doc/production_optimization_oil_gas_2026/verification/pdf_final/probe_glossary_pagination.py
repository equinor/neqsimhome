from pathlib import Path
import sys,json,re,hashlib
B=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent/'glossary_fixture';OUT.mkdir(exist_ok=True)
sys.path[:0]=[str(B/'.build/python_packages'),str(B.parents[1]/'tools')]
import yaml,pypandoc,typst,pymupdf
import book_render_pdf
cfg=yaml.safe_load((B/'book.yaml').read_text(encoding='utf-8'))
preamble=book_render_pdf.build_book_typst_preamble(cfg).split('// ── Title Page ──')[0]
markdown=(B/'backmatter/glossary.md').read_text(encoding='utf-8')
fragment=book_render_pdf.postprocess_typst(pypandoc.convert_text(markdown,'typst',format='md',extra_args=['--wrap=none']))
intro='#set heading(numbering: none)\n= Before Glossary\nA preceding section with substantive text.\n#pagebreak()\n'
variants={'baseline':'','show_set':'#show figure.where(kind: table): set block(breakable: true)\n',
          'body_only':'#show figure.where(kind: table): it => it.body\n'}
records=[]
for name,rule in variants.items():
 source=OUT/(name+'.typ');source.write_text(preamble+rule+intro+fragment,encoding='utf-8');dest=OUT/(name+'.pdf');dest.write_bytes(typst.compile(str(source)))
 doc=pymupdf.open(dest);pages=[]
 for i,page in enumerate(doc):
  lines=[(tuple(line['bbox']),''.join(s['text'] for s in line['spans'])) for block in page.get_text('dict')['blocks'] if block['type']==0 for line in block['lines']]
  bottom=[t for box,t in lines if box[3]>float(page.rect.height)-35 and not t.strip().isdigit()]
  page.get_pixmap(matrix=pymupdf.Matrix(1.4,1.4)).save(OUT/f'{name}_{i+1:02d}.png')
  pages.append({'page':i+1,'chars':len(page.get_text()),'bottom_content_lines':bottom,'text_start':page.get_text()[:160]})
 records.append({'variant':name,'page_count':len(doc),'pages':pages});print(json.dumps(records[-1],ensure_ascii=False),flush=True)
(OUT/'probes.json').write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf-8')
