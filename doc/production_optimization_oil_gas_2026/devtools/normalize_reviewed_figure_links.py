"""Apply canonical source labels after final placement; preserve literal code."""
from pathlib import Path
import hashlib,json,re,sys
B=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(B/'.build/python_packages'),str(B.parents[1]/'tools')]
import book_improvement_tools as tools
P=re.compile(r'^```[^\n]*\n.*?^```[^\n]*(?:\n|$)',re.M|re.S)
files=sorted((B/'chapters').glob('*/chapter.md'))
originals={p:p.read_text(encoding='utf-8') for p in files}
before={p:P.findall(text) for p,text in originals.items()}
# Meaningful regression: the canonical normalizer must attach a figure label
# to either supported observation style without removing any scientific prose.
tests=[]
for style in ('*','**'):
    image='![A source-backed scientific figure](figures/example.png)'
    observation=style+'Observation.'+style+' Density rises from1 to2 kg/m3.'
    source=image+'\n\n'+observation+'\n'
    result,changed=tools._normalise_discussion_heading(source,0,len(image),'Figure 1.1')
    assert changed and '**Discussion (Figure 1.1).**' in result and observation in result
    tests.append({'style':style,'passed':True})
fenced='See Figure 2.1.\n\x60\x60\x60python\nprint("Figure 2.1")\n\x60\x60\x60\n~~~java\nlogger.info("Figure 2.1");\n~~~\n'
fixed,count=tools._relabel_prose_figure_references(fenced,{'Figure 2.1':'Figure 2.2'})
assert count==1 and fixed.startswith('See Figure 2.2.') and 'print("Figure 2.1")' in fixed and 'logger.info("Figure 2.1");' in fixed
tests.append({'fenced_code_relabel_guard':True,'passed':True})
try:
    report=tools.normalize_figure_references(B)
    for p in files:
        assert P.findall(p.read_text(encoding='utf-8'))==before[p],str(p)+' literal code changed'
except BaseException:
    for p,text in originals.items():p.write_text(text,encoding='utf-8')
    raise
report['literal_code_unchanged']=True
report['normalizer_regressions']=tests
report['tool_sha256']=hashlib.sha256(Path(tools.__file__).read_bytes()).hexdigest()
(B/'verification/scientific_revision/figure_reference_normalization.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='changed'},indent=2))
