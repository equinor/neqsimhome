"""Apply reviewed scientific corrections, retaining an explicit issue ledger."""
from pathlib import Path
import json
import re

BOOK = Path(__file__).resolve().parents[1]
OUT = BOOK / "verification" / "scientific_revision"
ledger_path = OUT / "foundations_text_changes.json"
ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else []

def revise(chapter, identifier, old, new, issue, sources):
    if not old:
        raise ValueError('Empty replacement target is unsafe: ' + identifier)
    if any(row["id"] == identifier for row in ledger):
        return
    path = next((BOOK / "chapters").glob(chapter + "*/chapter.md"))
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise ValueError("Missing original text: " + identifier)
    text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    ledger.append({"chapter": path.parent.name, "id": identifier, "issue": issue,
                   "original": old, "correction": new, "sources": sources})
    ledger_path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")

revise("ch01", "ch01_hydrostatic_gradient",
    "**Reservoir pressure** is the primary driving force for production. Initial reservoir pressure depends on the burial depth — typically 1.0–1.2 psi per foot of true vertical depth subsea (TVDss), corresponding to a normal hydrostatic gradient. For a reservoir at 3,000 m TVDss, initial pressures of 300–400 bara are typical. As production proceeds without pressure support, the average reservoir pressure declines, and the well deliverability decreases accordingly.",
    r"**Reservoir pressure** supplies the pressure potential for production. A normal water-column gradient is approximately 0.433 psi/ft for fresh water and 0.465 psi/ft for a representative saline water, equivalent to 9.8–10.5 kPa/m. The constant-density estimate $p=p_{\mathrm{surface}}+\rho g z$ gives about 295 bara at 3,000 m below a 1.01325-bara datum for $\rho=1000$ kg/m³ and $g=9.80665$ m/s². A 1 psi/ft gradient is not normal hydrostatic pressure. Actual formation pressure also reflects salinity, fluid contacts, overpressure, depletion and the pressure datum; burial depth alone is insufficient.\cite{foundationSLBgradient} As production proceeds without pressure support, reservoir pressure and deliverability generally decline.",
    "Normal hydrostatic gradient was overstated by more than a factor of two.",
    ["https://glossary.slb.com/en/terms/p/pressure_gradient", "analytical: p=p0+rho*g*z"])

revise("ch01", "ch01_pressure_budget",
    r"p_{\text{res}} = p_{wf} + \Delta p_{\text{tubing}} + \Delta p_{\text{tree}} + \Delta p_{\text{flowline}} + \Delta p_{\text{riser}} + p_{\text{sep}}",
    r"p_{\text{res}} = \Delta p_{\text{reservoir}} + \Delta p_{\text{tubing}} + \Delta p_{\text{tree}} + \Delta p_{\text{flowline}} + \Delta p_{\text{riser}} + p_{\text{sep}}",
    "The series pressure budget counted bottomhole pressure instead of reservoir drawdown.", ["analytical: series pressure balance"])
revise("ch01", "ch01_pressure_budget_definition",
    "Minimizing the downstream pressure terms (flowline loss, riser hydrostatic, separator pressure) maximizes the drawdown available for production.",
    r"Here $\Delta p_{\mathrm{reservoir}}=p_{\mathrm{res}}-p_{wf}$ is reservoir drawdown; each remaining term is a pressure difference along the same flow path and datum. For upward production the hydrostatic contribution is positive. Acceleration and pressure gains from pumps must be added with their appropriate signs when present. Reducing downstream losses can increase available drawdown, subject to the coupled well and network solution.",
    "Defined pressure terms and the applicability of the simplified path balance.", ["analytical: steady momentum balance"])
