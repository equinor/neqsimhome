import java.util.*;
import java.util.function.*;
import java.nio.file.*;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import neqsim.thermo.system.*;
import neqsim.thermodynamicoperations.*;
import neqsim.process.processmodel.*;
import neqsim.process.processmodel.lifecycle.*;
import neqsim.process.equipment.*;
import neqsim.process.equipment.stream.*;
import neqsim.process.equipment.separator.*;
import neqsim.process.equipment.compressor.*;
import neqsim.process.equipment.pipeline.*;
import neqsim.process.equipment.pump.*;
import neqsim.process.equipment.heatexchanger.*;
import neqsim.process.equipment.valve.*;
import neqsim.process.equipment.capacity.*;
import neqsim.process.equipment.capacity.CapacityConstraint.*;
import neqsim.process.util.optimizer.*;
import neqsim.process.util.optimizer.ProductionOptimizer.*;
import neqsim.process.controllerdevice.*;
import neqsim.process.measurementdevice.*;
import neqsim.process.automation.*;
Logger logger = LogManager.getLogger("BookJavaExamples");
String bookFence = "BOOK_FENCE_1";
public interface CapacityConstrainedEquipmentExcerpt {
    
    Map<String, CapacityConstraint> getCapacityConstraints();
    CapacityConstraint getBottleneckConstraint();

    
    double getMaxUtilization();
    double getMaxUtilizationPercent();
    double getAvailableMargin();

    
    boolean isCapacityExceeded();
    boolean isHardLimitExceeded();
    boolean isNearCapacityLimit();

    
    boolean isCapacityAnalysisEnabled();
    void setCapacityAnalysisEnabled(boolean enabled);

    
    Map<String, Double> getUtilizationSummary();
}
String bookFence = "BOOK_FENCE_2";
import neqsim.thermo.system.*;
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
compressor.setUsePolytropicCalc(true);
ProcessSystem process = new ProcessSystem();
process.add(feed);
process.add(separator);
process.add(compressor);
process.run();
CapacityConstraint speedConstraint = new CapacityConstraint("speed", "RPM",
    CapacityConstraint.ConstraintType.HARD).setDesignValue(10000.0).setMaxValue(11000.0).setWarningThreshold(0.9).setDescription("Declared demonstration speed limit").setValueSupplier(() -> compressor.getSpeed());
String bookFence = "BOOK_FENCE_3";
compressor.enableAllConstraints();

String bookFence = "BOOK_FENCE_4";
process.enableAllConstraints();
String bookFence = "BOOK_FENCE_6";

process.disableAllConstraints();


separator.setCapacityAnalysisEnabled(false);
String bookFence = "BOOK_FENCE_7";
separator.autoSize(1.2);

String bookFence = "BOOK_FENCE_8";
compressor.autoSize(1.2);
compressor.getCompressorChart().setUseCompressorChart(false);
compressor.setSolveSpeed(false);
compressor.setUsePolytropicCalc(true);
for (Map.Entry<String,CapacityConstraint> entry : compressor.getCapacityConstraints().entrySet()) { entry.getValue().setEnabled(entry.getKey().equals("power")); }


String bookFence = "BOOK_FENCE_9";
ThrottlingValve valve = new ThrottlingValve("Example valve", feed);
valve.setOutletPressure(50.0);
valve.run();
valve.autoSize(1.2);
String bookFence = "BOOK_FENCE_10";
PipeBeggsAndBrills pipeline = new PipeBeggsAndBrills("Example pipe", feed);
pipeline.setLength(1000.0);
pipeline.setDiameter(0.25);
pipeline.setAngle(0.0);
pipeline.run();
pipeline.autoSize(1.2);
String bookFence = "BOOK_FENCE_11";
SystemInterface liquid = new SystemSrkEos(298.15, 5.0);
liquid.addComponent("n-heptane", 1.0);
liquid.setMixingRule("classic");
Stream pumpFeed = new Stream("Pump feed", liquid);
pumpFeed.setFlowRate(10000.0, "kg/hr");
pumpFeed.run();
Pump pump = new Pump("Example pump", pumpFeed);
pump.setOutletPressure(10.0);
pump.run();
pump.autoSize(1.2);
String bookFence = "BOOK_FENCE_12";

