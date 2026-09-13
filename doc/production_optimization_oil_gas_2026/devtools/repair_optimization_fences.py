"""Targeted repairs from actual fence execution, preserving teaching objectives."""
from pathlib import Path
import re
BOOK = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"^```(python|java)([^\n]*)\n(.*?)^```", re.M | re.S)

def change(number, function):
    path = next((BOOK / "chapters").glob(f"ch{number:02d}_*/chapter.md"))
    text = path.read_text(encoding="utf-8")
    matches = list(PATTERN.finditer(text))
    for index, match in reversed(list(enumerate(matches, 1))):
        code = function(index, match[1], match[3])
        if code is not None:
            text = text[:match.start(3)] + code.rstrip() + "\n" + text[match.end(3):]
    path.write_text(text, encoding="utf-8")

def ch23(n, lang, code):
    if n == 1:
        code = code.replace('compressor = Compressor("export compressor", separator.getGasOutStream())',
                            'compressor = Compressor("export compressor", separator.getGasOutStream())\ncompressor.setOutletPressure(150.0, "bara")\ncompressor.setUsePolytropicCalc(True)\ncompressor.setPolytropicEfficiency(0.78)\nexport = Stream("export", compressor.getOutletStream())')
        code = code.replace('process.add(compressor)', 'process.add(compressor)\nprocess.add(export)')
        return code
    if n == 3:
        return '''ProcessModel = jneqsim.process.processmodel.ProcessModel
# Reuse the solved equipment in explicitly named areas for this example.
separation_system = ProcessSystem()
separation_system.add(feed)
separation_system.add(separator)
compression_system = ProcessSystem()
compression_system.add(compressor)
export_system = ProcessSystem()
export_system.add(export)
plant = ProcessModel()
plant.add("Separation", separation_system)
plant.add("Compression", compression_system)
plant.add("Export", export_system)
plant.run()'''
    if n == 10:
        return '''import json
auto = ProcessAutomation(plant)
# Explicit Java collections avoid ambiguous JPype overload resolution.
setpoints = jpype.java.util.LinkedHashMap()
setpoints.put("Compression::export compressor.outletPressure", 150.0)
readbacks = jpype.java.util.ArrayList()
readbacks.add("Compression::export compressor.power")
evaluation = json.loads(str(auto.evaluate(
    setpoints, "bara", readbacks, "kW", 30, 5.0e-3)))
print(json.dumps(evaluation, indent=2))'''
    if n == 11:
        return '''# A synthetic sizing demonstration for the equipment built above.
separator.autoSize(1.2)
compressor.autoSize(1.2)
# Preserve the resulting ratings, but use fixed outlet pressure in later searches.
compressor.setUseCompressorChart(False)
print("Separator constraints:", list(separator.getCapacityConstraints().keySet()))
print("Compressor constraints:", list(compressor.getCapacityConstraints().keySet()))'''
    if n == 12:
        return '''# Presets are equipment-specific; discover the available constraint names.
separator.useEquinorConstraints()
print(list(separator.getCapacityConstraints().keySet()))
# Installed, approved ratings must replace synthetic presets in plant studies.'''
    if n == 13:
        return '''separator.enableAllConstraints()
separator.disableAllConstraints()
separator.setCapacityAnalysisEnabled(False)
constraints = separator.getCapacityConstraints()
constraints["gasLoadFactor"].setEnabled(True)
# Restore declared scope after demonstrating disablement.
separator.setCapacityAnalysisEnabled(True)
separator.enableAllConstraints()'''
    if n in (14, 15):
        return code.replace('SearchMode.GOLDEN_SECTION_SCORE', 'SearchMode.BINARY_FEASIBILITY').replace(
            'result.getBottleneck().getName()', '(result.getBottleneck().getName() if result.getBottleneck() else "none")')
    if n == 16:
        code = code.replace('variables = [', 'variables = jpype.java.util.ArrayList([').replace('\n]\n', '\n])\n')
        code = code.replace('result = optimizer.optimize(process, variables, config, objectives, constraints)', '''OptimizationObjective = ProductionOptimizer.OptimizationObjective
ObjectiveType = ProductionOptimizer.ObjectiveType
objectives = jpype.java.util.ArrayList()
objectives.add(OptimizationObjective("throughput",
    lambda proc: proc.getUnit("feed").getFlowRate("kg/hr"),
    1.0, ObjectiveType.MAXIMIZE))
result = optimizer.optimize(process, variables, config, objectives, None)''')
        return code
    if n == 22:
        return '''# Synthetic electrically driven export-gas case.
# Emissions intensity is an explicit scenario assumption, not a plant measurement.
gas_throughput = OptimizationObjective("gas_export",
    lambda proc: proc.getUnit("export").getFlowRate("kg/hr"),
    1.0, ObjectiveType.MAXIMIZE)
def calculate_emissions(proc):
    power_kW = proc.getUnit("export compressor").getPower("kW")
    return power_kW * 8760.0 * 0.10 / 1000.0  # t CO2/year, 0.10 kg/kWh
co2_limit = OptimizationConstraint.lessThan("co2_emissions",
    calculate_emissions, 50000.0, ConstraintSeverity.HARD, 200.0,
    "Illustrative annual electricity-related CO2 budget")
objectives = jpype.java.util.ArrayList([gas_throughput])
extra_constraints = jpype.java.util.ArrayList([co2_limit])
config = (OptimizationConfig(50000.0, 200000.0)
          .rateUnit("kg/hr").maxIterations(30)
          .searchMode(SearchMode.GOLDEN_SECTION_SCORE))
result = optimizer.optimize(process, feed, config, objectives, extra_constraints)
print(result.isFeasible(), result.getOptimalRate(), calculate_emissions(process))'''
    if n == 23:
        return '''objectives = jpype.java.util.ArrayList([gas_throughput, power_obj])
config.paretoGridSize(5)
pareto_result = optimizer.optimizePareto(process, feed, config,
    objectives, jpype.java.util.ArrayList([power_limit]))
for point in pareto_result.getParetoFront():
    values = point.getObjectiveValues()
    print("Gas (kg/hr):", values["gas_export"], "Power (kW):", values["power"])'''
    if n == 25:
        return '''engine.setFeedStreamName("feed")
engine.setOutletStreamName("export")
inlet_pressure, outlet_pressure = 60.0, 150.0  # bara
min_flow, max_flow = 50000.0, 200000.0          # kg/hr
engine_result = engine.findMaximumThroughput(
    inlet_pressure, outlet_pressure, min_flow, max_flow)
print(f"Maximum throughput: {engine_result.getOptimalValue():.0f} kg/hr")
# Replay explicitly for this engine before reading equipment outputs.
feed.setFlowRate(engine_result.getOptimalValue(), "kg/hr")
process.run()'''
    if n == 26:
        return '''report = engine.evaluateAllConstraints()
for item in report.getEquipmentStatuses():
    print(item.getEquipmentName(), item.getBottleneckConstraint(),
          item.getUtilization(), item.isWithinLimits())'''
    if n == 27:
        return '''sensitivity = engine.analyzeSensitivity(
    engine_result.getOptimalValue(), inlet_pressure, outlet_pressure)
print(str(sensitivity))'''
    if n == 28:
        return '''pressures = jpype.JArray(jpype.JDouble)([50.0, 60.0, 70.0])  # bara
temperatures = jpype.JArray(jpype.JDouble)([298.15])  # K
# Fixed composition and mass-flow basis; this is not a well VFP table.
capacity_table = engine.generateCapacityScreening(
    pressures, temperatures, 150.0, 50000.0, 200000.0)
print(capacity_table.toDiagnosticTable())'''
    if n == 34:
        return code.replace('opt.addConstraintLessOrEqual("Export Oil.RVP", 0.79, "bara", 1.0e4)',
            'opt.addConstraintLessOrEqual("Compression::export compressor.power", 15000.0, "kW", 1.0e4)')
    if n == 37:
        return code.replace('bottleneck.getName()', '(bottleneck.getName() if bottleneck else "none")')
    if n == 39:
        return '''# Address-based evaluator for external Python optimizers.
auto = ProcessAutomation(process)
def evaluate_external(flow_kghr, pressure_bara):
    points = jpype.java.util.LinkedHashMap()
    # Mixed units: default flow is kg/hr and pressure is bara.
    points.put("feed.flowRate", float(flow_kghr))
    points.put("export compressor.outletPressure", float(pressure_bara))
    outputs = jpype.java.util.ArrayList(["export compressor.power"])
    return json.loads(str(auto.evaluate(points, None, outputs, "kW", 30, 5e-3)))
print(evaluate_external(100000.0, 150.0))'''

change(23, ch23)

def basic(n, lang, code):
    code = code.replace('getLimitingConstraintName()', 'getConstraintName()')
    code = code.replace('getEquipmentNearCapacityLimit(0.9)', 'getEquipmentNearCapacityLimit()')
    code = code.replace('getEquipmentNearCapacityLimit(0.90)', 'getEquipmentNearCapacityLimit()')
    if lang == "python" and ('savefig("figures/' in code or "savefig('figures/" in code):
        code = 'from pathlib import Path\nPath("figures").mkdir(parents=True, exist_ok=True)\n' + code
    return code

for number in range(19, 36):
    change(number, basic)
