# Scientific review: foundation chapters01–18

Status: **PASS**. All18 full chapter texts reviewed; 382 recorded substantive corrections. Every published fence is linked by exact SHA-256 to its execution record.

Literal execution: 223 Python/Java fences. Scoped unit/case evaluations: 560; independent equation/unit checks: 19. These are numerical verification and analytical limits, not general model calibration.

| Chapter | Literal fences | Unit/case evaluations | Recorded corrections |
|---|---:|---:|---:|
| ch01_introduction | 6 | 7 | 22 |
| ch02_thermodynamic_foundations | 11 | 10 | 20 |
| ch03_fluid_characterization | 10 | 20 | 22 |
| ch04_reservoir_engineering | 6 | 3 | 15 |
| ch05_well_performance | 10 | 35 | 23 |
| ch06_wells_artificial_lift | 44 | 0 | 19 |
| ch07_subsea_production_systems | 6 | 15 | 13 |
| ch08_flowlines_and_risers | 7 | 21 | 18 |
| ch09_flow_assurance | 12 | 34 | 23 |
| ch10_separation_technology | 28 | 138 | 18 |
| ch11_oil_processing | 7 | 83 | 17 |
| ch12_gas_processing | 6 | 21 | 29 |
| ch13_produced_water_treatment | 5 | 15 | 21 |
| ch14_gas_compression | 21 | 45 | 25 |
| ch15_compressor_characteristics | 6 | 16 | 21 |
| ch16_heat_exchangers | 13 | 24 | 13 |
| ch17_valves_and_flow_control | 13 | 57 | 20 |
| ch18_power_production | 12 | 16 | 43 |

## ch01_introduction

The pressure budget now separates reservoir drawdown from downstream losses, and the water-column pressure estimate is checked by an independent unit conversion. The separator flowsheet has finite-state, component, mass and enthalpy checks; these checks support its calculated phase allocation, while export limits in the chapter remain illustrative contract inputs.

Limits: Export limits are illustrative contract inputs; entrainment/solids and sampling quality are not inferred from equilibrium composition.

Source SHA-256: `2112a49636acf41b4c9611394741e989f974bbdc7579b5ae0c3161ab963971db`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch02_thermodynamic_foundations

The worked TP flashes are checked for phase-fraction normalization, reconstruction of feed composition and equality of phase fugacities. Hydrate calculations are checked for finite temperatures only; neither a converged flash nor a physically plausible hydrate temperature establishes empirical accuracy. Independent methane reference-EOS comparisons are reported separately, with their own state range and teaching tolerance.

Limits: Hydrate and transport-property models have no independent calibration dataset in this review. Raw saturation-trace getters do not prove complete branch identity; the separately rebuilt figure has its own transition-bracket evidence.

Source SHA-256: `8e292f626afb243ea9e3f861cd62af49e06f2ae275880f1b302673d381b75994`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch03_fluid_characterization

The characterized-fluid examples retain explicit heavy-end assumptions and distinguish mole normalization from mass conservation. The bubble-pressure regression has a numerical residual test, but it fits a synthetic target and is not laboratory validation. The TBP phase-envelope trace in Section 3.7.5 is explicitly rejected as a complete envelope; finite getter arrays alone do not establish physical branch identity or completeness.

Limits: TBP saturation trace is explicitly unaccepted as a full envelope. BIP regression target is synthetic; characterization and fitted properties are not laboratory validation.

Source SHA-256: `95bf699f40c0f52395256dbb70c000e52d0b985d024a7912f41817d2dbfd2b09`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch04_reservoir_engineering

The decline cumulative-volume derivative and pressure/unit relations are checked independently. The reservoir objects demonstrate a lumped inventory/API boundary; they do not validate spatial reservoir sweep or commercial reserves. The P/Z interpretation is restricted to its closed, isothermal volumetric assumptions, and the Horner extrapolation is distinguished from average pressure in a bounded depleted reservoir.

Limits: Lumped reservoir configuration does not resolve field sweep or certify reserves. Arps/PZ/IPR interpretations are limited to the assumptions printed in the chapter.

Source SHA-256: `4ff85611e100d8f97e95b9bb2d88a1d8717fb22dc65eb6aa9754a6246b6abde4`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch05_well_performance

The completed wellbore trials are checked for finite positive pressure and temperature, material conservation and the upward pressure-loss direction; infeasible imposed-rate trials remain identified. The rod-pump displacement is checked against swept geometry, and the jet-pump example checks pressure and efficiency domains. These reduced lift models do not constitute a coupled power-fluid, reservoir and surface design; the Turner coefficient is separately checked for its stated unit convention.

Limits: Pipeline thermal/holdup correlations are not field-calibrated. Rod and jet pumps are reduced geometry/head-ratio demonstrations, not complete coupled lift designs.

Source SHA-256: `ad01d51d0265fc09fafce6f0834f7cb3cce1f01fb1e9c72c0a14594c4c939fdf`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch06_wells_artificial_lift

