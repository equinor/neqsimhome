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
String bookFence = "BOOK_FENCE_7";
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

import neqsim.process.controllerdevice.*;
Stream feedStream = feed;

ThrottlingValve valve = new ThrottlingValve("V-100", feedStream);

ControllerDeviceBaseClass levelController = new ControllerDeviceBaseClass();
levelController.setKp(2.0);
levelController.setTi(120.0);
levelController.setControllerSetPoint(0.5);

ControllerDeviceBaseClass pressureController = new ControllerDeviceBaseClass();
pressureController.setKp(1.5);
pressureController.setControllerSetPoint(50.0);


valve.addController("LC-100", levelController);
valve.addController("PC-200", pressureController);


ControllerDeviceInterface lc = valve.getController("LC-100");
Collection<ControllerDeviceInterface> all = valve.getControllers();
String bookFence = "BOOK_FENCE_8";




String bookFence = "BOOK_FENCE_9";

ProcessAutomation auto = process.getAutomation();


List<String> units = auto.getUnitList();  
String eqType = auto.getEquipmentType("HP Sep");  


List<SimulationVariable> vars = auto.getVariableList("HP Sep");
for (SimulationVariable v : vars) {
    logger.info(v.getAddress() + " [" + v.getType() + "] " + v.getDescription());
    
    
}


double T = auto.getVariableValue("HP Sep.gasOutStream.temperature", "C");
double P = auto.getVariableValue("HP Sep.pressure", "bara");
double flow = auto.getVariableValue("HP Sep.gasOutStream.flowRate", "kg/hr");


auto.setVariableValue("Compressor.outletPressure", 150.0, "bara");
process.run();  
String bookFence = "BOOK_FENCE_10";
ProcessModel plant = new ProcessModel();
plant.add("Separation", process);
ProcessAutomation plantAuto = plant.getAutomation();
List<String> areas = plantAuto.getAreaList();  


double T = plantAuto.getVariableValue("Separation::HP Sep.gasOutStream.temperature", "C");
plantAuto.setVariableValue("Separation::Compressor.outletPressure", 170.0, "bara");
plant.run();
String bookFence = "BOOK_FENCE_11";
ProcessAutomation auto = process.getAutomation();


String result = auto.getVariableValueSafe("hp separator.temperature", "C");






String setResult = auto.setVariableValueSafe("Compressor.outletPressure", 150.0, "bara");



String badResult = auto.setVariableValueSafe("Compressor.outletPressure", -50.0, "bara");


String bookFence = "BOOK_FENCE_12";
AutomationDiagnostics diag = auto.getDiagnostics();
String report = diag.getLearningReport();

String bookFence = "BOOK_FENCE_END";
/exit
