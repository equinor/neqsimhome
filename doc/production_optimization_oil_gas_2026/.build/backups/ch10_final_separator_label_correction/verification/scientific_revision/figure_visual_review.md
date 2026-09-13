# Notebook figure visual and scientific review

104 freshly executed chapter notebook figures and one independent NIST benchmark plot. Legacy manuscript illustrations are outside this audit and tracked separately.

Visual inspection by the reviewing agent of all 18 retained six-image contact sheets, 16 representative/repaired full-resolution views, and automatic CSV-to-metadata reconciliation. Material repairs were made in generating plot cells and all 35 notebooks rerun before final hashes.

**105/105 images inspected; 11 plot cells repaired; 16 full-resolution views; no unresolved material visual defect.** 302 exported series and 7480 rows reconcile with saved metadata at 1e-12 absolute/relative tolerance.

## Repairs and scientific qualifications

- Figure 26: Title explicitly identifies the constant-temperature case as isothermal; the seawater line is an ambient reference, not a heat-transfer calculation.
- Figure 27: Separated inlet/outlet annotations so both points can be identified.
- Figure 28: Moved the operating-point annotation clear of the annular-region label and explicitly marked the regime map illustrative.
- Figure 29: Moved narrow pressure-budget labels outside their bars; all seven increments and arrival pressure are readable.
- Figure 40: Moved the 8 bara optimum annotation below the title; maximum stock-tank liquid rate is 32.023 tonnes/h.
- Figure 44: Placed the two-axis legend above both bar series; API gravity and density retain distinct axes and units.
- Figure 49: Replaced the unreferenced typical C3+ specification with an illustrative 5 mol% limit; composition is not a dew-point certificate.
- Figure 72: Replaced the unreferenced typical pressure-drop specification with an illustrative 50 bar limit.
- Figure 87: Moved the combined two-axis legend above the bars so the 243 tonnes/h label is visible.
- Figure 91: Expanded the vertical scale using the actual data maximum; the low-gain overshoot near 64.5% is no longer clipped.
- Figure 93: Labelled the fraction as NeqSim gas-labelled phase fraction. Separate TP-flash probes confirmed the high-pressure unit fraction belongs to a single gas-labelled phase; the plot does not locate a critical point.

## Scope limits

- This is a scoped scientific/visual review of teaching examples, not field calibration or universal equipment certification.
- PNG/CSV export captures plotted line, bar and scatter series, but not full data for all filled plots or contours. The notebook physical ledger and native retained arrays are the evidence for those plot types.
- Pressure-budget bars encode pressure differences in bar; their position is absolute pressure in bara. Compressor map and operating limits are teaching inputs, not manufacturer ratings.
- Timing results depend on JVM warm-up and machine load and are not a controlled performance benchmark.
- Conceptual regime maps and idealized controller examples are explicitly illustrative; they are not measured plant behaviour.

## Inspected file inventory

