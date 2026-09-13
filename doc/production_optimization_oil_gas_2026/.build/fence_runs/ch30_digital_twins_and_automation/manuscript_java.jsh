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
String bookFence = "BOOK_FENCE_24";
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


ProcessSystemState state = ProcessSystemState.fromProcessSystem(process);
state.setName("Gas Processing — Q4 2025 Calibration");
state.setVersion("1.2.0");
state.saveToFile("model_q4_2025.json");      
state.saveToCompressedFile("model_q4_2025.json.gz");  


ProcessSystemState loaded = ProcessSystemState.loadFromFile("model_q4_2025.json");
ProcessSystemState.ValidationResult result = loaded.validate();
if (result.isValid()) {
    logger.info("State is valid and can be restored");
}
String bookFence = "BOOK_FENCE_25";
ProcessModel plant = new ProcessModel();
plant.add("Processing", process);

ProcessModelState modelState = ProcessModelState.fromProcessModel(plant);
modelState.setName("Platform X — Annual Review");
modelState.setVersion("3.0.0");
modelState.saveToFile("platform_x_v3.json");
String bookFence = "BOOK_FENCE_26";

ProcessModelState v1 = ProcessModelState.loadFromFile("platform_x_v3.json");
ProcessModelState v2 = ProcessModelState.fromProcessModel(plant);
v2.setVersion("3.0");

ProcessModelState.ModelDiff diff = ProcessModelState.compare(v1, v2);

if (diff.hasChanges()) {
    
    for (String param : diff.getModifiedParameters().keySet()) {
        logger.info("Modified: " + param);
    }
    
    for (String added : diff.getAddedEquipment()) {
        logger.info("Added: " + added);
    }
    for (String removed : diff.getRemovedEquipment()) {
        logger.info("Removed: " + removed);
    }
}
String bookFence = "BOOK_FENCE_27";

byte[] bytes = modelState.toCompressedBytes();



ProcessModelState restored = ProcessModelState.fromCompressedBytes(bytes);
String bookFence = "BOOK_FENCE_END";
/exit
