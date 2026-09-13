from pathlib import Path
import re,json
B=Path(__file__).resolve().parents[1];p=next((B/'chapters').glob('ch34*/chapter.md'));t=p.read_text(encoding='utf-8-sig')
fences=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',t,re.M|re.S))
replacements={7:(B/'devtools/scientific_case34_ngl.py').read_text(encoding='utf-8'),8:'''# Economic arithmetic under explicit assumptions, independent of the plant screen.
incremental_saleable_gas_MMscfd=50.0
hhv_MMBtu_per_scf=0.001025
price_USD_per_MMBtu=4.0
operating_days=330
assumed_capex_USD=2.5e6
annual_gross_USD=(incremental_saleable_gas_MMscfd*1e6*hhv_MMBtu_per_scf
                  *price_USD_per_MMBtu*operating_days)
assert abs(annual_gross_USD-67.65e6)<1e-6
print('Assumed incremental annual gross revenue (million USD):',annual_gross_USD/1e6)
print('CAPEX/gross revenue ratio (years, not net payback):',assumed_capex_USD/annual_gross_USD)
# Net project cash flow requires gas purchase/opportunity cost, OPEX, outages and tax.
''',9:'''import matplotlib.pyplot as plt
Path('figures').mkdir(exist_ok=True)
ngl_sweep=[]
for multiplier in np.linspace(.9,1.3,9):
    _,row=build_gas_plant(float(multiplier*design_rate))
    row['multiplier']=float(multiplier)
    row['screen_utilization']={k:row[k]/v for k,v in ngl_limits.items()}
    row['screen_feasible']=all(v<=1 for v in row['screen_utilization'].values())
    ngl_sweep.append(row)
assert len(ngl_sweep)==9
Path('ch34_ngl_sweep.json').write_text(json.dumps(ngl_sweep,indent=2))
fig,axes=plt.subplots(1,2,figsize=(11,4))
for key in ngl_limits:
    axes[0].plot([100*r['multiplier'] for r in ngl_sweep],
                 [100*r['screen_utilization'][key] for r in ngl_sweep],'o-',label=key)
axes[0].axhline(100,color='black',linestyle='--');axes[0].legend(fontsize=8)
axes[0].set_ylabel('Declared screening utilization (%)')
axes[1].plot([100*r['multiplier'] for r in ngl_sweep],
             [r['liquid_kghr']/1000 for r in ngl_sweep],'s-')
axes[1].set_ylabel('All withdrawn liquids (t/hr)')
for ax in axes:ax.set_xlabel('Feed mass rate (% of290,000kg/hr)');ax.grid(alpha=.3)
fig.suptitle('Reduced NGL model: explicit cooling and three declared screens')
fig.tight_layout();fig.savefig('figures/ch23_case3_debottleneck_analysis.png',dpi=150)
plt.close(fig)
print(json.dumps(ngl_sweep,indent=2))
'''}
for n,c in sorted(replacements.items(),reverse=True):
 m=fences[n-1];t=t[:m.start(3)]+c.rstrip()+'\n'+t[m.end(3):]
start=t.index('Three debottlenecking options are evaluated:');end=t.index('```python',start)
t=t[:start]+'''Three candidate studies for a fully specified plant are absorber internals, expander performance and driver capacity. No vendor rating, cost quotation or shutdown schedule is supplied, so the previous numerical upgrade gains and costs are not retained as evaluated results. The following arithmetic example teaches the price/energy/volume conversion and does not recommend any of these modifications.

'''+t[end:]
t=t.replace('Equipment utilization and NGL recovery as a function of feed rate for the gas plant debottlenecking study.', 'The actual reduced NGL sweep reports three assumed screening ratios and all withdrawn liquid mass. A specified-temperature cooler supplies external refrigeration; no second heat-exchanger stream, amine unit, dehydration unit or fractionation column is implicitly modeled. Expander and compressor work are reported separately; they are not asserted to balance on a shared shaft.')
t=t.replace('This chapter presents three complete case studies','This chapter presents three reduced teaching case studies')
t=t.replace('Chapter 18)', 'Chapters 20–25)')
# Actual FPSO result text from the independently checked parent-owned literal model.
needle='### 34.3.6 Engineering Interpretation\n'
addition='''
At the 30% reference water cut and fixed200m³/hr total reference liquid, the CPA model gives149.069m³/hr final oil at2.5bara,61.996m³/hr first-stage water at35bara/70°C, and0.306854MW compression. First-stage oil plus water at the same35bara/70°C totals223.752m³/hr, or55.94% of the assumed400m³/hr screen. Across10–80% reference water cut, first-stage utilization decreases57.18→52.85%; this particular boundary does not produce an increasing liquid-load bottleneck. Full mass/component/energy checks and the fifteen-case records are retained with the verification artifacts.

'''
t=t.replace(needle,needle+addition)
p.write_text(t,encoding='utf-8');print('NGL case replaced; parent FPSO fences preserved')
