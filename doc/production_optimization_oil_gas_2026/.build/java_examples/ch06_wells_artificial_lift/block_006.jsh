// Multiphase gathering line
NetworkPipe gatherLine = network.addPipe("WH-A", "Subsea-Manifold",
    "Gathering Line A", 5000.0, 0.2032);  // 8-inch, 5 km
gatherLine.setElementType(NetworkElementType.MULTIPHASE_PIPE);
gatherLine.setMultiphaseSegments(20);
gatherLine.setRoughness(4.5e-5);
