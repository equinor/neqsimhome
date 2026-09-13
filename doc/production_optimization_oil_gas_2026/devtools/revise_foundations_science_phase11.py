"""Final hydraulic and separation scientific corrections, retaining explicit assumptions."""
from revise_foundations_science_phase3 import R, S

R('ch08','inclination_attribution', '**Step 3: Correct for inclination** using the Payne et al. (1979) correction:', '**Step 3: Correct for inclination** using the Beggs–Brill inclination multiplier. A separately enabled Payne correction is an additional empirical holdup adjustment; it is not the definition of this multiplier:')
R('ch08','friction_multiplier', 'a correction factor that accounts for the roughness of the gas-liquid interface.', 'an empirical two-phase correction based on no-slip liquid fraction and liquid holdup; it is not a direct measurement of interfacial roughness.')
S('ch08','mukherjee_complete', r'Mukherjee and Brill \(1985\) developed an alternative correlation.*?(?=### 8.4.3)', 'Mukherjee–Brill correlates liquid holdup using inclination and dimensionless gas velocity, liquid velocity and viscosity groups, with distinct coefficients and regime conditions. The previously abbreviated four-term expression omitted required velocity dependencies and is not a usable implementation. Use the complete published correlation with its regime rules and consistent units when making a comparison.\n\n')
S('ch08','correlation_accuracy', r'\| Correlation \| Year \| Inclination Range \| Flow Regimes \| Accuracy \|.*?\| OLGA \(mechanistic\).*?\n', '''| Method | Required comparison basis |
|--------|---------------------------|
| Beggs–Brill | Experimental inclination, fluid and diameter range; distinguish original and optional corrections |
| Mukherjee–Brill | Original regime-specific coefficients and inclination coverage |
| Duns–Ros | Upward vertical gas–liquid flow and the original regime map |
| Hagedorn–Brown | Vertical well flow; check viscosity, diameter and liquid loading extrapolation |
| Mechanistic models | Closure correlations, transient boundary conditions and validation data for the particular implementation |

No universal pressure-drop accuracy percentage ranks these methods. Compare them against the same independent measurements, including measurement uncertainty, fluid properties and flow regime; a mechanistic formulation still contains empirical closures.
''')
R('ch08','mechanistic_extrapolation', 'The advantage of mechanistic models is their broader range of applicability and improved prediction outside the experimental data range used to develop empirical correlations.', 'Mechanistic models can represent additional mechanisms and transitions, but extrapolation beyond their closure-correlation validation range is not automatically more accurate.')
S('ch08','slack_condition', r'The onset of slack flow depends.*?\\text\{Slack flow if:.*?\$\$', r'''With inclination positive upward, gravity dominates friction in a descending, full-bore liquid segment when

$$\rho_L g |\sin\theta| > \frac{f_D\rho_L v^2}{2D},\qquad \theta<0.$$

This comparison alone is not a slack-flow criterion. Slack flow requires a loss of full-bore liquid occupancy, determined by the boundary heads, available inventory and local absolute pressure relative to vapor pressure. A vapor cavity or entrained-gas region requires an appropriate multiphase/transient model.''')
R('ch08','pig_inventory', 'The total slug volume at the pipeline outlet can be estimated as:', 'An inventory screening bound for liquid collected from the listed sections is:')
R('ch08','JT_enthalpy_scope', 'NeqSim automatically accounts for the JT effect in its pipeline calculations through rigorous enthalpy balance.', 'In the example, the pressure–enthalpy flash accounts for real-fluid temperature change as pressure falls, while a specified overall heat-transfer coefficient accounts for external cooling. The optional additional JT-heat and friction-heating switches remain disabled: adding a separate JT heat term to an enthalpy formulation would double count that mechanism. The present checks cover finite profiles, mass conservation and pressure direction; they do not independently validate the pipeline heat-loss closure.')

