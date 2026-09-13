NetworkOptimizer optimizer = study.createOptimizer();
optimizer.setAlgorithm(NetworkOptimizer.Algorithm.CMAES);
optimizer.setDeterministicSeed(2026L);
optimizer.setMaxEvaluations(60);
NetworkOptimizer.OptimizationResult result = optimizer.optimize();
logger.info("CMA-ES search converged {}, unvalidated candidate {} kg/hr: {}",
    result.converged, result.totalProductionKgHr, result.message);
