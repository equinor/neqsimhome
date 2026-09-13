# Literal-run figure visual review

passed_scoped_visual_and_caption_review.

Visual inspection by the reviewing agent of all eight source images with their adjacent chapter captions/prose, plus reconciliation of retained numerical arrays or literal-run scalar evidence. This is agent review, not human/domain peer certification.

All eight actual images were displayed. The water-cut image was tool-resized from 1980×1381 to 1881×1312; all labels were readable. Image/source-copy hashes match the copy manifest.

| # | Figure | Finding |
|---|---|---|
| 1 | fig28_tornado.png | Labels distinguish kg/h gas-rate response from water mole fraction, pressure, temperature and efficiency inputs. Low/high colors mean input endpoints, not unfavorable/favorable outcomes. Zero efficiency response is physically appropriate and explained in the caption. Bars agree with retained endpoint calculations.  |
| 2 | ch27_verified_resource_npv.png | Histogram counts and empirical CDF have distinct y axes; both use pre-tax NPV in MNOK. Both 200-scenario policies are named consistently. Aggressive has a higher median and upper tail in these samples, while no universal dominance, investment guarantee or robust optimum is claimed.  |
| 3 | ch29_verified_level_inventory.png | Level/diameter is dimensionless; pressure is bara; liquid withdrawal is kg/s; time is seconds. Solid and dashed timestep curves are nearly coincident. Small staircase features in the level signal are visible rather than cosmetically smoothed. The final 30.639 bara pressure and near-setpoint level agree with prose.  |
| 4 | ch29_verified_blowdown.png | Both absolute pressure and Celsius fluid temperature decline over 120 s. Fine/coarse trajectories overlap, consistent with the saved timestep comparison. The final 52.975 bara and 9.119 C agree with prose; the caption does not imply wall-temperature or relief-system qualification.  |
| 5 | ch29_verified_feed_pulse.png | A 20–40 s prescribed total-feed pulse raises the dimensionless level to about 0.5112, below the displayed 0.60 test limit, then returns toward 0.50. Legend and text distinguish the stress-test feed history from predicted slug generation. No trace is clipped or hidden.  |
| 6 | ch23_case1_hp_optimization.png | Both panels are readable and use bara, tonnes/h and MW consistently. Liquid mass has a shallow sampled maximum near 85 bara while compression power falls with pressure. Surrounding text correctly distinguishes process consistency from installed capacity and economic optimization.  |
| 7 | ch23_case2_water_cut_sensitivity.png | Four panels identify the reference conditions for feed water cut and keep local-state product volumes separate. Oil/gas/power decrease as water replaces hydrocarbon at fixed reference liquid rate. The first-separator utilization remains well below the explicitly assumed 400 m3/h limit; no false water-cut bottleneck appears.  |
| 8 | ch23_case3_debottleneck_analysis.png | Both panels show all nine feed-rate points, including the 130% point above the expander screen. The right panel reports total withdrawn liquid mass in tonnes/h. Corrected reader-facing legend names the three screening quantities and the feed-reference label has proper spaces.  |

## Numerical evidence checked

