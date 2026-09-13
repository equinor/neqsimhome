"""Migrate existing book notebooks to explicit, reproducible source execution."""
import json
import re
import shutil
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
BOOTSTRAP = '''# Execute against the selected, compiled NeqSim source checkout.
import os
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import jpype

if not os.environ.get("NEQSIM_PROJECT_ROOT"):
    raise RuntimeError("Set NEQSIM_PROJECT_ROOT to the NeqSim source checkout before running.")
PROJECT_ROOT = Path(os.environ["NEQSIM_PROJECT_ROOT"]).resolve()
if not (PROJECT_ROOT / "devtools" / "neqsim_dev_setup.py").exists():
    raise RuntimeError("NEQSIM_PROJECT_ROOT must contain devtools/neqsim_dev_setup.py.")
sys.path.insert(0, str(PROJECT_ROOT / "devtools"))
from neqsim_dev_setup import neqsim_init, neqsim_classes
ns = neqsim_classes(neqsim_init(project_root=PROJECT_ROOT, recompile=False, verbose=False))
jneqsim = jpype.JPackage("neqsim")
NEQSIM_MODE = "devtools"
NOTEBOOK_PATH = Path(globals().get("__vsc_ipynb_file__", Path.cwd() / "__NOTEBOOK_NAME__")).resolve()
BOOK_ROOT = NOTEBOOK_PATH.parents[3]
FIGURES_DIR = NOTEBOOK_PATH.parent.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)
sys.path.insert(0, str(BOOK_ROOT / "devtools"))
from book_figure_tools import configure_figures, export_figure_summary
configure_figures()
print(f"NeqSim source: {PROJECT_ROOT}; Python: {sys.executable}")

# Named NeqSim class bindings used throughout the chapter.
SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
SystemPrEos = jneqsim.thermo.system.SystemPrEos
SystemSrkCPAstatoil = jneqsim.thermo.system.SystemSrkCPAstatoil
ThermodynamicOperations = jneqsim.thermodynamicoperations.ThermodynamicOperations
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
ThreePhaseSeparator = jneqsim.process.equipment.separator.ThreePhaseSeparator
Compressor = jneqsim.process.equipment.compressor.Compressor
Cooler = jneqsim.process.equipment.heatexchanger.Cooler
Heater = jneqsim.process.equipment.heatexchanger.Heater
HeatExchanger = jneqsim.process.equipment.heatexchanger.HeatExchanger
Mixer = jneqsim.process.equipment.mixer.Mixer
Splitter = jneqsim.process.equipment.splitter.Splitter
ThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve
Pump = jneqsim.process.equipment.pump.Pump
Expander = jneqsim.process.equipment.expander.Expander
Recycle = jneqsim.process.equipment.util.Recycle
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
'''

AUTO_FIGURES = {
    "ch08": ["fig01_pressure_drop_vs_diameter.png", "fig02_pressure_drop_vs_flow.png", "fig03_liquid_holdup.png", "fig04_pipeline_capacity.png"],
    "ch09": ["fig01_hydrate_equilibrium.png", "fig02_meg_inhibition.png", "fig03_water_dewpoint.png", "fig04_hydrate_operating_envelope.png"],
    "ch10": ["fig01_phase_split.png", "fig02_souders_brown.png", "fig03_separator_optimization.png", "fig04_separation_train.png"],
}

for notebook in sorted(BOOK.glob("chapters/*/notebooks/*.ipynb")):
    original = BOOK / ".build" / "backups" / notebook.relative_to(BOOK)
    original.parent.mkdir(parents=True, exist_ok=True)
    if not original.exists():
        shutil.copy2(notebook, original)
    data = json.loads(notebook.read_text(encoding="utf-8"))
    first_code = True
    figure_index = 0
    chapter_code = notebook.parent.parent.name[:4]
    for cell in data["cells"]:
        source = "".join(cell["source"])
        if cell["cell_type"] == "code":
            if first_code:
                source = BOOTSTRAP.replace("__NOTEBOOK_NAME__", notebook.name)
                first_code = False
            else:
                source = source.replace("from neqsim import jneqsim", "# jneqsim is bound to the source JVM in the setup cell.")
                source = re.sub(r"dpi\s*=\s*150", "dpi=220", source)
                source = re.sub(r"([\"'])\.\./figures/([^\"']+)\1", r"FIGURES_DIR / '\2'", source)
                source = re.sub(r"Chapter \d+: ", "", source)
                # This elevation sign is defined in PipeBeggsAndBrills Javadoc.
                source = source.replace("setElevation(-2000.0)  # upward flow (negative = rising)", "setElevation(2000.0)  # positive elevation means upward flow")
                if chapter_code in AUTO_FIGURES and "plt.show()" in source and "savefig" not in source:
                    source = source.replace("plt.show()", 'plt.savefig(FIGURES_DIR / "{}", dpi=220, bbox_inches="tight")\nplt.show()'.format(AUTO_FIGURES[chapter_code][figure_index]))
                    figure_index += 1
            cell["outputs"] = []
            cell["execution_count"] = None
        cell["source"] = source.splitlines(keepends=True)
    if not any(c.get("metadata", {}).get("tags") == ["book-results-summary"] for c in data["cells"]):
        data["cells"].extend([
            {"cell_type": "markdown", "metadata": {}, "source": ["## Numerical output and figure provenance\n", "The following table is extracted from the plotted numerical data. Each saved figure has an adjacent CSV and JSON record; missing points remain visible and are not replaced by interpolated results. Extrema summarize the sampled operating envelope, and are not independent validation of the model.\n"]},
            {"cell_type": "code", "metadata": {"tags": ["book-results-summary"]}, "execution_count": None, "outputs": [], "source": ["figure_results = export_figure_summary(NOTEBOOK_PATH)\n", "print(figure_results.to_string(index=False, float_format=lambda value: f'{value:.6g}'))\n"]}
        ])
    data["metadata"]["neqsim_execution"] = {"mode": "source", "bootstrap": "neqsim_dev_setup", "automatic_package_installation": False}
    notebook.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("Migrated 35 notebooks; original files preserved in .build/backups.")
