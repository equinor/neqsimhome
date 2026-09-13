from pathlib import Path
import sys,os,re
BOOK=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BOOK/'.build/python_packages'))
SRC=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim');sys.path.insert(0,str(SRC/'devtools'));os.environ['JAVA_TOOL_OPTIONS']='-Xmx512m'
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=SRC,recompile=False,verbose=False)
source=next((BOOK/'chapters').glob('ch10*/chapter.md')).read_text(encoding='utf-8')
code=list(re.finditer(r'^```python\s*\n(.*?)^```',source,re.M|re.S))[5][1]
for mode in ['original','three_phase']:
 scope={};c=code
 if mode=='three_phase':c=c.replace('separator.Separator','separator.ThreePhaseSeparator')
 print('MODE',mode,flush=True);exec(c,scope)
 for key in ['hp_sep','mp_sep','lp_sep']:
  obj=scope[key];a=list(obj.getInletStreams());b=list(obj.getOutletStreams())
  for label,streams in [('IN',a),('OUT',b)]:
   for s in streams:
    f=s.getFluid();h0=f.getEnthalpy();f.init(3);h1=f.getEnthalpy()
    print(key,label,s.getName(),s.getFlowRate('kg/sec'),s.getTemperature('C'),f.getNumberOfPhases(),h0,h1,flush=True)
