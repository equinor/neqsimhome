from pathlib import Path
import re
BOOK=Path(__file__).resolve().parents[1]
FENCES=re.compile(r'^```(python|java)\s*\n(.*?)^```',re.M|re.S)

def edit(ch, replacements, transforms=None):
    p=next((BOOK/'chapters').glob(ch+'*/chapter.md'))
    text=p.read_text(encoding='utf-8')
    blocks=list(FENCES.finditer(text))
    for index,match in reversed(list(enumerate(blocks,1))):
        code=replacements.get(index,match[2])
        if transforms:
            code=transforms(code)
        text=text[:match.start(2)]+code.rstrip()+'\n'+text[match.end(2):]
    p.write_text(text,encoding='utf-8')

gt_setup='''# Illustrative 30 MW package, not an OEM performance guarantee.
gtpkg = jneqsim.process.equipment.powergeneration.gasturbine
spec = gtpkg.GasTurbineSpec("Teaching turbine", gtpkg.GasTurbineSpec.TurbineType.AERODERIVATIVE,
                          30.0e6, 9500.0, 90.0, 773.15, 25.0, 100.0, "Synthetic teaching basis")
fuel_gas = jneqsim.thermo.system.SystemSrkEos(298.15, 25.0)
for name, fraction in [("methane", 0.90), ("ethane", 0.06), ("propane", 0.03), ("CO2", 0.01)]:
    fuel_gas.addComponent(name, fraction)
fuel_gas.setMixingRule("classic")
fuel_stream = jneqsim.process.equipment.stream.Stream("Fuel gas", fuel_gas)
fuel_stream.setFlowRate(500.0, "kg/hr")
fuel_stream.run()
gas_turbine = gtpkg.GasTurbineUnit("GT-001", fuel_stream, spec)
gas_turbine.setAmbient(288.15, 1.01325)
gas_turbine.setDemandedPower(20.0e6)
gas_turbine.run()
print("Available shaft power (MW):", gas_turbine.getAvailablePowerW() / 1e6)
print("Demanded shaft power (MW):", gas_turbine.getDemandedPowerW() / 1e6)
print("Thermal efficiency:", gas_turbine.getThermalEfficiency())
print("Fuel demand (kg/hr):", gas_turbine.getFuelMassFlowKgPerHr())
print("Power shortfall (MW):", gas_turbine.getPowerShortfallW() / 1e6)
'''
edit('ch14',{1:gt_setup+'''# Link a calculated compressor load instead of prescribing shaft demand.
gas_feed = jneqsim.process.equipment.stream.Stream("Compression feed", fuel_gas.clone())
gas_feed.setFlowRate(50000.0, "kg/hr")
gas_feed.run()
compressor = jneqsim.process.equipment.compressor.Compressor("Driven compressor", gas_feed)
compressor.setOutletPressure(100.0)
compressor.setIsentropicEfficiency(0.78)
compressor.run()
gt = gtpkg.GasTurbineUnit("GT-A", fuel_stream, spec)
gt.setAmbient(288.15, 1.01325)
gt.addPowerConsumer(compressor)
gt.run()
print("Driven load (MW):", gt.getDemandedPowerW() / 1e6)
print("Fuel (kg/hr):", gt.getFuelMassFlowKgPerHr())
''',21:'''ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer
optimizer = ProductionOptimizer()
result = optimizer.optimizeThroughput(process, feed, 10000.0, 60000.0, "kg/hr", None)
print("Feasible:", result.isFeasible(), "Rate (kg/hr):", result.getOptimalRate())
print(ProductionOptimizer.formatUtilizationTable(result.getUtilizationRecords()))
''',},lambda s:s.replace('getPolytropicHead() / 1000.0','getPolytropicFluidHead()').replace('getPolytropicHead():.0f} J/kg','getPolytropicFluidHead():.1f} kJ/kg'))

