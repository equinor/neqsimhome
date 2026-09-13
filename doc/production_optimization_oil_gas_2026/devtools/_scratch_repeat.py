"""Scratch: is ProcessSimulationEvaluator.evaluate() repeatable?"""

from neqsim import jneqsim

SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
Compressor = jneqsim.process.equipment.compressor.Compressor
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
Evaluator = jneqsim.process.util.optimizer.ProcessSimulationEvaluator
Direction = Evaluator.ObjectiveDefinition.Direction


def build():
    fluid = SystemSrkEos(273.15 + 50.0, 60.0)
    fluid.addComponent("methane", 0.80)
    fluid.addComponent("ethane", 0.08)
    fluid.addComponent("propane", 0.05)
    fluid.addComponent("n-heptane", 0.07)
    fluid.setMixingRule("classic")
    feed = Stream("feed", fluid)
    feed.setFlowRate(100000.0, "kg/hr")
    feed.setTemperature(50.0, "C")
    feed.setPressure(60.0, "bara")
    sep = Separator("HP Sep", feed)
    comp = Compressor("Export Compressor", sep.getGasOutStream())
    comp.setOutletPressure(120.0, "bara")
    comp.setPolytropicEfficiency(0.78)
    comp.setUsePolytropicCalc(True)
    p = ProcessSystem()
    for u in (feed, sep, comp):
        p.add(u)
    p.run()
    return p


for clone in (False, True):
    p = build()
    ev = Evaluator(p)
    ev.setCloneForEvaluation(clone)
    ev.addParameter("HP Sep", "pressure", 30.0, 90.0, "bara")
    ev.addParameter("feed", "flowRate", 50000.0, 200000.0, "kg/hr")
    ev.addObjective(
        "gas export",
        lambda proc: float(proc.getUnit("HP Sep").getGasOutStream().getFlowRate("kg/hr")),
        Direction.MAXIMIZE,
    )
    vals = [float(ev.evaluate([60.0, 120000.0]).getObjectivesRaw()[0]) for _ in range(4)]
    print(f"cloneForEvaluation={clone}: {[round(v, 1) for v in vals]}")
