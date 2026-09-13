# Supplementary manuscript solution checks

**PASS — seven cases, 71 direct acceptance checks**, with additional phase material/fugacity residuals retained in JSON.

The six prior execution-only entries now have concrete solution checks. The seventh case strengthens the connected synthetic BIP regression. These numerical checks do not calibrate engineering correlations, mechanical ratings or field data.

| Chapter / Python fence | Verified scope | Result |
|---|---|---|
| ch01_introduction / 5 | Coupled three-area process actual separator/valve/compressor/cooler material and energy closure, configured outputP/T, positive compression work. | pass |
| ch03_fluid_characterization / 8 | Modified-BIP bubble point finite domain and fresh TP phase-transition brackets; no fitted data or BIP calibration claimed. | pass |
| ch03_fluid_characterization / 9 | Synthetic BIP recovery and pressure residual plus fresh TP vapor/liquid transition at fitted recipe; not laboratory calibration. | pass |
| ch04_reservoir_engineering / 6 | Wellhead TP flash closure, specified flow/T/P and independent ideal-standard gas-equivalent conversion at288.15K101325Pa; standard-equivalent total flow is not separated gas production. | pass |
| ch05_well_performance / 8 | Independent continuous least-squares Vogel fit, residual recomputation, pressure/rate domain and zero-flow/AOFP limits.1.5bar solver grid permits0.751bar fit error; curve interpolation permits0.3%. | pass |
| ch07_subsea_production_systems / 5 | Dimensional mechanical/cost screening: casing/tubing geometry domain, independent tubing mass conversion, itemized total-cost closure; no casing load-case, barrier functional or cost-model validation. | pass |
| ch11_oil_processing / 3 | Three equilibrium bubble pressures: kPa/bar conversion, monotone vapor-pressure trend and independently rerun TP phase-transition brackets. NotASTM Reid vapor pressure. | pass |

The initial rejected BIP result is archived in foundations_remaining_solution_checks_initial.json. Its821.1bara candidate led to dense oil-labelled phase splitting, so it is not presented as an accepted vapor/liquid bubble point. The revised oil-rich recipe yields171.167bara at100C and vapor fractions0.000771/0 in fresh below/above TP brackets. This is a changed teaching fluid, clearly disclosed in the manuscript.

No acceptance tolerance was loosened. The Vogel fit is compared with an independent continuous least-squares optimum using a0.751bara limit dictated by the source1.5bara search grid; tubing weight uses the exact pound conversion with a2e-5relative allowance for the source rounded0.4536kg/lb constant.
