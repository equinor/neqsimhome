"""Compile and execute the published Java fixture plus each operation fragment."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
BOOK = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get('NEQSIM_PROJECT_ROOT', r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim'))
chapter = BOOK / 'chapters/ch21_debottlenecking/chapter.md'
text = chapter.read_text(encoding='utf-8')
blocks = list(re.finditer(r'^```java\n(.*?)^```', text, re.M | re.S))
fixture = blocks[0][1]
imports, body = fixture.split('public class CapacityExample {', 1)
main_start = body.index('    public static void main(')
prefix = body[:main_start]
methods = []
for n, match in enumerate(blocks[1:], 1):
    methods.append('    private static void example%02d() throws Exception {\n%s\n    }\n' % (n, match[1]))
main = '''    public static void main(String[] args) throws Exception {
        List<String> outcomes = new ArrayList<String>();
        for (int n = 1; n <= COUNT; n++) {
            try {
                setup();
                CapacityExample.class.getDeclaredMethod(String.format("example%02d", n)).invoke(null);
                logger.error("BOOK_JAVA_PASS_{}", n);
                outcomes.add("BOOK_JAVA_PASS_" + n);
            } catch (Throwable error) {
                logger.error("BOOK_JAVA_FAIL_{} {}", n, error.toString(), error);
                outcomes.add("BOOK_JAVA_FAIL_" + n + " " + error.toString() + " cause=" + error.getCause());
            }
        }
        java.nio.file.Files.write(java.nio.file.Paths.get("outcomes.txt"), outcomes, java.nio.charset.StandardCharsets.UTF_8);
    }
'''.replace('COUNT', str(len(methods)))
script = imports + 'public class CapacityExample {\n' + prefix + '\n'.join(methods) + main + '}\nCapacityExample.main(new String[0]);\n/exit\n'
work = BOOK / '.build/ch21_java'
work.mkdir(parents=True, exist_ok=True)
outcome_path = work / 'outcomes.txt'
if outcome_path.exists():
    outcome_path.unlink()
(work / 'examples.jsh').write_text(script, encoding='utf-8')
dependencies = [p for p in (SOURCE / 'target/neqsim-dev-classpath.txt').read_text().strip().split(os.pathsep) if p.lower().endswith('.jar')]
cp = os.pathsep.join([str(SOURCE / 'target/classes'), str(SOURCE / 'src/main/resources')] + dependencies)
result = subprocess.run(['jshell', '-J--add-modules=ALL-SYSTEM', '-J-Xmx512m', '--execution', 'local', '--class-path', cp, str(work / 'examples.jsh')], cwd=work,
    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
log = result.stdout + '\n' + result.stderr
if outcome_path.exists():
    log += '\n' + outcome_path.read_text(encoding='utf-8')
(BOOK / 'verification/ch21_debottlenecking_java.log').write_text(log, encoding='utf-8')
rows = []
for n, match in enumerate(blocks):
    passed = (n == 0 and 'BOOK_JAVA_PASS_' in log) or (n > 0 and re.search(r'BOOK_JAVA_PASS_' + str(n) + r'\b', log) is not None)
    rows.append({'number': n + 1, 'operation': n, 'line': text.count('\n', 0, match.start()) + 1,
                 'sha256': hashlib.sha256(match[1].encode()).hexdigest(), 'language': 'java',
                 'status': 'passed' if passed else 'failed'})
report = {'chapter': chapter.parent.name, 'status': 'passed' if all(r['status'] == 'passed' for r in rows) else 'failed',
          'harness': 'Complete Java class, current source classpath, JShell host; Java 8 source constructs',
          'source_root': str(SOURCE), 'executed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'examples': rows, 'api_summaries': 4, 'error_diagnostics': len(re.findall(r'^Error:', log, re.M))}
(BOOK / 'verification/ch21_debottlenecking_java.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(report['status'], len(rows), 'Java fences;', report['error_diagnostics'], 'compile diagnostics')
if report['status'] != 'passed':
    print(log[-14000:])
    raise SystemExit(1)
