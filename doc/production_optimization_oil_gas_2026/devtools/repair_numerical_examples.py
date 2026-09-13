"""Documented corrections from the September 2026 execution audit."""
import json
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]


def edit(chapter, replacements=None, cells=None):
    path = next(BOOK.glob("chapters/{}*/notebooks/*.ipynb".format(chapter)))
    notebook = json.loads(path.read_text(encoding="utf-8"))
    for index, cell in enumerate(notebook["cells"]):
        source = "".join(cell["source"])
        for old, new in (replacements or {}).items():
            source = source.replace(old, new)
        if cells and index in cells:
            source = cells[index]
        cell["source"] = source.splitlines(keepends=True)
    path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


# A Cv rating does not activate the inverse pressure calculation by itself.
edit("ch06", {"choke.setCv(30.0)": "choke.setCv(30.0)\nchoke.setIsCalcOutPressure(True)",
              '    p_manifold = flowline.getOutletStream().getPressure("bara")': '    p_manifold = flowline.getOutletStream().getPressure("bara")\n    assert 0 < p_choke_out <= tubing.getOutletStream().getPressure("bara"), "Passive choke cannot increase pressure"'})

edit("ch04", {"(1 - Sw_norm)**no": "np.clip(1 - Sw_norm, 0.0, 1.0)**no",
              "(1 - Sw_star)**n_o": "np.clip(1 - Sw_star, 0.0, 1.0)**n_o"})

# Trace finite envelope branches, never draw a surrogate when continuation fails.
for chapter, create, filename, title in [
    ("ch01", "create_natural_gas(273.15 + 25.0, 50.0)", "fig03_phase_envelope.png", "Natural gas saturation envelope"),
    ("ch03", "create_gas_condensate(273.15 + 90.0, 200.0)", "fig02_phase_envelope_condensate.png", "Gas-condensate saturation envelope"),
]:
    path = next(BOOK.glob("chapters/{}*/notebooks/*.ipynb".format(chapter)))
    data = json.loads(path.read_text(encoding="utf-8"))
    index = next(i for i,c in enumerate(data["cells"]) if c["cell_type"] == "code" and "calcPTphaseEnvelope" in "".join(c["source"]))
    source = '''fluid_env = CREATE
fluid_env.setMultiPhaseCheck(True)
ops_env = ThermodynamicOperations(fluid_env)
ops_env.calcPTphaseEnvelope(True, 1.0)
branches = []
for t_key, p_key in [("dewT", "dewP"), ("bubT", "bubP")]:
    raw_t, raw_p = np.asarray(ops_env.get(t_key), dtype=float), np.asarray(ops_env.get(p_key), dtype=float)
    valid = np.isfinite(raw_t) & np.isfinite(raw_p) & (raw_t > 0) & (raw_p > 0)
    print(f"{t_key}: {valid.sum()} physical continuation points; {(~valid).sum()} sentinel entries excluded")
    if valid.sum() >= 2:
        branches.append((raw_t[valid] - 273.15, raw_p[valid]))
assert branches, "Envelope solver returned no finite physical branch"
# Continuation getter labels can be swapped: the dew branch contains the cricondentherm.
branches.sort(key=lambda branch: np.max(branch[0]), reverse=True)
fig, ax = plt.subplots(figsize=(8, 5.5))
for i, (temperature, pressure) in enumerate(branches):
    label = ("Dew branch" if i == 0 else "Bubble branch") if len(branches) == 2 else "Traced saturation branch"
    ax.plot(temperature, pressure, linewidth=2.4, label=label)
ax.set(xlabel="Temperature (°C)", ylabel="Pressure (bara)", title="TITLE")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_ylim(bottom=0)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "FILENAME", dpi=220, bbox_inches="tight")
plt.show()
'''.replace("CREATE", create).replace("TITLE", title).replace("FILENAME", filename)
    edit(chapter, cells={index: source})

