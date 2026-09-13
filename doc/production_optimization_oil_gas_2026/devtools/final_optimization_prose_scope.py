from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
def path(n):return next((B/'chapters').glob(f'ch{n:02d}_*/chapter.md'))
p=path(20);t=p.read_text(encoding='utf-8-sig');a=t.index('## 20.11 Debottlenecking Strategies');b=t.index('## 20.12',a)
section=t[a:b].replace('Typical Capacity Increase','Capacity qualification')
section=section.replace('When a bottleneck is identified, several strategies can be considered:',
 'When a bottleneck is identified, the following modifications can be screened. No general percentage gain is supported for a specified installed unit. Recalculate the full process with vendor performance, pressure loss, control and shared-resource constraints; adding nominal parallel capacity need not double production.')
section=re.sub(r'\| (?:\d+–\d+%[^|\n]*|100%[^|\n]*) \|', '| Requires unit and whole-process re-rating |',section)
section=section.replace('Doubles total capacity','Adds nominal installed capacity').replace('Doubles flow capacity','Adds nominal flow capacity').replace('Doubles capacity','Adds nominal exchanger capacity')
t=t[:a]+section+t[b:];p.write_text(t,encoding='utf-8')
p=path(31);t=p.read_text(encoding='utf-8-sig').replace('Cubic equations of state are known to predict liquid densities with systematic errors of 5–15%.',
 'Untranslated cubic equations of state can have substantial systematic liquid-density errors; their magnitude depends on fluid, temperature and pressure and must be benchmarked for the application.')
p.write_text(t,encoding='utf-8')
p=path(32);t=p.read_text(encoding='utf-8-sig').replace('Which method produces tighter intervals while maintaining the coverage guarantee?',
 'Compare interval widths and empirical coverage. State the exchangeability assumptions for marginal conformal coverage, and explain why ensemble spread alone has no distribution-free coverage guarantee.')
p.write_text(t,encoding='utf-8')
p=path(27);t=p.read_text(encoding='utf-8-sig').replace(
 'Tornado diagram showing the sensitivity of gas production to uncertain input parameters. Bars show low/high input endpoints relative to the base. Compressor efficiency has zero gas-yield effect in this prescribed upstream-feed model.',
 'CPA three-phase separator gas-rate sensitivity at a prescribed feed rate. The water input is overall water mole fraction. Low/high bars use the declared input endpoints and include the base in their range; isentropic efficiency has exactly zero upstream gas-rate response because the compressor has no feedback to the feed or separator. All eleven cases pass material and energy checks.')
p.write_text(t,encoding='utf-8')
print('Final prose scope corrections complete')
