"""Inspect ch29 notebook cells."""
import json
from pathlib import Path

path = Path(r"c:\Users\ESOL\Documents\GitHub\neqsim2\neqsim-paperlab\books\production_optimization_oil_gas_2026\chapters\ch29_solver_methods\notebooks\ch29_solver_methods.ipynb")
nb = json.load(open(path, encoding="utf-8"))
for i, c in enumerate(nb["cells"]):
    src = "".join(c.get("source", []))
    print(f"{i}: {c['cell_type']} - {src[:80]}")
