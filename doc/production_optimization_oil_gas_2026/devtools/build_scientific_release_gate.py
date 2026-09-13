"""Bind the final reviewed manuscript to executed and scoped scientific evidence."""
from pathlib import Path
from collections import Counter
import datetime
import hashlib
import json
import re
import sys

BOOK=Path(__file__).resolve().parents[1]
OUT=BOOK/'verification/scientific_revision'
def read(path):
    return json.loads((BOOK/path).read_text(encoding='utf-8-sig'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def asset_path(value):
    path=Path(value)
    return path if path.is_absolute() else BOOK/path
nb=read('verification/notebook_release_audit.json')
physics=read('verification/scientific_revision/notebook_physics_review.json')
runtime=read('verification/scientific_revision/runtime_artifact_manifest.json')
bench=read('verification/scientific_revision/benchmark_results.json')
fa=read('verification/foundations_release_audit.json')
oa=read('verification/optimization_chapters_audit_summary.json')
foundation=read('verification/scientific_revision/foundations_review.json')
optimization=read('verification/scientific_revision/optimization_review.json')
onshore=read('verification/scientific_revision/onshore_review.json')
sources=read('verification/scientific_revision/final_source_review.json')
illustrations=read('verification/scientific_revision/manuscript_figure_review.json')
visual=read('verification/scientific_revision/manuscript_repair_visual_review.json')
literal_visual=read('verification/scientific_revision/literal_figure_visual_review.json')
errors=[]
def require(condition,message):
    if not condition: errors.append(message)
require(nb['status']=='passed' and nb['passed_notebooks']==35,'Notebook integrity incomplete')
require(physics['notebooks_passed']==35 and physics['benchmark_failures']==0,'Notebook scientific checks incomplete')
require(runtime['source_commit']==physics['source_revision'] and runtime['tracked_java_and_pom_clean'],
        'Runtime/source identity differs from scientific verification')
for name,digest in runtime['compiled_classes'].items():
    require(sha(Path(runtime['source_root'])/'target/classes'/name)==digest,
            'Compiled NeqSim class changed after verification: '+name)
for name,digest in physics['validation_helper_sha256'].items():
    require(sha(OUT/name)==digest,'Notebook acceptance helper changed after checks: '+name)
for name,digest in bench['hashes'].items():
    require(sha(OUT/name)==digest,'Benchmark calculation or reference changed: '+name)
require(len(bench['comparisons'])==89 and all(r['passed'] for r in bench['comparisons']),'Benchmark failed or count changed')
require(fa['counts']=={'pass':sum(fa['counts'].values())} and not fa['exclusions'],'Foundation literal execution incomplete')
require(oa['all_runnable_fences_passed'] and not oa['stale_or_missing'],'Optimization literal execution incomplete')
require(optimization.get('numerical_coverage_complete') is True,
        'Optimization manuscript still lacks complete scoped numerical solution evidence')
require(optimization.get('unresolved_solution_verification')==[],
        'Optimization manuscript has unresolved numerical solution checks')
require(foundation.get('numerical_coverage_complete') is True,
        'Foundations manuscript still lacks complete scoped numerical solution evidence')
require(foundation.get('unresolved_solution_verification')==[],
        'Foundations manuscript has unresolved numerical solution checks')
review_rows=foundation['chapters']+optimization['chapters']+[onshore]
bychapter={r['chapter']:r for r in review_rows}
require(len(bychapter)==35,'Scientific review does not cover all35chapters')
require(all(r.get('full_text_review') for r in review_rows),'A chapter full-text review is missing')
fence=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
coverage=[]
for path in sorted((BOOK/'chapters').glob('*/chapter.md')):
    name=path.parent.name;source=path.read_text(encoding='utf-8')
    rows=bychapter.get(name,{})
    reviewed_hashes={e.get('code_sha256',e.get('sha256')) for e in rows.get('entries',[])}
    live=[];patterns=0
    for i,m in enumerate(fence.finditer(source),1):
        digest=hashlib.sha256(m[3].encode()).hexdigest();live.append(digest)
        if 'pattern' in m[2]:patterns+=1
        require(digest in reviewed_hashes,f'Scientific per-fence evidence missing: {name}/{i}')
        entry=next((e for e in rows.get('entries',[]) if e.get('code_sha256',e.get('sha256'))==digest),{})
        require(entry.get('classification')!='executed_numerical_or_api_demonstration_unqualified',
                f'Unqualified numerical example remains: {name}/{i}')
    frozen=sources['chapters'][name]
    require(sha(path)==frozen['final_sha256'],f'Manuscript changed after final source review: {name}')
    require(live==frozen['code_sha256'],f'Code changed during editorial integration: {name}')
    coverage.append({'chapter':name,'full_text_review':rows.get('full_text_review',False),
                     'executed_fences':len(live)-patterns,'integration_patterns':patterns,
                     'notebook_scope':next(r['scope'] for r in physics['ledger'] if r['chapter']==name),
                     'chapter_sha256':sha(path)})
require(not any(r['action']=='changed_asset_requires_manual_review' for r in illustrations['changes']),
        'A legacy image replacement still requires manual review')
require(visual.get('status')=='passed_scoped_visual_and_scientific_review'
        and visual['counts']['unresolved_material_findings']==0,'Manuscript illustration review incomplete')
for row in visual['images']:
    require(sha(Path(row['path']))==row['sha256'],'Reviewed manuscript image changed: '+row['path'])
require(literal_visual['unresolved_material_visual_defects']==0 and literal_visual['minor_corrections_pending']==0,
        'Literal-run figure review has unresolved findings')
for row in literal_visual['images']:
    require(sha(Path(row['path']))==row['sha256'],'Reviewed literal-run image changed: '+row['path'])
for name in ('figure_visual_review.json','legacy_phase_envelopes/visual_review.json'):
    audit=read('verification/scientific_revision/'+name)
    for row in audit['records']:
        require(sha(Path(row['path']))==row['sha256'],'Reviewed scientific image changed: '+row['path'])
for name in ('literal_solution_figure_review.json','ch21_figure_review.json','ch28_literal_solution_figure_review.json','ch24_figure_review.json',
             'additional_scientific_literal_figure_review.json','final_original_asset_review.json',
             'final_foundations_liquid_basis_review.json'):
    require((OUT/name).exists(),'Final numerical figure review missing: '+name)
    if (OUT/name).exists():
        audit=read('verification/scientific_revision/'+name)
        require(audit.get('status') in ('passed','passed_scoped_visual_and_source_array_review'),'Numerical figure review incomplete: '+name)
        for row in audit.get('images',audit.get('records',audit.get('figures',[]))):
            require(sha(asset_path(row['path']))==row['sha256'],'Reviewed numerical image changed: '+row['path'])
require('0 error(s)' in (BOOK/'verification/book_check_final.log').read_text(encoding='utf-8-sig'),
        'Canonical book check has errors')
evidence=read('evidence_report.json')
require(not any(r.get('severity')=='error' for r in evidence.get('issues',[])),
        'Canonical evidence report has errors')
types=Counter(r['evidence_type'] for r in bench['comparisons'])
independent=[r for r in bench['comparisons'] if r['evidence_type']=='independent reference EOS']
require(len(independent)==18,'Independent reference comparison count changed')
# Historical reports remain immutable. This snapshot binds current companion
# artifacts and the final source after explicitly reviewed editorial integration.
files=[BOOK/name for name in ('book.yaml','refs.bib','nomenclature.yaml',
       'evidence_report.json','figure_dossier.json','skill_stack_plan.json')]
for parent,pattern in [('frontmatter','*.md'),('backmatter','*.md'),('chapters','*/chapter.md'),
                       ('chapters','*/notebooks/*.ipynb'),('chapters','*/figures/*')]:
    files.extend(p for p in (BOOK/parent).glob(pattern) if p.is_file())
for name in ['notebook_release_audit.json','notebook_execution_report.json','foundations_release_audit.json',
             'optimization_chapters_audit_summary.json','figure_integration_report.json','book_check_final.log']:
    files.append(BOOK/'verification'/name)
for path in (BOOK/'verification/pdf_final').glob('*prose_fix.json'):
    audit=json.loads(path.read_text(encoding='utf-8'))
    require(audit.get('status')=='passed' and audit.get('code_unchanged') is True,
            'Final PDF prose correction lacks a code-preservation check: '+path.name)
    files.append(path)
for path in OUT.rglob('*'):
    if path.is_file() and path.suffix.lower() in ('.json','.md','.csv','.tsv','.txt','.bib','.py','.html','.pdf'):
        if path.name not in ('engineering_release_gate.json','SCIENTIFIC_REVIEW.md'):
            files.append(path)
report={'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status':'passed_with_declared_model_scope' if not errors else 'failed',
        'source_revision':physics['source_revision'],'python':sys.executable,
        'reviewed_chapters':len(bychapter),'executed_notebooks':35,'notebook_code_cells':nb['executed_code_cells'],
        'executed_manuscript_fences':sum(r['executed_fences'] for r in coverage),
        'integration_patterns_not_executed':sum(r['integration_patterns'] for r in coverage),
        'benchmark_comparisons':len(bench['comparisons']),
        'independent_reference_eos_comparisons':len(independent),'benchmark_evidence_types':dict(types),
        'unresolved_release_errors':errors,'chapters':coverage,
        'evidence_sha256':{str(p.relative_to(BOOK)):sha(p) for p in sorted(set(files))}}
lines=['# Scientific review of the production optimization textbook','',
       'The complete 35-chapter manuscript was read for scientific quality, corrected and checked against its stated calculation basis. The revised teaching calculations have execution and engineering acceptance evidence; this is not a blanket certification of field predictive accuracy.','',
       f"- Chapter notebooks: **35/35 passed, {nb['executed_code_cells']} code cells**.",
       f"- Literal manuscript code: **{report['executed_manuscript_fences']} executable Python/Java fragments passed** in their documented sequential chapter context.",
       '- These executable fragments include API/configuration examples and explicitly rejected native diagnostics. Execution success is not engineering acceptance; accepted numerical examples have additional scoped checks in their per-example ledgers.',
       f"- External integration patterns: **{report['integration_patterns_not_executed']}**, explicitly identified with prerequisites and excluded from execution claims.",
       '- Benchmark notebook: **89/89 comparisons passed**, including **18 independent NIST reference-EOS comparisons** at nine methane states. The remaining comparisons check analytical relations, balances and independent search procedures.',
       '- Every chapter has a scientific review ledger and exact published-code hashes. All 104 notebook figures have current calculation outputs and reviewed discussions.','',
       '## What changed scientifically','',
       '- Corrected units, standard/actual volume bases, water-cut and composition definitions, component recovery and molar/mass conversions.',
       '- Corrected metre/kilometre and vertical-flow direction errors, zero/undefined gas-quality calculations, a hundredfold capacity-percent reporting error, and economically mislabeled or dimensionally inconsistent examples.',
       '- Replaced gas-equivalent standard-volume oil pricing with an explicit 15 C/1.01325 bara stock-tank flash, all-phase product accounting and a liquid mass/density/volume identity check. Final-separator liquid and stock-tank oil are identified separately.',
       '- Added phase checks and knockout separation before gas compression and expansion, complete product accounting, and explicit heat and shaft-work boundaries.',
       '- Required column energy/equilibrium residuals and rigorous convergence; rejected apparently solved but physically inconsistent column states.',
       '- Exposed the approximate TEG absorber energy imbalance and documented the bounded fixed-composition energy reconstruction rather than hiding its native-model limitation.',
       '- Checked selected optimization points with fresh model replay and grid/analytical comparisons; separated assumed capacity screens from installed-equipment evidence.',
       '- Preserved the native tabulated gas-lift allocation failure as a rejected diagnostic and supplied an independently checked linear-programming allocation. Separated outside-map compressor penalties from numerical performance curves.',
       '- Replaced flat-rate resource uncertainty with executed depletion profiles, and checked transient inventory/energy balances and timestep refinement.',
       '- Replaced fabricated experimental plots and unsupported optimization curves; retained conceptual illustrations only with explicit synthetic assumptions.',
       '- Reconciled legacy plots with the current accepted literal executions and their actual source arrays; corrected stale maxima, flow bases and unsupported compressor-map boundaries.',
       '- Corrected scientific definitions, equations and reference metadata, and quarantined unverified unused bibliography entries.','',
       '## Independent validation and remaining scope','',
       'The methane density benchmark covers SRK and Peng–Robinson at 300, 350 and 400 K and 1, 50 and 100 bara. Maximum absolute relative deviations are 1.421% and 0.811%, respectively, within the declared 3% teaching accuracy budget. NIST supplies independent reference-EOS calculations, not raw experimental measurements; 3% is not NIST measurement uncertainty.','',
       'Conservation, equilibrium and solver residuals verify the implemented equations. They do not validate mixture characterization, hydrate/TEG prediction, corrosion/erosion correlations, vendor compressor maps, field hydraulics, plant dynamics or economics against measurements. Those domains retain explicit limitations in the chapter ledgers. No plant data or vendor acceptance tests were provided.','',
       'Chapter 3’s replacement phase-envelope illustration uses an explicitly different defined-compound surrogate; the original TBP trace did not pass branch checks and is not validated by that substitute. Chapter 12’s continuation gap remains open. Undefined physical states and rejected numerical candidates are documented rather than interpolated into accepted results.','',
       'Unsolved exercises remain learning assignments. API configuration examples are checked in their stated software context; optional service integrations cannot prove a live external connection. Synthetic prices, duties, ratings and control fixtures are assumptions, not measured or commercially qualified results.','',
       '## Chapter coverage','',
       '| Chapter | Executed manuscript fragments | External patterns | Checked notebook calculation |','|---|---:|---:|---|']
lines += [f"| {r['chapter']} | {r['executed_fences']} | {r['integration_patterns']} | {r['notebook_scope']} |" for r in coverage]
lines += ['', '## Evidence and reproduction','',
          '`engineering_release_gate.json` binds the final chapter sources and companion evidence by SHA256. The foundations, optimization and onshore review files describe per-example checks and limitations. `benchmark_results.json` retains expected values, computed values, tolerances and references; `references/SOURCES.md` indexes archived reference data.', '',
          'Use the interpreter and source checkout recorded in the book README. Notebook, literal manuscript, benchmark and publication checks are separate reproducible stages. The publication manifest identifies the exact reviewed PDF and HTML files; the prior edition is retained under `.build/pre_scientific_publication`.', '',
          'PaperLab’s marker-based evidence scanner is a diagnostic, not scientific approval. Figure captions are numbered by the PDF/HTML renderers; the final structure audit verifies those labels. Retained formatting warnings and the default publisher length advisory are explained in the release report.', '',
          'The PaperLab scientific-writing/traceability skills and notebook-verifier handoff were improved to preserve these distinctions, require actual figure inspection and avoid automatic approval from a discussion marker.']
if errors: lines += ['', '## Unresolved release errors','']+['- '+e for e in errors]
(OUT/'SCIENTIFIC_REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
report['evidence_sha256']['verification/scientific_revision/SCIENTIFIC_REVIEW.md']=sha(OUT/'SCIENTIFIC_REVIEW.md')
(OUT/'engineering_release_gate.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('chapters','evidence_sha256')},indent=2))
raise SystemExit(1 if errors else 0)
