"""Chapter21 physical balances, fixed-input semantics and independent rate screens."""
from collections import defaultdict
import math
import os
import numpy as np
import jpype

TARGET_FENCES={21:[25,28,29,30,31,32,36,39]}
checks=defaultdict(list)
previous={}
code_lines={}
def check(i,name,condition,observed,expected,scope='solution verification under declared synthetic assumptions'):
    row={'name':name,'passed':bool(condition),'observed':observed,'expected':expected,'scope':scope}
    checks[i].append(row)
    assert condition,row
def state(stream):
    f=stream.getFluid();f.initProperties();m=float(stream.getFlowRate('kg/sec'))
    return m,m*float(f.getEnthalpy('J/kg')),{str(f.getComponent(k).getComponentName()):float(f.getComponent(k).getNumberOfmoles()) for k in range(f.getNumberOfComponents())}
def balance(i,unit):
    name=str(unit.getName());kind=str(unit.getClass().getSimpleName())
    if kind=='Stream':return
    ins=list(unit.getInletStreams());outs=list(unit.getOutletStreams())
    assert ins and outs,(name,kind)
    a=[state(s) for s in ins];b=[state(s) for s in outs]
    mi=sum(s[0] for s in a);mo=sum(s[0] for s in b)
    hi=sum(s[1] for s in a);ho=sum(s[1] for s in b)
    ni=defaultdict(float);no=defaultdict(float)
    for row in a:
        for k,v in row[2].items():ni[k]+=v
    for row in b:
        for k,v in row[2].items():no[k]+=v
    mass=abs(mi-mo)/max(abs(mi),1e-12)
    comp=max(abs(ni[k]-no[k]) for k in ni.keys()|no.keys())/max(sum(abs(v) for v in ni.values()),1e-12)
    power=float(unit.getPower()) if kind=='Compressor' else float(unit.getDuty()) if kind in ('Heater','Cooler') else 0.0
    energy=abs(ho-hi-power)/max(abs(hi),abs(ho),abs(power),1.0)
    check(i,name+' mass/component/energy',max(mass,comp)<=1e-7 and energy<=1e-5,
          {'mass_relative':mass,'component_relative':comp,'energy_relative':energy},'mass/component<=1e-7;energy<=1e-5')
    for s in ins+outs:
        vals=[float(s.getPressure('bara')),float(s.getTemperature('K')),float(s.getFlowRate('kg/sec'))]
        check(i,str(s.getName())+' physical domain',all(math.isfinite(x) for x in vals) and vals[0]>0 and vals[1]>0 and vals[2]>=0,vals,'finite P>0 bara,T>0 K,mass>=0kg/s')
    if kind=='Compressor':
        f=ins[0].getFluid()
        check(i,name+' gas-only compression',int(f.getNumberOfPhases())==1 and str(f.getPhase(0).getType()).upper()=='GAS' and power>0 and outs[0].getPressure()>ins[0].getPressure(),
              {'phases':int(f.getNumberOfPhases()),'phase':str(f.getPhase(0).getType()),'power_W':power},'one gas phase,positive pressure rise/work')
def process_checks(i,p):
    for unit in p.getUnitOperations():balance(i,unit)
def fresh_waterfall(template):
    j=jpype.JPackage('neqsim');f=j.thermo.system.SystemSrkCPAstatoil(343.15,65.)
    for name,z in [('methane',.70),('ethane',.08),('propane',.05),('n-butane',.03),('n-heptane',.08),('water',.06)]:f.addComponent(name,z)
    f.setMixingRule(10);f.setMultiPhaseCheck(True)
    feed=j.process.equipment.stream.Stream('feed',f);feed.setFlowRate(200000.,'kg/hr')
    sep=j.process.equipment.separator.ThreePhaseSeparator('HP Sep',feed)
    comp=j.process.equipment.compressor.Compressor('Export Comp',sep.getGasOutStream());comp.setOutletPressure(150.)
    comp.setUsePolytropicCalc(True);comp.setPolytropicEfficiency(.78)
    p=j.process.processmodel.ProcessSystem();p.add(feed);p.add(sep);p.add(comp);p.run();sep.autoSize(1.2);comp.autoSize(1.2)
    for name in ['HP Sep','Export Comp']:
        old=template.getUnit(name).getCapacityConstraints();new=p.getUnit(name).getCapacityConstraints()
        for key in old.keySet():new.get(key).setEnabled(old.get(key).isEnabled())
    return p,feed
