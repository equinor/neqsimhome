"""Publish three full-view reviewed, array-linked figures; preserve all old assets."""
from pathlib import Path
import hashlib,json,re,shutil
B=Path(__file__).resolve().parents[1];V=B/'verification/scientific_revision'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
array_path=V/'additional_literal_figure_arrays.json';array_report=json.loads(array_path.read_text())
assert array_report['status']=='passed'
prior_path=V/'literal_figure_copies.json';prior_bytes=prior_path.read_bytes();prior=json.loads(prior_bytes)
preserved=[]
for entry in prior:
 assert sha(entry['path'])==entry['sha256'],entry['path']
 preserved.append({'path':entry['path'],'sha256':entry['sha256'],'status':'unchanged_existing_review_retained'})
definitions=[
 (24,62,'sep_pressure_optimization.png','ch24_stock_tank_pressure_sweep.png',
  'Stock-tank oil and a limited product-value screen across 28 separator pressures at 250,000 kg/h feed.',
  'The 28 actual flashes retain all gas, oil and any aqueous products at 15 °C and 1.01325 bara. Stock-tank oil spans 2192.7–2318.8 m³/day, with its sampled maximum at 55 bara; oil density is 677.886–678.983 kg/m³. The assumed product value less compressor electricity peaks at 45 bara and 2294.38 kUSD/day. Mass/component residuals are below 3×10⁻¹¹. Conditioning cooling of 1.21–1.91 MW is recorded but not priced, and flash gas has no sales credit. The different maxima reflect liquid partition, gas value and compression work. This is a 28-point sensitivity with assumed prices and heating value; it does not establish installed capacity, product qualification or a global operating optimum.',
  'Full image inspected: all four panels and axes visible; actual reference-state liquid units, sampled 45.0 bara marker and limited-economic-scope labels match the saved arrays.'),
 (30,19,'ch21_digital_twin_tracking.png','ch30_literal_input_propagation.png',
  'A 24-hour synthetic input sequence propagated through the source-backed process model.',
  'Feed varies from 95 to 105 t/h, with synthetic temperatures 54.26–64.74 °C and pressures 49.02–50.93 bara. The model compressor requires 3.739–4.321 MW. Separator gas temperature overlays its prescribed feed temperature because this equilibrium separator imposes no temperature change; the matching curves are not independent sensor validation. The case checks automation input propagation and process balances. Field use still requires measured observations and separate calibration.',
  'Full image inspected: three readable panels, 24 points, explicit synthetic-temperature legend, t/h and MW units; no plant measurements or injected 3 K offset are claimed.'),
 (32,2,'pareto_front.png','ch32_literal_pareto_grid.png',
  'Twenty-five independently solved rate cases compared with the native weighted-search sample.',
  'At fixed 50→150 bara compression and 40 °C suction, the independent grid spans 50,000–200,000 kg/h and 3250.84–13003.37 kW. Its monotonic linear trade-off has no unique knee or preferred throughput without a capacity or economic criterion. The native weighted search returns one endpoint near 200,000 kg/h, which agrees with the independently solved grid. Each grid point passes mass and shaft-work/enthalpy checks; this comparison establishes the sampled model trade-off, not a vendor-map or field validation.',
  'Full image inspected: 25 grid samples and one native endpoint are visible, legend distinguishes both sources, axes carry kg/h and kW, and title correctly says sampled non-dominated states.')]
images=[]
for n,i,filename,destname,caption,discussion,view in definitions:
 c=next((B/'chapters').glob(f'ch{n:02d}_*'));src=B/'.build/solution_runs'/c.name/'figures'/filename;dest=c/'figures'/destname
 fences=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',(c/'chapter.md').read_text(encoding='utf-8-sig'),re.M|re.S))
 digest=hashlib.sha256(fences[i-1][3].encode()).hexdigest()
 proof_path=V/f'ch{n:02d}_solution_checks.json';proof=json.loads(proof_path.read_text())
 exact=next(e for e in proof['entries'] if e['number']==i)
 assert exact['sha256']==digest and exact['status']=='passed'
 if n==24:
  values=B/'.build/solution_runs'/c.name/'stock_tank_pressure_sweep.json';r=json.loads(values.read_text())
  assert len(r['stock_tank_flashes'])==28 and r['pressure_bara'][r['best_grid_index']]==45.
  assert max(t['mass_relative_error'] for t in r['stock_tank_flashes'])<1e-6
 else:
  values=array_path;r=next(e for e in array_report['entries'] if e['fence']==i and e['chapter']==c.name)
  assert r['code_sha256']==digest and r['source_sha256']==sha(src)
 if dest.exists():assert sha(dest)==sha(src),'Preserve a different old asset instead of overwriting it'
 shutil.copy2(src,dest)
 images.append({'path':str(dest),'sha256':sha(dest),'source':str(src),'source_sha256':sha(src),
   'chapter':c.name,'fence':i,'code_sha256':digest,'status':'passed','full_view_inspected':True,
   'full_view_evidence':view,'source_arrays':str(values),'source_arrays_sha256':sha(values),
   'solution_report':str(proof_path),'solution_report_sha256':sha(proof_path),
   'caption':caption,'discussion':discussion})
unselected=[]
for n,name,reason in [(24,'facility_optimization_results.png','Retained as generated supplementary output only. Updated labels distinguish the returned native candidate from an optimum and explicitly state that there is no independently accepted convergence history.'),
 (24,'optimization_convergence.png','Native search diagnostic descends to a lower-bound candidate; it is not proof of a production maximum and duplicates the chapter acceptance discussion.'),
 (24,'pareto_front.png','Sparse native sampled states without an independently dense comparison; the new Chapter 32 figure is more informative.'),
 (32,'batch_study_contours.png','Twelve solved cases have valid numerical checks, but the x-axis labels are crowded and existing sweep figures cover this case. Not selected for publication.')]:
 c=next((B/'chapters').glob(f'ch{n:02d}_*'));p=B/'.build/solution_runs'/c.name/'figures'/name
 unselected.append({'source':str(p),'source_sha256':sha(p),'status':'not_selected_for_publication','reason':reason,'approved_as_release_figure':False})
assert prior_path.read_bytes()==prior_bytes
report={'status':'passed','scope':'Three new selected scientific literal figures only; unselected or rejected assets are excluded from approval.',
 'images':images,'unchanged_prior_reviewed_images':preserved,
 'prior_eight_image_ledger':str(prior_path),'prior_eight_image_ledger_sha256':sha(prior_path),
 'unselected_outputs':unselected,'rejected_basis_archive':str(V/'rejected_gas_equivalent_oil_basis/rejection.json')}
(V/'additional_scientific_literal_figure_review.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
(V/'additional_scientific_literal_figure_review.md').write_text('\n\n'.join(['# Additional scientific literal figure review','Status: passed for the three selected images.']+[f"## {r['chapter']}\n\n{r['caption']}\n\n{r['discussion']}\n\nVisual review: {r['full_view_evidence']}\n\nImage SHA256: {r['sha256']}\n\nLiteral SHA256: {r['code_sha256']}" for r in images]+['The existing eight-image review and all repaired legacy image bytes were preserved. Unselected native diagnostics are explicitly excluded from the publication approval. The incorrect gas-equivalent oil economic figure and prior source/report were archived as rejected evidence.']),encoding='utf-8')
print('Three selected literal figures copied and linked; eight prior reviewed hashes unchanged')
