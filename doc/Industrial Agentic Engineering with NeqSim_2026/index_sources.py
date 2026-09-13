"""Build a distributable guide to the public evidence used in this revision."""
from book_runtime import BOOK
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(BOOK.parents[1] / "tools"))
from citation_utils import collect_cited_keys, clean_bibtex_latex
from bib_validator import _parse_entries, resolve_validation_inputs


def reference_origin(fields):
    """Preserve DOI links and legacy BibTeX howpublished URL conventions."""
    if fields.get("url"):
        return fields["url"]
    if fields.get("doi"):
        return "https://doi.org/" + fields["doi"]
    match = re.search(r"https?://[^}\s]+", fields.get("howpublished", ""))
    return match.group(0) if match else "See refs.bib"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    config = yaml.safe_load((BOOK / "book.yaml").read_text(encoding="utf-8"))
    revision = config["revision"]
    edition_date = str(revision["date"])
    if commit != revision["source_commit"]:
        raise ValueError("Selected source checkout does not match book.yaml revision.source_commit")
    records = []
    sources = {
        "docs/integration/skills_guide.md": "Core discovery, installation and host exports",
        "docs/integration/enterprise_agent_skill_repos.md": "Private catalogs, trust and repository boundaries",
        "docs/integration/agent_skill_catalog_schema.md": "Enterprise catalog and package metadata contract",
        "docs/integration/mcp_neqsim_core_layer.md": "Transport-independent runners and calculation contracts",
        "docs/engineering/dexpi-guide.md": "Plant/Process exchange and qualification boundaries",
        ".github/agents/capability.scout.agent.md": "Capability assessment responsibilities",
        ".github/agents/process.model.agent.md": "Process specialist workflow and dependencies",
        ".github/agents/router.agent.md": "Routing and specialist selection",
        "devtools/neqsim_dev_setup.py": "Explicit workspace class loading",
        "devtools/agent_search.py": "Agent discovery across catalogs",
        "devtools/skill_search.py": "Skill discovery across catalogs",
        "devtools/neqsim_cli.py": "Current commands, task/document defaults and canonical report dispatch",
        "devtools/new_task.py": "Task and document-root precedence, document discovery and task creation",
        "devtools/neqsim_doctor.py": "Environment diagnostics and explicit repair options",
        "devtools/task_template/step3_report/generate_report.py": "Canonical report generation and Word-template selection",
        "devtools/generate_work_record.py": "Method and provenance companion generated from task artifacts",
        "devtools/validate_task_results.py": "Task result structure, warning/error/skip semantics and evidence-field checks",
        "devtools/consistency_checker.py": "Implemented scope and limitations of cross-document consistency screening",
        "devtools/install_agent.py": "Canonical agent installation, skill dependencies and host exports",
        "devtools/install_skill.py": "Canonical skill installation and optional executable dependencies",
        ".github/agents/solve.task.agent.md": "Task coordinator, study configuration and specialist handoffs",
        "devtools/task_template/study_config.yaml": "Study depth, data sources, document root, execution and report contract",
        "devtools/neqsim_runner/agent_bridge.py": "Explicit task/source handoff, notebook modes, job submission and result collection",
        "devtools/neqsim_runner/cli.py": "Calculation job commands and CLI status semantics",
        "devtools/neqsim_runner/supervisor.py": "Worker supervision, attempt limits and parallel execution",
        "devtools/neqsim_runner/worker.py": "Worker interpreter, source bootstrap and recorded job completion",
        "docs/development/TASK_SOLVING_GUIDE.md": "Reader workflow for current task locations, templates and reporting",
        "docs/integration/paperlab_vscode_install.md": "PaperLab gateway and public/internal export policy",
        "docs/thermo/gerg2008_eoscg.md": "GERG/EOS-CG interfaces and mixture-specific validation boundaries",
        "community-agents.yaml": "Core pointer to the public community-agent package catalog",
        "pom.xml": "Source build and project version",
    }
    classes = {
        "ProcessAutomation.java": "String-addressable process variables and diagnostics",
        "ProcessSystemState.java": "Saved process lifecycle state",
        "EnergyNetworkSolver.java": "Explicit energy network solution",
        "PipingRouteBuilder.java": "Route-based hydraulic construction",
        "EngineeringDeliverableCompiler.java": "Engineering evidence and deliverable compilation",
        "FlashRunner.java": "Executable core flash request contract",
        "PipeBeggsAndBrills.java": "Pipe geometry, increments and thermal mode",
        "SeparatorMechanicalDesign.java": "Physical separator design and configuration",
        "TaskResultValidator.java": "Java result-schema validation and issue severity semantics",
        "SimulationQualityGate.java": "Advisory simulation checks and limits of generic balance diagnostics",
    }
    for name, purpose in classes.items():
        matches = list((root / "src/main/java").rglob(name))
        if len(matches) != 1:
            raise ValueError("Expected one source for {}: {}".format(name, matches))
        sources[matches[0].relative_to(root).as_posix()] = purpose
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--", *sources], cwd=root, text=True)
    modified = {line[3:].replace("\\", "/") for line in status.splitlines() if line}
    for relative, purpose in sources.items():
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        records.append({"kind": "source snapshot", "file": relative, "origin":
                        "https://github.com/equinor/neqsim/blob/" + commit + "/" + relative,
                        "revision": commit, "reviewed": edition_date, "classification": "public source",
                        "summary": purpose, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "working_tree_modified": relative in modified,
                        "review_status": ("Inspected local working copy; linked commit is the baseline, and application validation is separate"
                                          if relative in modified else
                                          "Inspected for interface or workflow; application validation is separate")})
    community_path = BOOK / "references/web/community_agents_2026-09-13/source_manifest.json"
    community = json.loads(community_path.read_text(encoding="utf-8"))
    community_purposes = {
        "README.md": "Public package organisation, contribution and host integration overview",
        "community-agents.yaml": "Actual public agent catalog and declared dependencies",
        "docs/agent-catalog.md": "Human-readable catalog guide; package contents take precedence over stale counts",
        "agents/tie-in-screening-agent/agent.yaml": "Exact tie-in dependency identifiers and review requirement",
        "agents/tie-in-screening-agent/AGENT.md": "Tie-in screening workflow and limitations",
        "agents/flow-assurance-study-agent/agent.yaml": "Coordinator, optional context and specialist composition",
        "agents/technical-document-intelligence-agent/AGENT.md": "Document inventory, extraction choices and evidence records",
    }
    for item in community["files"]:
        local_path = BOOK / item["path"]
        digest = hashlib.sha256(local_path.read_bytes()).hexdigest()
        if digest != item["sha256"]:
            raise ValueError("Retained community source changed: " + str(local_path))
        records.append({"kind": "community source snapshot", "file": item["source_path"],
                        "local_file": local_path.relative_to(BOOK).as_posix(),
                        "origin": item["url"], "revision": community["commit"],
                        "retrieved": community["retrieval_date"], "reviewed": edition_date,
                        "classification": "public source", "sha256": digest,
                        "summary": community_purposes[item["source_path"]],
                        "review_status": "Inspected package contract; installation or end-to-end execution is not implied"})
    bib_path, manuscript_paths = resolve_validation_inputs(BOOK)
    bib = {entry["ID"]: entry for entry in _parse_entries(bib_path.read_text(encoding="utf-8"))}
    keys = []
    for p in manuscript_paths:
        for key in collect_cited_keys(p.read_text(encoding="utf-8")):
            if key not in keys:
                keys.append(key)
    for key in keys:
        fields = bib[key]
        records.append({"kind": "bibliographic reference", "id": key,
                        "origin": reference_origin(fields),
                        "summary": clean_bibtex_latex(fields.get("title", "")),
                        "review_status": "Primary software/protocol sources checked; established literature retained for method attribution",
                        "classification": "public reference", "year": fields.get("year")})
    records.append({"kind": "reader journey reference", "id": "original_published_book",
                    "origin": "https://equinor.github.io/neqsimhome/doc/agentic%20engineering/book.html",
                    "reviewed": edition_date, "classification": "public reference",
                    "summary": "Original published book's getting-started journey and local/cloud entry points",
                    "review_status": "Consulted for reader continuity; not evidence that old commands or scientific claims remain current"})
    nist = json.loads((BOOK / "references/nist/source.json").read_text(encoding="utf-8"))
    records.append(dict(nist, kind="retrieved dataset", review_status="Matched by temperature and pressure; duplicate-state consistency checked"))
    manifest = {"edition_date": edition_date, "source_commit": commit,
                "source_root": str(root), "community_commit": community["commit"],
                "community_local_clone_found": community["local_clone_found"], "sources": records,
                "data_gaps": ["No proprietary asset or vendor data supplied.",
                              "Pipe and hydrate demonstrations have no independent application-specific reference dataset.",
                              "MCP transport was documented; execution verification covers the core FlashRunner only.",
                              "NIST values are calculated reference-EOS properties, not new experimental measurements.",
                              "Community agent definitions and dependencies were inspected; a complete cross-host agent study was not executed.",
                              "AI-generated conceptual illustrations support explanation; image provenance or hash checks do not validate scientific claims."]}
    (BOOK / "references/collection_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    lines = ["# Sources for the September 2026 revision", "", "This index distinguishes inspected software, method references, and downloaded data. The book's bibliography contains the cited literature; this guide makes the source snapshot and its limits explicit.", "",
             "Edition review date: **" + edition_date + "**. Source snapshot: `" + commit + "`. Public release baseline: **" + str(revision["neqsim_release"]) + "**, released 8 September 2026. Source-snapshot functionality may be newer than that release. Local edits, where present, are explicitly identified and hashed.", "", "## Inspected source files", ""]
    for r in records:
        if r["kind"] == "source snapshot":
            qualifier = " Local working copy differs from the linked commit; see its digest in the manifest." if r["working_tree_modified"] else ""
            lines.extend(["- [" + r["file"] + "](" + r["origin"] + ") — " + r["summary"] + ". Inspected " + edition_date + "; public source." + qualifier])
    lines.extend(["", "## Retained community-agent source snapshot", "",
                  "Public repository revision `" + community["commit"] + "`, retrieved " + community["retrieval_date"] + ". No separate community clone was found in the searched local project/user areas; retained pinned files provide the inspected evidence.", ""])
    for r in records:
        if r["kind"] == "community source snapshot":
            local_link = Path(r["local_file"]).relative_to("references").as_posix()
            lines.append("- [" + r["file"] + "](" + r["origin"] + ") — " + r["summary"] + ". [Retained copy](" + local_link + ").")
    lines.extend(["", "## Original reader journey", "",
                  "The [original published book](https://equinor.github.io/neqsimhome/doc/agentic%20engineering/book.html) was consulted on " + edition_date + " for the getting-started journey and local/cloud entry points. Its earlier commands, capability counts and scientific claims are not treated as current validation evidence."])
    lines.extend(["", "## Method and online references", ""])
    for r in records:
        if r["kind"] == "bibliographic reference":
            origin = r["origin"]
            label = "[" + r["summary"] + "](" + origin + ")" if origin.startswith("http") else r["summary"]
            lines.append("- `" + r["id"] + "`: " + label + " (" + str(r["year"]) + ").")
    lines.extend(["", "## Downloaded reference data", "", "- [Methane at 298.15 K](nist/methane_298_15K.tsv): NIST Chemistry WebBook calculated reference-fluid properties at 1, 51, 101, 151 and 201 bara. Retrieved 12 September 2026. [Exact request and digest](nist/source.json). Used for the Chapter 9 SRK/PR comparison; not new measurements.", "", "## Data gaps and review limits", ""])
    lines.extend("- " + gap for gap in manifest["data_gaps"])
    lines.extend(["", "File-level SHA-256 digests and origins are in `collection_manifest.json`. Original supplied manuscript material is retained in the revision archive. No confidential enterprise catalog or asset data is reproduced.", ""])
    (BOOK / "references/SOURCES.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__": main()
