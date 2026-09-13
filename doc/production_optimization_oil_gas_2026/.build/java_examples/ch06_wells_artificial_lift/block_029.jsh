// Small, independently bounded network for the optimization tutorial.
// The detailed four-well multiphase calculation is demonstrated in Python below.
LoopedPipeNetwork study = new LoopedPipeNetwork("Choke optimization tutorial");
SystemSrkEos studyFluid = new SystemSrkEos(303.15, 90.0);
studyFluid.addComponent("methane", 0.95);
studyFluid.addComponent("ethane", 0.05);
studyFluid.setMixingRule("classic");
study.setFluidTemplate(studyFluid);
study.addSourceNode("Source-A", 90.0, 0.0);
study.addSourceNode("Source-B", 85.0, 0.0);
study.addJunctionNode("Down-A");
study.addJunctionNode("Down-B");
study.addSinkNode("Plant", 0.0);
study.getNode("Plant").setPressure(40.0e5);
study.getNode("Plant").setPressureFixed(true);
study.addChoke("Source-A", "Down-A", "Choke-A", 20.0, 80.0);
study.addChoke("Source-B", "Down-B", "Choke-B", 15.0, 80.0);
study.getPipe("Choke-A").setChokeUseValveModel(true);
study.getPipe("Choke-B").setChokeUseValveModel(true);
study.setRelaxationFactor(1.0);
study.addPipe("Down-A", "Plant", "Line-A", 5000.0, 0.2032);
study.addPipe("Down-B", "Plant", "Line-B", 4000.0, 0.2032);
study.setSolverType(SolverType.NEWTON_RAPHSON);
study.setMaxIterations(200);
study.setTolerance(100.0);  // Pa = 0.001 bar for this teaching solve
double[] openings = {40.0, 60.0, 80.0, 100.0};
for (double opening : openings) {
    study.getPipe("Choke-A").setChokeOpening(opening);
    study.run();
    double residualPa = study.getMaxResidual();
    double massErrorKgS = Math.abs(study.getMassBalanceError());
    double sinkKgS = study.getTotalSinkFlow();
    String chokeStatus = study.getPipe("Choke-A").getChokeModelStatus();
    if (!study.isConverged() || !Double.isFinite(residualPa)
        || residualPa > 100.0 || massErrorKgS > 1.0e-6
        || !Double.isFinite(sinkKgS) || sinkKgS <= 0.0
        || !chokeStatus.startsWith("IEC_GAS_")) {
        throw new IllegalStateException("Rejected hydraulic operating point");
    }
    double downAPa = study.getNode("Down-A").getPressure();
    double downBPa = study.getNode("Down-B").getPressure();
    if (!(40.0e5 < downAPa && downAPa < 90.0e5
        && 40.0e5 < downBPa && downBPa < 85.0e5)) {
        throw new IllegalStateException("Invalid passive-network pressure ordering");
    }
    logger.info("Accepted: residual {} Pa, mass error {} kg/s, status {}",
        residualPa, massErrorKgS, chokeStatus);
    logger.info("Opening {}%, flow {} kg/hr, converged {}", opening,
        study.getPipeFlowRate("Line-A"), study.getSolutionSummary().get("converged"));
    logger.info("Hydraulic residual {} Pa", study.getSolutionSummary().get("maxResidual_Pa"));
}
