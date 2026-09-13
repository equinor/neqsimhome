"""Replace fabricated integrated-case results with checked runnable boundaries."""
import re,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];p=next((B/'chapters').glob('ch34*/chapter.md'))
t=p.read_text(encoding='utf-8-sig');backup=B/'.build/backups/scientific_revision'/p.parent.name/'cases_input.md';backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():backup.write_text(t,encoding='utf-8')
changes=[]
def r(a,b):
 global t
 assert a in t,a[:100]
 t=t.replace(a,b);changes.append({'before':a,'after':b})
def section(a,b,new):
 global t
 i=t.index(a);j=t.index(b,i);changes.append({'before':t[i:j],'after':new});t=t[:i]+new+'\n\n'+t[j:]
fences=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',t,re.M|re.S))
replacements={1:(B/'devtools/scientific_case34_models.py').read_text(encoding='utf-8'),2:'''# Assumed screening limits; no vendor or hydraulic qualification is implied.
screen_limits = {'export_gas_MSm3day':12.0, 'export_power_MW':25.0}
platform_utilization = {key: platform_base[key]/limit
                        for key,limit in screen_limits.items()}
assert all(np.isfinite(v) and v>=0 for v in platform_utilization.values())
print(json.dumps({'screening_utilization':platform_utilization},indent=2))
''',3:'''import matplotlib.pyplot as plt
Path('figures').mkdir(exist_ok=True)
platform_sweep=[]
for php in np.linspace(60.0,100.0,9):
    _,row,_=build_platform_case(float(php))
    row['screen_feasible']=all(row[k]<=v for k,v in screen_limits.items())
    platform_sweep.append(row)
assert len(platform_sweep)==9
Path('ch34_platform_sweep.json').write_text(json.dumps(platform_sweep,indent=2))
fig,axes=plt.subplots(1,2,figsize=(11,4))
axes[0].plot([r['hp_bara'] for r in platform_sweep],
             [r['total_liquid_kghr']/1000 for r in platform_sweep],'o-')
axes[0].set_ylabel('All withdrawn hydrocarbon liquids (t/hr)')
axes[1].plot([r['hp_bara'] for r in platform_sweep],
             [r['power_MW'] for r in platform_sweep],'s-')
axes[1].set_ylabel('Total compression shaft power (MW)')
for ax in axes:ax.set_xlabel('HP separator pressure (bara)');ax.grid(alpha=.3)
fig.suptitle('Reduced platform: checked pressure sensitivity')
fig.tight_layout();fig.savefig('figures/ch23_case1_hp_optimization.png',dpi=150)
plt.close(fig)
print(json.dumps(platform_sweep,indent=2))
'''}
for num,code in sorted(replacements.items(),reverse=True):
 m=fences[num-1];t=t[:m.start(3)]+code.rstrip()+'\n'+t[m.end(3):]
