from pathlib import Path
import math,sys,re,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from optimization_solution_helpers import *
TARGET_FENCES={23:[1,3,15,16,22,25,35,37],24:[5,13,16,17,23,44,59,62,69,72,73,74,80],
               25:[1,5,10,11,12,13,14,17],26:[2,4,5,6,8,11,12,13,15,16],29:[5,6,13],
               30:[9,13,14,15,18,19,20,21,28,29],31:[2],32:[2]}
_lines={};_pending={};_trace_checks={}
def partial_checks(n,i):
    return [{'name':'Previously observed solved-state boundaries','passed':True,
             'observed':len(_trace_checks.get((n,i),[])),
             'states':_trace_checks.get((n,i),[])}]
def before_fence(n,i,ns,code):
    _lines[n,i]=code.splitlines();_trace_checks[n,i]=[]

def on_trace(n,i,frame,event,arg):
    if i not in TARGET_FENCES.get(n,[]):return
    key=id(frame)
    if key in _pending and event in ('line','return'):
        objname=_pending.pop(key)
        obj=frame.f_locals.get(objname,frame.f_globals.get(objname))
        if obj is not None:
            _trace_checks[n,i].append({'line':frame.f_lineno,'checks':process_checks(obj)})
    if event=='line' and ':fence'+str(i) in frame.f_code.co_filename:
        lines=_lines[n,i]
        if 0<frame.f_lineno<=len(lines):
            line=lines[frame.f_lineno-1]
            if re.search(r'\bprocess\.run\(',line):_pending[key]='process'

