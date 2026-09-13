#!/usr/bin/env python3
"""Execute all book notebooks in-place using nbconvert.

Uses the pip neqsim package (already installed). The dual-boot cell in each
notebook falls through to the pip path automatically.

Usage:
    python run_all_notebooks.py            # run all
    python run_all_notebooks.py --dry-run  # list without running
    python run_all_notebooks.py --only ch02  # run only matching chapter
"""

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError


BOOK_DIR = Path(__file__).resolve().parent
CHAPTERS_DIR = BOOK_DIR / "chapters"


def find_all_notebooks():
    """Return sorted list of all .ipynb files under chapters/."""
    return sorted(CHAPTERS_DIR.rglob("*.ipynb"))


def execute_notebook(nb_path, timeout=600):
    """Execute a notebook in-place. Returns (success, elapsed, error_msg)."""
    t0 = time.time()
    try:
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        ep = ExecutePreprocessor(
            timeout=timeout,
            kernel_name="python3",
            allow_errors=False,
        )
        # Execute in the notebook's own directory so relative paths work
        ep.preprocess(nb, {"metadata": {"path": str(nb_path.parent)}})

        # Write executed notebook back
        with open(nb_path, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)

        elapsed = time.time() - t0
        return True, elapsed, None

    except CellExecutionError as e:
        elapsed = time.time() - t0
        # Still save the partial outputs (the errored cell has traceback)
        try:
            with open(nb_path, "w", encoding="utf-8") as f:
                nbformat.write(nb, f)
        except Exception:
            pass
        return False, elapsed, str(e)[:500]

    except Exception as e:
        elapsed = time.time() - t0
        return False, elapsed, traceback.format_exc()[:500]


def main():
    parser = argparse.ArgumentParser(description="Execute all book notebooks")
    parser.add_argument("--dry-run", action="store_true", help="List notebooks without running")
    parser.add_argument("--only", type=str, default=None, help="Filter: only run notebooks matching this substring")
    parser.add_argument("--timeout", type=int, default=600, help="Per-cell timeout in seconds (default: 600)")
    parser.add_argument("--continue-on-error", action="store_true", help="Continue running remaining notebooks after a failure")
    args = parser.parse_args()

    notebooks = find_all_notebooks()
    if args.only:
        notebooks = [nb for nb in notebooks if args.only in str(nb)]

    print(f"Found {len(notebooks)} notebooks\n")

    if args.dry_run:
        for i, nb in enumerate(notebooks, 1):
            rel = nb.relative_to(CHAPTERS_DIR)
            print(f"  {i:2d}. {rel}")
        return

    results = []
    for i, nb_path in enumerate(notebooks, 1):
        rel = nb_path.relative_to(CHAPTERS_DIR)
        print(f"[{i:2d}/{len(notebooks)}] Running: {rel} ... ", end="", flush=True)

        success, elapsed, err = execute_notebook(nb_path, timeout=args.timeout)

        if success:
            print(f"OK ({elapsed:.1f}s)")
            results.append({"notebook": str(rel), "status": "OK", "time_s": round(elapsed, 1)})
        else:
            print(f"FAILED ({elapsed:.1f}s)")
            print(f"         Error: {err[:200]}")
            results.append({"notebook": str(rel), "status": "FAILED", "time_s": round(elapsed, 1), "error": err[:300]})
            if not args.continue_on_error:
                print("\nStopping. Use --continue-on-error to keep going.")
                break

    # Summary
    ok = sum(1 for r in results if r["status"] == "OK")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    total_time = sum(r["time_s"] for r in results)
    print(f"\n{'='*60}")
    print(f"Results: {ok} OK, {failed} FAILED out of {len(results)} run ({total_time:.0f}s total)")

    if failed:
        print("\nFailed notebooks:")
        for r in results:
            if r["status"] == "FAILED":
                print(f"  - {r['notebook']}")

    # Save results log
    log_path = BOOK_DIR / "notebook_execution_log.json"
    with open(log_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nLog saved to: {log_path}")


if __name__ == "__main__":
    main()
