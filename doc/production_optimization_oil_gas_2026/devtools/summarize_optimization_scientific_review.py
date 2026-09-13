"""Bind scientific review scope to literal code, execution and numerical evidence.

This is a conservative dossier generator, not an automatic physics validator.
The explicit acceptance map records reviewed tests. A successful call outside
that map is never promoted to an accepted engineering calculation.
"""
from pathlib import Path
from datetime import datetime,timezone
import ast,collections,hashlib,json,re,shutil,subprocess,sys
from optimization_solution_coverage import proof_index,inventory_kind,ADDITIONAL_CORRECTIONS,UPDATED_LIMITATIONS

B=Path(__file__).resolve().parents[1]
V=B/'verification/scientific_revision'
SOURCE=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
NUMBERS=list(range(19,33))+[34,35]
sha=lambda data:hashlib.sha256(data).hexdigest()

# These descriptions are reviewed scientific judgments, not inferred from a pass flag.
reviews={
19:(
 'Export thermodynamics, ISO6976 references, measurement uncertainty and fiscal scope',
 ['Corrected SI isothermal Darcy pressure-square equation and compression efficiency convention.',
  'Separated ISO6976 composition calculations from the assumed sales-quality envelope and water/hydrocarbon dew points.',
  'Corrected prover pulse factor, covariance-aware GUM propagation and RSS rounding; abbreviated orifice correlation is not fiscal ISO5167 implementation.',
  'Removed unsupported contractual/standards compliance claims and clarified flow-reference conditions.'],
 ['The literal gas-quality/dew-point/pipeline examples execute but do not each contain an independent numerical oracle or complete conservation audit. They remain illustrative calculations; gas specifications and custody-transfer uncertainty need contract-specific evidence.'],
 ['iso6976scope','jcgm100gum','sodir2023measurement','emerson2023valves']),
20:(
 'Equipment capacity metrics, physical dimensions, utilization and coupled bottlenecks',
 ['Corrected margin factors, surge denominator, head units, heat-transfer terminal approaches, flow coefficients and pipeline length units.',
  'Replaced arbitrary UA times 50K utilization with two solved clean/fouled heat-exchanger cases and explicit two-stream enthalpy closure.',
  'Added missing-equipment coverage rejection, corrected source-backed pipeline checks and removed unsupported universal debottlenecking percentages.',
  'Separated installed evidence, generated chart assumptions and nonlinear whole-process feasibility.'],
 ['Most remaining utilization snippets test API/report behavior rather than installed equipment capacity; no vendor map, certified relief sizing or separator carryover validation is supplied. Pipeline checks establish domain and mass only.'],
 ['neqsim2026update','emerson2023valves','api521scope']),
21:(
 'Debottlenecking API, enabled constraints, automatic sizing and economic comparisons',
 ['Corrected multiplicative automatic-size factors to 1.x and distinguished sizing heuristics from hydraulic re-rating.',
  'Corrected all31 Java fixtures/signatures; preset enablement and disabled checks do not increase physical feed capacity.',
  'Removed fabricated optimization statistics, clarified hypothetical economics, corrected profitability-index and currency/payback relationships.'],
 ['Java and Python fixtures establish API operation in declared sequential context. They do not qualify vendor equipment, a capital project or a globally feasible production increment.'],
 ['neqsim2026update']),
22:(
 'Optimization theory, KKT/globality, separator staging, gas lift and compression',
 ['Corrected BFGS minimization sign, convexity conditions, compressor staging assumptions and objective-unit consistency.',
  'Replaced invented gas-lift API with real NeqSim curves and an allocation checked by budget, marginals, direct objective replay and a 1000Sm3/day grid.',
  'Added separator material/enthalpy and compressor shaft-energy checks; corrected steady-state ratio and data-reconciliation interpretation.',
  'Removed unsupported performance claims and corrected the Nwachukwu primary reference.'],
 ['Gas-lift curves are declared algebraic performance models, not calibrated wells. Several remaining NODAL/Pareto/two-stage examples execute without their own full independent physical or optimum certificate. Local numerical success is not global proof.'],
 ['boyd2004convex','rockafellar2000cvar']),
23:(
 'Current NeqSim process architecture, automation, optimizer and strict evidence contracts',
 ['Updated ProcessAutomation.evaluate, ProductionOptimizer final-point replay and strict separator/pipeline/shared-resource coverage at the pinned source commit.',
  'Separated plant-capacity output from well-BHP VFP export, and generated compressor charts from installed maps.',
  'Corrected head units, source package/API names, feasibility acceptance and local-search claims.'],
 ['This chapter is primarily an API tutorial. Its successful fragments do not independently prove each returned optimizer point physically feasible. Accepted optimization and fresh replay are demonstrated explicitly in Chapter32 and the separate notebook benchmark.'],
 ['neqsim2026update','boyd2004convex']),
24:(
 'Production optimization implementation, capacity constraints and acceptance',
 ['Corrected objective signs, penalty scaling, hard/soft feasibility, bounds and final-state replay requirements.',
  'Corrected equipment geometry, pressure/flow units, gas valve assumptions, NPSH/UA/pipeline scope and automatic-size factors.',
  'Replaced false steady-state autocorrelation/Celsius CV claims with current ratio/slope behavior and signal-specific criteria.',
  'Separated interface examples, external integrations, rejected points and hypothetical economic comparisons.'],
 ['The many Java/Python interface demonstrations are executed configuration/API examples, not a separate physical acceptance certificate for each optimizer strategy. Historian, NLopt, plant calibration, flaring accounting and well adapters have explicit prerequisites.'],
 ['neqsim2026update','boyd2004convex','rockafellar2000cvar']),
25:(
 'Capacity surveillance, measurements, uncertainty and operating recommendations',
 ['Corrected utilization/margin denominators and distinguished calculated load, assumed limit and installed evidence.',
  'Removed unsupported field history, degradation and savings claims; marked thresholds and economics as assumed.',
  'Clarified history quality, consistency of units and effects of missing or disabled constraints.'],
 ['Monitoring fixtures verify data-access and reporting behavior; no live historian, sensor calibration, plant trend or installed equipment rating is validated.'],
 ['neqsim2026update','jcgm100gum']),
26:(
 'Well/network allocation, hydraulic boundaries and a verified reduced allocation problem',
 ['Corrected IPR/VFP pressure boundaries, volume-reference units, lift accounting and topology/solver interpretation.',
  'Replaced the central heuristic allocation with a six-well linear program, independent dual certificate and fresh NeqSim compression replay.',
  'Separated fixed-composition linear compression allocation from full hydraulic choke optimization and source-only integration adapters.'],
 ['The accepted LP uses fixed GOR/water cut/composition and linear power scaling verified over the stated model; it is not a calibrated reservoir-network optimum. Other network API examples have narrower checks.'],
 ['boyd2004convex','neqsim2026update','opmvfp']),
27:(
 'Scenarios, Monte Carlo, tornado sensitivity, robustness and resource economics',
 ['Replaced non-conserving/unbounded production forecasts with400 full NeqSim25-year isothermal depletion profiles, common stratified uncertain resource/price/CAPEX samples and explicit pre-tax cash flow.',
  'Rebuilt200-sample surface uncertainty and11-case OAT with normalized CPA water mole fraction, three-phase separation and per-unit/whole-process conservation.',
  'Eliminated silent failed-sample filtering; tornado endpoint labels are low/high inputs and span includes the base.',
  'Verified compressor efficiency has zero upstream gas-yield effect in the prescribed-rate model while changing power.',
  'Corrected CDF versus exceedance percentiles, CVaR loss convention, scenario confidence, EVPI/VSS and resource-balance scope.'],
 ['The reservoir is a pure-methane isothermal tank with a declared rate rule, not an IPR/well/network forecast. Sampled percentiles are not tail-confidence guarantees; no tax regime, field calibration, dependence model or mitigation value is established.'],
 ['rockafellar2000cvar','jcgm101mc','neqsim2026update']),
28:(
 'VFP construction, production-flow orientation and export contracts',
 ['Corrected BHP/WHP boundary semantics and the difference between well hydraulics and process maximum-flow curves.',
  'Documented current PipeBeggsAndBrills inverse pressure mode, outlet-setter ordering and pressure residual acceptance.',
  'Corrected water/GOR recombination bases, gravity/friction trends, nonmonotone production VFP behavior and software export metadata.',
  'Removed invented timing accuracy and automatic field-validity claims.'],
 ['Most literal Java/Python snippets demonstrate table configuration, diagnostic process capacity or export behavior. The accepted60-point upward-flow hydraulic calculation belongs to the separately checked companion notebook; it does not independently validate every literal diagnostic table. Field well-test validation is an explicit external-data pattern.'],
 ['opmvfp','neqsim2026update']),
29:(
 'Dynamic inventories, control, depressurization and protective-system scope',
 ['Replaced illustrative controller output presented as dynamics with native separator inventory transients and cumulative mass/internal-energy checks.',
  'Corrected level feedback sign, native fraction units, circular segment free-surface area and SIMC PI tuning equation.',
  'Added timestep-refined depressurization including explicitly budgeted1e-6kg/s regularization; distinguished gas temperature from wall/metal temperature.',
  'Separated steady recycle topology from antisurge protection and imposed feed pulse from resolved slug hydrodynamics; removed blanket API52115-minute claim.'],
 ['No wall thermal inertia, installed valve certificate, compressor map/surge dynamics, relief qualification or field controller validation. The blowdown has a quantified regularization inlet and coarser1e-3 energy tolerance; the companion notebook is separately an illustrative lumped controller.'],
 ['skogestad2003simc','api521scope','neqsim2026update']),
30:(
 'Digital-twin data contracts, model calibration, MPC, hybrid models and automation',
 ['Added local data-quality and steady-state fixtures that reject corrupt, missing, trending and oscillatory inputs.',
  'Corrected covariance-scaled anomaly score, data provenance, calibration uncertainty and native MPC scope.',
  'Corrected coupling at common physical junctions, input/output address contracts and save/restore limitations.',
  'Removed fabricated measured data/benefit claims and corrected primary NMPC/surrogate/informed-ML references.'],
 ['No live historian/OPC access, field-twin calibration, closed-loop plant control, trained model or predictive fault diagnosis. Synthetic tracking is a data-plumbing illustration.'],
 ['neqsim2026update','boyd2004convex','angelopoulos2022conformal']),
31:(
 'Flash, recycle, adjuster and numerical solver mathematics',
 ['Corrected fugacity iteration, Wegstein update, molar EOS basis, Rachford-Rice and phase-stability interpretations.',
  'Added phase-composition/fugacity and PH target checks, actual fresh-separator recycle with16 iterations and component/material/energy closure.',
  'Repaired adjuster callbacks and checked a reachable40C target through independent valve replay.',
  'Corrected native recycle tolerance units/cache behavior, column solver enum/acceptance distinctions and explicit/implicit time-integration claims.'],
 ['Column strategy and generic transient fragments need supplied consistent inventories/feed/boundaries. The accepted column example is in root-owned Chapter33. Tolerance attainment is numerical evidence, not experimental EOS validation.'],
 ['neqsim2026update','boyd2004convex']),
32:(
 'Advanced optimization, local calibration contracts, surrogate uncertainty and batch execution',
 ['Added a converged two-variable SciPy optimum using fresh full-process solves, independent feasible final replay and2121-point exhaustive grid bracket.',
  'Retained a rejected native candidate as a diagnostic instead of an accepted optimum.',
  'Added native steady-state ratio versus independent formula, linear reconciliation versus closed-form covariance oracle, and known-efficiency calibration with independent three-pressure replay.',
  'Corrected residual covariance, unit conversion boundaries, native API names, KKT/globality and ensemble/conformal coverage claims.',
  'Replaced invented parallel performance with compared sequential/two-worker fresh models.'],
 ['The grid brackets only the defined two-variable model and domain; it is not a general global certificate. Calibration observations are synthetic. ONNX, live historian, custom RL/plant adapters and physical surrogate certification remain external prerequisites.'],
 ['boyd2004convex','angelopoulos2022conformal','neqsim2026update']),
34:(
 'Integrated production examples with explicit process boundaries and generated sensitivities',
 ['Rebuilt platform topology with real cooler knockouts before compression, all product withdrawals and balanced nine-pressure sweep.',
  'Root rebuilt CPA FPSO with reference-volume water cut, fixed200m3/hr reference oil+water and304 unit/whole-process checks over base plus15 cases.',
  'Replaced one-sided exchanger/two-phase expander topology with explicit refrigeration, gas knockout and balanced NGL base/increased/nine-rate cases.',
  'Removed fabricated numerical tables/optima and corrected gross-revenue economics and heavy-oil claims.'],
 ['Defined synthetic feed recipes, assumed screening limits and external refrigeration duty; no full vendor plant rating, detailed heavy-oil characterization, gas-lift demand, water treatment specification or selected capital project. Expander and compressors are not asserted shaft-coupled.'],
 ['neqsim2026update','gpsa2016']),
35:(
 'Emissions, CO2, hydrogen, energy integration and prospective methods',
 ['Corrected carbon atom accounting, emission boundaries and double-counting, CO2 critical-state criteria and transport versus MMP claims.',
  'Corrected SMR/WGS/electrolysis stoichiometry and energy basis; mixed syngas conditioning is not hydrogen purification.',
  'Added actual native electrolyzer atom/current/power/thermal checks at unit Faradaic efficiency.',
  'Corrected ISO6976 Wobbe units, dry CO2 phase screening, storage chronology, implicit differentiation and ML physical-constraint claims.',
  'Updated sourced flare statistics and replaced promised technology gains/roadmaps with explicitly prospective discussion.'],
 ['Native electrolyzer example is deliberately restricted to Faradaic efficiency1; nonunit efficiency requires accounting for unreacted water not present in the current output topology. CO2 flash is not corrosion/transport/MMP qualification; no capture/PSA/reservoir physics is implied.'],
 ['nistco2properties','ivy2004electrolysis','worldbankflaring2024','worldbankflaring2026','iso6976scope'])
}

