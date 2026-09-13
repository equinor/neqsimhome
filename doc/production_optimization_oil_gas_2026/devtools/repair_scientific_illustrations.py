"""Replace misleading legacy artwork with explicit, checked teaching figures.

These figures are analytical illustrations unless their recorded provenance
identifies an executed NeqSim calculation or independent reference comparison.
Chapter source/captions are integrated separately after the authors freeze text.
"""
from pathlib import Path
import hashlib
import json
import shutil
import sys

BOOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / '.build/python_packages'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

OUT = BOOK / 'verification/scientific_revision'
plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10, 'axes.titlesize':12,
                     'axes.labelsize':10, 'legend.fontsize':9, 'axes.spines.top':False,
                     'axes.spines.right':False, 'savefig.facecolor':'white'})
records=[]
colors=['#087f8c','#b55239','#5462a6','#549b55']

def chapter(n):
    return next((BOOK / 'chapters').glob(f'ch{n:02d}_*'))

def save(n, name, fig, caption, discussion, data=None, checks=None, basis='analytical teaching illustration'):
    path=chapter(n)/'figures'/name
    path.parent.mkdir(exist_ok=True)
    fig.savefig(path,dpi=210,bbox_inches='tight')
    plt.close(fig)
    records.append(dict(chapter=chapter(n).name, file=name, path=str(path.relative_to(BOOK)),
                        sha256=hashlib.sha256(path.read_bytes()).hexdigest(), caption=caption,
                        discussion=discussion, basis=basis, data=data or {}, checks=checks or {}))

def axes(title, xlabel, ylabel, size=(7.6,4.3)):
    fig, ax=plt.subplots(figsize=size)
    ax.set(title=title,xlabel=xlabel,ylabel=ylabel)
    ax.grid(alpha=.2)
    return fig,ax

def diagram(title, size=(10,5)):
    fig,ax=plt.subplots(figsize=size)
    ax.set(xlim=(0,1),ylim=(0,1)); ax.axis('off'); ax.set_title(title,pad=12)
    return fig,ax

def box(ax,x,y,w,h,label,color='#dceef0'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.007,rounding_size=0.012',
                               facecolor=color,edgecolor='#47626b',linewidth=1.1))
    ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=9)

def arrow(ax,a,b,label='',color='#47626b',offset=(0,.025),style='-'):
    ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color=color,lw=1.4,linestyle=style))
    if label: ax.text((a[0]+b[0])/2+offset[0],(a[1]+b[1])/2+offset[1],label,
                      ha='center',va='bottom',fontsize=8,color=color)

# Correct a reversed Horner buildup trend using its stated analytical equation.
tp=100.; dt=np.geomspace(.1,10000,200); ratio=(tp+dt)/dt
pstar=330.; slope=10.; pressure=pstar-slope*np.log10(ratio)
assert np.all(np.diff(pressure)>0) and pressure[-1]<pstar
fig,ax=axes('Illustrative Horner buildup: fixed preceding production time',
            'Horner ratio (tp + Δt) / Δt (dimensionless)','Shut-in pressure (bara)')
ax.semilogx(ratio,pressure,color=colors[0]);ax.invert_xaxis()
ax.axhline(pstar,ls='--',color='#666',label='Extrapolated pressure, 330 bara')
ax.legend();ax.text(.04,.60,'p = 330 − 10 log10(Horner ratio)\ntp = 100 h; specified semilog model',transform=ax.transAxes,fontsize=9)
save(4,'horner_plot.png',fig,'Analytical Horner buildup illustration with increasing shut-in time toward the right',
     'As shut-in time increases, the Horner ratio approaches one and the modeled pressure rises toward 330 bara. The 10 bar-per-decade slope and 100 h preceding production time are specified teaching inputs; no measured well test is represented.',
     dict(tp_h=tp, slope_bar_per_decade=slope, pressure_star_bara=pstar),dict(pressure_increases_with_shutin_time=True))

