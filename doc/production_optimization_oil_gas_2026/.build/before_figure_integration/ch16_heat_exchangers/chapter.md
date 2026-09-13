# Heat Exchangers and Thermal Design

**Running the examples.** Start the source-workspace Python session described in Chapter 1, then run this chapter's Python blocks in reading order. Java blocks form a separate sequence using the same NeqSim build; carry forward objects from preceding Java blocks. The release execution records are in `verification/`; a successful run establishes API compatibility, while physical validation also requires the checks discussed in the text.

<!-- Chapter metadata -->
<!-- Notebooks: ch14_heat_exchanger_design.ipynb, ch14_pinch_analysis.ipynb -->
<!-- Estimated pages: 25 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Identify the principal heat exchanger types used in oil and gas production facilities and select the appropriate type for a given service
2. Apply heat transfer fundamentals — conduction, convection, overall heat transfer coefficient, and fouling factors — to exchanger design
3. Size heat exchangers using both the LMTD and effectiveness-NTU methods
4. Describe shell-and-tube exchanger geometry (tube layout, baffles, passes) and apply the Bell-Delaware method for shell-side heat transfer
5. Design air-cooled heat exchangers including fan sizing and ambient temperature correction
6. Perform heat integration and pinch analysis to minimize utility consumption
7. Model heat exchangers in NeqSim using the `HeatExchanger`, `Heater`, `Cooler`, and `PinchAnalysis` classes

---

## 16.1 Introduction

Heat exchangers are among the most numerous and critical pieces of equipment in any oil and gas production facility. On a typical offshore platform, 30–50% of equipment items by count are heat exchangers or coolers. They appear in virtually every processing stage: cooling the wellstream before separation, heating crude oil for stabilization, condensing overhead gas in distillation, cooling compressed gas before export, and recovering waste heat from turbine exhaust.

The fundamental purpose of a heat exchanger is to transfer thermal energy between two fluid streams without mixing them. The driving force for this transfer is the temperature difference between the streams. The design challenge is to achieve the required heat duty at an acceptable pressure drop, within a physically realizable and economically viable equipment size.

In the context of production optimization, heat exchangers play several critical roles:

- **Separation efficiency** — inlet cooling or heating directly affects the vapor–liquid split in separators
- **Compressor performance** — interstage and aftercooling temperature determines compressor power and whether gas meets export dewpoint
- **Export specifications** — gas dewpoint, oil RVP, and water content all depend on temperatures set by heat exchangers
- **Energy efficiency** — heat recovery reduces fuel gas consumption, emissions, and operating costs
- **Flow assurance** — maintaining temperatures above hydrate and wax appearance thresholds

This chapter covers the fundamental theory of heat transfer in exchangers, the principal exchanger types encountered in oil and gas, design methods (LMTD and effectiveness-NTU), and practical application using NeqSim's heat exchanger classes.

---

## 16.2 Heat Exchanger Types in Oil and Gas

### 16.2.1 Shell-and-Tube Heat Exchangers

Shell-and-tube exchangers are the workhorse of the process industry and the most common type in oil and gas facilities. They consist of a bundle of tubes enclosed within a cylindrical shell. One fluid flows through the tubes (tube side), while the other flows over the outside of the tubes within the shell (shell side).

The Tubular Exchanger Manufacturers Association (TEMA) classifies shell-and-tube exchangers using a three-letter designation system:

| Position | Designation | Description |
|----------|------------|-------------|
| Front end | B | Bonnet (integral cover) |
| Front end | A | Channel and removable cover |
| Shell type | E | One-pass shell |
| Shell type | F | Two-pass shell with longitudinal baffle |
| Shell type | J | Divided flow |
| Shell type | X | Cross flow |
| Rear end | M | Fixed tubesheet |
| Rear end | U | U-tube bundle |
| Rear end | S | Floating head with backing device |

For example, a BEM exchanger has a bonnet front end, single-pass shell, and fixed tubesheet. A BEU has a U-tube bundle, which allows differential thermal expansion and is common in high-temperature services.

TEMA also defines three classes of mechanical standards:

| TEMA Class | Service | Design Pressure |
|-----------|---------|----------------|
| R | Petroleum and heavy-duty | Up to 200 bar |
| C | General commercial | Moderate |
| B | Chemical service | Standard |

Most oil and gas exchangers are designed to TEMA R standards.

![Shell-and-tube heat exchanger with single segmental baffles (TEMA BEM type)](figures/shell_tube_hx_cross_section.png)

### 16.2.2 Plate and Frame Heat Exchangers

Plate heat exchangers use a series of corrugated metal plates held together in a frame. The fluids flow in alternating channels between the plates, creating a large surface area in a compact volume. Advantages include:

- **High thermal efficiency** — the corrugated plates promote turbulence, giving heat transfer coefficients 3–5 times those of shell-and-tube
- **Compact footprint** — important for offshore platforms where deck space is limited
- **Easy maintenance** — plates can be added or removed to change capacity

Limitations include lower design pressure (typically < 25 bar) and temperature (< 200 °C), and unsuitability for highly fouling or viscous fluids. In oil and gas, plate exchangers are used for glycol cooling, seawater systems, and produced water cooling.

### 16.2.3 Printed Circuit Heat Exchangers (PCHE)

Printed circuit heat exchangers (also called diffusion-bonded exchangers) use chemically etched flow channels in flat metal plates that are diffusion-bonded into a monolithic block. They offer:

- **Extreme compactness** — surface area densities of 1000–2500 m²/m³ (vs. 50–100 for shell-and-tube)
- **High-pressure capability** — up to 600 bar or more
- **Multi-stream capability** — can handle 3–12 streams in a single unit

PCHEs are widely used in LNG plants for cryogenic service (cold boxes) and increasingly in CO₂ transport and compression applications. Their main limitation is that they cannot be mechanically cleaned, so they require clean fluids.

### 16.2.4 Air-Cooled Heat Exchangers (Fin-Fan Coolers)

Air-cooled heat exchangers use ambient air blown across finned tube bundles by fans. They are essential where cooling water is unavailable or its use would create environmental problems. In oil and gas:

- **Onshore plants** — often use air coolers exclusively
- **Offshore platforms** — use air coolers for compressor aftercooling, gas dehydration, and produced water
- **Arctic environments** — ambient temperature can drop below −40 °C, requiring winterization measures

Key design parameters include:

| Parameter | Typical Range |
|-----------|--------------|
| Face velocity | 2.5–4.5 m/s |
| Number of tube rows | 3–8 |
| Fin density | 275–433 fins/m |
| Fan diameter | 1.5–5.5 m |
| Bundle width | 2.4–3.6 m |

Two fan configurations are used:

- **Forced draft** — fans below the bundle push air upward through the tubes. Easier maintenance, but hot air can recirculate.
- **Induced draft** — fans above the bundle pull air through. Better air distribution, less recirculation, but fans operate in hot air.

### 16.2.5 Double-Pipe Heat Exchangers

Double-pipe (hairpin) exchangers consist of one pipe inside another. The inner pipe carries one fluid, the annulus carries the other. They are simple, inexpensive, and used for:

- Small duties (< 500 kW)
- High-pressure applications
- Services with large temperature crosses

In oil and gas, double-pipe exchangers appear as sample coolers, small lube oil coolers, and chemical injection preheaters.

---

## 16.3 Heat Transfer Fundamentals

### 16.3.1 Modes of Heat Transfer

Heat transfer in exchangers involves three modes:

**Conduction** through the tube wall follows Fourier's law:

$$
q = -k A \frac{dT}{dx}
$$

where $k$ is the thermal conductivity of the tube material (W/(m·K)), $A$ is the cross-sectional area, and $dT/dx$ is the temperature gradient.

**Convection** between a fluid and a solid surface follows Newton's law of cooling:

$$
q = h A (T_s - T_f)
$$

where $h$ is the convective heat transfer coefficient (W/(m²·K)), $T_s$ is the surface temperature, and $T_f$ is the bulk fluid temperature.

**Radiation** is generally negligible inside heat exchangers at process temperatures, but becomes significant in fired heaters and flare systems.

### 16.3.2 Overall Heat Transfer Coefficient

The overall heat transfer coefficient $U$ combines all resistances to heat transfer in series. For a cylindrical tube:

$$
\frac{1}{U_o A_o} = \frac{1}{h_i A_i} + \frac{R_{f,i}}{A_i} + \frac{\ln(d_o/d_i)}{2\pi k_w L} + \frac{R_{f,o}}{A_o} + \frac{1}{h_o A_o}
$$

where:
- $h_i$, $h_o$ = inside and outside convective heat transfer coefficients
- $R_{f,i}$, $R_{f,o}$ = inside and outside fouling resistances (m²·K/W)
- $d_i$, $d_o$ = inside and outside tube diameters
- $k_w$ = tube wall thermal conductivity
- $L$ = tube length

For thin-walled tubes, the simplified form based on the outside area is:

$$
\frac{1}{U_o} = \frac{1}{h_o} + R_{f,o} + \frac{d_o \ln(d_o/d_i)}{2 k_w} + \frac{d_o}{d_i}\left(\frac{1}{h_i} + R_{f,i}\right)
$$

Typical overall heat transfer coefficients for oil and gas services:

| Service | $U$ (W/(m²·K)) |
|---------|----------------|
| Gas–gas | 50–150 |
| Gas–liquid (hydrocarbon) | 150–400 |
| Liquid–liquid (hydrocarbon) | 200–600 |
| Water–hydrocarbon liquid | 300–900 |
| Condensing steam–liquid | 500–2000 |
| Boiling–condensing | 600–1500 |

### 16.3.3 Fouling Factors

Fouling is the accumulation of unwanted material on heat transfer surfaces. In oil and gas, common fouling mechanisms include:

- **Scaling** — mineral deposits (CaCO₃, BaSO₄) from produced water
- **Corrosion fouling** — oxide layers from CO₂ or H₂S attack
- **Biological fouling** — algae and biofilm in seawater systems
- **Particulate fouling** — sand, wax, and asphaltene deposits
- **Chemical reaction** — polymerization of heavy hydrocarbons at high temperatures

TEMA recommends minimum fouling resistances:

| Fluid | $R_f$ (m²·K/W) |
|-------|----------------|
| Treated cooling water | 0.000176 |
| Seawater (< 50 °C) | 0.000088 |
| Crude oil (< 200 °C) | 0.000352 |
| Heavy fuel oil | 0.000528 |
| Natural gas | 0.000088–0.000176 |
| Compressed air | 0.000176 |

Fouling reduces the effective heat transfer coefficient and increases pressure drop. The cleanliness factor is defined as:

$$
CF = \frac{U_{\text{actual}}}{U_{\text{clean}}}
$$

A cleanliness factor below 0.7 typically triggers a cleaning campaign.

---

## 16.4 The LMTD Method

### 16.4.1 Derivation and Formulation

The Log Mean Temperature Difference (LMTD) method is the foundation of heat exchanger design. The heat duty is:

$$
Q = U A F \cdot \Delta T_{\text{LMTD}}
$$

where $F$ is the LMTD correction factor for multi-pass arrangements. The LMTD for a counterflow exchanger is:

$$
\Delta T_{\text{LMTD}} = \frac{\Delta T_1 - \Delta T_2}{\ln(\Delta T_1 / \Delta T_2)}
$$

where $\Delta T_1$ and $\Delta T_2$ are the temperature differences at each end of the exchanger:

- Counterflow: $\Delta T_1 = T_{h,\text{in}} - T_{c,\text{out}}$, $\Delta T_2 = T_{h,\text{out}} - T_{c,\text{in}}$
- Parallel flow: $\Delta T_1 = T_{h,\text{in}} - T_{c,\text{in}}$, $\Delta T_2 = T_{h,\text{out}} - T_{c,\text{out}}$

When $\Delta T_1 = \Delta T_2$, the LMTD reduces to the arithmetic mean: $\Delta T_{\text{LMTD}} = \Delta T_1 = \Delta T_2$.

### 16.4.2 LMTD Correction Factor

For shell-and-tube exchangers with multiple tube passes and one shell pass (TEMA E shell), the correction factor $F$ depends on two dimensionless parameters:

$$
R = \frac{T_{h,\text{in}} - T_{h,\text{out}}}{T_{c,\text{out}} - T_{c,\text{in}}} \qquad P = \frac{T_{c,\text{out}} - T_{c,\text{in}}}{T_{h,\text{in}} - T_{c,\text{in}}}
$$

where $R$ is the heat capacity ratio and $P$ is the thermal effectiveness. The correction factor for a 1-2 exchanger (one shell pass, two tube passes) is:

$$
F = \frac{\sqrt{R^2 + 1} \ln\left(\frac{1 - P}{1 - RP}\right)}{(R - 1) \ln\left(\frac{2 - P(R + 1 - \sqrt{R^2 + 1})}{2 - P(R + 1 + \sqrt{R^2 + 1})}\right)}
$$

A design should maintain $F > 0.75$; values below this indicate that a multi-shell arrangement is needed.

### 16.4.3 Design Procedure

The LMTD design procedure is:

1. Calculate the heat duty $Q$ from an energy balance: $Q = \dot{m}_h c_{p,h} (T_{h,\text{in}} - T_{h,\text{out}}) = \dot{m}_c c_{p,c} (T_{c,\text{out}} - T_{c,\text{in}})$
2. Assume or calculate $U$ from fluid properties and geometry
3. Compute $\Delta T_{\text{LMTD}}$ and the correction factor $F$
4. Calculate the required area: $A = Q / (U \cdot F \cdot \Delta T_{\text{LMTD}})$
5. Choose a tube layout and compute the number of tubes
6. Check the pressure drop on both sides
7. Iterate if necessary

### 16.4.4 NeqSim Example: LMTD-Based Design

The following NeqSim code demonstrates a two-stream heat exchanger where the UA value is specified and the outlet temperatures are computed:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Create the hot stream: gas from a compressor aftercooler
hot_fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 120.0, 80.0)
hot_fluid.addComponent("methane", 0.85)
hot_fluid.addComponent("ethane", 0.08)
hot_fluid.addComponent("propane", 0.04)
hot_fluid.addComponent("n-butane", 0.03)
hot_fluid.setMixingRule("classic")

hot_stream = jneqsim.process.equipment.stream.Stream("Hot Gas", hot_fluid)
hot_stream.setFlowRate(50000.0, "kg/hr")
hot_stream.setTemperature(120.0, "C")
hot_stream.setPressure(80.0, "bara")

# Create the cold stream: cooling medium (glycol-water)
cold_fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 25.0, 5.0)
cold_fluid.addComponent("water", 0.70)
cold_fluid.addComponent("MEG", 0.30)
cold_fluid.setMixingRule("classic")

