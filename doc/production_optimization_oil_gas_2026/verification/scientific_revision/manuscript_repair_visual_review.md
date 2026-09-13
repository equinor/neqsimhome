# Repaired manuscript illustration review

Completed 2026-09-12T20:49:31.003093+00:00. **PASS within the stated scope:** 20 images reviewed, four contact sheets, 10 distinct full-resolution views, all five corrected images re-inspected, and 20 equation/data/topology checks. No unresolved material findings.

Twenty repaired manuscript illustrations: actual contact-sheet visual inspection by the reviewing agent, representative full-resolution review, all changed images re-inspected at full resolution, caption/topology checks, and independent equation/data consistency checks. Synthetic illustrations are not external process-model validation; only the NIST plot inherits independent reference-fluid comparison evidence.

The initial contact sheets and their image hashes are retained. The final five repaired images were viewed individually. The editor corrected four label/legend issues and added the missing amine flash-gas outlet; the gas-lift formula received a white background after its move. Visual inspection was performed by the reviewing agent. It does not constitute human or domain-peer certification. The reviewer did not modify manuscript text or images.

## Figure-by-figure findings

| # | Figure | Review |
|---|---|---|
| 1 | ch04_reservoir_engineering: horner_plot.png | Reversed log-x axis correctly moves toward Horner ratio one at the right. Buildup approaches 330 bara; relocated formula is clear of the curve. |
| 2 | ch04_reservoir_engineering: nodal_analysis.png | Axes identify BHP and liquid rate. Diameter ordering and the three marked intersections match the analytical roots. Upper-axis clipping affects only high-pressure extensions outside the intersections. |
| 3 | ch05_well_performance: log_diagnostic.png | Logarithmic axes, derivative definition and approximately 10 bar plateau agree with the declared formula. Late boundary response is explicitly imposed. |
| 4 | ch13_produced_water_treatment: water_lifecycle_profile.png | Oil/water bars and percentage water-cut axis have distinct units. The relocated lower-right legend leaves late-year bar tops visible; both liquid volumes share a reference basis. |
| 5 | ch16_heat_exchangers: composite_curves.png | Hot/cold curves do not cross. The 25 K arrow lies at the minimum vertical separation, 5 MW; caption avoids claiming a plant pinch target. |
| 6 | ch18_power_production: brayton_cycle_ts.png | Both isentropes are vertical on the T–s plane; constant-pressure branches and states 1–4 are clear. Entropy is explicitly relative and temperature is in kelvin. |
| 7 | ch20_capacity_checks_and_utilization: utilization_vs_production.png | All utilization curves visibly continue above 100%. The first threshold is the declared compressor rating; fixed assumed ratings are not presented as installed capacity. |
| 8 | ch22_production_optimization_theory: pareto_front_oil_vs_power.png | Axis directions match oil maximization and power minimization. The selected star is on the nondominated set; the caption declares synthetic alternatives and preference function. |
| 9 | ch29_dynamic_simulation_and_control: ch20_compressor_map_antisurge.png | The arrow points toward greater actual compressor inlet flow, away from the stated low-flow boundary. The caption distinguishes compressor throughflow from net export and labels the map conceptual. |
| 10 | ch30_digital_twins_and_automation: ch21_digital_twin_tracking.png | Temperature and residual panels use Celsius and kelvin correctly. Shaded offset interval, correction lag, and noisy synthetic observations are visible; the caption does not claim measured plant evidence. |
| 11 | ch12_gas_processing: gas_processing_overview.png | Treatment sequence and arrows are readable. Conditional contaminant control and cryogenic pretreatment scope match the caption. |
| 12 | ch30_digital_twins_and_automation: ch21_rto_cycle.png | Six boxes form a readable closed operational workflow, including verification and authorization before implementation. |
| 13 | ch33_onshore_processing_plants: ch22_amine_unit_pfd.png | Separate rich/lean exchanger passages, heat-transfer arrow and final flash-gas outlet resolve the previous topology omission. The visible diagram and stated omissions agree. |
| 14 | ch33_onshore_processing_plants: ch22_onshore_plant_block_diagram.png | Readable dry-feed basis and external product arrows agree with the worked process topology. Utilities are explicit and the standalone TEG example is not silently included. |
| 15 | ch33_onshore_processing_plants: ch22_turboexpander_pfd.png | Two inlet paths and two product paths are visually unambiguous. Gas-only expansion and liquid bypass are consistent with the literal worked flowsheet. |
| 16 | ch02_thermodynamic_foundations: eos_comparison.png | Parity and deviation panels show all 18 comparisons with correct density/relative-error units. Legend distinguishes SRK and PR; bounds and narrow methane-state scope are explicit. |
| 17 | ch20_capacity_checks_and_utilization: compressor_capacity_map.png | Curves, speed labels, endpoint markers and the selected marker are consistent with the formula. No accepted-region shading implies validity outside specified endpoints. |
| 18 | ch22_production_optimization_theory: separator_pressure_contour.png | Pressure axes use bara; colorbar correctly labels a dimensionless algebraic objective. Dark stationary-point text remains legible over the light contour maximum. |
| 19 | ch04_reservoir_engineering: ipr_curves.png | The three inflow curves have readable legends with distinct assumed parameters. All terminate at zero flow at 300 bara and their AOF intercepts match the caption. |
| 20 | ch05_well_performance: gas_lift_performance.png | The saturating curve, stationary marker and declared cost assumption agree. The formula occupies lower whitespace; an opaque annotation background prevents the vertical guide obscuring text. |