SystemInterface fluid = new SystemSrkEos(273.15 + 70.0, 65.0);
fluid.addComponent("methane", 0.70);
fluid.addComponent("ethane", 0.08);
fluid.addComponent("propane", 0.05);
fluid.addComponent("n-butane", 0.03);
fluid.addComponent("n-heptane", 0.08);
fluid.addComponent("water", 0.06);
fluid.setMixingRule("classic");
fluid.setMultiPhaseCheck(true);

Stream feed = new Stream("feed", fluid);
feed.setFlowRate(200000.0, "kg/hr");

ThreePhaseSeparator sep = new ThreePhaseSeparator("HP Sep", feed);
Compressor comp = new Compressor("Export Comp", sep.getGasOutStream());
comp.setOutletPressure(150.0);
comp.setPolytropicEfficiency(0.78);
comp.setUsePolytropicCalc(true);

ProcessSystem process = new ProcessSystem();
process.add(feed);
process.add(sep);
process.add(comp);
process.run();


sep.autoSize(1.2);
comp.autoSize(1.2);
comp.getCompressorChart().setUseCompressorChart(false);
comp.setSolveSpeed(false);
comp.setUsePolytropicCalc(true);
for (Map.Entry<String,CapacityConstraint> entry : comp.getCapacityConstraints().entrySet()) { entry.getValue().setEnabled(entry.getKey().equals("power")); }


logger.info("Sep max util: " + sep.getMaxUtilizationPercent() + "%");
logger.info("Comp max util: " + comp.getMaxUtilizationPercent() + "%");
String bookFence = "BOOK_FENCE_14";
comp.setMaximumSpeed(12000.0);  
comp.reinitializeCapacityConstraints();
String bookFence = "BOOK_FENCE_15";
BottleneckResult capacityResult = process.findBottleneck();
logger.info("Bottleneck {} utilization {}", capacityResult.getEquipmentName(), capacityResult.getUtilization());
Map<String, Double> utilizationSummary = process.getCapacityUtilizationSummary();
List<String> nearLimit = process.getEquipmentNearCapacityLimit();
boolean anyOverloaded = process.isAnyEquipmentOverloaded();
boolean anyHardViolation = process.isAnyHardLimitExceeded();
List<neqsim.process.equipment.capacity.CapacityConstrainedEquipment> constrained = process.getConstrainedEquipment();
String bookFence = "BOOK_FENCE_19";
OptimizationConfig config = new OptimizationConfig(50000.0, 300000.0)  .rateUnit("kg/hr").tolerance(500.0)                          .maxIterations(40)                         .searchMode(SearchMode.BINARY_FEASIBILITY).defaultUtilizationLimit(0.95)             .utilizationLimitForType(Compressor.class, 0.90)  .utilizationLimitForName("HP Separator", 0.92)    .stagnationIterations(5)                   .maxCacheSize(500)                         .enableCaching(true).parallelEvaluations(true)                 .parallelThreads(4);                       
String bookFence = "BOOK_FENCE_21";
config.validate();

String bookFence = "BOOK_FENCE_22";
ProductionOptimizer optimizer = new ProductionOptimizer();

OptimizationResult result = optimizer.optimize(
    process,       
    feed,          
    config,        
    null,    
    null    
);
String bookFence = "BOOK_FENCE_24";
config.swarmSize(20)           .inertiaWeight(0.7)        .cognitiveWeight(1.5)      .socialWeight(1.5)         .randomSeed(42);           
String bookFence = "BOOK_FENCE_25";

double optRate = result.getOptimalRate();
String unit = result.getRateUnit();
boolean feasible = result.isFeasible();
double score = result.getScore();


ProcessEquipmentInterface bottleneck = result.getBottleneck();
double bnUtil = result.getBottleneckUtilization();


List<UtilizationRecord> records = result.getUtilizationRecords();
for (UtilizationRecord rec : records) {
    logger.info(String.format("  %s: %.1f%% (limit: %.1f%%)%n",
        rec.getEquipmentName(),
        rec.getUtilization() * 100,
        rec.getUtilizationLimit() * 100));
}


Map<String, Double> decisions = result.getDecisionVariables();


Map<String, Double> objectives = result.getObjectiveValues();


List<ConstraintStatus> statuses = result.getConstraintStatuses();
for (ConstraintStatus cs : statuses) {
    if (cs.violated()) {
        logger.info(String.format("  VIOLATED: %s (margin=%.4f)%n",
            cs.getName(), cs.getMargin()));
    }
}


