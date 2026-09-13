"""Independent boundary/stage reconstructions for the exact manuscript columns."""
import math
def column_gates(block,col):
 rows=[]
 def boundary(name,ins,outs,q):
  checks=[];row=dict(block=block,equipment=name,**{'class':'DistillationColumn'},scope='specified-feed equilibrium column conservation, active MESH and phase equilibrium; not tray efficiency or field calibration',checks=checks);rows.append(row)
  def gate(label,error,tol):checks.append(dict(name=label,error=error if math.isfinite(error) else str(error),tolerance=tol,**{'pass':math.isfinite(error) and error<=tol}))
  def state(st):
   f=st.getFluid();f.initProperties();m=float(st.getFlowRate('kg/sec'))
   return dict(m=m,h=m*float(f.getEnthalpy('J/kg')),p=float(st.getPressure('bara')),t=float(st.getTemperature('K')),n={str(f.getComponent(i).getComponentName()):float(f.getComponent(i).getNumberOfmoles()) for i in range(f.getNumberOfComponents())})
  a=[state(s) for s in ins];b=[state(s) for s in outs]
  mi=sum(x['m'] for x in a);mo=sum(x['m'] for x in b);hi=sum(x['h'] for x in a);ho=sum(x['h'] for x in b)
  gate('mass_relative',abs(mi-mo)/max(abs(mi),1e-12),1e-6)
  keys=set(k for x in a+b for k in x['n']);ni={k:sum(x['n'].get(k,0) for x in a) for k in keys};no={k:sum(x['n'].get(k,0) for x in b) for k in keys};scale=sum(ni.values())
  gate('component_relative_with_trace_floor',max(abs(ni[k]-no[k])/max(abs(ni[k]),1e-8*scale) for k in keys),1e-5)
  gate('energy_relative',abs(ho-hi-q)/max(abs(hi),abs(ho),abs(q),1),1e-5)
  gate('finite_positive_state',0 if all(all(math.isfinite(x[k]) for k in ['m','h','p','t']) and x['m']>=0 and x['t']>0 and x['p']>0 for x in a+b) else 1,0)
  row['boundary']=dict(mass_in_kg_s=mi,mass_out_kg_s=mo,enthalpy_in_W=hi,enthalpy_out_W=ho,external_energy_W=q)
  row['pass']=all(c['pass'] for c in checks)
  return row,gate
 try:
  # These manuscript cases have no condenser; reboiler heat is the only duty.
  try:q=float(col.getReboiler().getDuty())
  except Exception:q=0.0
  row,gate=boundary(str(col.getName()),list(col.getInletStreams()),list(col.getOutletStreams()),q)
  gate('rigorous_converged_status',0 if str(col.getLastSolveStatus())=='RIGOROUS_CONVERGED' else 1,0)
  gate('mesh_infinity_norm',float(col.getLastMeshResidualNorm()),1e-5)
  row['pass']=all(c['pass'] for c in row['checks'])
  for i in range(col.getNumberOfTrays()):
   tray=col.getTray(i)
   row,gate=boundary(str(col.getName())+' stage '+str(i),list(tray.getInletStreams()),[tray.getGasOutStream(),tray.getLiquidOutStream()],q if i==0 else 0.0)
   f=tray.getThermoSystem().clone();f.init(3);errors=[]
   for p in range(f.getNumberOfPhases()):gate('phase_'+str(p)+'_mole_fraction_sum',abs(sum(f.getPhase(p).getComponent(k).getx() for k in range(f.getNumberOfComponents()))-1),1e-8)
   if f.getNumberOfPhases()==2:
    for k in range(f.getNumberOfComponents()):
     a,b=[f.getPhase(p).getComponent(k) for p in range(2)];fa=a.getx()*a.getFugacityCoefficient();fb=b.getx()*b.getFugacityCoefficient()
     if min(fa,fb)>1e-14:errors.append(abs(math.log(fa/fb)))
    gate('max_log_phase_fugacity_ratio',max(errors or [0]),1e-5)
   row['phase_count']=int(f.getNumberOfPhases());row['pass']=all(c['pass'] for c in row['checks'])
 except Exception as exc:rows.append(dict(block=block,equipment=str(col.getName()),**{'class':'DistillationColumn','pass':False},error=str(exc)))
 return rows
