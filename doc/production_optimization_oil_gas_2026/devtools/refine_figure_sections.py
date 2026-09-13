"""Apply reviewed interpretations without changing any executed code or output.

Regenerates per-chapter ready-to-insert Markdown, the figure hand-off manifest,
and notebook discussion cells. Records the pre-edit notebook hash and proves
every executed code-cell hash is unchanged before updating artifact hashes.
"""
import hashlib
import json
import math
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from figure_editorial_context import CONTEXT, TITLES, SCOPES

BOOK = Path(__file__).resolve().parents[1]
VERIFICATION = BOOK / 'verification'
FOUNDATIONS = json.loads((VERIFICATION/'figure_interpretations_foundations.json').read_text(encoding='utf-8'))

def clean(s):
    return ' '.join(str(s).replace('−','-').split())

def number(v):
    return f'{v:.4g}' if isinstance(v, (int,float)) else str(v)

def quantity(label):
    label=clean(label)
    match=re.match(r'^(.*?)\s*[\[(]([^\[\]()]+)[\])]$', label)
    if match:
        return match.group(1), match.group(2)
    return label, ''

def rows_for(record):
    rows=[]
    for s in record['series']:
        if s['n_points'] < 3 or s['y_min'] is None:
            continue
        a=s.get('value_axis','y')
        if s['y_label'].startswith('Depth '):
            a='x'
        label=s[a+'_label']
        if not label:
            continue
        q,u=quantity(label)
        name=clean(s['series'])
        if re.match(r'^(Curve|Bars|Points) \d+$', name) or name.startswith('_'):
            name=q
        if name.lower()!=q.lower():
            name=f'{name}: {q.lower()}'
        row=[name,s[a+'_min'],s[a+'_max'],u]
        if row not in rows:
            rows.append(row)
    return rows

