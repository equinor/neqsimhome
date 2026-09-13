"""Run literal chapter examples or the in-development model, with retained evidence."""
from pathlib import Path
import os, sys, runpy, json, re, hashlib, time
BOOK = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim")
sys.path.insert(0, str(BOOK / '.build/python_packages'))
sys.path.insert(0, str(SRC / 'devtools'))
os.environ['JAVA_TOOL_OPTIONS'] = '-Xmx512m'
os.environ['NEQSIM_PROJECT_ROOT'] = str(SRC)
os.environ['MPLBACKEND'] = 'Agg'
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=SRC, recompile=False, verbose=False)
out = BOOK / 'verification/scientific_revision'
out.mkdir(exist_ok=True)
chapter = BOOK / 'chapters/ch33_onshore_processing_plants/chapter.md'
os.chdir(chapter.parent)
start = time.monotonic()
if '--literal' in sys.argv:
    source = chapter.read_text(encoding='utf-8')
    blocks = [m[1] for m in re.finditer(r'^```python\s*\n(.*?)^```', source, re.M | re.S)]
else:
    source = (BOOK / 'devtools/ch33_verified_models.py').read_text(encoding='utf-8')
    blocks = [source]
ns = {}
executions = []
for i, block in enumerate(blocks, 1):
    print(f'RUNNING BLOCK {i}', flush=True)
    exec(compile(block, f'ch33_block_{i}', 'exec'), ns)
    executions.append(dict(block=i, sha256=hashlib.sha256(block.encode()).hexdigest(), passed=True))
report = dict(source_sha256=hashlib.sha256(source.encode()).hexdigest(),
    literal='--literal' in sys.argv, python=sys.executable, source_root=str(SRC),
    seconds=time.monotonic()-start, executions=executions,
    balances=ns.get('engineering_checks', []), plant_results=ns.get('plant_results', {}),
    sensitivity=ns.get('sweep', []),
    analytical_checks={key: ns.get(key) for key in ('surge_m3', 'solution_kg_s', 'T2s', 'theta', 'Rmin')},
    teg={key: ns.get(key) for key in ('hin_teg', 'raw_hout_teg', 'raw_temperature_K',
        'closed_temperature_K', 'wet_ppmv', 'dry_ppmv')})
(out / 'ch33_physical_execution.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
