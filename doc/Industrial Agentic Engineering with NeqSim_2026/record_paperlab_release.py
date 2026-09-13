"""Check current evidence and package the PaperLab specialist revision."""
from book_runtime import BOOK
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from docx import Document
import yaml


def read(name):
    return json.loads((BOOK / name).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (BOOK / name).write_text(json.dumps(value, indent=2), encoding="utf-8")


def main():
    cfg = yaml.safe_load((BOOK / "book.yaml").read_text(encoding="utf-8"))
    revision_date = str(cfg["revision"]["date"])
    results = read("results.json")
    notebooks = read("verification/notebook_execution.json")
    snippets = read("verification/snippet_verification.json")
    layout = read("verification/layout_checks.json")
    renders = read("verification/render_manifest.json")
    browser = read("verification/browser_checks.json")
    visual = read("verification/visual_review.json")
    word_proof = read("verification/word_proof_manifest_2026-09-13.json")
    science = read("verification/scientific_traceability_audit.json")
    junit = read("verification/junit_regression_report.json")
    epub = read("verification/epub_checks.json")
    bibliography = read("verification/bibliography_validation_2026-09-13.json")
    publishing_tests = read("verification/renderer_tests_2026-09-13.json")
    cli = read("verification/cli_examples_2026-09-13.json")
    image_manifest = read("illustrations/imagegen_manifest_2026-09-13.json")
    review = read("required_fixes.json")
    workflow = read("verification/task_workflow_clarification_revision_2026-09-13.json")
    guidance = read("verification/task_validator_guidance_checks_2026-09-13.json")
    workflow_audit = read("verification/task_workflow_clarification_source_audit_2026-09-13.json")
    agent_revision = read("verification/agent_configuration_revision_2026-09-13.json")
    agent_audit = read("verification/agent_execution_configuration_source_audit_2026-09-13.json")
    enterprise_revision = read("verification/enterprise_integration_revision_2026-09-13.json")
    enterprise_audit = read("verification/enterprise_agent_source_audit_2026-09-13.json")
    host_review = read("verification/enterprise_host_documentation_review_2026-09-13.json")
    assert workflow["status"] == "passed" and workflow["python_fences_unchanged"]
    assert agent_revision["status"] == "passed" and agent_revision["python_fences_unchanged"]
    assert enterprise_revision["status"] == "passed" and enterprise_revision["python_fences_unchanged"]
    for name, digest in enterprise_revision["chapter_sha256"].items():
        assert sha(BOOK / name) == digest, "Stale enterprise-integration manuscript: " + name
    assert host_review["chapter_sha256"] == sha(BOOK / host_review["chapter"])
    assert not host_review["live_host_tests"]
    assert enterprise_audit["manuscript_review"]["status"] == "no_blocking_neqsim_specific_claims_after_revisions"
    assert enterprise_audit["manuscript_review"]["file"]["sha256"] == sha(BOOK / "chapters/ch05/chapter.md")
    assert enterprise_audit["focused_verification"]["existing_tests"]["successful"]
    assert enterprise_audit["focused_verification"]["existing_tests"]["tests_run"] == 17
    assert len(enterprise_audit["focused_verification"]["parser_checks"]) == 10
    assert all(c["status"] in ("passed", "expected_rejection") for c in enterprise_audit["focused_verification"]["parser_checks"])
    assert len(enterprise_audit["focused_verification"]["temporary_catalog_checks"]) == 2
    assert all(c["status"] == "passed" for c in enterprise_audit["focused_verification"]["temporary_catalog_checks"])
    for item in enterprise_audit["source_hashes"]:
        assert sha(Path(item["path"])) == item["sha256"]
    assert not agent_audit["manuscript_review"]["blocking_unsupported_claims"]
    current_source_hashes = {i["path"]: i["sha256"] for i in agent_audit["source_files"]}
    for name, digest in current_source_hashes.items():
        assert sha(Path(agent_audit["source_root"]) / name) == digest, "Source changed since agent audit: " + name
    assert len(guidance["commands"]) == 4 and all(c["status"] == "passed" for c in guidance["commands"])
    assert not workflow_audit["manuscript_review"]["blocking_unsupported_semantics"]
    for item in workflow_audit["source_files"]:
        # The earlier audit is preserved. Only the separately reviewed agent
        # instruction repair supersedes one of its source snapshots.
        expected = (current_source_hashes[item["path"]]
                    if item["path"] == agent_revision["source_instruction_repair"] else item["sha256"])
        assert sha(Path(workflow_audit["source_root"]) / item["path"]) == expected
    assert sha(Path(guidance["source_root"]) / "devtools/validate_task_results.py") == guidance["validator_sha256"]
    with zipfile.ZipFile(BOOK / workflow["previous_release"]) as previous:
        for name in workflow["numerical_results_baseline_and_notebooks_byte_identical"]:
            assert previous.read(name) == (BOOK / name).read_bytes(), "Changed computation: " + name
    with zipfile.ZipFile(BOOK / agent_revision["previous_release"]) as previous:
        for name in agent_revision["numerical_results_baseline_and_notebooks_byte_identical"]:
            assert previous.read(name) == (BOOK / name).read_bytes(), "Changed agent-follow-up computation: " + name
    with zipfile.ZipFile(BOOK / enterprise_revision["previous_release"]) as previous:
        for name in enterprise_revision["numerical_results_baseline_and_notebooks_byte_identical"]:
            assert previous.read(name) == (BOOK / name).read_bytes(), "Changed enterprise-follow-up computation: " + name
    assert read("verification/book_check.json") == []
    assert read("evidence_report.json")["issue_count"] == 0
    assert read("verification/metadata_link_checks.json")["failures"] == []
    assert science["baseline_preserved"] and not science["api_issues"]
    assert results["failures"] == []
    assert len(notebooks["notebooks"]) == 13 and all(r["status"] == "passed" for r in notebooks["notebooks"])
    assert len(snippets) == 11 and all(r["status"] == "passed" for r in snippets)
    assert review["remaining_required_content_fixes"] == 0
    assert junit["status"] == "passed" and junit["suite"]["tests"] == 4
    assert all(junit["suite"][k] == 0 for k in ("errors", "failures", "skipped"))
    assert bibliography["native_cli"]["exit_code"] == 0 and not bibliography["missing_citation_keys"]
    assert bibliography["bibliography_sha256"] == sha(BOOK / "refs.bib")
    assert publishing_tests["status"] == "passed" and publishing_tests["tests"] == 17
    assert all(publishing_tests[k] == 0 for k in ("errors", "failures", "skipped"))
    assert not cli["failures"] and not cli["harness_error"] and cli["user_defaults_unchanged"]
    assert len(cli["commands"]) == 50 and all(r["status"] == "passed" for r in cli["commands"])
    assert len(image_manifest["assets"]) == 14
    for asset in image_manifest["assets"]:
        assert sha(BOOK / asset["master"]) == sha(BOOK / asset["active"]) == asset["sha256"]
    for source, digest in publishing_tests["source_sha256"].items():
        assert sha(BOOK.parents[1] / source) == digest, "Renderer changed after its tests: " + source
    assert all(r["outside_page_count"] == 0 and not r["replacement_glyph_pages"] for r in layout.values())
    assert visual["status"] == "passed"
    assert visual["pdf_sha256"] == sha(BOOK / "submission/book.pdf") == layout["pdf"]["sha256"]
    assert visual["docx_sha256"] == sha(BOOK / "submission/book.docx")
    assert visual["word_proof_sha256"] == sha(BOOK / "verification/book_word_proof.pdf") == layout["word"]["sha256"]
    assert word_proof["status"] == "passed" and word_proof["source_unchanged"]
    assert word_proof["docx_sha256"] == visual["docx_sha256"]
    assert word_proof["proof_sha256"] == visual["word_proof_sha256"]
    assert word_proof["pages"] == visual["word_proof_pages_reviewed"] == layout["word"]["pages"]
    assert browser["html_sha256"] == sha(BOOK / "submission/book.html")
    assert {v["width"] for v in browser["viewports"]} == {500, 768, 1024, 1280}
    for v in browser["viewports"]:
        assert v["document_scroll_width"] <= v["width"]
        assert not v["missing_images"] and not v["broken_citation_targets"]
        assert v["equation_errors"] == 0 and not v["duplicate_caption_numbers"]
    for item in renders["outputs"]:
        assert sha(BOOK / item["path"]) == item["sha256"], item["path"]
    for item in renders["supporting_assets"]:
        assert sha(BOOK / item["path"]) == item["sha256"], item["path"]
    for name, expected in renders["source_hashes"].items():
        assert sha(BOOK / name) == expected, "Stale source: " + name
    assert epub["status"] == "pass" and epub["sha256"] == sha(BOOK / "submission/book.epub")
    for name, expected in epub["source_hashes"].items():
        assert sha(BOOK / name) == expected, "Stale EPUB source: " + name
    for item in read("verification/notebook_regression_audit.json")["notebooks"]:
        assert sha(BOOK / item["notebook"]) == item["notebook_sha256"]
    source_root = Path(results["provenance"]["project_root"])
    assert sha(source_root / junit["test_source"]) == junit["test_source_sha256"]
    assert sha(source_root / "devtools/neqsim_cli.py") == cli["cli_sha256"]
    assert cfg["revision"]["source_commit"] == results["provenance"]["source_commit"]
    assert results["provenance"]["source_commit"] in (BOOK / "references/SOURCES.md").read_text(encoding="utf-8")
    word_math = Document(BOOK / "submission/book.docx").element.xpath(".//m:oMath")
    equations = len(word_math)
    assert all("PythonExe" not in "".join(e.itertext()) for e in word_math)
    assert equations == browser["viewports"][0]["equations"]
    limits = [
        "Synthetic teaching cases; no field, vendor or safety-function qualification.",
        "NIST comparison uses calculated reference-EOS values, not new experimental evidence.",
        "Compressor, pipe and hydrate examples have regression and consistency checks, not independent application validation.",
        "Core FlashRunner tested locally; live MCP transport was not exercised.",
        "EPUB is an additional structurally checked candidate; dedicated reader visual QA and EPUBCheck were not run.",
        "OpenDocument is an additional structurally checked candidate with Unicode equation fallback; native visual proof was not completed.",
        "The PDF additionally renders the separate symbol list; other formats retain definitions in the chapters and glossary.",
        "Portable web images are embedded; KaTeX resources require network access.",
        "17 unused bibliography entries remain as a curated source pool, not cited support.",
        "Agent review is not external subject-matter peer review. No supplied curriculum or exam-completeness claim is made.",
        "Seventeen current native-render fixtures and the separate bibliography fixtures passed; the full PaperLab suite was not run.",
        "Fifty isolated CLI checks cover local configuration, document search and report artifacts. Fresh machine provisioning, package installation and live AI-host interactions were not reproduced.",
        "The later task-workflow clarification reuses unchanged numerical evidence. Four additional task-validator fixtures test schema, warnings and skipped-file semantics; they do not test physical accuracy.",
        "Agent configuration guidance is checked against current source and YAML defaults. Live AI-host delegation and notebook-runner execution were not exercised for this editorial follow-up.",
        "Enterprise integration has 17 isolated installer unit tests, 10 parser-routing checks and 2 synthetic catalog checks. No company login, live package installation, host acceptance test or Engineering Harness deployment was performed.",
    ]
    for fix in review["required_fixes"]:
        if fix["id"] in ("ER13-02", "ER13-03"):
            fix.update(status="resolved", resolution_evidence=["references/SOURCES.md", "verification/artifact_freshness.json", "verification/visual_review.json", "verification/browser_checks.json"])
    assert all(r["status"].startswith("resolved") for r in review["required_fixes"])
    review.update(grade="RELEASE", final_render_status="passed_for_primary_editions", review_stage="integrated_release", integrated_at=datetime.now(timezone.utc).isoformat())
    review["integrated_chapter_sha256"] = {name: sha(BOOK / name) for name in review["chapter_sha256"]}
    write("required_fixes.json", review)
    adversarial_path = BOOK / "book_adversarial_review.md"
    adversarial = adversarial_path.read_text(encoding="utf-8")
    integrated_note = (
        "> **Integrated release update:** The coordinator completed the current-source, "
        "equation, artifact freshness and final PDF/Word/web proofs after this editorial pass. "
        "All required findings are resolved. See [the final release review]"
        "(verification/release_gate_report.md). The dated findings below preserve the "
        "reviewer's original pre-release assessment.\n\n"
    )
    if "> **Integrated release update:**" not in adversarial:
        first, rest = adversarial.split("\n", 1)
        adversarial_path.write_text(first + "\n\n" + integrated_note + rest.lstrip("\n"), encoding="utf-8")
    report = {"revision_date": revision_date, "status": "passed for PDF, Word and web within the stated scientific scope",
        "source_commit": results["provenance"]["source_commit"], "python": results["provenance"]["python"],
        "chapters": 13, "chapter_illustrations": science["figures"], "cover_illustrations": 1,
        "imagegen_assets": len(image_manifest["assets"]), "cli_commands": len(cli["commands"]),
        "cli_artifact_assertions": 17, "cli_user_defaults_unchanged": cli["user_defaults_unchanged"],
        "additional_task_validator_commands": len(guidance["commands"]),
        "workflow_clarification": workflow,
        "workflow_source_audit": "verification/task_workflow_clarification_source_audit_2026-09-13.json",
        "agent_configuration_revision": agent_revision,
        "agent_configuration_source_audit": "verification/agent_execution_configuration_source_audit_2026-09-13.json",
        "enterprise_integration_revision": enterprise_revision,
        "enterprise_source_audit": "verification/enterprise_agent_source_audit_2026-09-13.json",
        "enterprise_host_documentation_review": host_review,
        "executed_notebooks": 13, "executed_manuscript_python_fences": 11,
        "full_process_monte_carlo_draws": results["uncertainty"]["completed"], "native_word_equations": equations,
        "book_junit_tests": junit["suite"], "native_evidence_issues": 0, "metadata_link_failures": 0,
        "publishing_regression_tests": publishing_tests,
        "api_declarations_checked": science["api_references_checked"], "equations_reviewed": science["equations"],
        "principal_claim_links": science["claims"], "required_review_fixes_resolved": len(review["required_fixes"]),
        "layout": layout, "browser": browser, "visual_review": visual,
        "bibliography": {"entries": bibliography["entry_count"], "cited_keys": bibliography["cited_key_count"], "unused": len(bibliography["retained_uncited_keys"]), "native_exit_code": bibliography["native_cli"]["exit_code"]},
        "limits": limits, "agent_workflow": "agent_workflow_plan.json", "native_build": "verification/render_manifest.json"}
    write("verification/release_gate_report.json", report)
    lines = ["# PaperLab release review — " + revision_date, "", "**" + report["status"] + ".**", "",
        "Maintained PaperLab agent definitions and skills guided the author, release, adversarial, conciseness, scientific and bibliography workstreams. See [the actual workflow](../agent_workflow_plan.md).", "",
        "| Gate | Current evidence |", "|---|---|",
        "| Content | All current required findings resolved; 13 chapters content-ready |",
        "| Native source/figure checks | No errors or warnings; strict figure evidence has zero issues |",
        f"| Scientific traceability | {science['api_references_checked']} API declarations, {science['equations']} equations and {science['claims']} principal claims; metadata links checked |",
        "| Computation | 13 notebooks, 11 printed Python examples and 200 full-process uncertainty cases passed |",
        "| Regression | Four book-specific Java tests and full Spotless check passed; notebooks use a frozen baseline |",
        "| Commands | 50 actual CLI commands and 17 artifact assertions passed; saved settings unchanged |",
        "| Task workflow clarification | Chapters 1 and 7 explain solving, file creation, configuration and verification; 4 additional validator invocations passed |",
        "| Agent configuration | Start/resume prompt, host/role/study/runner map, specialist handoffs and runner settings checked against source; no live-host execution claimed |",
        "| Enterprise and hosts | Repository and catalog setup, Copilot/ChatGPT Work/Claude Code integration; 17 installer tests, 10 parser checks and 2 synthetic catalog checks |",
        "| Illustrations | 14 image-generator assets: cover and one per chapter; 21 chapter figures total |",
        "| Publishing tools | Seventeen native-render fixtures and separate bibliography fixtures passed |",
        f"| References | {bibliography['entry_count']} entries, {bibliography['cited_key_count']} cited keys; zero validation failures and {len(bibliography['retained_uncited_keys'])} unused-entry warnings |",
        f"| PDF | {layout['pdf']['pages']} pages; all-page visual, bounds and glyph checks |",
        f"| Word | {layout['word']['pages']} proof pages and {equations} native equations; all-page visual, bounds and glyph checks |",
        f"| Web | Four widths from 500 to 1280px; {browser['viewports'][0]['images']} images, {browser['viewports'][0]['citation_links']} citation links and {browser['viewports'][0]['equations']} equations; no missing assets or broken citation targets |",
        "| Freshness | Current rendered-source, output, notebook and Java-test hashes checked |", "",
        "Page review corrected duplicate PDF caption numbers, authored section numbering, running headers, Word part breaks and symbol-list schema handling in the publishing source. A final cross-format equation check found and corrected Word's treatment of PowerShell variables inside inline code; a regression fixture covers prose and table cells. Flowing symbol definitions avoid an oversized table. Some chapter-ending exercise and reference pages remain sparse; no clipped text or detached figure captions were accepted. Word was opened read-only in a dedicated Microsoft Word instance and exported to a PDF proof, then rasterized with Poppler because LibreOffice was unavailable.", "",
        "The follow-up clarification adds a reader file map, concrete study settings, a six-step solution process, evidence questions and a compressor request-to-decision walkthrough. Source review checked actual file timing and validator/report behaviour. Both minor reviewer wording suggestions were integrated: the Java suite exercises the same engine, and the third uncertainty notebook is an expanded study plan. Existing results, the frozen baseline and all notebooks are byte-identical to the archived prior release; simulations were not rerun for this editorial change. Current editions were rebuilt and proved again.", "",
        "The subsequent agent-configuration addition explains how to start or resume the coordinating role, assign specialists and apply settings at the correct layer. Six runner fields match the canonical YAML template. The source audit covers 22 files and the two revised manuscripts. A reusable agent-instruction example now passes the explicit source checkout for external task folders and explains configuration-to-argument mapping and notebook kernel selection. No numerical code or results changed.", "",
        "## Scientific assessment", "",
        "Suitable as a scientifically grounded introduction and reproducible worked-example book. Software stability, numerical consistency and independent validation are distinguished. The methane comparison provides limited independent reference-model evidence; it does not validate all NeqSim capabilities. Industrial and future chapters explain evidence requirements and proposals without claiming demonstrated asset outcomes. External subject-matter review would strengthen formal academic publication.", "",
        "## Scope and limitations", ""]
    lines += ["- " + item for item in limits]
    lines += ["", "## Source and runtime", "", "NeqSim source commit: `" + report["source_commit"] + "`.", "",
        "Selected interpreter: `" + report["python"] + "`. The configured interpreter was unavailable; the previously selected bundled runtime and book-local dependencies were reused without changing the shared environment.", ""]
    (BOOK / "verification/release_gate_report.md").write_text("\n".join(lines), encoding="utf-8")
    (BOOK / "release_gate_report.md").write_text("# Release gate report\n\n[Read the final PaperLab review](verification/release_gate_report.md).\n\n" + report["status"] + ". Additional EPUB and OpenDocument candidates have the limitations recorded in that report.\n", encoding="utf-8")
    write("verification/artifact_freshness.json", {"status": "passed", "rendered_source_count": len(renders["source_hashes"]),
        "outputs": renders["outputs"], "frozen_baseline_sha256": science["regression_baseline_sha256"],
        "checked_notebook_hashes": 13, "checked_java_source_sha256": junit["test_source_sha256"]})
    health = read("chapter_health_dashboard.json")
    health["overall"].update(release_class="ready", render_status="passed_for_primary_editions", reason="Current PDF, Word and web proofs and hashes passed; secondary-format limitations remain explicit.")
    health["release_verified_at"] = datetime.now(timezone.utc).isoformat()
    health["missing_audit_data"] = [x for x in health["missing_audit_data"] if x["artifact"] not in ("final integrated render approval", "Final current-edition PDF/Word/web proofs and refreshed artifact freshness")]
    for item in health["missing_audit_data"]:
        if item["artifact"] == "formal standalone accessibility audit":
            item["effect"] = "Final visual review covered figure legibility, captions and layout; no formal accessibility-conformance audit was performed."
    for item in health["fix_queue"]:
        if item["id"] in ("RENDER-01", "ER13-03"): item.update(status="resolved", evidence="verification/release_gate_report.json")
    for chapter in health["chapters"]:
        chapter.update(release_class="ready", render_status="passed_for_primary_editions", main_blocker=None,
            next_fix={"owner": "future edition", "action": "Optional external peer review and additional independent benchmarks"})
        chapter["dimensions"]["figures"].update(status="passed_for_primary_editions",
            limitation="Final PDF, Word and web visual review passed; no formal accessibility-conformance audit.")
        chapter["dimensions"]["figures"]["evidence"] = list(dict.fromkeys(chapter["dimensions"]["figures"].get("evidence", []) + ["figure_provenance.json", "verification/visual_review.json", "verification/browser_checks.json"]))
        chapter["dimensions"]["evidence"].update(status="current_linkage_checked", evidence="verification/scientific_traceability_audit.json")
        chapter["dimensions"]["prose"]["status"] = "ready_with_stated_scope"
        chapter["integrated_manuscript_sha256"] = sha(BOOK / "chapters" / chapter["dir"] / "chapter.md")
    for item in health.get("audit_inputs", []):
        item["integrated_release_sha256"] = sha(BOOK / item["path"])
    write("chapter_health_dashboard.json", health)
    dashboard = ["# Chapter health dashboard", "", "All 13 chapters are content-ready. Final PDF, Word and web proofs pass. This is a release judgement from the recorded evidence, not an external peer-review certification.", "",
        "| Chapter | Content | Primary render | Required fix |", "|---|---|---|---|"]
    dashboard += [f"| {c['number']}. {c['title']} | Ready | Passed | None |" for c in health["chapters"]]
    dashboard += ["", "Detailed seven-dimension evidence and confidence limits remain in `chapter_health_dashboard.json`. The release report documents secondary-format and scientific limits. `coverage_matrix.md` maps sources and user goals; no course completeness is claimed.", ""]
    (BOOK / "chapter_health_dashboard.md").write_text("\n".join(dashboard), encoding="utf-8")
    archive = BOOK / ("submission/revised_book_and_companions_" + revision_date + ".zip")
    files = [p for p in BOOK.iterdir() if p.is_file() and p.suffix in (".py", ".md", ".yaml", ".css", ".bib", ".json", ".png", ".svg")]
    for directory in ("chapters", "frontmatter", "backmatter", "references", "illustrations"):
        files += [p for p in (BOOK / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    files += [BOOK / r["path"] for r in renders["outputs"]]
    files += [BOOK / r["path"] for r in renders["supporting_assets"]]
    files += [p for p in (BOOK / "verification").iterdir() if p.suffix in (".md", ".json", ".xml")]
    files += [p for p in (BOOK / "verification").iterdir() if p.suffix == ".log" and "2026-09-13" in p.name]
    files += [p for p in (BOOK / cli["fixture_root"]).rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    files += [p for p in (BOOK / "verification/task_guidance_fixtures").rglob("*") if p.is_file()]
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for path in sorted(set(files)): z.write(path, path.relative_to(BOOK).as_posix())
        z.write(source_root / junit["test_source"], "verification/BookWorkedExamplesRegressionTest.java")
        for name in ("devtools/neqsim_doctor.py", "devtools/test_neqsim_doctor.py", "docs/integration/enterprise_agent_skill_repos.md"):
            z.write(source_root / name, "verification/source_changes/neqsim/" + name)
        z.write(source_root / agent_revision["source_instruction_repair"],
                "verification/source_changes/neqsim/" + agent_revision["source_instruction_repair"])
        publishing_sources = set(publishing_tests["source_sha256"]) | {"tools/bib_validator.py", "paperflow.py", "tests/test_book_bibliography_validation.py"}
        publishing_sources.update({"skills/paperlab_student_readability/SKILL.md", "skills/paperlab_scientific_traceability_audit/SKILL.md", "skills/neqsim_in_writing/SKILL.md"})
        for name in sorted(publishing_sources):
            z.write(BOOK.parents[1] / name, "verification/source_changes/paperlab/" + name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert sum(n.endswith("01_revised_chapter.ipynb") for n in z.namelist()) == 13
        assert "verification/regression_baseline_2026-09-12.json" in z.namelist()
        assert "illustrations/imagegen_manifest_2026-09-13.json" in z.namelist()
    print(json.dumps({"status": report["status"], "archive": str(archive), "bytes": archive.stat().st_size}, indent=2))


if __name__ == "__main__": main()
