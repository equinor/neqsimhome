"""Run chapter examples in order, retaining globals only within a chapter.

No PyPI NeqSim package is loaded. The caller supplies the source repository.
Execution reports retain each source block, output, traceback and source hash.
"""
from pathlib import Path
import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import sys
import time
import traceback

BOOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / '.build' / 'python_packages'))
parser = argparse.ArgumentParser()
parser.add_argument('--project-root', type=Path, required=True)
parser.add_argument('--chapter', required=True)
parser.add_argument('--only-blocks', nargs='*', type=int)
args = parser.parse_args()
os.environ['NEQSIM_PROJECT_ROOT'] = str(args.project_root)
sys.path.insert(0, str(args.project_root / 'devtools'))
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=args.project_root, recompile=False, verbose=False)
import jpype
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
chapter = next((BOOK / 'chapters').glob(args.chapter + '*/chapter.md'))
work = BOOK / '.build' / 'fenced_examples' / chapter.parent.name
work.mkdir(parents=True, exist_ok=True)
(work / 'figures').mkdir(exist_ok=True)
os.chdir(work)
namespace = {'__name__': '__main__', 'jneqsim': jpype.JPackage('neqsim')}
source = chapter.read_text(encoding='utf-8')
results = {'chapter': chapter.parent.name, 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
           'project_root': str(args.project_root), 'python': sys.executable, 'blocks': []}
suffix = '_blocks_' + '_'.join(map(str,args.only_blocks)) if args.only_blocks else ''
report = BOOK / 'verification' / (chapter.parent.name + '_python' + suffix + '.json')
report.parent.mkdir(exist_ok=True)
pattern = re.compile(r'^```(python|java)\s*\n(.*?)^```', re.M | re.S)
for index, match in enumerate(pattern.finditer(source), 1):
    if match[1] != 'python':
        continue
    if args.only_blocks and index not in args.only_blocks:
        continue
    code = match[2]
    row = {'index': index, 'line': source[:match.start()].count('\n') + 1,
           'status': 'running', 'code': code}
    results['blocks'].append(row)
    report.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(chapter.parent.name, index, 'start', flush=True)
    before = source[:match.start()].rstrip().splitlines()[-1:]
    if before and '<!-- noexec -->' in before[0]:
        row.update(status='unsupported', reason='Explicit infrastructure or illustrative-only example')
    else:
        capture = io.StringIO()
        started = time.monotonic()
        try:
            with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
                exec(compile(code, str(chapter) + ':' + str(row['line']), 'exec'), namespace)
            row['status'] = 'pass'
        except Exception:
            row.update(status='fail', traceback=traceback.format_exc())
        row.update(seconds=round(time.monotonic() - started, 3), output=capture.getvalue())
        plt.close('all')
    report.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(chapter.parent.name, index, row['status'], flush=True)
print('DONE', chapter.parent.name, flush=True)
