# Export Systems and Fiscal Metering

<!-- Chapter metadata -->
<!-- Notebooks: ch17_gas_quality_iso6976.ipynb, ch17_export_pipeline_hydraulics.ipynb -->
<!-- Estimated pages: 22 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Design gas export systems including pipeline sizing, compression requirements, and gas quality specifications (heating value, Wobbe index, water dew point, hydrocarbon dew point)
2. Describe oil export options including pipeline, shuttle tanker, and FPSO operations
3. Explain the fundamentals of LNG as an export route and its quality requirements
4. Calculate gas quality parameters using ISO 6976 (calorific value, density, relative density, Wobbe index) and related AGA/ISO standards
5. Describe the operating principles, advantages, and limitations of fiscal metering technologies: ultrasonic, orifice/differential pressure, Coriolis, and turbine meters
6. Evaluate measurement uncertainty in fiscal metering and understand the role of prover systems
7. Distinguish between fiscal metering, custody transfer, and allocation metering
8. Model gas quality calculations, water dew point, hydrocarbon dew point (cricondentherm), and export pipeline pressure drop using NeqSim

---

## 19.1 Introduction

The export system is the final link in the production chain, connecting the processing facility to the market. It encompasses the physical infrastructure (pipelines, loading systems, compression), quality specifications (gas sales contracts, crude oil assays), and measurement systems (fiscal meters, provers, allocation systems) that govern the commercial transfer of hydrocarbons.

From a production optimization perspective, the export system imposes constraints that ripple back through the entire facility:

- **Gas quality specifications** (heating value, Wobbe index, dew points) determine the required processing depth — how much NGL must be extracted and how dry the gas must be
- **Pipeline hydraulics** set the required export pressure, which dictates compressor power and discharge temperature
- **Metering accuracy** directly affects revenue — a 0.1% measurement bias on a major pipeline can represent millions of dollars per year
- **Contractual obligations** (daily contracted quantities, quality windows, take-or-pay provisions) constrain the operating envelope

This chapter covers gas and oil export systems, LNG fundamentals, gas quality standards and calculations, fiscal metering technologies, custody transfer, and allocation metering. NeqSim examples demonstrate how to perform ISO 6976 gas quality calculations, determine dew points, and model export pipeline hydraulics.

---

## 19.2 Gas Export Systems

### 19.2.1 Pipeline Export

Gas export pipelines transport processed natural gas from offshore platforms or onshore processing plants to gas terminals, LNG facilities, or directly to distribution networks. Key design parameters include:

**Pipeline sizing** starts with a dimensional screening model. For horizontal, steady, isothermal, single-phase gas flow with constant $Z$, constant Darcy friction factor $f_D$, and negligible acceleration:

$$
\dot m=A\sqrt{\frac{D M_w(P_1^2-P_2^2)}{f_D L ZRT}},\qquad
Q_b=\frac{\dot m}{\rho_b},\qquad A=\frac{\pi D^2}{4}.
$$

Use $P_1,P_2$ in Pa absolute, $D,L$ in m, $M_w$ in kg/mol, $R$ in J/(mol K), $T$ in K and $\rho_b$ in kg/m³ at explicitly declared base conditions. The result is kg/s and base m³/s. This follows by integrating $dP/dz=-f_D\rho v^2/(2D)$ with $\rho=PM_w/(ZRT)$ and constant mass flow. It is an order-of-magnitude check, not the full Beggs–Brill calculation used later. Heat exchange, elevation, variable properties, acceleration and liquid phases require a more complete model. Empirical pipeline equations such as Panhandle must retain their original unit constants and applicability rather than mixing field and SI units.

**Typical pipeline parameters**:

| Parameter | Small (satellite) | Medium (platform) | Large (trunk line) |
|-----------|-------------------|--------------------|--------------------|
| Diameter (inches) | 8–16 | 20–32 | 36–48 |
| Length (km) | 10–50 | 50–200 | 200–1,200 |
| Inlet pressure (bara) | 80–150 | 100–200 | 150–250 |
| Flow rate (MSm³/d) | 1–5 | 5–20 | 20–100+ |
| Material | Carbon steel (CS) | CS / CRA-lined | CS |

### 19.2.2 Export Compression

Export gas compression is required to deliver gas at the contractual pipeline inlet pressure. The compression system must handle:

- **Steady-state operation**: Maintaining pipeline inlet pressure at varying production rates and reservoir pressures
- **Turndown**: As field production declines, the compressor must operate at reduced throughput while maintaining discharge pressure
- **Recycle**: At very low throughput, gas must be recycled to keep the compressor above its surge limit (see Chapter 13)

For a fixed inlet state, efficiency and discharge pressure, compression power is approximately proportional to mass flow; its dependence on pressure ratio is nonlinear (see Chapter 12). For export compression, the compression ratio is typically modest (1.5–3.0), but the gas volumes are large, resulting in significant power demand:

$$
W_{\text{export}} = \frac{\dot{m} \cdot Z_{\text{avg}} \cdot R \cdot T_1}{M \cdot \eta_s} \cdot \frac{k}{k-1} \cdot \left[\left(\frac{P_2}{P_1}\right)^{(k-1)/k} - 1\right]
$$

where $\dot{m}$ is the mass flow rate, $Z_{\text{avg}}$ is the average compressibility factor, $R$ is the universal gas constant, $T_1$ is the suction temperature, $M$ is the molecular weight, $\eta_s$ is the isentropic efficiency, and $k$ is the constant ratio of specific heats. This is a constant-property isentropic approximation with an approximate real-gas $Z$ correction, not the polytropic-path formula or an exact real-gas work calculation. Use the enthalpy-rise result for the NeqSim model.

### 19.2.3 Gas Quality Specifications

Gas sales contracts specify a quality window that the export gas must satisfy. Specifications vary by pipeline system and market. The following teaching windows are assumed examples, not verified current NCS, UK or US requirements; each real delivery point needs its applicable contract, pressure/temperature basis and period. ISO 6976 supplies a property-calculation method, not a sales-quality window \cite{iso6976scope}:

| Parameter | Illustrative contract A | Illustrative contract B | Illustrative contract C |
|-----------|-----------------|---------------|-------------------|
| Gross calorific value (MJ/Sm³) | 36.0–44.0 | 36.9–42.3 | 35.4–41.2 |
| Wobbe index (MJ/Sm³) | 46.5–54.0 | 47.2–51.4 | 44.6–52.2 |
| Water dew point (°C at delivery P) | −18 | −10 at 69 barg | −7 at 69 barg |
| HC dew point (cricondentherm, °C) | −2 | −2 at 1–69 barg | 7–15 |
| H₂S (mg/Sm³) | < 5 | < 5 | < 6 (¼ grain/100 scf) |
| CO₂ (mol%) | < 2.5 | < 2.0 | < 2.0 |
| Total sulfur (mg/Sm³) | < 30 | < 50 | < 115 |
| O₂ (mol%) | < 0.001 | < 0.001 | < 0.02–1.0 |
| Mercury (µg/Sm³) | < 0.03 | Not specified | Not specified |

**Heating value** (calorific value) is the amount of energy released per unit volume when the gas is burned completely. The gross (superior) calorific value (GCV) includes the latent heat of condensation of water vapor in the combustion products; the net (inferior) calorific value (NCV) excludes it. The GCV is typically 10–12% higher than the NCV for natural gas.

**Wobbe index** is the key parameter for gas interchangeability. It ensures that different gas compositions deliver approximately the same thermal output when burned in the same burner at the same supply pressure:

$$
W_s = \frac{H_s}{\sqrt{d}}
$$

where $W_s$ is the superior (gross) Wobbe index, $H_s$ is the superior calorific value (on a volumetric basis), and $d$ is the relative density of the gas (air = 1.0). The Wobbe index is the single most important combustion property because the heat input to a burner at constant pressure is proportional to $W_s$.

**Water dew point** — the temperature at which the first drop of liquid water condenses from the gas at a specified pressure. Cooling below the water dew point can cause liquid water accumulation in the pipeline, leading to corrosion, hydrate formation, and slug flow.

**Hydrocarbon dew point** is the temperature at which liquid hydrocarbon first forms at a specified pressure. The **cricondentherm** is the maximum temperature on the full hydrocarbon phase envelope; these are different specifications and must not be interchanged. Hydrocarbon condensation in the pipeline causes liquid accumulation, increased pressure drop, slugging, and measurement errors.