## Checked numerical results

- **1. Shut-in pressure approaches the stated asymptote from below:** {"first_bara": 299.9956592252068, "last_bara": 329.9567862621736, "asymptote_bara": 330}. Criterion: Strict increase with shut-in time; final deficit below 0.05 bar.
- **2. Saved intersections satisfy both pressure curves and diameter ordering:** {"rates_m3_day": [2497.8986772920794, 3268.139372653459, 3662.921148034056], "max_pressure_residual_bar": 7.105427357601002e-14}. Criterion: Residual < 1e-9 bar; strictly increasing rate with diameter.
- **3. Analytical derivative agrees with independent central differentiation in log time:** {"relative_error": 6.611583996512382e-11, "times_h": [0.001, 0.01, 0.1, 1.0, 10.0, 30.0, 200.0, 1000.0]}. Criterion: Relative error < 1e-7 at eight states away from the imposed transition.
- **4. Water cut uses the same plotted liquid volume basis:** {"max_error_percentage_points": 0.0, "first_water_cut_pct": 14.285714285714286, "last_water_cut_pct": 82.42081464469665, "final_oil_thousand_m3_day": 4.905572274612227, "final_water_thousand_m3_day": 23.0}. Criterion: Absolute error < 1e-12 percentage points and 0–100% bounds.
- **5. Both composites increase; the declared minimum gap occurs at 5 MW:** {"minimum_gap_K": 25.0, "enthalpy_at_minimum_MW": 5.0}. Criterion: Exact 25 K gap at 5 MW; no crossing.
- **6. Ideal Brayton pressure ratio, entropy closure and efficiency identities:** {"temperatures_K": [300.0, 579.209318664975, 1400.0, 725.1264550923697], "efficiency_pct": 48.20525320768788, "specific_heat_added_kJ_kg": 824.8946347417001, "specific_heat_rejected_kJ_kg": 427.2520873678315, "max_identity_error": 2.220446049250313e-16}. Criterion: Absolute identity error < 1e-12; constant cp and gamma only.
- **7. Overload is retained and the compressor is the first limit:** {"utilization_at_120_percent_demand_pct": [114.28571428571429, 130.43478260869566, 120.0], "first_limit_percent_reference": 92.0}. Criterion: No clipping above 100%; smallest declared rating 92%.
- **8. Independent exhaustive dominance and declared preference checks:** {"nondominated_count": 90, "selected_oil_m3_day": 4168.539325842697, "selected_power_MW": 15.092387324832723, "preference_score_error": 0.0}. Criterion: 90 of 250 alternatives nondominated; selected is in front and minimizes declared score to 1e-12.
- **9. Recycle arrow increases compressor throughflow:** {"start_m3_hr": 5600.0, "end_m3_hr": 8500.0}. Criterion: Rightward arrow from 5600 to 8500 m3/h; no net-export inference.
- **10. Seeded fixture and rolling residual correction reproduce saved summary:** {"mean_corrected_residual_K": 0.002769894859328405, "injected_offset_K": 3, "window_samples": 20}. Criterion: Saved-mean agreement < 1e-12 K; corrected plateau mean < 0.2 K, excluding transition lag.
- **16. Image exactly matches retained independent NIST benchmark; numerical deviations reproduce caption:** {"comparison_count": 18, "state_count": 9, "max_abs_relative_deviation_pct": {"SRK methane density": 1.4207593974357349, "PR methane density": 0.8112271996129237}, "benchmark_image_identical": true, "benchmark_results_sha256": "74e7a1670b4171276bc3dbbd3dad775d281637ac514c014da6c42a8d2c89ea86"}. Criterion: 18 comparisons at 9 NIST reference-EOS states; each deviation within declared 3% scope; identical plot hash.
- **17. Compressor-map endpoints and operating marker obey declared similarity relation:** {"max_endpoint_head_error_kJ_kg": 0.0, "marker_flow_m3_hr": 6000, "marker_head_kJ_kg": 135}. Criterion: Endpoint head errors < 1e-12 kJ/kg; decreasing head over positive-flow ranges; no installed-rating claim.
- **18. Declared contour has a feasible unique concave maximum:** {"stationary_pressures_bara": [60, 15], "hessian_eigenvalues": [-0.0022222222222222222, -0.008888888888888889], "gradient": [0.0, 0.0]}. Criterion: Gradient zero; negative definite Hessian; point within displayed domain.
- **19. Inflow curves obey no-drawdown and AOF limits with monotonic decline:** {"AOF_m3_day": [6000.0, 4500.0, 5500.0], "no_drawdown_rates_m3_day": [0.0, 0.0, 0.0]}. Criterion: Zero rate at reservoir BHP to 1e-12 m3/day; monotonically decreasing with BHP; extrapolated AOF only.
- **20. Lift net-benefit point satisfies the marginal condition and strict concavity:** {"stationary_g_thousand_Sm3_day": 77.70801496337481, "oil_at_stationary_point_m3_day": 2350.0, "marginal_oil_per_thousand_Sm3": 4.999999999999997, "second_derivative": -0.16666666666666657}. Criterion: Marginal yield equals declared cost-equivalent slope to 1e-12; negative second derivative; interior to displayed range.

