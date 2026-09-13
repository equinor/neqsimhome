ProductionOptimizer optimizer = new ProductionOptimizer();
ProductionOptimizer.OptimizationResult optimum = optimizer.optimizeThroughput(
    process, feed, 5000.0, 30000.0, "kg/hr", null);
logger.info("Feasible: {}, rate: {} kg/hr", optimum.isFeasible(), optimum.getOptimalRate());
