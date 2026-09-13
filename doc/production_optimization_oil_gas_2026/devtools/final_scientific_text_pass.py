"""Final scientific consistency and callable data-quality fixture checks."""
import re,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];changes=[]
def load(n):
 global t,p,chapter,markers
 chapter=n;p=next((B/'chapters').glob(f'ch{n:02}*/chapter.md'));t=p.read_text(encoding='utf-8-sig')
 b=B/'.build/backups/scientific_revision'/p.parent.name/'final_text_input.md';b.parent.mkdir(parents=True,exist_ok=True)
 if not b.exists():b.write_text(t,encoding='utf-8')
 markers=re.findall(r'<!-- reviewed-notebook-results:start -->.*?<!-- reviewed-notebook-results:end -->',t,re.S)
 for i,m in enumerate(markers):t=t.replace(m,f'PROTECTED_RESULTS_{i}')
def r(a,b):
 global t
 if a in t:t=t.replace(a,b);changes.append({'chapter':chapter,'before':a,'after':b})
def section(a,b,new):
 global t
 i=t.index(a);j=t.index(b,i);changes.append({'chapter':chapter,'before':t[i:j],'after':new});t=t[:i]+new+'\n\n'+t[j:]
def save():
 global t
 for i,m in enumerate(markers):t=t.replace(f'PROTECTED_RESULTS_{i}',m)
 p.write_text(t,encoding='utf-8')
load(30)
r('### 30.18.1 The Core Pattern','### 30.10.1 The Core Pattern');r('### 30.18.2 Complete Digital Twin Example','### 30.10.2 Complete Digital Twin Example')
r('Recreate any previous model state exactly','Restore supported captured fields with pinned source/dependencies and verify rerun outputs')
r('solved by mechanistic models (e.g., Beggs and Brill, OLGA) or drift-flux correlations','approximated by empirical correlations such as Beggs–Brill or by other qualified multiphase models')
section('1. **Initialize.** Assume an initial wellhead pressure','This iterative sequential approach',r'''1. **Initialize.** Choose a trial rate and bottomhole flowing pressure for each well, and a common manifold/facility boundary pressure.
2. **Reservoir evaluation.** Evaluate the IPR at **bottomhole** flowing pressure. Wellhead pressure is a different physical location and requires a tubing model.
3. **Transport evaluation.** Propagate each well through tubing, choke, flowline and riser to compute arrival pressure and temperature. Include any installed boosting equipment explicitly.
4. **Facility evaluation.** Solve the commingled facility at its imposed pressure/control specifications and current flows. Determine the required upstream interface pressure including inlet losses.
5. **Convergence check.** At the **same junction**, enforce $p_{\mathrm{arrival}}-p_{\mathrm{required}}=0$, along with each IPR/rate residual and mass/composition consistency. Update the free rate/pressure variables using a bounded root-solving method and rerun every domain.

Do not compare wellhead pressure directly with topside backpressure across a pressure-dropping line. The number of interface iterations is case-dependent; monitor scaled pressure/rate residuals and all unit convergence states.''')
r('production-grade closed-loop search','bounded simulation search')
r('— `optimize()` never throws:', '— supported evaluation failures are recorded diagnostically. Validate the returned result and handle configuration/runtime exceptions at the application boundary:')
r('Because the optimizer never throws and emits schema-versioned JSON', 'Because the optimizer exposes a trajectory and schema-versioned JSON')
r('so the same problem replays identically.', 'with repeatability dependent on identical inputs, source, solver settings and process state. Independent final replay tests this explicitly.')
r('| **Edge** | On-site server or gateway | < 1 s | Real-time control, safety |','| **Edge** | On-site server or gateway | Measure against required deadline | Local monitoring/control application; no safety certification implied |')
r('| **Fog** | Regional data center | 1–10 s | Production optimization |','| **Fog** | Regional data center | Measure network and solver latency | Production optimization |')
r('| **Cloud** | Cloud platform (Azure, AWS) | 10–100 s | Analytics, reporting, ML training |','| **Cloud** | Cloud platform | Measure network and solver latency | Analytics, reporting, training |')
r('The NeqSim JAR is < 50 MB including all dependencies','Measure the deployed classes, dependencies, optional native libraries and JVM memory for the actual distribution')
r('For Level 3 and 4 digital twins, edge deployment is essential because:', 'Local execution can support these requirements when the intended architecture needs them:')
r('represents the complete pattern','represents the local simulation pattern')
r('The following example demonstrates a complete digital twin workflow — from building the model to running the update loop:', 'The following example executes a local model-update loop with generated inputs. It does not access a live historian or establish field-tracking accuracy:')
r('the simulator can learn the transition dynamics','a validated dynamic model can supply transition calculations')
blocks=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',t,re.M|re.S))
replacements={5:'''import numpy as np
import pandas as pd

def clean_plant_data(df,tag_limits):
    """Preserve raw data; flag missing/nonfinite/out-of-range values, without imputation."""
    if not isinstance(df.index,pd.DatetimeIndex) or df.index.has_duplicates:
        raise ValueError('Unique timestamps are required')
    if not df.index.is_monotonic_increasing:
        raise ValueError('Timestamps must increase')
    clean=df.astype(float).copy();invalid=~np.isfinite(clean)
    for col in clean.columns:
        if col not in tag_limits:raise ValueError('Missing limits for '+col)
        lo,hi=tag_limits[col];invalid[col]|=(clean[col]<lo)|(clean[col]>hi)
    clean=clean.mask(invalid)
    clean.attrs['invalid_mask']=invalid
    return clean

tag_limits={'pressure':(10.0,100.0)}
raw=pd.DataFrame({'pressure':[60.0,61.0,999.0,np.nan]},
                 index=pd.date_range('2026-01-01',periods=4,freq='min',tz='UTC'))
clean=clean_plant_data(raw,tag_limits)
assert raw.iloc[2,0]==999.0 and clean.iloc[:2,0].notna().all()
assert clean.iloc[2:,0].isna().all() and clean.attrs['invalid_mask'].sum().iloc[0]==2
# A required invalid tag blocks model updating; site quality/age flags are additional inputs.
''',6:'''def is_steady_state(df,window=30,threshold=.5,min_duration_samples=15,
                    noise_floor=None,max_std=None):
    """Regular sampled-data screen with explicit unit-dependent noise/variation limits."""
    if noise_floor is None or max_std is None:
        raise ValueError('Declare noise floors and maximum standard deviations in tag units')
    if len(df)<2*window+min_duration_samples or not np.isfinite(df.to_numpy()).all():
        return False
    intervals=np.diff(df.index.asi8)
    if len(intervals) and (np.any(intervals<=0) or not np.all(intervals==intervals[0])):
        return False
    means=df.rolling(window).mean();stds=df.rolling(window).std()
    tests=[]
    for col in df.columns:
        floor=float(noise_floor[col]);ceiling=float(max_std[col])
        if floor<=0 or ceiling<=0:raise ValueError('Positive noise/variation limits required')
        normalized=means[col].diff(window).abs()/stds[col].clip(lower=floor)
        tests.append((normalized<threshold)&(stds[col]<=ceiling))
    accepted=pd.concat(tests,axis=1).all(axis=1)
    return bool(accepted.iloc[-min_duration_samples:].all())

times=pd.date_range('2026-01-01',periods=100,freq='min',tz='UTC')
arguments={'noise_floor':{'pressure':.02},'max_std':{'pressure':.1}}
constant=pd.DataFrame({'pressure':np.full(100,60.0)},index=times)
trend=pd.DataFrame({'pressure':np.linspace(60,80,100)},index=times)
oscillation=pd.DataFrame({'pressure':60+np.sin(np.arange(100)*np.pi/5)},index=times)
assert is_steady_state(constant,**arguments)
assert not is_steady_state(trend,**arguments)
assert not is_steady_state(oscillation,**arguments)
missing=constant.copy();missing.iloc[-1,0]=np.nan
assert not is_steady_state(missing,**arguments)
print('Local data-quality contracts: valid constant accepted; trend/oscillation/missing rejected')
# Known events, sensor freeze, multivariable dynamics and site quality flags remain separate gates.
'''}
for n,c in sorted(replacements.items(),reverse=True):
 m=blocks[n-1];t=t[:m.start(3)]+c.rstrip()+'\n'+t[m.end(3):]