# Correct diameter ordering with a transparent single-phase pressure-loss model.
q=np.linspace(0,5000,501); pr=300.; qmax=5000.; ipr=pr*(1-q/qmax)
fig,ax=axes('Illustrative nodal analysis: diameter dependence', 'Liquid production (m³/d)','Required / available flowing BHP (bara)')
ax.plot(q,ipr,color='#222',label='Linear IPR: PI = 16.667 m³/(d bar)')
roots=[]
for diameter,color in zip((3.5,4.5,5.5),colors):
    k=130./(3000.**2)*(3.5/diameter)**5
    vlp=60.+k*q*q
    root=(-pr/qmax+np.sqrt((pr/qmax)**2+4*k*(pr-60)))/(2*k)
    residual=pr*(1-root/qmax)-(60+k*root*root)
    assert abs(residual)<1e-9
    roots.append(root)
    ax.plot(q,vlp,color=color,label=f'{diameter:.1f} inch; friction ∝ D⁻⁵')
    ax.plot(root,pr*(1-root/qmax),'o',color=color)
assert np.all(np.diff(roots)>0)
ax.set_ylim(0,320);ax.legend(loc='upper right',fontsize=8)
save(4,'nodal_analysis.png',fig,'Checked analytical nodal intersections with fixed hydrostatic head and diameter-dependent friction',
     'This illustrative incompressible limit holds wellhead plus hydrostatic pressure at 60 bara and friction proportional to rate squared divided by diameter to the fifth power. Larger diameter lowers the required BHP at a fixed rate and raises the intersection rate. Multiphase wells require the coupled model developed in Chapters 5–8.',
     dict(diameters_in=[3.5,4.5,5.5],intersection_m3_day=roots),dict(root_pressure_residual_bar=1e-9,diameter_order_verified=True))

# A self-consistent pressure derivative, with an actual radial-flow plateau.
t=np.geomspace(.001,1000,600); transition=.1; late=100.
dp=10*np.log1p(t/transition)+5*np.maximum(t/late-1,0)**2
derivative=10*t/(transition+t)+10*(t/late)*np.maximum(t/late-1,0)
numeric=np.gradient(dp,np.log(t)); mid=(t>.3)&(t<30)
assert np.max(abs(numeric[mid]-derivative[mid])/derivative[mid])<.002
fig,ax=axes('Analytical pressure-transient illustration', 'Elapsed time (h)','Pressure change / derivative (bar)')
ax.loglog(t,dp,label='Specified pressure change Δp',color=colors[0])
ax.loglog(t,derivative,'--',label='d(Δp) / d ln(t)',color=colors[1])
ax.axhline(10,color='#666',ls=':',label='Radial plateau, approximately 10 bar')
ax.legend(loc='upper left');ax.set_ylim(.03,2000)
save(5,'log_diagnostic.png',fig,'Analytical log–log pressure and logarithmic-derivative curves with a radial-flow plateau',
     'The early-time pressure and derivative approach a unit-slope trend; the derivative then approaches 10 bar before a deliberately imposed late boundary response. The derivative is evaluated from the same pressure function and checked by numerical differentiation. This is a diagnostic-shape illustration, not a reservoir test interpretation.',
     dict(pressure_formula='10*ln(1+t/0.1)+5*max(t/100-1,0)^2'),dict(derivative_relative_error_below=.002))

# Correct depletion water cut from the plotted phase volumes themselves.
years=np.arange(2026,2047); oil=18*np.exp(-.065*(years-2026)); water=3+1.0*(years-2026)
wc=100*water/(oil+water);assert np.all((wc>=0)&(wc<=100))
fig,ax=axes('Specified oil and water lifecycle scenario','Year','Liquid production (10³ m³/d)')
ax.bar(years-.2,oil,width=.4,label='Oil',color=colors[0]);ax.bar(years+.2,water,width=.4,label='Water',color='#aecdd6')
right=ax.twinx();right.plot(years,wc,color=colors[1],label='Water cut');right.set_ylabel('Water cut at same liquid reference basis (%)');right.set_ylim(0,100)
ax.legend(loc='upper left');right.legend(loc='lower right');fig.tight_layout()
save(13,'water_lifecycle_profile.png',fig,'Specified oil/water production scenario with water cut calculated from the same liquid volumes',
     'Water cut is water volume divided by total liquid volume on the common stated reference basis. The scenario uses an assumed exponential oil-rate decline and linear water-rate increase; it illustrates treatment load and is not a NeqSim reservoir forecast or field history.',
     dict(year=years.tolist(),oil_thousand_m3_day=oil.tolist(),water_thousand_m3_day=water.tolist(),water_cut_pct=wc.tolist()),dict(water_cut_identity=True))

