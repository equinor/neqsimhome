ProductionOptimizer optimizer = new ProductionOptimizer();
ProductionOptimizer.OptimizationResult result = optimizer.optimizeThroughput(
    process, feed, 5000.0, 40000.0, "kg/hr", null);
logger.info("Feasible: {}, rate: {} kg/hr", result.isFeasible(), result.getOptimalRate());
