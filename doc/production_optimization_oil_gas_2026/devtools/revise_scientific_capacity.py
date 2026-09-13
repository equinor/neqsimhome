"""Scientific dimensional, metrology, and economics corrections in Chapters 19-21."""
import json
import re
from pathlib import Path
BOOK=Path(__file__).resolve().parents[1]
CHANGES=[]

def load(n):
    p=next((BOOK/'chapters').glob(f'ch{n:02d}_*/chapter.md'))
    s=p.read_text(encoding='utf-8-sig')
    b=BOOK/'.build/backups/scientific_revision'/p.parent.name/'chapter.md'
    b.parent.mkdir(parents=True,exist_ok=True)
    if b.exists(): s=b.read_text(encoding='utf-8')
    else: b.write_text(s,encoding='utf-8')
    return p,s

def rep(s,a,b,why):
    assert a in s, why
    CHANGES.append(why)
    return s.replace(a,b)

def sec(s,a,b,new,why):
    first=s.index(a);last=s.index(b,first+len(a))
    CHANGES.append(why)
    return s[:first]+new.rstrip()+'\n\n'+s[last:]

def save(p,old,s):
    marker=r'<!-- reviewed-notebook-results:start -->.*?<!-- reviewed-notebook-results:end -->'
    assert re.findall(marker,old,re.S)==re.findall(marker,s,re.S)
    p.write_text(s,encoding='utf-8')

