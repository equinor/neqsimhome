# Fluid Characterization and PVT Modeling

<!-- Chapter metadata -->
<!-- Notebooks: ch03_fluid_characterization.ipynb, ch03_pvt_simulations.ipynb, ch03_plus_fraction.ipynb -->
<!-- Estimated pages: 35 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Classify reservoir fluids by type (black oil, volatile oil, gas condensate, dry gas, wet gas) and explain their distinguishing characteristics
2. Describe common PVT laboratory experiments and their role in fluid characterization
3. Apply plus fraction characterization methods (Whitson gamma distribution, Pedersen) to extend a fluid analysis into pseudo-components
4. Use NeqSim to create characterized fluids with plus fractions and run PVT simulations
5. Tune EOS parameters to match experimental PVT data
6. Generate and interpret phase envelopes for different fluid types
7. Calculate key PVT properties: GOR, formation volume factor, API gravity, and compressibility
8. Evaluate fluid samples for quality and apply recombination procedures
9. Select between black oil correlations and compositional models for different engineering applications

## 3.1 Introduction

Accurate fluid characterization is the starting point for every production optimization model. The reservoir fluid — a complex mixture of hundreds or thousands of hydrocarbon species plus non-hydrocarbons — determines the phase behavior, flow properties, and processing requirements of the entire production system. A poor fluid model propagates errors through every subsequent calculation: wrong phase envelopes lead to incorrect separator design, wrong viscosities produce inaccurate pressure drops, and wrong compositions give misleading export specifications.

This chapter covers the complete fluid characterization workflow: from understanding what the laboratory measures, through the mathematical methods for representing the heavy end of the composition, to the practical steps of building and tuning a fluid model in NeqSim.

![Workflow from reservoir fluid sampling through PVT analysis to calibrated EOS model](figures/fluid_characterization_workflow.png)

## 3.2 Reservoir Fluid Types

Reservoir fluids are classified based on their initial conditions relative to the phase envelope, the gas-oil ratio (GOR), and the liquid content at surface conditions.

### 3.2.1 Classification Criteria

The five standard fluid types are:

| Fluid Type | GOR (Sm³/Sm³) | API Gravity | Oil FVF $B_o$ | Key Characteristic |
|-----------|----------------|-------------|---------------|-------------------|
| Black oil | < 200 | 15–40 | 1.0–2.0 | Reservoir T < critical T; wide two-phase region |
| Volatile oil | 200–600 | 40–50 | 1.5–3.0 | Close to critical point; significant shrinkage |
| Gas condensate | 600–15,000 | 40–60 | — | Reservoir T between Tc and cricondentherm |
| Wet gas | 15,000–100,000 | 40–60 | — | Single phase in reservoir; liquid at surface |
| Dry gas | > 100,000 | — | — | No liquid at any conditions |

### 3.2.2 Phase Envelope Characteristics

The position of the initial reservoir conditions on the phase envelope determines the fluid type:

- **Black oil:** Initial conditions are well to the left of the critical point; the reservoir is at a temperature below the critical temperature. As pressure drops during depletion, the fluid crosses the bubble point and gas evolves.
- **Volatile oil:** Initial conditions are near but to the left of the critical point. The fluid exhibits large changes in properties with small changes in pressure.
- **Gas condensate:** Initial conditions are to the right of the critical point. The reservoir temperature is between the critical temperature and the cricondentherm. As pressure drops below the dew point, retrograde condensation occurs — liquid drops out in the reservoir.
- **Wet gas:** The reservoir temperature exceeds the cricondentherm. The fluid is always single-phase in the reservoir, but at surface conditions it falls within the two-phase region, yielding some condensate.
- **Dry gas:** The phase envelope is so narrow that even surface conditions remain outside the two-phase region.

![Phase envelopes for the five reservoir fluid types showing the relationship between initial reservoir conditions and fluid classification](figures/fluid_type_phase_envelopes.png)

### 3.2.3 Fluid Type Identification from Field Data

In practice, fluid type is identified from:

1. **Initial producing GOR** — measured at the test separator
2. **Stock tank oil gravity (API)** — from sample analysis
3. **Reservoir temperature and pressure** — from well logs and DST data
4. **C$_{7+}$ fraction** — higher C$_{7+}$ content indicates heavier fluid
5. **Visual observation** — color of separator liquid (clear/straw = condensate; brown/black = oil)

Table 3.1 provides heuristic guidelines:

| Property | Black Oil | Volatile Oil | Gas Condensate | Wet Gas |
|----------|-----------|-------------|----------------|---------|
| C$_{7+}$ mol% | > 20 | 12–20 | 4–12 | < 4 |
| Initial GOR (Sm³/Sm³) | < 200 | 200–600 | 600–15,000 | > 15,000 |
| Stock tank API | < 40 | 40–50 | 40–60 | 40–60 |
| Fluid color | Black/dark brown | Brown/dark orange | Straw/light brown | Water-white |

## 3.3 Fluid Sampling

### 3.3.1 Sampling Methods

Reservoir fluid samples are collected by two fundamentally different methods, each with specific advantages and limitations.

**Bottomhole sampling** uses a wireline-conveyed tool (e.g., MDT, RDT, or RCI) to capture fluid directly at reservoir conditions. The tool is positioned opposite a permeable zone, a drawdown is applied, and a sample chamber is filled at in-situ pressure and temperature. The key requirement is that the bottomhole flowing pressure during sampling must exceed the saturation pressure; otherwise, the sample captures a two-phase mixture that is not representative of the original single-phase reservoir fluid.

**Surface recombination sampling** collects separator gas and separator liquid samples at the test separator, then recombines them in the laboratory at the measured producing GOR. This method is used when bottomhole sampling is impractical (e.g., gas condensate wells with high GOR, deep offshore wells) or when operating conditions prevent single-phase sampling.

### 3.3.2 Recombination Calculation

For surface recombination, the laboratory recombines separator gas and liquid at the measured separator GOR. The recombination calculation determines the mole fractions $z_i$ of each component in the reservoir fluid:

$$
z_i = \frac{n_g y_i + n_o x_i}{n_g + n_o}
$$

where $y_i$ is the mole fraction in the separator gas, $x_i$ is the mole fraction in the separator liquid, and $n_g / n_o$ is the molar gas-to-oil ratio. The molar ratio relates to the volumetric GOR by:

$$
\frac{n_g}{n_o} = \frac{\text{GOR} \cdot \rho_o^{\text{sc}} / M_o}{P^{\text{sc}} / (Z^{\text{sc}} R T^{\text{sc}})}
$$

In practice, the laboratory adjusts the GOR slightly during recombination to match the measured saturation pressure, ensuring a self-consistent sample.

### 3.3.3 Sample Quality Control

Sample quality is critical. Contamination with drilling mud, phase segregation during sampling, or loss of light ends during transfer can invalidate the entire PVT study. The following QC checks are applied:

1. **Consistency check:** Opening pressure of the sample bottle should match the expected reservoir or separator pressure. A lower opening pressure indicates leak or gas loss.
2. **Contamination monitoring:** MDT tool measures optical density during sampling to track mud filtrate contamination. Contamination below 5% is generally acceptable.
3. **Material balance:** The sum of separator gas and separator liquid compositions, recombined at the field GOR, should yield a single-phase fluid at reservoir conditions. If the recombined fluid is two-phase at the reported reservoir pressure, the sample or GOR data may be incorrect.
4. **Comparison with offset wells:** Saturation pressure, GOR, and C$_{7+}$ content should be consistent with neighboring wells in the same reservoir.
5. **Methane content check:** A sudden drop in methane content compared to offset data suggests gas loss during sampling.
6. **Repeatability:** Multiple PVT experiments should give consistent saturation pressures (within ±2–3%).

### 3.3.4 Choosing the Right Sampling Method

| Criterion | Bottomhole Sampling | Surface Recombination |
|-----------|--------------------|-----------------------|
| Fluid type | Black oil, volatile oil | Gas condensate, wet gas |
| GOR range | < 500 Sm³/Sm³ | > 500 Sm³/Sm³ |
| Reservoir pressure | Well above $P_{\text{sat}}$ | Any |
| Cost | Higher (wireline run) | Lower (separator samples) |
| Accuracy | Higher (single-phase) | Depends on GOR accuracy |
| Risk | Sampling below bubble point | Incorrect GOR |

## 3.4 PVT Laboratory Experiments

PVT experiments are conducted on reservoir fluid samples to measure phase behavior and properties at reservoir and process conditions. These measurements provide the data against which EOS models are tuned.

### 3.4.1 Constant Composition Expansion (CCE)

The CCE experiment measures the pressure-volume relationship of a reservoir fluid at reservoir temperature:

1. The sample is loaded into a PVT cell at a pressure above the saturation point
2. Pressure is reduced in steps, and the total volume is recorded at each step
3. The saturation pressure (bubble point for oil, dew point for gas condensate) is identified as the pressure where the slope of the $P$-$V$ curve changes
4. Below the saturation pressure, the total volume (gas + liquid) continues to be measured

The relative volume $V_{\text{rel}}$ at each pressure step is defined as:

$$
V_{\text{rel}} = \frac{V_t}{V_{\text{sat}}}
$$

where $V_t$ is the total volume at pressure $P$ and $V_{\text{sat}}$ is the volume at the saturation pressure. Above the saturation pressure, the fluid is single-phase and the relative volume is governed by isothermal compressibility:

$$
V_{\text{rel}} = \exp\left[c_o (P_{\text{sat}} - P)\right] \approx 1 + c_o (P_{\text{sat}} - P)
$$

Below the saturation pressure, gas evolves and the relative volume increases sharply. The Y-function provides a linearization useful for smoothing CCE data below the bubble point:

$$
Y = \frac{P_b - P}{P(V_{\text{rel}} - 1)}
$$

A plot of $Y$ vs. $P$ should approximate a straight line, and deviations indicate data quality issues.

For gas condensates, the CCE also measures the **liquid dropout curve** — the volume fraction of liquid in the cell as a function of pressure below the dew point. This is the retrograde condensation curve and is critical for reservoir simulation.

### 3.4.2 Constant Volume Depletion (CVD)

The CVD experiment simulates the depletion of a gas condensate reservoir where retrograde liquid remains immobile in the pore space:

1. The sample starts at the dew point pressure at reservoir temperature
2. Pressure is reduced in a step (typically 25–50 bar increments)
3. Gas is removed from the top of the cell to restore the original cell volume
4. The volume, composition, and Z-factor of the removed gas are measured
5. The liquid dropout (retrograde condensation volume) at each pressure is measured
6. Steps 2–5 are repeated down to abandonment pressure

The key quantities measured at each depletion step $j$ are:

- **Liquid dropout** $V_{\text{liq}} / V_{\text{cell}}$: Volume fraction of retrograde liquid
- **Gas Z-factor** from the removed gas: $Z_j = P_j V_{\text{removed}} / (n_{\text{removed}} R T)$
- **Cumulative recovery** of each component: $R_i = \sum_j y_{i,j} \Delta n_j / (z_i n_{\text{total}})$
- **Two-phase Z-factor**: $Z_{\text{2ph}} = Z_j (1 - \sum \Delta n_j / n_{\text{total}})$, used in the $P/Z$ material balance for gas condensate reservoirs