The compact, supported gas-network example supplies the accepted hydraulic case: four choke openings converge with pressure residual below 100 Pa, mass residual below 10⁻⁶ kg/s and valid pressure/flow directions. Its larger legacy multiphase API candidates remain explicitly unaccepted when hydraulics do not converge. The WellFlow example checks the declared drawdown and bottomhole-pressure constraints; neither solver convergence nor a software constraint authorizes operation beyond field limits.

Limits: The larger legacy multiphase network candidates and their optimizer/allocation continuations remain unaccepted as physical hydraulic solutions. Accepted gas choke network has mass/pressure/domain evidence, not field or valve-vendor calibration.

Source SHA-256: `67d01a323138482daa81b56e5f3b638052a5eba89c52c1875279d9e3bbc86183`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch07_subsea_production_systems

The completed subsea pipe/cooler calculations are checked for material conservation and valid pressures and temperatures. The thermal example states its chosen overall heat-transfer coefficient; the audit does not calibrate heat loss, multiphase holdup or vendor equipment performance. Published operator reports distinguish the actual Åsgard, Gullfaks and Vigdis technologies and startup dates; cost and casing factors are explicitly screening inputs.

Limits: Mechanical-design JSON leaves max/min design temperatures NaN; these are unset design inputs, not accepted material-temperature limits. Costs, casing factors and thermal performance remain screening inputs.

Source SHA-256: `70d77c649a290da0cc7db81f045f9e4aa4155020b10062a148f8a185db7c86f8`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch08_flowlines_and_risers

The completed route calculations are checked for mass/component conservation, positive profile states and pressure-loss direction. The fixed-property thermal characteristic length is independently checked by dimensional analysis; the NeqSim thermal closure itself is not independently calibrated here. Correlation accuracy requires matched measurements, and a gravity/friction comparison is not treated as a sufficient slack-flow or slugging criterion.

Limits: Pipe heat-loss and multiphase holdup closure have no independent model calibration in this manuscript audit. Steady-flow checks do not validate transient severe slugging or restart.

Source SHA-256: `807b4a436c107ee80ee44020ab5a63a0608e29ccbb54a3c4b0ef4376b62fd663`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch09_flow_assurance

The hydrate results are screened for finite temperature and the expected direction of MEG inhibition. Hammerschmidt concentration/depression conversions are checked against the corrected SI constant, while solid formation, deposition kinetics, corrosion and erosion require model-specific calibration beyond these examples. Phase equilibrium and a finite onset do not imply a safe shutdown time or an inhibitor guarantee.

Limits: Finite hydrate temperature and inhibitor direction are numerical/domain checks, not calibrated hydrate prediction. Corrosion, erosion, wax, asphaltene deposition and inhibitor hold time require corresponding laboratory/field/vendor evidence.

Source SHA-256: `6ccb40d76d35e641257fa5f20fe377c185e725fc5136b6f8d3da56644824747a`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch10_separation_technology

The separation cases are checked for total/component mass and steady-state enthalpy closure, including the explicit free-water outlet. Souders–Brown service factors and residence-time choices are declared screening assumptions; they are not inferred vendor guarantees. Horizontal droplet settling is assessed through residence time and settling distance rather than by comparing perpendicular velocity components.

Limits: Mechanical-design JSON has unset min/max design temperatures (NaN); vessel compliance is not claimed. Souders–Brown factors and droplet/retention sizing assumptions are not vendor capacity guarantees.

Source SHA-256: `14e052f910105251cc4e3a17a2d96e00f6010058e1396965af897550f9534f0a`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch11_oil_processing

The accepted reboiled columns use an explicit heat input and satisfy the strict numerical column status, MESH residual, stage/boundary mass and energy checks, and phase-fugacity checks. They illustrate the selected stripping conditions, not an unmeasured product specification. Bubble-pressure calculations are labeled TVP; a Reid vapor-pressure claim requires the stated test-method basis.

Limits: TVP calculation is not an ASTM Reid test result. Converged stripping cases do not establish unmeasured product-quality compliance.

Source SHA-256: `39049e5f1fce0c68e29f4b936052068106d1a96289341369aa6c01e147360351`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch12_gas_processing

The once-through TEG absorber and bounded NGL stabilizer satisfy column/stage material, energy and equilibrium residual checks; regeneration is outside their stated boundaries. The amine calculation instead prescribes removal, conserves transferred components and checks solvent loading, with the original undersized solvent case explicitly rejected. Its isothermal cooling is a required boundary duty, not an independent reactive-absorber energy prediction. Dry-gas JT cases place pretreatment upstream of the illustrated boundary.

Limits: SimpleAmineAbsorber removals are prescribed; inferred isothermal heat is not independent reactive energy validation. TEG regeneration and upstream dry-gas pretreatment are outside the illustrated boundary. NGL stripping example is not a product-spec deethanizer.

