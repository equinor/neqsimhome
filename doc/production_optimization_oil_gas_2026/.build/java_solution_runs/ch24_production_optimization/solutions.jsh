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

class BookSolutionChecks {
    static int fence = 0;
    static java.nio.file.Path destination;
    static java.util.List<java.util.Map<String,Object>> rows = new java.util.ArrayList<java.util.Map<String,Object>>();
    static void check(String name, boolean passed, double observed, double tolerance) {
        java.util.Map<String,Object> row = new java.util.LinkedHashMap<String,Object>();
        row.put("fence",fence); row.put("name",name);row.put("passed",passed);
        row.put("observed",observed);row.put("tolerance",tolerance);rows.add(row);
        try { java.nio.file.Files.write(destination,new com.google.gson.Gson().toJson(rows).getBytes(java.nio.charset.StandardCharsets.UTF_8)); }
        catch (java.io.IOException error) { throw new IllegalStateException(error); }
        if (!passed) { throw new IllegalStateException(name+" failed: "+observed); }
    }
    static void close(String name,double residual,double tolerance) {
        check(name,Double.isFinite(residual) && Math.abs(residual)<=tolerance,residual,tolerance);
    }
    static double mass(neqsim.process.equipment.stream.StreamInterface stream) {
        double value=stream.getFlowRate("kg/sec");
        check(stream.getName()+" finite nonnegative mass",Double.isFinite(value)&&value>=-1e-12,value,0);
        check(stream.getName()+" positive finite pressure",Double.isFinite(stream.getPressure())&&stream.getPressure()>0,stream.getPressure(),0);
        check(stream.getName()+" positive finite temperature",Double.isFinite(stream.getTemperature())&&stream.getTemperature()>0,stream.getTemperature(),0);
        return value;
    }
    static double h(neqsim.process.equipment.stream.StreamInterface stream) {
        if (stream.getFlowRate("kg/sec")<1e-12) { return 0; }
        stream.getFluid().initProperties();return stream.getFluid().getEnthalpy();
    }
    static void process(neqsim.process.processmodel.ProcessSystem process) {
        for (neqsim.process.equipment.ProcessEquipmentInterface unit:process.getUnitOperations()) {
            if (unit instanceof neqsim.process.equipment.stream.Stream) { continue; }
            java.util.List<neqsim.process.equipment.stream.StreamInterface> in=unit.getInletStreams();
            java.util.List<neqsim.process.equipment.stream.StreamInterface> out=unit.getOutletStreams();
            if (in.isEmpty()||out.isEmpty()) {continue;}
            double mi=0,mo=0,hi=0,ho=0,work=0,nscale=0;
            java.util.Map<String,Double> cin=new java.util.HashMap<String,Double>();
            java.util.Map<String,Double> cout=new java.util.HashMap<String,Double>();
            for (neqsim.process.equipment.stream.StreamInterface stream:in) {
                mi+=mass(stream);hi+=h(stream);
                for(int j=0;j<stream.getFluid().getNumberOfComponents();j++) {
                    String key=stream.getFluid().getComponent(j).getComponentName();
                    double value=stream.getFluid().getComponent(j).getNumberOfmoles();
                    cin.put(key,cin.getOrDefault(key,0.0)+value);nscale+=value;
                }
            }
            for (neqsim.process.equipment.stream.StreamInterface stream:out) {
                mo+=mass(stream);ho+=h(stream);
                for(int j=0;j<stream.getFluid().getNumberOfComponents();j++) {
                    String key=stream.getFluid().getComponent(j).getComponentName();
                    double value=stream.getFluid().getComponent(j).getNumberOfmoles();
                    cout.put(key,cout.getOrDefault(key,0.0)+value);
                }
            }
            if(mi<1e-10) {continue;}
            close(unit.getName()+" material balance relative",(mo-mi)/mi,1e-6);
            double componentError=0;
            for(String key:cin.keySet()) { componentError=Math.max(componentError,Math.abs(cout.getOrDefault(key,0.0)-cin.get(key))/Math.max(nscale,1e-12)); }
            close(unit.getName()+" component balance relative",componentError,1e-6);
            if(unit instanceof neqsim.process.equipment.compressor.Compressor) {
                check(unit.getName()+" single-phase compressor inlet",in.get(0).getFluid().getNumberOfPhases()==1,in.get(0).getFluid().getNumberOfPhases(),1);
                work=((neqsim.process.equipment.compressor.Compressor)unit).getPower();
                check(unit.getName()+" positive compressor shaft work",work>0,work,0);
            }
            if(unit instanceof neqsim.process.equipment.heatexchanger.Heater) { work=((neqsim.process.equipment.heatexchanger.Heater)unit).getDuty(); }
            if(unit instanceof neqsim.process.equipment.pipeline.PipeBeggsAndBrills) {
                check(unit.getName()+" upward/passive pressure decline",out.get(0).getPressure()>0&&out.get(0).getPressure()<=in.get(0).getPressure(),out.get(0).getPressure(),0);
            } else {
                close(unit.getName()+" energy balance relative",(ho-hi-work)/Math.max(1,Math.max(Math.abs(work),Math.max(Math.abs(hi),Math.abs(ho)))),1e-5);
            }
        }
    }
    static void optimizer(neqsim.process.util.optimizer.ProductionOptimizer.OptimizationResult result) {
        check("optimizer finite positive candidate rate",Double.isFinite(result.getOptimalRate())&&result.getOptimalRate()>0,result.getOptimalRate(),0);
        for(neqsim.process.util.optimizer.ProductionOptimizer.UtilizationRecord rec:result.getUtilizationRecords()) {
            if(result.isFeasible()) {check("feasible candidate utilization "+rec.getEquipmentName(),rec.getUtilization()<=rec.getUtilizationLimit()+1e-6,rec.getUtilization()-rec.getUtilizationLimit(),1e-6);}
        }
        if(!result.isFeasible()) {check("rejected candidate explicit diagnostic",result.getInfeasibilityDiagnosis()!=null,0,0);}
    }
    static void pareto(neqsim.process.util.optimizer.ProductionOptimizer.ParetoResult result,
            neqsim.process.processmodel.ProcessSystem model, String[] keys, boolean[] maximize) {
        java.util.List<neqsim.process.util.optimizer.ProductionOptimizer.ParetoPoint> front=result.getParetoFront();
        check("nonempty Pareto front",!front.isEmpty(),front.size(),0);
        for(neqsim.process.util.optimizer.ProductionOptimizer.ParetoPoint point:front) {
            java.util.Map<String,Double> values=point.getObjectiveValues();
            for(String key:keys) {check("finite Pareto objective "+key,Double.isFinite(values.get(key)),values.get(key),0);}
            boolean dominated=false;
            for(neqsim.process.util.optimizer.ProductionOptimizer.ParetoPoint other:front) {
                boolean weak=true,strict=false;
                for(int k=0;k<keys.length;k++) {
                    double a=values.get(keys[k]),b=other.getObjectiveValues().get(keys[k]);
                    weak=weak&&(maximize[k]?b>=a:b<=a);strict=strict||(maximize[k]?b>a:b<a);
                }
                dominated=dominated||(weak&&strict);
            }
            check("Pareto objective non-dominance",!dominated,0,0);
            neqsim.process.processmodel.ProcessSystem replay=model.copy();
            neqsim.process.equipment.stream.StreamInterface input=(neqsim.process.equipment.stream.StreamInterface)replay.getUnit("feed");
            input.setFlowRate(point.getFullResult().getOptimalRate(),"kg/hr");replay.run();process(replay);
            neqsim.process.equipment.compressor.Compressor compressor=(neqsim.process.equipment.compressor.Compressor)replay.getUnit("Export Comp");
            close("Pareto independently copied power replay",(compressor.getPower("MW")-values.get("power"))/Math.max(1e-6,Math.abs(values.get("power"))),1e-5);
            if(values.containsKey("oil_mass_kg_hr")) {
                neqsim.process.equipment.separator.ThreePhaseSeparator separator=(neqsim.process.equipment.separator.ThreePhaseSeparator)replay.getUnit("HP Sep");
                double oilMass=separator.getOilOutStream().getFlowRate("kg/hr");
                close("Pareto oil objective is separator mass kg/hr",(oilMass-values.get("oil_mass_kg_hr"))/Math.max(1.0,oilMass),1e-5);
                check("Pareto oil mass does not exceed feed mass",oilMass<=input.getFlowRate("kg/hr")*(1.0+1e-6),oilMass,input.getFlowRate("kg/hr"));
                double gasVolume=separator.getGasOutStream().getFlowRate("MSm3/day");
                close("Pareto gas objective standard gas volume",gasVolume-values.get("gas_rate"),1e-5);
            }
            optimizer(point.getFullResult());
        }
    }
    static void table(neqsim.process.util.optimizer.MultiScenarioVFPGenerator.VFPTable table) {
        check("nonempty declared diagnostic table",table.getTotalPoints()>0,table.getTotalPoints(),0);
        check("feasibility count within table bounds",table.getFeasibleCount()>=0&&table.getFeasibleCount()<=table.getTotalPoints(),table.getFeasibleCount(),0);
    }
    static void fluid(neqsim.thermo.system.SystemInterface fluid,double rate,double temperature,double pressure) {
        fluid.initProperties();double sum=0;
        for(double value:fluid.getMolarComposition()) {check("fluid finite nonnegative molar fraction",Double.isFinite(value)&&value>=0,value,0);sum+=value;}
        close("fluid composition normalization",sum-1,1e-8);
        close("fluid declared mass-flow normalization",fluid.getFlowRate("kg/hr")-rate,1e-5);
        close("fluid declared temperature",fluid.getTemperature()-temperature,1e-8);
        close("fluid declared pressure",fluid.getPressure()-pressure,1e-8);
        check("fluid positive finite density",Double.isFinite(fluid.getDensity("kg/m3"))&&fluid.getDensity("kg/m3")>0,fluid.getDensity("kg/m3"),0);
    }
}