![Typical gas quality envelope showing GCV, Wobbe index, HC dew point, and water dew point specifications](figures/gas_quality_envelope.png)

---

## 19.3 Oil Export Systems

### 19.3.1 Pipeline Export

Oil export pipelines transport stabilized crude oil or partially stabilized crude from the production facility to a terminal or refinery. Key considerations include:

- **Viscosity and pour point**: Heavy or waxy crudes may require heating, diluent injection, or chemical treatment to maintain pumpability
- **Pipeline pressure rating**: Designed for maximum allowable operating pressure (MAOP) accounting for internal pressure, external pressure (subsea), and surge (water hammer)
- **Wax management**: Regular pigging to remove wax deposits; chemical wax inhibitor injection
- **Vapor pressure**: The true vapor pressure (TVP) of the crude at pipeline temperature must be below the minimum local operating absolute pressure, including high points and transient minima to prevent gas breakout

The following RVP limits are illustrative exercise values. RVP is a specified test property; it is not interchangeable with true vapor pressure at pipeline conditions or a universal regional requirement:

| Climate/Region | Maximum RVP (kPa / psi) |
|---------------|------------------------|
| NCS crude pipeline | 82.7 kPa (12 psi) |
| North Sea export | 65–90 kPa |
| US Gulf Coast | 69 kPa (10 psi) |
| Hot climates | 48–55 kPa (7–8 psi) |

### 19.3.2 Shuttle Tanker Loading

Where pipeline export is not economical (remote locations, marginal fields), crude oil is exported via shuttle tankers loaded from an FPSO, FSO, or loading buoy:

- **Loading rate**: Typically 4,000–10,000 m³/hr depending on cargo pump capacity and tanker size
- **Cargo tank vapor management**: Inert gas (N₂ or flue gas) blankets prevent explosive atmospheres; vapor return lines manage displaced tank vapors
- **Crude quality**: Each tanker cargo is independently sampled and measured for custody transfer
- **Loading downtime**: Weather limitations (wave height, wind speed) and tanker scheduling affect production regularity

### 19.3.3 FPSO Operations

Floating Production, Storage, and Offloading (FPSO) vessels combine the production facility and crude storage. Export considerations include:

- **Storage capacity**: Typically 1–2 million barrels; must buffer production against shuttle tanker intervals
- **Crude blending**: Multiple reservoir fluids may be commingled; the export assay varies with production allocation
- **Gas export from FPSO**: Options include gas export pipeline, gas reinjection, gas-to-power, or LNG (rare offshore)

---

## 19.4 LNG Export

### 19.4.1 LNG Fundamentals

Liquefied Natural Gas (LNG) is natural gas cooled to approximately −162 °C at atmospheric pressure, reducing its volume by a factor of approximately 600. LNG export is used when pipeline export is not feasible due to distance or geopolitical barriers.

The key quality parameters for LNG differ from pipeline gas:

| Parameter | Typical LNG Spec |
|-----------|-----------------|
| Methane (mol%) | > 85 |
| Ethane (mol%) | < 10 |
| Propane + (mol%) | < 5 |
| CO₂ (ppm) | < 50 (to prevent freezing) |
| H₂S (ppm) | < 4 |
| Water (ppm) | < 1 (to prevent freezing and hydrate) |
| Mercury (ng/Sm³) | < 10 (to protect aluminum HX) |
| GCV (MJ/Sm³) | 37–43 (varies by destination) |

The extremely tight CO₂ and water specifications reflect the need to prevent solidification at cryogenic temperatures. Mercury removal to the ng/Sm³ level is required because mercury causes liquid metal embrittlement of the aluminum brazed plate-fin heat exchangers used in LNG plants.

### 19.4.2 LNG Heating Value and Regasification

LNG markets have different heating value preferences:

- **Japan/Korea/Taiwan**: Higher heating value (rich gas, GCV > 41 MJ/Sm³), requiring less NGL extraction
- **Europe/UK**: Lower heating value (lean gas, GCV 37–39 MJ/Sm³), requiring more NGL extraction or nitrogen ballasting
- **US Gulf Coast**: Moderate (GCV 37–41 MJ/Sm³)

At the receiving terminal, LNG is regasified and the heating value may be adjusted by:
- Adding nitrogen (to reduce GCV for lean-gas markets)
- Injecting LPG (to increase GCV for rich-gas markets)
- Extracting NGL (to reduce GCV and recover valuable liquids)

---

## 19.5 Gas Quality Calculations — ISO 6976

### 19.5.1 Overview of ISO 6976

ISO 6976 (*Natural gas — Calculation of calorific values, density, relative density and Wobbe indices from composition*) is the fundamental standard for gas quality calculations from compositional analysis. The 2016 edition (ISO 6976:2016) supersedes the 1995 version and includes updated physical constants and summation procedures.

The standard provides tabulated values for each pure component at reference conditions, enabling calculation of mixture properties by simple mole-fraction-weighted summation:

**Ideal superior (gross) calorific value** on a molar basis:

$$
H_{s,\text{ideal}}^{\circ} = \sum_{i=1}^{N} x_i \cdot H_{s,i}^{\circ}
$$

where $x_i$ is the mole fraction of component $i$ and $H_{s,i}^{\circ}$ is the ideal molar superior calorific value of pure component $i$ at the reference combustion temperature.

**Conversion to volumetric basis** requires the ideal gas molar volume at the volume reference conditions:

$$
H_s = \frac{H_{s,\text{ideal}}^{\circ}}{V_m^{\circ}} \cdot \frac{1}{Z_{\text{mix}}}
$$

where $V_m^{\circ} = RT_v / P_v$ is the ideal molar volume at the volumetric reference temperature $T_v$ and pressure $P_v$, and $Z_{\text{mix}}$ is the compressibility factor of the mixture at the stated volume reference conditions (accounting for non-ideal behavior).

The compressibility factor $Z_{\text{mix}}$ is calculated from summation factors:

$$
Z_{\text{mix}} = 1 - \left(\sum_{i=1}^{N} x_i \sqrt{b_i}\right)^2
$$

where $b_i$ are the summation factors tabulated in ISO 6976 for each component at specific temperatures.

### 19.5.2 Reference Conditions

ISO 6976 allows multiple combinations of reference conditions. The most common are:

| Region | Combustion Ref. T | Volume Ref. T | Volume Ref. P | Units |
|--------|-------------------|---------------|---------------|-------|
| International (ISO) | 25 °C | 15 °C | 101.325 kPa | MJ/Sm³ |
| NCS (Norway) | 25 °C | 15 °C | 101.325 kPa | MJ/Sm³ |
| UK | 15 °C | 15 °C | 101.325 kPa | MJ/Sm³ |
| USA | 60 °F (15.56 °C) | 60 °F | 14.696 psia | BTU/scf |
| Germany | 25 °C | 0 °C | 101.325 kPa | MJ/Nm³ |

It is essential to specify the reference conditions when reporting gas quality parameters. A heating value stated as "40 MJ/Sm³" is meaningless without stating the combustion temperature and the metering (volume) conditions.

### 19.5.3 Wobbe Index Calculation

The Wobbe index is calculated from the calorific value and relative density:

$$
W_s = \frac{H_s}{\sqrt{d}}
$$

Use real relative density with real volumetric calorific value, or ideal relative density with ideal calorific value. The ideal relative density is:

$$
d = \frac{\sum_{i} x_i \cdot M_i}{M_{\text{air}}}
$$

with $M_{\text{air}} = 28.9626$ g/mol (ISO 6976:2016 value). The real relative density accounts for non-ideal behavior:

$$
d_{\text{real}} = d_{\text{ideal}} \cdot \frac{Z_{\text{air}}}{Z_{\text{mix}}}
$$

### 19.5.4 NeqSim Example: ISO 6976 Gas Quality Calculation

NeqSim implements the ISO 6976 standard (both the 1995 and 2016 editions) through the `Standard_ISO6976` and `Standard_ISO6976_2016` classes. The following example calculates gas quality at explicitly stated reference conditions. The volume-basis getter returns kJ/Sm³, so calorific values and Wobbe indices are divided by 1000 before reporting MJ/Sm³. The source implementation, rather than a display label, establishes this unit conversion \cite{neqsim2026update}:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define export gas composition (mole fractions)
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 15.0, 1.01325)
gas.addComponent("nitrogen", 0.008)
gas.addComponent("CO2", 0.015)
gas.addComponent("methane", 0.890)
gas.addComponent("ethane", 0.055)
gas.addComponent("propane", 0.018)
gas.addComponent("i-butane", 0.004)
gas.addComponent("n-butane", 0.005)
gas.addComponent("i-pentane", 0.002)
gas.addComponent("n-pentane", 0.001)
gas.addComponent("n-hexane", 0.002)
gas.setMixingRule("classic")

