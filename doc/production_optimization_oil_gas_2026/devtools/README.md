# Reproducing the book's calculations

Use the Python interpreter selected for the workflow. For this edition the user
selected the bundled Codex Python runtime. Book-local dependencies were installed
under `.build/python_packages`; the executor passes that directory to the same
interpreter in every child process. There is no automatic package installation or
fallback to a different interpreter inside the notebooks.

Set `NEQSIM_PROJECT_ROOT` to a compiled NeqSim source checkout. The first code cell
uses `devtools/neqsim_dev_setup.py` and takes Java classes from `target/classes`.
The wrapper package is not required: `jneqsim` is a named JPype package binding to
the already-started source JVM.

Run the selected interpreter with:

```text
devtools/execute_book_notebooks.py --workers 2
devtools/refine_figure_sections.py
verification/scientific_revision/finalize_physics_review.py
devtools/audit_notebook_release.py
```

To re-run selected chapters, add `--chapters ch05,ch28`. Each notebook gets a fresh
process and JVM, each code cell runs in order, and the first error stops that
notebook. Python stdout, stderr, error details, and the freshly generated PNG
figures are retained in the notebook. The implementation executes ordinary Python
cells directly; it does not choose a Jupyter kernel or evaluate notebook magics.

`verification/notebook_execution_report.json` records the source revision, exact
Python executable, Java class origin, cell hashes, runtime, outputs and figure
hashes. `verification/notebook_release_audit.json` is the final integrity gate.
`verification/notebook_figure_updates.json` supplies captions, quantified
observations, physical mechanisms, implications, recommendations and results
tables for the chapter-author hand-off.

The refinement command applies plot-specific reviewed interpretations, writes
`verification/figure_sections/ch01.md` through `ch35.md`, and updates only notebook
discussion cells. It rechecks every executed code hash before recording the
new notebook artifact hash and the previous hash in an editorial-review record.
The scientific finalizer then writes the scope/evidence link cells and their final
artifact hashes. Run the final integrity gate after these editorial steps.
If the independent benchmarks change, run `verification/scientific_revision/build_benchmark_notebook.py`
before the scientific finalizer. Do not rerun `instrument_notebooks.py`: it is a
one-time migration from the original backup and would discard later edits.

Plots are exported at 220 dpi or higher. Each numerical line/bar/scatter plot has
an adjacent CSV of its coordinates and a JSON data record; the notebook ends with
a tabulated range summary. The executor appends a discussion after each generated
figure using that run's measured values and the chapter-specific physical context.

One-time migration scripts are retained as an audit trail; they are not part of
the normal execution commands. Original notebooks were preserved under
`.build/backups/chapters/`. Re-running a migration script on an edited book is not
a supported update workflow.

Execution and internal convergence are distinguished from independent model
validation. Undefined one-phase ratios and infeasible pressure trials remain
visible as domain gaps. Conceptual charts, the illustrative Python controller
balance, and synthetic sensor samples are identified explicitly; they must not be
presented as field measurements or validated NeqSim transient trajectories.

## Literal manuscript checks

The notebook checks and the printed examples are separate execution records.
The scientific review ledgers under `verification/scientific_revision` map each
printed Python/Java fence to its exact code hash, calculation or API scope, and
acceptance evidence. A successful execution log alone is insufficient.

The Python solution runner executes the actual chapter fragments in order in a
fresh JVM, with chapter-specific acceptance hooks. For example, pass these
arguments to the selected interpreter from the book directory:

```text
devtools/verify_optimization_solution_hooks.py --chapter 21 --hooks devtools/ch21_solution_hooks.py
```

Each `chNN_solution_checks.json` records its hook module, helper snapshots,
prerequisite code hashes, observed values, tolerances and checks. Java proofs
have separate `chNN_java_solution_checks.json` records. Foundations use their
chapter execution and supplemental-physics ledgers; Chapter 33 uses
`run_ch33_science.py --literal`. Follow the recorded runner and prerequisite
contracts when reproducing a case; do not substitute an execution-only audit
for these engineering checks.

After an intentional rerun, refresh the corresponding scientific ledger and
literal summary, review regenerated figures, and rebuild the final source
snapshot and engineering release gate. Any changed code, input, validation
helper, compiled class or output invalidates its earlier hash-bound evidence.
The source commit and all compiled class hashes are recorded in
`runtime_artifact_manifest.json`.

Rejected native candidates remain in the evidence. The accepted alternatives
must pass their stated balances, phase/domain checks and independent sampled or
analytical comparison. The 30 external integration patterns and unsolved learning
exercises remain outside claims that runnable calculations were checked.

## Final publication review

Build the PDF and HTML candidates, then inspect the exact artifacts before
promotion. A page-boundary check alone misses overprinted table rows, equation
number collisions, and pages containing only a footer. Review the glossary in
full and enlarge dense equations, tables and code. The final contact-sheet
manifest identifies current page images by PDF and image hashes; do not reuse
approval from a previous PDF after rebuilding.

The four specialist visual reports are combined by
`aggregate_final_visual_review.py`. It requires every current contact sheet to
be covered and rejects stale PDF or image hashes and unresolved findings.
`promote_reviewed_release.py` copies only the reviewed PDF and browser artifacts
after checking the scientific, source, structure and publication evidence.
