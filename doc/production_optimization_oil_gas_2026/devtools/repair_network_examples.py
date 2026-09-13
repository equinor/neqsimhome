from pathlib import Path
import re
BOOK=Path(__file__).resolve().parents[1]
p=BOOK/'chapters/ch06_wells_artificial_lift/chapter.md'
t=p.read_text(encoding='utf-8')
# Source-backed units: IPR arguments are SI, user getters return bara and kg/hr.
t=t.replace('network.setInitialFlowEstimate("pipe1", 50.0);', 'network.getPipe("Export Flowline").setFlowRate(50.0);')
t=re.sub(r'(network\.addTubing\([^;]*?),\s*(?:20|25|15)\s*\);',r'\1);',t)
t=t.replace('w["depth"], 0.1016, 90.0, 20)', 'w["depth"], 0.1016, 90.0)')
t=t.replace('250.0e5,   // reservoir pressure [Pa]\n    15.0);     // PI [Sm3/d/bar] — converted to kg/s/Pa internally', '15.0 * 800.0 / 86400.0 / 1e5, // SI PI from 15 Sm3/day/bar and 800 kg/Sm3\n    false);    // oil IPR; source node supplies reservoir pressure')
t=t.replace('300.0e5,   // reservoir pressure [Pa]\n    0.5);      // PI_gas [Sm3/d/bar²]', '0.5 * 0.8 / 86400.0 / 1e10, // kg/s/Pa2 from 0.8 kg/Sm3 gas\n    true);     // gas pressure-squared IPR')
t=re.sub(r'(network\.addWellIPRVogel\([^,]+,[^,]+,[^,]+,)\s*\d+\.0e5,\s*(?://[^\n]*\n\s*)?',r'\1 ',t)
t=re.sub(r'(network\.addWellIPRFetkovich\([^,]+,[^,]+,[^,]+,)\s*\d+\.0e5,\s*(?://[^\n]*\n\s*)?',r'\1 ',t)
t=t.replace('"IPR-A", 250.0e5, 15.0)', '"IPR-A", 15.0 * 800.0 / 86400.0 / 1e5, false)')
t=t.replace('"WI-IPR", 180.0e5, 25.0)', '"WI-IPR", 25.0 * 1000.0 / 86400.0 / 1e5, false)')
t=t.replace('    90.0,      // inclination from horizontal [degrees] (90 = vertical)\n    20);       // number of segments', '    90.0);     // inclination from horizontal [degrees] (90 = vertical)')
t=t.replace('    60.0,      // inclination [degrees]\n    25);       // segments', '    60.0);     // inclination [degrees]')
t=t.replace('network.addChoke("WH-A", "Downstream-A"', 'network.addJunctionNode("Downstream-A");\nnetwork.addChoke("WH-A", "Downstream-A"')
t=t.replace('result.optimalValues','result.chokeOpenings')
t=t.replace('point.objectives[1]','point.totalCompressorPowerKW')
t=t.replace('Production: %.1f kg/s, Water: %.1f kg/s', 'Production: %.1f kg/hr, Compressor power: %.1f kW')
t=t.replace('optimizer.setPopulationSize(50);', '// Population size is selected internally by the CMA-ES implementation.')
t=t.replace('optimizer.setMaxEvaluations(5000);','optimizer.setMaxEvaluations(100); // bounded teaching run; inspect convergence')
t=t.replace('summary.get("totalFlowRate")', 'network.getTotalSinkFlow()').replace("summary.get('totalFlowRate')", 'network.getTotalSinkFlow()')
t=t.replace('network.getSolutionSummary().get("totalFlowRate")','network.getTotalSinkFlow()')
t=t.replace('summary.get("residualNorm")','summary.get("maxResidual_Pa")')
t=t.replace('logger.info("Total production: " + network.getTotalSinkFlow() + " kg/s");','logger.info("Total production: {} kg/s", network.getTotalSinkFlow());')
t=re.sub(r'(network\.getNodePressure\([^\n;]*?\))\s*/\s*1e5',r'\1',t)
t=re.sub(r'(network\.getPipeFlowRate\([^\n;]*?\))(?!\s*/)',r'\1 / 3600.0',t)
t=t.replace('getNodePressure("WH-A");  // Pa','getNodePressure("WH-A");  // bara')
t=t.replace('// Returns emissions by source: flaring, venting, combustion, fugitive','// Compressor combustion emissions only; flaring, venting and fugitives need separate models.')
t=t.replace('// getHydraulicReport() returns a JSON-formatted string\n// with nodal pressures and element flow rates','logger.info("Hydraulic summary: {}", network.getSolutionSummary());')
t=t.replace('// getMassBalanceReport() checks that sum(sources) = sum(sinks)\n// within the solver tolerance','logger.info("Mass balance error: {} kg/s", network.getMassBalanceError());')
t=t.replace('// Water injection well\n', '// Independent injection topology illustration\nnetwork.addJunctionNode("WI-Wellhead");\nnetwork.addJunctionNode("WI-BH");\nnetwork.addSourceNode("WI-Reservoir", 180.0, 0.0);\n')
t=t.replace('// Add looped topology\n', '// Add the explicitly named junctions before their connections.\nfor (String node : Arrays.asList("Down-D", "Manifold-1", "Manifold-2")) {\n    network.addJunctionNode(node);\n}\n')
t=t.replace('// Subsea booster pump at manifold\n','// Compressor proxy: a liquid booster requires an actual pump model.\nnetwork.addJunctionNode("Manifold");\nnetwork.addJunctionNode("Boosted-Manifold");\n')
t=t.replace('// Pressure regulator maintaining 20 bar downstream\n','// Pressure regulator maintaining 20 bar downstream\nnetwork.addSourceNode("HP-Header", 40.0, 0.0);\nnetwork.addJunctionNode("LP-Header");\n')
t=t.replace('optimizer = network.createOptimizer();','optimizer = network.createOptimizer();')
t=t.replace('float(result.objectiveValue):.2f} kg/s','float(result.totalProductionKgHr) / 3600.0:.2f} kg/s')
t=t.replace('float(result.objectiveValue):.1f} kg/s','float(result.totalProductionKgHr) / 3600.0:.1f} kg/s')
t=t.replace('enumerate(wells):\n    print(f"  Choke-{name}: {float(optimal_values[i]):.1f}%")','enumerate(result.chokeNames):\n    print(f"  {name}: {float(optimal_values[i]):.1f}%")')
# Initial staged network has an illustrative field density for PI conversion.
note='''
### 6.2.1 API units and model scope in the 2026 release

`addSourceNode` accepts bara and optional kg/hr, whereas `NetworkNode.setPressure`
uses Pa. `addWellIPR` takes a productivity index in kg/s/Pa for oil or kg/s/Pa²
for gas and a Boolean gas flag; reservoir pressure comes from the source node.
The examples explicitly convert illustrative standard-volume indices using a
stated reference density. `getNodePressure` returns bara, `getPipeFlowRate`
returns kg/hr, and `getTotalSinkFlow` returns kg/s. Mixing these interfaces can
produce plausible-looking results wrong by factors of 100,000 or 3,600.

Tubing elements use a reduced hydraulic relation; the multiphase-pipe element
uses `PipeBeggsAndBrills`. Gas-lift, ESP and water-cut switches therefore support
screening, with detailed well and phase models needed to qualify an operating
recommendation. A reported optimizer objective is not a convergence or
feasibility certificate. Inspect `converged`, the residual in Pa, mass balance
in kg/s, and the candidate constraint report before comparing production.\cite{neqsim2026update}

'''
if '### 6.2.1 API units' not in t:
    pos=t.index('```java')
    t=t[:pos]+note+t[pos:]
p.write_text(t,encoding='utf-8')
