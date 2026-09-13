"""Repairs based on first execution across advanced chapters."""
from pathlib import Path
import re
BOOK = Path(__file__).resolve().parents[1]
PAT = re.compile(r"^```(python|java)([^\n]*)\n(.*?)^```", re.M | re.S)

def apply(number, callback):
    path = next((BOOK / "chapters").glob(f"ch{number:02d}_*/chapter.md"))
    text = path.read_text(encoding="utf-8-sig")
    matches = list(PAT.finditer(text))
    for n, m in reversed(list(enumerate(matches, 1))):
        result = callback(n, m[1], m[3])
        if result is None:
            continue
        annotation, code = result if isinstance(result, tuple) else (m[2], result)
        text = text[:m.start()] + f"```{m[1]}{annotation}\n{code.rstrip()}\n```" + text[m.end():]
    path.write_text(text, encoding="utf-8")

def ch25(n, language, code):
    if n == 1:
        setup = '''# Small, fully specified model for the following monitoring queries.
import jpype
jneqsim = jpype.JPackage("neqsim")
fluid = jneqsim.thermo.system.SystemSrkEos(333.15, 60.0)
fluid.addComponent("methane", 0.75)
fluid.addComponent("n-heptane", 0.25)
fluid.setMixingRule("classic")
feed = jneqsim.process.equipment.stream.Stream("Well fluid", fluid)
feed.setFlowRate(50000.0, "kg/hr")
separator = jneqsim.process.equipment.separator.Separator("HP separator", feed)
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(separator)
process.run()
separator.autoSize(1.2)
'''
        return setup + code.replace('constraint.getCurrentValue() / constraint.getMaxValue()', 'constraint.getUtilization()')
    if n == 3:
        return (' pattern: requires caller historian connection and tag mapping', code)
    if n == 5:
        code = code.replace('HeatExchanger = jneqsim.process.equipment.heatexchanger.HeatExchanger', 'Cooler = jneqsim.process.equipment.heatexchanger.Cooler')
        code = code.replace('gas_cooler = HeatExchanger("Gas cooler")\ngas_cooler.setFeedStream(0, hp_sep.getGasOutStream())',
                            'gas_cooler = Cooler("Gas cooler", hp_sep.getGasOutStream())\ngas_cooler.setOutTemperature(313.15)')
        code = code.replace('export_comp.setOutletPressure(150.0, "bara")',
                            'export_comp.setOutletPressure(150.0, "bara")\nexport_comp.setUsePolytropicCalc(True)\nexport_comp.setPolytropicEfficiency(0.78)')
        code = code.replace('unit.autoSize()', 'unit.autoSize(1.2)')
        code = code.replace('unit.enableConstraints()', 'unit.enableAllConstraints()')
        code = code.replace('utilization = process.getCapacityUtilizationSummary()',
                            'utilization = {str(unit.getName()): float(unit.getCapacityUtilization())\n               for unit in process.getUnitOperations()}')
        return code
    if n == 8:
        return code.replace('constraint.getCurrentValue() / constraint.getMaxValue()', 'constraint.getUtilization()')
    if n == 12:
        return code.replace('comp = process.getUnit("Export compressor")', 'comp = export_comp').replace(
            'comp.getOutletPressure() / comp.getInletPressure()', 'comp.getOutletStream().getPressure("bara") / comp.getInletStream().getPressure("bara")')
    if n == 13:
        return code.replace('hx = process.getUnit("Gas cooler")', 'hx = gas_cooler')
    if n == 14:
        code = code.replace('pipe = process.getUnit("Export pipeline")', '''pipe = PipeBeggsAndBrills("Export pipeline", export_comp.getOutletStream())
pipe.setLength(10000.0)  # m
pipe.setDiameter(0.5)   # m
pipe.setNumberOfIncrements(10)
pipe.run()''')
        return code.replace('pipe.getInletPressure()', 'pipe.getInletStream().getPressure("bara")').replace(
            'pipe.getOutletPressure()', 'pipe.getOutletStream().getPressure("bara")').replace(
            'pipe.getSuperficialVelocity()', 'pipe.getOutletStream().getFlowRate("m3/sec") / (3.141592653589793 * 0.5**2 / 4)')

def ch27(n, language, code):
    if n == 1:
        code = code.replace('ProductionOptimizer.OptimizationConfig.builder().build()',
                            '(ProductionOptimizer.OptimizationConfig(30000.0, 120000.0)\n              .rateUnit("kg/hr").maxIterations(20)\n              .searchMode(ProductionOptimizer.SearchMode.BINARY_FEASIBILITY))')
        return code.replace('name, process, feed, config, prob', 'name, process, feed, config, None, None').replace('{req.name}', '{req.getName()}')
    if n == 2:
        return '''# Scenario probabilities are study metadata, not constructor arguments.
optimizer = ProductionOptimizer()
comparison = optimizer.compareScenarios(
    jpype.java.util.ArrayList(scenario_requests),
    jpype.java.util.ArrayList([ProductionOptimizer.ScenarioKpi.optimalRate("kg/hr")]))
print(str(comparison))'''
    if n == 6:
        return '''RobustOptimizationStudy = jneqsim.process.optimization.valuechain.RobustOptimizationStudy
study = RobustOptimizationStudy()
for inputs in ([3.0, 0.85, 250.0], [2.2, 0.78, 240.0], [3.8, 0.90, 255.0]):
    study.addScenario(inputs)
study.setRequiredConfidence(0.90)
# Explicit algebraic toy evaluator demonstrates the uncertainty API.
def scenario_value(decision, scenario):
    rate = float(decision[0])
    return RobustOptimizationStudy.ScenarioOutcome(
        rate * scenario[0] * scenario[1], rate <= scenario[2])
result = study.evaluateDecision([200.0], scenario_value)
print(result.getP10(), result.getP50(), result.getP90(), result.getFeasibleFraction())'''
    if n == 7:
        return '''ParallelSweep = jneqsim.process.optimization.valuechain.ParallelSweep
sweep = ParallelSweep().setParallelism(2)
scenario_inputs = jpype.java.util.ArrayList()
for pressure in (40.0, 60.0, 80.0):
    scenario_inputs.add(jpype.JArray(jpype.JDouble)([pressure]))
# A serialization-only toy example. Each real simulation worker must build its own model.
outputs = sweep.run(scenario_inputs, lambda inputs: jpype.JDouble(inputs[0] * 2.0))
print(list(outputs))'''
    if n == 8:
        return code.replace('n_mc = 500', 'n_mc = 1000\nrng = np.random.default_rng(42)').replace(
            'np.random.triangular', 'rng.triangular').replace('plateau_rate * 0.3  # ramp-up', 'min(plateau_rate * 0.3, recoverable)  # ramp-up, resource capped')

