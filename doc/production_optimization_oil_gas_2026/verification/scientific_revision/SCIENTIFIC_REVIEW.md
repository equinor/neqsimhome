# Scientific review of the production optimization textbook

The complete 35-chapter manuscript was read for scientific quality, corrected and checked against its stated calculation basis. The revised teaching calculations have execution and engineering acceptance evidence; this is not a blanket certification of field predictive accuracy.

- Chapter notebooks: **35/35 passed, 300 code cells**.
- Literal manuscript code: **545 executable Python/Java fragments passed** in their documented sequential chapter context.
- These executable fragments include API/configuration examples and explicitly rejected native diagnostics. Execution success is not engineering acceptance; accepted numerical examples have additional scoped checks in their per-example ledgers.
- External integration patterns: **30**, explicitly identified with prerequisites and excluded from execution claims.
- Benchmark notebook: **89/89 comparisons passed**, including **18 independent NIST reference-EOS comparisons** at nine methane states. The remaining comparisons check analytical relations, balances and independent search procedures.
- Every chapter has a scientific review ledger and exact published-code hashes. All 104 notebook figures have current calculation outputs and reviewed discussions.

## What changed scientifically

- Corrected units, standard/actual volume bases, water-cut and composition definitions, component recovery and molar/mass conversions.
- Corrected metre/kilometre and vertical-flow direction errors, zero/undefined gas-quality calculations, a hundredfold capacity-percent reporting error, and economically mislabeled or dimensionally inconsistent examples.
- Replaced gas-equivalent standard-volume oil pricing with an explicit 15 C/1.01325 bara stock-tank flash, all-phase product accounting and a liquid mass/density/volume identity check. Final-separator liquid and stock-tank oil are identified separately.
- Added phase checks and knockout separation before gas compression and expansion, complete product accounting, and explicit heat and shaft-work boundaries.
- Required column energy/equilibrium residuals and rigorous convergence; rejected apparently solved but physically inconsistent column states.
- Exposed the approximate TEG absorber energy imbalance and documented the bounded fixed-composition energy reconstruction rather than hiding its native-model limitation.
- Checked selected optimization points with fresh model replay and grid/analytical comparisons; separated assumed capacity screens from installed-equipment evidence.
- Preserved the native tabulated gas-lift allocation failure as a rejected diagnostic and supplied an independently checked linear-programming allocation. Separated outside-map compressor penalties from numerical performance curves.
- Replaced flat-rate resource uncertainty with executed depletion profiles, and checked transient inventory/energy balances and timestep refinement.
- Replaced fabricated experimental plots and unsupported optimization curves; retained conceptual illustrations only with explicit synthetic assumptions.
- Reconciled legacy plots with the current accepted literal executions and their actual source arrays; corrected stale maxima, flow bases and unsupported compressor-map boundaries.
- Corrected scientific definitions, equations and reference metadata, and quarantined unverified unused bibliography entries.

## Independent validation and remaining scope

The methane density benchmark covers SRK and Peng–Robinson at 300, 350 and 400 K and 1, 50 and 100 bara. Maximum absolute relative deviations are 1.421% and 0.811%, respectively, within the declared 3% teaching accuracy budget. NIST supplies independent reference-EOS calculations, not raw experimental measurements; 3% is not NIST measurement uncertainty.

Conservation, equilibrium and solver residuals verify the implemented equations. They do not validate mixture characterization, hydrate/TEG prediction, corrosion/erosion correlations, vendor compressor maps, field hydraulics, plant dynamics or economics against measurements. Those domains retain explicit limitations in the chapter ledgers. No plant data or vendor acceptance tests were provided.

Chapter 3’s replacement phase-envelope illustration uses an explicitly different defined-compound surrogate; the original TBP trace did not pass branch checks and is not validated by that substitute. Chapter 12’s continuation gap remains open. Undefined physical states and rejected numerical candidates are documented rather than interpolated into accepted results.

Unsolved exercises remain learning assignments. API configuration examples are checked in their stated software context; optional service integrations cannot prove a live external connection. Synthetic prices, duties, ratings and control fixtures are assumptions, not measured or commercially qualified results.

## Chapter coverage

