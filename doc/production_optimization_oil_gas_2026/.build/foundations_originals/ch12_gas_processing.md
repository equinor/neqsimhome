# Gas Processing and Conditioning

<!-- Chapter metadata -->
<!-- Notebooks: 01_teg_dehydration.ipynb, 02_jt_dew_point_control.ipynb, 03_ngl_fractionation.ipynb, 04_amine_treating.ipynb -->
<!-- Estimated pages: 30 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Design and simulate a complete TEG dehydration system including regeneration
2. Explain the principles of hydrocarbon dew point control and select appropriate technologies
3. Model NGL recovery systems using turboexpanders and fractionation columns
4. Understand acid gas removal processes and their thermodynamic basis
5. Implement gas processing unit operations in NeqSim using ProcessSystem
6. Evaluate trade-offs between different gas processing technologies
7. Calculate water dew point and hydrocarbon dew point specifications

## 11.1 Introduction to Gas Processing

Natural gas as produced from the reservoir is rarely suitable for direct sale or transport. It contains water vapor, heavy hydrocarbons, acid gases (CO$_2$, H$_2$S), and sometimes mercury, nitrogen, and other contaminants that must be removed to meet pipeline quality specifications, protect downstream equipment, and ensure safe operations.

The gas processing chain typically follows this sequence:

1. **Inlet separation**: Removal of bulk liquids and solids
2. **Acid gas removal**: Removal of CO$_2$ and H$_2$S (if present)
3. **Dehydration**: Removal of water vapor to prevent hydrate formation and corrosion
4. **Hydrocarbon dew point control**: Removal or control of heavy hydrocarbons to prevent liquid dropout in pipelines
5. **NGL recovery**: Recovery of valuable C$_2$+ or C$_3$+ hydrocarbons (if economically attractive)
6. **Mercury removal**: Protection of aluminum heat exchangers (if mercury is present)

The specific processing requirements depend on the gas composition, pipeline specifications, and the economics of NGL recovery. This chapter covers each of these processing steps in detail, with emphasis on NeqSim simulation capabilities.

![Overview of a typical gas processing facility](figures/gas_processing_overview.png)

*Figure 11.1: Schematic of a gas processing facility showing the major unit operations from inlet separation through sales gas delivery.*

### 11.1.1 Sales Gas Specifications

Pipeline-quality natural gas must meet stringent specifications:

| Parameter | Typical Specification | Reason |
|-----------|----------------------|--------|
| Water dew point | < −18°C at delivery P | Hydrate prevention, corrosion |
| HC dew point | < −2°C (cricondentherm) | Prevent liquid dropout |
| H$_2$S content | < 4 ppm$_v$ | Toxicity, corrosion |
| CO$_2$ content | < 2–3 mol% | Heating value, corrosion |
| Total sulfur | < 20–50 mg/Sm$^3$ | Environmental, odor |
| O$_2$ content | < 0.1 mol% | Corrosion |
| Gross heating value | 36–42 MJ/Sm$^3$ | Combustion specifications |
| Wobbe Index | 45–55 MJ/Sm$^3$ | Interchangeability |

*Table 11.1: Typical sales gas specifications for European pipeline systems (varies by grid code).*

## 11.2 Gas Dehydration

### 11.2.1 Why Dehydration Is Necessary

Water vapor in natural gas causes three critical problems:

1. **Hydrate formation**: Gas hydrates are ice-like crystalline structures that form when water molecules cage small gas molecules (CH$_4$, C$_2$H$_6$, CO$_2$, H$_2$S) at elevated pressures and reduced temperatures. Hydrates can block pipelines, damage equipment, and create safety hazards.

2. **Corrosion**: Liquid water in combination with CO$_2$ and H$_2$S forms carbonic acid and sulfuric acid, causing severe internal corrosion of carbon steel pipelines.

3. **Liquid accumulation**: Water condensation in gas transmission pipelines reduces capacity and causes slugging.

The water content of saturated natural gas depends on temperature and pressure and can be estimated from the empirical McKetta–Wehe correlation or, more accurately, from equation of state calculations.

The water content of saturated gas at temperature $T$ and pressure $P$ is approximately:

$$w = \frac{A}{P} \exp\left(\frac{B}{T}\right)$$

where $w$ is the water content (lb/MMscf), $P$ is pressure (psia), and $A$ and $B$ are empirical constants. For typical pipeline conditions, saturated gas at 30°C and 70 bara contains approximately 700–800 mg/Sm$^3$ of water, while the specification is typically less than 50 mg/Sm$^3$.

### 11.2.2 TEG Absorption — Theory

Triethylene glycol (TEG) absorption is the most widely used dehydration method in the oil and gas industry. TEG is a hygroscopic liquid that absorbs water vapor from the gas stream through intimate contact in an absorption column.

The process consists of two main steps:

1. **Absorption**: Wet gas contacts lean (dry) TEG in a counter-current column. Water transfers from the gas phase to the TEG solution. The dried gas exits the top of the absorber.

2. **Regeneration**: Rich (wet) TEG is heated in a regeneration column (still) to drive off the absorbed water. The regenerated lean TEG is cooled and recycled to the absorber.

The thermodynamics of water absorption by TEG are governed by the vapor–liquid equilibrium between water in the gas phase and water dissolved in the TEG–water solution. The water dew point depression achievable depends on the TEG purity (lean TEG concentration), the number of equilibrium stages in the absorber, and the TEG circulation rate.

The equilibrium water dew point over a TEG solution can be correlated with TEG concentration:

| TEG Concentration (wt%) | Equilibrium Dew Point at 25°C (°C) |
|--------------------------|--------------------------------------|
| 95.0 | +8 |
| 98.0 | −5 |
| 99.0 | −18 |
| 99.5 | −30 |
| 99.9 | −55 |
| 99.95 | −65 |

*Table 11.2: Equilibrium water dew point over TEG solutions at 25°C contact temperature. Actual column performance depends on tray efficiency and number of stages.*

This table illustrates a critical point: achieving very low water dew points (below about −20°C) requires TEG purity above 99.5 wt%, which cannot be achieved by simple atmospheric reboiling (limited to approximately 98.5–99.0 wt% at 204°C reboiler temperature due to TEG thermal degradation). Enhanced regeneration methods are needed for deeper dehydration.

### 11.2.3 TEG Absorber Design

The absorber column is typically a tray column (bubble cap or valve trays) or a structured packing column. Key design parameters:

**Number of theoretical stages**: 2–4 stages are typical for most applications. A 3-tray absorber with 99.5% TEG achieves a dew point depression of approximately 40–50°C.

**TEG circulation rate**: Expressed as liters of TEG per kg of water absorbed, typically 15–40 L/kg. Higher circulation rates improve dew point but increase regeneration energy and TEG losses.

**Contact temperature**: Lower absorber temperatures favor water absorption but increase hydrocarbon absorption. Typical contact temperature is 30–50°C.

The mass transfer in the absorber is described by the Kremser equation for a dilute system:

$$N = \frac{\ln\left[\frac{y_{\text{in}} - m x_{\text{in}}}{y_{\text{out}} - m x_{\text{in}}} (1 - 1/A) + 1/A\right]}{\ln A}$$

where $N$ is the number of theoretical stages, $y$ and $x$ are water mole fractions in gas and TEG phases, $m$ is the equilibrium ratio, and $A = L/(mG)$ is the absorption factor.

### 11.2.4 TEG Regeneration

Standard TEG regeneration uses a reboiled still column operating at atmospheric pressure with a reboiler temperature of 190–204°C. The maximum reboiler temperature is limited by TEG thermal degradation — above 204°C, TEG decomposes to form acidic products that cause corrosion and foaming.

At atmospheric pressure and 204°C, the maximum achievable TEG purity is approximately 98.5–99.0 wt%, corresponding to a water dew point depression of 30–40°C. For deeper dehydration, enhanced regeneration methods are required:

**Stripping gas**: Injecting a small amount of dry gas (typically 0.5–2% of the gas being dehydrated) into the reboiler or the surge drum below the still column strips additional water from the TEG. This can increase purity to 99.5–99.7 wt%.

**Stahl column (azeotropic regeneration)**: A packed column located between the reboiler and the surge drum receives stripping gas counter-current to the hot TEG, providing additional mass transfer stages. This achieves 99.9+ wt% TEG purity.

**Drizo process**: Uses heavy hydrocarbon (typically iso-octane or a C$_7$–C$_8$ fraction) as an azeotroping agent in the regeneration column. The hydrocarbon forms an azeotrope with water that has a boiling point below the TEG degradation temperature, allowing more complete water removal. Drizo achieves 99.95+ wt% TEG purity.

**Vacuum regeneration**: Operating the still column under vacuum (0.3–0.5 bara) reduces the reboiler temperature needed for a given TEG purity. This is less common but useful when stripping gas is unavailable.

### 11.2.5 TEG Losses and Emissions

TEG is lost through three mechanisms:

1. **Vaporization losses**: TEG has a small but finite vapor pressure. At absorber conditions, the TEG carried in the dry gas is typically 5–15 L per million Sm$^3$ of gas.
2. **Carry-over losses**: Mechanical entrainment of TEG droplets from the absorber. Mist eliminators reduce this to acceptable levels.
3. **Degradation**: Thermal and chemical degradation products accumulate and must be periodically purged.

The BTEX (benzene, toluene, ethylbenzene, xylene) emissions from TEG regeneration are a significant environmental concern. Aromatic hydrocarbons absorbed by TEG in the absorber are released in the regenerator overhead, creating a concentrated waste gas stream. This stream may require incineration or other treatment to meet emission regulations.

### 11.2.6 Molecular Sieve Dehydration

For applications requiring very dry gas (< 1 ppm$_v$ water), molecular sieves (zeolites) are used. The most common types are 4A (sodium form) and 3A (potassium form), which selectively adsorb water due to their uniform pore size.

Molecular sieve systems operate in a cyclic batch mode:

1. **Adsorption cycle** (8–24 hours): Wet gas passes through the sieve bed, water is adsorbed
2. **Regeneration cycle** (8–12 hours): Hot regeneration gas (250–315°C) drives off adsorbed water
3. **Cooling cycle** (2–4 hours): The bed is cooled before returning to adsorption service

Molecular sieves achieve dew points below −75°C and can simultaneously remove CO$_2$ and H$_2$S at reduced loadings. They are the preferred technology for cryogenic gas plants (turboexpander plants) where extremely dry gas is needed to prevent freeze-out.

#### Bed Sizing and Breakthrough

The molecular sieve bed must be sized to adsorb the total water load during the adsorption cycle without breakthrough (water appearing in the outlet gas). The minimum bed mass is:

$$
m_{\text{bed}} = \frac{w_{\text{water}} \times Q_{\text{gas}} \times t_{\text{ads}}}{C_{\text{capacity}} \times \eta_{\text{bed}}}
$$

where $w_{\text{water}}$ is the water content of the inlet gas (kg/MSm$^3$), $Q_{\text{gas}}$ is the gas flow rate (MSm$^3$/hr), $t_{\text{ads}}$ is the adsorption time (hours), $C_{\text{capacity}}$ is the sieve water capacity (typically 10–15 wt% for fresh 4A sieve, degrading to 5–8 wt% over 3–5 years), and $\eta_{\text{bed}}$ is the bed utilization factor (typically 0.6–0.7 to account for the mass transfer zone).

The **breakthrough curve** describes the transition from dry outlet to saturated outlet as the bed approaches exhaustion. A sharp breakthrough indicates good mass transfer; a drawn-out curve indicates poor gas distribution or degraded sieve. Monitoring the breakthrough front position using temperature sensors within the bed is standard practice.

#### Regeneration Cycle Design

Regeneration consists of three steps:

1. **Heating step**: Hot gas (250–315°C) is passed through the bed in the reverse direction to adsorption. The bed temperature must exceed the desorption temperature of water on the sieve (typically 230–280°C depending on the sieve type).

2. **Peak temperature hold**: The entire bed must reach the regeneration temperature to ensure complete desorption. Insufficient heating leaves a residual water loading that reduces effective capacity.

3. **Cooling step**: Cool gas (typically inlet gas) is passed through the bed until the temperature drops to within 10–15°C of the adsorption temperature. Cooling must proceed in the same direction as adsorption to avoid disturbing the mass transfer zone.

The regeneration gas rate is typically 5–15% of the process gas flow. Regeneration energy is the primary operating cost for molecular sieve systems.

#### Comparison: TEG vs Molecular Sieve

| Parameter | TEG Dehydration | Molecular Sieve |
|-----------|----------------|-----------------|
| Outlet water dew point | −18 to −40°C (−65°C with Drizo) | < −75°C |
| CAPEX | Lower | Higher (multiple vessels, switching valves) |
| OPEX | Lower (mainly TEG makeup) | Higher (regeneration energy) |
| Space/weight | Smaller | Larger (2–3 parallel vessels) |
| Chemical consumption | TEG makeup 5–20 L/MMSm$^3$ | Sieve replacement every 3–5 years |
| BTEX emissions | Yes (from regeneration) | No |
| Simultaneous H$_2$S removal | No | Partial (with type 5A sieve) |
| Turndown capability | Good | Good |
| Preferred application | Standard pipeline spec | Cryogenic plants, LNG feed prep |

For cryogenic NGL recovery plants using turboexpanders, molecular sieve dehydration is mandatory because even traces of water (> 1 ppm$_v$) will freeze and block the cryogenic heat exchangers. TEG is typically used upstream of the molecular sieve as a bulk dehydration step to reduce the water load on the sieves.

## 11.3 Hydrocarbon Dew Point Control

### 11.3.1 The Hydrocarbon Dew Point Problem

Natural gas transported through pipelines must not form liquid hydrocarbons at any point along the pipeline. Liquid dropout creates safety hazards (slug flow), operational problems (liquid accumulation at low points), and metering errors. The hydrocarbon dew point (HCDP) is the temperature at which the first drop of liquid hydrocarbon forms at a given pressure.

The HCDP is particularly sensitive to the presence of small amounts of heavy hydrocarbons (C$_5$+). A gas with 0.5 mol% n-hexane may have an HCDP 30–40°C higher than the same gas with only C$_1$–C$_4$ components.

The cricondentherm — the maximum temperature on the phase envelope — is the most critical specification because it represents the highest possible dew point at any pressure:

$$T_{\text{HCDP,spec}} = T_{\text{cricondentherm,spec}}$$

### 11.3.2 Joule–Thomson (JT) Cooling

The simplest method for HCDP control is Joule–Thomson cooling. Gas is expanded through a valve (JT valve) from a high pressure to a lower pressure. For natural gas, which has a positive JT coefficient at typical conditions, this expansion produces cooling:

$$\mu_{\text{JT}} = \left(\frac{\partial T}{\partial P}\right)_H = \frac{1}{C_p}\left[T\left(\frac{\partial V}{\partial T}\right)_P - V\right]$$

For an ideal gas, $\mu_{\text{JT}} = 0$. For real natural gas at typical pipeline conditions, $\mu_{\text{JT}} \approx 3$–$6$ °C/MPa.

A typical JT system consists of:

1. **Inlet gas–gas heat exchanger**: Cools the incoming gas against the cold processed gas
2. **JT valve**: Expands the gas to produce the target temperature
3. **Cold separator**: Separates condensed liquids from the gas
4. **Outlet gas–gas heat exchanger**: Warms the cold gas against incoming gas

