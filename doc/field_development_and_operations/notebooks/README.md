# TPG4230 Notebook Distribution Bundle

This folder contains the final Jupyter notebooks distributed with *Field Development and Operations: A Computational Approach with NeqSim*.

## Contents

- Notebooks: 78
- Layout: flat folder, one `.ipynb` file per notebook
- Manifest: `manifest.json` maps each notebook back to its source chapter path
- Requirements: `requirements.txt` lists the Python packages used by the notebooks

## Quality Status

- No placeholder/scaffold notebook text remains.
- Every notebook has at least one stored code-cell output.
- No notebook contains stored error outputs.
- Every cell has `metadata.id` and `metadata.language` for stable editor handling.

## Running the Notebooks

Install the public dependencies with:

```bash
pip install -r requirements.txt
```

Most notebooks use the public `neqsim` Python package. A small number of advanced Chapter 26/production-optimisation notebooks use the repository developer setup when available so they can exercise newer Java APIs before a public wheel release.

When notebooks generate figures, they write to `../figures` relative to this folder, which matches the book submission layout.

## Notebook Index

- `1_3_value_chain.ipynb` ? Introduction to Field Development and Operations — 1.3 The Oil and Gas Value Chain at a Glance
- `1_4_stakeholders.ipynb` ? Introduction to Field Development and Operations — 1.4 Stakeholders and Their Roles
- `1_5_lifecycle_profile.ipynb` ? Introduction to Field Development and Operations — 1.5 The Petroleum Field Lifecycle
- `1_6_cost_influence.ipynb` ? Introduction to Field Development and Operations — 1.6 Why Early Decisions Dominate Value
- `1_8_neqsim_intro.ipynb` ? Introduction to Field Development and Operations — 1.8 Computational Tools and the Role of NeqSim
- `1_9_mini_field.ipynb` ? Introduction to Field Development and Operations — 1.9 Worked Example — A Mini Field Development Study
- `snippet_01_1_12_the_role_of_neqsim.ipynb` ? ch01_introduction — 1.12 The role of NeqSim
- `ch02_s01_value_chain.ipynb` ? The Oil and Gas Value Chain — From Reservoir to Consumer: A Walk-through
- `ch02_s05_stakeholder_map.ipynb` ? The Oil and Gas Value Chain — Stakeholders and Decision Rights
- `snippet_01_2_11_neqsim_implementation.ipynb` ? ch02_oil_gas_value_chain — 2.11 NeqSim implementation
- `ch03_s01_phase_envelope.ipynb` ? Reservoir Fluids and PVT Behaviour — Reservoir-Fluid Classification
- `ch03_s04_eos_comparison.ipynb` ? Reservoir Fluids and PVT Behaviour — Setting up an EOS in NeqSim
- `ch03_s06_cvd_experiment.ipynb` ? Reservoir Fluids and PVT Behaviour — PVT Laboratory Experiments
- `ch03_s08_p1_envelope.ipynb` ? Reservoir Fluids and PVT Behaviour — Worked Case: P1 Fluid Composition
- `snippet_01_3_10_neqsim_implementation.ipynb` ? ch03_reservoir_fluids_pvt — 3.10 NeqSim implementation
- `ch04_s03_flow_pattern_map.ipynb` ? Flow Performance in Production Systems — Two-phase Flow Patterns and Correlations
- `ch04_s06_ipr_vlp.ipynb` ? Flow Performance in Production Systems — Nodal Analysis
- `ch04_s07_pipe_profile.ipynb` ? Flow Performance in Production Systems — NeqSim Pipe Flow Implementation
- `snippet_01_4_9_neqsim_implementation.ipynb` ? ch04_flow_performance_production_systems — 4.9 NeqSim implementation
- `ch05_s02_concept_screen.ipynb` ? Facilities in the Value Chain — Selection Drivers
- `snippet_01_5_10_neqsim_a_simplified_topside.ipynb` ? ch05_facilities_value_chain — 5.10 NeqSim — a simplified topside
- `ch06_s01_pfd.ipynb` ? Introduction to Oil and Gas Processing — Generic Topsides PFD
- `ch06_s05_neqsim_flowsheet.ipynb` ? Introduction to Oil and Gas Processing — Building a Flowsheet in NeqSim
- `snippet_01_6_10_neqsim_multi_stage_flash_example.ipynb` ? ch06_intro_oil_gas_processing — 6.10 NeqSim — multi-stage flash example
- `ch07_s01_separator.ipynb` ? Oil and Water Processing and Separator Design — Three-phase Separation Principles
- `ch07_s04_mp_optimisation.ipynb` ? Oil and Water Processing and Separator Design — Multi-stage Separation Strategy
- `ch07_s05_train_results.ipynb` ? Oil and Water Processing and Separator Design — Worked Example: P1 Three-stage Train
- `snippet_01_7_10_neqsim_mechanical_design_example.ipynb` ? ch07_oil_water_separator_design — 7.10 NeqSim mechanical-design example
- `ch08_s03_hydrate_curve.ipynb` ? Flow Assurance and Gas Processing — Hydrate Inhibition
- `snippet_01_8_2_gas_hydrates.ipynb` ? ch08_flow_assurance_gas_processing — 8.2 Gas hydrates
- `snippet_02_8_8_process_modelling_for_flow_assurance.ipynb` ? ch08_flow_assurance_gas_processing — 8.8 Process modelling for flow assurance
- `ch09_s02_compression_power.ipynb` ? Dry Gas Production Systems — Multi-stage Compression Design
- `snippet_01_9_3_dewpoint_thermodynamics.ipynb` ? ch09_dry_gas_production_systems — 9.3 Dewpoint thermodynamics
- `ch10_s02_teg_contactor.ipynb` ? Acid Gas Removal and Dehydration — TEG Dehydration
- `ch10_s04_amine_column.ipynb` ? Acid Gas Removal and Dehydration — Amine Sweetening
- `snippet_01_10_2_dehydration.ipynb` ? ch10_acid_gas_removal_dehydration — 10.2 Dehydration
- `ch11_01_digital_twin_and_lifecycle.ipynb` ? Field Development Digital Twin and Lifecycle
- `ch11_02_concept_evaluation_framework.ipynb` ? Field Concept Evaluation: From Definition to Multi-Criterion Assessment
- `ch11_03_screening_and_feasibility.ipynb` ? Technical Screening and Feasibility Assessment
- `ch11_neqsim_field_development_building_blocks.ipynb` ? NeqSim Field-Development Building Blocks
- `ch11_s01_gates.ipynb` ? Field Development: Concepts, Gates and Deliverables — From Discovery to Sanction
- `ch11_s02_influence.ipynb` ? Field Development: Concepts, Gates and Deliverables — Cost-Influence Curve and FEL
- `ch11_s06_concept_screen.ipynb` ? Field Development: Concepts, Gates and Deliverables — Concept Selection (DG2)
- `ch13_02_surf_equipment_design_cost.ipynb` ? SURF Equipment Design and Cost Estimation
- `ch13_neqsim_tieback_subsea.ipynb` ? NeqSim Tieback and Subsea Screening
- `ch13_s01_layout.ipynb` ? Subsea Production Systems and SURF — Subsea Architecture
- `snippet_01_13_6_subsea_costs_and_neqsim.ipynb` ? ch13_subsea_surf_systems — 13.6 Subsea costs and NeqSim
- `snippet_01_14_2_casing_design_api_5c3_and_norsok_d_.ipynb` ? ch14_drilling_and_wells — 14.2 Casing design — API 5C3 and NORSOK D-010
- `ch15_s04_profile.ipynb` ? Reservoir Technology in Field Development — Production Forecasting
- `snippet_01_15_6_reservoir_simulation.ipynb` ? ch15_reservoir_technology — 15.6 Reservoir simulation
- `snippet_01_17_9_neqsim_cost_estimation_tooling.ipynb` ? ch17_cost_estimation_scheduling — 17.9 NeqSim cost-estimation tooling
- `ch18_s01_cashflow.ipynb` ? Economic Analysis: NPV, IRR, Fiscal Regimes and Uncertainty — Cash-Flow Model Building Blocks
- `ch18_s04_tornado.ipynb` ? Economic Analysis: NPV, IRR, Fiscal Regimes and Uncertainty — Exlandian Fiscal Regime (Ultima Thule case)
- `ch18_s07_mc_histogram.ipynb` ? Economic Analysis: NPV, IRR, Fiscal Regimes and Uncertainty — Monte-Carlo Probabilistic NPV (P3)
- `snippet_01_18_12_neqsim_economic_tooling.ipynb` ? ch18_economic_analysis_npv — 18.12 NeqSim economic tooling
- `ch19_s01_layout.ipynb` ? Production Scheduling — The Snøhvit Case — Snøhvit Field Overview
- `ch19_s03_base.ipynb` ? Production Scheduling — The Snøhvit Case — Base-Case Plateau and Decline
- `ch19_s07_set_model.ipynb` ? §19.12 The Production-Potential Tank Model (SET Model)
- `snippet_01_19_6_production_profile_fitting_in_neqsi.ipynb` ? ch19_production_scheduling_snohvit — 19.6 Production profile fitting in NeqSim
- `ch20_03_cash_flow_engine_and_economics.ipynb` ? Cash Flow Engine and Field Economics
- `ch20_04_network_optimization_gas_lift.ipynb` ? Production Network Optimization: Multi-Well Gathering and Gas Lift Allocation
- `ch20_neqsim_network_and_gas_lift.ipynb` ? NeqSim Network and Gas-Lift Screening
- `ch20_s03_mp_opt.ipynb` ? Production Optimisation — Separation Pressure Optimisation (P1.1)
- `snippet_01_20_3_neqsim_optimisation_toolkit.ipynb` ? ch20_production_optimisation — 20.3 NeqSim optimisation toolkit
- `snippet_02_20_8_worked_example_gas_lift_allocation_.ipynb` ? ch20_production_optimisation — 20.8 Worked example — gas-lift allocation field-wide
- `snippet_01_22_2_calorific_value_and_wobbe_index_iso.ipynb` ? Chapter 22 — ISO 6976 Gas Quality Example
- `ch23_s04_co2_envelope.ipynb` ? CO₂ in Field Development and Operations — CO₂ Pipeline Transport
- `ch24_02_field_development_api_mastery.ipynb` ? Field Development API Mastery
- `ch24_10_tieback_screening.ipynb` ? Tieback Screening with NeqSim
- `ch24_11_tieback_vs_standalone.ipynb` ? Tieback vs Standalone Concept Comparison
- `ch24_12_probabilistic_concept_selection.ipynb` ? Probabilistic Concept Selection
- `ch24_neqsim_field_development_framework.ipynb` ? NeqSim Field-Development Framework Map
- `ch24_s04_neqsim_pfd.ipynb` ? Computational Tools for Field Development — Building a Topsides Model
- `snippet_01_24_4_creating_a_fluid.ipynb` ? ch24_computational_tools_neqsim — 24.4 Creating a fluid
- `snippet_02_24_13_example_tpg4230_mini_task.ipynb` ? ch24_computational_tools_neqsim — 24.13 Example — TPG4230 mini-task
- `ch25_s02_snohvit.ipynb` ? Field Development Case Studies — Snøhvit — Subsea-to-Beach
- `ch25_s03_ut_concept.ipynb` ? Field Development Case Studies — Ultima Thule — Deep-water Oil
- `snippet_01_25_1_aasta_hansteen_overview.ipynb` ? ch25_case_studies_aasta_ultima_thule — 25.1 Aasta Hansteen — overview