save()
load(35)
r('The three main electrolysis technologies are:\n\nAlkaline','Alkaline')
r('## 35.4 Hydrogen Production from Natural Gas','## 35.4 Hydrogen Production and Integration')
r('ordinary differential equations','ordinary differential equations')
r('where the power balance must be maintained at all times, potentially requiring load shedding (reducing production) during low-wind periods.', 'Use a signed battery power (positive discharge, negative charge), explicit curtailment and consistent AC/DC losses. Storage capacity requires chronological operation, not only a wind-duration percentage. The power balance must be maintained at every step.')
r(r'E_{\text{storage}}(t) &\geq 0 \quad \forall t \\',r'0\leq E_{\text{storage}}(t)&\leq E_{\max}\quad\forall t \\')
r('This is a time-varying optimization that couples energy systems modeling with process simulation', r'Add the storage transition $E_{k+1}=E_k+\eta_c P_{c,k}\Delta t-P_{d,k}\Delta t/\eta_d$, charge/discharge power limits, mutually exclusive modes, and initial/terminal inventories. With kW and hours, energy is kWh. Cost terms require a common discounted time basis. This time-varying optimization couples energy systems modeling with process simulation')
r('Most production facilities operate at Level 1, with some advanced installations approaching Level 2.', 'The levels are illustrative; no survey of current facility adoption is supplied.')
r('The barriers to higher levels of autonomy are not primarily technical but organizational, regulatory, and cultural.', 'Barriers include technical reliability, model validity, assurance, organizational responsibilities and applicable regulation.')
r('because the underlying physical laws remain valid','subject to validated constitutive and numerical behavior')
r('wider operating envelopes','qualified operating envelopes')
r('thermodynamic equilibrium, equation-of-state relationships — are encoded in the simulator. These relationships hold in reality regardless of the operating conditions.', 'thermodynamic and constitutive approximations — are represented in the simulator. Conservation laws apply generally; equilibrium and specific EOS/transport closures have validity domains.')
r('with minimal human intervention','within the defined governance and operating scope')
save()
# Metadata and arithmetic corrections identified in the cross-book review.
for n in list(range(19,33))+[34,35]:
 load(n)
 r('GPSA Engineering Data Book (2024). 14th edition','GPSA Engineering Data Book (2016). 14th edition')
 r('GPSA (2017).','GPSA (2016).')
 r('NORSOK P-002 (2014). *Process System Design*.','NORSOK P-002 (2023, corrected 2024). *Process System Design*.')
 r('*Chemical Engineering Research and Design*, 166, 230–239','*Chemie Ingenieur Technik*, 93(12), 2029–2039')
 r('Fischer, Achim','Fischer, Asja')
 r('**Combined standard uncertainty** | — | **0.519**','**Combined standard uncertainty** | — | **0.520**')
 save()
(B/'verification/scientific_revision/final_text_corrections.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
print(len(changes),'final text corrections')
