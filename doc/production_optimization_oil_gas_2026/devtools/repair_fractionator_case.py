from pathlib import Path
BOOK=Path(__file__).resolve().parents[1]
p=next((BOOK/'chapters').glob('ch12*/chapter.md'))
t=p.read_text(encoding='utf-8')
t=t.replace('# Reduced eight-tray teaching column; not a 25-stage plant design', '# Five-stage cold-feed stripping section: no condenser or external reflux')
t=t.replace('"Deethanizer", 8, True, True', '"Deethanizer", 5, True, False')
t=t.replace('deethanizer.addFeedStream(ngl_feed, 4)', 'deethanizer.addFeedStream(ngl_feed, 5)  # cold feed at the top')
t=t.replace('deethanizer.getCondenser().setRefluxRatio(1.0)\ndeethanizer.getReboiler().setRefluxRatio(1.0)\n# Terminal ratios are specified; temperatures and duties are calculated.', 'deethanizer.setTopPressure(25.0)\ndeethanizer.setBottomPressure(26.0)\ndeethanizer.getReboiler().setOutTemperature(273.15 + 105.0)\n# Reboiler outlet temperature is specified; duty is calculated.')
t=t.replace('overhead = deethanizer.getCondenser().getGasOutStream()', 'overhead = deethanizer.getGasOutStream()')
needle='# NGL feed from turboexpander plant'
pos=t.rfind('```python',0,t.index(needle))
t=t[:pos]+('This compact example represents the cold-feed stripping section with five equilibrium stages and a reboiler. A complete deethanizer may also need rectification, a condenser and reflux; this model does not claim that full equipment scope. It prints the current convergence report and rejects unsolved products before reporting duty or temperatures.\n\n')+t[pos:]
p.write_text(t,encoding='utf-8')
p=next((BOOK/'chapters').glob('ch14*/chapter.md'))
t=p.read_text(encoding='utf-8')
t=t.replace('Heavier gases require more power per unit mass but less power per unit volume:', 'At comparable temperature, pressure ratio and efficiency, heavier gases generally require less specific head per unit mass; compressibility and heat capacity also affect the result. A fixed mass-flow comparison must be distinguished from a fixed standard-volume-flow comparison:')
t=t.replace('head = comp.getPolytropicHead()', 'head = comp.getPolytropicFluidHead()')
t=t.replace('f"{head:>8.0f} J/kg"', 'f"{head:>8.1f} kJ/kg"')
t=t.replace('// W (25 MW)', '// kW (25 MW)')
p.write_text(t,encoding='utf-8')
