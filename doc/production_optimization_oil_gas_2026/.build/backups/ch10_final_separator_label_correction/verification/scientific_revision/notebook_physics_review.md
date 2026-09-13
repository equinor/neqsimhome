# Notebook physics review

All 35 notebooks pass their stated physical and analytical checks. This is scoped verification, not universal predictive validation.

The run executed 300 code cells with 273 explicit notebook assertions. The reusable checks evaluated 153316 conditions across 9852 distinct labels; repeated evaluations are sweeps, not independent experiments.

The separate benchmark notebook passed 89 comparisons. Eighteen density comparisons use SRK and PR at nine independent NIST reference-EOS states. Remaining comparisons test analytical limits, conservation and search algorithms. Exact inputs, expected values, actual values, units and tolerances are in [benchmark_results.json](benchmark_results.json).

Physical acceptance criteria: positive absolute pressure/temperature and density; normalized overall and phase compositions; component reconstruction 1e-7 mole fraction; mass closure 1e-8 kg/s + 1e-7 relative; component flow closure 1e-7 times total inlet molar flow (minimum scale 1 mol/s); first-law closure 1e-5 times the largest absolute inlet/outlet/duty enthalpy rate (minimum 1 W). Case-specific analytical and constraint tolerances are retained in each chapter report. Missing phase quantities and rejected hydraulic candidates remain explicit.

| Chapter | Checked scope | Distinct checks | Evaluations | Rejected candidates |
|---|---|---:|---:|---:|
| 01 | Natural-gas PVT and actual volume | 76 | 948 | 0 |
| 02 | EOS comparisons, heat capacity, enthalpy and transport | 108 | 2364 | 0 |
| 03 | CCE liquid dropout, phase volumes and sample-specific Bo | 115 | 2717 | 0 |
| 04 | PI/Vogel endpoints and Corey saturation bounds | 74 | 1406 | 0 |
| 05 | Nodal pressure residual and production bounds | 182 | 6002 | 0 |
| 06 | Well, choke and manifold conservation | 423 | 1928 | 0 |
| 07 | Segmented flowline state and pressure budget | 499 | 685 | 0 |
| 08 | Hydraulic domains, holdup and diameter conversion | 223 | 6764 | 0 |
| 09 | Hydrate/inhibitor/dew-point domains and monotonic sensitivities | 33 | 33 | 0 |
| 10 | Phase mass splits and Souders-Brown identity | 599 | 5595 | 0 |
| 11 | TVP, reference-density API gravity and staged material release | 150 | 1594 | 0 |
| 12 | Water-content bounds, JT first law and heavy-component nesting | 242 | 2844 | 0 |
| 13 | Three-phase material conservation | 342 | 2986 | 0 |
| 14 | Compressor first law and efficiency sensitivity | 302 | 4346 | 0 |
| 15 | Assumed compressor-map affinity scaling | 144 | 152 | 0 |
| 16 | Two-stream energy closure, driving forces and effectiveness | 287 | 2690 | 0 |
| 17 | Valve mass and enthalpy conservation | 297 | 3493 | 0 |
| 18 | Fuel-energy and annual-emissions unit identities | 27 | 27 | 0 |
| 19 | Export hydraulics and calorific-value unit basis | 124 | 529 | 0 |
| 20 | Equipment utilization domains and fixed-rating capacity sweep | 478 | 3328 | 0 |
| 21 | Dimensionless utilization and debottleneck arithmetic | 200 | 233 | 0 |
| 22 | Feasible throughput bracket and search agreement | 672 | 13872 | 0 |
| 23 | Power-limited optimizer feasibility and independent grid search | 383 | 3819 | 0 |
| 24 | Manual and engine throughput feasibility | 634 | 3330 | 0 |
| 25 | Power utilization ratios | 576 | 9612 | 0 |
| 26 | Network stream conservation and bounded rate response | 820 | 30925 | 0 |
| 27 | Selected scenario constraint satisfaction | 141 | 26003 | 0 |
| 28 | VFP inverse-solution pressure residuals | 103 | 3604 | 0 |
| 29 | Lumped controller discrete inventory equation and actuator bounds | 124 | 154 | 0 |
| 30 | Synthetic measurement residual and normalization identities | 132 | 168 | 0 |
| 31 | Recycle residuals and achieved adjuster target | 266 | 5251 | 0 |
| 32 | Enumerated Pareto nondominance | 189 | 2101 | 0 |
| 33 | TEG material balance, explicit energy reconstruction and compression | 411 | 2709 | 0 |
| 34 | Integrated process material/energy accounting | 428 | 530 | 0 |
| 35 | CO2 PVT domains and hydrogen-mixture calorific trends | 48 | 574 | 0 |

## Scope limits by chapter

