"""Promote only strictly converged bounded column configurations to manuscript."""
from revise_foundations_scientific_text import revise, BOOK
import re,json
folder=BOOK/'verification/scientific_revision'
cases=[('ch11',4,'column_probes_five.json','stabilizer'),('ch11',5,'column_probes_final_400.json','stabilizer'),('ch12',2,'column_probes_final.json','absorber'),('ch12',4,'column_probes.json','deethanizer')]
for ch,idx,filename,var in cases:
 row=next(x for x in json.loads((folder/filename).read_text()) if x['chapter']==ch and x['block']==idx)
 assert row['status']=='RIGOROUS_CONVERGED' and row['mesh']<1e-5
 p=next((BOOK/'chapters').glob(ch+'*/chapter.md'));text=p.read_text(encoding='utf-8')
 old=list(re.finditer(r'^```python\s*\n(.*?)^```',text,re.M|re.S))[idx-1][1]
 code=row['code']
 marker=f'print({var}.getConvergenceDiagnostics())'
 gate=f'''assert str({var}.getLastSolveStatus()) == "RIGOROUS_CONVERGED"
assert {var}.getLastMeshResidualNorm() < 1e-5
'''
 code=code.replace(marker,marker+'\n'+gate)
 if ch=='ch11':
  code=code.replace('# Unrefluxed stripping section: specify reboiler temperature; calculate duty','# Unrefluxed stripping: specify heat input in the stage energy equations')
  code=code.replace('Additional recovery:', 'Liquid-yield difference:')
  code=code.replace('# --- Column Stabilization ---','# --- One contacting stage plus equilibrium reboiler, 400 kW ---')
  code=code.replace('# Compare','# Different feed pressure, temperature and duty: this is NOT an equal-quality comparison.')
  code=code.replace(gate,gate+f'assert {var}.getGasOutStream().getFlowRate("kg/hr") > 0.0\nassert {var}.getReboiler().getLiquidOutStream().getFlowRate("kg/hr") > 0.0\n')
 else:
  if idx==4:
   code=code.replace('# NGL feed from turboexpander plant','# Assumed NGL recipe for a separate stripping example; not a computed plant outlet')
   code=code.replace('# Five-stage cold-feed stripping section: no condenser or external reflux','# One contacting stage plus reboiler: a bounded NGL stabilizer, not a product-spec deethanizer')
   code=code.replace('"Deethanizer", 1','"NGL Stabilizer", 1')
   code=code.replace('# Reboiler outlet temperature is specified; duty is calculated.','# Specified heat input is 100 kW; product temperatures are calculated.')
   code=code.replace('=== Deethanizer Results ===','=== NGL Stripping Results ===')
   code=code.replace(gate,gate+f'assert {var}.getGasOutStream().getFlowRate("kg/hr") > 0.0\nassert {var}.getReboiler().getLiquidOutStream().getFlowRate("kg/hr") > 0.0\n')
  else:
   code += '\nassert water_in_gas < saturated_gas.getFluid().getPhase("gas").getComponent("water").getx() * 1e6\n'
 revise(ch,f'{ch}_column_{idx}_strict_physics',old,code,'Replace temperature-only falsely accepted column with explicitly specified heat input and enforced MESH, energy and mass gates; remove free liquid ahead of TEG absorber and correct lean TEG mass fraction where applicable.',['NeqSim source 6cc8026202a5: DistillationColumn, SimpleTray, Reboiler; '+filename])
