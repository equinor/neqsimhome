"""Replace misleading legacy demonstrations with executed current NeqSim APIs."""
import json
import re
from pathlib import Path
BOOK = Path(__file__).resolve().parents[1]

def edit(prefix, cells=None, replacements=None):
    path = next(BOOK.glob("chapters/{}*/notebooks/*.ipynb".format(prefix)))
    data = json.loads(path.read_text(encoding="utf-8"))
    for i,cell in enumerate(data["cells"]):
        source = "".join(cell["source"])
        for old,new in (replacements or {}).items(): source = source.replace(old,new)
        if cells and i in cells: source = cells[i]
        cell["source"] = source.splitlines(keepends=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

edit("ch05", replacements={
    "pwh_scan = np.asarray([wellhead_at_rate(q, P_res - q / PI) for q in q_scan])": '''pwh_scan = []
for q in q_scan:
    try:
        pwh_scan.append(wellhead_at_rate(q, P_res - q / PI))
    except Exception as error:
        print(f"Rate {q:.1f} t/hr is infeasible at its IPR pressure: {error}")
        pwh_scan.append(np.nan)
pwh_scan = np.asarray(pwh_scan)''',
})
edit("ch06", replacements={
    "    process.run()\n\n    p_choke_out": '''    try:
        process.run()
    except Exception as error:
        print(f"Opening {opening:.0f}% cannot pass the imposed 50 t/hr through the choke and flowline: {error}")
        choke_outlet_pressures.append(np.nan)
        manifold_pressures.append(np.nan)
        flow_rates_kg_hr.append(np.nan)
        continue

    p_choke_out''',
})
edit("ch31", replacements={
    'adjuster.setAdjustedVariable(valve, "pressure", "bara")': '''adjuster.setAdjustedVariable(valve, "pressure", "bara")
# A valve's pressure setpoint belongs to the equipment, not its outlet stream.
pressure_getter = jpype.JProxy("java.util.function.Function", dict={"apply": lambda equipment: float(equipment.getOutletPressure())})
pressure_setter = jpype.JProxy("java.util.function.BiConsumer", dict={"accept": lambda equipment, value: equipment.setOutletPressure(float(value))})
adjuster.setAdjustedValueGetter(pressure_getter)
adjuster.setAdjustedValueSetter(pressure_setter)''',
})

edit("ch26", replacements={
    "chokes = []": "chokes = []\nwells = []\nWellFlow = jneqsim.process.equipment.reservoir.WellFlow",
    '    choke = jneqsim.process.equipment.valve.ThrottlingValve(wd["name"] + " Choke", stream)': '''    stream.run()
    well = WellFlow(wd["name"] + " Inflow")
    well.setInletStream(stream)
    # Calibrate a pressure-squared inflow coefficient to the declared design rate.
    # Units: (MSm3/day)/bar2; this is an inflow-only illustration, without tubing.
    well.setWellProductionIndex(float(stream.getFlowRate("MSm3/day")) / (wd["pres"]**2 - (manifold_pressure + 10.0)**2))
    well.setOutletPressure(manifold_pressure + 10.0, "bara")
    well.solveFlowFromOutletPressure(True)
    wells.append(well)
    choke = jneqsim.process.equipment.valve.ThrottlingValve(wd["name"] + " Choke", well.getOutletStream())''',
    "    process.add(stream)\n    process.add(choke)": "    process.add(stream)\n    process.add(well)\n    process.add(choke)",
    '            choke.setOutletPressure(float(p_man))': '            wells[i].setOutletPressure(float(p_man + 10.0), "bara")\n            choke.setOutletPressure(float(p_man))',
    'rate = streams[i].getFlowRate("kg/hr")': 'rate = wells[i].getOutletStream().getFlowRate("kg/hr")',
    'for choke in chokes:\n    choke.setOutletPressure(manifold_pressure)': 'for well, choke in zip(wells, chokes):\n    well.setOutletPressure(manifold_pressure + 10.0, "bara")\n    choke.setOutletPressure(manifold_pressure)',
    '        p_out = manifold_pressure - dp_extra': '        p_out = manifold_pressure',
    '        choke.setOutletPressure(float(p_out))\n        process.run()': '        wells[idx].setOutletPressure(float(min(manifold_pressure + 10.0 + dp_extra, wd["pres"] - 0.1)), "bara")\n        choke.setOutletPressure(float(p_out))\n        process.run()',
    'rates_this_well.append(stream.getFlowRate("kg/hr"))': 'rates_this_well.append(wells[idx].getOutletStream().getFlowRate("kg/hr"))',
    '    # Reset choke\n    choke.setOutletPressure': '    # Reset well drawdown and choke\n    wells[idx].setOutletPressure(manifold_pressure + 10.0, "bara")\n    choke.setOutletPressure',
    "Choke Opening Sensitivity per Well": "Well rate sensitivity to an added choke pressure loss",
    "Choke Opening Sensitivity": "Additional choke pressure-loss sensitivity",
    "Individual well rates** are controlled by the pressure drop across the choke": "Individual well rates** follow the pressure-squared inflow relationship and the imposed choke loss",
})

edit("ch28", cells={5: '''# Current production VFP calculation: upward flow with a specified arrival pressure.
whp_bara = 80.0
wht_C = 90.0  # bottomhole inlet temperature; outlet temperature is calculated
flow_rate_kg_hr = 30000.0
bottomhole_stream = Stream("Bottomhole inlet", fluid.clone())
bottomhole_stream.setFlowRate(flow_rate_kg_hr, "kg/hr")
bottomhole_stream.setTemperature(wht_C, "C")
bottomhole_stream.setPressure(250.0, "bara")
wellbore = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills("Production well", bottomhole_stream)
wellbore.setPipeWallRoughness(roughness_m)
wellbore.setLength(well_depth_m)
wellbore.setElevation(well_depth_m)  # upward production, outlet above inlet
wellbore.setDiameter(tubing_id_m)
wellbore.setNumberOfIncrements(12)
wellbore.setCalculationMode(jneqsim.process.equipment.pipeline.PipeBeggsAndBrills.CalculationMode.CALCULATE_INLET_PRESSURE)
wellbore.setSpecifiedOutletPressure(whp_bara, "bara")
wellbore.setFlowConvergenceTolerance(1e-4)
wellbore.setMaxFlowIterations(60)
bottomhole_stream.run()
wellbore.run()
bhp = float(wellbore.getSolvedInletPressure())
bht = float(bottomhole_stream.getTemperature("C"))
assert abs(wellbore.getOutletStream().getPressure("bara") - whp_bara) < 0.05
assert bhp > whp_bara
print(f"Required BHP: {bhp:.3f} bara; achieved WHP: {wellbore.getOutletStream().getPressure('bara'):.3f} bara at {flow_rate_kg_hr/1000:.1f} t/hr")
''', 7: '''# Every VFP entry solves the upward NeqSim pipeline against the WHP boundary.
whp_values = [40.0, 60.0, 80.0, 100.0, 120.0]
flow_values = np.linspace(5000, 60000, 12)
vfp_table = {}
arrival_errors = []
for whp in whp_values:
    bhp_list = []
    for flow in flow_values:
        bottomhole_stream.setFlowRate(float(flow), "kg/hr")
        bottomhole_stream.setPressure(250.0, "bara")
        bottomhole_stream.setTemperature(90.0, "C")
        bottomhole_stream.run()
        wellbore.setSpecifiedOutletPressure(float(whp), "bara")
        wellbore.run()
        bhp_val = float(wellbore.getSolvedInletPressure())
        arrival_error = abs(float(wellbore.getOutletStream().getPressure("bara")) - whp)
        assert np.isfinite(bhp_val) and bhp_val > whp
        assert arrival_error < 0.05
        bhp_list.append(bhp_val)
        arrival_errors.append(arrival_error)
    vfp_table[whp] = bhp_list
import pandas as pd
vfp_results = pd.DataFrame({f"WHP {whp:.0f} bara": values for whp, values in vfp_table.items()}, index=flow_values/1000)
vfp_results.index.name = "Flow (t/hr)"
print(vfp_results.to_string(float_format=lambda value: f"{value:.3f}"))
vfp_results.to_csv(FIGURES_DIR / "ch28_production_vfp_table.csv")
print(f"Maximum pressure-boundary residual: {max(arrival_errors):.5f} bar")
'''}, replacements={
    "We set the wellhead conditions": "We specify the arrival pressure and bottomhole temperature",
    "pipe going downward": "pipe producing upward",
})

edit("ch29", replacements={
    "level_setpoint - level[i-1]": "level[i-1] - level_setpoint",
    "level_setpoint - lev[i-1]": "lev[i-1] - level_setpoint",
    "Kp = 2.0": "Kp = 200.0",
    "kp_values = [0.5, 2.0, 5.0]": "kp_values = [50.0, 200.0, 500.0]",
    "K_process = 0.2        # process gain [m/% valve]": "K_process = 1.0        # normalized outlet-flow gain for a 100% opening change",
    "Simple first-order-plus-delay model for separator level": "Illustrative integrating level balance (Python), initialized separately from the NeqSim steady state",
    "Simulated PID transient response": "Illustrative PID level-balance response (not NeqSim transient validation)",
    "Effect of Proportional Gain (Kp) on Level Control": "Illustrative level control: proportional-gain comparison",
    "Separator Level Control": "Illustrative separator level-control balance",
})

edit("ch32", cells={5: '''# All candidate points are full NeqSim compression simulations.
# Optimize two conflicting objectives: maximize throughput, minimize total power.
candidate_production, candidate_power, candidate_eta = [], [], []
for eta in [0.62, 0.70, 0.78]:
    for flow in flow_rates:
        candidate_feed = Stream("Pareto feed", fluid.clone())
        candidate_feed.setFlowRate(float(flow), "kg/hr")
        candidate_feed.run()
        candidate_comp = Compressor("Pareto compressor", candidate_feed)
        candidate_comp.setOutletPressure(120.0)
        candidate_comp.setUsePolytropicCalc(True)
        candidate_comp.setPolytropicEfficiency(float(eta))
        candidate_comp.run()
        candidate_production.append(float(candidate_comp.getOutletStream().getFlowRate("kg/hr"))/1000.0)
        candidate_power.append(float(candidate_comp.getPower("kW"))/1000.0)
        candidate_eta.append(eta)
production = np.asarray(candidate_production)
power = np.asarray(candidate_power)
is_pareto = np.asarray([not np.any((production >= q-1e-7) & (power <= w+1e-9) & ((production > q+1e-7) | (power < w-1e-9))) for q,w in zip(production,power)])
pareto_prod, pareto_power = production[is_pareto], power[is_pareto]
dom_prod, dom_power = production[~is_pareto], power[~is_pareto]
assert len(pareto_prod) >= 2 and np.all(np.isfinite(power))
print(f"Full NeqSim candidates: {len(production)}; non-dominated: {is_pareto.sum()}; dominated: {(~is_pareto).sum()}")
''', 6: '''fig, ax = plt.subplots(figsize=(8.5, 5.5))
ax.scatter(dom_prod, dom_power, c="#A5ABB1", s=45, alpha=0.7, label="Dominated NeqSim candidates")
sorted_idx = np.argsort(pareto_prod)
ax.plot(pareto_prod[sorted_idx], pareto_power[sorted_idx], "o-", linewidth=2.4, color="#146B8B", label="Non-dominated candidates")
ax.set(xlabel="Production rate (t/hr)", ylabel="Total compressor power (MW)", title="Production and compression-power trade-off")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "ch22_pareto_front.png", dpi=220, bbox_inches="tight")
plt.show()
'''}, replacements={
    "combining NeqSim results with synthetic variation": "using NeqSim evaluations at three assumed polytropic efficiencies",
    "specific power": "total compressor power",
})

# Align notebook headings to the manifest ordering and remove hard-coded figure numbers.
for path in BOOK.glob("chapters/*/notebooks/*.ipynb"):
    data = json.loads(path.read_text(encoding="utf-8"))
    chapter = int(path.parent.parent.name[2:4])
    old_heading = next(("".join(c["source"]) for c in data["cells"] if c["cell_type"] == "markdown"), "")
    match = re.search(r"Chapter (\d+)", old_heading)
    old_chapter = match.group(1) if match else str(chapter)
    for cell in data["cells"]:
        source = "".join(cell["source"])
        if cell["cell_type"] == "markdown":
            source = re.sub(r"Chapter \d+:", f"Chapter {chapter}:", source)
            source = re.sub(r"(?m)^(##+ )" + old_chapter + r"\.", r"\g<1>" + str(chapter) + ".", source)
        elif cell["cell_type"] == "code":
            source = re.sub(r"Figure \d+\.\d+: ", "", source)
        cell["source"] = source.splitlines(keepends=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("Updated production VFP, native well inflow, actual Pareto candidates, and controller model labelling.")
