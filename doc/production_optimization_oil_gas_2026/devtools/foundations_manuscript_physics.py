"""Execute literal manuscript blocks and verify selected declared engineering cases.

Checks are attached to concrete solved objects, not inferred from absence of exceptions.
The report retains source-code hashes and all gate measurements.
"""
from pathlib import Path
import sys,os,re,json,hashlib,time,traceback,contextlib,io,argparse
BOOK=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BOOK/'.build/python_packages'))
parser=argparse.ArgumentParser();parser.add_argument('--chapter',required=True);parser.add_argument('--probe',action='store_true');args=parser.parse_args()
SRC=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
os.environ['NEQSIM_PROJECT_ROOT']=str(SRC);os.environ['JAVA_TOOL_OPTIONS']='-Xmx512m'
sys.path.insert(0,str(SRC/'devtools'))
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=SRC,recompile=False,verbose=False)
import jpype,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
j=jpype.JPackage('neqsim')
chapter=next((BOOK/'chapters').glob(args.chapter+'*/chapter.md'));source=chapter.read_text(encoding='utf-8')
work=BOOK/'.build/scientific_revision_cases'/chapter.parent.name;work.mkdir(parents=True,exist_ok=True);(work/'figures').mkdir(exist_ok=True);os.chdir(work)
report={'chapter':chapter.parent.name,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'python':sys.executable,'source_root':str(SRC),'literal_blocks':[],'physical_checks':[]}
out=BOOK/'verification/scientific_revision'/(args.chapter+'_manuscript_physics.json')
scope={'__name__':'__main__','jneqsim':j}

def save():out.write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')
def finite_json(x):
 if isinstance(x,float) and not np.isfinite(x):return str(x)
 return x
def physical_gates(index, code, namespace=None):
 """Check only units explicitly run by this literal block or its flowsheet."""
 active=scope if namespace is None else namespace
 units=[]
 for name in re.findall(r'\b([A-Za-z_]\w*)\.run\s*\(',code):
  obj=active.get(name)
  if obj is None:continue
  if hasattr(obj,'getUnitOperations'):
   units.extend(list(obj.getUnitOperations()))
  else:units.append(obj)
 seen=set()
 for obj in units:
  if not hasattr(obj,'getClass') or not hasattr(obj,'getInletStreams'):continue
  cls=str(obj.getClass().getSimpleName());name=str(obj.getName())
  identity=(cls,name,int(obj.hashCode()))
  if identity in seen:continue
  seen.add(identity)
  if cls=='DistillationColumn':
   from foundations_column_gates import column_gates
   report['physical_checks'].extend(column_gates(index,obj))
   continue
  if cls not in ['Separator','ThreePhaseSeparator','GasScrubber','Mixer','StaticMixer','ThrottlingValve','Compressor','Pump','Heater','Cooler','HeatExchanger','PipeBeggsAndBrills']:continue
  row={'block':index,'equipment':name,'class':cls,'scope':'steady-flow conservation and state domain; not empirical model calibration','checks':[]}
  report['physical_checks'].append(row)
  def check(label,error,tol):
   row['checks'].append({'name':label,'error':finite_json(float(error)),'tolerance':tol,'pass':bool(np.isfinite(error) and error<=tol)})
  try:
   ins=list(obj.getInletStreams());outs=list(obj.getOutletStreams())
   if not ins or not outs:raise ValueError('missing boundary streams')
   def state(st):
    f=st.getFluid();f.initProperties()
    return {'mass':float(st.getFlowRate('kg/sec')),'H':float(st.getFlowRate('kg/sec'))*float(f.getEnthalpy('J/kg')),'P':float(st.getPressure('bara')),'T':float(st.getTemperature('K')),
      'components':{str(f.getComponent(k).getComponentName()):float(f.getComponent(k).getNumberOfmoles()) for k in range(f.getNumberOfComponents())}}
   a=[state(x) for x in ins];b=[state(x) for x in outs]
   mi=sum(x['mass'] for x in a);mo=sum(x['mass'] for x in b)
   hi=sum(x['H'] for x in a);ho=sum(x['H'] for x in b)
   check('relative_mass_closure',abs(mi-mo)/max(abs(mi),1e-12),1e-6)
   keys=set(k for x in a+b for k in x['components'])
   ni={k:sum(x['components'].get(k,0) for x in a) for k in keys};no={k:sum(x['components'].get(k,0) for x in b) for k in keys}
   check('component_mole_closure_normalized_by_total_feed',max([abs(ni[k]-no[k]) for k in keys] or [0])/max(sum(abs(x) for x in ni.values()),1e-12),1e-6)
   values=[x[k] for x in a+b for k in ['mass','H','P','T']]
   check('finite_positive_pressure_temperature_nonnegative_flow',0.0 if all(np.isfinite(values)) and all(x['mass']>=0 and x['P']>0 and x['T']>0 for x in a+b) else 1.0,0)
   work=0.0
   if cls in ['Compressor','Pump']:work=float(obj.getPower())
   if cls in ['Heater','Cooler']:work=float(obj.getDuty())
   scale=max(abs(hi),abs(ho),abs(work),1.0)
   if cls!='PipeBeggsAndBrills':check('energy_closure_relative_to_boundary_enthalpy_or_duty',abs(ho-hi-work)/scale,1e-5)
   else:
    row['scope']='pipeline material conservation, finite pressure/temperature, positive-rise pressure-loss sign and profile domain; no heat-loss or multiphase correlation calibration'
    if obj.getElevation()>=0:check('nonnegative_upward_or_horizontal_pressure_drop',max(0,b[0]['P']-a[0]['P']),1e-8)
    pp=list(obj.getPressureProfile());tt=list(obj.getTemperatureProfile())
    check('finite_positive_pressure_temperature_profile',0 if pp and tt and all(np.isfinite(v) and v>0 for v in pp+tt) else 1,0)
    row['thermal_mode']=str(obj.getHeatTransferMode());row['U_W_m2K']=float(obj.getHeatTransferCoefficient())
   if cls=='ThrottlingValve':check('nonnegative_pressure_drop_bar',max(0,b[0]['P']-a[0]['P']),1e-8)
   if cls=='Compressor':
    check('compression_pressure_and_work_sign',max(0,a[0]['P']-b[0]['P'],-work),1e-8)
   if cls=='HeatExchanger' and len(a)==len(b)==2:
    hot=0 if a[0]['T']>=a[1]['T'] else 1;cold=1-hot
    check('counterflow_terminal_approaches_K',max(0,b[cold]['T']-a[hot]['T'],a[cold]['T']-b[hot]['T']),1e-6)
   row['boundary']={'mass_in_kg_s':mi,'mass_out_kg_s':mo,'enthalpy_in_W':hi,'enthalpy_out_W':ho,'external_energy_W':work}
   row['pass']=all(x['pass'] for x in row['checks'])
  except Exception as exc:row['pass']=False;row['error']=str(exc)
 from foundations_flash_gates import flash_gates
 for name in re.findall(r'\b(\w+)\.TPflash\s*\(',code):
  ops=active.get(name)
  if ops is not None and hasattr(ops,'getSystem'):
   report['physical_checks'].append(flash_gates(index,name,ops.getSystem()))
