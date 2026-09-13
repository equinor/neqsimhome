"""Narrow two residual legacy figure claims; keep all executable code exact."""
from pathlib import Path
import hashlib
import json
import re
import shutil

BOOK = Path(__file__).resolve().parents[1]
QA = BOOK / 'verification/pdf_final'
backup = BOOK / '.build/rejected_visual_review_2cd8b9f'
edits = [
    ('ch12_gas_processing',
     'Phase envelope for a typical rich gas showing the dew point line, bubble point line, cricondentherm (maximum temperature), and cricondenbar (maximum pressure). The pipeline operating envelope must remain to the right of the dew point curve at all pressures.',
     'Check the actual pressure-temperature path using phase stability and the required hydrocarbon-dew-point margin. The incomplete plotted trace alone cannot qualify that path.'),
    ('ch22_production_optimization_theory',
     'The contour plot reveals the objective function landscape. The optimum is typically a broad, flat region, meaning the solution is not highly sensitive to small changes in pressure — a desirable feature for practical operation.',
     'The contour curvature is prescribed by the illustrative objective. Operating sensitivity requires the actual process model.'),
]
rows = []
for chapter, old, new in edits:
    path = BOOK / 'chapters' / chapter / 'chapter.md'
    before = path.read_text(encoding='utf-8')
    assert before.count(old) == 1, chapter
    after = before.replace(old, new)
    pattern = r'^```(?:python|java)[^\n]*\n(.*?)^```'
    assert re.findall(pattern, before, re.M | re.S) == re.findall(pattern, after, re.M | re.S)
    shutil.copy2(path, backup / (chapter + '_chapter.md'))
    path.write_text(after, encoding='utf-8')
    rows.append({'chapter': chapter, 'old': old, 'new': new,
                 'before_sha256': hashlib.sha256(before.encode()).hexdigest(),
                 'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
report = {'status': 'passed', 'code_unchanged': True, 'changes': rows,
          'scope': 'Final adjacent-figure prose reconciliation: incomplete VLE locus and specified quadratic objective.'}
(QA / 'figure_scope_prose_fix.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('PASS: two figure-scope claims corrected; all code preserved.')