# Signed elevation and a true pressure-boundary inversion for the VLP.
edit("ch05", {
    "setElevation(-well_depth)  # negative = upward flow": "setElevation(well_depth)  # outlet is above inlet",
    "setElevation(-2500.0)": "setElevation(2500.0)",
    "hc_total = 94.3": "hc_total = 94.3",  # actual composition sum retained
    "Water cut scenarios": "Water mole-fraction scenarios (not standard-liquid water cut)",
    "['0% WC', '10% WC', '30% WC', '50% WC']": "['0 mol% water', '10 mol% water', '30 mol% water', '50 mol% water']",
    "Different Water Cuts": "Different Water Mole Fractions",
    "    except Exception:\n        pass": "    except Exception as error:\n        print(f'Infeasible trial at {rate / 1000:.2f} t/hr: {error}')",
    "            pass  # Skip failed calculations": "            print(f'Infeasible trial at {rate / 1000:.2f} t/hr: {e}')",
}, cells={8: '''# Couple IPR to the actual NeqSim wellhead-pressure response.
# For each rate, the reservoir PI supplies BHP; the tubing must deliver >=50 bara.
from scipy.optimize import brentq
P_res = 250.0  # bara
PI = 0.8  # tonnes/hr/bar
P_wh_target = 50.0  # bara
def wellhead_at_rate(rate_tph, bottomhole_pressure):
    fluid_trial = create_well_fluid()
    feed_trial = Stream("Nodal feed", fluid_trial)
    feed_trial.setFlowRate(float(rate_tph * 1000.0), "kg/hr")
    feed_trial.setPressure(float(bottomhole_pressure), "bara")
    feed_trial.setTemperature(80.0, "C")
    tubing_trial = PipeBeggsAndBrills("Nodal tubing", feed_trial)
    tubing_trial.setPipeWallRoughness(2.5e-5)
    tubing_trial.setLength(2500.0)
    tubing_trial.setElevation(2500.0)
    tubing_trial.setDiameter(0.10)
    tubing_trial.setNumberOfIncrements(20)
    feed_trial.run()
    tubing_trial.run()
    pressure = float(tubing_trial.getOutletStream().getPressure("bara"))
    assert np.isfinite(pressure), "Non-finite wellhead pressure"
    return pressure

q_scan = np.linspace(5.0, 95.0, 19)
pwh_scan = np.asarray([wellhead_at_rate(q, P_res - q / PI) for q in q_scan])
residuals = pwh_scan - P_wh_target
crossings = [(q_scan[i], q_scan[i+1]) for i in range(len(q_scan)-1) if residuals[i] * residuals[i+1] < 0]
assert crossings, "No physically bracketed operating point in the sampled rate interval"
q_op = brentq(lambda q: wellhead_at_rate(q, P_res - q / PI) - P_wh_target, *crossings[-1], xtol=1e-3)
p_op = P_res - q_op / PI
achieved_pwh = wellhead_at_rate(q_op, p_op)
assert abs(achieved_pwh - P_wh_target) < 0.05
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))
ax.plot(q_scan, pwh_scan, "o-", label="NeqSim tubing + reservoir PI")
ax.axhline(P_wh_target, linestyle="--", color="#B54157", label="Wellhead boundary (50 bara)")
ax.plot(q_op, achieved_pwh, "*", markersize=14, color="black")
ax.set(xlabel="Production rate (t/hr)", ylabel="Wellhead pressure (bara)", title="Coupled operating point")
ax.legend()
ax2.plot(q_scan, P_res - q_scan / PI, label="IPR bottomhole pressure")
ax2.plot(q_op, p_op, "*", markersize=14, color="black", label=f"Solved rate {q_op:.2f} t/hr")
ax2.set(xlabel="Production rate (t/hr)", ylabel="Bottomhole pressure (bara)", title="Reservoir deliverability at the solution")
ax2.legend()
for axis in (ax, ax2): axis.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "ch05_fig02_operating_point.png", dpi=220, bbox_inches="tight")
plt.show()
print(f"Operating rate {q_op:.4f} t/hr; BHP {p_op:.4f} bara; wellhead {achieved_pwh:.4f} bara")
'''})

# Replace a nonexistent optimize() API and unbounded revenue surrogate with
# the current source optimizer and an explicit engineering power constraint.
edit("ch23", {
    "# compressor.setMaximumPower(5000.0)  # kW max power constraint  # Method not available in NeqSim": "# The 5000 kW nameplate is enforced below through the optimizer's total-power limit.",
    "# compressor.setMaximumSpeed(12000.0)  # RPM  # Method not available in NeqSim": "compressor.setMaximumSpeed(12000.0)  # RPM; a speed limit is distinct from a power limit.",
    "rates = np.linspace(20000, 120000, 25)": "rates = np.linspace(20000, 180000, 25)",
}, cells={5: '''# Current FlowRateOptimizer API; all candidates run the complete process.
FlowRateOptimizer = jneqsim.process.util.optimizer.FlowRateOptimizer
optimizer = FlowRateOptimizer(process, "Feed Gas", "Export Cooler")
optimizer.setAutoConfigureProcessCompressors(False)  # fixed-pressure design calculation, no synthetic map
optimizer.setCheckCapacityConstraints(False)  # equipment curves are unspecified in this screening case
optimizer.setMinFlowRate(20000.0)
optimizer.setMaxFlowRate(200000.0)
optimizer.setMaxTotalPowerLimit(4750.0)  # kW = 95% of the assumed 5000 kW nameplate
optimizer.setMaxEquipmentUtilizationLimit(1e6)  # only the declared total-power constraint is qualified here
result = optimizer.findMaximumFeasibleFlowRate(65.0, "bara", 1e6)
assert result is not None and result.isFeasible(), "No feasible operating point was found"
opt_rate = float(result.getFlowRate())
opt_value = float(result.getTotalPower())
feed.setFlowRate(opt_rate, "kg/hr")
process.run()
assert compressor.getPower("kW") <= 4750.0 + 1.0
assert abs(cooler.getOutletStream().getPressure("bara") - 150.0) < 1e-6
optimization_result = {"optimal_rate_kg_hr": opt_rate, "power_kW": opt_value,
                       "power_limit_kW": 4750.0, "feasible": bool(result.isFeasible()),
                       "scope": "power-limited fixed-pressure screening; map and vessel constraints not supplied"}
print(f"Maximum feasible sampled-resolution rate: {opt_rate:.1f} kg/hr")
print(f"Compressor power: {opt_value:.2f} kW; screening limit: 4750 kW")
'''})