cold_stream = jneqsim.process.equipment.stream.Stream("Cooling Water", cold_fluid)
cold_stream.setFlowRate(80000.0, "kg/hr")
cold_stream.setTemperature(25.0, "C")
cold_stream.setPressure(5.0, "bara")

# Create the heat exchanger with UA specification
hx = jneqsim.process.equipment.heatexchanger.HeatExchanger("Gas Cooler", hot_stream, cold_stream)
hx.setUAvalue(15000.0)  # UA = 15000 W/K

# Build and run the process
process = jneqsim.process.processmodel.ProcessSystem()
process.add(hot_stream)
process.add(cold_stream)
process.add(hx)
process.run()

# Read results
T_hot_out = hx.getOutStream(0).getTemperature("C")
T_cold_out = hx.getOutStream(1).getTemperature("C")
duty_kW = hx.getDuty() / 1000.0

print(f"Hot stream outlet temperature:  {T_hot_out:.1f} °C")
print(f"Cold stream outlet temperature: {T_cold_out:.1f} °C")
print(f"Heat duty: {duty_kW:.0f} kW")
print(f"UA value:  {hx.getUAvalue():.0f} W/K")
```

In this example, NeqSim solves for the outlet temperatures that satisfy the energy balance given the specified UA value. The `HeatExchanger` class internally computes the LMTD and iterates to find the outlet conditions.

---

## 16.5 The Effectiveness-NTU Method

### 16.5.1 Concept and Definitions

The effectiveness-NTU method is an alternative to LMTD that is particularly useful when the outlet temperatures are unknown (the rating problem). The key definitions are:

**Effectiveness** ($\varepsilon$): the ratio of actual heat transfer to the maximum possible:

$$
\varepsilon = \frac{Q}{Q_{\max}} = \frac{Q}{C_{\min}(T_{h,\text{in}} - T_{c,\text{in}})}
$$

where $C_{\min} = \min(\dot{m}_h c_{p,h}, \dot{m}_c c_{p,c})$ is the smaller heat capacity rate.

**Number of Transfer Units** (NTU): a dimensionless measure of exchanger size:

$$
\text{NTU} = \frac{UA}{C_{\min}}
$$

**Capacity ratio** ($C_r$):

$$
C_r = \frac{C_{\min}}{C_{\max}}
$$

### 16.5.2 Effectiveness Relations

For a counterflow exchanger:

$$
\varepsilon = \frac{1 - \exp[-\text{NTU}(1 - C_r)]}{1 - C_r \exp[-\text{NTU}(1 - C_r)]}
$$

For a parallel flow exchanger:

$$
\varepsilon = \frac{1 - \exp[-\text{NTU}(1 + C_r)]}{1 + C_r}
$$

For a 1-2 TEMA E shell-and-tube:

$$
\varepsilon = 2\left[1 + C_r + \sqrt{1 + C_r^2}\coth\left(\frac{\text{NTU}}{2}\sqrt{1 + C_r^2}\right)\right]^{-1}
$$

For a crossflow exchanger with both fluids unmixed:

$$
\varepsilon = 1 - \exp\left[\frac{\text{NTU}^{0.22}}{C_r}\left(\exp(-C_r \cdot \text{NTU}^{0.78}) - 1\right)\right]
$$

### 16.5.3 NeqSim and the Effectiveness Approach

NeqSim's `HeatExchanger` class reports the thermal effectiveness after a run:

```python
# After running the heat exchanger (from previous example)
effectiveness = hx.thermalEffectiveness
ntu = hx.getUAvalue() / min(
    hot_stream.getFlowRate("kg/sec") * hot_fluid.getCp("J/kgK"),
    cold_stream.getFlowRate("kg/sec") * cold_fluid.getCp("J/kgK")
)
print(f"Thermal effectiveness: {effectiveness:.3f}")
print(f"NTU: {ntu:.2f}")
```

---

## 16.6 Shell-and-Tube Design

### 16.6.1 Tube Layout and Geometry

The tube layout pattern determines the shell-side flow pattern and cleaning accessibility:

| Layout | Pitch Angle | Characteristics |
|--------|------------|----------------|
| Triangular (30°) | 30° | Highest tube count; not mechanically cleanable |
| Rotated triangular (60°) | 60° | Good tube count; limited cleaning |
| Square (90°) | 90° | Mechanically cleanable; lower tube count |
| Rotated square (45°) | 45° | Good heat transfer; limited cleaning |

Standard tube sizes in oil and gas are:

| Outer Diameter (mm) | Wall Thickness (mm) | Material |
|--------------------|--------------------|---------|
| 19.05 (3/4") | 1.65 (BWG 16) | Carbon steel, SS316 |
| 25.4 (1") | 2.11 (BWG 14) | Carbon steel, SS316 |
| 31.75 (1-1/4") | 2.77 (BWG 12) | Carbon steel, Duplex |

Tube pitch ratio $P_t/d_o$ is typically 1.25 for triangular and 1.25–1.33 for square layouts.

### 16.6.2 Baffles

Baffles serve two purposes: they support the tubes and direct the shell-side flow across the tube bundle, improving heat transfer. Types include:

- **Single segmental** — the most common; creates a zigzag flow path
- **Double segmental** — reduces pressure drop by about 50% compared to single segmental
- **Disc-and-doughnut** — axial-radial flow pattern; good for low pressure drop
- **Helical baffles** — spiral flow path; excellent for fouling services and low pressure drop

The baffle cut (expressed as a percentage of the shell inside diameter) and baffle spacing are key design parameters:

| Parameter | Typical Range |
|-----------|--------------|
| Baffle cut | 20–35% of shell ID |
| Baffle spacing (minimum) | 0.2 × shell ID |
| Baffle spacing (maximum) | shell ID |
| Number of baffles | 5–40 |

### 16.6.3 The Bell-Delaware Method

The Bell-Delaware method is the standard hand-calculation method for shell-side heat transfer and pressure drop. It accounts for the real flow patterns in a baffled shell:

1. **Ideal tube bank** — heat transfer coefficient for crossflow over a tube bank (Kern method baseline)
2. **Correction factors** — applied to the ideal coefficient:
   - $J_c$ — baffle cut correction (segmental baffle geometry)
   - $J_l$ — baffle leakage correction (tube-to-baffle and baffle-to-shell gaps)
   - $J_b$ — bypass correction (bundle-to-shell gap, pass partition lanes)
   - $J_s$ — unequal baffle spacing correction (inlet and outlet spacings differ)
   - $J_r$ — adverse temperature gradient correction for laminar flow

The corrected shell-side coefficient is:

$$
h_s = h_{\text{ideal}} \cdot J_c \cdot J_l \cdot J_b \cdot J_s \cdot J_r
$$

Similarly for pressure drop:

$$
\Delta P_s = \Delta P_{\text{ideal}} \cdot R_l \cdot R_b
$$

where $R_l$ and $R_b$ are pressure drop correction factors for leakage and bypass.

Typical values for the correction factors:

| Factor | Typical Range | Effect |
|--------|--------------|--------|
| $J_c$ | 0.65–1.0 | Baffle cut geometry |
| $J_l$ | 0.6–0.9 | Leakage through gaps |
| $J_b$ | 0.7–0.9 | Bypass around bundle |
| $J_s$ | 0.85–1.0 | Unequal baffle spacing |
| $J_r$ | 0.8–1.0 | Laminar temperature gradient |

---

## 16.7 Air-Cooled Heat Exchanger Design

### 16.7.1 Configuration and Components

An air-cooled heat exchanger (ACHE) consists of:

- **Tube bundle** — typically finned tubes (aluminum fins on carbon steel or alloy tubes)
- **Headers** — plug, removable cover, or welded cover types
- **Fans** — axial flow fans driven by electric motors
- **Support structure** — A-frame or horizontal mount

The overall heat transfer is controlled by the air-side resistance, which is much larger than the tube-side resistance due to the low heat transfer coefficient of air. Extended surfaces (fins) are used to compensate, with fin-to-bare tube area ratios of 15:1 to 25:1.

### 16.7.2 Fan Sizing

Fan power is calculated from:

$$
W_{\text{fan}} = \frac{\dot{V}_{\text{air}} \cdot \Delta P_{\text{air}}}{\eta_{\text{fan}} \cdot \eta_{\text{motor}}}
$$

where $\dot{V}_{\text{air}}$ is the volumetric air flow rate, $\Delta P_{\text{air}}$ is the total static pressure drop across the bundle, $\eta_{\text{fan}}$ is the fan efficiency (typically 0.65–0.75), and $\eta_{\text{motor}}$ is the motor efficiency (0.90–0.95).

The air flow rate required is:

$$
\dot{V}_{\text{air}} = \frac{Q}{\rho_{\text{air}} \cdot c_{p,\text{air}} \cdot \Delta T_{\text{air}}}
$$

where $\Delta T_{\text{air}} = T_{\text{air,out}} - T_{\text{air,in}}$ is the air temperature rise.

### 16.7.3 Ambient Temperature Correction

The design ambient temperature significantly affects ACHE sizing. In production optimization, air coolers must be checked at extreme conditions:

| Condition | Design Temperature |
|-----------|-------------------|
| Summer design | Site maximum + 2 °C |
| Winter design | Site minimum |
| Normal operation | Annual average |

The approach temperature — the difference between the process outlet temperature and the ambient air temperature — is a key economic parameter:

$$
T_{\text{approach}} = T_{\text{process,out}} - T_{\text{ambient}}
$$

Typical approach temperatures range from 10 °C (economical) to 5 °C (expensive, large air cooler). Approach temperatures below 5 °C are rarely justified.

### 16.7.4 NeqSim Example: Cooler Modeling

NeqSim models air coolers and other utility coolers using the `Cooler` class with an outlet temperature specification:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Compressed gas to be cooled
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 110.0, 70.0)
gas.addComponent("methane", 0.90)
gas.addComponent("ethane", 0.06)
gas.addComponent("propane", 0.03)
gas.addComponent("CO2", 0.01)
gas.setMixingRule("classic")

gas_stream = jneqsim.process.equipment.stream.Stream("Compressor Discharge", gas)
gas_stream.setFlowRate(30000.0, "kg/hr")
gas_stream.setTemperature(110.0, "C")
gas_stream.setPressure(70.0, "bara")

# Create the air cooler modeled as a Cooler with outlet temperature spec
aircooler = jneqsim.process.equipment.heatexchanger.Cooler("Air Cooler")
aircooler.setInletStream(gas_stream)
aircooler.setOutletTemperature(273.15 + 40.0)  # Target 40 °C outlet

process = jneqsim.process.processmodel.ProcessSystem()
process.add(gas_stream)
process.add(aircooler)
process.run()

# Read the cooling duty
duty_kW = aircooler.getDuty() / 1000.0
T_out = aircooler.getOutletStream().getTemperature("C")
print(f"Outlet temperature: {T_out:.1f} °C")
print(f"Cooling duty: {duty_kW:.0f} kW")

# Estimate air flow for 15 °C rise, ambient at 25 °C
rho_air = 1.2  # kg/m3
cp_air = 1005.0  # J/(kg·K)
delta_T_air = 15.0  # K
Q_watts = abs(aircooler.getDuty())
V_air = Q_watts / (rho_air * cp_air * delta_T_air)  # m3/s
print(f"Estimated air flow: {V_air:.1f} m³/s")
```

