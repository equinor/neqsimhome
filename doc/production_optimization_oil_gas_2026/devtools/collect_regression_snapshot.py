"""Collect an explicitly labelled candidate numerical regression snapshot."""
import argparse
import hashlib
import json
from pathlib import Path
BOOK = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--replace-candidate', action='store_true', help='Archive and replace this edition\'s unaccepted candidate only')
args = parser.parse_args()
entries = []
specifications = [
    ("ch03", "bo_values", 0, "Same-sample oil formation volume factor at 50 bara", "m3/m3", 0.01),
    ("ch03", "bo_values", -1, "Same-sample oil formation volume factor at 400 bara", "m3/m3", 0.01),
    ("ch05", "q_op", None, "Coupled production rate", "t/hr", 0.02),
    ("ch05", "achieved_pwh", None, "Solved wellhead pressure", "bara", 0.05),
    ("ch09", "hydrate_temps_C", 6, "Uninhibited hydrate equilibrium at 100 bara", "C", 0.05),
    ("ch09", "water_dew_temps", 0, "Water dew point, 50 ppmv at 20 bara", "C", 0.05),
    ("ch09", "water_dew_temps", -1, "Water dew point, 50 ppmv at 200 bara", "C", 0.05),
    ("ch14", "powers_75", 4, "Compression power, pressure ratio 6 and polytropic efficiency0.75", "kW", 1.0),
    ("ch14", "powers_85", 4, "Compression power, pressure ratio 6 and polytropic efficiency0.85", "kW", 1.0),
    ("ch16", "duty_kW", None, "Design heat transfer from hot stream", "kW", 0.2),
    ("ch17", "cv_values", 0, "Required valve Cv at 10 t/hr", "US Cv", 0.01),
    ("ch17", "cv_values", -1, "Required valve Cv at 80 t/hr", "US Cv", 0.01),
    ("ch23", "opt_rate", None, "Power-limited screening throughput", "kg/hr", 250.0),
    ("ch23", "opt_value", None, "Compressor power at screening throughput", "kW", 5.0),
    ("ch24", "opt_rates", 0, "Native binary-search throughput with power boundary", "kg/hr", 25.0),
    ("ch28", "bhp", None, "VFP BHP at 30 t/hr and 80 bara WHP", "bara", 0.05),
    ("ch31", "outlet_T", None, "Adjusted JT outlet temperature", "C", 0.05),
    ("ch31", "outlet_P", None, "Adjusted JT outlet pressure", "bara", 0.05),
    ("ch33", "water_content", 0, "Dry-gas water at 500 kg/hr lean TEG", "ppmv", 0.1),
    ("ch33", "water_content", -1, "Dry-gas water at 5000 kg/hr lean TEG", "ppmv", 0.1),
    ("ch35", "wobbe_indices", 0, "ISO 6976 superior Wobbe index, methane", "MJ/m3", 0.02),
    ("ch35", "wobbe_indices", -1, "ISO 6976 superior Wobbe index, 50 mol% H2", "MJ/m3", 0.02),
]
for prefix, variable, index, name, unit, tolerance in specifications:
    report = json.loads(next((BOOK / "verification" / "notebooks").glob(prefix + "*.json")).read_text(encoding="utf-8"))
    if report["status"] != "passed":
        raise RuntimeError("Cannot snapshot failed notebook: " + prefix)
    value = report["numeric_results"][variable]
    if index is not None:
        value = value[index]
    entries.append({"name": name, "value": value, "unit": unit, "suggested_abs_tolerance": tolerance,
                    "notebook": report["notebook"], "variable": variable, "index": index,
                    "source_revision": report["source_revision"], "notebook_sha256": report["notebook_sha256"]})
snapshot = {"status": "candidate", "purpose": "Numerical regression reference for this executed edition, not experimental validation.",
            "tolerance_note": "Suggested tolerances detect implementation drift; they are not uncertainty estimates or field acceptance criteria.", "entries": entries}
output = BOOK / "verification" / "scientific_regression_snapshot_2026_09.json"
if output.exists():
    previous=json.loads(output.read_text(encoding='utf-8'))
    if not args.replace_candidate or previous.get('status')!='candidate':
        raise RuntimeError("Snapshot exists; an accepted reference is never overwritten. Use --replace-candidate only after reviewing an unaccepted candidate.")
    backup=BOOK/'.build/backups/regression_snapshots'
    backup.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    (backup/(digest+'.json')).write_bytes(output.read_bytes())
output.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
print("Collected {} candidate regression outputs.".format(len(entries)))
