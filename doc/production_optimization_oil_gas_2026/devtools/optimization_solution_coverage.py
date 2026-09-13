"""Manual scientific-scope inventory; evidence is matched by literal SHA256."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1];V=B/'verification/scientific_revision'

# Reviewed computational cases, independently of syntax such as .run().
NUMERICAL={
19:set(range(1,9)),20:set(range(1,11)),21:{25,28,29,30,31,32,36,39},22:set(range(1,10)),
23:{1,3,10,15,16,22,23,25,27,28,31,35,37,39},
24:{2,5,12,13,14,16,17,18,22,23,24,33,34,40,41,42,43,44,59,61,62,63,64,65,69,72,73,74,75,80},
25:{1,4,5,9,10,11,12,13,14,15,17},26:{2,4,5,6,8,11,12,13,14,15,16,17},
27:{1,2,4,5,6,8},28:{3,4,5,10,11,12,13,17,18,20,21,22,23},
29:{1,2,3,4,5,6,7,9,13},30:{5,6,9,13,14,18,19,20,21,24,28},
31:{1,2,3,4,5},32:{1,2,3,4,5,6,7,9,10,12,13,14,15,16,17,20,21,22,24,25},
34:{1,2,3,4,5,7,8,9},35:set(range(1,7))}

# Explicit API/input-definition/reporting inventory, not an automatic fallback.
SOFTWARE={19:set(),20:{11},21:set(),22:set(),
23:{2,4,5,6,7,8,9,11,12,13,14,17,18,19,20,21,24,26,29,30,32,33,34,36,38},
24:{1,3,4,6,7,8,9,10,11,15,19,20,21,25,26,27,28,29,30,31,32,35,36,37,38,39,45,46,47,48,49,50,51,52,53,54,55,56,57,58,79,81,82},
25:{2,6,7,8,16},26:{1,9},27:{3,7},28:{2,6,7,8,9,16},
29:{8,10,11,12},30:{1,10,11,12,15,16,17,25,26,27,29},31:set(),
32:{11,18,19},34:set(),35:set()}

def passed_checks(checks):
 if not checks:return False
 def walk(x):
  if isinstance(x,dict):
   if x.get('passed') is False or x.get('pass') is False:return False
   return all(walk(v) for k,v in x.items() if k not in ['rejected_candidates','rejection_diagnostic','diagnostics'])
  if isinstance(x,list):return all(walk(v) for v in x)
  return True
 return walk(checks)

def proof_index():
 index={}
 for n in NUMERICAL:
  for suffix in ['solution_checks','java_solution_checks']:
   p=V/f'ch{n:02d}_{suffix}.json'
   if not p.exists():continue
   r=json.loads(p.read_text(encoding='utf-8-sig'))
   good=r.get('all_targeted_checks_passed') is True or r.get('status') in ['pass','passed']
   if not good:continue
   for e in r.get('entries',[]):
    digest=e.get('code_sha256',e.get('sha256'))
    if not digest or e.get('status') not in ['pass','passed'] or not passed_checks(e.get('checks')):continue
    index[n,digest]={'report_path':str(p.relative_to(B)),'report_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
      'verified_hash':digest,'checks':e['checks'],'source_classification':e.get('classification'),
      'solution_check_kind':e.get('solution_check_kind'),'scope':e.get('scope',r.get('scope',r.get('interpretation')))}
 return index

def inventory_kind(n,i,language,digest,proofs):
 # Java21 specialist reviewed its31 Java fragments individually (indices are Java-only).
 if n==21 and language=='java':
  proof=proofs.get((n,digest))
  if proof:
   return 'software_API_config/reporting' if proof['source_classification']=='API_configuration_or_reporting_contract' else 'numerical'
  return 'unresolved_inventory'
 if i in NUMERICAL[n]:return 'numerical'
 if i in SOFTWARE[n]:return 'software_API_config/reporting'
 return 'unresolved_inventory'

ADDITIONAL_CORRECTIONS={
19:['Every literal property case now has specific checks: same-basis ISO6976 identities, eight CPA water-dewpoint onset brackets, phase-envelope terminal-slot handling and pipeline conservation/domain.'],
20:['Corrected polytropic mode and fixed-reference-volume water cut; replaced invalid API relief expression with a dimensionally checked ideal-gas nozzle illustration; verified all10 calculations and one coverage contract.'],
21:['Additional root/specialist solution gates cover all8 Python and31 Java fences, including percentage units, fresh final-state replay,51-point grids, explicit disabled-chart sentinels and5 assumed economics cases.'],
22:['Replaced incorrectly oriented nodal calculation with forward upward hydraulics and a checked intersection; replayed intermediate compression and Pareto dominance at every sampled point.'],
23:['Capacity-engine native candidates are checked after replay; rejected points are retained alongside independently feasible bounded grids. Corrected minimum-outlet requirement versus actual compressor setter, disabled-chart sentinel labeling and head/power units.'],
24:['Supplementary checks cover every executed process solve, Pareto replay and weighted reconciliation; explicit polytropic mode and percent-to-fraction conversion fixed. Added real80km pipeline and axial mesh comparison, independent capacity grid, and32 attempted pressure states with30 accepted/two explicitly rejected trace-phase balance failures. Economics no longer converts masked total-feed gain into oil sales. Final figure review also rejected liquid Sm3/day as stock-tank volume: Java/Python upstream oil objectives now use kg/hr, while28 stock-tank flashes price only actual oil-phase volume at15C/1.01325bara with material/density/heat identities.'],
25:['Fixed native percent/fraction boundary in every monitoring path, with independent readback and trend/rule checks. Corrected CPA water handling and connected cooler/knockout/compressor topology.'],
26:['Verified pressure-boundary network junction balance and corrected kg/hr readback. Native tabulated lift candidate misses the accepted7050Sm3/day segment-LP optimum; this numerical rejection is retained explicitly.'],
27:['Additional checks verify all five scenario process boundaries, scenario probability normalization, algebraic quantile identities and parallel toy serialization.'],
28:['Specialist verifies each literal recombination/table/root/contract case; corrected third recombination argument to standard total liquid Sm3/hr and checks realized GOR/water cut.'],
29:['Supplementary steady recycle now uses explicit polytropic mode, tighter recycle tolerance and whole-process enthalpy/material checks. Java measurement readbacks verified against direct stream values.'],
30:['Supplementary process, batch tracking and synthetic comparison checks preserve Celsius absolute deviations; no percent-of-Celsius error or invented measured data. Java state fixtures use explicit polytropic mode.'],
32:['Added independent25-point Pareto trade-off grid, fresh12-case batch replay, full-model surrogate acceptance, dimensionally checked daily economics and scaled gas-lift SLSQP matching an independent KKT optimum within0.01bbl/day.'],
35:['All11 hydrogen-blend Wobbe outputs now satisfy an independently recomputed same-basis calorific-value/relative-density identity.']}

UPDATED_LIMITATIONS={
19:['Solution checks establish the declared property identities, phase boundaries and pipeline budgets. Contract acceptance, installed metering calibration and fiscal uncertainty still require independent site evidence.'],
20:['Computed capacity/dimension/energy examples and the coverage contract have explicit solution checks. No supplied vendor map, separator carryover test or certified relief calculation establishes installed capacity.'],
21:['All literal numerical/API cases have specific solution or software checks. Preset names, masking and auto-sizing remain assumptions; they do not qualify installed equipment or an investment.'],
22:['Numerical intersection, balances, optimum logic and dominance are checked in the stated examples. Declared gas-lift curves and model compositions are not calibrated field performance.'],
23:['Native source-engine failures are rejected and accompanied by independently accepted sampled candidates. Finite grids certify only sampled states; generated charts and strategy limits are not installed equipment evidence.'],
24:['Two of32 pressure states fail the strict1ppm material gate and remain explicit rejected candidates; selection uses30 accepted states. Capacity grids are sampled comparisons, not global certificates. Pipeline mesh/domain checks do not independently validate its thermal correlation. External historian/NLopt/plant adapters remain declared patterns.'],
25:['Local process equations, percentage conversions, trends and dashboard logic are checked; live historian measurements, field calibration and installed limits are not supplied.'],
28:['Literal pressure/recombination/constraint/contract results have explicit solution checks. Diagnostic process capacity is not production-well BHP, and field well-test calibration remains external.']}
