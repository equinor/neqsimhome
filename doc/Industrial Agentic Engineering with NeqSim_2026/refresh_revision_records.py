"""Refresh editorial support records from completed, separately recorded checks."""
from book_runtime import BOOK
import hashlib
import json
from datetime import datetime, timezone


def read(name):
    return json.loads((BOOK / name).read_text(encoding="utf-8"))


def write(name, value):
    (BOOK / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    bibliography = read("verification/bibliography_validation_2026-09-13.json")
    write("verification/bibliography_validation.json", bibliography)
    computation = read("verification/computation_verification_2026-09-13.json")
    java_commands = [c for c in computation["commands"] if c["command"][0] == "mvnw.cmd"]
    assert all(c["exit_code"] == 0 for c in java_commands)
    write("verification/java_quality_gates.json", {"date": "2026-09-13", "source_root": computation["provenance"]["project_root"],
        "source_commit": computation["source_commit"], "status": "passed", "commands": java_commands,
        "scope": "Current checkout compilation, packaging, full Spotless checks and focused four-test book regression suite. Other Java suites were not rerun."})
    renderer = read("verification/renderer_tests_2026-09-13.json")
    write("verification/paperlab_regression_tests.json", {
        "date": "2026-09-13", "status": "passed", "tests_run": renderer["tests"] + bibliography["focused_regression_tests"]["tests"],
        "errors": renderer["errors"], "failures": renderer["failures"], "skipped": renderer["skipped"],
        "evidence": ["verification/renderer_tests_2026-09-13.json", "verification/bibliography_validation_2026-09-13.json"],
        "scope": "Native renderer fixtures and bibliography validation fixtures; the full repository suite was not run."})
    plan = read("agent_workflow_plan.json")
    plan["agents"][0]["skills"] = list(dict.fromkeys(plan["agents"][0]["skills"] + ["imagegen"]))
    plan["agents"][2]["outputs"] = ["verification/computation_verification_2026-09-13.json", "verification/cli_examples_2026-09-13.json", "verification/renderer_tests_2026-09-13.json"]
    plan["agents"][3]["outputs"] = ["verification/repository_claim_review_2026-09-13.md", "verification/bibliography_validation_2026-09-13.json", "references/SOURCES.md", "references/collection_manifest.json"]
    plan["integration"] = {"illustrations": "illustrations/imagegen_manifest_2026-09-13.json", "scientific_traceability": "verification/scientific_traceability_audit.json", "primary_visual_proofs": "verification/visual_review.json", "release": "verification/release_gate_report.json"}
    write("agent_workflow_plan.json", plan)
    manifest = read("verification/render_manifest.json")
    from pathlib import Path
    candidate_html = Path(manifest["candidate"]) / "submission/book.html"
    html = BOOK / "submission/book.html"
    assert candidate_html.read_bytes() == html.read_bytes(), "Browser preview and release HTML differ"
    browser = read("verification/browser_checks.json")
    assert browser["html_sha256"] == hashlib.sha256(html.read_bytes()).hexdigest(), (
        "HTML differs from the separately recorded browser review; perform a new review")
    assert {v["width"] for v in browser["viewports"]} == {500, 768, 1024, 1280}
    # Preserve actual observations and their timestamp. Metadata refresh is not QA.


if __name__ == "__main__":
    main()