CVD data is essential for calibrating the EOS model for gas condensate production forecasting, particularly the liquid dropout curve and the changing gas composition with depletion.

### 3.4.3 Differential Liberation (DL)

The differential liberation experiment applies to black oil and volatile oil systems:

1. The sample starts at the bubble point at reservoir temperature
2. Pressure is reduced in a step
3. **All** evolved gas is removed at that pressure, and its volume and composition are measured
4. The remaining oil volume at that pressure is recorded
5. Steps 2–4 are repeated down to atmospheric pressure
6. The residual oil volume at 60°F (15.6°C) and atmospheric pressure is measured

The key outputs calculated from DL data are:

**Solution GOR** at each pressure:

$$
R_{s,j} = R_{s,j-1} - \frac{V_{g,j}^{\text{sc}}}{V_{o,\text{residual}}^{\text{sc}}}
$$

**Oil formation volume factor** relative to residual oil:

$$
B_{od,j} = \frac{V_{o,j}}{V_{o,\text{residual}}}
$$

**Gas formation volume factor** at each step:

$$
B_g = \frac{V_{g,j}}{V_{g,j}^{\text{sc}}} = \frac{Z_j T P^{\text{sc}}}{T^{\text{sc}} P_j}
$$

Note that DL values of $B_o$ and $R_s$ must be corrected using the separator test results before use in reservoir simulation, because the DL flashes all gas at each step (which differs from the separator flash path).

### 3.4.4 Separator Test

The separator test measures the GOR and oil properties at specific separator conditions:

1. A sample at the bubble point is flashed through a multi-stage separator train
2. Gas and liquid volumes are measured at each stage
3. The final stock tank oil volume, API gravity, and GOR are recorded

This test is critical because it defines the reference conditions for reporting field data:

$$
B_o = \frac{V_{\text{oil at reservoir conditions}}}{V_{\text{stock tank oil at standard conditions}}}
$$

The separator test also provides the correction factor $B_{ob}$ to convert DL-based $B_o$ values to separator-flash-based values:

$$
B_o = B_{od} \frac{B_{ob}}{B_{od,b}}
$$

$$
R_s = R_{s,d} \frac{B_{ob}}{B_{od,b}} + R_{sb} - R_{sd,b} \frac{B_{ob}}{B_{od,b}}
$$

where subscript $b$ denotes bubble-point values and subscript $d$ denotes DL values.

### 3.4.5 Swelling Test

The swelling test measures the effect of injecting gas (lean gas, CO$_2$, N$_2$) into a reservoir oil:

1. A reservoir oil sample is loaded at its bubble point
2. Gas is injected in measured amounts (typically 5–20 mol% increments)
3. The new bubble point pressure and swollen volume are measured after each injection
4. The process reveals how much gas can be dissolved and the resulting pressure changes

The swelling factor $S_f$ at each injection step is:

$$
S_f = \frac{V_{\text{sat, swollen}}}{V_{\text{sat, original}}}
$$

Swelling test data is essential for:

- Gas injection EOR studies — determining the MMP (minimum miscibility pressure) screening
- CO$_2$ flooding feasibility — how much CO$_2$ dissolves in the oil
- Lean gas cycling in gas condensate reservoirs
- Assessing the effect of gas lift gas dissolving in the produced oil

### 3.4.6 Viscosity Measurements

Viscosity is measured separately, typically using:

- **Capillary viscometer** for liquid viscosity at moderate pressures
- **Falling ball viscometer** for high-pressure measurements
- **Electromagnetic viscometer (EV)** for in-situ measurements
- **Rolling ball viscometer** for heavy oils at elevated pressures

Viscosity data at multiple pressures and temperatures is essential for tuning the viscosity correlation in the EOS model. Typical measurement protocol includes viscosity at 5–8 pressure steps above the bubble point and 5–8 steps below, all at reservoir temperature.

## 3.5 Plus Fraction Characterization

### 3.5.1 The Plus Fraction Problem

A typical gas chromatography (GC) analysis of a reservoir fluid resolves individual components up to C$_6$ or C$_9$, then reports a "plus fraction" — C$_{7+}$ or C$_{10+}$ — that lumps all heavier components together. This plus fraction may contain hundreds of individual species.

For an EOS model, the plus fraction must be split into a manageable number of pseudo-components, each with estimated critical properties ($T_c$, $P_c$, $\omega$) and molecular weight ($M_w$). The quality of this characterization directly affects the accuracy of the phase envelope, density, and viscosity predictions.

### 3.5.2 Whitson's Gamma Distribution

Whitson (1983) proposed modeling the molar distribution of the plus fraction using a three-parameter gamma distribution:

$$
p(M) = \frac{(M - \eta)^{\alpha - 1}}{\beta^{\alpha} \Gamma(\alpha)} \exp\left(-\frac{M - \eta}{\beta}\right)
$$

where:

- $M$ is the molecular weight
- $\eta$ is the minimum molecular weight (typically 84 g/mol for C$_7$+)
- $\alpha$ is the shape parameter (typically 1–5; $\alpha = 1$ gives an exponential distribution)
- $\beta = (\bar{M} - \eta) / \alpha$ where $\bar{M}$ is the average molecular weight of the plus fraction
- $\Gamma(\alpha)$ is the gamma function

The distribution is divided into $N$ pseudo-components (typically 3–10) by splitting the molecular weight range into intervals and calculating the average properties for each interval. The mole fraction of pseudo-component $k$ is:

$$
z_k = z_{+} \int_{M_{k-1}}^{M_k} p(M) \, dM
$$

where $z_{+}$ is the total mole fraction of the plus fraction and the integral boundaries are chosen to give equal-weight or Gaussian quadrature intervals.

### 3.5.3 Pedersen Method

The Pedersen method (Pedersen et al., 1989) uses carbon number as the independent variable and applies exponential decay for mole fraction:

$$
\ln z_n = A + B \cdot n
$$

where $z_n$ is the mole fraction of carbon number $n$, and $A$ and $B$ are fitted from the extended analysis. Molecular weight and density for each carbon number are:

$$
M_n = 14n - 4
$$

$$
\rho_n = 0.2855 + 0.0326 \cdot \ln(n)
$$

The Pedersen method is particularly useful when the laboratory provides a partial extended analysis (e.g., to C$_{20}$ or C$_{30}$) because the exponential fit can extrapolate beyond the measured range. However, for heavy crudes with bimodal distributions (e.g., a wax peak), the simple exponential model may not capture the full distribution.

### 3.5.4 Critical Property Correlations

Each pseudo-component needs critical properties. Several correlations are available:

**Lee-Kesler correlations:**

$$
T_c = 341.7 + 811.1 S_g + (0.4244 + 0.1174 S_g) T_b + (0.4669 - 3.2623 S_g) \times 10^5 / T_b
$$

$$
\ln P_c = 8.3634 - 0.0566/S_g - (0.24244 + 2.2898/S_g + 0.11857/S_g^2) \times 10^{-3} T_b + \ldots
$$

**Twu correlations:**

$$
T_c^0 = T_b \left[0.533272 + 0.191017 \times 10^{-3} T_b + 0.779681 \times 10^{-7} T_b^2 - \ldots \right]^{-1}
$$

**Riazi-Daubert correlations** (commonly used in industry):

$$
T_c = 19.06232 \, T_b^{0.58848} \, S_g^{0.3596}
$$

$$
P_c = 5.53027 \times 10^7 \, T_b^{-2.3125} \, S_g^{2.3201}
$$

These correlations require boiling point $T_b$ and specific gravity $S_g$ as input. When boiling points are not available, they can be estimated from molecular weight and density.

### 3.5.5 NeqSim Plus Fraction Methods

NeqSim provides two approaches for handling plus fractions:

**TBP fraction method** (`addTBPfraction`): Adds individual pseudo-components with specified molecular weight and density. The critical properties are calculated internally using the selected correlation.

**Plus fraction characterization** (`addPlusFraction`): Adds a single plus fraction that NeqSim then splits into pseudo-components using the Whitson or Pedersen method:

```python
from neqsim import jneqsim

# Using addPlusFraction for automatic splitting
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 90.0, 200.0)
fluid.addComponent("methane", 50.0)
fluid.addComponent("ethane", 7.0)
fluid.addComponent("propane", 4.0)
fluid.addComponent("n-butane", 2.5)
fluid.addComponent("n-pentane", 1.5)
fluid.addComponent("n-hexane", 1.0)

# Add C7+ as a plus fraction: mole%, MW (kg/mol), density (g/cm3)
fluid.addPlusFraction("C7", 34.0, 220.0 / 1000.0, 0.84)

fluid.setMixingRule("classic")

# Configure characterization
fluid.getCharacterization().setLumpingModel("no lumping")
fluid.getCharacterization().setCharacterizeMethod("Pedersen")
fluid.getCharacterization().characterisePlusFraction()

print(f"Components after characterization: {fluid.getNumberOfComponents()}")
```

### 3.5.6 Watson Characterization Factor

The Watson (or UOP) characterization factor $K_w$ distinguishes paraffinic from naphthenic and aromatic character:

$$
K_w = \frac{T_b^{1/3}}{S_g}
$$

where $T_b$ is the mean average boiling point in Rankine and $S_g$ is the specific gravity at 60°F. Typical values:

| Fluid Type | $K_w$ Range | Character |
|-----------|-------------|-----------|
| Paraffinic | 12.5–13.0 | Straight-chain, branched |
| Naphthenic | 11.0–12.5 | Cyclic |
| Aromatic | 10.0–11.0 | Benzene rings |

### 3.5.7 API Gravity

API gravity is the industry-standard measure of oil density:

$$
\text{API} = \frac{141.5}{S_g} - 131.5
$$

where $S_g$ is the specific gravity at 60°F relative to water. Higher API means lighter oil:

| API Range | Classification |
|-----------|---------------|
| > 40 | Light oil / condensate |
| 30–40 | Medium oil |
| 22–30 | Heavy oil |
| < 22 | Extra heavy oil |

## 3.6 Black Oil Correlations vs. Compositional Models

### 3.6.1 When to Use Each Approach

The choice between black oil correlations and compositional (EOS-based) models depends on the fluid type, the engineering application, and the available data.

**Black oil correlations** treat the fluid as two pseudo-components (oil and gas) with pressure-dependent properties ($B_o$, $R_s$, $B_g$, $\mu_o$, $\mu_g$) described by empirical correlations. They are appropriate when:

- The fluid is a black oil with GOR < 200 Sm³/Sm³
- The process conditions do not approach the critical point
- No compositional tracking is needed (e.g., no injection gas mixing)
- Speed is important (reservoir simulation with millions of grid cells)
- Limited PVT data is available

**Compositional models** track each component explicitly using an EOS. They are required when:

- The fluid is volatile oil or gas condensate
- Gas injection (CO$_2$, lean gas, N$_2$) is being evaluated
- Retrograde condensation is important
- Compositional grading affects the reservoir description
- Process simulation requires detailed composition (e.g., export gas specifications)

### 3.6.2 Standing Correlation (Bubble Point)

Standing (1947) developed one of the earliest and most widely used correlations for bubble point pressure:

$$
P_b = 18.2 \left[\left(\frac{R_s}{\gamma_g}\right)^{0.83} \times 10^{0.00091 T - 0.0125 \, \text{API}} - 1.4\right]
$$

where $P_b$ is in psia, $R_s$ is in scf/STB, $\gamma_g$ is the gas specific gravity, $T$ is in °F, and API is stock tank oil gravity.

### 3.6.3 Vasquez-Beggs Correlations

Vasquez and Beggs (1980) developed correlations for oil FVF and solution GOR as functions of pressure, temperature, gas gravity, and API gravity.

**Solution GOR:**

$$
R_s = C_1 \gamma_{gs} P^{C_2} \exp\left(\frac{C_3 \cdot \text{API}}{T + 460}\right)
$$

where the constants $C_1$, $C_2$, $C_3$ depend on whether API $\leq$ 30 or API > 30, and $\gamma_{gs}$ is the gas gravity corrected to a separator pressure of 100 psig.

**Oil formation volume factor:**

$$
B_o = 1.0 + C_1 R_s + C_2(T - 60)\left(\frac{\text{API}}{\gamma_{gs}}\right) + C_3 R_s (T - 60)\left(\frac{\text{API}}{\gamma_{gs}}\right)
$$

### 3.6.4 Comparison and Selection Guidelines

| Property | Best Correlation | Typical Error | Applicable Range |
|----------|-----------------|---------------|------------------|
| $P_b$ | Standing / Vasquez-Beggs | 5–15% | API 15–45, GOR < 500 |
| $B_o$ above $P_b$ | Vasquez-Beggs | 2–5% | Black oil |
| $R_s$ | Vasquez-Beggs | 5–10% | Black oil |
| $\mu_o$ (dead oil) | Beggs-Robinson | 10–30% | API 16–58, T 70–295°F |
| $\mu_o$ (live oil) | Beggs-Robinson | 10–20% | $R_s$ < 2000 scf/STB |
| $B_g$ | Direct from Z-factor | 1–3% | Any gas composition |

For production optimization, **compositional models are strongly preferred** because they provide consistent thermodynamic properties across the full range of conditions from reservoir to export, they naturally handle gas-liquid equilibrium at each separator stage, and they are directly coupled with process simulation. Black oil correlations should only be used for quick screening or when running large reservoir simulation models where compositional tracking is computationally prohibitive.

## 3.7 NeqSim Implementation: Fluid Characterization

### 3.7.1 Creating a Simple Defined Fluid

For fluids where all components are individually identified:

```python
from neqsim import jneqsim

# Simple gas condensate - all components defined
fluid = jneqsim.thermo.system.SystemPrEos(273.15 + 100.0, 250.0)
fluid.addComponent("nitrogen", 0.34)
fluid.addComponent("CO2", 3.59)
fluid.addComponent("methane", 74.16)
fluid.addComponent("ethane", 7.90)
fluid.addComponent("propane", 3.58)
fluid.addComponent("i-butane", 0.71)
fluid.addComponent("n-butane", 1.25)
fluid.addComponent("i-pentane", 0.48)
fluid.addComponent("n-pentane", 0.38)
fluid.addComponent("n-hexane", 0.50)
fluid.addComponent("n-heptane", 2.00)
fluid.addComponent("n-octane", 1.80)
fluid.addComponent("n-nonane", 1.30)
fluid.addComponent("n-decane", 1.01)
fluid.addComponent("water", 1.00)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)
```

### 3.7.2 Creating a Fluid with Plus Fraction Characterization

For fluids with a reported C$_{7+}$ or higher plus fraction, NeqSim provides built-in characterization:

```python
from neqsim import jneqsim

# Black oil with C7+ characterization
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 90.0, 200.0)

# Defined components
fluid.addComponent("nitrogen", 0.5)
fluid.addComponent("CO2", 1.2)
fluid.addComponent("methane", 45.0)
fluid.addComponent("ethane", 6.5)
fluid.addComponent("propane", 4.0)
fluid.addComponent("i-butane", 1.5)
fluid.addComponent("n-butane", 2.5)
fluid.addComponent("i-pentane", 1.2)
fluid.addComponent("n-pentane", 1.0)
fluid.addComponent("n-hexane", 1.5)

# Plus fraction: specify mole fraction, molecular weight, and density
fluid.addTBPfraction("C7", 5.0, 96.0 / 1000.0, 0.738)    # C7: M=96, rho=0.738
fluid.addTBPfraction("C8", 4.5, 107.0 / 1000.0, 0.765)   # C8: M=107, rho=0.765
fluid.addTBPfraction("C9", 3.5, 121.0 / 1000.0, 0.781)   # C9: M=121, rho=0.781
fluid.addTBPfraction("C10", 3.0, 134.0 / 1000.0, 0.792)  # C10: M=134, rho=0.792
fluid.addTBPfraction("C11", 2.5, 147.0 / 1000.0, 0.800)  # C11: M=147, rho=0.800
fluid.addTBPfraction("C12", 2.0, 161.0 / 1000.0, 0.810)  # C12: M=161, rho=0.810
fluid.addTBPfraction("C13", 1.8, 175.0 / 1000.0, 0.820)  # C13: M=175, rho=0.820
fluid.addTBPfraction("C14", 1.5, 190.0 / 1000.0, 0.830)  # C14: M=190, rho=0.830
fluid.addTBPfraction("C15", 1.2, 206.0 / 1000.0, 0.837)  # C15: M=206, rho=0.837
fluid.addTBPfraction("C16", 1.0, 222.0 / 1000.0, 0.843)  # C16: M=222, rho=0.843
fluid.addTBPfraction("C17", 0.8, 237.0 / 1000.0, 0.849)  # C17: M=237, rho=0.849
fluid.addTBPfraction("C18", 0.7, 251.0 / 1000.0, 0.854)  # C18: M=251, rho=0.854
fluid.addTBPfraction("C19", 0.6, 263.0 / 1000.0, 0.859)  # C19: M=263, rho=0.859
fluid.addTBPfraction("C20", 5.0, 450.0 / 1000.0, 0.920)  # C20+: M=450, rho=0.920

# Set mixing rule AFTER adding all components (including TBP fractions)
fluid.setMixingRule("classic")

# Characterize the plus fractions
fluid.getCharacterization().setLumpingModel("no lumping")
fluid.getCharacterization().characterisePlusFraction()
```

**Important notes:**

- Molecular weight is specified in kg/mol (divide g/mol by 1000)
- Density is specific gravity (relative to water)
- `setMixingRule()` must be called AFTER adding all components
- `characterisePlusFraction()` must be called AFTER `setMixingRule()`
- Do NOT use `+` in fraction names (e.g., use `"C20"` not `"C20+"`)

### 3.7.3 Automatic Fluid Creation

For rapid prototyping and screening studies, NeqSim can create fluids from minimal input:

```python
from neqsim import jneqsim

# North Sea gas condensate - typical composition
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 80.0, 150.0)

components = {
    "nitrogen": 0.8, "CO2": 2.5, "methane": 72.0,
    "ethane": 8.5, "propane": 4.2, "i-butane": 1.1,
    "n-butane": 1.8, "i-pentane": 0.7, "n-pentane": 0.5,
    "n-hexane": 0.8
}
for comp, frac in components.items():
    fluid.addComponent(comp, frac)

# Add C7+ as TBP fractions with characterization
fluid.addTBPfraction("C7", 2.5, 96.0 / 1000.0, 0.738)
fluid.addTBPfraction("C10", 2.0, 134.0 / 1000.0, 0.792)
fluid.addTBPfraction("C15", 1.3, 206.0 / 1000.0, 0.837)
fluid.addTBPfraction("C20", 1.3, 350.0 / 1000.0, 0.880)

fluid.setMixingRule("classic")
fluid.getCharacterization().characterisePlusFraction()
fluid.setMultiPhaseCheck(True)

# Quick check: flash at reservoir conditions
ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid)
ops.TPflash()
fluid.initProperties()
print(f"Phases: {fluid.getNumberOfPhases()}")
print(f"Density: {fluid.getDensity('kg/m3'):.1f} kg/m3")
```

### 3.7.4 Running PVT Simulations

#### Constant Composition Expansion (CCE)

```python
from neqsim import jneqsim

# Create characterized fluid
fluid = jneqsim.thermo.system.SystemPrEos(273.15 + 100.0, 400.0)
fluid.addComponent("methane", 60.0)
fluid.addComponent("ethane", 8.0)
fluid.addComponent("propane", 5.0)
fluid.addComponent("n-butane", 3.0)
fluid.addComponent("n-hexane", 2.0)
fluid.addTBPfraction("C7", 5.0, 96.0 / 1000.0, 0.738)
fluid.addTBPfraction("C10", 4.0, 134.0 / 1000.0, 0.792)
fluid.addTBPfraction("C15", 3.0, 206.0 / 1000.0, 0.837)
fluid.addTBPfraction("C20", 10.0, 450.0 / 1000.0, 0.920)
fluid.setMixingRule("classic")
fluid.getCharacterization().characterisePlusFraction()

# Perform CCE simulation
pressures = [400, 350, 300, 280, 260, 240, 220, 200, 180, 160, 140, 120, 100]
T_res = 273.15 + 100.0

cce_results = []
for P in pressures:
    fluid_copy = fluid.clone()
    fluid_copy.setTemperature(T_res)
    fluid_copy.setPressure(P, "bara")
    ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid_copy)
    ops.TPflash()
    fluid_copy.initProperties()

    result = {
        "pressure_bara": P,
        "number_of_phases": fluid_copy.getNumberOfPhases(),
        "vapor_fraction": fluid_copy.getBeta(),
        "density_kg_m3": fluid_copy.getDensity("kg/m3"),
    }
    cce_results.append(result)

for r in cce_results:
    print(f"P = {r['pressure_bara']:6.0f} bara | "
          f"Phases: {r['number_of_phases']} | "
          f"Beta: {r['vapor_fraction']:.4f} | "
          f"Density: {r['density_kg_m3']:.1f} kg/m3")
```

#### Separator Test Simulation