---

## 16.8 Heat Duty Calculations

### 16.8.1 Sensible Heat

For single-phase fluids without phase change, the heat duty is:

$$
Q = \dot{m} \cdot c_p \cdot (T_{\text{out}} - T_{\text{in}})
$$

where $\dot{m}$ is the mass flow rate (kg/s) and $c_p$ is the specific heat capacity (J/(kg·K)).

### 16.8.2 Latent Heat

For phase change processes (condensation or vaporization), the heat duty includes latent heat:

$$
Q = \dot{m} \cdot \Delta H_{\text{vap}}
$$

For hydrocarbon mixtures, phase change occurs over a temperature range, and the duty must be integrated along the condensation or vaporization curve. NeqSim handles this automatically through its rigorous enthalpy calculations.

### 16.8.3 Combined Sensible and Latent Heat

In many oil and gas heat exchangers, both sensible and latent heat transfer occur simultaneously. A hot gas stream being cooled may partially condense, while a cold liquid stream being heated may partially vaporize. The total duty is:

$$
Q = H_{\text{in}} - H_{\text{out}}
$$

where $H$ is the total stream enthalpy. NeqSim uses enthalpy-based (PH flash) calculations to correctly handle phase change.

### 16.8.4 NeqSim Example: Duty-Based Heater

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Crude oil requiring heating for stabilization
oil = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, 3.0)
oil.addComponent("methane", 0.02)
oil.addComponent("ethane", 0.03)
oil.addComponent("propane", 0.05)
oil.addComponent("n-butane", 0.06)
oil.addComponent("n-pentane", 0.08)
oil.addComponent("n-hexane", 0.10)
oil.addComponent("n-heptane", 0.15)
oil.addComponent("n-octane", 0.20)
oil.addComponent("n-nonane", 0.15)
oil.addComponent("n-decane", 0.16)
oil.setMixingRule("classic")

oil_stream = jneqsim.process.equipment.stream.Stream("Crude Oil Feed", oil)
oil_stream.setFlowRate(100000.0, "kg/hr")
oil_stream.setTemperature(30.0, "C")
oil_stream.setPressure(3.0, "bara")

# Create a heater with outlet temperature specification
heater = jneqsim.process.equipment.heatexchanger.Heater("Oil Heater")
heater.setInletStream(oil_stream)
heater.setOutletTemperature(75.0, "C")

process = jneqsim.process.processmodel.ProcessSystem()
process.add(oil_stream)
process.add(heater)
process.run()

