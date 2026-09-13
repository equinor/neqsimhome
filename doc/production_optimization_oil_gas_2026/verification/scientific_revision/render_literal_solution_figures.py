"""Render three Chapter22 plots from accepted exact-literal solution records."""
from pathlib import Path
import sys,json,hashlib,re
H=Path(__file__).resolve().parent;B=H.parents[1]
sys.path.insert(0,str(B/'.build/python_packages'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.labelsize':10,'legend.fontsize':9,'axes.spines.right':False,'axes.spines.top':False})
report_path=H/'ch22_solution_checks.json';report=json.loads(report_path.read_text(encoding='utf-8'))
assert report['all_targeted_checks_passed']
chapter=next((B/'chapters').glob('ch22_*'));records=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def entry(n):return next(e for e in report['entries'] if e['number']==n)
def observed(n):return entry(n)['checks'][-1]['observed']
def save(fig,name,n,data,caption,discussion,old_name):
    path=chapter/'figures'/name
    fig.savefig(path,dpi=220,bbox_inches='tight');plt.close(fig)
    record={'path':str(path),'sha256':sha(path),'source_report':str(report_path),'source_report_sha256':sha(report_path),'literal_fence':n,'literal_code_sha256':entry(n)['code_sha256'],'data':data,'caption':caption,'discussion':discussion,'replaces_chapter_link':old_name}
    records.append(record)

r=observed(1);q=np.linspace(0,3.5,160);p=np.sqrt(250**2-(q/.0035)**(1/.85))
qt=[.5,1,1.5,2,2.5,3,3.5];accepted=[(flow,pressure) for flow,pressure in zip(qt,r['TPR_required_BHP_bara']) if pressure is not None]
accepted.append((r['rate_MSm3_day'],r['BHP_bara']));accepted.sort()
fig,ax=plt.subplots(figsize=(7.4,4.6))
ax.plot(q,p,color='#087f8c',label='Specified backpressure IPR')
ax.plot(*np.array(accepted).T,'o-',color='#b55239',label='Forward NeqSim tubing solve')
ax.plot(r['rate_MSm3_day'],r['BHP_bara'],'*',ms=15,color='#273c70',label='Coupled operating point')
ax.axhline(250,ls=':',color='#777',label='Specified reservoir pressure')
ax.text(.97,.16,'No 80 bara arrival solution below 250 bara BHP\nat tested rates 2.5, 3.0 and 3.5 MSm³/day.',transform=ax.transAxes,ha='right',fontsize=8.5,bbox={'facecolor':'white','edgecolor':'none'})
ax.set(xlabel='Gas rate (MSm³/day)',ylabel='Bottomhole pressure (bara)',title='Checked IPR and forward upward tubing model')
ax.legend(loc='center left',bbox_to_anchor=(.015,.55),fontsize=8);ax.grid(alpha=.2)
save(fig,'ch22_verified_nodal_solution.png',1,{'analytic_IPR_rate_MSm3_day':q.tolist(),'analytic_IPR_BHP_bara':p.tolist(),'accepted_TPR_rate_BHP':accepted,'result':r},
     'Checked operating point from the specified IPR and a forward 3000 m upward NeqSim tubing calculation',
     f"The coupled solution is {r['rate_MSm3_day']:.5f} MSm³/day at {r['BHP_bara']:.3f} bara bottomhole pressure and {r['WHP_bara']:.3f} bara wellhead pressure. Friction and elevation increase required BHP with rate. Tested rates of 2.5–3.5 MSm³/day cannot reach the 80 bara target below the 250 bara reservoir pressure and are excluded from the curve. This is a numerical consistency check for the declared IPR and steady tubing model; calibration and a thermal wellbore model remain separate requirements.",
     'nodal_analysis_operating_point.png')

r=observed(6);data=r['sampled_results'];P=np.array([s['P_inter'] for s in data]);W=np.array([s['value'] for s in data])
assert np.max(abs(W[:,0]-W[:,1]-W[:,2]))<1e-10
fig,axes=plt.subplots(1,2,figsize=(9,4.2))
axes[0].plot(P,W[:,0],'o-',color='#087f8c',label='Total shaft power')
axes[0].plot(r['best_interstage_bara'],r['best_power_MW'],'*',ms=14,color='#b55239',label='Lowest sampled power')
axes[0].axvline(r['geometric_mean_reference_bara'],ls=':',color='#666',label='Equal-ratio reference')
axes[1].plot(P,W[:,1],'o-',color='#087f8c',label='Stage 1')
axes[1].plot(P,W[:,2],'s-',color='#b55239',label='Stage 2')
for ax in axes:ax.set(xlabel='Interstage pressure (bara)',ylabel='Shaft power (MW)');ax.grid(alpha=.2);ax.legend(fontsize=8)
fig.suptitle('Two-stage polytropic compression with explicit intercooling');fig.tight_layout()
save(fig,'ch22_verified_interstage_power.png',6,{'interstage_bara':P.tolist(),'total_stage1_stage2_MW':W.tolist(),'result':r},
     'Verified two-stage power sweep at 25 bara suction and 150 bara discharge, using the specified polytropic efficiencies',
     f"The lowest sampled total duty is {r['best_power_MW']:.3f} MW at {r['best_interstage_bara']:.0f} bara. Raising interstage pressure transfers duty from stage 2 to stage 1. The equal-ratio reference is {r['geometric_mean_reference_bara']:.2f} bara; unequal efficiencies, different stage-inlet temperatures and real-fluid properties shift the sampled minimum. Each stage and the whole cooled boundary satisfy mass, component and first-law checks. Refine the pressure grid and add equipment maps and temperature limits before an operating recommendation.",
     'interstage_pressure_optimization.png')

r=observed(7);data=r['all_points'];oil=np.array([v['oil_rate']/1000 for v in data]);power=np.array([v['power'] for v in data]);front=r['nondominated_points']
fig,ax=plt.subplots(figsize=(7.4,4.6));ax.plot(oil,power,'o-',color='#087f8c',label='Eleven checked pressure cases')
for v in front:ax.plot(v['oil_rate']/1000,v['power'],'*',ms=15,color='#b55239',label=f"Nondominated sample: {v['P_sep']} bara")
ax.set(xlabel='Separator oil mass (t/h)',ylabel='Compressor shaft power (MW)',title='Actual sampled objectives: one point dominates this sweep')
ax.legend(loc='upper right',fontsize=8);ax.grid(alpha=.2)
save(fig,'ch22_verified_pareto_samples.png',7,{'points':data,'nondominated':front},
     'Actual separator/compressor sweep with exhaustive nondominance checking; the sampled set has one nondominated point',
     f"At 70 bara the sample gives {front[0]['oil_rate']/1000:.3f} t/h separator oil and {front[0]['power']:.3f} MW compression duty, dominating the other ten tested pressures in these two objectives. Higher pressure retains more material in the separator liquid while reducing compression ratio. The calculation therefore does not demonstrate an oil–power trade-off. Liquid is measured at separator conditions; stock-tank stabilization, well response and additional constraints could change the objective landscape.",
     'pareto_front_oil_vs_power.png')

(H/'literal_solution_figure_data.json').write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf-8')
manuscript=chapter/'chapter.md';text=manuscript.read_text(encoding='utf-8')
for r in records:
    new=f"![{r['caption']}](figures/{Path(r['path']).name})\n\n{r['discussion']}"
    pattern=r'^!\[[^\n]*\]\(figures/'+re.escape(r['replaces_chapter_link'])+r'\)'
    if re.search(pattern,text,re.M):text=re.sub(pattern,lambda m:new,text,count=1,flags=re.M)
    else:assert f"(figures/{Path(r['path']).name})" in text,'Missing figure placement'
manuscript.write_text(text,encoding='utf-8')
print('Created three figures from full-precision accepted arrays and updated Chapter22 placements.')
