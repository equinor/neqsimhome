"""Replace four hand-drawn envelopes using the literal manuscript fluid bases.

Run with the selected Python and NEQSIM_PROJECT_ROOT. No source manuscript is edited.
"""
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1]
SOURCE = Path(os.environ["NEQSIM_PROJECT_ROOT"]).resolve()
sys.path.insert(0, str(BOOK / ".build/python_packages"))
sys.path.insert(0, str(SOURCE / "devtools"))
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=SOURCE, recompile=False, verbose=False)
import jpype
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
j = jpype.JPackage("neqsim")
OUT = HERE / "legacy_phase_envelopes"
OUT.mkdir(exist_ok=True)
CASES = [
    {"chapter": "ch02_thermodynamic_foundations", "file": "phase_envelope.png", "title": "Hydrocarbon mixture: SRK phase envelope", "eos": "SystemSrkEos", "basis_section": "2.6.3", "components": [("methane", .80), ("ethane", .08), ("propane", .05), ("n-butane", .03), ("n-pentane", .02), ("n-heptane", .02)]},
    {"chapter": "ch03_fluid_characterization", "file": "gas_condensate_phase_envelope.png", "title": "Six-component gas-condensate surrogate: PR", "eos": "SystemPrEos", "basis_section": "3.7.5", "substitute_basis": "Illustration-only six-defined-compound surrogate: methane/ethane/propane/n-butane/n-pentane/n-hexane = 70/10/8/5/4/3 mol%. This does not validate the original characterized-fluid envelope; original trace/TP-flash failures are retained in ch03_probe.json. An intermediate defined-compound C20 surrogate also left an unresolved bubble segment and is retained in ch03_c20_surrogate_evidence.json.", "components": [("methane", 70), ("ethane", 10), ("propane", 8), ("n-butane", 5), ("n-pentane", 4), ("n-hexane", 3)]},
    {"chapter": "ch12_gas_processing", "file": "phase_envelope_gas.png", "title": "Rich gas: SRK phase envelope", "eos": "SystemSrkEos", "basis_section": "12.8", "components": [("nitrogen", 1), ("CO2", 2.5), ("methane", 80), ("ethane", 6), ("propane", 4), ("i-butane", 1), ("n-butane", 2), ("i-pentane", .5), ("n-pentane", .5), ("n-hexane", 1), ("n-heptane", .5), ("n-octane", 1)]},
    {"chapter": "ch19_export_and_metering", "file": "phase_envelope_export_gas.png", "title": "Export-gas example: SRK phase envelope", "eos": "SystemSrkEos", "basis_section": "19.6.2", "components": [("nitrogen", .008), ("CO2", .015), ("methane", .880), ("ethane", .055), ("propane", .020), ("i-butane", .005), ("n-butane", .007), ("i-pentane", .003), ("n-pentane", .002), ("n-hexane", .003), ("n-heptane", .002)]},
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def new_fluid(case):
    f = getattr(j.thermo.system, case["eos"])(293.15, 50.)
    for name, amount in case["components"]:
        f.addComponent(name, float(amount))
    for name, amount, mw, density in case.get("tbp", []):
        f.addTBPfraction(name, float(amount), float(mw), float(density))
    f.setMixingRule("classic")
    if case.get("characterise_plus"):
        f.getCharacterization().characterisePlusFraction()
    return f

def flash_probe(case, temperature, pressure):
    f = new_fluid(case)
    f.setTemperature(float(temperature))
    f.setPressure(float(pressure))
    j.thermodynamicoperations.ThermodynamicOperations(f).TPflash()
    f.initProperties()
    beta = 0.
    phases = []
    z = np.array([float(f.getComponent(k).getz()) for k in range(f.getNumberOfComponents())])
    reconstructed = np.zeros_like(z)
    for i in range(f.getNumberOfPhases()):
        p = f.getPhase(i)
        b = float(f.getBeta(i))
        phases.append({"type": str(p.getType()), "beta": b, "density_kg_m3": float(p.getDensity("kg/m3"))})
        if str(p.getType()).lower() == "gas":
            beta += b
        x = np.array([float(p.getComponent(k).getx()) for k in range(len(z))])
        assert abs(x.sum()-1) < 1e-7
        reconstructed += b*x
    err = float(np.max(np.abs(z-reconstructed)))
    assert err < 1e-7
    assert all(np.isfinite(p["density_kg_m3"]) and p["density_kg_m3"] > 0 for p in phases)
    fugacity_error = None
    if f.getNumberOfPhases() == 2:
        values = []
        for i in range(2):
            p = f.getPhase(i)
            values.append(np.array([float(p.getComponent(k).getx()) * float(p.getComponent(k).getFugacityCoefficient()) for k in range(len(z))]))
        fugacity_error = float(np.max(np.abs(np.log(values[0]/values[1]))))
        assert fugacity_error < 1e-6, (case["chapter"], temperature, pressure, fugacity_error)
    return {"T_K": float(temperature), "P_bara": float(pressure), "gas_labelled_fraction": beta, "phases": phases, "component_closure_max_abs": err, "max_absolute_log_fugacity_ratio": fugacity_error}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.titlesize": 14, "axes.labelsize": 12, "axes.spines.top": False, "axes.spines.right": False, "legend.fontsize": 10, "savefig.dpi": 240})
records = []
for case in CASES:
    if len(sys.argv) > 1 and case["chapter"][:4] not in sys.argv[1:]:
        continue
    f = new_fluid(case)
    f.init(0)
    normalized = [{"component": str(f.getComponent(k).getComponentName()), "mole_fraction": float(f.getComponent(k).getz()), "molar_mass_kg_mol": float(f.getComponent(k).getMolarMass())} for k in range(f.getNumberOfComponents())]
    assert abs(sum(x["mole_fraction"] for x in normalized)-1) < 1e-12
    ops = j.thermodynamicoperations.ThermodynamicOperations(f)
    ops.calcPTphaseEnvelope(False, 1.)
    branches = []
    for tkey, pkey in [("dewT", "dewP"), ("bubT", "bubP")]:
        t, p = np.array(ops.get(tkey), dtype=float), np.array(ops.get(pkey), dtype=float)
        assert t.shape == p.shape
        valid = np.isfinite(t) & np.isfinite(p) & (t > 0) & (p > 0)
        assert valid.sum() >= 3, (case["chapter"], tkey, valid.sum())
        # Preserve discontinuity gaps; removing NaNs would draw false connections.
        t[~valid] = np.nan
        p[~valid] = np.nan
        branches.append({"getter_T": tkey, "T": t, "P": p, "valid": valid})
    branches.sort(key=lambda b: np.nanmax(b["T"]), reverse=True)
    probes = []
    for label, branch in zip(["Dew boundary", "Bubble boundary"], branches):
        branch["physical_label"] = label
        # At a low-pressure saturation point, temperature perturbations distinguish
        # the nearly all-gas dew limit from the nearly all-liquid bubble limit.
        for target_pressure in [5., 20., 40.]:
            index = int(np.nanargmin(np.abs(branch["P"] - target_pressure)))
            low = flash_probe(case, branch["T"][index] - .5, branch["P"][index])
            high = flash_probe(case, branch["T"][index] + .5, branch["P"][index])
            if label.startswith("Dew"):
                assert 0 < low["gas_labelled_fraction"] < 1 and high["gas_labelled_fraction"] > .99999, (case["chapter"], label, low, high)
            else:
                # A dense single-phase state can retain NeqSim's GAS label.
                # Identify the liquid side from density continuity with the
                # liquid-rich two-phase state, not from the phase name alone.
                assert len(low["phases"]) == 1 and len(high["phases"]) == 2, (case["chapter"], label, low, high)
                liquid = max(high["phases"], key=lambda p: p["density_kg_m3"])
                assert liquid["beta"] > .5, (case["chapter"], label, low, high)
                assert abs(low["phases"][0]["density_kg_m3"] / liquid["density_kg_m3"]-1) < .10, (case["chapter"], label, low, high)
            probes.append({"branch": label, "point_T_K": float(branch["T"][index]), "point_P_bara": float(branch["P"][index]), "minus_0_5K": low, "plus_0_5K": high})
    t_all = np.concatenate([b["T"] for b in branches])
    p_all = np.concatenate([b["P"] for b in branches])
    i_t, i_p = int(np.nanargmax(t_all)), int(np.nanargmax(p_all))
    extrema = {"sampled_cricondentherm": {"T_C": float(t_all[i_t]-273.15), "P_bara": float(p_all[i_t])}, "sampled_cricondenbar": {"T_C": float(t_all[i_p]-273.15), "P_bara": float(p_all[i_p])}}
    stem = case["chapter"][:4]
    csv_path = OUT / (stem + "_envelope.csv")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["branch", "original_getter", "point_index", "T_K", "T_C", "P_bara", "valid"])
        for b in branches:
            for k, (t, p, valid) in enumerate(zip(b["T"], b["P"], b["valid"])):
                writer.writerow([b["physical_label"], b["getter_T"], k, t, t-273.15, p, bool(valid)])
    fig, ax = plt.subplots(figsize=(8.5, 5.7))
    for b, color, style in zip(branches, ["#136F91", "#BE6A25"], ["-", "--"]):
        ax.plot(b["T"]-273.15, b["P"], color=color, linestyle=style, linewidth=2.3, label=b["physical_label"])
    for key, color, marker, offset in [("sampled_cricondentherm", "#136F91", "o", (-12,-35)), ("sampled_cricondenbar", "#5D476F", "s", (-5,25))]:
        point = extrema[key]
        ax.scatter(point["T_C"], point["P_bara"], color=color, marker=marker, s=43, zorder=5)
        name = "Cricondentherm" if "therm" in key else "Cricondenbar"
        ax.annotate(f"{name} (sampled)\n{point['T_C']:.1f} °C; {point['P_bara']:.1f} bara", (point["T_C"], point["P_bara"]), xytext=offset, textcoords="offset points", ha="right" if "therm" in key else "center", va="top" if "therm" in key else "bottom", fontsize=9, arrowprops={"arrowstyle": "-", "color": color}, bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "none", "alpha": .9})
    ax.set(xlabel="Temperature (°C)", ylabel="Pressure (bara)", title=case["title"])
    ax.set_ylim(0, np.nanmax(p_all)*1.24)
    ax.margins(x=.08)
    ax.grid(alpha=.22)
    ax.legend(loc="upper left")
    if case["chapter"] == "ch12_gas_processing":
        ax.annotate("Unresolved continuation\nsegments left open", (-55, 89), xytext=(-135, 100), fontsize=9, color="#525252", arrowprops={"arrowstyle": "->", "color": "#777777"})
    fig.text(.5, .012, "Fixed composition · classic mixing rule · VLE only (solids excluded) · continuation gaps left open", ha="center", fontsize=8.5, color="#525252")
    fig.tight_layout(rect=(0,.03,1,1))
    target = BOOK / "chapters" / case["chapter"] / "figures" / case["file"]
    backup = BOOK / ".build/backups/scientific_revision_legacy_envelopes" / case["chapter"] / case["file"]
    backup.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not backup.exists():
        shutil.copy2(target, backup)
    fig.savefig(target, bbox_inches="tight", dpi=240)
    plt.close(fig)
    composition_total = sum(x[1] for x in case["components"]) + sum(x[1] for x in case.get("tbp", []))
    basis = f"the explicitly specified fluid in Section {case['basis_section']}" if not case.get("substitute_basis") else "an illustration-only defined-compound surrogate, not the Section 3.7.5 TBP fluid"
    caption = f"NeqSim {case['eos'].replace('System', '').replace('Eos', '').upper()} vapour-liquid saturation envelope for {basis}. The traced maxima are {extrema['sampled_cricondentherm']['T_C']:.1f} °C (cricondentherm) and {extrema['sampled_cricondenbar']['P_bara']:.1f} bara (cricondenbar). Markers are sampled continuation extrema; no critical point or production/export trajectory is inferred. Dew/bubble assignment was checked by fresh TP flashes at three pressures around each branch. Continuation gaps remain open; solids, hydrates and aqueous stability are outside this VLE calculation."
    record = {**case, "raw_amount_sum": composition_total, "normalization": "All component amounts are normalized by NeqSim to the recorded mole fractions; TBP density inputs are g/cm3 and molar masses kg/mol.", "normalized_composition": normalized, "path": str(target), "sha256": sha(target), "data_path": str(csv_path), "data_sha256": sha(csv_path), "backup_path": str(backup), "caption": caption, "extrema": extrema, "branch_classification": "Dew branch has the larger maximum temperature, verified with fresh TP flashes at T +/- 0.5 K near 5 bara. Getter names alone were not trusted.", "branch_probes": probes, "raw_getter_mapping": [{"getter": b["getter_T"], "physical_label": b["physical_label"], "valid_points": int(b["valid"].sum()), "gap_points": int((~b["valid"]).sum())} for b in branches], "physics_scope": "Fixed-composition fluid saturation envelope; no solid, hydrate or aqueous stability envelope, lab tuning, critical-point certification, or operating trajectory. Extrema are sampled maxima, not independently optimized extrema."}
    records.append(record)
    record["basis_match"] = "illustration_only_surrogate" if case.get("substitute_basis") else "exact_manuscript_component_amounts_and_EOS"
    record["branch_classification"] = "Dew branch has the larger maximum temperature; fresh TP flashes at T +/- 0.5 K at three traced points nearest 5, 20 and 40 bara bracket the single-phase/two-phase transition. The dense single-phase bubble side is identified by density continuity, since its NeqSim phase label can be GAS. Getter names alone were not trusted."
    states = [p[key] for p in probes for key in ["minus_0_5K", "plus_0_5K"]]
    record["verification"] = {"status": "passed_scoped_VLE_checks", "fresh_TP_flash_states": len(states), "component_closure_max_abs": max(s["component_closure_max_abs"] for s in states), "component_closure_tolerance": 1e-7, "phase_composition_sum_tolerance": 1e-7, "two_phase_fugacity_max_abs_log_ratio": max(s["max_absolute_log_fugacity_ratio"] or 0 for s in states), "log_fugacity_ratio_tolerance": 1e-6, "positive_finite_phase_densities": True, "limitation": "Three low/moderate-pressure transition brackets per branch verify classification and local VLE consistency; they do not validate every continuation point or EOS accuracy against laboratory data. Sampled extrema and open continuation gaps remain explicitly qualified."}
    (OUT / (stem + "_evidence.json")).write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps({"chapter": case["chapter"], "extrema": extrema, "branches": record["raw_getter_mapping"]}), flush=True)
manifest = {"created_utc": datetime.now(timezone.utc).isoformat(), "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=SOURCE, text=True).strip(), "python": sys.executable, "script_sha256": sha(Path(__file__)), "records": records}
(OUT / "phase_envelope_replacements.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
(OUT / "captions.md").write_text("\n\n".join("## " + r["chapter"] + "\n\n" + r["caption"] + "\n\n" + "Input amounts: " + "; ".join(f"{name}={amount:g}" for name, amount in r["components"]) + ("; TBP fractions " + str(r["tbp"]) if r.get("tbp") else "") + f". Amount sum {r['raw_amount_sum']:g}, normalized as recorded in the evidence JSON." for r in records) + "\n", encoding="utf-8")