duty_MW = heater.getDuty() / 1.0e6
T_out = heater.getOutletStream().getTemperature("C")
print(f"Heater outlet temperature: {T_out:.1f} °C")
print(f"Heating duty: {duty_MW:.2f} MW")
```

---

## 16.9 Temperature Approach and Cross

### 16.9.1 Minimum Approach Temperature

The minimum approach temperature (MAT) is the smallest temperature difference between the hot and cold streams anywhere in the exchanger. It is a key design parameter:

$$
\Delta T_{\min} = \min(T_h(x) - T_c(x)) \quad \forall x \in [0, L]
$$

Design guidelines for minimum approach temperature:

| Service | $\Delta T_{\min}$ (°C) |
|---------|----------------------|
| Gas–gas | 10–20 |
| Gas–liquid | 5–10 |
| Liquid–liquid | 5–10 |
| Condensing | 3–5 |
| Cryogenic (LNG) | 2–3 |

### 16.9.2 Temperature Cross

A temperature cross occurs when the cold stream outlet temperature exceeds the hot stream outlet temperature. This is physically possible in counterflow exchangers but impossible in parallel flow. Temperature crosses require careful multi-shell design.

When a temperature cross exists, the LMTD correction factor drops rapidly, and a single TEMA E shell is insufficient. The solution is to use multiple shells in series or a TEMA F shell with a longitudinal baffle.

---

## 16.10 Heat Integration and Pinch Analysis

### 16.10.1 Fundamentals of Pinch Analysis

Pinch analysis, developed by Bodo Linnhoff in the 1970s, is a systematic methodology for minimizing energy consumption by maximizing heat recovery between process streams. The method identifies:

- **Minimum heating utility** ($Q_{h,\min}$) — the minimum external heating required
- **Minimum cooling utility** ($Q_{c,\min}$) — the minimum external cooling required
- **Pinch temperature** — the temperature that divides the process into a heat sink (above the pinch) and a heat source (below the pinch)

The fundamental principle is:

> No heat should be transferred across the pinch. Above the pinch, only heating utility should be used. Below the pinch, only cooling utility should be used.

### 16.10.2 Composite Curves

The composite curves are constructed by plotting cumulative enthalpy change against temperature for all hot streams (hot composite) and all cold streams (cold composite). The overlap between the curves represents the maximum heat recovery.

![Composite curves showing pinch point and utility targets](figures/composite_curves.png)

The area between the composite curves represents the heat transfer driving force. The pinch point is where the curves are closest (separated by $\Delta T_{\min}$).

### 16.10.3 Grand Composite Curve

The grand composite curve (GCC) plots net heat flow against shifted temperature. It shows:

- The shape of the utility demand (high-grade or low-grade heat needed)
- Opportunities for heat pump or heat engine placement
- Pocket areas where process-to-process heat exchange occurs naturally

### 16.10.4 NeqSim Pinch Analysis

NeqSim provides the `PinchAnalysis` class for performing pinch analysis on a set of process streams:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Create a PinchAnalysis with 10 °C minimum approach temperature
PinchAnalysis = jneqsim.process.equipment.heatexchanger.heatintegration.PinchAnalysis

pinch = PinchAnalysis(10.0)  # delta_T_min = 10 °C

# Add hot streams (need cooling)
# Parameters: name, supply_temp_C, target_temp_C, mCp (kW/K)
pinch.addHotStream("Reactor effluent", 250.0, 60.0, 20.0)
pinch.addHotStream("Product cooler", 160.0, 45.0, 15.0)
pinch.addHotStream("Overhead vapor", 110.0, 40.0, 30.0)

# Add cold streams (need heating)
pinch.addColdStream("Feed preheater", 30.0, 200.0, 18.0)
pinch.addColdStream("Reboiler", 80.0, 120.0, 35.0)
pinch.addColdStream("Stripper feed", 50.0, 90.0, 10.0)

# Run the pinch analysis
pinch.run()

# Get results
Qh = pinch.getMinimumHeatingUtility()
Qc = pinch.getMinimumCoolingUtility()
T_pinch = pinch.getPinchTemperatureC()

print(f"Minimum heating utility: {Qh:.0f} kW")
print(f"Minimum cooling utility: {Qc:.0f} kW")
print(f"Pinch temperature: {T_pinch:.1f} °C")

# Get composite curve data for plotting
hot_composite = pinch.getHotCompositeCurve()
grand_composite = pinch.getGrandCompositeCurve()
```

### 16.10.5 Pinch Analysis from a Process Simulation

For a more integrated approach, NeqSim can extract hot and cold streams directly from a `ProcessSystem`:

```python
PinchAnalysis = jneqsim.process.equipment.heatexchanger.heatintegration.PinchAnalysis
# Define explicit process-stream targets: automatic equipment discovery may be empty.
pinch = PinchAnalysis(10.0)
pinch.addHotStream("Hot utility source", 150.0, 60.0, 20.0)  # mCp in kW/K
pinch.addColdStream("Feed heating", 25.0, 120.0, 12.0)
pinch.run()
print("Minimum heating utility (kW):", pinch.getMinimumHeatingUtility())
print("Minimum cooling utility (kW):", pinch.getMinimumCoolingUtility())
print("Hot-side pinch (C):", pinch.getPinchTemperatureC())
```

This approach automatically identifies all thermal utilities in the process and computes the energy targets.

---

## 16.11 Hot Oil Systems

### 16.11.1 System Configuration

Hot oil systems provide indirect heating using a heat transfer fluid (typically a synthetic oil like Therminol or Dowtherm) circulated in a closed loop. The system consists of:

- **Hot oil heater** — a fired heater or waste heat recovery unit that heats the hot oil
- **Circulating pump** — maintains flow through the loop
- **Expansion tank** — accommodates thermal expansion of the oil
- **Process heat exchangers** — transfer heat from hot oil to process streams

Hot oil systems are preferred over direct fired heating because they:

- Provide consistent, controllable heat at lower temperatures
- Avoid hot spots and coking that occur with direct heating
- Are inherently safer (no combustion products in the process)

### 16.11.2 Typical Hot Oil Properties

| Property | Therminol 66 | Dowtherm A |
|----------|-------------|-----------|
| Operating range (°C) | −3 to 345 | 15 to 400 |
| Flash point (°C) | 170 | 113 |
| Specific heat at 300 °C (kJ/(kg·K)) | 2.27 | 2.26 |
| Thermal conductivity at 300 °C (W/(m·K)) | 0.098 | 0.096 |
| Viscosity at 300 °C (mPa·s) | 0.36 | 0.22 |

### 16.11.3 NeqSim Example: Hot Oil Loop

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Model a simple hot oil heating loop
# Hot oil: approximated as n-dodecane

hot_oil_fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 250.0, 5.0)
hot_oil_fluid.addComponent("n-dodecane", 1.0)
hot_oil_fluid.setMixingRule("classic")

hot_oil_stream = jneqsim.process.equipment.stream.Stream("Hot Oil Supply", hot_oil_fluid)
hot_oil_stream.setFlowRate(60000.0, "kg/hr")
hot_oil_stream.setTemperature(250.0, "C")
hot_oil_stream.setPressure(5.0, "bara")

# Process stream to be heated (crude oil)
crude = jneqsim.thermo.system.SystemSrkEos(273.15 + 40.0, 8.0)
crude.addComponent("n-heptane", 0.30)
crude.addComponent("n-octane", 0.35)
crude.addComponent("n-nonane", 0.20)
crude.addComponent("n-decane", 0.15)
crude.setMixingRule("classic")

crude_stream = jneqsim.process.equipment.stream.Stream("Crude Oil", crude)
crude_stream.setFlowRate(80000.0, "kg/hr")
crude_stream.setTemperature(40.0, "C")
crude_stream.setPressure(8.0, "bara")

# Heat exchanger between hot oil and crude
hx = jneqsim.process.equipment.heatexchanger.HeatExchanger(
    "Hot Oil HX", hot_oil_stream, crude_stream)
hx.setUAvalue(25000.0)  # W/K

process = jneqsim.process.processmodel.ProcessSystem()
process.add(hot_oil_stream)
process.add(crude_stream)
process.add(hx)
process.run()

T_crude_out = hx.getOutStream(1).getTemperature("C")
T_oil_return = hx.getOutStream(0).getTemperature("C")
duty = hx.getDuty() / 1000.0

