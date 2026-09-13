from pathlib import Path
import re
BOOK=Path(__file__).resolve().parents[1]
p=next((BOOK/'chapters').glob('ch10*/chapter.md'))
t=p.read_text(encoding='utf-8')
matches=list(re.finditer(r'^```(python|java)\s*\n(.*?)^```',t,re.M|re.S))
first=matches[6]; code=first[2]
code=code.replace('for mp_P in mp_pressures:\n', 'lp_liquid_rates = []\nfor mp_P in mp_pressures:\n')
code=code.replace('    print(f"{mp_P:>12} {oil_rate:>24.3f}")', '    lp_liquid_rates.append(oil_rate)\n    print(f"{mp_P:>12} {oil_rate:>24.3f}")')
code+='''
# A dedicated figure for this LP=2 bara case; do not reuse the later LP=3 bara plot.
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.plot(mp_pressures, lp_liquid_rates, "o-", color="#0F6B86")
ax.set(xlabel="MP separator pressure (bara)",
       ylabel="LP separator liquid rate (m3/hr)",
       title="Liquid recovery at 2 bara LP pressure")
ax.grid(True, alpha=0.25)
fig.tight_layout()
fig.savefig("figures/mp_pressure_lp_liquid_recovery.png", dpi=220, bbox_inches="tight")
plt.show()
'''
later=matches[26]; other=later[2]
start=other.index('# Fixed HP separator pressure')
end=other.index('# Plot\n',start)
other=other[:start]+'''# Size the physical vessels ONCE at the baseline MP pressure.
mp_pressures = np.arange(10.0, 55.0, 5.0)
lp_pressure = 3.0
f = Stream("Feed", fluid.clone())
f.setFlowRate(100000.0, "kg/hr")
f.setTemperature(75.0, "C")
f.setPressure(70.0, "bara")
hp = Separator("HP", f)
v1 = ThrottlingValve("V1", hp.getLiquidOutStream())
v1.setOutletPressure(30.0)
mp = Separator("MP", v1.getOutletStream())
v2 = ThrottlingValve("V2", mp.getLiquidOutStream())
v2.setOutletPressure(lp_pressure)
lp = Separator("LP", v2.getOutletStream())
proc = ProcessSystem()
for unit in [f, hp, v1, mp, v2, lp]:
    proc.add(unit)
proc.run()
for vessel in [hp, mp, lp]:
    vessel.autoSize(1.2)
proc.run()

oil_recovery, hp_utils, mp_utils = [], [], []
for mp_P in mp_pressures:
    v1.setOutletPressure(float(mp_P))
    proc.run()  # the same vessel geometry is retained for every trial
    oil_recovery.append(lp.getLiquidOutStream().getFlowRate("m3/hr"))
    hp_utils.append(hp.getMaxUtilization() * 100)
    mp_utils.append(mp.getMaxUtilization() * 100)

'''+other[end:]
other=other.replace('Stock Tank Oil Rate (m³/hr)','LP separator liquid rate (m³/hr)')
other=other.replace('label=f\'Optimal: {mp_pressures[opt_idx]:.0f} bara\'', 'label=f\'Highest sampled recovery: {mp_pressures[opt_idx]:.0f} bara\'')
other=other.replace('dpi=150','dpi=220')
t=t[:later.start(2)]+other+t[later.end(2):]
t=t[:first.start(2)]+code+t[first.end(2):]
t=t.replace('![Stock tank oil recovery vs. intermediate separator pressure](figures/separator_pressure_optimization.png)', '![LP separator liquid recovery at 2 bara vs. intermediate separator pressure](figures/mp_pressure_lp_liquid_recovery.png)')
t=t.replace('Stock tank oil recovery (left) and separator gas capacity utilization (right)', 'Liquid recovery at 3 bara LP pressure (left) and separator gas capacity utilization for vessels sized once at 30 bara MP pressure (right)')
t=t.replace('The optimal MP pressure balances oil recovery with equipment capacity.', 'The highest sampled recovery is a candidate only; reject pressures that violate fixed-vessel capacity or export quality constraints.')
p.write_text(t,encoding='utf-8')
