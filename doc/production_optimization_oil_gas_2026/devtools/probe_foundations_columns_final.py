"""Two bounded follow-up configurations; no manuscript mutation."""
from pathlib import Path
import sys, os, re, json, time, traceback
BOOK=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BOOK/'.build/python_packages'))
SRC=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
sys.path.insert(0,str(SRC/'devtools'));os.environ['JAVA_TOOL_OPTIONS']='-Xmx512m'
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=SRC,recompile=False,verbose=False)
prior=json.loads((BOOK/'verification/scientific_revision/column_probes.json').read_text())
out=[]
for ch,idx in ([('ch11',5)] if len(sys.argv)>1 else [('ch11',5),('ch12',2)]):
 row=next(x for x in prior if x['chapter']==ch and x['block']==idx)
 code=row['code'];var='stabilizer' if ch=='ch11' else 'absorber'
 if ch=='ch11':code=code.replace('setHeatInput(60000)', 'setHeatInput(400000)' if len(sys.argv)>1 else 'setHeatInput(150000)')
 else:
  code=code.replace('# TEG Dehydration System — Complete Simulation','# Once-through equilibrium TEG absorber: regeneration is outside the boundary')
  code=code.replace('teg_fluid.addComponent("water", 0.01)','teg_fluid.addComponent("water", 0.5 / 0.018015)  # kg / (kg/mol)')
  code=code.replace('teg_fluid.addComponent("TEG", 0.99)','teg_fluid.addComponent("TEG", 99.5 / 0.150174)  # 99.5 wt% lean TEG')
  code=code.replace('# Lean TEG stream','# Remove free liquid before the gas absorber.\nwet_feed.run()\ninlet_scrubber = jneqsim.process.equipment.separator.ThreePhaseSeparator("Inlet Scrubber", wet_feed)\ninlet_scrubber.run()\nsaturated_gas = inlet_scrubber.getGasOutStream()\nassert saturated_gas.getFluid().getNumberOfPhases() == 1\n\n# Lean TEG stream')
  code=code.replace('absorber.addFeedStream(wet_feed, 0)','absorber.addFeedStream(saturated_gas, 0)')
  code=code.replace('process.add(wet_feed)\n','process.add(wet_feed)\nprocess.add(inlet_scrubber)\n')
 row={'chapter':ch,'block':idx,'code':code};out.append(row);scope={};t=time.monotonic()
 try:
  exec(code,scope);col=scope[var]
  row.update(status=str(col.getLastSolveStatus()),mesh=float(col.getLastMeshResidualNorm()),diagnostics=str(col.getConvergenceDiagnostics()))
  row['gas_kg_hr']=float(col.getGasOutStream().getFlowRate('kg/hr'))
  row['liquid_kg_hr']=float(col.getLiquidOutStream().getFlowRate('kg/hr'))
 except Exception:row['error']=traceback.format_exc()
 row['seconds']=time.monotonic()-t
 (BOOK/('verification/scientific_revision/column_probes_final'+('_400' if len(sys.argv)>1 else '')+'.json')).write_text(json.dumps(out,indent=2),encoding='utf-8')
 print('PROBE',ch,idx,{k:v for k,v in row.items() if k not in ['code','diagnostics']},flush=True)