print(f"Crude outlet temperature: {T_crude_out:.1f} °C")
print(f"Hot oil return temperature: {T_oil_return:.1f} °C")
print(f"Heat duty: {duty:.0f} kW")
```

---

## 16.12 Seawater Cooling Systems

### 16.12.1 Design Considerations

Seawater is the primary cooling medium for most offshore platforms. Design considerations include:

- **Corrosion** — seawater is highly corrosive; titanium or Cu-Ni tubes are typically required
- **Biofouling** — marine organisms colonize surfaces; chlorination or anti-fouling coatings are needed
- **Temperature variation** — seawater temperature varies seasonally from 2 °C (Arctic) to 32 °C (Gulf)
- **Environmental regulations** — maximum discharge temperature rise (typically 7 °C above ambient)
- **Intake depth** — deeper intake provides colder, cleaner water

### 16.12.2 Material Selection

| Material | Application | Maximum Temperature |
|----------|-----------|-------------------|
| Titanium Gr. 2 | Primary coolers | 120 °C |
| 90/10 Cu-Ni | Low-temperature coolers | 70 °C |
| Super duplex | High-pressure coolers | 250 °C |
| GRP (fiberglass) | Piping, large heat exchangers | 60 °C |

### 16.12.3 Cooling Water System Sizing

The seawater flow rate required for a platform is:

$$
\dot{m}_{\text{sw}} = \frac{Q_{\text{total}}}{ c_{p,\text{sw}} \cdot \Delta T_{\text{sw}}}
$$

where $Q_{\text{total}}$ is the total cooling duty, $c_{p,\text{sw}} \approx 3990$ J/(kg·K), and $\Delta T_{\text{sw}}$ is the allowed seawater temperature rise (typically 7–10 °C).

---

## 16.13 Heat Exchanger Optimization in Production Systems

### 16.13.1 Impact on Separation Efficiency

The temperature of the fluid entering a separator directly affects the vapor–liquid split. Cooling the wellstream before the first-stage separator increases liquid recovery. The optimization trade-off is:

- **Lower inlet temperature** → more liquid recovery → more revenue from oil/condensate
- **Lower inlet temperature** → more cooling duty → higher energy cost and equipment size
- **Lower inlet temperature** → risk of hydrate formation → need for inhibitor injection

### 16.13.2 Impact on Compressor Performance

Interstage cooling between compressor stages reduces the work required for the next stage:

$$
W_{\text{stage}} = \frac{n}{n-1} \cdot \dot{m} R T_{\text{inlet}} \left[\left(\frac{P_{\text{out}}}{P_{\text{in}}}\right)^{(n-1)/n} - 1\right]
$$

Lower interstage temperature means lower $T_{\text{inlet}}$, which reduces power. However, cooling too close to the dewpoint may cause liquid dropout in the next stage.

### 16.13.3 Impact on Export Specifications

Gas export requires meeting a dewpoint specification (typically −18 °C at 69 barg per the Cricondentherm standard). The final gas cooler temperature determines whether the export gas meets this specification.

---

## 16.12 Heat Exchanger Capacity Constraints in Production Optimization

Heat exchangers are often the hidden bottleneck in production systems. Unlike valves or compressors where capacity limits are immediately obvious, heat exchanger constraints manifest as an inability to achieve the required outlet temperature — leading to off-spec products, equipment damage, or reduced throughput. NeqSim models heat exchanger capacity through duty constraints that integrate with the overall production optimization framework.

### 16.12.1 Duty Constraints

The fundamental capacity constraint for any heat exchanger is the maximum heat duty it can deliver. The duty is limited by:

- **Heat transfer area** — fixed by the physical design; cannot be increased without adding equipment
- **Overall heat transfer coefficient** — degrades with fouling; restored only by cleaning
- **Temperature driving force** — limited by the approach temperature and ambient conditions
- **Pressure drop** — excessive fouling or flow increases the pressure drop beyond allowable limits

The maximum design duty is the product of the clean UA value and the maximum driving force:

$$
Q_{\max} = U_{\text{design}} \cdot A \cdot F \cdot \Delta T_{\text{LMTD,max}}
$$

In NeqSim, the design duty constraint is set through the mechanical design interface:

```java
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
Logger logger = LogManager.getLogger("BookChapter16");
import neqsim.thermo.system.SystemSrkEos;
import neqsim.process.equipment.stream.Stream;
import neqsim.process.processmodel.ProcessSystem;
import neqsim.process.equipment.capacity.CapacityConstraint;
import neqsim.process.util.optimizer.ProductionOptimizer;
import java.util.*;
SystemSrkEos fluid = new SystemSrkEos(313.15, 80.0);
fluid.addComponent("methane", 0.80);
fluid.addComponent("ethane", 0.10);
fluid.addComponent("n-heptane", 0.08);
fluid.addComponent("water", 0.02);
fluid.setMixingRule("classic");
fluid.setMultiPhaseCheck(true);
Stream feed = new Stream("Feed", fluid);
feed.setFlowRate(20000.0, "kg/hr");
ProcessSystem process = new ProcessSystem();
process.add(feed);
process.run();
import neqsim.process.equipment.heatexchanger.Heater;
Stream feedStream = feed;
// Java: Set maximum design duty for a heater
Heater heater = new Heater("Inlet Heater", feedStream);
heater.setOutletTemperature(273.15 + 80.0);
process.add(heater);
process.run();

// Initialize mechanical design and set constraint
heater.initMechanicalDesign();
heater.getMechanicalDesign().setMaxDesignDuty(5000000.0);  // 5 MW max
```

When the required duty exceeds the design maximum, the heat exchanger cannot achieve the target outlet temperature. The optimizer must then either:

1. **Accept a lower outlet temperature** — adjust the process to work with what the heat exchanger can deliver
2. **Reduce the flow rate** — decrease production to bring the duty within the heat exchanger's capability
3. **Install additional area** — add a parallel heat exchanger or replace with a larger unit
4. **Improve fouling management** — more frequent cleaning to restore UA value

### 16.12.2 Heater and Cooler Maximum Design Duty

For utility exchangers (heaters and coolers), the capacity constraint is straightforward: the maximum heat input or removal rate. This is set through the mechanical design:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Create a process with a heater approaching its capacity
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 20.0, 80.0)
fluid.addComponent("methane", 0.85)
fluid.addComponent("ethane", 0.08)
fluid.addComponent("propane", 0.04)
fluid.addComponent("n-butane", 0.03)
fluid.setMixingRule("classic")

Stream = jneqsim.process.equipment.stream.Stream
Heater = jneqsim.process.equipment.heatexchanger.Heater
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

feed = Stream("Cold Gas", fluid)
feed.setFlowRate(50000.0, "kg/hr")
feed.setTemperature(20.0, "C")
feed.setPressure(80.0, "bara")

heater = Heater("Inlet Heater", feed)
heater.setOutletTemperature(273.15 + 60.0)  # Target: 60°C

process = ProcessSystem()
process.add(feed)
process.add(heater)
process.run()

# Report duty
duty_MW = abs(heater.getDuty()) / 1.0e6
T_out = heater.getOutletStream().getTemperature("C")
print(f"Required duty: {duty_MW:.2f} MW")
print(f"Outlet temperature: {T_out:.1f} °C")

# Sweep flow rates to find where heater becomes limiting
max_duty_MW = 3.0  # Assume 3 MW maximum heater capacity
print(f"\n{'Flow (kg/hr)':>14} {'Duty (MW)':>10} {'Status':>18}")
print("-" * 44)
for flow in [20000, 40000, 60000, 80000, 100000]:
    feed.setFlowRate(float(flow), "kg/hr")
    process.run()
    duty = abs(heater.getDuty()) / 1.0e6
    status = "OK" if duty < max_duty_MW else "EXCEEDS CAPACITY"
    print(f"{flow:>14,} {duty:>10.2f} {status:>18}")
```