The pressure drop required depends on the inlet conditions and the required dew point depression. For a typical North Sea application with inlet gas at 70 bara and 30°C requiring a dew point below −2°C, a pressure drop of approximately 25–35 bar is needed, yielding a cold separator temperature of approximately −10 to −15°C.

**Limitations of JT cooling**:
- Requires high available pressure drop (limits use in low-pressure systems)
- Pressure is consumed (not recoverable)
- Limited temperature depression per bar of pressure drop
- Rich gases may require very large pressure drops

### 11.3.3 Turboexpander

A turboexpander (expansion turbine) achieves the same cooling effect as a JT valve but recovers useful work from the expansion. The gas drives a turbine wheel, which can be coupled to:

- A compressor (compander configuration) that recompresses the processed gas
- An electrical generator

The isentropic expansion produces more cooling per unit pressure drop than the isenthalpic JT expansion:

$$\Delta T_{\text{turboexpander}} > \Delta T_{\text{JT}}$$

for the same pressure ratio. A turboexpander with 80% isentropic efficiency typically produces 30–50% more cooling than a JT valve for the same pressure drop.

The power recovered by the turboexpander is:

$$W = \dot{m} \eta_s (h_1 - h_{2s})$$

where $\dot{m}$ is the mass flow rate, $\eta_s$ is the isentropic efficiency, and $h_1 - h_{2s}$ is the isentropic enthalpy change.

### 11.3.4 JT Valve vs Turboexpander — Detailed Comparison

The choice between JT expansion and turboexpander has significant implications for plant design, economics, and product recovery. Understanding the thermodynamic difference is essential.

**Isenthalpic expansion (JT valve):** The gas passes through a restriction where kinetic energy is dissipated. No work is done on or by the gas, so the total enthalpy is conserved:

$$
h_1 = h_2 \quad \Rightarrow \quad T_2 = T_1 - \int_{P_1}^{P_2} \mu_{\text{JT}} \, dP
$$

For real gases, the Joule-Thomson coefficient $\mu_{\text{JT}}$ is positive below the inversion temperature (true for most natural gas conditions), producing cooling. Typical JT cooling: 3–6°C per MPa of pressure drop.

**Isentropic expansion (turboexpander):** The gas does work on the turbine wheel, extracting energy. The entropy is conserved (ideally):

$$
s_1 = s_2 \quad \Rightarrow \quad T_{2s} < T_{2,\text{JT}}
$$

Because isentropic expansion extracts energy that would otherwise remain as thermal energy in the gas, the isentropic outlet temperature is always lower than the isenthalpic outlet temperature for the same pressure ratio.

The temperature difference between the two processes depends on the gas composition and conditions:

| Parameter | JT Valve | Turboexpander (80% eff.) |
|-----------|----------|--------------------------|
| Cooling per 10 bar ΔP | 3–6°C | 5–10°C |
| Work recovery | None | 70–85% of isentropic work |
| NGL recovery | Low–moderate | High |
| Moving parts | None | High-speed rotating |
| CAPEX | Very low | High ($3–10 million) |
| OPEX | Negligible | Bearing/seal maintenance |
| Turndown | Excellent | Limited (40–110% of design) |
| Reliability | Very high | High (but requires maintenance) |

The turboexpander is economically justified when:
- The additional NGL recovery exceeds the annualized cost of the turboexpander
- The gas is rich enough to produce significant condensate (C$_3$+ > 3–4 mol%)
- A long operating period justifies the higher capital investment

For lean gas fields producing primarily methane with little C$_3$+ content, JT expansion is often sufficient for HCDP control. For rich gas or when ethane recovery is desired, the turboexpander is the standard technology.

**Retrograde condensation behavior** adds complexity to dew point control. When a gas condensate is expanded, the initial cooling produces more liquid, but as pressure continues to drop, some of the liquid re-vaporizes (retrograde behavior). The cold separator must operate at conditions that capture the maximum liquid, which is typically at the cricondenbar pressure on the dew point curve.

### 11.3.4 Mechanical Refrigeration

When the available pressure drop is insufficient for JT or turboexpander cooling, mechanical refrigeration provides external cooling. The most common refrigerant is propane, which operates in a closed-loop vapor-compression cycle:

1. **Chiller**: Propane evaporates at low pressure, cooling the process gas
2. **Compressor**: Propane vapor is compressed
3. **Condenser**: Compressed propane is condensed against air or cooling water
4. **Expansion valve**: Liquid propane flashes back to the evaporator pressure

Propane refrigeration can achieve gas temperatures of −30 to −40°C, sufficient for most HCDP specifications. For lower temperatures, cascade systems using ethane or ethylene as a secondary refrigerant extend the range to −60 to −100°C.

The coefficient of performance (COP) of a propane refrigeration cycle is:

$$\text{COP} = \frac{Q_{\text{evap}}}{W_{\text{comp}}} \approx 2.5\text{–}4.0$$

for typical gas processing conditions.

## 11.4 NGL Recovery and Fractionation

### 11.4.1 Economics of NGL Recovery

Natural gas liquids (C$_2$+) are often more valuable as separate products than as components of the sales gas. The decision to recover NGL depends on:

- **Product prices**: Ethane (petrochemical feedstock), LPG (propane + butane), and condensate (C$_5$+) prices relative to natural gas
- **Capital cost**: NGL recovery plant and fractionation train
- **Operating cost**: Compression power, refrigeration, and heat duties
- **Recovery level**: Ethane recovery (80–95%), propane recovery (95–99%), C$_4$+ recovery (>99%)

The ethane rejection flexibility — the ability to operate in either ethane recovery or ethane rejection mode depending on market prices — is a valuable design feature for NGL plants.

### 11.4.2 Turboexpander NGL Recovery

The turboexpander process is the dominant technology for NGL recovery from lean to moderately rich gases. The basic flow scheme includes:

1. **Inlet heat exchange**: Gas is cooled against cold plant products
2. **Turboexpander**: Gas expands to −60 to −100°C, condensing C$_2$+
3. **Demethanizer column**: Separates methane (overhead) from C$_2$+ (bottoms)
4. **Recompression**: Residue gas is compressed by the expander-coupled compressor

The key thermodynamic principle is that the isentropic expansion simultaneously cools the gas and reduces its pressure, shifting the phase envelope to favor liquid formation of heavy hydrocarbons.

**Enhanced turboexpander processes** include:
- **Gas subcooled process (GSP)**: A portion of the separator liquid is subcooled and used as reflux, improving ethane recovery to 85–92%
- **Recycle split vapor (RSV)**: Part of the residue gas is recycled to provide additional reflux
- **Cold residue recycle (CRR)**: Cold separator overhead is partially recycled after cooling, achieving ethane recovery above 95%

### 11.4.3 NGL Fractionation

The NGL stream from the demethanizer is separated into individual products in a series of distillation columns called the fractionation train:

1. **Deethanizer**: Separates ethane (overhead) from C$_3$+ (bottoms)
2. **Depropanizer**: Separates propane (overhead) from C$_4$+ (bottoms)
3. **Debutanizer**: Separates butanes (overhead) from C$_5$+ (bottoms, natural gasoline)

Each column is designed for a specific separation, with the number of stages and reflux ratio determined by the required product purity:

| Column | Typical Stages | Feed Location | Key Separation | Overhead Purity |
|--------|---------------|---------------|----------------|-----------------|
| Demethanizer | 15–30 | Top | C$_1$/C$_2$ | >98% CH$_4$ |
| Deethanizer | 25–35 | Middle | C$_2$/C$_3$ | >95% C$_2$ |
| Depropanizer | 30–40 | Middle | C$_3$/C$_4$ | >95% C$_3$ |
| Debutanizer | 25–35 | Middle | C$_4$/C$_5$ | >95% C$_4$ |

