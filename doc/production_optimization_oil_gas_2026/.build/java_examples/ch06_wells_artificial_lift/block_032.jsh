NetworkOptimizer optimizer = study.createOptimizer();
optimizer.setParetoPoints(3);
optimizer.setMaxEvaluations(60);
List<NetworkOptimizer.OptimizationResult> pareto = optimizer.optimizeMultiObjective();
for (NetworkOptimizer.OptimizationResult point : pareto) {
    logger.info("Unvalidated candidate {} kg/hr, compressor power {} kW, weight {}",
        point.totalProductionKgHr, point.totalCompressorPowerKW, point.paretoWeight);
}
// This unpowered teaching network has no production/power trade-off.
// Introduce a calibrated compressor and constraints before interpreting a Pareto front.
