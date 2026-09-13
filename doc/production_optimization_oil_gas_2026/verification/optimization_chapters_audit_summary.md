# Manuscript execution audit: chapters19–35

Source commit: `6cc8026202a5d3f9383c9abd1d97d448993813f9`.
Generated: 2026-09-12T22:35:11.000574+00:00.

| Chapter | Executed successfully | Integration patterns | Unresolved or stale |
|---|---:|---:|---:|
| ch19_export_and_metering | 8 | 0 | 0 |
| ch20_capacity_checks_and_utilization | 11 | 0 | 0 |
| ch21_debottlenecking | 39 | 0 | 0 |
| ch22_production_optimization_theory | 9 | 0 | 0 |
| ch23_neqsim_optimization_framework | 39 | 0 | 0 |
| ch24_production_optimization | 73 | 9 | 0 |
| ch25_utilization_monitoring | 16 | 1 | 0 |
| ch26_well_network_optimization | 14 | 3 | 0 |
| ch27_multi_scenario_optimization | 8 | 0 | 0 |
| ch28_field_development | 19 | 5 | 0 |
| ch29_dynamic_simulation_and_control | 13 | 0 | 0 |
| ch30_digital_twins_and_automation | 22 | 7 | 0 |
| ch31_solver_methods | 5 | 2 | 0 |
| ch32_advanced_topics | 23 | 2 | 0 |
| ch33_onshore_processing_plants | 9 | 0 | 0 |
| ch34_case_studies | 8 | 1 | 0 |
| ch35_future_directions | 6 | 0 | 0 |

## Scope and interpretation

- Python examples execute sequentially in a fresh source-backed JVM per chapter; they are not standalone isolated unit tests.
- Java examples execute in a chapter-scoped JShell host; complete public examples with main methods are invoked. This is not a separate Java8 compilation of each fragment.
- Passed means executed without a Python exception or Java compile/runtime diagnostic in the declared context. It does not establish model calibration, design compliance, every branch, or field validation.
- Annotated integration patterns require the listed files, external data, optional packages, trained models or engineering adapters and are not reported as executed.
- Chapter29 manuscript transients include inventory, energy and time-step checks; the companion notebook separately illustrates a lumped controller model. Neither constitutes field calibration.
- Chapter32 includes an accepted optimizer point, fresh-model replay and an independently enumerated bracket. Synthetic calibration data remain an estimator exercise.
- Chapter33 checks each unit, stage and whole-plant material and energy boundary; it reconstructs an approximate TEG outlet energy state explicitly and rebuilds from saved inputs. This is not experimental validation of the synthetic plant.
- Simple compressor throughput screens use power constraints; generated automatic-size charts are not installed compressor evidence.

## Reproducibility

Use the user-selected bundled Python runtime and the book-local `.build/python_packages` directory. The runners load `neqsim_dev_setup` from the declared source checkout, never a packaged NeqSim fallback. Each ledger row records the exact current code SHA256 and the underlying execution report. Notebook outcomes and rendered-PDF inspection are reported separately by the book release workflow.

The Chapter33 sensitivity figure is generated from seven fresh accepted whole-plant calculations; recovery uses component molar flow and thermal/shaft duties remain separate.

All runnable fences currently pass the execution/freshness gate: **True**.
Totals: `{"java_integration_pattern": 2, "java_passed": 111, "python_integration_pattern": 28, "python_passed": 211}`.