edit('ch15',{},lambda s:s.replace('chart.setSurgeCurve(surge_flow, surge_head)', 'SafeSplineSurgeCurve = jneqsim.process.equipment.compressor.SafeSplineSurgeCurve\nchart.setSurgeCurve(SafeSplineSurgeCurve(surge_flow, surge_head))').replace('compressor.setUseCompressorChart(True)','chart.setHeadUnit("kJ/kg")\nchart.setUseCompressorChart(True)\ncompressor.setSpeed(11500.0)').replace('speed100_eff)', '[v * 100.0 for v in speed100_eff])').replace('speed90_eff)', '[v * 100.0 for v in speed90_eff])').replace('speed80_eff)', '[v * 100.0 for v in speed80_eff])').replace('getPolytropicHead()', 'getPolytropicFluidHead()'))

edit('ch16',{6:'''PinchAnalysis = jneqsim.process.equipment.heatexchanger.heatintegration.PinchAnalysis
# Define explicit process-stream targets: automatic equipment discovery may be empty.
pinch = PinchAnalysis(10.0)
pinch.addHotStream("Hot utility source", 150.0, 60.0, 20.0)  # mCp in kW/K
pinch.addColdStream("Feed heating", 25.0, 120.0, 12.0)
pinch.run()
print("Minimum heating utility (kW):", pinch.getMinimumHeatingUtility())
print("Minimum cooling utility (kW):", pinch.getMinimumCoolingUtility())
print("Hot-side pinch (C):", pinch.getPinchTemperatureC())
'''},lambda s:s.replace('pinch = PinchAnalysis()\npinch.setMinDeltaT(10.0)','pinch = PinchAnalysis(10.0)').replace('getMaximumHeatRecovery()', 'getMaximumHeatRecovery()'))
edit('ch17',{},lambda s:s.replace('"V-1", stream','"V-1", feed').replace('"V-2", stream','"V-2", feed').replace('"V-3", stream','"V-3", feed'))

