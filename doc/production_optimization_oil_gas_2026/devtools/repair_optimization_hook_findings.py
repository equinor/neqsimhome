from pathlib import Path
import re,json
B=Path(__file__).resolve().parents[1]
fixes=[]
for n,targets in [(24,[5,13,23,69]),(25,[5,11])]:
 p=next((B/'chapters').glob(f'ch{n:02d}_*/chapter.md'));t=p.read_text(encoding='utf-8-sig')
 blocks=list(re.finditer(r'^```(?:python|java)[^\n]*\n(.*?)^```',t,re.M|re.S))
 for i in sorted(targets,reverse=True):
  m=blocks[i-1];c=m.group(1)
  c=c.replace('jneqsim.thermo.system.SystemSrkEos','jneqsim.thermo.system.SystemSrkCPAstatoil')
  # Chapter25 uses a class alias; the declaration replacement above changes its backing class.
  c=c.replace('fluid.setMixingRule("classic")','fluid.setMixingRule(10)\nfluid.setMultiPhaseCheck(True)')
  c=c.replace('comp.setPolytropicEfficiency(0.78)','comp.setPolytropicEfficiency(0.78)\ncomp.setUsePolytropicCalc(True)')
  c=c.replace('comp.setPolytropicEfficiency(0.77)','comp.setPolytropicEfficiency(0.77)\ncomp.setUsePolytropicCalc(True)')
  if n==25 and i==5:
   c=c.replace('export_comp = Compressor("Export compressor", hp_sep.getGasOutStream())',
    'suction_ko = jneqsim.process.equipment.separator.Separator(\n    "Compressor suction KO", gas_cooler.getOutletStream())\nexport_comp = Compressor("Export compressor", suction_ko.getGasOutStream())')
   c=c.replace('process.add(gas_cooler)\nprocess.add(export_comp)',
    'process.add(gas_cooler)\nprocess.add(suction_ko)\nprocess.add(export_comp)')
   c=c.replace('        unit.enableAllConstraints()',
    '        unit.enableAllConstraints()\n\n# No installed compressor chart is supplied: retain only the explicit power screen.\nexport_comp.getCompressorChart().setUseCompressorChart(False)\nexport_comp.setSolveSpeed(False)\nfor entry in export_comp.getCapacityConstraints().entrySet():\n    entry.getValue().setEnabled(str(entry.getKey()) == "power")')
  if n==24 and i==69:
   c=c.replace('pipeline.setLength(80.0)','pipeline.setLength(80000.0)  # m: declared 80 km horizontal export line')
   c=c.replace('pipeline.autoSize(1.2)',
    '# Retain the declared 0.508 m installed bore; velocity-only autoSize is not hydraulic sizing.\npipeline.initMechanicalDesign()')
  t=t[:m.start(1)]+c+t[m.end(1):]
  fixes.append({'chapter':n,'fence':i,'description':'CPA water phase consistency; consistent compressor efficiency basis'+(' and connected cooler/KO path' if (n,i)==(25,5) else '')+(' and declared80km fixed-bore pipeline' if (n,i)==(24,69) else '')})
 p.write_text(t,encoding='utf-8')
(B/'verification/scientific_revision/solution_hook_repairs.json').write_text(json.dumps(fixes,indent=2),encoding='utf-8')
print('Repaired',fixes)
