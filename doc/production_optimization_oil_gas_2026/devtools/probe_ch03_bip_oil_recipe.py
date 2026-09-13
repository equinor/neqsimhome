import sys,os,re
from pathlib import Path
B=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\GitHub\neqsim\neqsim-paperlab\books\production_optimization_oil_gas_2026');S=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim');sys.path[:0]=[str(B/'.build/python_packages'),str(S/'devtools')];os.environ['JAVA_TOOL_OPTIONS']='-Xmx512m'
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=S,recompile=False,verbose=False)
import jpype
j=jpype.JPackage('neqsim');p=next((B/'chapters').glob('ch03*/chapter.md'));code=list(re.finditer(r'^```python\n(.*?)^```',p.read_text(encoding='utf-8'),re.M|re.S))[7][1];code=code.replace('methane\", 70.0','methane\", 30.0').replace('\"C20\", 12.0','\"C20\", 52.0');s={'jneqsim':j};exec(code,s);f=s['fluid'];P=f.getPressure()
for pressure in [P-.002*P,P,P+.002*P]:
 a=f.clone();a.setPressure(pressure);j.thermodynamicoperations.ThermodynamicOperations(a).TPflash();a.initProperties()
 print('P',pressure,[(str(a.getPhase(k).getPhaseTypeName()),a.getBeta(k),a.getPhase(k).getDensity('kg/m3')) for k in range(a.getNumberOfPhases())],flush=True)
