from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess

BOOK = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--project-root', type=Path, required=True)
parser.add_argument('--chapter', required=True)
parser.add_argument('--timeout', type=int, default=240)
parser.add_argument('--only-blocks', nargs='*', type=int)
args = parser.parse_args()
source_path = next((BOOK / 'chapters').glob(args.chapter + '*/chapter.md'))
source = source_path.read_text(encoding='utf-8')
work = BOOK / '.build' / 'java_examples' / source_path.parent.name
work.mkdir(parents=True, exist_ok=True)
classpath = os.pathsep.join([str(args.project_root / 'target/classes'),
                           str(args.project_root / 'src/main/resources'),
                           os.pathsep.join(p for p in (args.project_root / 'target/neqsim-dev-classpath.txt').read_text().strip().split(os.pathsep) if p.endswith('.jar'))])
blocks = []
commands = ['/set feedback normal', 'import java.util.*;', 'org.apache.logging.log4j.core.config.Configurator.setRootLevel(org.apache.logging.log4j.Level.INFO);']
for index, match in enumerate(re.finditer(r'^```(python|java)\s*\n(.*?)^```', source, re.M | re.S), 1):
    if match[1] != 'java':
        continue
    if args.only_blocks and index not in args.only_blocks:
        continue
    snippet = work / ('block_%03d.jsh' % index)
    snippet.write_text(match[2], encoding='utf-8')
    commands.extend(['"BOOK_BLOCK_%03d_BEGIN";' % index,
                     '/open ' + snippet.as_posix(), '"BOOK_BLOCK_%03d_END";' % index])
    blocks.append({'index': index, 'line': source[:match.start()].count('\n') + 1, 'code': match[2]})
commands.append('/exit')
driver = work / 'run.jsh'
driver.write_text('\n'.join(commands), encoding='utf-8')
suffix = '_blocks_' + '_'.join(map(str,args.only_blocks)) if args.only_blocks else ''
log_path = BOOK / 'verification' / (source_path.parent.name + '_java' + suffix + '.log')
with log_path.open('w', encoding='utf-8') as log:
    try:
        completed = subprocess.run(['jshell', '--class-path', classpath], input=driver.read_text(encoding='utf-8'),
                                   text=True, encoding='utf-8', stdout=log, stderr=subprocess.STDOUT, cwd=work, timeout=args.timeout)
        returncode = completed.returncode
    except subprocess.TimeoutExpired:
        returncode = 'timeout'
output = log_path.read_text(encoding='utf-8', errors='replace')
for row in blocks:
    start = output.find('"BOOK_BLOCK_%03d_BEGIN"' % row['index'])
    end = output.find('"BOOK_BLOCK_%03d_END"' % row['index'])
    captured = output[start:end] if start >= 0 and end >= 0 else ''
    row.update(status='pass' if captured and not re.search(r'(?m)(?:\|\s+)?(?:Error:|Exception |cannot find symbol|package .* does not exist)', captured) else 'fail', output=captured)
    if not captured:
        row['status'] = 'not_completed'
    print(args.chapter, row['index'], row['status'])
report = {'chapter': source_path.parent.name, 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
          'engine': 'JShell, Java snippets constrained to Java 8 syntax', 'returncode': returncode, 'blocks': blocks}
(BOOK / 'verification' / (source_path.parent.name + '_java' + suffix + '.json')).write_text(json.dumps(report, indent=2), encoding='utf-8')
