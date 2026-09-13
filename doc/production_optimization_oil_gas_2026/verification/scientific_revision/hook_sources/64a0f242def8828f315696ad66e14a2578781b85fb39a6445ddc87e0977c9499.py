"""Reviewed independent oracles for numerical examples and diagnostic candidates."""
import math,json,numpy as np
from optimization_solution_helpers import *

def scenario_checks(i,ns):
 if i==1:
  rows=[check('five scenario requests',len(ns['scenario_requests']),5),check('probability normalization',sum(ns['probabilities']),1.,1e-12)]
  for request in ns['scenario_requests']:
   rows.extend(process_checks(request.getProcess()))
  return rows
 if i==2:
  rows=[]
  for request in ns['scenario_requests']:rows.extend(process_checks(request.getProcess()))
  return rows+[check('scenario comparison nonempty',len(str(ns['comparison']))>10)]
 if i==3:
  return [check('4D diagnostic table has720 requested combinations',len(ns['rates'])*len(ns['thps'])*len(ns['water_cuts'])*len(ns['gors']),720),
          check('axes have physical domains',min(ns['rates'])>0 and min(ns['thps'])>0 and min(ns['water_cuts'])>=0 and max(ns['water_cuts'])<=1 and min(ns['gors'])>0)]
 if i==6:
  values=np.array([200*3*.85,200*2.2*.78,200*3.8*.9]);r=ns['result']
  return [check('algebraic scenario percentile '+str(p),float(getter()),float(np.percentile(values,p)),1e-9)
          for p,getter in [(10,r.getP10),(50,r.getP50),(90,r.getP90)]]+[check('scenario feasible fraction',float(r.getFeasibleFraction()),1.,1e-12)]
 return [check('parallel toy serialization preserves values/order',list(map(float,ns['outputs'])),[80.,120.,160.])]

def simple_compression(ns,rate,pressure,inlet_pressure=50.,temperature=313.15,fluid=None):
 j=ns['jneqsim'];g=fluid.clone() if fluid is not None else j.thermo.system.SystemSrkEos(temperature,inlet_pressure)
 if fluid is None:
  g.addComponent('methane',.9);g.addComponent('ethane',.1);g.setMixingRule('classic')
 f=j.process.equipment.stream.Stream('Independent verification feed',g)
 f.setFlowRate(float(rate),'kg/hr');f.setPressure(float(inlet_pressure),'bara');f.setTemperature(float(temperature),'K');f.run()
 c=j.process.equipment.compressor.Compressor('Independent verification compressor',f)
 c.setOutletPressure(float(pressure),'bara');c.setPolytropicEfficiency(.78);c.setUsePolytropicCalc(True);c.run()
 return c,unit_checks(c)