revise("ch01", "ch01_separator_control",
    "The separator pressure is set by a balance between liquid level control and the suction pressure of the first-stage compressor.",
    "The separator pressure follows its gas inventory and gas-outlet/compressor controls; the liquid-level controller primarily manipulates liquid withdrawal. These loops interact, but liquid level is not the pressure setpoint.",
    "Corrected pressure-control versus liquid-level-control mechanisms.", ["analytical: gas and liquid inventory balances"])
revise("ch01", "ch01_backpressure_gain",
    "This chain of pressure dependencies means that *reducing the separator pressure by 5 bar can increase well deliverability by 10% or more*, because the back-pressure reduction propagates all the way to the sandface. This is the most common and most valuable optimization lever in production operations.",
    r"The gain is governed by the coupled pressure response. In the limiting linear-PI example with unchanged tubing losses and an initial drawdown of 50 bar, a 5-bar reduction in bottomhole pressure raises rate by $5/50=10\%$. A separator-pressure change need not propagate one-for-one to bottomhole pressure: friction, multiphase holdup, choke criticality and facility constraints determine the actual response. The network examples therefore solve and verify that response explicitly.",
    "Replaced an unsupported universal gain with a derived, fully stated limiting case.", ["analytical: q=PI*drawdown"])
revise("ch01", "ch01_hypothetical_tradeoff",
    "A compressor engineer, seeking to minimize compressor power, increases the first-stage separator pressure from 30 bara to 50 bara. This reduces the compression ratio, lowers the compressor power consumption by 15%, and reduces wear on the compressor. Viewed in isolation, this is clearly beneficial.\n\nHowever, the higher separator pressure increases the back-pressure on the wells. The field production rate drops by 8%. The revenue loss from reduced production far exceeds the energy savings from the compressor. The *system* optimum lies at a lower separator pressure than the *compressor* optimum.",
    "Consider a hypothetical operating change from 30 to 50 bara separator pressure. Assume a matched calculation predicts 15% less compressor power and 8% less saleable production. These percentages are assumptions for illustrating the decision, not measured improvements or a prediction for the book's fluid. Accept the change economically only if the value of power/fuel saved exceeds lost product revenue and any other incremental costs. Pressure ratio alone does not establish changes in wear or a field-wide optimum.",
    "Separated an invented trade-off from a measured or simulated result and gave the actual economic criterion.", ["analytical: incremental revenue minus incremental cost"])
revise("ch01", "ch01_arps_limit",
    "where $q_i$ is the initial rate, $D_i$ is the initial decline rate, and $b$ is the decline exponent ($b = 0$ for exponential, $0 < b < 1$ for hyperbolic, $b = 1$ for harmonic decline).",
    r"where $q_i$ is initial rate, $D_i$ is nominal initial decline with units inverse time, and $b$ is dimensionless. The displayed expression applies for $b>0$; its limit at $b\to0$ is $q(t)=q_i\exp(-D_i t)$, not direct substitution of zero into $1/b$. Classical hyperbolic decline uses $0<b<1$ and harmonic decline uses $b=1$. Forecasting also requires a stated terminal decline or economic limit; the curve is empirical and does not enforce reservoir material balance.",
    "Defined the b=0 limit and dimensional/forecast domain.", ["analytical: exponential limit of (1+b*x)^(-1/b)"])