# Per-fence tested acceptance, with precise limits. Unmapped examples are not certified.
accepted={}
def add(n,ids,kind,description):
 for i in ids:accepted[(n,i)]=(kind,description)
add(20,[3],'accepted_reduced_physical_case','Two solved clean/fouled UA cases: each side mass1e-8 relative, hot/cold enthalpy closure1e-5 relative, positive terminal approaches and reduced duty on fouling.')
add(20,[5],'physical_domain_and_mass_check','Pipeline positive downstream pressure below80bara; outlet150000kg/hr within1e-5kg/hr. No complete energy or pressure-drop benchmark.')
add(20,[11],'software_evidence_contract','Deliberately incomplete equipment coverage must fail completeness and emit MISSING_EQUIPMENT; not a plant capacity validation.')
add(22,[2,3],'accepted_reduced_physical_case','Every called two-stage model checks total mass1e-8 relative, adiabatic enthalpy1e-6 and positive oil yield. The36-point follow-on sweep reuses the checked factory; an optimum is grid-only.')
add(22,[4],'accepted_reduced_allocation_case','Declared NeqSim gas-lift curves: bounds,150000Sm3/day total lift within0.1, objective replay1e-6, marginal equality1e-7 and1000Sm3/day enumeration gap under1 oil-rate unit.')
add(22,[5],'accepted_reduced_physical_case','Each compressor pressure case: mass1e-10 relative, shaft power versus enthalpy rise1e-5 relative and positive work.')
add(26,[8],'solver_convergence_check','Native network convergence flag asserted; not an independent nodal/component/energy acceptance audit.')
add(26,[14],'allocation_budget_check','Native gas-lift total respects2500000Sm3/day budget to1e-9 relative. No independent optimality certificate for this fragment.')
add(26,[17],'accepted_reduced_allocation_case','Six-well LP: bounds1e-8, primal capacity1e-6, nonnegative dual multipliers1e-10, dual inequalities1e-9, dual gap1e-5; fresh NeqSim power replay1e-4kW, mass1e-10 and enthalpy-power1e-5 relative.')
add(27,[4,5],'accepted_reduced_physical_case','CPA three-phase surface cases: per separator/compressor/whole process mass/components1e-7 and energy1e-5 relative, finite positive p/T and nonnegative flow, gas-only compressor inlet.200 LHS cases plus11 OAT cases. OAT verifies zero upstream gas response to efficiency within1e-6kg/hr and nonzero correctly signed power response.')
add(27,[8],'accepted_reduced_dynamic_resource_case','400 NeqSim isothermal tank profiles,25 annual steps each: initial GIP1e-8 relative, cumulative mass1e-9, positive inventory,49<P<=250bara, fixedT1e-8K,0<RF<1; finite pre-tax NPV. No adiabatic energy claim because temperature is imposed.')
add(29,[1],'accepted_reduced_dynamic_case','120s native separator with20–40s feed pulse; integrated mass1e-10, energy1e-5 relative, finite0<level<1. dt0.5/0.25s: level difference<0.001 fraction, pressure difference<0.01bar; final level within0.002 of setpoint.')
add(29,[2],'recycle_mass_and_sign_check','Steady recycle: product mass matches100000kg/hr to1e-4 relative and positive compressor power. This is not an antisurge dynamics or full energy acceptance.')
add(29,[3],'accepted_reduced_dynamic_case','120s80bara blowdown: mass1e-10, energy1e-3 relative; dt0.5/0.25s differences<0.05bar/<0.1C; monotone pressure decline; regularization inlet contribution<1ppm of initial inventory.')
add(29,[4],'accepted_reduced_dynamic_case','Imposed separator feed pulse: native mass1e-10, energy1e-5 relative and level<0.6. Uses the checked inventory integrator; not resolved pipeline slug hydrodynamics.')
add(30,[5,6],'accepted_local_data_contract','Synthetic in-memory data: preserve raw values and mask implausible/missing data; steady detector accepts stationary case and rejects drift, oscillation and missing windows. No historian/field observation used.')
add(31,[1],'accepted_thermodynamic_consistency_case','TP equilibrium phase composition reconstruction1e-7, phase x sums1e-8, fugacity log ratio1e-5; PH target1e-7 relative at50bara. These are solver identities, not external experimental validation.')
add(31,[3,4],'accepted_reduced_physical_case','Fresh separator per tear iteration: actual flow/T/composition changes1e-7; whole-process mass, component and energy1e-7 relative.16 iterations; diagnostic figure uses actual residuals.')
add(31,[5],'accepted_reduced_physical_case','Adjuster40C target with5–95bara bounds; fresh independent JT valve replay within1e-4C, flow within1e-5kg/hr and isenthalpy1e-6 relative.')
add(32,[4],'rejected_candidate_diagnostic','A feasibility assertion occurs only on the accepted branch; native nonconverged/infeasible output is retained as diagnostic teaching and is not a validated optimum.')
add(32,[7],'accepted_reduced_optimization_case','Fresh full process each objective/constraint: successful SLSQP, q50k–200k kg/hr/P40–80bara, final power<=3500.001kW, mass1e-10 and shaft-energy1e-5 relative; independent2121-case grid brackets optimum within1500.001kg/hr.')
add(32,[16],'accepted_synthetic_calibration_contract','Native R ratio versus independent formula1e-10; native linear reconciliation versus covariance solution1e-6 and conservation1e-6; fit converged and eta within0.002 of known0.78, fresh130/150/170bara replay<0.02K; mass1e-5kg/hr and energy1e-5 relative.')
add(32,[20],'batch_execution_check','Batch failure count equals zero. Does not alone prove physical validity or optimality of all batch cases.')
add(32,[21],'mathematical_optimizer_contract','Declared algebraic network objective agrees with analytic150000 optimum within1 unit; not a physical hydraulic network certificate.')
add(32,[25],'accepted_parallel_reproducibility_contract','Three fresh compressor models run serially and with two workers: equality rtol1e-10/atol1e-6kW, positive finite work and mass error<1e-6kg/hr. No claimed generic speedup.')
add(34,[1,2,3],'accepted_reduced_physical_case','Fresh platform factory and nine-pressure sweep: all products included, mass/components1e-7 and energy1e-5 relative, dry compressor inlets, positive compression work and rising discharge pressure.2 is a screening-ratio report, not installed rating.')
add(34,[4,5],'accepted_reduced_physical_case','Root-owned CPA water-cut factory: base plus15 cases,304 unit/whole-process checks. Reference15C1.01325bara WC within1e-7, total liquid200m3/hr within1e-4; mass1e-6, components1e-7, energy1e-5 relative and dry compressor feeds.')
add(34,[7,9],'accepted_reduced_physical_case','NGL two baseline rates and nine-case sweep: reused whole-boundary mass/components1e-7 and energy1e-5 relative, pre-expander/comp gas-only feeds, negative expander work and positive compressor power. Explicit refrigeration duty and independent shafts.')
add(34,[8],'accepted_arithmetic_contract','Assumed incremental saleable50MMscfd revenue at330days,0.001025MMBtu/scf and4USD/MMBtu equals67.65MUSD/year within1e-6USD. Gross revenue/CAPEX ratio is not net payback or a justified investment.')
add(35,[1],'accepted_reduced_physical_case','Flare independent atom-carbon versus native CO2 within1e-6kg/day, imposed20% split mass1e-6kg/hr and recovery compressor enthalpy-power1e-5 relative.')
add(35,[2],'thermodynamic_domain_and_composition_check','DryCO2-rich five-pressure flashes: positive finite density, phase-composition reconstruction1e-7, x sums1e-8. No transport safety or phase-envelope validation.')
add(35,[3],'thermodynamic_domain_and_composition_check','CO2/oil single-flash mixture positive density and composition sum1e-8. Does not determine multicontact MMP or recovery.')
add(35,[4],'accepted_reduced_physical_case','CPA syngas conditioning: total product mass1e-7, whole-flow enthalpy plus shaft/cooler duty1e-5 relative; H2 component mass below mixture mass and mixture purity<99%. No reformer/PSA/capture claimed.')
add(35,[5],'accepted_reduced_physical_case','Native electrolyzer at etaFaradaic1:2mol/sH2 and1mol/sO2, atom balances1e-9mol/s, electrical power2F V nH2 within1e-6W, reaction-plus-rejected-heat1e-3 relative and52<SEC<54kWh/kg.')
add(35,[6],'gas_quality_domain_and_trend_check','Eleven ISO6976 cases: finite positive Wobbe and decreasing density between0–20%H2. Numerical Wobbe is not separately experimentally benchmarked by this literal snippet.')

