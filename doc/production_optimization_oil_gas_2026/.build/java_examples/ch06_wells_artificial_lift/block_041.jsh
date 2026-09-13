// Diagnostic: check if the network is physically feasible
network.setMaxIterations(200);
network.setTolerance(1e-4);  // Relaxed tolerance first
network.run();

Map<String, Object> summary = network.getSolutionSummary();
boolean converged = (boolean) summary.get("converged");
if (!converged) {
    logger.info("Residual norm: " + summary.get("maxResidual_Pa"));
    logger.info("Check supply/demand balance and element sizing");
}
