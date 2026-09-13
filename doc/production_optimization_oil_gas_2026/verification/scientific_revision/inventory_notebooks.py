"""Inventory the original calculation cells for a physics-focused book audit."""
from pathlib import Path
import ast
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DUMP = ROOT / '.build/scientific_revision/notebook_sources'
BACKUP = ROOT / '.build/backups/scientific_revision_notebooks'
DUMP.mkdir(parents=True, exist_ok=True)
BACKUP.mkdir(parents=True, exist_ok=True)
records = []
for path in sorted(ROOT.glob('chapters/*/notebooks/*.ipynb')):
    name = path.parent.parent.name
    target = BACKUP / name / path.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(path, target)
    nb = json.loads(path.read_text(encoding='utf-8'))
    cells = []
    source_parts = []
    for idx, cell in enumerate(nb['cells']):
        if cell['cell_type'] != 'code':
            continue
        source = ''.join(cell['source'])
        tree = ast.parse(source)
        names = sorted({node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)})
        assertions = [ast.get_source_segment(source, node) for node in ast.walk(tree) if isinstance(node, ast.Assert)]
        source_parts.append(f'\n# CELL {idx}\n' + source)
        cells.append({'cell_index': idx, 'code_sha256': hashlib.sha256(source.encode()).hexdigest(),
                      'assigned_names': names, 'assertions': assertions, 'lines': len(source.splitlines())})
    dump = DUMP / (name + '.py')
    dump.write_text('\n'.join(source_parts), encoding='utf-8')
    previous = json.loads((ROOT / 'verification/notebooks' / (name + '.json')).read_text(encoding='utf-8'))
    records.append({'chapter': name, 'notebook': str(path.relative_to(ROOT)),
                    'original_notebook_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'source_dump': str(dump), 'cells': cells,
                    'prior_numeric_results': previous.get('numeric_results', {})})
    print(name, 'cells', len(cells), 'lines', sum(c['lines'] for c in cells),
          'assertions', sum(len(c['assertions']) for c in cells))
(OUT / 'notebook_inventory.json').write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding='utf-8')
