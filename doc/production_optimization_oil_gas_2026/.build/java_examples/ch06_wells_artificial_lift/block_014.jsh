// Production choke with Kv = 25 m3/hr/sqrt(bar), 60% open
network.addJunctionNode("Downstream-A");
network.addChoke("WH-A", "Downstream-A", "Choke-A",
    25.0,    // Kv [m3/hr/sqrt(bar)]
    60.0);   // opening [%]

// Adjust choke opening later
NetworkPipe choke = network.getPipe("Choke-A");
choke.setChokeOpening(75.0);  // Open to 75%