def observation(record, rows, values):
    filename=Path(record['path']).name
    if filename=='ch22_teg_water_content.png':
        water=values['water_content']; rates=values['teg_rates']; minimum=min(range(len(water)),key=water.__getitem__)
        return f"Dry-gas water decreases from {water[0]:.3f} ppmv at {rates[0]:.0f} kg/hr circulation to a sampled minimum of {water[minimum]:.3f} ppmv at {rates[minimum]:.1f} kg/hr, then rises slightly to {water[-1]:.3f} ppmv at {rates[-1]:.0f} kg/hr. All reconstructed cases retain explicit material and energy checks."
    if filename=='ch04_fig03_density_vs_depth.png':
        return f"Across the assumed 0–3000 m depth interval, density spans {min(values['densities']):.1f}–{max(values['densities']):.1f} kg/m³ and temperature spans {min(values['temps']):.1f}–{max(values['temps']):.1f} °C."
    if filename=='ch05_fig02_operating_point.png':
        return f"The coupled solution gives {values['q_op']:.3f} t/hr at {values['p_op']:.2f} bara bottomhole pressure. The calculated wellhead pressure is {values['achieved_pwh']:.3f} bara against a {values['P_wh_target']:.0f} bara target."
    if filename=='fig04_pipeline_capacity.png':
        return f"The sampled pipe diameters span {values['diameters_cap_inch'][0]:.0f}–{values['diameters_cap_inch'][-1]:.0f} inches. Bisection finds throughputs of {min(values['max_flows']):.2f}–{max(values['max_flows']):.2f} t/hr at the {values['available_dp']:.0f} bar pressure-loss allowance; the search upper bound was checked to lie beyond the capacity boundary."
    if filename=='fig01_hydrate_equilibrium.png':
        temperatures=values['hydrate_temps_C']
        return f"The calculated hydrate equilibrium temperature rises from {temperatures[0]:.2f} °C at {values['pressures_bara'][0]:.0f} bara to {temperatures[-1]:.2f} °C at {values['pressures_bara'][-1]:.0f} bara for the stated gas and water recipe."
    if filename=='fig02_meg_inhibition.png':
        temperatures=values['hydrate_T_with_meg']
        return f"At {values['test_pressure']:.0f} bara, increasing the specified aqueous MEG concentration from 0 to 50 wt% lowers hydrate equilibrium temperature from {temperatures[0]:.2f} to {temperatures[-1]:.2f} °C, a depression of {temperatures[0]-temperatures[-1]:.2f} °C."
    if filename=='fig01_phase_split.png':
        return f"The separator-pressure sweep covers {min(values['sep_pressures']):.0f}–{max(values['sep_pressures']):.0f} bara. Gas accounts for {min(values['gas_fracs']):.2f}–{max(values['gas_fracs']):.2f} percent of feed mass across the plotted cases."
    if filename=='fig03_separator_optimization.png':
        oil_t_hr=values['opt_y']/1000.0
        assert any(abs(s['y_max']-oil_t_hr)<1e-6 for s in record['series']), 'Oil-rate observation must match plotted t/hr basis'
        return f"The largest sampled final-separator oil rate is {oil_t_hr:.3f} t/hr at a second-stage pressure of {values['opt_p']:.1f} bara, with the first and final stages fixed at {values['P1']:.0f} and {values['P3']:.1f} bara. The feed is 50 t/hr at 60 °C; final oil leaves at its calculated flash temperature, without a subsequent reference-condition flash."
    if filename=='fig12_4_power_comparison.png':
        return f"For the 5–150 bara train, one and four stages require {values['total_powers'][0]:.3f} and {values['total_powers'][-1]:.3f} MW. Their maximum discharge temperatures are {values['max_discharge_temps'][0]:.1f} and {values['max_discharge_temps'][-1]:.1f} °C. Three stages reach {values['max_discharge_temps'][2]:.1f} °C, slightly above the illustrative 150 °C limit."
    if filename=='ch18_utilization_bar_chart.png':
        return f"At the nominal 50 t/hr feed, the reported equipment utilization spans {min(values['utils']):.1f}–{max(values['utils']):.1f} percent of the stated screening capacities."
    if filename=='ch19_sensitivity_tornado.png':
        return f"The baseline bisection result is {values['base_max']/1000:.3f} t/hr. The largest negative throughput change in the single-rating sensitivity is {min(values['low_vals'])/1000:.3f} t/hr; the largest positive change is {max(values['high_vals'])/1000:.3f} t/hr."
    if filename=='ch25_feasibility_curve.png':
        return f"The sampled compression powers span {min(values['comp_power_kw']):.1f}–{max(values['comp_power_kw']):.1f} kW. The current FlowRateOptimizer returns {values['opt_rate']/1000:.3f} t/hr under the separately declared 4750 kW screening limit."
    if filename=='ch18_algorithm_comparison.png':
        return f"Binary and golden-section searches return {values['opt_rates'][0]/1000:.4f} and {values['opt_rates'][1]/1000:.4f} t/hr. Independent reruns give maximum utilizations of {values['opt_utils'][0]:.3f} and {values['opt_utils'][1]:.3f} percent."
    if filename=='ch26_utilization_heatmap.png':
        array=[v*100 for row in values['utilization_matrix'] for v in row]
        return f"Across the five operating fractions and two compressor stages, power utilization spans {min(array):.1f}–{max(array):.1f} percent of the assumed 3500 and 4000 kW stage ratings."
    if filename=='ch19_vfp_surface.png':
        residual=max(abs(x) for x in values['arrival_errors'])
        bhps=[v for row in values['BHP_grid'] for v in row]
        return f"The sixty upward-flow solutions span {min(bhps):.2f}–{max(bhps):.2f} bara required bottomhole pressure. The largest difference between solved and specified wellhead pressure is {residual:.4f} bar."
    if filename=='ch29_recycle_convergence.png':
        return f"The actual NeqSim tear-stream iteration meets the stated 10⁻⁷ normalized-residual criterion in {values['max_iters']:.0f} iterations. Residuals are measured from successive flow, temperature and composition updates; exact zeros use a 10⁻¹⁶ display floor on the logarithmic axis."
    if filename=='ch22_teg_water_content.png':
        water=values['water_content']
        rates=values['teg_rates']
        return f"Dry-gas water content falls from {water[0]:.2f} ppmv at {rates[0]:.0f} kg/hr TEG to {water[-1]:.2f} ppmv at {rates[-1]:.0f} kg/hr. The lowest sampled result is {min(water):.2f} ppmv, showing the small additional benefit at high circulation."
    if filename=='ch22_scenario_comparison.png':
        summer,winter=values['summer_vals'],values['winter_vals']
        return f"From summer to winter, compressor power changes from {summer[0]:.3f} to {winter[0]:.3f} MW and discharge temperature from {summer[1]:.2f} to {winter[1]:.2f} °C. Cooler duty changes from {summer[2]:.3f} to {winter[2]:.3f} MW, while export temperature changes from {summer[3]:.0f} to {winter[3]:.0f} °C."
    if filename=='ch24_h2_blending_wobbe.png':
        return f"From 0 to 50 mol% hydrogen in methane, the calculated superior Wobbe index decreases from {values['wobbe_indices'][0]:.2f} to {values['wobbe_indices'][-1]:.2f} MJ/m³. The standard-condition density decreases from {values['densities_blend'][0]:.3f} to {values['densities_blend'][-1]:.3f} kg/m³."
    if filename=='ch06_fig05_pressure_budget.png':
        return f"The assumed pressure allocation starts at {values['P_reservoir']:.0f} bara reservoir pressure and ends at {values['P_separator']:.0f} bara separation pressure. The individual losses are prescribed budget entries rather than a solved network balance."
    if filename=='ch30_power_demand_pie.png':
        return f"The assigned loads total {values['total_demand']:.1f} MW against {values['total_available']:.1f} MW of assumed available generation; the allocation is an illustrative platform power budget."
    if filename=='ch23_power_consumption.png':
        return f"The integrated case reports {values['lp_power_kW']:.1f} kW for the low-pressure compressor and {values['export_power_kW']:.1f} kW for export compression, giving {values['total_power_kW']:.1f} kW total shaft power."
    if not rows:
        return 'The diagram uses the explicit input values and model assumptions shown in the accompanying example.'
    fragments=[]
    for name, low, high, unit in rows[:2]:
        name=name[0].upper()+name[1:]
        suffix=(' '+unit) if unit and unit!='-' else ''
        if math.isclose(low,high,rel_tol=1e-9,abs_tol=1e-9):
            fragments.append(f'{name} remains {number(low)}{suffix} across the plotted cases.')
        else:
            fragments.append(f'{name} spans {number(low)}–{number(high)}{suffix} across the plotted cases.')
    return ' '.join(fragments)

