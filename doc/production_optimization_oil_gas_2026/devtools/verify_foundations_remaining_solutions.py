"""Close six scoped manuscript solution-verification gaps without changing sources."""
from pathlib import Path
import sys,os,re,json,hashlib,math,traceback,contextlib,io
B=Path(__file__).resolve().parents[1];sys.path[:0]=[str(B/'.build/python_packages'),str(B/'devtools')]
S=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim');os.environ['NEQSIM_PROJECT_ROOT']=str(S);os.environ['JAVA_TOOL_OPTIONS']='-Xmx512m';sys.path.insert(0,str(S/'devtools'))
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=S,recompile=False,verbose=False)
import jpype,numpy as np
from scipy.optimize import minimize_scalar
from foundations_flash_gates import flash_gates
j=jpype.JPackage('neqsim');rows=[]
w=B/'.build/foundations_remaining_solution_checks';w.mkdir(exist_ok=True,parents=True);os.chdir(w)
out=B/'verification/scientific_revision/foundations_remaining_solution_checks.json'
def save():out.write_text(json.dumps({'status':'pass' if rows and all(x.get('status')=='pass' for x in rows) else 'fail','scope':'Six exact literal fragments, domain/conservation/analytical identities and fresh saturation brackets; no field/vendor/property-model calibration','entries':rows},indent=2,allow_nan=False),encoding='utf-8')
def code(ch,idx):
 p=next((B/'chapters').glob(ch+'*/chapter.md'));ms=list(re.finditer(r'^```python\n(.*?)^```',p.read_text(encoding='utf-8'),re.M|re.S));return p,ms[idx-1][1]
def ck(r,n,error,tol):
 error=float(error);r['checks'].append({'name':n,'error':error if math.isfinite(error) else str(error),'tolerance':tol,'pass':math.isfinite(error) and abs(error)<=tol})
 if not r['checks'][-1]['pass']:raise AssertionError(n+' '+str(error))
def boo(r,n,b):ck(r,n,0 if b else 1,0)
def phase(r,n,f):
 x=flash_gates(0,n,f);r.setdefault('flash_checks',[]).append(x)
 boo(r,n+' phase material and fugacity closure',x['pass'])
def unit(r,u):
 ins=list(u.getInletStreams());outs=list(u.getOutletStreams());
 def state(s):
  f=s.getFluid();f.initProperties();return float(s.getFlowRate('kg/sec')),float(s.getFlowRate('kg/sec'))*float(f.getEnthalpy('J/kg')),{str(f.getComponent(k).getComponentName()):float(f.getComponent(k).getNumberOfmoles()) for k in range(f.getNumberOfComponents())}
 a=[state(s) for s in ins];b=[state(s) for s in outs];mi=sum(x[0] for x in a);mo=sum(x[0] for x in b);hi=sum(x[1] for x in a);ho=sum(x[1] for x in b)
 name=str(u.getName());work=float(u.getPower()) if hasattr(u,'getPower') else float(u.getDuty()) if hasattr(u,'getDuty') else 0
 ck(r,name+' mass closure',(mo-mi)/mi,1e-6)
 keys=set(k for x in a+b for k in x[2]);ni={k:sum(x[2].get(k,0) for x in a) for k in keys};no={k:sum(x[2].get(k,0) for x in b) for k in keys}
 ck(r,name+' component closure',max(abs(ni[k]-no[k]) for k in keys)/sum(ni.values()),1e-6)
 ck(r,name+' energy closure',(ho-hi-work)/max(1,abs(hi),abs(ho),abs(work)),1e-5)
 for s in ins+outs:boo(r,name+' finite positive T P and nonnegative flow',all(math.isfinite(v) for v in [s.getPressure(),s.getTemperature(),s.getFlowRate('kg/sec')]) and s.getPressure()>0 and s.getTemperature()>0 and s.getFlowRate('kg/sec')>=0)
 r.setdefault('boundaries',[]).append({'unit':name,'mass_in_kg_s':mi,'mass_out_kg_s':mo,'H_in_W':hi,'H_out_W':ho,'external_energy_W':work})
