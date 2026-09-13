from pathlib import Path
import re
B=Path(__file__).resolve().parents[1];p=next((B/'chapters').glob('ch24_*'))/'chapter.md';s=p.read_text(encoding='utf-8')
m=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',s,re.M|re.S))[72]
c='''import itertools
import math
import numpy as np

# Independently test each attempted state, including rejected native flash points.
def facility_balance_residuals():
    residuals = {"mass_relative": 0.0, "component_relative": 0.0,
                 "energy_relative": 0.0, "domain_valid": True}
    for unit in process.getUnitOperations():
        if str(unit.getClass().getSimpleName()) == "Stream":
            continue
        ins, outs = list(unit.getInletStreams()), list(unit.getOutletStreams())
        if not ins or not outs:
            continue
        for stream in ins + outs:
            stream.getFluid().initProperties()
            residuals["domain_valid"] &= (stream.getFlowRate("kg/hr") >= 0 and
                stream.getPressure("bara") > 0 and stream.getTemperature("K") > 0)
        mi = sum(float(st.getFlowRate("kg/hr")) for st in ins)
        mo = sum(float(st.getFlowRate("kg/hr")) for st in outs)
        residuals["mass_relative"] = max(residuals["mass_relative"], abs(mo-mi)/mi)
        names = {str(st.getFluid().getComponent(k).getComponentName())
                 for st in ins+outs for k in range(st.getFluid().getNumberOfComponents())}
        scale = sum(float(st.getFluid().getTotalNumberOfMoles()) for st in ins)
        for name in names:
            ni = sum(float(st.getFluid().getComponent(name).getNumberOfmoles()) for st in ins)
            no = sum(float(st.getFluid().getComponent(name).getNumberOfmoles()) for st in outs)
            residuals["component_relative"] = max(residuals["component_relative"], abs(no-ni)/scale)
        kind = str(unit.getClass().getSimpleName())
        if kind == "Compressor":
            residuals["domain_valid"] &= ins[0].getFluid().getNumberOfPhases() == 1
        # Pipeline thermal boundary is not independently checked by this budget.
        if kind == "PipeBeggsAndBrills":
            continue
        work = float(unit.getPower()) if kind == "Compressor" else float(unit.getDuty()) if kind in ("Heater", "Cooler") else 0.0
        hin = sum(float(st.getFluid().getEnthalpy()) for st in ins)
        hout = sum(float(st.getFluid().getEnthalpy()) for st in outs)
        err = abs(hout-hin-work)/max(abs(hin), abs(hout), abs(work), 1.0)
        residuals["energy_relative"] = max(residuals["energy_relative"], err)
    return residuals

sep_pressures = [50.0, 60.0, 70.0, 80.0]
comp_pressures = [120.0, 140.0, 160.0, 180.0]
results_matrix = []
for rate, sep_p, comp_p in itertools.product(
        [250000.0, 350000.0], sep_pressures, comp_pressures):
    feed.setFlowRate(rate, "kg/hr")
    feed.setPressure(sep_p, "bara")
    comp.setOutletPressure(comp_p)
    run_facility()
    residuals = facility_balance_residuals()
    accepted = (residuals["domain_valid"] and residuals["mass_relative"] < 1e-6 and
                residuals["component_relative"] < 1e-6 and residuals["energy_relative"] < 1e-5)
    deficit = (float(cooler.getOutletStream().getFlowRate("kg/hr")) -
               sum(float(st.getFlowRate("kg/hr")) for st in export_ko.getOutletStreams()))
    results_matrix.append({"rate_kg_hr": rate, "sep_P": sep_p, "comp_P": comp_p,
        "power_MW": float(comp.getPower("MW")), "accepted": bool(accepted),
        "knockout_mass_deficit_kg_hr": deficit, "residuals": residuals})
    print(results_matrix[-1])

assert len(results_matrix) == 32
rejected = [row for row in results_matrix if not row["accepted"]]
assert len(rejected) == 2
assert all(row["sep_P"] == 80.0 and row["comp_P"] == 140.0 for row in rejected)
assert abs(rejected[0]["knockout_mass_deficit_kg_hr"] - 0.407180316) < 1e-4
best_by_rate = {}
for rate in (250000.0, 350000.0):
    accepted_rows = [r for r in results_matrix if r["accepted"] and r["rate_kg_hr"] == rate]
    best_by_rate[rate] = min(accepted_rows, key=lambda row: row["power_MW"])
best = best_by_rate[250000.0]  # compare pressures at a common production rate
feed.setFlowRate(best["rate_kg_hr"], "kg/hr")
feed.setPressure(best["sep_P"], "bara")
comp.setOutletPressure(best["comp_P"])
run_facility()
assert abs(comp.getPower("MW")-best["power_MW"]) < 1e-5
assert facility_balance_residuals()["mass_relative"] < 1e-6
Path("ch24_pressure_grid_acceptance.json").write_text(json.dumps(results_matrix, indent=2))
print("Lowest-power accepted sampled pressure settings at each fixed rate:", best_by_rate)
print("Rejected states remain in the record; no complete-grid or global optimum is claimed.")
'''
p.write_text(s[:m.start(3)]+c+s[m.end(3):],encoding='utf-8')
