"""Targeted manuscript corrections from supplementary solution verification."""
from pathlib import Path
import re,json,hashlib
B=Path(__file__).resolve().parents[1]
P=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
changes=[]
def edit(n,i,fn):
 p=next((B/'chapters').glob(f'ch{n:02d}_*'))/'chapter.md'
 text=p.read_text(encoding='utf-8-sig');m=list(P.finditer(text))[i-1];old=m.group(3);new=fn(old)
 assert old!=new,(n,i)
 p.write_text(text[:m.start(3)]+new+text[m.end(3):],encoding='utf-8')
 changes.append({'chapter':n,'fence':i,'before_sha256':hashlib.sha256(old.encode()).hexdigest(),'after_sha256':hashlib.sha256(new.encode()).hexdigest()})

def facility(c):
 c=c.replace('fluid.setMultiPhaseCheck(True)\nfluid.setMultiPhaseCheck(True)','fluid.setMultiPhaseCheck(True)')
 c=c.replace('pipeline = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills(\n    "Export Pipeline", cooler.getOutletStream())', 'export_ko = jneqsim.process.equipment.separator.Separator(\n    "Export cooler knockout", cooler.getOutletStream())\npipeline = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills(\n    "Export Pipeline", export_ko.getGasOutStream())')
 c=c.replace('pipeline.setNumberOfIncrements(50)','pipeline.setNumberOfIncrements(10)')
 c=c.replace('process.add(cooler)\nprocess.add(pipeline)','process.add(cooler)\nprocess.add(export_ko)\nprocess.add(pipeline)')
 c=c.replace('print("Step 1: Process model built and solved")', '''# Check axial discretization at the declared lower/base/upper sweep rates.
# This is a mesh check, not an independent validation of Beggs-Brill physics.
pipeline_mesh = []
for check_rate in (125000.0, 250000.0, 350000.0):
    feed.setFlowRate(check_rate, "kg/hr")
    states = []
    for increments in (10, 20):
        pipeline.setNumberOfIncrements(increments)
        process.run()
        states.append((float(pipeline.getOutletStream().getPressure("bara")),
                       float(pipeline.getOutletStream().getTemperature("K"))))
    pressure_error = abs(states[0][0]-states[1][0])
    temperature_error = abs(states[0][1]-states[1][1])
    assert pressure_error < 0.2 and temperature_error < 0.1, states
    pipeline_mesh.append({"rate_kg_hr": check_rate,
                          "pressure_difference_bar": pressure_error,
                          "temperature_difference_K": temperature_error})
pipeline.setNumberOfIncrements(10)
feed.setFlowRate(250000.0, "kg/hr")
process.run()
print("Step 1: Process model built and mesh checked", pipeline_mesh)''')
 c=c.replace('print(f"Optimal feed rate:', 'print(f"Returned feed rate:')
 return c
edit(24,69,facility)

def scipy(c):
 c=c.replace('L-BFGS-B optimal flow rate:', 'L-BFGS-B candidate objective:').replace('DE optimal flow rate:', 'DE candidate objective:').replace('SLSQP optimal:', 'SLSQP candidate:')
 c+='''
# Optimizer termination and physical feasibility are separate acceptance gates.
scipy_candidates = []
for name, answer, objective in (("L-BFGS-B", result, neqsim_objective),
                                ("DE", result_de, neqsim_objective),
                                ("SLSQP", result_slsqp, multi_objective)):
    objective_value = float(objective(answer.x))
    candidate_power = float(comp.getPower("MW"))
    feasible = (not process.isAnyHardLimitExceeded() and
                (name != "SLSQP" or candidate_power <= 25.000001))
    accepted = bool(answer.success and feasible)
    scipy_candidates.append({"method": name, "success": bool(answer.success),
                             "feasible": feasible, "accepted": accepted,
                             "flow_kg_hr": float(feed.getFlowRate("kg/hr")),
                             "power_MW": candidate_power,
                             "objective": objective_value})
    print(name, "accepted candidate" if accepted else "rejected candidate",
          "(local/grid-independent global optimality is not established)")
'''
 return c
edit(24,59,scipy)
edit(24,74,lambda c:c.replace('# Disable the bottleneck constraints (simulate upgrade)','# Disable a check for a diagnostic screen; this does not model a physical upgrade.').replace('Debottlenecking Staircase:', 'Constraint-mask sensitivity (no physical upgrade credit):'))

def scenario(c):
 c=c.replace('compressor = Compressor("compressor", valve.getOutletStream())', 'suction_ko = jneqsim.process.equipment.separator.Separator("Suction knockout", valve.getOutletStream())\n    compressor = Compressor("compressor", suction_ko.getGasOutStream())')
 c=c.replace('process.add(valve)\n    process.add(compressor)', 'process.add(valve)\n    process.add(suction_ko)\n    process.add(compressor)')
 return c
edit(27,1,scenario)
edit(32,21,lambda c:c.replace('jneqsim.thermo.system.SystemSrkEos(273.15 + 80, 250.0)', 'jneqsim.thermo.system.SystemSrkCPAstatoil(273.15 + 80, 250.0)').replace('fluid_i.setMixingRule("classic")','fluid_i.setMixingRule(10)'))

path=B/'verification/scientific_revision/final_solution_closure_corrections.json'
old=json.loads(path.read_text()) if path.exists() else []
path.write_text(json.dumps(old+changes,indent=2),encoding='utf-8')
print(changes)
