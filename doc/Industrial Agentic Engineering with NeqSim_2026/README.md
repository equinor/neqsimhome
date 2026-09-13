# Industrial Agentic Engineering with NeqSim

Updated 13 September 2026 against the current local NeqSim source (`9a95440e194a6fdc2890e4efafff647711beedce`). The maintained manuscript is configured by `book.yaml`.

## Read the book

- [Print edition (PDF)](submission/book.pdf)
- [Editable Word edition](submission/book.docx)
- [Portable web edition](submission/book_standalone.html)
- [OpenDocument candidate](submission/book.odt)
- [EPUB candidate](submission/book.epub)

The portable web edition embeds its illustrations. Rendering equations requires access to the declared KaTeX resources. The PDF is the preferred offline reading edition. Word contains editable native equations. EPUB and OpenDocument are additional candidates with structural checks; dedicated reader/native visual checks remain limited. OpenDocument uses Unicode equation fallback. The separate symbol list is currently rendered in the PDF.

For a short explanation of how a task is solved and checked, start with Chapter 1 section 1.10. Chapter 7 sections 7.3-7.7 explain settings, file creation and evidence; section 7.12 follows one compressor result through its actual checks. Section 7.5 now also provides an agent start/resume prompt, a configuration map, specialist handoffs and notebook-runner settings.

## Revision contents

The thirteen chapters progress from a command-led first NeqSim calculation to fluid modelling, agents and skills, repository organisation, reproducible studies, calculation services, worked examples, industrial deployment and future directions. The quick start follows the original edition's practical reader journey with current commands. Task folders, document libraries, report templates and agent installation each have a clear role.

A new image-generator cover and one matching conceptual illustration per chapter use an ivory, navy, teal and gold style. The 21 chapter figures comprise 13 generated illustrations, six scientific plots and two code-native diagrams. Each chapter has an executed companion notebook. Generated image masters, full prompts, semantic limits and hashes are retained in `illustrations/imagegen_manifest_2026-09-13.json`; notebooks verify these assets and regenerate the numerical plots.

The revision uses PaperLab's maintained book agents and skills. [Workflow](agent_workflow_plan.md), [chapter readiness](chapter_health_dashboard.md), and [scientific review](verification/scientific_traceability_audit.md) retain their evidence.

See [revision notes](REVISION_NOTES.md), [sources](references/SOURCES.md), [numerical results](results.json), and [release checks](verification/release_gate_report.md).

The reader-and-companion ZIP includes the current editions, manuscript, notebooks, figures and verification records. It excludes installed dependencies, page proofs and the original revision archive. Publication rebuilding requires this book inside an updated NeqSim PaperLab checkout; numerical notebooks require the explicitly selected NeqSim source checkout.

## Rebuild

Select one Python interpreter explicitly. Set `NEQSIM_PROJECT_ROOT` to the intended NeqSim checkout and compile that checkout first. Replace the placeholders below; in PowerShell use `&` before a quoted executable path.

```text
<python-executable> verify_examples.py --project-root ABSOLUTE_NEQSIM_SOURCE_PATH
<python-executable> verify_snippets.py --project-root ABSOLUTE_NEQSIM_SOURCE_PATH
<python-executable> verify_cli_examples.py --project-root ABSOLUTE_NEQSIM_SOURCE_PATH
<python-executable> verify_workflow_guidance.py --project-root ABSOLUTE_NEQSIM_SOURCE_PATH
<python-executable> build_illustrations.py
<python-executable> build_notebooks.py --project-root ABSOLUTE_NEQSIM_SOURCE_PATH
<python-executable> index_sources.py --project-root ABSOLUTE_NEQSIM_SOURCE_PATH
<python-executable> build_traceability.py --project-root ABSOLUTE_NEQSIM_SOURCE_PATH
<python-executable> build_book.py
<python-executable> verify_epub.py
```

The example runtime loads `target/classes` through NeqSim's development setup. Publishing dependencies can be supplied by the selected environment or the book-local `revision_history/build_dependencies` directory. No shared Python environment is reconfigured by these scripts. The execution manifests preserve the actual interpreter and source revision used for this edition.

CLI verification uses isolated settings and fixtures. It exercises task creation, document search and report templates without changing saved user defaults. Clone, package installation and live AI-host interactions are documented setup steps, not fully reproduced environment-provisioning tests.

Render and inspect PDF pages and a Word-generated PDF proof after a layout change. `verify_layout.py` summarises page bounds and creates contact sheets from the rasterised pages. Run the PaperLab citation regression tests when changing reference rendering.

## Previous material

The complete original is preserved in `revision_history/original_before_2026-09-12_revision.zip`; the completed earlier revision is preserved in `revision_history/before_2026-09-13_command_refresh.zip`. The immediately preceding edition is preserved in `revision_history/before_task_workflow_clarification_2026-09-13.zip`. Replaced illustrations are in `revision_history/illustrations_before_2026-09-13`. Earlier placeholder notebooks and helpers remain archived; use the current build scripts above.

`build_book.py` invokes native PaperLab checks and a staged `book-build`, then native EPUB rendering. After visual proofs and responsive checks, `record_release.py` verifies current hashes and packages the companions. Do not replace the frozen regression baseline merely because a new calculation differs.


## Enterprise and host integration — 13 September 2026

For company setup read Chapter 5 Section 5.8; for GitHub Copilot, ChatGPT Work and Claude Code integration read Section 5.10. Section 7.5 supplies the start/resume and runner configuration guide.
