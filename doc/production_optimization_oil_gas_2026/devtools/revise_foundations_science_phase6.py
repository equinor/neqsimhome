"""Resolve remaining known scientific overclaims with stated model boundaries."""
from revise_foundations_science_phase3 import R,S,BOOK
R('ch03','API_classes','| > 40 | Light oil / condensate |\n| 30–40 | Medium oil |\n| 22–30 | Heavy oil |\n| < 22 | Extra heavy oil |','| > 31.1 | Light oil (illustrative convention) |\n| 22.3–31.1 | Medium oil |\n| 10–22.3 | Heavy oil |\n| < 10 | Extra-heavy oil |')
R('ch03','recomb_basis',r'\text{GOR}\,\frac{P^{\text{sc}}M_o}{Z^{\text{sc}} R T^{\text{sc}}\rho_o^{\text{sc}}}',r'\mathrm{GOR}_{g,sc/o,sep}\,\frac{P^{sc}M_{o,sep}}{Z^{sc}RT^{sc}\rho_{o,sep}}')
S('ch03','recomb_basis_explanation',r'In practice, the laboratory adjusts the GOR slightly.*?self-consistent sample\.',r'''Here the gas standard volume is divided by the separator-liquid volume, and $M_{o,sep},\rho_{o,sep}$ describe that same sampled liquid. A producing GOR per stock-tank oil volume needs the separator-to-stock-tank shrinkage and flash-gas accounting first. Recombination ratios are measured inputs with uncertainty; changing them solely to force a saturation-pressure match can conceal sample loss or inconsistent bases.''')
S('ch03','incomplete_critical_correlations',r'Each pseudo-component needs critical properties\. Several correlations are available:.*?(?=### 3\.5\.5)',r'''Each pseudo-component needs molecular weight, density and estimated critical/acentric properties. Lee–Kesler and Twu correlations use boiling point and specific gravity with specific unit systems and fitted reference-fluid relations. An expression ending in an ellipsis, or a reference-paraffin expression without the specific-gravity correction, cannot be used as a complete correlation. Use the documented NeqSim characterization model or the complete cited original method, retain its units and validity range, and check the resulting saturation pressure and density against the PVT sample. The next example performs the implemented characterization directly.

''')
R('ch03','Pedersen_year','Pedersen, K. S., Thomassen, P., & Fredenslund, A. (1989). Thermodynamics of petroleum mixtures containing heavy hydrocarbons.','Pedersen, K. S., Thomassen, P., & Fredenslund, A. (1985). Thermodynamics of petroleum mixtures containing heavy hydrocarbons.')
S('ch10','settling_example',r'4\. \*\*Small droplets are very slow\*\*.*?gravity alone\.',r'''4. **Droplet size and continuous-phase viscosity both matter.** For rigid-sphere Stokes settling in water, $d=100$µm, $\Delta\rho=200$kg/m³ and $\mu_c=0.001$Pa·s give $v_t=1.09$mm/s; at10µm the result is0.0109mm/s. These values describe oil droplets rising in water, not oil settling in gas. Verify the resulting droplet Reynolds number and interfacial behavior before using Stokes drag.''')
S('ch10','autosize_source',r'The `autoSize\(designMargin\)` method performs the following steps:.*?(?=### 10\.17\.2)',r'''The argument is a **capacity multiplier**:1.2 requests20% above the operating basis. The implementation calls mechanical sizing using the current phase rates and design settings, then exposes capacity constraints. It does not justify increasing an existing vessel's allowable K-factor by20%. The resulting utilization depends on rounded geometry and whichever gas/liquid/inlet constraint governs; it is not necessarily83%.

For an existing vessel, retain its actual diameter, level, internals and validated limits while changing process conditions. For a new vessel, inspect the generated mechanical design, selected factors and constraint values before accepting a capacity increase. Repeatedly resizing during a production sweep changes the equipment and cannot reveal the installed vessel's bottleneck.

''',sources=['NeqSim source 6cc8026202a5: Separator.autoSize and SeparatorMechanicalDesign.calcDesign'])
S('ch10','constraint_table',r'\| Constraint Name \| Physical Limit \| Typical Design Value \| Standard \|.*?(?=The gas load factor constraint)',r'''| Constraint | Physical question | Required basis |
|------------|-------------------|----------------|
| Gas load factor | Is gas velocity within the internals envelope? | Installed geometry and vendor/service K-factor |
| Liquid/water residence | Is available volume sufficient at the actual level? | Separation/foam/emulsion tests and control-volume basis |
| Droplet removal | Is carry-over acceptable for the downstream duty? | Inlet droplet distribution and efficiency curve |
| Inlet momentum | Does the inlet device remain within its tested range? | Device-specific momentum and pressure-drop limits |

These are distinct mechanisms, not universal numerical clauses of NORSOK/API. Confirm the actual constraints returned by the selected class and configuration.

''')
R('ch10','K_factor_summary','K-factors range from 0.06 m/s (bare vessel) to 0.25 m/s (axial cyclone demister) and must be corrected for elevated pressure','K-factors depend on the internals and fluid service; any additional pressure derating needs a vendor or measured basis, without double-counting the density dependence already in Souders–Brown')
R('ch11','stocktank_axis','plt.ylabel("Stock-Tank Oil Rate (kg/hr)", fontsize=12)','plt.ylabel("Final 1.5 bara Liquid Rate (kg/hr)", fontsize=12)')
R('ch11','rvp_variable','rvp = calculate_tvp(stream, 37.8)','tvp_37_8 = calculate_tvp(stream, 37.8)')
R('ch11','rvp_print','{rvp:.1f} kPa','{tvp_37_8:.1f} kPa')
S('ch11','stabilizer_intro',r'### 11\.9\.4 Stabilizer Column Modeling\n.*?(?=```python)',r'''### 11.9.4 Stabilizer Column Modeling

The first column has five equilibrium contacting stages plus an equilibrium reboiler, no condenser and a specified60kW heat input. Top/bottom pressures are8/8.5bara; the calculated bottoms temperature is about107.1°C and both products have positive flow. The second, deliberately smaller comparison uses one contact plus reboiler and400kW on a different feed condition. Strict MESH and individual-stage balances are checked for both. Comparing their oil yields with a flash does not establish superior recovery at equal product quality: pressures, feed heating, duty and vapor-pressure specifications must first be equalized.

''')
S('ch12','TEG_example_intro',r'### 12\.7\.1 TEG Dehydration System\n.*?(?=```python)',r'''### 12.7.1 TEG Absorber Calculation with NeqSim

This is a once-through five-equilibrium-stage contactor. The raw feed is flashed in a three-phase inlet scrubber, and only its saturated gas enters the absorber. The lean solution is99.5wt%TEG at43°C and5,000kg/hr; specifying0.995 as a mole fraction would describe a different solvent. Regeneration, stripping gas, solvent inventory and tray hydraulic efficiency are outside this boundary. The code enforces mass, energy and MESH convergence before reporting dry-gas water content.

''')
S('ch12','ngl_example_intro',r'### 12\.7\.3 NGL Fractionation — Deethanizer Example\n.*?(?=```python)',r'''### 12.7.3 NGL Stripping Calculation with NeqSim

The defined cold NGL mixture below is an assumed feed recipe, independent of the upstream example. A small stabilizer with one contacting stage, an equilibrium reboiler and100kW heat input converges with enforced MESH/energy gates. It illustrates stripping and duty accounting; it has no condenser/reflux and does not establish a deethanizer product specification. A five-stage100kW candidate was rejected at a MESH residual of8.79×10⁻⁵ against1×10⁻⁵; increasing model complexity requires a new feasible design, not relaxed acceptance.

''')
