"""Bind exact-source physics/ordinary execution and completed figure review."""
from pathlib import Path
from datetime import datetime,timezone
import json,re,hashlib,sys
H=Path(__file__).resolve().parent;B=H.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
hook=H/'export_capacity_solution_hooks.py';chapter_records=[]
pattern=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
for n in (19,20,22):
    chapter=next((B/'chapters').glob(f'ch{n:02d}_*'));p=chapter/'chapter.md'
    text=p.read_text(encoding='utf-8-sig');fences=list(pattern.finditer(text))
    source={i:hashlib.sha256(m.group(3).encode()).hexdigest() for i,m in enumerate(fences,1) if m.group(1)=='python'}
    ordinary_path=B/'verification'/f'{chapter.name}_fences.json';ordinary=read(ordinary_path)
    solution_path=H/f'ch{n:02d}_solution_checks.json';solution=read(solution_path)
    assert solution['all_targeted_checks_passed'] and solution['hook_sha256']==sha(hook)
    old=read(H/'literal_solution_previous_execution'/ordinary_path.name)
    old_hashes={r['number']:r['sha256'] for r in old['examples']}
    for table in (ordinary['examples'],solution['entries']):
        assert len(table)==len(source)
        for row in table:assert row['status']=='passed' and row['sha256']==source[row['number']],(n,row['number'])
    chapter_records.append({'chapter':n,'path':str(p),'sha256':sha(p),'code_fences':len(source),'checks':sum(len(row['checks']) for row in solution['entries']),
                            'ordinary_execution_path':str(ordinary_path),'ordinary_execution_sha256':sha(ordinary_path),'solution_path':str(solution_path),'solution_sha256':sha(solution_path),
                            'fences':[{'number':number,'sha256':digest,'previous_sha256':old_hashes.get(number),'changed':old_hashes.get(number)!=digest,'status':'passed_exact_source_execution_and_solution_checks'} for number,digest in source.items()]})

data_path=H/'literal_solution_figure_data.json';figures=read(data_path)
assert len(figures)==3
visual_notes=[
    'Original-resolution view inspected. The IPR and forward tubing curves meet at the plotted operating star; the dotted reservoir bound is distinct. No line bridges unavailable TPR states. Legend and rejection annotation are clear of data, and gas-rate/BHP units match the retained values.',
    'Original-resolution view inspected. Total duty and the two stage duties have separate panels so the shallow total-power minimum remains visible. The 70 bara sampled minimum and 61.24 bara equal-ratio reference are distinct. All axes/legends are readable and correctly use MW and bara.',
    'Original-resolution view inspected. All eleven actual objective pairs are visible; the 70 bara nondominated sample is highlighted. Oil is labeled separator mass in t/h, rather than stock-tank volume. The title and adjacent discussion explicitly state that this sample set has one dominating point.'
]
for i,r in enumerate(figures):
    assert sha(r['path'])==r['sha256'] and sha(r['source_report'])==r['source_report_sha256']
    source=read(r['source_report']);entry=next(e for e in source['entries'] if e['number']==r['literal_fence'])
    assert entry['code_sha256']==r['literal_code_sha256']
    observed=entry['checks'][-1]['observed']
    if i==0:
        assert r['data']['result']==observed
        assert [observed['rate_MSm3_day'],observed['BHP_bara']] in r['data']['accepted_TPR_rate_BHP']
        for q,p in zip(r['data']['analytic_IPR_rate_MSm3_day'],r['data']['analytic_IPR_BHP_bara']):assert abs(p**2-(250**2-(q/.0035)**(1/.85)))<1e-8
    elif i==1:
        assert r['data']['result']==observed
        for j,s in enumerate(observed['sampled_results']):assert r['data']['interstage_bara'][j]==s['P_inter'] and r['data']['total_stage1_stage2_MW'][j]==s['value']
    else:assert r['data']['points']==observed['all_points'] and r['data']['nondominated']==observed['nondominated_points']
    r.update(status='passed',visual_inspection=visual_notes[i],numerical_reconciliation='Full-precision plotted arrays match the accepted exact-literal evidence; analytical IPR values independently satisfy the declared equation.',actual_image_inspected=True)
review={'generated_at':datetime.now(timezone.utc).isoformat(),'status':'passed_scoped_visual_and_source_array_review','method':'Visual inspection by the reviewing agent of all three actual original-resolution images, plus programmatic exact-array reconciliation. Not human/domain peer certification.',
        'data_manifest_sha256':sha(data_path),'generator':str(H/'render_literal_solution_figures.py'),'generator_sha256':sha(H/'render_literal_solution_figures.py'),'figures':figures}
(H/'literal_solution_figure_review.json').write_text(json.dumps(review,indent=2,ensure_ascii=False),encoding='utf-8')
(H/'literal_solution_figure_review.md').write_text('# Exact-literal solution figures\n\nPASS: three actual plots visually inspected by the reviewing agent and reconciled against accepted full-precision arrays.\n\n'+'\n\n'.join(f'**{Path(r["path"]).name}:** {r["visual_inspection"]}\n\n{r["discussion"]}\n\nSHA-256: `{r["sha256"]}`.' for r in figures)+'\n',encoding='utf-8')