def ch29(n, language, code):
    # Measurement constructors take material streams, whereas the level transmitter takes a separator.
    code = re.sub(r'((?:Pressure|Temperature)Transmitter\("[^"]+", )(sep|vessel)(\))', r'\1\2.getGasOutStream()\3', code)
    code = re.sub(r'((?:LT100|LT|LT_sep)\.setUnit\()"m"\)', r'\1"")', code)
    # The transmitter reports percent of its calibrated range, not metres.
    code = code.replace('LC100.setControllerSetPoint(1.2)', 'LC100.setControllerSetPoint(48.0)')
    code = code.replace('LC.setControllerSetPoint(1.0)', 'LC.setControllerSetPoint(33.3333333333)')
    code = code.replace('level_arr[i] = LT100.getMeasuredValue()', 'level_arr[i] = sep.getLiquidLevel() * sep.getInternalDiameter()')
    code = code.replace('level_s[i] = LT.getMeasuredValue()', 'level_s[i] = sep.getLiquidLevel() * sep.getInternalDiameter()')
    code = code.replace('LT100.getMeasuredValue():.2f} m', 'sep.getLiquidLevel() * sep.getInternalDiameter():.2f} m')
    code = code.replace("y=6.9, color='r', linestyle='--', label='Target (6.9 barg)'", "y=7.91325, color='r', linestyle='--', label='Illustrative target (6.9 barg)'")
    return code

def ch30(n, language, code):
    if n in (2, 3, 4):
        return (' pattern: requires authenticated historian and site tag configuration', code)
    if n == 7:
        return (' pattern: requires reader calibrator optimizer and writer callbacks', code)
    if n == 8:
        return (' pattern: requires caller calibration dataset and scikit-learn', code)
    if n == 13:
        return code.replace('# ... add separation equipment ...', 'separation.add(feed)\nseparation.add(sep)').replace(
            '# ... add compression equipment ...', 'compression.add(comp)')
    if n == 20:
        code = code.replace('auto.setVariableValue("HP Separator.pressure", P, "bara")',
                            'auto.setVariableValue("Feed.pressure", P, "bara")')
        code = code.replace('json.loads(str(liq_flow_json)).get("value", 0)', 'json.loads(str(liq_flow_json))["value"]')
        code = code.replace('json.loads(str(power_json)).get("value", 0)', 'json.loads(str(power_json))["value"]')
        return code.replace('    return {\n        "optimal_pressure"',
                            '    auto.setVariableValue("Feed.pressure", best["pressure_bara"], "bara")\n    process.run()\n    return {\n        "optimal_pressure"')
    if n == 22:
        return (' pattern: requires caller run_neqsim_model and output schema', code)
    if n == 23:
        return (' pattern: requires the five fully configured plant-area models', code)
    if n == 29:
        return code.replace('compressed = state_v2.toCompressedBytes()',
                            'import gzip\ncompressed = gzip.compress(str(state_v2.toJson()).encode("utf-8"))').replace(
            'ProcessSystemState.fromCompressedBytes(compressed)', 'ProcessSystemState.fromJson(gzip.decompress(compressed).decode("utf-8"))')

apply(25, ch25)
apply(27, ch27)
apply(29, ch29)
apply(30, ch30)

# Basic current API and presentation corrections throughout the owned range.
for chapter in (BOOK / "chapters").glob("ch*"):
    if not 19 <= int(chapter.name[2:4]) <= 35:
        continue
    path = chapter / "chapter.md"
    text = path.read_text(encoding="utf-8-sig")
    text = re.sub(r'(\b(?:comp|compressor)\.)setUseCompressorChart\(', r'\1getCompressorChart().setUseCompressorChart(', text)
    text = text.replace('jneqsim.process.fielddevelopment.integrated.NetworkAllocationOptimizer', 'jneqsim.process.optimization.valuechain.NetworkAllocationOptimizer')
    # Tag ASCII diagrams/output without changing executable language fences.
    lines, inside = text.splitlines(), False
    for i, line in enumerate(lines):
        if line.startswith('```'):
            if not inside and line.strip() == '```':
                lines[i] = '```text'
            inside = not inside
    path.write_text('\n'.join(lines) + '\n', encoding="utf-8")