*Table 11.3: Typical design parameters for NGL fractionation columns.*

## 11.5 Acid Gas Removal

### 11.5.1 Acid Gas Components

Acid gases — primarily hydrogen sulfide (H$_2$S) and carbon dioxide (CO$_2$) — must be removed from natural gas for several reasons:

- **H$_2$S toxicity**: H$_2$S is lethal at concentrations above 500–700 ppm$_v$ and causes impairment at much lower levels
- **Corrosion**: Both CO$_2$ and H$_2$S cause severe corrosion in the presence of water
- **Pipeline specifications**: Typical limits are 4 ppm$_v$ H$_2$S and 2–3 mol% CO$_2$
- **Heating value**: CO$_2$ is inert and reduces the heating value of the gas
- **Environmental**: H$_2$S combustion produces SO$_2$; excess CO$_2$ affects carbon footprint

### 11.5.2 Amine Treating — Fundamentals

Chemical absorption using aqueous alkanolamine solutions is the most widely used acid gas removal technology. The amines react reversibly with CO$_2$ and H$_2$S:

**H$_2$S absorption** (instantaneous, ionic reaction):

$$\text{H}_2\text{S} + \text{R}_2\text{NH} \rightleftharpoons \text{R}_2\text{NH}_2^+ + \text{HS}^-$$

**CO$_2$ absorption by primary/secondary amines** (carbamate formation):

$$\text{CO}_2 + 2\text{RNH}_2 \rightleftharpoons \text{RNHCOO}^- + \text{RNH}_3^+$$

**CO$_2$ absorption by tertiary amines** (bicarbonate formation, slow):

$$\text{CO}_2 + \text{R}_3\text{N} + \text{H}_2\text{O} \rightleftharpoons \text{R}_3\text{NH}^+ + \text{HCO}_3^-$$

The key difference between primary/secondary amines (MEA, DEA) and tertiary amines (MDEA) is that the carbamate mechanism is fast and requires 2 moles of amine per mole of CO$_2$, while the bicarbonate mechanism is slow but requires only 1 mole of amine. This has profound implications for selective H$_2$S removal.

### 11.5.3 Common Amines

| Amine | Type | MW | Typical Conc. (wt%) | CO$_2$ Loading | Selectivity |
|-------|------|-----|---------------------|----------------|-------------|
| MEA | Primary | 61 | 15–20 | 0.3–0.4 mol/mol | Non-selective |
| DEA | Secondary | 105 | 25–35 | 0.3–0.5 mol/mol | Slightly selective |
| MDEA | Tertiary | 119 | 35–55 | 0.4–0.7 mol/mol | Highly H$_2$S selective |
| DGA | Primary | 105 | 50–60 | 0.3–0.4 mol/mol | Non-selective |
| DIPA | Secondary | 133 | 30–40 | 0.3–0.5 mol/mol | Moderately selective |

*Table 11.4: Common amines used for acid gas removal and their characteristics.*

**MDEA** is the most widely used amine today because of its key advantages:
- High selectivity for H$_2$S over CO$_2$ (exploiting the slow bicarbonate mechanism)
- Higher loading capacity (lower circulation rate)
- Lower heat of reaction with CO$_2$ (lower regeneration energy)
- Higher concentration (35–55 wt%) without excessive corrosion
- Lower vapor pressure (lower amine losses)

Activated MDEA formulations add small amounts of piperazine or other promoters to accelerate CO$_2$ absorption when both CO$_2$ and H$_2$S removal are needed.

### 11.5.4 Amine System Design

A standard amine treating unit consists of:

1. **Absorber**: Counter-current column (15–25 trays or equivalent packing) where lean amine contacts sour gas. Operating pressure is the gas pressure; temperature is 35–50°C.

2. **Flash drum**: Rich amine is flashed to remove co-absorbed hydrocarbons (reduces foaming and hydrocarbon losses).

3. **Lean–rich heat exchanger**: Rich amine is heated against lean amine, recovering heat and reducing reboiler duty.

4. **Regenerator (stripper)**: Rich amine is steam-stripped at low pressure (1.5–2.0 bara) to drive off acid gases. Reboiler temperature is 110–125°C.

5. **Condenser and reflux drum**: Overhead vapor is cooled to condense water, which is returned as reflux.

6. **Lean amine cooler**: Regenerated amine is cooled before returning to the absorber.

The amine circulation rate is determined by the acid gas loading:

$$\dot{m}_{\text{amine}} = \frac{Q_{\text{acid gas}}}{\alpha_{\text{rich}} - \alpha_{\text{lean}}} \times \frac{MW_{\text{amine}}}{w_{\text{amine}}}$$

where $\alpha$ is the acid gas loading (mol acid gas / mol amine), $MW_{\text{amine}}$ is the amine molecular weight, and $w_{\text{amine}}$ is the amine weight fraction.

#### Regeneration Energy

The regeneration energy (reboiler duty) is one of the largest operating costs of an amine unit. It consists of three components:

1. **Sensible heat**: Heating the rich amine from the heat exchanger outlet to the reboiler temperature
2. **Heat of reaction**: Reversing the exothermic acid gas absorption reactions
3. **Stripping steam**: Generating sufficient steam to maintain vapor traffic and reduce acid gas partial pressure

Typical regeneration energies by amine type:

| Amine | Reboiler Duty (GJ/tonne CO$_2$) | Reboiler Temperature (°C) |
|-------|--------------------------------|--------------------------|
| MEA 15–20% | 3.5–4.5 | 115–125 |
| DEA 25–35% | 3.0–3.5 | 110–120 |
| MDEA 50% | 2.5–3.0 | 110–120 |
| Activated MDEA | 2.0–2.8 | 110–120 |

The lower regeneration energy of MDEA (compared to MEA) is due to its lower heat of reaction with CO$_2$ and its ability to operate at higher concentrations (which reduces the sensible heat contribution).

#### Amine Degradation and Operational Issues

Amine degradation is a persistent operational challenge that increases makeup costs, causes foaming, and generates corrosive byproducts:

- **Oxidative degradation**: Occurs when oxygen enters the system (from air leaks or dissolved O$_2$ in feed gas). MEA is most susceptible; produces heat-stable salts (HSS) such as formate, acetate, and oxalate. MDEA is more resistant to oxidative degradation.
- **Thermal degradation**: Occurs at elevated temperatures (> 130°C for MEA, > 150°C for MDEA). The reboiler is the most vulnerable point; hot spots on fire-tube reboilers accelerate degradation.
- **CO$_2$-induced degradation**: MEA reacts irreversibly with CO$_2$ at high temperatures to form 2-oxazolidone (HEOD), which further degrades to other compounds. This is a primary reason MEA concentrations are limited to 15–20 wt%.

Mitigation strategies include: oxygen scavengers, nitrogen blanketing on tanks, proper reboiler design (low heat flux < 30 kW/m$^2$), activated carbon filtration to remove degradation products, and reclaimer operation to purge heat-stable salts.

#### NeqSim Amine Simulation Example

NeqSim models amine systems using the electrolyte CPA equation of state, which captures the chemical reactions between amines and acid gases:

