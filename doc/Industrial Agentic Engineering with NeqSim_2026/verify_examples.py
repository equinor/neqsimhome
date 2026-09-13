"""Execute the revised book's synthetic cases against an explicit source checkout.

No installed-NeqSim fallback and no LLM calls inside numerical loops.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from book_runtime import BOOK, bootstrap

COMPOSITION = {"methane": 0.85, "ethane": 0.10, "propane": 0.05}


def make_fluid(ns, pressure=60.0, temperature=303.15, model="SRK", composition=None):
    cls = ns.thermo.system.SystemSrkEos if model == "SRK" else ns.thermo.system.SystemPrEos
    fluid = cls(temperature, pressure)
    for name, amount in (composition or COMPOSITION).items():
        fluid.addComponent(name, amount)
    fluid.setMixingRule("classic")
    return fluid


def compression_case(ns, pressure=120.0, efficiency=0.75, flow=10000.0):
    fluid = make_fluid(ns)
    feed = ns.process.equipment.stream.Stream("Feed", fluid)
    feed.setFlowRate(flow, "kg/hr")
    sep = ns.process.equipment.separator.Separator("Inlet separator", feed)
    comp = ns.process.equipment.compressor.Compressor("Compressor", sep.getGasOutStream())
    comp.setOutletPressure(pressure, "bara")
    comp.setUsePolytropicCalc(True)
    comp.setPolytropicEfficiency(efficiency)
    cooler = ns.process.equipment.heatexchanger.Cooler("Aftercooler", comp.getOutletStream())
    cooler.setOutTemperature(308.15)
    process = ns.process.processmodel.ProcessSystem()
    for unit in (feed, sep, comp, cooler):
        process.add(unit)
    process.run()
    inlet = float(feed.getFlowRate("kg/hr"))
    outlet = float(sep.getGasOutStream().getFlowRate("kg/hr") + sep.getLiquidOutStream().getFlowRate("kg/hr"))
    gas_flow = float(sep.getGasOutStream().getFlowRate("kg/hr"))
    # Specific enthalpy times mass flow avoids treating the system's extensive
    # enthalpy getter as a power unit. Retain both material outlets.
    def enthalpy_rate_kW(stream):
        return float(stream.getFluid().getEnthalpy("kJ/kg")) * float(stream.getFlowRate("kg/sec"))
    h_in = enthalpy_rate_kW(feed)
    h_gas_out = enthalpy_rate_kW(cooler.getOutletStream())
    h_liquid_out = enthalpy_rate_kW(sep.getLiquidOutStream())
    row = {
        "outlet_pressure_bara": pressure,
        "polytropic_efficiency": efficiency,
        "feed_mass_flow_kg_h": inlet,
        "gas_mass_flow_kg_h": gas_flow,
        "liquid_mass_flow_kg_h": float(sep.getLiquidOutStream().getFlowRate("kg/hr")),
        "power_kW": float(comp.getPower("kW")),
        "discharge_temperature_C": float(comp.getOutletStream().getTemperature("C")),
        "cooled_temperature_C": float(cooler.getOutletStream().getTemperature("C")),
        "cooler_duty_kW": float(cooler.getDuty() / 1000.0),
        "mass_balance_relative_error": abs(inlet - outlet) / inlet,
        "inlet_enthalpy_rate_kW": h_in,
        "cooled_outlet_enthalpy_rate_kW": h_gas_out,
        "liquid_outlet_enthalpy_rate_kW": h_liquid_out,
    }
    row["enthalpy_change_kW"] = h_gas_out + h_liquid_out - h_in
    row["energy_balance_residual_kW"] = row["enthalpy_change_kW"] - row["power_kW"] - row["cooler_duty_kW"]
    assert all(math.isfinite(v) for v in row.values()), row
    assert row["mass_balance_relative_error"] < 1e-8, row
    assert row["power_kW"] > 0 and row["discharge_temperature_C"] > 30.0, row
    assert abs(row["cooled_temperature_C"] - 35.0) < 1e-6, row
    assert abs(row["energy_balance_residual_kW"]) < 1e-5, row
    return row, process


def pipeline_case(ns, diameter, increments=20):
    feed = ns.process.equipment.stream.Stream("Pipe feed", make_fluid(ns))
    feed.setFlowRate(10000.0, "kg/hr")
    pipe_cls = ns.process.equipment.pipeline.PipeBeggsAndBrills
    pipe = pipe_cls("Teaching pipe", feed)
    pipe.setLength(5000.0)
    pipe.setDiameter(diameter)
    pipe.setElevation(0.0)
    pipe.setPipeWallRoughness(1e-5)
    pipe.setNumberOfIncrements(increments)
    pipe.setHeatTransferMode(pipe_cls.HeatTransferMode.ISOTHERMAL)
    process = ns.process.processmodel.ProcessSystem()
    process.add(feed)
    process.add(pipe)
    process.run()
    pout = float(pipe.getOutletStream().getPressure("bara"))
    assert 0.0 < pout < 60.0
    profile = [float(v) for v in pipe.getPressureProfile()]
    return {"diameter_m": diameter, "increments": increments,
            "outlet_pressure_bara": pout, "pressure_drop_bar": 60.0 - pout,
            "pressure_profile_bara": profile,
            "outlet_temperature_C": float(pipe.getOutletStream().getTemperature("C"))}


def nist_reference():
    refdir = BOOK / "references" / "nist"
    refdir.mkdir(parents=True, exist_ok=True)
    params = {"Action": "Data", "Wide": "on", "ID": "C74828", "Type": "IsoTherm",
              "Digits": "8", "PLow": "1", "PHigh": "201", "PInc": "50", "T": "298.15",
              "RefState": "DEF", "TUnit": "K", "PUnit": "bar", "DUnit": "kg/m3",
              "HUnit": "kJ/kg", "WUnit": "m/s", "VisUnit": "uPa*s", "STUnit": "N/m"}
    url = "https://webbook.nist.gov/cgi/fluid.cgi?" + urllib.parse.urlencode(params)
    path = refdir / "methane_298_15K.tsv"
    if not path.exists():
        request = urllib.request.Request(url, headers={"User-Agent": "NeqSim-book-validation/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
        path.write_bytes(data)
    raw = path.read_text(encoding="utf-8")
    rows = list(csv.DictReader(io.StringIO(raw), delimiter="\t"))
    assert len(rows) >= 5 and "Density (kg/m3)" in rows[0], raw[:500]
    provenance = {"url": url, "retrieved": "2026-09-12", "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                  "source": "NIST Chemistry WebBook SRD 69, calculated reference-fluid properties",
                  "classification": "public reference data", "file": str(path.relative_to(BOOK))}
    (refdir / "source.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return rows, provenance


def run(project_root, monte_carlo=200):
    import numpy as np
    start = time.monotonic()
    ns = bootstrap(project_root)
    output = {"basis": {"composition_mole_fraction": COMPOSITION, "temperature_K": 303.15,
                        "pressure_bara": 60.0, "mass_flow_kg_h": 10000.0, "model": "SRK",
                        "mixing_rule": "classic", "case_status": "synthetic teaching case"},
              "provenance": {"python": sys.executable, "python_version": sys.version,
                             "project_root": str(Path(project_root).resolve()),
                             "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=project_root, text=True).strip()},
              "checks": {}, "failures": []}
    import jpype
    output["provenance"]["loaded_code_source"] = str(jpype.JClass("neqsim.thermo.system.SystemSrkEos").class_.getProtectionDomain().getCodeSource().getLocation())
    assert "target/classes" in output["provenance"]["loaded_code_source"].replace("\\", "/")
    densities = []
    for p in (1.0, 51.0, 101.0, 151.0, 201.0):
        row = {"pressure_bara": p, "temperature_K": 298.15}
        for model in ("SRK", "PR"):
            f = make_fluid(ns, p, 298.15, model, {"methane": 1.0})
            ns.thermodynamicoperations.ThermodynamicOperations(f).TPflash()
            f.initProperties()
            row[model + "_density_kg_m3"] = float(f.getDensity("kg/m3"))
            row[model + "_Z"] = float(f.getZ())
            assert row[model + "_density_kg_m3"] > 0
        densities.append(row)
    output["methane_properties"] = densities
    try:
        refs, provenance = nist_reference()
        # NIST can repeat a state at a phase-label boundary. Match by state,
        # never by row position, and reject conflicting repeated densities.
        by_state = {}
        for ref in refs:
            key = (float(ref["Temperature (K)"]), float(ref["Pressure (bar)"]))
            if key in by_state:
                assert abs(float(ref["Density (kg/m3)"]) - float(by_state[key]["Density (kg/m3)"])) < 1e-8
            by_state[key] = ref
        for row in densities:
            ref = by_state[(row["temperature_K"], row["pressure_bara"])]
            assert abs(float(ref["Temperature (K)"]) - row["temperature_K"]) < 1e-8
            assert abs(float(ref["Pressure (bar)"]) - row["pressure_bara"]) < 1e-8
            row["NIST_density_kg_m3"] = float(ref["Density (kg/m3)"])
            for model in ("SRK", "PR"):
                row[model + "_deviation_pct"] = 100 * (row[model + "_density_kg_m3"] / row["NIST_density_kg_m3"] - 1)
        output["independent_reference"] = provenance
        output["checks"]["nist_reference_comparison"] = "completed; deviations reported, no universal accuracy claim"
    except Exception as exc:
        output["checks"]["nist_reference_comparison"] = "unavailable"
        output["failures"].append({"case": "reference_retrieval", "error": str(exc)})
    base, process = compression_case(ns)
    output["compression_base"] = base
    output["compression_sensitivity"] = [compression_case(ns, pressure=p)[0] for p in (80.0, 100.0, 120.0, 140.0, 160.0)]
    auto = process.getAutomation()
    assert "Compressor" in list(auto.getUnitList())
    before = float(auto.getVariableValue("Compressor.outletPressure", "bara"))
    auto.setVariableValue("Compressor.outletPressure", 130.0, "bara")
    process.run()
    after = float(auto.getVariableValue("Compressor.outletPressure", "bara"))
    assert abs(before - 120.0) < 1e-8 and abs(after - 130.0) < 1e-8
    output["checks"]["automation_read_write"] = {"before_bara": before, "after_bara": after}
    state = ns.process.processmodel.lifecycle.ProcessSystemState.fromProcessSystem(process)
    outdir = BOOK / "verification"
    outdir.mkdir(exist_ok=True)
    state.saveToFile(str(outdir / "process_state.json"))
    restored = ns.process.processmodel.lifecycle.ProcessSystemState.loadFromFile(str(outdir / "process_state.json"))
    json.loads(str(restored.toJson()))
    output["checks"]["state_save_load"] = "passed; JSON state only, not full environment replay"
    request = {"model": "SRK", "temperature": {"value": 25.0, "unit": "C"},
               "pressure": {"value": 50.0, "unit": "bara"}, "flashType": "TP",
               "components": COMPOSITION, "mixingRule": "classic"}
    runner_result = json.loads(str(ns.mcp.runners.FlashRunner.run(json.dumps(request))))
    (outdir / "flash_runner_response.json").write_text(json.dumps(runner_result, indent=2), encoding="utf-8")
    assert runner_result.get("status") == "success", runner_result
    output["checks"]["flash_runner"] = "passed; local core runner, not live MCP transport"
    output["pipeline_sensitivity"] = [pipeline_case(ns, d) for d in (0.15, 0.20, 0.25, 0.30)]
    output["pipeline_refinement"] = [pipeline_case(ns, 0.20, n) for n in (10, 20, 40)]
    output["hydrate_screening"] = []
    for p in (40.0, 60.0, 80.0, 100.0):
        try:
            wet_composition = dict(COMPOSITION)
            wet_composition["water"] = 0.01
            f = make_fluid(ns, p, 283.15, composition=wet_composition)
            f.setHydrateCheck(True)
            ns.thermodynamicoperations.ThermodynamicOperations(f).hydrateFormationTemperature()
            t = float(f.getTemperature("C"))
            assert math.isfinite(t) and -20 < t < 50
            output["hydrate_screening"].append({"pressure_bara": p, "hydrate_temperature_C": t})
        except Exception as exc:
            output["failures"].append({"case": "hydrate", "pressure_bara": p, "error": str(exc)})
    rng = np.random.default_rng(20260912)
    mc = []
    for i in range(monte_carlo):
        flow = float(rng.triangular(9000, 10000, 11000))
        efficiency = float(rng.triangular(0.70, 0.75, 0.80))
        try:
            row, _ = compression_case(ns, flow=flow, efficiency=efficiency)
            mc.append(row)
        except Exception as exc:
            output["failures"].append({"case": "monte_carlo", "index": i, "flow_kg_h": flow,
                                       "efficiency": efficiency, "error": str(exc)})
    output["uncertainty"] = {"seed": 20260912, "requested": monte_carlo, "completed": len(mc),
                             "method": "full NeqSim process run per draw", "convention": "non-exceedance",
                             "assumptions": "independent triangular flow 9000/10000/11000 kg/h and efficiency 0.70/0.75/0.80; teaching ranges",
                             "cases": mc}
    if mc:
        output["uncertainty"]["power_kW_quantiles"] = dict(zip(("q10", "q50", "q90"), map(float, np.quantile([r["power_kW"] for r in mc], [0.1, 0.5, 0.9]))))
    output["elapsed_seconds"] = time.monotonic() - start
    (BOOK / "results.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"base": base, "checks": output["checks"], "failures": output["failures"],
                      "monte_carlo_completed": len(mc), "elapsed_seconds": output["elapsed_seconds"]}, indent=2))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--monte-carlo", type=int, default=200)
    args = parser.parse_args()
    run(args.project_root, args.monte_carlo)