- **01.** SRK/PR methane NIST density benchmark is contextual; mixture data are not independently calibrated.
- **02.** Methane density and dilute limits benchmark EOS; no independent mixture viscosity or JT dataset.
- **03.** CCE is not CVD. TBP characterization and reservoir PVT need laboratory calibration.
- **04.** Inflow and relative-permeability curves are specified correlations; imposed depth gradients are not a coupled hydrostatic solution.
- **05.** Gas-lift response is an illustrative correlation. No measured well test or lift calibration.
- **06.** Fixed-rate manifold example is not a pressure-coupled field network validation.
- **07.** Flow-regime map and waterfall allocations are conceptual; hydrate boundary lacks external validation.
- **08.** Hydrostatic and no-flow limits do not validate Beggs-Brill against multiphase field data.
- **09.** No measured hydrate or inhibited-water dataset; composition and inhibitor basis must match the application.
- **10.** K factor and residence criteria are assumed screening inputs, not separator vendor performance.
- **11.** 37.8 C bubble pressure is TVP, not ASTM RVP. No crude assay benchmark.
- **12.** No independent gas-conditioning recovery or dew-point dataset.
- **13.** Equilibrium phase split does not predict emulsions, droplet separation or water-treatment removal efficiency.
- **14.** Independent dilute-argon limit supports equations; assumed efficiencies and temperature limits are not vendor guarantees.
- **15.** Map curves are pedagogical, not measured machine curves; no surge or choke certification.
- **16.** Linear temperature profiles interpolate endpoints; exchanger UA and fouling need design data.
- **17.** Fixed-state Cv sizing and opening sweeps do not validate cavitation, noise or vendor trim performance.
- **18.** Gas-turbine part-load curve, carbon factor and annual hours are assumptions; no emissions certification.
- **19.** ISO calculator execution is not custody-transfer certification or metering uncertainty validation.
- **20.** Autosizing establishes teaching ratings, not installed equipment capacity.
- **21.** Capacity changes are assigned scenarios; no CAPEX or production optimum is independently validated.
- **22.** Search checks use the same process model. Monotone feasibility is case-specific.
- **23.** Independent search algorithm comparison uses the same EOS; unspecified mechanical constraints remain outside scope.
- **24.** Screening constraints are not a complete installed facility envelope.
- **25.** Overloads are deliberately plotted; a positive value is not an acceptance decision.
- **26.** No independent multiwell production history; well response and boundary conditions are illustrative.
- **27.** Discrete scenario comparison is not a probability model or an uncertainty quantile.
- **28.** Measured VFP and thermal profiles are required for well prediction; analytic hydrostatics covers only a limit.
- **29.** Python lumped dynamics illustrate control; these are not NeqSim equipment transients or a calibrated plant response.
- **30.** Noise-generated observations are not independent field validation or calibration.
- **31.** Timing is machine-dependent. Convergence does not establish model accuracy.
- **32.** Efficiency is an assumed scenario/design input; tradeoffs are not an implementable optimal controller.
- **33.** Native SimpleTEGAbsorber has an energy residual after water transfer; reconstructed outlets close energy without validating stage mass transfer.
- **34.** Illustrative facility inputs lack plant calibration, operability and full equipment design evidence.
- **35.** Single-phase CO2 is not miscibility evidence; H2 Wobbe trends do not establish material compatibility or burner interchangeability.

## Diagnosed model and execution issues

- **property_initialization (chapters 12, 26).** Valve outlets may have uninitialized phase-density caches. Initialize properties before testing density; no new equilibrium flash is performed.
- **model_approximation (chapters 33).** Native SimpleTEGAbsorber transfers water after a PH flash and leaves an energy residual. The example explicitly reconstructs common outlet temperature at fixed component inventories; it does not claim native rigorous stage energy closure.
- **solver_cache_applicability (chapters 31).** Separator skips changes below 1e-6 relative input tolerance. A tighter 1e-7 recycle demonstration now creates fresh separator phase allocations rather than weakening conservation assertions.
- **sensitivity_applicability (chapters 21, 33).** Utilization can rise when both capacity and loads increase; warm solvent can cause a shallow water-content minimum. Replaced unjustified monotonic assertions with the actual case equations and material-removal bounds.
- **reference_basis (chapters 19).** ISO6976 real-gas relative density differs from the ideal molecular-weight ratio. Verified Wobbe=GHV/sqrt(relative density) on the same ISO basis.

## Provenance

Source revision: `6cc8026202a5d3f9383c9abd1d97d448993813f9`. Selected interpreter: `C:\Users\solbraa\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.

[Primary source archive](references/SOURCES.md) · [Executed independent benchmark notebook](36_benchmark_validation.ipynb) · [Machine-readable ledger and hashes](notebook_physics_review.json)

No production Java code was changed. Post-execution edits only clarify notebook discussions and add benchmark links; executed code hashes were rechecked and artifact hashes refreshed.