# Create ISO 6976:2016 standard object
# Parameters: (fluid, volumeRefTemp_C, energyRefTemp_C, basis)
iso6976 = jneqsim.standards.gasquality.Standard_ISO6976_2016(
    gas, 15, 25, "volume"
)

# Calculate all properties
iso6976.calculate()

# Retrieve key results
gcv = iso6976.getValue("SuperiorCalorificValue") / 1000.0   # MJ/Sm3
ncv = iso6976.getValue("InferiorCalorificValue") / 1000.0    # MJ/Sm3
wobbe_sup = iso6976.getValue("SuperiorWobbeIndex") / 1000.0  # MJ/Sm3
rel_density = iso6976.getValue("RelativeDensity")   # dimensionless
density = iso6976.getValue("MolarMass")             # g/mol

print("=== ISO 6976:2016 Gas Quality Report ===")
print(f"Reference conditions: volume at 15 °C, combustion at 25 °C")
print(f"Superior Calorific Value (GCV):  {gcv:.2f} MJ/Sm³")
print(f"Inferior Calorific Value (NCV):  {ncv:.2f} MJ/Sm³")
print(f"Superior Wobbe Index:            {wobbe_sup:.2f} MJ/Sm³")
print(f"Relative Density (air=1):        {rel_density:.4f}")
print(f"Molar Mass:                      {density:.2f} g/mol")
```

### 19.5.5 Sensitivity Analysis: Effect of NGL Content on Gas Quality

The gas processing depth (degree of NGL extraction) directly determines the export gas quality. The following example shows how heating value and Wobbe index vary with the ethane-plus content:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Base composition: vary C2+ content from lean to rich gas
c2_plus_fractions = [0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15]

print(f"{'C2+ (mol%)':>12} {'GCV (MJ/Sm³)':>14} {'Wobbe (MJ/Sm³)':>16} {'d (rel)':>10}")
print("-" * 54)

for c2_frac in c2_plus_fractions:
    gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 15.0, 1.01325)
    gas.addComponent("nitrogen", 0.01)
    gas.addComponent("CO2", 0.015)

    # Distribute C2+ among ethane, propane, butane
    c2 = c2_frac * 0.60
    c3 = c2_frac * 0.25
    c4 = c2_frac * 0.15
    c1 = 1.0 - 0.01 - 0.015 - c2 - c3 - c4
    gas.addComponent("methane", c1)
    gas.addComponent("ethane", c2)
    gas.addComponent("propane", c3)
    gas.addComponent("n-butane", c4)
    gas.setMixingRule("classic")

    iso6976 = jneqsim.standards.gasquality.Standard_ISO6976_2016(
        gas, 15, 25, "volume"
    )
    iso6976.calculate()

    gcv = iso6976.getValue("SuperiorCalorificValue") / 1000.0
    wobbe = iso6976.getValue("SuperiorWobbeIndex") / 1000.0
    rel_d = iso6976.getValue("RelativeDensity")

    print(f"{c2_frac*100:>12.1f} {gcv:>14.2f} {wobbe:>16.2f} {rel_d:>10.4f}")
```

![Effect of NGL content on gas heating value and Wobbe index](figures/gcv_wobbe_vs_ngl.png)

---

## 19.6 Dew Point Calculations

### 19.6.1 Water Dew Point

The water dew point is the temperature at which the gas becomes saturated with water vapor at a given pressure. It is the critical specification for preventing free water in the pipeline:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Calculate water dew point of export gas
gas = jneqsim.thermo.system.SystemSrkCPAstatoil(273.15 + 15.0, 70.0)
gas.addComponent("methane", 0.890)
gas.addComponent("ethane", 0.055)
gas.addComponent("propane", 0.018)
gas.addComponent("CO2", 0.015)
gas.addComponent("nitrogen", 0.008)
gas.addComponent("water", 20e-6)  # 20 ppm water in gas
gas.setMixingRule(10)

# Run water dew point flash
ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(gas)
try:
    ops.waterDewPointTemperatureFlash()
    wdp_K = gas.getTemperature()
    wdp_C = wdp_K - 273.15
    print(f"Water dew point at 70 bara: {wdp_C:.1f} °C")
except Exception as e:
    print(f"Water dew point calculation: {e}")

# Vary pressure and compute water dew point line
pressures = [20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 150.0]
print(f"\n{'P (bara)':>10} {'WDP (°C)':>10}")
print("-" * 22)
for P in pressures:
    gas_p = gas.clone()
    gas_p.setPressure(P, "bara")
    ops_p = jneqsim.thermodynamicoperations.ThermodynamicOperations(gas_p)
    try:
        ops_p.waterDewPointTemperatureFlash()
        wdp = gas_p.getTemperature() - 273.15
        print(f"{P:>10.0f} {wdp:>10.1f}")
    except Exception:
        print(f"{P:>10.0f} {'N/A':>10}")
```

### 19.6.2 Hydrocarbon Dew Point and Cricondentherm

The hydrocarbon dew point curve defines the boundary between single-phase gas and two-phase (gas + liquid hydrocarbon) regions. The cricondentherm — the maximum temperature on this curve — is one possible contractual measure of the highest condensation temperature. Other contracts specify a dew point at one pressure or over a pressure interval, which requires a different comparison:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Calculate HC dew point curve (phase envelope)
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 15.0, 70.0)
gas.addComponent("nitrogen", 0.008)
gas.addComponent("CO2", 0.015)
gas.addComponent("methane", 0.880)
gas.addComponent("ethane", 0.055)
gas.addComponent("propane", 0.020)
gas.addComponent("i-butane", 0.005)
gas.addComponent("n-butane", 0.007)
gas.addComponent("i-pentane", 0.003)
gas.addComponent("n-pentane", 0.002)
gas.addComponent("n-hexane", 0.003)
gas.addComponent("n-heptane", 0.002)
gas.setMixingRule("classic")

# Calculate phase envelope to get cricondentherm
ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(gas)
ops.calcPTphaseEnvelope()

# Get dew point curve data
dew_temps = ops.get("dewT")   # temperatures in K
dew_press = ops.get("dewP")   # pressures in bara

# Find cricondentherm (max temperature on dew point curve)
max_T_K = max([float(t) for t in dew_temps])
max_T_C = max_T_K - 273.15
idx = [float(t) for t in dew_temps].index(max_T_K)
cricondentherm_P = float(dew_press[idx])

print(f"Cricondentherm: {max_T_C:.1f} °C at {cricondentherm_P:.1f} bara")

# Print dew point curve
print(f"\n{'T (°C)':>10} {'P (bara)':>10}")
print("-" * 22)
for i in range(len(dew_temps)):
    T_C = float(dew_temps[i]) - 273.15
    P = float(dew_press[i])
    if P > 0.5:  # filter valid points
        print(f"{T_C:>10.1f} {P:>10.1f}")
```

The HC dew point is critically sensitive to the heavy-end characterization. Even trace amounts of C7+ components (a few hundred ppm) can shift the cricondentherm by several degrees. This is why accurate gas chromatography with extended analysis (C6+ or C9+ breakdown) is essential for dew point prediction.

![Phase envelope showing cricondentherm and cricondenbar for typical export gas](figures/phase_envelope_export_gas.png)

### 19.6.3 Effect of Processing on Dew Points

The gas processing choices directly affect the export gas dew points:

| Processing Option | Effect on HC Dew Point | Effect on Water Dew Point |
|-------------------|----------------------|--------------------------|
| TEG dehydration | No change | Reduces to −15 to −25 °C |
| Molecular sieve | No change | Reduces to −40 to −80 °C |
| JT expansion | Reduces significantly | Reduces moderately |
| Turboexpander | Reduces significantly | Reduces moderately |
| NGL extraction (C3+) | Reduces significantly | No direct effect |
| Refrigeration | Reduces (sets spec) | May condense water |

---

## 19.7 Fiscal Metering Technologies