diagnostic={'scope':'Rejected native dew-point method diagnosis before the manuscript switched to the multiphase method and verified the phase boundary. These are observed outputs from the retained probe, not fabricated reference values.',
            'probe_script':str(H/'probe_ch19_export.py'),'probe_script_sha256':sha(H/'probe_ch19_export.py'),
            'rejected_results':[{'method':mode,'pressure_bara':pressure,'returned_temperature_K':0.0,'accepted':False} for mode in ('raw waterDewPointTemperatureFlash','init(0) then waterDewPointTemperatureFlash') for pressure in (20.,70.,150.)],
            'accepted_method':'waterDewPointTemperatureMultiphaseFlash with fresh TP phase-onset brackets at -0.2/+0.2 K; exact eight-state evidence in ch19_solution_checks.json',
            'other_diagnostics':['ch19_initial_solution_failure.json','ch19_envelope_array_probe.json','ch22_solution_checks.json: fence1 rejected_solver_diagnostics', 'literal_solution_previous_execution/']}
(H/'literal_solution_rejected_diagnostics.json').write_text(json.dumps(diagnostic,indent=2),encoding='utf-8')

changes=[
 'Initialized mole fractions before ISO6976; the former zero GCV/NaN Wobbe output is rejected. Checked positive GCV>NCV, Wobbe=GCV/sqrt(relative density), compositional molar mass, reference units and all declared quality-screen predicates.',
 'Replaced the failing direct water-dew-point call with a normalized exactly 20 mol-ppm CPA recipe and a multiphase VLE calculation. Eight pressure states each have aqueous liquid below and no aqueous liquid above their onset. Ice/hydrate scope is explicit.',
 'Retained finite contiguous hydrocarbon envelope data and documented the undefined terminal continuation slot. The reported quantity is a sampled dew-curve maximum, with no invented critical point.',
 'Export pipelines and diameter alternatives have positive pressure, material/component balance and accepted/rejected-domain checks; coupled compressor and cooler boundaries have first-law checks.',
 'Corrected the facility pipeline length from 80 m to 80,000 m. Replaced claims of a complete LP/two-stage/UA facility with the actual HP/single-stage/specified-temperature-cooler boundary.',
 'Explicitly enabled polytropic calculation wherever a polytropic efficiency was specified. Compressor checks include single-phase inlets, positive work, rising pressure/temperature and first-law closure.',
 'Verified half-full separator geometry, retention and Souders–Brown arithmetic, UA clean/fouled heat balance, isenthalpic valve behavior, erosional-unit conversion and fixed-rating utilization arithmetic. A linear extrapolation is explicitly not a solved facility capacity.',
 'Replaced the unexecuted water-cut placeholder and assumed trend with eight actual CPA methane/heptane/water cases using fixed 200 m3/h liquid at 15 C/1.01325 bara and a specified associated-gas/oil ratio. Each separation and compression boundary is checked.',
 'Replaced the dimensionally invalid API-area expression with a clearly scoped SI ideal-gas sonic-nozzle limit. An independent sonic-state density×velocity×area check reproduces its mass rate. Real-fluid Z and pressure convention are explicit; no PSV rating is claimed.',
 'Replaced reverse 3 m wellbore integration with a forward 3000 m upward tubing solve coupled to the declared IPR. Nonphysical trial states are excluded and diagnosed; accepted TPR and operating-point residuals are checked.',
 'Verified every separation and compressor sample and all objective selections. Actual two-objective samples have one nondominated point. Gas-lift allocation is checked by analytical KKT conditions and an independent exhaustive grid.',
 'Replaced three stale adjacent Chapter22 illustrations with actual accepted nodal, interstage-power and sampled-objective plots, with connected quantitative discussions.'
]
summary={'generated_at':datetime.now(timezone.utc).isoformat(),'status':'passed_frozen_exact_source_solution_review','scope':'All 28 published Python fences in chapters 19, 20 and 22, including API coverage behavior and explicitly scoped engineering calculations. This is solution verification, not universal field calibration or standards certification.',
         'source_commit':read(H/'ch19_solution_checks.json')['source_commit'],'python':sys.executable,'hook_sha256':sha(hook),'chapters':chapter_records,
         'counts':{'chapters':3,'literal_fences':sum(c['code_fences'] for c in chapter_records),'solution_check_records':sum(c['checks'] for c in chapter_records),'new_actual_figures':3},
         'changes':changes,'rejected_diagnostics_sha256':sha(H/'literal_solution_rejected_diagnostics.json'),'figure_review_sha256':sha(H/'literal_solution_figure_review.json'),
         'new_reference_folder':str(H/'references/nasa'),'notebooks_modified':False,
         'regeneration':['Run audit_optimization_examples.py --chapters 19,20,22 with the selected Python.','Run verify_optimization_solution_hooks.py separately for chapters 19, 20 and 22 with export_capacity_solution_hooks.py.','Run render_literal_solution_figures.py, inspect actual figures, then run this finalizer.','Repair scripts are one-time editors, not routine regeneration steps.']}
(H/'literal_solution_revision_19_20_22.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
(H/'literal_solution_revision_19_20_22.md').write_text('# Chapters 19, 20 and 22 solution verification\n\nPASS: all 28 literal Python fences execute and match current source hashes, with '+str(summary['counts']['solution_check_records'])+' scoped solution-check records. Three new actual figures passed visual and array review. The 35 chapter notebooks were not modified.\n\n'+'\n\n'.join('- '+x for x in changes)+'\n\nExact code/report/image hashes, tolerances and observed values are retained in the JSON records. These checks establish the stated numerical/physical scopes and do not provide field or standards certification.\n',encoding='utf-8')
print(json.dumps(summary['counts']))
