## Software Basis and Reproducibility

This revision follows NeqSim source commit `6cc8026202a5d3f9383c9abd1d97d448993813f9`, dated 12 September 2026. The project version at that commit is 3.20.0. The commit identifies the implemented behavior more precisely than the version number: a packaged 3.20.0 installation may predate the changes described here.

### The Calculation Record

The companion source includes the chapter notebooks, executable-example checks, figures and verification reports. Use a full JDK and the deliberately selected Python interpreter. Notebook setup loads compiled workspace classes through `neqsim_dev_setup`; it must not silently replace the source build with an older packaged JAR. Compile the recorded source before executing the examples.

The verification record should be read with the book. It distinguishes successfully executed calculations, numerical checks, source-level API review and examples requiring a plant historian, control system or other external service. An integration pattern does not demonstrate a live plant connection.

### Engineering Checks and Independent Benchmarks

The scientific revision adds explicit acceptance tests to all 35 chapter notebooks. The retained execution contains 300 code cells. The checks cover units and reference conditions, finite physical states, component and total mass conservation, heat and shaft-work accounting, phase-equilibrium consistency, stated constraints, and applicable analytical or numerical limits. Sweeps repeat these checks at each candidate state; repeated assertions are not independent experiments.

The separate benchmark notebook contains 89 comparisons. Eighteen compare NeqSim SRK and Peng–Robinson methane densities with nine NIST reference-fluid states: 300, 350 and 400 K, each at 1, 50 and 100 bara. Maximum absolute relative deviations are 1.421 percent for SRK and 0.811 percent for Peng–Robinson, within the declared 3 percent teaching accuracy budget. That budget is not the uncertainty of NIST's data. The other comparisons test analytical limits, balance equations and independent search procedures.

Three levels of evidence have different meanings:

| Evidence | What it establishes | What it does not establish |
|---|---|---|
| Execution | The exact recorded code runs with its documented setup and dependencies | Correct physics or appropriate field inputs |
| Solution verification | The calculation satisfies its declared equations, balances, constraints and tolerances | Predictive accuracy of the underlying model |
| Independent reference comparison | Agreement with a separately sourced reference over the tested cases | Accuracy for other fluids, equipment or operating regions |

The physical checks exposed errors that an exception-free run missed. Corrections include phase-aware separation, explicit energy reconstruction for the approximate TEG contactor, stage energy and equilibrium gates for distillation, fresh calculations inside sensitivity loops, complete product accounting, and replay of selected optimization points. Approximate correlations, assumed equipment maps and synthetic economic inputs retain their stated scope.

The companion `verification/scientific_revision` directory contains chapter review ledgers, exact code hashes, expected and computed benchmark values, tolerances and the source archive. NIST values here are independent reference-EOS calculations, not new experimental measurements. No measured mixture PVT, plant history, vendor performance or economic data were supplied for the synthetic cases; those examples are verified teaching calculations, with field calibration still required for a specific installation.

### Current Capabilities in Context

| Capability | Where to use it in this book | Interpretation |
|---|---|---|
| PVT calibration and validation workflows | Chapter 3 | Keep regression data separate from independent validation observations |
| Explicit installed-equipment and constraint evidence | Chapters 10, 14–15, 20–21 | A calculated utilization is meaningful only with its rating basis and applicability |
| Shared-resource and common-shaft evidence | Chapters 18, 20 and 23 | Check declared participants, units, current solve and coverage |
| Final-point replay in production optimization | Chapters 23–24 and 27 | Re-solve the selected decisions before reporting an accepted result |
| Structured automation and bounded agentic search | Chapters 23, 25 and 30–32 | Inspect rejected setpoints, failed readbacks, constraints and convergence |
| Qualified VFP serialization | Chapters 26 and 28 | Supplied well BHP and standard phase-volume axes are distinct from process screening |

### Reading the Figures

Simulation figures show the stated inputs, output units and model assumptions. Sensitivity plots describe the evaluated range; a smooth curve alone does not establish a global optimum. An apparent capacity margin is conditional on the constraints actually configured and sampled.

The cover and the separator and compressor cutaways were created with OpenAI's built-in image-generation tool and selected for explanatory use. They are marked as conceptual artwork. The tool did not expose a selectable model identifier, so this edition does not claim that a specific image-model version was used. Prompts and asset provenance are retained with the source.

### Source Reference

NeqSim Project. *NeqSim source and documentation, September 2026 revision*. [Recorded source revision](https://github.com/equinor/neqsim/tree/6cc8026202a5d3f9383c9abd1d97d448993813f9). See the source documentation on optimization validation and the VFP export contract for the detailed execution and data conventions.
