"""Record reviewing-agent image inspection and reconcile exported plot arrays."""
import csv
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent.parent
AUDIT = HERE / "figure_visual_review"
initial = json.loads((AUDIT / "inspection_inventory.json").read_text(encoding="utf-8"))
full_resolution = {26, 27, 28, 29, 40, 44, 49, 59, 60, 72, 87, 89, 91, 93, 99, 105}
fixes = {
    26: "Title explicitly identifies the constant-temperature case as isothermal; the seawater line is an ambient reference, not a heat-transfer calculation.",
    27: "Separated inlet/outlet annotations so both points can be identified.",
    28: "Moved the operating-point annotation clear of the annular-region label and explicitly marked the regime map illustrative.",
    29: "Moved narrow pressure-budget labels outside their bars; all seven increments and arrival pressure are readable.",
    40: "The highest sampled final-separator oil rate is 32.023 tonnes/h at 8 bara second-stage pressure. Final pressure is 1.5 bara at calculated flash temperature; no reference-condition stock-tank flash is applied. Corrected axis/annotation labels are readable.",
    44: "Placed the two-axis legend above both bar series; API gravity and density retain distinct axes and units.",
    49: "Replaced the unreferenced typical C3+ specification with an illustrative 5 mol% limit; composition is not a dew-point certificate.",
    72: "Replaced the unreferenced typical pressure-drop specification with an illustrative 50 bar limit.",
    87: "Moved the combined two-axis legend above the bars so the 243 tonnes/h label is visible.",
    91: "Expanded the vertical scale using the actual data maximum; the low-gain overshoot near 64.5% is no longer clipped.",
    93: "Labelled the fraction as NeqSim gas-labelled phase fraction. Separate TP-flash probes confirmed the high-pressure unit fraction belongs to a single gas-labelled phase; the plot does not locate a critical point.",
}
notes = {
    59: "Full-size compressor map has explicit flow, head, efficiency and speed units; surge/stonewall curves are distinguished from speed curves.",
    60: "Heat-exchanger endpoint temperatures remain separated, with no temperature cross. The horizontal coordinate is fractional duty, not a measured axial profile.",
    89: "VFP contours have a labelled bara colour scale and wellhead pressure/rate axes. Retained BHP_grid, whp_values and flow_values underlie the contour, which is not represented by the line-only CSV export.",
    99: "The retained nonmonotonic TEG trend is visible and discussed: minimum 18.1767 ppmv at 4181.8 kg/h, increasing slightly to 18.1951 ppmv at 5000 kg/h. The 30 ppmv line is the example input specification.",
    105: "NIST parity and deviation panels were inspected at full resolution; all 18 SRK/PR values use nine separately archived reference states and the declared 3% teaching accuracy budget.",
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def reconcile(path):
    metadata = json.loads(path.with_suffix(".data.json").read_text(encoding="utf-8"))
    assert metadata["sha256"] == sha(path), str(path)
    data_path = path.with_suffix(".csv")
    if not data_path.exists():
        assert not metadata["series"]
        return {"status": "no_line_bar_scatter_data", "series_count": 0, "limitation": "Filled regions, stackplots, pies and contours require retained notebook arrays/source plus the physical ledger; absence of a CSV is not a data validation pass."}
    with data_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    groups = defaultdict(list)
    for row in rows:
        groups[(int(row["panel"]), row["series"])].append(row)
    for series in metadata["series"]:
        group = groups[(series["panel"], series["series"])]
        assert len(group) == series["n_points"], (path, series, len(group))
        finite = [r for r in group if math.isfinite(float(r["x"])) and math.isfinite(float(r["y"]))]
        assert len(group) - len(finite) == series["n_nonfinite"]
        if finite:
            for axis in ("x", "y"):
                values = [float(r[axis]) for r in finite]
                for suffix, value in (("min", min(values)), ("max", max(values))):
                    assert math.isclose(value, series[f"{axis}_{suffix}"], rel_tol=1e-12, abs_tol=1e-12), (path, series, axis)
    return {"status": "passed", "csv_path": str(data_path), "csv_sha256": sha(data_path), "metadata_sha256": sha(path.with_suffix(".data.json")), "series_count": len(metadata["series"]), "rows": len(rows), "nonfinite_rows": sum(s["n_nonfinite"] for s in metadata["series"]), "tolerance": {"relative": 1e-12, "absolute": 1e-12}, "scope": "Exported line, bar and scatter point counts, finite masks and extrema versus companion metadata; visual trends/axis units were reviewed separately."}

records = []
for index, old in enumerate(initial, 1):
    path = Path(old["path"])
    result = reconcile(path) if index < 105 else {"status": "benchmark_results_provenance", "evidence": str(HERE / "benchmark_results.json"), "sha256": sha(HERE / "benchmark_results.json")}
    records.append({"index": index, "chapter": old["chapter"], "path": str(path), "sha256": sha(path), "initial_sha256": old["sha256"], "contact_sheet": old["contact_sheet"], "contact_sheet_sha256": sha(Path(old["contact_sheet"])), "overview_inspected": True, "full_resolution_inspected": index in full_resolution, "review_status": "passed_after_repair" if index in fixes else "passed_scoped_review", "findings": [fixes[index]] if index in fixes else [notes.get(index, "Axes, units, legend, displayed trends and domain gaps inspected in the contact-sheet review; no material visual defect identified.")], "data_reconciliation": result})

report = {"created_utc": datetime.now(timezone.utc).isoformat(), "scope": "104 freshly executed chapter notebook figures and one independent NIST benchmark plot. Legacy manuscript illustrations are outside this audit and tracked separately.", "method": "Visual inspection by the reviewing agent of all 18 retained six-image contact sheets, 16 representative/repaired full-resolution views, and automatic CSV-to-metadata reconciliation. Material repairs were made in generating plot cells and all 35 notebooks rerun before final hashes.", "summary": {"images_inspected": len(records), "contact_sheets_inspected": 18, "full_resolution_views": len(full_resolution), "plot_cells_repaired": len(fixes), "unresolved_material_visual_defects": 0, "exported_series_reconciled": sum(r["data_reconciliation"].get("series_count", 0) for r in records), "exported_rows_reconciled": sum(r["data_reconciliation"].get("rows", 0) for r in records)}, "limitations": ["This is a scoped scientific/visual review of teaching examples, not field calibration or universal equipment certification.", "PNG/CSV export captures plotted line, bar and scatter series, but not full data for all filled plots or contours. The notebook physical ledger and native retained arrays are the evidence for those plot types.", "Pressure-budget bars encode pressure differences in bar; their position is absolute pressure in bara. Compressor map and operating limits are teaching inputs, not manufacturer ratings.", "Timing results depend on JVM warm-up and machine load and are not a controlled performance benchmark.", "Conceptual regime maps and idealized controller examples are explicitly illustrative; they are not measured plant behaviour."], "notebook_physics_review_sha256": sha(HERE / "notebook_physics_review.json"), "execution_report_sha256": sha(BOOK / "verification" / "notebook_execution_report.json"), "records": records}
(HERE / "figure_visual_review.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
lines = ["# Notebook figure visual and scientific review", "", report["scope"], "", report["method"], "", f"**105/105 images inspected; 11 plot cells repaired; 16 full-resolution views; no unresolved material visual defect.** {report['summary']['exported_series_reconciled']} exported series and {report['summary']['exported_rows_reconciled']} rows reconcile with saved metadata at 1e-12 absolute/relative tolerance.", "", "## Repairs and scientific qualifications", ""]
lines += [f"- Figure {i}: {text}" for i, text in fixes.items()]
lines += ["", "## Scope limits", ""] + [f"- {text}" for text in report["limitations"]]
lines += ["", "## Inspected file inventory", "", "| Image | Chapter | File | Full resolution | Data evidence |", "|---|---|---|---|---|"]
lines += [f"| {r['index']} | {r['chapter']} | {Path(r['path']).name} | {'yes' if r['full_resolution_inspected'] else 'contact sheet'} | {r['data_reconciliation']['status']} |" for r in records]
lines += ["", "The JSON companion retains absolute paths, final image/CSV/metadata hashes, original contact-sheet hashes and per-image findings. Native retained arrays and their physical checks are in the chapter execution reports and notebook_physics_review.json."]
(HERE / "figure_visual_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps(report["summary"], indent=2))
