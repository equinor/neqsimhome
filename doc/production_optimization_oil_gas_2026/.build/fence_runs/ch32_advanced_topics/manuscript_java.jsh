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
ProductionOptimizer optimizer = new ProductionOptimizer();
List<OptimizationObjective> objectives = Arrays.asList(
    new OptimizationObjective("production", proc -> ((StreamInterface) proc.getUnit("Feed")).getFlowRate("kg/hr"), 1.0, ObjectiveType.MAXIMIZE),
    new OptimizationObjective("power", proc -> ((Compressor) proc.getUnit("Compressor")).getPower("kW"), 1.0, ObjectiveType.MINIMIZE));
OptimizationConfig config = new OptimizationConfig(50000.0,200000.0).rateUnit("kg/hr").maxIterations(20).paretoGridSize(5);
ParetoResult pareto = optimizer.optimizePareto(process, feed, config, objectives, Collections.emptyList());
List<ParetoPoint> front = pareto.getParetoFront();
logger.info("Non-dominated sampled points: {}", front.size());

String bookFence = "BOOK_FENCE_3";
import neqsim.process.util.optimizer.SQPoptimizer;


SQPoptimizer sqp = new SQPoptimizer(2);


sqp.setObjectiveFunction(new SQPoptimizer.ObjectiveFunc() {
    public double evaluate(double[] x) {
        return Math.pow(x[0] - 3.0, 2) + Math.pow(x[1] - 2.0, 2);
    }
});


sqp.addInequalityConstraint(new SQPoptimizer.ConstraintFunc() {
    public double evaluate(double[] x) {
        return x[0] + x[1] - 4.0;  
    }
});


sqp.addEqualityConstraint(new SQPoptimizer.ConstraintFunc() {
    public double evaluate(double[] x) {
        return x[0] - x[1] - 1.0;  
    }
});


sqp.setVariableBounds(
    new double[]{0.0, 0.0},     
    new double[]{10.0, 10.0}    
);


sqp.setInitialPoint(new double[]{5.0, 5.0});


SQPoptimizer.OptimizationResult result = sqp.solve();

logger.info("Optimal x: " + Arrays.toString(result.getOptimalPoint()));
logger.info("Optimal f: " + result.getOptimalValue());
logger.info("Converged: " + result.isConverged());
logger.info("Iterations: " + result.getIterations());
String bookFence = "BOOK_FENCE_5";
ProcessSimulationEvaluator evaluator = new ProcessSimulationEvaluator(process);
evaluator.addParameterWithSetter("flow", (proc, value) -> ((StreamInterface) proc.getUnit("Feed")).setFlowRate(value,"kg/hr"), 50000.0,200000.0,"kg/hr");
evaluator.addParameterWithSetter("suction", (proc, value) -> ((StreamInterface) proc.getUnit("Feed")).setPressure(value,"bara"), 40.0,80.0,"bara");
evaluator.addObjective("production", proc -> ((StreamInterface) proc.getUnit("Feed")).getFlowRate("kg/hr"), ProcessSimulationEvaluator.ObjectiveDefinition.Direction.MAXIMIZE);
evaluator.addConstraintUpperBound("power", proc -> ((Compressor) proc.getUnit("Compressor")).getPower("kW"),5000.0);
double[] x = {100000.0,60.0};
ProcessSimulationEvaluator.EvaluationResult result = evaluator.evaluate(x);
logger.info("Objective {}, feasible {}, converged {}", result.getObjective(),result.isFeasible(),result.isSimulationConverged());
double rejectedPowerKW = compressor.getPower("kW");

if (result.isFeasible() || rejectedPowerKW <= 5000.0) {
    throw new IllegalStateException("Expected the high-rate candidate to be rejected");
}
ProcessSimulationEvaluator.EvaluationResult acceptedEvaluation = evaluator.evaluate(new double[]{80000.0,60.0});
if (!acceptedEvaluation.isFeasible() || !acceptedEvaluation.isSimulationConverged()
        || compressor.getPower("kW") > 5000.0) {
    throw new IllegalStateException("Lower-rate evaluator candidate failed acceptance");
}
logger.info("Accepted 80000 kg/hr candidate, power {} kW", compressor.getPower("kW"));
String bookFence = "BOOK_FENCE_9";
evaluator.setFiniteDifferenceStep(0.001);
evaluator.setUseRelativeStep(true);
double[] gradient = evaluator.estimateGradient(x);
logger.info("Forward finite-difference objective gradient: {}", Arrays.toString(gradient));
String bookFence = "BOOK_FENCE_11";

