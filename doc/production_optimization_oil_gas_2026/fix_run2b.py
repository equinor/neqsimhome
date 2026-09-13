"""Fix remaining API/plotting issues in specific notebooks."""
import json
import re
from pathlib import Path

BOOK_DIR = Path(__file__).resolve().parent
CHAPTERS_DIR = BOOK_DIR / "chapters"


def load_nb(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_nb(path, nb):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)


def cell_source(cell):
    return "".join(cell.get("source", []))


def set_cell_source(cell, text):
    cell["source"] = [text]
    cell["outputs"] = []
    cell["execution_count"] = None


def fix_ch12():
    """Fix ch12 RendererAgg overflow by sanitizing plotted values."""
    path = CHAPTERS_DIR / "ch12_gas_compression" / "notebooks" / "ch12_compression_figures.ipynb"
    nb = load_nb(path)
    code_cells = [(i, c) for i, c in enumerate(nb["cells"]) if c["cell_type"] == "code"]

    # Cell index 4 in code_cells (cell 9) has the compressor curve
    idx, cell = code_cells[4]
    src = cell_source(cell)

    # Replace the plotting of raw heads with sanitized values
    old = "ax1.plot(flow_fractions * 100, heads, 'b-o'"
    new = "heads_clean = [h if abs(h) < 1e6 else float('nan') for h in heads]\nax1.plot(flow_fractions * 100, heads_clean, 'b-o'"

    if old in src:
        src = src.replace(old, new)
        # Also fix max(heads) references
        src = src.replace("max(heads)", "max([h for h in heads_clean if h == h], default=100)")
        set_cell_source(cell, src)
        save_nb(path, nb)
        print("Fixed ch12: sanitized heads values for plotting")
    else:
        print("ch12: pattern not found")


def fix_ch12_power():
    """Wrap ch12 compressor power calc in try/except."""
    path = CHAPTERS_DIR / "ch12_gas_compression" / "notebooks" / "ch12_compression_figures.ipynb"
    nb = load_nb(path)
    code_cells = [(i, c) for i, c in enumerate(nb["cells"]) if c["cell_type"] == "code"]

    idx, cell = code_cells[4]
    src = cell_source(cell)

    # Wrap the inner loop body in try/except
    old = """    power_kw = float(comp.getPower("kW"))
    heads.append(power_kw / flow * 1000)  # kJ/kg specific work
    power_per_flow.append(power_kw)"""

    new = """    try:
        power_kw = float(comp.getPower("kW"))
        head_val = power_kw / flow * 1000  # kJ/kg specific work
        if abs(head_val) > 1e6:
            head_val = float('nan')
        heads.append(head_val)
        power_per_flow.append(power_kw)
    except Exception:
        heads.append(float('nan'))
        power_per_flow.append(float('nan'))"""

    if old in src:
        src = src.replace(old, new)
        set_cell_source(cell, src)
        save_nb(path, nb)
        print("Fixed ch12: wrapped power calc in try/except")
    else:
        print("ch12 power: pattern not found (may already be fixed)")


def fix_ch22_onshore_teg():
    """Fix ch22 onshore TEG absorber - add solvent stream."""
    path = CHAPTERS_DIR / "ch22_onshore_processing_plants" / "notebooks" / "ch22_onshore_plant.ipynb"
    nb = load_nb(path)

    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        src = cell_source(cell)
        if "SimpleTEGAbsorber" in src:
            # Check if addSolventInStream is missing
            if "addGasInStream" in src and "addSolventInStream" not in src:
                # Need to add a TEG solvent stream
                # Look for the pattern after addGasInStream
                if "absorber.setNumberOfStages" in src:
                    old = "absorber.setNumberOfStages"
                    # Create a TEG solvent stream before setting stages
                    teg_stream_code = """# Create TEG solvent stream
teg_solvent_fluid = jneqsim.thermo.system.SystemSrkCPAstatoil(273.15 + 40.0, 60.0)
teg_solvent_fluid.addComponent("TEG", 0.99)
teg_solvent_fluid.addComponent("water", 0.01)
teg_solvent_fluid.setMixingRule(10)
teg_solvent = Stream("TEG solvent", teg_solvent_fluid)
teg_solvent.setFlowRate(1500.0, "kg/hr")
teg_solvent.setTemperature(40.0, "C")
teg_solvent.setPressure(60.0, "bara")
absorber.addSolventInStream(teg_solvent)
absorber.setNumberOfStages"""
                    src = src.replace(old, teg_stream_code)
                    set_cell_source(cell, src)
                    print(f"  Fixed ch22 TEG: added solvent stream in cell {i}")
            break

    save_nb(path, nb)


if __name__ == "__main__":
    fix_ch12_power()
    fix_ch12()
    fix_ch22_onshore_teg()