BookSolutionChecks.destination=Paths.get("C:\\Users\\solbraa\\OneDrive - NTNU\\Documents\\GitHub\\neqsim\\neqsim-paperlab\\books\\production_optimization_oil_gas_2026\\.build\\java_solution_runs\\ch24_production_optimization\\checks.json");
BookSolutionChecks.fence=1;
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
BookSolutionChecks.fence=2;
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
process.run(); BookSolutionChecks.process(process);
CapacityConstraint speedConstraint = new CapacityConstraint("speed", "RPM",
    CapacityConstraint.ConstraintType.HARD).setDesignValue(10000.0).setMaxValue(11000.0).setWarningThreshold(0.9).setDescription("Declared demonstration speed limit").setValueSupplier(() -> compressor.getSpeed());
BookSolutionChecks.fence=3;
compressor.enableAllConstraints();

BookSolutionChecks.fence=4;
process.enableAllConstraints();
BookSolutionChecks.fence=6;

process.disableAllConstraints();


separator.setCapacityAnalysisEnabled(false);
BookSolutionChecks.fence=7;
separator.autoSize(1.2);

BookSolutionChecks.fence=8;
compressor.autoSize(1.2);
compressor.getCompressorChart().setUseCompressorChart(false);
compressor.setSolveSpeed(false);
compressor.setUsePolytropicCalc(true);
for (Map.Entry<String,CapacityConstraint> entry : compressor.getCapacityConstraints().entrySet()) { entry.getValue().setEnabled(entry.getKey().equals("power")); }


