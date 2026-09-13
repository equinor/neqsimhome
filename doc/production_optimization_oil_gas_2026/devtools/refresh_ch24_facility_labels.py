"""Reexecute the self-contained facility fence after figure-only label correction.

All old sequential evidence is archived. Only the changed fence's exact-hash
record is replaced by this explicitly isolated, fresh-JVM execution.
"""
from pathlib import Path
import os,sys,re,json,hashlib,contextlib,io,time
B=Path(__file__).resolve().parents[1]
S=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
os.environ['NEQSIM_PROJECT_ROOT']=str(S);os.environ['MPLBACKEND']='Agg';os.environ['_JAVA_OPTIONS']='-Xmx512m'
sys.path[:0]=[str(B/'.build/python_packages'),str(S/'devtools'),str(B/'devtools')]
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=S,recompile=False,verbose=False)
import optimization_solution_hooks as hooks
C=next((B/'chapters').glob('ch24*'));n=24;i=69
fences=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',(C/'chapter.md').read_text(encoding='utf-8-sig'),re.M|re.S))
code=fences[i-1][3];digest=hashlib.sha256(code.encode()).hexdigest()
work=B/'.build/solution_runs'/C.name;os.chdir(work)
ns={'__name__':'__main__'};hooks.before_fence(n,i,ns,code)
def trace(frame,event,arg):
 if frame.f_code.co_filename.startswith(C.name+':fence'):hooks.on_trace(n,i,frame,event,arg)
 return trace
captured=io.StringIO();start=time.monotonic()
with contextlib.redirect_stdout(captured):
 sys.settrace(trace)
 try:exec(compile(code,f'{C.name}:fence{i}','exec'),ns)
 finally:sys.settrace(None)
 checks=hooks.after_fence(n,i,ns,code)
assert checks and all(r['passed'] for r in checks)
row={'number':69,'sha256':digest,'code_sha256':digest,'language':'python','checks':checks,
     'seconds':time.monotonic()-start,'status':'passed','output':captured.getvalue(),
     'execution_context':'Self-contained literal69 in a fresh source-backed JVM after plot-label-only correction.'}
path=B/'verification/scientific_revision/ch24_solution_checks.json'
data=path.read_bytes();report=json.loads(data);assert report['all_targeted_checks_passed']
archive=B/'verification/scientific_revision/prior_execution_records';archive.mkdir(exist_ok=True)
(archive/(hashlib.sha256(data).hexdigest()+'.json')).write_bytes(data)
report['entries']=[row if old['number']==69 else old for old in report['entries']]
for old in report['prerequisite_fences']:
 if old['number']==69:old.update(sha256=digest,status='passed',execution_context=row['execution_context'])
report['isolated_refresh']={'script':str(Path(__file__).resolve()),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'fence':69,'prior_record_sha256':hashlib.sha256(data).hexdigest()}
path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
figure=work/'figures/facility_optimization_results.png'
(B/'verification/scientific_revision/ch24_facility_plot_arrays.json').write_text(json.dumps({
 'status':'passed','fence':69,'code_sha256':digest,'image':str(figure),'image_sha256':hashlib.sha256(figure.read_bytes()).hexdigest(),
 'sweep_data':ns['sweep_data'],'native_returned_rate_kg_hr':float(ns['result'].getOptimalRate()),
 'native_reported_feasible':bool(ns['result'].isFeasible()),'checks':checks},indent=2),encoding='utf-8')
print('69 isolated label/array refresh passed',flush=True);os._exit(0)
