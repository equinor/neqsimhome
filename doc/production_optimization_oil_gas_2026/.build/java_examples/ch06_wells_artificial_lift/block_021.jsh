// Apply gas lift to Well A: 5000 kg/hr of lift gas
network.setGasLift("Tubing-A", 5000.0);  // kg/hr

// Solve again to see the effect
network.run();