BookSolutionChecks.fence=9;
ThrottlingValve valve = new ThrottlingValve("Example valve", feed);
valve.setOutletPressure(50.0);
valve.run();
valve.autoSize(1.2);
BookSolutionChecks.fence=10;
PipeBeggsAndBrills pipeline = new PipeBeggsAndBrills("Example pipe", feed);
pipeline.setLength(1000.0);
pipeline.setDiameter(0.25);
pipeline.setAngle(0.0);
pipeline.run();
pipeline.autoSize(1.2);
BookSolutionChecks.fence=11;
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
BookSolutionChecks.fence=12;

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
process.run(); BookSolutionChecks.process(process);


sep.autoSize(1.2);
comp.autoSize(1.2);
comp.getCompressorChart().setUseCompressorChart(false);
comp.setSolveSpeed(false);
comp.setUsePolytropicCalc(true);
for (Map.Entry<String,CapacityConstraint> entry : comp.getCapacityConstraints().entrySet()) { entry.getValue().setEnabled(entry.getKey().equals("power")); }


logger.info("Sep max util: " + sep.getMaxUtilizationPercent() + "%");
logger.info("Comp max util: " + comp.getMaxUtilizationPercent() + "%");
BookSolutionChecks.process(process);
BookSolutionChecks.fence=14;
comp.setMaximumSpeed(12000.0);  
comp.reinitializeCapacityConstraints();
BookSolutionChecks.process(process);
BookSolutionChecks.fence=15;
BottleneckResult capacityResult = process.findBottleneck();
logger.info("Bottleneck {} utilization {}", capacityResult.getEquipmentName(), capacityResult.getUtilization());
Map<String, Double> utilizationSummary = process.getCapacityUtilizationSummary();
List<String> nearLimit = process.getEquipmentNearCapacityLimit();
boolean anyOverloaded = process.isAnyEquipmentOverloaded();
boolean anyHardViolation = process.isAnyHardLimitExceeded();
List<neqsim.process.equipment.capacity.CapacityConstrainedEquipment> constrained = process.getConstrainedEquipment();
BookSolutionChecks.fence=19;
OptimizationConfig config = new OptimizationConfig(50000.0, 300000.0)  .rateUnit("kg/hr").tolerance(500.0)                          .maxIterations(40)                         .searchMode(SearchMode.BINARY_FEASIBILITY).defaultUtilizationLimit(0.95)             .utilizationLimitForType(Compressor.class, 0.90)  .utilizationLimitForName("HP Separator", 0.92)    .stagnationIterations(5)                   .maxCacheSize(500)                         .enableCaching(true).parallelEvaluations(true)                 .parallelThreads(4);                       
BookSolutionChecks.fence=21;
config.validate();