| Image | Chapter | File | Full resolution | Data evidence |
|---|---|---|---|---|
| 1 | ch01_introduction | fig01_density_vs_pressure.png | contact sheet | passed |
| 2 | ch01_introduction | fig02_z_factor_vs_pressure.png | contact sheet | passed |
| 3 | ch01_introduction | fig03_phase_envelope.png | contact sheet | passed |
| 4 | ch01_introduction | fig04_production_sensitivity.png | contact sheet | passed |
| 5 | ch02_thermodynamic_foundations | fig01_density_srk_vs_pr.png | contact sheet | passed |
| 6 | ch02_thermodynamic_foundations | fig02_cp_vs_temperature.png | contact sheet | passed |
| 7 | ch02_thermodynamic_foundations | fig03_enthalpy_vs_temperature.png | contact sheet | passed |
| 8 | ch02_thermodynamic_foundations | fig04_viscosity_vs_pressure.png | contact sheet | passed |
| 9 | ch02_thermodynamic_foundations | fig05_jt_coefficient_vs_pressure.png | contact sheet | passed |
| 10 | ch03_fluid_characterization | fig01_molecular_weight_distribution.png | contact sheet | passed |
| 11 | ch03_fluid_characterization | fig02_phase_envelope_condensate.png | contact sheet | passed |
| 12 | ch03_fluid_characterization | fig03_liquid_dropout_curve.png | contact sheet | passed |
| 13 | ch03_fluid_characterization | fig04_gor_vs_pressure.png | contact sheet | passed |
| 14 | ch03_fluid_characterization | fig05_bo_vs_pressure.png | contact sheet | passed |
| 15 | ch04_reservoir_engineering | ch04_fig01_ipr_curves.png | contact sheet | passed |
| 16 | ch04_reservoir_engineering | ch04_fig02_gor_vs_pressure.png | contact sheet | passed |
| 17 | ch04_reservoir_engineering | ch04_fig03_density_vs_depth.png | contact sheet | passed |
| 18 | ch04_reservoir_engineering | ch04_fig04_rel_perm_curves.png | contact sheet | passed |
| 19 | ch05_well_performance | ch05_fig01_vlp_curves.png | contact sheet | passed |
| 20 | ch05_well_performance | ch05_fig02_operating_point.png | contact sheet | passed |
| 21 | ch05_well_performance | ch05_fig03_gas_lift_optimization.png | contact sheet | passed |
| 22 | ch05_well_performance | ch05_fig04_watercut_effect.png | contact sheet | passed |
| 23 | ch06_wells_artificial_lift | ch15w_choke_sensitivity.png | contact sheet | passed |
| 24 | ch06_wells_artificial_lift | ch15w_well_network_comparison.png | contact sheet | passed |
| 25 | ch07_subsea_production_systems | ch06_fig01_pressure_profile.png | contact sheet | passed |
| 26 | ch07_subsea_production_systems | ch06_fig02_temperature_profile.png | yes | passed |
| 27 | ch07_subsea_production_systems | ch06_fig03_hydrate_risk.png | yes | passed |
| 28 | ch07_subsea_production_systems | ch06_fig04_flow_regime_map.png | yes | passed |
| 29 | ch07_subsea_production_systems | ch06_fig05_pressure_budget.png | yes | passed |
| 30 | ch08_flowlines_and_risers | fig01_pressure_drop_vs_diameter.png | contact sheet | passed |
| 31 | ch08_flowlines_and_risers | fig02_pressure_drop_vs_flow.png | contact sheet | passed |
| 32 | ch08_flowlines_and_risers | fig03_liquid_holdup.png | contact sheet | passed |
| 33 | ch08_flowlines_and_risers | fig04_pipeline_capacity.png | contact sheet | passed |
| 34 | ch09_flow_assurance | fig01_hydrate_equilibrium.png | contact sheet | passed |
| 35 | ch09_flow_assurance | fig02_meg_inhibition.png | contact sheet | passed |
| 36 | ch09_flow_assurance | fig03_water_dewpoint.png | contact sheet | passed |
| 37 | ch09_flow_assurance | fig04_hydrate_operating_envelope.png | contact sheet | passed |
| 38 | ch10_separation_technology | fig01_phase_split.png | contact sheet | no_line_bar_scatter_data |
| 39 | ch10_separation_technology | fig02_souders_brown.png | contact sheet | passed |
| 40 | ch10_separation_technology | fig03_separator_optimization.png | yes | passed |
| 41 | ch10_separation_technology | fig04_separation_train.png | contact sheet | passed |
| 42 | ch11_oil_processing | fig10_1_rvp_vs_temperature.png | contact sheet | passed |
| 43 | ch11_oil_processing | fig10_2_api_vs_pressure.png | contact sheet | passed |
| 44 | ch11_oil_processing | fig10_3_multistage_oil_quality.png | yes | passed |
| 45 | ch11_oil_processing | fig10_4_gas_shrinkage.png | contact sheet | passed |
| 46 | ch12_gas_processing | fig11_1_water_content.png | contact sheet | passed |
| 47 | ch12_gas_processing | fig11_2_jt_cooling.png | contact sheet | passed |
| 48 | ch12_gas_processing | fig11_3_turbo_expander_profile.png | contact sheet | passed |
| 49 | ch12_gas_processing | fig11_4_dewpoint_control.png | yes | passed |
| 50 | ch13_produced_water_treatment | ch16_watercut_sensitivity.png | contact sheet | passed |
| 51 | ch13_produced_water_treatment | ch16_pressure_effect.png | contact sheet | passed |
| 52 | ch14_gas_compression | fig12_1_power_vs_ratio.png | contact sheet | passed |
| 53 | ch14_gas_compression | fig12_2_compressor_curve.png | contact sheet | passed |
| 54 | ch14_gas_compression | fig12_3_multistage_profile.png | contact sheet | passed |
| 55 | ch14_gas_compression | fig12_4_power_comparison.png | contact sheet | passed |
| 56 | ch14_gas_compression | fig12_5_discharge_temperature.png | contact sheet | passed |
| 57 | ch15_compressor_characteristics | ch13_head_vs_flow.png | contact sheet | passed |
| 58 | ch15_compressor_characteristics | ch13_efficiency_vs_flow.png | contact sheet | passed |
| 59 | ch15_compressor_characteristics | ch13_operating_envelope.png | yes | passed |
| 60 | ch16_heat_exchangers | ch14_temperature_profile.png | yes | passed |
| 61 | ch16_heat_exchangers | ch14_duty_vs_flow.png | contact sheet | passed |
| 62 | ch16_heat_exchangers | ch14_ua_sizing.png | contact sheet | passed |
| 63 | ch17_valves_and_flow_control | ch15_cv_and_jt_vs_flow.png | contact sheet | passed |
| 64 | ch17_valves_and_flow_control | ch15_jt_cooling_vs_dp.png | contact sheet | passed |
| 65 | ch17_valves_and_flow_control | ch15_pt_path.png | contact sheet | passed |
| 66 | ch17_valves_and_flow_control | ch15_valve_opening.png | contact sheet | passed |
| 67 | ch18_power_production | ch30_fuel_consumption.png | contact sheet | passed |
| 68 | ch18_power_production | ch30_power_demand_pie.png | contact sheet | no_line_bar_scatter_data |
| 69 | ch18_power_production | ch30_gt_ambient_temp.png | contact sheet | passed |
| 70 | ch18_power_production | ch30_co2_emissions.png | contact sheet | passed |
| 71 | ch19_export_and_metering | ch17_pipeline_profiles.png | contact sheet | passed |
| 72 | ch19_export_and_metering | ch17_diameter_sensitivity.png | yes | passed |
| 73 | ch20_capacity_checks_and_utilization | ch18_utilization_bar_chart.png | contact sheet | passed |
| 74 | ch20_capacity_checks_and_utilization | ch18_utilization_vs_feed_rate.png | contact sheet | passed |
| 75 | ch21_debottlenecking | ch21_debottleneck_cascade.png | contact sheet | passed |
| 76 | ch22_production_optimization_theory | ch19_objective_function_landscape.png | contact sheet | passed |
| 77 | ch22_production_optimization_theory | ch19_sensitivity_tornado.png | contact sheet | passed |
| 78 | ch23_neqsim_optimization_framework | ch25_utilization_vs_rate.png | contact sheet | passed |
| 79 | ch23_neqsim_optimization_framework | ch25_feasibility_curve.png | contact sheet | passed |
| 80 | ch24_production_optimization | ch18_optimization_convergence.png | contact sheet | passed |
| 81 | ch24_production_optimization | ch18_algorithm_comparison.png | contact sheet | passed |
| 82 | ch25_utilization_monitoring | ch26_utilization_heatmap.png | contact sheet | no_line_bar_scatter_data |
| 83 | ch25_utilization_monitoring | ch26_bottleneck_transition.png | contact sheet | passed |
| 84 | ch26_well_network_optimization | ch27_manifold_pressure_sweep.png | contact sheet | passed |
| 85 | ch26_well_network_optimization | ch27_choke_sensitivity.png | contact sheet | passed |
| 86 | ch27_multi_scenario_optimization | ch28_scenario_utilization.png | contact sheet | passed |
| 87 | ch27_multi_scenario_optimization | ch28_scenario_comparison.png | yes | passed |
| 88 | ch28_field_development | ch19_vfp_curves.png | contact sheet | passed |
| 89 | ch28_field_development | ch19_vfp_surface.png | yes | no_line_bar_scatter_data |
| 90 | ch29_dynamic_simulation_and_control | ch20_level_controller_response.png | contact sheet | passed |
| 91 | ch29_dynamic_simulation_and_control | ch20_pid_tuning_comparison.png | yes | passed |
| 92 | ch30_digital_twins_and_automation | ch21_digital_twin_comparison.png | contact sheet | passed |
| 93 | ch31_solver_methods | ch29_flash_convergence.png | yes | passed |
| 94 | ch31_solver_methods | ch29_initial_guess_effect.png | contact sheet | passed |
| 95 | ch31_solver_methods | ch29_recycle_convergence.png | contact sheet | passed |
| 96 | ch31_solver_methods | ch29_component_scaling.png | contact sheet | passed |
| 97 | ch32_advanced_topics | ch22_pareto_front.png | contact sheet | passed |
| 98 | ch32_advanced_topics | ch22_scenario_comparison.png | contact sheet | passed |
| 99 | ch33_onshore_processing_plants | ch22_teg_water_content.png | yes | passed |
| 100 | ch33_onshore_processing_plants | ch22_compression_power.png | contact sheet | passed |
| 101 | ch34_case_studies | ch23_process_conditions.png | contact sheet | passed |
| 102 | ch34_case_studies | ch23_power_consumption.png | contact sheet | passed |
| 103 | ch35_future_directions | ch35_co2_density_compressibility.png | contact sheet | passed |
| 104 | ch35_future_directions | ch24_h2_blending_wobbe.png | contact sheet | passed |
| 105 | 36_benchmark | nist_methane_density_validation.png | yes | benchmark_results_provenance |

The JSON companion retains absolute paths, final image/CSV/metadata hashes, original contact-sheet hashes and per-image findings. Native retained arrays and their physical checks are in the chapter execution reports and notebook_physics_review.json.
