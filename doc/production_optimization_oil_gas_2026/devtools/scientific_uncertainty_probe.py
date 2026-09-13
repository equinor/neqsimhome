"""Bounded isothermal NeqSim depletion used by the Chapter 27 uncertainty case."""
import json,os,sys
from pathlib import Path
BOOK=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BOOK/'.build/python_packages'))
sys.path.insert(0,str(Path(os.environ.get('NEQSIM_PROJECT_ROOT',r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim'))/'devtools'))
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=Path(os.environ.get('NEQSIM_PROJECT_ROOT',r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')),recompile=False,verbose=False)
import jpype,numpy as np
jneqsim=jpype.JPackage('neqsim')

def depletion_profile(gip_GSm3,capacity_GSm3_year,years=25):
    """Isothermal dry-gas material-balance tank; explicitly assumed withdrawal rule."""
    fluid=jneqsim.thermo.system.SystemSrkEos(373.15,250.0)
    fluid.addComponent('methane',1.0)
    fluid.setMixingRule('classic')
    probe=jneqsim.process.equipment.reservoir.SimpleReservoir('Unit-volume tank')
    probe.setReservoirFluid(fluid.clone(),1.0,0.0,0.0)
    reservoir_volume=gip_GSm3*1e9/float(probe.getGasInPlace('Sm3'))
    reservoir=jneqsim.process.equipment.reservoir.SimpleReservoir('Depletion tank')
    reservoir.setReservoirFluid(fluid,reservoir_volume,0.0,0.0)
    reservoir.setLowPressureLimit(1.0,'bara')
    producer=reservoir.addGasProducer('Gas production')
    reservoir.run()
    state=reservoir.getReservoirFluid()
    mass0=float(state.getTotalNumberOfMoles()*state.getMolarMass())
    initial_gip=float(reservoir.getGasInPlace('GSm3'))
    assert abs(initial_gip/gip_GSm3-1.0)<1e-8
    withdrawn=0.0;relative_errors=[];productions=[];pressures=[]
    for year in range(years):
        pressure=float(state.getPressure('bara'))
        # Assumed deliverability control: taper rate towards a 50 bara abandonment pressure.
        # This rule is not an IPR or a tubing solution; the tank pressure is solved by TV flash.
        supply_fraction=max(0.0,min(1.0,(pressure-50.0)/200.0))
        remaining=float(reservoir.getGasInPlace('GSm3'))
        annual=min(capacity_GSm3_year*supply_fraction,0.12*remaining)
        producer.setFlowRate(max(annual*1e9/365.0,1e-6),'Sm3/day')
        producer.run()
        dt=365.0*86400.0
        m_rate=float(producer.getFlowRate('kg/sec'))
        produced=float(producer.getFlowRate('Sm3/day'))*365.0/1e9
        withdrawn+=m_rate*dt
        reservoir.runTransient(dt,jpype.JClass('java.util.UUID').randomUUID())
        mass=float(state.getTotalNumberOfMoles()*state.getMolarMass())
        error=abs(mass-(mass0-withdrawn))/mass0
        assert error<1e-9
        assert mass>0.0 and 49.0<float(state.getPressure('bara'))<=250.0
        assert abs(state.getTemperature('K')-373.15)<1e-8
        relative_errors.append(error);productions.append(produced)
        pressures.append(float(state.getPressure('bara')))
    recovery=sum(productions)/initial_gip
    assert 0.0<recovery<1.0
    return {'production_GSm3':productions,'pressure_bara':pressures,
            'recovery_fraction':recovery,'gip_GSm3':initial_gip,
            'max_relative_mass_error':max(relative_errors)}

if __name__=='__main__':
 results={str(gip):depletion_profile(gip,rate) for gip,rate in [(65.,6.),(100.,8.),(145.,10.)]}
 path=BOOK/'verification/scientific_revision/ch27_depletion_probe.json'
 path.write_text(json.dumps(results,indent=2),encoding='utf-8')
 print([(k,v['recovery_fraction'],v['max_relative_mass_error']) for k,v in results.items()],flush=True)
 sys.stdout.flush();sys.stderr.flush();os._exit(0)
