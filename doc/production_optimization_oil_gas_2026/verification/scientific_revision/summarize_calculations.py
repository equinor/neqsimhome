import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
records = json.loads((ROOT / 'notebook_inventory.json').read_text(encoding='utf-8'))
for record in records:
    print('\n' + record['chapter'])
    print('NUMERIC:', ', '.join(record['prior_numeric_results']))
    source = Path(record['source_dump']).read_text(encoding='utf-8')
    tree = ast.parse(source)
    important = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            important.append(ast.get_source_segment(source, node).splitlines()[0])
        elif isinstance(node, ast.Assign):
            text = ast.get_source_segment(source, node)
            if any(term in text for term in ('npv', 'np.exp', 'np.power', '**', ' / ', 'capacity', 'optimal', 'efficien', 'power_constraint')):
                if len(text) < 200 and not any(term in text for term in ('jneqsim', 'FIGURES_DIR', 'plt.', 'ax.', 'ax1.', 'ax2.')):
                    important.append(text)
    print('\n'.join(important))
