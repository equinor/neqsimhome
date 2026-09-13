"""Record the completed agent visual review and independently check teaching math.

Read-only with respect to book inputs and images. This script does not perform
visual inspection: the reviewing agent observations below record the actual review.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1]
sys.path.insert(0, str(BOOK / '.build/python_packages'))
import numpy as np
from PIL import Image


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


records = json.loads((HERE / 'illustration_repairs.json').read_text(encoding='utf-8'))
initial = json.loads((HERE / 'manuscript_repair_visual_review/inspection_inventory.json').read_text(encoding='utf-8'))
assert len(records) == len(initial) == 20
checks = [[] for _ in records]


def check(index, label, passed, measured=None, criterion=None):
    result = dict(label=label, passed=bool(passed), measured=measured, criterion=criterion)
    checks[index-1].append(result)
    assert passed, (index, result)


def data(index):
    return records[index-1]['data']


# These checks use retained inputs/equations, not the image-generating script.
# They establish consistency of the illustrations, not independent field truth.
d = data(1)
dt = np.geomspace(.1, 10000, 200)
ratio = (d['tp_h'] + dt) / dt
p = d['pressure_star_bara'] - d['slope_bar_per_decade'] * np.log10(ratio)
check(1, 'Shut-in pressure approaches the stated asymptote from below',
      np.all(np.diff(p)>0) and p[-1]<330 and 330-p[-1]<.05,
      {'first_bara':float(p[0]), 'last_bara':float(p[-1]), 'asymptote_bara':330},
      'Strict increase with shut-in time; final deficit below 0.05 bar')

d = data(2)
rates = np.array(d['intersection_m3_day'])
diameters = np.array(d['diameters_in'])
k = 130/3000**2*(3.5/diameters)**5
residual = 300*(1-rates/5000) - (60+k*rates**2)
check(2, 'Saved intersections satisfy both pressure curves and diameter ordering',
      np.max(abs(residual))<1e-9 and np.all(np.diff(rates)>0),
      {'rates_m3_day':rates.tolist(), 'max_pressure_residual_bar':float(np.max(abs(residual)))},
      'Residual < 1e-9 bar; strictly increasing rate with diameter')

t = np.array([.001,.01,.1,1,10,30,200,1000])
def pressure(time):
    return 10*np.log1p(time/.1)+5*np.maximum(time/100-1,0)**2
step = 1e-5
numeric = (pressure(t*np.exp(step))-pressure(t*np.exp(-step)))/(2*step)
analytic = 10*t/(.1+t)+10*(t/100)*np.maximum(t/100-1,0)
error = float(np.max(abs(numeric-analytic)/analytic))
check(3, 'Analytical derivative agrees with independent central differentiation in log time',
      error<1e-7, {'relative_error':error, 'times_h':t.tolist()}, 'Relative error < 1e-7 at eight states away from the imposed transition')

d=data(4); oil=np.array(d['oil_thousand_m3_day']); water=np.array(d['water_thousand_m3_day']); wc=np.array(d['water_cut_pct'])
error=float(np.max(abs(wc-100*water/(oil+water))))
check(4, 'Water cut uses the same plotted liquid volume basis', error<1e-12 and np.all((wc>=0)&(wc<=100)),
      {'max_error_percentage_points':error,'first_water_cut_pct':float(wc[0]),'last_water_cut_pct':float(wc[-1]),'final_oil_thousand_m3_day':float(oil[-1]),'final_water_thousand_m3_day':float(water[-1])},
      'Absolute error < 1e-12 percentage points and 0–100% bounds')

d=data(5); gap=np.array(d['hot_C'])-np.array(d['cold_C']); h=np.array(d['enthalpy_MW'])
check(5, 'Both composites increase; the declared minimum gap occurs at 5 MW',
      np.all(np.diff(d['hot_C'])>0) and np.all(np.diff(d['cold_C'])>0) and min(gap)==25 and h[np.argmin(gap)]==5,
      {'minimum_gap_K':float(min(gap)), 'enthalpy_at_minimum_MW':float(h[np.argmin(gap)])}, 'Exact 25 K gap at 5 MW; no crossing')

d=data(6); T1,T2,T3,T4=d['T_K']; cp=d['cp_kJ_kg_K']; rp=d['pressure_ratio']; gamma=1.4
eta=1-rp**(-(gamma-1)/gamma)
ds_heat=cp*np.log(T3/T2); ds_cool=cp*np.log(T4/T1)
err=max(abs(T2/T1-T3/T4),abs(ds_heat-ds_cool),abs(d['efficiency']-eta))
check(6, 'Ideal Brayton pressure ratio, entropy closure and efficiency identities',err<1e-12,
      {'temperatures_K':d['T_K'],'efficiency_pct':100*eta,'specific_heat_added_kJ_kg':cp*(T3-T2),'specific_heat_rejected_kJ_kg':cp*(T4-T1),'max_identity_error':float(err)},
      'Absolute identity error < 1e-12; constant cp and gamma only')

caps=np.array(data(7)['capacities_pct_reference']); util=100*120/caps
check(7, 'Overload is retained and the compressor is the first limit',min(caps)==92 and np.all(util>100),
      {'utilization_at_120_percent_demand_pct':util.tolist(),'first_limit_percent_reference':float(min(caps))}, 'No clipping above 100%; smallest declared rating 92%')

points=np.array(data(8)['points']); chosen=np.array(data(8)['selected'])
non_dominated=np.array([not np.any((points[:,0]>=x)&(points[:,1]<=y)&((points[:,0]>x)|(points[:,1]<y))) for x,y in points])
front=points[non_dominated]
score=lambda values:((5000-values[...,0])/2000)**2+((values[...,1]-14)/3.2)**2
err=float(abs(score(chosen)-min(score(front))))
check(8, 'Independent exhaustive dominance and declared preference checks',sum(non_dominated)==90 and err<1e-12 and np.any(np.all(front==chosen,axis=1)),
      {'nondominated_count':int(sum(non_dominated)),'selected_oil_m3_day':float(chosen[0]),'selected_power_MW':float(chosen[1]),'preference_score_error':err},
      '90 of 250 alternatives nondominated; selected is in front and minimizes declared score to 1e-12')

d=data(9)
check(9, 'Recycle arrow increases compressor throughflow',d['end_m3_hr']>d['start_m3_hr']>5500,
      {'start_m3_hr':d['start_m3_hr'],'end_m3_hr':d['end_m3_hr']}, 'Rightward arrow from 5600 to 8500 m3/h; no net-export inference')

d=data(10); rng=np.random.default_rng(d['seed'])
# The generator uses the same random stream after the two Pareto-cloud arrays.
rng.uniform(3000,5000,160); rng.uniform(.4,8,160)
time=np.linspace(0,48,481); noise=rng.normal(0,.35,len(time)); known=np.where((time>=24)&(time<36),d['known_offset_K'],0)
raw=noise+known; estimate=np.zeros_like(raw); window=d['window_samples']
for i in range(window,len(time)):
    estimate[i]=np.mean(raw[i-window+1:i+1])
mean=float(np.mean((raw-estimate)[(time>=28)&(time<35)]))
check(10, 'Seeded fixture and rolling residual correction reproduce saved summary',abs(mean-d['mean_corrected_residual_K'])<1e-12 and abs(mean)<.2,
      {'mean_corrected_residual_K':mean,'injected_offset_K':d['known_offset_K'],'window_samples':window}, 'Saved-mean agreement < 1e-12 K; corrected plateau mean < 0.2 K, excluding transition lag')

# Agent visual topology checks are separated from numerical calculation checks.
manual = {
 11: 'Visible order is inlet liquid removal, acid-gas treatment, deep drying/mercury control, cryogenic recovery, residue compression. Caption makes configuration conditional and does not equate TEG with cryogenic dehydration.',
 12: 'Six directed steps close the monitoring/reconciliation loop. Verification and authorization precede implementation; caption does not claim a live plant connection.',
 13: 'Rich solvent passes flash drum and rich exchanger side to regeneration; hot lean solvent passes lean exchanger side, cooler and pump back to absorber. The final flash-gas outlet is visible. Heat is a separate dashed connection, not solvent mixing.',
 14: '350 t/h, 70 bara dry feed, inlet separator, precooling/knockout with separate gas expansion and liquid letdown, cold separation, 70 bara residue compression and 4.5 MW stabilizer agree with literal Chapter 33. Four external product boundaries are represented.',
 15: 'The gas outlet of upstream knockout enters the expander; liquid uses a letdown valve. Both rejoin before cold separation. Compression and stabilization follow separate product streams; there is no invented common-shaft connection.'
}
for index, observation in manual.items():
    checks[index-1].append({'label':'Agent visual topology and caption cross-check','passed':True,'measured':observation,'criterion':'Actual visible connections and stated omissions agree with scoped caption; indices 14–15 also checked against literal worked flowsheet'})

benchmark_path=HERE/'benchmark_results.json'
bench=json.loads(benchmark_path.read_text(encoding='utf-8'))
dens=[r for r in bench['comparisons'] if r['name'] in ('SRK methane density','PR methane density')]
states={(r['case']['T_K'],r['case']['P_bara']) for r in dens}
maxima={name:100*max(abs((r['actual']-r['expected'])/r['expected']) for r in dens if r['name']==name) for name in ('SRK methane density','PR methane density')}
match=digest(BOOK/records[15]['path'])==digest(HERE/'figures/nist_methane_density_validation.png')
check(16, 'Image exactly matches retained independent NIST benchmark; numerical deviations reproduce caption',
      len(dens)==18 and states=={(t,p) for t in (300.,350.,400.) for p in (1.,50.,100.)} and max(maxima.values())<3 and all(r['passed'] for r in dens) and match,
      {'comparison_count':len(dens),'state_count':len(states),'max_abs_relative_deviation_pct':maxima,'benchmark_image_identical':match,'benchmark_results_sha256':digest(benchmark_path)},
      '18 comparisons at 9 NIST reference-EOS states; each deviation within declared 3% scope; identical plot hash')

d=data(17); speeds=np.array(d['relative_speeds']); surge=np.array(d['surge']); high=np.array(d['high_flow'])
head=lambda q,n:180*n**2*(1-.25*(q/(6000*n))**2)
err=max(np.max(abs(surge[:,1]-head(surge[:,0],speeds))),np.max(abs(high[:,1]-head(high[:,0],speeds))))
check(17,'Compressor-map endpoints and operating marker obey declared similarity relation',err<1e-12 and head(6000,1)==135 and np.all(surge[:,0]<high[:,0]) and np.all(surge[:,1]>high[:,1]),
      {'max_endpoint_head_error_kJ_kg':float(err),'marker_flow_m3_hr':6000,'marker_head_kJ_kg':135}, 'Endpoint head errors < 1e-12 kJ/kg; decreasing head over positive-flow ranges; no installed-rating claim')

d=data(18); hessian=np.array(d['hessian_diagonal'])
gradient=[-2*(d['stationary_HP_bara']-60)/900,-2*(d['stationary_MP_bara']-15)/225]
check(18,'Declared contour has a feasible unique concave maximum',np.all(hessian<0) and max(abs(np.array(gradient)))==0 and 30<=d['stationary_HP_bara']<=90 and 5<=d['stationary_MP_bara']<=30,
      {'stationary_pressures_bara':[60,15],'hessian_eigenvalues':hessian.tolist(),'gradient':gradient},'Gradient zero; negative definite Hessian; point within displayed domain')

d=data(19); pwf=np.linspace(0,d['reservoir_bara'],250); r=pwf/d['reservoir_bara']
curves=[d['PI_m3_day_bar']*(d['reservoir_bara']-pwf),d['Vogel_AOF_m3_day']*(1-.2*r-.8*r**2),d['Fetkovich_AOF_m3_day']*(1-r**2)**d['Fetkovich_exponent']]
check(19,'Inflow curves obey no-drawdown and AOF limits with monotonic decline',all(abs(c[-1])<1e-12 and np.all(np.diff(c)<0) for c in curves),
      {'AOF_m3_day':[float(c[0]) for c in curves],'no_drawdown_rates_m3_day':[float(c[-1]) for c in curves]}, 'Zero rate at reservoir BHP to 1e-12 m3/day; monotonically decreasing with BHP; extrapolated AOF only')

d=data(20); g=d['stationary_injection_thousand_Sm3_day']; marginal=2000/30*np.exp(-g/30); second=-2000/900*np.exp(-g/30); q=500+2000*(1-np.exp(-g/30))
check(20,'Lift net-benefit point satisfies the marginal condition and strict concavity',abs(marginal-d['cost_equivalent'])<1e-12 and second<0 and 0<g<200,
      {'stationary_g_thousand_Sm3_day':g,'oil_at_stationary_point_m3_day':float(q),'marginal_oil_per_thousand_Sm3':float(marginal),'second_derivative':float(second)}, 'Marginal yield equals declared cost-equivalent slope to 1e-12; negative second derivative; interior to displayed range')

observations = [
 'Reversed log-x axis correctly moves toward Horner ratio one at the right. Buildup approaches 330 bara; relocated formula is clear of the curve.',
 'Axes identify BHP and liquid rate. Diameter ordering and the three marked intersections match the analytical roots. Upper-axis clipping affects only high-pressure extensions outside the intersections.',
 'Logarithmic axes, derivative definition and approximately 10 bar plateau agree with the declared formula. Late boundary response is explicitly imposed.',
 'Oil/water bars and percentage water-cut axis have distinct units. The relocated lower-right legend leaves late-year bar tops visible; both liquid volumes share a reference basis.',
 'Hot/cold curves do not cross. The 25 K arrow lies at the minimum vertical separation, 5 MW; caption avoids claiming a plant pinch target.',
 'Both isentropes are vertical on the T–s plane; constant-pressure branches and states 1–4 are clear. Entropy is explicitly relative and temperature is in kelvin.',
 'All utilization curves visibly continue above 100%. The first threshold is the declared compressor rating; fixed assumed ratings are not presented as installed capacity.',
 'Axis directions match oil maximization and power minimization. The selected star is on the nondominated set; the caption declares synthetic alternatives and preference function.',
 'The arrow points toward greater actual compressor inlet flow, away from the stated low-flow boundary. The caption distinguishes compressor throughflow from net export and labels the map conceptual.',
 'Temperature and residual panels use Celsius and kelvin correctly. Shaded offset interval, correction lag, and noisy synthetic observations are visible; the caption does not claim measured plant evidence.',
 'Treatment sequence and arrows are readable. Conditional contaminant control and cryogenic pretreatment scope match the caption.',
 'Six boxes form a readable closed operational workflow, including verification and authorization before implementation.',
 'Separate rich/lean exchanger passages, heat-transfer arrow and final flash-gas outlet resolve the previous topology omission. The visible diagram and stated omissions agree.',
 'Readable dry-feed basis and external product arrows agree with the worked process topology. Utilities are explicit and the standalone TEG example is not silently included.',
 'Two inlet paths and two product paths are visually unambiguous. Gas-only expansion and liquid bypass are consistent with the literal worked flowsheet.',
 'Parity and deviation panels show all 18 comparisons with correct density/relative-error units. Legend distinguishes SRK and PR; bounds and narrow methane-state scope are explicit.',
 'Curves, speed labels, endpoint markers and the selected marker are consistent with the formula. No accepted-region shading implies validity outside specified endpoints.',
 'Pressure axes use bara; colorbar correctly labels a dimensionless algebraic objective. Dark stationary-point text remains legible over the light contour maximum.',
 'The three inflow curves have readable legends with distinct assumed parameters. All terminate at zero flow at 300 bara and their AOF intercepts match the caption.',
 'The saturating curve, stationary marker and declared cost assumption agree. The formula occupies lower whitespace; an opaque annotation background prevents the vertical guide obscuring text.'
]
full_resolution={1,4,6,10,11,13,14,15,18,20}
repaired={1,4,13,18,20}
findings={
 1:'Moved Horner formula away from the pressure curve.',
 4:'Moved the water-cut legend away from the final water-bar tops.',
 13:'Added the physically required flash-gas outlet to the rich-solvent flash drum.',
 18:'Changed stationary-point annotation to dark text on the light contour fill.',
 20:'Moved the gas-lift equation into whitespace and shielded it from the vertical guide with an opaque background.'
}
items=[]
for i,(r,old) in enumerate(zip(records,initial),1):
    path=BOOK/r['path']; actual=digest(path)
    assert path.resolve()==Path(old['path']).resolve() and actual==r['sha256']
    assert (actual!=old['sha256']) == (i in repaired), (i,'Unexpected image change after initial contact inspection')
    with Image.open(path) as im:
        size=list(im.size)
    items.append(dict(index=i,path=str(path),sha256=actual,size_px=size,caption=r['caption'],discussion=r['discussion'],basis=r['basis'],
                      visual_status='passed',caption_science_status='passed_with_stated_scope',observation=observations[i-1],
                      inspection=dict(contact_sheet=old['contact_sheet'],contact_sheet_sha256=digest(old['contact_sheet']),image_sha256_at_contact_inspection=old['sha256'],
                                      full_resolution_inspected=i in full_resolution,full_resolution_final_repair_inspected=i in repaired),
                      resolved_finding=findings.get(i),checks=checks[i-1]))

report=dict(schema_version=1,generated_at=datetime.now(timezone.utc).isoformat(),status='passed_scoped_visual_and_scientific_review',
            scope='Twenty repaired manuscript illustrations: actual contact-sheet visual inspection by the reviewing agent, representative full-resolution review, all changed images re-inspected at full resolution, caption/topology checks, and independent equation/data consistency checks. Synthetic illustrations are not external process-model validation; only the NIST plot inherits independent reference-fluid comparison evidence.',
            python=sys.executable,illustration_manifest_sha256=digest(HERE/'illustration_repairs.json'),repair_script_sha256=digest(BOOK/'devtools/repair_scientific_illustrations.py'),review_script_sha256=digest(__file__),
            counts=dict(images=20,initial_contact_sheets=4,full_resolution_distinct_images=len(full_resolution),repaired_images_reinspected=len(repaired),checks=sum(map(len,checks)),unresolved_material_findings=0),
            input_mutations_by_reviewer='None. Root editor applied five requested figure corrections. Review scripts write evidence only.',
            inspection_method='Visual inspection by the reviewing agent used actual tool-displayed images, not inferred from successful file generation. The initial contact sheets preserve the first inspected image hashes; final repairs were viewed individually at original resolution.',
            limitations=['No field calibration or vendor-map validation is inferred from analytical teaching plots.', 'The NIST panel validates only methane density at its nine stated temperature/pressure states within a declared teaching tolerance.', 'The two executed-plant topology drawings were checked against literal Chapter 33; this image audit does not rerun or replace the separately retained material and energy balance gate.', 'This audit covers the source images and caption records. Final PDF sizing and pagination are a separate publication review.'],
            images=items)
(HERE/'manuscript_repair_visual_review.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
lines=['# Repaired manuscript illustration review','',f'Completed {report["generated_at"]}. **PASS within the stated scope:** 20 images reviewed, four contact sheets, {len(full_resolution)} distinct full-resolution views, all five corrected images re-inspected, and {sum(map(len,checks))} equation/data/topology checks. No unresolved material findings.','',report['scope'],'',
       'The initial contact sheets and their image hashes are retained. The final five repaired images were viewed individually. The editor corrected four label/legend issues and added the missing amine flash-gas outlet; the gas-lift formula received a white background after its move. Visual inspection was performed by the reviewing agent. It does not constitute human or domain-peer certification. The reviewer did not modify manuscript text or images.','',
       '## Figure-by-figure findings','', '| # | Figure | Review |', '|---|---|---|']
for item in items:
    lines.append(f'| {item["index"]} | {Path(item["path"]).parent.parent.name}: {Path(item["path"]).name} | {item["observation"]} |')
lines.extend(['','## Checked numerical results',''])
for item in items:
    for result in item['checks']:
        if isinstance(result['measured'],dict):
            lines.append(f'- **{item["index"]}. {result["label"]}:** {json.dumps(result["measured"],ensure_ascii=False)}. Criterion: {result["criterion"]}.')
lines.extend(['','## Scope and limitations','']+['- '+x for x in report['limitations']])
lines.extend(['','## Final image hashes','', '| # | SHA-256 |', '|---|---|'])
lines.extend(f'| {i["index"]} | `{i["sha256"]}` |' for i in items)
lines.extend(['',f'Input manifest SHA-256: `{report["illustration_manifest_sha256"]}`.',f'Repair script SHA-256: `{report["repair_script_sha256"]}`.', 'The JSON report retains absolute paths, image dimensions, caption text, checks, initial/final inspection hashes and contact-sheet hashes.'])
(HERE/'manuscript_repair_visual_review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'counts':report['counts'],'report':str(HERE/'manuscript_repair_visual_review.json')}))