Source SHA-256: `e0ab60386b35cb8538d7a95751a578d05bacf41daea3a0e81e13e5670854d451`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch13_produced_water_treatment

The process-unit examples are checked for material/enthalpy consistency. Salt mass-fraction conversion and the limiting-reactant barite inventory are independently checked; supersaturation and an inventory upper bound do not predict deposited scale or treatment kinetics. The OSPAR statement is tied to the flow-weighted monthly performance standard and its reference analytical method, with site-permit conditions separate.

Limits: Material consistency is not deoiling/scale/corrosion performance calibration. Barite result is an inventory upper bound rather than predicted deposition.

Source SHA-256: `66a966f069593fc21ce0e21c42aaeaddc9b1213ce0b1e7212cc189aec9f59008`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch14_gas_compression

The solved compressor cases are checked for positive compression work and mass/component/enthalpy closure; the optimizer is checked for returned numerical feasibility. The equal-pressure-ratio result is independently tested only for its equal-efficiency, perfect-intercooling ideal-gas limit. Generated charts and software utilization ratios remain synthetic design aids until matched to the actual gas basis and vendor performance envelope.

Limits: Synthetic compressor map and software sizing/constraint demonstrations are not vendor-map validation. Numerical feasible optimizer output is not a proof of global optimality.

Source SHA-256: `49ee0769b0bc3165f2f48f337510e77778fff5f7e20693bbf7a58ccae010331a`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch15_compressor_characteristics

The operating compressor examples have mass, energy and state-domain checks. The plotted map curves are explicitly synthetic and are useful for illustrating speed/head/efficiency relationships; their surge and choke boundaries are not a qualified compressor map. Mechanical-speed, gas-property and driver constraints require the corresponding vendor and installation data.

Limits: Synthetic speed curves, surge/choke and cooling/recycle assumptions require vendor maps and operating validation.

Source SHA-256: `39c89d394a8880b64fe88bc9822bf1b66171249a4e897f29dd7d49b9899a03bd`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch16_heat_exchangers

The exchanger examples are checked for hot/cold energy closure and feasible terminal temperatures. A separate shifted-temperature heat cascade reproduces the stated pinch utility targets for the supplied constant heat-capacity streams; this verifies the calculation, not the plant stream data or exchanger network layout. Airflow and seawater sizing retain their explicit heat-capacity and approach assumptions.

Limits: Pinch cascade assumes stated constant heat-capacity streams; utility balance does not construct a realizable exchanger network. Material/permit temperature inputs require service-specific qualification.

Source SHA-256: `71c27502426d0eefd4c601e4ba90674c0ad776311b99101ac5413b229969dcba`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch17_valves_and_flow_control

The valve calculations are checked for mass/component conservation, isenthalpic throttling and nonnegative pressure drop. Flow-coefficient constants are tied to the specified flow, pressure, temperature and molecular-weight units; operating mode is set explicitly before using coefficient/opening to predict pressure. Relief-area arithmetic does not replace a complete relief-scenario, discharge-system or code assessment.

Limits: Valve isenthalpy does not calibrate Cv/opening or erosive/flashing performance. Relief arithmetic does not constitute a full code-compliant relief assessment.

Source SHA-256: `9be32450be392b8e2130e952596d2ac1ea5dab41b3db924a8dbecf2bb2794588`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## ch18_power_production

The package turbine example checks heat-rate/efficiency identities and the finite ambient-derating trend, while its map and exhaust recipe remain assumed. The accepted backpressure steam example checks recovered duty and shaft-work closure; the failed condensing candidate is retained as a rejection. The electrical bus conserves supply/served/unserved demand, and methane-slip accounting conserves carbon on one fuel and uptime basis.

Limits: Steam case uses SRK water without independent steam-table calibration; 0.08bara candidate is explicitly rejected on energy closure. Turbine map/exhaust are synthetic; no combustor or complete combined-cycle balance is claimed. Dated taxes and illustrative scenario prices are distinguished; carbon accounting uses explicit fuel/slip/GWP boundaries.

Source SHA-256: `188a014298ebb93abca071034fe1c20b8247aef1b21f0d6c6ea22c0b69ba3e0a`. Exact code hashes, classification, primary references and concrete issue/correction pairs are in the matching JSON chapter entry.

## Supplementary solution checks

The final supplemental gate executes 7 exact cases with 71 targeted checks. It closes the six formerly execution-only property/process/screening entries and additionally checks the repaired synthetic BIP regression. Full details and tolerances are in foundations_remaining_solution_checks.json.

The raw saturation-trace portions in Chapters02,03,09 and12 are explicitly unaccepted as complete physical envelopes; successful API execution is retained as diagnostic evidence only. The original Chapter03 BIP recipe was replaced by an explicitly oil-rich illustrative recipe after its821.1bara dense-phase candidate failed the vapor/liquid bracket. The accepted171.167bara case and connected synthetic regression pass fresh vapor/liquid, material and fugacity checks.