```python
from neqsim import jneqsim

# Create oil fluid at bubble point conditions
fluid = jneqsim.thermo.system.SystemPrEos(273.15 + 90.0, 250.0)
fluid.addComponent("nitrogen", 0.5)
fluid.addComponent("CO2", 1.5)
fluid.addComponent("methane", 50.0)
fluid.addComponent("ethane", 7.0)
fluid.addComponent("propane", 5.0)
fluid.addComponent("n-butane", 3.5)
fluid.addComponent("n-pentane", 2.0)
fluid.addComponent("n-hexane", 2.5)
fluid.addTBPfraction("C7", 5.0, 96.0 / 1000.0, 0.738)
fluid.addTBPfraction("C10", 5.0, 134.0 / 1000.0, 0.792)
fluid.addTBPfraction("C20", 18.0, 400.0 / 1000.0, 0.910)
fluid.setMixingRule("classic")
fluid.getCharacterization().characterisePlusFraction()

# Build separator train
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
ThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

feed = Stream("Feed", fluid)
feed.setFlowRate(10000.0, "kg/hr")
feed.setTemperature(90.0, "C")
feed.setPressure(70.0, "bara")

hp_sep = Separator("HP Separator", feed)

valve_mp = ThrottlingValve("HP-MP Valve", hp_sep.getLiquidOutStream())
valve_mp.setOutletPressure(15.0, "bara")

mp_sep = Separator("MP Separator", valve_mp.getOutletStream())

valve_lp = ThrottlingValve("MP-LP Valve", mp_sep.getLiquidOutStream())
valve_lp.setOutletPressure(1.5, "bara")

lp_sep = Separator("LP Separator", valve_lp.getOutletStream())

process = ProcessSystem()
process.add(feed)
process.add(hp_sep)
process.add(valve_mp)
process.add(mp_sep)
process.add(valve_lp)
process.add(lp_sep)
process.run()

# Report separator test results
print("=== Separator Test Results ===")
print(f"HP gas rate: {hp_sep.getGasOutStream().getFlowRate('MSm3/day'):.4f} MSm3/day")
print(f"MP gas rate: {mp_sep.getGasOutStream().getFlowRate('MSm3/day'):.4f} MSm3/day")
print(f"LP gas rate: {lp_sep.getGasOutStream().getFlowRate('MSm3/day'):.4f} MSm3/day")
print(f"Stock tank oil rate: {lp_sep.getLiquidOutStream().getFlowRate('m3/hr'):.2f} m3/hr")

oil_density = lp_sep.getLiquidOutStream().getFluid().getPhase("oil").getDensity("kg/m3")
sg = oil_density / 999.1
api = 141.5 / sg - 131.5
print(f"Stock tank oil API gravity: {api:.1f}")
```

![Separator test results showing GOR and oil formation volume factor](figures/separator_test.png)

### 3.7.5 Phase Envelope Generation

```python
from neqsim import jneqsim

# Gas condensate fluid
fluid = jneqsim.thermo.system.SystemPrEos(273.15 + 20.0, 50.0)
fluid.addComponent("nitrogen", 0.5)
fluid.addComponent("CO2", 3.0)
fluid.addComponent("methane", 75.0)
fluid.addComponent("ethane", 8.0)
fluid.addComponent("propane", 4.0)
fluid.addComponent("i-butane", 1.0)
fluid.addComponent("n-butane", 1.5)
fluid.addComponent("i-pentane", 0.5)
fluid.addComponent("n-pentane", 0.4)
fluid.addComponent("n-hexane", 0.6)
fluid.addTBPfraction("C7", 2.0, 96.0 / 1000.0, 0.738)
fluid.addTBPfraction("C10", 1.5, 134.0 / 1000.0, 0.792)
fluid.addTBPfraction("C20", 2.0, 350.0 / 1000.0, 0.880)
fluid.setMixingRule("classic")
fluid.getCharacterization().characterisePlusFraction()

# Calculate phase envelope
ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid)
ops.calcPTphaseEnvelope()

# Access results
dew_T = [t for t in ops.getOperation().get("dewT")]
dew_P = [p for p in ops.getOperation().get("dewP")]
bub_T = [t for t in ops.getOperation().get("bubT")]
bub_P = [p for p in ops.getOperation().get("bubP")]

print(f"Cricondenbar: T = {ops.getOperation().get('cricondenbar')[0]:.1f} K, "
      f"P = {ops.getOperation().get('cricondenbar')[1]:.1f} bara")
print(f"Cricondentherm: T = {ops.getOperation().get('cricondentherm')[0]:.1f} K, "
      f"P = {ops.getOperation().get('cricondentherm')[1]:.1f} bara")
```

![Phase envelope for the gas condensate fluid showing bubble point, dew point, cricondenbar and cricondentherm](figures/gas_condensate_phase_envelope.png)

## 3.8 EOS Parameter Tuning

### 3.8.1 Why Tuning Is Necessary

Default EOS parameters (from generalized correlations) typically give acceptable results for defined components but may be inaccurate for the pseudo-components representing the plus fraction. The critical properties assigned to pseudo-components are estimates, and small errors in $T_c$, $P_c$, or $\omega$ propagate into significant errors in saturation pressure and liquid density. Tuning adjusts selected parameters to match experimental PVT data.

### 3.8.2 Binary Interaction Parameters ($k_{ij}$)

The binary interaction parameter modifies the attractive term in the EOS mixing rule:

$$
a_{\text{mix}} = \sum_i \sum_j x_i x_j \sqrt{a_i a_j} (1 - k_{ij})
$$

A positive $k_{ij}$ reduces the effective attraction between components $i$ and $j$, generally increasing the saturation pressure and reducing miscibility. The most sensitive BIPs for production optimization are:

| Component Pair | Typical $k_{ij}$ Range | Primary Effect |
|---------------|----------------------|----------------|
| CH$_4$ – C$_{7+}$ | 0.02–0.06 | Bubble/dew point pressure |
| CO$_2$ – C$_{7+}$ | 0.10–0.15 | CO$_2$ solubility, MMP |
| N$_2$ – C$_{7+}$ | 0.05–0.10 | N$_2$ rejection efficiency |
| CH$_4$ – CO$_2$ | 0.10–0.13 | Gas phase density |

### 3.8.3 Volume Translation

Cubic equations of state (SRK, PR) systematically underpredict liquid density by 5–15%. The Peneloux volume translation corrects this without affecting the phase equilibrium calculation:

$$
v_{\text{corrected}} = v_{\text{EOS}} - \sum_i x_i c_i
$$

where $c_i$ is the volume shift parameter for component $i$. For pseudo-components, $c_i$ is tuned to match the measured liquid density at reservoir conditions.

### 3.8.4 Matching Priority and Tolerances

The order of matching priority for production optimization is:

1. **Saturation pressure** — bubble point or dew point (highest priority)
2. **Liquid density / oil FVF** — affects volumetric calculations
3. **Gas-oil ratio** — separator test GOR
4. **Liquid dropout** — for gas condensates (CVD)
5. **Viscosity** — affects pressure drop calculations

Acceptable tolerances for tuned models:

| Property | Target Accuracy |
|----------|----------------|
| Saturation pressure | ±1–2% |
| Liquid density | ±1–2% |
| GOR | ±3–5% |
| Liquid dropout (CVD) | ±10% of peak |
| Viscosity | ±10–15% |

### 3.8.5 Regression Workflow

A systematic tuning workflow:

1. **Start with default parameters** and compare against experimental data
2. **Adjust plus fraction molecular weight** (±10%) to match saturation pressure
3. **Tune $k_{ij}$** between methane and heavy pseudo-components to refine saturation pressure and liquid dropout
4. **Adjust volume shift** to match liquid density
5. **Check separator test** GOR and API gravity
6. **Verify phase envelope** shape and critical point location
7. **Iterate** until all experimental data are matched within acceptable tolerances

### 3.8.6 Tuning in NeqSim

```python
from neqsim import jneqsim

# Create fluid and tune BIP between methane and a heavy fraction
fluid = jneqsim.thermo.system.SystemPrEos(273.15 + 100.0, 300.0)
fluid.addComponent("methane", 70.0)
fluid.addComponent("ethane", 8.0)
fluid.addComponent("propane", 5.0)
fluid.addTBPfraction("C7", 5.0, 96.0 / 1000.0, 0.738)
fluid.addTBPfraction("C20", 12.0, 400.0 / 1000.0, 0.910)
fluid.setMixingRule("classic")
fluid.getCharacterization().characterisePlusFraction()

# Set custom binary interaction parameter
methane_index = 0
heavy_index = fluid.getPhase(0).getNumberOfComponents() - 1
fluid.setInteractionParameter(methane_index, heavy_index, 0.04)

# Recalculate to check effect
ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid)
ops.bubblePointPressureFlash(False)
print(f"Bubble point after tuning: {fluid.getPressure('bara'):.1f} bara")
```

#### Simple Regression Example

A bisection approach to find the $k_{ij}$ that matches a target bubble point:

```python
from neqsim import jneqsim

target_pb = 245.0  # Target bubble point (bara)

def calc_bubble_point(kij_value):
    fluid = jneqsim.thermo.system.SystemPrEos(273.15 + 100.0, 300.0)
    fluid.addComponent("methane", 65.0)
    fluid.addComponent("ethane", 8.0)
    fluid.addComponent("propane", 5.0)
    fluid.addComponent("n-butane", 3.0)
    fluid.addTBPfraction("C7", 5.0, 96.0 / 1000.0, 0.738)
    fluid.addTBPfraction("C20", 14.0, 400.0 / 1000.0, 0.910)
    fluid.setMixingRule("classic")
    fluid.getCharacterization().characterisePlusFraction()

    idx_c1 = 0
    idx_heavy = fluid.getPhase(0).getNumberOfComponents() - 1
    fluid.setInteractionParameter(idx_c1, idx_heavy, kij_value)

    ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid)
    ops.bubblePointPressureFlash(False)
    return fluid.getPressure("bara")

# Bisection search
kij_low, kij_high = -0.02, 0.10
for iteration in range(20):
    kij_mid = (kij_low + kij_high) / 2.0
    pb_calc = calc_bubble_point(kij_mid)
    if abs(pb_calc - target_pb) < 0.5:
        print(f"Converged: kij = {kij_mid:.4f}, Pb = {pb_calc:.1f} bara")
        break
    if pb_calc > target_pb:
        kij_low = kij_mid
    else:
        kij_high = kij_mid
```

## 3.9 Key PVT Properties

### 3.9.1 Gas-Oil Ratio (GOR)

The gas-oil ratio is the ratio of gas volume to oil volume at standard conditions:

$$
\text{GOR} = \frac{V_{\text{gas}}^{\text{sc}}}{V_{\text{oil}}^{\text{sc}}}
$$

The solution GOR $R_s$ is the amount of gas dissolved in the oil at reservoir conditions. As pressure drops below the bubble point, gas evolves and $R_s$ decreases.

### 3.9.2 Formation Volume Factor

The oil formation volume factor $B_o$ converts reservoir volumes to surface volumes:

$$
B_o = \frac{V_{\text{oil}}^{\text{reservoir}}}{V_{\text{oil}}^{\text{stock tank}}}
$$

The total formation volume factor $B_t$ accounts for both the oil and its dissolved gas:

$$
B_t = B_o + (R_{si} - R_s) B_g
$$

The gas formation volume factor:

$$
B_g = \frac{ZT P^{\text{sc}}}{T^{\text{sc}} P}
$$

### 3.9.3 Compressibility

The isothermal compressibility of oil above the bubble point is:

$$
c_o = -\frac{1}{V}\left(\frac{\partial V}{\partial P}\right)_T
$$

The effective total compressibility in a reservoir is:

$$
c_t = c_o S_o + c_w S_w + c_g S_g + c_f
$$

### 3.9.4 Viscosity Correlations

**Dead oil viscosity** (Beggs-Robinson):

$$
\mu_{od} = 10^{10^{(3.0324 - 0.02023 \cdot \text{API})}/T^{1.163}} - 1
$$

**Live oil viscosity:**

$$
\mu_o = A \cdot \mu_{od}^B
$$

where $A$ and $B$ depend on the solution GOR.

## 3.10 Fluid Characterization Quality Checks

After creating a characterized fluid model, several quality checks should be performed:

1. **Mass balance:** Verify that the sum of all mole fractions equals 1.0
2. **Phase envelope reasonableness:** The critical point and cricondenbar should be physically reasonable
3. **Saturation pressure:** Compare predicted vs. measured bubble/dew point
4. **Density:** Compare predicted vs. measured at reservoir conditions
5. **GOR:** Compare predicted vs. measured at separator conditions
6. **Molecular weight:** The calculated mixture M$_w$ should match the reported value

```python
# Quality check: print fluid summary
ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid)
ops.TPflash()
fluid.initProperties()

print(f"Number of components: {fluid.getNumberOfComponents()}")
print(f"Number of phases: {fluid.getNumberOfPhases()}")
print(f"Mixture molecular weight: {fluid.getMolarMass('kg/mol') * 1000:.1f} g/mol")
print(f"Overall density: {fluid.getDensity('kg/m3'):.1f} kg/m3")

# Check sum of mole fractions
total_z = 0.0
for i in range(fluid.getNumberOfComponents()):
    total_z += fluid.getPhase(0).getComponent(i).getz()
print(f"Sum of mole fractions: {total_z:.6f}")
```

## 3.11 Advanced Topics

### 3.11.1 Lumping and Delumping

For computational efficiency, the pseudo-components from characterization can be lumped into a smaller number of groups. Common lumping schemes:

- **3-component:** Light (C$_1$–C$_3$), intermediate (C$_4$–C$_6$), heavy (C$_7+$)
- **6-component:** N$_2$+CO$_2$, C$_1$, C$_2$–C$_3$, C$_4$–C$_6$, C$_7$–C$_{12}$, C$_{13+}$
- **Reservoir-specific:** Optimized grouping based on K-value behavior

### 3.11.2 Wax and Asphaltene Characterization

For flow assurance studies, the plus fraction characterization must capture the wax-forming and asphaltene fractions:

- **Wax:** Primarily normal paraffins in the C$_{16}$–C$_{60+}$ range
- **Asphaltenes:** Heavy polar components. The CPA or PC-SAFT equation is better suited than cubic EOS.

### 3.11.3 Compositional Grading

In thick reservoirs, gravity causes compositional variation with depth:

$$
\ln f_i(T, P(z), x_i(z)) = \ln f_i(T, P_{\text{ref}}, x_{i,\text{ref}}) + \frac{M_i g (z - z_{\text{ref}})}{RT}
$$

where $f_i$ is the fugacity of component $i$ and $z$ is depth.

## 3.12 Summary

Key points from this chapter:

- **Reservoir fluids** are classified as black oil, volatile oil, gas condensate, wet gas, or dry gas based on their phase behavior and composition
- **Fluid sampling** requires careful attention to method (bottomhole vs. surface recombination), QC checks, and representative conditions
- **PVT experiments** (CCE, CVD, DL, separator test, swelling test, viscosity) provide the data for fluid model calibration — each experiment provides specific information for different aspects of the model
- **Plus fraction characterization** splits the heavy end into pseudo-components with estimated critical properties, using methods such as the Whitson gamma distribution or Pedersen correlations
- **Black oil correlations** (Standing, Vasquez-Beggs) are useful for quick screening, but compositional models are preferred for production optimization
- **EOS parameter tuning** adjusts BIPs, critical properties, and volume shifts to match experimental data — the saturation pressure and liquid density are highest priority
- **NeqSim** provides TBP fraction handling, plus fraction characterization, phase envelope calculation, and separator test simulation for complete PVT workflows
- **Quality checks** (mass balance, phase envelope, saturation pressure, density, GOR) must be performed before using a fluid model in production optimization

## Exercises

1. **Exercise 3.1:** Given the following plus fraction data for a gas condensate (C$_{7+}$ = 8.5 mol%, M$_w$ = 155 g/mol, density = 0.795 g/cm³), create a NeqSim fluid model with at least 5 pseudo-components. Calculate the phase envelope and identify the fluid type.

2. **Exercise 3.2:** For a black oil with bubble point pressure of 180 bara at 95°C, perform a CCE simulation from 300 bara down to 50 bara. Plot the relative volume vs. pressure and identify the bubble point from the change in slope.

3. **Exercise 3.3:** Set up a three-stage separator test (70/15/1.5 bara) for a typical North Sea black oil. Calculate the GOR at each stage and the total GOR.

4. **Exercise 3.4:** Create two fluid models for the same composition — one with SRK, one with PR. Compare predicted bubble point pressures and liquid densities.

5. **Exercise 3.5:** Investigate the effect of C$_{7+}$ molecular weight on the phase envelope. Vary the M$_w$ by ±20% and plot three phase envelopes on the same graph.

6. **Exercise 3.6:** Calculate the API gravity and Watson K-factor for stock tank oils from three different reservoir fluids using NeqSim separator test simulations.

7. **Exercise 3.7:** Implement a bisection regression to tune the methane-C$_{7+}$ BIP to match a measured bubble point pressure of 210 bara.

8. **Exercise 3.8:** For a gas condensate with known CVD data, run a NeqSim CVD simulation and compare the predicted liquid dropout curve against experimental data.

9. **Exercise 3.9:** Using the Standing and Vasquez-Beggs correlations, estimate $P_b$, GOR, and $B_o$ for a fluid with API = 35, $T$ = 200°F, $\gamma_g$ = 0.75. Compare with a NeqSim compositional model.

10. **Exercise 3.10 (Advanced):** Collect separator gas and liquid compositions from a NeqSim separator test. Perform the recombination calculation manually to reconstruct the feed composition.

## References

1. Whitson, C. H. (1983). Characterizing hydrocarbon plus fractions. *Society of Petroleum Engineers Journal*, 23(4), 683–694.
2. Pedersen, K. S., Thomassen, P., & Fredenslund, A. (1989). Thermodynamics of petroleum mixtures containing heavy hydrocarbons. *Industrial & Engineering Chemistry Process Design and Development*, 24(4), 948–954.
3. Pedersen, K. S., & Christensen, P. L. (2007). *Phase Behavior of Petroleum Reservoir Fluids*. CRC Press.
4. Danesh, A. (1998). *PVT and Phase Behaviour of Petroleum Reservoir Fluids*. Elsevier.
5. Lee, B. I., & Kesler, M. G. (1975). A generalized thermodynamic correlation based on three-parameter corresponding states. *AIChE Journal*, 21(3), 510–527.
6. Twu, C. H. (1984). An internally consistent correlation for predicting the critical properties and molecular weights of petroleum and coal-tar liquids. *Fluid Phase Equilibria*, 16(2), 137–150.
7. Ahmed, T. (2016). *Reservoir Engineering Handbook* (5th ed.). Gulf Professional Publishing.
8. McCain, W. D., Spivey, J. P., & Lenn, C. P. (2011). *Petroleum Reservoir Fluid Property Correlations*. PennWell Books.
9. Beggs, H. D., & Robinson, J. R. (1975). Estimating the viscosity of crude oil systems. *Journal of Petroleum Technology*, 27(9), 1140–1141.
10. Watson, K. M., & Nelson, E. F. (1933). Improved methods for approximating critical and thermal properties of petroleum fractions. *Industrial & Engineering Chemistry*, 25(8), 880–887.
11. Standing, M. B. (1947). A pressure-volume-temperature correlation for mixtures of California oils and gases. *API Drilling and Production Practice*, 275–287.
12. Vasquez, M. E., & Beggs, H. D. (1980). Correlations for fluid physical property prediction. *Journal of Petroleum Technology*, 32(6), 968–970.
13. Peneloux, A., Rauzy, E., & Fréze, R. (1982). A consistent correction for Redlich-Kwong-Soave volumes. *Fluid Phase Equilibria*, 8(1), 7–23.
14. Riazi, M. R., & Daubert, T. E. (1987). Characterization parameters for petroleum fractions. *Industrial & Engineering Chemistry Research*, 26(4), 755–759.
# Fluid Characterization and PVT Modeling

<!-- Chapter metadata -->
<!-- Notebooks: ch03_fluid_characterization.ipynb, ch03_pvt_simulations.ipynb, ch03_plus_fraction.ipynb -->
<!-- Estimated pages: 25 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Classify reservoir fluids by type (black oil, volatile oil, gas condensate, dry gas, wet gas) and explain their distinguishing characteristics
2. Describe common PVT laboratory experiments and their role in fluid characterization
3. Apply plus fraction characterization methods (Whitson gamma distribution, Pedersen) to extend a fluid analysis into pseudo-components
4. Use NeqSim to create characterized fluids with plus fractions and run PVT simulations
5. Tune EOS parameters to match experimental PVT data
6. Generate and interpret phase envelopes for different fluid types
7. Calculate key PVT properties: GOR, formation volume factor, API gravity, and compressibility

## 3.1 Introduction

Accurate fluid characterization is the starting point for every production optimization model. The reservoir fluid — a complex mixture of hundreds or thousands of hydrocarbon species plus non-hydrocarbons — determines the phase behavior, flow properties, and processing requirements of the entire production system. A poor fluid model propagates errors through every subsequent calculation: wrong phase envelopes lead to incorrect separator design, wrong viscosities produce inaccurate pressure drops, and wrong compositions give misleading export specifications.

This chapter covers the complete fluid characterization workflow: from understanding what the laboratory measures, through the mathematical methods for representing the heavy end of the composition, to the practical steps of building and tuning a fluid model in NeqSim.

![Workflow from reservoir fluid sampling through PVT analysis to calibrated EOS model](figures/fluid_characterization_workflow.png)

## 3.2 Reservoir Fluid Types

Reservoir fluids are classified based on their initial conditions relative to the phase envelope, the gas-oil ratio (GOR), and the liquid content at surface conditions.

### 3.2.1 Classification Criteria

The five standard fluid types are:

| Fluid Type | GOR (Sm³/Sm³) | API Gravity | Oil FVF $B_o$ | Key Characteristic |
|-----------|----------------|-------------|---------------|-------------------|
| Black oil | < 200 | 15–40 | 1.0–2.0 | Reservoir T < critical T; wide two-phase region |
| Volatile oil | 200–600 | 40–50 | 1.5–3.0 | Close to critical point; significant shrinkage |
| Gas condensate | 600–15,000 | 40–60 | — | Reservoir T between Tc and cricondentherm |
| Wet gas | 15,000–100,000 | 40–60 | — | Single phase in reservoir; liquid at surface |
| Dry gas | > 100,000 | — | — | No liquid at any conditions |

### 3.2.2 Phase Envelope Characteristics

The position of the initial reservoir conditions on the phase envelope determines the fluid type:

- **Black oil:** Initial conditions are well to the left of the critical point; the reservoir is at a temperature below the critical temperature. As pressure drops during depletion, the fluid crosses the bubble point and gas evolves.
- **Volatile oil:** Initial conditions are near but to the left of the critical point. The fluid exhibits large changes in properties with small changes in pressure.
- **Gas condensate:** Initial conditions are to the right of the critical point. The reservoir temperature is between the critical temperature and the cricondentherm. As pressure drops below the dew point, retrograde condensation occurs — liquid drops out in the reservoir.
- **Wet gas:** The reservoir temperature exceeds the cricondentherm. The fluid is always single-phase in the reservoir, but at surface conditions it falls within the two-phase region, yielding some condensate.
- **Dry gas:** The phase envelope is so narrow that even surface conditions remain outside the two-phase region.

