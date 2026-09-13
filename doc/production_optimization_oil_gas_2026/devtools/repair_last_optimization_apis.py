from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
for ch in (20,22,23,24,26,29):
 p=next((B/'chapters').glob(f'ch{ch:02d}*/chapter.md'));text=p.read_text(encoding='utf-8-sig')
 if ch==20:text=text.replace('compressor.getPolytropicHead()  # J/kg or kJ/kg depending on version','compressor.getPolytropicFluidHead()  # kJ/kg, solved fluid head')
 if ch==23:text=text.replace('getPolytropicHead("kJ/kg")','getPolytropicFluidHead()')
 for n,m in reversed(list(enumerate(PAT.finditer(text),1))):
  code=m[3];new=None
  if ch==24:
   if n==3:new='compressor.enableAllConstraints();\n// Constraints and limits require explicit equipment-specific configuration; no standard-compliance preset is implied.'
   if n==4:new='process.enableAllConstraints();'
   if n==5:new=re.sub(r'for unit in process.getUnitOperations\(\):\n    unit.enableConstraints\(\)', 'process.enableAllConstraints()',code)
   if n==21:new='config.validate();\n// This method returns void and throws IllegalArgumentException for an invalid configuration.'
   if n==22:new=code.replace('objectives,', 'null,').replace('constraints    //', 'null    //')
   if n==29:new='OptimizationSummary optimizationSummary = optimizer.optimize(process, feed, config, null, null).toSummary();\nlogger.info("Rate {} {}, feasible {}", optimizationSummary.getMaxRate(), optimizationSummary.getRateUnit(), optimizationSummary.isFeasible());'
   if n==30:new=code.replace('ProcessOptimizationEngine.LiftCurve', 'LiftCurve')
   if n==40:new=code.replace('Optional<ParetoPoint> knee = pareto.findKneePoint();', '// Select a preferred Pareto point using an explicit decision rule; no knee-point helper exists in this revision.')
   if n==82:new='config.rejectInvalidSimulations(true);\n// This search-screening option supplements explicit final feasibility and replay checks.'
  if ch==26 and n==8:
   new=code.replace('network.addSinkNode("Platform", 10000.0)  # demand in kg/hr', 'network.addFixedPressureSinkNode("Platform", 85.0)  # bara backpressure')
   new=new.replace('network.run()', 'network.setSolverType(LoopedPipeNetwork.SolverType.NEWTON_RAPHSON)\nnetwork.run()')
  if ch==29 and n==7:new=code.replace('Map<String, ControllerDeviceInterface> all', 'Collection<ControllerDeviceInterface> all')
  if new is not None:text=text[:m.start()]+'```'+m[1]+m[2]+'\n'+new.rstrip()+'\n```'+text[m.end():]
 if ch==24:
  text=text.replace('`enableConstraints()`, `useEquinorConstraints()`, `useAPIConstraints()`, or `useAllConstraints()`', '`enableAllConstraints()` on the equipment or process')
  text=text.replace('18 built-in', 'registered').replace('with knee point detection', 'with an explicit decision rule for selecting a preferred point')
 p.write_text(text,encoding='utf-8')