p,old=load(19);s=old
s=sec(s,'**Pipeline sizing**:', '**Typical pipeline parameters**:',r'''**Pipeline sizing** starts with a dimensional screening model. For horizontal, steady, isothermal, single-phase gas flow with constant $Z$, constant Darcy friction factor $f_D$, and negligible acceleration:

$$
\dot m=A\sqrt{\frac{D M_w(P_1^2-P_2^2)}{f_D L ZRT}},\qquad
Q_b=\frac{\dot m}{\rho_b},\qquad A=\frac{\pi D^2}{4}.
$$

Use $P_1,P_2$ in Pa absolute, $D,L$ in m, $M_w$ in kg/mol, $R$ in J/(mol K), $T$ in K and $\rho_b$ in kg/m³ at explicitly declared base conditions. The result is kg/s and base m³/s. This follows by integrating $dP/dz=-f_D\rho v^2/(2D)$ with $\rho=PM_w/(ZRT)$ and constant mass flow. It is an order-of-magnitude check, not the full Beggs–Brill calculation used later. Heat exchange, elevation, variable properties, acceleration and liquid phases require a more complete model. Empirical pipeline equations such as Panhandle must retain their original unit constants and applicability rather than mixing field and SI units.
''','19: replace undocumented pipeline constants with derived all-SI screening equation')
s=rep(s,'The required compression power is proportional to the flow rate and the compression ratio','For a fixed inlet state, efficiency and discharge pressure, compression power is approximately proportional to mass flow; its dependence on pressure ratio is nonlinear','19: compression ratio dependence is nonlinear')
s=s.replace(r'\eta_p',r'\eta_s')
s=rep(s,'$\\eta_s$ is the polytropic efficiency','$\\eta_s$ is the isentropic efficiency','19: correct efficiency type in ideal-gas power approximation')
s=rep(s,'and $k$ is the ratio of specific heats.', 'and $k$ is the constant ratio of specific heats. This is a constant-property isentropic approximation with an approximate real-gas $Z$ correction, not the polytropic-path formula or an exact real-gas work calculation. Use the enthalpy-rise result for the NeqSim model.','19: qualify compressor equation')
s=rep(s,'| Parameter | Typical NCS Spec | Typical UK NTS | Typical US Pipeline |','| Parameter | Illustrative contract A | Illustrative contract B | Illustrative contract C |','19: remove unsupported jurisdiction attribution from gas-quality windows')
s=rep(s,'Specifications vary by pipeline system and market, but common parameters include:', 'Specifications vary by pipeline system and market. The following teaching windows are assumed examples, not verified current NCS, UK or US requirements; each real delivery point needs its applicable contract, pressure/temperature basis and period. ISO 6976 supplies a property-calculation method, not a sales-quality window \\cite{iso6976scope}:','19: distinguish gas quality standards from sales contracts')
s=rep(s,'Exceeding the water dew point causes liquid water accumulation', 'Cooling below the water dew point can cause liquid water accumulation','19: correct condensation direction')
s=rep(s,'below the pipeline design pressure at any point (including the high point)', 'below the minimum local operating absolute pressure, including high points and transient minima','19: vapor breakout depends on operating pressure not design pressure')
s=rep(s,'The Reid Vapor Pressure (RVP) specification for pipeline crude oil is typically:', 'The following RVP limits are illustrative exercise values. RVP is a specified test property; it is not interchangeable with true vapor pressure at pipeline conditions or a universal regional requirement:','19: qualify illustrative RVP values')
s=rep(s,'where $d$ is the ideal relative density:', 'Use real relative density with real volumetric calorific value, or ideal relative density with ideal calorific value. The ideal relative density is:','19: consistent Wobbe relative-density basis')
s=rep(s,'### 19.6.2 Hydrocarbon Dew Point (Cricondentherm)', '### 19.6.2 Hydrocarbon Dew Point and Cricondentherm','19: distinguish dew point at pressure from envelope maximum')
s=rep(s,'is the specification used in gas sales contracts because it represents the worst-case condensation temperature:', 'is one possible contractual measure of the highest condensation temperature. Other contracts specify a dew point at one pressure or over a pressure interval, which requires a different comparison:','19: avoid universal cricondentherm contract claim')
s=rep(s,r'Q_m = C_d \cdot E \cdot',r'Q_m = C_d \cdot \varepsilon \cdot E \cdot','19: include gas expansibility in orifice mass flow')
s=rep(s,'where $Q_m$ is the mass flow rate, $C_d$', 'where $Q_m$ is the mass flow rate, $\\varepsilon$ is the gas expansibility factor (approximately one for an incompressible liquid), $C_d$','19: define expansibility factor')
s=rep(s,'The discharge coefficient is calculated using the Reader-Harris/Gallagher equation (ISO 5167-2):', 'The following expression shows the structure of the Reader–Harris/Gallagher correlation. The complete applicable ISO 5167-2 equation includes tap and small-pipe corrections and its limits on geometry and Reynolds number; this abbreviated display is not a fiscal implementation:','19: identify abbreviated discharge correlation')
s=rep(s,'where $\\text{Re}_D$ is the pipe Reynolds number and the tap correction terms depend', 'Here $A=(19000\\beta/\\mathrm{Re}_D)^{0.8}$, $\\mathrm{Re}_D$ is the pipe Reynolds number, and the symbolic tap correction terms depend','19: define omitted correlation parameter')
s=rep(s,r'\dot{m} = K_s \cdot \frac{\Delta t}{f^2}',r'\dot{m}=K_{\Delta t}\Delta t','19: replace unsupported generic Coriolis frequency law')
s=rep(s,'where $\\dot{m}$ is the mass flow rate, $K_s$ is the meter stiffness factor, $\\Delta t$ is the time delay between sensor signals (proportional to the Coriolis force), and $f$ is the tube vibration frequency.', 'Here $K_{\\Delta t}$ is an instrument-specific calibrated coefficient with the units needed to convert sensor time delay to mass flow. This is a local response approximation; the transmitter applies its own temperature, pressure and zero corrections. The density relation below is likewise a calibrated oscillator model, not a universal meter calibration.','19: specify instrument-specific calibration')
s=rep(s,r'u_c^2(Q_m) = \sum_{i=1}^{N} \left(\frac{\partial Q_m}{\partial x_i}\right)^2 u^2(x_i)',r'u_c^2(Q_m)=\sum_i c_i^2u^2(x_i)+2\sum_{i<j}c_ic_j\operatorname{cov}(x_i,x_j),\qquad c_i=\frac{\partial Q_m}{\partial x_i}','19: include covariance in uncertainty propagation')
s=rep(s,'where $k = 2$ for approximately 95% confidence (assuming normal distribution).', 'The shorthand $k=2$ approximates 95% coverage for an approximately normal result with sufficiently large effective degrees of freedom. It is not a general conversion from every stated instrument limit. Convert input uncertainties to standard deviations and include correlations before combination \\cite{jcgm100gum}.','19: standard uncertainty and coverage assumptions')
s=rep(s,'**Gas metering (orifice plate)**:', '**Illustrative gas-meter budget**, with independent one-standard-deviation relative inputs, ideal-density sensitivity, fixed expansibility/discharge correlations and $\\beta=0.60$. Correlation and expansibility contributions omitted here must be added for a fiscal system:','19: state assumptions for metering budget')
s=s.replace('| Orifice diameter ($d$) | 0.03 | 2.00 | 0.060 |','| Orifice diameter ($d$) | 0.03 | 2.298 | 0.069 |')
s=s.replace('| Pipe diameter ($D$) | 0.04 | 0.25 | 0.010 |','| Pipe diameter ($D$) | 0.04 | −0.298 | 0.012 |')
s=s.replace('| **Combined (RSS)** | | | **~0.51** |','| **Combined (RSS)** | | | **0.519** |')
s=rep(s,'For liquid metering, the uncertainty is typically lower', 'The geometric relative sensitivity coefficients are $2/(1-\\beta^4)$ for bore and $-2\\beta^4/(1-\\beta^4)$ for pipe diameter when $C_d$ and $\\varepsilon$ are held fixed. Their values are therefore not constant across all diameter ratios.\n\nFor liquid metering, the uncertainty is often lower','19: correct beta-dependent orifice sensitivity')
s=sec(s,'K = \\frac{N_{\\text{pulses}}}', '**Small volume prover',r'''K=\frac{N_{\mathrm{pulses}}}{V_{\mathrm{displaced,at\ meter}}}.
$$

Express the calibrated displaced volume and meter indication at the same liquid temperature/pressure basis. Steel expansion and liquid pressure/temperature corrections are applied with their specified numerator/denominator convention; multiplying an arbitrary set of correction factors onto $N/V_{base}$ is not generally valid. Use the applicable API MPMS proving procedure and traceable calibration data.

**Small volume prover''','19: correct prover K-factor volume basis')
s=s.replace('**Small volume prover\n\n**Small volume prover','**Small volume prover')
s=sec(s,'| Jurisdiction | Authority | Typical Requirement |', '### 19.9.2',r'''As a current NCS example, the Norwegian Offshore Directorate's measurement regulations, Section 10 Table 1, specify a 0.30% uncertainty limit for net oil quantity delivered or measured over a month. This is a system/measurand requirement, not a universal meter accuracy specification. Determine the relevant measurement type, measurand, coverage convention and applicable exceptions from the current regulation; the UK, US and other jurisdictions require their own review \cite{sodir2023measurement}.
''','19: replace obsolete metering authority/limits table with verified regulatory example')
s=rep(s,'where $Q_{\\text{flare}}$ is the standard volumetric flow rate of flare gas,', 'This equation assumes complete conversion of hydrocarbon carbon to CO₂ and a consistent gas molar-volume basis. Include inlet CO₂ separately when reporting total emitted CO₂, and quantify unburned methane and incomplete combustion separately for greenhouse-gas reporting. Use $M_{CO_2}=0.04401$ kg/mol when the desired output is kg per unit time. Here $Q_{\\text{flare}}$ is the standard volumetric flow rate of flare gas,','19: flare carbon balance and mass units')
s=s.replace('HC dew point (cricondentherm) is extremely','HC dew point and cricondentherm are strongly')
s=s.replace('the NCS specification (GCV 36–44','the assumed contract-A window (GCV 36–44')
s=s.replace('±0.04%, discharge coefficient ±0.5%.','±0.04%, discharge coefficient ±0.5%. Treat these as independent one-standard-deviation relative uncertainties at a diameter ratio of 0.60; ignore composition uncertainty for this exercise and state the fixed-coefficient approximation.')
save(p,old,s)

