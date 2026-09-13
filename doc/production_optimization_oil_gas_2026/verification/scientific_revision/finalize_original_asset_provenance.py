"""Bind eleven remaining manuscript plots to current literal arrays or declared fixtures.

This is a publication-only transformation: no source fence or simulation input changes.
"""
from pathlib import Path
from datetime import datetime, timezone
import sys, json, re, hashlib, shutil
OUT=Path(__file__).resolve().parent; BOOK=OUT.parents[1]
sys.path.insert(0,str(BOOK/'.build/python_packages'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,
                     'axes.labelsize':11,'legend.fontsize':9,'axes.spines.top':False,
                     'axes.spines.right':False,'savefig.dpi':220})
BACKUP=BOOK/'.build/backups/final_original_asset_provenance'
BACKUP.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
write=lambda p,d:p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
chap=lambda n:next((BOOK/'chapters').glob(f'ch{n:02d}*/chapter.md'))
fences=lambda text:[m[0] for m in re.finditer(r'^```[^\n]*\n.*?^```',text,re.M|re.S)]
images=[]; changes=[]
def backup(path):
    dest=BACKUP/path.relative_to(BOOK)
    if not dest.exists():
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
    return str(dest.relative_to(BOOK))
def figure_path(n,name):
    p=chap(n).parent/'figures'/name;backup(p);return p
def finish_image(p,source,transformation,checks=None):
    images.append({'path':str(p.relative_to(BOOK)),'sha256':sha(p),'source':source,
                   'transformation':transformation,'checks':checks or [],
                   'previous_asset':str((BACKUP/p.relative_to(BOOK)).relative_to(BOOK)),
                   'previous_sha256':sha(BACKUP/p.relative_to(BOOK)),
                   'visual_review_status':'pending_final_view'})
def source_record(n,name):
    rp=OUT/f'final_original_ch{n:02d}_plot_arrays.json';r=read(rp)
    plot=next(x for x in r['plots'] if Path(x['path']).name==name)
    assert sha(Path(plot['path']))==plot['sha256']
    text=chap(n).read_text(encoding='utf-8-sig')
    matches=[m for m in re.finditer(r'^```(python|java)\s*\n(.*?)^```',text,re.M|re.S) if name in m[2]]
    assert len(matches)==1
    digest=hashlib.sha256(matches[0][2].encode()).hexdigest()
    pr=OUT/f'ch{n:02d}_manuscript_physics.json';physics=read(pr)
    literal=next(e for e in physics['literal_blocks'] if e['code_sha256']==digest)
    assert literal['execution']=='pass' and all(x['pass'] for x in physics['physical_checks'])
    return plot,{'type':'unchanged_published_literal_replay','chapter':n,'source_fence_index':literal['index'],
                 'code_sha256':digest,'captured_arrays':str(rp.relative_to(BOOK)),'captured_arrays_sha256':sha(rp),
                 'physics_report':str(pr.relative_to(BOOK)),'physics_report_sha256':sha(pr),
                 'replayed_image_sha256':plot['sha256']}
direct={10:['mp_pressure_lp_liquid_recovery.png','separator_utilization_profile.png','separator_pressure_optimization.png'],
        14:['compression_pr_sensitivity.png','compressor_speed_sensitivity.png'],18:['gt_ambient_performance.png']}
for n,names in direct.items():
    for name in names:
        plot,source=source_record(n,name);p=figure_path(n,name);shutil.copy2(plot['path'],p)
        finish_image(p,source,'Byte-for-byte copy from the accepted exact-literal replay; all line arrays retained separately.')

# Ch14: preserve the computed point and analytic line arrays, remove an unsupported
# surge series. Those polynomial speed families are not a solved compressor chart.
name='compressor_performance_map.png';plot,source=source_record(14,name)
lines=plot['axes'][0]['lines'];fig,ax=plt.subplots(figsize=(9.2,5.8))
for line in lines[:5]:
    ax.plot(line['x'],line['y'],label=line['label'].replace(' speed',' assumed speed'),lw=1.8)
point=lines[5];x,y=point['x'][0],point['y'][0]
ax.plot([x],[y],'ko',ms=7,label='Calculated thermodynamic point')
ax.annotate(f'{x:.0f} m³/hr; {y:.2f} kJ/kg',xy=(x,y),xytext=(.37,.18),textcoords='axes fraction',
            arrowprops={'arrowstyle':'->','color':'black'},bbox={'facecolor':'white','edgecolor':'none','alpha':.95})
