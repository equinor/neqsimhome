"""Evidence ledger for the reviewing agent's actual eight-image inspection.

Only writes review artifacts. --final is used after the corrected eighth image
has actually been displayed and inspected; it does not automate visual review.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import sys

HERE=Path(__file__).resolve().parent
BOOK=HERE.parents[1]
sys.path.insert(0,str(BOOK/'.build/python_packages'))
import numpy as np
from PIL import Image

FINAL='--final' in sys.argv
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))
manifest_path=HERE/'literal_figure_copies.json'
records=read(manifest_path)
assert len(records)==8
initial_path=HERE/'literal_figure_initial_inspection.json'
if not initial_path.exists():
    initial_path.write_text(json.dumps({'inspected_at':datetime.now(timezone.utc).isoformat(),'method':'Visual inspection by the reviewing agent of all eight actual images at original resolution; displayed water-cut image was resized by the tool from 1980x1381 to 1881x1312, with all labels readable.','images':records},indent=2),encoding='utf-8')
initial=read(initial_path)
details=[{} for _ in records]
evidence=[[] for _ in records]
def load_case(index,relative):
    p=BOOK/relative
    evidence[index-1].append({'path':str(p),'sha256':sha(p)})
    return read(p)

tornado=load_case(1,'.build/fence_runs/ch27_multi_scenario_optimization/ch27_surface_tornado.json')
base=tornado['base']['gas_production_kg_hr']; rows=tornado['rows']
for row in rows:
    for side in ('low','high'):
        assert abs(row[side]-(row[side+'_case']['gas_production_kg_hr']-base))<1e-9
eff=next(r for r in rows if r['label'].startswith('Isentropic'))
assert eff['low']==eff['high']==0
details[0]={'base_gas_kg_hr':base,'ranked_swings_kg_hr':[[r['label'],r['swing']] for r in rows], 'reconciliation':'All ten endpoint-minus-base gas rates agree with plotted deltas to 1e-9 kg/h; compressor efficiency has exactly zero upstream gas response.'}

npv=load_case(2,'.build/fence_runs/ch27_multi_scenario_optimization/ch27_depletion_monte_carlo.json')
for name, rows in npv['samples'].items():
    values=np.array([r['npv_MNOK'] for r in rows]); assert len(values)==200 and np.isfinite(values).all()
    expected=npv['summary'][name]['npv_cdf_P10_P50_P90_MNOK']
    assert np.max(abs(np.percentile(values,[10,50,90])-expected))<1e-8
    details[1][name]={'sample_count':len(values),'npv_min_max_MNOK':[float(min(values)),float(max(values))],'npv_CDF_P10_P50_P90_MNOK':expected}

for index,case,columns,tolerances in [(3,'inventory',[1,2],[.001,.01]),(4,'blowdown',[1,2],[.05,.1])]:
    item=load_case(index,f'.build/fence_runs/ch29_dynamic_simulation_and_control/ch29_{case}_checks.json')
    fine=np.array(item['fine']['series']); coarse=np.array(item['coarse']['series'])
    assert np.max(abs(fine[1::2,0]-coarse[:,0]))<1e-12
    errors=np.max(abs(fine[1::2,columns]-coarse[:,columns]),axis=0)
    assert np.all(errors<np.array(tolerances))
    details[index-1]={'fine_final_series_row':fine[-1].tolist(),'coarse_fine_aligned_max_differences':errors.tolist(),'difference_acceptance_limits':tolerances,'fine_max_mass_relative_residual':item['fine']['max_mass_relative_residual'],'fine_max_energy_relative_residual':item['fine']['max_energy_relative_residual']}
    if index==3:
        assert abs(fine[-1,1]-.5)<.002
        details[index-1]['level_peak_fraction']=float(max(fine[:,1]))
        details[index-1]['level_final_offset_percentage_points']=float(100*(fine[-1,1]-.5))
    else:
        assert np.all(np.diff(fine[:,1])<0) and np.all(np.diff(fine[:,2])<0)

fences=load_case(5,'verification/ch29_dynamic_simulation_and_control_fences.json')
pulse=next(x for x in fences['examples'] if 'Peak level fraction:' in x.get('output',''))
peak=float(re.search(r'Peak level fraction:\s*([\d.]+)',pulse['output']).group(1)); assert peak<.60 and pulse['status']=='passed'
details[4]={'reported_peak_level_fraction':peak,'declared_test_limit_fraction':.60,'margin_below_test_limit_fraction':.60-peak,'literal_code_sha256':pulse['sha256'],'scope':'Prescribed total-feed pulse, not a predicted slug-arrival model; retained scalar output and plot inspected, no complete pulse series was retained in this evidence file.'}

platform=load_case(6,'.build/fence_runs/ch34_case_studies/ch34_platform_sweep.json')
best=max(platform,key=lambda r:r['total_liquid_kghr'])
assert len(platform)==9 and best['hp_bara']==85 and all(r['screen_feasible'] for r in platform)
assert np.all(np.diff([r['power_MW'] for r in platform])<0)
details[5]={'pressure_range_bara':[platform[0]['hp_bara'],platform[-1]['hp_bara']],'sampled_max_liquid_t_hr':best['total_liquid_kghr']/1000,'pressure_at_sampled_max_bara':best['hp_bara'],'power_first_last_MW':[platform[0]['power_MW'],platform[-1]['power_MW']],'scope':'All withdrawn liquid is aggregated by mass; the sampled maximum is not an economic optimum or stock-tank volume.'}

fpso=load_case(7,'verification/scientific_revision/ch34_fpso_physics.json')['sweep']
assert len(fpso)==15
assert np.all(np.diff([r['water_cut_pct'] for r in fpso])>0)
assert max(abs(r['sep1_liquid_util_pct']-100*r['sep1_actual_liquid_m3hr']/400) for r in fpso)<1e-10
details[6]={'water_cut_first_last_pct':[fpso[0]['water_cut_pct'],fpso[-1]['water_cut_pct']],'oil_first_last_m3_hr':[fpso[0]['oil_rate_m3hr'],fpso[-1]['oil_rate_m3hr']],'water_first_last_m3_hr':[fpso[0]['sep1_water_m3hr'],fpso[-1]['sep1_water_m3hr']],'compression_first_last_MW':[fpso[0]['compression_MW'],fpso[-1]['compression_MW']],'first_separator_liquid_utilization_first_last_pct':[fpso[0]['sep1_liquid_util_pct'],fpso[-1]['sep1_liquid_util_pct']],'scope':'Feed water cut uses 15 C/1.01325 bara reference liquid; displayed final oil and first-separator water are separate local-state volumes, not a common product-volume balance.'}

ngl=load_case(8,'.build/fence_runs/ch34_case_studies/ch34_ngl_sweep.json')
assert len(ngl)==9 and not ngl[-1]['screen_feasible'] and all(r['screen_feasible'] for r in ngl[:-1])
assert ngl[-1]['screen_utilization']['expander_MW']>1
details[7]={'feed_percent_first_last':[100*ngl[0]['multiplier'],100*ngl[-1]['multiplier']],'liquids_first_last_t_hr':[ngl[0]['liquid_kghr']/1000,ngl[-1]['liquid_kghr']/1000],'utilization_last_pct':{k:100*v for k,v in ngl[-1]['screen_utilization'].items()},'scope':'130% feed case exceeds the declared expander-power screen; plotted rejected point is intentionally retained. These three screens are not a complete plant rating.'}

observations=[
 'Labels distinguish kg/h gas-rate response from water mole fraction, pressure, temperature and efficiency inputs. Low/high colors mean input endpoints, not unfavorable/favorable outcomes. Zero efficiency response is physically appropriate and explained in the caption. Bars agree with retained endpoint calculations.',
 'Histogram counts and empirical CDF have distinct y axes; both use pre-tax NPV in MNOK. Both 200-scenario policies are named consistently. Aggressive has a higher median and upper tail in these samples, while no universal dominance, investment guarantee or robust optimum is claimed.',
 'Level/diameter is dimensionless; pressure is bara; liquid withdrawal is kg/s; time is seconds. Solid and dashed timestep curves are nearly coincident. Small staircase features in the level signal are visible rather than cosmetically smoothed. The final 30.639 bara pressure and near-setpoint level agree with prose.',
 'Both absolute pressure and Celsius fluid temperature decline over 120 s. Fine/coarse trajectories overlap, consistent with the saved timestep comparison. The final 52.975 bara and 9.119 C agree with prose; the caption does not imply wall-temperature or relief-system qualification.',
 'A 20–40 s prescribed total-feed pulse raises the dimensionless level to about 0.5112, below the displayed 0.60 test limit, then returns toward 0.50. Legend and text distinguish the stress-test feed history from predicted slug generation. No trace is clipped or hidden.',
 'Both panels are readable and use bara, tonnes/h and MW consistently. Liquid mass has a shallow sampled maximum near 85 bara while compression power falls with pressure. Surrounding text correctly distinguishes process consistency from installed capacity and economic optimization.',
 'Four panels identify the reference conditions for feed water cut and keep local-state product volumes separate. Oil/gas/power decrease as water replaces hydrocarbon at fixed reference liquid rate. The first-separator utilization remains well below the explicitly assumed 400 m3/h limit; no false water-cut bottleneck appears.',
 'Both panels show all nine feed-rate points, including the 130% point above the expander screen. The right panel reports total withdrawn liquid mass in tonnes/h. Corrected reader-facing legend names the three screening quantities and the feed-reference label has proper spaces.'
]
items=[]
for index,r in enumerate(records,1):
    p=Path(r['path']); source=Path(r['source']); actual=sha(p)
    assert actual==r['sha256']==sha(source)
    chapter=BOOK/'chapters'/r['chapter']/'chapter.md'
    text=chapter.read_text(encoding='utf-8'); lines=text.splitlines()
    matches=[(i,line) for i,line in enumerate(lines) if line.startswith('![') and p.name in line]
    assert len(matches)==1
    i,caption_line=matches[0]
    caption=caption_line.split('](',1)[0][2:]
    excerpt='\n'.join(lines[max(0,i-2):min(len(lines),i+16)])
    with Image.open(p) as im: size=list(im.size)
    findings=[]
    if index==6 and not FINAL:
        findings=['Caption should say pressure sensitivity, not optimization results; adjacent prose already states the correct scope.']
    if index==8 and not FINAL:
        findings=['Add spaces to feed-reference label and replace internal dictionary keys with reader-facing screening names.']
    if FINAL and index==6:
        assert 'sensitivity' in caption.lower() and 'optimization results' not in caption.lower()
    if FINAL and index==8:
        assert 'of 290,000 kg/h' in text
        for label in ('Inlet gas screen','Expander power screen','Residue compressor power screen'):
            assert label in text
    items.append(dict(index=index,path=str(p),sha256=actual,source_copy_path=str(source),source_copy_hash_matches=True,size_px=size,
                      initial_inspected_sha256=initial['images'][index-1]['sha256'],actual_visual_inspection=True,inspection_method='Visual inspection by the reviewing agent of the actual displayed image, requested at original resolution.',
                      status='passed' if not findings else 'minor_editorial_correction_pending',observation=observations[index-1] if index!=8 or FINAL else observations[index-1].split('Corrected')[0],
                      findings=findings,resolved_findings=(['Changed caption from optimization results to pressure sensitivity.'] if index==6 else ['Spaced feed-rate reference and replaced internal legend keys with screening names.'] if index==8 else []) if FINAL else [],
                      caption=caption,caption_line=i+1,adjacent_text=excerpt,adjacent_text_sha256=hashlib.sha256(excerpt.encode('utf-8')).hexdigest(),chapter_path=str(chapter),chapter_sha256=sha(chapter),retained_numerical_evidence=details[index-1],evidence_files=evidence[index-1]))

report=dict(generated_at=datetime.now(timezone.utc).isoformat(),status='passed_scoped_visual_and_caption_review' if FINAL else 'review_complete_pending_two_editorial_corrections',
            method='Visual inspection by the reviewing agent of all eight source images with their adjacent chapter captions/prose, plus reconciliation of retained numerical arrays or literal-run scalar evidence. This is agent review, not human/domain peer certification.',
            image_count=8,full_image_views=8,unresolved_material_visual_defects=0,minor_corrections_pending=0 if FINAL else 2,
            limitations=['This visual audit does not replace the separately retained process-physics gate or independently validate field applicability.','Timestep plots qualify only the stated numerical cases and intervals.','Economic samples use specified illustrative distributions/policies; they do not establish investment suitability.','Whole-book PDF size, pagination and accessibility remain separate publication checks.'],
            python=sys.executable,copy_manifest_sha256=sha(manifest_path),review_script_sha256=sha(__file__),images=items)
(HERE/'literal_figure_visual_review.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
lines=['# Literal-run figure visual review','',report['status']+'.', '',report['method'],'','All eight actual images were displayed. The water-cut image was tool-resized from 1980×1381 to 1881×1312; all labels were readable. Image/source-copy hashes match the copy manifest.','', '| # | Figure | Finding |', '|---|---|---|']
for item in items:
    lines.append(f'| {item["index"]} | {Path(item["path"]).name} | {item["observation"]} {" ".join(item["findings"])} |')
lines.extend(['','## Numerical evidence checked',''])
for item in items:
    lines.append(f'- **{item["index"]}:** {json.dumps(item["retained_numerical_evidence"],ensure_ascii=False)}')
lines.extend(['','## Scope limits','']+['- '+x for x in report['limitations']])
lines.extend(['','## Final image hashes','', '| # | SHA-256 |','|---|---|']+[f'| {item["index"]} | `{item["sha256"]}` |' for item in items])
lines.extend(['',f'Copy manifest SHA-256: `{report["copy_manifest_sha256"]}`.','The JSON report retains full paths, image dimensions, source-copy equality, caption text, adjacent excerpts, and numerical-evidence hashes.'])
(HERE/'literal_figure_visual_review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'images':len(items),'minor_corrections_pending':report['minor_corrections_pending']}))
