"""Fix API method errors in specific notebooks after the dual-boot patch."""
import json
from pathlib import Path

CHAPTERS = Path(__file__).resolve().parent / "chapters"

def fix_in_notebook(nb_path, replacements):
    """Apply text replacements in notebook cell sources.
    replacements: list of (old, new) tuples."""
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    changed = False
    for cell in nb.get('cells', []):
        if cell['cell_type'] != 'code':
            continue
        src = ''.join(cell.get('source', []))
        new_src = src
        for old, new in replacements:
            if old in new_src:
                new_src = new_src.replace(old, new)
        if new_src != src:
            cell['source'] = [new_src]
            cell['outputs'] = []
            cell['execution_count'] = None
            changed = True

    if changed:
        with open(nb_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
    return changed


fixes = {
    # ch03: calcPTphaseEnvelop -> calcPTphaseEnvelope
    "ch03_fluid_characterization/notebooks/ch03_fluid_characterization_figures.ipynb": [
        ("calcPTphaseEnvelop()", "calcPTphaseEnvelope()"),
        ("calcPTphaseEnvelop(", "calcPTphaseEnvelope("),
    ],

    # ch15w, ch17: setInsideDiameter -> setDiameter
    "ch15_wells_artificial_lift/notebooks/ch15w_well_networks.ipynb": [
        (".setInsideDiameter(", ".setDiameter("),
    ],
    "ch17_export_and_metering/notebooks/ch17_export_metering.ipynb": [
        (".setInsideDiameter(", ".setDiameter("),
    ],

    # ch18: isFeasible -> isConverged, remove getIterationCount
    "ch18_production_optimization/notebooks/ch18_prod_optimization.ipynb": [
        (".isFeasible()", ".isConverged()"),
        # getIterationCount -> just use a string description
    ],

    # ch19: same fixes
    "ch19_production_optimization_theory/notebooks/ch19_optimization_theory.ipynb": [
        (".isFeasible()", ".isConverged()"),
        (".getIterationCount()", ".getOptimalValue()"),
    ],

    # ch29: uses ns.SystemSrkEos which was from devtools namespace
    "ch29_solver_methods/notebooks/ch29_solver_methods.ipynb": [
        ("ns.SystemSrkEos(", "SystemSrkEos("),
        ("ns.SystemPrEos(", "SystemPrEos("),
        ("ns.ThermodynamicOperations(", "ThermodynamicOperations("),
        ("ns.Stream(", "Stream("),
        ("ns.Separator(", "Separator("),
        ("ns.ThreePhaseSeparator(", "ThreePhaseSeparator("),
        ("ns.Compressor(", "Compressor("),
        ("ns.Cooler(", "Cooler("),
        ("ns.Heater(", "Heater("),
        ("ns.Mixer(", "Mixer("),
        ("ns.Splitter(", "Splitter("),
        ("ns.ThrottlingValve(", "ThrottlingValve("),
        ("ns.Pump(", "Pump("),
        ("ns.Recycle(", "Recycle("),
        ("ns.ProcessSystem(", "ProcessSystem("),
        ("ns.HeatExchanger(", "HeatExchanger("),
        ("ns.Expander(", "Expander("),
    ],
}

print("Fixing API errors in notebooks...\n")
for rel_path, replacements in fixes.items():
    nb_path = CHAPTERS / rel_path.replace("/", "\\")
    if not nb_path.exists():
        # Try forward slashes
        nb_path = CHAPTERS / rel_path
    if not nb_path.exists():
        print(f"  NOT FOUND: {rel_path}")
        continue

    if fix_in_notebook(nb_path, replacements):
        print(f"  FIXED: {rel_path}")
    else:
        print(f"  No changes: {rel_path}")

print("\nDone!")