revise("ch01", "ch01_pressure_staging",
    r"The optimal pressure staging can be estimated by the equal compression ratio rule. For $n$ stages with inlet pressure $p_1$ and final pressure $p_n$, the optimal stage pressures follow:" + "\n\n$$\n" + r"\frac{p_{k+1}}{p_k} = \left(\frac{p_n}{p_1}\right)^{1/n} \quad \text{for } k = 1, \ldots, n-1" + "\n$$\n\n" + "In practice, the optimal pressures deviate from this rule due to the nonlinear phase behavior of real fluids — the amount of gas liberated at each stage depends on the composition and temperature, not just the pressure ratio. NeqSim's flash calculations capture these effects rigorously.",
    r"For $n$ separator pressure levels, a geometric sequence is one possible initial guess, with $n-1$ pressure intervals:" + "\n\n$$\n" + r"\frac{p_{k+1}}{p_k} = \left(\frac{p_n}{p_1}\right)^{1/(n-1)}, \qquad k=1,\ldots,n-1." + "\n$$\n\n" + "This identity is not a separation optimum. Separator pressures must be optimized against recovered product value, quality and recompression constraints using flashes at each stage. Equal pressure ratios minimize ideal, perfectly intercooled compressor work only under additional assumptions: identical stage inlet temperatures and efficiencies, unchanged gas composition and flow, and negligible interstage pressure losses. Those compressor assumptions usually fail across a separation train, where each stage releases a different amount and composition of gas.",
    "Fixed the interval count and removed an invalid separation-optimum interpretation.", ["analytical: product of pressure ratios", "https://www.grc.nasa.gov/www/k-12/airplane/compth.html"])
revise("ch01", "ch01_compression_efficiency",
    r"The total compression power $W$ for an ideal gas compressing from $p_1$ to $p_2$ in $n_s$ stages with a polytropic efficiency $\eta_p$ is:",
    r"For a calorically perfect ideal gas, $n_s$ compressor stages with equal pressure ratios, identical suction temperature $T_1$ after perfect intercooling, identical stage isentropic efficiency $\eta_s$ and negligible intercooler pressure loss give the shaft-power estimate:",
    "The original formula used isentropic efficiency but labeled it polytropic.", ["https://www.grc.nasa.gov/www/k-12/airplane/compth.html"])
revise("ch01", "ch01_compression_equation",
    r"W = \frac{n_s}{\eta_p} \cdot \frac{\gamma}{\gamma - 1} \cdot Z \, R \, T_1 \cdot \dot{m} \cdot \left[\left(\frac{p_2}{p_1}\right)^{(\gamma - 1)/(\gamma \, n_s)} - 1\right]",
    r"W = \frac{n_s}{\eta_s} \frac{\gamma}{\gamma - 1} R \, T_1 \dot{m} \left[\left(\frac{p_2}{p_1}\right)^{(\gamma - 1)/(\gamma n_s)} - 1\right]",
    "Made the ideal-gas formula consistent with its stated model and efficiency.", ["https://www.grc.nasa.gov/www/k-12/airplane/compth.html"])
revise("ch01", "ch01_compression_units",
    r"where $\gamma$ is the heat capacity ratio, $Z$ is the compressibility factor, $R$ is the specific gas constant, $T_1$ is the suction temperature, and $\dot{m}$ is the mass flow rate. In practice, real-gas effects, interstage cooling, and compressor characteristic curves make the calculation more complex — these are the subjects of Chapters 12 and 13.",
    r"Here $\gamma=c_p/c_v$ is constant, $R$ is the specific gas constant in J/(kg K), $T_1$ is in K and $\dot m$ is in kg/s, so $W$ is in W. All pressure ratios use absolute pressure. This expression uses isentropic efficiency; polytropic efficiency appears inside the temperature-ratio exponent for a differential-stage ideal-gas model and is not interchangeable with $\eta_s$. Real-gas enthalpy changes and actual intercooling are calculated explicitly in Chapters 14–15.\cite{foundationNASAcompression}",
    "Corrected units, efficiency interpretation, and chapter references.", ["https://www.grc.nasa.gov/www/k-12/airplane/compth.html"])
revise("ch01", "ch01_ospar_limit",
    "Typical requirements are less than 30 mg/L dispersed oil for offshore discharge (OSPAR convention) and less than 5 mg/L for reservoir reinjection (to avoid formation damage).",
    r"OSPAR Recommendation 2001/1, as amended, uses 30 mg/L dispersed oil as a flow-weighted monthly average for produced/displacement-water discharges; it is not a universal instantaneous outlet specification. The applicable permit can impose additional controls.\cite{foundationOSPAR2023} Reinjection quality must be selected from formation-compatibility and injectivity evidence, including oil/solids size distributions, filterability and chemistry; no universal 5 mg/L oil limit establishes protection against formation damage.",
    "Corrected averaging basis and removed a falsely universal injection-quality limit.", ["https://oap.ospar.org/en/ospar-assessments/quality-status-reports/qsr-2023/thematic-assessments/offshore-industry/response/"])