```python
from neqsim import jneqsim

# Define sour gas with acid gases
sour_gas = jneqsim.thermo.system.SystemElectrolyteCPAstatoil(
    273.15 + 40.0, 70.0)
sour_gas.addComponent("methane", 90.0)
sour_gas.addComponent("CO2", 5.0)
sour_gas.addComponent("H2S", 0.5)
sour_gas.addComponent("water", 4.5)
sour_gas.setMixingRule(10)

# Define lean MDEA solution
lean_amine = jneqsim.thermo.system.SystemElectrolyteCPAstatoil(
    273.15 + 40.0, 70.0)
lean_amine.addComponent("MDEA", 50.0)
lean_amine.addComponent("water", 50.0)
lean_amine.setMixingRule(10)

# Create streams
gas_feed = jneqsim.process.equipment.stream.Stream("Sour Gas", sour_gas)
gas_feed.setFlowRate(5.0e6, "Sm3/day")
gas_feed.setTemperature(40.0, "C")
gas_feed.setPressure(70.0, "bara")

amine_feed = jneqsim.process.equipment.stream.Stream("Lean MDEA", lean_amine)
amine_feed.setFlowRate(5000.0, "kg/hr")
amine_feed.setTemperature(40.0, "C")
amine_feed.setPressure(70.0, "bara")

# Amine absorber column
absorber = jneqsim.process.equipment.absorber.SimpleTEGAbsorber("Amine Absorber")
absorber.addGasInStream(gas_feed)
absorber.addSolventInStream(amine_feed)
absorber.setNumberOfStages(15)

process = jneqsim.process.processmodel.ProcessSystem()
process.add(gas_feed)
process.add(amine_feed)
process.add(absorber)
process.run()

sweet_gas = absorber.getGasOutStream()
print(f"Sweet gas CO2: {sweet_gas.getFluid().getPhase('gas').getComponent('CO2').getx() * 1e6:.0f} ppm")
```

### 11.5.5 Physical Solvents Physical solvents absorb CO$_2$ proportionally to its partial pressure (Henry's law), without the stoichiometric limitation of chemical reactions.

**Selexol** (dimethyl ether of polyethylene glycol): Operates at ambient temperature, regenerated by pressure reduction and/or air stripping. Widely used for bulk CO$_2$ removal in high-pressure applications.

**Rectisol** (chilled methanol at −40 to −60°C): Achieves very deep removal (< 1 ppm CO$_2$). Used in synthesis gas applications and LNG plants. Requires refrigeration.

The solubility of CO$_2$ in a physical solvent follows Henry's law:

$$x_{\text{CO}_2} = \frac{P_{\text{CO}_2}}{H_{\text{CO}_2}(T)}$$

where $H_{\text{CO}_2}(T)$ is the Henry's law constant, which decreases with temperature (favoring absorption at lower temperatures).

## 11.6 Mercury Removal

Mercury in natural gas (typically 10–200 μg/Nm$^3$) attacks aluminum heat exchangers by amalgamation, causing catastrophic embrittlement failure. Mercury removal is essential upstream of any cryogenic processing equipment containing aluminum (plate-fin heat exchangers, turboexpanders).

### 11.6.1 Mercury Species and Sources

Mercury in natural gas exists in several forms:

- **Elemental mercury** (Hg$^0$): Volatile, carried in the gas phase. This is the dominant form.
- **Organic mercury compounds** (R-Hg): Dimethylmercury, diethylmercury. Present in condensate.
- **Ionic mercury** (Hg$^{2+}$): Associated with produced water.

Mercury concentrations vary dramatically by region. Southeast Asian fields (Sumatra, Thailand) can have 200+ μg/Nm$^3$, while North Sea fields typically have < 10 μg/Nm$^3$. The failure mechanism in aluminum heat exchangers is **liquid metal embrittlement (LME)**: mercury amalgamates with the aluminum grain boundaries, causing stress-corrosion cracking that can propagate to catastrophic failure with no warning.

### 11.6.2 Removal Technologies

The standard removal method uses fixed-bed adsorbents:

**Sulfur-impregnated activated carbon** is the most common adsorbent. Elemental mercury reacts with the sulfur to form cinnabar (HgS), which is highly stable:

$$
\text{Hg}^0 + \text{S} \rightarrow \text{HgS} \quad (\Delta G^0 = -50.6 \text{ kJ/mol})
$$

This adsorbent is non-regenerable and must be replaced when exhausted (typically 3–5 year bed life).

**Metal sulfide adsorbents** (CuS, ZnS on alumina support) offer higher capacity and faster kinetics. Copper sulfide converts mercury by displacement:

$$
\text{Hg}^0 + \text{CuS} \rightarrow \text{HgS} + \text{Cu}^0
$$

These adsorbents can also remove organic mercury compounds, which activated carbon may not fully capture.

**Silver-impregnated zeolites** are used for ultra-low mercury specifications (< 0.01 μg/Nm$^3$) required for some LNG plants.

### 11.6.3 Bed Sizing

Bed sizing follows:

$$V_{\text{bed}} = \frac{\dot{m}_{\text{Hg}} \times t_{\text{life}}}{C_{\text{Hg,capacity}} \times \rho_{\text{bed}}}$$

where $C_{\text{Hg,capacity}}$ is the adsorbent mercury capacity (typically 5–15 wt%) and $t_{\text{life}}$ is the desired bed life (typically 3–5 years).

The bed must be sized for the maximum expected mercury concentration, not the average. A typical guard bed arrangement uses two vessels in series (lead-lag configuration), where the lead bed is replaced when breakthrough is detected by mercury analyzers between the beds.

**Typical mercury specifications:**

| Application | Maximum Hg Level |
|-------------|-----------------|
| Pipeline gas | Not usually specified |
| LNG feed | < 0.01 μg/Nm$^3$ |
| Cryogenic NGL plant | < 0.1 μg/Nm$^3$ |
| Petrochemical feed | < 0.01 μg/Nm$^3$ |
| Condensate export | < 10 μg/kg |

### 11.6.4 Placement in the Process

Mercury removal is placed **downstream of dehydration** and **upstream of cryogenic equipment**. Wet gas can deactivate some mercury adsorbents by occupying active sites with water. The typical sequence is:

1. TEG or molecular sieve dehydration
2. Mercury removal bed
3. HCDP control (JT/turboexpander)
4. NGL recovery

## 11.6A Nitrogen Rejection

### 11.6A.1 When Nitrogen Rejection Is Required

Nitrogen is an inert gas that dilutes natural gas, reducing its heating value. Pipeline specifications typically require a maximum of 3–5 mol% nitrogen. Reservoirs with elevated nitrogen content (> 5–10 mol%) require nitrogen rejection to produce marketable gas.

Common sources of high nitrogen include:
- Nitrogen-rich reservoirs (some fields in the North Sea, Algeria, Russia)
- Nitrogen used for enhanced oil recovery (N$_2$ injection)
- Air ingress during production

### 11.6A.2 Nitrogen Rejection Technologies

**Cryogenic nitrogen rejection unit (NRU)** is the dominant technology for large-scale nitrogen removal. It exploits the volatility difference between nitrogen (BP = −196°C) and methane (BP = −161°C) through cryogenic distillation:

1. The feed gas is cooled to approximately −170°C in a cold box
2. A distillation column separates nitrogen overhead (>95% pure) from methane bottoms
3. The cold nitrogen stream provides refrigeration through heat exchange with the feed

Cryogenic NRU achieves > 98% methane recovery with nitrogen purity sufficient for venting or for sale as industrial nitrogen. For gas containing both nitrogen and helium, the NRU can be combined with a helium recovery unit (helium is even more volatile than nitrogen and concentrates in the overhead).

**Membrane separation** uses polymeric membranes that are selectively permeable to hydrocarbons over nitrogen. Nitrogen, being a slower-permeating gas, concentrates in the retentate (high-pressure side). Membranes are economically attractive for:
- Moderate nitrogen content (5–15 mol%)
- Small gas volumes (< 2 MSm$^3$/day)
- Offshore locations where cryogenic equipment is impractical

However, membrane systems have lower methane recovery (85–95%) compared to cryogenic NRU (>98%), and the methane lost to the permeate stream represents both a revenue loss and a potential emissions concern.

**Pressure swing adsorption (PSA)** uses molecular sieves that preferentially adsorb nitrogen at high pressure and release it at low pressure. PSA is suitable for small-scale applications (< 0.5 MSm$^3$/day) and can achieve nitrogen reduction to < 3 mol%.

