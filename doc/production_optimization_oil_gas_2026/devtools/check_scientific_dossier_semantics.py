"""Check that heuristic figure markers cannot falsely approve scientific content."""
from pathlib import Path
import json
import sys

BOOK = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(BOOK / '.build/python_packages'), str(BOOK.parents[1] / 'tools')]
from book_improvement_tools import DISCUSSION_RE

samples = {'**Observation.** The rate increases.': True,
           '*Mechanism.* The pressure ratio increases.': True,
           '**Discussion (Figure 2.1).** An interpretation.': True,
           'Discussion (Figure 2.1)': True,
           'The discussion is incomplete.': False,
           'Observation without an explicit marker': False}
for value, expected in samples.items():
    assert bool(DISCUSSION_RE.search(value)) == expected, value
dossier = json.loads((BOOK / 'figure_dossier.json').read_text(encoding='utf-8'))
assert dossier['figures']
for row in dossier['figures']:
    assert row['review_status'] == ('exempt' if row['exempt'] else 'needs-human-check')
    assert row['discussion_detection'] == ('explicit-marker' if row['discussion_present'] else 'no-explicit-marker')
report = {'status': 'passed', 'marker_cases': len(samples), 'figure_records': len(dossier['figures']),
          'conclusion': 'Explicit discussion detection is tested separately from scientific approval; no automatic approval is inferred.'}
(BOOK / 'verification/scientific_revision/dossier_semantics_check.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
