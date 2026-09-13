// Select the NR-GGA solver
network.setSolverType(SolverType.NEWTON_RAPHSON);

// Convergence settings
network.setTolerance(1e-6);       // Residual tolerance (Pa)
network.setMaxIterations(100);    // Maximum iterations