BookSolutionChecks.fence=22;
ProductionOptimizer optimizer = new ProductionOptimizer();

OptimizationResult result = optimizer.optimize(
    process,       
    feed,          
    config,        
    null,    
    null    
);
BookSolutionChecks.process(process);
BookSolutionChecks.optimizer(result);
BookSolutionChecks.fence=24;
config.swarmSize(20)           .inertiaWeight(0.7)        .cognitiveWeight(1.5)      .socialWeight(1.5)         .randomSeed(42);           
BookSolutionChecks.process(process);
BookSolutionChecks.optimizer(result);
BookSolutionChecks.fence=25;

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
BookSolutionChecks.fence=26;
if (!result.isFeasible()) {
    logger.info(result.getInfeasibilityDiagnosis());
}
BookSolutionChecks.fence=29;
OptimizationSummary optimizationSummary = optimizer.quickOptimize(process, feed, "kg/hr", null);
logger.info("Rate {} {}, feasible {}", optimizationSummary.getMaxRate(), optimizationSummary.getRateUnit(), optimizationSummary.isFeasible());
BookSolutionChecks.fence=30;
ProcessOptimizationEngine engine = new ProcessOptimizationEngine(process);
engine.setFeedStreamName("feed");
engine.setOutletStreamName("Export Comp");
ProcessOptimizationEngine.OptimizationResult engineResult = engine.findMaximumThroughput(65.0, 150.0, 50000.0, 300000.0);
ProcessOptimizationEngine.ConstraintReport report = engine.evaluateAllConstraints();
ProcessOptimizationEngine.SensitivityResult sens = engine.analyzeSensitivity(100000.0, 65.0, 150.0);
ProcessOptimizationEngine.LiftCurveData curve = engine.generateCapacityScreening(new double[]{50.0,65.0,80.0},
    new double[]{343.15}, 150.0, 50000.0, 300000.0);
logger.info("Capacity screening points {}", curve.getPoints().size());
BookSolutionChecks.fence=31;
EquipmentCapacityStrategyRegistry registry = EquipmentCapacityStrategyRegistry.getInstance();
logger.info("Registered capacity strategies: {}", registry.getStrategyCount());
for (EquipmentCapacityStrategy strategy : registry.getAllStrategies()) {
    logger.info("Strategy {}", strategy.getClass().getSimpleName());
}
BookSolutionChecks.fence=36;
OptimizationObjective throughput = new OptimizationObjective("throughput",
    proc -> ((StreamInterface) proc.getUnit("feed")).getFlowRate("kg/hr"), 1.0, ObjectiveType.MAXIMIZE);
OptimizationObjective minPower = new OptimizationObjective("power",
    proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 0.3, ObjectiveType.MINIMIZE);
List<OptimizationObjective> objectives = Arrays.asList(throughput, minPower);
BookSolutionChecks.fence=38;
OptimizationConstraint maxPower = OptimizationConstraint.lessThan("compressor_power",
    proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 25.0,
    ProductionOptimizer.ConstraintSeverity.HARD, 100.0, "Declared power ceiling (MW)");

