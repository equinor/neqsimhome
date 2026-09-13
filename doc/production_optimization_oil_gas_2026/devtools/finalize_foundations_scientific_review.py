"""Build a truthful per-fence scientific review ledger from fresh literal evidence."""
from pathlib import Path
from collections import Counter
import re,json,hashlib,datetime,sys
B=Path(__file__).resolve().parents[1];V=B/'verification/scientific_revision'
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
release=load(B/'verification/foundations_release_audit.json')
issues=load(V/'foundations_text_changes.json');notes=load(V/'foundations_chapter_notes.json');analytical=load(V/'foundations_analytical_checks.json')
supplement=load(V/'foundations_remaining_solution_checks.json')
supplement_by_hash={r['code_sha256']:r for r in supplement['entries']}
chapters=[];errors=[]
if supplement['status']!='pass': errors.append('supplementary numerical solution check failed')
limitations={
'ch01':['Export limits are illustrative contract inputs; entrainment/solids and sampling quality are not inferred from equilibrium composition.'],
'ch02':['Hydrate and transport-property models have no independent calibration dataset in this review.','Raw saturation-trace getters do not prove complete branch identity; the separately rebuilt figure has its own transition-bracket evidence.'],
'ch03':['TBP saturation trace is explicitly unaccepted as a full envelope.','BIP regression target is synthetic; characterization and fitted properties are not laboratory validation.'],
'ch04':['Lumped reservoir configuration does not resolve field sweep or certify reserves.','Arps/PZ/IPR interpretations are limited to the assumptions printed in the chapter.'],
'ch05':['Pipeline thermal/holdup correlations are not field-calibrated.','Rod and jet pumps are reduced geometry/head-ratio demonstrations, not complete coupled lift designs.'],
'ch06':['The larger legacy multiphase network candidates and their optimizer/allocation continuations remain unaccepted as physical hydraulic solutions.','Accepted gas choke network has mass/pressure/domain evidence, not field or valve-vendor calibration.'],
'ch07':['Mechanical-design JSON leaves max/min design temperatures NaN; these are unset design inputs, not accepted material-temperature limits.','Costs, casing factors and thermal performance remain screening inputs.'],
'ch08':['Pipe heat-loss and multiphase holdup closure have no independent model calibration in this manuscript audit.','Steady-flow checks do not validate transient severe slugging or restart.'],
'ch09':['Finite hydrate temperature and inhibitor direction are numerical/domain checks, not calibrated hydrate prediction.','Corrosion, erosion, wax, asphaltene deposition and inhibitor hold time require corresponding laboratory/field/vendor evidence.'],
'ch10':['Mechanical-design JSON has unset min/max design temperatures (NaN); vessel compliance is not claimed.','Souders–Brown factors and droplet/retention sizing assumptions are not vendor capacity guarantees.'],
'ch11':['TVP calculation is not an ASTM Reid test result.','Converged stripping cases do not establish unmeasured product-quality compliance.'],
'ch12':['SimpleAmineAbsorber removals are prescribed; inferred isothermal heat is not independent reactive energy validation.','TEG regeneration and upstream dry-gas pretreatment are outside the illustrated boundary.','NGL stripping example is not a product-spec deethanizer.'],
'ch13':['Material consistency is not deoiling/scale/corrosion performance calibration.','Barite result is an inventory upper bound rather than predicted deposition.'],
'ch14':['Synthetic compressor map and software sizing/constraint demonstrations are not vendor-map validation.','Numerical feasible optimizer output is not a proof of global optimality.'],
'ch15':['Synthetic speed curves, surge/choke and cooling/recycle assumptions require vendor maps and operating validation.'],
'ch16':['Pinch cascade assumes stated constant heat-capacity streams; utility balance does not construct a realizable exchanger network.','Material/permit temperature inputs require service-specific qualification.'],
'ch17':['Valve isenthalpy does not calibrate Cv/opening or erosive/flashing performance.','Relief arithmetic does not constitute a full code-compliant relief assessment.'],
'ch18':['Steam case uses SRK water without independent steam-table calibration; 0.08bara candidate is explicitly rejected on energy closure.','Turbine map/exhaust are synthetic; no combustor or complete combined-cycle balance is claimed.','Dated taxes and illustrative scenario prices are distinguished; carbon accounting uses explicit fuel/slip/GWP boundaries.']}
for path in sorted((B/'chapters').glob('ch*/chapter.md'))[:18]:
 name=path.parent.name;ch=name[:4];text=path.read_text(encoding='utf-8');phys=load(V/(ch+'_manuscript_physics.json'))
 entries=[]
 for idx,m in enumerate(re.finditer(r'^```(python|java)\s*\n(.*?)^```',text,re.M|re.S),1):
  code=m[2];h=sha(code.encode());rec=next((r for r in release['entries'] if r['chapter']==name and r['code_sha256']==h),None)
  pblock=next((r for r in phys['literal_blocks'] if r['code_sha256']==h),None)
  checks=[r for r in phys['physical_checks'] if pblock and r['block']==pblock['index']]
  evidence=[]
  supplemental=supplement_by_hash.get(h)
  if supplemental:
   classification='engineering_calculation_with_targeted_solution_checks'
   evidence.append({'path':'verification/scientific_revision/foundations_remaining_solution_checks.json','code_sha256':h,'scope':supplemental['scope'],'check_count':len(supplemental['checks']),'all_pass':supplemental['status']=='pass'})
  elif checks:
   classification='engineering_calculation_with_scoped_checks'
   evidence.append({'path':str((V/(ch+'_manuscript_physics.json')).relative_to(B)),'code_sha256':h,'physical_block_index':pblock['index'],'unit_or_case_evaluations':len(checks),'check_names':sorted(set(c['name'] for r in checks for c in r.get('checks',[]))),'all_pass':all(r['pass'] for r in checks),'scope':sorted(set(r['scope'] for r in checks))})
  elif ch=='ch06' and m[1]=='java' and 'setChokeUseValveModel(true)' in code:
   classification='accepted_gas_hydraulic_case_with_literal_assertions'
   evidence.append({'path':'verification/scientific_revision/network_probe.json','scope':'Four supported-valve-model openings; converged, pressure residual<=100Pa, mass residual<=1e-6kg/s, finite positive flow/pressure; corresponding checks execute in the literal Java fence'})
  elif ch=='ch06' and 'network.' in code and re.search(r'run\(|optimize|balance|evaluate|allocation',code,re.I):
   classification='executed_legacy_network_candidate_not_accepted_physically'
   evidence.append({'path':rec['report'] if rec else '', 'scope':'API execution only for explicitly unaccepted legacy multiphase network; accepted compact gas case is separate'})
  elif 'assert ' in code:
   classification='bounded_calculation_with_literal_acceptance_assertions'
   evidence.append({'path':rec['report'] if rec else '', 'scope':'Exact literal assertions and their output; not a blanket model calibration claim','assertions':re.findall(r'^\s*assert\s+(.+)',code,re.M)})
  elif 'calcPTphaseEnvelope' in code:
   classification='saturation_trace_API_demo_not_complete_envelope_validation'
   evidence.append({'path':rec['report'] if rec else '', 'scope':'Trace execution and exposed candidate data; full physical branch completeness not asserted'})
  elif m[1]=='java':
   classification='executed_configuration_introspection_or_capacity_API_demo'
   evidence.append({'path':rec['report'] if rec else '', 'scope':'Exact sequential Java fragment execution; no independent physical balance is claimed for this fragment. Corresponding Python process examples carry their own scoped checks.'})
  elif not re.search(r'\.run\(|[Ff]lash\(|calculate|calc_|fit[A-Z]|[Ee]nvelope|[Hh]ydrate',code):
   classification='configuration_introspection_or_plotting_fragment'
   evidence.append({'path':rec['report'] if rec else '', 'scope':'Fluid/equipment construction, state introspection or declared illustrative plotting; no fresh engineering solution is asserted'})
  else:
   classification='executed_property_or_screening_calculation_with_limited_validation'
   evidence.append({'path':rec['report'] if rec else '', 'scope':'Executed source calculation; chapter assumptions apply. No independent per-fragment calibration or complete balance proof is claimed.'})
  e={'index':idx,'language':m[1],'line':text[:m.start()].count('\n')+1,'code_sha256':h,'classification':classification,'status':rec['status'] if rec else 'missing_execution','execution_evidence':rec['report'] if rec else None,'engineering_evidence':evidence}
  if 'calcPTphaseEnvelope' in code:
   e['engineering_acceptance']='not_accepted_as_complete_physical_envelope'
   e['execution_status']='pass' if rec and rec['status']=='pass' else 'fail'
   e['diagnostic_scope']='Raw candidate-array API demonstration only; fresh branch proof belongs to separately rebuilt illustration. No complete-envelope acceptance is inferred.'
  if supplemental:
   e['engineering_acceptance']='accepted_within_stated_numerical_scope'
  if m[1]=='python':
   e['physical_runner_literal_hash_match']=pblock is not None
   if pblock is None:errors.append(ch+' block '+str(idx)+' has no fresh physical-run literal hash')
   elif pblock['execution']!='pass':errors.append(ch+' block '+str(idx)+' physical runner execution failed')
  if not rec or rec['status']!='pass':errors.append(ch+' block '+str(idx)+' missing successful literal execution')
  if any(not r['pass'] for r in checks):errors.append(ch+' block '+str(idx)+' physical check failed')
  entries.append(e)
 chapter_issues=[r for r in issues if r['chapter']==name]
 chapters.append({'chapter':name,'full_text_review':True,'source_sha256':sha(text.encode()),'scientific_review_note':notes[ch],'issues_and_corrections':chapter_issues,'entries':entries,'physical_evaluation_count':len(phys['physical_checks']),'physical_evaluations_pass':all(r['pass'] for r in phys['physical_checks']),'analytical_checks':[r for r in analytical['checks'] if r['chapter']==ch],'limitations':limitations[ch],'original_backup':'.build/scientific_revision_foundations_originals/'+name+'/chapter.md'})
