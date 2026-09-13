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
String bookFence = "BOOK_FENCE_2";
import neqsim.process.util.optimizer.FluidMagicInput;
import neqsim.thermo.system.SystemInterface;
import neqsim.thermo.system.SystemSrkEos;


SystemInterface refFluid = new SystemSrkEos(273.15 + 80.0, 200.0);
refFluid.addComponent("nitrogen", 0.5);
refFluid.addComponent("CO2", 2.0);
refFluid.addComponent("methane", 65.0);
refFluid.addComponent("ethane", 8.0);
refFluid.addComponent("propane", 5.0);
refFluid.addComponent("i-butane", 1.5);
refFluid.addComponent("n-butane", 3.0);
refFluid.addComponent("n-pentane", 2.0);
refFluid.addComponent("n-hexane", 1.5);
refFluid.addComponent("n-heptane", 4.0);
refFluid.addComponent("n-octane", 3.5);
refFluid.addComponent("n-decane", 2.0);
refFluid.addComponent("water", 2.0);
refFluid.setMixingRule("classic");
refFluid.setMultiPhaseCheck(true);


FluidMagicInput input = FluidMagicInput.builder().referenceFluid(refFluid).gorRange(200, 8000).waterCutRange(0.02, 0.50).numberOfGORPoints(6).numberOfWaterCutPoints(5).build();

input.separateToStandardConditions();
String bookFence = "BOOK_FENCE_3";
import neqsim.process.util.optimizer.RecombinationFlashGenerator;

RecombinationFlashGenerator flashGen = new RecombinationFlashGenerator(input);


SystemInterface fluid = flashGen.generateFluid(
    1500.0,     
    0.20,       
    10000.0,    
    353.15,     
    50.0);      


String stats = flashGen.getCacheStatistics();
String bookFence = "BOOK_FENCE_4";
import neqsim.process.util.optimizer.MultiScenarioVFPGenerator;
import neqsim.process.processmodel.ProcessSystem;
import java.util.function.Supplier;


Supplier<ProcessSystem> processFactory = () -> {
    
    SystemInterface fluid = new SystemSrkEos(273.15 + 80.0, 200.0);
    fluid.addComponent("methane", 70.0);
    fluid.addComponent("ethane", 8.0);
    fluid.addComponent("propane", 4.0);
    fluid.addComponent("n-butane", 2.0);
    fluid.addComponent("n-heptane", 8.0);
    fluid.addComponent("n-decane", 5.0);
    fluid.addComponent("water", 3.0);
    fluid.setMixingRule("classic");
    fluid.setMultiPhaseCheck(true);

    Stream feed = new Stream("Feed", fluid);
    feed.setFlowRate(10000.0, "kg/hr");
    PipeBeggsAndBrills tubing = new PipeBeggsAndBrills("Tubing", feed);
    tubing.setLength(2500.0);
    tubing.setAngle(90.0);
    tubing.setDiameter(0.1016);
    tubing.setNumberOfIncrements(30);

    PipeBeggsAndBrills flowline = new PipeBeggsAndBrills("Flowline", tubing.getOutletStream());
    flowline.setLength(10000.0);
    flowline.setAngle(0.0);
    flowline.setDiameter(0.2032);
    flowline.setNumberOfIncrements(20);

    ProcessSystem process = new ProcessSystem();
    process.add(feed);
    process.add(tubing);
    process.add(flowline);
    process.add(new Stream("Export Outlet", flowline.getOutletStream()));
    return process;
};


MultiScenarioVFPGenerator vfpGen = new MultiScenarioVFPGenerator(
    processFactory,
    "Feed",        
    "Export Outlet" 
);


vfpGen.setFlashGenerator(flashGen);


vfpGen.setFlowRateUnit("kg/hr");
vfpGen.setInletTemperature(358.15);
vfpGen.setFlowRates(new double[]{5000.0,10000.0,20000.0});
vfpGen.setOutletPressures(new double[]{30.0,50.0});
vfpGen.setWaterCuts(new double[]{0.05});
vfpGen.setGORs(new double[]{300.0,1000.0});





vfpGen.setMinInletPressure(20.0);    
vfpGen.setMaxInletPressure(350.0);   
vfpGen.setPressureTolerance(0.5);    


vfpGen.setEnableParallel(false);
vfpGen.setNumberOfWorkers(8);


MultiScenarioVFPGenerator.VFPTable table = vfpGen.generateVFPTable();
String bookFence = "BOOK_FENCE_5";