### 11.6A.3 Technology Selection

| Parameter | Cryogenic NRU | Membrane | PSA |
|-----------|--------------|----------|-----|
| Scale | > 2 MSm$^3$/day | 0.5–5 MSm$^3$/day | < 0.5 MSm$^3$/day |
| N$_2$ in feed | Any level | 5–15 mol% | 5–20 mol% |
| CH$_4$ recovery | > 98% | 85–95% | 80–90% |
| N$_2$ purity | > 95% | N/A (rejected in CH$_4$ stream) | N/A |
| CAPEX | Very high | Low–moderate | Moderate |
| OPEX | High (compression, refrigeration) | Low (pressure-driven) | Moderate |
| Footprint | Large | Compact | Moderate |
| Helium recovery | Possible | No | No |

## 11.7 NeqSim Implementation

### 11.7.1 TEG Dehydration System

The following example demonstrates a complete TEG dehydration system modeled in NeqSim, including the absorber, regeneration column, and TEG recirculation:

```python
from neqsim import jneqsim

# ============================================================
# TEG Dehydration System — Complete Simulation
# ============================================================

# Define wet gas composition
wet_gas = jneqsim.thermo.system.SystemSrkCPAstatoil(
    273.15 + 30.0, 70.0)
wet_gas.addComponent("methane", 85.0)
wet_gas.addComponent("ethane", 5.0)
wet_gas.addComponent("propane", 2.5)
wet_gas.addComponent("n-butane", 1.0)
wet_gas.addComponent("n-pentane", 0.3)
wet_gas.addComponent("n-hexane", 0.1)
wet_gas.addComponent("CO2", 2.0)
wet_gas.addComponent("water", 4.0)
wet_gas.addComponent("TEG", 0.0)
wet_gas.setMixingRule(10)  # CPA mixing rule
wet_gas.setMultiPhaseCheck(True)

# Wet gas feed stream
wet_feed = jneqsim.process.equipment.stream.Stream(
    "Wet Gas Feed", wet_gas)
wet_feed.setFlowRate(10.0, "MSm3/day")
wet_feed.setTemperature(30.0, "C")
wet_feed.setPressure(70.0, "bara")

# Lean TEG stream
teg_fluid = jneqsim.thermo.system.SystemSrkCPAstatoil(
    273.15 + 43.0, 70.0)
teg_fluid.addComponent("methane", 0.0)
teg_fluid.addComponent("ethane", 0.0)
teg_fluid.addComponent("propane", 0.0)
teg_fluid.addComponent("n-butane", 0.0)
teg_fluid.addComponent("n-pentane", 0.0)
teg_fluid.addComponent("n-hexane", 0.0)
teg_fluid.addComponent("CO2", 0.0)
teg_fluid.addComponent("water", 0.01)
teg_fluid.addComponent("TEG", 0.99)
teg_fluid.setMixingRule(10)
teg_fluid.setMultiPhaseCheck(True)

lean_teg = jneqsim.process.equipment.stream.Stream(
    "Lean TEG", teg_fluid)
lean_teg.setFlowRate(5000.0, "kg/hr")
lean_teg.setTemperature(43.0, "C")
lean_teg.setPressure(70.0, "bara")

# TEG Absorber Column
absorber = jneqsim.process.equipment.distillation.DistillationColumn(
    "TEG Absorber", 5, False, False)
absorber.addFeedStream(wet_feed, 5)    # Gas enters at bottom
absorber.addFeedStream(lean_teg, 1)    # TEG enters at top

# Build and run process
process = jneqsim.process.processmodel.ProcessSystem()
process.add(wet_feed)
process.add(lean_teg)
process.add(absorber)
process.run()

# Get results
dry_gas = absorber.getGasOutStream()
rich_teg = absorber.getLiquidOutStream()

print("=== TEG Dehydration Results ===")
print(f"Dry gas flow:  {dry_gas.getFlowRate('MSm3/day'):.2f} MSm3/day")
print(f"Dry gas T:     {dry_gas.getTemperature('C'):.1f} C")
print(f"Rich TEG flow: {rich_teg.getFlowRate('kg/hr'):.0f} kg/hr")
print(f"Rich TEG T:    {rich_teg.getTemperature('C'):.1f} C")

# Water content of dry gas
dry_gas.getFluid().initProperties()
water_in_gas = dry_gas.getFluid().getPhase("gas").getComponent(
    "water").getx() * 1e6
print(f"Water in dry gas: {water_in_gas:.1f} ppm (mole)")
```

### 11.7.2 JT Dew Point Control

This example shows how to model Joule–Thomson cooling for hydrocarbon dew point control:

```python
from neqsim import jneqsim

# Define rich gas (with significant C5+ content)
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, 70.0)
gas.addComponent("nitrogen", 0.5)
gas.addComponent("CO2", 2.0)
gas.addComponent("methane", 80.0)
gas.addComponent("ethane", 6.0)
gas.addComponent("propane", 4.0)
gas.addComponent("i-butane", 1.2)
gas.addComponent("n-butane", 2.0)
gas.addComponent("i-pentane", 0.8)
gas.addComponent("n-pentane", 0.7)
gas.addComponent("n-hexane", 1.0)
gas.addComponent("n-heptane", 0.5)
gas.addComponent("n-octane", 0.3)
gas.addComponent("water", 1.0)
gas.setMixingRule("classic")
gas.setMultiPhaseCheck(True)

# Feed stream
feed = jneqsim.process.equipment.stream.Stream("Rich Gas", gas)
feed.setFlowRate(5.0, "MSm3/day")
feed.setTemperature(30.0, "C")
feed.setPressure(70.0, "bara")

# Gas-gas heat exchanger (inlet cooling)
inlet_cooler = jneqsim.process.equipment.heatexchanger.Heater(
    "Inlet Cooler", feed)
inlet_cooler.setOutTemperature(273.15 + 10.0)

# JT Valve
jt_valve = jneqsim.process.equipment.valve.ThrottlingValve(
    "JT Valve", inlet_cooler.getOutletStream())
jt_valve.setOutletPressure(40.0)

# Cold separator
cold_sep = jneqsim.process.equipment.separator.Separator(
    "Cold Separator", jt_valve.getOutletStream())

# Build process
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(inlet_cooler)
process.add(jt_valve)
process.add(cold_sep)
process.run()

# Results
cold_gas = cold_sep.getGasOutStream()
condensate = cold_sep.getLiquidOutStream()

print("=== JT Dew Point Control Results ===")
print(f"Feed T/P:        {feed.getTemperature('C'):.1f} C / "
      f"{feed.getPressure():.1f} bara")
print(f"After cooler:    {inlet_cooler.getOutletStream().getTemperature('C'):.1f} C")
print(f"After JT valve:  {jt_valve.getOutletStream().getTemperature('C'):.1f} C / "
      f"{jt_valve.getOutletStream().getPressure():.1f} bara")
print(f"Cold sep gas:    {cold_gas.getFlowRate('MSm3/day'):.3f} MSm3/day")
print(f"Condensate:      {condensate.getFlowRate('kg/hr'):.1f} kg/hr")

# Calculate the dew point of the processed gas
dew_gas = cold_gas.getFluid().clone()
ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(dew_gas)
ops.dewPointTemperatureFlash()
print(f"HC dew point:    {dew_gas.getTemperature('C'):.1f} C "
      f"at {dew_gas.getPressure():.1f} bara")
```

### 11.7.3 NGL Fractionation — Deethanizer Example

