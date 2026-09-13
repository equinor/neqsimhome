// Platform manifold (fixed back-pressure)
network.addSinkNode("Manifold", 0.0);  // demand determined by network solution

// Alternative: fixed pressure at sink
NetworkNode manifold = network.getNode("Manifold");
manifold.setPressure(40.0e5);        // 40 bara in Pa
manifold.setPressureFixed(true);