Fiscal metering is the measurement of hydrocarbon quantities for the purpose of commercial transactions (sale, purchase, tariff, or tax). The financial implications demand the highest possible accuracy, typically ±0.1% to ±0.5% of reading for oil and ±0.5% to ±1.0% for gas.

### 19.7.1 Ultrasonic Meters

Ultrasonic flow meters measure the transit time difference of acoustic pulses traveling with and against the flow:

$$
v = \frac{L}{2\cos\theta} \cdot \frac{\Delta t}{t_{\text{up}} \cdot t_{\text{down}}}
$$

where $v$ is the average flow velocity along the acoustic path, $L$ is the path length, $\theta$ is the angle between the acoustic path and the pipe axis, $\Delta t = t_{\text{up}} - t_{\text{down}}$ is the transit time difference, and $t_{\text{up}}$ and $t_{\text{down}}$ are the upstream and downstream transit times.

Multi-path ultrasonic meters (typically 4–6 paths) sample the velocity profile at multiple chord positions, using numerical quadrature to determine the volume flow rate:

$$
Q = A \cdot \sum_{i=1}^{n} w_i \cdot v_i
$$

where $A$ is the pipe cross-sectional area, $w_i$ are the quadrature weights (e.g., Gauss-Jacobi), and $v_i$ are the path velocities.

**Advantages**: No pressure drop, no moving parts, wide rangeability (100:1), bidirectional capability, diagnostic information (speed of sound, velocity profile symmetry, turbulence indicators).

**Limitations**: Sensitive to installation effects (upstream disturbances), requires careful calibration, acoustic coupling challenges in some fluids (high CO₂, wet gas).

**Standards**: AGA Report No. 9 (gas), API MPMS Chapter 5.8 (liquid).

### 19.7.2 Orifice Plates (Differential Pressure)

The orifice plate is the traditional fiscal metering technology for gas measurement. Flow rate is calculated from the measured differential pressure across a precisely machined sharp-edged orifice:

$$
Q_m = C_d \cdot \varepsilon \cdot E \cdot \frac{\pi}{4} d^2 \cdot \sqrt{2 \rho_1 \Delta P}
$$

where $Q_m$ is the mass flow rate, $\varepsilon$ is the gas expansibility factor (approximately one for an incompressible liquid), $C_d$ is the discharge coefficient (typically 0.59–0.61), $E = (1 - \beta^4)^{-1/2}$ is the velocity of approach factor, $d$ is the orifice bore diameter, $\beta = d/D$ is the diameter ratio, $\rho_1$ is the upstream density, and $\Delta P$ is the differential pressure.

The following expression shows the structure of the Reader–Harris/Gallagher correlation. The complete applicable ISO 5167-2 equation includes tap and small-pipe corrections and its limits on geometry and Reynolds number; this abbreviated display is not a fiscal implementation:

$$
\begin{aligned}
C_d ={}& 0.5961 + 0.0261\beta^2 - 0.216\beta^8 \\
&+ 0.000521\left(\frac{10^6\beta}{\mathrm{Re}_D}\right)^{0.7} \\
&+ (0.0188+0.0063A)\beta^{3.5}\left(\frac{10^6}{\mathrm{Re}_D}\right)^{0.3}
+ \Delta C_{\mathrm{up}} + \Delta C_{\mathrm{down}}
\end{aligned}
$$

Here $A=(19000\beta/\mathrm{Re}_D)^{0.8}$, $\mathrm{Re}_D$ is the pipe Reynolds number, and the symbolic tap correction terms depend on the tap location (flange, D-D/2, or corner taps).

**Advantages**: Well-established, mature standards (ISO 5167, AGA Report No. 3), no calibration required if manufactured to standard, low cost.

**Limitations**: Limited rangeability (3:1 to 5:1 per orifice plate), permanent pressure loss (40–90% of DP), sensitivity to edge condition (erosion, deposits), square-root relationship amplifies measurement errors at low flow.

### 19.7.3 Coriolis Meters

Coriolis meters measure mass flow directly by detecting the Coriolis force acting on fluid flowing through vibrating tubes:

$$
\dot{m}=K_{\Delta t}\Delta t
$$

Here $K_{\Delta t}$ is an instrument-specific calibrated coefficient with the units needed to convert sensor time delay to mass flow. This is a local response approximation; the transmitter applies its own temperature, pressure and zero corrections. The density relation below is likewise a calibrated oscillator model, not a universal meter calibration.

Additionally, Coriolis meters provide a direct density measurement from the vibration frequency:

$$
\rho = K_1 \cdot \frac{1}{f^2} - K_2
$$

where $K_1$ and $K_2$ are calibration constants.

**Advantages**: Direct mass flow measurement (no density input needed), simultaneous density measurement, high accuracy (±0.05% for liquid, ±0.35% for gas), insensitive to velocity profile, no straight pipe requirements.

**Limitations**: High cost for large sizes (> 8 inches), sensitive to two-phase flow (gas bubbles in liquid or liquid droplets in gas), pressure drop through curved tubes, potential vibration interference in some installations.

**Standards**: ISO 10790, API MPMS Chapter 5.6.

### 19.7.4 Turbine Meters

Turbine meters measure volumetric flow rate from the rotational speed of a rotor placed in the flow:

$$
Q = \frac{f_{\text{pulse}}}{K}
$$

where $Q$ is the volumetric flow rate, $f_{\text{pulse}}$ is the pulse frequency from the rotor, and $K$ is the K-factor (pulses per unit volume, determined by calibration).

**Advantages**: High accuracy for liquid (±0.15%), direct volumetric measurement suitable for prover calibration, well-established technology, relatively compact.

**Limitations**: Moving parts (bearing wear limits life), sensitive to viscosity changes, requires flow conditioning, limited rangeability (10:1 to 20:1), upstream strainer required to prevent bearing damage.

**Standards**: API MPMS Chapter 5.3.

### 19.7.5 Metering Technology Comparison

| Feature | Ultrasonic | Orifice | Coriolis | Turbine |
|---------|-----------|---------|---------|---------|
| Measurement type | Velocity → Volume | DP → Mass/Volume | Mass (direct) | Volume (direct) |
| Typical accuracy (gas) | ±0.5–1.0% | ±0.5–1.5% | ±0.35–0.5% | ±0.5–1.0% |
| Typical accuracy (liquid) | ±0.15–0.3% | ±0.5–1.0% | ±0.05–0.1% | ±0.15–0.25% |
| Rangeability | 100:1 | 3:1 – 5:1 | 80:1 | 10:1 – 20:1 |
| Pressure loss | None | 40–90% of DP | Moderate | Moderate |
| Moving parts | None | None | None (vibrating) | Yes (rotor) |
| Calibration required | Yes (flow cal) | No (if to std) | Yes | Yes |
| Size range (inches) | 2–60 | 2–30 | 0.5–16 | 2–24 |
| Multiphase tolerance | Limited | Poor | Poor | Poor |
| Diagnostic capability | Excellent | Limited | Good | Limited |

### 19.7.6 Wet Gas and Multiphase Metering

Conventional meters assume single-phase flow and introduce significant errors when liquid is present in the gas stream (wet gas) or when multiple phases flow simultaneously. Specialized meters have been developed:

**Wet gas meters** correct for the presence of small amounts of liquid in a predominantly gas flow. The over-reading of a standard meter due to liquid presence is correlated by the Lockhart-Martinelli parameter:

$$
X_{LM} = \frac{\dot{m}_L}{\dot{m}_G} \sqrt{\frac{\rho_G}{\rho_L}}
$$

where $\dot{m}_L$ and $\dot{m}_G$ are the liquid and gas mass flow rates, and $\rho_G$ and $\rho_L$ are the gas and liquid densities. Corrections based on $X_{LM}$ can reduce the over-reading from 20–40% (uncorrected) to 2–5% (corrected).

**Multiphase flow meters (MPFM)** combine multiple measurement principles — typically a combination of gamma-ray attenuation (for phase fractions), venturi or cross-correlation (for velocity), and microwave or capacitance (for water cut) — to measure oil, gas, and water flow rates simultaneously. Accuracy is typically ±5% for each phase, sufficient for allocation metering but not fiscal-quality measurement.

---

## 19.8 Measurement Uncertainty

### 19.8.1 Uncertainty Analysis Framework

Fiscal metering systems must comply with measurement uncertainty requirements set by regulations and contracts. The uncertainty analysis follows ISO/GUM (Guide to the Expression of Uncertainty in Measurement) and specific industry standards:

The combined standard uncertainty of the mass flow measurement is:

$$
u_c^2(Q_m)=\sum_i c_i^2u^2(x_i)+2\sum_{i<j}c_ic_j\operatorname{cov}(x_i,x_j),\qquad c_i=\frac{\partial Q_m}{\partial x_i}
$$

where $x_i$ are the input quantities (differential pressure, density, discharge coefficient, pipe diameter, etc.) and $u(x_i)$ are their standard uncertainties. The expanded uncertainty at 95% confidence is:

$$
U = k \cdot u_c(Q_m)
$$

The shorthand $k=2$ approximates 95% coverage for an approximately normal result with sufficiently large effective degrees of freedom. It is not a general conversion from every stated instrument limit. Convert input uncertainties to standard deviations and include correlations before combination \cite{jcgm100gum}.

### 19.8.2 Typical Uncertainty Budgets

**Illustrative gas-meter budget**, with independent one-standard-deviation relative inputs, ideal-density sensitivity, fixed expansibility/discharge correlations and $\beta=0.60$. Correlation and expansibility contributions omitted here must be added for a fiscal system:

| Parameter | Typical Uncertainty (%) | Sensitivity Coefficient | Contribution (%) |
|-----------|------------------------|------------------------|-------------------|
| Differential pressure ($\Delta P$) | 0.10 | 0.50 | 0.050 |
| Static pressure ($P$) | 0.05 | 0.50 | 0.025 |
| Temperature ($T$) | 0.10 | 0.50 | 0.050 |
| Orifice diameter ($d$) | 0.03 | 2.298 | 0.069 |
| Pipe diameter ($D$) | 0.04 | −0.298 | 0.012 |
| Discharge coefficient ($C_d$) | 0.50 | 1.00 | 0.500 |
| Gas composition | 0.10 | — | 0.100 |
| **Combined (RSS)** | | | **0.520** |

The geometric relative sensitivity coefficients are $2/(1-\beta^4)$ for bore and $-2\beta^4/(1-\beta^4)$ for pipe diameter when $C_d$ and $\varepsilon$ are held fixed. Their values are therefore not constant across all diameter ratios.

For liquid metering, the uncertainty is often lower because the measurement principle (volumetric) and the calibration method (prover) are more direct.

### 19.8.3 Prover Systems

A prover is a calibrated reference device used to verify and adjust the K-factor of a fiscal meter in situ. The most common types are:

**Conventional (bidirectional) pipe prover**: A precisely measured volume of pipe (between two detector switches) through which a displacer sphere or piston travels. The meter's pulse count during the known volume displacement gives the K-factor:

$$
K=\frac{N_{\mathrm{pulses}}}{V_{\mathrm{displaced,at\ meter}}}.
$$

Express the calibrated displaced volume and meter indication at the same liquid temperature/pressure basis. Steel expansion and liquid pressure/temperature corrections are applied with their specified numerator/denominator convention; multiplying an arbitrary set of correction factors onto $N/V_{base}$ is not generally valid. Use the applicable API MPMS proving procedure and traceable calibration data.

**Small volume prover (compact prover)**: Uses a precision piston in a smaller volume, requiring higher reproducibility per pass. Typical uncertainty: ±0.02% on prover volume.

**Master meter**: A calibrated reference meter (usually Coriolis or turbine) used to verify the fiscal meter. Requires periodic recalibration against a primary prover.

---

## 19.9 Custody Transfer

### 19.9.1 Definition and Legal Framework

Custody transfer is the point at which ownership of hydrocarbons passes from one party to another. The metering station at this point must satisfy legal metrology requirements, which vary by jurisdiction:

As a current NCS example, the Norwegian Offshore Directorate's measurement regulations, Section 10 Table 1, specify a 0.30% uncertainty limit for net oil quantity delivered or measured over a month. This is a system/measurand requirement, not a universal meter accuracy specification. Determine the relevant measurement type, measurand, coverage convention and applicable exceptions from the current regulation; the UK, US and other jurisdictions require their own review \cite{sodir2023measurement}.

### 19.9.2 Oil Custody Transfer

A typical oil custody transfer metering station includes:

1. **Sampling system** — automatic composite sampler (ISO 3171) collecting a flow-proportional sample for quality determination (API gravity, water content, sulfur, etc.)
2. **Fiscal meter** — turbine or Coriolis meter, calibrated against prover
3. **Prover** — bidirectional pipe prover or compact prover
4. **Ancillary instruments** — temperature transmitters (±0.05 °C), pressure transmitters (±0.025%), densitometer
5. **Flow computer** — real-time calculation of standard volume, mass, and energy from measured variables

The standard (custody transfer) volume is calculated from the observed volume using correction factors:

$$
V_{\text{std}} = V_{\text{obs}} \cdot C_{\text{tl}} \cdot C_{\text{pl}} \cdot C_{\text{sw}}
$$

where $C_{\text{tl}}$ is the temperature correction for the liquid, $C_{\text{pl}}$ is the pressure correction for the liquid, and $C_{\text{sw}}$ is the correction for sediment and water (S&W). The temperature correction uses API/ASTM Tables 54 (volume correction factors for crude oil):

$$
C_{\text{tl}} = \exp\left[-\alpha_T \cdot \Delta T \cdot (1 + 0.8 \cdot \alpha_T \cdot \Delta T)\right]
$$

where $\alpha_T$ is the thermal expansion coefficient of the crude oil and $\Delta T = T_{\text{obs}} - T_{\text{ref}}$.

### 19.9.3 Gas Custody Transfer

Gas custody transfer typically measures energy flow rather than volume:

$$
\dot{E} = Q_v \cdot H_s
$$

where $\dot{E}$ is the energy flow rate, $Q_v$ is the standard volume flow rate, and $H_s$ is the superior calorific value (from ISO 6976 or GPA 2172). Gas composition is measured by online gas chromatograph (GC) per ISO 6974, typically with C6+ analysis updated every 3–5 minutes.

---

## 19.10 Allocation Metering

### 19.10.1 Purpose

Allocation metering distributes the total measured production (at the fiscal meter) back to individual contributing fields, wells, or license owners. Unlike fiscal metering, which directly determines revenue, allocation metering determines each party's share of the total:

$$
f_i = \frac{Q_{\text{alloc},i}}{\sum_{j=1}^{N} Q_{\text{alloc},j}}
$$

where $f_i$ is the allocation factor for stream $i$ and $Q_{\text{alloc},i}$ is the measured or calculated contribution of stream $i$.

### 19.10.2 Well-Stream Allocation Methods

Several allocation methods are used, depending on the complexity of the commingling arrangement:

1. **Direct measurement**: Each well or satellite has a dedicated meter; the fiscal total is allocated in proportion to the measured rates
2. **Periodic well testing**: Flow rates are measured periodically (e.g., monthly) using a test separator; allocation factors are updated after each test
3. **Virtual metering**: Flow rates are estimated from pressure, temperature, and choke position using well models; the estimates are reconciled against the fiscal total
4. **Tracer-based**: Chemical tracers injected into individual wells allow back-allocation from commingled measurements

### 19.10.3 Uncertainty in Allocation

Allocation uncertainty is typically much higher than fiscal uncertainty — often ±2% to ±5% per stream. The uncertainty in each party's share depends on:

- The number of streams being allocated
- The accuracy of individual allocation meters
- The frequency and quality of well tests
- The variability of production rates between tests

The reconciliation equation ensures that all allocated volumes sum to the fiscal total:

$$
\sum_{i=1}^{N} Q_{\text{alloc},i} = Q_{\text{fiscal}} \quad (\text{exact, by definition})
$$

Any discrepancy between the sum of allocation meters and the fiscal meter is distributed among the parties, typically in proportion to their allocated volumes.

---

## 19.11 Flare and Vent Measurement

### 19.11.1 Purpose and Regulatory Drivers

Accurate measurement of flare and vent gas is increasingly important due to:

