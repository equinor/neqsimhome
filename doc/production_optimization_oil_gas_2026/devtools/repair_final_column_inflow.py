from pathlib import Path
import re
BOOK=Path(__file__).resolve().parents[1]
p=next((BOOK/'chapters').glob('ch06*/chapter.md'))
t=p.read_text(encoding='utf-8')
t=t.replace('well.setVogelParameters(qTest, pwfTest, reservoirP)       # Vogel', '''# Explicit liquid-volume basis (Sm3/day), unlike the legacy MSm3/day setter.
InflowPerformance = jneqsim.process.equipment.reservoir.InflowPerformance
ratio = pwfTest / reservoirP
pi_liquid = qTest * 1.8 / (reservoirP * (1.0 - 0.2*ratio - 0.8*ratio**2))
well.setInflowPerformance(InflowPerformance.vogel(pi_liquid, reservoirP))
well.setLiquidRate(qTest)''')
t=t.replace('print("Rate:", well.getOutletStream().getFlowRate("Sm3/day"),','assert 200.0 < well.getLiquidRate() < 400.0\nprint("Liquid rate (Sm3/day):", well.getLiquidRate(),')
t=t.replace('study.setTolerance(1e-4);','study.setTolerance(100.0);  // Pa = 0.001 bar for this teaching solve')
t=t.replace('study.getPipeFlowRate("Line-A"), study.getSolutionSummary().get("converged"));','study.getPipeFlowRate("Line-A"), study.getSolutionSummary().get("converged"));\n    logger.info("Hydraulic residual {} Pa", study.getSolutionSummary().get("maxResidual_Pa"));')
t=t.replace('logger.info("Converged {}, message {}", result.converged, result.message);','study.run();\nlogger.info("Optimizer converged {}, hydraulics converged {}, message {}",\n    result.converged, study.getSolutionSummary().get("converged"), result.message);')
t=t.replace('CMA-ES converged {}, production {} kg/hr: {}','CMA-ES search converged {}, unvalidated candidate {} kg/hr: {}')
t=t.replace('Candidate production {} kg/hr, compressor power {} kW, weight {}','Unvalidated candidate {} kg/hr, compressor power {} kW, weight {}')
needle='### 6.9.2 NetworkOptimizer with BOBYQA and CMA-ES\n'
t=t.replace(needle,needle+'\nOptimizer termination and hydraulic convergence are separate checks. Reject any candidate whose network residuals fail even if the optimizer reports success. The examples print these statuses explicitly; candidate rates are not accepted operating recommendations.\n')
p.write_text(t,encoding='utf-8')

p=next((BOOK/'chapters').glob('ch11*/chapter.md'))
t=p.read_text(encoding='utf-8')
t=t.replace('# Parameters: name, numberOfTrays, hasCondenser, hasReboiler', '# Parameters: name, equilibrium stages, hasReboiler, hasCondenser')
t=t.replace('"Crude Stabilizer", 12, True, True','"Crude Stabilizer", 5, True, False')
t=t.replace('"Stabilizer", 12, True, True','"Stabilizer", 5, True, False')
t=t.replace('stabilizer.addFeedStream(feed, 6)  # Feed at tray 6','stabilizer.addFeedStream(feed, 5)  # Feed at the top of the stripping section')
t=t.replace('stabilizer.addFeedStream(col_feed, 6)','stabilizer.addFeedStream(col_feed, 5)')
t=t.replace('stabilizer.setCondenserTemperature(273.15 + 45.0)\nstabilizer.getReboiler().setHeatInput(500000.0)  # W', 'stabilizer.getReboiler().setOutTemperature(273.15 + 105.0)\nstabilizer.setTopPressure(8.0)\nstabilizer.setBottomPressure(8.5)\nstabilizer.setMaxNumberOfIterations(80, True)')
t=t.replace('stabilizer.setCondenserTemperature(273.15 + 45.0)\nstabilizer.getReboiler().setHeatInput(500000.0)', 'stabilizer.getReboiler().setOutTemperature(273.15 + 105.0)\nstabilizer.setTopPressure(8.0)\nstabilizer.setBottomPressure(8.5)\nstabilizer.setMaxNumberOfIterations(80, True)')
t=t.replace('overhead = stabilizer.getCondenser().getGasOutStream()','overhead = stabilizer.getGasOutStream()')
t=t.replace('print(stabilizer.getConvergenceDiagnostics())','print(stabilizer.getConvergenceDiagnostics())\nassert stabilizer.solved(), "Reject unsolved column products"')
t=t.replace('The calculated column liquid rate is lower for these settings; recovery superiority cannot be inferred', 'Recovery superiority cannot be inferred')
t=t.replace('# Set condenser and reboiler specifications','# Unrefluxed stripping section: specify reboiler temperature; calculate duty')
t=t.replace('### 11.9.4 Stabilization Column\n','### 11.9.4 Stabilization Column\n\nThe runnable case is a five-stage unrefluxed stripping section with a reboiler. It is a smaller teaching model than a complete refluxed stabilizer and exposes the convergence gate before reporting product rates.\n')
p.write_text(t,encoding='utf-8')
