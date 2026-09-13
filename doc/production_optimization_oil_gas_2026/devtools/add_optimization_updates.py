"""Source-grounded September 2026 additions; chapters 19--35 only."""
from pathlib import Path
import re
BOOK = Path(__file__).resolve().parents[1]
updates = {
19: ("Export calculations need an explicit basis", r"""An export decision joins three different models: thermodynamic quality, pipeline hydraulics, and contractual acceptance. Preserve the composition, volume-reference temperature and pressure, combustion-reference temperature, pressure datum, and applicable contractual period with each result. `Standard_ISO6976_2016` uses a volume-reference basis for its gas-quality calculation; the explicit kJ-to-MJ conversion in this chapter is essential when comparing with a specification in MJ/Sm³. An operating-pressure compressibility factor is a separate metering correction.

`PipeBeggsAndBrills.setLength()` takes metres. Thus a 200 km export line is entered as 200000.0, and a 250 km line as 250000.0. A simulation can converge with an incorrect length and still produce a misleadingly small pressure loss. Dimensional checks belong alongside convergence checks.

The current `PlantPipelineEvidence` adapter freezes one completed Beggs–Brill profile with six explicitly declared limits: maximum absolute pressure, pressure drop, minimum receiving pressure, maximum mixture superficial velocity, and minimum/maximum bulk temperature. It also retains the profile-node location of the controlling value. This adapter requires verified geometry provenance, current calculation identity, finite profile values, and complete convergence. It does not certify hydrate, wax, erosion, acoustic vibration, slugging or transient envelopes. Those remain separate calculations and operating restrictions \cite{neqsim2026update}.

The practical outcome is a traceable export constraint: “receiving pressure below its declared lower limit at the current solved flow” is actionable evidence. “Pipeline utilization is 95%” without the controlling physical quantity, limit and basis is insufficient."""),
20: ("Capacity coverage and strict evidence", r"""A capacity report must answer two questions before it ranks equipment: which restrictions were expected, and which of those restrictions were actually evaluated? `UtilizationCoverageReport` now records declared equipment and constraint identities independently of discovery. Missing equipment, missing constraints, absent ratings, default screening limits and failed suppliers remain visible. Unknown values are `NaN` in Java and `null` in JSON; they must never be converted into zero utilization \cite{neqsim2026update}.

Completion has a narrow meaning: evidence is available for the declared scope. It does not establish process convergence, operating feasibility, mechanical integrity or whole-plant completeness. A deliberately disabled constraint remains an auditable row. Similarly, `autoSize()` establishes a synthetic design basis for a screening exercise; it is not evidence of the installed capacity of an existing vessel or compressor.

The strict separator, pipeline and shared-resource adapters are post-solve evidence collectors. `PlantSeparatorEvidence` records the supported separator metrics only when their declared geometry, phase availability and validity conditions are satisfied. `PlantSharedResourceEvidence` checks participant-complete compressor/pump shaft demand or solved `EnergyBus` electrical demand against the authoritative aggregate. `PlantCommonShaftEvidence` checks a declared steady-state casing/driver/shaft group, including common speed, power balance, torque and casing map margins. They freeze existing results and do not introduce new equipment physics.

Use an explicit evidence ledger in capacity studies:

| Question | Required report field | Interpretation |
|---|---|---|
| What is limited? | Stable equipment/constraint identity | Distinguishes similarly named trains |
| On what basis? | Unit, phase/rate basis, geometry and provenance | Makes limits comparable |
| Is the value current? | Calculation identity and convergence | Prevents stale acceptance |
| What is missing? | Coverage diagnostics and disabled rows | Prevents empty “all clear” reports |
| Is the candidate feasible? | Signed margin and severity | Separates availability from compliance |

The following intentional missing-equipment example is a small executable regression of this principle. Its successful outcome is an incomplete report, not a feasible plant:

```python
import json
import jpype
jneqsim = jpype.JPackage("neqsim")
Coverage = jneqsim.process.util.optimizer.UtilizationCoverageReport
coverage = (Coverage.builder("Book capacity example")
            .expectConstraint("Compression", "Missing compressor", "power")
            .build())
assert not coverage.isComplete()
diagnostics = [str(item) for item in coverage.getDiagnostics()]
assert any("MISSING_EQUIPMENT" in item for item in diagnostics)
print(json.dumps(json.loads(str(coverage.toJson())), indent=2))
```
<!-- @neqsim:claim
  test: src/test/java/neqsim/process/util/optimizer/UtilizationCoverageReportTest.java
-->
"""),
21: ("Debottlenecking with a reproducible constraint ladder", r"""The latest plant-evidence layer changes the deliverable of a debottlenecking study. For each proposed modification, retain the baseline state, the changed design or operating variable, the current solved state, and the complete ranked list of applicable constraints. When compressor power is relaxed, a receiving-pressure or shared-power restriction may become controlling. The new bottleneck is meaningful only if both the old and new restrictions retain stable identities and comparable evidence \cite{neqsim2026update}.

Do not rank capital projects from `autoSize()` margins alone. Replace synthetic ratings with installed-equipment provenance, then repeat the process calculation. For a shared driver or electrical bus, reconcile all declared participants before assessing budget headroom. A missing participant is unavailable evidence; it is not a zero-power load. For a separator, retained vessel dimensions and internals assumptions must accompany changes in gas load, liquid residence and phase availability.

The recommended decision table contains baseline throughput, replayed candidate throughput, incremental power, binding restriction, remaining margin, evidence coverage and uncertainty. A project that increases a numerical optimum but makes the next restriction unavailable should remain unresolved until that evidence gap is closed."""),
22: ("Numerical optimum, physical feasibility and model scope", r"""Production optimization now has a stronger distinction between a numerical candidate and an accepted process state. `ProductionOptimizer` replays the selected decision vector on the full model without relying on cached evidence before returning. Reported feasibility and live equipment readbacks therefore refer to that replayed point. If a selected point becomes physically infeasible, recorded feasible candidates are reconsidered in deterministic order; a failed final solve is an error, not a successful stale answer \cite{neqsim2026update}.

This guarantee does not make an unregistered restriction disappear. The objective, installed limits, flow basis, composition, convergence tolerance and evidence coverage remain the modeler's responsibility. Binary feasibility assumes a suitable monotonic feasible interval. Score-based searches require an explicit objective: an empty objective list has zero objective score and is not a declaration to maximize production.

The gas-lift allocation formulas in this chapter are illustrative response curves. They explain the equal-marginal-return principle, but they do not calculate tubing hydraulics and are not validated NeqSim well predictions. For design work replace them with qualified well-performance curves or a coupled reservoir/well/network calculation, and preserve lift-gas and produced-gas bases separately. Likewise, a grid of oil-rate/power results is only a candidate set; a Pareto frontier requires removal of dominated points."""),
23: ("September 2026 execution and acceptance contract", r"""Three interfaces in this chapter serve different purposes. `ProcessAutomation.evaluate()` applies setpoints, solves and returns requested readbacks. `AgenticProcessOptimizer` provides a bounded, address-based search that may use penalties. `ProductionOptimizer` provides equipment-aware optimization with explicit objectives and constraints. A successful address operation or search termination does not itself establish installed-equipment capacity, whole-plant coverage or permission to operate \cite{neqsim2026update}.

The current `ProductionOptimizer` always reapplies and solves the selected decision vector without cached evidence before returning. It may replay earlier feasible points if the first selection fails physical feasibility; final solve exceptions propagate. Preserve the replayed flow, equipment readbacks and result diagnostics together. Do not quote the best objective from the search tape alongside readbacks from another point.

For rate-only monotonic feasibility searches, use `BINARY_FEASIBILITY`. For golden-section, swarm or other score-based searches, supply an explicit objective. `null`/`None` objectives produce a zero objective score; they do not implicitly maximize throughput. The distinction matters when comparing algorithms.

`UtilizationCoverageReport` and `PlantUtilizationSnapshot` complement these optimizers. They represent declared coverage, evidence identity and validity, rather than inventing constraints from a sparse flowsheet. The new separator, pipeline, shared-resource and common-shaft adapters collect narrowly defined post-solve evidence. Read their unavailable status as a data gap, not as an unconstrained green operating point.

When integrating an external solver, use a fresh process instance per concurrent candidate or a rigorously managed state boundary. Record the exact NeqSim commit, variable units, objective scaling and termination reason. Recompute the selected point with the full process model and report its balances and constraint margins before treating the solver output as an engineering recommendation."""),
24: ("Current optimizer replay and screening-table semantics", r"""At the September 2026 source revision, `ProductionOptimizer` returns a freshly replayed decision vector and corresponding feasibility evidence. This resolves the case in which the search's best point and the mutable process previously represented different operating states. Applications must still check feasibility and preserve any final-solve exception; a search history entry is not an accepted result by itself \cite{neqsim2026update}.

The interpretation of pressure/flow tables also matters. `ProcessOptimizationEngine.generateCapacityScreening(pressures, temperatures)` performs fixed-composition mass-throughput screening. The five-argument overload accepts explicit outlet-pressure and lower/upper mass-flow limits. It does not recombine a fluid at arbitrary water cut/GOR, solve a well datum pressure, or certify a global optimum. Legacy `generateLiftCurve(P,T,WC,GOR)` accepts only the supported singleton zero composition placeholders; nonzero/multiple composition axes now fail explicitly.

A process-capacity maximum is not flowing bottomhole pressure. Generic process tables should be exported as diagnostic JSON, CSV or formatted text. Reservoir `VFPPROD`/`VFPINJ` output is a separate contract: supply a complete, finite, positive BHP grid to `EclipseVFPExporter`, state the datum and phase-volume basis, preserve all axes and use compatible METRIC or FIELD units. The exporter formats supplied pressures; it does not qualify the well hydraulics. See Chapter 28 for the distinction and the current source export contract \cite{neqsim2026update}.

Finally, synthetic auto-sizing and disabled constraints are study assumptions. Preserve them alongside each optimum so that a reader can distinguish an installed-plant recommendation from an algorithm demonstration."""),
25: ("A dashboard must display missing evidence", r"""Extend the familiar green/yellow/red capacity display with an explicit unavailable state. A sensor dropout, stale calculation identity, unverified installed rating or absent compressor-map envelope must not be rendered as zero utilization. `UtilizationCoverageReport` retains missing expected constraints even when discovery finds no supplier, while strict plant snapshots distinguish incomplete evidence from a finite limit violation \cite{neqsim2026update}.

The operating dashboard should display the current value, limit, unit/basis, signed margin, source, age and coverage status. Only current, applicable evidence can receive a numerical utilization colour. Disabled restrictions should remain visible with their reason. Do not use a single aggregate percentage to imply that hydraulic, thermal, mechanical, quality and availability restrictions have all been checked.

For common-shaft compression, present casing map margins together with shared torque/power and the declared participant list. For pipelines, show the controlling profile location and receiving pressure rather than inlet velocity alone. For separators, expose phase-availability and retained geometry assumptions. These additions turn a dashboard from a ranked list into a reproducible basis for action."""),
26: ("Network-to-facility boundaries and qualified well curves", r"""The newest VFP contract separates network/facility pressure requirements from qualified well bottomhole pressure. A gathering-network outlet condition or process capacity table cannot be relabelled as BHP. Establish the well datum, tubing geometry, thermal boundary conditions, friction and hydrostatic losses, fluid recombination and standard phase-volume rate before constructing a reservoir-compatible table \cite{neqsim2026update}.

Gas-lift allocation also requires two distinct balances: injected lift gas and produced reservoir gas. An allocation curve is usable only over its stated valid range and operating boundary conditions. Separator pressure changes can alter every well's backpressure and therefore invalidate a previously fitted allocation curve. After allocating gas, replay the coupled well/network/facility state and check compressor, separator, export and shared-resource restrictions together.

The polynomial and equal-slope examples in this chapter are optimization demonstrations. Their numerical response is not a replacement for calibrated tubing hydraulics. Preserve that distinction when producing a forecast or comparing a platform-pressure change with an artificial-lift investment."""),
27: ("Scenario isolation and current constraint evidence", r"""A scenario is a complete model state: composition, rates, thermodynamic method, topology, equipment availability, installed limits and utility budgets. Reusing an unchanged flow vector after a limit or lineup change is not a valid cache hit. The current plant evidence contracts require stable identities and current calculation provenance, and the selected optimization point must be replayed against the active scenario \cite{neqsim2026update}.

Report scenario success, physical feasibility and evidence completeness separately. A finite but overloaded scenario is useful adverse-case evidence. A scenario with failed convergence or missing capacity evidence is unresolved and must not be ranked as if its absent load were zero. Preserve all failed samples with explicit causes in uncertainty studies; dropping them changes the sampled population and can bias percentiles.

For parallel execution, each worker needs an independent process model and decision state. Concurrency tests should reproduce a sequential reference before runtime claims are made. Record seed, composition, input ranges, solver settings and the number of successful/failed evaluations with every uncertainty or operating-envelope figure."""),
28: ("The current VFP export boundary", r"""`MultiScenarioVFPGenerator` calculates required process inlet pressures for configured outlet conditions. Its legacy `getBHP()` name does not establish a bottomhole-pressure datum. At the current revision, `toVFPEXPString()` and `exportVFPEXP()` produce diagnostic process-screening text; they do not produce reservoir deck keywords. Use `toDiagnosticString()` and a `.txt` output when retaining these generic process results \cite{neqsim2026update}.

`EclipseVFPExporter` has a different role: it formats supplied, qualified flowing BHP at a declared well datum. A complete production grid has axes for standard phase-volume flow, THP, water ratio, gas ratio and artificial lift. The Java pressure-array order is `[flow][THP][water ratio][gas ratio][ALQ]`, while each deck row uses one-based THP/water/gas/lift indices followed by all flow values. The exporter validates structure and conversions; the caller qualifies the physical well model.

Default input units are Sm³/day and bara even when FIELD output is requested. METRIC and FIELD output must match the surrounding reservoir deck. In FIELD tables gas rate and GRAT use Mscf/day, and GOR uses Mscf/STB. Do not substitute kg/hr, actual volume, gauge pressure or a process mass-capacity optimum. Standard-volume reference conditions must already match those of the reservoir model.

All axis entries and BHP cells must be finite, positive where required and dimensionally complete. Infeasible values remain unavailable in diagnostic results and must not be interpolated, copied or filled into a deck silently. Select and validate a feasible grid before export. Neither a correctly serialized file nor the synthetic serialization examples constitute execution in a reservoir simulator or validation of field well performance.

For a field-development decision, retain three independent artifacts: a calibrated well-model validation, a complete process-capacity/quality assessment, and an exporter contract check. This prevents an attractive process-screening result from becoming an unjustified production forecast."""),
29: ("Keep steady-state evidence separate from dynamic protection", r"""The current strict common-shaft and pipeline adapters qualify specific steady-state solved quantities. They do not qualify transient overspeed, surge during a trip, water hammer, slug arrival, start-up or shutdown. A complete steady-state snapshot is therefore an input to a dynamic study, not a validation of its protective behaviour \cite{neqsim2026update}.

For each dynamic example record the initial inventory/state, controller modes, time step, boundary trajectories and equipment model assumptions. Check component and energy accumulation as well as inlet/outlet balances. Repeating the run with a smaller time step should preserve the decision-driving peak, integral and settling behaviour within a declared tolerance.

When an optimizer supplies supervisory setpoints, rate-limit and validate the transition in the control model. Preserve independent trip and operating constraints. An address-based optimization interface changes simulation inputs; it does not itself provide a plant control-system connection or operational authority."""),
30: ("Automation is an evaluator, not a plant authorization", r"""`ProcessAutomation.evaluate()` is the current apply–solve–read primitive for model evaluation. `AgenticProcessOptimizer` builds bounded address-based searches on this mechanism. Keep discovery, unit conversion, solve outcome, objective/penalty values and constraint evidence in the recorded result. A valid address or a completed search does not establish installed-equipment feasibility \cite{neqsim2026update}.

The strict evidence adapters add a useful boundary for digital twins: calculations are accepted only with current identity, finite values, applicable provenance and the required convergence/participant coverage. Missing plant measurements or missing model restrictions should remain unavailable. Self-correction of a misspelled simulation address is convenient during exploration, but a deployed tag mapping should be approved, explicit and regression checked.

Historian and real-time integration listings in this chapter require a caller-configured data source, credentials, tag mapping and independently supplied callbacks. They cannot be executed against a real facility merely by importing NeqSim. Synthetic offline examples validate the model-side calculation, while historian connectivity, live-data quality and setpoint application require separate integration tests.

For release and rollback, save model state with the exact source revision, schema, composition and calibration data identifiers. State serialization preserves a model representation; it is not proof that live plant and model states agree. After restoration, rerun the process and check balances, current constraints and expected readbacks before resuming optimization."""),
31: ("Choose a solver with a measurable acceptance contract", r"""Compare algorithms on the same objective, bounds, constraint set, fluid model and stopping tolerance. Score-based searches with empty objective lists have zero objective score; they cannot be compared with explicitly defined throughput maximization as if the optimization problems were identical. Binary feasibility requires a suitable monotonic region, while non-monotonic maps or disconnected feasible regions require a broader search strategy \cite{neqsim2026update}.

The current `ProductionOptimizer` replays its selected point without cached evidence. External solver integrations must implement an equivalent final evaluation. Measure both numerical termination and physical acceptance: finite state, process convergence, balances, constraint margins, declared evidence coverage and reproducibility. Cache timing should distinguish unchanged states from changed constraints or equipment lineups.

Pressure/flow screening remains a process calculation. The current `generateCapacityScreening()` interface makes its fixed-composition, mass-throughput basis explicit. It is not a numerical shortcut for a qualified well VFP model; reservoir deck formatting requires supplied BHP and the separate axis/unit contract described in Chapter 28."""),
32: ("Qualification of advanced optimization and surrogate workflows", r"""An advanced optimizer or surrogate inherits the limitations of its training and evaluation model. Preserve the thermodynamic method, composition envelope, phase transitions, equipment limits, validity range and failed samples in the training record. A low average interpolation error does not establish reliable behaviour near an active compressor-map or export-quality restriction.

The current plant evidence classes freeze existing physics results and their provenance; they are not new general-purpose predictive models. Their scale benchmarks qualify particular evidence paths or synthetic fixtures, rather than demonstrating complete industrial optimization for every plant topology. Do not extrapolate a single elapsed time into a generic performance claim \cite{neqsim2026update}.

Use a surrogate to propose or screen candidates, then replay the selected candidate with the full NeqSim process model. Compare the objective and every active constraint against the surrogate prediction, record discrepancies, and reject unavailable or stale evidence. A model-assisted policy should revert to a validated feasible baseline when its domain or evidence checks fail. The same distinction applies to reinforcement learning: an offline simulation policy is not demonstrated plant control."""),
33: ("Plant-wide utility and evidence boundaries", r"""An onshore complex links compressors, pumps, heating/cooling duties, products and shared utilities across areas. Local headroom can coexist with a saturated plant utility. `PlantSharedResourceEvidence` now supplies participant-complete maximum-budget evidence for supported total shaft-demand and solved electrical-demand cases; its sum is checked against the authoritative process or bus aggregate \cite{neqsim2026update}.

A shared resource needs a stable identity, explicit unit/basis, participant list, installed or agreed limit, and current solve identity. Missing or stale participants are evidence gaps. Do not infer a complete site fuel, steam, cooling-water or electrical model from the presence of one supported aggregate adapter.

For optimization studies, show both the local controlling equipment restriction and the plant-level budget. Rerun product quality, receiving pressure, utility demand and all relevant area boundaries at the selected production rate. This links a proposed throughput increase to the restrictions that the operating team actually has to manage."""),
34: ("How to reproduce and assess the case studies", r"""Treat the case-study inputs as disclosed teaching assumptions unless an external dataset is explicitly identified. A reported increase is reproduced only when the same composition, rate basis, topology, limits and source revision are used. The September 2026 audit executes manuscript examples against the local source build; execution records belong with the book's verification artifacts \cite{neqsim2026update}.

For each study compare the baseline and final replay on one results table: production rates, power, discharge/arrival conditions, balances, binding restriction, signed margin, convergence and coverage. A change that increases apparent production while omitting water handling, shared power or export quality is incomplete scope, not a verified debottlenecking result.

Use the figures to ask a decision question. Where does the controlling restriction change? How much incremental production survives the power and quality checks? Which uncertain input changes the preferred alternative? Synthetic sensitivity curves illustrate mechanisms; they should not be presented as measured field performance or an independent benchmark."""),
35: ("What is available now and what remains research", r"""At the source revision used for this edition, bounded address-based model evaluation, optimizer final-point replay, explicit utilization coverage and strict post-solve evidence adapters are implemented capabilities. The separator, pipeline, shared-resource and common-shaft adapters have deliberately stated scopes. Their presence does not imply a complete dynamic plant optimizer, universal installed-equipment qualification, or autonomous field operation \cite{neqsim2026update}.

The immediate engineering opportunity is improved traceability: a proposed operating point can be tied to the exact solved model, current constraints, stable participant identities and unavailable-data diagnostics. This is a stronger basis for human review than a single optimum or traffic-light percentage.

Research opportunities remain in complete large-plant benchmark topologies, robust convergence across discrete lineups, coupled well/reservoir uncertainty, domain-aware surrogates and defensible dynamic transitions. Progress should be demonstrated with reproducible cases and physically meaningful failure tests. Faster calculation is useful when it preserves the same evidence and decision; an unqualified change in model scope is not a speed improvement."""),
}
for number, (title, content) in updates.items():
    path = next((BOOK / "chapters").glob(f"ch{number:02d}_*/chapter.md"))
    text = path.read_text(encoding="utf-8")
    start = "<!-- September 2026 source update -->"
    if start in text:
        continue
    # Put contemporary interpretation before the first numbered summary.
    match = re.search(r"^## \d+\.\d+ (?:Summary|Conclusions)", text, re.M)
    position = match.start() if match else text.find("## Exercises")
    if position < 0:
        position = len(text)
    section = f"\n{start}\n## {title}\n\n{content.strip()}\n\n---\n\n"
    text = text[:position] + section + text[position:]
    path.write_text(text, encoding="utf-8")
