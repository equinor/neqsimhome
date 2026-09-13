from pathlib import Path
import re
BOOK=Path(__file__).resolve().parents[1]
F=re.compile(r'^```(python|java)\s*\n(.*?)^```',re.M|re.S)
for p in sorted((BOOK/'chapters').glob('*/chapter.md'))[:18]:
    t=p.read_text(encoding='utf-8');ch=int(p.parent.name[2:4])
    if ch in (14,18):
        t=re.sub(r'\.setMaximumPower\(([^\n)]+)\)',r'.updatePowerConstraint((\1) / 1000.0)',t)
        t=t.replace('# W: 15 MW driver limit','# Rating in kW after conversion from W')
    if ch==6:
        t=t.replace('WellFlow("Well-A", reservoirStream)','WellFlow("Well-A")\nwell.setInletStream(reservoirStream)')
        t=t.replace('np.arange(10, 101, 5)','np.array([40.0, 60.0, 80.0, 100.0])')
        t=t.replace('10% to 100% in steps of 5%','four teaching points; refine around active constraints')
        t=t.replace('result = network.optimizeProductionNLP()','optimizer = network.createOptimizer()\noptimizer.setMaxEvaluations(60)\nresult = optimizer.optimize()')
        # Keep indentation in the conditional allocation workflow.
        t=t.replace('    optimizer = network.createOptimizer()\noptimizer.setMaxEvaluations(60)\nresult = optimizer.optimize()', '    optimizer = network.createOptimizer()\n    optimizer.setMaxEvaluations(60)\n    result = optimizer.optimize()')
    if ch==5:
        t=t.replace('bh_stream.setFlowRate(80000.0, "kg/hr")','bh_stream.setFlowRate(20000.0, "kg/hr")  # feasible teaching base; sweep higher rates separately')
        t=t.replace('prod_stream.setFlowRate(60000.0, "kg/hr")','prod_stream.setFlowRate(15000.0, "kg/hr")  # conservative gas-lift teaching base')
        t=t.replace('setElevation(-well_depth)','setElevation(well_depth)').replace('negative = upward','positive = upward')
        # The fixed-rate sweep must preserve rejected points instead of reading stale outputs.
        t=t.replace('    process.run()\n\n    whp =','    try:\n        process.run()\n    except Exception as error:\n        print("Infeasible fixed-rate tubing case:", str(error).splitlines()[0])\n        continue\n\n    whp =')
        t=t.replace('    process.run()\n\n    whp =','    try:\n        process.run()\n    except Exception as error:\n        print("Infeasible fixed-rate tubing case:", str(error).splitlines()[0])\n        continue\n\n    whp =')
    if ch==10:
        t=re.sub(r'// Separator implements CapacityConstrainedEquipment and AutoSizeable\npublic class Separator.*?\n\}', 'logger.info("Capacity implementation: {}", separator.getClass().getName());',t,flags=re.S)
        # This worked example stores Stream objects, not Phase objects.
        for name in ('gas','oil','water'):
            t=t.replace('print(f"'+name.title()+' density:   {'+name+'.getDensity', 'print(f"'+name.title()+' density:   {'+name+'.getFluid().getDensity')
        t=t.replace("{water.getDensity('kg/m3')", "{water.getFluid().getDensity('kg/m3')")
    if ch in (16,17):
        t=t.replace('process.add(feed);\nprocess.add(heater);\nprocess.run();','process.add(feed);\nprocess.run();')
        t=t.replace('process.add(feed);\nprocess.add(valve);\nprocess.run();','process.add(feed);\nprocess.run();')
    if ch==17:
        t=t.replace('valve.getDesignCv("US")','valve.getMechanicalDesign().getMaxDesignCv()')
        t=t.replace('valve.getDesignVolumeFlow("m3/hr")','valve.getMechanicalDesign().getMaxDesignVolumeFlow()')
        t=t.replace('valve.setDesignCv(350.0, "US")','valve.getMechanicalDesign().setMaxDesignCv(350.0)')
        t=t.replace('valve.setDesignVolumeFlow(2500.0, "m3/hr")','valve.getMechanicalDesign().setMaxDesignVolumeFlow(2500.0)')
    if ch==9:
        t=t.replace('pipeline.getMaxDesignVelocity()','pipeline.getMechanicalDesign().getMaxDesignVelocity()')
        t=t.replace('pipeline.getMaxDesignPressureDrop()','pipeline.getMechanicalDesign().getMaxDesignPressureDrop()')
        t=t.replace('pipeline.setMaxDesignPressureDrop(15.0)','pipeline.getMechanicalDesign().setMaxDesignPressureDrop(15.0)')
        t=t.replace('pipeline.setMaxLOF(', 'pipeline.setMaxDesignLOF(').replace('pipeline.setMaxFRMS(', 'pipeline.setMaxDesignFRMS(')
    p.write_text(t,encoding='utf-8')

# Heat exchanger report gets a complete two-stream model rather than a missing object.
p=BOOK/'chapters/ch16_heat_exchangers/chapter.md';t=p.read_text(encoding='utf-8')
t=t.replace('// Java: Generate heat exchanger feasibility report','''import neqsim.process.equipment.heatexchanger.HeatExchanger;
import neqsim.process.mechanicaldesign.heatexchanger.HeatExchangerDesignFeasibilityReport;
SystemSrkEos coldFluid = new SystemSrkEos(288.15, 5.0);
coldFluid.addComponent("water", 1.0);
coldFluid.setMixingRule("classic");
Stream cold = new Stream("Cooling water", coldFluid);
cold.setFlowRate(30000.0, "kg/hr");
cold.run();
feed.setTemperature(120.0, "C");
feed.run();
HeatExchanger heatExchanger = new HeatExchanger("HX-01", feed, cold);
heatExchanger.setUAvalue(10000.0);
heatExchanger.run();
// Generate a screening report; supplier matching is not a vendor guarantee.''')
p.write_text(t,encoding='utf-8')
