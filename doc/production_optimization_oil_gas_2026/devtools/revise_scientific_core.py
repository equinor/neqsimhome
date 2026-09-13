"""Targeted, recorded scientific corrections; run once against the reviewed text."""
import ast
import json
import re
from pathlib import Path
BOOK = Path(__file__).resolve().parents[1]
REPORT = BOOK / "verification/scientific_revision"
REPORT.mkdir(parents=True, exist_ok=True)
CHANGES = []


def load(number):
    path = next((BOOK / "chapters").glob(f"ch{number:02d}_*/chapter.md"))
    text = path.read_text(encoding="utf-8-sig")
    backup = BOOK / ".build/backups/scientific_revision" / path.parent.name / "chapter.md"
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        backup.write_text(text, encoding="utf-8")
    else:
        text = backup.read_text(encoding="utf-8")
    return path, text


def replace(text, old, new, topic):
    if old not in text:
        raise AssertionError("Unmatched correction: " + topic)
    CHANGES.append(topic)
    return text.replace(old, new)


def section(text, start, end, new, topic):
    a, b = text.index(start), text.index(end, text.index(start)+len(start))
    CHANGES.append(topic)
    return text[:a]+new.rstrip()+"\n\n"+text[b:]


def fence(text, key, code):
    matches = [m for m in re.finditer(r"^```python[^\n]*\n(.*?)^```", text, re.M|re.S) if key in m[1]]
    assert len(matches)==1, (key,len(matches))
    m=matches[0]
    return text[:m.start()]+"```python\n"+code.rstrip()+"\n```"+text[m.end():]


def save(path, old, new):
    pattern=r"<!-- reviewed-notebook-results:start -->.*?<!-- reviewed-notebook-results:end -->"
    assert re.findall(pattern,old,re.S)==re.findall(pattern,new,re.S), "Notebook blocks changed"
    path.write_text(new,encoding="utf-8")


probe=(BOOK/"devtools/scientific_optimization_probe.py").read_text(encoding="utf-8")
probe_lines=probe.splitlines()
functions={node.name:"\n".join(probe_lines[node.lineno-1:node.end_lineno]) for node in ast.parse(probe).body if isinstance(node,ast.FunctionDef)}

