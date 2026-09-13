"""Capture exact-source plotted arrays for two self-contained literal cases."""
from pathlib import Path
import os,sys,re,json,hashlib
B=Path(__file__).resolve().parents[1]
S=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
os.environ['NEQSIM_PROJECT_ROOT']=str(S);os.environ['MPLBACKEND']='Agg';os.environ['_JAVA_OPTIONS']='-Xmx512m'
sys.path[:0]=[str(B/'.build/python_packages'),str(S/'devtools'),str(B/'devtools')]
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=S,recompile=False,verbose=False)
import optimization_solution_hooks as hooks
out=[]
for n,i,names,filename in [(30,19,['hours','flow_profile','temp_profile','pressure_profile','model_power','model_sep_T'],'ch21_digital_twin_tracking.png'),
                           (32,2,['grid_production','grid_power','production','power'],'pareto_front.png')]:
 c=next((B/'chapters').glob(f'ch{n:02d}*'))
 fences=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',(c/'chapter.md').read_text(encoding='utf-8-sig'),re.M|re.S))
 code=fences[i-1][3];work=B/'.build/figure_array_replay'/c.name;work.mkdir(parents=True,exist_ok=True);os.chdir(work)
 ns={'__name__':'__main__'};hooks.before_fence(n,i,ns,code)
 def trace(frame,event,arg):
  if frame.f_code.co_filename.startswith(c.name+':fence'):hooks.on_trace(n,i,frame,event,arg)
  return trace
 sys.settrace(trace)
 try:exec(compile(code,f'{c.name}:fence{i}','exec'),ns)
 finally:sys.settrace(None)
 checks=hooks.after_fence(n,i,ns,code)
 arrays={name:list(map(float,ns[name])) for name in names}
 generated=work/'figures'/filename;previous=B/'.build/solution_runs'/c.name/'figures'/filename
 digest=hashlib.sha256(generated.read_bytes()).hexdigest()
 assert digest==hashlib.sha256(previous.read_bytes()).hexdigest(),(n,'Different replay image: inspect before copying')
 out.append({'chapter':c.name,'fence':i,'code_sha256':hashlib.sha256(code.encode()).hexdigest(),
             'source_image':str(previous),'source_sha256':digest,'arrays':arrays,'checks':checks,'status':'passed',
             'scope':'Exact self-contained literal rerun with numerical solution checks, not measured plant data.'})
 print(n,'arrays captured, image byte-identical',flush=True)
(B/'verification/scientific_revision/additional_literal_figure_arrays.json').write_text(json.dumps({'status':'passed','entries':out},indent=2),encoding='utf-8')
sys.stdout.flush();os._exit(0)