correction_files=['core','capacity','framework','theory','network','uncertainty','vfp',
                  'twin_solver','contracts','case','future','final_text','final_optimization']
correction_artifacts=[]
for stem in correction_files:
 p=V/(stem+'_corrections.json')
 if p.exists():
  d=json.loads(p.read_text(encoding='utf-8-sig'))
  entries=d if isinstance(d,list) else d.get('changes',d.get('corrections',[]))
  correction_artifacts.append({'path':str(p.relative_to(B)),'sha256':sha(p.read_bytes()),
                               'record_count':len(entries)})

E=V/'optimization_evidence';E.mkdir(exist_ok=True)
evidence=[]
for n in NUMBERS:
 folder=next((B/'.build/fence_runs').glob(f'ch{n:02d}_*'),None)
 if folder:
  for p in folder.glob(f'ch{n:02d}_*.json'):
   dest=E/p.name;shutil.copy2(p,dest)
   evidence.append({'chapter':n,'path':str(dest.relative_to(B)),
                    'source':str(p.relative_to(B)),'sha256':sha(dest.read_bytes()),
                    'kind':'literal_example_numerical_output'})
for name,n in [('ch34_fpso_physics.json',34),('ch29_dynamic_probe.json',29),
               ('ch29_blowdown_probe.json',29),('ch31_energy_probe.json',31),
               ('ch32_optimum_probe.json',32)]:
 p=V/name
 if p.exists():evidence.append({'chapter':n,'path':str(p.relative_to(B)),
                               'sha256':sha(p.read_bytes()),'kind':'supplementary_or_root_case_verification'})

