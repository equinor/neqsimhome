import jpype
import json
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

jneqsim = jpype.JPackage("neqsim")
Stream = jneqsim.process.equipment.stream.Stream
ThreePhaseSeparator = jneqsim.process.equipment.separator.ThreePhaseSeparator
Compressor = jneqsim.process.equipment.compressor.Compressor
Valve = jneqsim.process.equipment.valve.ThrottlingValve
Mixer = jneqsim.process.equipment.mixer.Mixer
Cooler = jneqsim.process.equipment.heatexchanger.Cooler
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
ProcessModel = jneqsim.process.processmodel.ProcessModel
ThermodynamicOperations = jneqsim.thermodynamicoperations.ThermodynamicOperations

fpso_balance_checks = []
dry_recipe = {
    "nitrogen": .003, "CO2": .008, "methane": .280, "ethane": .045,
    "propane": .035, "i-butane": .012, "n-butane": .020,
    "i-pentane": .015, "n-pentane": .012, "n-hexane": .025,
    "n-heptane": .045, "n-octane": .060, "n-nonane": .080,
    "n-decane": .360,
}
assert abs(sum(dry_recipe.values()) - 1.0) < 1e-12

def reference_fluid(water_moles):
    fluid = jneqsim.thermo.system.SystemSrkCPAstatoil(288.15, 1.01325)
    for name, fraction in dry_recipe.items():
        fluid.addComponent(name, fraction)
    fluid.addComponent("water", float(water_moles))
    fluid.setMixingRule(10)
    fluid.setMultiPhaseCheck(True)
    ThermodynamicOperations(fluid).TPflash()
    fluid.initProperties()
    return fluid

def reference_liquid_volumes(fluid):
    oil = fluid.getPhase("oil").getVolume("m3") if fluid.hasPhaseType("oil") else 0.0
    water = fluid.getPhase("aqueous").getVolume("m3") if fluid.hasPhaseType("aqueous") else 0.0
    assert oil > 0 and water >= 0
    return float(oil), float(water)

def fpso_balance(name, inlets, outlets, heat_and_work_W=0.0):
    def mass(stream):
        return float(stream.getFlowRate("kg/sec"))
    def enthalpy(stream):
        return float(stream.getFluid().getEnthalpy()) if mass(stream) > 1e-12 else 0.0
    mi, mo = sum(map(mass, inlets)), sum(map(mass, outlets))
    hi, ho = sum(map(enthalpy, inlets)), sum(map(enthalpy, outlets))
    mass_error = abs(mo-mi)/max(mi, 1e-8)
    names = list(dry_recipe) + ["water"]
    molar_scale = max(sum(s.getFluid().getTotalNumberOfMoles() for s in inlets), 1.0)
    errors = []
    for component in names:
        ni = sum(s.getFluid().getComponent(component).getNumberOfmoles() for s in inlets)
        no = sum(s.getFluid().getComponent(component).getNumberOfmoles() for s in outlets)
        errors.append(abs(ni-no)/molar_scale)
    energy_error = abs(ho-hi-heat_and_work_W)/max(abs(hi), abs(ho), abs(heat_and_work_W), 1.0)
    assert all(math.isfinite(x) for x in [mi, mo, hi, ho, energy_error])
    assert mass_error < 1e-6, (name, "mass", mass_error)
    assert max(errors) < 1e-7, (name, "component", max(errors))
    assert energy_error < 1e-5, (name, "energy", energy_error)
    for stream in outlets:
        if mass(stream) > 1e-10:
            fluid = stream.getFluid()
            fluid.initProperties()
            assert fluid.getTemperature() > 0 and fluid.getPressure() > 0
            assert fluid.getDensity("kg/m3") > 0
    fpso_balance_checks.append(dict(name=name, mass_relative=mass_error,
                                    component_relative=max(errors), energy_relative=energy_error))

