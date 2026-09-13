"""Repair production chapter's sequential Python contexts and external boundaries."""
from pathlib import Path
import re
BOOK=Path(__file__).resolve().parents[1]
p=next((BOOK/'chapters').glob('ch24*/chapter.md'))
text=p.read_text(encoding='utf-8-sig')
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
matches=list(PAT.finditer(text))
setup=matches[12][3]
def fix(n,language,code):
    if n==5:
        return setup+'\nprocess.enableConstraints()\nprint("Enabled constraints for the explicitly built process")\n'
    if n==32:
        return '''ProcessOptimizationEngine = jneqsim.process.util.optimizer.ProcessOptimizationEngine
engine = ProcessOptimizationEngine(process)
engine.setFeedStreamName("feed")
engine.setOutletStreamName("Export Comp")
report = engine.evaluateAllConstraints()
for equipment in report.getEquipmentStatuses():
    print(equipment.getEquipmentName(), equipment.getUtilization(), equipment.isWithinLimits())
    for constraint in equipment.getConstraints():
        print(constraint.getName(), constraint.getCurrentValue(), constraint.getUtilization())'''
    if n==33:
        return '''sensitivity = engine.analyzeSensitivity(feed.getFlowRate("kg/hr"),
                                        feed.getPressure("bara"), 150.0)
print("Flow sensitivity:", sensitivity.getFlowGradient())
print("Tightest constraint:", sensitivity.getTightestConstraint())'''
    if n==34:
        return '''# Fixed-composition process capacity; temperatures are kelvin.
pressures = [40.0, 60.0, 80.0]
temperatures = [343.15]
curve = engine.generateCapacityScreening(pressures, temperatures,
                                        150.0, 50000.0, 300000.0)
for point in curve.getPoints():
    print(point.getInletPressure(), point.getTemperature(), point.getMaxFlowRate())'''
    if n==35:
        return '''from pathlib import Path
rows = ["inlet_pressure_bara,temperature_K,max_mass_flow_kghr"]
for point in curve.getPoints():
    rows.append(f"{point.getInletPressure()},{point.getTemperature()},{point.getMaxFlowRate()}")
Path("process_capacity.csv").write_text("\\n".join(rows), encoding="utf-8")'''
    if n==41:
        return '''from pathlib import Path
import matplotlib.pyplot as plt
Path("figures").mkdir(exist_ok=True)
Objective = ProductionOptimizer.OptimizationObjective
Direction = ProductionOptimizer.ObjectiveType
objectives = jpype.java.util.ArrayList([
    Objective("throughput", lambda proc: proc.getUnit("feed").getFlowRate("kg/hr"),
              1.0, Direction.MAXIMIZE),
    Objective("power", lambda proc: proc.getUnit("Export Comp").getPower("MW"),
              1.0, Direction.MINIMIZE)])
pareto_config = (OptimizationConfig(50000.0, 300000.0).rateUnit("kg/hr")
    .searchMode(SearchMode.GOLDEN_SECTION_SCORE).maxIterations(20).paretoGridSize(5))
pareto = optimizer.optimizePareto(process, feed, pareto_config, objectives, None)
rates, powers = [], []
for point in pareto.getParetoFront():
    values = point.getObjectiveValues()
    rates.append(float(values["throughput"]))
    powers.append(float(values["power"]))
plt.figure(figsize=(7, 4))
plt.scatter(rates, powers)
plt.xlabel("Mass throughput (kg/hr)")
plt.ylabel("Compressor power (MW)")
plt.title("Non-dominated points for the declared synthetic model")
plt.grid(True, alpha=0.3)
plt.savefig("figures/pareto_front.png", dpi=150, bbox_inches="tight")'''
    if n==48:
        return '''# Query chart-derived constraint margins; curve units belong to the chart basis.
for name, constraint in comp.getCapacityConstraints().items():
    print(name, constraint.getCurrentValue(), constraint.getUnit(), constraint.getUtilization())
# Use a declared mass-flow envelope for this synthetic screening study.
config = (OptimizationConfig(50000.0, 300000.0).rateUnit("kg/hr")
          .searchMode(SearchMode.BINARY_FEASIBILITY).maxIterations(25))'''
    if n==59:
        return 'hp_sep = sep\n'+code+'\n# Reapply and solve the selected SLSQP candidate before reading equipment outputs.\nmulti_objective(result_slsqp.x)\n'
    if n==60:
        return (' pattern: optional NLopt package is required',code)
    if n==62:
        code='hp_sep = sep\n'+code
        code=code.replace('oil_rvps', 'oil_process_pressures')
        code=code.replace('# Oil vapor pressure (RVP)', '# Operating liquid pressure; this is not Reid vapor pressure.')
        code=code.replace('gas_rates[i] * 35.3 * gas_price / 1000', 'gas_rates[i] * 1.0e6 * 38.0 / 1055.05585262 * gas_price / 1000')
        return code.replace('# kUSD/day (approx)', '# kUSD/day; illustrative GCV=38 MJ/Sm3')
    if n in (66,67):
        return (' pattern: requires historian reconciliation and scheduled-run infrastructure',code.replace('SearchMode.GOLDEN_SECTION_SCORE','SearchMode.BINARY_FEASIBILITY'))
    if n in (70,71):
        return (' pattern: requires calibrated gas-lift well models and allocation callbacks',code)
    if n==72:
        return code.replace('summary = process.getCapacityUtilizationSummary()',
            'summary = {str(unit.getName()): float(unit.getCapacityUtilization())\n               for unit in process.getUnitOperations()}')
    if n==74:
        return 'config = (OptimizationConfig(50000.0, 300000.0).rateUnit("kg/hr")\n          .searchMode(SearchMode.BINARY_FEASIBILITY).maxIterations(25))\noptimizer = ProductionOptimizer()\n'+code
    if n==75:
        return code.replace('gain_kghr / 150.0', 'gain_kghr * 24.0 / (850.0 * 0.158987294928)').replace(
            '# approximate conversion','# illustrative liquid density 850 kg/m3').replace(
            'payback = cost / revenue_musd_yr', 'exchange_rate_nok_per_usd = 10.0  # explicit scenario assumption\n    payback = cost / (revenue_musd_yr * exchange_rate_nok_per_usd)')
    if n in (76,77,78):
        return (' pattern: requires a fully defined flare driver and emissions model',code)
    return None
for n,m in reversed(list(enumerate(matches,1))):
    v=fix(n,m[1],m[3])
    if v is None: continue
    note,code=v if isinstance(v,tuple) else (m[2],v)
    prefix=''
    if 'pattern:' in note:
        prefix='**Execution scope:** This integration pattern '+note.split('pattern:',1)[1].strip()+'.\n\n'
    text=text[:m.start()]+prefix+f'```{m[1]}{note}\n{code.rstrip()}\n```'+text[m.end():]
text=text.replace('Export to Eclipse VFP Format','Export Process Screening Diagnostics')
text=text.replace('### 24.13.4 Operating Range from Surge and Stonewall','### 24.13.4 Operating Range and Chart Basis')
p.write_text(text,encoding='utf-8')
