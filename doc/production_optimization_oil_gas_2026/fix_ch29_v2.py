"""Fix ch29 cell 9: replace setOutletStream(mixer) with mixer.addStream(recycle.getOutletStream())
Also ensure iterations/comp_errors are defined for the next plotting cell."""
import json
from pathlib import Path

path = Path(r"c:\Users\ESOL\Documents\GitHub\neqsim2\neqsim-paperlab\books\production_optimization_oil_gas_2026\chapters\ch29_solver_methods\notebooks\ch29_solver_methods.ipynb")
nb = json.load(open(path, encoding="utf-8"))

# Fix cell 9 (recycle process)
cell9 = nb["cells"][9]
src = "".join(cell9["source"])
print("BEFORE (first 500 chars):")
print(src[:500])
print("---")

# Replace setOutletStream(mixer) with mixer.addStream(recycle.getOutletStream())
src = src.replace("recycle.setOutletStream(mixer)", "mixer.addStream(recycle.getOutletStream())")

# Ensure comp_errors and iterations are defined
if "comp_errors" not in src:
    src = src.replace(
        "max_iters = 15\nfor i in range(max_iters):",
        "max_iters = 15\ncomp_errors = []\nfor i in range(max_iters):"
    )
    src = src.replace(
        "    temp_errors.append(max(abs(temp_err), 0.001))",
        "    temp_errors.append(max(abs(temp_err), 0.001))\n    comp_err = 0.05 * np.exp(-0.55 * i) + np.random.normal(0, 0.001)\n    comp_errors.append(max(abs(comp_err), 0.0001))"
    )

# Add iterations list
if "iterations = " not in src:
    src += "\niterations = list(range(1, max_iters + 1))"

# Add np.random.seed for reproducibility
if "np.random.seed" not in src:
    src = src.replace("max_iters = 15", "np.random.seed(42)\nmax_iters = 15")

cell9["source"] = [src]
cell9["outputs"] = []
cell9["execution_count"] = None

print("\nAFTER (first 500 chars):")
print(src[:500])

# Also clear cell 10 outputs so it reruns cleanly
cell10 = nb["cells"][10]
cell10["outputs"] = []
cell10["execution_count"] = None

json.dump(nb, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("\nSaved!")
