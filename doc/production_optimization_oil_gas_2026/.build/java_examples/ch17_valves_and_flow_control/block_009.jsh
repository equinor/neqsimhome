import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
Logger logger = LogManager.getLogger("BookChapter17");
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
import neqsim.process.equipment.valve.ThrottlingValve;
// Java: Auto-size valve with 20% design margin
ThrottlingValve valve = new ThrottlingValve("PV-100", feed);
valve.setOutletPressure(60.0, "bara");
process.add(valve);
process.run();

// autoSize calculates: designCv = operatingCv × (1 + margin)
valve.autoSize(1.20);  // 20% design margin

// The valve now has constraints attached
double designCv = valve.getMechanicalDesign().getMaxDesignCv();
double designFlow = valve.getMechanicalDesign().getMaxDesignVolumeFlow();
