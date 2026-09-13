"""One-time repairs of demonstrated capacity-example errors."""
from pathlib import Path
import re,shutil
B=Path(__file__).resolve().parents[2];P=re.compile(r'^```python([^\n]*)\n(.*?)^```',re.M|re.S)
path=next((B/'chapters').glob('ch20_*/chapter.md'));backup=B/'.build/backups/literal_solution_revision'/path.parent.name
backup.mkdir(parents=True,exist_ok=True)
if not (backup/'chapter.md').exists():shutil.copy2(path,backup/'chapter.md')
text=path.read_text(encoding='utf-8-sig');blocks=list(P.finditer(text));changes={}
changes[6]=blocks[5].group(2).replace('pipeline.setLength(80.0)','pipeline.setLength(80000.0)  # 80 km; API length is metres')
code=blocks[6].group(2)
code=code.replace('maximum system throughput','linear screening extrapolation').replace('Maximum system throughput:','Linear screening extrapolation:')
code+='\nprint("This extrapolation is not a capacity solution: rerun the full process and all constraints at any candidate rate.")\n'
changes[7]=code
changes[9]='''# Executed water-cut scenario on an explicit common liquid reference basis.
# Fixed oil+water reference volume; methane input follows a specified gas/oil ratio.
import numpy as np
reference_liquid_m3_hr = 200.0
reference_GOR_Sm3_m3 = 100.0
reference = {}
for component in ["n-heptane", "water", "methane"]:
    pure = jneqsim.thermo.system.SystemSrkCPAstatoil(288.15, 1.01325)
    pure.addComponent(component, 1.0)
    pure.setMixingRule(10)
    jneqsim.thermodynamicoperations.ThermodynamicOperations(pure).TPflash()
    pure.initProperties()
    reference[component] = (float(pure.getDensity("kg/m3")),
                            float(pure.getMolarMass()))
water_cut_results = []
for wc in [.10, .20, .30, .40, .50, .60, .70, .80]:
    oil_volume = reference_liquid_m3_hr*(1-wc)
    water_volume = reference_liquid_m3_hr*wc
    gas_volume = reference_GOR_Sm3_m3*oil_volume
    mass_rates = {name:volume*reference[name][0] for name,volume in
                  [("n-heptane",oil_volume),("water",water_volume),
                   ("methane",gas_volume)]}
    wet = jneqsim.thermo.system.SystemSrkCPAstatoil(343.15,65.0)
    for name,mass in mass_rates.items():
        wet.addComponent(name,mass/reference[name][1])
    wet.setMixingRule(10);wet.setMultiPhaseCheck(True)
    fd = jneqsim.process.equipment.stream.Stream("Specified wet feed",wet)
    fd.setFlowRate(sum(mass_rates.values()),"kg/hr")
    sep = jneqsim.process.equipment.separator.ThreePhaseSeparator("Water-cut separator",fd)
    comp = jneqsim.process.equipment.compressor.Compressor("Associated gas compressor",sep.getGasOutStream())
    comp.setOutletPressure(120.0);comp.setPolytropicEfficiency(.78)
    ps=jneqsim.process.processmodel.ProcessSystem()
    for equipment in [fd,sep,comp]:ps.add(equipment)
    ps.run()
    local_liquid=sum(float(s.getFlowRate("m3/hr")) for s in
                     [sep.getOilOutStream(),sep.getWaterOutStream()])
    water_cut_results.append({"reference_water_cut_pct":100*wc,
                              "first_separator_liquid_m3_hr":local_liquid,
                              "liquid_screen_utilization_pct":100*local_liquid/400.,
                              "gas_kg_hr":float(sep.getGasOutStream().getFlowRate("kg/hr")),
                              "compression_MW":float(comp.getPower("MW"))})
print(json.dumps(water_cut_results,indent=2))
print("Basis: oil and water volumes at 15 C, 1.01325 bara; fixed 200 m3/h liquid and specified GOR 100 Sm3/m3 oil.")
print("This methane/heptane/water scenario is not a well-deliverability prediction.")
'''
code=blocks[9].group(2)
code=code.replace('# At relief conditions (10% above design pressure)','# Explicit pressure convention: 10% overpressure applied to gauge set pressure')
code=code.replace('P_relief = P_design * 1.10  # bara, relief pressure','P_atm = 1.01325\nP_relief = P_atm + 1.10*(P_design-P_atm)  # bara')
code=code.replace('# Gas properties at relief conditions for API 520 sizing','# Gas-phase properties at the specified relief state; no device sizing certification\nfluid = feed.getFluid()')
start=code.index('# API 520 orifice area calculation (simplified)')
code=code[:start]+'''# Independent SI ideal-gas sonic-nozzle illustration (NASA Glenn mass-flow relation).
# Constant gamma=1.30 and Z=1 define the ideal-gas limiting calculation.
# The real-fluid Z printed above shows why this is not an API 520 PSV rating.
W_relief = 250000.0  # kg/hr, explicitly assumed gas load, not derived from blockage
T_relief = 353.15    # K, upstream stagnation temperature for the ideal model
gamma_ideal = 1.30
R_specific = 8.314462618/(MW_gas/1000.0)  # J/(kg K)
P_stagnation_Pa = P_relief*1e5
sonic_factor = (2/(gamma_ideal+1))**((gamma_ideal+1)/(2*(gamma_ideal-1)))
ideal_mass_flux = P_stagnation_Pa/math.sqrt(T_relief)*math.sqrt(gamma_ideal/R_specific)*sonic_factor
A_required = (W_relief/3600.0)/ideal_mass_flux  # m2; ideal nozzle, unit coefficient
critical_pressure_ratio = (2/(gamma_ideal+1))**(gamma_ideal/(gamma_ideal-1))
print(f"Ideal sonic mass flux: {ideal_mass_flux:.2f} kg/(m2 s)")
print(f"Ideal throat area: {A_required:.6f} m2; critical backpressure ratio {critical_pressure_ratio:.4f}")
print("Not a rated relief device: real-gas/two-phase discharge, coefficients, backpressure and code requirements remain to be evaluated.")
'''
changes[10]=code
for n,m in reversed(list(enumerate(blocks,1))):
    if n in changes:text=text[:m.start(2)]+changes[n].rstrip()+'\n'+text[m.end(2):]
text=text.replace('print("    Maximum system throughput:', 'print("    Linear screening extrapolation:')
# The cited primary equation supports only the newly explicit ideal-gas limit.
marker='print("Not a rated relief device: real-gas/two-phase discharge, coefficients, backpressure and code requirements remain to be evaluated.")\n```'
assert marker in text
text=text.replace(marker,marker+'\n\nThe sonic mass-flux expression follows the [NASA Glenn ideal-gas mass-flow relation](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/mass-flow-rate-equations/) at Mach one. It is used here to verify SI dimensions and the ideal limit; the assumed gas load and ideal area do not qualify a pressure-relief device.\n',1)
path.write_text(text,encoding='utf-8')
print('Repaired capacity pipeline length, extrapolation claim, executed reference-volume water-cut scenario and SI ideal nozzle illustration.')
