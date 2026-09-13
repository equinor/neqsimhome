"""Align manuscript outputs with rerun notebooks and correct physical interpretation."""
from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
def p(n):return next((B/'chapters').glob(f'ch{n:02d}*/chapter.md'))
def edit(n, fn):
 f=p(n); f.write_text(fn(f.read_text(encoding='utf-8-sig')),encoding='utf-8')
edit(21,lambda s:s.replace('config = (OptimizationConfig(', 'config = (ProductionOptimizer.OptimizationConfig('))
edit(32,lambda s:s.replace('detector.isAllSteadyState()', 'detector.evaluate().isAtSteadyState()'))
def quality(s):
 a=s.index('    # Wobbe index: W = HHV / sqrt(relative_density)');b=s.index('\n```',a)
 s=s[:a]+'''    quality = jneqsim.standards.gasquality.Standard_ISO6976(gas, 15.0, 15.0, "volume")
    quality.calculate()
    wobbe = float(quality.getValue("SuperiorWobbeIndex")) / 1000.0
    properties["h2_pct"].append(float(h2_frac) * 100)
    properties["density_kgm3"].append(float(density))
    properties["wobbe_MJm3"].append(wobbe)

print("H2 mol% | density kg/m3 | superior Wobbe MJ/m3 at 15 C reference")
for h2, density, wobbe in zip(properties["h2_pct"], properties["density_kgm3"],
                               properties["wobbe_MJm3"]):
    print(f"{h2:7.1f} | {density:13.4f} | {wobbe:12.3f}")
# Flame propagation is outside this thermodynamic model; use validated combustion data.
''' + s[b:]
 s=s.replace('"wobbe_MJm3": [], "flame_speed_rel": []', '"wobbe_MJm3": []')
 s=s.replace('0-20 vol% H2', '0-20 mol% H2 (approximately volume fraction for ideal gas)')
 s=s.replace('print("→ CO2 is miscible with oil at these conditions")', 'print("Single equilibrium phase for this overall composition at this P,T")')
 s=s.replace('print("→ CO2 is immiscible — pressure below MMP")', 'print("Multiple equilibrium phases for this overall composition at this P,T")\nprint("A single flash does not determine multicontact minimum miscibility pressure")')
 s=s.replace('figures/ch24_co2_phase_envelope.png','figures/ch35_co2_density_compressibility.png')
 s=s.replace('Co2 Phase Envelope','CO2 density and compressibility screening')
 s=s.replace('CO$_2$ is non-toxic', 'CO$_2$ is an asphyxiant at elevated concentration and')
 s+='''

### Reading the regenerated composition screens

The companion notebook's binary methane/hydrogen series uses ISO 6976 with both volume and combustion reference temperatures at 15°C. Superior Wobbe index falls from 50.73 MJ/m³ for methane to 44.63 MJ/m³ at 50 mol% hydrogen. This binary series has a different base composition from the methane/ethane/propane worked example above; their endpoint values should not be interchanged. The calculation describes gas quality, while material compatibility and combustion behavior require their own evidence.

The CO2 figure is a density and compressibility-factor sweep. It helps identify rapid property changes in the sampled pressure range. It is not a phase envelope and does not establish a pipeline operating envelope or an MMP.
'''
 return s
edit(35,quality)
edit(28,lambda s:s+'''

### A verified upward-flow pressure solve

The companion notebook now solves upward production flow by finding the bottomhole pressure that reproduces the specified wellhead pressure. For the declared fluid and geometry, 30,000 kg/hr at 80 bara wellhead pressure requires 155.869 bara bottomhole pressure. All 60 sampled points solved; the maximum wellhead-pressure residual was 0.011934 bar. Required bottomhole pressure spans 53.792–272.216 bara across that grid. These results belong to the notebook's well model, distinct from the process-capacity diagnostic tables above.

Hydrostatic elevation and friction both demand additional upstream pressure in this upward-flow case. Before exporting a production VFP table, preserve the production direction, rate basis, fluid composition, well datum and residual for every point. A reduced route length alone does not simulate a booster or qualify an alternative field concept.
''')
edit(33,lambda s:s+'''

### Interpreting the regenerated TEG sensitivity

The notebook uses a CPA fluid model and `SimpleTEGAbsorber` with 99.5 wt% lean TEG, five stages and 70% stage efficiency. At the declared feed conditions, increasing circulation from 500 to 909.1 kg/hr reduces outlet water from 36.596 to 22.723 ppmv. At 5,000 kg/hr the result is 18.195 ppmv; the sampled minimum is 18.177 ppmv at 4,181.8 kg/hr. The plateau shows diminishing returns at fixed solvent purity and stage performance. Increasing circulation alone cannot be assumed to meet a lower moisture specification: evaluate regeneration, lean-solvent purity, contactor efficiency and uncertainty together.
''')