### 16.12.3 Heat Exchanger as Bottleneck: Cold Ambient Maximum Heating Scenario

A critical bottleneck scenario for heat exchangers occurs in cold climates or during winter operation, where the inlet temperature to the process drops significantly. The heater must provide a larger duty to achieve the same outlet temperature, but its maximum heat input is fixed by the hot utility system (steam, hot oil, or direct fire):

**Scenario**: An offshore platform in the North Sea operates an inlet heater to keep the wellstream above 40 °C for hydrate prevention. In summer (ambient 15 °C), the heater operates at 60% of capacity. In winter (ambient −10 °C), the wellstream arrives colder and the required duty increases:

$$
Q_{\text{winter}} = \dot{m} \cdot c_p \cdot (T_{\text{target}} - T_{\text{inlet,winter}})
$$

If $Q_{\text{winter}} > Q_{\text{design}}$, the heater becomes the bottleneck. The operator must either reduce flow (lost production) or accept a lower outlet temperature (hydrate risk).

```python
# Cold ambient scenario — heater becomes bottleneck in winter
print("=== Seasonal Impact on Heater Capacity ===")
print(f"{'Season':>10} {'T_in (°C)':>10} {'Duty (MW)':>10} {'% Capacity':>12}")
print("-" * 44)

max_duty = 3.5e6  # 3.5 MW design capacity

for season, T_in in [("Summer", 15.0), ("Autumn", 5.0),
                      ("Winter", -5.0), ("Arctic", -15.0)]:
    feed.setFlowRate(60000.0, "kg/hr")
    feed.setTemperature(T_in, "C")
    heater.setOutletTemperature(273.15 + 40.0)
    process.run()
    duty = abs(heater.getDuty())
    pct = duty / max_duty * 100
    print(f"{season:>10} {T_in:>10.0f} {duty/1e6:>10.2f} {pct:>12.0f}%")
```

### 16.12.4 Heat Exchanger Design Feasibility Report

NeqSim provides a comprehensive `HeatExchangerDesignFeasibilityReport` that evaluates whether a heat exchanger can be physically built and operated for the required duty and conditions. The report covers:

- **Thermal design** — LMTD, effectiveness, required area, tube count
- **Mechanical design** — TEMA/ASME compliance, tube wall thickness, shell pressure rating
- **Cost estimation** — CAPEX (equipment + installation), OPEX (cleaning, utilities), lifecycle cost
- **Supplier matching** — evaluates the design against capabilities of 14 international HX suppliers
- **Feasibility verdict** — FEASIBLE, FEASIBLE_WITH_WARNINGS, or NOT_FEASIBLE with severity-classified issues

```java
import neqsim.process.equipment.heatexchanger.HeatExchanger;
import neqsim.process.mechanicaldesign.heatexchanger.HeatExchangerDesignFeasibilityReport;
SystemSrkEos coldFluid = new SystemSrkEos(288.15, 5.0);
coldFluid.addComponent("water", 1.0);
coldFluid.setMixingRule("classic");
Stream cold = new Stream("Cooling water", coldFluid);
cold.setFlowRate(30000.0, "kg/hr");
cold.run();
feed.setTemperature(120.0, "C");
feed.run();
HeatExchanger heatExchanger = new HeatExchanger("HX-01", feed, cold);
heatExchanger.setUAvalue(10000.0);
heatExchanger.run();
// Generate a screening report; supplier matching is not a vendor guarantee.
HeatExchangerDesignFeasibilityReport hxReport =
    new HeatExchangerDesignFeasibilityReport(heatExchanger);
hxReport.setExchangerType("shell-and-tube");
hxReport.setDesignStandard("TEMA-R");
hxReport.generateReport();

String verdict = hxReport.getVerdict();  // FEASIBLE / NOT_FEASIBLE
String json = hxReport.toJson();         // Full JSON report
```

The feasibility report is particularly valuable during debottlenecking studies, where it answers the question: *If I need 20% more heat transfer area, can I get a single exchanger that handles the duty, or do I need two in parallel?*

### 16.12.5 Heat Integration with the PinchAnalysis Class

For facility-wide optimization, individual heat exchanger sizing is insufficient — the engineer must consider the entire heat exchange network. NeqSim provides the `PinchAnalysis` class for systematic heat integration analysis:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define hot and cold streams for pinch analysis
PinchAnalysis = jneqsim.process.equipment.heatexchanger.heatintegration.PinchAnalysis

pinch = PinchAnalysis(10.0)  # Minimum approach temperature = 10°C

# Add hot streams (streams that need cooling)
pinch.addHotStream("Compressor Discharge", 120.0, 40.0, 2500.0)  # Tin, Tout, mCp (kW/K)
pinch.addHotStream("Reactor Effluent", 200.0, 60.0, 1800.0)

# Add cold streams (streams that need heating)
pinch.addColdStream("Feed Preheat", 25.0, 80.0, 2200.0)
pinch.addColdStream("Reboiler", 100.0, 150.0, 1500.0)

pinch.run()

# Results
print(f"Pinch temperature: {pinch.getPinchTemperatureC():.1f} °C")
print(f"Minimum hot utility: {pinch.getMinimumHeatingUtility():.0f} kW")
print(f"Minimum cold utility: {pinch.getMinimumCoolingUtility():.0f} kW")
print(f"Maximum heat recovery: {pinch.getMaximumHeatRecovery():.0f} kW")
```

The pinch analysis identifies the **pinch temperature** — the point in the temperature scale where the hot and cold composite curves are closest. The pinch divides the process into two regions:

- **Above the pinch** — heat deficit; requires external heating (hot utility)
- **Below the pinch** — heat surplus; requires external cooling (cold utility)

The three golden rules of pinch analysis are:

1. Do not transfer heat across the pinch
2. Do not use external cooling above the pinch
3. Do not use external heating below the pinch

Violating these rules increases the total utility consumption beyond the thermodynamic minimum.

### 16.12.6 Comprehensive Example: Heat Exchanger Sizing with Constraints

The following example demonstrates a complete heat exchanger capacity analysis within a production optimization context:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# --- Build a gas processing train with heat exchangers ---
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 100.0, 70.0)
gas.addComponent("methane", 0.88)
gas.addComponent("ethane", 0.06)
gas.addComponent("propane", 0.03)
gas.addComponent("CO2", 0.02)
gas.addComponent("nitrogen", 0.01)
gas.setMixingRule("classic")

Stream = jneqsim.process.equipment.stream.Stream
Cooler = jneqsim.process.equipment.heatexchanger.Cooler
Heater = jneqsim.process.equipment.heatexchanger.Heater
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# Compressor discharge stream (hot gas to be cooled)
hot_gas = Stream("Compressor Discharge", gas)
hot_gas.setFlowRate(80000.0, "kg/hr")
hot_gas.setTemperature(100.0, "C")
hot_gas.setPressure(70.0, "bara")

# Air cooler (ambient-limited)
aircooler = Cooler("Aftercooler")
aircooler.setInletStream(hot_gas)
aircooler.setOutletTemperature(273.15 + 35.0)

process = ProcessSystem()
process.add(hot_gas)
process.add(aircooler)
process.run()

# Design duty at base conditions
base_duty_MW = abs(aircooler.getDuty()) / 1e6
print(f"Base case duty: {base_duty_MW:.2f} MW")

# Sensitivity: ambient temperature impact on approach and duty
print("\n=== Air Cooler: Ambient Temperature Sensitivity ===")
print(f"{'T_amb (°C)':>12} {'T_out (°C)':>12} {'Duty (MW)':>10} {'Approach':>10}")
print("-" * 46)

for T_amb in [-10, 0, 10, 20, 30, 35]:
    # Approach temperature = T_process_out - T_ambient
    T_out_target = max(T_amb + 10.0, 25.0)  # Min 10°C approach
    aircooler.setOutletTemperature(273.15 + T_out_target)
    process.run()
    duty = abs(aircooler.getDuty()) / 1e6
    approach = T_out_target - T_amb
    print(f"{T_amb:>12.0f} {T_out_target:>12.0f} {duty:>10.2f} {approach:>10.0f}")
```

