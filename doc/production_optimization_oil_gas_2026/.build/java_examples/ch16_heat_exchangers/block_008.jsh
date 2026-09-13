import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
Logger logger = LogManager.getLogger("BookChapter16");
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
import neqsim.process.equipment.heatexchanger.Heater;
Stream feedStream = feed;
// Java: Set maximum design duty for a heater
Heater heater = new Heater("Inlet Heater", feedStream);
heater.setOutletTemperature(273.15 + 80.0);
process.add(heater);
process.run();

// Initialize mechanical design and set constraint
heater.initMechanicalDesign();
heater.getMechanicalDesign().setMaxDesignDuty(5000000.0);  // 5 MW max