revise("ch01", "ch01_dynamic_reference", "Chapter 20 develops dynamic simulation in detail.", "Chapter 29 develops dynamic simulation in detail.", "Corrected the scientific prerequisite reference.", [])
revise("ch01", "ch01_codas_reference",
    "Codas, A., Campos, S., Misener, R., Camponogara, E., and Experiment, M. (2012). Integrated Production Optimization of Oil Fields with Pressure and Routing Constraints. *Computers & Chemical Engineering*, 46, 1–17.",
    "Codas, A., Campos, S., Camponogara, E., Gunnerud, V., and Sunjerga, S. (2012). Integrated production optimization of oil fields with pressure and routing constraints: The Urucu field. *Computers & Chemical Engineering*, 46, 178–189. DOI: 10.1016/j.compchemeng.2012.06.016.",
    "Corrected invented/misattributed authors, title and page range from the publisher record.", ["https://www.sciencedirect.com/science/article/pii/S0098135412001925"])

ch01 = next((BOOK / "chapters").glob("ch01*/chapter.md"))
current = ch01.read_text(encoding="utf-8")
if not any(row["id"] == "ch01_gain_table" for row in ledger):
    old = current[current.index("The economic value of production optimization is substantial"):current.index("### 1.1.6 Historical Perspective")]
    new = r"""The value of optimization must be demonstrated against a specified baseline. Codas et al.'s Urucu study connects calibrated well/network models, pressure constraints and routing decisions; it supports the integrated workflow rather than a universal percentage gain.\cite{foundationCodas2012} Table 1.1 identifies quantities that an optimization study should measure.

| Improvement area | Quantity to compare against the baseline | Mechanism to test |
|---|---|---|
| Oil or gas production | Saleable production at matched reservoir and facility conditions | Back-pressure, rate allocation and routing |
| Recovery | Cumulative produced volume divided by a stated initial resource | Pressure maintenance and sweep |
| Energy | Net shaft/electrical energy per saleable unit | Pressure staging, recycle and efficiency |
| Reliability | Availability and maintenance intervals from operating records | Vibration, fouling and thermal cycling |
| Export quality | Off-spec frequency using the contract's sampling/averaging basis | Treatment and control performance |
| Chemicals | Active-chemical consumption at matched protection targets | Inhibitor concentration and recovery |
| Deferred investment | Discounted incremental cash flow at the revised investment date | Verified usable installed capacity |

For an illustrative oil-only calculation, 100,000 bbl/d, a 2% increase, 365 operating days/year and a constant price of US$60/bbl give US$43.8 million/year of additional gross revenue. Taxes, royalties, incremental operating cost, outages and gas/oil-equivalent conversion are excluded. A separate US$500-million investment deferred two years at a 10% annual discount rate has a time-zero cost reduction of $500[1-(1.10)^{-2}]=86.8$ million dollars if all other cash flows remain unchanged. This is a transparent timing calculation, not evidence that an actual deferral is technically feasible.

"""
    revise("ch01", "ch01_gain_table", old, new, "Replaced unsupported industry-wide percentage gains with measurable benefit definitions and dimensionally explicit economic examples.", ["https://www.sciencedirect.com/science/article/pii/S0098135412001925", "analytical: revenue and discounted cost"])