def refine(item, record, values):
    key=item['chapter']+'/'+item['figure']
    if item['figure'] in CONTEXT:
        item.update(dict(zip(('mechanism','implication','recommendation'),CONTEXT[item['figure']].split('|'))))
    else:
        assert key in FOUNDATIONS, 'Missing reviewed interpretation: '+key
        item.update(FOUNDATIONS[key])
    item['title']=TITLES.get(item['figure'],clean(item['title']))
    item['caption']=item['title'].rstrip('.')+'.'
    scope=SCOPES.get(item['figure'],'')
    if scope:
        item['caption']+=' '+scope
    rows=rows_for(record)
    item['observation']=observation(record,rows,values)
    missing=sum(s['n_nonfinite'] for s in record['series'])
    if missing:
        item['observation']+=' Gaps retain undefined phase quantities or hydraulic states that fail the stated operating boundary; they are not interpolated.'
    item['table']={'headers':['Quantity / series','Minimum','Maximum','Unit'],'rows':rows[:5]}
    item['editorial_review']='Plot-specific interpretation reviewed against executed source and numerical data.'
    return item

def discussion(item):
    return '**Executed-figure discussion.** '+item['observation']+'\n\n'+item['mechanism']+' '+item['implication']+' '+item['recommendation']+'\n'