# Correct noncrossing composite curves with a defined minimum temperature gap.
h=np.array([0.,2.,5.,8.,12.]); cold=np.array([30.,55.,90.,125.,155.]); hot=np.array([65.,85.,115.,165.,205.])
gap=hot-cold;assert min(gap)==25 and np.all(np.diff(hot)>0) and np.all(np.diff(cold)>0)
fig,ax=axes('Illustrative unshifted composite curves','Cumulative enthalpy coordinate (MW)','Temperature (°C)')
ax.plot(h,hot,'o-',color=colors[1],label='Hot composite');ax.plot(h,cold,'s-',color=colors[0],label='Cold composite')
ax.annotate('',xy=(5,115),xytext=(5,90),arrowprops=dict(arrowstyle='<->',color='#222'))
ax.text(5.3,102.5,'Minimum gap\n25 K',va='center',fontsize=9);ax.legend(loc='upper left')
save(16,'composite_curves.png',fig,'Specified noncrossing hot and cold composite curves with a 25 K minimum vertical temperature gap',
     'Both composites increase with their cumulative enthalpy coordinate. Their closest vertical separation is 25 K at 5 MW in this constructed example. Utility targets require the underlying stream heat-capacity flows, temperature intervals and enthalpy alignment; this diagram alone is not a solved plant heat-integration study.',
     dict(enthalpy_MW=h.tolist(),hot_C=hot.tolist(),cold_C=cold.tolist()),dict(minimum_gap_K=25))

# Thermodynamically consistent ideal Brayton cycle, all four legs defined.
gamma=1.4;cp=1.005;rp=10.;T1=300.;T3=1400.;T2=T1*rp**((gamma-1)/gamma);T4=T3/rp**((gamma-1)/gamma)
s1=0.;s2=0.;s3=cp*np.log(T3/T2);s4=s3
assert abs(T2/T1-T3/T4)<1e-12
efficiency=1-(T4-T1)/(T3-T2);assert abs(efficiency-(1-rp**(-(gamma-1)/gamma)))<1e-12
fig,ax=axes('Ideal constant-cp Brayton cycle','Specific entropy relative to state 1 (kJ/(kg K))','Temperature (K)')
ax.plot([0,0],[T1,T2],color=colors[0]);temp=np.linspace(T2,T3,80);ax.plot(cp*np.log(temp/T2),temp,color=colors[1])
ax.plot([s3,s4],[T3,T4],color=colors[0]);temp=np.linspace(T1,T4,80);ax.plot(cp*np.log(temp/T1),temp,color=colors[1])
for n,(s,temp) in enumerate(zip([s1,s2,s3,s4],[T1,T2,T3,T4]),1): ax.plot(s,temp,'o',color='#222');ax.annotate(str(n),(s,temp),xytext=(6,7),textcoords='offset points')
ax.margins(.12);ax.text(.05,.9,'Pressure ratio = 10\nγ = 1.4; cp = 1.005 kJ/(kg K)',transform=ax.transAxes,va='top',fontsize=9)
save(18,'brayton_cycle_ts.png',fig,'Checked ideal Brayton cycle with isentropic compression/expansion and constant-pressure heat transfer',
     f'The two vertical legs are isentropic and both use pressure ratio 10. Constant-pressure heating and cooling satisfy ds = cp dT/T. With the specified constant heat capacities, thermal efficiency is {100*efficiency:.2f} percent. Real turbine performance requires irreversible component models, pressure losses and temperature-dependent properties.',
     dict(T_K=[T1,T2,T3,T4],pressure_ratio=rp,cp_kJ_kg_K=cp,efficiency=efficiency),dict(pressure_ratio_consistency=True,cycle_efficiency_identity=True))

