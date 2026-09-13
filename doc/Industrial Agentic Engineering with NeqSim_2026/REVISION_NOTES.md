# Revision of 13 September 2026

## Current-source refresh

The book uses the local NeqSim 3.20.0 source snapshot `9a95440e194a6fdc2890e4efafff647711beedce` from 13 September 2026. Chapter 1 follows the original edition's command-led reader journey: prepare a checkout, select Python, check the installation, create a task and run a methane calculation. Chapter 7 distinguishes task destinations, document libraries, task intake configuration and Word templates, including precedence, missing-template behaviour, report filenames and work records.

Chapters 4–8 explain current core and community agent packaging, skill dependencies, host exports, installation and execution boundaries. Community claims are pinned to `0ca1428a5dbd9425bace430c64a7b1bd6556b25d`; no local community checkout was found. Chapter 3 adds an orientation to GERG model selection and EOS-CG. Chapters 12–13 describe industrial evidence requirements and proposed future capabilities without presenting proposals as demonstrated outcomes.

## Writing and scientific quality

All thirteen chapters follow a progression from the physical question to executable calculation, evidence and engineering review. Learning objectives, reading paths, connected examples, exercises, a glossary and a reproducibility appendix support the reader. Unsupported field-success claims, general productivity percentages and claims of an already-realised speculative future were removed.

The running case is a declared synthetic methane/ethane/propane gas at 10,000 kg/h. This resolves the earlier draft's incompatible 50 MMSCFD and MSm3/day basis. The process chapter includes a complete train energy balance and an ideal-gas temperature estimate. The pipe calculation constructs a fresh fluid at the original feed state. Predictions, regression checks, physical consistency and independent validation are distinguished.

The methane comparison uses calculated NIST reference-EOS values, not new measurements. Compressor, pipeline and hydrate examples remain teaching demonstrations without independent application-specific validation. Neither field equipment nor live MCP transport was qualified. Agent review does not constitute external scientific peer review.

## Illustrations and editions

Fourteen newly generated image assets provide a matching cover and one conceptual illustration per chapter. The 21 chapter figures comprise 13 AI illustrations, six numerical charts and two code-native diagrams. Full prompts, unchanged masters, hashes and semantic limits are retained in the illustration manifest. Numerical figures come from recorded simulations; artwork does not count as validation evidence.

The B5 PDF, editable Word and responsive web editions have fresh proofs. Shared PaperLab renderer fixes preserve authored section numbers, explicit trim, chapter-scoped images, literal shell variables, citations, native Word equations, chapter figure numbering, symbol definitions and backmatter. Word receives the generated cover and corrected part breaks; table headers stay with the first data row and repeat across pages. Twelve focused renderer fixtures exercise native output, including literal PowerShell variables in Word prose and tables and long-table pagination; six bibliography fixtures cover separate validation behaviour. Final page counts and visual findings are recorded in `verification/release_gate_report.md`.

EPUB has structural, image, link, chapter and MathML checks; a dedicated reader review and EPUBCheck remain outside this pass. OpenDocument retains its Unicode equation fallback and limited visual-proof status.

## Execution evidence

All 13 notebooks and 11 exact Python manuscript fragments ran against the current checkout. The numerical suite includes SRK/PR methane properties at five reference-matched states, compressor performance and pressure sensitivity, automation access, saved-state JSON, a core flash runner, pipe diameter and increment sensitivities, wet-gas hydrate examples, and 200 full NeqSim process Monte Carlo draws. All 3,353 originally recorded basis/output leaves match the frozen Sep12 baseline; that baseline was not replaced.

Fifty actual CLI commands and 17 artifact assertions cover configuration, document search, tasks and report generation in an isolated workspace. Saved user settings were unchanged. Four book-specific Java regression tests and the full formatting check passed. A diagnostic defect found during setup was fixed: `neqsim doctor` now selects the current POM-version JAR instead of the first filesystem glob match. Seven focused scenarios and 15 assertions cover selection.