revise("ch01", "ch01_fuel_fraction",
    "The fuel gas consumption is typically 8–12% of the total gas production, which means that fuel gas demand competes directly with gas export revenue.",
    r"Fuel share depends on duty, efficiency, heating value and available gas rate. For example, 20 MW net output at 35% LHV efficiency with 50 MJ/kg fuel requires $20/(0.35\times50)=1.143$ kg/s of fuel, or 1.14% of a 100 kg/s gas feed. The same duty consumes 11.4% of a 10 kg/s feed. Fuel gas demand therefore competes directly with gas export revenue, and no fixed percentage is transferable between fields.",
    "Replaced an unsupported fuel fraction with an explicit energy-balance example.", ["analytical: m_fuel=W/(eta*LHV)"])
revise("ch01", "ch01_steady_state_stability",
    "**Steady-state simulation** calculates the equilibrium operating point of a process given fixed inputs. Time does not appear in the equations — the system is assumed to have reached a stable state.",
    "**Steady-state simulation** calculates a time-independent solution for specified inputs and boundary conditions. Material and energy accumulation vanish, but dynamic stability does not follow from solving those algebraic balances. A steady solution can be unstable; stability requires perturbation/dynamic analysis with the relevant equipment and controls.",
    "Separated existence of a steady solution from dynamical stability.", ["analytical: algebraic equilibrium versus perturbation eigenvalues"])
revise("ch01", "ch01_fullplant_solver_claim",
    "The `ProcessModel` iterates between the areas until the shared boundary streams converge, enabling full-plant optimization where changes in one area propagate to all others.",
    "A `ProcessModel` executes configured process areas and allows downstream areas to consume updated streams. Feedback across areas requires correctly configured recycle/convergence handling and an explicit boundary-residual check; adding areas is not itself proof of a converged whole-plant solution.",
    "Removed an automatic full-plant convergence guarantee.", ["source: neqsim.process.processmodel.ProcessModel#run"])
revise("ch01", "ch01_simultaneous_solver_claim",
    "Each element is connected through streams, and the entire system is solved simultaneously.",
    "Equipment is connected through streams and normally evaluated sequentially; specified recycle loops require iteration. Coupled hydraulic network equations may use a simultaneous solver. The chosen execution and convergence scheme is part of the model specification.",
    "Distinguished sequential process execution from simultaneous hydraulic solving.", ["source: neqsim.process.processmodel.ProcessSystem#run"])
revise("ch01", "ch01_runtime_claims",
    "NeqSim's fast computation speed (Java-based with efficient EOS solvers) makes it practical to embed rigorous models directly in optimization loops for many problems, reducing the need for surrogate approximations. A typical NeqSim flash calculation completes in 1–5 milliseconds, and a full process model with 20 equipment items evaluates in 0.5–5 seconds.",
    "Measure warm-start and cold-start runtimes for the actual composition, phase region, recycle structure and hardware before setting an optimization budget. The execution records for this book retain elapsed time per example. Near-critical flashes, hydrate calculations and difficult columns can be much more expensive than a single-phase TP flash, so equipment count alone is not a runtime predictor.",
    "Removed unbenchmarked universal runtime claims and identified the actual measured evidence.", ["verification: foundations_release_audit.json and per-chapter execution reports"])

current = ch01.read_text(encoding="utf-8")
if not any(row["id"] == "ch01_software_comparison" for row in ledger):
    old = current[current.index("Table 1.2 compares NeqSim"):current.index("### 1.4.3 Key Capabilities")]
    new = r"""Software selection should follow the required calculation and validation evidence. Table 1.2 gives criteria used in this book rather than an unversioned ranking of simulator products. Commercial HYSYS/UniSim and ProMax workflows depend on purchased options and supported interfaces. Other open-source tools also support automation: DWSIM documents native dynamic simulation, Python/.NET automation and an MCP interface.\cite{foundationDWSIM2026}

| Criterion | Evidence to request |
|---|---|
| Thermodynamic applicability | Model equations, component/interaction data, valid domain and independent property comparisons |
| Equipment capability | Implemented physics, installed limits, boundary conditions and convergence diagnostics |
| Automation | Documented variable names, units, input/output roles and reproducible scripts |
| Dynamics | Explicit storage/transport equations, time-step convergence and control-response checks |
| Reproducibility | Software revision, runtime, input data, tolerances and output provenance |
| Deployment and licensing | License terms, runtime/platform support and the actual purchased or installed modules |

NeqSim supplies source access, a Java/Python bridge and process automation used by the worked examples. Their scientific value comes from the verified model, not from the interface or the license alone.

"""
    revise("ch01", "ch01_software_comparison", old, new, "Removed demonstrably false DWSIM dynamic/MCP/Python entries and replaced unversioned feature assertions with evidence-based selection criteria.", ["https://dwsim.org/", "https://dwsim.org/tutorials/en/index.html"])

