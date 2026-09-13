"""Provide complete Java contexts and repair current optimization signatures."""
from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
def path(n):return next((B/'chapters').glob(f'ch{n:02d}*/chapter.md'))
fixture='''import neqsim.thermo.system.*;
import neqsim.process.processmodel.*;
import neqsim.process.equipment.stream.*;
import neqsim.process.equipment.separator.*;
import neqsim.process.equipment.compressor.*;
import neqsim.process.equipment.valve.*;
import neqsim.process.equipment.pipeline.*;
import neqsim.process.equipment.pump.*;
import neqsim.process.equipment.capacity.*;
import neqsim.process.util.optimizer.*;
import neqsim.process.util.optimizer.ProductionOptimizer.*;
import neqsim.process.automation.*;
import neqsim.process.processmodel.lifecycle.*;
import java.util.*;
import org.apache.logging.log4j.*;
Logger logger = LogManager.getLogger("ProductionBook");
SystemInterface gas = new SystemSrkEos(313.15, 60.0);
gas.addComponent("methane", 0.90);
gas.addComponent("ethane", 0.10);
gas.setMixingRule("classic");
Stream feed = new Stream("Feed", gas);
feed.setFlowRate(100000.0, "kg/hr");
Separator separator = new Separator("HP Sep", feed);
Compressor compressor = new Compressor("Compressor", separator.getGasOutStream());
compressor.setOutletPressure(150.0, "bara");
compressor.setPolytropicEfficiency(0.78);
ProcessSystem process = new ProcessSystem();
process.add(feed);
process.add(separator);
process.add(compressor);
process.run();
'''
fix24={
2:fixture+'''CapacityConstraint speedConstraint = new CapacityConstraint("speed", "RPM",
    CapacityConstraint.ConstraintType.HARD).setDesignValue(10000.0).setMaxValue(11000.0)
    .setWarningThreshold(0.9).setDescription("Declared demonstration speed limit")
    .setValueSupplier(() -> compressor.getSpeed());''',
4:'''for (ProcessEquipmentInterface equipment : process.getUnitOperations()) {
    equipment.enableConstraints();
}
// Repeat over each declared ProcessSystem when composing multiple areas.''',
9:'''ThrottlingValve valve = new ThrottlingValve("Example valve", feed);
valve.setOutletPressure(50.0);
valve.run();
valve.autoSize(1.2);''',
10:'''PipeBeggsAndBrills pipeline = new PipeBeggsAndBrills("Example pipe", feed);
pipeline.setLength(1000.0);
pipeline.setDiameter(0.25);
pipeline.setAngle(0.0);
pipeline.run();
pipeline.autoSize(1.2);''',
11:'''SystemInterface liquid = new SystemSrkEos(298.15, 5.0);
liquid.addComponent("n-heptane", 1.0);
liquid.setMixingRule("classic");
Stream pumpFeed = new Stream("Pump feed", liquid);
pumpFeed.setFlowRate(10000.0, "kg/hr");
pumpFeed.run();
Pump pump = new Pump("Example pump", pumpFeed);
pump.setOutletPressure(10.0);
pump.run();
pump.autoSize(1.2);''',
15:'''BottleneckResult capacityResult = process.findBottleneck();
logger.info("Bottleneck {} utilization {}", capacityResult.getEquipmentName(), capacityResult.getUtilization());
Map<String, Double> utilizationSummary = process.getCapacityUtilizationSummary();
List<String> nearLimit = process.getEquipmentNearCapacityLimit();
boolean anyOverloaded = process.isAnyEquipmentOverloaded();
boolean anyHardViolation = process.isAnyHardLimitExceeded();
List<neqsim.process.equipment.capacity.CapacityConstrainedEquipment> constrained = process.getConstrainedEquipment();''',
29:'''OptimizationSummary optimizationSummary = optimizer.optimizeSummary(process, feed, config, null, null);
logger.info("Maximum rate {} {}, limiting equipment {}, feasible {}",
    optimizationSummary.getMaxRate(), optimizationSummary.getRateUnit(),
    optimizationSummary.getLimitingEquipment(), optimizationSummary.isFeasible());''',
30:'''ProcessOptimizationEngine engine = new ProcessOptimizationEngine(process);
engine.setFeedStreamName("feed");
engine.setOutletStreamName("Export Comp");
ProcessOptimizationEngine.OptimizationResult engineResult = engine.findMaximumThroughput(65.0, 150.0, 50000.0, 300000.0);
ProcessOptimizationEngine.ConstraintReport report = engine.evaluateAllConstraints();
ProcessOptimizationEngine.SensitivityResult sens = engine.analyzeSensitivity(100000.0, 65.0, 150.0);
ProcessOptimizationEngine.LiftCurve curve = engine.generateCapacityScreening(new double[]{50.0,65.0,80.0},
    new double[]{343.15}, 150.0, 50000.0, 300000.0);
logger.info("Capacity screening points {}", curve.getPoints().size());''',
31:'''EquipmentCapacityStrategyRegistry registry = EquipmentCapacityStrategyRegistry.getInstance();
logger.info("Registered capacity strategies: {}", registry.getStrategyCount());
for (EquipmentCapacityStrategy strategy : registry.getAllStrategies()) {
    logger.info("Strategy {}", strategy.getClass().getSimpleName());
}''',
36:'''OptimizationObjective throughput = new OptimizationObjective("throughput",
    proc -> ((StreamInterface) proc.getUnit("feed")).getFlowRate("kg/hr"), 1.0, ObjectiveType.MAXIMIZE);
OptimizationObjective minPower = new OptimizationObjective("power",
    proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 0.3, ObjectiveType.MINIMIZE);
List<OptimizationObjective> objectives = Arrays.asList(throughput, minPower);''',
38:'''OptimizationConstraint maxPower = OptimizationConstraint.lessThan("compressor_power",
    proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 25.0,
    ProductionOptimizer.ConstraintSeverity.HARD, 100.0, "Declared power ceiling (MW)");
// Operating temperature is not a dew point; compute a separate property test for a dew-point specification.
OptimizationConstraint maxTemperature = OptimizationConstraint.lessThan("discharge_temperature",
    proc -> ((Compressor) proc.getUnit("Export Comp")).getOutletStream().getTemperature("C"), 180.0,
    ProductionOptimizer.ConstraintSeverity.SOFT, 10.0, "Illustrative discharge temperature preference");
List<OptimizationConstraint> constraints = Arrays.asList(maxPower, maxTemperature);''',
42:'''// Explicit separator outlets avoid invented export equipment names.
List<OptimizationObjective> threeObjectives = Arrays.asList(
    new OptimizationObjective("oil_rate", proc -> ((ThreePhaseSeparator) proc.getUnit("HP Sep")).getOilOutStream().getFlowRate("Sm3/day"), 1.0, ObjectiveType.MAXIMIZE),
    new OptimizationObjective("gas_rate", proc -> ((ThreePhaseSeparator) proc.getUnit("HP Sep")).getGasOutStream().getFlowRate("MSm3/day"), 1.0, ObjectiveType.MAXIMIZE),
    new OptimizationObjective("power", proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 1.0, ObjectiveType.MINIMIZE));
config.paretoGridSize(3).maxIterations(15);
ParetoResult threeObjectiveResult = optimizer.optimizePareto(process, feed, config, threeObjectives, constraints);''',
43:'''List<ScenarioRequest> scenarios = new ArrayList<ScenarioRequest>();
for (double pressure : new double[]{50.0, 65.0, 80.0}) {
    ProcessSystem scenarioProcess = process.copy();
    StreamInterface scenarioFeed = (StreamInterface) scenarioProcess.getUnit("feed");
    scenarioFeed.setPressure(pressure, "bara");
    OptimizationConfig scenarioConfig = new OptimizationConfig(50000.0, 300000.0)
        .rateUnit("kg/hr").maxIterations(20).searchMode(SearchMode.BINARY_FEASIBILITY);
    scenarios.add(new ScenarioRequest("Suction " + pressure, scenarioProcess, scenarioFeed, scenarioConfig, null, null));
}
for (ScenarioResult scenario : optimizer.optimizeScenarios(scenarios)) {
    logger.info("{}: {} kg/hr, feasible {}", scenario.getName(),
        scenario.getResult().getOptimalRate(), scenario.getResult().isFeasible());
}''',
45:'''// Generate screening curves from an already solved design point.
comp.getCompressorChart().setUseCompressorChart(false);
comp.setOutletPressure(150.0);
process.run();
CompressorChartGenerator chartGen = new CompressorChartGenerator(comp);
chartGen.generateCompressorChart("midpoint");
comp.setMaximumSpeed(comp.getSpeed() * 1.15);
// Vendor performance data and units must replace these synthetic design curves.''',
56:'''config.defaultUtilizationLimit(0.60);
// Equipment names are explicit identities in this process.
config.utilizationLimitForName("Export Comp", 0.85);''',
57:'''OptimizationResult result = optimizer.optimize(process, feed, config, objectives, constraints);
for (IterationRecord entry : result.getIterationHistory()) {
    logger.info("Rate {}, score {}, feasible {}", entry.getRate(), entry.getScore(), entry.isFeasible());
}
String csv = result.exportIterationHistoryAsCsv();
String json = result.exportIterationHistoryAsJson();''',
58:'''ProcessSimulationEvaluator evaluator = new ProcessSimulationEvaluator(process);
evaluator.addParameterWithSetter("flow", (proc, value) -> ((StreamInterface) proc.getUnit("feed")).setFlowRate(value, "kg/hr"), 50000.0, 300000.0, "kg/hr");
evaluator.addObjective("throughput", proc -> ((StreamInterface) proc.getUnit("feed")).getFlowRate("kg/hr"), ProcessSimulationEvaluator.ObjectiveDefinition.Direction.MAXIMIZE);
evaluator.addConstraintUpperBound("power", proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 25.0);
ProcessSimulationEvaluator.EvaluationResult evaluation = evaluator.evaluate(new double[]{200000.0});
logger.info("Objective {}, feasible {}, converged {}", evaluation.getObjective(), evaluation.isFeasible(), evaluation.isSimulationConverged());''',
61:'''SQPoptimizer sqp = new SQPoptimizer(1);
// Dimensionless throughput variable; every constraint evaluation solves the process.
sqp.setObjectiveFunction(x -> -x[0]);
sqp.addInequalityConstraint(x -> {
    feed.setFlowRate(x[0] * 100000.0, "kg/hr");
    process.run();
    return (25.0 - comp.getPower("MW")) / 25.0;
});
sqp.setVariableBounds(new double[]{0.5}, new double[]{3.0});
sqp.setInitialPoint(new double[]{1.0});
SQPoptimizer.OptimizationResult sqpResult = sqp.solve();
feed.setFlowRate(sqpResult.getOptimalPoint()[0] * 100000.0, "kg/hr");
process.run();
logger.info("SQP converged {}, final power {} MW", sqpResult.isConverged(), comp.getPower("MW"));''',
63:'''import neqsim.process.util.reconciliation.*;
SteadyStateDetector detector = new SteadyStateDetector();
SteadyStateVariable pressure = detector.addVariable("pressure").setUnit("bara");
for (int sample = 0; sample < 60; sample++) { pressure.addValue(65.0); }
SteadyStateResult steady = detector.evaluate();
logger.info("Synthetic constant-pressure window at steady state: {}", steady.isAtSteadyState());''',
82:'''// Current optimizer validation and replay reject non-finite or invalid final candidates.
// There is no rejectInvalidSimulations configuration method in this revision.
if (!result.isFeasible()) {
    logger.warn("Candidate not accepted: {}", result.getInfeasibilityDiagnosis());
}'''
}
for ch in (22,24,29,30):
 p=path(ch); text=p.read_text(encoding='utf-8-sig')
 for n,m in reversed(list(enumerate(PAT.finditer(text),1))):
  if m[1]!='java':continue
  code=m[3]; annotation=m[2]
  if ch==24:
   code=fix24.get(n,code)
   if n==1:code=code.replace('interface CapacityConstrainedEquipment', 'interface CapacityConstrainedEquipmentExcerpt')
   if n==40:
    code=code.replace('proc.getUnit("feed").getFlowRate', '((StreamInterface) proc.getUnit("feed")).getFlowRate')
    code=code.replace('proc.getUnit("compressor").getPower() / 1e6', '((Compressor) proc.getUnit("Export Comp")).getPower("MW")')
    code=code.replace('point.getObjectiveValue("throughput")', 'point.getObjectiveValues().get("throughput")').replace('point.getObjectiveValue("power")','point.getObjectiveValues().get("power")')
    code=code.replace('ParetoPoint knee = pareto.getKneePoint();', 'Optional<ParetoPoint> knee = pareto.findKneePoint();').replace('.paretoGridSize(15)', '.paretoGridSize(5).maxIterations(20)')
   if n==46:code=code.replace('Map<String, CapacityConstraint> constraints', 'Map<String, CapacityConstraint> chartConstraints')
   if n==49:code=code.replace('proc.getUnit("compressor")', 'proc.getUnit("Export Comp")').replace('.maxIterations(200)', '.maxIterations(30)')
   if n in (64,65):annotation=' pattern: requires a measured-variable reconciliation model and statistical acceptance policy'
   code=code.replace('SearchMode.GOLDEN_SECTION_SCORE','SearchMode.BINARY_FEASIBILITY') if n==19 else code
  if ch==29:
   if n==7:
    code=fixture+'\nimport neqsim.process.controllerdevice.*;\nStream feedStream = feed;\n'+code
    code=code.replace('ControllerDeviceInterface levelController =', 'ControllerDeviceBaseClass levelController =').replace('ControllerDeviceInterface pressureController =', 'ControllerDeviceBaseClass pressureController =')
    code=code.replace('levelController.setControllerType("PI");\n','').replace('pressureController.setControllerType("P");\n','')
   if n==9:code=code.replace('// "HP Sep.pressure [INPUT] Operating pressure"','// Discover the actual access type; separator pressure is read-only in this facade.')
   if n==10:
    code='ProcessModel plant = new ProcessModel();\nplant.add("Separation", process);\n'+code.replace('Compression::Compressor','Separation::Compressor')
  if ch==30:
   if n==24:code=fixture+'\n'+code
   if n==25:code='ProcessModel plant = new ProcessModel();\nplant.add("Processing", process);\n'+code
   if n==26:code=code.replace('platform_x_v2.json','platform_x_v3.json').replace('diff.getModifiedParameters()', 'diff.getModifiedParameters().keySet()')
  lead=(f'**Execution scope:** {annotation.split("pattern:",1)[1].strip()}.\n\n' if 'pattern:' in annotation and 'pattern' not in m[2] else '')
  text=text[:m.start()]+lead+'```java'+annotation+'\n'+code.rstrip()+'\n```'+text[m.end():]
 if ch==22:
  text=text.replace(r'|x_{k+1} - x_k|', r'\lvert x_{k+1} - x_k\rvert')
  text=text.replace('$1.1 million per day', '$105,000 per day')
 p.write_text(text,encoding='utf-8')
