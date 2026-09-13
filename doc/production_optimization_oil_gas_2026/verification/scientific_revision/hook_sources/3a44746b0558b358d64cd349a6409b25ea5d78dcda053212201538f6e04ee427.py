"""Physical/solution checks on the exact published Chapter 28 Python fences.

Native hydraulics replay is a solution check, not an independent field benchmark.
Analytical component reconstruction and network constitutive equations are separate.
"""
from pathlib import Path
import json, math, sys
import numpy as np
from scipy.optimize import brentq

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from export_capacity_solution_hooks import result, state, balance, pipeline_check
TARGET_FENCES={28:[13,16,17,18,20,21,22,23]}
ROWS={};FAILURES={};LINES={};SEEN={}

def fluid_check(f,label):
    f.initProperties()
    z=np.array([float(f.getComponent(i).getz()) for i in range(f.getNumberOfComponents())])
    assert np.isfinite(z).all() and min(z)>=0 and abs(sum(z)-1)<1e-9,(label,z)
    T=float(f.getTemperature());P=float(f.getPressure());rho=float(f.getDensity('kg/m3'))
    assert all(math.isfinite(v) and v>0 for v in (T,P,rho)),(label,T,P,rho)
    mol=float(f.getTotalNumberOfMoles())
    inventory=np.zeros(len(z));phases=[]
    for k in range(f.getNumberOfPhases()):
        p=f.getPhase(k);x=np.array([float(p.getComponent(i).getx()) for i in range(len(z))]);beta=float(f.getBeta(k))
        assert min(x)>=-1e-14 and abs(sum(x)-1)<1e-8 and 0<=beta<=1
        inventory+=beta*x
        phases.append({'type':str(p.getPhaseTypeName()),'mole_fraction':beta})
    residual=float(max(abs(inventory-z)))
    assert residual<1e-8,(label,residual)
    return result(label,{'T_K':T,'P_bara':P,'rho_kg_m3':rho,'mol_s':mol,'phases':phases,'component_flash_balance_absolute':residual},1e-8)

def recombination_check(f,fmi,gor,wc,rate,label):
    import jpype
    rows=[fluid_check(f,label+' operating flash')]
    # Independently sum the separated-reference molar inventories from specified
    # standard volumetric blending rates. A later equilibrium flash can repartition.
    source=[fmi.getGasPhase(),fmi.getOilPhase(),fmi.getWaterPhase()]
    rates=[rate*(1-wc)*gor/3600,rate*(1-wc)/3600,rate*wc/3600]
    expected={}
    for phase,q in zip(source,rates):
        assert phase is not None
        volume=float(phase.getVolume('m3'));assert volume>0
        for i in range(phase.getNumberOfComponents()):
            c=phase.getComponent(i);name=str(c.getComponentName())
            expected[name]=expected.get(name,0)+q/volume*float(c.getNumberOfmoles())
    total=sum(expected.values())
    error=max(abs(float(f.getComponent(name).getz())-value/total) for name,value in expected.items())
    assert error<1e-8,(label,'recombined inventory',error)
    std=f.clone();std.setTemperature(288.15);std.setPressure(1.01325)
    jpype.JClass('neqsim.thermodynamicoperations.ThermodynamicOperations')(std).TPflash();std.initProperties()
    assert all(std.hasPhaseType(p) for p in ('gas','oil','aqueous'))
    volumes={p:float(std.getPhase(p).getVolume('m3'))*3600 for p in ('gas','oil','aqueous')}
    liquid=volumes['oil']+volumes['aqueous'];actual_gor=volumes['gas']/volumes['oil'];actual_wc=volumes['aqueous']/liquid
    rate_error=abs(liquid-rate)/rate
    assert rate_error<1e-6,(label,'standard liquid normalization',liquid,rate)
    rows.append(result(label+' independent composition and standard-volume contract',{'requested_GOR_Sm3_Sm3':gor,'requested_watercut':wc,'standard_liquid_rate_Sm3_hr':liquid,'requested_liquid_rate_Sm3_hr':rate,'actual_equilibrium_GOR':actual_gor,'actual_equilibrium_watercut':actual_wc,'mass_rate_kg_hr':float(f.getFlowRate('kg/hr')),'relative_liquid_error':rate_error,'max_composition_error':error}, {'standard_liquid_relative':1e-6,'composition_absolute':1e-8},'GOR and water cut prescribe reference-phase mixing; report equilibrium ratios separately instead of assuming exact ratios.'))
    return rows

def replay(factory,gen,rate,gor,wc,pin,T=358.15):
    process=factory();feed=process.getUnit('Feed')
    fluid=gen.generateFluid(float(gor),float(wc),float(rate),T,float(pin))
    feed.setFluid(fluid);feed.setFlowRate(float(rate),'kg/hr');feed.setTemperature(T,'K');feed.setPressure(float(pin),'bara');process.run()
    outlet=process.getUnit('Export')
    if outlet is None:outlet=process.getUnit('Export Outlet')
    return process,float(outlet.getPressure('bara'))

