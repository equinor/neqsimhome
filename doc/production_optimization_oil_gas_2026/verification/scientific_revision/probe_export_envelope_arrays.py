from pathlib import Path
import sys,re,json,hashlib
B=Path(__file__).resolve().parents[2];sys.path.insert(0,str(B/'.build/python_packages'))
S=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim');sys.path.insert(0,str(S/'devtools'))
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=S,recompile=False,verbose=False)
p=next((B/'chapters').glob('ch19_*/chapter.md'));code=list(re.finditer(r'^```python[^\n]*\n(.*?)^```',p.read_text(encoding='utf-8'),re.M|re.S))[3].group(1)
ns={}
try:exec(code,ns)
except AssertionError:
    t=ns['raw_dew_T'];pr=ns['raw_dew_P'];v=ns['valid_dew']
    result={'code_sha256':hashlib.sha256(code.encode()).hexdigest(),'raw_T_K':t.tolist(),'raw_P_bara':pr.tolist(),'invalid_T_K':t[~v].tolist(),'invalid_P_bara':pr[~v].tolist()}
    (B/'verification/scientific_revision/ch19_envelope_array_probe.json').write_text(json.dumps(result,indent=2))
    print('invalid',result['invalid_T_K'],result['invalid_P_bara'],flush=True)