# Show overload; utilization is never clipped at one for visual convenience.
rate=np.linspace(40,120,41); capacities=[105.,92.,100.]
fig,ax=axes('Specified independent equipment limits','Demand rate (% of reference rate)','Utilization (%)')
for cap,name,color in zip(capacities,['Separator','Compressor','Dehydration'],colors):ax.plot(rate,100*rate/cap,label=f'{name}: limit {cap:g}%',color=color)
ax.axhline(100,color='#222',ls='--',label='Declared limit');ax.axhline(90,color='#b48c3c',ls=':',label='Illustrative warning at 90%');ax.legend(fontsize=8)
save(20,'utilization_vs_production.png',fig,'Unclipped utilization for three explicitly assumed independent equipment ratings',
     'Utilization is demand divided by a fixed rating. At a demand above 92 percent of reference, the assumed compressor limit is exceeded; curves remain above 100 percent so the overload is visible. These ratings illustrate constraint arithmetic and do not establish installed-equipment capacity.',
     dict(capacities_pct_reference=capacities),dict(overload_values_retained=True))

# Correct a false Pareto front and a dominated selected solution.
rng=np.random.default_rng(2409); production=np.linspace(3000,5000,90)
power=14+.0000008*(production-3000)**2
cloud_x=rng.uniform(3000,5000,160);cloud_y=14+.0000008*(cloud_x-3000)**2+rng.uniform(.4,8,160)
points=np.column_stack((np.r_[production,cloud_x],np.r_[power,cloud_y]))
front=np.array([not np.any((points[:,0]>=x)&(points[:,1]<=y)&((points[:,0]>x)|(points[:,1]<y))) for x,y in points])
pf=points[front];pf=pf[np.argsort(pf[:,0])];score=((5000-pf[:,0])/2000)**2+((pf[:,1]-14)/3.2)**2;selected=pf[np.argmin(score)]
assert len(pf)==90 and not np.any((points[:,0]>=selected[0])&(points[:,1]<=selected[1])&((points[:,0]>selected[0])|(points[:,1]<selected[1])))
fig,ax=axes('Enumerated synthetic production–power trade-off','Assumed oil production (m³/d)','Assumed shaft-power demand (MW)')
ax.scatter(cloud_x,cloud_y,s=15,alpha=.4,color='#8fbcc7',label='Dominated alternatives');ax.plot(pf[:,0],pf[:,1],color=colors[1],label='Nondominated alternatives')
ax.plot(*selected,'*',ms=15,color=colors[2],label='Declared normalized-distance choice');ax.legend(loc='upper left',fontsize=8)
save(22,'pareto_front_oil_vs_power.png',fig,'Explicitly enumerated synthetic Pareto set; the selected point passes a nondominance check',
     'The alternatives use the declared teaching relation P = 14 + 8×10⁻⁷(q − 3000)² MW, with additional dominated alternatives placed above it. Oil rate is maximized and power minimized. The selected point minimizes squared normalized distance to the ideal objective values within the enumerated front; it is a preference choice, not a NeqSim field optimum.',
     dict(points=points.tolist(),selected=selected.tolist()),dict(front_points=90,selected_nondominated=True))

# Correct anti-surge action direction, using a purely illustrative local map.
fig,ax=axes('Illustrative anti-surge action on a local speed curve','Actual inlet flow (m³/h)','Polytropic head (kJ/kg)')
flow=np.linspace(4500,12000,200);head=100-2e-7*(flow-6500)**2
ax.plot(flow,head,color=colors[0],label='Specified speed curve');ax.axvline(5000,color=colors[1],label='Illustrative surge boundary');ax.axvline(5500,color='#ad8536',ls='--',label='Illustrative control margin')
start=5600.;end=8500.;ax.annotate('',xy=(end,100-2e-7*(end-6500)**2),xytext=(start,100-2e-7*(start-6500)**2),arrowprops=dict(arrowstyle='->',color=colors[2],lw=2))
ax.text(7700,102,'More recycle increases\ncompressor throughflow',ha='center',fontsize=9);ax.set_ylim(80,111);ax.legend(loc='lower left',fontsize=8)
save(29,'ch20_compressor_map_antisurge.png',fig,'Conceptual anti-surge action: opening recycle raises compressor inlet throughflow toward the right',
     'The arrow indicates increased compressor throughflow when recycle opens, even though net export can decrease. The speed curve, surge boundary and margin shown here are specified illustrations. Actual control design must use the installed map and evaluate the connected pressure system and valve dynamics.',
     dict(start_m3_hr=start,end_m3_hr=end),dict(recycle_arrow_increases_compressor_flow=True))