# Chapter 29: real inventory evolution, controller sign, and conservation.
path,original=load(29)
t=original
t=replace(t,"A separator with 10 m³ volume and 100 m³/hr throughput has a time constant of 6 minutes (360 seconds). Larger vessels respond more slowly — they provide more buffering against disturbances.","For 10 m³ of liquid inventory and 100 m³/hr liquid throughput, this ratio is a residence time of 360 s. It is not generally the level-loop time constant: with fixed withdrawal, level integrates the inlet–outlet mismatch and has no finite open-loop settling time. A first-order level time constant requires a specified level-dependent outlet relation or an identified closed-loop model \\cite{skogestad2003simc}.","29: distinguish liquid residence time from integrating level dynamics")
t=replace(t,"For a separator liquid level:","A residence-time scale, distinct from a level-loop time constant, is:","29: correct residence-time definition")
t=replace(t,r"\tau = \frac{V_{\text{vessel}}}{\dot{V}_{\text{throughput}}}",r"t_{\mathrm{res}} = \frac{V_L}{\dot{V}_L}","29: liquid inventory basis")
t=replace(t,"where $A_{\\text{cross}}(h)$ is the cross-sectional area of the liquid surface at level $h$.","Here $A_{\\text{cross}}(h)=dV_L/dh=2L\\sqrt{h(D-h)}$ is the horizontal free-surface area. This simplified level balance assumes constant liquid density and negligible interphase mass transfer; the NeqSim example below instead integrates component inventory and energy before flashing.","29: level-area derivative and assumptions")
t=replace(t,"$f$ is the friction factor", "$f$ is the Darcy friction factor", "29: specify Darcy convention")
t=replace(t,"Over 95% of control loops in oil and gas facilities use some form of PID control.","PID is widely used in regulatory process control.","29: remove unsupported PID prevalence statistic")
t=section(t,"**Internal Model Control (IMC)** tuning.","### 29.3.4",r"""**SIMC PI tuning.** For a stable FOPDT process with gain $K_p$, time constant $\tau$ and delay $\theta$, use the following PI starting values \cite{skogestad2003simc}:

$$
K_c=\frac{\tau}{K_p(\lambda+\theta)},\qquad
T_i=\min[\tau,4(\lambda+\theta)],\qquad T_d=0.
$$

The desired response time $\lambda$ is a tuning choice; choosing it at least as large as the effective delay is a conservative starting point, not a universal stability guarantee. The sign must produce negative feedback. Integrating processes require the integrating-process gain form. Derivative tuning depends on the identified lag structure and PID implementation; adding $T_d=\theta/2$ to this PI rule is not the SIMC rule.
""","29: replace mixed IMC PI/PID formula with sourced SIMC PI")
t=section(t,"- **Direct acting**:","---\n\n## 29.4",r"""- **Direct acting**: Measurement rises and the manipulated output rises. Both an opening gas outlet valve for pressure control and an opening liquid outlet valve for level control normally require this action.
- **Reverse acting**: Measurement rises and the manipulated output falls; for example, a heating-duty command falls when outlet temperature rises.

The preceding mathematical PID uses $e=SP-PV$. NeqSim's `ControllerDeviceBaseClass` internally uses $PV-SP`; `setReverseActing(False)` therefore gives direct action for positive gain. The level transmitter returns a fraction from 0 to 1, so a 50% level setpoint is `0.5`, not `50`. Test the sign of the complete actuator–process path with a small perturbation; valve fail position alone does not determine the required feedback sign.
""","29: correct feedback action and native level fraction")
t=t.replace("$PV-SP`","$PV-SP$")
t=replace(t,"The secondary loop must be 3–5 times faster than the primary loop for cascade to be effective.","A secondary loop several times faster than the primary is a useful design aim; identify both responses and check their interaction. An outlet flow controller rejects outlet-pressure and valve disturbances. It does not detect an incoming slug before the level changes unless a separate feedforward measurement supplies that information.","29: cascade disturbance path")
t=replace(t,"When a slug arrives, the FC rapidly adjusts the valve to maintain the flow set point, long before the level controller needs to respond.","The flow loop rapidly tracks the flow setpoint requested by the level controller and rejects disturbances in the outlet path.","29: remove anticipatory cascade claim")
t=replace(t,"This ensures smooth transitions between normal operation and protective actions.","A designed split-range sequence can coordinate these valves. This regulatory strategy is separate from independent pressure relief and shutdown functions; a numerical output split alone establishes neither smooth transitions nor protection adequacy.","29: split-range control is not independent relief")
dynamic_code="""from pathlib import Path
import json
import jpype
import numpy as np
import matplotlib.pyplot as plt
jneqsim = jpype.JPackage("neqsim")
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
Path("figures").mkdir(exist_ok=True)
"""+functions["dynamic_case"]+"""

coarse = dynamic_case(0.5)
fine = dynamic_case(0.25)
coarse_rows = np.asarray(coarse["series"])
fine_rows = np.asarray(fine["series"])
assert np.max(np.abs(coarse_rows[:, 1]-fine_rows[1::2, 1])) < 0.001
assert np.max(np.abs(coarse_rows[:, 2]-fine_rows[1::2, 2])) < 0.01
assert abs(fine_rows[-1, 1]-fine["setpoint_fraction"]) < 0.002
assert np.max(fine_rows[:, 5]) > fine["base_liquid_kg_s"]
print("Initial inventory kg:", fine["mass0_kg"])
print("Final time, level fraction, pressure bara, temperature C, mass kg, liquid kg/s:")
print(fine_rows[-1].tolist())
print("Maximum relative mass/energy residuals:",
      fine["max_mass_relative_residual"], fine["max_energy_relative_residual"])
with open("ch29_inventory_checks.json", "w") as handle:
    json.dump({"coarse": coarse, "fine": fine}, handle, indent=2)
fig, axes = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
for ax, column, label in zip(axes, [1, 2, 5],
        ["Liquid level / diameter", "Pressure (bara)", "Liquid withdrawal (kg/s)"]):
    ax.plot(fine_rows[:, 0], fine_rows[:, column], label="dt = 0.25 s")
    ax.plot(coarse_rows[:, 0], coarse_rows[:, column], "--", label="dt = 0.5 s")
    ax.set_ylabel(label)
    ax.grid(True, alpha=0.3)
axes[0].axhline(0.5, color="black", linewidth=0.8)
axes[0].legend()
axes[-1].set_xlabel("Time (s)")
fig.tight_layout()
fig.savefig("figures/ch29_verified_level_inventory.png", dpi=180)
# Continue the instrument examples with the final vessel from the fine run.
process = ProcessSystem()
process.add(sep)
PT100 = jneqsim.process.measurementdevice.PressureTransmitter(
    "PT-100", sep.getGasOutStream())
PT100.setUnit("bara")
"""
t=fence(t,"# --- Fluid definition ---",dynamic_code)
t=replace(t,"The following example demonstrates dynamic separator level control in NeqSim:","The following example checks a NeqSim two-component SRK vessel with explicit inventory initialization, VU flashes and a PI controller acting on prescribed liquid withdrawal. Gas withdrawal is fixed. The 2.0 kg/s feed rises to 2.4 kg/s for 20 s; this is a defined feed pulse, not a pipeline slug prediction. The controller output is a liquid mass-flow command in kg/s, with gain 0.10 kg/s per percentage point of level, integral time 30 s and bounds 0–6 kg/s. It is not a valve-hydraulics or pressure-control model. Each time step uses a new calculation identity, because controllers suppress repeated execution for the same identity \\cite{neqsim2026update}.","29: explicit tested dynamic scope and controller units")
t=section(t,"![Dynamic response of separator level", "---\n\n## 29.6",r"""![Checked NeqSim liquid inventory, pressure and withdrawal with timestep comparison](figures/ch29_verified_level_inventory.png)

The initial inventory is 696.53 kg. The feed pulse adds liquid and gas; direct-acting PI control increases liquid withdrawal and returns the liquid level to within 0.2 percentage points of its initial value by 120 s. Gas withdrawal remains fixed, so the pressure rises to about 30.64 bara rather than returning to 30 bara. This distinction makes the modeled control boundary visible.

The code integrates the actual boundary mass and enthalpy rates independently of the vessel inventory update. Required relative residuals are below $10^{-10}$ for mass and $10^{-5}$ for energy, normalized by initial mass and absolute initial internal energy. Halving the timestep must change the aligned liquid-level fraction by less than 0.001 and pressure by less than 0.01 bar. These are numerical acceptance criteria for this case; they are not plant validation or proof of trip protection.

<!-- @neqsim:claim
  test: devtools/scientific_optimization_probe.py
  baseline: verification/scientific_revision/ch29_dynamic_probe.json
-->
""","29: replace unsupported dynamic narration with balance/timestep evidence")
t=replace(t,"- $\\theta/\\tau > 0.5$: PID is essential; consider also Smith predictor or IMC structures", "- For delay-dominated processes, consider slower robust PI tuning or a validated predictor; derivative action cannot remove a pure transport delay.","29: derivative is not mandatory for delay dominance")
t=replace(t,"Temperature loops are typically tuned with full PID action to compensate for the large dead time and second-order dynamics.","Derivative action can help compensate a resolved secondary lag, but amplifies measurement noise and does not cancel pure dead time. Choose PI or filtered PID from an identified model and verify disturbance rejection.","29: qualify temperature-loop derivative benefit")
t=section(t,"The time constant for pressure response is:","### 29.6.3",r"""For fixed gas volume, temperature, composition and compressibility, define the gas capacitance $C_P=\partial M_g/\partial P=V_gM_w/(ZRT)$ in kg/Pa. If the local outlet relation is $\delta\dot m_{out}=K_P\delta P+K_u\delta u$, then

$$
\tau_P=\frac{C_P}{K_P},\qquad K_P=\left(\frac{\partial\dot m_{out}}{\partial P}\right)_u.
$$

Here $K_P$ has units kg/(s Pa), giving $\tau_P$ in seconds. A raw valve $C_v$ cannot replace this derivative without its dimensional flow equation. Variable temperature, real-gas compressibility, liquid level and phase transfer require the coupled inventory/energy equations.
""","29: replace dimensionally invalid pressure time constant")
# Repair the steady compression/recycle topology without claiming surge protection.
t=replace(t,"asv = ThrottlingValve(\"anti-surge valve\", aftercooler.getOutletStream())", "Splitter = jneqsim.process.equipment.splitter.Splitter\nsplitter = Splitter(\"product/recycle split\", aftercooler.getOutletStream())\nsplitter.setSplitFactors([0.75, 0.25])\nasv = ThrottlingValve(\"anti-surge valve\", splitter.getSplitStream(1))", "29: provide product outlet in recycle topology")
t=replace(t,"process.add(aftercooler)\nprocess.add(asv)","process.add(aftercooler)\nprocess.add(splitter)\nprocess.add(asv)","29: propagate product/recycle splitter")
t=t.replace("getPolytropicFluidHead():.0f} J/kg", "getPolytropicFluidHead():.1f} kJ/kg")
t=replace(t,"print(f\"Compressor power: {compressor.getPower('MW'):.2f} MW\")", "product_rate = float(splitter.getSplitStream(0).getFlowRate(\"kg/hr\"))\nassert abs(product_rate-100000.0)/100000.0 < 1e-4\nassert float(compressor.getPower(\"kW\")) > 0.0\nprint(f\"Product mass closure: {product_rate:.2f} kg/hr\")\nprint(f\"Compressor power: {compressor.getPower('MW'):.2f} MW\")", "29: check recycle product closure")
t=replace(t,"### 29.8.3 NeqSim Anti-Surge Control Example", "### 29.8.3 NeqSim Recycle Topology and Mass Closure\n\nThis steady-state example recycles 25% of cooled discharge and exports 75%. It checks recycle mass closure. It contains no installed surge map, recycle-valve actuator response or transient compressor model, and therefore does not demonstrate anti-surge protection.","29: separate recycled-flow topology from surge-control validation")
t=replace(t,"3. **Achieve target pressure within the required time**: API 521 and NORSOK S-001 require depressurization to 50% of design pressure or 6.9 barg (whichever is lower) within 15 minutes", "3. **Achieve the scenario-specific pressure target**: establish the pressure–time requirement from the governing design basis, current applicable standard, fire/rupture analysis and equipment limits. API 521 gives guidance for depressuring-system design; 50% pressure, 6.9 barg and 15 min are not interchangeable universal requirements. This chapter has not verified a NORSOK clause for such a blanket rule \\cite{api521scope}.","29: remove unverified universal depressuring requirement")
t=section(t,"During blowdown, the pressure drops rapidly", "### 29.9.3",r"""For a rigid, well-mixed vessel, with no inlet, no shaft work and negligible kinetic/potential energy, the appropriate open-system equations are

$$
\frac{dM}{dt}=-\dot m_{out},\qquad
\frac{d(Mu)}{dt}=-\dot m_{out}h_{out}+\dot Q_{wall}.
$$

For an ideal gas with constant heat capacities, $u=c_vT$, $h=c_pT$, and $P=MR_sT/V$:

$$
\frac{dT}{dt}=-(\gamma-1)\frac{\dot m_{out}}{M}T
+\frac{\dot Q_{wall}}{Mc_v},\qquad
\frac{1}{P}\frac{dP}{dt}=\frac{1}{M}\frac{dM}{dt}+\frac{1}{T}\frac{dT}{dt}.
$$

Here $\gamma=c_p/c_v$ and $R_s=R/M_w$. The vessel cools because the escaping stream removes enthalpy while the remaining inventory stores internal energy. This occurs even for an ideal gas whose Joule–Thomson coefficient is zero. The valve's approximately isenthalpic expansion is a separate process. Omitting the temperature term from the pressure derivative while simultaneously modeling cooling is inconsistent.

Real-gas blowdown requires the EOS, changing phase composition, outlet flow law and heat transfer. Fluid temperature alone is not metal temperature: a thermal wall model and stress/fracture assessment are needed for a material-temperature decision. API 521 provides the relevant design framework \cite{api521scope}.
""","29: derive consistent open-system blowdown balances and thermal meaning")
blowdown_code=functions["blowdown_case"]+"""

bd_coarse = blowdown_case(0.5)
bd_fine = blowdown_case(0.25)
bc = np.asarray(bd_coarse["series"])
bf = np.asarray(bd_fine["series"])
for case in [bd_coarse, bd_fine]:
    assert case["max_mass_relative_residual"] < 1e-10
    assert case["max_energy_relative_residual"] < 1e-3
assert np.max(np.abs(bc[:, 1]-bf[1::2, 1])) < 0.05
assert np.max(np.abs(bc[:, 2]-bf[1::2, 2])) < 0.1
assert np.all(np.diff(bf[:, 1]) < 0.0)
assert bf[-1, 1] < 80.0 and bf[-1, 2] < 40.0
assert 120.0e-6/bd_fine["mass0_kg"] < 1e-6
print("Final blowdown time s, pressure bara, fluid C, inventory kg, outlet kg/s:")
print(bf[-1].tolist())
with open("ch29_blowdown_checks.json", "w") as handle:
    json.dump({"coarse": bd_coarse, "fine": bd_fine}, handle, indent=2)
fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
for ax, column, label in zip(axes, [1, 2], ["Pressure (bara)", "Fluid temperature (C)"]):
    ax.plot(bf[:, 0], bf[:, column], label="dt = 0.25 s")
    ax.plot(bc[:, 0], bc[:, column], "--", label="dt = 0.5 s")
    ax.set_ylabel(label)
    ax.grid(True, alpha=0.3)
axes[0].legend()
axes[-1].set_xlabel("Time (s)")
fig.tight_layout()
fig.savefig("figures/ch29_verified_blowdown.png", dpi=180)
"""
t=fence(t,"# --- Rich gas fluid for blowdown ---",blowdown_code)
t=replace(t,"### 29.9.3 NeqSim Depressurization Simulation", "### 29.9.3 Checked NeqSim Depressurization Simulation\n\nThe 1 m diameter, 3 m long SRK vessel starts at 80 bara and 40 °C with 95/5 mol% methane/ethane. A valve with declared $C_v=1$ discharges to 1.01325 bara for 120 s. Heat input is zero and wall dynamics are omitted. A $10^{-6}$ kg/s inlet regularizes this implementation's zero-flow stream properties; its total contribution is below one part per million of initial inventory and is included in both balances. This is a numerically checked approximation to isolation, not a validated emergency-depressuring design. The flow law is evaluated before each explicit inventory step.","29: declared blowdown boundaries and finite-inlet regularization")
t=section(t,"![Pressure and temperature profiles during vessel blowdown]", "---\n\n## 29.10",r"""![Checked real-gas vessel depressurization with timestep comparison](figures/ch29_verified_blowdown.png)

The fine-grid calculation reduces pressure to about 52.98 bara and fluid temperature to 9.12 °C after 120 s. The independent inventory checks require relative mass closure below $10^{-10}$ and energy closure below $10^{-3}$. Halving the step from 0.5 to 0.25 s must change pressure by less than 0.05 bar and temperature by less than 0.1 °C at aligned times. These checks qualify the numerical trajectory over the stated 120 s interval; they do not establish a 15-minute target, wall temperature, MDMT compliance or flare-system adequacy.

<!-- @neqsim:claim
  test: devtools/scientific_optimization_probe.py
  baseline: verification/scientific_revision/ch29_blowdown_probe.json
-->
""","29: evidence-based depressurization interpretation")
t=section(t,"The characteristic slug frequency for terrain-induced slugging is:","### 29.10.2", "Severe-slug periods depend on upstream gas compressibility, liquid accumulation, geometry, backpressure and operating rates. A dimensional ratio such as gas velocity divided by riser height is not a qualified frequency correlation. Use a validated transient flow model or measured arrival history for separator sizing.","29: remove unsupported severe-slug frequency correlation")
t=replace(t,r"V_{\text{surge}} = V_{\text{slug}} - \dot{V}_{L,\text{out}} \cdot t_{\text{slug}}",r"V_{\text{surge,required}}=\max_t\left[0,\int_0^t\left(\dot V_{L,in}(s)-\dot V_{L,out}(s)\right)ds\right]", "29: integrate net liquid surge rather than subtract incompatible volumes")
t=replace(t,"where $V_{\\text{slug}}$ is the slug volume, $\\dot{V}_{L,\\text{out}}$ is the liquid processing rate, and $t_{\\text{slug}}$ is the slug duration.","Use actual liquid volumes at consistent separator conditions. Include the base inflow as well as the excess slug volume, the available level band, phase transfer and the time-dependent downstream withdrawal. The constant-density integral is a sizing approximation.","29: clarify surge-volume basis")
slug_code="""# A prescribed total-feed pulse tests vessel response, not slug generation.
slug = dynamic_case(0.25, slug=True)
slug_rows = np.asarray(slug["series"])
assert slug["max_mass_relative_residual"] < 1e-10
assert slug["max_energy_relative_residual"] < 1e-5
assert np.max(slug_rows[:, 1]) < 0.60
plt.figure(figsize=(8, 4))
plt.plot(slug_rows[:, 0], slug_rows[:, 1], label="3 kg/s pulse from 20 to 40 s")
plt.axhline(0.5, color="black", linestyle="--", label="Level setpoint")
plt.axhline(0.60, color="red", linestyle=":", label="Declared test limit")
plt.xlabel("Time (s)")
plt.ylabel("Liquid level / diameter")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("figures/ch29_verified_feed_pulse.png", dpi=180)
print("Peak level fraction:", float(np.max(slug_rows[:, 1])))
"""
t=fence(t,"# --- Build separator model ---",slug_code)
t=replace(t,"The following code demonstrates how to model a separator's response to a slug event:","The following bounded stress test reuses the checked vessel and increases its total-feed pulse to 3 kg/s. Both gas and liquid components increase; a measured liquid-only slug would require a separate composition/flow trajectory. The declared limit is a 0.60 liquid-level fraction.","29: explicit prescribed-pulse meaning")
t=t.replace("![Separator level response during slug arrival with averaging level control](figures/ch20_slug_response.png)","![Checked vessel response to the prescribed feed pulse](figures/ch29_verified_feed_pulse.png)")
t=replace(t,"| Level transmitter | `LevelTransmitter` | Liquid level (m, %) | LT-xxx |", "| Level transmitter | `LevelTransmitter` | Level fraction (empty unit string); multiply by vessel height for m | LT-xxx |", "29: correct supported transmitter unit")
t=replace(t,"| Differential pressure | `PressureTransmitter` | ΔP across equipment | PDT-xxx |", "| Differential pressure | Difference of two pressure measurements | Explicit upstream-minus-downstream pressure | PDT-xxx |", "29: pressure transmitter is not differential-pressure computation")
t=replace(t,"6. **Run dynamic simulation** with `process.runTransient(dt)` in a loop.","6. **Activate inventory dynamics** explicitly with `setCalculateSteadyState(False)` for the vessel and appropriate dynamic equipment, initialize inventory, and verify that mass actually accumulates. A call to `runTransient(dt)` can delegate to a steady-state run when this flag is unchanged. Then run the transient steps.","29: mandatory transient-mode activation")
t=replace(t,"time to first peak (±20% acceptable), peak overshoot (±30% acceptable for initial validation), and settling time (±50% acceptable given model simplifications)","time to first peak, peak overshoot and settling time, with tolerances justified by measurement uncertainty and the consequence of the modeled decision", "29: remove unjustified universal dynamics acceptance tolerances")
save(path,original,t)

