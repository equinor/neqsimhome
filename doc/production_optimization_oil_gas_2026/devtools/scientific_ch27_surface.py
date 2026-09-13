import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import qmc
import jpype
jneqsim = jpype.JPackage('neqsim')
Path('figures').mkdir(exist_ok=True)

def surface_case(feed_rate, feed_pres, water_mole_fraction, temperature, comp_eff):
    """Fresh CPA three-phase feed; prescribed mass rate, no upstream feedback."""
    assert feed_rate > 0 and 0 < water_mole_fraction < 1
    assert 0 < feed_pres < 120 and 0 < comp_eff <= 1
    fluid = jneqsim.thermo.system.SystemSrkCPAstatoil(temperature+273.15, feed_pres)
    # Hydrocarbon fractions normalized before the overall water mole fraction.
    for name, amount in [('methane', .75), ('ethane', .08),
                         ('propane', .04), ('nC10', .08)]:
        fluid.addComponent(name, amount/.95*(1-water_mole_fraction))
    fluid.addComponent('water', water_mole_fraction)
    fluid.setMixingRule(10); fluid.setMultiPhaseCheck(True)
    feed = jneqsim.process.equipment.stream.Stream('Feed', fluid)
    feed.setFlowRate(feed_rate, 'kg/hr'); feed.run()
    sep = jneqsim.process.equipment.separator.ThreePhaseSeparator('Separator', feed)
    sep.run()
    gas = sep.getGasOutStream()
    assert gas.getFluid().getNumberOfPhases() == 1
    comp = jneqsim.process.equipment.compressor.Compressor('Compressor', gas)
    comp.setIsentropicEfficiency(comp_eff)
    comp.setOutletPressure(120., 'bara'); comp.run()
    assert comp.getPower() > 0
    def balance(inlet, outlets, work=0.):
        streams = [inlet]+outlets
        for s in streams: s.getFluid().initProperties()
        assert all(np.isfinite(s.getFlowRate('kg/hr')) and s.getFlowRate('kg/hr') >= 0
                   and s.getTemperature('K') > 0 and s.getPressure('bara') > 0
                   for s in streams)
        f = inlet.getFluid()
        mass = abs(sum(s.getFlowRate('kg/hr') for s in outlets)
                   - inlet.getFlowRate('kg/hr'))/inlet.getFlowRate('kg/hr')
        h0 = float(f.getEnthalpy())
        h1 = sum(float(s.getFluid().getEnthalpy()) for s in outlets)
        energy = abs(h1-h0-work)/max(abs(h0),abs(h1),abs(work),1.)
        components = 0.
        for i in range(f.getNumberOfComponents()):
            name = str(f.getComponent(i).getComponentName())
            ni = float(f.getComponent(name).getNumberOfmoles())
            no = sum(float(s.getFluid().getComponent(name).getNumberOfmoles())
                     for s in outlets)
            components = max(components,abs(no-ni)/f.getTotalNumberOfMoles())
        assert mass < 1e-7 and components < 1e-7 and energy < 1e-5, (mass,components,energy)
        return dict(mass_relative=mass,component_relative=components,energy_relative=energy)
    liquids = [sep.getOilOutStream(), sep.getWaterOutStream()]
    checks = {'separator':balance(feed,[gas]+liquids),
              'compressor':balance(gas,[comp.getOutletStream()],float(comp.getPower())),
              'whole_process':balance(feed,[comp.getOutletStream()]+liquids,float(comp.getPower()))}
    return dict(gas_production_kg_hr=float(gas.getFlowRate('kg/hr')),
                compressor_power_kW=float(comp.getPower('kW')),checks=checks)

# Independent uniform inputs are an explicitly assumed screening distribution.
param_ranges = {'feed_rate':(50000.,120000.), 'feed_pres':(35.,75.),
                'water_mole_fraction':(.02,.45), 'temperature':(25.,50.),
                'comp_eff':(.70,.85)}
unit_samples = qmc.LatinHypercube(d=5,seed=42).random(200)
samples = qmc.scale(unit_samples,[v[0] for v in param_ranges.values()],
                    [v[1] for v in param_ranges.values()])
screen_records = []
for values in samples:
    inputs = dict(zip(param_ranges,map(float,values)))
    screen_records.append({'inputs':inputs,**surface_case(**inputs)})
assert len(screen_records) == 200  # Failed balances raise; no silent survivor-only CDF.
gas_prod = np.array([r['gas_production_kg_hr'] for r in screen_records])
print('Gas rate CDF P10/P50/P90 kg/hr:',np.percentile(gas_prod,[10,50,90]))
Path('ch27_surface_monte_carlo.json').write_text(json.dumps(screen_records,indent=2))
