"""Selected independent reference comparisons and analytical-limit benchmarks."""
import os
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BOOK=ROOT.parents[1]
sys.path.insert(0,str(BOOK/'.build/python_packages'))
SOURCE=Path(os.environ['NEQSIM_PROJECT_ROOT'])
sys.path.insert(0,str(SOURCE/'devtools'))
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=SOURCE,recompile=False,verbose=False)
import jpype
import json
import hashlib
import math
import traceback
import subprocess
from datetime import datetime, timezone
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
j=jpype.JPackage('neqsim')
design=json.loads((ROOT/'benchmark_design.json').read_text())
expected=json.loads((ROOT/'reference_expected.json').read_text())
results=[]
failures=[]
figdir=ROOT/'figures';figdir.mkdir(exist_ok=True)

def record(name,actual,reference,tolerance,unit,kind,source,case=None,relative=False):
    error=abs(float(actual)-float(reference))
    bound=tolerance*abs(reference) if relative else tolerance
    item={'name':name,'actual':float(actual),'expected':float(reference),'absolute_error':error,
          'relative_error':error/abs(reference) if reference else None,'acceptance_bound_absolute':bound,
          'passed':bool(math.isfinite(actual) and error<=bound),'unit':unit,'evidence_type':kind,
          'reference':source,'case':case or {}}
    results.append(item)
    if not item['passed']: failures.append(item)
    return item

def fluid(T,P,composition=None,eos='SRK'):
    f=(j.thermo.system.SystemSrkEos if eos=='SRK' else j.thermo.system.SystemPrEos)(float(T),float(P))
    for name,z in (composition or [('methane',1)]):f.addComponent(name,float(z))
    f.setMixingRule('classic')
    j.thermodynamicoperations.ThermodynamicOperations(f).TPflash();f.initProperties()
    return f

def stream(name,f,rate=1000):
    s=j.process.equipment.stream.Stream(name,f);s.setFlowRate(float(rate),'kg/hr');s.run();return s

def totals(streams):
    mass=0.;h=0.;components={}
    for s in streams:
        f=s.getFluid();f.initProperties()
        m=float(s.getFlowRate('kg/sec'));mass+=m;h+=m*float(f.getEnthalpy('J/kg'))
        for i,z in enumerate(f.getMolarComposition()):
            key=str(f.getComponent(i).getComponentName())
            components[key]=components.get(key,0)+m/float(f.getMolarMass())*float(z)
    return mass,h,components

def guarded(name,fn):
    try:fn()
    except Exception as error:
        failures.append({'name':name,'passed':False,'exception':str(error),'traceback':traceback.format_exc()})
        print(name,'ERROR',error,flush=True)
    else:print(name,'done',flush=True)

def nist_pvt():
    for eos in ['SRK','PR']:
        for state in expected['states']:
            f=fluid(state['T_K'],state['P_bara'],eos=eos)
            record(eos+' methane density',float(f.getDensity('kg/m3')),state['density_kg_m3'],
                   design['nist_density_relative_tolerance'],'kg/m3','independent reference EOS',
                   state['source_file'],state,relative=True)
    fig,axes=plt.subplots(1,2,figsize=(10,4.2))
    for eos,marker in [('SRK','o'),('PR','s')]:
        rows=[r for r in results if r['name']==eos+' methane density']
        x=[r['expected'] for r in rows];y=[r['actual'] for r in rows]
        axes[0].plot(x,y,marker,ls='none',label=eos)
        axes[1].plot(range(1,len(rows)+1),[(r['actual']/r['expected']-1)*100 for r in rows],marker+'-',label=eos)
    limit=max(r['expected'] for r in results if r['unit']=='kg/m3')*1.05
    axes[0].plot([0,limit],[0,limit],color='.5',ls='--',label='Parity')
    axes[0].set(xlabel='NIST reference density (kg/m³)',ylabel='NeqSim density (kg/m³)',title='Methane: 300–400 K, 1–100 bara')
    axes[1].axhline(3,color='#b5443c',ls='--');axes[1].axhline(-3,color='#b5443c',ls='--')
    axes[1].set(xlabel='State index: 1/50/100 bara × 300/350/400 K',ylabel='Density deviation (%)',title='Declared teaching accuracy budget ±3%')
    for ax in axes:ax.grid(alpha=.2);ax.legend()
    fig.tight_layout();fig.savefig(figdir/'nist_methane_density_validation.png',dpi=220,bbox_inches='tight');plt.close(fig)

