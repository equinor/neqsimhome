"""Repair remaining Chapter21 engineering examples before exact-source checks."""
from pathlib import Path
import re
BOOK=Path(__file__).resolve().parents[1]
p=next((BOOK/'chapters').glob('ch21*/chapter.md'));text=p.read_text(encoding='utf-8')
pat=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
replacements={}
for i,m in enumerate(pat.finditer(text),1):
    code=m[3]
    if i in (25,28):
        code=code.replace('SystemSrkEos(', 'SystemSrkCPAstatoil(').replace('fluid.setMixingRule("classic")','fluid.setMixingRule(10)')
    if i==25:
        code=code.replace('comp.setPolytropicEfficiency(0.78)','comp.setUsePolytropicCalc(True)\ncomp.setPolytropicEfficiency(0.78)')
        code=code.replace('    new_rate = float(feed.getFlowRate("kg/hr"))','    assert optimum.isFeasible(), "Relaxed candidate failed declared constraints"\n    new_rate = float(feed.getFlowRate("kg/hr"))\n    assert abs(new_rate - optimum.getOptimalRate()) <= 1e-6 * max(new_rate, 1.0)')
        code=code.replace("+ [0],\n       bottom=", "+ [current_rate],\n       bottom=")
        code=code.replace("'Debottlenecking Waterfall Analysis'","'Assumed constraint-relaxation sensitivity'")
    if i==28:
        code=code.replace('Separator = jneqsim.process.equipment.separator.Separator','Separator = jneqsim.process.equipment.separator.ThreePhaseSeparator')
        code=code.replace('compressor.setOutletPressure(150.0, "bara")','compressor.setOutletPressure(150.0, "bara")\ncompressor.setIsentropicEfficiency(0.78)')
    if i==30:
        code=code.replace('# Re-run to find new operating point','# Rerun the imposed-rate model: disabling a constraint does not change feed flow')
        code=code.replace('delta_q = debottlenecked_flow - baseline_flow','delta_q = debottlenecked_flow - baseline_flow\nassert abs(delta_q) <= 1e-9, "A reporting mask must not alter the imposed feed rate"')
    if i==36:
        code=code.replace('    pi = npv / opt["capex_mnok"]','    pi = 1.0 + npv / opt["capex_mnok"]\n    annuity_factor = (1.0 - (1.0 + discount_rate)**(-remaining_years)) / discount_rate\n    assert abs(pv_factor - annuity_factor) < 1e-12\n    assert abs(pi - annual_revenue_mnok * annuity_factor / opt["capex_mnok"]) < 1e-10')
    if i==39:
        code=code.replace('"date": "2025-01-15"','"date": "2026-09-12"')
    if code!=m[3]:replacements[m.span(3)]=code
for (start,end),code in sorted(replacements.items(),reverse=True):text=text[:start]+code+text[end:]
text=text.replace('This waterfall analysis reveals not just the first bottleneck, but the entire **bottleneck sequence** — the ordered list of constraints that must be removed to progressively increase production. Often, removing the first bottleneck yields 60-80% of the total potential gain, with diminishing returns for subsequent debottlenecks.',
    'This calculation ranks the effects of relaxing the configured screening constraints inside the declared search interval. It is a diagnostic sensitivity: disabling a constraint does not physically modify equipment or qualify a higher installed capacity. The search upper bound may become the final limit. Keep a fresh replay and an independent sampled comparison for each selected point; no universal percentage gain follows from the order of relaxed constraints.')
text=text.replace('This sensitivity plot reveals critical information: at what production rate does the bottleneck shift from one equipment item to another? This determines the sequence of debottlenecking projects needed to reach different production targets.',
    'The sweep identifies the largest configured utilization at each imposed feed rate. An overload is retained as a rejected operating screen, not silently clipped to 100 percent. Changes in the highest utilization suggest which restrictions deserve a detailed study; they do not determine a physical retrofit sequence without installed ratings and project evidence.')
text=text.replace('## 21.9 Summary','## 21.12 Summary')
text=text.replace('4. **What-if analysis** through selective constraint disabling quantifies the production gain from each potential debottleneck',
    '4. **What-if analysis** separates a constraint-reporting mask from a reoptimized candidate; only the latter estimates a conditional rate change, and neither establishes an installed-equipment modification')
text=text.replace('This automated approach enables regular (weekly or monthly) capacity assessments without manual engineering effort, ensuring that debottlenecking opportunities are identified as soon as they arise.',
    'The report automates extraction and ranking of configured capacity information. An engineer must still review model calibration, current operating states, missing restrictions and installed-rating provenance; scheduled report generation alone does not ensure an opportunity is valid or timely.')
text=text.replace('3. **autoSize** creates constraints from design calculations, enabling quick capacity assessment of existing equipment',
    '3. **autoSize** supplies calculated screening dimensions and ratings; existing equipment requires its actual geometry and rating evidence')
text=text.replace('- Large capital items (new vessels, new compressor trains) typically require 2–3 years of planning and fabrication and are justified only when the remaining field life exceeds 10 years',
    '- Large projects need a schedule and discounted cash-flow analysis; there is no universal ten-year remaining-life threshold for economic justification')
text=text.replace('4. **What-If Debottlenecking**: Starting from Exercise 3, disable the bottleneck constraint and re-run. What is the new bottleneck? Calculate the total production gain from removing both the first and second bottleneck.',
    '4. **What-If Debottlenecking**: Starting from Exercise 3, disable a reporting constraint and verify that the imposed feed rate stays unchanged. Then perform a bounded throughput search, replay each selected point, and compare the result with a grid. Explain why relaxing two constraints is still not an approved equipment modification.')
p.write_text(text,encoding='utf-8')
print('Revised Chapter21 solution basis and associated interpretation.')
