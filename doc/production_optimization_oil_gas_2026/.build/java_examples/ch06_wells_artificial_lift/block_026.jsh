LoopedPipeNetwork variant = new LoopedPipeNetwork("Topology illustration");
variant.setFluidTemplate(fluid);
variant.addSourceNode("Platform", 250.0, 0.0);
// Independent injection topology illustration
variant.addJunctionNode("WI-Wellhead");
variant.addJunctionNode("WI-BH");
variant.addSourceNode("WI-Reservoir", 180.0, 0.0);
variant.addPipe("Platform", "WI-Wellhead", "WI-Flowline", 10000.0, 0.2032);
variant.addTubing("WI-Wellhead", "WI-BH", "WI-Tubing", 3000.0, 0.1778, 90.0);
variant.addWellIPR("WI-BH", "WI-Reservoir", "WI-IPR", 25.0 * 1000.0 / 86400.0 / 1e5, false);
