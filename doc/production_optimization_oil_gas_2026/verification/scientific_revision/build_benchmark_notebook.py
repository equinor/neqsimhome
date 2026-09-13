"""Create and execute a self-contained review notebook with the selected runtime."""
from pathlib import Path
import base64
import contextlib
import hashlib
import io
import json
import sys
ROOT=Path(__file__).resolve().parent
NOTEBOOK=ROOT/'36_benchmark_validation.ipynb'
cells=[]
def md(text):cells.append({'cell_type':'markdown','metadata':{},'source':text.splitlines(keepends=True)})
def code(text):cells.append({'cell_type':'code','metadata':{},'source':text.splitlines(keepends=True),'execution_count':None,'outputs':[]})
md('# Independent references and physical limits\n\nThis notebook distinguishes predictive property comparisons against an independent reference EOS from conservation-law and search-algorithm verification. Expected NIST states are archived separately from NeqSim outputs. The declared tolerances in `benchmark_design.json` predate the first actual comparisons. No case-specific field calibration is claimed.\n')
code('''import os, sys, subprocess, json
from pathlib import Path
ROOT = Path(globals().get('__file__', '36_benchmark_validation.ipynb')).resolve().parent
assert os.environ.get('NEQSIM_PROJECT_ROOT'), 'Select the compiled NeqSim source explicitly'
completed = subprocess.run([sys.executable, str(ROOT/'run_independent_benchmarks.py')],
                           capture_output=True, text=True, env=os.environ.copy())
print(completed.stdout)
if completed.stderr: print(completed.stderr)
completed.check_returncode()
results = json.loads((ROOT/'benchmark_results.json').read_text(encoding='utf-8'))
assert results['status'] == 'passed' and not results['failures']
print('Source revision:', results['source_revision'])
print('Interpreter:', results['python'])
print('Passed comparisons:', len(results['comparisons']))
''')
md('The property comparison covers nine methane states at 300, 350 and 400 K and 1, 50 and 100 bara with both SRK and PR. These NIST WebBook values are reference-equation calculations, not raw experimental observations. Their use checks selected cubic-EOS predictions against an independent thermodynamic model.\n')
code('''print('EOS | T (K) | P (bara) | NIST density (kg/m3) | NeqSim density (kg/m3) | deviation (%)')
for row in results['comparisons']:
    if row['name'] in ('SRK methane density', 'PR methane density'):
        state = row['case']
        deviation = 100*(row['actual']/row['expected']-1)
        print(f"{row['name'][:3]} | {state['T_K']:.0f} | {state['P_bara']:.0f} | {row['expected']:.8g} | {row['actual']:.8g} | {deviation:+.5f}")
FIGURE = ROOT/'figures/nist_methane_density_validation.png'
assert FIGURE.exists()
''')
md('The parity and deviation plot tests the stated ±3% teaching accuracy budget. Higher-pressure deviations reflect the approximate attraction and excluded-volume descriptions in cubic EOS. Passing this grid supports these methane states only; mixture phase envelopes, water association and near-critical derivatives require their own reference data. Use measured composition and applicable laboratory data before extending the model to a field fluid.\n')
code('''from collections import defaultdict
groups = defaultdict(list)
for row in results['comparisons']: groups[row['evidence_type']].append(row)
print('Evidence class | comparisons | passed')
for name, rows in groups.items(): print(name, '|', len(rows), '|', sum(r['passed'] for r in rows))
for row in results['comparisons']:
    if 'optimizer' in row['name'] or 'hydrostatic' in row['name'] or 'argon' in row['name']:
        print(row['name'], ':', row['actual'], row['unit'], '; expected', row['expected'],
              '; absolute acceptance bound', row['acceptance_bound_absolute'])
''')
md('The ideal-gas and monatomic-argon compressor cases use analytical limits independent of NeqSim. Hydrostatics tests the momentum equation using a specified input density, so it does not independently validate liquid density. Flash fugacity equality, stream material balance and the first law verify internal consistency. The optimizer is checked by direct enumeration in a fresh process; its thermodynamics still use the same EOS.\n\nPrimary sources and retrieved originals are indexed in [the reference archive](references/SOURCES.md). No external hydrate, inhibited-solvent, vendor-map, field-flow, transient-control or economic dataset is included; those predictions remain outside this benchmark’s accuracy claim.\n')
namespace={'__name__':'__main__','__file__':str(NOTEBOOK)}
for number,cell in enumerate([c for c in cells if c['cell_type']=='code'],1):
    output=io.StringIO()
    with contextlib.redirect_stdout(output):exec(compile(''.join(cell['source']),str(NOTEBOOK)+f':cell{number}','exec'),namespace)
    cell['execution_count']=number
    cell['outputs']=[{'output_type':'stream','name':'stdout','text':output.getvalue().splitlines(keepends=True)}]
    if 'FIGURE =' in ''.join(cell['source']):
        data=(ROOT/'figures/nist_methane_density_validation.png').read_bytes()
        cell['outputs'].append({'output_type':'display_data','metadata':{},'data':{'image/png':base64.b64encode(data).decode(),'text/plain':['Executed NIST methane parity and deviation plot']}})
notebook={'cells':cells,'metadata':{'kernelspec':{'display_name':'Selected Codex Python (explicit source JVM)','language':'python','name':'python3'},
                                  'language_info':{'name':'python','version':sys.version.split()[0]}},'nbformat':4,'nbformat_minor':5}
NOTEBOOK.write_text(json.dumps(notebook,indent=1,ensure_ascii=False),encoding='utf-8')
print('Executed',NOTEBOOK)
