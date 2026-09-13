"""Apply the reviewed scientific replacement chapter, preserving notebook evidence."""
from pathlib import Path
import re
BOOK = Path(__file__).resolve().parents[1]
chapter = BOOK / 'chapters/ch33_onshore_processing_plants/chapter.md'
old = chapter.read_text(encoding='utf-8')
notebook_section = re.search(r'<!-- reviewed-notebook-results:start -->.*?<!-- reviewed-notebook-results:end -->', old, re.S)[0]
models = (BOOK / 'devtools/ch33_verified_models.py').read_text(encoding='utf-8')
helpers, model = models.split('def build_dry_plant', 1)
helpers = helpers.split('\n', 1)[1]
model = 'def build_dry_plant' + model
text = r'''# Onshore Gas Processing Plants

## Learning Objectives

After studying this chapter, the reader will be able to:

1. Select process boundaries and distinguish sales-gas treating from cryogenic pretreatment.
2. Separate liquid inventory estimates from transient slug-catcher sizing.
3. Explain amine and TEG absorption, solvent loading, regeneration and their model requirements.
4. Compare JT expansion, refrigeration and expansion with work recovery on a common energy basis.
5. Apply component recovery, minimum-reflux and rigorous column-convergence checks.
6. Build and verify a three-area NeqSim hydrocarbon-processing model, including its internal and whole-plant balances.
7. Identify the product-quality, utility, hydraulic and evidence constraints needed for plant optimization.

The worked cryogenic model starts with an explicitly dry, acid-gas-free hydrocarbon feed. A separate CPA example covers TEG absorption with an external lean-solvent supply. These boundaries make the calculations reproducible without implying that an unmodeled treating or regeneration unit has met a product specification.

## 33.1 Process Configuration and Boundaries

An onshore gas plant can separate feed into residue gas, condensate and individual natural-gas-liquid (NGL) products. Sour-gas processing may also produce elemental sulfur. The economic task is to select the product slate and operating conditions that meet delivery requirements at the best achievable margin. Maximum liquid recovery alone is not the objective: extracted components lose their value in the gas stream, and recovery consumes utilities and capacity.

Onshore and offshore plants use the same thermodynamics. Their practical constraints differ, but neither location determines an achievable recovery by itself.

| Design consideration | Offshore emphasis | Onshore emphasis |
|---|---|---|
| Weight and footprint | Deck loads, lifting and module envelope | Foundations, plot availability, access and separation distances |
| Utilities | Local generation and heat integration | Available grid, fuel, water and heat-rejection infrastructure |
| Maintenance | Marine access and weather windows | Road access, lifting and shutdown arrangements |
| Processing depth | Selected against transport and topsides constraints | Selected against feed, market and utility constraints |
| Redundancy | Availability benefit versus weight and cost | Availability benefit versus installed cost and common-cause failures |

*Table 33.1: Design considerations. Neither column supplies a cost estimate, recovery guarantee or universal plant configuration.*

A possible process sequence is inlet separation, acid-gas treatment, dehydration, NGL recovery and fractionation. Cryogenic service can require additional deep drying, CO2 control and mercury removal before aluminum equipment. Molecular-sieve drying is commonly used for cryogenic feeds; a pipeline water specification or a TEG calculation alone does not demonstrate freeze-free operation \cite{uopMercuryRemoval2026}.

![Conceptual block flow diagram of an onshore gas-processing complex; the selected configuration depends on feed and products](figures/ch22_onshore_plant_block_diagram.png)

The diagram shows possible areas and material paths. It is a process concept, not the exact simulated flowsheet in Section 33.10. The worked model declares its narrower dry-hydrocarbon boundary and accounts for every product crossing that boundary.

## 33.2 Inlet Receiving and Conservation Checks

### 33.2.1 Liquid inventory and slug storage

Pipeline liquid inventory is

$$
V_{L,\mathrm{inventory}}=\int_0^L A(x)H_L(x)\,dx
\simeq\sum_j A_j L_j H_{L,j}.
$$

This expression has units of volume. It does not predict how much liquid arrives together during a pigging event or terrain-induced slug. A storage calculation requires the arrival history and the permitted drain rate. With a consistent liquid-volume basis,

$$
V_L(t)=V_L(0)+\int_0^t[Q_{L,\mathrm{in}}(\tau)-Q_{L,\mathrm{out}}(\tau)]\,d\tau,
\qquad
V_{\mathrm{surge,required}}=\max_t V_L(t)-V_{L,\mathrm{normal}}.
$$

Determine the usable storage between normal and maximum allowable levels, then add the project-specific uncertainty allowance. Flashing liquids need mass accumulation and a pressure-dependent volume conversion. A steady pipeline holdup estimate can support an inventory screen; it does not replace a transient arrival study. Vessel and finger-type slug catchers differ in geometry, drainage and gas-liquid disengagement, so equal gross volume does not establish equal performance.

### 33.2.2 Separator design and model scope

The Souders–Brown screen introduced in Chapter 10 is

$$
v_{G,\max}=K_{SB}\sqrt{(\rho_L-\rho_G)/\rho_G}.
$$

The coefficient $K_{SB}$ has units m/s and depends on internals, droplets, service and the required carryover. Use a supported value for the selected equipment. An equilibrium separator calculates phase splitting; it does not establish demister capacity, liquid residence time or transient surge performance.

For every nonreacting steady unit, verify total and component mass flow. Neglecting kinetic and potential energy changes, the energy balance is

$$
\sum_{\mathrm{in}}\dot m h+\dot Q+\dot W_{\mathrm{in}}
=\sum_{\mathrm{out}}\dot m h.
$$

Positive heat or work enters the control volume. The helper below checks the actual inlet and outlet streams, including trace-component scaling. Its tolerance of $10^{-5}$ is a numerical solution requirement, not an estimate of EOS accuracy. Execute the chapter blocks in order after initializing the workspace NeqSim runtime described in Chapter 2.

```python
__HELPERS__
```

### 33.2.3 An analytical storage calculation

For an illustrative constant liquid arrival of 0.12 m3/s over 10 minutes and a permitted drain of 0.02 m3/s, the added inventory is 60 m3. These are assumed inputs, not measured slug data. The calculation checks the storage balance and units:

```python
arrival_m3_s, drain_m3_s, duration_s = 0.12, 0.02, 600.0
surge_m3 = (arrival_m3_s-drain_m3_s)*duration_s
assert abs(surge_m3-60.0) < 1e-10
print(f"Illustrative added liquid inventory: {surge_m3:.1f} m3")
```

## 33.3 Gas Sweetening and Amine Regeneration

### 33.3.1 Acid gases and product requirements

Hydrogen sulfide makes gas sour; CO2 is also an acid gas but CO2 alone should not be confused with the H2S hazard. Product H2S and CO2 limits come from the applicable transport or sales contract. They are separate from occupational exposure limits. NIOSH lists an H2S immediately-dangerous-to-life-or-health concentration of 100 ppm; a single statement that a higher concentration is always lethal ignores exposure duration and is not an adequate safety basis \cite{nioshH2S2026}.

Amine absorption is one treating option. Selection between solvents, membranes or other processes depends on acid-gas partial pressures, required selectivity, hydrocarbons, utilities and the downstream acid-gas destination. A physical SRK flash without the required aqueous reaction and electrolyte treatment cannot demonstrate an amine specification.

### 33.3.2 Chemistry and selectivity

Write the proton-transfer equilibrium for a generic amine base $B$ as

$$
\mathrm{H_2S}+B\rightleftharpoons BH^++\mathrm{HS^-}.
$$

Primary and secondary amines can form carbamate; a primary-amine representation is

$$
\mathrm{CO_2}+2\mathrm{RNH_2}
\rightleftharpoons\mathrm{RNHCOO^-}+\mathrm{RNH_3^+}.
$$

Tertiary amines such as MDEA support bicarbonate formation in water:

$$
\mathrm{CO_2}+\mathrm{R_3N}+\mathrm{H_2O}
\rightleftharpoons\mathrm{R_3NH^+}+\mathrm{HCO_3^-}.
$$

Fast H2S proton transfer compared with CO2 hydration can favor H2S selectivity in MDEA. The achieved outlet composition still depends on equilibrium, mass transfer, reaction kinetics and contacting; H2S absorption is not automatically complete. Promoters can change CO2 uptake substantially.

### 33.3.3 Loading, circulation and duty

Let $\alpha$ be moles of absorbed acid gas per mole of amine, $w_A$ the amine mass fraction in solution, and $M_A$ the amine molar mass in kg/mol. A capacity balance gives

$$
\dot m_{\mathrm{solution}}=
\frac{\dot n_{\mathrm{acid,removed}}M_A}
{(\alpha_{\mathrm{rich}}-\alpha_{\mathrm{lean}})w_A}.
$$

For $\dot n$ in mol/s the result is kg/s. Specify whether loadings include both H2S and CO2 and include their separate residual targets. The rich loading must be achievable by the absorber and compatible with the solvent/material limits; this balance alone does not size the contactor.

```python
# Illustrative MDEA capacity balance, independent of a reaction-rate calculation.
acid_removed_mol_s = 100.0
M_MDEA_kg_mol, w_MDEA = 0.11916, 0.45
lean_loading, rich_loading = 0.01, 0.40
solution_kg_s = acid_removed_mol_s*M_MDEA_kg_mol / (
    (rich_loading-lean_loading)*w_MDEA)
reconstructed_removal = solution_kg_s*w_MDEA/M_MDEA_kg_mol * (
    rich_loading-lean_loading)
assert abs(reconstructed_removal/acid_removed_mol_s-1) < 1e-12
print(f"Assumed-loading circulation: {solution_kg_s:.3f} kg/s")
```

A regeneration duty account includes sensible heating, desorption/reaction effects, vaporization, heat recovery and losses on a consistent stream basis. Do not add separate reaction or latent terms to an enthalpy balance that already includes those contributions. Lower lean loading can improve the absorption driving force, but may require more regeneration duty. A fixed duty per mole of CO2 cannot represent all amines, loadings, pressures and heat-integration arrangements.

![Conceptual amine absorber and regenerator with solvent heat recovery](figures/ch22_amine_unit_pfd.png)

The rich/lean exchanger recovers heat within the solvent loop. Reboiler, condenser, makeup, purge and acid-gas streams remain external boundaries when closing the whole-unit balance. Corrosion, foaming and solvent degradation require chemistry and operating information beyond equilibrium phase splitting.

## 33.4 TEG Dehydration

### 33.4.1 Equilibrium, contacting and regeneration

TEG removes water by contacting wet gas with lean solvent. Outlet water content depends on pressure, temperature, lean solvent mass fraction, circulation and contacting efficiency. A dew-point depression table indexed by TEG purity alone is under-specified. Use a thermodynamic model suitable for associating TEG-water mixtures and verify against relevant equilibrium data \cite{twuTEG2005}.

Regeneration reduces the water activity of returning solvent. Stripping gas and other enhanced regeneration arrangements can improve achievable lean concentration, but their benefit depends on temperature, pressure and material/energy integration \cite{neaguTEG2017}. A quoted maximum temperature is not a discontinuous chemical degradation threshold: residence time, contamination and supplier limits also matter.

For the regenerator control volume,

$$
\dot Q_{\mathrm{external}}+\sum\dot H_{\mathrm{in}}
=\sum\dot H_{\mathrm{out}}+\dot Q_{\mathrm{loss}}.
$$

Include water removed overhead, solvent makeup/purge and stripping-agent flows. A sensible-plus-latent estimate is useful only if its mass basis is clear and heat recovery is not counted twice.

### 33.4.2 CPA absorber calculation

This example specifies 99.5 **mass percent** lean TEG and an external 5000 kg/hr solvent supply. `addComponent` uses molar amounts, so mass fractions must first be divided by molar mass. The upstream three-phase separator excludes free water from the gas-contactor feed. Five model stages at 70 percent efficiency are stated assumptions. This calculation covers the absorber; it does not predict a regeneration loop or guarantee a cryogenic water specification.

The current `SimpleTEGAbsorber` first PH-flashes the combined feed and then transfers water according to its absorption approximation. That second operation does not re-solve energy. The code therefore reports the raw energy residual and explicitly reconstructs an adiabatic common outlet temperature with fixed predicted outlet compositions. This is an energy-closed outlet reconstruction of the approximate contacting calculation, not a rigorous tray-temperature profile. The bounded correction and inventory checks make the approximation visible; validation against independent contacting data is still required to establish water-removal accuracy.

<!-- @neqsim:claim
  test: devtools/run_ch33_science.py
  baseline: verification/scientific_revision/ch33_physical_execution.json
  scope: TEG component inventories and explicit outlet-energy reconstruction; no field calibration
-->

```python
CPA = jneqsim.thermo.system.SystemSrkCPAstatoil
ThreePhaseSeparator = jneqsim.process.equipment.separator.ThreePhaseSeparator
SimpleTEGAbsorber = jneqsim.process.equipment.absorber.SimpleTEGAbsorber
wet = CPA(303.15, 70.0)
for name, fraction in {"methane": .85, "ethane": .08, "propane": .04,
        "n-butane": .015, "n-pentane": .005, "CO2": .005, "water": .005}.items():
    wet.addComponent(name, fraction)
wet.setMixingRule(10)
wet.setMultiPhaseCheck(True)
wet_feed = Stream("Wet Feed", wet)
wet_feed.setFlowRate(400000.0, "kg/hr")
free_liquid_sep = ThreePhaseSeparator("Free Liquid Knockout", wet_feed)
lean = CPA(318.15, 70.0)
lean.addComponent("TEG", .995/150.174)
lean.addComponent("water", .005/18.01528)
lean.setMixingRule(10)
lean_teg = Stream("Lean TEG", lean)
lean_teg.setFlowRate(5000.0, "kg/hr")
absorber = SimpleTEGAbsorber("TEG Contactor")
absorber.addGasInStream(free_liquid_sep.getGasOutStream())
absorber.addSolventInStream(lean_teg)
absorber.setNumberOfStages(5)
absorber.setStageEfficiency(.70)
teg_system = ProcessSystem()
for unit in (wet_feed, free_liquid_sep, lean_teg, absorber):
    teg_system.add(unit)
teg_system.run()
check_balance("TEG feed knockout", [wet_feed], [free_liquid_sep.getGasOutStream(),
    free_liquid_sep.getOilOutStream(), free_liquid_sep.getWaterOutStream()])
from scipy.optimize import brentq
teg_products = [absorber.getGasOutStream(), absorber.getSolventOutStream()]
hin_teg = free_liquid_sep.getGasOutStream().getFluid().getEnthalpy()+lean_teg.getFluid().getEnthalpy()
raw_hout_teg = sum(s.getFluid().getEnthalpy() for s in teg_products)
raw_temperature_K = teg_products[0].getTemperature("K")
def outlet_energy_residual(temperature_K):
    for stream in teg_products:
        stream.getFluid().setTemperature(float(temperature_K))
        stream.getFluid().init(3)  # Preserve predicted phase inventories; no new equilibrium flash.
    return sum(s.getFluid().getEnthalpy() for s in teg_products)-hin_teg
closed_temperature_K = brentq(outlet_energy_residual,
    raw_temperature_K-5.0, raw_temperature_K+5.0, xtol=1e-9)
outlet_energy_residual(closed_temperature_K)
assert abs(closed_temperature_K-raw_temperature_K) < 5.0
for stream in teg_products:
    stream.getFluid().initProperties()
    assert stream.getFluid().getNumberOfPhases() == 1
    assert stream.getFluid().getDensity("kg/m3") > 0
    assert stream.getFluid().getCp() > 0
print(f"Raw absorber H residual: {raw_hout_teg-hin_teg:.3f} W")
print(f"Outlet energy correction: {closed_temperature_K-raw_temperature_K:.5f} K")
check_balance("TEG absorber with explicit outlet-energy reconstruction", [free_liquid_sep.getGasOutStream(), lean_teg],
    [absorber.getGasOutStream(), absorber.getSolventOutStream()])
wet_ppmv = 1e6*free_liquid_sep.getGasOutStream().getFluid().getComponent("water").getz()
dry_ppmv = 1e6*absorber.getGasOutStream().getFluid().getComponent("water").getz()
assert 0 < dry_ppmv < wet_ppmv
teg_mass = lean.getComponent("TEG").getNumberOfmoles()*lean.getComponent("TEG").getMolarMass()
water_mass = lean.getComponent("water").getNumberOfmoles()*lean.getComponent("water").getMolarMass()
assert abs(teg_mass/(teg_mass+water_mass)-.995) < 1e-5
print(f"Gas water content: {wet_ppmv:.2f} to {dry_ppmv:.2f} ppmv")
```

## 33.5 NGL Recovery and Energy Accounting

### 33.5.1 Recovery is a component-flow ratio

For component $i$, define recovery to a named product set as

$$
R_i=\frac{\sum_{p\in\mathrm{selected\ products}}\dot n_{i,p}}
{\dot n_{i,\mathrm{feed}}}.
$$

State whether inlet condensate is included and whether the denominator is the raw plant feed or recovery-unit feed. A liquid volume at separator conditions is neither a C3+ component recovery nor a standard-condition product volume. Check $0\le R_i\le1$ and reconcile the unrecovered component in the other outlets.

### 33.5.2 Technology comparison

| Method | Thermodynamic operation | Main accounting requirement |
|---|---|---|
| JT valve | Approximately constant flow enthalpy; no shaft work | Include any required recompression |
| Mechanical refrigeration | External heat removal and refrigerant compression | Close the refrigerant cycle or state the assumed COP |
| Turboexpander | Enthalpy reduction with recovered shaft work | Include dry gas-inlet conditioning, separation and residue recompression |

*Table 33.2: Comparison on a common boundary. Recovery percentages require specified feed, pressures, temperatures and separation configuration.*

For a single phase, the Joule–Thomson coefficient is

$$
\mu_{JT}=\left(\frac{\partial T}{\partial P}\right)_h
=\frac{T(\partial v/\partial T)_P-v}{c_p}.
$$

The molar or mass bases of $v$ and $c_p$ must agree. With SI pressure the result is K/Pa; multiply by $10^5$ for K/bar. A finite pressure drop, particularly across phase appearance, requires a PH flash. Constant positive cooling per bar is not a universal natural-gas property.

### 33.5.3 Refrigeration duty

For cooling duty taken positive,

$$
\dot Q_{\mathrm{ref}}=\dot m(h_{\mathrm{in}}-h_{\mathrm{out}}),
\qquad
\mathrm{COP}=\frac{\dot Q_{\mathrm{ref}}}{\dot W_{\mathrm{cycle}}}
\le\frac{T_c}{T_h-T_c}.
$$

The enthalpy difference already includes condensation when a multiphase EOS flash is used. Adding another latent-heat term double counts it. The upper bound is the reversible refrigeration limit between reservoirs at $T_c$ and $T_h$ in kelvin; real heat-exchanger approaches, pressure losses and compressor efficiency reduce the achievable COP.

### 33.5.4 Expander efficiency and its limiting cases

With heat loss and kinetic-energy changes neglected,

$$
\eta_s=\frac{h_1-h_2}{h_1-h_{2s}},\qquad s_{2s}=s_1.
$$

For a calorically perfect ideal gas only,

$$
T_{2s}=T_1(P_2/P_1)^{(\gamma-1)/\gamma},\qquad
T_2=T_1-\eta_s(T_1-T_{2s}).
$$

Lower efficiency gives less cooling and less recovered work. This ideal-gas check tests the sign and limits of the equation; the NeqSim calculation in Section 33.10 instead uses real-fluid enthalpy and an independently reconstructed PS reference.

```python
T1, ratio, gamma = 300.0, 0.30, 1.30
T2s = T1*ratio**((gamma-1)/gamma)
T2 = lambda efficiency: T1-efficiency*(T1-T2s)
assert abs(T2(0.0)-T1) < 1e-12
assert abs(T2(1.0)-T2s) < 1e-12
assert T2s < T2(.85) < T2(.50) < T1
print(f"Ideal-gas limit: T2s={T2s:.2f} K; T2 at85%={T2(.85):.2f} K")
```

![Conceptual turboexpander recovery process with cold separation and downstream fractionation](figures/ch22_turboexpander_pfd.png)

This conceptual diagram shows where heat recovery and fractionation can enter a plant. The worked model represents precooling as an external cooler, provides a knockout before the expander and accounts for its liquid bypass. It credits no gas-gas heat recovery or automatic shaft coupling.

## 33.6 Fractionation and Convergence

A demethanizer separates methane-rich overhead from heavier material. A deethanizer, depropanizer and debutanizer successively target ethane, propane and butanes. Column pressure, stages, reflux, boilup and feed condition must be solved together. Product purity and component recovery are different specifications; purity alone is not a product-standard compliance assessment.

For a constant-relative-volatility shortcut with the usual constant-molar-overflow assumptions, the minimum-reflux feed equation and rectifying-section equation are

$$
\sum_i\frac{\alpha_i z_{F,i}}{\alpha_i-\theta}=1-q,
\qquad
R_{\min}+1=\sum_i\frac{\alpha_i x_{D,i}}{\alpha_i-\theta}.
$$

Here $q=1$ is saturated-liquid feed and $q=0$ is saturated-vapor feed. For the simple two-key split, use the relevant root between heavy- and light-key relative volatilities; multicomponent distributed-key separations require the appropriate root/specification treatment. The equations describe a limiting infinite-stage calculation, not a finite-column solution \cite{waterlooDistillation2026}.

```python
from scipy.optimize import brentq
alpha, zF, xD, q = (2.0, 1.0), (.5, .5), (.95, .05), 1.0
def underwood(theta):
    return sum(a*z/(a-theta) for a, z in zip(alpha, zF))-(1-q)
theta = brentq(underwood, 1.0+1e-9, 2.0-1e-9)
Rmin = sum(a*x/(a-theta) for a, x in zip(alpha, xD))-1
assert abs(theta-4/3) < 1e-10
assert abs(Rmin-1.70) < 1e-10
print(f"Binary analytical check: theta={theta:.8f}, Rmin={Rmin:.4f}")
```

The rigorous example below is deliberately a small stabilizer: one contacting tray plus an equilibrium reboiler, with no condenser. It demonstrates an accepted multicomponent stage calculation. It is not a full deethanizer train and does not claim ethane purity or commercial condensate stability. A larger stage count is useful only when its equations converge and its intended product specifications pass.

Require `RIGOROUS_CONVERGED`, active material/energy/MESH tolerances, positive products, and independent whole-column component and energy closure. MESH denotes material balances, equilibrium, summation and heat/energy equations. Specifying reboiler heat input here makes that duty explicit in the tray energy equations. A fixed-temperature terminal can report a calculated duty even when a residual evaluator uses a different boundary representation; inspect the equations and do not accept a status flag or reconciled product flow alone.

## 33.7 Sulfur Recovery

The Claus process partially oxidizes H2S to SO2 and reacts it with the remaining H2S to form elemental sulfur. An atom-balanced representation is

$$
2\mathrm{H_2S}+3\mathrm{O_2}\rightarrow2\mathrm{SO_2}+2\mathrm{H_2O},
$$

$$
2\mathrm{H_2S}+\mathrm{SO_2}\rightleftharpoons3\mathrm{S}+2\mathrm{H_2O}.
$$

Combining the reactions in the required proportions gives $\mathrm{H_2S}+0.5\mathrm{O_2}\rightarrow\mathrm{S}+\mathrm{H_2O}$. Here S is an elemental-sulfur accounting symbol; actual vapor sulfur species and liquid allotropes matter in a thermochemical model. Reaction enthalpies require specified reference temperature, physical phases and stoichiometric basis. A generic heat value per unspecified mole is insufficient for furnace or waste-heat-boiler sizing.

Thermal and catalytic stages, sulfur condensation and tail-gas treatment determine recovery. Tail-gas processes may reduce sulfur compounds to H2S for recycle or recover SO2 after oxidation. Actual emissions obligations depend on the jurisdiction and permit; a generic recovery percentage is not a regulatory requirement. EPA's natural-gas-processing description identifies acid-gas treating and sulfur-recovery boundaries, while its emissions factors have separate applicability conditions \cite{epaGasProcessing1995}.

## 33.8 Product Storage and Loading

Storage design follows the product phase envelope, composition, temperature range, required inventory and loading conditions. Pressure alone does not identify a liquid storage state. Ethane is particularly instructive: NIST lists a normal boiling point near184.6 K and a critical temperature near305.3 K. Therefore an unspecified ambient temperature and a generic30–35 bara cannot establish liquid ethane storage \cite{nistEthanePhase2026}.

| Product | Thermodynamic assessment | Additional design boundaries |
|---|---|---|
| Ethane | Refrigerated or pressure-temperature state relative to saturation/critical point | Heat ingress, boiloff/refrigeration, containment and transfer |
| Propane and butanes | Mixture vapor pressure at maximum operating temperature | Relief basis, fire exposure, loading and vapor return |
| Natural gasoline | Actual light-end content and vapor pressure | Vent/emissions basis, flashing, losses and tank suitability |
| Sulfur | Required physical form and temperature | Heating, corrosion, handling and sulfur-vapor hazards |

*Table 33.3: Storage assessment requirements, not vessel sizes or allowable operating pressures.*

Loading lines, pumps and vapor return must share the storage pressure and thermal boundary. A phase calculation does not replace mechanical design, relief sizing or the applicable product/storage standard.

## 33.9 Utilities and Shared Constraints

Compression demand depends on flow, composition, pressure ratio, inlet state and efficiency. Plant throughput alone does not justify a fixed MW estimate. The electrical boundary must also account for motors, drives, auxiliaries and generation losses; shaft power and imported electricity are different quantities.

Heating may use steam, hot oil, fired duty or recovered heat. Cooling may use air, water or refrigeration. Match each duty to a feasible temperature level and capacity: adding all MW is insufficient when a low-temperature duty cannot be served by cooling water. A heat-recovery credit requires both stream sides and a feasible approach temperature.

`PlantSharedResourceEvidence` supports participant-complete maximum-budget evidence for supported total shaft-demand and solved electrical-demand cases in the September2026 workspace. Its sum is checked against the authoritative aggregate. It does not supply a complete fuel, steam or cooling-water model by itself \cite{neqsim2026update}. Report the contributing units, units of measure, limit and solve identity before using an aggregate as an optimization constraint.

## 33.10 Worked Three-Area Hydrocarbon Plant

### 33.10.1 Stated basis

The feed is350,000 kg/hr at25 C and70 bara, with the mole fractions explicitly given in the code. Water, CO2, H2S and mercury are absent from this teaching recipe. It represents a boundary **after** the corresponding pretreatment, not a simulated removal efficiency. Both gas and condensate may occur at the inlet state. Standard-volume conversion, if needed, must use a named reference temperature and pressure and the actual molecular weight.

The model includes inlet separation; external precooling and feed knockout; expander and liquid letdown; cold mixing/separation; two compression stages with30 C intercooling/aftercooling; and a small stabilizer. Its outlets are inlet condensate, residue gas, stabilizer overhead and stabilizer bottoms. Stabilizer overhead is retained as a separate product boundary; its later recovery, fuel use or recompression is not silently credited.

### 33.10.2 Build and verify

The reboiler receives4.5 MW, the column operates from20 bara at the bottom to19.5 bara at the top, and the feed is conditioned to−30 C. All duties are reported. The expander is fed only the gas from its upstream knockout; condensed liquid bypasses through a valve and rejoins the cold stream. Compressor efficiency is explicitly polytropic, and recovered expander work is reported separately from gross compression.

```python
__MODEL__
```

### 33.10.3 Interpreting the accepted result

For this recipe and solver state, the reproduced outlet rates are:

| Outlet or duty | Value | Unit |
|---|---:|---|
| Residue gas |199168.361|kg/hr|
| Inlet condensate |69244.161|kg/hr|
| Stabilizer overhead |35407.168|kg/hr|
| Stabilizer bottoms |46180.311|kg/hr|
| Gross compression |11.3103|MW|
| Recovered expander work |4.4726|MW|
| External precooling, heat removed |16.2331|MW|
| Reboiler heat input |4.5000|MW|

The four outlet mass rates sum to350,000 kg/hr before rounding. The maximum relative component error in the whole plant is below$10^{-10}$ and its normalized energy residual is below$10^{-6}$ in the retained execution. The column MESH norm is below$10^{-5}$. These tests establish a numerically consistent calculation for the stated model.

<!-- @neqsim:claim
  test: devtools/run_ch33_science.py
  baseline: verification/scientific_revision/ch33_physical_execution.json
  scope: stated dry feed; individual units, each column stage and external plant boundary
-->

The bottoms still contain about2.225 mol% methane. That observation prevents describing them as a demonstrated commercial stabilized product. A product vapor-pressure requirement, deeper methane removal or ethane separation needs additional specifications and accepted calculations. The example gives a sound starting point for those studies.

<!-- @neqsim:claim
  test: devtools/run_ch33_science.py
  baseline: verification/scientific_revision/ch33_physical_execution.json
  result: plant_results.stabilizer_bottoms_methane_mol_pct
-->

### 33.10.4 Automation readback and reproducibility

```python
plant = case["plant"]
auto = plant.getAutomation()
read_pressure = auto.getVariableValue(
    "NGL Recovery::Residue Gas Compressor.outletStream.pressure", "bara")
assert abs(read_pressure-plant_results["export_pressure_bara"]) < 1e-8
print("Process areas:", [str(a) for a in auto.getAreaList()])
print(f"Automation discharge pressure: {read_pressure:.3f} bara")
# A saved input record is not a serialized process state. Rebuild and compare.
from pathlib import Path
input_record = {"precooling_C": -30.0, "flow_kg_hr": 350000.0}
Path("gas_plant_verified_inputs.json").write_text(json.dumps(input_record, indent=2))
restored_inputs = json.loads(Path("gas_plant_verified_inputs.json").read_text())
replayed = verify_dry_plant(build_dry_plant(**restored_inputs))
for key in ("export_kg_hr", "stabilizer_bottoms_kg_hr", "gross_compression_MW"):
    assert abs(replayed[key]-plant_results[key])/max(abs(plant_results[key]), 1.0) < 1e-7
```

## 33.11 Sensitivity and Economic Optimization

A valid sensitivity reruns the complete dependent flowsheet and all its acceptance checks. The following sweep changes precooling and rebuilds fresh process objects. This avoids presenting a new upstream state with stale downstream products. It reports inlet-condensate and stabilizer-bottoms C3+ recovery on the **whole-plant feed** basis; overhead hydrocarbons are outside this selected product set.

```python
import numpy as np
import matplotlib.pyplot as plt
temperatures = np.linspace(-40.0, -10.0, 7)
sweep = []
c3plus = ("propane", "i-butane", "n-butane", "i-pentane", "n-pentane",
    "n-hexane", "n-heptane", "n-octane")
def c3plus_moles(stream):
    return sum(stream.getFluid().getComponent(c).getNumberOfmoles() for c in c3plus)
for temperature in temperatures:
    trial = build_dry_plant(precooling_C=float(temperature))
    result = verify_dry_plant(trial)
    selected = c3plus_moles(trial["inlet_sep"].getLiquidOutStream()) + c3plus_moles(
        trial["column"].getReboiler().getLiquidOutStream())
    recovery = selected/c3plus_moles(trial["feed"])
    assert 0 <= recovery <= 1
    residue_loss = c3plus_moles(trial["aftercooler"].getOutletStream())/c3plus_moles(trial["feed"])
    overhead_loss = c3plus_moles(trial["column"].getGasOutStream())/c3plus_moles(trial["feed"])
    assert abs(recovery+residue_loss+overhead_loss-1) < 1e-6
    sweep.append(dict(temperature_C=float(temperature), recovery_pct=100*recovery,
        residue_C3plus_pct=100*residue_loss, stabilizer_overhead_C3plus_pct=100*overhead_loss,
        gross_compression_MW=result["gross_compression_MW"],
        expander_recovered_MW=result["recovered_expander_MW"],
        cooling_removed_MW=-result["precooler_duty_MW"]))
Path("figures").mkdir(exist_ok=True)
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
axes[0].plot(temperatures, [r["recovery_pct"] for r in sweep], "o-", color="#067a75")
axes[0].set_ylabel("Selected-product C3+ molar recovery (%)")
for key, label in (("gross_compression_MW", "Gross compression"),
        ("expander_recovered_MW", "Expander work recovered"),
        ("cooling_removed_MW", "Precooling heat removed")):
    axes[1].plot(temperatures, [r[key] for r in sweep], "o-", label=label)
axes[1].set_ylabel("Shaft power or thermal duty (MW)")
axes[1].legend(fontsize=8)
for ax in axes:
    ax.set_xlabel("Specified precooling temperature (C)")
    ax.grid(alpha=.25)
fig.suptitle("Verified dry-hydrocarbon plant: recovery and utility trade-off")
fig.tight_layout()
fig.savefig("figures/ch22_ngl_sensitivity.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print(json.dumps(sweep, indent=2))
```

![Dry-hydrocarbon plant sensitivity; every point is a fresh accepted NeqSim calculation, with thermal duty distinguished from shaft power](figures/ch22_ngl_sensitivity.png)

The left panel measures the selected C3+ product recovery by component flow. The right panel keeps gross compression, recovered work and external cooling visible separately. Lower precooling temperature changes both condensate bypass and expansion-feed composition, so a single assumed recovery percentage cannot represent the response. Cooling MW is not electrical MW; price it through a feasible utility model or explicitly stated refrigeration cycle before selecting an economic optimum.

Selected-product recovery reaches87.81 percent at−35 C among these seven cases, compared with81.35 percent at−10 C and87.10 percent at−40 C. The response belongs to this complete flowsheet with a fixed4.5 MW reboiler; it is not a general monotonic refrigeration-recovery law. The unselected C3+ components are explicitly reconciled between residue gas and stabilizer overhead. Use that loss split to decide whether additional cooling, a different column duty or overhead recovery is the useful next study.

<!-- @neqsim:figure
  file: chapters/ch33_onshore_processing_plants/figures/ch22_ngl_sensitivity.png
  test: devtools/run_ch33_science.py
  baseline: verification/scientific_revision/ch33_physical_execution.json
  result: sensitivity
-->

For a common time interval, a suitable contribution-margin objective is

$$
J=\sum_p\dot m_p p_p+\dot E_{\mathrm{gas}}p_{\mathrm{gas}}
-\dot W_{\mathrm{import}}c_{\mathrm{electricity}}
-\dot E_{\mathrm{fuel}}c_{\mathrm{fuel}}
-\sum_u\dot Q_u c_u-C_{\mathrm{other}}.
$$

Mass, energy and prices must use compatible bases and the same time unit. Do not sell a component both as extracted liquid and as residue-gas energy. Avoid double-counting fuel-derived electricity in both utility costs. Constraints include contractual gas and liquid quality, receiving pressure, actual equipment capacities, shaft/driver limits and available temperature-level-specific utilities. A sample sweep is not an optimization proof; Chapter32 demonstrates an accepted optimizer result with independent replay and sampled-search comparison.

## 33.12 Debottlenecking

Capacity restrictions include contactor flooding, separator carryover, expander flow/shaft limits, compressor surge/choke/driver limits, column hydraulics and utility supply. Diagnose the controlling mechanism before choosing a change. Adding packing height does not generally relieve a cross-sectional flooding restriction; increasing duty does not cure a hydraulic limit.

For an upper-bound restriction, utilization can be written $U=Q_{\mathrm{actual}}/Q_{\mathrm{allowable}}$ on a consistent basis. Chapter20 discusses the associated evidence checks. An alarm threshold such as90 percent is an operating policy, not a universal physical boundary. Surge and other lower-bound constraints need their own margin definition.

The worked plant has no vendor capacity curves or installed utility limits. Increasing its flow scales and resolves a thermodynamic model; it cannot identify a site's first mechanical bottleneck without those inputs. Combine the updated optimization and shared-resource APIs with supported limits, then rerun every accepted physical and product-quality check at the selected rate.

__NOTEBOOK__

## Summary

Gas-plant optimization needs explicit boundaries, component accounting and utility-temperature levels. The chapter's revised calculations test inventory units, amine circulation, expander limits, minimum reflux, TEG absorption and a fully balanced dry-hydrocarbon plant. The accepted stabilizer illustrates rigorous multicomponent solution verification while retaining its actual product quality. Scaling this evidence to a commercial plant requires the missing treating, product, hydraulic and equipment data to be supplied and checked.

## Exercises

These are design assignments rather than precomputed validated cases. Supply the missing design information before claiming their acceptance.

**Exercise33.1 — TEG operating envelope.** Extend the CPA absorber calculation over pressure, gas temperature and lean mass fraction. Report water mass flow and ppmv, gas and solvent component balances, and the heat boundary. Convert to a water dew point at a stated delivery pressure and compare with independent TEG-water-gas equilibrium data.

**Exercise33.2 — Recovery on equal boundaries.** Replace the gas expander with a JT valve while retaining the feed knockout and liquid bypass. Compare C3+ recovery, recovered work, cooling and recompression at the same inlet and export conditions. Require the entire plant balance to pass for every case.

**Exercise33.3 — Amine design information.** For an assumed5 mol% CO2 and200 ppmv H2S feed, list the gas composition, flow, pressure, temperature, solvent model, kinetics, lean loadings and product limits needed to compare DEA and MDEA. Apply the loading balance; explain why that result alone cannot establish absorber size or regeneration duty.

**Exercise33.4 — Stabilizer product quality.** Starting from the accepted two-equilibrium-stage configuration, vary reboiler duty and test component recovery and product vapor pressure. Add stages only when all convergence gates pass. Do not label the bottoms stable merely because methane concentration decreases.

**Exercise33.5 — Plant capacity.** Increase feed by25 percent and provide explicit separator geometry, compressor maps, driver ratings and utility budgets. Evaluate both physical solution checks and those additional capacities before proposing a throughput increase.

**Exercise33.6 — Economic objective.** With explicitly assumed component prices and a refrigeration/power model, price every external product and utility from the sweep. State the price date and units, compute the margin, and verify the chosen candidate with a fresh model. Report its sensitivity to prices and utility assumptions.

## References

The chapter uses the verified bibliography entries cited at the relevant claims: NIOSH for the H2S IDLH value, NIST for ethane phase properties, primary TEG research for thermodynamic/regeneration context, University of Waterloo for the distillation shortcut, and EPA/UOP for process-boundary context. The September2026 NeqSim source snapshot establishes API behavior. None of these references by itself validates the complete illustrative plant against operating data.
'''
text = text.replace('__HELPERS__', helpers.rstrip()).replace('__MODEL__', model.rstrip()).replace('__NOTEBOOK__', notebook_section)
# Keep ordinary prose numbers separated from words for readable typesetting.
for before, after in [('near184.6','near 184.6'), ('near305.3','near 305.3'), ('generic30–35','generic 30–35'),
        ('September2026','September 2026'), ('is350,000','is 350,000'), ('at25 C','at 25 C'),
        ('and70 bara','and 70 bara'), ('with30 C','with 30 C'), ('receives4.5','receives 4.5'),
        ('from20 bara','from 20 bara'), ('to19.5','to 19.5'), ('to−30','to −30'),
        ('to350,000','to 350,000'), ('below$','below $'), ('about2.225','about 2.225'),
        ('Chapter32','Chapter 32'), ('Chapter20','Chapter 20'), ('as90 percent','as 90 percent'),
        ('Exercise33.','Exercise 33.'), ('assumed5 mol','assumed 5 mol'), ('and200 ppmv','and 200 ppmv'),
        ('by25 percent','by 25 percent'), ('reaches87.81','reaches 87.81'), ('at−35','at −35'),
        ('with81.35','with 81.35'), ('at−10','at −10'), ('and87.10','and 87.10'),
        ('at−40','at −40'), ('fixed4.5','fixed 4.5')]:
    text = text.replace(before, after)
chapter.write_text(text, encoding='utf-8')
print('Revised chapter 33:', len(text.split()), 'words')