![Phase envelopes for the five reservoir fluid types showing the relationship between initial reservoir conditions and fluid classification](figures/fluid_type_phase_envelopes.png)

### 3.2.3 Fluid Type Identification from Field Data

In practice, fluid type is identified from:

1. **Initial producing GOR** — measured at the test separator
2. **Stock tank oil gravity (API)** — from sample analysis
3. **Reservoir temperature and pressure** — from well logs and DST data
4. **C$_{7+}$ fraction** — higher C$_{7+}$ content indicates heavier fluid
5. **Visual observation** — color of separator liquid (clear/straw = condensate; brown/black = oil)

Table 3.1 provides heuristic guidelines:

| Property | Black Oil | Volatile Oil | Gas Condensate | Wet Gas |
|----------|-----------|-------------|----------------|---------|
| C$_{7+}$ mol% | > 20 | 12–20 | 4–12 | < 4 |
| Initial GOR (Sm³/Sm³) | < 200 | 200–600 | 600–15,000 | > 15,000 |
| Stock tank API | < 40 | 40–50 | 40–60 | 40–60 |
| Fluid color | Black/dark brown | Brown/dark orange | Straw/light brown | Water-white |

## 3.3 PVT Laboratory Experiments

PVT experiments are conducted on reservoir fluid samples to measure phase behavior and properties at reservoir and process conditions. These measurements provide the data against which EOS models are tuned.

### 3.3.1 Fluid Sampling

Reservoir fluid samples are collected by two methods:

- **Bottomhole sampling:** A sample is taken at reservoir conditions using a wireline tool. This provides a single-phase sample if the bottomhole pressure exceeds the saturation pressure.
- **Surface recombination:** Separator gas and liquid samples are collected and recombined at the measured GOR. This is more common for gas condensate systems.

Sample quality is critical. Contamination with drilling mud, phase segregation during sampling, or loss of light ends during transfer can invalidate the entire PVT study.

### 3.3.2 Constant Composition Expansion (CCE)

The CCE experiment measures the pressure-volume relationship of a reservoir fluid at reservoir temperature:

1. The sample is loaded into a PVT cell at a pressure above the saturation point
2. Pressure is reduced in steps, and the total volume is recorded at each step
3. The saturation pressure (bubble point for oil, dew point for gas condensate) is identified as the pressure where the slope of the $P$-$V$ curve changes
4. Below the saturation pressure, the total volume (gas + liquid) continues to be measured

Key measurements from CCE:

- Saturation pressure ($P_b$ or $P_d$)
- Relative volume $V/V_{\text{sat}}$ as a function of pressure
- Oil compressibility above the bubble point
- Liquid dropout curve for gas condensates (liquid volume fraction vs. pressure)

### 3.3.3 Constant Volume Depletion (CVD)

The CVD experiment simulates the depletion of a gas condensate reservoir where retrograde liquid remains immobile in the pore space:

1. The sample starts at the dew point pressure at reservoir temperature
2. Pressure is reduced in steps
3. At each step, gas is removed to restore the original volume (constant volume)
4. The composition and volume of the removed gas are measured
5. The liquid dropout (retrograde condensation) at each pressure is measured

CVD data is essential for:

- Gas condensate reservoir simulation (material balance)
- Predicting liquid dropout in the reservoir
- Calculating the recovery factor for gas and condensate components

### 3.3.4 Differential Liberation (DL)

The differential liberation experiment applies to black oil and volatile oil systems:

1. The sample starts at the bubble point at reservoir temperature
2. Pressure is reduced in a step
3. All evolved gas is removed at that pressure, and its volume and composition are measured
4. The oil volume at that pressure is recorded
5. Steps 2–4 are repeated down to atmospheric pressure

Key outputs:

- Solution GOR ($R_s$) as a function of pressure
- Oil formation volume factor ($B_o$) as a function of pressure
- Gas formation volume factor ($B_g$)
- Oil density and viscosity at each pressure step

### 3.3.5 Separator Test

The separator test measures the GOR and oil properties at specific separator conditions:

1. A sample at the bubble point is flashed through a multi-stage separator train
2. Gas and liquid volumes are measured at each stage
3. The final stock tank oil volume, API gravity, and GOR are recorded

This test is critical because it defines the reference conditions for reporting field data:

$$
B_o = \frac{V_{\text{oil at reservoir conditions}}}{V_{\text{stock tank oil at standard conditions}}}
$$

### 3.3.6 Swelling Test

The swelling test measures the effect of injecting gas (lean gas, CO$_2$, N$_2$) into a reservoir oil:

1. A reservoir oil sample is loaded at its bubble point
2. Gas is injected in measured amounts
3. The new bubble point and volume are measured after each injection
4. The process reveals how much gas can be dissolved and the resulting pressure changes

Swelling test data is essential for:

- Gas injection EOR studies
- CO$_2$ flooding feasibility
- Lean gas cycling in gas condensate reservoirs

### 3.3.7 Viscosity Measurements

Viscosity is measured separately, typically using:

- **Capillary viscometer** for liquid viscosity
- **Falling ball viscometer** for high-pressure measurements
- **Electromagnetic viscometer (EV)** for in-situ measurements

Viscosity data at multiple pressures and temperatures is essential for tuning the viscosity correlation in the EOS model.

## 3.4 Plus Fraction Characterization

### 3.4.1 The Plus Fraction Problem

A typical gas chromatography (GC) analysis of a reservoir fluid resolves individual components up to C$_6$ or C$_9$, then reports a "plus fraction" — C$_{7+}$ or C$_{10+}$ — that lumps all heavier components together. This plus fraction may contain hundreds of individual species.

For an EOS model, the plus fraction must be split into a manageable number of pseudo-components, each with estimated critical properties ($T_c$, $P_c$, $\omega$) and molecular weight ($M_w$). The quality of this characterization directly affects the accuracy of the phase envelope, density, and viscosity predictions.

### 3.4.2 Whitson's Gamma Distribution

Whitson (1983) proposed modeling the molar distribution of the plus fraction using a three-parameter gamma distribution:

$$
p(M) = \frac{(M - \eta)^{\alpha - 1}}{\beta^{\alpha} \Gamma(\alpha)} \exp\left(-\frac{M - \eta}{\beta}\right)
$$

where:

- $M$ is the molecular weight
- $\eta$ is the minimum molecular weight (typically 84 g/mol for C$_7$+)
- $\alpha$ is the shape parameter (typically 1–5; $\alpha = 1$ gives an exponential distribution)
- $\beta = (\bar{M} - \eta) / \alpha$ where $\bar{M}$ is the average molecular weight of the plus fraction
- $\Gamma(\alpha)$ is the gamma function

The distribution is divided into $N$ pseudo-components (typically 3–10) by splitting the molecular weight range into intervals and calculating the average properties for each interval.

### 3.4.3 Critical Property Correlations

Each pseudo-component needs critical properties. Several correlations are available:

**Lee-Kesler correlations:**

$$
T_c = 341.7 + 811.1 S_g + (0.4244 + 0.1174 S_g) T_b + (0.4669 - 3.2623 S_g) \times 10^5 / T_b
$$

$$
\ln P_c = 8.3634 - 0.0566/S_g - (0.24244 + 2.2898/S_g + 0.11857/S_g^2) \times 10^{-3} T_b + \ldots
$$

**Twu correlations:**

$$
T_c^0 = T_b \left[0.533272 + 0.191017 \times 10^{-3} T_b + 0.779681 \times 10^{-7} T_b^2 - \ldots \right]^{-1}
$$

**Pedersen method:**

The Pedersen method (Pedersen et al., 1989) uses carbon number as the independent variable and applies exponential decay for mole fraction:

$$
\ln z_n = A + B \cdot n
$$

where $z_n$ is the mole fraction of carbon number $n$, and $A$ and $B$ are fitted from the extended analysis. Molecular weight and density for each carbon number are:

$$
M_n = 14n - 4
$$

$$
\rho_n = 0.2855 + 0.0326 \cdot \ln(n)
$$

### 3.4.4 Watson Characterization Factor

The Watson (or UOP) characterization factor $K_w$ distinguishes paraffinic from naphthenic and aromatic character:

$$
K_w = \frac{T_b^{1/3}}{S_g}
$$

where $T_b$ is the mean average boiling point in Rankine and $S_g$ is the specific gravity at 60°F. Typical values:

| Fluid Type | $K_w$ Range | Character |
|-----------|-------------|-----------|
| Paraffinic | 12.5–13.0 | Straight-chain, branched |
| Naphthenic | 11.0–12.5 | Cyclic |
| Aromatic | 10.0–11.0 | Benzene rings |

### 3.4.5 API Gravity

API gravity is the industry-standard measure of oil density:

$$
\text{API} = \frac{141.5}{S_g} - 131.5
$$

where $S_g$ is the specific gravity at 60°F relative to water. Higher API means lighter oil:

| API Range | Classification |
|-----------|---------------|
| > 40 | Light oil / condensate |
| 30–40 | Medium oil |
| 22–30 | Heavy oil |
| < 22 | Extra heavy oil |

## 3.5 NeqSim Implementation: Fluid Characterization

### 3.5.1 Creating a Simple Defined Fluid

For fluids where all components are individually identified:

```python
from neqsim import jneqsim

# Simple gas condensate - all components defined
fluid = jneqsim.thermo.system.SystemPrEos(273.15 + 100.0, 250.0)
fluid.addComponent("nitrogen", 0.34)
fluid.addComponent("CO2", 3.59)
fluid.addComponent("methane", 74.16)
fluid.addComponent("ethane", 7.90)
fluid.addComponent("propane", 3.58)
fluid.addComponent("i-butane", 0.71)
fluid.addComponent("n-butane", 1.25)
fluid.addComponent("i-pentane", 0.48)
fluid.addComponent("n-pentane", 0.38)
fluid.addComponent("n-hexane", 0.50)
fluid.addComponent("n-heptane", 2.00)
fluid.addComponent("n-octane", 1.80)
fluid.addComponent("n-nonane", 1.30)
fluid.addComponent("n-decane", 1.01)
fluid.addComponent("water", 1.00)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)
```

### 3.5.2 Creating a Fluid with Plus Fraction Characterization

For fluids with a reported C$_{7+}$ or higher plus fraction, NeqSim provides built-in characterization:

```python
from neqsim import jneqsim

# Black oil with C7+ characterization
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 90.0, 200.0)

# Defined components
fluid.addComponent("nitrogen", 0.5)
fluid.addComponent("CO2", 1.2)
fluid.addComponent("methane", 45.0)
fluid.addComponent("ethane", 6.5)
fluid.addComponent("propane", 4.0)
fluid.addComponent("i-butane", 1.5)
fluid.addComponent("n-butane", 2.5)
fluid.addComponent("i-pentane", 1.2)
fluid.addComponent("n-pentane", 1.0)
fluid.addComponent("n-hexane", 1.5)

# Plus fraction: specify mole fraction, molecular weight, and density
fluid.addTBPfraction("C7", 5.0, 96.0 / 1000.0, 0.738)    # C7: M=96, rho=0.738
fluid.addTBPfraction("C8", 4.5, 107.0 / 1000.0, 0.765)   # C8: M=107, rho=0.765
fluid.addTBPfraction("C9", 3.5, 121.0 / 1000.0, 0.781)   # C9: M=121, rho=0.781
fluid.addTBPfraction("C10", 3.0, 134.0 / 1000.0, 0.792)  # C10: M=134, rho=0.792
fluid.addTBPfraction("C11", 2.5, 147.0 / 1000.0, 0.800)  # C11: M=147, rho=0.800
fluid.addTBPfraction("C12", 2.0, 161.0 / 1000.0, 0.810)  # C12: M=161, rho=0.810
fluid.addTBPfraction("C13", 1.8, 175.0 / 1000.0, 0.820)  # C13: M=175, rho=0.820
fluid.addTBPfraction("C14", 1.5, 190.0 / 1000.0, 0.830)  # C14: M=190, rho=0.830
fluid.addTBPfraction("C15", 1.2, 206.0 / 1000.0, 0.837)  # C15: M=206, rho=0.837
fluid.addTBPfraction("C16", 1.0, 222.0 / 1000.0, 0.843)  # C16: M=222, rho=0.843
fluid.addTBPfraction("C17", 0.8, 237.0 / 1000.0, 0.849)  # C17: M=237, rho=0.849
fluid.addTBPfraction("C18", 0.7, 251.0 / 1000.0, 0.854)  # C18: M=251, rho=0.854
fluid.addTBPfraction("C19", 0.6, 263.0 / 1000.0, 0.859)  # C19: M=263, rho=0.859
fluid.addTBPfraction("C20", 5.0, 450.0 / 1000.0, 0.920)  # C20+: M=450, rho=0.920

# Set mixing rule AFTER adding all components (including TBP fractions)
fluid.setMixingRule("classic")

# Characterize the plus fractions
fluid.getCharacterization().setLumpingModel("no lumping")
fluid.getCharacterization().characterisePlusFraction()
```

**Important notes:**

- Molecular weight is specified in kg/mol (divide g/mol by 1000)
- Density is specific gravity (relative to water)
- `setMixingRule()` must be called AFTER adding all components
- `characterisePlusFraction()` must be called AFTER `setMixingRule()`
- Do NOT use `+` in fraction names (e.g., use `"C20"` not `"C20+"`)

### 3.5.3 Running PVT Simulations

#### Constant Composition Expansion (CCE)

```python
from neqsim import jneqsim

# Create characterized fluid (as above, simplified here)
fluid = jneqsim.thermo.system.SystemPrEos(273.15 + 100.0, 400.0)
fluid.addComponent("methane", 60.0)
fluid.addComponent("ethane", 8.0)
fluid.addComponent("propane", 5.0)
fluid.addComponent("n-butane", 3.0)
fluid.addComponent("n-hexane", 2.0)
fluid.addTBPfraction("C7", 5.0, 96.0 / 1000.0, 0.738)
fluid.addTBPfraction("C10", 4.0, 134.0 / 1000.0, 0.792)
fluid.addTBPfraction("C15", 3.0, 206.0 / 1000.0, 0.837)
fluid.addTBPfraction("C20", 10.0, 450.0 / 1000.0, 0.920)
fluid.setMixingRule("classic")
fluid.getCharacterization().characterisePlusFraction()

# Perform CCE simulation
pressures = [400, 350, 300, 280, 260, 240, 220, 200, 180, 160, 140, 120, 100]
T_res = 273.15 + 100.0

cce_results = []
for P in pressures:
    fluid_copy = fluid.clone()
    fluid_copy.setTemperature(T_res)
    fluid_copy.setPressure(P, "bara")
    ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid_copy)
    ops.TPflash()
    fluid_copy.initProperties()

    result = {
        "pressure_bara": P,
        "number_of_phases": fluid_copy.getNumberOfPhases(),
        "vapor_fraction": fluid_copy.getBeta(),
        "density_kg_m3": fluid_copy.getDensity("kg/m3"),
    }
    cce_results.append(result)

for r in cce_results:
    print(f"P = {r['pressure_bara']:6.0f} bara | "
          f"Phases: {r['number_of_phases']} | "
          f"Beta: {r['vapor_fraction']:.4f} | "
          f"Density: {r['density_kg_m3']:.1f} kg/m3")
```

#### Separator Test Simulation

```python
from neqsim import jneqsim

# Create oil fluid at bubble point conditions
fluid = jneqsim.thermo.system.SystemPrEos(273.15 + 90.0, 250.0)
fluid.addComponent("nitrogen", 0.5)
fluid.addComponent("CO2", 1.5)
fluid.addComponent("methane", 50.0)
fluid.addComponent("ethane", 7.0)
fluid.addComponent("propane", 5.0)
fluid.addComponent("n-butane", 3.5)
fluid.addComponent("n-pentane", 2.0)
fluid.addComponent("n-hexane", 2.5)
fluid.addTBPfraction("C7", 5.0, 96.0 / 1000.0, 0.738)
fluid.addTBPfraction("C10", 5.0, 134.0 / 1000.0, 0.792)
fluid.addTBPfraction("C20", 18.0, 400.0 / 1000.0, 0.910)
fluid.setMixingRule("classic")
fluid.getCharacterization().characterisePlusFraction()

# Build separator train
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
ThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# Feed stream
feed = Stream("Feed", fluid)
feed.setFlowRate(10000.0, "kg/hr")
feed.setTemperature(90.0, "C")
feed.setPressure(70.0, "bara")

# HP Separator (70 bara)
hp_sep = Separator("HP Separator", feed)

# Valve to MP
valve_mp = ThrottlingValve("HP-MP Valve", hp_sep.getLiquidOutStream())
valve_mp.setOutletPressure(15.0, "bara")

# MP Separator (15 bara)
mp_sep = Separator("MP Separator", valve_mp.getOutletStream())

# Valve to LP
valve_lp = ThrottlingValve("MP-LP Valve", mp_sep.getLiquidOutStream())
valve_lp.setOutletPressure(1.5, "bara")

# LP Separator (1.5 bara)
lp_sep = Separator("LP Separator", valve_lp.getOutletStream())

# Build and run process
process = ProcessSystem()
process.add(feed)
process.add(hp_sep)
process.add(valve_mp)
process.add(mp_sep)
process.add(valve_lp)
process.add(lp_sep)
process.run()

# Report separator test results
print("=== Separator Test Results ===")
print(f"HP gas rate: {hp_sep.getGasOutStream().getFlowRate('MSm3/day'):.4f} MSm3/day")
print(f"MP gas rate: {mp_sep.getGasOutStream().getFlowRate('MSm3/day'):.4f} MSm3/day")
print(f"LP gas rate: {lp_sep.getGasOutStream().getFlowRate('MSm3/day'):.4f} MSm3/day")
print(f"Stock tank oil rate: {lp_sep.getLiquidOutStream().getFlowRate('m3/hr'):.2f} m3/hr")

oil_density = lp_sep.getLiquidOutStream().getFluid().getPhase("oil").getDensity("kg/m3")
sg = oil_density / 999.1
api = 141.5 / sg - 131.5
print(f"Stock tank oil API gravity: {api:.1f}")
```

![Separator test results showing GOR and oil formation volume factor](figures/separator_test.png)

### 3.5.4 Phase Envelope Generation

```python
from neqsim import jneqsim

# Gas condensate fluid
fluid = jneqsim.thermo.system.SystemPrEos(273.15 + 20.0, 50.0)
fluid.addComponent("nitrogen", 0.5)
fluid.addComponent("CO2", 3.0)
fluid.addComponent("methane", 75.0)
fluid.addComponent("ethane", 8.0)
fluid.addComponent("propane", 4.0)
fluid.addComponent("i-butane", 1.0)
fluid.addComponent("n-butane", 1.5)
fluid.addComponent("i-pentane", 0.5)
fluid.addComponent("n-pentane", 0.4)
fluid.addComponent("n-hexane", 0.6)
fluid.addTBPfraction("C7", 2.0, 96.0 / 1000.0, 0.738)
fluid.addTBPfraction("C10", 1.5, 134.0 / 1000.0, 0.792)
fluid.addTBPfraction("C20", 2.0, 350.0 / 1000.0, 0.880)
fluid.setMixingRule("classic")
fluid.getCharacterization().characterisePlusFraction()

# Calculate phase envelope
ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid)
ops.calcPTphaseEnvelope()

# Access results
dew_T = [t for t in ops.getOperation().get("dewT")]
dew_P = [p for p in ops.getOperation().get("dewP")]
bub_T = [t for t in ops.getOperation().get("bubT")]
bub_P = [p for p in ops.getOperation().get("bubP")]

print(f"Cricondenbar: T = {ops.getOperation().get('cricondenbar')[0]:.1f} K, "
      f"P = {ops.getOperation().get('cricondenbar')[1]:.1f} bara")
print(f"Cricondentherm: T = {ops.getOperation().get('cricondentherm')[0]:.1f} K, "
      f"P = {ops.getOperation().get('cricondentherm')[1]:.1f} bara")
```

![Phase envelope for the gas condensate fluid showing bubble point, dew point, cricondenbar and cricondentherm](figures/gas_condensate_phase_envelope.png)

## 3.6 EOS Parameter Tuning

### 3.6.1 Why Tuning Is Necessary

Default EOS parameters (from generalized correlations) typically give acceptable results for defined components but may be inaccurate for the pseudo-components representing the plus fraction. Tuning adjusts selected parameters to match experimental PVT data.

### 3.6.2 Tunable Parameters

The most commonly tuned parameters are:

1. **Binary interaction parameters ($k_{ij}$):** Especially between light components (CH$_4$, C$_2$, CO$_2$) and the heavy pseudo-components
2. **Critical properties of pseudo-components:** $T_c$, $P_c$, $\omega$ of C$_{7+}$ fractions
3. **Volume shift parameters:** To match liquid density
4. **Plus fraction molecular weight:** The reported M$_w$ of the plus fraction often has ±10% uncertainty

### 3.6.3 Matching Priority

The order of matching priority for production optimization is:

1. **Saturation pressure** — bubble point or dew point (highest priority)
2. **Liquid density / oil FVF** — affects volumetric calculations
3. **Gas-oil ratio** — separator test GOR
4. **Liquid dropout** — for gas condensates (CVD)
5. **Viscosity** — affects pressure drop calculations

### 3.6.4 Regression Workflow

A systematic tuning workflow:

1. **Start with default parameters** and compare against experimental data
2. **Adjust plus fraction molecular weight** (±10%) to match saturation pressure
3. **Tune $k_{ij}$** between methane and heavy pseudo-components to refine saturation pressure and liquid dropout
4. **Adjust volume shift** to match liquid density
5. **Iterate** until all experimental data are matched within acceptable tolerances

Acceptable tolerances for tuned models:

| Property | Target Accuracy |
|----------|----------------|
| Saturation pressure | ±1–2% |
| Liquid density | ±1–2% |
| GOR | ±3–5% |
| Liquid dropout (CVD) | ±10% of peak |
| Viscosity | ±10–15% |

### 3.6.5 Tuning in NeqSim

NeqSim allows modification of EOS parameters for tuning:

