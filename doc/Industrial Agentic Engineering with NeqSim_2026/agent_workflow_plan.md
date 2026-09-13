# PaperLab agents and skills used

User instruction: use the book agents and skills in NeqSim PaperLab.

The coordinating book author and release orchestrator integrated three specialist workstreams: adversarial/learning/conciseness review; scientific traceability and numerical regression; bibliography and EPUB production. Each used the maintained agent definitions and skills recorded in `agent_workflow_plan.json`, with separate file ownership and a shared source/runtime basis.

Source and evidence checks precede rendering. Native `book-check`, `book-evidence-check --strict`, `validate-bib`, source inventory, coverage and conciseness audits provide their implemented checks. Book-local verifiers add claim, equation, Java-test and frozen-baseline checks that the generic commands do not implement. The native `book-build` runs against a frozen candidate with pre-executed notebooks, and `book-render --format epub` supplies the additional format.

The final release gate records current output hashes, visual proofs, unresolved limitations and the resolved review findings. No draft-paper performance figures were imported without supporting evidence.

For the 13 September refresh, the editorial specialist rewrote the practical quick start and document workflow and reviewed all thirteen chapters. The source specialist revised the core/community explanations and future chapter, verified the pinned community snapshot, and repaired bibliography handling. The execution specialist tested the current Java build, frozen numerical results and actual CLI operations, then repaired shared publishing tools with native-render fixtures. The coordinating author generated and inspected fourteen images, integrated the chapter figures, separated image provenance from numerical evidence, and reviewed the final editions.

Useful changes were fed back into PaperLab's writing, bibliography and scientific-traceability skills. They now preserve the selected interpreter and checkout, avoid silently substituting an installed package, validate citations against the configured manuscripts, and distinguish verification of a retained AI illustration from its generation or scientific validation.

The follow-up reused the scientific-traceability specialist to inspect task creation, study settings, result validators, consistency checks and report generation. The coordinator revised Chapters 1 and 7 and the reading path, integrated the two minor wording suggestions, executed four isolated validator checks, and rebuilt and proved the editions. Existing computation was compared with the archived prior release and retained unchanged. Student-readability and traceability guidance now cross-reference the file lifecycle and actual check coverage.

For the subsequent agent-configuration addition, the same specialist reviewed 22 source files and the changed Chapter 1/7 text. The coordinator added the prompt, configuration map, handoff guide and runner settings, checked the YAML excerpt, and repaired the external-task source-path example in the reusable task-solving instructions. The evidence distinguishes source inspection from live-host or runner execution.


## Enterprise and host integration — 13 September 2026

The author extended Chapter 5 using PaperLab book creation/readability skills, a separate PaperLab traceability audit of enterprise source and isolated installer fixtures, and official host documentation through OpenAI Docs and primary vendor pages. See verification/enterprise_agent_source_audit_2026-09-13.json and verification/enterprise_host_documentation_review_2026-09-13.json.
