"""Create and execute the revision's companion notebooks using one selected Python."""
from book_runtime import BOOK, LOCAL_DEPS
import argparse
import json
import os
import sys
from pathlib import Path
import nbformat
from nbclient import NotebookClient


def build(project_root):
    project_root = Path(project_root).resolve()
    kernel_root = BOOK / "verification" / "jupyter" / "kernels" / "neqsim_book_revision"
    kernel_root.mkdir(parents=True, exist_ok=True)
    kernel = {"argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
              "display_name": "NeqSim book selected Python", "language": "python",
              "env": {"PYTHONPATH": str(LOCAL_DEPS) + os.pathsep + str(BOOK),
                      "NEQSIM_PROJECT_ROOT": str(project_root)}}
    (kernel_root / "kernel.json").write_text(json.dumps(kernel, indent=2), encoding="utf-8")
    os.environ["JUPYTER_PATH"] = str(kernel_root.parents[1])
    report = []
    import yaml
    cfg = yaml.safe_load((BOOK / "book.yaml").read_text(encoding="utf-8-sig"))
    for part in cfg["parts"]:
        for chapter in part["chapters"]:
            slug = chapter["dir"]
            directory = BOOK / "chapters" / slug / "notebooks"
            directory.mkdir(exist_ok=True)
            path = directory / "01_revised_chapter.ipynb"
            setup = '''import os
import sys
from pathlib import Path

start = Path.cwd().resolve()
BOOK_DIR = next(p for p in [start] + list(start.parents)
                if (p / "book.yaml").is_file() and (p / "book_runtime.py").is_file())
sys.path.insert(0, str(BOOK_DIR))
from book_runtime import bootstrap
from build_illustrations import generate_chapter
import json
results = json.loads((BOOK_DIR / "results.json").read_text(encoding="utf-8"))
baseline_record = json.loads((BOOK_DIR / "verification" / "regression_baseline_2026-09-12.json").read_text(encoding="utf-8"))
baselines = baseline_record["outputs"]
assert results["basis"] == baseline_record["basis"], "Review a changed case basis before updating accepted baselines"
'''
            cells = [nbformat.v4.new_markdown_cell("# " + chapter["title"] + "\n\n13 September 2026 revision. The numerical examples use a synthetic teaching basis. Conceptual illustrations represent workflow relationships; they are not measured performance data. The image-generator art is retained with prompts and hashes in `illustrations/imagegen_manifest_2026-09-13.json`; this notebook checks and restores the reviewed raster asset rather than regenerating it through an AI call. Other diagrams and numerical plots are drawn by the maintained illustration code. Set `NEQSIM_PROJECT_ROOT` to the recorded source checkout before running numerical cells."),
                     nbformat.v4.new_code_cell(setup)]
            if slug in ("ch09", "ch10", "ch11"):
                cells.append(nbformat.v4.new_code_cell('jneqsim = bootstrap(os.environ["NEQSIM_PROJECT_ROOT"])\nfrom verify_examples import make_fluid, compression_case, pipeline_case'))
            if slug == "ch09":
                cells.append(nbformat.v4.new_markdown_cell("## Re-run the methane comparison\n\nThe NIST table is retained separately and matched by state, rather than row position. Agreement is reported for these states only."))
                cells.append(nbformat.v4.new_code_cell('''for row in baselines["methane_properties"]:
    for model in ("SRK", "PR"):
        fluid = make_fluid(jneqsim, row["pressure_bara"], 298.15, model, {"methane": 1.0})
        jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid).TPflash()
        fluid.initProperties()
        calculated = float(fluid.getDensity("kg/m3"))
        assert abs(calculated - row[model + "_density_kg_m3"]) < 1e-6
    print(row)
'''))
            elif slug == "ch10":
                cells.append(nbformat.v4.new_code_cell('''base, process = compression_case(jneqsim)
assert abs(base["power_kW"] - baselines["compression_base"]["power_kW"]) < 1e-6
print(base)
for expected in baselines["compression_sensitivity"]:
    row, _ = compression_case(jneqsim, pressure=expected["outlet_pressure_bara"])
    for key in ("power_kW", "discharge_temperature_C", "cooler_duty_kW", "cooled_temperature_C"):
        assert abs(row[key] - expected[key]) < 1e-6, (key, row[key], expected[key])
    assert row["mass_balance_relative_error"] < 1e-8
    print(row)
'''))
                cells.append(nbformat.v4.new_markdown_cell("## Repeat all uncertainty realisations\n\nThe low/base/high inputs are teaching assumptions. Each draw performs a complete NeqSim process run. Quantiles use the non-exceedance convention."))
                cells.append(nbformat.v4.new_code_cell('''import numpy as np
rng = np.random.default_rng(20260912)
powers = []
for _ in range(200):
    flow = float(rng.triangular(9000, 10000, 11000))
    efficiency = float(rng.triangular(0.70, 0.75, 0.80))
    row, _ = compression_case(jneqsim, flow=flow, efficiency=efficiency)
    powers.append(row["power_kW"])
quantiles = np.quantile(powers, [0.1, 0.5, 0.9])
expected = baselines["uncertainty"]["power_kW_quantiles"]
assert np.allclose(quantiles, [expected[k] for k in ("q10", "q50", "q90")], atol=1e-6, rtol=0)
print({"completed": len(powers), "power_kW_quantiles": quantiles.tolist()})
'''))
            elif slug == "ch11":
                cells.append(nbformat.v4.new_code_cell('''import numpy as np
for expected in baselines["pipeline_sensitivity"]:
    row = pipeline_case(jneqsim, expected["diameter_m"], expected["increments"])
    assert abs(row["pressure_drop_bar"] - expected["pressure_drop_bar"]) < 1e-6
    assert abs(row["outlet_temperature_C"] - expected["outlet_temperature_C"]) < 1e-6
    assert np.allclose(row["pressure_profile_bara"], expected["pressure_profile_bara"], atol=1e-6, rtol=0)
    print({k: v for k, v in row.items() if k != "pressure_profile_bara"})
for expected in baselines["pipeline_refinement"]:
    row = pipeline_case(jneqsim, expected["diameter_m"], expected["increments"])
    assert abs(row["pressure_drop_bar"] - expected["pressure_drop_bar"]) < 1e-6
    assert abs(row["outlet_temperature_C"] - expected["outlet_temperature_C"]) < 1e-6
    assert np.allclose(row["pressure_profile_bara"], expected["pressure_profile_bara"], atol=1e-6, rtol=0)
    print({"increments": row["increments"], "pressure_drop_bar": row["pressure_drop_bar"]})
'''))
                cells.append(nbformat.v4.new_code_cell('''from verify_examples import COMPOSITION
for reference in baselines["hydrate_screening"]:
    composition = dict(COMPOSITION)
    composition["water"] = 0.01
    fluid = make_fluid(jneqsim, reference["pressure_bara"], 283.15, composition=composition)
    fluid.setHydrateCheck(True)
    jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid).hydrateFormationTemperature()
    calculated = float(fluid.getTemperature("C"))
    assert abs(calculated - reference["hydrate_temperature_C"]) < 1e-6
    print({"pressure_bara": reference["pressure_bara"], "hydrate_temperature_C": calculated})
'''))
            cells.append(nbformat.v4.new_code_cell(f'generate_chapter("{slug}")\nprint("Chapter illustrations regenerated from maintained source and verified results.")'))
            for image in sorted((directory.parent / "figures").glob("*.png")):
                cells.append(nbformat.v4.new_markdown_cell(f"![{image.stem.replace('_', ' ').capitalize()}](../figures/{image.name})\n\nRead the corresponding chapter discussion for the diagram's meaning or the numerical figure's observation, mechanism, implication and recommendation."))
            nb = nbformat.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "neqsim_book_revision", "display_name": kernel["display_name"], "language": "python"}})
            nbformat.write(nb, path)
            client = NotebookClient(nb, timeout=300, kernel_name="neqsim_book_revision", resources={"metadata": {"path": str(directory)}})
            client.execute()
            nbformat.write(nb, path)
            report.append({"chapter": slug, "notebook": str(path.relative_to(BOOK)), "status": "passed",
                           "executed_cells": sum(c.cell_type == "code" for c in nb.cells)})
            print(slug + ": passed", flush=True)
    (BOOK / "verification" / "notebook_execution.json").write_text(json.dumps({"python": sys.executable, "project_root": str(project_root), "notebooks": report}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    build(parser.parse_args().project_root)