# Transparent synthetic monitoring data; never mislabel generated values measured.
time=np.linspace(0,48,481);truth=65+4*np.sin(time/5);noise=rng.normal(0,.35,len(time));bias=np.where((time>=24)&(time<36),3.,0.)
observed=truth+noise+bias;estimate=np.zeros_like(time)
for i in range(20,len(time)):estimate[i]=np.mean((observed-truth)[i-19:i+1])
residual=observed-(truth+estimate)
interval=(time>=28)&(time<35);assert abs(np.mean(residual[interval]))<.2
fig,(ax,bx)=plt.subplots(2,1,figsize=(8.2,5.5),sharex=True)
ax.plot(time,observed,color='#9fb7c8',lw=.8,label='Synthetic sensor fixture');ax.plot(time,truth,color=colors[0],label='Specified reference');ax.plot(time,truth+estimate,color=colors[1],label='20-sample residual-mean correction')
ax.set(title='Synthetic monitoring exercise with a known injected offset',ylabel='Temperature (°C)');ax.legend(fontsize=8,loc='upper left',ncol=2)
bx.plot(time,observed-truth,color='#9fb7c8',label='Raw residual');bx.plot(time,residual,color=colors[1],label='Corrected residual');bx.set(xlabel='Time (h)',ylabel='Temperature residual (K)');bx.legend(fontsize=8,loc='upper left')
for a in (ax,bx):a.axvspan(24,36,color='#ddbb80',alpha=.17);a.grid(alpha=.2)
fig.tight_layout()
save(30,'ch21_digital_twin_tracking.png',fig,'Synthetic sensor/model residuals with a known 3 K injected offset and a declared rolling-mean correction',
     'The shaded 24–36 h interval contains an imposed 3 K sensor offset. The correction uses the latest 20 residuals against a specified reference; it lags the offset changes. No field measurements, automated fault diagnosis or calibrated digital twin are claimed. Distinguishing sensor bias from model error needs additional independent evidence.',
     dict(seed=2409,known_offset_K=3,window_samples=20,mean_corrected_residual_K=float(np.mean(residual[interval]))),dict(corrected_mean_error_below_K=.2),basis='checked synthetic statistical teaching exercise')

# Diagrams are deliberately simple and state their omissions.
fig,ax=diagram('Gas conditioning before cryogenic recovery',(10,3.4))
labels=['Inlet liquids\nremoval','Acid-gas\ntreatment','Deep drying /\nmercury control','Cryogenic\nNGL recovery','Residue-gas\ncompression']
for i,label in enumerate(labels):box(ax,.015+i*.198,.4,.175,.28,label); 
for i in range(4):arrow(ax,(.19+i*.198,.54),(.213+i*.198,.54))
ax.text(.5,.15,'Configuration depends on feed contaminants, temperature and product requirements.',ha='center',fontsize=9)
save(12,'gas_processing_overview.png',fig,'Conceptual treatment sequence placing required contaminant removal before cryogenic processing',
     'The sequence locates acid-gas treatment and deep drying upstream of cold equipment. Mercury control is included when required by feed and materials. Product requirements determine the actual treatment train; TEG dehydration alone does not establish a cryogenic water specification.')

fig,ax=diagram('Production optimization: verify before implementation',(10,4.8))
steps=['Acquire and\nreconcile data','Update / calibrate\nprocess model','Optimize within\ndeclared limits','Verify and replay\nselected decisions','Review and authorize\nimplementation','Monitor response\nand model residuals']
coords=[(.02,.63),(.355,.63),(.69,.63),(.69,.18),(.355,.18),(.02,.18)]
for (x,y),label in zip(coords,steps):box(ax,x,y,.285,.22,label)
for i in (0,1):arrow(ax,(coords[i][0]+.285,.74),(coords[i+1][0],.74))
arrow(ax,(.832,.63),(.832,.40));arrow(ax,(.69,.29),(.64,.29));arrow(ax,(.355,.29),(.305,.29));arrow(ax,(.162,.40),(.162,.63),'Feedback',offset=(.06,0))
save(30,'ch21_rto_cycle.png',fig,'Operational optimization cycle with verification and authorization before implementation',
     'Each recommendation is checked against the accepted model and operating limits before authorized implementation. Monitoring returns new observations to the reconciliation step. The diagram specifies a workflow; it does not demonstrate a live plant connection.')

