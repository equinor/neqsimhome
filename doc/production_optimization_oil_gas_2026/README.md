# Production Optimization of Oil and Gas Fields Using NeqSim

September 2026 revision of the 35-chapter textbook by Even Solbraa. The primary
reading edition is `submission/book.pdf`; `submission/book_standalone.html`
provides the browser edition with embedded illustrations. The browser edition
uses its declared online math-rendering resources.

The scientific revision includes a complete chapter review, engineering acceptance
checks, current NeqSim examples, executed notebooks and traceable numerical figures.
Read `verification/scientific_revision/SCIENTIFIC_REVIEW.md` for the final chapter
coverage, corrected scientific issues, independent benchmarks and model limits.
`verification/release_gate_report.md` records the exact publication checks.

## Software basis

- NeqSim source commit: `6cc8026202a5d3f9383c9abd1d97d448993813f9`
- Project version: 3.20.0; the source revision is authoritative.
- Source checkout used for this edition:
  `C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim`
- Python selected by the user:
  `C:\Users\solbraa\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
- Additional book dependencies: `.build/python_packages`.

Use a JDK suitable for the recorded NeqSim source build. The Java examples avoid
post-Java-8 language constructs; that does not imply that the compiled NeqSim
dependency itself can run on a Java 8 runtime.

## Reproduce the calculations

From this book directory in PowerShell, select the same interpreter and source:

```powershell
$bookPython = 'C:\Users\solbraa\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$env:NEQSIM_PROJECT_ROOT = 'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim'
& $bookPython devtools/execute_book_notebooks.py --workers 2
& $bookPython devtools/audit_notebook_release.py
```

Compile the source checkout before running calculations. From its directory:

```powershell
.\mvnw.cmd -B -ntp -DskipTests compile dependency:build-classpath '-Dmdep.outputFile=target/neqsim-dev-classpath.txt'
```

The notebooks load workspace classes through `neqsim_dev_setup.py`. They do not
install packages, change interpreters, or silently use a packaged NeqSim JAR.
See `devtools/README.md` for selective chapter execution and retained outputs.
The manuscript-example reports preserve code hashes and execution diagnostics;
the release report identifies the corresponding audit commands.

## Rebuild the book

```powershell
& $bookPython devtools/run_paperlab.py book-check (Get-Location).Path
& $bookPython devtools/build_release.py --formats html,pdf
& $bookPython devtools/inspect_pdf.py .build/release_candidate/submission/book.pdf
```

The build uses the canonical PaperLab renderers and writes review candidates
under `.build/release_candidate/submission`. Review those artifacts before
updating `submission`. The build manifest records source and artifact hashes and
rejects a candidate if source files change during rendering.

The `devtools/repair_*`, `revise_*` and migration scripts are an audit trail of
this revision, not normal rebuild steps. Do not rerun them against an edited
manuscript. Original material and the previous publication are preserved under
`.build`.

## Evidence and artwork

- `verification/notebook_execution_report.json`: cell execution and figure data.
- `verification/notebook_release_audit.json`: current notebook/figure integrity.
- `verification/foundations_release_audit.json`: current code coverage, Chapters 1–18.
- `verification/ch21_debottlenecking_java.json`: complete Java fixture and operations.
- `verification/illustration_manifest.json`: OpenAI artwork prompts and provenance.
- `verification/render_manifest.json`: source and rendered artifact hashes.

All 35 chapter notebooks contain explicit physical acceptance checks. The separate
benchmark notebook includes 89 comparisons, of which 18 compare methane density
with independent NIST reference-EOS values. The remaining comparisons test
analytical relations, conservation and independently enumerated searches.

Conservation and convergence establish solution verification within the stated
model, inputs and domain. Predictive accuracy for a particular field still needs
measured mixture properties, well and plant data, and applicable equipment ratings.
External integration patterns and unsolved exercises are explicitly separate from
the executed calculations. Native model limitations and rejected states remain
documented in the scientific ledgers.

Historical figure generators are archived in
`verification/scientific_revision/legacy_generators`; they are excluded from the
current rebuild workflow. Current scientific plots use the executed notebooks or
the documented calculation scripts with retained numerical records.