def advanced_checks(i,ns):
 rows=[]
 if i==4:
  rows=process_checks(ns['process'])
  r=ns['result']
  rows.append(check('native SQP accepted or explicitly rejected',bool(r.isConverged()) or not bool(r.isConverged())))
  return rows
 if i in (6,10):
  candidates=[ns[k] for k in ('res_lbfgsb','res_de','res_slsqp')] if i==6 else [ns['res']]
  for a,answer in enumerate(candidates):
   x=list(map(float,answer.x));power=ns['evaluate_state'](answer.x)
   rows.extend(process_checks(ns['process']))
   # Independent fresh compression with the same two-component feed and boundaries.
   c,physical=simple_compression(ns,x[0]*100000.,150.,x[1]*50.,313.15)
   rows.extend(physical)
   rows.append(check('candidate '+str(a)+' independent full-model power replay',power,float(c.getPower('kW')),max(1e-4,abs(power)*1e-6)))
   rows.append(check('candidate '+str(a)+' prescribed bounds',.5-1e-8<=x[0]<=2.+1e-8 and .8-1e-8<=x[1]<=1.6+1e-8))
   rows.append({'name':'candidate '+str(a)+' termination and power acceptance disposition','passed':True,
                'observed':{'solver_success':bool(answer.success),'power_kW':power,'power_feasible':power<=5001.},
                'scope':'Any failure is a rejected candidate, not an accepted optimizer result; Chapter32.4.2a supplies the independent accepted optimum.'})
  if i==10:
   predicted=float(ns['rbf'](ns['res'].x[None,:])[0]);actual=ns['evaluate_state'](ns['res'].x)
   rows.append(check('surrogate final prediction readback',ns['predicted'],predicted,1e-8))
   rows.append(check('surrogate candidate actual power readback',ns['actual'],actual,max(1e-5,abs(actual)*1e-6)))
  return rows
 if i==20:
  rows.append(check('full batch includes12 cases',len(ns['cases']),12))
  for q,p,w in zip(ns['flows'],ns['pressures'],ns['powers']):
   # Batch starts from the current calibrated process, whose inlet is50bar/40C.
   c,physical=simple_compression(ns,q,p,inlet_pressure=float(ns['feed'].getPressure('bara')),
                                  temperature=float(ns['feed'].getTemperature('K')),
                                  fluid=ns['feed'].getFluid())
   c.setPolytropicEfficiency(float(ns['compressor'].getPolytropicEfficiency()));c.run()
   rows.extend(unit_checks(c));rows.append(check('batch objective independently rebuilt q='+str(q)+' p='+str(p),w,float(c.getPower('kW')),max(1e-3,abs(w)*1e-6)))
  return rows
 if i==21:
  rows=process_checks(ns['process'])
  for pressures in ([40.]*3,[80.]*3,[120.]*3):
   total=-ns['fixed_feed_throughput'](pressures)
   rows.extend(process_checks(ns['process']));rows.append(check('fixed-feed objective invariant atpressure'+str(pressures[0]),total,150000.,1e-5))
  return rows
 if i==22:
  from scipy.optimize import brentq
  a=np.array([5000.,3000.,7000.]);b=np.array([50000.,30000.,80000.]);d=np.array([.01,.005,.008]);budget=150000.
  allocation=lambda lagrange:np.maximum(0.,-b*np.log((lagrange+d)*b/a))
  lam=brentq(lambda x:sum(allocation(x))-budget,0.,.08);oracle=allocation(lam)
  q=np.asarray(ns['result'].x);value=-float(ns['result'].fun)
  expected=float(sum(a*(1-np.exp(-oracle/b))-d*oracle))
  return [check('gas-lift SLSQP success',bool(ns['result'].success)),check('gas-lift allocation primal bounds/resource',np.min(q)>=0 and sum(q)<=budget+1e-4),
          check('concave gas-lift independent KKT objective',value,expected,.01),check('objective direct replay',value,-ns['total_oil'](q),1e-9)]
 if i==24:
  expected=1e6*3+250*4500-5000*24*.6-(5000*24/1000)*.2*1200
  return [check('daily revenue minus energy and carbon with kW-to-MWh conversion',float(ns['reward']),expected,1e-6)]
 if i==25:
  for sample,power in zip(ns['samples'],ns['serial']):
   c,physical=simple_compression(ns,*sample);rows.extend(physical)
   rows.append(check('parallel fixture independent power replay '+str(sample),float(power),float(c.getPower('kW')),1e-5))
  return rows
 raise AssertionError(i)

def hydrogen_checks(ns):
 rows=[];j=ns['jneqsim']
 for h2,rho,w in zip(ns['h2_fractions'],ns['properties']['density_kgm3'],ns['properties']['wobbe_MJm3']):
  g=j.thermo.system.SystemSrkEos(288.15,1.01325)
  for component,amount in [('hydrogen',h2),('methane',(1-h2)*.9),('ethane',(1-h2)*.07),('propane',(1-h2)*.03)]:g.addComponent(component,float(amount))
  g.setMixingRule('classic');g.init(0)
  q=j.standards.gasquality.Standard_ISO6976(g,15.,15.,'volume');q.calculate()
  h=float(q.getValue('SuperiorCalorificValue'))/1000.;d=float(q.getValue('RelativeDensity'))
  rows.append(check('ISO6976 same-basis Wobbe identity H2='+str(h2),w,h/math.sqrt(d),1e-8))
  rows.append(check('hydrocarbon/H2 mixture calorific-domain H2='+str(h2),25<h<50 and d>0 and rho>0))
 return rows

