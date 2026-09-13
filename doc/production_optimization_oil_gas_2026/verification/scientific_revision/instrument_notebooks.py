"""Place explicit physical assertions at each central state/equipment solution."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKUP = ROOT / '.build/backups/scientific_revision_notebooks'
manifest = []
for path in sorted(ROOT.glob('chapters/*/notebooks/*.ipynb')):
    original = BACKUP / path.parent.parent.name / path.name
    notebook = json.loads(original.read_text(encoding='utf-8'))
    cells = [c for c in notebook['cells'] if 'book-generated-figure-discussion' not in c.get('metadata', {}).get('tags', [])]
    injected = []
    for index, cell in enumerate(cells):
        if cell['cell_type'] != 'code':
            continue
        source = ''.join(cell['source'])
        if 'NEQSIM_PROJECT_ROOT' in source and 'configure_figures()' in source:
            source += '\n# Physical verification uses the same model state, source and interpreter.\n'
            source += 'sys.path.insert(0, str(BOOK_ROOT / "verification" / "scientific_revision"))\n'
            source += 'from notebook_physics_checks import PhysicsChecks\n_physics = PhysicsChecks(NOTEBOOK_PATH)\n'
            cell['source'] = source.splitlines(keepends=True)
            continue
        tree = ast.parse(source)
        parent = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parent[child] = node
        additions = {}
        expanded_lines = {}
        original_lines = source.splitlines()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
                continue
            call = node.value
            if not isinstance(call.func, ast.Attribute) or call.func.attr not in ('initProperties', 'run'):
                continue
            ancestors = []
            previous = node
            while previous in parent:
                previous = parent[previous]
                ancestors.append(previous)
            candidate = any(isinstance(p, (ast.Try, ast.FunctionDef, ast.AsyncFunctionDef)) for p in ancestors)
            receiver = ast.get_source_segment(source, call.func.value)
            if not receiver or '\n' in receiver:
                continue
            method = 'state' if call.func.attr == 'initProperties' else 'run'
            label = f'calculation_cell_{index}:{receiver}'
            original_line = original_lines[node.lineno - 1]
            indent = len(original_line) - len(original_line.lstrip())
            inline_parent = next((p for p in ancestors if isinstance(p, (ast.For, ast.If, ast.With, ast.FunctionDef))
                                  and p.lineno == node.lineno and p.body[0].lineno == node.lineno), None)
            if inline_parent is not None:
                body_start = inline_parent.body[0].col_offset
                expanded_lines[node.lineno] = original_line[:body_start].rstrip() + '\n' + ' ' * (indent + 4) + original_line[body_start:]
                indent += 4
            statement = f'{" " * indent}assert _physics.{method}({receiver}, {label!r}, candidate={candidate})'
            additions.setdefault(node.end_lineno, []).append(statement)
            injected.append({'original_cell': index, 'receiver': receiver, 'method': method,
                             'candidate_domain': candidate, 'source_line': node.lineno})
        lines = source.splitlines()
        for line_number, expanded in expanded_lines.items():
            lines[line_number - 1] = expanded
        for line_number in sorted(additions, reverse=True):
            lines[line_number:line_number] = additions[line_number]
        updated = '\n'.join(lines) + '\n'
        ast.parse(updated)
        cell['source'] = updated.splitlines(keepends=True)
    cells.extend([
        {'cell_type': 'markdown', 'metadata': {'tags': ['book-physics-validation']},
         'source': ['## Physical verification and its limits\n',
                    'The assertions above test the calculated states and steady-state conservation laws. ',
                    'Rejected operating candidates remain excluded; they do not become synthetic outputs. ',
                    'The chapter-specific checks below state the applicable limits. ',
                    'Independent reference-fluid and analytic benchmarks are recorded separately in ',
                    '`verification/scientific_revision/benchmark_results.json`. ',
                    'Passing these checks does not establish field calibration or an installed equipment rating.\n']},
        {'cell_type': 'code', 'execution_count': None, 'outputs': [], 'metadata': {'tags': ['book-physics-validation']},
         'source': ['from chapter_specific_checks import validate_chapter\n',
                    'assert validate_chapter(_physics, globals())\n', 'assert _physics.finish()\n']}
    ])
    notebook['cells'] = cells
    path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    manifest.append({'chapter': path.parent.parent.name, 'notebook': str(path.relative_to(ROOT)),
                     'assertions_injected': len(injected), 'injections': injected})
    print(path.parent.parent.name, len(injected), 'central assertions')
(Path(__file__).parent / 'assertion_injection_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
