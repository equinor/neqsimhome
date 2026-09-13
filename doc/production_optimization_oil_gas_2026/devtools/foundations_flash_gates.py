"""Reconstruct phase material and fugacity closure after a published TP flash."""
import math
def flash_gates(block,name,fluid):
 row=dict(block=block,equipment=name,**{'class':'TPflash'},scope='phase material/fugacity closure and state domain; not independent EOS calibration',checks=[])
 def gate(n,e,t):row['checks'].append(dict(name=n,error=e if math.isfinite(e) else str(e),tolerance=t,**{'pass':math.isfinite(e) and e<=t}))
 try:
  f=fluid.clone();f.init(3);np=f.getNumberOfPhases();nc=f.getNumberOfComponents()
  betas=[float(f.getBeta(p)) for p in range(np)]
  gate('finite_positive_T_P',0 if math.isfinite(f.getTemperature()) and math.isfinite(f.getPressure()) and f.getTemperature()>0 and f.getPressure()>0 else 1,0)
  gate('beta_sum',abs(sum(betas)-1),1e-8)
  gate('beta_domain',max([max(0,-b,b-1) for b in betas]),1e-8)
  for p in range(np):gate('phase_'+str(p)+'_composition_sum',abs(sum(f.getPhase(p).getComponent(k).getx() for k in range(nc))-1),1e-8)
  gate('feed_composition_reconstruction',max(abs(f.getComponent(k).getz()-sum(betas[p]*f.getPhase(p).getComponent(k).getx() for p in range(np))) for k in range(nc)),1e-7)
  residuals=[]
  for k in range(nc):
   fug=[]
   for p in range(np):
    c=f.getPhase(p).getComponent(k);v=float(c.getx()*c.getFugacityCoefficient())
    if betas[p]>1e-8 and v>1e-12:fug.append(v)
   if len(fug)>1:residuals.append(math.log(max(fug)/min(fug)))
  gate('maximum_log_phase_fugacity_ratio',max(residuals or [0]),1e-5)
  row.update(phase_count=int(np),temperature_K=float(f.getTemperature()),pressure_bara=float(f.getPressure()))
  row['pass']=all(c['pass'] for c in row['checks'])
 except Exception as exc:row['pass']=False;row['error']=str(exc)
 return row
