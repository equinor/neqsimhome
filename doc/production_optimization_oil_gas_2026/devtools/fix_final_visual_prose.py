"""Apply the final visual review's prose-only corrections, preserving code."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil

BOOK = Path(__file__).resolve().parents[1]
QA = BOOK / 'verification/pdf_final'
backup = BOOK / '.build/rejected_visual_review_2cd8b9f'
backup.mkdir(parents=True, exist_ok=True)
for name in ('book.pdf', 'book.html'):
    src = BOOK / '.build/release_candidate/submission' / name
    if not (backup / name).exists():
        shutil.copy2(src, backup / name)
for path in QA.glob('*.json'):
    shutil.copy2(path, backup / path.name)
shutil.copy2(BOOK / 'verification/render_manifest.json', backup / 'render_manifest.json')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def code(text):
    return [sha(m.encode()) for m in re.findall(r'^```(?:python|java)([^\n]*\n.*?)^```', text, re.M | re.S)]

ch15 = BOOK / 'chapters/ch15_compressor_characteristics/chapter.md'
ch33 = BOOK / 'chapters/ch33_onshore_processing_plants/chapter.md'
replacements = {
    ch15: [
        ('Centrifugal compressor performance map showing polytropic head vs. actual inlet volume flow for multiple speed lines. The surge line (left boundary), stonewall line (right boundary), and constant efficiency contours define the operating envelope.\n\n', ''),
        ('Complete compressor operating envelope showing surge line, stonewall line, speed lines, constant efficiency contours, and the operating window. The anti-surge control line (ASCL) is set at a safety margin to the right of the surge line.\n\n', ''),
    ],
    ch33: [(r'''J=\sum_p\dot m_p p_p+\dot E_{\mathrm{gas}}p_{\mathrm{gas}}
-\dot W_{\mathrm{import}}c_{\mathrm{electricity}}
-\dot E_{\mathrm{fuel}}c_{\mathrm{fuel}}
-\sum_u\dot Q_u c_u-C_{\mathrm{other}}.''', r'''\begin{aligned}
J={}&\sum_p\dot m_p p_p+\dot E_{\mathrm{gas}}p_{\mathrm{gas}} \\
&-\dot W_{\mathrm{import}}c_{\mathrm{electricity}}
-\dot E_{\mathrm{fuel}}c_{\mathrm{fuel}} \\
&-\sum_u\dot Q_u c_u-C_{\mathrm{other}}.
\end{aligned}''')],
}
rows = []
for path, edits in replacements.items():
    before = path.read_text(encoding='utf-8')
    after = before
    for old, new in edits:
        assert after.count(old) == 1, (path, old)
        after = after.replace(old, new)
    assert code(before) == code(after)
    shutil.copy2(path, backup / (path.parent.name + '_chapter.md'))
    path.write_text(after, encoding='utf-8')
    rows.append({'path': str(path.relative_to(BOOK)), 'before_sha256': sha(before.encode()),
                 'after_sha256': sha(path.read_bytes()), 'edits': len(edits)})
report = {'status': 'passed', 'code_unchanged': True,
          'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'scope': 'Remove two stale Ch15 schematic descriptions; wrap the unchanged Ch33 contribution-margin equation over three aligned lines.',
          'changes': rows, 'rejected_candidate': str(backup)}
(QA / 'final_visual_prose_fix.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