revise("ch01", "ch01_exercise_energy_basis",
    r"assuming $\gamma = 1.3$, $Z = 0.9$, $T_1 = 313$ K, $\eta_p = 0.80$, and 3 stages. Is the revenue gain from 10% increased production (at \$60/bbl, 100,000 bbl/d base rate) likely to exceed the additional compression cost (at \$0.05/kWh fuel cost)?",
    r"assuming $\gamma=1.3$, $R=450$ J/(kg K), $T_1=313$ K, $\eta_s=0.80$ and three perfectly intercooled stages. Use a baseline gas flow of 100 kg/s and a 10% increase in both gas and oil rate. Compare the incremental gas-compression energy cost at US$0.05/kWh with the incremental gross oil revenue at US$60/bbl and a 100,000-bbl/d baseline. State the exclusions: fixed efficiency, ideal gas, no pressure losses, unchanged gas/oil ratio, and no taxes or additional equipment/operating costs.",
    "Made the economic exercise solvable by supplying a gas-flow/energy basis and matching the corrected efficiency convention.", ["analytical: ideal intercooled compression and revenue"])

revise("ch02", "ch02_cubic_roots",
    "This cubic equation has one or three real roots. At conditions above the critical point (supercritical), there is one real root. At conditions within the two-phase envelope, there are three real roots — the smallest corresponds to the liquid phase, the largest to the vapor phase, and the middle root is physically meaningless.",
    r"A cubic at fixed temperature, pressure and composition has one or three real roots, with repeated roots at discriminant-zero conditions. When three admissible roots exist, the outer roots are liquid-like and vapor-like candidates; the middle branch is mechanically unstable. Root count is not a mixture phase-stability test: the coexisting phases have different compositions, and a mixture can split even when the cubic at its overall composition has only one admissible root. Fugacity equality plus a Gibbs-energy stability test selects the equilibrium state.\cite{soave1972,foundationMichelsen1982}",
    "Corrected the false equivalence between three roots and the mixture two-phase envelope.", ["https://www.sciencedirect.com/science/article/pii/0378381282850012"])
revise("ch02", "ch02_ssi_update",
    r"K_i^{\text{new}} = K_i^{\text{old}} \frac{\phi_i^L}{\phi_i^V}",
    r"K_i^{\text{new}} = \frac{\phi_i^L(\mathbf{x})}{\phi_i^V(\mathbf{y})} = K_i^{\text{old}}\frac{f_i^L}{f_i^V}",
    "The former update multiplied by K twice; corrected using fugacity equality.", ["analytical: fL/fV=(phiL/phiV)/Kold"])
revise("ch02", "ch02_ssi_convergence",
    r"5. **Check convergence:** If $\sum_i (\ln K_i^{\text{new}} - \ln K_i^{\text{old}})^2 < \epsilon$, stop; otherwise return to step 2.",
    r"5. **Check convergence:** Require small component fugacity residuals $\max_i|\ln(f_i^L/f_i^V)|$ for materially present components, normalized phase compositions, component balances and admissible phase fractions. A small change in $\ln K_i$ alone can reflect damping or stagnation. Recheck stability before accepting a trivial $K_i=1$ solution.",
    "Replaced an iteration-step-only stop criterion with physical equilibrium and balance conditions.", ["https://www.sciencedirect.com/science/article/pii/0378381282850012"])