def table_check(table,factory,gen,label,tolerance=0.5):
    rows=[];points=[]
    axes=[list(table.getFlowRates()),list(table.getOutletPressures()),list(table.getWaterCuts()),list(table.getGORs())]
    assert [len(a) for a in axes]==[3,2,1,2] and table.getTotalPoints()==12
    assert str(table.getFlowRateUnit())=='kg/hr'
    for ri,rate in enumerate(axes[0]):
      for pi,target in enumerate(axes[1]):
       for wi,wc in enumerate(axes[2]):
        for gi,gor in enumerate(axes[3]):
          pin=float(table.getBHP(ri,pi,wi,gi));accepted=bool(table.isFeasible(ri,pi,wi,gi))
          record={'indices':[ri,pi,wi,gi],'rate_kg_hr':float(rate),'outlet_target_bara':float(target),'watercut_input':float(wc),'GOR_input':float(gor),'required_inlet_bara':pin if math.isfinite(pin) else None,'accepted':accepted}
          if accepted:
            assert 20<=pin<=350 and math.isfinite(pin)
            process,pout=replay(factory,gen,rate,gor,wc,pin)
            assert math.isfinite(pout) and pout>=target-1e-6 and pout<pin,(label,record,pout)
            rows.append(pipeline_check(process.getUnit('Tubing'),label+' tubing '+str(record['indices'])))
            rows.append(pipeline_check(process.getUnit('Flowline'),label+' flowline '+str(record['indices'])))
            assert abs(float(process.getUnit('Feed').getFlowRate('kg/hr'))-rate)<1e-6
            lower=max(20,pin-tolerance-1e-8)
            _,below=replay(factory,gen,rate,gor,wc,lower)
            assert math.isfinite(below) and below<target+1e-6,(label,'lower pressure does not bracket target',record,below)
            record.update(replayed_outlet_bara=pout,lower_inlet_bara=lower,lower_outlet_bara=below)
          else:
            assert not math.isfinite(pin),'Invalid grid result must remain unavailable'
            try:_,pmax=replay(factory,gen,rate,gor,wc,350)
            except Exception as ex:pmax=None;record['maximum_pressure_error']=str(ex)
            assert pmax is None or not math.isfinite(pmax) or pmax<target
            record['maximum_pressure_outlet_bara']=pmax
          points.append(record)
    assert sum(p['accepted'] for p in points)==table.getFeasibleCount()
    rows.append(result(label+' all 12 pressure roots and explicit unavailable-domain cells',points,{'pressure_search_width_bar':tolerance,'target_numerical_bar':1e-6},'Fresh NeqSim replay checks the reported root and lower bracket; mass/components and pressure domains checked for both physical pipe segments. Correlation validity against field data remains uncalibrated.'))
    return rows

def before_fence(ch,i,ns,code):
    ROWS[i]=[];FAILURES[i]=[];LINES[i]=code.splitlines();SEEN[i]=set()

def on_trace(ch,i,frame,event,arg):
    if i!=21 or event!='line' or frame.f_code.co_filename.split(':')[-1]!='fence21':return
    if 'densities.append' not in LINES[i][frame.f_lineno-1]:return
    ns=frame.f_locals;gor=float(ns['gor'])
    if gor in SEEN[i]:return
    try:ROWS[i]+=recombination_check(ns['fl'],ns['fmi'],gor,.1,10000,f'Density sample GOR {gor}');SEEN[i].add(gor)
    except Exception as ex:FAILURES[i].append(str(ex));raise