int iterations = result.getIterations();
List<IterationRecord> history = result.getIterationHistory();
String bookFence = "BOOK_FENCE_26";
if (!result.isFeasible()) {
    logger.info(result.getInfeasibilityDiagnosis());
}
String bookFence = "BOOK_FENCE_29";
OptimizationSummary optimizationSummary = optimizer.quickOptimize(process, feed, "kg/hr", null);
logger.info("Rate {} {}, feasible {}", optimizationSummary.getMaxRate(), optimizationSummary.getRateUnit(), optimizationSummary.isFeasible());
String bookFence = "BOOK_FENCE_30";
ProcessOptimizationEngine engine = new ProcessOptimizationEngine(process);
engine.setFeedStreamName("feed");
engine.setOutletStreamName("Export Comp");
ProcessOptimizationEngine.OptimizationResult engineResult = engine.findMaximumThroughput(65.0, 150.0, 50000.0, 300000.0);
ProcessOptimizationEngine.ConstraintReport report = engine.evaluateAllConstraints();
ProcessOptimizationEngine.SensitivityResult sens = engine.analyzeSensitivity(100000.0, 65.0, 150.0);
ProcessOptimizationEngine.LiftCurveData curve = engine.generateCapacityScreening(new double[]{50.0,65.0,80.0},
    new double[]{343.15}, 150.0, 50000.0, 300000.0);
logger.info("Capacity screening points {}", curve.getPoints().size());
String bookFence = "BOOK_FENCE_31";
EquipmentCapacityStrategyRegistry registry = EquipmentCapacityStrategyRegistry.getInstance();
logger.info("Registered capacity strategies: {}", registry.getStrategyCount());
for (EquipmentCapacityStrategy strategy : registry.getAllStrategies()) {
    logger.info("Strategy {}", strategy.getClass().getSimpleName());
}
String bookFence = "BOOK_FENCE_36";
OptimizationObjective throughput = new OptimizationObjective("throughput",
    proc -> ((StreamInterface) proc.getUnit("feed")).getFlowRate("kg/hr"), 1.0, ObjectiveType.MAXIMIZE);
OptimizationObjective minPower = new OptimizationObjective("power",
    proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 0.3, ObjectiveType.MINIMIZE);
List<OptimizationObjective> objectives = Arrays.asList(throughput, minPower);
String bookFence = "BOOK_FENCE_38";
OptimizationConstraint maxPower = OptimizationConstraint.lessThan("compressor_power",
    proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 25.0,
    ProductionOptimizer.ConstraintSeverity.HARD, 100.0, "Declared power ceiling (MW)");

OptimizationConstraint maxTemperature = OptimizationConstraint.lessThan("discharge_temperature",
    proc -> ((Compressor) proc.getUnit("Export Comp")).getOutletStream().getTemperature("C"), 180.0,
    ProductionOptimizer.ConstraintSeverity.SOFT, 10.0, "Illustrative discharge temperature preference");
List<OptimizationConstraint> constraints = Arrays.asList(maxPower, maxTemperature);
String bookFence = "BOOK_FENCE_40";
List<OptimizationObjective> objectives = Arrays.asList(
    new OptimizationObjective("throughput",
        proc -> ((StreamInterface) proc.getUnit("feed")).getFlowRate("kg/hr"),
        1.0, ObjectiveType.MAXIMIZE),
    new OptimizationObjective("power",
        proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"),
        1.0, ObjectiveType.MINIMIZE)
);

OptimizationConfig config = new OptimizationConfig(50000.0, 300000.0).searchMode(SearchMode.GOLDEN_SECTION_SCORE).paretoGridSize(5).maxIterations(20);  

ParetoResult pareto = optimizer.optimizePareto(
    process, feed, config, objectives, constraints);


List<ParetoPoint> front = pareto.getParetoFront();
for (ParetoPoint point : front) {
    logger.info(String.format("Rate=%.0f kg/hr, Power=%.1f MW, Feasible=%s%n",
        point.getObjectiveValues().get("throughput"),
        point.getObjectiveValues().get("power"),
        point.isFeasible()));
}



String bookFence = "BOOK_FENCE_42";

