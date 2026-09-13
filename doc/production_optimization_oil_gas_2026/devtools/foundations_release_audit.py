"""Match every published executable fence to literal-code execution evidence."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import datetime
import sys
BOOK=Path(__file__).resolve().parents[1]
pattern=re.compile(r'^```(python|java)\s*\n(.*?)^```',re.M|re.S)
reports=[]
for p in sorted((BOOK/'verification').glob('ch*_*.json'), key=lambda p:p.stat().st_mtime):
    try: data=json.loads(p.read_text(encoding='utf-8'))
    except (ValueError,OSError): continue
    if not isinstance(data,dict) or 'blocks' not in data: continue
    reports.append((p,data))
entries=[]
for chapter in sorted((BOOK/'chapters').glob('*/chapter.md'))[:18]:
    text=chapter.read_text(encoding='utf-8')
    for index,m in enumerate(pattern.finditer(text),1):
        code=m[2]
        matches=[]
        for report,data in reports:
            if data.get('chapter') != chapter.parent.name: continue
            for row in data['blocks']:
                if row.get('code')==code: matches.append((report,data,row))
        selected=matches[-1] if matches else None
        row={'chapter':chapter.parent.name,'index':index,'language':m[1],
             'line':text[:m.start()].count('\n')+1,'code_sha256':hashlib.sha256(code.encode()).hexdigest(),
             'chapter_sha256':hashlib.sha256(text.encode()).hexdigest(),
             'classification':'runnable_sequential_example',
             'status':selected[2]['status'] if selected else 'unverified_current_code'}
        if selected:
            report,data,evidence=selected
            row.update(report=str(report.relative_to(BOOK)),executed_index=evidence['index'],
                       report_chapter_sha256=data.get('source_sha256'),
                       exact_code_match=True)
            out=evidence.get('output','')
            row['physical_diagnostics']={'mentions_infeasible': bool(re.search('INFEASIBLE|Reject|Unconverged',out)),
                                         'unsolved_column': 'Solved: false' in out,
                                         'nan_output': bool(re.search(r'\bnan\b',out,re.I)),
                                         'hydraulics_unconverged': bool(re.search(r'hydraulics converged false|Opening.*converged false',out))}
        if m[1]=='java' and not re.search(r'\b(?:run|optimize|autoSize|calcDesign|generate|solve)\(',code):
            row['classification']='executed_configuration_or_introspection_fragment'
        entries.append(row)
summary={'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'source_repository':r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim',
         'source_revision':'6cc8026202a5d3f9383c9abd1d97d448993813f9',
         'scope':'Chapter 01–18 Python and Java fences, literal code matched against execution records',
         'counts':dict(Counter(r['status'] for r in entries)),
         'languages':dict(Counter(r['language'] for r in entries)),
         'classifications':dict(Counter(r['classification'] for r in entries)),
         'exclusions':[],
         'limitations':['API execution is distinct from physical validation, convergence and calibration.',
                        'Python snippets run in chapter order after the documented source/JVM bootstrap.',
                        'Java fragments run in JShell with a shared chapter state; not every fragment is a standalone class.',
                        'Java source uses Java 8 compatible syntax; JShell itself runs on the installed JDK25.'],
         'entries':entries}
path=BOOK/'verification/foundations_release_audit.json'
path.write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(summary['counts'],summary['languages'],summary['classifications'])
for row in entries:
    if row['status']!='pass' or any(row.get('physical_diagnostics',{}).values()):
        print(row['chapter'],row['index'],row['language'],row['status'],row.get('physical_diagnostics',{}))
if any(row['status']!='pass' for row in entries):
    sys.exit(1)