OptimizationConstraint maxTemperature = OptimizationConstraint.lessThan("discharge_temperature",
    proc -> ((Compressor) proc.getUnit("Export Comp")).getOutletStream().getTemperature("C"), 180.0,
    ProductionOptimizer.ConstraintSeverity.SOFT, 10.0, "Illustrative discharge temperature preference");
List<OptimizationConstraint> constraints = Arrays.asList(maxPower, maxTemperature);
BookSolutionChecks.fence=40;
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



BookSolutionChecks.process(process);
BookSolutionChecks.pareto(pareto,process,new String[]{"throughput","power"},new boolean[]{true,false});
BookSolutionChecks.fence=42;

List<OptimizationObjective> threeObjectives = Arrays.asList(
    new OptimizationObjective("oil_mass_kg_hr", proc ->
        ((ThreePhaseSeparator) proc.getUnit("HP Sep")).getOilOutStream().getFlowRate("kg/hr"),
        1.0, ObjectiveType.MAXIMIZE),
    new OptimizationObjective("gas_rate", proc -> ((ThreePhaseSeparator) proc.getUnit("HP Sep")).getGasOutStream().getFlowRate("MSm3/day"), 1.0, ObjectiveType.MAXIMIZE),
    new OptimizationObjective("power", proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 1.0, ObjectiveType.MINIMIZE));
config.paretoGridSize(3).maxIterations(15);
ParetoResult threeObjectiveResult = optimizer.optimizePareto(process, feed, config, threeObjectives, constraints);
BookSolutionChecks.process(process);
BookSolutionChecks.pareto(threeObjectiveResult,process,new String[]{"oil_mass_kg_hr","gas_rate","power"},new boolean[]{true,true,false});
BookSolutionChecks.fence=43;
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
BookSolutionChecks.process(process);
for(ScenarioRequest request:scenarios){BookSolutionChecks.process(request.getProcess());}
BookSolutionChecks.fence=45;

comp.getCompressorChart().setUseCompressorChart(false);
comp.setOutletPressure(150.0);
process.run(); BookSolutionChecks.process(process);
CompressorChartGenerator chartGen = new CompressorChartGenerator(comp);
chartGen.generateCompressorChart("midpoint");
comp.setMaximumSpeed(comp.getSpeed() * 1.15);

BookSolutionChecks.fence=46;
comp.getCompressorChart().setUseCompressorChart(true);
comp.autoSize(1.2);
comp.getCompressorChart().setUseCompressorChart(false);
comp.setSolveSpeed(false);
comp.setUsePolytropicCalc(true);
for (Map.Entry<String,CapacityConstraint> entry : comp.getCapacityConstraints().entrySet()) { entry.getValue().setEnabled(entry.getKey().equals("power")); }


Map<String, CapacityConstraint> chartConstraints = comp.getCapacityConstraints();



BookSolutionChecks.fence=47;

comp.setMaximumSpeed(12000.0);


comp.reinitializeCapacityConstraints();


BookSolutionChecks.fence=49;
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
BookSolutionChecks.fence=50;
config.stagnationIterations(5);  
BookSolutionChecks.fence=51;
config.initialGuess(new double[]{180000.0});  
BookSolutionChecks.fence=52;
config.enableCaching(true);
config.maxCacheSize(500);  
BookSolutionChecks.fence=53;
config.parallelEvaluations(true);
config.parallelThreads(8);  
BookSolutionChecks.fence=54;
config.randomSeed(42);       
config.useFixedSeed(true);   
BookSolutionChecks.fence=55;
config.useFixedSeed(false);  
BookSolutionChecks.fence=56;
config.defaultUtilizationLimit(0.60);