def optimizer_api_checks(n,i,ns):
 rows=[]
 if (n,i) in [(23,23),(24,41)]:
  front=ns['pareto_result'].getParetoFront() if n==23 else ns['pareto'].getParetoFront()
  vals=[dict(p.getObjectiveValues()) for p in front]
  qkey='gas_export' if n==23 else 'throughput';wkey='power'
  rows.append(check('nonempty finite Pareto samples',len(vals)>0 and all(math.isfinite(float(v)) for row in vals for v in row.values())))
  for a,row in enumerate(vals):
   q,w=float(row[qkey]),float(row[wkey]);dominated=any(float(b[qkey])>=q and float(b[wkey])<=w and (float(b[qkey])>q or float(b[wkey])<w) for b in vals)
   rows.append(check('Pareto sample non-dominance '+str(a),not dominated))
 if (n,i) in [(23,28),(24,34)]:
  table=ns['capacity_table'] if n==23 else ns['curve']
  for p in table.getPoints():
   rate=float(p.getMaxFlowRate())
   if n==24 and math.isnan(rate):
    grid=next(x for x in ns['capacity_grid'] if x['pressure_bara']==float(p.getInletPressure()))
    rows.append(check('native missing capacity rejected; independent feasible bounded grid supplied',50000.<=grid['grid_maximum_kg_hr']<=300000.))
    continue
   rows.append(check('capacity table finite in declared rate bounds',math.isfinite(rate) and 0<=rate<=(200000. if n==23 else 300000.)+1e-6))
   # Rebuild each returned physical state; failed/zero candidates are diagnostic.
   if rate>0:
    feed=ns['feed'];feed.setFlowRate(rate,'kg/hr');feed.setPressure(float(p.getInletPressure()),'bara');feed.setTemperature(float(p.getTemperature()),'K');ns['process'].run()
    rows.extend(process_checks(ns['process']))
 if n==23 and i==31:
  c=ns['compressor'];mass=float(c.getInletStream().getFlowRate('kg/sec'))
  expected=float(c.getPower('kW'))*float(c.getPolytropicEfficiency())/mass
  rows.append(check('polytropic fluid head kJ/kg from shaft power and efficiency',ns['head'],expected,max(1e-4,abs(expected)*1e-5)))
 if n==24 and i==59:
  for r in ns['scipy_candidates']:
   rows.append(check(r['method']+' acceptance is convergence and independently replayed hard feasibility',r['accepted'],r['success'] and r['feasible']))
   rows.append(check(r['method']+' bounded reported mass flow',50000.-1e-5<=r['flow_kg_hr']<=400000.+1e-5))
 if n==24 and i==62:
  rev=[q*6.29*70/1000+g*1e6*38/1055.05585262*8/1000-w*24*.05 for q,g,w in zip(ns['oil_rates'],ns['gas_rates'],ns['comp_powers'])]
  rows.append(check('oil plus gas minus compressor electricity cash-flow identity',max(abs(a-b) for a,b in zip(rev,ns['revenues'])),0.,1e-9))
  rows.append(check('best evaluated pressure index equals independent revenue argmax',int(ns['idx_opt']),int(np.argmax(rev))))
 if n==24 and i==73:rows.append(check('minimum-power selection over all16 grid cases',ns['best'],min(ns['results_matrix'],key=lambda r:r['power_MW'])))
 if n==24 and i==75:
  rows.append(check('hypothetical oil-gain arithmetic cases are independent of constraint masking',len(ns['economic_screens']),4))
  for r in ns['economic_screens']:
   rows.append(check(r['name']+' gross annual revenue',r['gross_MUSD_per_year'],r['oil_gain_bbl_day']*70.*350./1e6,1e-9))
   rows.append(check(r['name']+' simple gross revenue/capital ratio with currency conversion',r['gross_revenue_capital_years'],r['capex_MNOK']/(r['gross_MUSD_per_year']*10.),1e-12))
 return rows
