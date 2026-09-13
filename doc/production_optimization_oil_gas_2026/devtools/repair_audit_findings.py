"""Second-pass corrections from executed figure and output evidence."""
import json
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
for prefix in ["ch04", "ch09", "ch30", "ch31", "ch35"]:
    path = next(BOOK.glob("chapters/{}*/notebooks/*.ipynb".format(prefix)))
    data = json.loads(path.read_text(encoding="utf-8"))
    for index, cell in enumerate(data["cells"]):
        source = "".join(cell["source"])
        if prefix == "ch04":
            source = source.replace("Se = (Sw - Swc) / (1.0 - Swc - Sor)", "Se = np.clip((Sw - Swc) / (1.0 - Swc - Sor), 0.0, 1.0)")
            if index == 8:
                source = source.replace("fig, ax = plt.subplots", "# A gas/oil phase ratio is undefined outside the two-phase domain.\nfinite_gor = np.isfinite(gor_values)\nprint(f'Two-phase GOR domain: {finite_gor.sum()} of {len(pressures)} states; remaining single-phase states are not assigned a GOR.')\nfig, ax = plt.subplots")
        if prefix == "ch09":
            source = source.replace("fluid.setMultiPhaseCheck(True)", "fluid.setMultiPhaseCheck(True)\n" + ("    " if index in [4, 8, 11] else "") + "fluid.setHydrateCheck(True)")
            # Each fluid-construction block uses four-space indentation.
            if index == 4:
                source = source.replace("        hydrate_temps_C.append(float('nan'))", "        raise RuntimeError(f'Hydrate equilibrium failed at {P} bara')")
                source += '\nassert np.all(np.isfinite(hydrate_temps_C)), "Hydrate curve must be fully finite"\n'
            if index == 8:
                source = source.replace("        hydrate_T_with_meg.append(float('nan'))", "        raise RuntimeError(f'MEG hydrate equilibrium failed at {meg_wt*100:.0f} wt%')")
                source = source.replace("base_T = hydrate_T_with_meg[0] if not np.isnan(hydrate_T_with_meg[0]) else 20.0", "assert np.all(np.isfinite(hydrate_T_with_meg))\nbase_T = hydrate_T_with_meg[0]")
            source = source.replace("Safe operating region", "Hydrate-free equilibrium region")
            source = source.replace("# Simulated pipeline T-P path", "# Assumed illustrative pipeline T-P path (not a transient simulation)")
            source = source.replace("'Normal operation (wellhead → platform)'", "'Assumed normal-operation path'")
            source = source.replace("'Shutdown cooldown'", "'Assumed shutdown path'")
        if prefix == "ch30":
            source = source.replace("After Cooler.outStream.temperature", "After Cooler.outletStream.temperature")
            source = source.replace("'Plant Measurement'", "'Synthetic sensor sample'")
            source = source.replace("'Digital Twin vs Plant Measurements'", "'Digital twin with synthetic sensor noise'")
            if index == 8:
                source = source.replace("sim_vals = [30.0, 40.0, 50000.0, 1500.0, 35.0]  # representative values", "sim_vals = [float(simulated_values[address]) for address, unit in variables_to_read]  # actual process predictions")
        if prefix == "ch31" and index == 13:
            source = source.replace("target temperature = 20 C", "target temperature = 40 C")
            source = source.replace('adjuster.setTargetVariable(valve.getOutletStream(), "temperature", 273.15 + 20.0, "K")', 'adjuster.setTargetVariable(valve.getOutletStream(), "temperature", 40.0, "C")\n# Current Adjuster supports custom targets through the functional callback.\ntemperature_reader = jpype.JProxy("java.util.function.Function", dict={"apply": lambda equipment: float(equipment.getTemperature("C"))})\nadjuster.setTargetValueCalculator(temperature_reader)')
            source = source.replace("Target temperature:   20.0", "Target temperature:   40.0")
            source += '\nassert abs(outlet_T - 40.0) < 0.05, "Adjuster must satisfy the stated target"\n'
        if prefix == "ch35" and index == 5:
            source = '''# Explicit density and compressibility calculations, not a phase-envelope fallback.
# Pure-CO2 critical properties do not define a mixture's two-phase boundary.
assert np.all(np.isfinite(densities)) and np.all(np.asarray(densities) > 0)
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))
ax.plot(pressures, densities, "o-", label="96 mol% CO2 stream, SRK")
ax.set(xlabel="Pressure (bara)", ylabel="Bulk density (kg/m³)", title="CO2-rich stream at 25 °C")
ax2.plot(pressures, z_factors, "s-", color="#DF7B29")
ax2.set(xlabel="Pressure (bara)", ylabel="Compressibility factor (-)", title="Pressure sensitivity")
for axis in (ax, ax2): axis.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig(FIGURES_DIR / "ch35_co2_density_compressibility.png", dpi=220, bbox_inches="tight")
plt.show()
print("SRK screening mixture: 96 mol% CO2, 2 mol% N2, 1 mol% O2, 1 mol% water. These are model predictions, not a certified transport envelope.")
'''
        if prefix == "ch35" and index == 7:
            start = source.index("    # Wobbe index approximation")
            end = source.index("    wobbe_indices.append(wobbe)")
            source = source[:start] + '''    # ISO 6976 calculation handles mole fractions consistently.
    # Volume and combustion reference temperatures are both 15 degrees C.
    gas_quality = jneqsim.standards.gasquality.Standard_ISO6976(blend, 15.0, 15.0, "volume")
    gas_quality.calculate()
    wobbe = float(gas_quality.getValue("SuperiorWobbeIndex")) / 1000.0  # kJ/m3 -> MJ/m3
''' + source[end:]
            source += '\nassert np.all(np.diff(wobbe_indices) < 0), "Hydrogen addition must reduce the superior Wobbe index for this methane blend"\n'
        if prefix == "ch35" and index == 8:
            source = source.replace("# Typical Wobbe index limits for gas appliances", "# Example comparison band only; appliance interchangeability needs a full specification.")
            source = source.replace('label="Typical appliance range"', 'label="Illustrative comparison band"')
        cell["source"] = source.splitlines(keepends=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("Applied hydration initialization, saturation boundary, callback, Wobbe and provenance fixes.")
