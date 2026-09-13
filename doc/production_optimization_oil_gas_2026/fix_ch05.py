"""Fix ch05 format string error."""
import json

path = r'c:\Users\ESOL\Documents\GitHub\neqsim2\neqsim-paperlab\books\production_optimization_oil_gas_2026\chapters\ch05_well_performance\notebooks\ch05_well_performance_figures.ipynb'
nb = json.load(open(path, encoding='utf-8'))

cell = nb['cells'][6]
src = ''.join(cell['source'])

old = "f'{color}-o', linewidth=2, markersize=5,"
new = "'-o', color=color, linewidth=2, markersize=5,"

if old in src:
    src = src.replace(old, new)
    cell['source'] = [src]
    cell['outputs'] = []
    cell['execution_count'] = None
    json.dump(nb, open(path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('Fixed ch05 format string')
else:
    print('Pattern not found, searching...')
    for i, line in enumerate(src.split('\n')):
        if 'color' in line and ('-o' in line or 'plot' in line):
            print(f'  Line {i}: {line.strip()}')
