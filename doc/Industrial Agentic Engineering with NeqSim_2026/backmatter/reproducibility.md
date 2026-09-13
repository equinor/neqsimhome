# Reproducibility and Source Snapshot

This revision uses NeqSim release 3.20.0 as its public baseline and source commit `9a95440e194a6fdc2890e4efafff647711beedce` for source-level descriptions and executed examples. The latter is newer than the release tag. Preserve the distinction when reproducing an interface.

## Rebuild the examples

Select one Python interpreter explicitly and set the NeqSim source root. Build that checkout before starting the Python process. From this book's directory, run:

```text
<python-executable> verify_examples.py --project-root ABSOLUTE_NEQSIM_SOURCE_PATH
<python-executable> verify_cli_examples.py --project-root ABSOLUTE_NEQSIM_SOURCE_PATH
<python-executable> build_illustrations.py
<python-executable> build_notebooks.py --project-root ABSOLUTE_NEQSIM_SOURCE_PATH
<python-executable> verify_snippets.py --project-root ABSOLUTE_NEQSIM_SOURCE_PATH
<python-executable> build_book.py
```

The book runtime helper uses the selected interpreter and optionally reads publishing dependencies from the book-local `revision_history/build_dependencies` directory. It never substitutes an installed NeqSim package for the explicit source checkout. The numerical run records its interpreter, source commit and loaded Java code location in `results.json`.

The cover and one conceptual image per chapter were generated with the built-in image generator. The exact prompts, retained PNG masters, hashes and installation paths are recorded in `illustrations/imagegen_manifest_2026-09-13.json`. Notebook execution verifies and restores these retained images; it does not reproduce a stochastic image-generation call. Numerical plots continue to come from saved NeqSim outputs.

## What was checked

The execution suite covers five methane states with SRK and PR, a matching NIST reference comparison, a base compression process, five discharge-pressure cases, automation input access, process-state save/load, the core flash runner, four pipe diameters, three numerical refinements, four wet-gas hydrate demonstrations, and 200 full-process Monte Carlo realisations.

The command-line checks execute the current dispatcher using temporary task defaults and fixture documents. They exercise the separate task, document and template settings; recursive filename discovery; intake/task creation; title-derived report generation; and work records. They preserve the real user settings. Installation and live AI-host interaction remain environment-dependent setup steps, rather than simulated confirmations of a human chat session.

The book-specific Java class `neqsim.book.industrialagentic2026.BookWorkedExamplesRegressionTest` checks selected methane, compressor, pipe and hydrate outputs against recorded constants. The companion notebooks compare against the frozen `verification/regression_baseline_2026-09-12.json`, which is separate from the refreshed `results.json`. A changed result therefore requires investigation rather than automatic replacement of its expected value. These checks preserve software behaviour; they are not independent physical validation.

The scientific traceability review connects numerical claims, figures and implemented equations to source methods, notebooks and recorded baselines. Teaching approximations are identified separately. Hidden `@neqsim` comments record these links in the manuscript; the current generic book checker does not itself verify Java assertion tolerances or automatically turn these comments into reader hyperlinks. The source table below and the companion audit records provide the navigation.

The NIST reference is a calculated reference-fluid dataset, not new experimental data. The raw tab-separated table, exact request URL and file digest are stored under `references/nist`. Duplicate rows at phase-label boundaries are matched by temperature and pressure, with consistency checked before use.

The pipe and hydrate examples are numerical demonstrations. They have not been independently validated for a real route or wet-fluid system. The local flash-runner test does not exercise a live MCP host or transport. State save/load verifies the saved JSON representation; it does not replay an entire external environment. No proprietary field case or vendor machine is qualified by these examples.

## Source navigation

| Topic | Source location in the recorded NeqSim checkout |
|---|---|
| Thermodynamic models | `src/main/java/neqsim/thermo/system/` |
| Flash operations | `src/main/java/neqsim/thermodynamicoperations/` |
| Process variables | `src/main/java/neqsim/process/automation/` |
| Process lifecycle | `src/main/java/neqsim/process/processmodel/lifecycle/` |
| Energy networks | `src/main/java/neqsim/process/equipment/energy/` |
| Route construction | `src/main/java/neqsim/process/equipment/pipeline/routing/` |
| Engineering packages | `src/main/java/neqsim/process/engineering/deliverables/` |
| DEXPI exchange | `src/main/java/neqsim/process/processmodel/dexpi/` |
| MCP runners and contracts | `src/main/java/neqsim/mcp/` |
| PVT experiments | `src/main/java/neqsim/pvtsimulation/` |
| Core agent discovery | `.github/agents/` |
| Core skill discovery | `.github/skills/` |
| Community catalogs | `community-agents.yaml`, `community-skills.yaml` |

The full public source can be browsed at the [recorded revision](https://github.com/equinor/neqsim/tree/9a95440e194a6fdc2890e4efafff647711beedce). The book's `references/SOURCES.md` provides a more detailed guide to the revision's sources.

## Maintaining a later edition

Update the source snapshot and rerun the examples before changing verification dates. Check units and physical meaning as well as exceptions. Rebuild all output formats after changes to prose, figures or references. Preserve earlier sources and execution records when results change.

The original manuscript and assets are preserved in `revision_history/original_before_2026-09-12_revision.zip`. Legacy placeholder notebooks and unverified figures have been removed from active chapter directories and retained in the revision archive. The active figures and notebooks belong to this revision.