def screen(p):
    values=[]
    for name in ['HP Sep','Export Comp']:
        u=p.getUnit(name)
        if any(c.isEnabled() for c in u.getCapacityConstraints().values()):values.append(float(u.getMaxUtilization()))
        elif name=='HP Sep':values.append(float(u.getLiquidLevel()))
        else:values.append(float(u.getCapacityDuty())/float(u.getCapacityMax()))
    return max(values)
def verify_selected(i,ns):
    selected=float(ns['feed'].getFlowRate('kg/hr'));original=ns['process']
    p,feed=fresh_waterfall(original);feed.setFlowRate(selected,'kg/hr');p.run();process_checks(i,p)
    ratio=screen(p)
    limit=float(ns['config'].getDefaultUtilizationLimit())
    details={'selected_kg_hr':selected,'fresh_maximum':ratio,'step':ns.get('step'),
      'constraints':{name:{str(e.getKey()):{'enabled':bool(e.getValue().isEnabled()),'design':float(e.getValue().getDesignValue()),'maximum':float(e.getValue().getMaxValue()),'utilization':float(e.getValue().getUtilization())} for e in p.getUnit(name).getCapacityConstraints().entrySet()} for name in ['HP Sep','Export Comp']}}
    check(i,'fresh selected-point feasibility',ratio<=limit+1e-6,details,f'maximum active utilization <={limit}')
    if os.environ.get('CH21_CHECK_MODE')=='probe':return
    feasible=[]
    for rate in np.linspace(50000,300000,51):
        feed.setFlowRate(float(rate),'kg/hr');p.run();process_checks(i,p)
        if screen(p)<=limit:feasible.append(float(rate))
    assert feasible
    best=max(feasible)
    check(i,'independent 51-point grid bracket',abs(selected-best)<=5000.01,
          {'selected_kg_hr':selected,'grid_best_kg_hr':best},'agreement within5000kg/hr grid interval')
def before_fence(n,i,ns,code):code_lines[i]=code.splitlines();previous.clear()
def on_trace(n,i,frame,event,arg):
    if event!='line':return
    prior=previous.get(id(frame));previous[id(frame)]=frame.f_lineno
    if prior and prior<=len(code_lines.get(i,[])) and code_lines[i][prior-1].strip()=='process.run()':
        ns=frame.f_locals
        if 'process' in ns:
            process_checks(i,ns['process'])
            if i==25 and 'optimum' in ns:verify_selected(i,ns)
def after_fence(n,i,ns,code):
    assert os.environ.get('CH21_CHECK_MODE')!='probe','Diagnostic probe cannot qualify a release'
    if i in (25,28,29,30,31,32,39):process_checks(i,ns['process'])
    if i==25:
        gains=sum(b['gain'] for b in ns['bottlenecks']);total=ns['current_rate']-ns['base_rate']
        check(i,'waterfall arithmetic',abs(gains-total)<1e-7 and all(b['gain']>=-1e-7 for b in ns['bottlenecks']),[gains,total],'incremental gains reconcile with final minus baseline')
    if i in (29,31,32,39):
        vals={str(e.getKey()):float(e.getValue()) for e in ns['process'].getCapacityUtilizationSummary().entrySet()}
        check(i,'utilization table domain',vals and all(math.isfinite(v) and v>=0 for v in vals.values()),vals,'finite,nonnegative; values>1 retained as overloads')
    if i==30:check(i,'mask preserves imposed flow',abs(ns['delta_q'])<=1e-9,ns['delta_q'],'zero kg/hr without changing feed')
    if i==32:
        check(i,'sweep coverage',len(ns['bottleneck_utils'])==20 and all(math.isfinite(v) and v>=0 for v in ns['bottleneck_utils']),ns['bottleneck_utils'],'20 nonnegative finite sampled maxima')
    if i==36:
        r=ns['discount_rate'];N=ns['remaining_years'];factor=(1-(1+r)**(-N))/r
        check(i,'annuity and profitability-index identity',abs(ns['pv_factor']-factor)<1e-12 and abs(ns['pi']-(1+ns['npv']/ns['opt']['capex_mnok']))<1e-10,
              {'annuity_factor':factor,'last_PI':ns['pi']},'PI=PVbenefits/CAPEX=1+NPV/CAPEX; assumed constant annual volume and no incrementalOPEX')
    if i==39:
        r=ns['report'];actual=float(ns['process'].getUnit('Feed').getFlowRate('kg/hr'))
        check(i,'reported flow matches solved stream',abs(r['total_production_kg_hr']-actual)<1e-8,r['total_production_kg_hr'],actual)
    return checks[i]
def partial_checks(n,i):return checks[i]
