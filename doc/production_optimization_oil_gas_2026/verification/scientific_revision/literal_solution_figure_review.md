# Exact-literal solution figures

PASS: three actual plots visually inspected by the reviewing agent and reconciled against accepted full-precision arrays.

**ch22_verified_nodal_solution.png:** Original-resolution view inspected. The IPR and forward tubing curves meet at the plotted operating star; the dotted reservoir bound is distinct. No line bridges unavailable TPR states. Legend and rejection annotation are clear of data, and gas-rate/BHP units match the retained values.

The coupled solution is 2.30293 MSm³/day at 245.829 bara bottomhole pressure and 80.000 bara wellhead pressure. Friction and elevation increase required BHP with rate. Tested rates of 2.5–3.5 MSm³/day cannot reach the 80 bara target below the 250 bara reservoir pressure and are excluded from the curve. This is a numerical consistency check for the declared IPR and steady tubing model; calibration and a thermal wellbore model remain separate requirements.

SHA-256: `8130558ad5bbf8a6f64cfd67b69e10b743ae2b3c29daede0cea743391242006c`.

**ch22_verified_interstage_power.png:** Original-resolution view inspected. Total duty and the two stage duties have separate panels so the shallow total-power minimum remains visible. The 70 bara sampled minimum and 61.24 bara equal-ratio reference are distinct. All axes/legends are readable and correctly use MW and bara.

The lowest sampled total duty is 15.352 MW at 70 bara. Raising interstage pressure transfers duty from stage 2 to stage 1. The equal-ratio reference is 61.24 bara; unequal efficiencies, different stage-inlet temperatures and real-fluid properties shift the sampled minimum. Each stage and the whole cooled boundary satisfy mass, component and first-law checks. Refine the pressure grid and add equipment maps and temperature limits before an operating recommendation.

SHA-256: `abb5bc53ec13a93e586fa2a495cc625b5b4eb35dcd14e09f44cfc77f659a5667`.

**ch22_verified_pareto_samples.png:** Original-resolution view inspected. All eleven actual objective pairs are visible; the 70 bara nondominated sample is highlighted. Oil is labeled separator mass in t/h, rather than stock-tank volume. The title and adjacent discussion explicitly state that this sample set has one dominating point.

At 70 bara the sample gives 153.384 t/h separator oil and 1.120 MW compression duty, dominating the other ten tested pressures in these two objectives. Higher pressure retains more material in the separator liquid while reducing compression ratio. The calculation therefore does not demonstrate an oil–power trade-off. Liquid is measured at separator conditions; stock-tank stabilization, well response and additional constraints could change the objective landscape.

SHA-256: `c875352d13fdf6abeeb6efce2dae3e8f331555dfb7184b7b2cc785ad923204d1`.