# Actual tear-stream iterations replace fabricated exponential residual curves.
edit("ch31", cells={9: '''# Actual direct-substitution recycle iteration, with a 35% gas recycle.
# This records each NeqSim equipment evaluation rather than inventing residuals.
recycle_fluid = SystemSrkEos(303.15, 40.0)
for name, fraction in [("methane", 0.65), ("ethane", 0.15), ("propane", 0.10), ("n-butane", 0.10)]:
    recycle_fluid.addComponent(name, fraction)
recycle_fluid.setMixingRule("classic")
feed = Stream("Fresh feed", recycle_fluid)
feed.setFlowRate(50000.0, "kg/hr")
feed.run()
tear = Stream("Recycle tear", recycle_fluid.clone())
tear.setFlowRate(1000.0, "kg/hr")
tear.setTemperature(40.0, "C")
tear.run()
mixer = Mixer("Recycle mixer")
mixer.addStream(feed)
mixer.addStream(tear)
cooler_loop = Cooler("Loop cooler", mixer.getOutletStream())
cooler_loop.setOutTemperature(293.15)
separator = Separator("Loop separator", cooler_loop.getOutletStream())
splitter_loop = Splitter("Gas recycle split", separator.getGasOutStream())
splitter_loop.setSplitFactors([0.35, 0.65])
flow_errors, temp_errors, comp_errors = [], [], []
for iteration in range(60):
    old_flow = float(tear.getFlowRate("kg/hr"))
    old_temperature = float(tear.getTemperature("K"))
    old_composition = np.asarray(tear.getFluid().getMolarComposition(), dtype=float)
    for unit in [mixer, cooler_loop, separator, splitter_loop]: unit.run()
    updated = splitter_loop.getSplitStream(0)
    new_flow = float(updated.getFlowRate("kg/hr"))
    new_temperature = float(updated.getTemperature("K"))
    new_composition = np.asarray(updated.getFluid().getMolarComposition(), dtype=float)
    # Normalize different quantities before comparing them on a common axis.
    flow_errors.append(abs(new_flow - old_flow) / 50000.0)
    temp_errors.append(abs(new_temperature - old_temperature) / 303.15)
    comp_errors.append(float(np.max(np.abs(new_composition - old_composition))))
    tear.setThermoSystem(updated.getThermoSystem().clone())
    if max(flow_errors[-1], temp_errors[-1], comp_errors[-1]) < 1e-7:
        break
assert max(flow_errors[-1], temp_errors[-1], comp_errors[-1]) < 1e-7, "Recycle did not converge"
max_iters = len(flow_errors)
iterations = list(range(1, max_iters + 1))
print(f"Measured recycle convergence: {max_iters} iterations; flow={new_flow:.5f} kg/hr")
print(f"Final normalized residuals: flow={flow_errors[-1]:.3g}, T={temp_errors[-1]:.3g}, composition={comp_errors[-1]:.3g}")
'''}, replacements={
    'ax.set_ylabel("Absolute Error", fontsize=12)': 'ax.set_ylabel("Normalized residual (-)", fontsize=12)',
    "ax.axhline(y=1e-3, color='red', linestyle='--', alpha=0.5, label='Tolerance (1e-3)')": "ax.axhline(y=1e-7, color='red', linestyle='--', alpha=0.5, label='Tolerance (1e-7)')",
    'label=\'Flow Error\'': 'label=\'Flow change / fresh-feed flow\'',
    'label=\'Temperature Error\'': 'label=\'Temperature change / 303.15 K\'',
    'label=\'Composition Error\'': 'label=\'Maximum mole-fraction change\'',
})
print("Applied physics, phase-envelope, optimizer and recycle corrections.")
