import neqsim.process.equipment.network.NetworkOptimizer;
NetworkOptimizer optimizer = study.createOptimizer();
optimizer.setMaxEvaluations(50);
NetworkOptimizer.OptimizationResult result = optimizer.optimize();
study.run();
logger.info("Optimizer converged {}, hydraulics converged {}, message {}",
    result.converged, study.getSolutionSummary().get("converged"), result.message);
logger.info("Candidate production {} kg/hr, choke openings {}",
    result.totalProductionKgHr, Arrays.toString(result.chokeOpenings));
