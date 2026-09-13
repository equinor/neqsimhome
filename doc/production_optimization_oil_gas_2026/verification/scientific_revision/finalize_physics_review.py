"""Verify execution integrity and build the explicit all-chapter coverage ledger."""
import ast
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
BOOK=ROOT.parents[1]
sys.path.insert(0,str(BOOK/'.build/python_packages'))
import numpy as np
from chapter_specific_checks import SCOPES
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
helper_names=['notebook_physics_checks.py','chapter_specific_checks.py','teg_energy_reconstruction.py']
helper_hashes={name:sha(ROOT/name) for name in helper_names}
inventory=json.loads((ROOT/'notebook_inventory.json').read_text(encoding='utf-8'))
ledger=[];execution=[];changes=[]
for original in inventory:
    chapter=original['chapter'];number=int(chapter[2:4])
    path=BOOK/original['notebook'];report_path=BOOK/'verification/notebooks'/(chapter+'.json')
    report=json.loads(report_path.read_text(encoding='utf-8'))
    evidence_path=ROOT/'notebooks'/(chapter+'.json')
    evidence=json.loads(evidence_path.read_text(encoding='utf-8'))
    assert report['status']=='passed' and evidence['status']=='passed',chapter
    assert report['executed_cells']==report['code_cells'],chapter
    assert sha(path)==report['notebook_sha256'],'Unreported edit: '+chapter
    notebook=json.loads(path.read_text(encoding='utf-8'))
    for run in report['cell_runs']:
        cell=notebook['cells'][run['cell_index']]
        assert hashlib.sha256(''.join(cell['source']).encode()).hexdigest()==run['sha256'],chapter
    # Markdown-only handoff does not rerun or change the calculations. Preserve
    # execution provenance and explicitly refresh only the artifact hash.
    scope,limitations=SCOPES[number]
    text=('## Physical verification and scope\n\n'+scope+'. '+limitations+'\n\n'
          'The final code cell checks the computed cases against explicit physical, analytical or constraint criteria. '
          'A passed conservation check establishes internal consistency; it does not establish field accuracy. '
          'Independent reference values, actual model results, units, acceptance tolerances and source provenance '
          'are retained in the [benchmark notebook](../../../verification/scientific_revision/36_benchmark_validation.ipynb), '
          '[benchmark results](../../../verification/scientific_revision/benchmark_results.json) and '
          '[chapter validation ledger](../../../verification/scientific_revision/notebook_physics_review.md).\n')
    existing=[c for c in notebook['cells'] if 'scientific-validation-scope' in c.get('metadata',{}).get('tags',[])]
    if existing:existing[0]['source']=text.splitlines(keepends=True)
    else:notebook['cells'].append({'cell_type':'markdown','metadata':{'tags':['scientific-validation-scope']},'source':text.splitlines(keepends=True)})
    before=sha(path);path.write_text(json.dumps(notebook,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
    report['notebook_sha256']=sha(path)
    report['scientific_validation']={'physics_report':str(evidence_path.relative_to(BOOK)),
        'validation_helper_sha256':helper_hashes,'pre_scope_markdown_sha256':before,
        'post_execution_edit':'Added scope and independent benchmark links only; every executed code-cell hash rechecked.'}
    report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    execution.append(report)
    checks=evidence['checks'];categories=Counter()
    for row in checks:categories[row['category']]+=row['evaluations']
    assertions=sum(isinstance(node,ast.Assert) for cell in notebook['cells'] if cell['cell_type']=='code' for node in ast.walk(ast.parse(''.join(cell['source']))))
    item={'chapter':chapter,'number':number,'notebook':str(path.relative_to(BOOK)),
          'status':'passed_scoped_checks','scope':scope,'limitations':limitations,
          'code_cells':report['code_cells'],'explicit_notebook_assertions':assertions,
          'distinct_check_labels':len(checks),'evaluations':sum(r['evaluations'] for r in checks),
          'category_evaluations':dict(categories),'rejected_candidates':len(evidence['rejected_candidates']),
          'uncovered_equipment':evidence['uncovered_equipment'],
          'notebook_sha256':sha(path),'code_cell_sha256':[r['sha256'] for r in report['cell_runs']],
          'physics_report_sha256':sha(evidence_path),'physics_report':str(evidence_path.relative_to(BOOK)),
          'validation_helper_sha256':helper_hashes,'runtime_seconds':report['runtime_seconds'],
          'figure_coverage':[{'path':r['path'],'sha256':r['sha256'],'series':len(r['series']),
                              'nonfinite_plotted_values':sum(s['n_nonfinite'] for s in r['series'])} for r in report['figures']]}
    ledger.append(item)
    prior=original['prior_numeric_results'];current=report['numeric_results']
    for key in sorted(set(prior)&set(current)):
        if not isinstance(prior[key],list) or not isinstance(current[key],list):continue
        try:a,b=np.asarray(prior[key],dtype=float),np.asarray(current[key],dtype=float)
        except (TypeError,ValueError):continue
        if a.shape!=b.shape:
            changes.append({'chapter':chapter,'variable':key,'change':'shape changed','old_shape':a.shape,'new_shape':b.shape});continue
        valid=np.isfinite(a)&np.isfinite(b)
        if not np.any(valid):continue
        delta=np.max(np.abs(a[valid]-b[valid]));scale=max(np.max(np.abs(a[valid])),1.)
        if delta>1e-5*scale:
            changes.append({'chapter':chapter,'variable':key,'max_absolute_change':float(delta),'relative_to_previous_range':float(delta/scale),
                            'old_min':float(a[valid].min()),'old_max':float(a[valid].max()),'new_min':float(b[valid].min()),'new_max':float(b[valid].max()),
                            'interpretation':'Timings vary with runtime; other changes require model/source interpretation.'})
assert len(ledger)==35
benchmark=json.loads((ROOT/'benchmark_results.json').read_text(encoding='utf-8'))
assert benchmark['status']=='passed' and not benchmark['failures']
source=Path(os.environ['NEQSIM_PROJECT_ROOT'])
revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
assert revision==benchmark['source_revision']
summary={'status':'passed_scoped_validation','generated_at':datetime.now(timezone.utc).isoformat(),
         'source_root':str(source),'source_revision':revision,'python':sys.executable,
         'notebooks_passed':35,'code_cells_executed':sum(r['code_cells'] for r in ledger),
         'explicit_notebook_assertions':sum(r['explicit_notebook_assertions'] for r in ledger),
         'distinct_check_labels':sum(r['distinct_check_labels'] for r in ledger),
         'physical_check_evaluations':sum(r['evaluations'] for r in ledger),
         'rejected_candidates':sum(r['rejected_candidates'] for r in ledger),
         'benchmark_comparisons':len(benchmark['comparisons']),'benchmark_failures':0,
         'important_limitations':benchmark['limitations'],
         'classified_findings':[
          {'type':'property_initialization','chapters':[12,26],'finding':'Valve outlets may have uninitialized phase-density caches. Initialize properties before testing density; no new equilibrium flash is performed.'},
          {'type':'model_approximation','chapters':[33],'finding':'Native SimpleTEGAbsorber transfers water after a PH flash and leaves an energy residual. The example explicitly reconstructs common outlet temperature at fixed component inventories; it does not claim native rigorous stage energy closure.'},
          {'type':'solver_cache_applicability','chapters':[31],'finding':'Separator skips changes below 1e-6 relative input tolerance. A tighter 1e-7 recycle demonstration now creates fresh separator phase allocations rather than weakening conservation assertions.'},
          {'type':'sensitivity_applicability','chapters':[21,33],'finding':'Utilization can rise when both capacity and loads increase; warm solvent can cause a shallow water-content minimum. Replaced unjustified monotonic assertions with the actual case equations and material-removal bounds.'},
          {'type':'reference_basis','chapters':[19],'finding':'ISO6976 real-gas relative density differs from the ideal molecular-weight ratio. Verified Wobbe=GHV/sqrt(relative density) on the same ISO basis.'}],
         'validation_helper_sha256':helper_hashes,
         'benchmark_results_sha256':sha(ROOT/'benchmark_results.json'),
         'benchmark_notebook_sha256':sha(ROOT/'36_benchmark_validation.ipynb'),
         'reference_manifest_sha256':sha(ROOT/'references/collection_manifest.json'),
         'ledger':ledger}
(ROOT/'notebook_physics_review.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
(ROOT/'numerical_changes.json').write_text(json.dumps(changes,indent=2,ensure_ascii=False),encoding='utf-8')
(BOOK/'verification/notebook_execution_report.json').write_text(json.dumps(execution,indent=2,ensure_ascii=False),encoding='utf-8')
lines=['# Notebook physics review','','All 35 notebooks pass their stated physical and analytical checks. This is scoped verification, not universal predictive validation.','',
 f"The run executed {summary['code_cells_executed']} code cells with {summary['explicit_notebook_assertions']} explicit notebook assertions. The reusable checks evaluated {summary['physical_check_evaluations']} conditions across {summary['distinct_check_labels']} distinct labels; repeated evaluations are sweeps, not independent experiments.",
 '',f"The separate benchmark notebook passed {len(benchmark['comparisons'])} comparisons. Eighteen density comparisons use SRK and PR at nine independent NIST reference-EOS states. Remaining comparisons test analytical limits, conservation and search algorithms. Exact inputs, expected values, actual values, units and tolerances are in [benchmark_results.json](benchmark_results.json).",'',
 'Physical acceptance criteria: positive absolute pressure/temperature and density; normalized overall and phase compositions; component reconstruction 1e-7 mole fraction; mass closure 1e-8 kg/s + 1e-7 relative; component flow closure 1e-7 times total inlet molar flow (minimum scale 1 mol/s); first-law closure 1e-5 times the largest absolute inlet/outlet/duty enthalpy rate (minimum 1 W). Case-specific analytical and constraint tolerances are retained in each chapter report. Missing phase quantities and rejected hydraulic candidates remain explicit.','',
 '| Chapter | Checked scope | Distinct checks | Evaluations | Rejected candidates |', '|---|---|---:|---:|---:|']
for r in ledger:lines.append(f"| {r['number']:02d} | {r['scope']} | {r['distinct_check_labels']} | {r['evaluations']} | {r['rejected_candidates']} |")
lines+=['','## Scope limits by chapter','']
for r in ledger:lines.append(f"- **{r['number']:02d}.** {r['limitations']}")
lines+=['','## Diagnosed model and execution issues','']
for r in summary['classified_findings']:lines.append(f"- **{r['type']} (chapters {', '.join(str(v) for v in r['chapters'])}).** {r['finding']}")
lines+=['','## Provenance','',f"Source revision: `{revision}`. Selected interpreter: `{sys.executable}`.",
        '','[Primary source archive](references/SOURCES.md) · [Executed independent benchmark notebook](36_benchmark_validation.ipynb) · [Machine-readable ledger and hashes](notebook_physics_review.json)',
        '', 'No production Java code was changed. Post-execution edits only clarify notebook discussions and add benchmark links; executed code hashes were rechecked and artifact hashes refreshed.']
(ROOT/'notebook_physics_review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k in ['status','notebooks_passed','code_cells_executed','explicit_notebook_assertions','distinct_check_labels','physical_check_evaluations','rejected_candidates','benchmark_comparisons']},indent=2))
print('Changed numerical arrays:',len(changes))