import argparse
_parser=argparse.ArgumentParser(description='Refine executed-figure discussions without changing numerical outputs.')
_parser.add_argument('--chapters', help='Comma-separated chapter prefixes, e.g. ch10; omitted processes all chapters.')
_args=_parser.parse_args()
_selected={s.strip() for s in _args.chapters.split(',')} if _args.chapters else None
all_items=[]
sections=VERIFICATION/'figure_sections'
sections.mkdir(exist_ok=True)
for rp in sorted((VERIFICATION/'notebooks').glob('*.json')):
    report=json.loads(rp.read_text(encoding='utf-8'))
    if _selected is not None and rp.stem[:4] not in _selected:
        all_items.extend(report['figure_discussions'])
        continue
    assert report['status']=='passed', 'Complete numerical verification first: '+rp.name
    nb_path=BOOK/report['notebook']
    nb=json.loads(nb_path.read_text(encoding='utf-8'))
    for run in report['cell_runs']:
        source=''.join(nb['cells'][run['cell_index']]['source'])
        assert hashlib.sha256(source.encode()).hexdigest()==run['sha256'], 'Executed code changed'
    old_hash=hashlib.sha256(nb_path.read_bytes()).hexdigest()
    assert old_hash==report['notebook_sha256'], 'Unreported notebook edit: '+str(nb_path)
    records={Path(r['path']).name:r for r in report['figures']}
    items=[refine(item, records[item['figure']], report['numeric_results']) for item in report['figure_discussions']]
    cells=[c for c in nb['cells'] if c['cell_type']=='markdown' and ''.join(c['source']).startswith('**Executed-figure discussion.**')]
    assert len(cells)==len(items), 'Discussion coverage mismatch: '+rp.name
    for cell,item in zip(cells,items):
        cell['source']=discussion(item).splitlines(True)
    nb_path.write_text(json.dumps(nb,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
    report['notebook_sha256']=hashlib.sha256(nb_path.read_bytes()).hexdigest()
    report['editorial_review']={'reviewed_at':datetime.now(timezone.utc).isoformat(),
        'pre_review_notebook_sha256':old_hash,'code_and_outputs_unchanged':True,
        'description':'Replaced generated discussion prose with plot-specific reviewed interpretation; every executed code hash rechecked.'}
    report['figure_discussions']=items
    rp.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    all_items.extend(items)
    chapter_number=items[0]['chapter_number']
    text=['## Verified numerical illustrations','',
          'These examples use the stated fluid recipes and operating assumptions. Curves represent NeqSim calculations unless a caption identifies an analytical illustration, assumed equipment map or synthetic data.','']
    table_rows=[]
    for item in items:
        text += ['![{}]({})'.format(item['title'],item['figure_path']),'',
                 '*'+item['caption']+'*','',item['observation'],'',
                 item['mechanism']+' '+item['implication']+' '+item['recommendation'],'']
        if item['table']['rows']:
            table_rows.append(item['table']['rows'][0])
    if table_rows:
        text+=['Selected numerical ranges from the plotted cases:','',
               '| Quantity / series | Minimum | Maximum | Unit |',
               '|---|---:|---:|---|']
        for row in table_rows:
            text.append('| '+' | '.join(number(value).replace('|','/') for value in row)+' |')
        text+=['','Ranges describe the sampled cases; they are not independent validation tolerances.','']
    (sections/f'ch{chapter_number:02d}.md').write_text('\n'.join(text),encoding='utf-8')
(VERIFICATION/'notebook_figure_updates.json').write_text(json.dumps(all_items,indent=2,ensure_ascii=False),encoding='utf-8')
print(f'Reviewed {len(all_items)} figures; created {len(list(sections.glob("ch*.md")))} chapter sections. No executed code or outputs changed.')
