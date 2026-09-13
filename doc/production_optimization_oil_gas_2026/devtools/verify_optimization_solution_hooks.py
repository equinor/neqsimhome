"""Execute exact literal Python with chapter-specific solution-verification hooks.

Hook module contract:
  TARGET_FENCES = {19: [1, 2, ...], ...}
  after_fence(chapter_number, fence_number, namespace, literal_code) -> list[dict]
Each returned check includes name, passed, observed and optionally expected,
tolerance and scope. Optional before_fence with same arguments can install
fixtures. Optional on_trace(chapter, fence, frame, event, arg) observes actual
Python manuscript line events; do not mutate the manuscript's numerical inputs.
The hooks must assert meaningful conditions, not only absence of exceptions.
"""
from pathlib import Path
import argparse,contextlib,hashlib,importlib.util,io,json,os,re,sys,time,traceback,subprocess
B=Path(__file__).resolve().parents[1]
SOURCE=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
P=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--chapter',type=int,required=True)
 parser.add_argument('--hooks',type=Path,required=True);parser.add_argument('--output',type=Path)
 args=parser.parse_args();n=args.chapter;args.hooks=args.hooks.resolve()
 os.environ['NEQSIM_PROJECT_ROOT']=str(SOURCE);os.environ['MPLBACKEND']='Agg'
 os.environ.setdefault('_JAVA_OPTIONS','-Xmx512m')
 sys.path.insert(0,str(B/'.build/python_packages'));sys.path.insert(0,str(SOURCE/'devtools'))
 from neqsim_dev_setup import neqsim_init
 neqsim_init(project_root=SOURCE,recompile=False,verbose=False)
 spec=importlib.util.spec_from_file_location('solution_hooks',args.hooks.resolve())
 hooks=importlib.util.module_from_spec(spec);spec.loader.exec_module(hooks)
 targets=set(hooks.TARGET_FENCES[n]);assert targets
 chapter=next((B/'chapters').glob(f'ch{n:02d}_*'));text=(chapter/'chapter.md').read_text(encoding='utf-8-sig')
 work=B/'.build/solution_runs'/chapter.name;work.mkdir(parents=True,exist_ok=True);os.chdir(work)
 ns={'__name__':'__main__','__file__':str(chapter/'chapter.md')}
 output=args.output or B/f'verification/scientific_revision/ch{n:02d}_solution_checks.json'
 archive=B/'verification/scientific_revision/hook_sources';archive.mkdir(exist_ok=True)
 hook_bytes=args.hooks.read_bytes();hook_digest=hashlib.sha256(hook_bytes).hexdigest()
 (archive/(hook_digest+'.py')).write_bytes(hook_bytes)
 helper_records=[]
 for module in list(sys.modules.values()):
  filename=getattr(module,'__file__',None)
  if filename and Path(filename).parent==B/'devtools' and 'solution' in Path(filename).name:
   data=Path(filename).read_bytes();digest=hashlib.sha256(data).hexdigest()
   (archive/(digest+'.py')).write_bytes(data)
   helper_records.append({'module':str(filename),'sha256':digest,'snapshot':str((archive/(digest+'.py')).relative_to(B))})
 report={'chapter':chapter.name,'source_commit':subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip(),
         'python_executable':sys.executable,'hook_module':str(args.hooks.resolve()),
         'hook_sha256':hook_digest,'hook_snapshot':str((archive/(hook_digest+'.py')).relative_to(B)),
         'helper_sources':helper_records,
         'interpretation':'Exact literal execution with supplementary numerical/physical/software solution checks; not field calibration.',
         'prerequisite_fences':[],'entries':[]}
 failures=[]
 for i,m in enumerate(P.finditer(text),1):
  if i>max(targets):break
  lang,ann,code=m.groups();digest=hashlib.sha256(code.encode()).hexdigest()
  if lang!='python' or 'pattern' in ann:continue
  filename=f'{chapter.name}:fence{i}'
  row={'number':i,'sha256':digest,'code_sha256':digest,'language':lang,'checks':[]}
  captured=io.StringIO();start=time.monotonic()
  try:
   if hasattr(hooks,'before_fence'):hooks.before_fence(n,i,ns,code)
   def trace(frame,event,arg):
    if frame.f_code.co_filename.startswith(chapter.name+':fence') and hasattr(hooks,'on_trace'):
     hooks.on_trace(n,i,frame,event,arg)
    return trace
   with contextlib.redirect_stdout(captured),contextlib.redirect_stderr(captured):
    if hasattr(hooks,'on_trace'):sys.settrace(trace)
    try:exec(compile(code,filename,'exec'),ns)
    finally:sys.settrace(None)
    if i in targets:
     row['checks']=hooks.after_fence(n,i,ns,code)
     assert row['checks'], 'Targeted fence must return substantive checks'
     assert all(check.get('passed') is True for check in row['checks']),row['checks']
   row['status']='passed'
  except BaseException as exc:
   sys.settrace(None)
   if hasattr(hooks,'partial_checks'):
    row['checks']=hooks.partial_checks(n,i)
   if isinstance(exc,AssertionError) and exc.args and isinstance(exc.args[0],dict):
    row['checks'].append(exc.args[0])
   row.update(status='failed',error=str(exc),traceback=traceback.format_exc());failures.append(i)
  row['seconds']=time.monotonic()-start;row['output']=captured.getvalue()
  report['prerequisite_fences'].append({'number':i,'sha256':digest,'status':row['status']})
  if i in targets or row['status']=='failed':report['entries'].append(row)
  report['all_targeted_checks_passed']=not failures and set(e['number'] for e in report['entries'])>=targets
  output.parent.mkdir(parents=True,exist_ok=True)
  output.write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str),encoding='utf-8')
  print(n,i,row['status'],row.get('error','')[:160],flush=True)
  if row['status']=='failed':break
 sys.stdout.flush();sys.stderr.flush();os._exit(1 if failures else 0)

if __name__=='__main__':main()
