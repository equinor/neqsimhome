import neqsim.process.equipment.network.LoopedPipeNetwork;
import neqsim.process.equipment.network.LoopedPipeNetwork.*;
import neqsim.thermo.system.SystemInterface;
import neqsim.thermo.system.SystemSrkEos;

// Step 1: Fluid template
SystemInterface fluid = new SystemSrkEos(273.15 + 80.0, 200.0);
fluid.addComponent("nitrogen", 0.5);
fluid.addComponent("CO2", 1.5);
fluid.addComponent("methane", 72.0);
fluid.addComponent("ethane", 8.0);
fluid.addComponent("propane", 4.5);
fluid.addComponent("i-butane", 1.0);
fluid.addComponent("n-butane", 2.0);
fluid.addComponent("n-pentane", 1.5);
fluid.addComponent("n-hexane", 1.0);
fluid.addComponent("n-heptane", 4.0);
fluid.addComponent("n-octane", 2.5);
fluid.addComponent("water", 1.5);
fluid.setMixingRule("classic");
fluid.setMultiPhaseCheck(true);

LoopedPipeNetwork network = new LoopedPipeNetwork("Subsea Field");
network.setFluidTemplate(fluid);

// Step 2: Source nodes (reservoirs)
network.addSourceNode("Res-A", 250.0, 0.0);
network.addSourceNode("Res-B", 220.0, 0.0);
network.addSourceNode("Res-C", 200.0, 0.0);

// Step 3: Junction nodes
network.addJunctionNode("BH-A");
network.addJunctionNode("BH-B");
network.addJunctionNode("BH-C");
network.addJunctionNode("WH-A");
network.addJunctionNode("WH-B");
network.addJunctionNode("WH-C");
network.addJunctionNode("Down-A");
network.addJunctionNode("Down-B");
network.addJunctionNode("Down-C");
network.addJunctionNode("Subsea-Manifold");

// Step 4: Sink node (platform)
network.addSinkNode("Platform", 0.0);
NetworkNode platform = network.getNode("Platform");
platform.setPressure(35.0e5);  // 35 bara back-pressure
platform.setPressureFixed(true);

// Step 5: Elements — IPRs
network.addWellIPR("Res-A", "BH-A", "IPR-A", 15.0 * 800.0 / 86400.0 / 1e5, false);
network.addWellIPRVogel("Res-B", "BH-B", "IPR-B", 80.0);
network.addWellIPRFetkovich("Res-C", "BH-C", "IPR-C", 2.0e-8, 0.80);

// Step 5: Elements — Tubing
network.addTubing("BH-A", "WH-A", "Tubing-A", 2500.0, 0.1016, 90.0);
network.addTubing("BH-B", "WH-B", "Tubing-B", 3000.0, 0.1016, 75.0);
network.addTubing("BH-C", "WH-C", "Tubing-C", 2000.0, 0.1016, 90.0);

// Step 5: Elements — Chokes
network.addChoke("WH-A", "Down-A", "Choke-A", 25.0, 80.0);
network.addChoke("WH-B", "Down-B", "Choke-B", 30.0, 70.0);
network.addChoke("WH-C", "Down-C", "Choke-C", 20.0, 90.0);

// Step 5: Elements — Gathering flowlines (multiphase)
NetworkPipe fl_a = network.addPipe("Down-A", "Subsea-Manifold",
    "Flowline-A", 5000.0, 0.2032);
fl_a.setElementType(NetworkElementType.MULTIPHASE_PIPE);
fl_a.setMultiphaseSegments(15);

NetworkPipe fl_b = network.addPipe("Down-B", "Subsea-Manifold",
    "Flowline-B", 8000.0, 0.2032);
fl_b.setElementType(NetworkElementType.MULTIPHASE_PIPE);
fl_b.setMultiphaseSegments(20);

NetworkPipe fl_c = network.addPipe("Down-C", "Subsea-Manifold",
    "Flowline-C", 3000.0, 0.2032);
fl_c.setElementType(NetworkElementType.MULTIPHASE_PIPE);
fl_c.setMultiphaseSegments(10);

// API assembly only: no elevation profile is supplied for this nominal riser.
// Step 5: Elements — Riser
NetworkPipe riser = network.addPipe("Subsea-Manifold", "Platform",
    "Production Riser", 1500.0, 0.254);
riser.setElementType(NetworkElementType.MULTIPHASE_PIPE);
riser.setMultiphaseSegments(15);

// Step 6: Solver configuration
network.setSolverType(SolverType.NEWTON_RAPHSON);
network.setTolerance(1e-6);
network.setMaxIterations(100);

// Step 7: Solve
network.run();

// Step 7: Results
Map<String, Object> summary = network.getSolutionSummary();
logger.info("Converged: " + summary.get("converged"));
logger.info("Iterations: " + summary.get("iterations"));
logger.info("Total production: {} kg/s", network.getTotalSinkFlow());