List<OptimizationObjective> threeObjectives = Arrays.asList(
    new OptimizationObjective("oil_mass_kg_hr", proc ->
        ((ThreePhaseSeparator) proc.getUnit("HP Sep")).getOilOutStream().getFlowRate("kg/hr"),
        1.0, ObjectiveType.MAXIMIZE),
    new OptimizationObjective("gas_rate", proc -> ((ThreePhaseSeparator) proc.getUnit("HP Sep")).getGasOutStream().getFlowRate("MSm3/day"), 1.0, ObjectiveType.MAXIMIZE),
    new OptimizationObjective("power", proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 1.0, ObjectiveType.MINIMIZE));
config.paretoGridSize(3).maxIterations(15);
ParetoResult threeObjectiveResult = optimizer.optimizePareto(process, feed, config, threeObjectives, constraints);
String bookFence = "BOOK_FENCE_43";
List<ScenarioRequest> scenarios = new ArrayList<ScenarioRequest>();
for (double pressure : new double[]{50.0, 65.0, 80.0}) {
    ProcessSystem scenarioProcess = process.copy();
    StreamInterface scenarioFeed = (StreamInterface) scenarioProcess.getUnit("feed");
    scenarioFeed.setPressure(pressure, "bara");
    OptimizationConfig scenarioConfig = new OptimizationConfig(50000.0, 300000.0).rateUnit("kg/hr").maxIterations(20).searchMode(SearchMode.BINARY_FEASIBILITY);
    scenarios.add(new ScenarioRequest("Suction " + pressure, scenarioProcess, scenarioFeed, scenarioConfig, null, null));
}
for (ScenarioResult scenario : optimizer.optimizeScenarios(scenarios)) {
    logger.info("{}: {} kg/hr, feasible {}", scenario.getName(),
        scenario.getResult().getOptimalRate(), scenario.getResult().isFeasible());
}
String bookFence = "BOOK_FENCE_45";

comp.getCompressorChart().setUseCompressorChart(false);
comp.setOutletPressure(150.0);
process.run();
CompressorChartGenerator chartGen = new CompressorChartGenerator(comp);
chartGen.generateCompressorChart("midpoint");
comp.setMaximumSpeed(comp.getSpeed() * 1.15);

String bookFence = "BOOK_FENCE_46";
comp.getCompressorChart().setUseCompressorChart(true);
comp.autoSize(1.2);
comp.getCompressorChart().setUseCompressorChart(false);
comp.setSolveSpeed(false);
comp.setUsePolytropicCalc(true);
for (Map.Entry<String,CapacityConstraint> entry : comp.getCapacityConstraints().entrySet()) { entry.getValue().setEnabled(entry.getKey().equals("power")); }


Map<String, CapacityConstraint> chartConstraints = comp.getCapacityConstraints();



String bookFence = "BOOK_FENCE_47";

comp.setMaximumSpeed(12000.0);


comp.reinitializeCapacityConstraints();


String bookFence = "BOOK_FENCE_49";
List<ManipulatedVariable> variables = Arrays.asList(
    new ManipulatedVariable("flowRate", 50000, 300000, "kg/hr",
        (proc, val) -> {
            ((StreamInterface) proc.getUnit("feed")).setFlowRate(val, "kg/hr");
        }),
    new ManipulatedVariable("sepPressure", 40, 90, "bara",
        (proc, val) -> {
            ((StreamInterface) proc.getUnit("feed")).setPressure(val, "bara");
        }),
    new ManipulatedVariable("compOutP", 120, 180, "bara",
        (proc, val) -> {
            ((Compressor) proc.getUnit("Export Comp")).setOutletPressure(val);
        })
);

OptimizationConfig config = new OptimizationConfig(0, 1)  .searchMode(SearchMode.NELDER_MEAD_SCORE).maxIterations(30);

OptimizationResult result = optimizer.optimize(
    process, variables, config, objectives, constraints);

Map<String, Double> optimal = result.getDecisionVariables();
logger.info("Optimal flow: " + optimal.get("flowRate") + " kg/hr");
logger.info("Optimal sep P: " + optimal.get("sepPressure") + " bara");
logger.info("Optimal comp P: " + optimal.get("compOutP") + " bara");
String bookFence = "BOOK_FENCE_50";
config.stagnationIterations(5);  
String bookFence = "BOOK_FENCE_51";
config.initialGuess(new double[]{180000.0});  
String bookFence = "BOOK_FENCE_52";
config.enableCaching(true);
config.maxCacheSize(500);  
String bookFence = "BOOK_FENCE_53";
config.parallelEvaluations(true);
config.parallelThreads(8);  
String bookFence = "BOOK_FENCE_54";
config.randomSeed(42);       
config.useFixedSeed(true);   
String bookFence = "BOOK_FENCE_55";
config.useFixedSeed(false);  
String bookFence = "BOOK_FENCE_56";
config.defaultUtilizationLimit(0.60);

