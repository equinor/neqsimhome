from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];V=B/'verification/scientific_revision';p=B/'chapters/ch32_advanced_topics/chapter.md'
t=p.read_text(encoding='utf-8')
old='logger.info("Objective {}, feasible {}, converged {}", result.getObjective(),result.isFeasible(),result.isSimulationConverged());'
new='''logger.info("Objective {}, feasible {}, converged {}", result.getObjective(),result.isFeasible(),result.isSimulationConverged());
double rejectedPowerKW = compressor.getPower("kW");
// The 100000 kg/hr candidate exceeds the declared 5 MW ceiling.
if (result.isFeasible() || rejectedPowerKW <= 5000.0) {
    throw new IllegalStateException("Expected the high-rate candidate to be rejected");
}
ProcessSimulationEvaluator.EvaluationResult acceptedEvaluation = evaluator.evaluate(new double[]{80000.0,60.0});
if (!acceptedEvaluation.isFeasible() || !acceptedEvaluation.isSimulationConverged()
        || compressor.getPower("kW") > 5000.0) {
    throw new IllegalStateException("Lower-rate evaluator candidate failed acceptance");
}
logger.info("Accepted 80000 kg/hr candidate, power {} kW", compressor.getPower("kW"));'''
if old in t and 'double rejectedPowerKW' not in t:p.write_text(t.replace(old,new,1),encoding='utf-8')
report=V/'ch32_java_corrections.json';rows=json.loads(report.read_text())
if not any(r.get('id')=='evaluator_accepted_case' for r in rows):
 rows.append({'id':'evaluator_accepted_case','issue':'Initial evaluator point is correctly infeasible at the 5MW ceiling; pair its rejection with a checked successful case.','correction':'Retain100000kg/hr rejection; accept80000kg/hr with returned convergence/feasibility and direct power-limit assertions.','before':old,'after':new})
 report.write_text(json.dumps(rows,indent=2),encoding='utf-8')
# Preserve the original audit, including its excessively strict absolute
# objective-replay threshold, before the documented relative check is applied.
prior=V/'ch32_java_solution_checks.json';backup=V/'ch32_java_solution_checks_initial.json'
if prior.exists() and not backup.exists():backup.write_bytes(prior.read_bytes())