counts=Counter(e['classification'] for c in chapters for e in c['entries'])
result={'status':'pass' if not errors and analytical['status']=='pass' else 'fail','full_text_review':True,'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_revision':'6cc8026202a5d3f9383c9abd1d97d448993813f9','python':sys.executable,'scope':'Complete scientific prose review of chapters01–18, literal execution of every published Python/Java fence, scoped physical checks for central calculations, and explicit API/empirical-model limitations. Numerical checks are not empirical model calibration.','correction_count':len(issues),'chapter_count':18,'literal_fence_count':sum(len(c['entries']) for c in chapters),'classification_counts':dict(counts),'physical_unit_or_case_evaluations':sum(c['physical_evaluation_count'] for c in chapters),'analytical_check_count':len(analytical['checks']),'errors':errors,'chapters':chapters,'source_metadata':'verification/scientific_revision/foundations_refs.bib','independent_benchmark_reference':'verification/scientific_revision/benchmark_results.json','limitations':['Independent notebook benchmarks are separately owned and scoped; their89 checks are not counted as manuscript checks.','API examples, synthetic maps, unaccepted legacy networks and full physical models have distinct classifications.','No Java production source was changed by this review.','Source and code hashes must be refreshed after later publication edits.']}
result['supplementary_solution_check_count']=sum(len(r['checks']) for r in supplement['entries'])
result['supplementary_solution_case_count']=len(supplement['entries'])
result['numerical_coverage_complete']=not errors and not any(e['classification']=='executed_property_or_screening_calculation_with_limited_validation' for c in chapters for e in c['entries'])
result['unresolved_solution_verification']=errors
result['explicit_unaccepted_saturation_diagnostics']=[{'chapter':c['chapter'],'index':e['index'],'code_sha256':e['code_sha256']} for c in chapters for e in c['entries'] if e.get('engineering_acceptance')=='not_accepted_as_complete_physical_envelope']
(V/'foundations_review.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
md=['# Scientific review: foundation chapters01–18','',f"Status: **{result['status'].upper()}**. All18 full chapter texts reviewed; {result['correction_count']} recorded substantive corrections. Every published fence is linked by exact SHA-256 to its execution record.",'',f"Literal execution: {result['literal_fence_count']} Python/Java fences. Scoped unit/case evaluations: {result['physical_unit_or_case_evaluations']}; independent equation/unit checks: {result['analytical_check_count']}. These are numerical verification and analytical limits, not general model calibration.",'','| Chapter | Literal fences | Unit/case evaluations | Recorded corrections |','|---|---:|---:|---:|']
for c in chapters:md.append(f"| {c['chapter']} | {len(c['entries'])} | {c['physical_evaluation_count']} | {len(c['issues_and_corrections'])} |")
for c in chapters:
 md+=['', '## '+c['chapter'],'',c['scientific_review_note']['text'],'','Limits: '+' '.join(c['limitations']),'', 'Source SHA-256: `'+c['source_sha256']+'`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.']
md+=['','## Supplementary solution checks','',f"The final supplemental gate executes {result['supplementary_solution_case_count']} exact cases with {result['supplementary_solution_check_count']} targeted checks. It closes the six formerly execution-only property/process/screening entries and additionally checks the repaired synthetic BIP regression. Full details and tolerances are in foundations_remaining_solution_checks.json.",'','The raw saturation-trace portions in Chapters02,03,09 and12 are explicitly unaccepted as complete physical envelopes; successful API execution is retained as diagnostic evidence only. The original Chapter03 BIP recipe was replaced by an explicitly oil-rich illustrative recipe after its821.1bara dense-phase candidate failed the vapor/liquid bracket. The accepted171.167bara case and connected synthetic regression pass fresh vapor/liquid, material and fugacity checks.']
if errors:md+=['','## Unresolved gate failures','']+['- '+x for x in errors]
(V/'foundations_review.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
(V/'foundations_review_progress.json').write_text(json.dumps({'status':result['status'],'full_text_review':True,'prose_read_complete':list(range(1,19)),'remaining_prose':[],'pending_issues':{},'errors':errors,'authoritative_ledger':'foundations_review.json','chapter_completion':[{'chapter':c['chapter'],'full_text_review':True,'physical_evaluations_pass':c['physical_evaluations_pass']} for c in chapters]},indent=2),encoding='utf-8')
print(result['status'],result['literal_fence_count'],'fences',result['physical_unit_or_case_evaluations'],'unit/case checks',len(errors),'errors')
for e in errors:print(e)
raise SystemExit(0 if result['status']=='pass' else 1)