R('ch10','pressure_physics', '**Settling velocity scales with $\\Delta\\rho$** — as pressure increases, gas density increases and oil density decreases, reducing the driving force. High-pressure separators are less efficient.', '**Settling speed scales with the magnitude of $\\Delta\\rho$** at otherwise fixed droplet size and viscosity. Pressure changes phase compositions, densities, gas volume and interfacial tension together. A lower density difference alone does not establish lower separator efficiency: at fixed gas mass flow the actual gas velocity also changes.')
R('ch10','settling_sign', '- $v_t$ is the terminal settling velocity [m/s]', '- $v_t$ is the signed terminal velocity, positive downward for a denser droplet [m/s]; use $|v_t|$ and $|\\rho_d-\\rho_c|$ when calculating a rising-bubble speed or Reynolds number')
S('ch10','pressure_derating', r'\*\*Pressure correction\*\*.*?(?=### 10.3.4)', r'''**Additional derating** — the Souders–Brown density term already uses gas and liquid densities at operating pressure. Any extra factor must have an identified internals/vendor or test basis covering pressure, interfacial tension, liquid loading and service. A universal pressure-only lookup is not justified.

$$K_{\mathrm{effective}}=K_{\mathrm{reference}}F_{\mathrm{service}}.$$

The worked calculation assumes $K_{\mathrm{reference}}=0.107$ m/s and $F_{\mathrm{service}}=0.82$ as a stated screening case, giving $K_{\mathrm{effective}}=0.08774$ m/s. These inputs are not a vendor capacity guarantee or a prescribed 70 bara correction.

''')
R('ch10','derating_code', 'F_P = 0.82  # Pressure correction at 70 bara', 'F_P = 0.82  # Assumed service derating; not a universal pressure correlation')
R('ch10','derating_step', '- Apply pressure correction', '- Apply an additional service derating only when supported by the selected internals/test basis')
R('ch10','horizontal_settling', '- Verify gas velocity < terminal velocity (with safety factor)', '- For upward vertical gas flow, check gas velocity against downward droplet speed. For horizontal flow, compare vertical settling time across the gas space with axial gas residence time, including distribution and internals effects.')
R('ch10','bubble_settling', '- Verify liquid velocity < terminal velocity (with safety factor)', '- Compare bubble rise time through the liquid depth with liquid residence time; a horizontal liquid velocity cannot be compared directly with a vertical rise speed as a universal removal criterion.')
R('ch10','utilization_threshold', 'When $u_{\\text{gasLoadFactor}} \\geq 1.0$, the gas velocity exceeds the design limit, and liquid carryover into the gas outlet increases dramatically.', 'At $u_{\\text{gasLoadFactor}}=1$, the selected model capacity is reached; above unity it is exceeded. This scalar check does not quantify carryover or establish a sharp physical flooding transition without an internals performance model and supporting data.')

R('ch04','remaining_resource', '- The current position gives the remaining reserves', '- Under the volumetric, isothermal, closed-tank assumptions, $G-G_p$ is remaining gas in place on the same standard-volume basis; recoverable reserves additionally require an abandonment and commercial-development assessment')
R('ch04','condensate_Z', 'For gas condensate reservoirs, the two-phase Z-factor $Z_{\\text{2ph}}$ from the CVD experiment (Chapter 3) should be used instead of the single-phase $Z$ to account for the liquid dropout in the reservoir.', 'For gas-condensate depletion, use a compositional material balance consistent with the evolving reservoir inventory and produced composition. A two-phase volume factor inferred from CVD may support a defined depletion path; simply replacing $Z$ in the dry-gas straight line does not generally restore linearity when composition, phase inventory or produced gas composition changes.')
R('ch04','banking_range', 'The productivity reduction can be severe — 50–80% reduction in gas PI — and is not captured by simple IPR models.', 'The productivity reduction depends on condensate saturation, relative permeability, capillary number and the near-well pressure/composition path; no universal 50–80% PI penalty follows from crossing the dew point. A fixed single-phase IPR does not resolve this mechanism.')
