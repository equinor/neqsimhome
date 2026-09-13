"""Scratch: isolate why a re-run separator returns the whole feed as gas."""

from neqsim import jneqsim

SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

fluid = SystemSrkEos(273.15 + 50.0, 60.0)
for c, x in [("methane", 0.80), ("ethane", 0.08), ("propane", 0.05), ("n-heptane", 0.07)]:
    fluid.addComponent(c, x)
fluid.setMixingRule("classic")

feed = Stream("feed", fluid)
feed.setFlowRate(100000.0, "kg/hr")
feed.setTemperature(50.0, "C")
feed.setPressure(60.0, "bara")
sep = Separator("HP Sep", feed)

p = ProcessSystem()
p.add(feed)
p.add(sep)

for i in range(4):
    p.run()
    print(f"run {i}: feed={float(feed.getFlowRate('kg/hr')):9.1f}  "
          f"gas={float(sep.getGasOutStream().getFlowRate('kg/hr')):9.1f}  "
          f"liq={float(sep.getLiquidOutStream().getFlowRate('kg/hr')):9.1f}")

print("\nnow change separator pressure between runs")
for i, pres in enumerate([60.0, 60.0, 50.0, 50.0]):
    sep.setPressure(pres, "bara")
    p.run()
    print(f"run {i} (P={pres}): gas={float(sep.getGasOutStream().getFlowRate('kg/hr')):9.1f}  "
          f"liq={float(sep.getLiquidOutStream().getFlowRate('kg/hr')):9.1f}")