def examine(index):
 observations=[]
 for name,obj in list(scope.items()):
  if name.startswith('_') or not hasattr(obj,'getClass'):continue
  try:cls=str(obj.getClass().getName())
  except Exception:continue
  if not cls.startswith('neqsim.'):continue
  obs={'name':name,'class':cls}
  for method,unit in [('getFlowRate','kg/sec'),('getPressure','bara'),('getTemperature','C'),('getPower','W')]:
   if hasattr(obj,method):
    try:obs[method+'_'+unit]=finite_json(float(getattr(obj,method)(unit)))
    except Exception:pass
  if hasattr(obj,'getInletStreams'):
   try:obs['inlets']=[str(x.getName()) for x in obj.getInletStreams()];obs['outlets']=[str(x.getName()) for x in obj.getOutletStreams()]
   except Exception:pass
  if 'process' in cls or 'thermo.system' in cls:observations.append(obs)
 return observations

for idx,m in enumerate(re.finditer(r'^```(python|java)\s*\n(.*?)^```',source,re.M|re.S),1):
 if m[1]!='python':continue
 row={'index':idx,'code_sha256':hashlib.sha256(m[2].encode()).hexdigest(),'line':source[:m.start()].count('\n')+1}
 report['literal_blocks'].append(row);started=time.monotonic();capture=io.StringIO()
 try:
  filename=str(chapter)+':'+str(row['line'])
  pending={};literal_lines=m[2].splitlines()
  def completed_calculation(frame,event,arg):
   if frame.f_code.co_filename!=filename:return None
   ident=id(frame)
   if event=='exception':pending.pop(ident,None)
   elif event in ['line','return']:
    prior=pending.pop(ident,None)
    if prior is not None:physical_gates(idx,prior,dict(frame.f_globals,**frame.f_locals))
    if event=='line' and 0<frame.f_lineno<=len(literal_lines):
     line=literal_lines[frame.f_lineno-1]
     if re.search(r'\b\w+\.(run|TPflash)\s*\(',line):pending[ident]=line
   return completed_calculation
  sys.settrace(completed_calculation)
  try:
   with contextlib.redirect_stdout(capture),contextlib.redirect_stderr(capture):exec(compile(m[2],filename,'exec'),scope)
  finally:sys.settrace(None)
  row['execution']='pass'
  from foundations_case_gates import case_gates
  report['physical_checks'].extend(case_gates(args.chapter,idx,m[2],scope))
  if args.probe:row['objects']=examine(idx)
 except Exception:row['execution']='fail';row['traceback']=traceback.format_exc()
 row['seconds']=time.monotonic()-started;row['output']=capture.getvalue();plt.close('all');save();print(args.chapter,idx,row['execution'],flush=True)
save()