This example shows how the air cooler duty varies with ambient temperature and approach constraints. The results directly inform facility design: oversizing the air cooler for summer ambient conditions may be necessary to maintain throughput year-round, but the cost increases non-linearly as the approach temperature decreases.

---

## Summary

- **Heat exchanger types** — shell-and-tube (TEMA classification), plate-and-frame, printed circuit, air-cooled, and double-pipe exchangers each serve specific roles in process facilities
- **Heat transfer fundamentals** — the overall heat transfer coefficient combines tube-side convection, wall conduction, shell-side convection, and fouling resistances
- **LMTD method** — sizes exchangers when all four temperatures are known; uses a correction factor $F$ for multi-pass arrangements
- **Effectiveness-NTU method** — rates exchangers when outlet temperatures are unknown; relates effectiveness to NTU and capacity ratio
- **Shell-and-tube design** — tube layout, baffles, and the Bell-Delaware method account for real flow patterns
- **Air-cooled exchangers** — ambient temperature correction and fan sizing are critical for production optimization
- **Pinch analysis** — identifies minimum utility requirements and the pinch temperature for heat integration
- **NeqSim tools** — `HeatExchanger` (UA-based two-stream), `Heater`/`Cooler` (utility exchangers), and `PinchAnalysis` (heat integration) provide comprehensive modeling capability

---

## Exercises

**Exercise 16.1 — Gas Cooler Sizing**
A natural gas stream (90% methane, 5% ethane, 3% propane, 2% CO₂) at 120 °C and 85 bara flows at 45,000 kg/hr. Design a gas cooler to reduce the temperature to 35 °C using seawater at 20 °C. (a) Calculate the heat duty using NeqSim. (b) If $U = 300$ W/(m²·K) and the seawater rise is 8 °C, calculate the required heat transfer area using the LMTD method. (c) What is the minimum seawater flow rate?

**Exercise 16.2 — Heat Exchanger Rating**
A shell-and-tube heat exchanger has $UA = 20{,}000$ W/K. The hot stream (produced water) enters at 85 °C with a flow rate of 50,000 kg/hr. The cold stream (injection water) enters at 15 °C with a flow rate of 60,000 kg/hr. Using NeqSim, determine the outlet temperatures and the heat duty. Verify using the effectiveness-NTU method.

**Exercise 16.3 — Crude Oil Heater**
A crude oil stabilizer requires heating from 35 °C to 80 °C at 3 bara. The crude oil composition is 5% methane, 5% ethane, 10% propane, 15% n-butane, 15% n-pentane, 20% n-hexane, 15% n-heptane, and 15% n-octane. The flow rate is 120,000 kg/hr. (a) Model the heater in NeqSim and determine the heating duty. (b) If a hot oil system at 250 °C is used, estimate the required UA value.

**Exercise 16.4 — Air Cooler Ambient Sensitivity**
Using the NeqSim `Cooler` class, model an air cooler for a gas stream (85% methane, 10% ethane, 5% propane) at 95 °C, 60 bara, and 25,000 kg/hr. Calculate the cooling duty for outlet temperatures of 30, 35, 40, 45, and 50 °C. Plot the duty versus outlet temperature and discuss the implications for summer versus winter operation.

**Exercise 16.5 — Pinch Analysis**
A gas processing plant has the following thermal streams:

| Stream | Type | $T_{\text{supply}}$ (°C) | $T_{\text{target}}$ (°C) | $\dot{m}c_p$ (kW/K) |
|--------|------|--------------------------|--------------------------|---------------------|
| H1 | Hot | 200 | 50 | 25 |
| H2 | Hot | 130 | 40 | 18 |
| C1 | Cold | 25 | 180 | 22 |
| C2 | Cold | 50 | 110 | 30 |

Using the NeqSim `PinchAnalysis` class with $\Delta T_{\min} = 10$ °C: (a) Determine the minimum heating and cooling utilities. (b) Find the pinch temperature. (c) Calculate the maximum heat recovery.

**Exercise 16.6 — Multi-Stream Heat Exchanger**
Design a gas-gas heat exchanger for a compressor interstage cooling application where the compressed gas at 150 °C exchanges heat with the incoming feed gas at 30 °C. Both streams are at 40 bara and flow at 35,000 kg/hr (lean gas: 95% methane, 5% ethane). Using NeqSim, determine the optimal UA value that cools the compressed gas to within 15 °C of the feed gas temperature.

**Exercise 16.7 — Fouling Impact Assessment**
For the gas cooler in Exercise 16.1, investigate the impact of fouling on performance. Start with a clean $U = 300$ W/(m²·K) and add fouling resistances of $R_{f,i} = 0.000088$ and $R_{f,o} = 0.000176$ m²·K/W. (a) Calculate the fouled $U$ value. (b) Using the same area, what is the new outlet temperature? (c) At what point does the gas cooler fail to meet the 35 °C specification?

---

## References

1. Kern, D. Q. (1950). *Process Heat Transfer*. McGraw-Hill.
2. Bell, K. J. (1981). "Delaware Method for Shell-Side Design." In *Heat Exchangers: Thermal-Hydraulic Fundamentals and Design*, Hemisphere Publishing.
3. Linnhoff, B., et al. (1982). *A User Guide on Process Integration for the Efficient Use of Energy*. IChemE.
4. TEMA (2019). *Standards of the Tubular Exchanger Manufacturers Association*, 10th Edition.
5. API 661 (2013). *Air-Cooled Heat Exchangers for General Refinery Service*.
6. Smith, R. (2016). *Chemical Process Design and Integration*, 2nd Edition. Wiley.
7. Serth, R. W., and Lestina, T. G. (2014). *Process Heat Transfer: Principles, Applications and Rules of Thumb*, 2nd Edition. Academic Press.
8. Sinnott, R. K. (2005). *Chemical Engineering Design*, Volume 6, 4th Edition. Butterworth-Heinemann.
9. Kemp, I. C. (2007). *Pinch Analysis and Process Integration*, 2nd Edition. Butterworth-Heinemann.
10. GPSA Engineering Data Book (2017). 14th Edition, Gas Processors Suppliers Association.


## Figures

![Figure 16.1: Duty Vs Flow](figures/ch14_duty_vs_flow.png)

*Figure 16.1: Duty Vs Flow*

![Figure 16.2: Temperature Profile](figures/ch14_temperature_profile.png)

*Figure 16.2: Temperature Profile*

![Figure 16.3: Ua Sizing](figures/ch14_ua_sizing.png)

*Figure 16.3: Ua Sizing*
