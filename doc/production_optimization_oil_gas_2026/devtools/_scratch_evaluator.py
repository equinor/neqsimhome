"""Scratch: prove the real ProcessSimulationEvaluator / optimizer APIs work from Python."""

from neqsim import jneqsim

SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
Compressor = jneqsim.process.equipment.compressor.Compressor
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
Evaluator = jneqsim.process.util.optimizer.ProcessSimulationEvaluator


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
    return p, feed, sep, comp


p, feed, sep, comp = build()
print("baseline power kW:", round(float(comp.getPower("kW")), 1))

ev = Evaluator(p)
ev.addParameter("HP Sep", "pressure", 30.0, 90.0, "bara")
ev.addParameter("feed", "flowRate", 50000.0, 200000.0, "kg/hr")

Direction = jneqsim.process.util.optimizer.ProcessSimulationEvaluator.ObjectiveDefinition.Direction

ev.addObjective(
    "gas export",
    lambda proc: float(proc.getUnit("HP Sep").getGasOutStream().getFlowRate("kg/hr")),
    Direction.MAXIMIZE,
)
ev.addConstraintUpperBound(
    "compressor power",
    lambda proc: float(proc.getUnit("Export Compressor").getPower("kW")),
    4000.0,
)

print("params:", ev.getParameterCount(), "objs:", ev.getObjectiveCount(),
      "cons:", ev.getConstraintCount())
print("bounds lo:", list(ev.getLowerBounds()), "hi:", list(ev.getUpperBounds()))

res = ev.evaluate([60.0, 120000.0])
print("objectives:", list(res.getObjectives()))
print("raw:", list(res.getObjectivesRaw()))
print("constraint values:", list(res.getConstraintValues()))
print("feasible:", bool(res.isFeasible()), "converged:", bool(res.isSimulationConverged()))
print("penalized:", ev.evaluatePenalizedObjective([60.0, 120000.0]))
