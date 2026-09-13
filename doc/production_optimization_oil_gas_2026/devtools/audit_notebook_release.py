"""Read-only integrity gate for the executed notebook and figure release."""
import hashlib
import json
import math
import sys
from importlib import metadata
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]

def strict_json_values(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, list):
        return [strict_json_values(item) for item in value]
    if isinstance(value, dict):
        return {key: strict_json_values(item) for key, item in value.items()}
    return value

reports = []
for report_path in sorted((BOOK / "verification" / "notebooks").glob("*.json")):
    report = strict_json_values(json.loads(report_path.read_text(encoding="utf-8")))
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    reports.append(report)
problems = []
figures = []
partial_domains = []
if len(reports) != 35:
    problems.append("Expected 35 chapter notebook reports; found {}".format(len(reports)))
for report in reports:
    path = BOOK / report["notebook"]
    notebook = json.loads(path.read_text(encoding="utf-8"))
    if report["status"] != "passed" or report["executed_cells"] != report["code_cells"]:
        problems.append("Incomplete execution: " + report["notebook"])
    if Path(report["python"]).resolve() != Path(sys.executable).resolve():
        problems.append("Notebook used another Python interpreter: " + report["notebook"])
    if hashlib.sha256(path.read_bytes()).hexdigest() != report["notebook_sha256"]:
        problems.append("Notebook changed after execution: " + report["notebook"])
    for cell_run in report["cell_runs"]:
        cell = notebook["cells"][cell_run["cell_index"]]
        digest = hashlib.sha256("".join(cell["source"]).encode()).hexdigest()
        if digest != cell_run["sha256"]:
            problems.append("Code cell changed after execution: {} / {}".format(report["notebook"], cell_run["execution_count"]))
    error_outputs = [output for cell in notebook["cells"] for output in cell.get("outputs", []) if output["output_type"] == "error"]
    if error_outputs:
        problems.append("Notebook retains error outputs: " + report["notebook"])
    if "target/classes" not in report.get("neqsim_class_origin", "").replace("\\", "/"):
        problems.append("Source class origin not verified: " + report["notebook"])
    for name, values in report.get("numeric_results", {}).items():
        if not isinstance(values, list):
            continue
        flat = [value for row in values for value in (row if isinstance(row, list) else [row])]
        if len(flat) > 2 and not any(value is not None and math.isfinite(value) for value in flat):
            problems.append("Entire numerical array is undefined: {} / {}".format(report["notebook"], name))
    for figure in report["figures"]:
        figure_path = Path(figure["path"])
        if not figure_path.exists() or hashlib.sha256(figure_path.read_bytes()).hexdigest() != figure["sha256"]:
            problems.append("Missing or stale figure: " + str(figure_path))
        figures.append(str(figure_path.relative_to(BOOK)))
    if report.get("nonfinite_series"):
        partial_domains.append({"notebook": report["notebook"], "series": report["nonfinite_series"],
                                "interpretation": "Undefined one-phase quantities or physically infeasible hydraulic trials are explicitly retained as gaps."})

summary = {"status": "passed" if not problems else "failed", "notebooks": len(reports),
           "passed_notebooks": sum(report["status"] == "passed" for report in reports),
           "executed_code_cells": sum(report["executed_cells"] for report in reports),
           "fresh_figures": len(set(figures)), "figure_discussions": sum(len(report.get("figure_discussions", [])) for report in reports),
           "source_revisions": sorted(set(report["source_revision"] for report in reports)),
           "python_interpreters": sorted(set(report["python"] for report in reports)),
           "python_version": sys.version,
           "book_local_dependencies": {distribution.metadata["Name"]: distribution.version
               for distribution in metadata.distributions(path=[str(BOOK / ".build" / "python_packages")])
               if distribution.metadata["Name"].lower() in {"numpy", "scipy", "pandas", "matplotlib", "jpype1", "nbformat", "ipython"}},
           "problems": problems, "declared_partial_domains": partial_domains,
           "validation_scope": "Executed code, source provenance, artifact integrity, finite-result audit and notebook engineering assertions. This does not constitute blanket validation against independent experimental or field data."}
(BOOK / "verification" / "notebook_release_audit.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
updates = [item for report in reports for item in report.get("figure_discussions", [])]
(BOOK / "verification" / "notebook_figure_updates.json").write_text(json.dumps(updates, indent=2, ensure_ascii=False), encoding="utf-8")
(BOOK / "verification" / "notebook_execution_report.json").write_text(json.dumps(reports, indent=2, ensure_ascii=False), encoding="utf-8")
lines = ["# Notebook release verification", "", "Status: **{}**".format(summary["status"].upper()), "",
         "- Chapter notebooks executed: {} / 35".format(summary["passed_notebooks"]),
         "- Code cells executed: {}".format(summary["executed_code_cells"]),
         "- Fresh generated scientific figures: {}".format(summary["fresh_figures"]),
         "- Figure discussion blocks: {}".format(summary["figure_discussions"]),
         "- Source revision: `{}`".format(", ".join(summary["source_revisions"])), "",
         summary["validation_scope"], "", "## Declared operating-domain gaps", "",
         "Some hydraulic trial rates cannot satisfy a positive pressure solution, and a gas/oil phase ratio is undefined in a one-phase state. Those states are kept as explicit gaps rather than interpolated or replaced with invented values.", "",
         "## Integrity checks", "",
         "The gate checks every code-cell hash, notebook hash, generated PNG hash, the active Python executable, NeqSim's source-class origin, retained error outputs, and arrays containing no finite result."]
if problems:
    lines += ["", "## Unresolved issues", ""] + ["- " + problem for problem in problems]
(BOOK / "verification" / "NOTEBOOK_VERIFICATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({k: summary[k] for k in ("status", "notebooks", "passed_notebooks", "executed_code_cells", "fresh_figures", "figure_discussions", "problems")}, indent=2))
raise SystemExit(0 if not problems else 1)