ledger=json.loads((B/'verification/optimization_chapters_audit_summary.json').read_text(encoding='utf-8'))
bychap={x['chapter']:x for x in ledger['chapters']}
report={
 'generated_at':datetime.now(timezone.utc).isoformat(),
 'source_root':str(SOURCE),'source_commit':subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip(),
 'python_executable':sys.executable,'full_text_review':True,
 'review_scope':'All manuscript scientific prose, equations, examples, tables and figure claims in chapters19–32 and34–35; notebooks, Chapter33 and final rendered-release qualification are separate owners.',
 'review_method':'PaperLab scientific traceability audit + book adversarial review + NeqSim in writing; full-text reading with source checks, primary literature, literal-code execution and targeted independent balances/optimum/calibration checks.',
 'skills':['agents/book_adversarial_reviewer.paperlab.md','skills/paperlab_scientific_traceability_audit/SKILL.md','skills/neqsim_in_writing/SKILL.md'],
 'status':'reviewed_with_qualified_examples_and_explicit_remaining_gaps',
 'all_examples_independently_physically_validated':False,
 'chapters':[],'correction_artifacts':correction_artifacts,'numerical_evidence':evidence,
 'references_bib':str((V/'optimization_refs.bib').relative_to(B)),
 'reference_metadata_checks':[
  {'chapter':[22,30],'correction':'Nwachukwu et al.2018 JPSE163463–475, all four authors; original SPE title/pages were unsupported.',
   'primary_url':'https://snu.elsevierpure.com/en/publications/fast-evaluation-of-well-placements-in-heterogeneous-reservoir-mod/','doi':'10.1016/j.petrol.2018.01.019'},
  {'chapter':[30],'correction':'Willersrud/Imsland/Hauger/Kittilsen2011 IFAC44(1)10851–10856; corrected invented author/year/journal.',
   'primary_url':'https://skoge.folk.ntnu.no/prost/proceedings/ifac11-proceedings/data/html/papers/1216.pdf','doi':'10.3182/20110828-6-IT-1002.01216'},
  {'chapter':[30],'correction':'von Rueden informed-ML issue year2023 versus online2021.',
   'primary_url':'https://publica.fraunhofer.de/entities/publication/8dd37839-a5e4-4e70-bdaf-4d57e8720e2b','doi':'10.1109/TKDE.2021.3079836'},
  {'chapter':[32],'correction':'Schweidtmann/Huster/Lüthje/Mitsos2019 correct CCE title and pages12167–74.',
   'primary_url':'https://research.tudelft.nl/en/publications/deterministic-global-process-optimization-accurate-single-species/','doi':'10.1016/j.compchemeng.2018.10.007'}],
 'global_limitations':[
  'A successful literal execution is distinct from numerical conservation, an independent benchmark, experimental model validation and design compliance. Per-fence classifications enforce that distinction.',
  'Most API/configuration fragments intentionally exercise software contracts. Unmapped numerical demonstrations are explicitly unqualified; the presence of a central accepted example does not certify all other examples in its chapter.',
  'Examples share previous chapter definitions in a fresh JVM. Java fragments execute in a chapter-scoped JShell fixture; Java8 source compatibility was reviewed, but each fragment is not a separately compiled Java8 application.',
  'Assertions are recorded with code hashes; coverage is the exercised inputs and branches only. Assertions inside functions support acceptance only when the mapped example actually calls those functions.',
  'None of this review establishes installed equipment performance, contractual product acceptance, relief/safety-system adequacy, live historian accuracy, environmental permitting, fiscal advice or full-field reservoir calibration.',
  'The parent release owns legacy/generated quantitative asset replacement and104 notebook figure integrations. Whole-manuscript hashes may change through these audited editorial operations while executable-fence hashes remain fixed.',
  '89 benchmark comparisons, including18 independent NIST comparisons, belong to the separate notebook benchmark dossier; they are not89 independent experimental validations of each manuscript example.'
 ]}
