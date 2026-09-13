LoopedPipeNetwork variant = new LoopedPipeNetwork("Topology illustration");
variant.setFluidTemplate(fluid);
// Compressor proxy: a liquid booster requires an actual pump model.
variant.addJunctionNode("Manifold");
variant.addJunctionNode("Boosted-Manifold");
NetworkPipe booster = variant.addPipe("Manifold", "Boosted-Manifold",
    "Subsea Booster", 10.0, 0.254);
booster.setElementType(NetworkElementType.COMPRESSOR);
booster.setCompressorEfficiency(0.72);
booster.setCompressorSpeed(4500.0);  // RPM