- **1:** {"base_gas_kg_hr": 39353.10572530252, "ranked_swings_kg_hr": [["Feed rate (kg/hr)", 34433.96750963968], ["Water mole fraction (-)", 14186.33046184984], ["Feed pressure (bara)", 1951.1413675448275], ["Temperature (C)", 1238.1575341965436], ["Isentropic efficiency (-)", 0.0]], "reconciliation": "All ten endpoint-minus-base gas rates agree with plotted deltas to 1e-9 kg/h; compressor efficiency has exactly zero upstream gas response."}
- **2:** {"Conservative": {"sample_count": 200, "npv_min_max_MNOK": [11759.28563181631, 78946.23899398206], "npv_CDF_P10_P50_P90_MNOK": [26799.680981055702, 42572.618177312674, 63551.70832926569]}, "Aggressive": {"sample_count": 200, "npv_min_max_MNOK": [9692.958465837775, 101629.55370179912], "npv_CDF_P10_P50_P90_MNOK": [30946.097682060416, 50776.62036414444, 81058.62912309937]}}
- **3:** {"fine_final_series_row": [120.0, 0.50048828125, 30.638975903665266, 40.08495539138437, 697.2206387822127, 1.8423406786263214], "coarse_fine_aligned_max_differences": [0.0001220703125, 0.000271551819896132], "difference_acceptance_limits": [0.001, 0.01], "fine_max_mass_relative_residual": 2.1345911840196278e-15, "fine_max_energy_relative_residual": 4.4767743136168996e-06, "level_peak_fraction": 0.5045166015625, "level_final_offset_percentage_points": 0.048828125}
- **4:** {"fine_final_series_row": [120.0, 52.97548737244282, 9.119298806455049, 100.9274384376304, 0.23983120585978374], "coarse_fine_aligned_max_differences": [0.013611519754086032, 0.034594094427859545], "difference_acceptance_limits": [0.05, 0.1], "fine_max_mass_relative_residual": 1.1543031308321625e-15, "fine_max_energy_relative_residual": 0.0004608642043813972}
- **5:** {"reported_peak_level_fraction": 0.51123046875, "declared_test_limit_fraction": 0.6, "margin_below_test_limit_fraction": 0.08876953124999998, "literal_code_sha256": "19f7193ab78aa24396ba962b0a6429862a75a851db3a1efaf8e4df62d19c5021", "scope": "Prescribed total-feed pulse, not a predicted slug-arrival model; retained scalar output and plot inspected, no complete pulse series was retained in this evidence file."}
- **6:** {"pressure_range_bara": [60.0, 100.0], "sampled_max_liquid_t_hr": 130.68288740547433, "pressure_at_sampled_max_bara": 85.0, "power_first_last_MW": [19.087941744316396, 9.76152871988804], "scope": "All withdrawn liquid is aggregated by mass; the sampled maximum is not an economic optimum or stock-tank volume."}
- **7:** {"water_cut_first_last_pct": [10.000000000001087, 80.0], "oil_first_last_m3_hr": [191.6543429535022, 42.604239029710904], "water_first_last_m3_hr": [20.721417140826183, 165.17576283850894], "compression_first_last_MW": [0.3947992764753307, 0.08711083482332202], "first_separator_liquid_utilization_first_last_pct": [57.17470928872874, 52.84519212711061], "scope": "Feed water cut uses 15 C/1.01325 bara reference liquid; displayed final oil and first-separator water are separate local-state volumes, not a common product-volume balance."}
- **8:** {"feed_percent_first_last": [90.0, 130.0], "liquids_first_last_t_hr": [112.34698908391118, 162.27898422547517], "utilization_last_pct": {"inlet_gas_MSm3day": 87.02814175498352, "expander_MW": 101.61502315188145, "residue_comp_MW": 29.58438390034941}, "scope": "130% feed case exceeds the declared expander-power screen; plotted rejected point is intentionally retained. These three screens are not a complete plant rating."}

## Scope limits

- This visual audit does not replace the separately retained process-physics gate or independently validate field applicability.
- Timestep plots qualify only the stated numerical cases and intervals.
- Economic samples use specified illustrative distributions/policies; they do not establish investment suitability.
- Whole-book PDF size, pagination and accessibility remain separate publication checks.

## Final image hashes

| # | SHA-256 |
|---|---|
| 1 | `808b9d902c42fc3262b613e2d63eaeffbb0366735a8b22bc4e6cd9d81cd8eded` |
| 2 | `c9b914a337e14224465b1d5b9a3a19699981fc8fe1df8d7af28b86c23cbbaeca` |
| 3 | `a1e18dab02b398b2f607a90e3997acdeee8cf708b06b04ed275d0e12ee3b0661` |
| 4 | `4f80b5e48694a4c42f06138d531d427d8f513840faa8414aaab64daa3a93eef5` |
| 5 | `a67e2ebd7f7c301ff6c1d77430a9fba923804907ec5ce38b4cd0f8c4f60e0d19` |
| 6 | `a215f2054389f955af01745228f2f12528965e00df921966a79d6e9d8a26b968` |
| 7 | `c65904773289c318026dfe69c6de18c23d9a4b0be8825e0b58b7e98ad904e75e` |
| 8 | `2b0b22e7e8df5a5171e51e93f4b8a4a15c745a389b2ab015c41d83a55d18a988` |

Copy manifest SHA-256: `2314ef39d7ea07eb0dfd060d8fa51619ceb8b7e2ce4f8cc1726fb56bd7f388a7`.
The JSON report retains full paths, image dimensions, source-copy equality, caption text, adjacent excerpts, and numerical-evidence hashes.