proofs=proof_index()
totals=collections.Counter();unresolved=[];solution_gaps=[]
for n in NUMBERS:
 p=next((B/'chapters').glob(f'ch{n:02d}_*/chapter.md'));t=p.read_text(encoding='utf-8-sig')
 audit=bychap[p.parent.name];old={x['sha256']:x for x in audit['examples']}
 title,corrections,gaps,refs=reviews[n]
 corrections=corrections+ADDITIONAL_CORRECTIONS.get(n,[])
 gaps=UPDATED_LIMITATIONS.get(n,gaps)
 row={'chapter':p.parent.name,'number':n,'full_text_review':True,'source_sha256':sha(p.read_bytes()),
      'reviewed_characters':len(t),'scientific_focus':title,'corrections':corrections,
      'citations_reviewed':refs,'limitations':gaps,'entries':[]}
 for i,m in enumerate(PAT.finditer(t),1):
  language,annotation,code=m.groups();digest=sha(code.encode());a=old.get(digest,{})
  headings=list(re.finditer(r'^#{2,4} (.*)',t[:m.start()],re.M));heading=headings[-1].group(1) if headings else ''
  assertions=[]
  if language=='python':
   assertions=[ast.unparse(x.test) for x in ast.walk(ast.parse(code)) if isinstance(x,ast.Assert)]
  status=a.get('status','stale_or_missing')
  proof=proofs.get((n,digest))
  kind=inventory_kind(n,i,language,digest,proofs)
  if 'pattern' in annotation:
   classification='declared_external_pattern';scope='Not executed; requires the explicitly annotated adapter/data/model/environment.'
  elif kind=='numerical' and proof:
   classification='solution_verified_numerical'
   scope=proof.get('scope') or 'Exact-source numerical/physical/identity checks detailed in the linked supplementary report.'
  elif kind=='numerical' and (n,i) in accepted and status=='passed' and assertions:
   classification='solution_verified_numerical';scope=accepted[n,i][1]
  elif kind=='software_API_config/reporting':
   classification=kind
   scope='Reviewed definition/configuration/serialization or reporting of previously computed values in the documented sequential fixture; no independent installed-equipment claim.'
  else:
   classification='unresolved_solution_verification'
   scope='An explicit current passing numerical proof or complete reviewed inventory is still required.'
   solution_gaps.append({'chapter':n,'fence':i,'language':language,'inventory':kind,'sha256':digest})
  prerequisites=annotation.strip() if 'pattern' in annotation else (
    'Pinned source target/classes and devtools bootstrap; book-local dependencies; earlier runnable Python fences in this chapter.' if language=='python' else
    'Pinned source classpath, chapter Java fixture/imports/logger and earlier Java fragments; source-compatible Java8 syntax.')
  engineering={'acceptance_scope':scope,'assertions_in_literal_code':assertions,
               'verified_hash':digest if classification=='solution_verified_numerical' else None,
               'execution_report':a.get('execution_report'),
               'case_records':[x for x in evidence if x['chapter']==n] if (n,i) in accepted else [],
               'qualification':'solution_verified_for_declared_model_and_tested_conditions' if classification=='solution_verified_numerical' else 'software_contract_or_external_scope'}
  if proof:
   engineering['solution_report']=proof['report_path'];engineering['solution_report_sha256']=proof['report_sha256']
   engineering['checks']=proof['checks'];engineering['solution_check_kind']=proof.get('solution_check_kind')
  elif classification=='solution_verified_numerical':
   engineering['evidence_type']='Executed exact-literal assertion contract with reviewed exercised factory/case prerequisites'
   engineering['solution_report']=a.get('execution_report')
  entry={'number':i,'language':language,'line':t.count('\n',0,m.start())+1,'heading':heading,
         'code_sha256':digest,'sha256':digest,'classification':classification,'status':status,
         'engineering_evidence':engineering,'prerequisites':prerequisites}
  row['entries'].append(entry);totals[classification]+=1
  if status not in ['passed','integration_pattern']:unresolved.append({'chapter':n,'fence':i,'status':status})
 row['execution_counts']=dict(collections.Counter(e['status'] for e in row['entries']))
 row['classification_counts']=dict(collections.Counter(e['classification'] for e in row['entries']))
 report['chapters'].append(row)