```python
from neqsim import jneqsim

# Create fluid and tune BIP between methane and a heavy fraction
fluid = jneqsim.thermo.system.SystemPrEos(273.15 + 100.0, 300.0)
fluid.addComponent("methane", 70.0)
fluid.addComponent("ethane", 8.0)
fluid.addComponent("propane", 5.0)
fluid.addTBPfraction("C7", 5.0, 96.0 / 1000.0, 0.738)
fluid.addTBPfraction("C20", 12.0, 400.0 / 1000.0, 0.910)
fluid.setMixingRule("classic")
fluid.getCharacterization().characterisePlusFraction()

# Set custom binary interaction parameter
# Between methane (index 0) and a heavy fraction
methane_index = 0
heavy_index = fluid.getPhase(0).getNumberOfComponents() - 1
fluid.setInteractionParameter(methane_index, heavy_index, 0.04)

# Recalculate to check effect
ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid)
ops.bubblePointPressureFlash(False)
print(f"Bubble point after tuning: {fluid.getPressure('bara'):.1f} bara")
```

## 3.7 Key PVT Properties

### 3.7.1 Gas-Oil Ratio (GOR)

The gas-oil ratio is the ratio of gas volume to oil volume at standard conditions:

$$
\text{GOR} = \frac{V_{\text{gas}}^{\text{sc}}}{V_{\text{oil}}^{\text{sc}}}
$$

where "sc" denotes standard conditions (typically 15°C and 1.01325 bara). GOR is expressed in Sm³/Sm³ (SI) or scf/bbl (field units).

The solution GOR $R_s$ is the amount of gas dissolved in the oil at reservoir conditions. As pressure drops below the bubble point, gas evolves and $R_s$ decreases.

### 3.7.2 Formation Volume Factor

The oil formation volume factor $B_o$ converts reservoir volumes to surface volumes:

$$
B_o = \frac{V_{\text{oil}}^{\text{reservoir}}}{V_{\text{oil}}^{\text{stock tank}}}
$$

$B_o$ is always greater than 1 (typically 1.1–2.0 for black oils) because the oil at reservoir conditions contains dissolved gas, which expands the volume. Below the bubble point, $B_o$ decreases as gas evolves.

The gas formation volume factor $B_g$ converts gas volumes:

$$
B_g = \frac{V_{\text{gas}}^{\text{reservoir}}}{V_{\text{gas}}^{\text{standard}}} = \frac{ZT P^{\text{sc}}}{T^{\text{sc}} P}
$$

### 3.7.3 Compressibility

The isothermal compressibility of oil above the bubble point is:

$$
c_o = -\frac{1}{V}\left(\frac{\partial V}{\partial P}\right)_T
$$

Oil compressibility is typically $10^{-5}$ to $10^{-4}$ bar$^{-1}$, much smaller than gas compressibility. Below the bubble point, the total system compressibility increases dramatically as free gas appears.

### 3.7.4 Viscosity Correlations

For cases where the EOS-based viscosity prediction is insufficient, empirical correlations can supplement:

**Dead oil viscosity** (Beggs-Robinson):

$$
\mu_{od} = 10^{10^{(3.0324 - 0.02023 \cdot \text{API})}/T^{1.163}} - 1
$$

**Live oil viscosity** (with dissolved gas):

$$
\mu_o = A \cdot \mu_{od}^B
$$

where $A$ and $B$ depend on the solution GOR.

## 3.8 Fluid Characterization Quality Checks

After creating a characterized fluid model, several quality checks should be performed:

1. **Mass balance:** Verify that the sum of all mole fractions equals 1.0 (or the intended total)
2. **Phase envelope reasonableness:** The critical point and cricondenbar should be physically reasonable for the fluid type
3. **Saturation pressure:** Compare predicted vs. measured bubble/dew point
4. **Density:** Compare predicted vs. measured at reservoir conditions
5. **GOR:** Compare predicted vs. measured at separator conditions
6. **Molecular weight:** The calculated mixture M$_w$ should match the reported value

```python
# Quality check: print fluid summary
ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid)
ops.TPflash()
fluid.initProperties()

print(f"Number of components: {fluid.getNumberOfComponents()}")
print(f"Number of phases: {fluid.getNumberOfPhases()}")
print(f"Mixture molecular weight: {fluid.getMolarMass('kg/mol') * 1000:.1f} g/mol")
print(f"Overall density: {fluid.getDensity('kg/m3'):.1f} kg/m3")

# Check sum of mole fractions
total_z = 0.0
for i in range(fluid.getNumberOfComponents()):
    total_z += fluid.getPhase(0).getComponent(i).getz()
print(f"Sum of mole fractions: {total_z:.6f}")
```

## 3.9 Advanced Topics

### 3.9.1 Lumping and Delumping

For computational efficiency, the pseudo-components from characterization can be lumped into a smaller number of groups. Common lumping schemes:

- **3-component:** Light (C$_1$–C$_3$), intermediate (C$_4$–C$_6$), heavy (C$_7+$)
- **6-component:** N$_2$+CO$_2$, C$_1$, C$_2$–C$_3$, C$_4$–C$_6$, C$_7$–C$_{12}$, C$_{13+}$
- **Reservoir-specific:** Optimized grouping based on K-value behavior

Delumping recovers the detailed composition from a lumped model for downstream calculations that require full composition information.

### 3.9.2 Wax and Asphaltene Characterization

For flow assurance studies, the plus fraction characterization must capture the wax-forming and asphaltene fractions:

- **Wax:** Primarily normal paraffins in the C$_{16}$–C$_{60+}$ range. Requires characterization of the n-paraffin content vs. carbon number.
- **Asphaltenes:** Heavy polar components. The CPA or PC-SAFT equation is better suited for asphaltene modeling than cubic EOS.

### 3.9.3 Compositional Grading

In thick reservoirs, gravity causes compositional variation with depth — lighter components concentrate at the top, heavier components at the bottom. This can lead to different fluid types at different depths in the same reservoir (e.g., gas cap above oil zone). Compositional grading models use the EOS to calculate the equilibrium composition profile.

## 3.10 Summary

Key points from this chapter:

- **Reservoir fluids** are classified as black oil, volatile oil, gas condensate, wet gas, or dry gas based on their phase behavior and composition
- **PVT experiments** (CCE, CVD, DL, separator test, swelling test, viscosity) provide the data for fluid model calibration
- **Plus fraction characterization** splits the heavy end into pseudo-components with estimated critical properties, using methods such as the Whitson gamma distribution or Pedersen correlations
- **EOS parameter tuning** adjusts BIPs, critical properties, and volume shifts to match experimental data — the saturation pressure and liquid density are highest priority
- **NeqSim** provides TBP fraction handling, phase envelope calculation, and separator test simulation for complete PVT workflows
- **Quality checks** (mass balance, phase envelope, saturation pressure, density) must be performed before using a fluid model in production optimization

## Exercises

1. **Exercise 3.1:** Given the following plus fraction data for a gas condensate:
   - C$_{7+}$ mole fraction: 8.5%
   - C$_{7+}$ molecular weight: 155 g/mol
   - C$_{7+}$ density: 0.795 g/cm³

   Create a NeqSim fluid model with at least 5 pseudo-components for the C$_{7+}$ fraction. Calculate the phase envelope and identify the fluid type.

2. **Exercise 3.2:** For a black oil with bubble point pressure of 180 bara at 95°C, perform a CCE simulation from 300 bara down to 50 bara. Plot the relative volume vs. pressure and identify the bubble point from the change in slope.

3. **Exercise 3.3:** Set up a three-stage separator test (70/15/1.5 bara) for a typical North Sea black oil. Calculate the GOR at each stage and the total GOR. How does the GOR change if you add a fourth stage at 5 bara?

4. **Exercise 3.4:** Create two fluid models for the same composition — one with SRK, one with PR. Compare the predicted bubble point pressures and liquid densities at reservoir conditions. Which equation gives results closer to typical literature values?

5. **Exercise 3.5:** Investigate the effect of C$_{7+}$ molecular weight on the phase envelope. Using the base case from Exercise 3.1, vary the C$_{7+}$ molecular weight by ±20% and plot the three phase envelopes on the same graph. How does the cricondenbar change?

6. **Exercise 3.6:** Calculate the API gravity and Watson K-factor for stock tank oils from three different reservoir fluids: a lean gas condensate (GOR ~ 5000), a volatile oil (GOR ~ 400), and a black oil (GOR ~ 100). Use NeqSim separator test simulations.

7. **Exercise 3.7 (Advanced):** Implement a simple regression to tune the methane-C$_{7+}$ BIP to match a measured bubble point pressure. Use a bisection algorithm to find the $k_{ij}$ value that gives the target bubble point within ±1 bara.

## References

1. Whitson, C. H. (1983). Characterizing hydrocarbon plus fractions. *Society of Petroleum Engineers Journal*, 23(4), 683–694.
2. Pedersen, K. S., Thomassen, P., & Fredenslund, A. (1989). Thermodynamics of petroleum mixtures containing heavy hydrocarbons. 3. Efficient flash calculation procedures using the SRK equation of state. *Industrial & Engineering Chemistry Process Design and Development*, 24(4), 948–954.
3. Pedersen, K. S., & Christensen, P. L. (2007). *Phase Behavior of Petroleum Reservoir Fluids*. CRC Press.
4. Danesh, A. (1998). *PVT and Phase Behaviour of Petroleum Reservoir Fluids*. Elsevier.
5. Lee, B. I., & Kesler, M. G. (1975). A generalized thermodynamic correlation based on three-parameter corresponding states. *AIChE Journal*, 21(3), 510–527.
6. Twu, C. H. (1984). An internally consistent correlation for predicting the critical properties and molecular weights of petroleum and coal-tar liquids. *Fluid Phase Equilibria*, 16(2), 137–150.
7. Ahmed, T. (2016). *Reservoir Engineering Handbook* (5th ed.). Gulf Professional Publishing.
8. McCain, W. D., Spivey, J. P., & Lenn, C. P. (2011). *Petroleum Reservoir Fluid Property Correlations*. PennWell Books.
9. Beggs, H. D., & Robinson, J. R. (1975). Estimating the viscosity of crude oil systems. *Journal of Petroleum Technology*, 27(9), 1140–1141.
10. Watson, K. M., & Nelson, E. F. (1933). Improved methods for approximating critical and thermal properties of petroleum fractions. *Industrial & Engineering Chemistry*, 25(8), 880–887.


## Figures

![Figure 3.1: Fig01 Molecular Weight Distribution](figures/fig01_molecular_weight_distribution.png)

*Figure 3.1: Fig01 Molecular Weight Distribution*

![Figure 3.2: Fig02 Phase Envelope Condensate](figures/fig02_phase_envelope_condensate.png)

*Figure 3.2: Fig02 Phase Envelope Condensate*

![Figure 3.3: Fig03 Liquid Dropout Curve](figures/fig03_liquid_dropout_curve.png)

*Figure 3.3: Fig03 Liquid Dropout Curve*

![Figure 3.4: Fig04 Gor Vs Pressure](figures/fig04_gor_vs_pressure.png)

*Figure 3.4: Fig04 Gor Vs Pressure*

![Figure 3.5: Fig05 Bo Vs Pressure](figures/fig05_bo_vs_pressure.png)

*Figure 3.5: Fig05 Bo Vs Pressure*