def dilute():
    R=8.31446261815324;M=.01604246
    for T in [300,350,400]:
        P=.001;f=fluid(T,P)
        record('dilute methane ideal-gas density',float(f.getDensity('kg/m3')),P*1e5*M/(R*T),
               design['dilute_gas_density_relative_tolerance'],'kg/m3','independent analytical limit',
               'pV=nRT; R=8.31446261815324 J/(mol K), methane M=0.01604246 kg/mol',{'T_K':T,'P_bara':P},True)

def rachford_rice():
    for K,z in [([2,.5],[.5,.5]),([4,.25],[.5,.5]),([3,.2],[.6,.4])]:
        d=np.asarray(K)-1;analytic=-(z[0]*d[0]+z[1]*d[1])/(d[0]*d[1])
        solver=j.thermodynamicoperations.flashops.RachfordRice()
        beta=float(solver.calcBeta(K,z))
        record('binary Rachford-Rice vapour fraction',beta,analytic,design['rachford_rice_beta_absolute_tolerance'],
               'mol/mol','independent analytical solution','Cleared-denominator binary Rachford-Rice equation',{'K':K,'z':z})

def flash_balances():
    comp=[('methane',.5),('ethane',.2),('n-butane',.3)]
    for T in [270,300,330]:
        for P in [10,30,60]:
            f=fluid(T,P,comp);z=np.asarray(f.getMolarComposition());recon=np.zeros(len(z));xs=[];phis=[]
            for i in range(f.getNumberOfPhases()):
                phase=f.getPhase(i);beta=float(f.getBeta(i));x=np.array([phase.getComponent(k).getx() for k in range(len(z))])
                recon+=beta*x;xs.append(x);phis.append(np.array([phase.getComponent(k).getFugacityCoefficient() for k in range(len(z))]))
                record('flash phase composition sums to unity',float(x.sum()),1,1e-7,'mol/mol','conservation and equilibrium verification','Phase composition normalization',{'T_K':T,'P_bara':P,'phase':i})
            record('flash component material reconstruction',float(np.max(np.abs(recon-z))),0,
                   design['flash_component_absolute_tolerance'],'mol/mol','conservation and equilibrium verification',
                   'z_i=sum(beta_alpha*x_i_alpha)',{'T_K':T,'P_bara':P,'phases':int(f.getNumberOfPhases())})
            if len(xs)>1:
                logratio=np.log((xs[0]*phis[0])/(xs[1]*phis[1]))
                record('flash phase fugacity equality',float(np.max(np.abs(logratio))),0,
                       design['flash_log_fugacity_ratio_absolute_tolerance'],'ln(f1/f2)','conservation and equilibrium verification',
                       'At TP equilibrium, component fugacities are equal across phases',{'T_K':T,'P_bara':P})

def valves():
    for pin,pout in [(100,50),(80,20),(60,5)]:
        feed=stream('valve feed',fluid(320,pin));v=j.process.equipment.valve.ThrottlingValve('isenthalpic valve',feed)
        v.setOutletPressure(float(pout));v.run();out=v.getOutletStream();out.getFluid().initProperties()
        record('adiabatic throttle specific enthalpy',float(out.getFluid().getEnthalpy('J/kg')),float(feed.getFluid().getEnthalpy('J/kg')),
               design['valve_specific_enthalpy_absolute_tolerance_J_kg'],'J/kg','conservation-law verification',
               'Steady adiabatic first law, no shaft work, negligible kinetic/potential change',{'Pin_bara':pin,'Pout_bara':pout})
        mi,hi,ci=totals([feed]);mo,ho,co=totals([out])
        record('throttle mass flow',mo,mi,1e-8,'kg/s','conservation-law verification','Steady material balance')

