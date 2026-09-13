import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
Logger logger = LogManager.getLogger("BookChapter6");
import neqsim.process.equipment.network.LoopedPipeNetwork;
import neqsim.process.equipment.network.LoopedPipeNetwork.*;
import neqsim.thermo.system.SystemInterface;
import neqsim.thermo.system.SystemSrkEos;

// Create a fluid template for the network
SystemInterface gas = new SystemSrkEos(273.15 + 80.0, 200.0);
gas.addComponent("methane", 0.80);
gas.addComponent("ethane", 0.08);
gas.addComponent("propane", 0.04);
gas.addComponent("n-butane", 0.02);
gas.addComponent("n-heptane", 0.04);
gas.addComponent("water", 0.02);
gas.setMixingRule("classic");
gas.setMultiPhaseCheck(true);

// Create the network
LoopedPipeNetwork network = new LoopedPipeNetwork("Production Network");
network.setFluidTemplate(gas);
