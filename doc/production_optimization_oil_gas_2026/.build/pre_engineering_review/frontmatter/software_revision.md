## Software Basis and Reproducibility

This revision follows NeqSim source commit `6cc8026202a5d3f9383c9abd1d97d448993813f9`, dated 12 September 2026. The project version at that commit is 3.20.0. The commit identifies the implemented behavior more precisely than the version number: a packaged 3.20.0 installation may predate the changes described here.

### The Calculation Record

The companion source includes the chapter notebooks, executable-example checks, figures and verification reports. Use a full JDK and the deliberately selected Python interpreter. Notebook setup loads compiled workspace classes through `neqsim_dev_setup`; it must not silently replace the source build with an older packaged JAR. Compile the recorded source before executing the examples.

The verification record should be read with the book. It distinguishes successfully executed calculations, numerical checks, source-level API review and examples requiring a plant historian, control system or other external service. An integration pattern does not demonstrate a live plant connection.

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
