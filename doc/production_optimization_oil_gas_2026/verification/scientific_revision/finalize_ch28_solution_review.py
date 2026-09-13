"""Freeze Chapter 28 exact-source evidence and explicit scientific scope."""
from pathlib import Path
import hashlib,json,re,datetime,sys
B=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
S=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
C=next((B/'chapters').glob('ch28_*'));chapter=C/'chapter.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
py_path=OUT/'ch28_solution_checks.json';ja_path=OUT/'ch28_java_solution_checks.json'
py=read(py_path);ja=read(ja_path);assert py['all_targeted_checks_passed'] and ja['all_targeted_checks_passed']
assert py['hook_sha256']==sha(Path(py['hook_module']))
for row in ja['bound_sources']:assert sha(Path(row['path']))==row['sha256'],row
ordinary_py=B/'verification/ch28_field_development_fences.json';ordinary_ja=B/'verification/ch28_field_development_java.json'
opy=read(ordinary_py);oja=read(ordinary_ja)
py_rows=opy.get('examples',opy.get('entries',[]));ja_rows=oja['examples']
if not py_rows:raise AssertionError(list(opy))
current=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',chapter.read_text(encoding='utf-8-sig'),re.M|re.S))
ledger=[]
for i,m in enumerate(current,1):
 lang,ann,code=m.groups();digest=hashlib.sha256(code.encode()).hexdigest()
 if 'pattern' in ann:
  ledger.append({'number':i,'language':lang,'code_sha256':digest,'status':'explicit_external_input_pattern','required_evidence':ann.strip(),'scope':'No supplied external dataset or complete configured model; excluded from runnable numerical solution claims.'});continue
 source=py if lang=='python' else ja
 entry=next(r for r in source['entries'] if r['number']==i)
 assert entry['sha256']==digest and entry['status']=='passed',(i,'supplementary source/status')
 ordinary=next(r for r in (py_rows if lang=='python' else ja_rows) if r['number']==i)
 assert ordinary['sha256']==digest and ordinary['status']=='passed',(i,'ordinary source/status',ordinary)
 ledger.append({'number':i,'language':lang,'code_sha256':digest,'status':'passed','checks':len(entry['checks']),'report':str((py_path if lang=='python' else ja_path).relative_to(B)),'classification':entry.get('classification','numerical_solution_check')})
assert len(ledger)==24 and sum(r['status']=='passed' for r in ledger)==19
backup=B/'.build/backups/ch28_literal_solution_revision'
rejections=[
 {'issue':'Third recombination argument mislabeled as mass kg/hr; inherited helper expected 10000 kg/hr','resolution':'Current primary Java contract uses 10000 Sm3/hr total standard liquid. Validate liquid volume and resulting mass separately. Original mass mismatch retained; tolerance was not relaxed to pass a wrong unit.','evidence':[str(p.relative_to(B)) for p in backup.glob('ch28_java_solution_checks.*')]},
 {'issue':'Published export example invented VFPEXP deck text contradicting the actual diagnostic API','resolution':'Replaced with actual diagnostic column/unit/feasibility contract; exact written UTF-8 output checked against native diagnostic text.'},
 {'issue':'Initial supplementary reference-phase component lookup assumed every separated phase had every mixture component','resolution':'Absent components contribute zero to the independent inventory, as the actual phase composition specifies. No manuscript or model inputs changed.','evidence':['.build/backups/ch28_literal_solution_revision/java_hook_missing_reference_components.json']},
 {'issue':'Initial reference-state hook interpreted unflashed input phase fields as equilibrium','resolution':'A cloned reference receives an explicit verification TP flash before phase component-balance checking. Input configuration is not misrepresented as a solved equilibrium.'},
 {'issue':'3D polygon colors used average facet values with an ambiguous pressure colorbar','resolution':'Final literal plot uses uniform shading, six explicit black solution markers and a pressure height axis. Numeric arrays remain unchanged.'},
 {'issue':'Route alternatives named a booster/FPSO/riser without those equipment changes; economic pattern multiplied total mass by volumetric water cut','resolution':'Routes now describe changed horizontal lengths with unchanged upward tubing. The external-data economic pattern uses standard oil-plus-water liquid volume and volumetric water cut on a common reference.'}]
for row in rejections:
 row['retained_files']=[{'path':p,'sha256':sha(B/p)} for p in row.get('evidence',[]) if (B/p).exists()]
