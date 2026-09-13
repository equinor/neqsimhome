from pathlib import Path
import os,sys,re,json,hashlib
B=Path(__file__).resolve().parents[1]
S=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
os.environ['NEQSIM_PROJECT_ROOT']=str(S);os.environ['MPLBACKEND']='Agg';os.environ['_JAVA_OPTIONS']='-Xmx512m'
sys.path[:0]=[str(B/'.build/python_packages'),str(S/'devtools'),str(B/'devtools')]
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=S,recompile=False,verbose=False)
from optimization_solution_helpers import process_checks
C=next((B/'chapters').glob('ch24*'))
F=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',(C/'chapter.md').read_text(encoding='utf-8-sig'),re.M|re.S))
work=B/'.build/stock_tank_probe';work.mkdir(exist_ok=True);os.chdir(work)
ns={'__name__':'__main__'}
for i in [5,62]:exec(compile(F[i-1][3],f'fence{i}','exec'),ns)
print('Final process checks',len(process_checks(ns['process'])))
print(json.dumps({k:[min(ns[k]),max(ns[k])] for k in ['oil_rates','gas_rates','comp_powers','revenues']}))
print('Flash products',ns['stock_tank_results'][0])
sys.stdout.flush();os._exit(0)
