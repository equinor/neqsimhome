"""Check the documented task-validator semantics using isolated schema fixtures."""
from book_runtime import BOOK
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()
    source = Path(args.project_root).resolve()
    validator = source / "devtools/validate_task_results.py"
    root = BOOK / "verification/task_guidance_fixtures"
    for name in ("schema_valid_acceptance_false", "missing_results", "invalid_schema"):
        (root / name).mkdir(parents=True, exist_ok=True)
    fixture = {
        "key_results": {"schema_fixture_value": 1.0},
        "validation": {"acceptance_criteria_met": False},
        "approach": "Schema fixture only; no simulation was executed.",
        "conclusions": "The acceptance criterion has not passed.",
    }
    (root / "schema_valid_acceptance_false/results.json").write_text(json.dumps(fixture), encoding="utf-8")
    (root / "invalid_schema/results.json").write_text('{"key_results": {}}', encoding="utf-8")
    cases = [
        ("schema_valid_acceptance_false", [], 0, "1 file(s) checked, 0 error(s)"),
        ("schema_valid_acceptance_false", ["--strict-warnings"], 1, "warning(s)"),
        ("missing_results", [], 0, "No results.json files found"),
        ("invalid_schema", [], 1, "ERROR"),
    ]
    records = []
    for name, options, expected_code, expected_text in cases:
        command = [sys.executable, "-X", "utf8", str(validator), str(root / name)] + options
        run = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        record = {"fixture": name, "command": command, "exit_code": run.returncode,
                  "stdout": run.stdout, "stderr": run.stderr,
                  "status": "passed" if run.returncode == expected_code and expected_text in run.stdout else "failed"}
        records.append(record)
    report = {"recorded_at": datetime.now(timezone.utc).isoformat(), "python": sys.executable,
              "source_root": str(source), "validator_sha256": hashlib.sha256(validator.read_bytes()).hexdigest(),
              "scope": "Four actual task-validator invocations against synthetic structure fixtures; no engineering computation or shared-setting change.",
              "commands": records, "status": "passed" if all(r["status"] == "passed" for r in records) else "failed"}
    (BOOK / "verification/task_validator_guidance_checks_2026-09-13.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    assert report["status"] == "passed", "Task-validator behaviour differs from the chapter explanation"
    print("Four task-validator checks passed, including skipped input and acceptance-false cases.")


if __name__ == "__main__":
    main()
