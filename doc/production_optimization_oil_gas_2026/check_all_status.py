"""Check all notebooks for error outputs."""
import json
from pathlib import Path

CHAPTERS_DIR = Path("chapters")
failed = []
ok = []

for nb_path in sorted(CHAPTERS_DIR.rglob("*.ipynb")):
    nb = json.load(open(nb_path, encoding="utf-8"))
    has_error = False
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                has_error = True
                break
        if has_error:
            break
    if has_error:
        failed.append(str(nb_path.relative_to(CHAPTERS_DIR)))
    else:
        # Check if it has any execution outputs (was it run?)
        has_outputs = any(
            len(c.get("outputs", [])) > 0
            for c in nb["cells"] if c["cell_type"] == "code"
        )
        ok.append((str(nb_path.relative_to(CHAPTERS_DIR)), has_outputs))

print(f"Notebooks with errors: {len(failed)}")
for f in failed:
    print(f"  FAIL: {f}")

print(f"\nNotebooks OK: {len(ok)}")
unexecuted = [name for name, has_out in ok if not has_out]
if unexecuted:
    print(f"  Unexecuted: {len(unexecuted)}")
    for u in unexecuted:
        print(f"    {u}")