fig,ax=diagram('Simplified amine solvent circuit and heat recovery',(10,5.4))
for x,y,w,h,label in [(.03,.57,.15,.23,'Absorber'),(.27,.57,.14,.23,'Rich-solvent\nflash drum'),(.49,.57,.15,.23,'Rich side of\nlean/rich HX'),(.76,.57,.18,.23,'Regenerator'),(.49,.12,.15,.23,'Lean side of\nlean/rich HX'),(.27,.12,.14,.23,'Lean cooler'),(.03,.12,.15,.23,'Lean pump')]:box(ax,x,y,w,h,label)
arrow(ax,(.0,.69),(.03,.69),'Sour gas',offset=(.025,.07));arrow(ax,(.105,.8),(.105,.98),'Sweet gas',offset=(.07,0))
arrow(ax,(.18,.69),(.27,.69),'Rich');arrow(ax,(.41,.69),(.49,.69));arrow(ax,(.64,.69),(.76,.69))
arrow(ax,(.34,.80),(.34,.98),'Flash gas',offset=(.07,0))
arrow(ax,(.85,.8),(.85,.98),'Acid gas',offset=(.07,0));arrow(ax,(.85,.57),(.85,.235),'Lean',offset=(.04,0));arrow(ax,(.85,.235),(.64,.235));arrow(ax,(.49,.235),(.41,.235));arrow(ax,(.27,.235),(.18,.235));arrow(ax,(.105,.35),(.105,.57))
arrow(ax,(.565,.35),(.565,.57),'Heat',color='#b55239',offset=(.055,0),style='--')
arrow(ax,(.69,.47),(.78,.57),'Reboiler heat',color='#b55239',offset=(-.04,0))
ax.text(.83,.04,'Overhead condensation and\nreboiler circulation omitted.',ha='center',fontsize=8)
save(33,'ch22_amine_unit_pfd.png',fig,'Simplified amine circuit with separate rich/lean sides of solvent heat recovery',
     'Rich solvent is depressurized, preheated by regenerated lean solvent, and sent to the regenerator. The hot lean solvent returns through the exchanger, cooler and pump to the absorber. The dashed connection denotes heat transfer, not solvent mixing; condenser/reflux and reboiler circulation are omitted from this conceptual circuit.')

fig,ax=diagram('Verified dry-gas teaching plant: external product boundaries',(11,5.6))
items=[(.02,.65,.15,.20,'Feed\n350 t/h; 70 bara'),(.22,.65,.15,.20,'Inlet\nseparator'),(.43,.65,.19,.20,'Precooling / KO\nGas expansion +\nliquid letdown'),(.69,.65,.15,.20,'Cold\nseparator'),(.69,.25,.15,.20,'Stabilizer\n4.5 MW heat'),(.22,.25,.15,.20,'Inlet\ncondensate'),(.87,.65,.115,.20,'Gas\ncompression\n70 bara')]
for x,y,w,h,label in items:box(ax,x,y,w,h,label)
for a,b in [((.17,.75),(.22,.75)),((.37,.75),(.43,.75)),((.62,.75),(.69,.75)),((.84,.75),(.87,.75)),((.295,.65),(.295,.45)),((.765,.65),(.765,.45))]:arrow(ax,a,b)
arrow(ax,(.69,.35),(.50,.35),'Overhead gas');arrow(ax,(.765,.25),(.765,.08),'Bottoms liquid',offset=(.09,0));arrow(ax,(.985,.75),(1.,.75))
ax.text(.035,.08,'Dry, acid-gas-free input.\nExternal coolers and shaft duties are explicit.\nNo unmodeled heat or shaft recovery credit.',fontsize=8)
save(33,'ch22_onshore_plant_block_diagram.png',fig,'Block diagram of the executed dry-hydrocarbon plant with four external product streams',
     'The four product boundaries are inlet condensate, recompressed residue gas, stabilizer overhead and stabilizer bottoms. Feed and products are reconciled component by component. The separate standalone TEG example and a complete raw-gas pretreatment train are outside this numerical flowsheet.',basis='diagram of the executed Chapter33 flowsheet')