- **Emissions reporting**: CO₂ equivalents from flare combustion and uncombusted methane must be reported under greenhouse gas regulations
- **Carbon tax**: In jurisdictions with carbon pricing (e.g., Norway's CO₂ tax), flare gas represents a direct cost
- **Flare consent**: Many regulators require justification for flaring above minimum levels
- **Production accounting**: Flare gas must be included in the hydrocarbon balance for allocation

### 19.11.2 Measurement Technologies

Flare gas measurement presents unique challenges: highly variable flow (turndown > 1,000:1), variable composition (process upsets change the gas quality), and high temperatures.

| Technology | Principle | Rangeability | Accuracy |
|-----------|-----------|-------------|----------|
| Ultrasonic (transit time) | Velocity from $\Delta t$ | 1,000:1+ | ±2–5% |
| Thermal mass | Heat dissipation | 100:1 | ±2–5% |
| Averaging pitot tube | $\Delta P$ | 10:1 | ±3–10% |
| Optical (laser) | Scintillation | 100:1 | ±5–10% |

Ultrasonic meters are the dominant technology for flare measurement due to their extreme rangeability and ability to operate in the hostile flare stack environment. A three-path ultrasonic meter with speed of sound correction provides both flow velocity and a composition indicator.

### 19.11.3 Emissions Calculation from Flare Measurement

The CO₂ emission from flaring is calculated from the measured volumetric flow rate, composition, and combustion stoichiometry:

$$
\dot{m}_{\text{CO}_2} = Q_{\text{flare}} \cdot \sum_{i} x_i \cdot n_{c,i} \cdot \frac{M_{\text{CO}_2}}{V_m^{\circ}}
$$

This equation assumes complete conversion of hydrocarbon carbon to CO₂ and a consistent gas molar-volume basis. Include inlet CO₂ separately when reporting total emitted CO₂, and quantify unburned methane and incomplete combustion separately for greenhouse-gas reporting. Use $M_{CO_2}=0.04401$ kg/mol when the desired output is kg per unit time. Here $Q_{\text{flare}}$ is the standard volumetric flow rate of flare gas, $x_i$ is the mole fraction of each hydrocarbon component, $n_{c,i}$ is the number of carbon atoms in component $i$, $M_{\text{CO}_2} = 44.01$ g/mol, and $V_m^{\circ}$ is the molar volume at standard conditions.

---

## 19.12 NeqSim Export Pipeline Modeling

### 19.12.1 Pipeline Pressure Drop

NeqSim can model gas export pipeline pressure drop using the `PipeBeggsAndBrills` class, which accounts for single-phase gas friction and (if liquid is present) two-phase flow correlations:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define export gas
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 40.0, 150.0)
gas.addComponent("nitrogen", 0.008)
gas.addComponent("CO2", 0.015)
gas.addComponent("methane", 0.890)
gas.addComponent("ethane", 0.055)
gas.addComponent("propane", 0.018)
gas.addComponent("i-butane", 0.004)
gas.addComponent("n-butane", 0.005)
gas.addComponent("i-pentane", 0.002)
gas.addComponent("n-pentane", 0.001)
gas.addComponent("n-hexane", 0.002)
gas.setMixingRule("classic")

# Create a stream for the export gas
feed = jneqsim.process.equipment.stream.Stream("Export Gas", gas)
feed.setFlowRate(10.0, "MSm3/day")
feed.setTemperature(40.0, "C")
feed.setPressure(150.0, "bara")

# Create export pipeline
pipeline = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills(
    "Export Pipeline", feed
)
pipeline.setPipeWallRoughness(5e-6)        # 5 micron (internal coated)
pipeline.setLength(200000.0)                   # 200 km
pipeline.setDiameter(0.7366)               # ~30 inch ID (m)
pipeline.setAngle(0.0)                      # horizontal
pipeline.setNumberOfIncrements(50)          # segments for calculation

# Build and run process system
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(pipeline)
process.run()

# Get outlet conditions
outlet = pipeline.getOutletStream()
P_out = outlet.getPressure("bara")
T_out = outlet.getTemperature("C")
dP = feed.getPressure("bara") - P_out

print("=== Export Pipeline Results ===")
print(f"Inlet:  {feed.getPressure('bara'):.1f} bara, "
      f"{feed.getTemperature('C'):.1f} °C")
print(f"Outlet: {P_out:.1f} bara, {T_out:.1f} °C")
print(f"Pressure drop: {dP:.1f} bar over 200 km")
print(f"Specific dP: {dP/200:.2f} bar/km")
```

### 19.12.2 Pipeline Sizing Study

A common engineering task is to determine the required pipeline diameter for a given flow rate and allowable pressure drop. The following example performs a parametric study:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Pipeline sizing study: vary diameter
diameters_inch = [24, 28, 30, 32, 36, 40, 42]

print(f"{'ID (inch)':>10} {'ID (m)':>10} {'dP (bar)':>10} "
      f"{'v (m/s)':>10} {'Arrival P':>12}")
print("-" * 54)

for d_inch in diameters_inch:
    d_m = d_inch * 0.0254  # convert to meters

    gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 40.0, 150.0)
    gas.addComponent("nitrogen", 0.008)
    gas.addComponent("CO2", 0.015)
    gas.addComponent("methane", 0.890)
    gas.addComponent("ethane", 0.055)
    gas.addComponent("propane", 0.018)
    gas.addComponent("n-butane", 0.009)
    gas.addComponent("i-pentane", 0.002)
    gas.addComponent("n-pentane", 0.001)
    gas.addComponent("n-hexane", 0.002)
    gas.setMixingRule("classic")

    feed = jneqsim.process.equipment.stream.Stream("Feed", gas)
    feed.setFlowRate(15.0, "MSm3/day")
    feed.setTemperature(40.0, "C")
    feed.setPressure(150.0, "bara")

    pipe = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills(
        "Pipe", feed
    )
    pipe.setPipeWallRoughness(5e-6)
    pipe.setLength(300000.0)
    pipe.setDiameter(d_m)
    pipe.setAngle(0.0)
    pipe.setNumberOfIncrements(50)

    process = jneqsim.process.processmodel.ProcessSystem()
    process.add(feed)
    process.add(pipe)
    process.run()

    outlet = pipe.getOutletStream()
    P_out = outlet.getPressure("bara")
    dP = 150.0 - P_out

    # Estimate gas velocity at inlet
    rho_gas = feed.getFluid().getPhase("gas").getDensity("kg/m3")
    mass_flow = feed.getFlowRate("kg/hr") / 3600.0  # kg/s
    area = 3.14159 * (d_m / 2) ** 2
    v_gas = mass_flow / (rho_gas * area)

    print(f"{d_inch:>10d} {d_m:>10.4f} {dP:>10.1f} "
          f"{v_gas:>10.1f} {P_out:>12.1f}")
```

**Design guideline**: Gas pipeline velocities should typically be kept below 15–20 m/s to limit erosion and noise. The pressure drop should be balanced against the cost of compression — the most economic diameter minimizes the total lifecycle cost (pipeline CAPEX + compressor CAPEX + compressor OPEX).

![Pipeline sizing study: pressure drop vs. diameter for 15 MSm³/d over 300 km](figures/pipeline_sizing_dp_vs_diameter.png)

### 19.12.3 Integrated Export Compression and Pipeline Model

The following example models export compression followed by pipeline transport, demonstrating how to connect equipment in NeqSim:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define processed gas from the platform
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 35.0, 80.0)
gas.addComponent("nitrogen", 0.008)
gas.addComponent("CO2", 0.015)
gas.addComponent("methane", 0.890)
gas.addComponent("ethane", 0.055)
gas.addComponent("propane", 0.018)
gas.addComponent("n-butane", 0.009)
gas.addComponent("n-pentane", 0.003)
gas.addComponent("n-hexane", 0.002)
gas.setMixingRule("classic")

# Feed stream (from gas processing)
feed = jneqsim.process.equipment.stream.Stream("Platform Gas", gas)
feed.setFlowRate(12.0, "MSm3/day")
feed.setTemperature(35.0, "C")
feed.setPressure(80.0, "bara")

# Export compressor
compressor = jneqsim.process.equipment.compressor.Compressor(
    "Export Compressor", feed
)
compressor.setOutletPressure(170.0, "bara")
compressor.setPolytropicEfficiency(0.80)
compressor.setUsePolytropicCalc(True)

# After-cooler (cool compressed gas before pipeline)
cooler = jneqsim.process.equipment.heatexchanger.Cooler(
    "Export Cooler", compressor.getOutletStream()
)
cooler.setOutTemperature(273.15 + 40.0)

# Export pipeline
pipeline = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills(
    "Export Pipeline", cooler.getOutletStream()
)
pipeline.setPipeWallRoughness(5e-6)
pipeline.setLength(250000.0)
pipeline.setDiameter(0.762)  # 30-inch
pipeline.setAngle(0.0)
pipeline.setNumberOfIncrements(50)