revise("ch02", "ch02_rachford_domain",
    r"The Rachford-Rice equation is monotonic in $\beta$ and has a unique solution in the interval $[\beta_{\min}, \beta_{\max}]$, where:" + "\n\n$$\n" + r"\beta_{\min} = \frac{1}{1 - K_{\max}}, \qquad \beta_{\max} = \frac{1}{1 - K_{\min}}" + "\n$$\n\n" + "This property makes it straightforward to solve using Newton-Raphson or bisection methods.",
    r"For fixed positive $K_i$ and normalized nonnegative $z_i$, define the left-hand side as $F(\beta)$. On the physical interval $0\le\beta\le1$," + "\n\n$$\n" + r"F'(\beta)=-\sum_i\frac{z_i(K_i-1)^2}{[1+\beta(K_i-1)]^2}\le0." + "\n$$\n\n" + r"An interior two-phase root exists when $F(0)>0$ and $F(1)<0$, and is unique unless the nonzero-composition components all have $K_i=1$. Otherwise the fixed-K calculation selects a single-phase endpoint; phase stability still needs the EOS test. The poles $1/(1-K_{\max})$ and $1/(1-K_{\min})$ can bound an algebraic search when the K-values straddle unity, but they are not physical vapor-fraction limits. Use safeguarded Newton iteration or bisection on $[0,1]$ for a bracketed two-phase case.\cite{rachford1952}",
    "Corrected physical phase-fraction bounds, root existence and the all-K=1 degeneracy.", ["analytical: Rachford-Rice derivative and endpoint signs"])
revise("ch02", "ch02_cpa_not_hv",
    "In NeqSim, the CPA equation of state with Huron-Vidal mixing rules effectively combines EOS and activity coefficient approaches — it uses SRK for the physical contribution and an activity coefficient model for the association/non-ideal contribution. For most production optimization applications, this hybrid approach (CPA) is preferred over a pure activity coefficient model because it handles both the vapor and liquid phases consistently across all pressures.",
    "CPA and Huron–Vidal address different model contributions. CPA adds a site-association free-energy term derived from Wertheim theory to a cubic physical term; it is not an NRTL/activity-coefficient association correction. Huron–Vidal is an excess-Gibbs-energy mixing rule for the cubic contribution and can be used where its parameters and implementation support the system. The chosen CPA association scheme, cross-association rules and interaction data must be stated separately. No such model is validated at all pressures merely because it treats both phases with one framework.",
    "Corrected a conflation of CPA association and Huron–Vidal mixing theory.", ["source: neqsim.thermo.phase.PhaseSrkCPAs", "source: neqsim.thermo.mixingrule.EosMixingRuleHandler"])
revise("ch02", "ch02_departure_sign",
    r"H - H^{\text{ig}} = RT(Z - 1) + \frac{a - T \frac{da}{dT}}{b} \ln\left(\frac{v + b}{v}\right)",
    r"H - H^{\text{ig}} = RT(Z - 1) + \frac{T \frac{da}{dT}-a}{b} \ln\left(\frac{v + b}{v}\right)",
    "Corrected the sign of the SRK enthalpy departure attraction term.", ["https://idaes-pse.readthedocs.io/en/2.0.0/explanations/components/property_package/general/eos/cubic.html"])
revise("ch02", "ch02_entropy_reference",
    r"S - S^{\text{ig}} = R \ln\left(\frac{v - b}{v}\right) + \frac{\frac{da}{dT}}{b} \ln\left(\frac{v + b}{v}\right)",
    r"S - S^{\text{ig}}(T,P) = R \ln(Z-B) + \frac{\frac{da}{dT}}{b} \ln\left(\frac{v + b}{v}\right)",
    "Made entropy departure consistent with the same-temperature-and-pressure ideal-gas reference.", ["https://idaes-pse.readthedocs.io/en/2.0.0/explanations/components/property_package/general/eos/cubic.html"])
