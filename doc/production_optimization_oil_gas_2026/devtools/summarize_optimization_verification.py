"""Hash-gated execution ledger for chapters 19–35; does not promote stale results."""
from pathlib import Path
from datetime import datetime,timezone
import ast,collections,hashlib,json,re,subprocess
B=Path(__file__).resolve().parents[1]
SOURCE=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
commit=subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip()
report={'source_root':str(SOURCE),'source_commit':commit,'generated_at':datetime.now(timezone.utc).isoformat(),
        'scope':'Manuscript Python and Java fences in chapters19–35, separate from notebook execution',
        'chapters':[],'limitations':[
 'Python examples execute sequentially in a fresh source-backed JVM per chapter; they are not standalone isolated unit tests.',
 'Java examples execute in a chapter-scoped JShell host; complete public examples with main methods are invoked. This is not a separate Java8 compilation of each fragment.',
 'Passed means executed without a Python exception or Java compile/runtime diagnostic in the declared context. It does not establish model calibration, design compliance, every branch, or field validation.',
 'Annotated integration patterns require the listed files, external data, optional packages, trained models or engineering adapters and are not reported as executed.',
 'Chapter29 manuscript transients include inventory, energy and time-step checks; the companion notebook separately illustrates a lumped controller model. Neither constitutes field calibration.',
 'Chapter32 includes an accepted optimizer point, fresh-model replay and an independently enumerated bracket. Synthetic calibration data remain an estimator exercise.',
 'Chapter33 checks each unit, stage and whole-plant material and energy boundary; it reconstructs an approximate TEG outlet energy state explicitly and rebuilds from saved inputs. This is not experimental validation of the synthetic plant.',
 'Simple compressor throughput screens use power constraints; generated automatic-size charts are not installed compressor evidence.'
]}
total=collections.Counter(); stale=[];bad=[]
for n in range(19,36):
 chapter=next((B/'chapters').glob(f'ch{n:02d}_*'));source=(chapter/'chapter.md').read_text(encoding='utf-8-sig')
 pyfile=B/'verification'/f'{chapter.name}_fences.json';jfile=B/'verification'/f'{chapter.name}_java.json'
 py=json.loads(pyfile.read_text(encoding='utf-8')) if pyfile.exists() else {}
 ja=json.loads(jfile.read_text(encoding='utf-8')) if jfile.exists() else {}
 pybyhash={r['sha256']:r for r in py.get('examples',[]) if r.get('language')=='python'}
 jbyhash={r['sha256']:r for r in ja.get('examples',[])}
 if n==33:
  pyfile=B/'verification/scientific_revision/ch33_physical_execution.json'
  physical=json.loads(pyfile.read_text(encoding='utf-8'))
  assert physical['literal']
  pybyhash={r['sha256']:{'sha256':r['sha256'],'status':'passed' if r['passed'] else 'failed'}
            for r in physical['executions']}
 rows=[];counts=collections.Counter()
 for index,m in enumerate(PAT.finditer(source),1):
  language,annotation,code=m.groups();digest=hashlib.sha256(code.encode()).hexdigest()
  row={'number':index,'language':language,'line':source.count('\n',0,m.start())+1,'sha256':digest}
  if language=='python':
   try: ast.parse(code)
   except SyntaxError as error:
    row.update(status='syntax_error',error=str(error));rows.append(row);counts[row['status']]+=1;bad.append([n,index,row['status']]);continue
  if 'pattern' in annotation:
   row.update(status='integration_pattern',prerequisites=annotation.strip())
  else:
   previous=(pybyhash if language=='python' else jbyhash).get(digest)
   if not previous:
    row['status']='stale_or_missing';stale.append([n,index,language])
   else:
    row['status']=previous.get('status','unknown')
    if language=='java' and row['status']=='attempted_in_chapter_context':
     logfile=B/'verification'/f'{chapter.name}_java.log'
     log=logfile.read_text(encoding='utf-8') if logfile.exists() else ''
     if ja.get('error_diagnostics')==0 and ja.get('status')=='executed_with_diagnostics' and 'Exception ' not in log:
      row['status']='passed'
    row['execution_report']=str((pyfile if language=='python' else jfile).relative_to(B))
    if 'error' in previous:row['error']=previous['error']
    if row['status'] not in ('passed','integration_pattern'):bad.append([n,index,row['status']])
  rows.append(row);counts[row['status']]+=1;total[f'{language}_{row["status"]}']+=1
 report['chapters'].append({'chapter':chapter.name,'counts':dict(counts),'examples':rows})
report['totals']=dict(total);report['stale_or_missing']=stale;report['unresolved']=bad
report['all_runnable_fences_passed']=not stale and not bad
out=B/'verification/optimization_chapters_audit_summary.json'
out.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
lines=['# Manuscript execution audit: chapters19–35','',f'Source commit: `{commit}`.',
       f'Generated: {report["generated_at"]}.','',
       '| Chapter | Executed successfully | Integration patterns | Unresolved or stale |',
       '|---|---:|---:|---:|']
for chapter in report['chapters']:
 c=chapter['counts'];unresolved=sum(v for k,v in c.items() if k not in ('passed','integration_pattern'))
 lines.append(f'| {chapter["chapter"]} | {c.get("passed",0)} | {c.get("integration_pattern",0)} | {unresolved} |')
lines+=['','## Scope and interpretation','']+[f'- {item}' for item in report['limitations']]
lines+=['','## Reproducibility','',
 'Use the user-selected bundled Python runtime and the book-local `.build/python_packages` directory. '
 'The runners load `neqsim_dev_setup` from the declared source checkout, never a packaged NeqSim fallback. '
 'Each ledger row records the exact current code SHA256 and the underlying execution report. '
 'Notebook outcomes and rendered-PDF inspection are reported separately by the book release workflow.','',
 'The Chapter33 sensitivity figure is generated from seven fresh accepted whole-plant calculations; recovery uses component molar flow and thermal/shaft duties remain separate.','',
 f'All runnable fences currently pass the execution/freshness gate: **{report["all_runnable_fences_passed"]}**.',
 f'Totals: `{json.dumps(dict(total),sort_keys=True)}`.']
if stale or bad:lines+=['',f'Stale/missing: `{stale}`.',f'Unresolved: `{bad}`.']
(B/'verification/optimization_chapters_audit_summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'totals':dict(total),'stale':stale,'unresolved':bad,'all_runnable_fences_passed':report['all_runnable_fences_passed']},indent=2))