# Build process
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(compressor)
process.add(cooler)
process.add(pipeline)
process.run()

# Report results
print("=== Export System Results ===")
print(f"Compressor suction:   {feed.getPressure('bara'):.1f} bara, "
      f"{feed.getTemperature('C'):.1f} °C")

comp_out = compressor.getOutletStream()
print(f"Compressor discharge: {comp_out.getPressure('bara'):.1f} bara, "
      f"{comp_out.getTemperature('C'):.1f} °C")
print(f"Compressor power:     {compressor.getPower('MW'):.2f} MW")

cool_out = cooler.getOutletStream()
print(f"After cooler outlet:  {cool_out.getPressure('bara'):.1f} bara, "
      f"{cool_out.getTemperature('C'):.1f} °C")

pipe_out = pipeline.getOutletStream()
print(f"Pipeline arrival:     {pipe_out.getPressure('bara'):.1f} bara, "
      f"{pipe_out.getTemperature('C'):.1f} °C")
print(f"Pipeline dP:          "
      f"{cool_out.getPressure('bara') - pipe_out.getPressure('bara'):.1f} bar")
```

---

## 19.13 Gas Sales Contracts and Quality Management

### 19.13.1 Contract Structure

A typical gas sales agreement (GSA) includes:

- **Annual Contracted Quantity (ACQ)**: The total volume to be delivered per contract year
- **Daily Contracted Quantity (DCQ)**: The nominated daily delivery quantity
- **Flexibility**: Upward (typically 110–120% DCQ) and downward (typically 70–90% DCQ) flexibility bands
- **Take-or-pay**: Buyer pays for a minimum quantity (typically 80–90% ACQ) whether taken or not
- **Quality specifications**: The quality window (heating value, Wobbe, dew points, contaminants) that the gas must satisfy
- **Penalties/adjustments**: Price adjustments for out-of-specification gas; right to reject non-conforming gas

### 19.13.2 Gas Quality Management

Maintaining gas quality within the contractual window requires coordination between upstream processing and export compression:

1. **NGL extraction depth**: Controls the heating value and HC dew point; deeper extraction produces leaner gas (lower GCV, lower HC dew point)
2. **Dehydration performance**: Controls the water dew point; TEG dehydration typically achieves −15 to −25 °C water dew point
3. **Acid gas removal**: Controls H₂S and CO₂ content; amine treating targets < 4 ppm H₂S and < 2.5% CO₂
4. **Inert content**: N₂ content affects heating value and Wobbe index; high N₂ reduces GCV

NeqSim's sales contract framework (`neqsim.standards.salescontract`) enables automated checking of gas quality against contractual specifications:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define export gas
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 15.0, 1.01325)
gas.addComponent("nitrogen", 0.008)
gas.addComponent("CO2", 0.015)
gas.addComponent("methane", 0.890)
gas.addComponent("ethane", 0.055)
gas.addComponent("propane", 0.018)
gas.addComponent("i-butane", 0.004)
gas.addComponent("n-butane", 0.005)
gas.addComponent("i-pentane", 0.002)
gas.addComponent("n-pentane", 0.001)
gas.addComponent("n-hexane", 0.002)
gas.setMixingRule("classic")

# Create the ISO 6976 standard for gas quality
iso6976 = jneqsim.standards.gasquality.Standard_ISO6976_2016(
    gas, 15, 25, "volume"
)
iso6976.calculate()

# Check against typical NCS specifications
gcv = iso6976.getValue("SuperiorCalorificValue") / 1000.0
wobbe = iso6976.getValue("SuperiorWobbeIndex") / 1000.0

print("=== Gas Quality vs. Specification ===")
print(f"{'Parameter':<35} {'Value':>10} {'Min':>8} {'Max':>8} {'Status':>8}")
print("-" * 71)

# GCV check
gcv_min, gcv_max = 36.0, 44.0
gcv_status = "PASS" if gcv_min <= gcv <= gcv_max else "FAIL"
print(f"{'GCV (MJ/Sm³)':<35} {gcv:>10.2f} {gcv_min:>8.1f} "
      f"{gcv_max:>8.1f} {gcv_status:>8}")

# Wobbe index check
wi_min, wi_max = 46.5, 54.0
wi_status = "PASS" if wi_min <= wobbe <= wi_max else "FAIL"
print(f"{'Wobbe Index (MJ/Sm³)':<35} {wobbe:>10.2f} {wi_min:>8.1f} "
      f"{wi_max:>8.1f} {wi_status:>8}")

# CO2 check
co2_pct = 0.015 * 100
co2_max = 2.5
co2_status = "PASS" if co2_pct <= co2_max else "FAIL"
print(f"{'CO2 (mol%)':<35} {co2_pct:>10.2f} {'—':>8} "
      f"{co2_max:>8.1f} {co2_status:>8}")
```

---


<!-- reviewed-notebook-results:start -->
## Reproduced Calculation Results

These examples use the stated fluid recipes and operating assumptions. Curves represent NeqSim calculations unless a caption identifies an analytical illustration, assumed equipment map or synthetic data.

![Gas Export Pipeline: Pressure Profile](figures/ch17_pipeline_profiles.png)

Pressure spans 177.2–180 bara across the plotted cases. Temperature spans 3.978–40 C across the plotted cases.

Friction reduces pressure along the line, while the specified surroundings remove sensible heat. The small pressure loss in this case does not imply a large thermal margin: the outlet approaches the ambient temperature. Evaluate low-rate and shutdown thermal conditions separately before choosing insulation or inhibition.

![Pressure Drop vs Pipeline Diameter (150 km, 5 MSm3/day)](figures/ch17_diameter_sensitivity.png)

Total Pressure Drop spans 0.2295–8.012 bar across the plotted cases. Arrival Pressure spans 172–179.8 bara across the plotted cases.

Increasing diameter reduces phase velocity and friction for the fixed export rate. The hydraulic benefit diminishes as the pressure loss becomes small compared with the available pressure. Compare the incremental pressure saving with pipe and installation cost on the same route basis.

Selected numerical ranges from the plotted cases:

| Quantity / series | Minimum | Maximum | Unit |
|---|---:|---:|---|
| Pressure | 177.2 | 180 | bara |
| Total Pressure Drop | 0.2295 | 8.012 | bar |

Ranges describe the sampled cases; they are not independent validation tolerances.
<!-- reviewed-notebook-results:end -->

## Summary

This chapter covered the design, operation, and measurement of export systems for oil and gas production:

- **Gas export systems** — pipeline sizing uses the Panhandle equations or detailed simulators; export compression delivers gas at the contractual pipeline inlet pressure; gas quality specifications (GCV, Wobbe, water dew point, HC dew point) determine the required processing depth
- **Oil export** — pipeline or shuttle tanker, constrained by vapor pressure (RVP), pour point, and cargo scheduling; FPSO operations add storage management complexity
- **LNG** — liquefaction at −162 °C reduces volume by 600×; extremely tight CO₂ (< 50 ppm), water (< 1 ppm), and mercury (< 10 ng/Sm³) specifications
- **Gas quality calculations (ISO 6976)** — calorific value, density, and Wobbe index calculated from composition using tabulated pure-component values with compressibility corrections; reference conditions (combustion temperature, volume temperature) must always be stated
- **Dew points** — water dew point depends on water content and is calculated using CPA; HC dew point and cricondentherm are strongly sensitive to the heavy-end composition and is calculated from the phase envelope
- **Fiscal metering** — ultrasonic (no pressure drop, excellent diagnostics), orifice (mature standards, limited rangeability), Coriolis (direct mass, simultaneous density), and turbine (high liquid accuracy, moving parts); selection depends on fluid, accuracy requirement, and operating range
- **Measurement uncertainty** — analyzed per ISO/GUM; orifice meters are dominated by discharge coefficient uncertainty; prover systems provide traceable calibration of fiscal meters
- **Custody transfer** — the legal point of ownership change; oil requires volume correction to standard conditions with sampler-derived quality; gas is typically transacted on an energy basis using ISO 6976 and online GC
- **Allocation metering** — distributes fiscal totals to individual contributors; lower accuracy than fiscal but critical for equitable revenue distribution
- **Flare and vent measurement** — ultrasonic meters dominate due to extreme turndown requirements; emissions calculations link flare gas composition to CO₂ equivalents
- **NeqSim modeling** — ISO 6976 gas quality via `Standard_ISO6976_2016`, water dew point via `waterDewPointTemperatureFlash()`, HC dew point via phase envelope (`calcPTphaseEnvelope`), and pipeline hydraulics via `PipeBeggsAndBrills`