fig,ax=diagram('Gas-only expansion with separate liquid letdown',(10,4.6))
for x,y,w,h,label in [(.02,.43,.16,.24,'Cooled feed\nknockout'),(.31,.69,.18,.22,'Gas\nexpander'),(.31,.14,.18,.22,'Liquid\nletdown valve'),(.61,.43,.17,.24,'Remix and\ncold separator'),(.84,.69,.145,.22,'Residue-gas\ncompression'),(.84,.14,.145,.22,'Liquid\nstabilization')]:box(ax,x,y,w,h,label)
arrow(ax,(.18,.60),(.31,.80),'Gas');arrow(ax,(.18,.49),(.31,.25),'Liquid');arrow(ax,(.49,.80),(.61,.60));arrow(ax,(.49,.25),(.61,.49));arrow(ax,(.78,.60),(.84,.80));arrow(ax,(.78,.49),(.84,.25))
ax.text(.5,.02,'Recovered expander work and compressor demand are accounted separately.',ha='center',fontsize=9)
save(33,'ch22_turboexpander_pfd.png',fig,'Verified process topology with gas-only expansion, liquid bypass letdown, remixing and cold separation',
     'Upstream knockout prevents routing the entire two-phase cooled feed through the gas expander. The liquid takes a throttling bypass and rejoins the expanded gas before separation. The worked model reports expander recovery and compressor demand separately; this diagram does not impose an unmodeled common shaft.',basis='diagram of the executed Chapter33 flowsheet')

# Replace invented experimental markers with independently benchmarked results.
source=OUT/'figures/nist_methane_density_validation.png';target=chapter(2)/'figures/eos_comparison.png'
shutil.copy2(source,target)
records.append(dict(chapter=chapter(2).name,file=target.name,path=str(target.relative_to(BOOK)),
                    sha256=hashlib.sha256(target.read_bytes()).hexdigest(),basis='18 executed comparisons with 9 NIST methane reference-EOS states',
                    caption='SRK and Peng–Robinson methane density compared with independent NIST reference-fluid data at nine states',
                    discussion='The parity and deviation panels compare 300, 350 and 400 K at 1, 50 and 100 bara. Maximum absolute relative deviations are 1.421 percent for SRK and 0.811 percent for Peng–Robinson, within the declared 3 percent teaching budget. These are NIST reference-EOS values, not invented experimental points or a general mixture-accuracy claim. The separate benchmark notebook retains inputs, raw reference tables, computed values and tolerances.',
                    data={'record':'verification/scientific_revision/benchmark_results.json'},checks={'benchmark_status':'passed'}))

# A capacity diagram must not shade the region to the left of surge as accepted.
fig,ax=axes('Specified centrifugal-compressor map geometry','Actual inlet flow (m³/h)','Polytropic head (kJ/kg)')
surge=[];choke=[]
for ratio,color in zip([.8,1.,1.1],colors):
    flow=np.linspace(3000*ratio,9500*ratio,90)
    head=180*ratio**2*(1-.25*(flow/(6000*ratio))**2)
    assert np.all(np.diff(head)<0)
    ax.plot(flow,head,color=color,label=f'{100*ratio:g}% relative speed')
    surge.append([flow[0],head[0]]);choke.append([flow[-1],head[-1]])
surge=np.array(surge);choke=np.array(choke)
ax.plot(*surge.T,'o--',color='#b55239',label='Specified surge endpoints')
ax.plot(*choke.T,'s:',color='#666',label='Specified high-flow endpoints')
ax.plot(6000,135,'*',ms=13,color='#222',label='Illustrative point on 100% curve')
ax.legend(fontsize=8)
save(20,'compressor_capacity_map.png',fig,'Analytical compressor-map illustration with explicit surge and high-flow endpoints',
     'The curves obey the stated similarity form H = 180N²[1 − 0.25(q/(6000N))²] kJ/kg, where N is relative speed. Endpoints are specified for this geometry illustration; there is no shaded region implying that points beyond those bounds are accepted. These curves are not measured vendor data or an installed-machine rating.',
     dict(relative_speeds=[.8,1.,1.1],surge=surge.tolist(),high_flow=choke.tolist()),dict(head_decreases_with_flow=True))