| Chapter | Executed manuscript fragments | External patterns | Checked notebook calculation |
|---|---:|---:|---|
| ch01_introduction | 6 | 0 | Natural-gas PVT and actual volume |
| ch02_thermodynamic_foundations | 11 | 0 | EOS comparisons, heat capacity, enthalpy and transport |
| ch03_fluid_characterization | 10 | 0 | CCE liquid dropout, phase volumes and sample-specific Bo |
| ch04_reservoir_engineering | 6 | 0 | PI/Vogel endpoints and Corey saturation bounds |
| ch05_well_performance | 10 | 0 | Nodal pressure residual and production bounds |
| ch06_wells_artificial_lift | 44 | 0 | Well, choke and manifold conservation |
| ch07_subsea_production_systems | 6 | 0 | Segmented flowline state and pressure budget |
| ch08_flowlines_and_risers | 7 | 0 | Hydraulic domains, holdup and diameter conversion |
| ch09_flow_assurance | 12 | 0 | Hydrate/inhibitor/dew-point domains and monotonic sensitivities |
| ch10_separation_technology | 28 | 0 | Phase mass splits and Souders-Brown identity |
| ch11_oil_processing | 7 | 0 | TVP, reference-density API gravity and staged material release |
| ch12_gas_processing | 6 | 0 | Water-content bounds, JT first law and heavy-component nesting |
| ch13_produced_water_treatment | 5 | 0 | Three-phase material conservation |
| ch14_gas_compression | 21 | 0 | Compressor first law and efficiency sensitivity |
| ch15_compressor_characteristics | 6 | 0 | Assumed compressor-map affinity scaling |
| ch16_heat_exchangers | 13 | 0 | Two-stream energy closure, driving forces and effectiveness |
| ch17_valves_and_flow_control | 13 | 0 | Valve mass and enthalpy conservation |
| ch18_power_production | 12 | 0 | Fuel-energy and annual-emissions unit identities |
| ch19_export_and_metering | 8 | 0 | Export hydraulics and calorific-value unit basis |
| ch20_capacity_checks_and_utilization | 11 | 0 | Equipment utilization domains and fixed-rating capacity sweep |
| ch21_debottlenecking | 39 | 0 | Dimensionless utilization and debottleneck arithmetic |
| ch22_production_optimization_theory | 9 | 0 | Feasible throughput bracket and search agreement |
| ch23_neqsim_optimization_framework | 39 | 0 | Power-limited optimizer feasibility and independent grid search |
| ch24_production_optimization | 73 | 9 | Manual and engine throughput feasibility |
| ch25_utilization_monitoring | 16 | 1 | Power utilization ratios |
| ch26_well_network_optimization | 14 | 3 | Network stream conservation and bounded rate response |
| ch27_multi_scenario_optimization | 8 | 0 | Selected scenario constraint satisfaction |
| ch28_field_development | 19 | 5 | VFP inverse-solution pressure residuals |
| ch29_dynamic_simulation_and_control | 13 | 0 | Lumped controller discrete inventory equation and actuator bounds |
| ch30_digital_twins_and_automation | 22 | 7 | Synthetic measurement residual and normalization identities |
| ch31_solver_methods | 5 | 2 | Recycle residuals and achieved adjuster target |
| ch32_advanced_topics | 23 | 2 | Enumerated Pareto nondominance |
| ch33_onshore_processing_plants | 9 | 0 | TEG material balance, explicit energy reconstruction and compression |
| ch34_case_studies | 8 | 1 | Integrated process material/energy accounting |
| ch35_future_directions | 6 | 0 | CO2 PVT domains and hydrogen-mixture calorific trends |

## Evidence and reproduction

`engineering_release_gate.json` binds the final chapter sources and companion evidence by SHA256. The foundations, optimization and onshore review files describe per-example checks and limitations. `benchmark_results.json` retains expected values, computed values, tolerances and references; `references/SOURCES.md` indexes archived reference data.

Use the interpreter and source checkout recorded in the book README. Notebook, literal manuscript, benchmark and publication checks are separate reproducible stages. The publication manifest identifies the exact reviewed PDF and HTML files; the prior edition is retained under `.build/pre_scientific_publication`.

PaperLab’s marker-based evidence scanner is a diagnostic, not scientific approval. Figure captions are numbered by the PDF/HTML renderers; the final structure audit verifies those labels. Retained formatting warnings and the default publisher length advisory are explained in the release report.

The PaperLab scientific-writing/traceability skills and notebook-verifier handoff were improved to preserve these distinctions, require actual figure inspection and avoid automatic approval from a discussion marker.
