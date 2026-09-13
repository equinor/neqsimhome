"""Extract actual tracebacks from executed (failed) notebooks."""
import json, sys, os

BOOK_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(BOOK_DIR, "chapters")

# Read the execution log
log_path = os.path.join(BOOK_DIR, "notebook_execution_log.json")
with open(log_path) as f:
    log = json.load(f)

failed = [e for e in log if e["status"] == "FAILED"]
print(f"=== {len(failed)} failed notebooks ===\n")

for entry in failed:
    nb_rel = entry["notebook"]
    nb_path = os.path.join(CHAPTERS_DIR, nb_rel)

    print(f"--- {nb_rel} ---")

    if not os.path.exists(nb_path):
        print("  FILE NOT FOUND\n")
        continue

    with open(nb_path, encoding="utf-8") as f:
        nb = json.load(f)

    # Find cells with error outputs
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                ename = output.get("ename", "?")
                evalue = output.get("evalue", "?")
                # Get last few lines of traceback
                tb = output.get("traceback", [])
                # Strip ANSI codes for readability
                import re
                tb_clean = [re.sub(r'\x1b\[[0-9;]*m', '', line) for line in tb]
                tb_short = "\n".join(tb_clean[-4:]) if len(tb_clean) > 4 else "\n".join(tb_clean)

                # Get first line of cell source
                src = "".join(cell["source"])[:120]
                print(f"  Cell {i}: {ename}: {evalue}")
                print(f"  Source: {src}")
                print(f"  Traceback tail:")
                for line in tb_clean[-3:]:
                    print(f"    {line}")
                print()
                break  # only first error per notebook
    print()