def build_fpso_model(water_cut_fraction):
    """Reduced separator/compressor model; WC is equilibrium liquid volume at 15 C, 1.01325 bara."""
    wc = float(water_cut_fraction)
    assert .10 <= wc <= .80
    def error(water_moles):
        oil, water = reference_liquid_volumes(reference_fluid(water_moles))
        return water/(oil+water)-wc
    water_moles = brentq(error, 1e-7, 1000., xtol=1e-10)
    fluid = reference_fluid(water_moles)
    vo, vw = reference_liquid_volumes(fluid)
    calculated_wc = vw/(vo+vw)
    assert abs(calculated_wc-wc) < 1e-7
    # Fixed TOTAL equilibrium liquid volume at the declared reference conditions.
    mass_in_sample = fluid.getTotalNumberOfMoles()*fluid.getMolarMass()
    flow_kg_hr = mass_in_sample*200.0/(vo+vw)
    fluid.setTotalFlowRate(flow_kg_hr, "kg/hr")
    ThermodynamicOperations(fluid).TPflash()
    fluid.initProperties()
    reference_oil, reference_water = reference_liquid_volumes(fluid)
    assert abs(3600*(reference_oil+reference_water)-200.0) < 1e-4
    assert abs(reference_water/(reference_oil+reference_water)-wc) < 1e-7
    feed = Stream("FPSO Inlet", fluid)
    feed.setTemperature(70.0, "C")
    feed.setPressure(35.0, "bara")
    sep1 = ThreePhaseSeparator("1st Stage Sep", feed)
    valve12 = Valve("Sep1-Sep2 Valve", sep1.getOilOutStream())
    valve12.setOutletPressure(8.0)
    sep2 = ThreePhaseSeparator("2nd Stage Sep", valve12.getOutletStream())
    valve23 = Valve("Sep2-Sep3 Valve", sep2.getOilOutStream())
    valve23.setOutletPressure(2.5)
    sep3 = ThreePhaseSeparator("3rd Stage Sep", valve23.getOutletStream())
    sep_system = ProcessSystem()
    for unit in [feed, sep1, valve12, sep2, valve23, sep3]:
        sep_system.add(unit)
    sep_system.run()

    comp_system = ProcessSystem()
    compressors, coolers, knockouts, mixers = [], [], [], []
    def compression_stage(index, inlet, pressure, efficiency):
        comp = Compressor(f"Compressor {index}", inlet)
        comp.setOutletPressure(pressure, "bara")
        comp.setUsePolytropicCalc(True)
        comp.setPolytropicEfficiency(efficiency)
        cooler = Cooler(f"Cooler {index}", comp.getOutletStream())
        cooler.setOutTemperature(313.15)
        knockout = ThreePhaseSeparator(f"Compressor KO {index}", cooler.getOutletStream())
        for unit in [comp, cooler, knockout]:
            comp_system.add(unit)
        compressors.append(comp); coolers.append(cooler); knockouts.append(knockout)
        return knockout.getGasOutStream()

    # LP gas is first raised to 8 bara before it joins 8 bara separator gas.
    gas8 = compression_stage(1, sep3.getGasOutStream(), 8., .72)
    mixer8 = Mixer("8 bara Gas Mixer")
    mixer8.addStream(gas8); mixer8.addStream(sep2.getGasOutStream())
    comp_system.add(mixer8); mixers.append(mixer8)
    suction8 = ThreePhaseSeparator("8 bara Suction Scrubber", mixer8.getOutletStream())
    comp_system.add(suction8); knockouts.append(suction8)
    gas20 = compression_stage(2, suction8.getGasOutStream(), 20., .74)
    gas35 = compression_stage(3, gas20, 35., .76)
    hp_mixer = Mixer("HP Gas Mixer")
    hp_mixer.addStream(gas35); hp_mixer.addStream(sep1.getGasOutStream())
    comp_system.add(hp_mixer); mixers.append(hp_mixer)
    export_ko = ThreePhaseSeparator("Export Knockout", hp_mixer.getOutletStream())
    comp_system.add(export_ko); knockouts.append(export_ko)
    comp_system.run()
    fpso = ProcessModel()
    fpso.add("Separation", sep_system); fpso.add("Compression", comp_system)
    equipment = dict(feed=feed, sep1=sep1, sep2=sep2, sep3=sep3,
        comp1=compressors[0], comp2=compressors[1], comp3=compressors[2],
        hp_mixer=hp_mixer, export_ko=export_ko, valves=[valve12,valve23],
        compressors=compressors, coolers=coolers, knockouts=knockouts, mixers=mixers,
        reference_water_cut=calculated_wc, reference_liquid_m3_hr=200.0)
    return fpso, equipment

def verify_fpso(equipment):
    e=equipment
    separators=[e['sep1'], e['sep2'], e['sep3']]+e['knockouts']
    for unit in separators:
        fpso_balance(str(unit.getName()), list(unit.getInletStreams()),
            [unit.getGasOutStream(),unit.getOilOutStream(),unit.getWaterOutStream()])
    for unit in e['valves']+e['mixers']:
        fpso_balance(str(unit.getName()),list(unit.getInletStreams()),[unit.getOutletStream()])
    for unit in e['compressors']:
        inlet=unit.getInletStream().getFluid()
        assert inlet.getNumberOfPhases()==1 and str(inlet.getPhase(0).getType())=='GAS'
        assert unit.getOutletStream().getPressure('bara')>unit.getInletStream().getPressure('bara')
        assert unit.getPower()>0
        fpso_balance(str(unit.getName()),list(unit.getInletStreams()),[unit.getOutletStream()],unit.getPower())
    for unit in e['coolers']:
        fpso_balance(str(unit.getName()),list(unit.getInletStreams()),[unit.getOutletStream()],unit.getDuty())
    # Every separated aqueous/condensate stream crosses the external boundary.
    liquids=[e['sep3'].getOilOutStream()]
    liquids += [unit.getWaterOutStream() for unit in (e['sep1'],e['sep2'],e['sep3'])]
    liquids += [stream for unit in e['knockouts'] for stream in (unit.getOilOutStream(),unit.getWaterOutStream())]
    products=liquids+[e['export_ko'].getGasOutStream()]
    duty=sum(unit.getPower() for unit in e['compressors'])+sum(unit.getDuty() for unit in e['coolers'])
    fpso_balance('whole reduced FPSO',[e['feed']],products,duty)
    sep1_liquid=e['sep1'].getOilOutStream().getFlowRate('m3/hr')+e['sep1'].getWaterOutStream().getFlowRate('m3/hr')
    return dict(water_cut_pct=100*e['reference_water_cut'],
        inlet_mass_kg_hr=e['feed'].getFlowRate('kg/hr'),
        reference_liquid_m3_hr=e['reference_liquid_m3_hr'],
        oil_rate_m3hr=e['sep3'].getOilOutStream().getFlowRate('m3/hr'),
        sep1_water_m3hr=e['sep1'].getWaterOutStream().getFlowRate('m3/hr'),
        gas_rate_MSm3d=e['export_ko'].getGasOutStream().getFlowRate('MSm3/day'),
        compression_MW=sum(unit.getPower() for unit in e['compressors'])/1e6,
        sep1_actual_liquid_m3hr=sep1_liquid,
        sep1_liquid_util_pct=100*sep1_liquid/400.,
        mass_products_kg_hr=sum(s.getFlowRate('kg/hr') for s in products))

fpso, equip = build_fpso_model(.30)
fpso.run()
fpso_base = verify_fpso(equip)
print(json.dumps(fpso_base, indent=2))