## Reusable improvements and preservation

PaperLab's book agents and skills guided the work. Writing and scientific-traceability skills now preserve the selected interpreter and source checkout, avoid a silent installed-package fallback, validate citations against the configured manuscripts, and separate retained AI-asset verification from generation and physical validation. Bibliography handling supports the installed parser API and existing URL conventions.

The original and completed Sep12 revision remain in dated archives. Replaced illustrations are archived. No changes were pushed or published. Production Java was not changed; the book-specific regression class was added to the current source checkout. The configured default Python was unavailable, so the previously selected bundled interpreter and book-local dependencies were reused. Source, runtime and output hashes are retained in the verification manifests.

The Sep12 edition had 104 PDF pages and 90 Word proof pages. Those historical counts do not describe this revision; consult the current release report.

## Follow-up: solving tasks, files, settings and evidence

Chapter 1 section 1.10 introduces the path from a request to recorded inputs, executable calculation and evidence. Chapter 7 sections 7.3-7.7 explain study settings, the files created at each stage, six steps of task solving and the distinct questions a verification process must answer. Section 7.12 follows the recorded compressor result from request through explicit checks to a qualified conclusion.

The configuration guide distinguishes command-enforced paths and templates from instructions the agent must implement. It records that the current report command writes Word and HTML regardless of `report.formats`, and that a new task contains starter material rather than completed results or executed planned notebooks. The file map explains where the answer, work record, source documents, notebooks, figures and structured results can be found.

A source specialist checked fifteen implementation files and the existing numerical evidence. Four additional isolated validator invocations confirmed schema failure, warning handling and the no-results skip. The same-engine Java regression wording and the expanded uncertainty-notebook plan were clarified following review. The computations, all thirteen notebooks and frozen baseline are unchanged from `revision_history/before_task_workflow_clarification_2026-09-13.zip`; simulations were not rerun for these editorial additions. All editions were rebuilt, with fresh 123-page PDF and 111-page Word proofs and web checks at four widths.

PaperLab's student-readability and scientific-traceability skills now cross-reference file lifecycle, effective settings and actual validator coverage. The NeqSim writing skill distinguishes generic publication checks from book-local numerical and claim checks. Detailed evidence is in `verification/task_workflow_clarification_revision_2026-09-13.json` and its linked source audit and validator records.

## Follow-up: agent execution and configuration

Chapter 1 section 1.6 now points directly to the coordinating task-solving role. Chapter 7 section 7.5 adds a start/resume prompt, a map of host, role, study and runner settings, a specialist handoff explanation and a six-field notebook execution configuration. The text explains that installing an agent does not start it, that AgentBridge does not automatically load the study YAML, that notebook kernels require a separate interpreter check, and that individual job status must be inspected.

A PaperLab source specialist reviewed 22 source files and the two changed chapters without finding blocking unsupported claims. The YAML excerpt was parsed and matched to the canonical template. No new Python calculation was added, and the numerical outputs, notebooks and baseline are byte-identical to the archived preceding edition. Live AI-host delegation and runner execution were not tested in this editorial pass. Fresh format and layout checks cover the updated files.

The reusable task-solving agent instructions now pass the explicit source checkout to AgentBridge rather than infer it from an external task's parent folders. They also explain how to pass configuration values and verify the notebook kernel. PaperLab's readability skill now requires the same configuration-layer distinction and an actionable start/resume prompt. The immediately preceding release is preserved in `revision_history/before_agent_configuration_clarification_2026-09-13.zip`. The instruction repair is a local change, included in the companion package; it has not been pushed or published.


## Enterprise and host integration — 13 September 2026

Expanded Chapter 5 with enterprise repository setup, dependency contracts, private-catalog onboarding, company ownership and acceptance testing. Added documented Copilot, ChatGPT Work and Claude Code handoffs and start/resume/update procedures. Numerical examples remain byte-identical; no live company deployment is claimed.
