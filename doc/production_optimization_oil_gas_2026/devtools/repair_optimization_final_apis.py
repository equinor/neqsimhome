"""Repair remaining current-source APIs, with explicit integration boundaries."""
from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
def path(n):return next((B/'chapters').glob(f'ch{n:02d}*/chapter.md'))
def blocks(n):return list(PAT.finditer(path(n).read_text(encoding='utf-8-sig')))
setup=blocks(24)[12][3]
def transform(ch,n,lang,code):
 if ch==21 and n==28:
  # Actual capacity search at each relaxation, bounded by number of constraints.
  code=code.replace('while True:', 'for step in range(8):')
  code=code.replace('    process.run()\n\n    new_rate', '''    config = (OptimizationConfig(50000.0, 300000.0).rateUnit("kg/hr")
              .searchMode(ProductionOptimizer.SearchMode.BINARY_FEASIBILITY))
    optimum = ProductionOptimizer().optimize(process, feed, config, None, None)
    process.run()

    new_rate''')
  return setup+'\n'+code
 if ch==24 and n==5:
  return code.replace('process.enableConstraints()', 'for unit in process.getUnitOperations():\n    unit.enableConstraints()')
 if ch==24 and n==68:return (' pattern: requires installed historian tagreader client and authenticated site data',code)
 if ch==25 and n==7:
  return '# Demonstration alert sink; route to approved monitoring infrastructure in deployment.\nalerts = []\ndef raise_warning(message):\n    alerts.append(("warning", str(message)))\ndef raise_alarm(message):\n    alerts.append(("alarm", str(message)))\n'+code
 if ch==26 and n==8:return code.replace('network.setNodeFluid', 'network.setFluidTemplate(fluid)\nnetwork.setNodeFluid')
 if ch==26 and n==15:return code.replace('    return sum(', '    score = sum(').replace('for i, value in enumerate(values))', 'for i, value in enumerate(values))\n    return NetworkAllocationOptimizer.AllocationResult(values, score, True)')
 if ch==28 and n in (16,17,18):
  identifier=f'vfp_concept{n-15}'
  code=code.replace('"Feed", "Flowline")','"Feed", "Export")')
  code=code.replace('# ... configure and generate ...',f'''{identifier}.setFlashGenerator(flash_gen)
{identifier}.setFlowRateUnit("kg/hr")
{identifier}.setInletTemperature(358.15)
{identifier}.setFlowRates(jpype.JArray(jpype.JDouble)([5000.0, 10000.0, 20000.0]))
{identifier}.setOutletPressures(jpype.JArray(jpype.JDouble)([30.0, 50.0]))
{identifier}.setWaterCuts(jpype.JArray(jpype.JDouble)([0.05]))
{identifier}.setGORs(jpype.JArray(jpype.JDouble)([300.0, 1000.0]))
{identifier}.setMinInletPressure(20.0)
{identifier}.setMaxInletPressure(350.0)
{identifier}.setEnableParallel(False)''')
  return code.replace('# Add booster pump effect (modeled as reduced flowline length or adjusted head)', '# This comparison changes flowline length only; no booster is modeled.').replace('8 km + booster','8 km route only').replace('Concept 3 (FPSO)', 'Concept 3 (short route)')
 if ch==30 and n==13:return code.replace('compression.add(comp)', 'compression.add(compressor)').replace('# ... add gas treatment equipment ...', 'gas_treatment.add(aftercooler)')
 if ch==33 and n==6:return code.replace('Inlet Separator.pressure','Inlet Separator.gasOutStream.pressure')
 return None
for ch in range(19,36):
 p=path(ch); text=p.read_text(encoding='utf-8-sig'); matches=list(PAT.finditer(text))
 for n,m in reversed(list(enumerate(matches,1))):
  result=transform(ch,n,m[1],m[3])
  if result is None:continue
  annotation,code=result if isinstance(result,tuple) else (m[2],result)
  lead=(f'**Execution scope:** {annotation.split("pattern:",1)[1].strip()}.\n\n' if 'pattern:' in annotation and 'pattern' not in m[2] else '')
  text=text[:m.start()]+lead+'```'+m[1]+annotation+'\n'+code.rstrip()+'\n```'+text[m.end():]
 text=re.sub(r'getEquipmentNearCapacityLimit\([\d.]+\)', 'getEquipmentNearCapacityLimit()',text)
 text=text.replace('.getConstraintType()', '.getType()')
 text=text.replace('.getCapacityUtilization()', '.getMaxUtilization()')
 p.write_text(text,encoding='utf-8')