---


<!-- September 2026 source update -->
## Export calculations need an explicit basis

An export decision joins three different models: thermodynamic quality, pipeline hydraulics, and contractual acceptance. Preserve the composition, volume-reference temperature and pressure, combustion-reference temperature, pressure datum, and applicable contractual period with each result. `Standard_ISO6976_2016` uses a volume-reference basis for its gas-quality calculation; the explicit kJ-to-MJ conversion in this chapter is essential when comparing with a specification in MJ/Sm³. An operating-pressure compressibility factor is a separate metering correction.

`PipeBeggsAndBrills.setLength()` takes metres. Thus a 200 km export line is entered as 200000.0, and a 250 km line as 250000.0. A simulation can converge with an incorrect length and still produce a misleadingly small pressure loss. Dimensional checks belong alongside convergence checks.

The current `PlantPipelineEvidence` adapter freezes one completed Beggs–Brill profile with six explicitly declared limits: maximum absolute pressure, pressure drop, minimum receiving pressure, maximum mixture superficial velocity, and minimum/maximum bulk temperature. It also retains the profile-node location of the controlling value. This adapter requires verified geometry provenance, current calculation identity, finite profile values, and complete convergence. It does not certify hydrate, wax, erosion, acoustic vibration, slugging or transient envelopes. Those remain separate calculations and operating restrictions \cite{neqsim2026update}.

The practical outcome is a traceable export constraint: “receiving pressure below its declared lower limit at the current solved flow” is actionable evidence. “Pipeline utilization is 95%” without the controlling physical quantity, limit and basis is insufficient.

---

## Exercises

**Exercise 19.1 — Gas Quality Calculation**
A natural gas has the following composition (mol%): N₂ = 1.5, CO₂ = 2.0, CH₄ = 86.0, C₂H₆ = 6.0, C₃H₈ = 2.5, i-C₄ = 0.5, n-C₄ = 0.8, i-C₅ = 0.3, n-C₅ = 0.2, n-C₆ = 0.2. Using NeqSim's ISO 6976:2016 implementation, calculate: (a) The GCV and NCV at reference conditions 15 °C (volume), 25 °C (combustion). (b) The superior Wobbe index. (c) The relative density. (d) Does this gas meet the assumed contract-A window (GCV 36–44 MJ/Sm³, Wobbe 46.5–54.0 MJ/Sm³)?

**Exercise 19.2 — NGL Extraction Depth Study**
Starting from the composition in Exercise 19.1, simulate the effect of removing propane-plus (C₃+) components. For C₃+ removal levels of 0%, 20%, 40%, 60%, 80%, and 95%: (a) Recalculate the normalized composition. (b) Calculate GCV and Wobbe index using NeqSim. (c) Plot GCV and Wobbe versus C₃+ removal percentage. (d) At what removal level does the gas fall below a GCV of 37 MJ/Sm³? (e) Discuss the trade-off between NGL revenue and gas quality compliance.

**Exercise 19.3 — Water Dew Point Specification**
An export gas has 30 ppm (mole) water content at 70 bara. Using NeqSim with the CPA equation of state: (a) Calculate the water dew point temperature. (b) If the contractual specification is −18 °C at delivery pressure of 70 bara, does this gas comply? (c) What maximum water content (ppm) would meet the −18 °C specification? (Hint: iterate on water content.) (d) If the gas is dehydrated to 10 ppm water, what is the new water dew point at 70 bara?

**Exercise 19.4 — Hydrocarbon Dew Point Sensitivity**
Using NeqSim, calculate the phase envelope and cricondentherm for the gas in Exercise 19.1 with three different C7+ characterizations: (a) 0.1 mol% n-C₇ only; (b) 0.1 mol% n-C₇ + 0.05 mol% n-C₈; (c) 0.1 mol% n-C₇ + 0.05 mol% n-C₈ + 0.02 mol% n-C₉. For each case, report the cricondentherm and the pressure at which it occurs. Discuss the sensitivity of HC dew point to the heavy-end characterization and the implications for gas chromatograph analysis requirements.

**Exercise 19.5 — Export Pipeline Sizing**
Design a 250 km gas export pipeline to transport 20 MSm³/day of natural gas (composition from Exercise 19.1) with an inlet pressure of 160 bara and a minimum arrival pressure of 90 bara at the receiving terminal. Using NeqSim's `PipeBeggsAndBrills` class: (a) Determine the minimum pipeline internal diameter (from the set: 28, 30, 32, 36, 40, 42 inches). (b) For the selected diameter, calculate the gas velocity at the inlet. (c) Estimate the compressor power required to boost the gas from 80 bara (platform conditions) to the pipeline inlet pressure.

**Exercise 19.6 — Metering Uncertainty Analysis**
An orifice plate fiscal metering station has the following individual uncertainties: $\Delta P$ transmitter ±0.1%, static pressure transmitter ±0.05%, temperature transmitter ±0.1%, orifice bore ±0.03%, pipe diameter ±0.04%, discharge coefficient ±0.5%. Treat these as independent one-standard-deviation relative uncertainties at a diameter ratio of 0.60; ignore composition uncertainty for this exercise and state the fixed-coefficient approximation. (a) Calculate the combined standard uncertainty in mass flow rate using the sensitivity coefficients from Section 19.8.2. (b) Calculate the expanded uncertainty at 95% confidence (k = 2). (c) If the annual gas sales volume is 5 billion Sm³ and the gas price is 2.0 NOK/Sm³, what is the financial exposure (in MNOK) corresponding to the measurement uncertainty? (d) If an ultrasonic meter with ±0.5% uncertainty replaces the orifice, what is the change in financial exposure?

---

## References

1. ISO 6976:2016. *Natural Gas — Calculation of Calorific Values, Density, Relative Density and Wobbe Indices from Composition*. International Organization for Standardization.
2. ISO 5167-2:2003. *Measurement of Fluid Flow — Pressure Differential Devices — Part 2: Orifice Plates*. International Organization for Standardization.
3. AGA Report No. 3 (2012). *Orifice Metering of Natural Gas and Other Related Hydrocarbon Fluids*, 4th Edition. American Gas Association.
4. AGA Report No. 9 (2007). *Measurement of Gas by Multipath Ultrasonic Meters*, 2nd Edition. American Gas Association.
5. ISO 10790:2015. *Measurement of Fluid Flow in Closed Conduits — Guidance to the Selection, Installation and Use of Coriolis Meters*. International Organization for Standardization.
6. API MPMS (Manual of Petroleum Measurement Standards). American Petroleum Institute. Chapters 4 (Proving), 5 (Metering), 7 (Temperature), 11 (Physical Properties).
7. NORSOK I-104 (2005). *Fiscal Measurement Systems for Hydrocarbon Liquid and Gas*. Standards Norway.
8. ISO/GUM (2008). *Guide to the Expression of Uncertainty in Measurement*. JCGM 100:2008.
9. Mokhatab, S., Poe, W. A., and Mak, J. Y. (2019). *Handbook of Natural Gas Transmission and Processing*, 4th Edition. Gulf Professional Publishing.
10. Campbell, J. M. (2014). *Gas Conditioning and Processing*, Volume 2: The Equipment Modules, 9th Edition. Campbell Petroleum Series.
11. Kidnay, A. J., Parrish, W. R., and McCartney, D. G. (2011). *Fundamentals of Natural Gas Processing*, 2nd Edition. CRC Press.
12. GPSA Engineering Data Book (2017). 14th Edition, Gas Processors Suppliers Association.
13. ISO 6974 (2012). *Natural Gas — Determination of Composition and Associated Uncertainty by Gas Chromatography*. International Organization for Standardization.
14. ISO 3171 (1988). *Petroleum Liquids — Automatic Pipeline Sampling*. International Organization for Standardization.
15. API RP 86 (2005). *API Recommended Practice for Measurement of Multiphase Flow*. American Petroleum Institute.
16. Husain, Z. D. (2010). "Theoretical uncertainty of orifice flow measurement." *Proceedings of FLOMEKO*, Paper 245.


