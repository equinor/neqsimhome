from pathlib import Path
import hashlib, json, re, sys
BOOK=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(BOOK/'.build/python_packages'))
sys.path.insert(0,str(BOOK.parents[1]/'tools'))
import typst, fitz
from book_render_pdf import build_book_typst_preamble
cfg={'title':'Code layout regression','settings':{'code_font_size':7.2}}
style=build_book_typst_preamble(cfg).split('// ── Code blocks ──')[1].split('// ── Block quotes ──')[0]
assert 'show raw.line: line =>' in style
blocks=[]
for prefix, needle in [('ch12','deethanizer.setSolverType(jneqsim'),('ch32','observed=HashMap();observed.put'),('ch34','liquids=[inlet_sep.getLiquidOutStream()')]:
    chapter=next((BOOK/'chapters').glob(prefix+'*/chapter.md'))
    found=[(lang,code) for lang,code in re.findall(r'^```(python|java)[^\n]*\n(.*?)^```',chapter.read_text(encoding='utf-8'),re.M|re.S) if needle in code]
    assert len(found)==1,(prefix,len(found))
    blocks.append((chapter.parent.name,*found[0]))
blocks.append(('long-token-regression','python','value = "'+'verylongidentifier'*18+'"\nif value:\n    result = value\n'))
blocks.append(('java-layout-regression','java','''if (active) {
    final String label = "Figure 24.2: literal code string must remain verbatim";
    column.setSolverType(neqsim.process.equipment.distillation.DistillationColumn.SolverType.DIRECT_SUBSTITUTION);
    logger.info("Run result {}", label);
}
'''))
body='\n#pagebreak()\n'.join('#text(size: 12pt, weight: "bold")['+name+']\n#raw('+json.dumps(code)+', block: true, lang: '+json.dumps(lang)+')\n' for name,lang,code in blocks)
source='#set page(width:170mm,height:244mm,margin:(left:21mm,right:17mm,top:19mm,bottom:19mm))\n#set text(size:10pt)\n'+style+body
target=OUT/'code_layout_probe.typ';target.write_text(source,encoding='utf-8')
(OUT/'code_layout_probe.pdf').write_bytes(typst.compile(str(target)))
doc=fitz.open(OUT/'code_layout_probe.pdf')
spans=[(i+1,s) for i,p in enumerate(doc) for b in p.get_text('dict')['blocks'] if 'lines'in b for l in b['lines'] for s in l['spans']]
overflow=[{'page':i,'text':s['text'],'bbox':s['bbox']} for i,s in spans if s['bbox'][0]<21/25.4*72-0.5 or s['bbox'][2]>(170-17)/25.4*72+0.5]
assert not overflow,overflow
code_sizes=sorted({round(s['size'],3) for _,s in spans if 'Mono' in s['font']})
assert code_sizes==[7.2],code_sizes
query=json.loads(typst.query(str(target),'raw'))
assert [r['text'] for r in query]==[code for _,_,code in blocks],query
for i,p in enumerate(doc):p.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(OUT/f'code_layout_probe_{i+1:02}.png')
record={'pages':len(doc),'overflow':overflow,'code_font_sizes_pt':code_sizes,'raw_source_preserved':True,'blocks':[{'chapter':name,'code_sha256':hashlib.sha256(code.encode()).hexdigest()} for name,_,code in blocks]}
(OUT/'code_layout_probe.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record,indent=2))
