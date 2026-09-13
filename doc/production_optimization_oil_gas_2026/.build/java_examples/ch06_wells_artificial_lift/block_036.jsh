LoopedPipeNetwork variant = new LoopedPipeNetwork("Topology illustration");
variant.setFluidTemplate(fluid);
for (String node : Arrays.asList("Down-A", "Down-B", "Down-C")) { variant.addJunctionNode(node); }
// Add the explicitly named junctions before their connections.
for (String node : Arrays.asList("Down-D", "Manifold-1", "Manifold-2")) {
    variant.addJunctionNode(node);
}
variant.addPipe("Down-A", "Manifold-1", "FL-A1", 5000.0, 0.2032);
variant.addPipe("Down-B", "Manifold-2", "FL-B1", 4000.0, 0.2032);
variant.addPipe("Down-C", "Manifold-1", "FL-A2", 6000.0, 0.2032);
variant.addPipe("Down-D", "Manifold-2", "FL-B2", 3500.0, 0.2032);

// Crossover creates the loop
variant.addPipe("Manifold-1", "Manifold-2", "Crossover",
    2000.0, 0.1524);  // 6-inch tie-in
