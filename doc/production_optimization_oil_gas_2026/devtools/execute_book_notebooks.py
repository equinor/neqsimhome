"""Execute every code cell using this exact Python interpreter and source JVM.

The executor deliberately uses a fresh process per notebook, avoiding notebook
kernel selection and stale Java classes. It stops at the first failed cell,
persists cell outputs and records source hashes and generated figure evidence.
"""
import argparse
import base64
import concurrent.futures
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone

BOOK = Path(__file__).resolve().parents[1]


def run_one(path):
    started = time.monotonic()
    notebook = json.loads(path.read_text(encoding="utf-8"))
    notebook["cells"] = [cell for cell in notebook["cells"] if "book-generated-figure-discussion" not in cell.get("metadata", {}).get("tags", [])]
    namespace = {"__name__": "__main__", "__file__": str(path), "__vsc_ipynb_file__": str(path)}
    os.chdir(path.parent)
    count, errors, cell_runs = 0, [], []
    discussions_by_cell = {}
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        count += 1
        source = "".join(cell["source"])
        stdout, stderr = io.StringIO(), io.StringIO()
        cell_start = time.monotonic()
        cell["execution_count"] = count
        cell["outputs"] = []
        failure = None
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                exec(compile(source, "{}:cell{}".format(path.name, index), "exec"), namespace)
            except BaseException as error:
                failure = error
                detail = traceback.format_exc()
        for name, capture in (("stdout", stdout), ("stderr", stderr)):
            if capture.getvalue():
                cell["outputs"].append({"output_type": "stream", "name": name, "text": capture.getvalue().splitlines(keepends=True)})
        # Preserve fresh generated plots inline, as well as their external files.
        try:
            from book_figure_tools import FIGURE_RECORDS
            if "_displayed_figure_count" not in namespace:
                namespace["_displayed_figure_count"] = 0
            for record in FIGURE_RECORDS[namespace["_displayed_figure_count"]:]:
                image_path = Path(record["path"])
                if image_path.suffix.lower() == ".png":
                    cell["outputs"].append({"output_type": "display_data", "data": {
                        "image/png": base64.b64encode(image_path.read_bytes()).decode("ascii"),
                        "text/plain": ["Executed figure: " + image_path.name]}, "metadata": {}})
                from book_discussions import describe
                discussion = describe(record, int(path.parent.parent.name[2:4]), path.parent.parent.name, path.name)
                discussions_by_cell.setdefault(index, []).append(discussion)
            namespace["_displayed_figure_count"] = len(FIGURE_RECORDS)
        except ImportError:
            pass
        if failure is not None:
            cell["outputs"].append({"output_type": "error", "ename": type(failure).__name__, "evalue": str(failure), "traceback": detail.splitlines()})
            errors.append({"cell_index": index, "error": type(failure).__name__, "message": str(failure), "traceback": detail})
        cell_runs.append({"cell_index": index, "execution_count": count, "runtime_seconds": round(time.monotonic() - cell_start, 3),
                          "sha256": hashlib.sha256(source.encode()).hexdigest(), "status": "failed" if failure else "passed"})
        if failure:
            break
    result = {"notebook": str(path.relative_to(BOOK)), "status": "failed" if errors else "passed",
              "executed_at": datetime.now(timezone.utc).isoformat(), "python": sys.executable,
              "source_root": os.environ["NEQSIM_PROJECT_ROOT"], "runtime_seconds": round(time.monotonic() - started, 2),
              "code_cells": sum(c["cell_type"] == "code" for c in notebook["cells"]), "executed_cells": count,
              "cell_runs": cell_runs, "errors": errors}
    result["source_revision"] = subprocess.check_output(["git", "-C", result["source_root"], "rev-parse", "HEAD"], text=True).strip()
    try:
        import jpype
        result["java_version"] = str(jpype.JClass("java.lang.System").getProperty("java.version"))
        result["neqsim_class_origin"] = str(jpype.JClass("neqsim.thermo.system.SystemSrkEos").class_.getProtectionDomain().getCodeSource().getLocation())
        from book_figure_tools import FIGURE_RECORDS
        result["figures"] = FIGURE_RECORDS
        result["nonfinite_series"] = [s for f in FIGURE_RECORDS for s in f["series"] if s["n_nonfinite"]]
        import numpy as np
        numeric_results = {}
        for name, value in namespace.items():
            if name.startswith("_"):
                continue
            if isinstance(value, (int, float, np.number)) and not isinstance(value, bool):
                numeric_results[name] = float(value) if np.isfinite(value) else None
            elif isinstance(value, (list, tuple, np.ndarray)):
                try:
                    array = np.asarray(value, dtype=float)
                    if array.ndim in (1, 2) and array.size <= 2000:
                        numeric_results[name] = np.where(np.isfinite(array), array, np.nan).tolist()
                except (TypeError, ValueError):
                    pass
        result["numeric_results"] = numeric_results
    except Exception:
        result["figures"] = []
    result["figure_discussions"] = [item for items in discussions_by_cell.values() for item in items]
    from book_discussions import markdown
    updated_cells = []
    index_map = {}
    for original_index, cell in enumerate(notebook["cells"]):
        index_map[original_index] = len(updated_cells)
        updated_cells.append(cell)
        for item in discussions_by_cell.get(original_index, []):
            updated_cells.append({"cell_type": "markdown", "metadata": {"tags": ["book-generated-figure-discussion"],
                "figure": item["figure"]}, "source": markdown(item).splitlines(keepends=True)})
    notebook["cells"] = updated_cells
    for cell_run in result["cell_runs"]:
        cell_run["cell_index"] = index_map[cell_run["cell_index"]]
    for error in result["errors"]:
        error["cell_index"] = index_map[error["cell_index"]]
    notebook["metadata"]["execution_verification"] = {k: result[k] for k in ("status", "executed_at", "source_revision", "python", "runtime_seconds")}
    path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    result["notebook_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    output = BOOK / "verification" / "notebooks" / (path.parent.parent.name + ".json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(path.parent.parent.name, result["status"], result["runtime_seconds"], "seconds", flush=True)
    return not errors


def subprocess_one(path):
    log = BOOK / "verification" / "logs" / (path.parent.parent.name + ".log")
    log.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONPATH"] = str(BOOK / ".build" / "python_packages") + os.pathsep + env.get("PYTHONPATH", "")
    env["JAVA_TOOL_OPTIONS"] = "-Xmx2g -Djava.awt.headless=true"
    with log.open("w", encoding="utf-8") as output:
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--one", str(path)], env=env,
                                   stdout=output, stderr=subprocess.STDOUT, timeout=1200)
    print(path.parent.parent.name, "PASS" if completed.returncode == 0 else "FAIL", flush=True)
    return completed.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--one", type=Path)
    parser.add_argument("--chapters", default="")
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    if args.one:
        sys.exit(0 if run_one(args.one.resolve()) else 1)
    notebooks = sorted(BOOK.glob("chapters/*/notebooks/*.ipynb"))
    if args.chapters:
        prefixes = args.chapters.split(",")
        notebooks = [p for p in notebooks if any(p.parent.parent.name.startswith(prefix) for prefix in prefixes)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(subprocess_one, notebooks))
    reports = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((BOOK / "verification" / "notebooks").glob("*.json"))]
    (BOOK / "verification" / "notebook_execution_report.json").write_text(json.dumps(reports, indent=2, ensure_ascii=False), encoding="utf-8")
    figure_updates = [item for report in reports for item in report.get("figure_discussions", [])]
    (BOOK / "verification" / "notebook_figure_updates.json").write_text(json.dumps(figure_updates, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Completed:", sum(code == 0 for code in results), "/", len(results), "passed", flush=True)
