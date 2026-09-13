from pathlib import Path
import re
BOOK=Path(__file__).resolve().parents[1]
F=re.compile(r'^```(python|java)\s*\n(.*?)^```',re.M|re.S)
base='''import neqsim.thermo.system.SystemSrkEos;
import neqsim.process.equipment.stream.Stream;
import neqsim.process.processmodel.ProcessSystem;
import neqsim.process.equipment.capacity.CapacityConstraint;
import neqsim.process.util.optimizer.ProductionOptimizer;
import java.util.*;
SystemSrkEos fluid = new SystemSrkEos(313.15, 80.0);
fluid.addComponent("methane", 0.80);
fluid.addComponent("ethane", 0.10);
fluid.addComponent("n-heptane", 0.08);
fluid.addComponent("water", 0.02);
fluid.setMixingRule("classic");
fluid.setMultiPhaseCheck(true);
Stream feed = new Stream("Feed", fluid);
feed.setFlowRate(20000.0, "kg/hr");
ProcessSystem process = new ProcessSystem();
process.add(feed);
process.run();
'''
extra={
9:'import neqsim.process.equipment.pipeline.PipeBeggsAndBrills;\nimport neqsim.process.equipment.network.LoopedPipeNetwork;\n',
10:'''import neqsim.process.equipment.separator.Separator;
import neqsim.process.equipment.separator.ThreePhaseSeparator;
import neqsim.process.equipment.valve.ThrottlingValve;
import neqsim.process.mechanicaldesign.separator.SeparatorMechanicalDesign;
Separator separator = new Separator("HP Separator", feed);
process.add(separator);
process.run();
''',
14:'import neqsim.process.equipment.compressor.*;\n',
16:'import neqsim.process.equipment.heatexchanger.Heater;\nStream feedStream = feed;\n',
17:'import neqsim.process.equipment.valve.ThrottlingValve;\n',
}
for ch in extra:
    p=next((BOOK/'chapters').glob('ch%02d*/chapter.md'%ch))
    text=p.read_text(encoding='utf-8')
    matches=list(F.finditer(text))
    first=next(m for m in matches if m[1]=='java')
    code=first[2]
    logger_end=code.index('\n',code.index('Logger logger ='))+1
    code=code[:logger_end]+base+extra[ch]+code[logger_end:]
    text=text[:first.start(2)]+code+text[first.end(2):]
    matches=list(F.finditer(text))
    for index,m in reversed(list(enumerate(matches,1))):
        code=m[2]
        if m[1]!='java': continue
        code=code.replace('# Generated charts','// Generated charts')
        if ch==9:
            code=code.replace('pipeline.setElevation(200.0);   // downhill','pipeline.setElevation(-200.0);  // outlet below inlet')
            code=code.replace('process.run();\n\n// Auto-size','process.add(pipeline);\nprocess.run();\n\n// Auto-size')
            if index==11:
                code='''LoopedPipeNetwork network = new LoopedPipeNetwork("Gathering System");
network.setFluidTemplate(fluid);
network.addSourceNode("Well-1", 90.0, 0.0);
network.addSourceNode("Well-2", 85.0, 0.0);
network.addSourceNode("Well-3", 88.0, 0.0);
network.addJunctionNode("Junction-A");
network.addJunctionNode("Junction-B");
network.addSinkNode("Plant Inlet", 0.0);
network.getNode("Plant Inlet").setPressure(70.0e5);
network.getNode("Plant Inlet").setPressureFixed(true);
network.addPipe("Well-1", "Junction-A", "Line 1", 5000.0, 0.2032);
network.addPipe("Well-2", "Junction-A", "Line 2", 3000.0, 0.1524);
network.addPipe("Well-3", "Junction-B", "Line 3", 8000.0, 0.2032);
network.addPipe("Junction-A", "Junction-B", "Crossover", 2000.0, 0.254);
network.addPipe("Junction-B", "Plant Inlet", "Export", 10000.0, 0.3048);
network.setSolverType(LoopedPipeNetwork.SolverType.NEWTON_RAPHSON);
network.run();
logger.info("Network results: {}", network.getSolutionSummary());
'''
        if ch==10:
            code=code.replace('design.setMaxDesignGassVolFlow(5000.0);','// Gas flow is obtained from the solved stream; impose project envelope separately.')
            code=code.replace('design.setMaxDesignPressure(85.0);','design.setMaxOperationPressure(85.0);')
            if index==20: code=code.replace('process.run();','process.add(threePhaseSep);\nprocess.run();')
            if index==21:
                code='''ProductionOptimizer optimizer = new ProductionOptimizer();
ProductionOptimizer.OptimizationResult result = optimizer.optimizeThroughput(
    process, feed, 5000.0, 40000.0, "kg/hr", null);
logger.info("Feasible: {}, rate: {} kg/hr", result.isFeasible(), result.getOptimalRate());
'''
            if index==22:
                code='''String bottleneck = result.getBottleneck() == null ? "none" : result.getBottleneck().getName();
logger.info("Bottleneck: {}", bottleneck);
'''
            if index==23:
                code='''Separator hpSep = separator;
ThrottlingValve mpValve = new ThrottlingValve("HP-MP", hpSep.getLiquidOutStream());
mpValve.setOutletPressure(15.0);
Separator mpSep = new Separator("MP", mpValve.getOutletStream());
ThrottlingValve lpValve = new ThrottlingValve("MP-LP", mpSep.getLiquidOutStream());
lpValve.setOutletPressure(2.0);
Separator lpSep = new Separator("LP", lpValve.getOutletStream());
process.add(mpValve);
process.add(mpSep);
process.add(lpValve);
process.add(lpSep);
process.run();
for (Separator stage : Arrays.asList(hpSep, mpSep, lpSep)) {
    stage.autoSize(1.2);
    stage.enableConstraints();
}
logger.info("Separation train configured; pressure optimization requires explicit decision bounds.");
'''
        if ch==14:
            code=code.replace('comp.setSurgeMargin(0.10);','comp.getAntiSurge().setSurgeControlFactor(1.10);')
            code=code.replace('comp.enableConstraints();','comp.reinitializeCapacityConstraints();')
            if index==7: code+='\nprocess.add(comp);\nprocess.run();\nCompressor compressor = comp;\n'
            if index==13:
                code='''ProductionOptimizer optimizer = new ProductionOptimizer();
ProductionOptimizer.OptimizationResult optimum = optimizer.optimizeThroughput(
    process, feed, 5000.0, 30000.0, "kg/hr", null);
logger.info("Feasible: {}, rate: {} kg/hr", optimum.isFeasible(), optimum.getOptimalRate());
'''
            if index==15:
                code='''// Separate parallel-machine setup; an optimizer needs independent split decisions.
Stream feedA = new Stream("Train A feed", fluid.clone());
Stream feedB = new Stream("Train B feed", fluid.clone());
feedA.setFlowRate(10000.0, "kg/hr");
feedB.setFlowRate(10000.0, "kg/hr");
feedA.run();
feedB.run();
Compressor compA = new Compressor("Train A", feedA);
Compressor compB = new Compressor("Train B", feedB);
compA.setOutletPressure(120.0);
compB.setOutletPressure(120.0);
compA.run();
compB.run();
logger.info("Parallel baseline power: {} kW", compA.getPower("kW") + compB.getPower("kW"));
'''
        if ch==16 and index==8: code=code.replace('process.run();','process.add(heater);\nprocess.run();')
        if ch==17 and index==9: code=code.replace('process.run();','process.add(valve);\nprocess.run();')
        text=text[:m.start(2)]+code+text[m.end(2):]
    p.write_text(text,encoding='utf-8')

p=BOOK/'chapters/ch06_wells_artificial_lift/chapter.md'
t=p.read_text(encoding='utf-8')
for index,m in reversed(list(enumerate(F.finditer(t),1))):
    if index not in (26,36,37,38):continue
    code=m[2]
    code='LoopedPipeNetwork variant = new LoopedPipeNetwork("Topology illustration");\nvariant.setFluidTemplate(fluid);\n'+code.replace('network.','variant.')
    if index==26:code='\n'.join(code.splitlines()[:2])+'\nvariant.addSourceNode("Platform", 250.0, 0.0);\n'+'\n'.join(code.splitlines()[2:])
    if index==36:code='\n'.join(code.splitlines()[:2])+'\nfor (String node : Arrays.asList("Down-A", "Down-B", "Down-C")) { variant.addJunctionNode(node); }\n'+'\n'.join(code.splitlines()[2:])
    t=t[:m.start(2)]+code+'\n'+t[m.end(2):]
p.write_text(t,encoding='utf-8')