```python
from neqsim import jneqsim

# NGL feed from turboexpander plant
ngl = jneqsim.thermo.system.SystemSrkEos(273.15 + (-30.0), 25.0)
ngl.addComponent("methane", 5.0)
ngl.addComponent("ethane", 35.0)
ngl.addComponent("propane", 25.0)
ngl.addComponent("i-butane", 8.0)
ngl.addComponent("n-butane", 12.0)
ngl.addComponent("i-pentane", 5.0)
ngl.addComponent("n-pentane", 5.0)
ngl.addComponent("n-hexane", 3.0)
ngl.addComponent("n-heptane", 2.0)
ngl.setMixingRule("classic")

# NGL feed stream
ngl_feed = jneqsim.process.equipment.stream.Stream("NGL Feed", ngl)
ngl_feed.setFlowRate(2000.0, "kg/hr")
ngl_feed.setTemperature(-30.0, "C")
ngl_feed.setPressure(25.0, "bara")

# Deethanizer column
deethanizer = jneqsim.process.equipment.distillation.DistillationColumn(
    "Deethanizer", 25, True, True)
deethanizer.addFeedStream(ngl_feed, 12)
deethanizer.setCondenserTemperature(273.15 + (-25.0))
deethanizer.getReboiler().setReBoilerDuty(200000.0)  # W

# Build and run
process = jneqsim.process.processmodel.ProcessSystem()
process.add(ngl_feed)
process.add(deethanizer)
process.run()

# Results
overhead = deethanizer.getCondenser().getGasOutStream()
bottoms = deethanizer.getReboiler().getLiquidOutStream()

print("=== Deethanizer Results ===")
print(f"Overhead T: {overhead.getTemperature('C'):.1f} C")
print(f"Overhead P: {overhead.getPressure():.1f} bara")
print(f"Bottoms T:  {bottoms.getTemperature('C'):.1f} C")
print(f"Reboiler duty: "
      f"{deethanizer.getReboiler().getDuty()/1e3:.1f} kW")
```

### 11.7.4 Complete Gas Processing Train

This comprehensive example combines dehydration, JT dew point control, and NGL separation into an integrated gas processing simulation:

```python
from neqsim import jneqsim

# ============================================================
# Integrated Gas Processing Simulation
# ============================================================

# Step 1: Define the raw gas
raw_gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 35.0, 80.0)
raw_gas.addComponent("nitrogen", 1.0)
raw_gas.addComponent("CO2", 2.5)
raw_gas.addComponent("methane", 78.0)
raw_gas.addComponent("ethane", 6.5)
raw_gas.addComponent("propane", 4.0)
raw_gas.addComponent("i-butane", 1.2)
raw_gas.addComponent("n-butane", 2.0)
raw_gas.addComponent("i-pentane", 0.8)
raw_gas.addComponent("n-pentane", 0.6)
raw_gas.addComponent("n-hexane", 0.8)
raw_gas.addComponent("n-heptane", 0.3)
raw_gas.addComponent("n-octane", 0.2)
raw_gas.addComponent("water", 2.1)
raw_gas.setMixingRule("classic")
raw_gas.setMultiPhaseCheck(True)

# Feed stream
feed = jneqsim.process.equipment.stream.Stream("Raw Gas", raw_gas)
feed.setFlowRate(8.0, "MSm3/day")
feed.setTemperature(35.0, "C")
feed.setPressure(80.0, "bara")

# Step 2: Inlet separation (remove free water and liquids)
inlet_sep = jneqsim.process.equipment.separator.ThreePhaseSeparator(
    "Inlet Separator", feed)

# Step 3: Gas cooling and dew point control
gas_cooler = jneqsim.process.equipment.heatexchanger.Heater(
    "Gas Cooler", inlet_sep.getGasOutStream())
gas_cooler.setOutTemperature(273.15 + 15.0)

# JT expansion
jt_valve = jneqsim.process.equipment.valve.ThrottlingValve(
    "JT Valve", gas_cooler.getOutletStream())
jt_valve.setOutletPressure(55.0)

# Cold separator
cold_sep = jneqsim.process.equipment.separator.Separator(
    "Cold Separator", jt_valve.getOutletStream())

# Step 4: Recompression of sales gas
compressor = jneqsim.process.equipment.compressor.Compressor(
    "Recompressor", cold_sep.getGasOutStream())
compressor.setOutletPressure(70.0)

after_cooler = jneqsim.process.equipment.heatexchanger.Heater(
    "After Cooler", compressor.getOutletStream())
after_cooler.setOutTemperature(273.15 + 30.0)

# Build process
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(inlet_sep)
process.add(gas_cooler)
process.add(jt_valve)
process.add(cold_sep)
process.add(compressor)
process.add(after_cooler)
process.run()

# Report results
sales_gas = after_cooler.getOutletStream()
ngl = cold_sep.getLiquidOutStream()

print("=" * 60)
print("INTEGRATED GAS PROCESSING RESULTS")
print("=" * 60)
print(f"\nRaw gas rate:     {feed.getFlowRate('MSm3/day'):.2f} MSm3/day")
print(f"Sales gas rate:   {sales_gas.getFlowRate('MSm3/day'):.2f} MSm3/day")
print(f"NGL condensate:   {ngl.getFlowRate('kg/hr'):.0f} kg/hr")
print(f"Sales gas T/P:    {sales_gas.getTemperature('C'):.1f} C / "
      f"{sales_gas.getPressure():.1f} bara")
print(f"Compressor power: {compressor.getPower()/1e3:.1f} kW")
print(f"JT temperature:   {jt_valve.getOutletStream().getTemperature('C'):.1f} C")
```

## 11.8 Phase Envelope and Dew Point Calculations

Understanding the phase envelope of the gas is essential for specifying the required dew point control. NeqSim can calculate the complete phase envelope, including the cricondentherm and cricondenbar:

```python
from neqsim import jneqsim

# Define gas composition for phase envelope
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 20.0, 50.0)
gas.addComponent("nitrogen", 1.0)
gas.addComponent("CO2", 2.5)
gas.addComponent("methane", 80.0)
gas.addComponent("ethane", 6.0)
gas.addComponent("propane", 4.0)
gas.addComponent("i-butane", 1.0)
gas.addComponent("n-butane", 2.0)
gas.addComponent("i-pentane", 0.5)
gas.addComponent("n-pentane", 0.5)
gas.addComponent("n-hexane", 1.0)
gas.addComponent("n-heptane", 0.5)
gas.addComponent("n-octane", 1.0)
gas.setMixingRule("classic")

ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(gas)
ops.calcPTphaseEnvelope()

# Extract data for plotting
temperatures = []
pressures = []
dew_temps = ops.getOperation().get("dewT")
dew_pres = ops.getOperation().get("dewP")
bub_temps = ops.getOperation().get("bubT")
bub_pres = ops.getOperation().get("bubP")

print("Phase envelope calculated successfully")
print(f"Number of dew points: {len(list(dew_temps))}")
print(f"Number of bubble points: {len(list(bub_temps))}")
```

![Phase envelope showing dew point and bubble point curves with cricondentherm and cricondenbar marked](figures/phase_envelope_gas.png)

*Figure 11.2: Phase envelope for a typical rich gas showing the dew point line, bubble point line, cricondentherm (maximum temperature), and cricondenbar (maximum pressure). The pipeline operating envelope must remain to the right of the dew point curve at all pressures.*

## 11.9 Gas Sweetening — Detailed Considerations

### 11.9.1 Selective H$_2$S Removal

In many applications, only H$_2$S removal is required while CO$_2$ may remain in the gas (e.g., for enhanced oil recovery or when CO$_2$ content is already within specification). MDEA provides selective H$_2$S removal by exploiting the kinetic difference between the fast ionic H$_2$S reaction and the slow CO$_2$ hydration reaction.

The selectivity factor is defined as:

$$S = \frac{y_{\text{H}_2\text{S,feed}} / y_{\text{H}_2\text{S,product}}}{y_{\text{CO}_2\text{,feed}} / y_{\text{CO}_2\text{,product}}}$$

