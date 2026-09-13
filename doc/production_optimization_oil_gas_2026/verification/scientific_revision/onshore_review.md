# Chapter 33 scientific review

The complete chapter was rewritten after a scientific read-through. All nine current literal Python blocks executed successfully, including the explicit thermodynamic and engineering acceptance assertions.

The retained run includes 146 unit/stage/whole-plant balance evaluations, a rebuilt input round trip and seven independently rebuilt temperature cases. Every checked mass, component and energy residual is below its declared tolerance.

## Corrected issues

- **Inventory sizing:** Separated transient surge accumulation from residence-time inventory and defined standard/actual volume bases.
- **Amine circulation:** Restored solvent molar mass in the solution mass-flow relation; separated loadings, weight fraction and circulation.
- **Hydrogen sulfide:** Replaced unsupported concentration/consequence claims with the NIOSH 100 ppm IDLH value and a primary citation.
- **TEG composition:** Converted 99.5 mass% lean solution to molar amounts; the old molar recipe did not represent the stated concentration.
- **TEG energy conservation:** Exposed the native approximate absorber residual and solved an explicit fixed-composition outlet-temperature energy reconstruction; retained the raw residual.
- **Cryogenic pretreatment:** Defined the numerical feed as dry and acid-gas-free; distinguished TEG dew-point reduction from molecular-sieve cryogenic pretreatment.
- **Heat exchange boundary:** Replaced unsupported one-sided heat-recovery credit with a cooler having an explicit external thermal duty.
- **Expander inlet:** Added a knockout separator, gas-only expansion and separate liquid letdown/remixing to avoid expanding a wet two-phase feed as turbine gas.
- **Expander efficiency:** Corrected the efficiency/temperature relation; lower efficiency produces less cooling at fixed pressure ratio.
- **Refrigeration:** Used enthalpy duty without adding latent heat twice; stated the Carnot COP upper bound and utility-model requirement.
- **Recovery basis:** Computed recovery by component molar flow rather than mixed-phase volume ratios, accounting for all loss paths.
- **Distillation shortcuts:** Corrected the saturated-liquid Underwood formulation and its root interval, with an independently checked binary example.
- **Column acceptance:** Replaced a failed large column with a converged equilibrium-stage stabilizer and explicit stage heat input, stage energy and MESH gates.
- **Column duty accounting:** Matched reboiler heatInput to the stage-energy boundary; rejected a fixed-temperature result that appeared solved while failing rigorous energy residuals.
- **Sulfur recovery:** Corrected sulfur atom accounting and removed an ambiguous reaction-enthalpy value without a specified sulfur reference state.
- **Ethane storage:** Used NIST boiling/critical properties and removed an unsupported ambient-pressure liquid-storage guarantee near the critical temperature.
- **Plant scope:** Replaced the claimed complete raw-gas plant with an explicit three-area dry-gas teaching flowsheet; standalone TEG is a separate model.
- **Product specification:** Reported 2.2246 mol% methane in stabilizer bottoms as a calculated composition, without claiming an untested storage/product specification.
- **Export constraint:** Made 70 bara export pressure an explicit requirement rather than treating low-pressure gas as sales-ready production.
- **Energy objective:** Reported gross compression, recovered expansion and thermal cooling separately; no shaft coupling or utility conversion is silently assumed.
- **Persistence:** Rebuilt from a checked input specification rather than claiming an unverified whole-state archive proves reproducibility.
- **Sensitivity:** Rebuilt every plant for seven temperatures and retained the nonmonotonic recovery maximum under fixed stabilizer heat input.
- **Design numbers:** Removed universal cost, recovery, life and capacity claims without a documented basis.
- **Exercises and standards:** Labeled design assignments and standards scope explicitly; no unsolved exercise or catalogue citation is represented as an executed design or compliance proof.

## Exact published-code evidence

- Block 1 — bindings and conservation helper: Reusable mass, each-component and enthalpy/work/heat residual calculations are exercised by all subsequent process cases.
- Block 2 — surge inventory: Independent dimensional arithmetic: 60 m3 of accumulated liquid from flow imbalance and duration.
- Block 3 — amine circulation: Independent dimensional arithmetic: 67.8974 kg/s of lean solution including solvent molar mass, weight fraction and loading change.
- Block 4 — TEG contactor: Mass, each component and explicit corrected energy boundary; raw energy residual retained. Positive heat capacities/densities, single retained phase and bounded temperature correction.
- Block 5 — ideal-gas expansion limit: Analytical temperature/efficiency relation, correct sign of work and temperature drop.
- Block 6 — binary shortcut distillation: Independent Fenske/Underwood/Gilliland assumptions; saturated-liquid binary Underwood root 4/3 and minimum reflux 1.7.
- Block 7 — complete dry-gas plant: Unit and whole-plant mass/component/energy balances, rigorous column status and MESH residual, independent fugacity equality and reconstructed expander efficiency.
- Block 8 — automation and saved input record: Pressure readback matches the accepted process; fresh model rebuild from the serialized input specification reproduces export/product/energy results.
- Block 9 — seven-case temperature sweep and scientific figure: Fresh whole-plant rebuild at each temperature; all physical acceptance checks, component recovery plus every loss path sums to one; plot uses executed data and separate heat/shaft-power quantities.

## Scope of the evidence

- Conservation, equilibrium and reconstructed efficiency are solution verification; the same EOS is not an independent experimental reference.
- No measured performance data were available for this synthetic plant or TEG case; no field calibration is claimed.
- SimpleTEGAbsorber water transfer remains an approximate stage-efficiency model; the explicit energy reconstruction does not make it a rigorous rate-based contactor.
- The small stabilizer is a converged teaching calculation, not a sized or validated commercial fractionation train.
- Only the specified dry feed, pressure, temperature and duty range is covered by the executed plant checks.
- References to safety values and standards do not establish a facility safety assessment or regulatory compliance.

The machine-readable ledger records every current code-block hash and points to the complete numerical execution record.
