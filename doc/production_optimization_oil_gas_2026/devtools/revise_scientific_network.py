"""Scientific review fixes: utilization, hydraulic signs and accepted allocation."""
import json,re
from pathlib import Path
BOOK=Path(__file__).resolve().parents[1]
changes=[]
def load(n):
 p=next((BOOK/'chapters').glob(f'ch{n:02d}_*/chapter.md'));o=p.read_text(encoding='utf-8-sig')
 b=BOOK/'.build/backups/scientific_revision'/p.parent.name/'network_input.md';b.parent.mkdir(parents=True,exist_ok=True)
 if not b.exists():b.write_text(o,encoding='utf-8')
 return p,o,b.read_text(encoding='utf-8')
def r(old,new):
 global t
 if old not in t:raise AssertionError(old[:140])
 t=t.replace(old,new);changes.append({'chapter':n,'before':old,'after':new})
def save():
 markers=lambda x:re.findall(r'<!-- reviewed-notebook-results:start -->.*?<!-- reviewed-notebook-results:end -->',x,re.S)
 assert markers(t)==markers(o)
 p.write_text(t,encoding='utf-8')
n=25;p,o,t=load(n)
r('Chapters 18–19 and implemented in Chapters 25 and 28','Chapters 22–24')
r('Chapter 25 introduced','Chapter 23 introduced')
r('`ProcessAutomation` API (Chapter 25)','`ProcessAutomation` API (Chapter 23)')
r('`ProductionOptimizer` (Chapter 25)','`ProductionOptimizer` (Chapter 23)')
r('Chapter 21 on digital twins and automation','Chapter 30 on digital twins and automation')
r('For example, a compressor with 50 kW of power margin may be acceptable regardless of whether the rated power is 500 kW ($U = 0.90$) or 5000 kW ($U = 0.99$).','For example, 50 kW is the same absolute power margin on 500 and 5000 kW drivers, but its adequacy depends on disturbances, uncertainty and the driver response; neither the absolute nor relative margin alone establishes acceptance.')
r('In practice, this integral is approximated by averaging discrete samples from the plant historian:', 'For equally spaced, valid samples this integral is approximated by their arithmetic mean. For irregular historian samples use time weighting and explicitly handle gaps:')
r('| Compressor surge monitoring | 1–5 seconds | Fast dynamics near surge |','| Compressor-map advisory trending | Site-specific display interval | Does not replace dedicated fast anti-surge protection |')
r('`maxUtilization` (0–1)','`maxUtilization` (dimensionless, possibly above one)')
r(r'U_{\text{surge}} = 1 - \frac{\text{SM}}{\text{SM}_{\text{design}}}',r'U_{\text{surge}} = \frac{\text{SM}_{\text{min}}}{\text{SM}}\quad (\text{SM}>0)')
r('### 25.6.2 Power Utilization','At the minimum positive margin this ratio is one. Treat zero/negative margin as a violation rather than evaluating a negative utilization; a missing map is unavailable evidence. This is an explicit engineering ratio, not a promise that every NeqSim constraint supplier uses the same normalization.\n\n### 25.6.2 Power Utilization')
r('A 2–3% drop in polytropic efficiency from the as-new baseline typically triggers a maintenance recommendation.', 'Correct for gas properties, speed and operating point before attributing efficiency changes to degradation. Maintenance thresholds require uncertainty, vendor guidance and a cost/availability assessment.')
r('Tracking $R_f$ over time provides a direct measure of fouling progression. Typical fouling rates range from 0.0001 to 0.001 m² K/W per year depending on the service (clean gas vs. crude oil vs. produced water).', 'Back-calculated $R_f$ is an apparent resistance relative to the clean baseline. Changes in flow, properties, bypass, heat loss and sensor bias can imitate fouling; normalize or model these effects before estimating a growth rate.')
r('Exceeding the erosional velocity limit causes accelerated pipe wall thinning and eventual failure. Monitoring $U_v$ is especially important in wells and flowlines with sand production.', 'The API velocity criterion is an empirical screen, not a prediction of wall-loss rate or proof of protection. Sand size/loading, impact geometry, corrosion and material response require a separate erosion assessment.')
r('These trends are gradual (months to years) but inexorable.', 'These trends are scenario-dependent; pressure support, reservoir architecture and well interventions can change their direction.')
r('This section presents a comprehensive case study demonstrating how utilization monitoring reveals evolving constraints over a three-year period on a representative North Sea oil production platform.', 'This section is an assumed three-year planning scenario, not a field dataset or output from the reduced compression example. The utilization tables illustrate interpretation only; the reproduced calculations later in the chapter have their own explicit inputs and do not validate these scenario values.')
r('Change from Year 1','Change from Year 1 (percentage points)')
r('Change from Year 2','Change from Year 2 (percentage points)')
r('The water treatment system is now in the yellow zone and trending upward.', 'Water treatment is still green under the stated 70% threshold, but its upward trend warrants review.')
r('Consider wellhead compression to maintain wellhead flowing pressure','Consider wellhead compression to lower the upstream backpressure seen by the well while meeting downstream delivery pressure')
r('The net value of the monitoring system is the avoided deferment minus the cost of implementation. For a typical offshore platform, the monitoring system costs $0.5–2M to implement (software, instrumentation, engineering) and $0.2–0.5M/year to operate. The avoided production deferment of $25.5M provides a payback period of less than one month — making utilization monitoring one of the highest-return investments available to production operations.', 'The 25.5 million USD figure is the undiscounted value of 182.5 days × 2,000 bbl/day × 70 USD/bbl under the assumed scenario. Deferred production is not necessarily permanently lost: value recovery timing, discounting and any lost reserves explicitly. No implementation costs, net present value or payback period have been measured here.')
r('the deferred production costs $25.5M.', 'the deferred gross revenue is $25.5M before considering subsequent recovery.')
r('Calculate the gas capacity utilization $U_{\\text{gas}}$ and the liquid capacity utilization $U_{\\text{liquid}}$.', 'Assume horizontal half-full geometry and standard gas density 0.80 kg/Sm³. Convert gas standard volume to mass and then actual volume before calculating $U_{\\text{gas}}$ and $U_{\\text{liquid}}$.')
r('Calculate the UA utilization and the fouling resistance.', 'Assume heat-transfer area 1,000 m². Calculate the UA utilization and the apparent fouling resistance on this area basis.')
save()
n=26;p,o,t=load(n)
r('dynamic simulation (Chapter 20)','dynamic simulation (Chapter 29)')
r('Chapter 29 for advanced solver strategies','Chapter 31 for advanced solver strategies')
r('`ProductionOptimizer` (Chapter 25)','`ProductionOptimizer` (Chapter 23)')
r('These nonlinearities mean that simple linear programming (LP) is insufficient.', 'These nonlinearities generally require a nonlinear model. A fixed-GOR, fixed-water-cut allocation approximation can be linear, as demonstrated in Section 26.11, provided its missing network coupling is explicit.')
r('**Vogel\'s equation** (1968) accounts for this effect:', '**Vogel\'s equation** (1968) is an empirical saturated solution-gas-drive IPR approximation. For an initially undersaturated reservoir with $p_r>p_b$, use a composite linear/Vogel relation rather than applying the saturated formula across the whole pressure range:')
r('For $n = 1$, this reduces to a form similar to Darcy flow for gas wells. For $n = 0.5$, it represents fully turbulent (non-Darcy) flow.', 'The fitted exponent describes test response. Its limiting values resemble linear/quadratic resistance when using a pressure-squared gas formulation, but they do not uniquely identify a turbulence regime in an oil well.')
r('For wells where non-Darcy flow near the wellbore is significant (high-rate gas wells, gravel-packed wells),', 'For liquid wells where inertial near-wellbore pressure loss is significant (for example gravel-packed completions),')
r('The first term represents viscous pressure drop; the second represents inertial pressure drop near the wellbore.', 'The first term represents viscous pressure loss and the second inertial loss. For gas, use pressure-squared or gas pseudopressure differences with consistently fitted coefficient units; do not reuse the liquid pressure-difference coefficients.')
r(r'+ \Delta p_{\text{friction}} - \Delta p_{\text{acceleration}}',r'+ \Delta p_{\text{friction}} + \Delta p_{\text{acceleration}}')
r('steady-state energy equation for multiphase flow','steady-state momentum balance for multiphase flow')
r(r'\frac{dp}{dz} = \frac{g \rho_m \sin\theta}{g_c} + \frac{f \rho_m v_m^2}{2 d} + \rho_m v_m \frac{dv_m}{dz}',r'-\frac{dp}{ds}=\rho_h g\sin\theta+\frac{f_D\rho_fv_m^2}{2d}+\rho_av_m\frac{dv_m}{ds}')
r('Here $\\rho_m$ is the mixture density, $v_m$ is the mixture velocity, $d$ is the tubing internal diameter, $f$ is the friction factor, $\\theta$ is the inclination angle, and $z$ is the distance along the flow path.', 'Here $s$ increases along the flow, $\\theta>0$ uphill, $f_D$ is Darcy friction factor and all quantities are SI. Holdup density $\\rho_h$ generally differs from the densities used in the friction/acceleration closure. The displayed balance is schematic; a named multiphase correlation supplies those closures.')
r('- Tubing head pressure $p_{th}$ (for VFPPROD tables) or bottomhole pressure (for VFPINJ tables)', '- Tubing-head pressure at a defined reference location (both production and injection tables store BHP responses; the axis sets and flow direction differ)')
r('At sufficiently high pressure ratios,','At sufficiently low downstream-to-upstream pressure ratios,')
r('In critical flow, the choke acts as a **decoupler** — upstream pressure variations do not propagate downstream, and vice versa.', 'For ideal single-phase gas choking, further downstream-pressure reductions do not increase the mass flow while upstream stagnation state and throat area remain fixed. Upstream changes still alter flow and downstream conditions; this is not two-way hydraulic decoupling. The ideal-nozzle ratio is not a universal multiphase choke criterion.')
r('- Optimization of wells in critical flow requires only adjusting the choke opening, not re-solving the entire network', '- Even if a well remains choked, recompute the downstream network, phase rates and facility constraints for each changed allocation')
r('and repeat until all constraints are active.', 'and repeat until no feasible improving move is found. An optimum generally leaves many constraints inactive.')
r('This greedy algorithm converges to the global optimum because the gas lift performance curves are concave (diminishing returns).', 'For separable concave response curves with one shared budget and simple bounds, a properly solved equal-slope allocation has a global certificate. Discrete greedy steps give only a step-size approximation; coupled network constraints invalidate the simple guarantee. Chapter 22 includes a native allocation with independent KKT and grid checks.')
r('where $q_{o,\\text{max}}$ is the maximum achievable oil rate with unlimited gas lift and $\\alpha$ is a well-specific constant that depends on the well depth, tubing size, reservoir deliverability, and fluid properties.', 'This exponential is only an assumed monotone response with zero natural-flow intercept. It cannot describe the falling branch at excessive injection or infer a maximum from tubing physics. Fit a nonzero base and a friction-loss term or tabulate a qualified well response when those effects matter.')
r('- The bubble point pressure at separator temperature (to maintain single-phase liquid oil)', '- Product stability, flash-gas handling and downstream minimum-pressure requirements; separation intentionally permits flashing below the feed bubble point')
r('This sensitivity is negative (lower separator pressure yields more production) and its magnitude depends on the network geometry and well characteristics. Typical values range from 50–500 Sm³/d per bar for oil-producing platforms.', 'For a supply-limited stable branch this derivative is often negative. Facility constraints, lift behavior and phase changes can alter the overall response; evaluate it rather than assuming a universal magnitude or sign.')
r('Subsea networks have flow assurance constraints that do not apply to topside systems:', 'Subsea networks face especially demanding flow-assurance constraints, although hydrates and wax can also affect topside systems:')
r('This algorithm naturally handles multiple constraints', 'A simple single-resource rank does not solve general multi-resource allocation. A full constrained solve or valid multiplier update is needed as constraints interact. Sequential rate bumping can be used as a heuristic')
r('For a gas-handling constraint:', 'For a single active gas constraint and wells strictly inside their bounds (with a separable response):')
# Replace the invented results and mere ranking with a real solve and a dual certificate.
a=t.index('### 26.11.4');b=t.index('<!-- September 2026',a)
replacement='''### 26.11.4 Accepted Fixed-Composition Allocation

This example treats the tabulated maxima as available **oil** rates and assumes fixed GOR and water cut. It is a linear allocation model, not a solved tubing/choke network. Gas compression is evaluated with NeqSim at a common 60 bara suction, 180 bara discharge and 30°C inlet, using an assumed 90/10 methane/ethane blend and 78% polytropic efficiency. At fixed gas state and efficiency, power is proportional to mass rate, so the compression constraint can be included in the allocation matrix.

```python
import numpy as np
import jpype
from scipy.optimize import linprog
jneqsim = jpype.JPackage("neqsim")
qmax = np.array([4500.,3800.,3200.,5000.,2800.,4200.])
gor = np.array([120.,180.,250.,100.,200.,150.])
wc = np.array([.05,.15,.30,.08,.45,.12])
water_per_oil = wc/(1.0-wc)

def compression(gas_rate_Sm3_day):
    gas = jneqsim.thermo.system.SystemSrkEos(303.15,60.0)
    gas.addComponent("methane",.90)
    gas.addComponent("ethane",.10)
    gas.setMixingRule("classic")
    stream = jneqsim.process.equipment.stream.Stream("Allocated gas",gas)
    stream.setFlowRate(float(gas_rate_Sm3_day),"Sm3/day")
    comp = jneqsim.process.equipment.compressor.Compressor("Export",stream)
    comp.setOutletPressure(180.0)
    comp.setUsePolytropicCalc(True)
    comp.setPolytropicEfficiency(.78)
    process = jneqsim.process.processmodel.ProcessSystem()
    process.add(stream)
    process.add(comp)
    process.run()
    m_in = float(stream.getFlowRate("kg/hr"))
    assert abs(comp.getOutletStream().getFlowRate("kg/hr")-m_in)/m_in < 1e-10
    dh = comp.getOutletStream().getFluid().getEnthalpy()-stream.getFluid().getEnthalpy()
    power = float(comp.getPower("kW"))
    assert abs(dh/1000.0-power)/power < 1e-5
    return power

power_per_gas = compression(1.0e6)/1.0e6  # kW per (Sm3/day)
A = np.vstack([gor,water_per_oil,gor*power_per_gas,np.ones(6)])
b = np.array([3.5e6,8000.,18000.,25000.])
answer = linprog(-np.ones(6),A_ub=A,b_ub=b,
                 bounds=list(zip(np.zeros(6),qmax)),method="highs")
assert answer.success, answer.message
q = answer.x.copy()
assert np.all(q >= -1e-8) and np.all(q <= qmax+1e-8)
assert np.all(A@q <= b+1e-6)
# Independent dual upper bound for max sum(q): lambda>=0, mu>=0,
# A.T lambda + mu >= 1, then sum(q) <= lambda.b + mu.qmax.
lam = -answer.ineqlin.marginals
mu = -answer.upper.marginals
assert np.min(lam) >= -1e-10 and np.min(mu) >= -1e-10
assert np.min(A.T@lam+mu-np.ones(6)) >= -1e-9
dual_bound = float(lam@b+mu@qmax)
assert abs(dual_bound-q.sum()) < 1e-5
replayed_power = compression(float(gor@q))  # entirely fresh NeqSim process
assert abs(replayed_power-A[2]@q) < 1e-4
assert replayed_power <= 18000.0+1e-4
print("Oil allocation P-1..P-6 (Sm3/day):",q)
print(f"Oil {q.sum():.3f}; gas {gor@q:.3f}; water {water_per_oil@q:.3f}")
print(f"Power {replayed_power:.3f} kW; dual bound {dual_bound:.3f} Sm3/day")
```

### 26.11.5 Interpreting the Accepted Result

The numerical output is the accepted optimum **of the stated allocation approximation**. The independent dual bound certifies global optimality for this linear problem within $10^{-5}$ Sm³/day; the fresh NeqSim solve checks the selected gas duty. Water rate is $q_o f_w/(1-f_w)$, not $q_of_w$, because water cut is water divided by total liquid. The marginal oil return per unit gas is $1/\mathrm{GOR}$; multiplying it again by oil cut double-counts the liquid basis.

This model does not determine choke positions, validate the six Vogel curves against tubing hydraulics or predict a separator-pressure benefit. Supply those missing couplings before interpreting the allocation as a field operating plan. The previous illustrative 18,800 Sm³/day result and uncomputed upgrade sensitivities are not retained as evidence.

### 26.11.6 Sensitivity Analysis

Change one entry of the capacity vector, repeat the allocation and independently replay compression. A water-capacity increase provides no benefit while its constraint is inactive. A separator-pressure change requires rebuilding the well and network supply limits, not adding a fixed oil uplift. Compare any incremental oil value on a consistent time and currency basis and include the expansion's costs and availability.

---

'''
t=t[:a]+replacement+t[b:]
changes.append({'chapter':26,'topic':'Replaced fabricated 6-well result with solved LP, independent dual certificate and fresh NeqSim compression replay'})
r('The case study demonstrated that well allocation optimization can recover significant production compared to naive equal-rate or proportional-rate strategies, particularly when wells have different GOR and water cut characteristics.', 'The case study demonstrates a certified allocation optimum for fixed fluid-yield assumptions and a checked NeqSim compression duty. The remaining hydraulic and reservoir coupling is stated explicitly.')
save()
(BOOK/'verification/scientific_revision/network_corrections.json').write_text(json.dumps(changes,indent=2,ensure_ascii=False),encoding='utf-8')
print(f'Applied {len(changes)} corrections')