config.utilizationLimitForName("Export Comp", 0.85);
String bookFence = "BOOK_FENCE_57";
OptimizationResult result = optimizer.optimize(process, feed, config, objectives, constraints);
for (IterationRecord entry : result.getIterationHistory()) {
    logger.info("Rate {}, score {}, feasible {}", entry.getRate(), entry.getScore(), entry.isFeasible());
}
String csv = result.exportIterationHistoryAsCsv();
String json = result.exportIterationHistoryAsJson();
String bookFence = "BOOK_FENCE_58";
ProcessSimulationEvaluator evaluator = new ProcessSimulationEvaluator(process);
evaluator.addParameterWithSetter("flow", (proc, value) -> ((StreamInterface) proc.getUnit("feed")).setFlowRate(value, "kg/hr"), 50000.0, 300000.0, "kg/hr");
evaluator.addObjective("throughput", proc -> ((StreamInterface) proc.getUnit("feed")).getFlowRate("kg/hr"), ProcessSimulationEvaluator.ObjectiveDefinition.Direction.MAXIMIZE);
evaluator.addConstraintUpperBound("power", proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 25.0);
ProcessSimulationEvaluator.EvaluationResult evaluation = evaluator.evaluate(new double[]{200000.0});
logger.info("Objective {}, feasible {}, converged {}", evaluation.getObjective(), evaluation.isFeasible(), evaluation.isSimulationConverged());
String bookFence = "BOOK_FENCE_61";
SQPoptimizer sqp = new SQPoptimizer(1);

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
logger.info("SQP converged {}, final power {} MW", sqpResult.isConverged(), comp.getPower("MW"));
String bookFence = "BOOK_FENCE_63";
import neqsim.process.util.reconciliation.*;
SteadyStateDetector detector = new SteadyStateDetector();
SteadyStateVariable pressure = detector.addVariable("pressure").setUnit("bara");
for (int sample = 0; sample < 60; sample++) { pressure.addValue(65.0); }
SteadyStateResult steady = detector.evaluate();
logger.info("Synthetic constant-pressure window at steady state: {}", steady.isAtSteadyState());
String bookFence = "BOOK_FENCE_64";
import neqsim.process.util.reconciliation.*;
DataReconciliationEngine reconciler = new DataReconciliationEngine();

reconciler.addVariable(new ReconciliationVariable("feed",200000.0,2000.0));
reconciler.addVariable(new ReconciliationVariable("gas",150000.0,1500.0));
reconciler.addVariable(new ReconciliationVariable("oil",48000.0,1000.0));
reconciler.addVariable(new ReconciliationVariable("water",5000.0,500.0));
reconciler.addConstraint(new double[]{1.0,-1.0,-1.0,-1.0},"Mass balance");
ReconciliationResult reconciliation = reconciler.reconcile();
if (!reconciliation.isConverged()) { throw new IllegalStateException(reconciliation.getErrorMessage()); }
logger.info("Chi-square {}, global test passed {}",reconciliation.getChiSquareStatistic(),reconciliation.isGlobalTestPassed());
logger.info("Mass-balance residuals kg/hr: {}",Arrays.toString(reconciliation.getConstraintResidualsAfter()));
String bookFence = "BOOK_FENCE_65";
for (ReconciliationVariable suspect : reconciliation.getGrossErrors()) {
    logger.warn("Suspect {} normalized residual {}",suspect.getName(),suspect.getNormalizedResidual());
}
String bookFence = "BOOK_FENCE_79";
config.defaultUtilizationLimit(0.95)                    .utilizationLimitForType(Compressor.class, 0.88)    .utilizationLimitForType(ThrottlingValve.class, 0.80) .utilizationLimitForName("Old Compressor K-101", 0.82); 
String bookFence = "BOOK_FENCE_81";
config.stagnationIterations(5);  
String bookFence = "BOOK_FENCE_82";
config.rejectInvalidSimulations(true);

String bookFence = "BOOK_FENCE_END";
/exit
