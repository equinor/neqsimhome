"""Separate metrics with different physical units into their own panels."""
import json
from pathlib import Path
BOOK=Path(__file__).resolve().parents[1]
p=next((BOOK/'chapters').glob('ch32*/notebooks/*.ipynb'))
nb=json.loads(p.read_text(encoding='utf-8'))
for c in nb['cells']:
    if c['cell_type']=='code' and 'summer_vals = ' in ''.join(c['source']):
        c['source']='''metrics = list(list(results.values())[0].keys())
scenario_names = list(results.keys())
summer_vals = [results[scenario_names[0]][m] for m in metrics]
winter_vals = [results[scenario_names[1]][m] for m in metrics]
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
for axis, metric, summer, winter in zip(axes.flat, metrics, summer_vals, winter_vals):
    name, unit = metric.rsplit(' [', 1)
    unit = unit.rstrip(']').replace('C', '°C')
    bars = axis.bar(['Summer', 'Winter'], [summer, winter], color=['#D86562', '#367AA3'])
    axis.set_title(name)
    axis.set_ylabel(unit)
    axis.set_ylim(0, max(summer, winter)*1.23)
    axis.grid(True, axis='y', alpha=0.25)
    for bar, value in zip(bars, [summer, winter]):
        axis.text(bar.get_x()+bar.get_width()/2, value+max(summer,winter)*0.02,
                  f'{value:.2f}', ha='center')
    axis.text(0.5, 0.92, f'Winter minus summer: {winter-summer:+.2f} {unit}',
              transform=axis.transAxes, ha='center', fontsize=10)
fig.suptitle('Seasonal operation: separate process and utility quantities', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig(FIGURES_DIR/'ch22_scenario_comparison.png', dpi=220, bbox_inches='tight')
plt.show()
print('Metric | Summer | Winter | Difference (same unit)')
for metric, summer, winter in zip(metrics, summer_vals, winter_vals):
    print(f'{metric} | {summer:.4f} | {winter:.4f} | {winter-summer:+.4f}')
'''.splitlines(True)
p.write_text(json.dumps(nb,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
