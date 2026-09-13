from pathlib import Path
import re
BOOK=Path(__file__).resolve().parents[1]
p=next((BOOK/'chapters').glob('ch06*/chapter.md'))
t=p.read_text(encoding='utf-8')
t=t.replace('well.solveFlowFromOutletPressure()', 'well.solveFlowFromOutletPressure(True)\nwell.run()')
t=t.replace('well.getFlowRate("Sm3/day")','well.getOutletStream().getFlowRate("Sm3/day")')
t=t.replace('fl.setMultiphaseSegments(15)', 'fl.setMultiphaseSegments(3)')
t=t.replace('riser.setMultiphaseSegments(10)', 'riser.setMultiphaseSegments(3)')
t=t.replace('w["depth"], 0.1016, 90.0)\n', 'w["depth"], 0.1016, 90.0)\n    network.getPipe(f"Tubing-{name}").setTubingSegments(3)\n')
t=t.replace('optimizer.setMaxEvaluations(60)', 'optimizer.setMaxEvaluations(30)')
t=t.replace('print(f"Optimal total production:', 'print(f"Optimizer converged: {result.converged}; {result.message}")\nprint(f"Candidate total production:')
t=t.replace('network.setTolerance(1e-6)\n','network.setTolerance(1e-4)\n')
t=t.replace('        # Record flow rate\n        flow = network.getPipeFlowRate(f"Tubing-{name}") / 3600.0', '        # Exclude unconverged candidates from the sensitivity curve.\n        converged = bool(network.getSolutionSummary().get("converged"))\n        flow = (network.getPipeFlowRate(f"Tubing-{name}") / 3600.0\n                if converged else float("nan"))')
matches=list(re.finditer(r'^```(python|java)\s*\n(.*?)^```',t,re.M|re.S))
changes={}
changes[29]='''// Small, independently bounded network for the optimization tutorial.
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
study.addPipe("Down-A", "Plant", "Line-A", 5000.0, 0.2032);
study.addPipe("Down-B", "Plant", "Line-B", 4000.0, 0.2032);
study.setSolverType(SolverType.NEWTON_RAPHSON);
study.setMaxIterations(100);
study.setTolerance(1e-4);
double[] openings = {40.0, 60.0, 80.0, 100.0};
for (double opening : openings) {
    study.getPipe("Choke-A").setChokeOpening(opening);
    study.run();
    logger.info("Opening {}%, flow {} kg/hr, converged {}", opening,
        study.getPipeFlowRate("Line-A"), study.getSolutionSummary().get("converged"));
}
'''
changes[30]='''import neqsim.process.equipment.network.NetworkOptimizer;
NetworkOptimizer optimizer = study.createOptimizer();
optimizer.setMaxEvaluations(50);
NetworkOptimizer.OptimizationResult result = optimizer.optimize();
logger.info("Converged {}, message {}", result.converged, result.message);
logger.info("Candidate production {} kg/hr, choke openings {}",
    result.totalProductionKgHr, Arrays.toString(result.chokeOpenings));
'''
changes[31]='''NetworkOptimizer optimizer = study.createOptimizer();
optimizer.setAlgorithm(NetworkOptimizer.Algorithm.CMAES);
optimizer.setDeterministicSeed(2026L);
optimizer.setMaxEvaluations(60);
NetworkOptimizer.OptimizationResult result = optimizer.optimize();
logger.info("CMA-ES converged {}, production {} kg/hr: {}",
    result.converged, result.totalProductionKgHr, result.message);
'''
changes[32]='''NetworkOptimizer optimizer = study.createOptimizer();
optimizer.setParetoPoints(3);
optimizer.setMaxEvaluations(60);
List<NetworkOptimizer.OptimizationResult> pareto = optimizer.optimizeMultiObjective();
for (NetworkOptimizer.OptimizationResult point : pareto) {
    logger.info("Candidate production {} kg/hr, compressor power {} kW, weight {}",
        point.totalProductionKgHr, point.totalCompressorPowerKW, point.paretoWeight);
}
// This unpowered teaching network has no production/power trade-off.
// Introduce a calibrated compressor and constraints before interpreting a Pareto front.
'''
for index,code in sorted(changes.items(),reverse=True):
    m=matches[index-1];t=t[:m.start(2)]+code+t[m.end(2):]
t=re.sub(r'\| Network Size \|.*?(?=The solver\'s efficiency)', 'Solve time depends on fluid flashes, segment count, coupling iterations, topology, hardware, and initialization. Record timing and residuals for the actual study; no sub-second performance guarantee follows from the solver algorithm alone.\n\n',t,flags=re.S)
t=t.replace('The sub-second solve time of the NR-GGA solver makes this real-time loop feasible even for large networks.', 'A deployment must benchmark the complete data-to-recommendation cycle and define stale-data, non-convergence, and operator-approval handling before selecting its update interval.')
t=t.replace('The `optimizeMultiObjective()` method generates a Pareto front:', 'The `optimizeMultiObjective()` method evaluates weighted production and compressor-power objectives. Its candidates still need independent feasibility and non-dominance checks. In the unpowered tutorial network below, all compressor powers are zero and the trade-off is degenerate:')
t=t.replace('### 6.10.1 Building a Multi-Well Network in Python\n','### 6.10.1 Building a Multi-Well Network in Python\n\nThree segments per element keep this teaching example tractable. Before using it for operating decisions, refine the segments until pressures and rates stabilize, calibrate the IPR and multiphase correlation, and reject non-converged results. The short optimizer budget demonstrates candidate generation rather than guaranteeing an optimum.\n')
t=t.replace('where $C$ is typically 100–150 (125 for continuous service) and $\\rho_m$ is the mixture density [kg/m³].','Here the traditional $C$ values 100–150 use velocity in ft/s and density in lb/ft³. For SI inputs use $v_e=1.2193 C/\\sqrt{\\rho_m}$ with $v_e$ in m/s and $\\rho_m$ in kg/m³. Selection of $C$ needs a service-specific basis; this correlation does not cover solids erosion or flow-induced vibration by itself.')
p.write_text(t,encoding='utf-8')
