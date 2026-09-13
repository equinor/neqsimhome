
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
import jpype
jneqsim = jpype.JPackage("neqsim")

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
import jpype
jneqsim = jpype.JPackage("neqsim")

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
import jpype
jneqsim = jpype.JPackage("neqsim")

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
import jpype
jneqsim = jpype.JPackage("neqsim")

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
import jpype
jneqsim = jpype.JPackage("neqsim")

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

Illustrative teaching targets for tuned models, to be replaced by project-specific criteria and laboratory uncertainty:

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
import jpype
jneqsim = jpype.JPackage("neqsim")

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
fluid.setBinaryInteractionParameter(methane_index, heavy_index, 0.04)

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

$B_o$ is commonly greater than 1 for live reservoir oils (typically 1.1–2.0 for black oils) because the oil at reservoir conditions contains dissolved gas, which expands the volume. Below the bubble point, $B_o$ decreases as gas evolves.

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
