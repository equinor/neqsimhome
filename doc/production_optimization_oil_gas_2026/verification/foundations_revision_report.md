# Chapters 01–18 revision and execution report

The revision used PaperLab's `book_author.paperlab.md`, `book_creation/SKILL.md`, and `neqsim_in_writing/SKILL.md`. Technical changes were checked against the newer NeqSim source repository at revision `6cc8026202a5d3f9383c9abd1d97d448993813f9`, rather than the older repository surrounding the book.

## Published-code coverage

The authoritative machine-readable report is `foundations_release_audit.json`. It matches every current Python and Java code fence against literal code retained in an execution report, using a SHA-256 digest for each fence and each chapter. Prose-only changes can change a chapter hash without invalidating matching code execution evidence.

| Coverage | Count |
|---|---:|
| Published Python fences executed | 153 |
| Published Java fences executed | 70 |
| Total current fences with passing execution evidence | 223 |
| Runnable sequential examples | 178 |
| Executed configuration or introspection fragments | 45 |
| Excluded / unsupported fences | 0 |

Python used the explicitly selected bundled Codex interpreter, book-local dependencies, `neqsim_dev_setup`, and the compiled workspace classes. No installed NeqSim wheel or older packaged JAR was substituted. Python state was retained within each chapter after the documented JVM bootstrap. Java fragments were executed in chapter order with JShell, actual NeqSim classes, and Log4j output. They use Java 8 compatible syntax, while JShell itself ran on the installed JDK 25. This is not a claim that every fragment is a standalone Java class.

Complete chapter reports are named `chXX_*_python.json` and `chXX_*_java.json`. Selective final repairs have `*_blocks_*.json` reports. The release audit consolidates these by exact code, so an obsolete failure in an earlier full-chapter report does not override a successful run of the changed published code. Reports retain source, output, runtime, and exceptions for review.

## Physical checks and deliberate diagnostic cases

Execution without an exception is distinct from a calibrated model, physical feasibility or a converged numerical solution. The revised book makes this distinction explicit.

- The compact Chapter 6 Java optimization example demonstrates a rejected candidate: optimizer termination reports success while the hydraulic residual remains above its specified tolerance. The output prints both statuses. Those candidate rates are not accepted recommendations. The separate four-well Python case converges, with approximately 38.31 kg/s baseline and 40.80 kg/s after the illustrated choke search.
- Chapter 6 now uses the explicit liquid-basis `InflowPerformance` API. Its Vogel example returns about 326.18 Sm3/day of stock-tank liquid. The legacy `setVogelParameters` path interprets rate in MSm3/day and was inappropriate for the original liquid-rate example.
- Chapter 7 checks that a passive choke does not increase pressure and that its illustrative subsea booster consumes positive power. Its compressor proxy is identified as a screening approximation, not a qualified multiphase pump or wet-gas machine model.
- Chapter 9 reports hydraulically infeasible pipeline rates and diameters explicitly instead of plotting stale or negative-pressure results. Hydrate phase checking is enabled before hydrate formation calculations.
- Chapters 11 and 12 use clearly identified compact stripping sections with `solved()` checks before accepting results. Earlier refluxed-column examples failed rigorous convergence gates and were replaced with bounded, converged teaching models. Chapter 12's five-stage TEG example also reports its convergence diagnostics.
- Mechanical-design JSON examples in Chapters 7 and 10 still contain unconfigured optional fields. Null/non-finite design fields are explicitly identified as missing data, not validated design limits or evidence of code compliance.
- Chapter 10's pressure-capacity study now sizes its vessels once and retains those vessels across the sweep. The low-pressure point with highest sampled liquid recovery violates MP gas capacity; the narrative rejects it and recommends refining near the feasible boundary.

## Main technical and editorial changes

All chapter headings and local numbered references were aligned with Chapters 01–18. Duplicated full chapter versions were removed while retaining unique technical material and figures. The deduplication report records 22 redundant code fences removed across Chapters 1, 3, 4, 7 and 11. Complete original sources and reviewed secondary versions remain under `.build/foundations_originals`. One new typed-energy allocation example was added; the resulting total is 223 current executable fences.

The source revision adds or corrects reproducible workspace setup; PVT regression and reporting guidance; plus-fraction versus TBP characterization; explicit inlet/outlet and elevation conventions; dimensional hydraulic equations; named network APIs and SI boundaries; separator internals and fixed-geometry capacity assessment; compressor maps, efficiency units and driver-power units; gas-turbine/HRSG/steam examples; explicit pinch streams; and typed energy allocation with a verified unmet-demand case.

Additional scientific corrections distinguish hydrocarbon dew point at contract pressure from cricondentherm, quality inequalities from equalities, equilibrium TVP from ASTM RVP, 60°F API gravity from hot-oil density, and fixed-composition pressure sweeps from true depletion experiments. The book no longer promises column-recovery superiority from unmatched product quality or generic sub-second network performance.

## Figures

`foundations_published_figures.json` records ten referenced figures refreshed from passing fenced examples, with producer-code and image SHA-256 digests. Old images are backed up under `.build/foundations_original_figures`. Chapter 10's two different pressure studies now use separate images, including the new `mp_pressure_lp_liquid_recovery.png`; its fixed-vessel utilization image was visually inspected after regeneration.

`figure_interpretations_foundations.json` provides 70 individually written physical mechanisms, implications and recommendations for the notebook-generated figures in Chapters 01–18. The notebook agent integrates their observations and captions, and the parent workflow handles the book-wide PDF render and final page inspection.

Conceptual AI illustrations were inserted in the separator and compression chapters with explicit conceptual labels and limits on their interpretation as vendor or mechanical evidence.

## Follow-through for the parent build

After adding figure discussions, run `devtools/foundations_release_audit.py` with the selected bundled interpreter to update chapter hashes. It will fail to find passing evidence if a published code fence changes without a corresponding run. Use the release audit, not historical per-chapter failure logs, for final published-code coverage.
