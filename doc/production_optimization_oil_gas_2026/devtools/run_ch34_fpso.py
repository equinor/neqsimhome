from pathlib import Path
import hashlib, json, os, sys, re
BOOK=Path(__file__).resolve().parents[1]
SRC=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
sys.path[:0]=[str(BOOK/'.build/python_packages'),str(SRC/'devtools')]
os.environ['JAVA_TOOL_OPTIONS']='-Xmx512m'
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=SRC,recompile=False,verbose=False)
chapter=BOOK/'chapters/ch34_case_studies/chapter.md'
source=chapter.read_text(encoding='utf-8')
blocks=[m[1] for m in re.finditer(r'^```python[^\n]*\n(.*?)^```',source,re.M|re.S)
        if 'def build_fpso_model(' in m[1] or ('water_cuts = np.linspace(' in m[1] and 'build_fpso_model(' in m[1])]
assert len(blocks)==2
os.chdir(chapter.parent)
ns={};executions=[]
for code in blocks:
    exec(compile(code,'ch34_fpso_literal','exec'),ns)
    executions.append(dict(sha256=hashlib.sha256(code.encode()).hexdigest(),status='passed'))
report=dict(literal=True,executions=executions,base=ns['fpso_base'],
            sweep=ns['fpso_sweep'],balances=ns['fpso_balance_checks'])
(BOOK/'verification/scientific_revision/ch34_fpso_physics.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PASS',len(report['sweep']),'cases',len(report['balances']),'balance checks')