def compressor_limit():
    for ratio in [1.5,2,3]:
        T=300.;eta=.8;M=.039948;R=8.31446261815324;cp=2.5*R/M
        feed=stream('argon inlet',fluid(T,.001,[('argon',1)]))
        comp=j.process.equipment.compressor.Compressor('argon compressor',feed)
        comp.setUsePolytropicCalc(False);comp.setIsentropicEfficiency(eta);comp.setOutletPressure(.001*ratio);comp.run()
        actualT=float(comp.getOutletStream().getTemperature('K'))
        expectedT=T+T*(ratio**.4-1)/eta
        case={'T_in_K':T,'Pin_bara':.001,'pressure_ratio':ratio,'isentropic_efficiency':eta}
        record('ideal monatomic argon compressor outlet temperature',actualT,expectedT,
               design['ideal_argon_compressor_relative_tolerance'],'K','independent analytical limit',
               'NASA Glenn compressor equation; ideal monatomic cp=5R/(2M), gamma=5/3',case,True)
        expected_power=(1000/3600)*cp*(expectedT-T)/1000
        record('ideal monatomic argon compressor shaft power',float(comp.getPower('kW')),expected_power,
               design['ideal_argon_compressor_relative_tolerance'],'kW','independent analytical limit',
               'Wdot=mdot cp Tin [(pout/pin)^((gamma-1)/gamma)-1]/eta',case,True)
        _,hi,_=totals([feed]);_,ho,_=totals([comp.getOutletStream()])
        record('compressor first law',ho-hi,float(comp.getPower('kW'))*1000,.1,'W','conservation-law verification','Hout-Hin=Wshaft',case)

def hydraulics():
    for rise in [-100.,0.,100.]:
        feed=stream('low-flow liquid',fluid(298.15,50,[('n-heptane',1)]),1.)
        rho=float(feed.getFluid().getDensity('kg/m3'))
        pipe=j.process.equipment.pipeline.PipeBeggsAndBrills('hydrostatic limit',feed)
        pipe.setLength(100.);pipe.setDiameter(.2);pipe.setElevation(rise);pipe.setNumberOfIncrements(20);pipe.run()
        drop=50-float(pipe.getOutletStream().getPressure('bara'))
        reference=rho*9.80665*rise/1e5
        record('liquid low-flow hydrostatic limit',drop,reference,
               abs(reference)*design['hydrostatic_pressure_relative_tolerance']+1e-6,'bar','analytical momentum limit',
               'NASA hydrostatics: dp=-rho*g*dz; density is a specified model input, not independently validated',
               {'rise_m':rise,'rho_input_kg_m3':rho,'flow_kg_hr':1.,'length_m':100.,'diameter_m':.2})
    feed=stream('stagnant horizontal gas',fluid(300,60),0.)
    pipe=j.process.equipment.pipeline.PipeBeggsAndBrills('zero-flow horizontal',feed)
    pipe.setLength(1000.);pipe.setDiameter(.2);pipe.setElevation(0.);pipe.setMinimumFlow(1e-5);pipe.run()
    record('horizontal zero-flow pressure limit',float(pipe.getOutletStream().getPressure('bara')),60.,
           design['horizontal_zero_flow_absolute_pressure_tolerance_bar'],'bara','independent analytical limit',
           'Zero flow, zero elevation: no friction or hydrostatic pressure change; low-flow bypass explicitly enabled')

def separator():
    for T in [280,300,320]:
        feed=stream('separator feed',fluid(T,30,[('methane',.5),('ethane',.2),('n-butane',.3)]),50000)
        sep=j.process.equipment.separator.Separator('flash separator',feed);sep.run()
        mi,hi,ci=totals([feed]);mo,ho,co=totals(list(sep.getOutletStreams()))
        record('separator mass balance',mo,mi,1e-7,'kg/s','conservation-law verification','Steady material balance',{'T_K':T})
        err=max(abs(co.get(k,0)-ci.get(k,0)) for k in set(ci)|set(co))
        record('separator component balance',err,0,1e-5,'mol/s','conservation-law verification','Component molar-flow conservation',{'T_K':T})
        record('separator first law',ho-hi,0,.1,'W','conservation-law verification','Adiabatic flash separator, no shaft work',{'T_K':T})