hp=np.linspace(30,90,101);mp=np.linspace(5,30,91);HP,MP=np.meshgrid(hp,mp)
score=1-((HP-60)/30)**2-((MP-15)/15)**2
fig,ax=axes('Specified concave objective: stationary point and feasible domain','HP separator decision (bara)','MP separator decision (bara)')
cs=ax.contourf(HP,MP,score,levels=15,cmap='viridis');fig.colorbar(cs,ax=ax,label='Algebraic teaching objective (dimensionless)')
ax.plot(60,15,'*',ms=15,color='white',mec='#222');ax.text(62,15,'Stationary maximum',color='#18252f',fontsize=9)
save(22,'separator_pressure_contour.png',fig,'Explicit algebraic objective surface for illustrating a constrained pressure-search problem',
     'The contour is the declared dimensionless function 1 − [(pHP − 60)/30]² − [(pMP − 15)/15]², whose gradient vanishes at 60 and 15 bara and whose Hessian is negative definite. It explains a search landscape; it does not represent computed oil recovery. Actual separation optima require the verified process calculations elsewhere in the book.',
     dict(stationary_HP_bara=60,stationary_MP_bara=15,hessian_diagonal=[-2/900,-2/225]),dict(negative_definite_hessian=True))

pwf=np.linspace(0,300,250);ratio=pwf/300
fig,ax=axes('Specified inflow correlations: different assumed well parameters','Liquid production (m³/d)','Flowing bottomhole pressure (bara)')
ax.plot(20*(300-pwf),pwf,label='Linear PI = 20 m³/(d bar)',color=colors[0])
ax.plot(4500*(1-.2*ratio-.8*ratio**2),pwf,label='Vogel: AOF = 4500 m³/d',color=colors[1])
ax.plot(5500*(1-ratio**2)**.8,pwf,label='Fetkovich: AOF = 5500 m³/d, n = 0.8',color=colors[2])
ax.legend(fontsize=8)
save(4,'ipr_curves.png',fig,'Analytical PI, Vogel and Fetkovich inflow curves with all assumed parameters stated',
     'Each equation gives zero rate at 300 bara flowing BHP. At zero BHP the respective absolute-open-flow extrapolations are 6000, 4500 and 5500 m³/d. Different parameters are deliberately used to illustrate the forms; this is not a fit of three models to one well or permission to produce at zero BHP.',
     dict(reservoir_bara=300,PI_m3_day_bar=20,Vogel_AOF_m3_day=4500,Fetkovich_AOF_m3_day=5500,Fetkovich_exponent=.8),dict(zero_drawdown_zero_rate=True))

injection=np.linspace(0,200,301);oil=500+2000*(1-np.exp(-injection/30));cost_equivalent=5.;optimum=30*np.log(2000/(30*cost_equivalent))
assert abs(2000/30*np.exp(-optimum/30)-cost_equivalent)<1e-12
fig,ax=axes('Explicit saturating lift response and assumed cost trade-off','Lift-gas rate (10³ standard m³/d)','Assumed oil production (m³/d)')
ax.plot(injection,oil,color=colors[0]);ax.plot(optimum,500+2000*(1-np.exp(-optimum/30)),'o',color=colors[1])
ax.axvline(optimum,color=colors[1],ls=':');ax.text(.38,.10,'q = 500 + 2000[1 − exp(−g/30)]\nCost-equivalent slope = 5 m³ oil per 10³ m³ gas',transform=ax.transAxes,fontsize=9,bbox=dict(facecolor='white',edgecolor='none',pad=2))
ax.annotate(f'Stationary net-benefit point\ng = {optimum:.2f}',(optimum,500+2000*(1-np.exp(-optimum/30))),xytext=(105,1600),arrowprops=dict(arrowstyle='->'),fontsize=9)
save(5,'gas_lift_performance.png',fig,'Analytical gas-lift illustration with an explicit marginal cost-equivalent assumption',
     f'The declared response has diminishing incremental oil yield. With the stated cost-equivalent slope of 5 m³ oil per thousand standard m³ lift gas, the stationary net-benefit injection is {optimum:.2f} thousand standard m³/d. This synthetic trade-off is checked by differentiation; it is not a calibrated lift curve, a current market-price forecast or a native gas-lift allocation result.',
     dict(response='500+2000*(1-exp(-g/30))',cost_equivalent=5,stationary_injection_thousand_Sm3_day=optimum),dict(marginal_condition_residual_below=1e-12))

(OUT/'illustration_repairs.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print(f'Rebuilt {len(records)} scientifically corrected illustrations; captions await author freeze.')