p,old=load(20);s=old
s=rep(s,'The equipment with the highest utilization factor is the **bottleneck** — it is the constraint that limits the overall system throughput. The system capacity is determined by:', 'The highest reported utilization identifies the most loaded declared criterion. It is a throughput bottleneck only if it becomes active along the chosen production change; reservoir supply, lower bounds and coupled constraints can govern instead. If all upper-limit loads scale linearly with a common feed multiplier and ratings stay fixed, a screening estimate is:','20: limit inverse-utilization capacity formula to proportional scaling')
s=rep(s,'This chapter provides the theoretical foundation for capacity checking', 'The inverse-utilization expression is not valid for nonlinear pressure loss, changing phase split, surge minima or missing constraint coverage. Solve and replay the increased-flow candidate before accepting a facility capacity.\n\nThis chapter provides the theoretical foundation for capacity checking','20: require replay for facility capacity estimate')
s=rep(s,r'SM = \frac{Q_{\text{actual}} - Q_{\text{surge}}}{Q_{\text{actual}}}',r'SM = \frac{Q_{\text{actual}} - Q_{\text{surge}}}{Q_{\text{surge}}}','20: use consistent surge-line-relative margin convention')
s=rep(s,'The stonewall flow is nearly independent of speed and represents the absolute maximum volumetric throughput.', 'The choke boundary depends on speed, gas properties and corrected map coordinates. Use the applicable vendor map; a single speed-independent flow limit is only a declared screening approximation.','20: correct compressor choke-map dependence')
s=rep(s,r'\Delta T_{\text{min}} = T_{\text{hot,out}} - T_{\text{cold,in}} \quad \text{(for countercurrent flow)}',r'\Delta T_{\mathrm{end,min}}=\min(T_{h,in}-T_{c,out},T_{h,out}-T_{c,in})','20: check both countercurrent terminal approaches')
s=rep(s,'Typical minimum approaches:', 'For a single-phase countercurrent exchanger with constant heat capacities, the minimum occurs at one terminal. With phase change or variable heat capacity, inspect the internal temperature profile for a tighter pinch.\n\nIllustrative approach targets, to be replaced by service-specific design requirements:','20: distinguish terminal approach from internal pinch')
s=sec(s,'$$\nv_{\\text{tube,max}} = C_{\\text{eros}}', 'Practical velocity limits:', 'Select tube velocity limits from the material, service, fouling/solids loading, pressure drop and vibration assessment. The petroleum-piping $C/\\sqrt{\\rho}$ screening rule is not a universal heat-exchanger tube limit.\n\nIllustrative velocity ranges:','20: remove unsupported generic tube erosional constant')
s=s.replace('Illustrative velocity ranges:\n\nPractical velocity limits:','Illustrative velocity ranges:')
s=rep(s,'The critical velocity for vortex shedding is approximately:', 'Matching the vortex-shedding frequency to a tube natural frequency gives a resonance-screening velocity:','20: resonance estimate is not universal vibration threshold')
s=rep(s,'Flow-induced vibration can cause rapid tube failure', 'This condition alone does not establish safety: fluidelastic instability, turbulent buffeting, damping and support geometry need separate checks. Flow-induced vibration can cause rapid tube failure','20: include other tube-vibration mechanisms')
s=rep(s,'where $Q$ is the volumetric flow rate, $f(\\ell)$', 'For the customary US $C_v$ convention, use $Q$ in US gal/min and $\\Delta P$ in psi with specific gravity relative to water; SI flow needs the corresponding conversion factor. Here $f(\\ell)$','20: specify Cv field-unit convention')
s=rep(s,r'\cdot Y \cdot x \cdot \sqrt{x \cdot \rho_1 \cdot P_1}',r'\cdot Y \cdot \sqrt{x_{\mathrm{sizing}} \cdot \rho_1 \cdot P_1}','20: remove erroneous extra gas-valve pressure-ratio multiplier')
s=rep(s,'where $W$ is the mass flow rate, $N_8$ is a numerical constant', 'Here $x_{\\mathrm{sizing}}=\\min(\\Delta P/P_1,F_kx_{TP})$ accounts for choking; $Y$, $F_P$, $x_{TP}$ and the unit constant must come from the selected valve-sizing convention. $W$ is the mass flow rate, $N_8$ is a numerical constant','20: define sizing pressure ratio and choking basis')
s=rep(s,r'\text{Opening} = \frac{C_{v,\text{required}}}{C_{v,\text{max}}} \times 100\%',r'f(\ell)=\frac{C_{v,\mathrm{required}}}{C_{v,\mathrm{max}}},\qquad \ell=f^{-1}\left(\frac{C_{v,\mathrm{required}}}{C_{v,\mathrm{max}}}\right)','20: valve Cv ratio is travel only for a linear characteristic')
s=rep(s,'Good control practice requires the valve to operate between 20% and 80% opening during normal operation.', 'Only a linear inherent characteristic gives travel equal to the $C_v$ ratio. Evaluate the installed characteristic, trim, noise/cavitation and required authority; 20–80% is an illustrative preferred operating band, not a universal rule \\cite{emerson2023valves}.','20: qualify valve controllability band')
s=rep(s,r'x_T = \frac{\Delta P_{\text{choked}}}{P_1} = F_k \cdot x_{TP}',r'x_{\mathrm{choked}}=\frac{\Delta P_{\mathrm{choked}}}{P_1}=F_kx_{TP}','20: distinguish terminal coefficient from critical pressure ratio')
s=rep(s,'The API RP 14E erosional velocity limits the maximum velocity in piping to prevent erosion damage:', 'The API RP 14E density-based velocity expression is an empirical screening criterion, not a general erosion-rate model or assurance against sand erosion/corrosion:','20: qualify erosional-velocity screening')
s=rep(s,'where $v_{\\text{eros}}$ is the erosional velocity (m/s), $C$ is the erosional velocity constant (typically 100–200 for continuous service in carbon steel; some operators use lower values for corrosive or sand-laden fluids), and $\\rho_m$ is the mixture density (kg/m³).', 'The customary expression uses velocity in ft/s and density in lb/ft³. If an illustrative $C_{US}=150$ is selected, convert consistently: $v_{SI}=0.3048C_{US}\\sqrt{16.01846}/\\sqrt{\\rho_{SI}}$ in m/s. A bare value of 150 is not the same coefficient in SI. Select the applicable criterion and service limits independently; this example does not qualify sand/corrosion erosion.','20: fix API14E imperial-to-SI conversion')
s=rep(s,'pipe.setLength(25.0)          # km','pipe.setLength(25000.0)       # m = 25 km','20: fix 1000-fold pipeline length error')
s=rep(s,'v_eros = C_eros / math.sqrt(rho_mix)','v_eros = 0.3048 * C_eros * math.sqrt(16.01846337 / rho_mix)','20: correct executable erosional velocity units')
s=rep(s,'print(f"Outlet pressure:       {P_out:.1f} bara")','assert 0.0 < P_out < 80.0\nassert abs(pipe.getOutletStream().getFlowRate("kg/hr")-150000.0) < 1e-5\nprint(f"Outlet pressure:       {P_out:.1f} bara")','20: test finite hydraulic response and pipeline mass closure')
s=rep(s,'where $P_{\\text{downstream,min}}$ is the minimum required arrival pressure (set by the receiving facility).', 'Here $P_{\\text{downstream,min}}$ is the minimum required arrival pressure. This ratio requires a strictly positive available pressure drop. If the inlet is already below the arrival requirement, report infeasibility explicitly rather than dividing by a nonpositive allowance.','20: pressure-drop utilization domain')
s=sec(s,'$$\nP_{\\text{back}} \\leq 0.10', 'The flare header utilization is:', 'Allowable built-up and superimposed backpressure depend on relief-valve type, overpressure allowance, service and certified manufacturer data. The often quoted 10% conventional and 50% balanced-bellows values are not universal acceptance limits; use the applicable sizing/design basis and capacity corrections.\n\nThe flare header utilization is:','20: remove universal relief backpressure limits')
s=s.replace('The flare header utilization is:\n\nThe flare header utilization is:','The flare header utilization is:')
s=rep(s,r'P(\text{bottleneck} = i) = \frac{N_i}{N_{\text{total}}}',r'\widehat P(\text{most loaded criterion}=i)=\frac{N_i}{N_{\mathrm{valid}}}','20: sampled bottleneck frequency is an estimator with explicit valid denominator')
s=rep(s,'where $N_i$ is the number of Monte Carlo trials in which equipment $i$ is the bottleneck, and $N_{\\text{total}}$ is the total number of trials.', 'Here $N_i$ counts valid trials assigned to criterion $i$, with a declared tie rule. Report invalid/unsolved trials separately and never silently remove them from reliability estimates. Specify the sampled distributions, correlations and sampling error; a design grid is not automatically a probability sample.','20: Monte Carlo coverage and failed-case accounting')
s=rep(s,r'V_{\text{slug,max}} = V_{\text{liquid,surge}} \cdot (1 - \bar{U}_{\text{liquid}})',r'\max_t\int_0^t(\dot V_{L,in}-\dot V_{L,out})\,ds\leq V_{HH}-V_{initial}','20: replace unsupported utilization-based slug capacity with inventory balance')
s=rep(s,'where $V_{\\text{liquid,surge}}$ is the total surge volume between normal and high-high level, and $\\bar{U}_{\\text{liquid}}$ is the average liquid utilization. If the expected slug volume exceeds $V_{\\text{slug,max}}$,', 'Use a consistent actual-liquid basis and include base flow, excess slug inflow and time-varying withdrawal. Capacity utilization alone cannot determine the volume that can be absorbed. If the net accumulated liquid exceeds the available level-band volume,','20: define actual surge accumulation')
s=s.replace('The time to reach surge on the remaining compressor(s) determines', 'The fastest relevant pressure, flow or trip-limit excursion determines')
s=s.replace('Sections 18.2–18.7','Sections 20.2–20.7')
s=s.replace('Using $C = 150$, calculate','Using $C_{US}=150$ with the stated imperial-to-SI conversion, calculate')
s=s.replace('the required $C_v$ is 245. Calculate','the required $C_v$ is 245. Assume a linear inherent characteristic and fixed pressure conditions. Calculate')
s=s.replace('as a percentage of current production.', 'as a percentage of current production under proportional-load scaling, then explain why a fresh nonlinear process solve is still required.')
save(p,old,s)

