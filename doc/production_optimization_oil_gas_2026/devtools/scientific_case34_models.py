"""Literal Chapter 34 factories: explicit equilibrium knockout and energy boundary."""
import jpype
import numpy as np
import json
from pathlib import Path
jneqsim = jpype.JPackage('neqsim')
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
Compressor = jneqsim.process.equipment.compressor.Compressor
Cooler = jneqsim.process.equipment.heatexchanger.Cooler
Valve = jneqsim.process.equipment.valve.ThrottlingValve
Mixer = jneqsim.process.equipment.mixer.Mixer
Expander = jneqsim.process.equipment.expander.Expander
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

platform_recipe = dict(zip(
    ['nitrogen','CO2','methane','ethane','propane','i-butane',
     'n-butane','i-pentane','n-pentane','n-hexane','n-heptane',
     'n-octane','n-nonane','n-decane'],
    [.008,.025,.750,.080,.040,.012,.018,.010,.008,.012,.015,
     .010,.007,.005]))

def process_boundary_check(feed, products, duties_W):
    """Adiabatic valves/mixers/separators; shaft work and cooler duty enter fluid."""
    f = feed.getFluid()
    mass_in = float(feed.getFlowRate('kg/hr'))
    mass_out = sum(float(s.getFlowRate('kg/hr')) for s in products)
    mass_error = abs(mass_out-mass_in)/mass_in
    h_in = float(f.getEnthalpy())
    h_out = sum(float(s.getFluid().getEnthalpy()) for s in products)
    energy_error = abs(h_out-h_in-sum(duties_W))/max(
        abs(h_in), abs(h_out), sum(abs(v) for v in duties_W), 1.0)
    component_error = 0.0
    n_scale = float(f.getTotalNumberOfMoles())
    for i in range(f.getNumberOfComponents()):
        name = str(f.getComponent(i).getComponentName())
        ni = float(f.getComponent(name).getNumberOfmoles())
        no = sum(float(s.getFluid().getComponent(name).getNumberOfmoles())
                 for s in products)
        component_error = max(component_error, abs(no-ni)/n_scale)
    assert mass_error < 1e-7, mass_error
    assert component_error < 1e-7, component_error
    assert energy_error < 1e-5, energy_error
    assert all(np.isfinite(s.getFlowRate('kg/hr')) and
               s.getFlowRate('kg/hr') >= 0 and
               s.getPressure('bara') > 0 and s.getTemperature('K') > 0
               for s in products)
    return dict(mass_relative=mass_error, component_relative=component_error,
                energy_relative=energy_error)

def build_platform_case(hp_bara=80.0, rate_kghr=500000.0):
    """Reduced topsides with ideal equilibrium knockout before each compressor."""
    fluid = jneqsim.thermo.system.SystemSrkEos(348.15, 120.0)
    for name, fraction in platform_recipe.items():
        fluid.addComponent(name, fraction)
    fluid.setMixingRule('classic')
    ps = ProcessSystem(); liquids=[]; compressors=[]; coolers=[]
    def run_add(unit):
        ps.add(unit); unit.run(); return unit
    feed = Stream('Platform Feed', fluid)
    feed.setFlowRate(rate_kghr,'kg/hr'); run_add(feed)
    choke = Valve('HP Choke', feed)
    choke.setOutletPressure(hp_bara); run_add(choke)
    hp = run_add(Separator('HP Separator',choke.getOutletStream()))
    valve = Valve('HP-LP Valve',hp.getLiquidOutStream())
    valve.setOutletPressure(15.0);run_add(valve)
    lp=run_add(Separator('LP Separator',valve.getOutletStream()))
    liquids.append(lp.getLiquidOutStream())
    gas=lp.getGasOutStream()
    for i,pout in enumerate([30.0,55.0,hp_bara],1):
        cooler=Cooler('Recompression Cooler '+str(i),gas)
        cooler.setOutTemperature(308.15);run_add(cooler);coolers.append(cooler)
        knockout=run_add(Separator('Recompression KO '+str(i),cooler.getOutletStream()))
        liquids.append(knockout.getLiquidOutStream())
        comp=Compressor('Recomp Stage '+str(i),knockout.getGasOutStream())
        comp.setUsePolytropicCalc(True);comp.setPolytropicEfficiency(.75)
        comp.setOutletPressure(pout,'bara');run_add(comp);compressors.append(comp)
        gas=comp.getOutletStream()
    mixer=Mixer('Combined HP Gas');mixer.addStream(hp.getGasOutStream())
    mixer.addStream(gas);run_add(mixer)
    cooler=Cooler('Export Suction Cooler',mixer.getOutletStream())
    cooler.setOutTemperature(308.15);run_add(cooler);coolers.append(cooler)
    knockout=run_add(Separator('Export Suction KO',cooler.getOutletStream()))
    liquids.append(knockout.getLiquidOutStream())
    comp=Compressor('Export Compressor',knockout.getGasOutStream())
    comp.setUsePolytropicCalc(True);comp.setPolytropicEfficiency(.78)
    comp.setOutletPressure(180.0,'bara');run_add(comp);compressors.append(comp)
    cooler=Cooler('Export Aftercooler',comp.getOutletStream())
    cooler.setOutTemperature(313.15);run_add(cooler);coolers.append(cooler)
    export_ko=run_add(Separator('Export KO',cooler.getOutletStream()))
    liquids.append(export_ko.getLiquidOutStream())
    export=export_ko.getGasOutStream();ps.run()
    checks=process_boundary_check(feed,liquids+[export],
        [float(c.getPower()) for c in compressors]+[float(c.getDuty()) for c in coolers])
    for c in compressors:
        assert c.getPower()>0
        inlet=c.getInletStream()
        assert inlet.getFluid().getNumberOfPhases()==1
        assert c.getOutletStream().getPressure('bara')>inlet.getPressure('bara')
    row=dict(hp_bara=hp_bara, feed_kghr=rate_kghr,
             lp_liquid_m3hr=float(lp.getLiquidOutStream().getFlowRate('m3/hr')),
             total_liquid_kghr=sum(float(s.getFlowRate('kg/hr')) for s in liquids),
             export_gas_MSm3day=float(export.getFlowRate('MSm3/day')),
             power_MW=sum(float(c.getPower()) for c in compressors)/1e6,
             export_power_MW=float(comp.getPower())/1e6,
             export_temperature_C=float(export.getTemperature('C')),
             checks=checks)
    return ps,row,dict(feed=feed,hp=hp,lp=lp,compressors=compressors,
                       products=liquids+[export],coolers=coolers)

platform, platform_base, platform_units=build_platform_case()
Path('ch34_platform_base.json').write_text(json.dumps(platform_base,indent=2))
print(json.dumps(platform_base,indent=2))
