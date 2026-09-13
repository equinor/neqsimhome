"""Reconcile final-separator reporting prose with unchanged accepted calculations.

This is a one-time editorial patch. It does not change a calculation or a notebook.
The Chapter 11 source artifact was inspected at full size before copying.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil

BOOK = Path(__file__).resolve().parents[1]
OUT = BOOK / 'verification/scientific_revision'
BACKUP = BOOK / '.build/final_foundations_liquid_basis_originals'
BACKUP.mkdir(parents=True, exist_ok=True)
sha = lambda value: hashlib.sha256(value).hexdigest()
file_sha = lambda path: sha(path.read_bytes())
fences = lambda text: re.findall(r'^```(python|java)\s*\n(.*?)^```', text, re.M | re.S)
images = lambda text: re.findall(r'!\[(Figure\s+\d+\.\d+).*?\]\(([^)]+)\)', text)

chapter11 = BOOK / 'chapters/ch11_oil_processing/chapter.md'
literal = json.loads((BOOK / 'verification/ch11_oil_processing_python.json').read_text(encoding='utf-8'))
physics_path = OUT / 'ch11_manuscript_physics.json'
physics = json.loads(physics_path.read_text(encoding='utf-8'))
code = fences(chapter11.read_text(encoding='utf-8'))[1][1]
literal2 = next(b for b in literal['blocks'] if b['index'] == 2)
physical2 = next(b for b in physics['literal_blocks'] if b['index'] == 2)
assert literal2['status'] == 'pass' and literal2['code'] == code
assert physical2['execution'] == 'pass' and physical2['code_sha256'] == sha(code.encode())
points = [list(map(float, point)) for point in re.findall(
    r'MP =\s*([\d.]+) bara -> Oil rate = ([\d.]+) kg/hr', physical2['output'])]
assert len(points) == 12 and max(points, key=lambda pair: pair[1]) == [7.0, 7893.3]
checks = [c for c in physics['physical_checks'] if c['block'] == 2]
assert len(checks) == 60 and all(c['pass'] for c in checks)
assert all(c['pass'] for group in checks for c in group['checks'])

accepted = BOOK / '.build/scientific_revision_cases/ch11_oil_processing/figures/mp_pressure_optimization.png'
replayed = BOOK / '.build/fenced_examples/ch11_oil_processing/figures/mp_pressure_optimization.png'
placed = chapter11.parent / 'figures/mp_pressure_optimization.png'
assert file_sha(accepted) == file_sha(replayed)
image_before = file_sha(placed)
shutil.copy2(placed, BACKUP / 'mp_pressure_optimization.png')
shutil.copy2(accepted, placed)
assert file_sha(placed) == file_sha(accepted)

replacements = {
    'ch11_oil_processing': [
        ('The following example demonstrates a systematic optimization of separator pressures in a 3-stage separation train. The objective is to maximize stock-tank oil flow rate by varying the MP separator pressure:',
         'The following example sweeps 12 MP separator pressures for a three-stage train supplied with 10,000 kg/h at 70 bara and 80°C. The reported objective is the hydrocarbon liquid mass rate leaving the final separator at 1.5 bara and its calculated flash temperature. No subsequent flash to stock-tank reference conditions is performed:'),
        ('![Figure 11.2: Optimization curve showing stock-tank oil rate vs. MP separator pressure](figures/mp_pressure_optimization.png)',
         '![Figure 11.2: Final 1.5 bara separator liquid mass rate versus MP separator pressure for the 10,000 kg/h feed](figures/mp_pressure_optimization.png)'),
        ('Stock-tank oil recovery as a function of intermediate (MP) separator pressure for a 3-stage separation train. The optimum is typically found at 8–12 bara for this fluid composition.',
         'The largest of the 12 sampled liquid rates is 7,893.3 kg/h at 7 bara MP pressure; the 10 bara case gives 7,887.3 kg/h. These points identify a broad sampled maximum, not a continuous optimum or a general 8–12 bara rule. Intermediate pressure changes gas withdrawal, residual liquid composition and throttling cooling. To optimize stock-tank oil recovery, add a flash of each final liquid product at explicitly defined reference pressure and temperature, then compare the remaining liquid at that common basis. Export-quality and recompression constraints would also be needed for an operating recommendation.'),
    ],
    'ch10_separation_technology': [
        ('The largest sampled stock-tank oil rate is 32.023 t/hr at a second-stage pressure of 8.0 bara, with the first and final stages fixed at 70 and 1.5 bara.',
         'The largest sampled final-separator oil rate is 32.023 t/hr at a second-stage pressure of 8.0 bara, with the first and final stages fixed at 70 and 1.5 bara. The feed is 50 t/hr at 60°C; the final oil leaves at its calculated flash temperature, without a subsequent reference-condition flash.'),
        ('Changing intermediate pressure redistributes light components between vented gas and the liquid passed to later separation stages. The best pressure for liquid recovery may differ from the best pressure for export quality, recompression duty or total value. Optimize against the complete separation train and a consistent stock-tank reference, with vapor-pressure and compression constraints included.',
         'Changing intermediate pressure redistributes light components between separated gas and the liquid passed to later stages. The best pressure for final-separator liquid recovery may differ from the best pressure for export quality, recompression duty or total value. A stock-tank objective requires an additional product flash at explicitly specified reference pressure and temperature. Apply that same basis to every case and include vapor-pressure and compression constraints before selecting an operating pressure.'),
    ],
}
chapter_records = []
fixes = []
for dirname, pairs in replacements.items():
    path = BOOK / 'chapters' / dirname / 'chapter.md'
    # Read immediately before writing; another author owns unrelated Chapter 10 captions.
    original = path.read_text(encoding='utf-8')
    shutil.copy2(path, BACKUP / (dirname + '.md'))
    updated = original
    for old, new in pairs:
        assert updated.count(old) == 1, (dirname, old)
        updated = updated.replace(old, new, 1)
        fixes.append({'chapter': dirname, 'before': old, 'after': new})
    assert fences(original) == fences(updated)
    assert images(original) == images(updated)
    path.write_text(updated, encoding='utf-8')
    chapter_records.append({'chapter': dirname, 'source_sha256': file_sha(path),
                            'before_sha256': sha(original.encode()),
                            'code_unchanged': True, 'figure_order_and_numbers_unchanged': True})

report = {
    'status': 'passed',
    'reviewed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'Final liquid reporting basis and Chapter 11 literal pressure-sweep plot provenance. Prior scientific and editorial ledgers are preserved.',
    'chapters': chapter_records,
    'fixes': fixes,
    'images': [{
        'path': str(placed.relative_to(BOOK)),
        'sha256': file_sha(placed),
        'source': str(accepted.relative_to(BOOK)),
        'source_sha256': file_sha(accepted),
        'before_sha256': image_before,
        'action': 'replaced stale stock-tank axis label with the unchanged accepted literal-output artifact',
        'literal_fence_index': 2,
        'code_sha256': sha(code.encode()),
        'execution_evidence': str((BOOK / 'verification/ch11_oil_processing_python.json').relative_to(BOOK)),
        'physics_evidence': str(physics_path.relative_to(BOOK)),
        'physics_evidence_sha256': file_sha(physics_path),
        'independent_literal_replay_image_sha256': file_sha(replayed),
        'full_view': True,
        'visual_observations': [
            'All 12 points are visible; pressure axis is bara and final 1.5 bara liquid rate axis is kg/hr.',
            'Maximum is the 7 bara point, with the adjacent 10 bara point slightly lower.',
            'Line shape matches the accepted tabulated output; no clipped labels, overlap or unreadable legend.',
            'The replacement changes the incorrect stock-tank label while retaining the accepted computed curve.'
        ],
        'points_from_accepted_stdout_rounded': points,
        'point_units': ['bara', 'kg/hr'],
        'physical_evaluations': len(checks),
        'individual_checks': sum(len(c['checks']) for c in checks),
        'physical_scope': 'Five units in each of twelve cases: mass, component and energy closure; finite positive pressure/temperature and nonnegative flow; passive-valve pressure direction. Numerical solution verification, not empirical model validation.',
    }],
    'notebook_changes_by_this_pass': False,
    'handoff': 'Root authorized the notebook specialist to correct and rerun only the Chapter 10 notebook axis label and result discussion, then root reintegrates that result section. That specialist owns its image provenance ledger.',
    'source_frozen': True,
    'unresolved': [],
}
(OUT / 'final_foundations_liquid_basis_review.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print('passed: 5 prose/caption fixes; 1 accepted plot copied; 12 points and 60 physical unit evaluations traced; all code unchanged')