ax.set(xlabel='Actual inlet volume flow (m³/hr)',ylabel='Polytropic head (kJ/kg)',
       title='Illustrative head curves around a calculated point')
ax.grid(alpha=.25);ax.legend(loc='upper center',bbox_to_anchor=(.5,-.15),ncol=2)
fig.tight_layout();p=figure_path(14,name);fig.savefig(p,bbox_inches='tight');plt.close(fig)
finish_image(p,source,'Unchanged captured five analytic speed-line arrays and computed point. Removed the unsupported synthetic surge series; moved legend/annotation clear of data. The curves are an illustration, not an installed compressor rating.',
             [{'name':'source arrays preserved','passed':True,'retained_lines':6,'removed_lines':1},
              {'name':'computed point','flow_m3_hr':x,'head_kJ_kg':y}])

# Ch15: both panels use the same accepted mask; no clipping to a lower efficiency
# axis can conceal a physically inadmissible extrapolation.
name='compressor_map_complete.png';plot,source=source_record(15,name)
head=plot['axes'][0]['lines'];eff=plot['axes'][1]['lines'];rejected=[]
fig,axes=plt.subplots(2,1,figsize=(9.2,9),sharex=True)
for i,(h,e) in enumerate(zip(head[:5],eff)):
    xx,hh,ee=np.array(h['x']),np.array(h['y']),np.array(e['y']);assert np.array_equal(xx,e['x'])
    mask=np.isfinite(ee)&(ee>0)&(ee<=100)&np.isfinite(hh)&(hh>0)
    for k in np.flatnonzero(~mask):rejected.append({'speed_line':e['label'],'sample_index':int(k),'flow_m3_hr':float(xx[k]),'head_kJ_kg':float(hh[k]),'efficiency_percent':float(ee[k]),'reason':'polynomial extrapolation has efficiency outside (0,100]% or nonpositive head'})
    axes[0].plot(xx,np.where(mask,hh,np.nan),lw=1.8,label=h['label'])
    axes[1].plot(xx,np.where(mask,ee,np.nan),lw=1.8,label=e['label'])
boundary=head[5]
axes[0].plot(boundary['x'],boundary['y'],'k--',lw=1.6,label='Assumed boundary (third sample)')
axes[0].set(ylabel='Polytropic head (kJ/kg)',title='Illustrative polynomial head curves')
axes[1].set(xlabel='Actual inlet volume flow (m³/hr)',ylabel='Polytropic efficiency (%)',ylim=(0,85),
            title='Efficiency fixture: physically admissible samples only')