def bracket(r,fluid,pressure=None,temperature=None):
 f=fluid.clone();P=float(f.getPressure()) if pressure is None else pressure;T=float(f.getTemperature()) if temperature is None else temperature
 boo(r,'saturation P T finite positive',math.isfinite(P) and math.isfinite(T) and P>0 and 150<T<700)
 gas=[];delta=max(.05,.002*P)
 for sign in [-1,1]:
  a=f.clone();a.setPressure(P+sign*delta);a.setTemperature(T);j.thermodynamicoperations.ThermodynamicOperations(a).TPflash();a.initProperties();phase(r,'fresh bubble-pressure bracket '+str(sign),a)
  frac=float(a.getBeta(a.getPhaseNumberOfPhase('gas'))) if a.hasPhaseType('gas') else 0.0
  gas.append(frac)
 boo(r,'bubble bracket vapor below and all liquid above',gas[0]>1e-7 and gas[1]<1e-8)
 r.setdefault('saturation_brackets',[]).append({'T_K':T,'candidate_P_bara':P,'delta_P_bar':delta,'gas_mole_fraction_below_above':gas})
for ch,idx in [('ch01',5),('ch03',8),('ch03',9),('ch04',6),('ch05',8),('ch07',5),('ch11',3)]:
 p,c=code(ch,idx);r={'chapter':p.parent.name,'python_index':idx,'code_sha256':hashlib.sha256(c.encode()).hexdigest(),'checks':[]};rows.append(r);s={'jneqsim':j,'__name__':'__main__'};capture=io.StringIO()
 try:
  with contextlib.redirect_stdout(capture):
   if ch=='ch01':exec(compile(code(ch,4)[1],str(p)+':prerequisite4','exec'),s)
   exec(compile(c,str(p)+':'+str(idx),'exec'),s)
  if ch=='ch01':
   for key in ['separation_system','compression_system','gas_processing_system']:
    for u in s[key].getUnitOperations():
     if str(u.getClass().getSimpleName())!='Stream':unit(r,u)
   ck(r,'compression output pressure bara',s['compressor'].getOutletStream().getPressure()-120,1e-8)
   ck(r,'cooler temperature K',s['cooler'].getOutletStream().getTemperature()-313.15,1e-8)
   boo(r,'positive compressor power',s['compressor'].getPower()>0)
   r['scope']='Coupled three-area process actual separator/valve/compressor/cooler material and energy closure, configured outputP/T, positive compression work.'
  elif ch=='ch03':
   if idx==8:
    bracket(r,s['fluid']);r['scope']='Modified-BIP bubble point finite domain and fresh TP phase-transition brackets; no fitted data or BIP calibration claimed.'
   else:
    base={'jneqsim':j};exec(code(ch,8)[1],base);a=base['fluid'].clone();a.setBinaryInteractionParameter(0,a.getNumberOfComponents()-1,float(s['kij_mid']))
    bracket(r,a,float(s['pb_calc']),373.15)
    ck(r,'recovered synthetic BIP',s['kij_mid']-.035,1e-4)
    ck(r,'regression bubble-pressure residual bar',s['residual'],.05)
    r['scope']='Synthetic BIP recovery and pressure residual plus fresh TP vapor/liquid transition at fitted recipe; not laboratory calibration.'
  elif ch=='ch04':
   f=s['well_fluid'];f.initProperties();phase(r,'wellhead stream flash',f)
   ck(r,'specified mass rate kg/hr',s['well_stream'].getFlowRate('kg/hr')-50000,1e-6);ck(r,'specified T C',s['well_stream'].getTemperature('C')-75,1e-8);ck(r,'specified P bara',s['well_stream'].getPressure()-70,1e-8)
   n=s['well_stream'].getFlowRate('kg/sec')/f.getMolarMass();standard=n*8.314462618*288.15/101325*86400/1e6
   ck(r,'total ideal-standard equivalent MSm3/day',s['well_stream'].getFlowRate('MSm3/day')/standard-1,1e-5)
   r['scope']='Wellhead TP flash closure, specified flow/T/P and independent ideal-standard gas-equivalent conversion at288.15K101325Pa; standard-equivalent total flow is not separated gas production.'
  elif ch=='ch05':
   q=np.array([1200.,2100.,2800.]);pw=np.array([180.,150.,120.]);curve=s['curve'];pr=float(s['match'].getReservoirPressure());qm=float(curve.getAbsoluteOpenFlowPotential())
   def obj(p):
    z=pw/p;v=1-.2*z-.8*z*z;qm0=np.dot(q,v)/np.dot(v,v);return np.mean((qm0*v-q)**2)
   fit=minimize_scalar(obj,bounds=(181,781),method='bounded',options={'xatol':1e-10})
   # NeqSim searches1.5bar grid: nearest gridpoint can differ by at most0.75bar.
   ck(r,'grid fit versus continuous least squares bara',pr-fit.x,.751)
   ck(r,'reported RMS residual Sm3/day',s['match'].getRmsError()-math.sqrt(obj(pr)),1e-8)
   ck(r,'AOFP zero-pressure boundary',curve.rateAt(0)-qm,1e-8)
   ck(r,'zero production at reservoir pressure',curve.rateAt(pr),1e-8)
   expected=qm*(1-.2*100/pr-.8*(100/pr)**2)
   ck(r,'interpolated deliverability versus Vogel at100bara relative',curve.rateAt(100)/expected-1,.003)
   vals=[curve.rateAt(float(x)) for x in np.linspace(0,pr,30)];boo(r,'bounded monotone IPR',all(0<=v<=qm+1e-6 for v in vals) and all(a>=b for a,b in zip(vals,vals[1:])))
   r['values']={'reservoir_pressure_bara':pr,'continuous_fit_bara':float(fit.x),'AOFP_Sm3_day':qm,'RMS_Sm3_day':float(s['match'].getRmsError()),'rate_100bara_Sm3_day':float(curve.rateAt(100))};r['scope']='Independent continuous least-squares Vogel fit, residual recomputation, pressure/rate domain and zero-flow/AOFP limits.1.5bar solver grid permits0.751bar fit error; curve interpolation permits0.3%.'
  elif ch=='ch07':
   d=json.loads(str(s['json_output']));des=s['design'];well=s['well'];r['reported_design']=d
   boo(r,'configured tubing OD below production casing OD',well.getTubingOD()<well.getProductionCasingOD())
   for key in ['productionCasingWallThicknessMm','tubingWallThicknessMm']:boo(r,key+' positive finite',math.isfinite(d['designResults'][key]) and d['designResults'][key]>0)
   boo(r,'wall thickness smaller than corresponding radius',d['designResults']['productionCasingWallThicknessMm']<well.getProductionCasingOD()*25.4/2 and d['designResults']['tubingWallThicknessMm']<well.getTubingOD()*25.4/2)
   expected=23*0.45359237/.3048*(3800-350)/1000
   ck(r,'tubing mass lb/ft to tonnes independent conversion',d['weights']['totalTubingWeightTonnes']/expected-1,2e-5)
   ce=des.getCostEstimator();cost=d['costEstimation'];subtotal=sum(float(getattr(ce,m)()) for m in ['getDrillingCost','getCasingMaterialCost','getCementCost','getMudCost','getBitsCost','getCompletionCost','getWellheadCost','getSafetyValveCost','getLoggingCost','getWellTestCost'])
   ck(r,'cost subtotal plus contingency USD',cost['totalCostUSD']-subtotal-ce.getContingencyCost(),1e-6)
   boo(r,'positive estimated cost and dimensions',cost['totalCostUSD']>0 and d['weights']['totalCasingWeightTonnes']>0)
   r['scope']='Dimensional mechanical/cost screening: casing/tubing geometry domain, independent tubing mass conversion, itemized total-cost closure; no casing load-case, barrier functional or cost-model validation.'
  elif ch=='ch11':
   vals=[s['tvp_37_8'],s['tvp_50'],s['tvp_60']];boo(r,'TVP increasing with temperature',0<vals[0]<vals[1]<vals[2])
   for T,v in zip([37.8,50,60],vals):bracket(r,s['stream'].getFluid(),v/100,T+273.15)
   r['scope']='Three equilibrium bubble pressures: kPa/bar conversion, monotone vapor-pressure trend and independently rerun TP phase-transition brackets. NotASTM Reid vapor pressure.'
  r['status']='pass'
 except Exception as e:r['status']='fail';r['error']=str(e);r['traceback']=traceback.format_exc()
 r['literal_output']=capture.getvalue();save();print(ch,idx,r['status'],r.get('error',''),flush=True)
print('PASS' if all(x['status']=='pass' for x in rows) else 'FAIL')
