from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
for ch in (23,24,33):
 p=next((B/'chapters').glob(f'ch{ch:02d}*/chapter.md'));text=p.read_text(encoding='utf-8-sig')
 if ch==23:
  text=re.sub(r'\*\*String-addressable automation\.\*\*[^\n]+', '**String-addressable automation.** The `ProcessAutomation` API exposes equipment and connected-stream properties through short addresses, such as `HP Sep.gasOutStream.density`. Discover the address, access type and unit before each update. This supports Python clients, structured configuration and agent-generated studies without requiring knowledge of internal object chains.',text)
  text=text.replace('industry-standard constraint presets','explicit equipment constraint limits').replace('`enableConstraints()`, or preset methods','`enableAllConstraints()`, or explicit constraint configuration').replace('loaded from industry-standard presets','configured from documented equipment ratings')
 for n,m in reversed(list(enumerate(PAT.finditer(text),1))):
  code=m[3];original=code
  if ch==24 and n==29:code=code.replace('optimizer.quickOptimize(process, feed, "kg/hr", 50000.0, 300000.0)','optimizer.quickOptimize(process, feed, "kg/hr", null)')
  if ch==33 and n==5:
   code=code.replace('HeatExchanger("Gas-Gas HX", dry_gas_stream)', 'jneqsim.process.equipment.heatexchanger.Cooler("Gas-Gas HX", dry_gas_stream)')
   code=code.replace('# Gas-gas heat exchanger (precooler)', '# Specified precooling duty represented by a Cooler; no second HX side is modeled.')
   code=code.replace('# Recompressor (shaft-coupled to expander)', '# Recompressor with specified discharge pressure; shaft power is not coupled here.')
  if ch==33 and n==6:
   a=code.index('state = ProcessModelState.fromProcessModel(plant)')
   code=code[:a]+'''# Full state serialization must support every selected unit, including column internals.
try:
    state = ProcessModelState.fromProcessModel(plant)
    state.setName("Illustrative gas plant")
    state.setVersion("2026.09")
    state.saveToFile("gas_plant_base_case.json")
    print("Full state saved; validate restoration before relying on the archive")
except jpype.JException as error:
    from pathlib import Path
    Path("gas_plant_state_diagnostic.txt").write_text(str(error), encoding="utf-8")
    print("Full state archive unavailable for these unit internals; diagnostic saved")
    # This diagnostic is not a successful archive or a restorable process state.
'''
  if code!=original:text=text[:m.start()]+'```'+m[1]+m[2]+'\n'+code.rstrip()+'\n```'+text[m.end():]
 p.write_text(text,encoding='utf-8')