double requiredInletPressure = table.getBHP(2, 1, 0, 1);



int feasible = table.getFeasibleCount();
int total = table.getTotalPoints();
logger.info(String.format("Feasible: %d/%d (%.1f%%)%n",
    feasible, total, 100.0 * feasible / total));


table.printSlice(0, 1);  
String bookFence = "BOOK_FENCE_6";

java.nio.file.Files.write(Paths.get("production_screening.txt"),
    vfpGen.toDiagnosticString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
String bookFence = "BOOK_FENCE_7";

input.setGorSpacing(FluidMagicInput.GORSpacing.LOGARITHMIC);
input.setGORRange(200, 10000);
input.setNumberOfGORPoints(8);

String bookFence = "BOOK_FENCE_8";
input.setWaterCutRange(0.02, 0.60);
input.setNumberOfWaterCutPoints(5);

String bookFence = "BOOK_FENCE_9";
vfpGen.setMinInletPressure(15.0);     
vfpGen.setMaxInletPressure(400.0);    
vfpGen.setPressureTolerance(0.5);     
String bookFence = "BOOK_FENCE_10";

ProcessSystem testProcess = processFactory.get();
testProcess.run();
double testPressure = ((StreamInterface) testProcess.getUnit("Export Outlet")).getPressure("bara");
logger.info("Test outlet pressure: " + testPressure + " bara");


SystemInterface testFluid = flashGen.generateFluid(1000.0, 0.20, 10000.0, 353.15, 50.0);
testFluid.initProperties();
logger.info("Test fluid components: " + testFluid.getNumberOfComponents());
logger.info("Test fluid density: " + testFluid.getDensity("kg/m3") + " kg/m3");
String bookFence = "BOOK_FENCE_11";

for (double diameter : new double[]{0.076, 0.102}) {
    ProcessSystem diameterCase = processFactory.get();
    ((PipeBeggsAndBrills) diameterCase.getUnit("Tubing")).setDiameter(diameter);
    MultiScenarioVFPGenerator diameterGenerator = new MultiScenarioVFPGenerator(diameterCase, "Feed", "Export Outlet");
    diameterGenerator.setFlashGenerator(flashGen);
    diameterGenerator.setFlowRateUnit("kg/hr");
    diameterGenerator.setInletTemperature(358.15);
    diameterGenerator.setFlowRates(new double[]{5000.0,10000.0,20000.0});
    diameterGenerator.setOutletPressures(new double[]{30.0,50.0});
    diameterGenerator.setWaterCuts(new double[]{0.05});
    diameterGenerator.setGORs(new double[]{300.0,1000.0});
    diameterGenerator.setMinInletPressure(20.0);
    diameterGenerator.setMaxInletPressure(350.0);
    diameterGenerator.setEnableParallel(false);
    MultiScenarioVFPGenerator.VFPTable diameterTable = diameterGenerator.generateVFPTable();
    logger.info("Internal diameter {} m: {} of {} feasible sampled points", diameter,
        diameterTable.getFeasibleCount(), diameterTable.getTotalPoints());
}
String bookFence = "BOOK_FENCE_12";
import neqsim.process.util.optimizer.FluidMagicInput;
import neqsim.process.util.optimizer.RecombinationFlashGenerator;
import neqsim.process.util.optimizer.MultiScenarioVFPGenerator;
import neqsim.process.equipment.stream.Stream;
import neqsim.process.equipment.pipeline.PipeBeggsAndBrills;
import neqsim.process.processmodel.ProcessSystem;
import neqsim.thermo.system.SystemInterface;
import neqsim.thermo.system.SystemSrkEos;
import java.util.function.Supplier;

public class VFPGenerationExample {
    private static final org.apache.logging.log4j.Logger logger = org.apache.logging.log4j.LogManager.getLogger(VFPGenerationExample.class);

    /** Process factory that creates a fresh well + flowline model. */
    static Supplier<ProcessSystem> createProcessFactory() {
        return () -> {
            SystemInterface fluid = new SystemSrkEos(273.15 + 85.0, 200.0);
            fluid.addComponent("nitrogen", 0.4);
            fluid.addComponent("CO2", 1.8);
            fluid.addComponent("methane", 68.0);
            fluid.addComponent("ethane", 7.5);
            fluid.addComponent("propane", 4.5);
            fluid.addComponent("i-butane", 1.0);
            fluid.addComponent("n-butane", 2.5);
            fluid.addComponent("n-pentane", 1.5);
            fluid.addComponent("n-hexane", 1.2);
            fluid.addComponent("n-heptane", 4.5);
            fluid.addComponent("n-octane", 3.5);
            fluid.addComponent("n-decane", 2.1);
            fluid.addComponent("water", 1.5);
            fluid.setMixingRule("classic");
            fluid.setMultiPhaseCheck(true);

            Stream feed = new Stream("Feed", fluid);
    feed.setFlowRate(10000.0, "kg/hr");
            feed.setFlowRate(30000.0, "kg/hr");
            feed.setTemperature(85.0, "C");
            feed.setPressure(200.0, "bara");

            
            PipeBeggsAndBrills tubing =
                new PipeBeggsAndBrills("Tubing", feed);
            tubing.setLength(2800.0);
            tubing.setAngle(90.0);
            tubing.setDiameter(0.1016);
            tubing.setPipeWallRoughness(2.5e-5);
            tubing.setNumberOfIncrements(25);

            
            PipeBeggsAndBrills flowline =
                new PipeBeggsAndBrills("Export", tubing.getOutletStream());
            flowline.setLength(12000.0);
            flowline.setAngle(0.0);
            flowline.setDiameter(0.2032);
            flowline.setPipeWallRoughness(4.5e-5);
            flowline.setNumberOfIncrements(20);

            ProcessSystem process = new ProcessSystem();
            process.add(feed);
            process.add(tubing);
            process.add(flowline);
    process.add(new Stream("Export Outlet", flowline.getOutletStream()));
            return process;
        };
    }

    public static void main(String[] args) throws Exception {
        
        SystemInterface refFluid = new SystemSrkEos(273.15 + 85.0, 200.0);
        refFluid.addComponent("nitrogen", 0.4);
        refFluid.addComponent("CO2", 1.8);
        refFluid.addComponent("methane", 68.0);
        refFluid.addComponent("ethane", 7.5);
        refFluid.addComponent("propane", 4.5);
        refFluid.addComponent("i-butane", 1.0);
        refFluid.addComponent("n-butane", 2.5);
        refFluid.addComponent("n-pentane", 1.5);
        refFluid.addComponent("n-hexane", 1.2);
        refFluid.addComponent("n-heptane", 4.5);
        refFluid.addComponent("n-octane", 3.5);
        refFluid.addComponent("n-decane", 2.1);
        refFluid.addComponent("water", 1.5);
        refFluid.setMixingRule("classic");
        refFluid.setMultiPhaseCheck(true);

        
        FluidMagicInput input = new FluidMagicInput(refFluid);
        input.setGORRange(300, 8000);
        input.setWaterCutRange(0.05, 0.55);
        input.setNumberOfGORPoints(6);
        input.setNumberOfWaterCutPoints(5);
        input.setGorSpacing(FluidMagicInput.GORSpacing.LOGARITHMIC);
        input.separateToStandardConditions();

        
        RecombinationFlashGenerator flashGen =
            new RecombinationFlashGenerator(input);

        
        MultiScenarioVFPGenerator vfpGen = new MultiScenarioVFPGenerator(
            createProcessFactory(), "Feed", "Export Outlet");
        vfpGen.setFlashGenerator(flashGen);

        vfpGen.setFlowRateUnit("kg/hr");
vfpGen.setInletTemperature(358.15);
vfpGen.setFlowRates(new double[]{5000.0,10000.0,20000.0});
vfpGen.setOutletPressures(new double[]{30.0,50.0});
vfpGen.setWaterCuts(new double[]{0.05});
vfpGen.setGORs(new double[]{300.0,1000.0});
        
        
        

        vfpGen.setMinInletPressure(20.0);
        vfpGen.setMaxInletPressure(350.0);
        vfpGen.setPressureTolerance(0.5);
        vfpGen.setEnableParallel(false);
        vfpGen.setNumberOfWorkers(8);

        
        MultiScenarioVFPGenerator.VFPTable table =
            vfpGen.generateVFPTable();

        logger.info(String.format("Feasible: %d/%d%n",
            table.getFeasibleCount(), table.getTotalPoints()));

        
        table.printSlice(0, 1);  

        
        java.nio.file.Files.write(java.nio.file.Paths.get("production_screening.txt"),
            vfpGen.toDiagnosticString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
        logger.info("Process screening diagnostics exported to production_screening.txt");
    }
}
VFPGenerationExample.main(new String[0]);
String bookFence = "BOOK_FENCE_END";
/exit