# Chapter 32: correct optimization mathematics and demonstrate accepted optimum.
path,original=load(32)
t=original
t=replace(t,"The KKT conditions are necessary for local optimality. Under regularity conditions (constraint qualification), they are also sufficient.","Under a constraint qualification, KKT conditions are necessary for a differentiable local optimum. They are sufficient for global optimality for a convex minimization problem with convex inequality functions written as $g\\leq0$ and affine equalities; nonconvex problems need additional second-order sufficiency conditions. Constraint qualification alone is not sufficient. Bound multipliers must also be included when bounds are active \\cite{boyd2004convex}.","32: correct KKT necessity and sufficiency")
t=replace(t,"ensures global convergence. The penalty parameter", "supports globalization under additional regularity and algorithmic assumptions; it does not prove convergence to a global minimum. The penalty parameter", "32: distinguish globalized algorithm from global optimum")
t=replace(t,"KKT convergence guarantees", "reported KKT residuals that require interpretation", "32: remove unconditional SQP convergence guarantee")
t=replace(t,"| `getKneePoint()` | The point with maximum curvature (balanced trade-off) |", "| `getKneePoint()` | A normalized geometric compromise among sampled points; not an economic decision |", "32: distinguish sampled knee heuristic from curvature optimizer")
t=replace(t,"The knee point identifies the operating condition that balances both objectives.","At fixed inlet state and constant efficiency, power is approximately proportional to mass flow, so this example has an almost straight trade-off and no physically privileged knee. A sampled geometric heuristic does not supply economic preferences.","32: linear Pareto case has no unique economic knee")
t=replace(t,"The knee point is significant because small improvements in either objective beyond this point require disproportionately large sacrifices in the other objective.","Curvature depends on objective scaling and on parameterization. A knee can be useful when a curved front has a clearly stated normalization, but is not automatically the best compromise.","32: qualify knee interpretation")
t=replace(t,"By systematically varying the $\\epsilon_k$ bounds, the entire Pareto front — including non-convex regions — is traced out.","A suitable epsilon grid can recover nonconvex portions that weighted sums miss, provided the subproblems are solved adequately. A finite grid returns sampled non-dominated states, not a guarantee of the complete continuous front.","32: qualify epsilon-front completeness")
t=replace(t,"The weighted-sum method has the advantage of simplicity and can use any single-objective optimizer.","The weighted-sum method has the advantage of simplicity and can use a suitable single-objective optimizer; strictly positive weights avoid zero-weight ties that can include weakly efficient points.","32: require positive Pareto weights")
t=replace(t,"| Oil production rate | Maximize | `feed.getFlowRate(\"bbl/day\")` |", "| Oil production rate | Maximize | Stabilized oil product volume at declared stock-tank conditions |", "32: oil objective must be stock-tank product, not multiphase feed")
t=replace(t,"| Gas dew point | Minimize | `gasExport.getDewPointTemperature(\"C\")` |", "| Gas dew point | Minimize | Explicit dew-point flash on the gas composition at stated pressure |", "32: dewpoint objective is not nonexistent stream getter")
optimum_code=functions["optimize_case"]+"""

accepted = optimize_case()
assert accepted["success"]
assert accepted["replayed_power_kW"] <= 3500.001
assert 0.5 <= accepted["x"][0] <= 2.0
assert 0.8 <= accepted["x"][1] <= 1.6+1e-8
grid_rate = accepted["grid_best"][0]*100000.0
optimum_rate = accepted["x"][0]*100000.0
assert -1e-3 <= optimum_rate-grid_rate <= 1500.001
print("Accepted optimum and independent replay:", accepted)
with open("ch32_accepted_optimum.json", "w") as handle:
    json.dump(accepted, handle, indent=2)
"""
addition=r"""### 32.4.2a Accepted compressor optimum with an independent comparison

This self-contained SRK case maximizes feed mass rate with suction pressure between 40 and 80 bara, feed temperature 40 °C, discharge pressure 150 bara, constant polytropic efficiency 0.78 and a 3500 kW absorbed-power limit. Suction pressure is assumed available without an upstream production or energy penalty. Therefore it is a compressor screening problem, not a well-network economic optimum. Installed map, driver losses and export-quality limits are outside this declared two-variable problem.

SLSQP must report convergence; the selected state is then rebuilt in a fresh NeqSim process. The replay checks mass closure to $10^{-10}$ relative and compressor enthalpy-rise closure to $10^{-5}$ relative. A separate full-model grid contains 101 rates and 21 suction pressures; the optimizer must achieve at least the best feasible grid throughput and differ by at most one 1500 kg/hr grid interval.

```python
import json
Stream = jneqsim.process.equipment.stream.Stream
Compressor = jneqsim.process.equipment.compressor.Compressor
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
"""+optimum_code+r"""
```

The accepted result is 105201.48 kg/hr at 80 bara suction and 3500.00 kW, reached in four iterations. The grid's best feasible throughput is 104000 kg/hr. This agreement is numerical evidence for this small model; it is not a proof of global optimality for arbitrary nonlinear process networks. The earlier rejected native SQP candidate remains a lesson in checking solver status separately from physical feasibility.

<!-- @neqsim:claim
  test: devtools/scientific_optimization_probe.py
  baseline: verification/scientific_revision/ch32_optimum_probe.json
-->

"""
t=replace(t,"### 32.4.3 NLopt Integration",addition+"### 32.4.3 NLopt Integration","32: converged SLSQP plus fresh physical replay and 2121-point grid")
t=replace(t,"the `ProcessSimulationEvaluator` can estimate gradients via central finite differences:", "central finite differences provide the following general approximation:", "32: separate central-difference theory from forward API implementation")
t=replace(t,"The step size is critical: too small and numerical noise dominates; too large and the linear approximation is poor.","The shown `estimateGradient` API uses forward differences in this source revision. The step size is critical: too small and numerical solver noise dominates; too large and the linear approximation is poor. Test derivative stability across several steps and respect variable bounds before relying on gradients.","32: current finite difference API and noise sensitivity")
t=replace(t,r"p_w^{\text{res}} - J_w q_w = p_w^{\text{wh}}",r"p_w^{\text{res}} - q_w/J_w = p_w^{\text{bh}}", "32: fix productivity-index units and bottomhole reference")
t=replace(t,r"p_w^{\text{wh}} - \Delta p_{w,m}(q_w) = p_m",r"p_w^{\text{bh}} - \Delta p_{w,m}(q_w) = p_m", "32: include tubing loss from bottomhole to manifold")
t=replace(t,"$J_w$ is the productivity index, and $\\Delta p$ denotes pressure drops through the network.","$J_w$ has units of rate per pressure difference. The linear IPR is an illustrative single-phase approximation. The bottomhole-to-manifold pressure change includes tubing hydrostatics, friction, acceleration and the surface flowline; do not apply reservoir drawdown directly to wellhead pressure.","32: state IPR model scope")
t=replace(t,"(Beggs and Brill, Hazen-Williams, or Darcy-Weisbach correlations)","(for example, Darcy–Weisbach for a qualified single-phase pipe or Beggs–Brill for its empirical multiphase scope)","32: remove water-only Hazen-Williams from hydrocarbon network methods")
t=replace(t,"This means sparse solvers (LU decomposition with fill-in reduction, iterative methods like GMRES) achieve $O(N)$ scaling vs $O(N^3)$ for dense solvers.","Sparse storage can be $O(N)$ for bounded-degree network equations, but solve time depends on topology, fill-in, ordering and conditioning. Neither sparse LU nor GMRES has a general $O(N)$ cost guarantee for this network model.","32: correct sparse solver complexity claim")
t=replace(t,"The key insight is that at the optimum, the **marginal oil gain per unit gas lift** should be equal across all wells.","For differentiable concave gas-lift curves and an active shared-gas constraint, wells strictly inside their individual bounds have equal marginal oil gain per unit lift gas. Wells at zero flow or another bound satisfy the corresponding KKT inequality instead.","32: equal-slope condition needs interior wells and concavity")
t=replace(t,r"\dot{m}_{\text{out},i} = \dot{m}_{\text{in},i} \cdot \frac{\hat{y}_i}{\sum_j \hat{y}_j}",r"\dot{m}_{\text{out},i} = \dot{m}_{\text{in},i}","32: correct nonreacting compressor component conservation")
t=replace(t,"where $\\hat{y}_i$ is the surrogate's predicted outlet composition for component $i$, normalized to ensure closure.","A nonreacting single-inlet/single-outlet compressor preserves each component mass rate. Renormalizing predicted composition alone does not conserve inlet components. A multi-outlet separator instead requires the sum of each component's outlet rates to equal its inlet rate.","32: distinguish composition normalization from component conservation")
t=replace(t,"Training a PINN on these equations produces a surrogate that respects conservation laws by construction, even when extrapolating beyond the training data.","A finite residual penalty encourages conservation at sampled points; it does not enforce exact balances or guarantee extrapolation. Test integral and component balances on independent cases and near phase boundaries. Hard conservative architectures or explicit projections require their own analysis \\cite{raissi2019pinn}.","32: remove false PINN conservation/extrapolation guarantee")
t=replace(t,"improving generalization, reducing data requirements, and ensuring that predictions respect fundamental physical laws.","which may improve generalization or data efficiency when the physics, loss scaling and training are appropriate; predictions still require independent residual checks.","32: qualify physics-informed learning claims")
t=replace(t,"enabling exact evaluation of spatial and temporal derivatives.","evaluating derivatives of the differentiable network to floating-point precision. This does not automatically differentiate an external Java flash solver or eliminate discretization, optimization and model error.","32: clarify automatic differentiation scope")
t=replace(t,r"+ w_{\text{balance}} \cdot \sigma(\mathbf{u}_t)^{-1}",r"- w_{\text{balance}} \cdot \sigma(\mathbf{u}_t)^2", "32: remove singular reciprocal-variance RL reward")
t=replace(t,"This creates a smooth gradient that guides the agent away from infeasible regions.","The hinge penalty is continuous but nondifferentiable at the limit, and a finite reward penalty does not guarantee feasibility. Keep hard feasibility rejection outside the reward and scale all reward terms consistently. Penalizing loading variance is optional: equal utilization is not generally the economic optimum.","32: nonsmooth penalties cannot guarantee feasible policies")
t=replace(t,"or increase separator pressure to flash more gas", "or test a different separation pressure and recompute gas/liquid loads; increasing pressure at fixed temperature generally suppresses vaporization", "32: correct pressure effect on flashing")
t=replace(t,"The constraint-penalty reward of Section 32.13.3 keeps the agent feasible, but", "The constraint-penalty reward of Section 32.13.3 guides search but does not keep the agent feasible;", "32: separate reward shaping from feasibility")
t=t.replace("package `neqsim.process.fielddevelopment.integrated`", "package `neqsim.process.optimization.valuechain`")
t=replace(t,"For process simulation surrogates, an ensemble of 5–10 models provides well-calibrated uncertainty estimates with manageable computational overhead.","An ensemble size such as 5–10 is an experimental design choice, not evidence of calibrated uncertainty. Verify empirical coverage and interval width on independent states; correlated model errors can leave ensemble spread small despite large shared bias.","32: ensemble size does not establish calibration")
t=replace(t,"For production optimization surrogates, conformal prediction converts any point-prediction model into one that provides calibrated confidence intervals — a critical requirement for operator trust.","Split conformal prediction provides marginal prediction coverage under exchangeability, not conditional coverage at every operating state, a parameter confidence interval, or a guarantee after an optimizer adaptively selects an extreme point. Use held-out calibration data independent of training; if the corrected quantile index exceeds the calibration count, take an infinite interval rather than an invalid quantile. Distribution shift and time dependence require separate treatment \\cite{angelopoulos2023conformal}.","32: conformal marginal coverage and adaptive selection limits")
t=replace(t,"Safety-critical constraints (pressure relief, flammability limits) warrant robust or high-probability chance-constrained treatment.","Declared hard safety and design limits remain hard acceptance conditions. A probability estimate from a surrogate does not authorize their relaxation. Robust/chance-constrained studies can quantify uncertainty only under a separately justified model, uncertainty set and risk criterion.","32: probabilistic confidence is not safety-limit authorization")
# Replace unmeasured timing claims with a measured, reproducible performance protocol.
t=section(t,"### 32.12.6 Computational Feasibility", "### 32.12.7", """### 32.12.6 Computational Feasibility

Measure complete environment-step time on the intended hardware, including state reset, simulation, observation/reward extraction and policy updates. A small steady compressor case is not a timing benchmark for a dynamic facility. PPO/SAC sample requirements and achieved reward depend on the task and seed; no fixed step count guarantees convergence. Section 32.16 gives a reproducible timing protocol.
""","32: remove unsupported RL throughput and convergence timings")
t=section(t,"### 32.15.5 Workflow Example", "### 32.15.6", """### 32.15.5 Workflow Example

For a requested separator-pressure comparison, record the current case, construct two isolated candidates, solve both, and report product rates, power, balances and every declared constraint with units. Compute gas specific energy as $24W/Q$ when power $W$ is kW and gas rate $Q$ is kSm³/day. Monetary comparison additionally needs declared product prices, energy/carbon costs and saleable-product definitions. A numerical preference is withheld when those inputs or any required constraint evidence are missing. The accepted compressor example in Section 32.4.2a demonstrates replay and feasibility; it does not supply a separator-pressure recommendation for a plant.
""","32: remove fabricated agent scenario results, timing and economic threshold")
t=replace(t,"The LLM agent applies the same rigorous methodology every time — proper flash initialization, mixing rule selection, property initialization — eliminating the variability of manual setups.","Structured schemas and executable checks can reduce setup variability, but LLM-generated configurations still need review and validation; the interface does not guarantee correct physics or units.","32: remove deterministic LLM rigor claim")
t=section(t,"## 32.16 Computational Requirements for AI Training on Process Simulators", "## Exercises", r"""## 32.16 Measuring computational requirements

Report timings for the actual model and workload. Component count alone does not determine flash cost: stability searches, phase appearance, EOS choice, derivatives and convergence difficulty also matter. Pairwise mixing-rule work can grow quadratically with component count, but this is not a universal law for end-to-end process execution.

For a reproducible study, record the source commit, processor, runtime, model, convergence tolerances, input envelope, warm-up policy, repetition count, failures and whether setup or cloning is included. Report median and upper quantiles rather than extrapolating a single warm evaluation. Measure complete training-loop time separately from NeqSim evaluation time; neither policy learning nor parallel execution is free.

Independent cases can be parallelized only with isolated mutable state and verified serial/parallel agreement. Throughput is bounded by CPU, memory, JVM behavior and workload imbalance. Eight workers do not imply an eightfold speedup. The following local fixture compares isolated results without claiming live historian access, trained surrogate validity or a production compressor map:

```python
from concurrent.futures import ThreadPoolExecutor

def local_compression_contract(sample):
    rate, pressure = sample
    gas = jneqsim.thermo.system.SystemSrkEos(313.15, 50.0)
    gas.addComponent("methane", 0.9)
    gas.addComponent("ethane", 0.1)
    gas.setMixingRule("classic")
    local_feed = jneqsim.process.equipment.stream.Stream("Local feed", gas)
    local_feed.setFlowRate(float(rate), "kg/hr")
    local_comp = jneqsim.process.equipment.compressor.Compressor("Local compressor", local_feed)
    local_comp.setOutletPressure(float(pressure), "bara")
    local_comp.setPolytropicEfficiency(0.78)
    local_comp.setUsePolytropicCalc(True)
    local_feed.run()
    local_comp.run()
    power = float(local_comp.getPower("kW"))
    assert np.isfinite(power) and power > 0.0
    assert abs(local_comp.getOutletStream().getFlowRate("kg/hr")-rate) < 1e-6
    return power

samples = [(50000.0, 120.0), (75000.0, 150.0), (100000.0, 180.0)]
serial = [local_compression_contract(sample) for sample in samples]
with ThreadPoolExecutor(max_workers=2) as pool:
    parallel = list(pool.map(local_compression_contract, samples))
assert np.allclose(serial, parallel, rtol=1e-10, atol=1e-6)
print("Serial/parallel isolated-case powers kW:", serial, parallel)
```

Active learning can target regions of high interpolation error or small constraint margin, but sample savings must be measured against a held-out benchmark. Choose dataset size by error and coverage requirements, including phase boundaries and failed states; a prescribed count such as $10^4$ is not an accuracy guarantee. The cost comparison is measured training plus repeated surrogate inference/replay versus repeated full simulation over the intended number of uses.

---

""","32: replace invented performance tables with local parallel contract and benchmarking protocol")
save(path,original,t)
(REPORT/"core_corrections.json").write_text(json.dumps(CHANGES,indent=2),encoding="utf-8")
print("Applied",len(CHANGES),"scientific corrections")
