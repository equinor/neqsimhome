"""Current Java APIs for advanced methods, with honest data-dependent boundaries."""
from pathlib import Path
import re,ast
B=Path(__file__).resolve().parents[1]
tree=ast.parse((B/'devtools/repair_optimization_java_examples.py').read_text())
fixture=next(ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='fixture' for t in node.targets))
p=next((B/'chapters').glob('ch32*/chapter.md'));text=p.read_text(encoding='utf-8-sig')
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
new={
1:fixture+'''ProductionOptimizer optimizer = new ProductionOptimizer();
List<OptimizationObjective> objectives = Arrays.asList(
    new OptimizationObjective("production", proc -> ((StreamInterface) proc.getUnit("Feed")).getFlowRate("kg/hr"), 1.0, ObjectiveType.MAXIMIZE),
    new OptimizationObjective("power", proc -> ((Compressor) proc.getUnit("Compressor")).getPower("kW"), 1.0, ObjectiveType.MINIMIZE));
OptimizationConfig config = new OptimizationConfig(50000.0,200000.0).rateUnit("kg/hr").maxIterations(20).paretoGridSize(5);
ParetoResult pareto = optimizer.optimizePareto(process, feed, config, objectives, Collections.emptyList());
List<ParetoPoint> front = pareto.getParetoFront();
logger.info("Non-dominated sampled points: {}", front.size());
// Selection from this set requires an explicit operational/economic preference.''',
5:'''ProcessSimulationEvaluator evaluator = new ProcessSimulationEvaluator(process);
evaluator.addParameterWithSetter("flow", (proc, value) -> ((StreamInterface) proc.getUnit("Feed")).setFlowRate(value,"kg/hr"), 50000.0,200000.0,"kg/hr");
evaluator.addParameterWithSetter("suction", (proc, value) -> ((StreamInterface) proc.getUnit("Feed")).setPressure(value,"bara"), 40.0,80.0,"bara");
evaluator.addObjective("production", proc -> ((StreamInterface) proc.getUnit("Feed")).getFlowRate("kg/hr"), ProcessSimulationEvaluator.ObjectiveDefinition.Direction.MAXIMIZE);
evaluator.addConstraintUpperBound("power", proc -> ((Compressor) proc.getUnit("Compressor")).getPower("kW"),5000.0);
double[] x = {100000.0,60.0};
ProcessSimulationEvaluator.EvaluationResult result = evaluator.evaluate(x);
logger.info("Objective {}, feasible {}, converged {}", result.getObjective(),result.isFeasible(),result.isSimulationConverged());''',
8:'''evaluator.setFiniteDifferenceStep(0.001);
evaluator.setUseRelativeStep(true);
double[] gradient = evaluator.estimateGradient(x);
logger.info("Forward finite-difference objective gradient: {}", Arrays.toString(gradient));''',
10:'''Map<String,Object> definition = evaluator.getProblemDefinition();
String json = new com.google.gson.GsonBuilder().setPrettyPrinting().create().toJson(definition);
logger.info("Problem definition: {}",json);''',
11:'''import neqsim.process.util.reconciliation.*;
SteadyStateDetector detector = new SteadyStateDetector();
SteadyStateVariable pressure = detector.addVariable("Pressure").setUnit("bara");
for (int index=0; index<60; index++) { pressure.addValue(60.0); }
SteadyStateResult steady = detector.evaluate();
logger.info("Synthetic constant signal steady: {}; R-statistic {}", steady.isAtSteadyState(),pressure.getRStatistic());
// Site signals require timestamps, quality flags, a declared window and tolerances.''',
12:'''DataReconciliationEngine engine = new DataReconciliationEngine();
// Synthetic readings and one-standard-deviation uncertainties, all kg/hr.
engine.addVariable(new ReconciliationVariable("Feed",100000.0,2000.0));
engine.addVariable(new ReconciliationVariable("Gas",70000.0,1500.0));
engine.addVariable(new ReconciliationVariable("Oil",28000.0,1000.0));
engine.addVariable(new ReconciliationVariable("Water",5000.0,500.0));
engine.addConstraint(new double[]{1.0,-1.0,-1.0,-1.0},"Mass balance");
ReconciliationResult reconciled = engine.reconcile();
if (!reconciled.isConverged()) { throw new IllegalStateException(reconciled.getErrorMessage()); }
logger.info("Reconciled feed {} kg/hr; residuals {}", engine.getVariable("Feed").getReconciledValue(),Arrays.toString(reconciled.getConstraintResidualsAfter()));''',
13:'''logger.info("Global test passed: {}",reconciled.isGlobalTestPassed());
for (ReconciliationVariable suspect : reconciled.getGrossErrors()) {
    logger.warn("Suspect {} normalized residual {}",suspect.getName(),suspect.getNormalizedResidual());
}''',
16:'''BatchStudy study = BatchStudy.builder(process)
    .vary("Feed.flowRate",50000.0,200000.0,4)
    .vary("Compressor.outletPressure",120.0,200.0,3)
    .addObjective("flow",BatchStudy.Objective.MAXIMIZE, proc -> ((StreamInterface) proc.getUnit("Feed")).getFlowRate("kg/hr"))
    .addObjective("power",BatchStudy.Objective.MINIMIZE, proc -> ((Compressor) proc.getUnit("Compressor")).getPower("kW"))
    .parallelism(1).name("Compression envelope").build();
BatchStudy.BatchStudyResult batch = study.run();
if (batch.getFailureCount()!=0) { throw new IllegalStateException(batch.getSummary()); }
logger.info("Cases run {}",batch.getTotalCases());''',
17:'''List<BatchStudy.CaseResult> nonDominated = batch.getParetoFront("flow","power");
for (BatchStudy.CaseResult candidate : nonDominated) {
    logger.info("Parameters {} objectives {}",candidate.parameters.values,candidate.objectiveValues);
}
// Non-dominated candidates have no unique preference rank without a decision rule.''',
18:'''double[] powers = batch.getSuccessfulResults().stream().mapToDouble(candidate -> candidate.objectiveValues.get("power")).toArray();
java.util.DoubleSummaryStatistics statistics = Arrays.stream(powers).summaryStatistics();
logger.info("Design-grid power minimum {}, mean {}, maximum {} kW",statistics.getMin(),statistics.getAverage(),statistics.getMax());
// These equally weighted design points are not a probability distribution or a P10/P90 reserve assessment.'''
}
for n,m in reversed(list(enumerate(PAT.finditer(text),1))):
 code=new.get(n,m[3]);annotation=m[2];lead=''
 if n==7:
  annotation=' pattern: optional NLopt package is required'
  code=code.replace('result = evaluator.evaluate(x)\n        return -float(result.getObjective())','return penalty_objective(x)')
  code=code.replace('[30.0, 100.0]','[0.5, 0.8]').replace('[120.0, 200.0]','[2.0, 1.6]').replace('[60.0, 150.0]','[1.0, 1.0]')
 if n==14:annotation=' pattern: requires calibration observations, current estimator adapters and an identifiability study'
 if n==20:
  code=code.replace('# Create well fluids (different GOR and water cut)', '# Declared feed compositions; the labels below do not recombine an exact stock-tank GOR/water cut.')
  code=code.replace('# Optimize choke pressures to maximize total oil production', '# Demonstrate why fixed feed rates cannot identify a production-maximizing choke pressure.')
  code=code.replace('total_oil_production','fixed_feed_throughput').replace('Optimal choke outlet pressures:', 'Numerically selected choke pressures for a constant mass-flow objective:')
  code+='\nassert abs(-result.fun - 150000.0) < 1.0\nprint("No production optimum is identified: all three feed rates were prescribed.")\n# Couple calibrated WellFlow inflow and tubing hydraulics before optimizing deliverability.\n'
 if n==21:code=code.replace('# Gas lift performance curves for each well (from simulation)', '# Synthetic analytic gas-lift response curves; not NeqSim well simulation results.')
 if n==22:annotation=' pattern: conceptual adapter requiring trained ONNX model, stream fields, domain checks and conservation implementation'
 if 'pattern:' in annotation and 'pattern' not in m[2]:lead=f'**Execution scope:** {annotation.split("pattern:",1)[1].strip()}.\n\n'
 text=text[:m.start()]+lead+'```'+m[1]+annotation+'\n'+code.rstrip()+'\n```'+text[m.end():]
p.write_text(text,encoding='utf-8')
