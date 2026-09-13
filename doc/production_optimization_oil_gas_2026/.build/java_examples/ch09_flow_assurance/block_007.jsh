import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
Logger logger = LogManager.getLogger("BookChapter9");
import neqsim.thermo.system.SystemSrkEos;
import neqsim.process.equipment.stream.Stream;
import neqsim.process.processmodel.ProcessSystem;
import neqsim.process.equipment.capacity.CapacityConstraint;
import neqsim.process.util.optimizer.ProductionOptimizer;
import java.util.*;
SystemSrkEos fluid = new SystemSrkEos(313.15, 80.0);
fluid.addComponent("methane", 0.80);
fluid.addComponent("ethane", 0.10);
fluid.addComponent("n-heptane", 0.08);
fluid.addComponent("water", 0.02);
fluid.setMixingRule("classic");
fluid.setMultiPhaseCheck(true);
Stream feed = new Stream("Feed", fluid);
feed.setFlowRate(20000.0, "kg/hr");
ProcessSystem process = new ProcessSystem();
process.add(feed);
process.run();
import neqsim.process.equipment.pipeline.PipeBeggsAndBrills;
import neqsim.process.equipment.network.LoopedPipeNetwork;
// Java: Auto-size pipeline with 20% design margin
PipeBeggsAndBrills pipeline = new PipeBeggsAndBrills("Export Pipeline", feed);
pipeline.setLength(25000.0);  // 25 km
pipeline.setElevation(-200.0);  // outlet below inlet
pipeline.setDiameter(0.254);  // 10-inch initial guess
process.add(pipeline);
process.run();

// Auto-size: finds minimum diameter satisfying constraints + margin
pipeline.autoSize(1.20);  // 20% design margin on velocity

pipeline.initMechanicalDesign();
// The pipeline now carries constraint metadata
double designVelocity = pipeline.getMechanicalDesign().getMaxDesignVelocity();
double designDP = pipeline.getMechanicalDesign().getMaxDesignPressureDrop();
