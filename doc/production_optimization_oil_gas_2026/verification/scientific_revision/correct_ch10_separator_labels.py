"""One-time, authorized label correction; retain the prior executed evidence."""
from pathlib import Path
import hashlib
import json
import shutil

OUT = Path(__file__).resolve().parent
BOOK = OUT.parents[1]
BACKUP = BOOK / '.build/backups/ch10_final_separator_label_correction'
BACKUP.mkdir(parents=True, exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
nb_path = next((BOOK/'chapters/ch10_separation_technology/notebooks').glob('*.ipynb'))
paths = [nb_path, BOOK/'verification/notebooks/ch10_separation_technology.json',
         OUT/'notebooks/ch10_separation_technology.json',
         BOOK/'verification/notebook_execution_report.json', BOOK/'verification/notebook_figure_updates.json',
         BOOK/'verification/figure_sections/ch10.md', BOOK/'verification/figure_interpretations_foundations.json',
         OUT/'notebook_physics_review.json', OUT/'notebook_physics_review.md',
         OUT/'figure_visual_review.json', OUT/'figure_visual_review.md']
paths.extend((BOOK/'chapters/ch10_separation_technology/figures').glob('fig03_separator_optimization.*'))
for p in paths:
    dest = BACKUP/p.relative_to(BOOK)
    assert not dest.exists(), 'This migration already ran: '+str(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p,dest)
all_notebooks = list((BOOK/'chapters').glob('*/notebooks/*.ipynb'))
(BACKUP/'before_hashes.json').write_text(json.dumps({str(p.relative_to(BOOK)):sha(p) for p in all_notebooks}, indent=2),encoding='utf-8')
nb=json.loads(nb_path.read_text(encoding='utf-8'))
for c in nb['cells']:
    s=''.join(c['source'])
    s=s.replace('3rd stage / stock tank pressure (fixed)','final separator pressure (fixed)')
    s=s.replace('# Stage 3 (stock tank)','# Stage 3 (final separator)')
    s=s.replace('Stock-Tank Oil Rate (tonnes/hr)','Final-separator oil rate (tonnes/hr)')
    s=s.replace("f'Optimum: {opt_p:.0f} bara'", "f'Highest sampled rate: {opt_p:.0f} bara'")
    if s.startswith('## 10.4 Figure 3:'):
        s=('## 10.4 Figure 3: Three-Stage Separation Optimization\n\n'
           'This sweep calculates oil leaving the final separator. The first and final stages are fixed at '
           '70 and 1.5 bara, while the second-stage pressure varies. Feed rate is 50 t/hr at 60 °C; '
           'the final oil remains at its calculated flash temperature. No reference-condition stock-tank flash is applied.\n')
    if s.startswith('**Discussion:** The optimal 2nd-stage pressure'):
        s=('**Discussion:** The highest sampled final-separator oil rate occurs at 8 bara second-stage pressure. '
           'Intermediate pressure changes the separated gas and the composition passed to the final flash. '
           'This is a sampled liquid-rate objective for the declared separation path. A stock-tank objective '
           'requires a subsequent flash at declared reference pressure and temperature, together with '
           'vapor-pressure, recompression and equipment-capacity constraints.\n')
    c['source']=s.splitlines(True)
nb_path.write_text(json.dumps(nb,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
fp=BOOK/'verification/figure_interpretations_foundations.json'
data=json.loads(fp.read_text(encoding='utf-8'))
entry=data['ch10_separation_technology/fig03_separator_optimization.png']
entry['mechanism']='Changing intermediate pressure redistributes light components between separated gas and the liquid passed to later separation stages.'
entry['recommendation']='For a stock-tank objective, add a final flash at declared reference pressure and temperature; include vapor-pressure, recompression and equipment-capacity constraints before selecting an operating pressure.'
fp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Retained prior notebook and evidence; corrected labels and explanatory text only.')