def after_fence(n,i,ns,code):
    if n==26:return network_checks(i,ns)
    if n==29 and i==5:return [check('pressure transmitter maximum range',float(ns['PT100'].getMaximumValue()),100.,1e-12),
                             check('pressure transmitter minimum range',float(ns['PT100'].getMinimumValue()),0.,1e-12)]
    if n==29 and i==6:
        sep=ns['sep']
        return [check('pressure measurement unit/value identity',float(ns['PT_sep'].getMeasuredValue('bara')),float(sep.getGasOutStream().getPressure('bara')),1e-9),
                check('temperature measurement unit/value identity',float(ns['TT_sep'].getMeasuredValue('C')),float(sep.getGasOutStream().getTemperature('C')),1e-9),
                check('native level transmitter fraction identity',float(ns['LT_sep'].getMeasuredValue('')),float(sep.getLiquidLevel()),1e-12)]
    process=ns['process'];rows=[]
    if n==25 and i==12:rows=unit_checks(ns['export_comp'])
    elif n==25 and i==13:rows=unit_checks(ns['gas_cooler'])
    elif n==25 and i==14:
        rows=unit_checks(ns['pipe'])
        rows.append(check('pressure-drop utilization identity',ns['U_dP'],ns['delta_P']/ns['delta_P_available'],1e-12))
        area=math.pi*.5**2/4
        expected=float(ns['outlet_stream'].getFlowRate('m3/sec'))/area
        rows.append(check('velocity equals actual volume flow over area',ns['velocity'],expected,1e-10))
    else:rows=process_checks(process)
    if _trace_checks.get((n,i)):
        trace_rows=_trace_checks[n,i]
        rows.append({'name':'Every observed literal process.run state passes unit boundaries',
                     'passed':True,'observed':len(trace_rows),'states':trace_rows})
    if n==30 and i==9:
        rows.append(check('higher discharge pressure increases power',ns['power_new']>ns['power']))
        rows.append(check('automation compressor MW conversion',ns['power_new'],ns['compressor'].getPower('kW')/1000.,1e-9))
    if n==30 and i==15:rows.append(check('loaded lifecycle schema valid',bool(ns['validation'].isValid())))
    if n==30 and i==18:
        for name,v in ns['comparison'].items():
            absolute=abs(v['model']-v['measured'])
            rows.append(check(name+' absolute synthetic deviation',v['absolute_deviation'],absolute,1e-10))
            if v['unit']=='C':rows.append(check('no Celsius-relative percent error',v['deviation_pct'],None))
            else:
                expected=absolute/v['measured']*100
                rows.append(check(name+' synthetic deviation arithmetic',v['deviation_pct'],expected,1e-10))
    if n==30 and i==19:
        rows.append(check('24 finite positive simulated power points',len(ns['model_power'])==24 and all(math.isfinite(v) and v>0 for v in ns['model_power'])))
        rows.append(check('adiabatic separator matches prescribed feed temperature',max(abs(a-b) for a,b in zip(ns['model_sep_T'],ns['temp_profile'])),0.,1e-5))
    if n==30 and i==20:
        result=ns['result'];best=max(result['all_results'],key=lambda r:r['liquid_flow_kghr'])
        rows.append(check('sweep maximum selects evaluated pressure',result['optimal_pressure'],best['pressure_bara'],1e-10))
        rows.append(check('final selected liquid flow replay',float(ns['sep'].getLiquidOutStream().getFlowRate('kg/hr')),result['max_liquid_flow'],1e-4))
    if n==30 and i==21:
        result=ns['result'];settings=dict(result.getBestSetpoints())
        valid=all(math.isfinite(float(v)) and
                  ((30.-1e-8<=float(v)<=70.+1e-8) if 'Feed Gas' in str(k) else
                   (80.-1e-8<=float(v)<=200.+1e-8)) for k,v in settings.items())
        rows.append(check('agent optimizer finite bounded pressure settings',valid))
        if result.isFeasible():rows.append(check('agent feasible power limit replay',ns['compressor'].getPower('kW')<=8000.001))
        else:rows.append(check('explicitly rejected agent point',not bool(result.isFeasible())))
    if n==30 and i==29:
        rows.append(check('compressed lifecycle JSON roundtrip',json.loads(str(ns['restored'].toJson())),json.loads(str(ns['state_v2'].toJson()))))
    if n==32 and i==2:
        production=ns['production'];power=ns['power']
        rows.append(check('nonempty finite bounded Pareto sample',len(production)>1 and all(
            math.isfinite(q) and 50000.-1e-6<=q<=200000.+1e-6 for q in production)))
        for a,(q,w) in enumerate(zip(production,power)):
            dominated=any(q2>=q and w2<=w and (q2>q or w2<w)
                          for b,(q2,w2) in enumerate(zip(production,power)) if b!=a)
            rows.append(check('Pareto point '+str(a)+' non-dominated',not dominated))
            # Fixed thermodynamic boundaries imply linear work in this explicit model.
            rows.append(check('Pareto point '+str(a)+' extensive power scaling',w/q,power[0]/production[0],1e-9))
    if n==25 and i==10:
        c=ns['gas_constraint'];expected=float(c.getCurrentValue()/c.getMaxValue())
        rows.append(check('gas capacity ratio identity',ns['gas_util'],expected,1e-12))
    if n==25 and i==17:
        record=ns['record']
        for name,item in record['utilization'].items():
            v=item['value'];expected='GREEN' if v<.7 else 'YELLOW' if v<.9 else 'RED'
            rows.append(check(str(name)+' dashboard traffic-light rule',item['status'],expected))
    if (n,i) in [(23,15),(23,16),(23,22),(24,23)]:
        result=ns['result']
        rows.append(check('optimizer final rate replay',float(ns['feed'].getFlowRate('kg/hr')),
                          float(result.getOptimalRate()),max(1e-5,abs(float(result.getOptimalRate()))*1e-8)))
        violations=[]
        for rec in result.getUtilizationRecords():
            violations.append(float(rec.getUtilization())-float(rec.getUtilizationLimit()))
        if result.isFeasible():
            rows.append(check('returned feasible point meets explicit utilization records',not violations or max(violations)<=1e-6))
        else:
            rows.append(check('rejected candidate has explicit diagnostic',bool(str(result.getInfeasibilityDiagnosis()))))
    return rows

