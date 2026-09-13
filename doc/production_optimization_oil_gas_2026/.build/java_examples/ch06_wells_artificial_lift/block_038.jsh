LoopedPipeNetwork variant = new LoopedPipeNetwork("Topology illustration");
variant.setFluidTemplate(fluid);
// Pressure regulator maintaining 20 bar downstream
variant.addSourceNode("HP-Header", 40.0, 0.0);
variant.addJunctionNode("LP-Header");
NetworkPipe reg = variant.addPipe("HP-Header", "LP-Header",
    "PRV-001", 1.0, 0.1016);
reg.setElementType(NetworkElementType.REGULATOR);
reg.setRegulatorSetPoint(20.0e5);  // 20 bara in Pa

