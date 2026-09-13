"""Add executable acceptance checks and explicitly reject unsupported legacy cases."""
from revise_foundations_science_phase3 import R,S,BOOK
from revise_foundations_scientific_text import revise,ledger
import re
R('ch06','gas_IPR_derivative',r'\frac{2 P_{wf}}{\text{PI}_{gas}}',r'\frac{1}{2P_{wf}\,\text{PI}_{gas}}')
R('ch06','NR_global','Adaptive relaxation prevents divergence','Adaptive relaxation can improve robustness but does not guarantee convergence')
R('ch06','NR_global2','**Adaptive relaxation** prevents divergence without excessive damping','**Adaptive relaxation** can reduce oversized steps; nonsmooth or infeasible cases can still fail')
R('ch06','well_constraint_success','well.setMinBottomHolePressure(90.0, "bara")  # lift / stability limit','''well.setMinBottomHolePressure(90.0, "bara")  # lift / stability limit
# Registering a constraint does not make the old 130-bar drawdown feasible.
assert well.getDrawdown() > 40.0  # rejected previous operating point
well.setOutletPressure(210.0, "bara")  # reservoir 250 bara minus allowed 40 bar
well.run()
assert well.getDrawdown() <= 40.0 + 1e-8
assert well.getBottomHolePressure() >= 90.0
assert 0.0 < well.getLiquidRate() < qTest
print("Accepted constrained IPR rate:", well.getLiquidRate(), "Sm3/day")''')
R('ch06','scenario_restore_before','original_flow = network.getPipeFlowRate("Tubing-B") / 3600.0','original_flow = network.getPipeFlowRate("Tubing-B") / 3600.0\noriginal_opening = network.getPipe("Choke-B").getChokeOpening()')
R('ch06','scenario_restore_after','network.getPipe("Choke-B").setChokeOpening(70.0)','network.getPipe("Choke-B").setChokeOpening(original_opening)')
R('ch06','legacy_python_status','Three segments per element keep this teaching example tractable.','The following legacy multiphase network is an API and candidate-generation example, not an accepted engineering solution: its default choke relation does not support critical gas capacity, and the pipe named Riser has no elevation profile. The explicitly checked forward gas-choke network in Section6.9.1 is the accepted hydraulic example. Three segments per element keep this API example tractable.')
R('ch06','legacy_java_status','// Step 5: Elements — Riser','// API assembly only: no elevation profile is supplied for this nominal riser.\n// Step 5: Elements — Riser')
for ch in ['ch07','ch08']:
 ident=ch+'_explicit_pipeline_U'
 if any(x['id']==ident for x in ledger):continue
 p=next((BOOK/'chapters').glob(ch+'*/chapter.md'));old=p.read_text(encoding='utf-8')
 def fix(m):
  code=m[1]
  code=re.sub(r'^( *)(\w+)\.setConstantSurfaceTemperature\(([^\n]+)\)\s*$',lambda z:z[0]+'\n'+z[1]+z[2]+'.setHeatTransferCoefficient(5.0)  # assumed insulated-pipe U, W/(m2 K)',code,flags=re.M)
  return '```python\n'+code+'```'
 new=re.sub(r'^```python\s*\n(.*?)^```',fix,old,flags=re.M|re.S)
 revise(ch,ident,old,new,'Specify the assumed heat-transfer coefficient instead of silently using estimated inner-film heat transfer as overall U.',['NeqSim PipeBeggsAndBrills.setHeatTransferCoefficient switches SPECIFIED_U'])
R('ch03','envelope_rejection_intro','### 3.7.5 Phase Envelope Generation','''### 3.7.5 Phase Envelope Generation

This characterized PR/TBP recipe is retained as a numerical-diagnostics example. The current source trace does not provide a verified complete saturation envelope: a missing branch and a candidate that fails an independent TP phase-transition bracket must be rejected. Do not report cricondentherm/cricondenbar as fluid specifications from this trace. The separately labelled defined-compound illustration uses a different fluid basis.''')
S('ch03','envelope_no_false_extrema',r'print\(f"Cricondenbar:.*?\{ops\.getOperation\(\)\.get\(\x27cricondentherm\x27\)\[1\]:\.1f\} bara"\)',r'''import math
finite_branches = {}
for label, ts, ps in [("getter dew", dew_T, dew_P), ("getter bubble", bub_T, bub_P)]:
    points = [(float(t), float(p)) for t, p in zip(ts, ps)
              if math.isfinite(t) and math.isfinite(p) and t > 0 and p > 0]
    finite_branches[label] = points
    print(label, "finite candidate points:", len(points))
print("REJECTED for specification: complete physical branch validation is absent.")
# Branch names are getter labels, not proof of bubble/dew identity.
# A finite candidate additionally needs a fresh TP bracket at the same composition.''')
