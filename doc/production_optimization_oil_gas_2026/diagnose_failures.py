"""Diagnose notebook failures by reading error outputs from executed notebooks."""
import json, os, sys
from pathlib import Path

BOOK = Path(__file__).parent
CHAPTERS = BOOK / "chapters"

log = json.load(open(BOOK / "notebook_execution_log.json"))
failed = [e for e in log if e["status"] == "FAILED"]

for entry in failed:
    nb_rel = entry["notebook"]
    nb_path = CHAPTERS / nb_rel
    if not nb_path.exists():
        print(f"\n{'='*70}\n{nb_rel}: FILE NOT FOUND\n")
        continue

    nb = json.load(open(nb_path, encoding="utf-8"))
    # Find first cell with error output
    for i, cell in enumerate(nb.get("cells", [])):
        if cell["cell_type"] != "code":
            continue
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                ename = out.get("ename", "?")
                evalue = out.get("evalue", "?")
                src_preview = "".join(cell["source"][:3]).strip()[:120]
                print(f"\n{'='*70}")
                print(f"NB: {nb_rel}")
                print(f"Cell {i}: {ename}: {evalue[:200]}")
                print(f"Source: {src_preview}")
                # Print last few traceback lines
                tb = out.get("traceback", [])
                if tb:
                    # strip ANSI
                    import re
                    last = re.sub(r'\x1b\[[0-9;]*m', '', tb[-1]) if tb else ""
                    print(f"TB: {last[:200]}")
                break  # Only first error per notebook
        else:
            continue
        break
