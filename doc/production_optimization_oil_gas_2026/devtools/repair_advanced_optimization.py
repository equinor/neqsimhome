"""Replace obsolete advanced API examples with solved current-source workflows."""
from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
p=next((B/'chapters').glob('ch32*/chapter.md')); text=p.read_text(encoding='utf-8-sig')
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
new={
2:'''from pathlib import Path
Path("figures").mkdir(parents=True, exist_ok=True)
import jpype
import numpy as np
import matplotlib.pyplot as plt
jneqsim = jpype.JPackage("neqsim")
fluid = jneqsim.thermo.system.SystemSrkEos(313.15, 50.0)
fluid.addComponent("methane", 0.90)
fluid.addComponent("ethane", 0.10)
fluid.setMixingRule("classic")
feed = jneqsim.process.equipment.stream.Stream("Feed", fluid)
feed.setFlowRate(100000.0, "kg/hr")
compressor = jneqsim.process.equipment.compressor.Compressor("Compressor", feed)
compressor.setOutletPressure(150.0, "bara")
compressor.setPolytropicEfficiency(0.78)
compressor.setUsePolytropicCalc(True)
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(compressor)
process.run()
ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer
OptimizationConfig = ProductionOptimizer.OptimizationConfig
Objective = ProductionOptimizer.OptimizationObjective
Direction = ProductionOptimizer.ObjectiveType
optimizer = ProductionOptimizer()
objectives = jpype.java.util.ArrayList([
    Objective("production", lambda proc: proc.getUnit("Feed").getFlowRate("kg/hr"),
              1.0, Direction.MAXIMIZE),
    Objective("power", lambda proc: proc.getUnit("Compressor").getPower("kW"),
              1.0, Direction.MINIMIZE)])
config = (OptimizationConfig(50000.0, 200000.0).rateUnit("kg/hr")
          .maxIterations(20).paretoGridSize(7))
pareto = optimizer.optimizePareto(process, feed, config, objectives, None)
front = pareto.getParetoFront()
production = [float(p.getObjectiveValues()["production"]) for p in front]
power = [float(p.getObjectiveValues()["power"]) for p in front]
plt.figure(figsize=(7, 4))
plt.scatter(production, power)
plt.xlabel("Feed flow (kg/hr)")
plt.ylabel("Compressor power (kW)")
plt.title("Sampled non-dominated process states")
plt.grid(True, alpha=0.3)
plt.savefig("figures/pareto_front.png", dpi=150, bbox_inches="tight")
print("Non-dominated points:", len(front))''',
4:'''SQPoptimizer = jneqsim.process.util.optimizer.SQPoptimizer
# Dimensionless decisions: flow / 100000 kg/hr and suction pressure / 50 bara.
def solved_state(x):
    feed.setFlowRate(float(x[0]) * 100000.0, "kg/hr")
    feed.setPressure(float(x[1]) * 50.0, "bara")
    compressor.setOutletPressure(150.0, "bara")
    process.run()
    return float(compressor.getPower("kW"))

def production_objective(x):
    solved_state(x)
    return -float(x[0])

def power_margin(x):
    return (5000.0 - solved_state(x)) / 5000.0

sqp = SQPoptimizer(2)
sqp.setObjectiveFunction(production_objective)
sqp.addInequalityConstraint(power_margin)
sqp.setVariableBounds([0.5, 0.8], [2.0, 1.6])
sqp.setInitialPoint([1.0, 1.0])
sqp.setMaxIterations(60)
result = sqp.solve()
selected = result.getOptimalPoint()
final_power = solved_state(selected)
print("SQP converged:", result.isConverged(), "KKT residual:", result.getKktError())
print("Final flow (kg/hr):", feed.getFlowRate("kg/hr"), "power (kW):", final_power)
assert np.isfinite(final_power) and final_power <= 5000.0 + 1.0
# Check convergence and the physical residual before accepting a deployment decision.''',
6:'''from scipy.optimize import minimize, differential_evolution
# The address-based automation facade applies inputs and solves before extraction.
import json
auto = process.getAutomation()
def evaluate_state(x):
    inputs = jpype.java.util.LinkedHashMap()
    inputs.put("Feed.flowRate", float(x[0]) * 100000.0)
    inputs.put("Feed.pressure", float(x[1]) * 50.0)
    requested = jpype.java.util.ArrayList(["Compressor.power"])
    report = json.loads(str(auto.evaluate(inputs, None, requested, "kW", 30, 0.005)))
    power = float(compressor.getPower("kW"))
    if not np.isfinite(power):
        raise RuntimeError("Non-finite compressor power")
    return power

def penalty_objective(x):
    return -float(x[0]) + 100.0 * max(0.0, (evaluate_state(x) - 5000.0) / 5000.0)

bounds = [(0.5, 2.0), (0.8, 1.6)]
res_lbfgsb = minimize(penalty_objective, [1.0, 1.0], method="L-BFGS-B", bounds=bounds)
res_de = differential_evolution(penalty_objective, bounds, seed=42, maxiter=20, popsize=5)
res_slsqp = minimize(lambda x: -float(x[0]), [1.0, 1.0], method="SLSQP", bounds=bounds,
    constraints={"type": "ineq", "fun": lambda x: (5000.0-evaluate_state(x))/5000.0})
for name, answer in [("L-BFGS-B", res_lbfgsb), ("DE", res_de), ("SLSQP", res_slsqp)]:
    power = evaluate_state(answer.x)  # full-model replay at each reported answer
    print(name, "success=", answer.success, "flow kg/hr=", answer.x[0]*100000.0,
          "power kW=", power, "power-feasible=", power <= 5001.0)''',
9:'''from scipy.interpolate import RBFInterpolator
from scipy.stats.qmc import LatinHypercube
sampler = LatinHypercube(d=2, seed=42)
limits = np.array(bounds)
X = sampler.random(n=20) * (limits[:, 1]-limits[:, 0]) + limits[:, 0]
Y = np.array([evaluate_state(x) for x in X])
# Thin-plate spline avoids an arbitrary multiquadric shape parameter.
rbf = RBFInterpolator(X, Y, kernel="thin_plate_spline")
res = minimize(lambda x: -float(x[0]), [1.0, 1.0], method="SLSQP", bounds=bounds,
    constraints={"type": "ineq", "fun": lambda x: (5000.0-float(rbf(np.asarray(x)[None,:])[0]))/5000.0})
predicted = float(rbf(res.x[None,:])[0])
actual = evaluate_state(res.x)
print("Surrogate candidate flow kg/hr:", res.x[0]*100000.0)
print("Predicted/actual power kW:", predicted, actual)
print("Accepted power constraint:", actual <= 5001.0)
# A failed full-model check triggers more samples and another search.''',
19:'''BatchStudy = jneqsim.process.util.optimizer.BatchStudy
study = (BatchStudy.builder(process)
    .vary("Feed.flowRate", 50000.0, 200000.0, 4)
    .vary("Compressor.outletPressure", 120.0, 200.0, 3)
    .addObjective("power_kW", BatchStudy.Objective.MINIMIZE,
                  lambda case: float(case.getUnit("Compressor").getPower("kW")))
    .parallelism(1).name("Compression envelope").build())
results = study.run()
assert results.getFailureCount() == 0
print(results.getSummary())
cases = results.getSuccessfulResults()
flows = [float(case.parameters.values["Feed.flowRate"]) for case in cases]
pressures = [float(case.parameters.values["Compressor.outletPressure"]) for case in cases]
powers = [float(case.objectiveValues["power_kW"]) for case in cases]
plt.figure(figsize=(7, 4))
plt.scatter(flows, pressures, c=powers, s=100)
plt.xlabel("Feed flow (kg/hr)")
plt.ylabel("Compressor discharge pressure (bara)")
plt.colorbar(label="Power (kW)")
plt.title("Full-model compression sweep")
plt.savefig("figures/batch_study_contours.png", dpi=150, bbox_inches="tight")'''
}
for n,m in reversed(list(enumerate(PAT.finditer(text),1))):
 code=new.get(n,m[3]); annotation=m[2]; lead=''
 if n==15:
  annotation=' pattern: requires measured time series, reconciler constraints and calibration data'
  code=code.replace('detector.isSteadyState()', 'detector.isAllSteadyState()')
 if n==23:
  code=code.replace('fielddevelopment.integrated', 'optimization.valuechain')
  code+='\nprint("Synthetic scenario net value NOK/day:", reward)'
  code='exportGasSm3PerDay, exportOilSm3PerDay, totalPowerKw = 1.0e6, 250.0, 5000.0\n# Declared synthetic scenario values; replace with solved process outputs.\n'+code
 if n==24:
  annotation=' pattern: requires a declared training design and a calibrated chart-equipped base process'
  code=code.replace('copy.deepcopy(base_process)', 'base_process.copy()').replace('process.getUnit("Separator").setPressure', 'process.getUnit("Feed").setPressure')
  code=code.replace('# Generate 10,000 samples using 8 threads', '# Execute the explicitly prepared sample list; independent Java copies per worker.')
 if 'pattern:' in annotation and 'pattern' not in m[2]:
  lead=f'**Execution scope:** {annotation.split("pattern:",1)[1].strip()}.\n\n'
 text=text[:m.start()]+lead+'```'+m[1]+annotation+'\n'+code.rstrip()+'\n```'+text[m.end():]
p.write_text(text,encoding='utf-8')