report['totals']={'chapters':len(report['chapters']),'literal_fences':sum(len(c['entries']) for c in report['chapters']),
                  'classifications':dict(totals),'execution':dict(collections.Counter(
                      e['status'] for c in report['chapters'] for e in c['entries'])),
                  'correction_records_in_saved_artifacts':sum(a['record_count'] for a in correction_artifacts)}
report['unresolved_execution']=unresolved
report['all_runnable_literal_hashes_current_and_passed']=not unresolved
report['unresolved_solution_verification']=solution_gaps
report['numerical_coverage_complete']=not solution_gaps and not unresolved
report['all_examples_independently_physically_validated']=False
report['solution_verification_levels']={'numerical_solution':'balances, identities, dimensions, domains, feasibility, replay, convergence or analytical/grid optimum checks appropriate to each case',
 'independent_model_validation':'separate benchmark dossier; not established universally by solution checks',
 'field_validation':'no universal field calibration, installed rating or compliance certification'}
report['status']='complete_solution_verification_with_explicit_model_limits' if report['numerical_coverage_complete'] else 'solution_verification_in_progress'
report['global_limitations'][1]='Definitions, configuration and reporting are explicitly inventoried separately from numerical calculations. Every numerical calculation requires its own exact-source passing solution proof; rejected native candidates remain diagnostics and are not accepted designs.'
(V/'optimization_review.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
lines=['# Scientific review: optimization chapters','',
 'All16 assigned chapters were read and scientifically revised. Every numerical case is explicitly inventoried and linked to its current solution-verification evidence. Software/configuration/reporting and external patterns have separate scopes. **Solution verification does not establish universal experimental or field-model validity.** Rejected native candidates are retained as diagnostics.','',
 f'Numerical coverage complete: **{report["numerical_coverage_complete"]}**. Unresolved solution cases: `{len(solution_gaps)}`.','',
 f'Pinned NeqSim source: `{report["source_commit"]}`. Current executable-hash gate: **{not unresolved}**.','',
 f'Execution counts: `{json.dumps(report["totals"]["execution"])}`; `{report["totals"]["literal_fences"]}` literal Python/Java fences in16 chapters.','',
 '## Chapter review coverage','',
 '| Chapter | Scientific focus | Executed | Patterns | Explicitly mapped checks |',
 '|---|---|---:|---:|---:|']
for c in report['chapters']:
 mapped=sum(e['classification']=='solution_verified_numerical' for e in c['entries'])
 lines.append(f'| {c["number"]} | {c["scientific_focus"]} | {c["execution_counts"].get("passed",0)} | {c["execution_counts"].get("integration_pattern",0)} | {mapped} |')
for c in report['chapters']:
 lines+=['',f'## Chapter{c["number"]}: {c["scientific_focus"]}','',
         f'Source SHA256: `{c["source_sha256"]}`. Full text reviewed: yes.','']
 lines += ['- '+x for x in c['corrections']]
 lines += ['', '**Acceptance and limitations.** '+ ' '.join(c['limitations']),'',
           '| Fence | Language | Execution | Scientific classification | Exact code SHA256 |',
           '|---:|---|---|---|---|']
 for e in c['entries']:
  lines.append(f'| {e["number"]} | {e["language"]} | {e["status"]} | {e["classification"]} | `{e["code_sha256"]}` |')
 for e in c['entries']:
  if (c['number'],e['number']) in accepted:
   lines+=['',f'- Fence{e["number"]}: {e["engineering_evidence"]["acceptance_scope"]}']
lines+=['','## Global qualification limits','']+['- '+x for x in report['global_limitations']]
lines+=['','## Reproducibility','',
 'Run `devtools/summarize_optimization_verification.py` to refresh the exact-code execution gate, then run `devtools/summarize_optimization_scientific_review.py` with the selected bundled Python runtime. The latter copies current literal numerical records into `verification/scientific_revision/optimization_evidence/` and writes this report plus the complete machine-readable per-fence ledger. It never reruns simulations or infers physical acceptance from execution alone.','',
 'Primary references requested for the book are in `optimization_refs.bib`; exact metadata corrections and primary-source URLs are recorded in the JSON. The root release combines these with its bibliographic audit and source index.','']
(V/'optimization_review.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(report['totals'],indent=2));print('Unresolved execution:',unresolved);print('Unresolved solution:',solution_gaps)
