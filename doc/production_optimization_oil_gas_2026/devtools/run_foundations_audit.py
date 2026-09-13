from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import json
import subprocess
import sys

BOOK = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--project-root', required=True)
parser.add_argument('--chapters', nargs='*', default=['ch%02d' % i for i in range(1, 19)])
parser.add_argument('--timeout', type=int, default=300)
args = parser.parse_args()

def run(chapter):
    logfile = BOOK / 'verification' / (chapter + '_process.log')
    with logfile.open('w', encoding='utf-8') as log:
        try:
            result = subprocess.run([sys.executable, str(BOOK / 'devtools/verify_foundations_python.py'),
                                     '--project-root', args.project_root, '--chapter', chapter],
                                    stdout=log, stderr=subprocess.STDOUT, timeout=args.timeout)
            return chapter, result.returncode
        except subprocess.TimeoutExpired:
            return chapter, 'timeout'

with ThreadPoolExecutor(max_workers=2) as pool:
    futures = [pool.submit(run, chapter) for chapter in args.chapters]
    for future in as_completed(futures):
        print(*future.result(), flush=True)

for path in sorted((BOOK / 'verification').glob('ch*_python.json')):
    results = json.loads(path.read_text(encoding='utf-8'))
    print('\n', results['chapter'])
    for row in results['blocks']:
        if row['status'] != 'pass':
            print(row['index'], row['status'], row.get('traceback', '').splitlines()[-1:])
