"""Bounded strict convergence probes of literal column feed recipes."""
from pathlib import Path
import sys,os,re,json,traceback,time
BOOK=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BOOK/'.build/python_packages'))
SRC=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim');sys.path.insert(0,str(SRC/'devtools'));os.environ['JAVA_TOOL_OPTIONS']='-Xmx512m'
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=SRC,recompile=False,verbose=False)
out=[]
cases=[('ch11',4,'stabilizer',1,60000),('ch11',5,'stabilizer',1,60000),('ch12',4,'deethanizer',1,100000),('ch12',2,'absorber',5,None)]
suffix=''
if len(sys.argv)>1:
 cases=[('ch11',4,'stabilizer',5,60000),('ch11',5,'stabilizer',5,150000),('ch12',4,'deethanizer',5,100000)]
 suffix='_five'
for ch,idx,var,stages,q in cases:
 src=next((BOOK/'chapters').glob(ch+'*/chapter.md')).read_text(encoding='utf-8');code=list(re.finditer(r'^```python\s*\n(.*?)^```',src,re.M|re.S))[idx-1][1]
 if q is not None:
  code=re.sub(r'("[^"]+", )5(, True, False)',lambda m:m[1]+str(stages)+m[2],code)
  code=re.sub(r'('+var+r'\.addFeedStream\([^,]+, )5\)',lambda m:m[1]+str(stages)+')',code)
  code=re.sub(var+r'\.getReboiler\(\)\.setOutTemperature\([^\n]+',f'{var}.getReboiler().setHeatInput({q})',code)
 # determine column variable for absorber from actual assignment
 if q is None:
  m=re.search(r'(\w+) = .*?DistillationColumn\(',code)
  if m:var=m[1]
 strict=f'''{var}.setSolverType(jneqsim.process.equipment.distillation.DistillationColumn.SolverType.DIRECT_SUBSTITUTION)
{var}.setMaxNumberOfIterations(100, True)
{var}.setTemperatureTolerance(1e-7)
{var}.setMassBalanceTolerance(1e-6)
{var}.setEnthalpyBalanceTolerance(1e-5)
{var}.setEnforceEnergyBalanceTolerance(True)
{var}.setMeshResidualTolerance(1e-5)
{var}.setEnforceMeshResidualTolerance(True)
'''
 code=re.sub(r'^'+var+r'\.setMaxNumberOfIterations\([^\n]+',strict,code,flags=re.M)
 code=re.sub(r'^assert .*$', '',code,flags=re.M)
 row={'chapter':ch,'block':idx,'stages':stages,'Q_W':q};out.append(row);t=time.monotonic();scope={}
 try:
  exec(code,scope);col=scope[var]
  row.update(status=str(col.getLastSolveStatus()),mesh=float(col.getLastMeshResidualNorm()),diagnostics=str(col.getConvergenceDiagnostics()))
  row['code']=code
 except Exception:row['error']=traceback.format_exc()
 row['seconds']=time.monotonic()-t
 (BOOK/('verification/scientific_revision/column_probes'+suffix+'.json')).write_text(json.dumps(out,indent=2),encoding='utf-8')
 print('PROBE',ch,idx,{k:v for k,v in row.items() if k not in ['code','diagnostics']},flush=True)