MDEA typically achieves selectivity factors of 5–15, depending on:
- Absorber height (fewer trays = more selective)
- TEG circulation rate (lower rate = more selective)
- Temperature (lower temperature = more selective)
- CO$_2$/H$_2$S ratio in the feed

### 11.9.2 Regeneration Energy

The specific regeneration energy (heat duty per unit of acid gas removed) is a critical economic parameter:

| Amine | Typical Regen. Energy (GJ/t CO$_2$) | Reboiler T (°C) |
|-------|--------------------------------------|-----------------|
| MEA 30% | 3.5–4.5 | 120–125 |
| DEA 30% | 3.0–3.5 | 115–120 |
| MDEA 50% | 2.5–3.0 | 110–120 |
| Activated MDEA | 2.0–2.8 | 110–120 |

*Table 11.5: Typical specific regeneration energy for different amine systems.*

The heat of regeneration includes three contributions:

$$Q_{\text{regen}} = Q_{\text{sensible}} + Q_{\text{reaction}} + Q_{\text{stripping steam}}$$

where $Q_{\text{sensible}}$ is the heat to raise the rich amine from the exchanger outlet temperature to the reboiler temperature, $Q_{\text{reaction}}$ is the heat of acid gas desorption (reverse of absorption), and $Q_{\text{stripping steam}}$ is the energy of the stripping steam that provides vapor traffic in the regenerator.

## 11.10 Comparison of Gas Processing Technologies

The choice of gas processing technology depends on multiple factors. Table 11.6 provides a comparison matrix:

| Criterion | TEG Dehyd. | Mol. Sieve | JT Valve | Turboexpander | Mech. Refrig. |
|-----------|-----------|-----------|---------|---------------|--------------|
| Dew point (°C) | −18 to −40 | < −75 | −15 to −30 | −60 to −100 | −30 to −40 |
| CAPEX | Low | Medium | Low | High | Medium |
| OPEX | Low | Medium | None | Low | Medium |
| Power req. | Low | Medium | None | Net producer | High |
| Pressure drop | Low | Low | High | Medium | Low |
| NGL recovery | No | No | Partial | High | Moderate |
| Turndown | Good | Good | Poor | Moderate | Good |
| Footprint | Medium | Large | Small | Medium | Medium |

*Table 11.6: Comparison of gas processing technologies for dew point control and NGL recovery.*

## 11.11 Summary

This chapter has covered the major gas processing operations required to convert raw natural gas into pipeline-quality sales gas and valuable NGL products:

1. **TEG dehydration** is the standard method for water dew point control, with enhanced regeneration (stripping gas, Stahl column, Drizo) extending the achievable dew point depression below −40°C.

2. **Hydrocarbon dew point control** can be achieved through JT cooling (simple, low CAPEX), turboexpander (efficient, work recovery), or mechanical refrigeration (independent of pressure drop).

3. **NGL recovery** using turboexpander processes with demethanizer columns can achieve ethane recovery above 90% with modern enhanced processes.

4. **Acid gas removal** using amine treating is the standard for H$_2$S and CO$_2$ removal, with MDEA offering selective H$_2$S removal and lower regeneration energy.

5. **NeqSim provides** comprehensive modeling capability for all these unit operations, with the CPA equation of state being particularly important for accurate water–glycol–hydrocarbon equilibria in dehydration calculations.

6. The **integration** of these processing steps requires careful attention to heat and pressure management to minimize energy consumption and maximize product recovery.

## Exercises

**Exercise 11.1**: Design a TEG dehydration system to achieve a water dew point of −18°C for a gas at 70 bara and 30°C with a flow rate of 5 MSm$^3$/day. Determine the required TEG concentration, circulation rate, and number of absorber trays.

**Exercise 11.2**: Compare JT cooling and turboexpander technologies for a gas with the following composition (mol%): C$_1$ 82, C$_2$ 6, C$_3$ 4, iC$_4$ 1, nC$_4$ 2, iC$_5$ 0.8, nC$_5$ 0.6, C$_6$ 0.5, C$_7$+ 0.3, N$_2$ 1, CO$_2$ 1.8. The inlet conditions are 80 bara and 30°C. The cricondentherm must be below −2°C.

**Exercise 11.3**: Model a deethanizer column for an NGL feed with the composition given in Example 11.7.3. Determine the number of trays and reflux ratio required to achieve 95% ethane recovery with less than 2% propane in the overhead product.

**Exercise 11.4**: Calculate the phase envelope (dew point and bubble point curves) for the gas in Exercise 11.2 using NeqSim. Identify the cricondentherm and cricondenbar. Determine the minimum temperature to which the gas must be cooled to meet the HCDP specification at all pressures between 40 and 120 bara.

**Exercise 11.5**: Design an MDEA treating system to reduce H$_2$S from 500 ppm$_v$ to 4 ppm$_v$ in a gas containing 3 mol% CO$_2$. Calculate the required MDEA circulation rate, number of absorber trays, and regeneration energy.

**Exercise 11.6**: Compare the economics of TEG dehydration versus molecular sieve dehydration for a gas rate of 10 MSm$^3$/day requiring a water dew point of −40°C. Consider capital cost, operating cost, space requirements, and maintenance.

**Exercise 11.7**: Model an integrated gas processing plant in NeqSim that includes inlet separation, JT dew point control, and recompression. Optimize the JT outlet pressure to minimize compressor power while meeting a cricondentherm specification of −2°C.

## References

1. Campbell, J.M. (2014). *Gas Conditioning and Processing, Vol. 2: The Equipment Modules*, 9th ed. Campbell Petroleum Series.
2. Kidnay, A.J., Parrish, W.R., and McCartney, D.G. (2011). *Fundamentals of Natural Gas Processing*, 2nd ed. CRC Press.
3. Kohl, A.L. and Nielsen, R.B. (1997). *Gas Purification*, 5th ed. Gulf Professional Publishing.
4. GPSA Engineering Data Book (2004). 12th ed. Gas Processors Suppliers Association.
5. Manning, F.S. and Thompson, R.E. (1991). *Oilfield Processing of Petroleum, Vol. 1: Natural Gas*. PennWell Books.
6. Mokhatab, S., Poe, W.A., and Mak, J.Y. (2019). *Handbook of Natural Gas Transmission and Processing*, 4th ed. Gulf Professional Publishing.
7. Carroll, J.J. (2014). *Natural Gas Hydrates: A Guide for Engineers*, 3rd ed. Gulf Professional Publishing.
8. Maddox, R.N. and Morgan, D.J. (2006). *Gas Conditioning and Processing, Vol. 4: Gas Treating and Sulfur Recovery*. Campbell Petroleum Series.
9. Younger, A.H. (2004). Natural gas processing principles and technology. Technical report, University of Calgary.
10. Solbraa, E. (2002). Measurement and modelling of absorption of carbon dioxide into methyldiethanolamine solutions at high pressures. PhD thesis, Norwegian University of Science and Technology.
11. Kontogeorgis, G.M. and Folas, G.K. (2010). *Thermodynamic Models for Industrial Applications*. John Wiley & Sons.
12. NORSOK P-002 (2014). Process System Design. Standards Norway.


## Figures

![Figure 12.1: Fig11 1 Water Content](figures/fig11_1_water_content.png)

*Figure 12.1: Fig11 1 Water Content*

![Figure 12.2: Fig11 2 Jt Cooling](figures/fig11_2_jt_cooling.png)

*Figure 12.2: Fig11 2 Jt Cooling*

![Figure 12.3: Fig11 3 Turbo Expander Profile](figures/fig11_3_turbo_expander_profile.png)

*Figure 12.3: Fig11 3 Turbo Expander Profile*

![Figure 12.4: Fig11 4 Dewpoint Control](figures/fig11_4_dewpoint_control.png)

*Figure 12.4: Fig11 4 Dewpoint Control*