## Scope and limitations

- No field calibration or vendor-map validation is inferred from analytical teaching plots.
- The NIST panel validates only methane density at its nine stated temperature/pressure states within a declared teaching tolerance.
- The two executed-plant topology drawings were checked against literal Chapter 33; this image audit does not rerun or replace the separately retained material and energy balance gate.
- This audit covers the source images and caption records. Final PDF sizing and pagination are a separate publication review.

## Final image hashes

| # | SHA-256 |
|---|---|
| 1 | `048ae0ab4e8aed157c477ed0ca1fd34976087ff9005435d15a312ec2a963809a` |
| 2 | `7d8ef9e93e5535daf4da59d6dfd3b6f48ddb5096e10424cf6a0c26d980ba0ecd` |
| 3 | `2beaa5d163328ed5bfbbcb5fab599cc751ee1521520a5c53c85e4417e7478ff5` |
| 4 | `368dd53475843e0f7ad21da97feed984d0558fccb4adb1a46d6c383625c57752` |
| 5 | `9f30d2c98bc5c2912324cb62c937ffcdeb7929835a4614128f6ff618ff2cb88b` |
| 6 | `59f89427c54bc05c48e8a6519f176c17bba39f81a1dade9482332d4bbb138e4c` |
| 7 | `9c5682e1e7a4971f4ae75e2ddf11b92ee666d866845b1c24f7f3cb6c65bf2b47` |
| 8 | `c25a1c5296216485a12bff81025517f8f7abc0dc58bf6f210721b333a086afa7` |
| 9 | `6e6648df71f93579150940215d60489cbe8e50cdeafc88101f9bf600cde34f25` |
| 10 | `329ea09edf9dc632dfbcebd24a7fd2f52f316ed2b0b2416736f3bea3be9b9064` |
| 11 | `0abef1e514081c4d80dfc65d98b71ea093c75b03f8206d99be0a912e610f7a34` |
| 12 | `008beaccbd2b044837cd1128760e8296531f6b874948282e5528b16291386552` |
| 13 | `3075f5e4d54beadf4d1da92a44d51984512bccdf055fc574dbf61cc57304ed84` |
| 14 | `95e79a4b36998db25d7eb22fb5872efffa93aa84ebd1db900f0b4ad639f6277e` |
| 15 | `75d2f8b0d94c2718d0dfccb0a05b05272e555b2d1e384f69506b21e48f4e01b0` |
| 16 | `26cb6604e75ea9e6deac74de028192df89fbbe35ea9fedac7ec6ad298546e7d2` |
| 17 | `0702beed5f3322addd94d80ac45e8d5ece67f178bde057668565006d3d27da21` |
| 18 | `b3ba84e68add2d01395285a5836e7c7ab15b83e2792a6776473bd9553cb27435` |
| 19 | `ff618f544d489042af0a0f672d89d6a4c8c86bb6c7b42e15bc6995b85dd7eed3` |
| 20 | `d4f54d6b1bd631b1463729d7411a5302ac0cf26dc45b14ad1ed712094db50ef0` |

Input manifest SHA-256: `fccf913c23503833922f0c6d6a22690997336cf875a2087b8901bf6778a5164e`.
Repair script SHA-256: `cf65dcbb3943386cc3966af6a6520e09bd7f64b2f67d113371d6210d8052b12f`.
The JSON report retains absolute paths, image dimensions, caption text, checks, initial/final inspection hashes and contact-sheet hashes.