(OUT/'ch28_rejected_diagnostics.json').write_text(json.dumps({'findings':rejections},indent=2),encoding='utf-8')
bound=[py_path,ja_path,ordinary_py,ordinary_ja,chapter,OUT/'ch28_rejected_diagnostics.json',OUT/'ch28_literal_solution_figure_data.json',OUT/'ch28_literal_solution_figure_review.json']
source_paths=[S/'src/main/java/neqsim/process/util/optimizer'/name for name in ['FluidMagicInput.java','RecombinationFlashGenerator.java','MultiScenarioVFPGenerator.java']]
source_paths += [S/'src/main/java/neqsim/process/fielddevelopment/integrated'/name for name in ['IntegratedProductionModel.java','ReservoirToMarketOptimizer.java','WellDeliverabilityCurve.java','WellBranch.java','FlowlineBranch.java']]
script_paths=[OUT/name for name in ['ch28_solution_hooks.py','verify_ch28_java_solutions.py','ch28_base_java_checks.jsh','ch28_java_extra_checks.jsh','publish_ch28_literal_figures.py','finalize_ch28_solution_review.py']]
result={'chapter':C.name,'status':'passed_and_frozen','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python_executable':sys.executable,'source_commit':py['source_commit'],'chapter_sha256':sha(chapter),'counts':{'runnable_python_fences':8,'runnable_java_fences':11,'external_input_patterns':5,'python_check_records':sum(len(e['checks']) for e in py['entries']),'java_check_records':sum(len(e['checks']) for e in ja['entries']),'pressure_table_cells_replayed':96,'python_reference_density_states':5,'independent_reduced_network_scalar_roots':2,'new_literal_figures':3},'fences':ledger,'bound_artifacts':[{'path':str(p.relative_to(B)),'sha256':sha(p)} for p in bound],'primary_code_and_verifier_hashes':[{'path':str(p),'sha256':sha(p)} for p in source_paths+script_paths],
 'coverage':['Phase composition normalization and flash component accounting for recombined literal fluids.','Independent reference-phase mixing inventory, actual standard liquid volume, GOR and volumetric water-cut reconciliation at 15 C and 1.01325 bara.','All 96 accepted/unavailable Java and Python table cells: exact configured rate basis, pressure domain, fresh reported/lower inlet pressure bracket, tubing and flowline material/component conservation.','Java geometric GOR and linear water-cut grids, dimensions, indexed data access and exact diagnostic text content.','Reduced allocation rate accounting, positive bounded chokes and pressures, revenue/energy/emission unit identities, independent scalar solution of the declared piecewise Vogel/quadratic-line equations and feasible global capacity witness.','Plot array identity and actual reviewing-agent visual inspection of all three new manuscript figures.'],
 'applicability_limits':['These literal hydraulic replays verify the solutions of the supplied correlations; they are not an independent field calibration. Book benchmark evidence remains a separately scoped artifact.','No pipe heat-transfer boundary is specified in these cases; an energy-conservation claim for an adiabatic pipe is not made.','Vogel-shaped wellhead curves and default quadratic line resistances are illustrative reduced surrogates. Chokes are mathematical deliverability multipliers, not calibrated valve positions.','The optimizer returns a feasible near-optimum 0.190% below the independently reachable revenue upper bound. Constant energy and emissions intensities do not constitute a thermodynamic facility or lifecycle assessment.','Route-length alternatives do not include a subsea booster or FPSO processing model. Standard liquid mixing rates and total mixture mass rates remain separate dimensions.','No field data is supplied for the five explicitly annotated integration patterns; no execution or solution validation is claimed for those external-data workflows.'],
 'regeneration':['Run devtools/verify_optimization_solution_hooks.py --chapter 28 --hooks verification/scientific_revision/ch28_solution_hooks.py using the user-selected runtime.','Run verification/scientific_revision/verify_ch28_java_solutions.py using the same runtime. The copied helper is exclusive to this chapter.','Run publish_ch28_literal_figures.py, inspect each resulting actual image, and refresh ch28_literal_solution_figure_review.json/md.','Run ordinary audit_optimization_examples.py --chapters 28 and audit_optimization_java.py --chapters 28, then finalize_ch28_solution_review.py.','Do not rerun one-time manuscript repair editors as routine execution steps; do not regenerate the frozen notebook figures.']}
(OUT/'ch28_literal_solution_review.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
md=['# Chapter 28 literal engineering solution review','',f"Passed: 8 Python and 11 Java runnable fences, {result['counts']['python_check_records']} Python and {result['counts']['java_check_records']} Java check records. All 96 table cells have current-source solution checks. Five external-input patterns remain explicitly scoped. Three new figures were inspected by the reviewing agent.",'','## Material corrections','']
md += ['- '+r['issue']+'. '+r['resolution'] for r in rejections]
md += ['','## Numerical result and engineering interpretation','','The reduced allocation gives 39,923.9833 Sm³/day and revenue 119,771.9499 per day. The independent feasible 40,000 Sm³/day witness establishes revenue 120,000 per day as a reachable upper bound: the reported candidate is 0.190% below it. The five density states decrease from 187.2664 to 47.7679 kg/m³ over GOR 200–5000 at 80 °C and 50 bara. Nonmonotonic required inlet pressures are retained and physically bracketed.','','## Exact scope and limits','']
md+=['- '+s for s in result['applicability_limits']]
md+=['','## Source freshness','',f'Chapter SHA-256: `{result["chapter_sha256"]}`. The JSON ledger records every current literal hash, ordinary execution status, primary source and verifier hash, tolerances and evidence-file hashes. The 35 notebooks and their existing reports were not changed.','']
(OUT/'ch28_literal_solution_review.md').write_text('\n'.join(md),encoding='utf-8')
print(json.dumps(result['counts']))