def optimizer_search():
    def build():
        f=fluid(298.15,65,[('nitrogen',.02),('CO2',.03),('methane',.80),('ethane',.08),('propane',.04),('n-butane',.02),('n-hexane',.01)])
        feed=stream('Feed Gas',f,50000);sep=j.process.equipment.separator.Separator('HP Separator',feed)
        comp=j.process.equipment.compressor.Compressor('Export Compressor',sep.getGasOutStream());comp.setOutletPressure(150.)
        cool=j.process.equipment.heatexchanger.Cooler('Export Cooler',comp.getOutletStream());cool.setOutTemperature(308.15)
        process=j.process.processmodel.ProcessSystem()
        for unit in [feed,sep,comp,cool]:process.add(unit)
        process.run();return process,feed,comp
    process,feed,comp=build()
    optimizer=j.process.util.optimizer.FlowRateOptimizer(process,'Feed Gas','Export Cooler')
    optimizer.setAutoConfigureProcessCompressors(False);optimizer.setCheckCapacityConstraints(False)
    optimizer.setMinFlowRate(20000.);optimizer.setMaxFlowRate(200000.)
    optimizer.setMaxTotalPowerLimit(4750.);optimizer.setMaxEquipmentUtilizationLimit(1e6)
    optimum=optimizer.findMaximumFeasibleFlowRate(65.,'bara',1e6)
    qopt=float(optimum.getFlowRate())
    # Independent enumeration: fresh process, no optimizer constraint/objective helpers.
    p2,f2,c2=build();grid=np.arange(20000.,200001.,design['optimizer_grid_spacing_kg_hr']);powers=[]
    for q in grid:f2.setFlowRate(float(q),'kg/hr');p2.run();powers.append(float(c2.getPower('kW')))
    powers=np.asarray(powers);qgrid=float(grid[powers<=4750][-1]);nextq=qgrid+design['optimizer_grid_spacing_kg_hr']
    record('optimizer versus independent brute-force bracket',qopt,(qgrid+nextq)/2,
           design['optimizer_grid_spacing_kg_hr']/2+1.,'kg/hr','independent search algorithm verification',
           'Fresh-process direct enumeration at 1000 kg/hr intervals, independently evaluated 4750 kW limit',
           {'largest_grid_feasible_kg_hr':qgrid,'next_grid_infeasible_kg_hr':nextq})
    f2.setFlowRate(qopt,'kg/hr');p2.run();popt=float(c2.getPower('kW'))
    record('optimizer replay hits power boundary',popt,4750.,4750.*design['optimizer_relative_power_tolerance'],'kW',
           'constraint verification','Independent fresh-process replay, same EOS')
    proportional_rate=grid[0]*4750/powers[0]
    record('fixed-state throughput proportionality limit',qopt,float(proportional_rate),100.,'kg/hr',
           'analytical scaling verification','At fixed composition, suction state and pressure ratio, shaft power scales with mass rate')
    (ROOT/'optimizer_grid_actual.json').write_text(json.dumps({'flow_kg_hr':grid.tolist(),'power_kW':powers.tolist(),'optimizer_kg_hr':qopt},indent=2))

for name,fn in [('NIST methane',nist_pvt),('ideal dilute gas',dilute),('Rachford-Rice',rachford_rice),('flash equilibrium',flash_balances),
                ('throttling valves',valves),('ideal compressor',compressor_limit),('hydraulic limits',hydraulics),('separator',separator),('optimizer',optimizer_search)]:
    guarded(name,fn)
revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=SOURCE,text=True).strip()
report={'generated_at':datetime.now(timezone.utc).isoformat(),'source_revision':revision,'python':sys.executable,
        'status':'passed' if not failures else 'failed','comparisons':results,'failures':failures,
        'coverage':{'independent_property_data':'18 SRK/PR comparisons at nine archived NIST methane states',
                    'analytic_limits':'Ideal gas, binary Rachford-Rice, monatomic compressor, low-flow hydrostatics, zero-flow horizontal pipe',
                    'same_model_verification':'Flash fugacity and material closure, unit balances, optimizer independently enumerated search'},
        'limitations':['NIST values are independent reference-EOS calculations, not raw experimental measurements.',
                       'No external validation of multicomponent transport, TBP characterization, hydrate/MEG/TEG prediction, vendor maps, field hydraulics, dynamics or economics.',
                       'Passing a conservation identity does not establish independent predictive model accuracy.'],
        'hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'benchmark_design.json',ROOT/'reference_expected.json']}}
(ROOT/'benchmark_results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('BENCHMARKS',len(results),'comparisons;',len(failures),'failures',flush=True)
sys.exit(1 if failures else 0)
