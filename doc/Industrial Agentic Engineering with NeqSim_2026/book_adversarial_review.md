# Editorial and adversarial review — 13 September 2026

> **Integrated release update:** The coordinator completed the current-source, equation, artifact freshness and final PDF/Word/web proofs after this editorial pass. All required findings are resolved. See [the final release review](verification/release_gate_report.md). The dated findings below preserve the reviewer's original pre-release assessment.

Recorded: 2026-09-13T13:50:54.763875+00:00

**Content: ready within the stated teaching scope. Grade: MINOR REVISION until current-edition release gates are closed. Final rendered release: pending root proofs.**

All 13 chapters were read using PaperLab's author/adversarial roles and student-readability/chapter-flow skills. The original edition supplied style and reader-journey inspiration only. This pass reviewed current code and evidence; it did not edit chapters or inspect final rendered editions.

The authoritative source is `9a95440e194a6fdc2890e4efafff647711beedce` under `C:\Users\solbraa\OneDrive - NTNU\Documents\GitHub\neqsim`. The diagnostic correction is a local change after that commit, identified by file hashes in its verification record.

## Findings and release boundary

| Finding | State | Required action |
|---|---|---|
| ER13-01: The new conceptual discussion used measured-state labels for a comparison that uses NIST reference-model values. | resolved | Use specified-state or evaluated-state labels; preserve the explicit distinction from measurements. |
| ER13-02: The Sep12 source index cannot identify the newly reviewed Sep13 checkout by itself. | resolved | Identify the current source commit and locally changed diagnostic files, retaining old reference retrieval and regression baseline dates as history. |
| ER13-03: Sep12 figure/API/claim and rendered-artifact passes do not certify the integrated Sep13 text, source and illustrations. | pending_root_proofs | Refresh native evidence and figure dossiers, current snippet/claim links and artifact hashes; render and inspect final editions before marking release passed. |
| ER13-04: JAR selection used the first glob result, reporting a stale old shaded artifact after a successful current package build. | resolved | Prefer current POM-version runtime artifacts, then modification time. Implemented with regression coverage and actual CLI verification. |
| ER13-05: The model-family orientation omitted current GERG model-selection paths and EOS-CG. | resolved | Short orientation integrated; source-linked derivative and validation limitations inspected against both Java commonInitialization methods. |

The GERG/EOS-CG orientation is now present. Its derivative limitation matches the inspected Java classes. Older skills' blanket density-accuracy or custody-transfer recommendations were not imported.

No current CLI contradiction was found across Chapters 1, 5, 6, 7, 8 and 12. The manuscript distinguishes package discovery/installation from execution, agent run guidance from an autonomous run, literal relative-path document search from extraction, the task parent from the active task and source checkout, and report styling from review status. It accurately describes title-derived report filenames and preserved work-record narratives.

## Current checks and retained evidence

- Fresh native book-check: 0 issues. Native status: 13 chapters, 21 figures, 13 notebooks and 0 TODOs.
- The current manuscript contains 13 labelled AI-generated chapter illustrations. Scientific curves retain computational evidence; the future chapter's illustration is a conceptual map of cooperating capabilities around human review, not a maturity score or sequence assigned to NeqSim.
- Native conciseness functions: 0 exact duplicate paragraph groups, 0 near-duplicate pairs and 0 duplicate figure groups. The status count (23,658 words) and conciseness count (22,079) use different source-processing rules; neither is a measured page count.
- Current CLI evidence: 50 real commands and 17 artifact assertions, 0 failures, user defaults unchanged. The doctor-specific follow-up adds seven scenarios and 15 assertions with an actual successful CLI run.
- Current computation record: 3,353 historical baseline leaves compared without drift, 4 focused Java tests with no failures, and 200 full-process Monte Carlo cases completed. These records were inspected, not rerun by this editorial pass.
- Current native bibliography record: exit 0, 53 entries, no missing citation keys. Its 17 uncited entries are warnings for review, not unresolved citations.
- The diagnostic regression is a genuine workflow improvement: a fresh package is now selected ahead of old leftover JARs. pytest was unavailable; the selected-runtime stdlib checks and real command passed without installs. The earlier missing-runtime-support diagnostic was preserved in a separate log.

## Chapter review