p,old=load(21);s=old
s=rep(s,'Every production facility has a bottleneck — one piece of equipment whose capacity limits the throughput of the entire system.', 'A facility can be limited by one or several active constraints, or by upstream supply, commercial demand or utility availability. The most loaded equipment is not necessarily a unique throughput bottleneck.','21: distinguish most-loaded item from active throughput constraint')
s=rep(s,'This objective, data-driven approach replaces subjective engineering judgment with quantified metrics.', 'This is a heuristic screening score with units of rate per currency. It does not replace NPV, engineering judgment, uncertainty analysis, installation feasibility or the interactions between modifications.','21: qualify heuristic upgrade priority score')
s=rep(s,r'\text{PI} = \frac{\text{NPV}}{\text{CAPEX}_{\text{mod}}}',r'\text{PI}=\frac{\mathrm{PV}(\text{incremental net operating cash flows})}{\mathrm{CAPEX}_{mod}}=1+\frac{\mathrm{NPV}}{\mathrm{CAPEX}_{mod}}','21: correct profitability-index definition')
s=rep(s,'Options with PI > 1.0 are economic. Options with PI > 3.0 are highly attractive and should be fast-tracked.', 'For this single initial-outlay definition, PI > 1 is equivalent to positive NPV. A high ratio alone does not determine project priority: mutually exclusive options, capital rationing, uncertainty and shutdown losses matter. The ratio NPV/CAPEX is sometimes used as a separate ranking measure and has a zero, rather than one, break-even threshold.','21: correct economic break-even threshold')
s=rep(s,'Running `findBottleneck()` at different production rates reveals the bottleneck sequence:', 'The following assumed planning data illustrate a possible bottleneck sequence. They are not outputs of the small executable fixture in this chapter; a full model and installed ratings are needed to reproduce them:','21: identify previously fabricated case-study results as assumed inputs')
s=rep(s,'The analysis shows that the HP Compressor is the first bottleneck, and a driver uprate combined with adding a cyclone inlet device to the HP Separator would provide the largest production gain per unit investment.', 'The assumed data suggest checking compressor power first. They do not establish the production gain or investment ranking; that requires solved before/after cases with all other constraints retained.','21: remove unsupported case-study optimum')
s=sec(s,'Based on the NPV analysis:', '---\n\n## 21.11', '''The candidate list is a planning exercise, not a computed NPV ranking. Separator internals, drag-reducer compatibility, compressor uprating and water-treatment expansion must each be checked against the active constraint. An option that does not relieve an active constraint may produce no extra saleable production.

For the assumed costs above, separator internals (15 MNOK), liquid-service DRA equipment (5 MNOK) and a driver uprate (45 MNOK) total 65 MNOK. Including the assumed hydrocyclone expansion adds 25 MNOK, bringing the total to 90 MNOK. No production gain, profitability index or payback is established for this hypothetical platform until currency-consistent incremental cash flows are supplied.
''','21: correct cost total and remove uncomputed PI/payback recommendations')
s=rep(s,r'\text{Value Ratio} = \frac{\Delta Q \times P_{\text{oil}} \times T_{\text{remaining}}}{C_{\text{modification}}}',r'\text{Gross value ratio}=\frac{365\,\eta_{up}\,\Delta Q\,P_{oil}\,T_{remaining}}{C_{modification}}','21: include days/year and uptime in gross value ratio')
s=rep(s,'A value ratio greater than 3–5 is typically required to justify the investment, given the uncertainties in production forecasts and commodity prices.', 'Use one currency throughout. This undiscounted gross-revenue ratio omits incremental OPEX, decline, tax, shutdown losses and timing, so it is not an investment acceptance criterion.','21: remove unsupported gross-value investment threshold')
s=sec(s,'For example, if a compressor driver uprate costs 45 MNOK', '### 21.11.3',r'''For an explicitly assumed exchange rate of 10 NOK/USD, a 45 MNOK uprate and an assumed additional 5000 bbl/day at USD 70/bbl give a **gross-revenue-only** payback:

$$
T_{gross}=\frac{45\times10^6}{5000\times70\times10\times365}
=0.0352\ \mathrm{year}=12.9\ \mathrm{days}.
$$

The calculation is an arithmetic check, not a project forecast. Actual net payback includes incremental OPEX, downtime, uptime, decline and taxes; the assumed production gain must first be established by reservoir and facility models. The exchange rate is a teaching input, not a current market quote.
''','21: correct NOK/USD payback dimensional error')
s=rep(s,'$\\Delta Q_t$ is the production gain in year $t$ (which may decline as the reservoir depletes)', '$\\Delta Q_t$ is the incremental annual produced volume in year $t$, not a daily rate (it may decline as the reservoir depletes)','21: define annual volume in NPV equation')
s=rep(s,'Debottlenecking projects typically exhibit very high IRRs (50–200%) because the initial investment is small relative to the incremental production value.', 'IRR is meaningful only when a valid cash-flow root exists; nonconventional cash flows may have multiple or no IRRs. Use NPV at the declared discount rate as the primary comparison rather than assuming a generic high return.','21: remove unsupported generic IRR range')
s=rep(s,'The following table provides order-of-magnitude costs for common debottlenecking modifications on offshore platforms (Norwegian Continental Shelf, 2024 cost level):', 'The following assumed cost and schedule ranges are classroom screening inputs, not sourced 2024 NCS estimates or vendor quotations. Establish project location, price year, currency, estimate class, installation scope, shutdown losses and uncertainty before use:','21: disclose unsourced cost estimates')
s=rep(s,'1. Statoil Engineering Reports (2014). *Debottlenecking Best Practices for North Sea Platforms*. Internal Technical Report.', '1. The hypothetical platform assumptions in this chapter are teaching data; no internal company report has been supplied or used as evidence.','21: remove unverifiable internal-report citation')
s=s.replace('calculate the payback period for each option.', 'calculate the gross and net payback for each option using an explicitly assumed exchange rate, uptime and incremental operating cost.')
save(p,old,s)
(BOOK/'verification/scientific_revision/capacity_corrections.json').write_text(json.dumps(CHANGES,indent=2),encoding='utf-8')
print('Applied',len(CHANGES),'scientific capacity corrections')