config.utilizationLimitForName("Export Comp", 0.85);
BookSolutionChecks.fence=57;
OptimizationResult result = optimizer.optimize(process, feed, config, objectives, constraints);
for (IterationRecord entry : result.getIterationHistory()) {
    logger.info("Rate {}, score {}, feasible {}", entry.getRate(), entry.getScore(), entry.isFeasible());
}
String csv = result.exportIterationHistoryAsCsv();
String json = result.exportIterationHistoryAsJson();
BookSolutionChecks.fence=58;
ProcessSimulationEvaluator evaluator = new ProcessSimulationEvaluator(process);
evaluator.addParameterWithSetter("flow", (proc, value) -> ((StreamInterface) proc.getUnit("feed")).setFlowRate(value, "kg/hr"), 50000.0, 300000.0, "kg/hr");
evaluator.addObjective("throughput", proc -> ((StreamInterface) proc.getUnit("feed")).getFlowRate("kg/hr"), ProcessSimulationEvaluator.ObjectiveDefinition.Direction.MAXIMIZE);
evaluator.addConstraintUpperBound("power", proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 25.0);
ProcessSimulationEvaluator.EvaluationResult evaluation = evaluator.evaluate(new double[]{200000.0});
logger.info("Objective {}, feasible {}, converged {}", evaluation.getObjective(), evaluation.isFeasible(), evaluation.isSimulationConverged());
BookSolutionChecks.fence=61;
SQPoptimizer sqp = new SQPoptimizer(1);

sqp.setObjectiveFunction(x -> -x[0]);
sqp.addInequalityConstraint(x -> {
    feed.setFlowRate(x[0] * 100000.0, "kg/hr");
    process.run(); BookSolutionChecks.process(process);
    return (25.0 - comp.getPower("MW")) / 25.0;
});
sqp.setVariableBounds(new double[]{0.5}, new double[]{3.0});
sqp.setInitialPoint(new double[]{1.0});
SQPoptimizer.OptimizationResult sqpResult = sqp.solve();
feed.setFlowRate(sqpResult.getOptimalPoint()[0] * 100000.0, "kg/hr");
process.run(); BookSolutionChecks.process(process);
logger.info("SQP converged {}, final power {} MW", sqpResult.isConverged(), comp.getPower("MW"));
BookSolutionChecks.process(process);
BookSolutionChecks.close("SQP bounded linear throughput optimum",sqpResult.getOptimalPoint()[0]-3.0,1e-4);
BookSolutionChecks.check("SQP independently replayed power constraint",comp.getPower("MW")<=25.00001,comp.getPower("MW"),25.00001);
BookSolutionChecks.fence=63;
import neqsim.process.util.reconciliation.*;
SteadyStateDetector detector = new SteadyStateDetector();
SteadyStateVariable pressure = detector.addVariable("pressure").setUnit("bara");
for (int sample = 0; sample < 60; sample++) { pressure.addValue(65.0); }
SteadyStateResult steady = detector.evaluate();
logger.info("Synthetic constant-pressure window at steady state: {}", steady.isAtSteadyState());
BookSolutionChecks.check("constant synthetic detector signal accepted",steady.isAtSteadyState(),0,0);
BookSolutionChecks.fence=64;
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
for(double r:reconciliation.getConstraintResidualsAfter()){BookSolutionChecks.close("reconciled mass constraint",r,1e-6);}
double[] measuredValues={200000,150000,48000,5000}; double[] variances={4000000,2250000,1000000,250000}; double[] signs={1,-1,-1,-1}; String[] variableNames={"feed","gas","oil","water"}; for(int k=0;k<4;k++){double expected=measuredValues[k]+variances[k]*signs[k]*3000.0/7500000.0; BookSolutionChecks.close("closed-form weighted reconciliation "+variableNames[k],reconciler.getVariable(variableNames[k]).getReconciledValue()-expected,1e-6);}
BookSolutionChecks.close("chi-square from normalized independent residual",reconciliation.getChiSquareStatistic()-1.2,1e-8);
BookSolutionChecks.fence=65;
for (ReconciliationVariable suspect : reconciliation.getGrossErrors()) {
    logger.warn("Suspect {} normalized residual {}",suspect.getName(),suspect.getNormalizedResidual());
}
for(double r:reconciliation.getConstraintResidualsAfter()){BookSolutionChecks.close("reconciled mass constraint",r,1e-6);}
BookSolutionChecks.fence=79;
config.defaultUtilizationLimit(0.95)                    .utilizationLimitForType(Compressor.class, 0.88)    .utilizationLimitForType(ThrottlingValve.class, 0.80) .utilizationLimitForName("Old Compressor K-101", 0.82); 
BookSolutionChecks.fence=81;
config.stagnationIterations(5);  
BookSolutionChecks.fence=82;
config.rejectInvalidSimulations(true);


/exit