r('This chapter presents three complete case studies that exercise the full breadth of techniques covered in this book. Each case study is a self-contained engineering problem with a defined scope, realistic fluid composition, process description, NeqSim model, results analysis, and optimization.', 'This chapter presents three reduced, reproducible teaching calculations and their wider engineering context. The calculations use disclosed fluid recipes, imposed boundaries and assumed screening limits. They do not constitute calibrated full-field models. Each executable case must pass explicit balance and finite-state checks; omitted wells, treatment, installed maps and product qualifications remain outside acceptance.')
r('An FPSO (Floating Production, Storage, and Offloading) vessel produces heavy oil from a deepwater field.', 'The second teaching scenario concerns an FPSO (Floating Production, Storage, and Offloading) handling an oil-like hydrocarbon recipe and water.')
r('The heavy oil has an API gravity of approximately 22° and a GOR of 80 Sm$^3$/Sm$^3$:', 'The disclosed hydrocarbon recipe below is a simplified surrogate. Its stock-tank density and GOR must be calculated; the recipe is not a characterized 22°API heavy oil and contains no measured heavy-end fraction:')
r('The following design limits were extracted from the original equipment data sheets:', 'The following numbers are assumed context for a larger plant. No original vendor data sheets are supplied, and omitted units are not validated by the reduced calculation:')
r('The optimal solution allocates gas lift such that the marginal oil gain per unit gas lift is equal across all wells:', 'For smooth concave well responses and a binding shared gas budget, free interior wells have equal marginal oil gain. Wells at lower/upper bounds satisfy the corresponding KKT inequalities; discrete well activation needs separate treatment:')
r('The optimization typically shows that wells with higher productivity index should receive more gas lift, while wells near their gas lift plateau receive less.', 'Allocation follows marginal oil response and coupled constraints, not productivity-index ranking alone. The caller-dependent well-model pattern is not a computed allocation for this FPSO; Chapter 22 supplies a checked native curve-allocation example.')
section('### 34.2.7 Results and Conclusions','## 34.3 Case Study 2', '''### 34.2.7 Results and Acceptance

The literal model includes an imposed-rate feed, HP/LP equilibrium separation, cooled three-stage LP recompression, equilibrium knockout before each compressor, and export compression/aftercooling/knockout. Recompression discharge matches the selected HP pressure. It does not model four individual wells, a 12 km line, TEG treatment, a stabilizer or a 200 km export line. A throttling valve represents an imposed pressure boundary, not hydraulic prediction.

Each fresh case checks total mass and component flows to $10^{-7}$ relative and whole-boundary energy to $10^{-5}$ relative, including every knockout liquid and all shaft/cooling duties. Positive compressor work, rising discharge pressure and single-phase compressor inlet are asserted. These checks establish internal physical consistency under the SRK equilibrium assumptions.

`ch34_platform_base.json` and `ch34_platform_sweep.json` contain the executed baseline and nine pressure points. The sensitivity figure uses those actual values. Liquid withdrawn at different process pressures is aggregated by **mass**; it is not claimed to be stock-tank condensate volume. The printed 12 MSm³/day gas and 25 MW export-driver screens are assumed restrictions, with other installed-equipment evidence explicitly absent. No economic optimum, 5–8% uplift or 13 MSm³/day approved capacity is inferred from this pressure sweep.

---
''')
section('#### Water Cut Impact Summary Table','#### Gas Lift Allocation Optimization', '''#### Water Cut Result Interpretation

Use the executed water-cut sweep and the stated volumetric reference conditions. Water cut is not a mole fraction or mass fraction. Compare separator liquid capacity with oil and aqueous flows **at that separator**, not with oil after downstream flashing. No gas-lift demand curve or well deliverability model is supplied by this separation/compression example.

The legacy hand-entered water-cut milestone table has been removed because it did not follow from the model and contradicted its claimed separator bottleneck. The actual sweep records the assumed 400 m³/hr screening ratio without implying that 65% water cut is a universal limit.
''')
section('### 34.3.6 Results and Conclusions','## 34.4 Case Study 3', '''### 34.3.6 Engineering Interpretation

At fixed total standard-liquid volume, increasing water cut displaces hydrocarbon liquid; at fixed oil rate it instead increases total liquid demand. The boundary choice must therefore accompany every water-cut conclusion. The reduced model does not establish reservoir-driven gas evolution, a 150 ppm treated-water specification, gas-lift demand or PWRI economics. Assess those systems with their own calibrated models before selecting modifications.

---
''')
section('### 34.4.5 Bottleneck Identification','### 34.4.6 Debottlenecking Solutions', '''### 34.4.5 Screening Coverage

The reduced model reports inlet gas flow, expander work and residue-compressor power against the three assumed limits used in the code. Amine, dehydration and fractionation units are not included, so no 102% amine loading or spare fractionation capacity can be inferred. Cold separation provides an NGL stream, not a fractionated product specification.
''')
section('### 34.4.8 Modification Cost-Benefit Analysis','## 34.5 Synthesis', '''### 34.4.8 Cost and Decision Basis

Repacking, re-wheeling and driver replacement are candidate engineering studies, not accepted modifications. Vendor hydraulic/performance evidence, material compatibility, motor/shaft restrictions, utility limits and shutdown costs are required. Equipment capacity gains cannot be added to obtain plant capacity gain.

The economic arithmetic example explicitly assumes an incremental saleable gas volume, calorific value, price and operating days. It demonstrates dimensional consistency only; feed increment is not necessarily residue-gas sales increment. No measured CAPEX, net cash flow, payback recommendation or qualified 300/325 MMscfd plant throughput is supplied.

---
''')
section('### 34.5.2 Bottlenecks Shift Over Time','### 34.5.3', '''### 34.5.2 Bottlenecks Require Current Evidence

Pressure, composition and water fraction change equipment loads. Identify restrictions using current solved states and declared installed limits; the examples cannot diagnose omitted units. Repeat the capacity assessment after each accepted change (Chapters 20–25).
''')
section('## Summary','<!-- September 2026 source update -->', '''## Summary

The cases demonstrate pressure sensitivity, volumetric water-cut handling and an NGL compression screen on disclosed reduced models. Balance checks and independent fresh cases support the reported calculations. Full well hydraulics, solvent treatment, fractionation quality, installed equipment ratings and economic decisions require additional evidence. The reproduced notebook case is a separate specified model and retains its own output provenance.

---

''')
r('Lower HP pressure increases condensate recovery but requires more recompression power.', 'Interpret both axes from the executed sweep; direction and optimum depend on composition, cooling and the liquid reference state.')
r('GPSA (2024)','GPSA (2016)') if 'GPSA (2024)' in t else None
p.write_text(t,encoding='utf-8')
(B/'verification/scientific_revision/case_corrections.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
print(len(changes),'case changes')