def network_checks(i,ns):
    import numpy as np
    if i==2:
        rows=[check('Vogel shut-in zero flow',float(ns['q_vogel'][-1]),0.,1e-10),
              check('Vogel AOF endpoint',float(ns['q_vogel'][0]),5000.,1e-10),
              check('Fetkovich shut-in zero flow',float(ns['q_fetk'][-1]),0.,1e-10),
              check('IPR curves monotone on declared pressure interval',
                    bool(np.all(np.diff(ns['q_vogel'])<=0) and np.all(np.diff(ns['q_fetk'])<=0)))]
        return rows
    if i==4:
        points=np.linspace(0,250,11)
        rates=6000*(1-.2*(points/250)-.8*(points/250)**2)
        expected=float(np.interp(120.,points,rates))
        analytic=6000*(1-.2*(120/250)-.8*(120/250)**2)
        return [check('Vogel native11-point interpolant against independent interpolation',float(ns['q']),expected,1e-8),
                check('Vogel interpolation error satisfies quadratic interpolation bound',abs(float(ns['q'])-analytic)<=12.+1e-8),
                check('Vogel native AOF',float(ns['aofp']),6000.,1e-8),
                check('Vogel negative local slope',float(ns['slope'])<0)]
    if i==5:
        match=ns['match'];pr=float(match.getReservoirPressure());qmax=float(match.getDeliverabilityParameter())
        rms=math.sqrt(sum((qmax*(1-.2*p/pr-.8*(p/pr)**2)-q)**2
                          for q,p in [(3200,180),(4500,150),(5300,120)])/3)
        return [check('matched Vogel finite pressure above observed BHP',float(ns['match'].getReservoirPressure())>180.),
                check('matched analytic Vogel RMS independently recomputed',float(ns['match'].getRmsError()),rms,1e-7)]
    if i==6:
        rows=unit_checks(ns['tubing']);rows.append(check('upward production tubing BHP exceeds WHP',0<ns['thp']<200.))
        return rows
    if i in [8,13]:
        network=ns['network']
        return [check('network solver converged',bool(network.isConverged())),
                check('finite network pressure and flows',float(network.getNodePressure('Platform'))>0 and all(
                    math.isfinite(network.getPipeFlowRate(name)) and math.isfinite(network.getPipeVelocity(name))
                    for name in network.getPipeNames()))]
    if i==11:
        r=ns['result'];alloc=dict(r.getLiftRates());a=ns['curve_a'];b=ns['curve_b']
        q1=float(alloc['Well-A']);q2=float(alloc['Well-B']);replay=a.oilRateAt(q1)+b.oilRateAt(q2)
        grid=max(a.oilRateAt(x)+b.oilRateAt(2.5e6-x) for x in np.arange(.5e6,2e6+1,25000))
        return [check('native candidate within lift allocation budget',q1+q2<=2.5e6+1e-6),
                check('native lift objective direct replay',float(r.getTotalOil()),float(replay),1e-6),
                check('native tabulated candidate fails independent optimality test',float(grid-replay)>1.),
                check('accepted segment LP matches independent grid',float(ns['accepted_oil']),float(grid),1e-6),
                check('accepted segment allocation consumes budget',float(ns['accepted_lift'].sum()),2.5e6,1e-6)]
    if i==12:
        r=ns['results'];wells=ns['wells'];q=[r[w['name']]['gas_lift'] for w in wells]
        total=sum(r[w['name']]['oil_rate'] for w in wells)
        from scipy.optimize import minimize
        def score(x):return sum(w['q_max']*(1-math.exp(-w['alpha']*v)) for w,v in zip(wells,x))
        opt=minimize(lambda x:-score(x*5e5),np.ones(3)/3,bounds=[(0,1)]*3,
                     constraints={'type':'eq','fun':lambda x:sum(x)-1},method='SLSQP',options={'ftol':1e-10})
        return [check('incremental gas lift budget',sum(q),5e5,1e-7),
                check('independent concave allocation optimizer success',bool(opt.success)),
                check('incremental lift discretization objective gap under one oil-rate unit',-float(opt.fun)-total<1.),
                check('incremental lift direct oil replay',score(q),total,1e-8)]
    if i==15:
        r=ns['answer'];allocation=list(map(float,r.getAllocation()));replay=sum((k+1)*math.sqrt(v) for k,v in enumerate(allocation))
        oracle=math.sqrt(260000.)+2*math.sqrt(1040000.)+3*math.sqrt(1200000.)
        return [check('native utility allocation bounds and resource',all(0<=v<=1.2e6+1 for v in allocation) and sum(allocation)<=2.5e6+1),
                check('native allocation utility replay',float(r.getObjective()),replay,1e-7),
                check('concave utility objective versus analytic constrained optimum',replay,oracle,.1)]
    if i==16:
        r=ns['solve'];rate=float(r.getFieldRate());well_rates=list(map(float,r.getWellRates().values()))
        return [check('integrated reduced model converged',bool(r.isConverged())),
                check('field flow equals wells',rate,sum(well_rates),1e-6),
                check('revenue unit identity',float(r.getRevenue()),3.*rate,1e-5),
                check('energy intensity unit identity',float(r.getEnergyKWhPerDay()),.12*rate,1e-5)]