| Chapter | Teaching arc and strongest asset | Reader friction / action |
|---|---|---|
| 1: Getting Started | Setup to a recorded methane calculation. Explicit interpreter, PowerShell steps, host prompt and script/notebook routes make the first session actionable. | Separate the quick property task from the Standard process study introduced in Chapter 7. Keep the source/bootstrap and units explicit; no further structural edit. |
| 2: What Agentic Engineering Changes | Decision chain to evidence and review. The five evidence claims distinguish execution, implementation, plausibility, validation and acceptance. | EOS and PVT are compact terms; glossary support is useful before Chapter 3. Keep the repeated evidence reminders where later applications need them. |
| 3: The NeqSim Physics Engine | Physical basis to current numerical interfaces. Cubic equations, flash balance, phase properties and process construction build on a short prerequisite bridge. | The interface and model-family survey is orientation depth, not a tested example of every capability. The integrated GERG H2/NH3 and EOS-CG paragraph matches current source limitations; keep it separate from Chapter 9's exercised SRK/PR comparison. |
| 4: How Agents Use Skills and Tools | Observable tool cycle to durable handoffs. The illustrative YAML is explicitly distinguished from an executable runner schema. | Host skill discovery and NeqSim package discovery must remain separate. Current host/context/absolute-path additions preserve that boundary; no rewrite needed. |
| 5: Agents and Repositories | Repository ownership to discovery and composition. Canonical source, installation and export are distinguished with current identifiers and real package dependencies. | Commands span source and community catalogs; readers must inspect their chosen host and package. Keep installation distinct from execution, including agent run as launch guidance only. |
| 6: Building and Maintaining Skills | Method ownership to verification and maintenance. A compact fluid example and failure table connect metadata to actual engineering behaviour. | The sample verification date is illustrative; it must never be updated as an unearned assurance. Keep instruction dependencies separate from packages, tools and private access. |
| 7: The Task Solving Workflow | Scope and configuration to evidence and report. Separate roots, literal document patterns, intake policy, complete study configuration and title-derived output names give a usable workflow. | This is a Standard study contract; its full notebooks and uncertainty requirements should not be inferred for every quick query. The chapter already states adaptive scope and labels schema fragments; retain these explanations. |
| 8: MCP and Governed Calculation Services | Protocol to typed calculation and deployment. The two JSON shapes expose the adapter boundary between local FlashRunner and MCP tool arguments. | The book does not exercise a live MCP session or certify a deployment. Keep local runner evidence and service/permission tests as different checks. |
| 9: Thermodynamic Property Calculations | Controlled methane comparison to application limits. Matching NIST reference states, deviations and an ideal-gas limit teach three distinct checks. | Reference-model values are not new experimental measurements; decorative curves have no numerical meaning. Retain that distinction in both the new conceptual illustration discussion and the numerical figures. |
| 10: Process Simulation and Equipment Design | Gas-train basis to balance, sensitivity and qualification. The complete enthalpy balance explains why cooling duty exceeds compressor power, followed by an explicit physical estimate. | The efficiency and uncertainty distributions are teaching assumptions; no vendor operating window is supplied. Keep the exact schematic and numerical plots separate from the new conceptual scene; retain all material outlets. |
| 11: Flow Assurance and Pipeline Studies | Route basis to hydraulics and wet-fluid screening. The pipe reconstructs the original dry feed, compares diameter and refinement, then declares a separate wet hydrate basis. | Horizontal isothermal calculations cannot establish arrival temperature, cooldown or hydrate operating safety. The new illustration discussion states this boundary; no case-continuity repair remains. |
| 12: From Teaching Cases to Industrial Studies | Teaching evidence to industrial qualification. Study patterns, document intelligence, data quality and recipient-tool qualification explain what an asset study adds. | A catalog workflow does not provide OCR services, private data, software licences or approval by itself. Preserve concrete evidence and review requirements instead of expanding with unsupported named-asset claims. |
| 13: The Future of Agentic Engineering | Observable present to testable future directions. The proposed-improvement table ties future autonomy to dependency, recovery, evaluation and qualification evidence. | A coordinator manifest is evidence of intended cooperation, not demonstrated end-to-end deployment. Keep Chapter 13 separate from Chapter 12: this chapter is an outlook, while Chapter 12 describes present industrial study practice. |

No chapter merge, split or reorder is needed. Chapters 12 and 13 answer different questions: present industrial qualification and proposed future developments. Repeated units, evidence and ownership reminders are useful where the application changes; no duplicate-text removal is indicated.

## Scientific and review limitations

- Current computation is regression and execution evidence. The independent reference comparison covers pure methane at one temperature and five pressures; NIST supplies reference-model values, not new measurements.
- Pipe refinement and compressor mass/energy closure are numerical checks. No independent field hydraulic, hydrate or vendor compressor validation was added.
- The 200-draw full-process uncertainty example propagates declared independent teaching distributions; it is not an asset uncertainty model or a tail-convergence guarantee.
- GERG/EOS-CG discussion is source-grounded model orientation. Positive finite results and model selection do not establish custody-transfer accuracy or a published validity range.
- Local FlashRunner execution does not test live MCP transport. Catalog/source inspection does not demonstrate private integrations, commercial-engine access or industrial approval.
- This reviewer inspected prose, source and retained execution records, not final rendered pages. Root visual and package proofs remain pending.
- pytest was unavailable in the selected interpreter and existing book-local dependencies. Doctor-specific stdlib assertions and actual CLI passed; repository pytest regressions were added but not run with pytest here.

Native coverage lists no supplied lecture, exam or exercise-document sources. It is not a course-completeness score. Source-to-chapter and user-goal coverage are recorded in coverage_matrix.md; external syllabus alignment would require a specified course and assessment basis.

Review snapshot hashes, per-chapter observations and evidence paths are retained in verification/editorial_review_2026-09-13.json. Subsequent substantive manuscript changes require a focused re-review; root proofs remain an explicit gate.

## Task-workflow follow-up

The added guidance in Chapters 1 and 7 received a separate source and evidence review in [the dated workflow audit](verification/task_workflow_clarification_source_audit_2026-09-13.md). Its two minor wording suggestions were integrated. The original findings above remain historical; current output proofs and verification scope are recorded in the release report.

The subsequent agent-configuration additions received a separate [source and manuscript audit](verification/agent_execution_configuration_source_audit_2026-09-13.md) with no blocking concerns. Current proofs cover those additions; no live-agent performance claim was added.


## Enterprise and host integration — 13 September 2026

Enterprise and host-integration follow-up reviewed separately in verification/enterprise_agent_source_audit_2026-09-13.json. Host instructions are documentation-checked, not live-deployment evidence; prior numerical qualification limits remain.
