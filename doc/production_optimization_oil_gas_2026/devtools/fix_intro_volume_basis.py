"""Replace an uncalibrated production proxy with a dimensional EOS result."""
import json
from pathlib import Path
BOOK=Path(__file__).resolve().parents[1]
path=next((BOOK/'chapters').glob('ch01*/notebooks/*.ipynb'))
nb=json.loads(path.read_text(encoding='utf-8'))
for cell in nb['cells']:
    if cell['cell_type']=='code' and 'flow_idx' in ''.join(cell['source']):
        cell['source']='''# Actual volumetric load for a specified mass flow; this is not well deliverability.
whp_pressures = [30, 50, 70, 90, 120]
mass_flow_kg_hr = 50000.0
actual_volume_m3_hr = []
for P in whp_pressures:
    fluid = create_natural_gas(273.15 + 40.0, float(P))
    ops = ThermodynamicOperations(fluid)
    ops.TPflash()
    fluid.initProperties()
    actual_volume_m3_hr.append(mass_flow_kg_hr / float(fluid.getDensity("kg/m3")))
assert actual_volume_m3_hr[-1] < actual_volume_m3_hr[0]
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar([str(p) for p in whp_pressures], actual_volume_m3_hr, color='#146B8B')
ax.set_xlabel('Pressure (bara)')
ax.set_ylabel('Actual volumetric flow (m³/hr)')
ax.set_title('Volumetric equipment load at 50 t/hr and 40 °C')
ax.grid(True, axis='y', alpha=0.3)
ax.set_ylim(0, max(actual_volume_m3_hr)*1.18)
for bar, value in zip(bars, actual_volume_m3_hr):
    ax.text(bar.get_x()+bar.get_width()/2, value+20, f'{value:.0f}', ha='center')
plt.tight_layout()
plt.savefig(FIGURES_DIR/'fig04_production_sensitivity.png', dpi=220, bbox_inches='tight')
plt.show()
print('Pressure (bara) | Actual volume (m3/hr) at 50 t/hr')
for P, value in zip(whp_pressures, actual_volume_m3_hr):
    print(f'{P:6.0f} | {value:10.2f}')
'''.splitlines(True)
path.write_text(json.dumps(nb,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
path=next((BOOK/'chapters').glob('ch03*/notebooks/*.ipynb'))
nb=json.loads(path.read_text(encoding='utf-8'))
for cell in nb['cells']:
    s=''.join(cell['source'])
    if 'liquid_vol_pct = []' in s:
        s=s.replace('if n_phases > 1 and fluid.hasPhaseType("oil"):', 'if fluid.hasPhaseType("oil"):')
    cell['source']=s.splitlines(True)
path.write_text(json.dumps(nb,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