revise("ch02", "ch02_departure_basis",
    "The enthalpy departure from the ideal gas state is calculated from the EOS:",
    r"In this subsection $H$, $S$ and $C_p$ denote molar properties (J/mol, J/(mol K), and J/(mol K)); $v$ is molar volume and composition is fixed. The residual is relative to an ideal gas at the same $T$, $P$ and composition. These unshifted SRK expressions assume temperature-independent $b$ and the stated classical mixing rule. The NeqSim stream API's unqualified enthalpy value instead represents an extensive flow-basis quantity; specify a unit such as J/mol when comparing with these equations.\cite{foundationIDAEScubic} The molar enthalpy departure is:",
    "Defined reference state, molar dimensions and limits of the analytical departure expressions.", ["https://idaes-pse.readthedocs.io/en/2.0.0/explanations/components/property_package/general/eos/cubic.html"])
revise("ch02", "ch02_newton_derivatives",
    "Newton-Raphson methods can accelerate convergence by using second-derivative information.",
    "Newton–Raphson methods use the Jacobian, the first derivatives of the residual equations with respect to their unknowns. Fugacity-composition derivatives can themselves involve second derivatives of a thermodynamic potential.",
    "Clarified what the Newton Jacobian differentiates.", ["analytical: Newton residual linearization"])
revise("ch02", "ch02_trivial_solution",
    "**Trivial solution:** Both phases converge to the same composition — indicates a single-phase condition",
    "**Trivial solution:** Both trial phases converge to the same composition; this can be numerical stagnation or a true single phase. Resolve it with stability analysis rather than accepting K=1 automatically",
    "Identical trial compositions do not establish thermodynamic stability.", ["https://www.sciencedirect.com/science/article/pii/0378381282850012"])
revise("ch02", "ch02_surface_tension_trend",
    "Surface tension decreases as conditions approach the critical point (where the two phases become identical) and increases with pressure for gas-liquid systems far from the critical region. For separator design, typical gas-condensate surface tensions are 5–15 mN/m, while crude oil–gas surface tensions are 15–30 mN/m.",
    "Interfacial tension tends to zero as coexisting phases become identical at a critical point. Its pressure dependence away from that point depends on composition and temperature; increasing pressure does not imply a universal increase. Use measured or validated interfacial tension at the separator conditions for droplet/coalescence calculations rather than a generic range.",
    "Removed a false universal pressure trend and unqualified interfacial-tension ranges.", ["analytical: parachor density/composition difference"])
revise("ch02", "ch02_exercise_phase_count",
    "Enable multi-phase checking and verify that NeqSim predicts three phases (gas, hydrocarbon liquid, aqueous).",
    "Enable multi-phase checking and determine the stable phase count rather than prescribing it. At these conditions methane is above its pure-component critical temperature; expect a methane-rich fluid and an aqueous liquid, not a separate methane liquid merely because three-phase checking is enabled. Check phase compositions and component closure.",
    "Corrected a physically false demanded three-phase result for methane/water at293.15K.", ["analytical: methane critical temperature190.56K", "targeted test: methane-water phase and component balances"])
revise("ch02", "ch02_exercise_viscosity_trend",
    "Plot the result and explain the trend — why does viscosity initially decrease with pressure, then increase?",
    "Plot the result, identify whether it is monotonic over the sampled range, and relate it to dilute-gas and dense-fluid transport. Do not impose an initial decrease that the selected model or reference data may not show.",
    "Removed a leading exercise statement that dictated an unsupported viscosity minimum.", ["source: selected transport model; requires calculated trend"])