axes[0].legend(ncol=2,fontsize=8,loc='upper center',bbox_to_anchor=(.5,1.35))
axes[1].legend(ncol=3,fontsize=8,loc='lower center',bbox_to_anchor=(.5,-.37))
for ax in axes:ax.grid(alpha=.25)
fig.text(.5,.01,f'{len(rejected)} of 100 paired samples rejected: negative-efficiency extrapolation at 70% speed.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.04,1,.94],h_pad=2.5);p=figure_path(15,name);fig.savefig(p,bbox_inches='tight');plt.close(fig)
assert len(rejected)==1 and rejected[0]['efficiency_percent']<0
finish_image(p,source,'Use captured arrays only; reject the one nonphysical efficiency sample from BOTH paired panels, expand efficiency scale to zero, remove unrelated shading, and identify the selected boundary as assumed.',
             [{'name':'explicit sample-domain ledger','passed':True,'original_paired_samples':100,'accepted_paired_samples':99,'rejected_samples':rejected,
               'acceptance':'finite positive head and 0 < efficiency_percent <= 100; no empirical-map validation implied'}])

# Ch19: the accepted exact-source hooks retained the numerical outputs separately
# from these obsolete original plots. Algebraic identities were already checked.
report_path=OUT/'ch19_solution_checks.json';report=read(report_path)
text=chap(19).read_text(encoding='utf-8-sig');py=list(re.finditer(r'^```python[^\n]*\n(.*?)^```',text,re.M|re.S))
for idx in [2,6]:
    entry=next(e for e in report['entries'] if e['number']==idx)
    assert entry['status']=='passed' and entry['code_sha256']==hashlib.sha256(py[idx-1][1].encode()).hexdigest()
    source={'type':'accepted_exact_literal_solution_hook_data','chapter':19,'source_fence_index':idx,
            'code_sha256':entry['code_sha256'],'report':str(report_path.relative_to(BOOK)),'report_sha256':sha(report_path)}
    if idx==2:
        data=[dict(c['observed'],C2plus_mol_percent=float(c['name'].split()[-1])*100) for c in entry['checks'] if c['name'].startswith('C2+ fraction')]
        assert len(data)==7
        fig,axes=plt.subplots(1,2,figsize=(10,4.7),sharex=True)
        for ax,key,label in zip(axes,['GCV_MJ_Sm3','Wobbe_MJ_Sm3'],['Superior calorific value (MJ/Sm³)','Superior Wobbe index (MJ/Sm³)']):
            ax.plot([v['C2plus_mol_percent'] for v in data],[v[key] for v in data],'o-',color='#0F6B86')
            ax.set(xlabel='C₂+ fraction (mol%)',ylabel=label);ax.grid(alpha=.25)
        fig.suptitle('Gas-quality sensitivity: 15 °C volume / 25 °C combustion basis');fig.tight_layout()
        name='gcv_wobbe_vs_ngl.png';p=figure_path(19,name);fig.savefig(p,bbox_inches='tight');plt.close(fig)
    else:
        data=next(c['observed'] for c in entry['checks'] if c['name']=='Diameter sweep domain ledger')
        assert len(data)==7 and all(v['physical_pressure_domain'] for v in data)
        assert all(0<v['outlet_bara']<=150 and v['inlet_velocity_m_s']>0 for v in data)
        xx=[v['diameter_inch'] for v in data];dp=[150-v['outlet_bara'] for v in data]
        assert all(b<a for a,b in zip(dp,dp[1:]))
        fig,axes=plt.subplots(1,2,figsize=(10,4.7),sharex=True)
        axes[0].plot(xx,dp,'o-',color='#0F6B86');axes[0].set_ylabel('Pressure drop (bar)')
        axes[1].plot(xx,[v['inlet_velocity_m_s'] for v in data],'s-',color='#C5682A');axes[1].set_ylabel('Inlet gas velocity (m/s)')
        for ax in axes:ax.set_xlabel('Internal diameter (inch)');ax.grid(alpha=.25)
        fig.suptitle('300 km horizontal export pipe: 15 MSm³/day, 150 bara inlet');fig.tight_layout()
        name='pipeline_sizing_dp_vs_diameter.png';p=figure_path(19,name);fig.savefig(p,bbox_inches='tight');plt.close(fig)
    dp=OUT/('final_original_'+name.replace('.png','_data.json'));write(dp,{'source':source,'points':data})
    source.update(data_path=str(dp.relative_to(BOOK)),data_sha256=sha(dp))
    finish_image(p,source,'Redrawn directly from accepted exact-source output records. No surrogate formulas or independently invented sample values.',
                 [{'name':'literal code hash and data coverage','passed':True,'points':len(data)}])

# Ch17: normalized inherent-Cv illustration; the equations are the source fixture.
xx=np.linspace(0,1,200);r=50.;vals={'Linear':xx,'Equal percentage (R=50)':r**(xx-1),'Quick opening (square-root fixture)':np.sqrt(xx)}
assert all(np.isfinite(y).all() and (y>=0).all() and (y<=1).all() and (np.diff(y)>=0).all() for y in vals.values())
assert vals['Equal percentage (R=50)'][0]==1/r
fixture={'basis':'u=travel/max_travel; normalized Cv/Cvmax','rangeability':50,'travel_fraction':xx.tolist(),
         'equations':{'Linear':'u','Equal percentage (R=50)':'50**(u-1)','Quick opening (square-root fixture)':'sqrt(u)'},
         'normalized_Cv':{k:v.tolist() for k,v in vals.items()},
         'limits':'The equal-percentage 1/R minimum is a controllable-capacity endpoint, not shutoff leakage. Square root is an illustrative quick-opening approximation.'}
dp=OUT/'final_original_valve_characteristics_data.json';write(dp,fixture)
fig,ax=plt.subplots(figsize=(8.5,5.2))
for (label,y),style in zip(vals.items(),['-','--','-.']):ax.plot(xx*100,y*100,style,lw=2,label=label)
ax.set(xlabel='Travel (% of range)',ylabel='Normalized capacity Cv/Cvmax (%)',title='Idealized inherent valve characteristics',xlim=(0,100),ylim=(0,105))
ax.grid(alpha=.25);ax.legend(loc='upper left');fig.tight_layout();p=figure_path(17,'valve_characteristics_curves.png');fig.savefig(p,bbox_inches='tight');plt.close(fig)
finish_image(p,{'type':'declared_analytic_fixture','data_path':str(dp.relative_to(BOOK)),'data_sha256':sha(dp),
                'source_equations':'Chapter 17, section 17.2.2','legacy_generator_sha256':sha(OUT/'legacy_generators/generate_figures_batch2.py')},
             'Recreated the three published equations on 200 normalized travel points; explicit fixture labels and units.',
             [{'name':'analytical endpoints and domain','passed':True,'equal_percentage_minimum':.02,'linear_endpoints':[0,1],'square_root_endpoints':[0,1],'monotonic_nonnegative_bounded':True}])

def caption(n,name,title,paragraph,replace_next=False):
    cp=chap(n);backup(cp);text=cp.read_text(encoding='utf-8-sig');before=fences(text)
    pattern=r'!\[Figure ([^:]+):[^\n]*\]\(figures/'+re.escape(name)+r'\)'
    m=re.search(pattern,text);assert m,(n,name)
    start,end=m.span();old=m[0]
    replacement=f'![Figure {m[1]}: {title}](figures/{name})'
    tail=text[end:]
    if replace_next:
        pm=re.match(r'\n\n([^\n]+)\n',tail);assert pm and not pm[1].startswith(('#','---','```','![')),(name,tail[:100])
        old+='\n\n'+pm[1];tail=tail[pm.end()-1:]
    text=text[:start]+replacement+'\n\n'+paragraph+tail
    assert fences(text)==before,'Unexpected code edit'
    cp.write_text(text,encoding='utf-8')
    changes.append({'chapter':n,'figure':name,'previous_prose':old,'caption':title,'discussion':paragraph,'source_code_unchanged':True})

caption(10,'mp_pressure_lp_liquid_recovery.png','LP separator liquid recovery at 2 bara, from the published three-stage sweep',
        'At 100 t/hr feed, 75 °C and 70 bara first-stage pressure, the calculated final-separator liquid rate decreases from 97.14 to 92.58 m³/hr as intermediate pressure increases from 10 to 50 bara. These are liquid-stream volumes at the 2 bara final separator and its calculated flash temperature; they include the modeled liquid phases and are not reference-condition stock-tank oil rates.')
caption(10,'separator_utilization_profile.png','Fixed-vessel separator gas utilization and K-factor across the declared feed-rate sweep',
        'The vessel is sized once at 100 t/hr, 70 bara and 70 °C with the example sizing factor 1.2. Across 50–175 t/hr, gas utilization rises from 41.48% to 145.17%; the plot retains the over-capacity points. The 85% warning line is an illustrative operating threshold, and the 0.107 m/s design K-factor is the assumed screening basis rather than a measured internals rating.',True)
caption(10,'separator_pressure_optimization.png','LP separator liquid recovery at 3 bara and fixed-vessel gas utilization versus MP pressure',
        'The left panel reports liquid-stream volume at the 3 bara final separator and calculated flash temperature. Vessels in the right panel are sized once at 30 bara MP pressure. Lower MP pressure increases gas flashing and MP loading; the highest sampled liquid recovery at 10 bara is rejected by the fixed-vessel gas-capacity constraint. A reference-condition oil objective requires an additional declared flash.',True)
caption(14,'compression_pr_sensitivity.png','Calculated power and discharge temperature for the 20 t/hr, 80% polytropic-efficiency pressure-ratio sweep',
        'At 10 bara and 30 °C suction, increasing pressure ratio from 1.5 to 5 raises power from 374.40 to 1744.37 kW and discharge temperature from 63.58 to 174.63 °C. The 150 °C dashed line is an illustrative temperature constraint; an actual allowable temperature must come from the selected machine and service.',True)
caption(14,'compressor_performance_map.png','Illustrative analytic head curves around a calculated thermodynamic point; no surge boundary is established',
        'The five speed families are the explicit polynomial/affinity illustration in the code, anchored to the computed point of 3159.7 m³/hr and 150.14 kJ/kg. They are not extracted manufacturer curves or an installed compressor rating. The publication view omits the code’s independently invented surge series because it does not establish a stability boundary on those curves. A throughput optimizer needs a calibrated chart and measured surge data before using a speed or surge constraint.',True)
caption(14,'compressor_speed_sensitivity.png','Fixed-pressure-ratio NeqSim power sweep and a separate cubic affinity-law reference',
        'At the fixed 10-to-30 bara pressure ratio, 30 °C suction and prescribed 80% polytropic efficiency, calculated power increases linearly from 833.97 to 3335.88 kW over 15–60 t/hr. The red cubic reference is anchored at 40 t/hr and describes a different similarity trajectory with changing head; it is not a fit to these fixed-pressure-ratio results. The flat efficiency trace is an input assumption.',True)
caption(15,'compressor_map_complete.png','Illustrative polynomial compressor map, with nonphysical extrapolation rejected and the boundary explicitly assumed',
        'These are teaching polynomials at five assumed speeds, not NeqSim-derived or manufacturer performance data. Of 100 paired head/efficiency samples, 99 meet positive-head and 0 < efficiency ≤ 100% bounds. The 70% speed point at 4252.5 m³/hr predicts −2.609% efficiency and is rejected from both panels; it was previously hidden by the axis range. The dashed curve simply joins the third sample on each speed line and is an assumed boundary, not validated surge onset. The nominal fixture basis is 4500 m³/hr, 105 kJ/kg, 80% efficiency and 11500 rpm.',True)
caption(18,'gt_ambient_performance.png','Available shaft power and fuel demand versus ambient temperature at 20 MW shaft demand',
        'This illustrative gas-turbine package model retains a fixed 20 MW shaft demand. Available power decreases from 37.35 to 24.75 MW over −20 to 40 °C. The right panel shows fuel demand, not efficiency: it reaches a shallow minimum near 30 °C before increasing. That shape follows the assumed ambient and part-load corrections; it is not a universal gas-turbine performance trend or an OEM guarantee.')
caption(19,'gcv_wobbe_vs_ngl.png','Calculated GCV and superior Wobbe index versus C₂+ content on the declared ISO6976 basis',
        'For C₂+ increasing from 2 to 15 mol%, GCV rises from 37.677 to 43.405 MJ/Sm³ and superior Wobbe index from 49.114 to 52.372 MJ/Sm³. The mixture assigns C₂+ as 60% ethane, 25% propane and 15% n-butane, with fixed 1% nitrogen and 1.5% CO₂. The reference basis is 15 °C volume and 25 °C combustion. These points come from the exact published calculation and satisfy the same-basis Wobbe identity; they do not certify custody-transfer metering.')
caption(19,'pipeline_sizing_dp_vs_diameter.png','Accepted 300 km pipeline pressure-drop and inlet-velocity results at 15 MSm³/day',
        'All seven sampled diameters have a finite positive outlet-pressure solution for the stated horizontal pipe, 150 bara/40 °C inlet and 5 μm roughness. Increasing internal diameter from 24 to 42 inches decreases pressure drop from 40.394 to 2.168 bar and inlet gas velocity from 3.585 to 1.171 m/s. Pressure positivity is only a domain check: an arrival-pressure specification, thermal analysis and lifecycle costs are still required to choose a diameter.')
caption(17,'valve_characteristics_curves.png','Idealized normalized Cv equations: linear, equal-percentage R = 50, and square-root quick opening',
        'The figure evaluates the three stated equations, not measured valve data. At 50% travel their normalized capacities are 50%, 14.14% and 70.71%, respectively. The equal-percentage endpoint of 1/R = 2% is the minimum controllable-capacity model, not a shutoff-leakage prediction. The square-root curve is an illustrative quick-opening approximation; installed flow also depends on the changing system pressure drop.')
assert len(images)==11
for r in images:
    n=r['source'].get('chapter',17);cp=chap(n)
    r['current_chapter_sha256']=sha(cp)
    r['caption_evidence']=next(c for c in changes if c['chapter']==n and c['figure']==Path(r['path']).name)
report={'status':'pending_final_visual_review','created_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Eleven placed numerical manuscript assets in Chapters 10,14,15,17,18,19. Independent of the 104 notebook figures and earlier frozen repair ledger.',
        'method':'Exact-source replay with observational figure-array capture; accepted literal hook arrays; explicit analytical fixture; visual inspection by the reviewing agent.',
        'images':images,'removed_placements':[],'prose_changes':changes,'manuscript_code_unchanged':True,
        'renderer':str(Path(__file__).relative_to(BOOK)),'renderer_sha256':sha(Path(__file__))}
write(OUT/'final_original_asset_review.json',report)
print('Prepared 11 accepted/explicitly scoped replacements and precise captions. Final visual review pending.')
