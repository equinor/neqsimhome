"""Correct the Java field screening examples and bound their demonstration grids."""
from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
p=next((B/'chapters').glob('ch28*/chapter.md'));text=p.read_text(encoding='utf-8-sig')
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
axes='''vfpGen.setFlowRateUnit("kg/hr");
vfpGen.setInletTemperature(358.15);
vfpGen.setFlowRates(new double[]{5000.0,10000.0,20000.0});
vfpGen.setOutletPressures(new double[]{30.0,50.0});
vfpGen.setWaterCuts(new double[]{0.05});
vfpGen.setGORs(new double[]{300.0,1000.0});'''
for n,m in reversed(list(enumerate(PAT.finditer(text),1))):
 if m[1]!='java':continue
 code=m[3];annotation=m[2];lead=''
 if n==1:
  annotation=' pattern: requires a validated local FLUID.E300 reference-fluid file'
  lead='**Execution scope:** requires the named local E300 fluid file with a validated composition and characterization.\n\n'
 if n==3:code=code.replace('total liquid rate [Sm3/hr] for normalization','mass-flow normalization [kg/hr]; this is not a stock-tank liquid rate')
 if n in (4,12):
  code=code.replace('tubing.setElevation(-2500.0);','tubing.setAngle(90.0);')
  code=code.replace('new Stream("Feed", fluid);','new Stream("Feed", fluid);\n    feed.setFlowRate(10000.0, "kg/hr");')
  code=code.replace('process.add(flowline);','process.add(flowline);\n    process.add(new Stream("Export Outlet", flowline.getOutletStream()));')
  code=code.replace('"Flowline"     // outlet stream name (pressure target)', '"Export Outlet" // actual outlet stream (pressure target)')
  code=code.replace('createProcessFactory(), "Feed", "Export"', 'createProcessFactory(), "Feed", "Export Outlet"')
  code=re.sub(r'vfpGen\.setFlowRates\(\s*new double\[\]\{[^}]+\}\);',axes,code)
  for axis in ('OutletPressures','WaterCuts','GORs'):
   # Keep the first assignment in the new bounded axes block only.
   found=list(re.finditer(r'vfpGen\.set'+axis+r'\(new double\[\]\{[^}]+\}\);',code))
   for later in reversed(found[1:]):code=code[:later.start()]+code[later.end():]
  code=code.replace('setEnableParallel(true)', 'setEnableParallel(false)')
  code=code.replace('vfpGen.exportVFPEXP("production_screening.txt", 1);', 'java.nio.file.Files.write(java.nio.file.Paths.get("production_screening.txt"),\n            vfpGen.toDiagnosticString().getBytes(java.nio.charset.StandardCharsets.UTF_8));')
  code=code.replace('// Step 7: Export to Eclipse', '// Step 7: Export diagnostic process screening, not a well VFP deck')
  code=code.replace('table.printSlice(0, 2);  // WC=5%, GOR=1500','table.printSlice(0, 1);  // WC=5%, GOR=1000')
  code=code.replace('exported to production_vfp.inc','exported to production_screening.txt')
 if n==5:
  code=code.replace('double bhp = table.getBHP(2, 1, 0, 3);  // rate[2], THP[1], WC[0], GOR[3]', 'double requiredInletPressure = table.getBHP(2, 1, 0, 1);\n// Legacy getter name; this is the inlet pressure for the declared process model.')
  code=code.replace('table.printSlice(0, 3)', 'table.printSlice(0, 1)')
 if n==6:code='''// Preserve the process-screening semantics in the file name and content.
java.nio.file.Files.write(Paths.get("production_screening.txt"),
    vfpGen.toDiagnosticString().getBytes(java.nio.charset.StandardCharsets.UTF_8));'''
 if n==7:code=code.replace('// Generates: 200, 370, 680, 1260, 2320, 4280, 7900, 10000','// Eight geometrically spaced values including both endpoints.')
 if n==10:
  code=code.replace('((StreamInterface) testProcess.getUnit("Flowline"))\n    .getOutletStream()', '((StreamInterface) testProcess.getUnit("Export Outlet"))')
  code=code.replace('logger.info("Test fluid components:', 'testFluid.initProperties();\nlogger.info("Test fluid components:')
 if n==11:code='''// Compare explicit internal diameters; nominal pipe sizes require wall-thickness data.
for (double diameter : new double[]{0.076, 0.102}) {
    ProcessSystem diameterCase = processFactory.get();
    ((PipeBeggsAndBrills) diameterCase.getUnit("Tubing")).setDiameter(diameter);
    MultiScenarioVFPGenerator diameterGenerator = new MultiScenarioVFPGenerator(diameterCase, "Feed", "Export Outlet");
    diameterGenerator.setFlashGenerator(flashGen);
    diameterGenerator.setFlowRateUnit("kg/hr");
    diameterGenerator.setInletTemperature(358.15);
    diameterGenerator.setFlowRates(new double[]{5000.0,10000.0,20000.0});
    diameterGenerator.setOutletPressures(new double[]{30.0,50.0});
    diameterGenerator.setWaterCuts(new double[]{0.05});
    diameterGenerator.setGORs(new double[]{300.0,1000.0});
    diameterGenerator.setMinInletPressure(20.0);
    diameterGenerator.setMaxInletPressure(350.0);
    diameterGenerator.setEnableParallel(false);
    MultiScenarioVFPGenerator.VFPTable diameterTable = diameterGenerator.generateVFPTable();
    logger.info("Internal diameter {} m: {} of {} feasible sampled points", diameter,
        diameterTable.getFeasibleCount(), diameterTable.getTotalPoints());
}'''
 if n==12:
  code=code.replace('public class VFPGenerationExample {', 'public class VFPGenerationExample {\n    private static final org.apache.logging.log4j.Logger logger = org.apache.logging.log4j.LogManager.getLogger(VFPGenerationExample.class);')
 text=text[:m.start()]+lead+'```java'+annotation+'\n'+code.rstrip()+'\n```'+text[m.end():]
p.write_text(text,encoding='utf-8')