Object finiteJsonValue(Object value) {
    if (value instanceof Double && !Double.isFinite(((Double) value).doubleValue())) { return null; }
    if (value instanceof Map) {
        Map<String,Object> clean = new LinkedHashMap<String,Object>();
        for (Map.Entry<?,?> entry : ((Map<?,?>) value).entrySet()) {
            clean.put(String.valueOf(entry.getKey()), finiteJsonValue(entry.getValue()));
        }
        return clean;
    }
    if (value instanceof Iterable) {
        List<Object> clean = new ArrayList<Object>();
        for (Object entry : (Iterable<?>) value) { clean.add(finiteJsonValue(entry)); }
        return clean;
    }
    return value;
}
Map<String,Object> definition = evaluator.getProblemDefinition();
definition.put("unboundedLimitEncoding", "null");
String json = new com.google.gson.GsonBuilder().serializeNulls().setPrettyPrinting().create().toJson(finiteJsonValue(definition));
logger.info("Problem definition: {}",json);
String bookFence = "BOOK_FENCE_12";
import neqsim.process.util.reconciliation.*;
SteadyStateDetector detector = new SteadyStateDetector();
SteadyStateVariable pressure = detector.addVariable("Pressure").setUnit("bara");
for (int index=0; index<60; index++) { pressure.addValue(60.0); }
SteadyStateResult steady = detector.evaluate();
logger.info("Synthetic constant signal steady: {}; R-statistic {}", steady.isAtSteadyState(),pressure.getRStatistic());

String bookFence = "BOOK_FENCE_13";
DataReconciliationEngine engine = new DataReconciliationEngine();

engine.addVariable(new ReconciliationVariable("Feed",100000.0,2000.0));
engine.addVariable(new ReconciliationVariable("Gas",70000.0,1500.0));
engine.addVariable(new ReconciliationVariable("Oil",28000.0,1000.0));
engine.addVariable(new ReconciliationVariable("Water",5000.0,500.0));
engine.addConstraint(new double[]{1.0,-1.0,-1.0,-1.0},"Mass balance");
ReconciliationResult reconciled = engine.reconcile();
if (!reconciled.isConverged()) { throw new IllegalStateException(reconciled.getErrorMessage()); }
logger.info(
    "Reconciled feed {} kg/hr; residuals {}",
    engine.getVariable("Feed").getReconciledValue(),
    Arrays.toString(reconciled.getConstraintResidualsAfter()));
String bookFence = "BOOK_FENCE_14";
logger.info("Global test passed: {}",reconciled.isGlobalTestPassed());
for (ReconciliationVariable suspect : reconciled.getGrossErrors()) {
    logger.warn("Suspect {} normalized residual {}",suspect.getName(),suspect.getNormalizedResidual());
}
String bookFence = "BOOK_FENCE_15";
import neqsim.process.calibration.BatchParameterEstimator;
import neqsim.process.calibration.BatchResult;


compressor.setUsePolytropicCalc(true);
compressor.setPolytropicEfficiency(0.78);
feed.setFlowRate(100000.0,"kg/hr");
feed.setPressure(60.0,"bara");
BatchParameterEstimator estimator = new BatchParameterEstimator(process);
estimator.addTunableParameter("Compressor.polytropicEfficiency","-",0.60,0.90,0.72);
estimator.addMeasuredVariable("Compressor.outletStream.temperature","K",1.0);
for (double discharge : new double[]{130.0,150.0,170.0}) {
    compressor.setOutletPressure(discharge,"bara");
    process.run();
    Map<String,Double> conditions = new HashMap<String,Double>();
    conditions.put("Compressor.outletPressure",discharge);
    Map<String,Double> observations = new HashMap<String,Double>();
    observations.put("Compressor.outletStream.temperature",
        compressor.getOutletStream().getTemperature("K"));
    estimator.addDataPoint(conditions,observations);
}
compressor.setPolytropicEfficiency(0.72);
estimator.setMaxIterations(40);
BatchResult fit = estimator.solve();
logger.info("Converged {}, estimated efficiency {}, RMSE {}",fit.isConverged(),fit.getEstimate(0),fit.getRMSE());
if (!Double.isFinite(fit.getEstimate(0)) || Math.abs(fit.getEstimate(0)-0.78)>0.01) {
    throw new IllegalStateException("Synthetic efficiency recovery failed");
}


String bookFence = "BOOK_FENCE_17";
BatchStudy study = BatchStudy.builder(process).vary("Feed.flowRate",50000.0,200000.0,4).vary("Compressor.outletPressure",120.0,200.0,3).addObjective("flow",BatchStudy.Objective.MAXIMIZE, proc -> ((StreamInterface) proc.getUnit("Feed")).getFlowRate("kg/hr")).addObjective("power",BatchStudy.Objective.MINIMIZE, proc -> ((Compressor) proc.getUnit("Compressor")).getPower("kW")).parallelism(1).name("Compression envelope").build();
BatchStudy.BatchStudyResult batch = study.run();
if (batch.getFailureCount()!=0) { throw new IllegalStateException(batch.getSummary()); }
logger.info("Cases run {}",batch.getTotalCases());
String bookFence = "BOOK_FENCE_18";
List<BatchStudy.CaseResult> nonDominated = batch.getParetoFront("flow","power");
for (BatchStudy.CaseResult candidate : nonDominated) {
    logger.info("Parameters {} objectives {}",candidate.parameters.values,candidate.objectiveValues);
}

String bookFence = "BOOK_FENCE_19";
double[] powers = batch.getSuccessfulResults().stream().mapToDouble(candidate -> candidate.objectiveValues.get("power")).toArray();
java.util.DoubleSummaryStatistics statistics = Arrays.stream(powers).summaryStatistics();
logger.info("Design-grid power minimum {}, mean {}, maximum {} kW",statistics.getMin(),statistics.getAverage(),statistics.getMax());

String bookFence = "BOOK_FENCE_END";
/exit