def after_fence(ch,i,ns,code):
    rows=ROWS[i];assert not FAILURES[i],FAILURES[i]
    if i==13:
        ref=ns['ref_fluid'].clone()
        ns['jneqsim'].thermodynamicoperations.ThermodynamicOperations(ref).TPflash()
        rows.append(fluid_check(ref,'Configured reference after explicit verification TP flash'))
        rows+=table_check(ns['table'],ns['create_process'],ns['flash_gen'],'Base 12 km',1.)
        rows+=recombination_check(ns['flash_gen'].generateFluid(1000.,.05,10000.,358.15,50.),ns['fmi'],1000.,.05,10000.,'Base mixture')
        ns['_base_table_flash_generator']=ns['flash_gen']
    elif i in (16,17,18):
        k=i-15
        rows+=table_check(ns[f'table_concept{k}'],ns[f'concept_{k}_factory'],ns['_base_table_flash_generator'],f'Route {k}')
    elif i==20:
        model=ns['model'];r=ns['result'];sol=model.solve()
        q=float(r.getFieldRate());rates={str(k):float(v) for k,v in r.getWellRates().items()};chokes={str(k):float(v) for k,v in r.getChokeSettings().items()}
        assert sol.isConverged() and r.isFeasible() and 0<q<=40000*(1+1e-4)
        assert all(0<=c<=1 for c in chokes.values()) and min(rates.values())>=0
        assert abs(sum(rates.values())-q)<1e-8 and abs(float(sol.getFieldRate())-q)<1e-6
        assert abs(float(r.getRevenue())-3*q)<1e-8 and abs(float(r.getObjectiveValue())-3*q)<1e-8
        assert abs(float(sol.getEnergyKWhPerDay())-.12*q)<1e-8 and abs(float(sol.getEmissionsKgPerDay())-.02*q)<1e-8
        gap=(40000-q)/40000
        assert 0<=gap<.005,(q,gap)
        rows.append(result('Converged reduced-network allocation and independent revenue upper bound',{'field_rate_Sm3_day':q,'well_rates':rates,'chokes':chokes,'revenue_currency_day':float(r.getRevenue()),'upper_bound_currency_day':120000,'relative_upper_bound_gap':gap,'energy_kWh_day':float(sol.getEnergyKWhPerDay()),'emissions_kg_day':float(sol.getEmissionsKgPerDay()),'nodes':{str(k):float(v) for k,v in sol.getNodePressures().items()}},{'rate_accounting_absolute':1e-8,'upper_bound_gap':.005},'Reduced Vogel/network model and assumed constant intensities; objective bound follows rate<=40000 and common positive price, not field-calibrated optimality.'))
        nodes={str(k):float(v) for k,v in sol.getNodePressures().items()}
        analytical=[]
        for name,aof,pres in [('Well-A',2e6,250.),('Well-B',1.5e6,220.)]:
            c=chokes[name];a=np.linspace(0,1,11)
            def deliverability(p):return float(np.interp(p,a*pres,aof*(1-.2*a-.8*a*a)))
            def residual(rate):return rate-c*deliverability(90+1e-10*rate*rate)
            exact=brentq(residual,0,aof,xtol=1e-8)
            published=rates[name];pw=nodes[name+'_WH']
            branch_residual=abs(published-c*deliverability(pw));pressure_error=abs(pw-90-1e-10*published**2)
            assert 90<=pw<pres and branch_residual<10 and pressure_error<1e-8 and abs(published-exact)<10
            analytical.append({'well':name,'native_rate_Sm3_day':published,'independent_scalar_root_Sm3_day':exact,'absolute_rate_difference_Sm3_day':abs(published-exact),'wellhead_bara':pw,'node_continuity_residual_Sm3_day':branch_residual,'flowline_equation_residual_bar':pressure_error})
        a=np.linspace(0,1,11);witness_p=90+1e-10*40000**2
        witness_choke=40000/np.interp(witness_p,a*220,1.5e6*(1-.2*a-.8*a*a))
        assert 0<witness_choke<1 and 90<witness_p<220
        rows.append(result('Independent piecewise Vogel and quadratic-line solution plus feasible capacity witness',{'native_candidate_wells':analytical,'capacity_witness':{'Well-A_choke':0.,'Well-B_choke':float(witness_choke),'Well-B_rate_Sm3_day':40000.,'Well-B_wellhead_bara':witness_p,'revenue_currency_day':120000.}},{'network_rate_absolute_Sm3_day':10.,'flowline_equation_bar':1e-8,'independent_root_xtol_Sm3_day':1e-8},'Independent Python equations reproduce the declared 11-point Vogel interpolation and default line coefficient 1e-10 bar/(Sm3/day)^2. The 10 Sm3/day rate tolerance is the native documented network stopping tolerance; the exact capacity witness establishes a reachable upper bound for this reduced model.'))
    elif i==21:
        assert len(SEEN[i])==5
        assert np.all(np.diff(ns['densities'])<0)
        rows.append(result('Five actual density samples, finite and decreasing for this fixed composition family',{'GOR_input':ns['gors'],'density_kg_m3':[float(v) for v in ns['densities']]},scope='Thermodynamic bulk density, not in-situ slip/holdup-weighted pipe density.'))
    elif i in (22,23):
        table=ns['table']
        expected=np.array([[float(table.getBHP(a,b,0,1)) for b in range(2)] for a in range(3)])
        if i==22:assert np.allclose(ns['bhp_data'],expected,equal_nan=True)
        rows.append(result('Plot arrays retain exact previously checked table values',{'flow_kg_hr':list(table.getFlowRates()),'outlet_bara':list(table.getOutletPressures()),'GOR_1000_inlet_bara':expected.tolist(),'feasible_points':int(table.getFeasibleCount())},0.,'Explicit actual source table, no extrapolated or fabricated unavailable cells.'))
    return rows