edit('ch18',{
1:gt_setup,
2:'''import matplotlib.pyplot as plt
ambient_temps = list(range(-20, 42, 2))
available_mw, fuel_kg_hr = [], []
for temperature_c in ambient_temps:
    gas_turbine.setAmbient(temperature_c + 273.15, 1.01325)
    gas_turbine.run()
    available_mw.append(gas_turbine.getAvailablePowerW() / 1e6)
    fuel_kg_hr.append(gas_turbine.getFuelMassFlowKgPerHr())
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].plot(ambient_temps, available_mw)
axes[0].axhline(20.0, linestyle="--", color="black", label="Shaft demand")
axes[0].set_ylabel("Available shaft power (MW)")
axes[0].legend()
axes[1].plot(ambient_temps, fuel_kg_hr)
axes[1].set_ylabel("Fuel demand (kg/hr)")
for ax in axes:
    ax.set_xlabel("Ambient temperature (C)")
    ax.grid(alpha=0.3)
fig.suptitle("Illustrative turbine ambient derating at 20 MW demand")
fig.tight_layout()
fig.savefig("figures/gt_ambient_performance.png", dpi=150, bbox_inches="tight")
''',
3:'''# Heat-recovery screening from an explicitly specified exhaust composition.
# GasTurbineUnit supplies package exhaust flow/T; this is not a combustor chemistry model.
gas_turbine.setAmbient(288.15, 1.01325)
gas_turbine.run()
exhaust_fluid = jneqsim.thermo.system.SystemSrkEos(gas_turbine.getExhaustTemperatureK(), 1.05)
for name, fraction in [("nitrogen", 0.76), ("oxygen", 0.12), ("CO2", 0.06), ("water", 0.06)]:
    exhaust_fluid.addComponent(name, fraction)
exhaust_fluid.setMixingRule("classic")
exhaust = jneqsim.process.equipment.stream.Stream("Illustrative exhaust", exhaust_fluid)
exhaust.setFlowRate(gas_turbine.getExhaustMassFlowKgPerS(), "kg/sec")
exhaust.run()
hrsg = jneqsim.process.equipment.powergeneration.HRSG("HRSG", exhaust)
hrsg.setSteamPressure(40.0)
hrsg.setSteamTemperature(673.15)
hrsg.setFeedWaterTemperature(363.15)
hrsg.setEffectiveness(0.80)
hrsg.run()
steam_fluid = jneqsim.thermo.system.SystemSrkEos(673.15, 40.0)
steam_fluid.addComponent("water", 1.0)
steam_fluid.setMixingRule("classic")
steam = jneqsim.process.equipment.stream.Stream("Recovered steam", steam_fluid)
steam.setFlowRate(hrsg.getSteamFlowRate("kg/sec"), "kg/sec")
steam.run()
steam_turbine = jneqsim.process.equipment.powergeneration.SteamTurbine("ST", steam)
steam_turbine.setOutletPressure(0.08, "bara")
steam_turbine.setIsentropicEfficiency(0.85)
steam_turbine.run()
print("Recovered duty (MW):", hrsg.getHeatTransferred("MW"))
print("Steam production (kg/sec):", steam.getFlowRate("kg/sec"))
print("Steam turbine power (MW):", steam_turbine.getPower("MW"))
''',
6:'''ProcessSystem = jneqsim.process.processmodel.ProcessSystem
Compressor = jneqsim.process.equipment.compressor.Compressor
ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer
feed = jneqsim.process.equipment.stream.Stream("Compression feed", fuel_gas.clone())
feed.setFlowRate(20000.0, "kg/hr")
feed.setPressure(25.0, "bara")
comp = Compressor("Export compressor", feed)
comp.setOutletPressure(150.0, "bara")
comp.setIsentropicEfficiency(0.78)
comp.setMaximumPower(15.0e6)  # W: 15 MW driver limit
process = ProcessSystem()
process.add(feed)
process.add(comp)
process.run()
result = ProductionOptimizer().optimizeThroughput(process, feed, 5000.0, 50000.0, "kg/hr", None)
print("Feasible:", result.isFeasible(), "Rate (kg/hr):", result.getOptimalRate())
print("Compression power (MW):", comp.getPower("MW"))
''',
7:'''gt = gtpkg.GasTurbineUnit("GT-A", fuel_stream, spec)
gt.setAmbient(288.15, 1.01325)
gt.addPowerConsumer(comp)
gt.run()
print("Demanded shaft power (MW):", gt.getDemandedPowerW() / 1e6)
print("Available power (MW):", gt.getAvailablePowerW() / 1e6)
print("Fuel demand (kg/hr):", gt.getFuelMassFlowKgPerHr())
print("CO2 (kg/hr):", gt.getCO2EmissionKgPerHr())
print("Overloaded:", gt.isOverloaded())
''',
8:'''# Compare matched pressure-ratio operating points before introducing an OEM map.
design_rate = feed.getFlowRate("kg/hr")
design_power_kw = comp.getPower("kW")
feed.setFlowRate(0.70 * design_rate, "kg/hr")
process.run()
print("70% flow power (kW):", comp.getPower("kW"))
print("Design flow power (kW):", design_power_kw)
print("Constant-efficiency screening; vendor map and recycle losses are not included.")
feed.setFlowRate(design_rate, "kg/hr")
process.run()
''',
},lambda s:s.replace('PinchAnalysis("Platform Heat Integration")','PinchAnalysis(10.0)').replace('pinch.setMinApproachTemperature(10.0)','# Minimum approach was set in the constructor.').replace('fluid.addComponent("C7", 0.20)','fluid.addTBPfraction("C7", 0.20, 0.200, 0.85)').replace('setMaximumPower(40000.0)','setMaximumPower(40.0e6)').replace('# Carbon cost (Norwegian NCS)','# Illustrative carbon-price scenario, not current Norwegian tax or ETS quotations').replace('# Simulate power demand at varying production rates','# Illustrative assumed demand curves; these arrays are not NeqSim predictions.'))
