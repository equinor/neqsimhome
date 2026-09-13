
# Reservoir Engineering and Inflow Performance

<!-- Chapter metadata -->
<!-- Notebooks: ch04_ipr_curves.ipynb, ch04_reservoir_decline.ipynb, ch04_nodal_analysis.ipynb -->
<!-- Estimated pages: 20 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Apply Darcy's law and the radial flow equation to calculate well productivity
2. Construct inflow performance relationships (IPR) for oil wells (Vogel) and gas wells (back-pressure, LIT equations)
3. Explain reservoir drive mechanisms and their effect on pressure decline
4. Perform material balance calculations for different drive types
5. Use decline curve analysis (Arps) to forecast production
6. Understand the NODAL analysis framework for integrated well-reservoir-facility analysis
7. Use NeqSim's `SimpleReservoir` class for reservoir modeling in production optimization workflows

## 4.1 Introduction

Reservoir engineering provides the boundary conditions for production optimization. The reservoir determines how much fluid can be produced, at what rate, and for how long. No amount of topside optimization can overcome the fundamental constraints imposed by the reservoir — its pressure, permeability, fluid properties, and remaining reserves.

This chapter covers the reservoir engineering concepts most relevant to production optimization: inflow performance relationships that define what the well can deliver, reservoir pressure decline that governs the production life cycle, and the system analysis framework that connects reservoir performance to the rest of the production chain.

We focus on practical modeling rather than detailed reservoir simulation. For integrated production optimization, the reservoir is typically represented by IPR curves and decline profiles — simplified models that capture the essential behavior without the computational cost of full reservoir simulation.

## 4.2 Darcy's Law and Radial Flow

### 4.2.1 Darcy's Law

Darcy's law describes the flow of a single-phase fluid through a porous medium:

$$
q = -\frac{kA}{\mu}\frac{dP}{dx}
$$

where:

- $q$ = volumetric flow rate [m³/s]
- $k$ = permeability [m² or Darcy; 1 D = 9.869 × 10$^{-13}$ m²]
- $A$ = cross-sectional area [m²]
- $\mu$ = fluid viscosity [Pa·s]
- $dP/dx$ = pressure gradient [Pa/m]

The negative sign indicates that flow is in the direction of decreasing pressure.

### 4.2.2 Radial Flow to a Vertical Well

For steady-state radial flow to a vertical well in a homogeneous reservoir, integrating Darcy's law in cylindrical coordinates gives:

$$
q_o = \frac{2\pi k h (P_e - P_{wf})}{B_o \mu_o \left[\ln\left(\frac{r_e}{r_w}\right) + S\right]}
$$

where:

- $q_o$ = oil flow rate at surface conditions [m³/s]
- $k$ = reservoir permeability [m²]
- $h$ = net pay thickness [m]
- $P_e$ = reservoir pressure at the drainage boundary [Pa]
- $P_{wf}$ = flowing bottomhole pressure [Pa]
- $B_o$ = oil formation volume factor [-]
- $\mu_o$ = oil viscosity at reservoir conditions [Pa·s]
- $r_e$ = drainage radius [m]
- $r_w$ = wellbore radius [m]
- $S$ = skin factor [-]

For practical field units (bbl/day, mD, ft, psi, cp):

$$
q_o = \frac{0.00708\, k h (P_e - P_{wf})}{B_o \mu_o \left[\ln\left(\frac{r_e}{r_w}\right) - 0.75 + S\right]}
$$

### 4.2.3 The Productivity Index

The productivity index (PI or $J$) linearizes the well inflow for undersaturated oil:

$$
J = \frac{q_o}{P_e - P_{wf}} = \frac{2\pi k h}{B_o \mu_o \left[\ln\left(\frac{r_e}{r_w}\right) + S\right]}
$$

The PI has units of m³/s/Pa (or bbl/day/psi in field units). A higher PI means the well produces more for a given drawdown. The PI depends on:

- **Rock properties:** Permeability $k$ and thickness $h$
- **Fluid properties:** Viscosity $\mu_o$ and FVF $B_o$ (both pressure-dependent)
- **Completion quality:** Skin factor $S$ (positive = damaged, negative = stimulated)
- **Well geometry:** Drainage and wellbore radii

Typical productivity indices:

| Well Type | PI Range (Sm³/d/bar) |
|-----------|---------------------|
| Low permeability gas well | 100–1,000 |
| Average oil well | 1–50 |
| High productivity oil well | 50–500 |
| Fractured well | 100–2,000 |

### 4.2.4 Skin Factor

The skin factor $S$ accounts for the additional pressure drop (or reduced pressure drop) near the wellbore due to:

| Cause | Effect on $S$ | Typical Range |
|-------|--------------|---------------|
| Drilling damage (mud invasion) | Positive (damage) | +1 to +20 |
| Partial penetration | Positive | +1 to +10 |
| Perforation skin | Positive | +1 to +5 |
| Hydraulic fracturing | Negative (stimulated) | -2 to -6 |
| Acid stimulation | Negative | -1 to -3 |
| Gravel pack | Positive or negative | -1 to +5 |

The apparent skin $S$ transforms the wellbore radius to an effective radius:

$$
r_{w,\text{eff}} = r_w e^{-S}
$$

A skin of $S = -4$ is equivalent to increasing the effective wellbore radius by a factor of 55 — the effect of a hydraulic fracture.

## 4.3 Inflow Performance Relationships (IPR)

### 4.3.1 Linear IPR (Undersaturated Oil)

When the flowing bottomhole pressure $P_{wf}$ remains above the bubble point $P_b$, the oil behaves as a single-phase liquid with approximately constant compressibility, viscosity, and FVF. The IPR is linear:

$$
q_o = J(P_r - P_{wf})
$$

where $P_r$ is the average reservoir pressure and $J$ is the productivity index. The maximum flow rate occurs when $P_{wf} = 0$:

$$
q_{o,\max} = J \cdot P_r
$$

This linear relationship is plotted as a straight line on a $P_{wf}$ vs. $q_o$ graph.

### 4.3.2 Vogel's IPR (Saturated Oil)

When $P_{wf}$ falls below the bubble point, gas evolves in the reservoir near the wellbore, reducing the effective permeability to oil. Vogel (1968) developed an empirical correlation for this non-linear behavior:

$$
\frac{q_o}{q_{o,\max}} = 1 - 0.2\left(\frac{P_{wf}}{P_r}\right) - 0.8\left(\frac{P_{wf}}{P_r}\right)^2
$$

This gives a concave-downward curve on the $P_{wf}$ vs. $q_o$ plot. At $P_{wf} = P_r$, $q_o = 0$; at $P_{wf} = 0$, $q_o = q_{o,\max}$.

For the case where the reservoir pressure is above the bubble point but $P_{wf}$ falls below it, the composite IPR combines the linear region (above $P_b$) with the Vogel region (below $P_b$):

$$
q_o = J(P_r - P_b) + \frac{J P_b}{1.8}\left[1 - 0.2\left(\frac{P_{wf}}{P_b}\right) - 0.8\left(\frac{P_{wf}}{P_b}\right)^2\right] \quad \text{for } P_{wf} < P_b
$$

![IPR curves showing linear (undersaturated) and Vogel (saturated) behavior](figures/ipr_curves.png)

### 4.3.3 Gas Well IPR: Back-Pressure Equation

For gas wells, the inflow relationship accounts for the pressure-dependent gas properties. The simplified back-pressure equation (Rawlins and Schellhardt, 1935):

$$
q_g = C(P_r^2 - P_{wf}^2)^n
$$

where:

- $q_g$ = gas flow rate [Sm³/day]
- $C$ = performance coefficient (determined from well test)
- $n$ = deliverability exponent (0.5 ≤ $n$ ≤ 1.0; $n = 1$ for laminar flow, $n = 0.5$ for fully turbulent)

The coefficient $C$ and exponent $n$ are determined from a multi-rate well test (typically 4 stabilized rates).

### 4.3.4 Gas Well IPR: Laminar-Inertial-Turbulent (LIT) Equation

The more rigorous LIT equation separates laminar and turbulent contributions:

$$
P_r^2 - P_{wf}^2 = aq_g + bq_g^2
$$

where $a$ represents the laminar (Darcy) flow resistance and $b$ represents the turbulent (non-Darcy) flow resistance. This can also be written using pseudo-pressures $m(P)$ for improved accuracy at high pressures:

$$
m(P_r) - m(P_{wf}) = aq_g + bq_g^2
$$

The pseudo-pressure is defined as:

$$
m(P) = 2\int_{P_0}^{P} \frac{P'}{\mu_g(P') Z(P')} dP'
$$

which accounts for the variation of gas viscosity and Z-factor with pressure.

### 4.3.5 Horizontal Well IPR

For horizontal wells, the Joshi (1988) productivity equation modifies the radial flow equation:

$$
J_h = \frac{2\pi k_h h}{B_o \mu_o \left[\ln\left(\frac{a + \sqrt{a^2 - (L/2)^2}}{L/2}\right) + \frac{h}{L}\ln\left(\frac{h}{2\pi r_w}\right)\right]}
$$

where $L$ is the horizontal well length and:

$$
a = \frac{L}{2}\left[0.5 + \sqrt{0.25 + \left(\frac{2r_e}{L}\right)^4}\right]^{0.5}
$$

The horizontal well PI can be 2–5 times higher than a vertical well in the same reservoir, depending on the $L/h$ ratio and reservoir anisotropy $k_v/k_h$.

## 4.4 Reservoir Pressure Decline and Material Balance

### 4.4.1 Drive Mechanisms

The energy that drives fluid from the reservoir to the wellbore comes from several mechanisms:

| Drive Mechanism | Typical Recovery Factor | Pressure Behavior |
|----------------|----------------------|-------------------|
| Solution gas drive | 5–30% OOIP | Rapid decline |
| Gas cap drive | 20–40% OOIP | Moderate decline |
| Water drive (natural) | 30–60% OOIP | Near-constant pressure |
| Rock/fluid expansion | 1–5% OOIP | Above bubble point |
| Gravity drainage | 40–70% OOIP | Slow decline |
| Combination | Varies | Depends on dominant mechanism |

### 4.4.2 Material Balance Equation

The general material balance equation for an oil reservoir (Schilthuis, 1936):

$$
N_p[B_o + (R_p - R_s)B_g] = N\left[(B_o - B_{oi}) + (R_{si} - R_s)B_g + \frac{B_{oi}c_w S_{wi} + c_f}{1-S_{wi}}\Delta P\right] + \frac{m N B_{oi}}{B_{gi}}(B_g - B_{gi}) + W_e - W_p B_w
$$

where:

- $N_p$ = cumulative oil production
- $N$ = original oil in place (OOIP)
- $R_p$ = cumulative producing GOR
- $m$ = ratio of gas cap volume to oil zone volume
- $W_e$ = cumulative water influx
- $W_p$ = cumulative water production
- Subscript $i$ = initial conditions

This equation, combined with the PVT properties from Chapter 3, allows estimation of original oil in place and prediction of reservoir performance.

### 4.4.3 Gas Material Balance (P/Z Plot)

For a volumetric gas reservoir (no water influx), the material balance simplifies to:

$$
\frac{P}{Z} = \frac{P_i}{Z_i}\left(1 - \frac{G_p}{G}\right)
$$

where $G_p$ is the cumulative gas production and $G$ is the original gas in place (OGIP). A plot of $P/Z$ vs. $G_p$ is a straight line:

- The y-intercept gives $P_i/Z_i$
- The x-intercept gives $G$ (OGIP)
- The current position gives the remaining reserves

![P/Z plot for a volumetric gas reservoir showing original gas in place estimation](figures/pz_plot.png)

## 4.5 Decline Curve Analysis

### 4.5.1 Arps Decline Equations

Arps (1945) defined three types of production decline:

**Exponential decline** ($b = 0$):

$$
q(t) = q_i \exp(-D_i t)
$$

$$
N_p(t) = \frac{q_i - q(t)}{D_i}
$$

**Hyperbolic decline** ($0 < b < 1$):

$$
q(t) = \frac{q_i}{(1 + bD_i t)^{1/b}}
$$

$$
N_p(t) = \frac{q_i^b}{D_i(1-b)}\left[q_i^{1-b} - q(t)^{1-b}\right]
$$

**Harmonic decline** ($b = 1$):

$$
q(t) = \frac{q_i}{1 + D_i t}
$$

$$
N_p(t) = \frac{q_i}{D_i}\ln\left(\frac{q_i}{q(t)}\right)
$$

where:

- $q_i$ = initial production rate
- $D_i$ = initial decline rate [1/time]
- $b$ = decline exponent (0 ≤ $b$ ≤ 1)
- $N_p(t)$ = cumulative production at time $t$

Typical $b$ values by drive mechanism:

| Drive Mechanism | Typical $b$ |
|----------------|------------|
| Solution gas drive | 0.3–0.5 |
| Gas cap drive | 0.3–0.5 |
| Water drive | 0.0–0.3 |
| Gas well (volumetric) | 0.4–0.6 |

### 4.5.2 Decline Rate

The instantaneous decline rate is:

$$
D = -\frac{1}{q}\frac{dq}{dt}
$$

For exponential decline, $D$ is constant. For hyperbolic decline:

$$
D(t) = \frac{D_i}{1 + bD_i t}
$$

The effective annual decline rate $d$ relates to the nominal decline rate $D$ by:

$$
d = 1 - e^{-D}
$$

## 4.6 System Analysis: NODAL Analysis

### 4.6.1 Concept

NODAL analysis (first described by Gilbert, 1954; formalized by Mach et al., 1979) is the framework for analyzing the integrated well-reservoir-facility system. The system is divided at a "node" — typically the bottomhole — and two performance curves are plotted:

1. **Inflow Performance Relationship (IPR):** The rate the reservoir can deliver as a function of bottomhole pressure (from Section 4.3)
2. **Vertical Flow Performance (VFP):** The bottomhole pressure required to lift the fluid to the surface at each rate (from Chapter 5)

The operating point is where the two curves intersect. The inflow and outflow curves must be evaluated at the same node.

![NODAL analysis showing IPR and VFP curve intersection at the operating point](figures/nodal_analysis.png)

### 4.6.2 Applications of NODAL Analysis

| Application | What Changes |
|------------|-------------|
| Tubing size selection | VFP curve shifts |
| Choke sizing | VFP curve back-pressure increases |
| Artificial lift design | VFP curve lowered |
| Separator pressure optimization | VFP curve back-pressure changes |
| Stimulation evaluation | IPR curve shifts (skin reduction) |
| Water cut effect | Both curves change |

### 4.6.3 Multi-Well Optimization

When multiple wells produce into a common facility, the individual well operating points are coupled through the shared back-pressure. The total production is:

$$
q_{\text{total}} = \sum_{i=1}^{N_w} q_i(P_{wf,i})
$$

subject to:

- Each well's IPR constraint
- The gathering system pressure drop model
- The facility capacity constraint (separator capacity, compressor capacity)

This optimization problem — maximizing $q_{\text{total}}$ subject to constraints — is the core of production optimization, developed further in Chapter 19.

## 4.7 NeqSim Implementation: Reservoir Modeling

### 4.7.1 The SimpleReservoir Class

NeqSim provides the `SimpleReservoir` class for coupling reservoir performance with process simulation:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Create reservoir fluid
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 100.0, 250.0)
fluid.addComponent("nitrogen", 0.5)
fluid.addComponent("CO2", 2.0)
fluid.addComponent("methane", 65.0)
fluid.addComponent("ethane", 8.0)
fluid.addComponent("propane", 4.0)
fluid.addComponent("i-butane", 1.0)
fluid.addComponent("n-butane", 2.0)
fluid.addComponent("i-pentane", 0.8)
fluid.addComponent("n-pentane", 0.6)
fluid.addComponent("n-hexane", 1.0)
fluid.addComponent("n-heptane", 5.0)
fluid.addComponent("n-octane", 4.0)
fluid.addComponent("n-nonane", 3.0)
fluid.addComponent("n-decane", 2.1)
fluid.addComponent("water", 1.0)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

# Create reservoir
SimpleReservoir = jneqsim.process.equipment.reservoir.SimpleReservoir
reservoir = SimpleReservoir("Main Reservoir")
# Initial in-situ gas, oil and water pore volumes in m3 (illustrative).
reservoir.setReservoirFluid(fluid, 1.0e7, 2.0e7, 5.0e6)

# Add a production well
producer = reservoir.addOilProducer("Producer-1")
producer.setFlowRate(10000.0, "kg/hr")
```

### 4.7.2 Well Stream Setup

Setting up a well stream from the reservoir for process simulation:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Create reservoir fluid at typical conditions
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 95.0, 300.0)
fluid.addComponent("nitrogen", 0.4)
fluid.addComponent("CO2", 1.8)
fluid.addComponent("methane", 68.0)
fluid.addComponent("ethane", 7.5)
fluid.addComponent("propane", 4.2)
fluid.addComponent("n-butane", 2.5)
fluid.addComponent("n-pentane", 1.5)
fluid.addComponent("n-hexane", 1.2)
fluid.addComponent("n-heptane", 3.5)
fluid.addComponent("n-octane", 3.0)
fluid.addComponent("n-nonane", 2.4)
fluid.addComponent("n-decane", 2.0)
fluid.addComponent("water", 2.0)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

# Create well stream at wellhead conditions
Stream = jneqsim.process.equipment.stream.Stream
well_stream = Stream("Well-1 Stream", fluid)
well_stream.setFlowRate(50000.0, "kg/hr")     # 50 t/hr
well_stream.setTemperature(75.0, "C")          # Wellhead temperature
well_stream.setPressure(70.0, "bara")           # Wellhead pressure
well_stream.run()

# Check the well stream properties
well_fluid = well_stream.getFluid()
print(f"Number of phases: {well_fluid.getNumberOfPhases()}")
print(f"Gas rate: {well_stream.getFlowRate('MSm3/day'):.3f} MSm3/day (total)")
print(f"Temperature: {well_stream.getTemperature('C'):.1f} C")
print(f"Pressure: {well_stream.getPressure('bara'):.1f} bara")
```

### 4.7.3 IPR Curve Generation with NeqSim

Using NeqSim to generate IPR curves by solving the well-reservoir system at different bottomhole pressures:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Reservoir parameters
P_reservoir = 250.0  # bara
T_reservoir = 95.0   # C
PI = 15.0            # Sm3/d/bar (productivity index)
P_bubble = 180.0     # bara (bubble point)

# Calculate IPR using composite Vogel method
pressures_bhp = []
rates = []

for i in range(50):
    P_wf = 10.0 + i * 4.8  # 10 to 250 bara
    pressures_bhp.append(P_wf)

    if P_wf >= P_bubble:
        # Linear region (above bubble point)
        q = PI * (P_reservoir - P_wf)
    else:
        # Vogel region (below bubble point)
        q_at_pb = PI * (P_reservoir - P_bubble)
        q_vogel_max = q_at_pb + PI * P_bubble / 1.8
        q = q_at_pb + (q_vogel_max - q_at_pb) * (
            1.0 - 0.2 * (P_wf / P_bubble) - 0.8 * (P_wf / P_bubble) ** 2
        )
    rates.append(max(0.0, q))

# Print table
print(f"{'P_wf (bara)':>12} {'q_o (Sm3/d)':>12}")
print("-" * 26)
for p, q in zip(pressures_bhp[::5], rates[::5]):
    print(f"{p:12.1f} {q:12.1f}")
```

### 4.7.4 Decline Curve Implementation

```python
import math

# Arps decline curve parameters
q_i = 5000.0     # Initial rate, Sm3/d
D_i = 0.001      # Initial decline rate, 1/day (about 30% per year)
b = 0.5           # Hyperbolic exponent

# Forecast for 10 years
time_days = [i * 30 for i in range(121)]  # Monthly steps for 10 years
rates = []
cum_production = []
cum = 0.0

for t in time_days:
    # Hyperbolic decline
    q = q_i / (1.0 + b * D_i * t) ** (1.0 / b)
    rates.append(q)

    if t > 0:
        dt = time_days[1]  # Step size
        cum += q * dt
    cum_production.append(cum)

# Print annual summary
print(f"{'Year':>6} {'Rate (Sm3/d)':>14} {'Cum (MSm3)':>12} {'Annual Decline':>16}")
print("-" * 50)
for yr in range(11):
    idx = yr * 12
    if idx < len(rates):
        annual_decline = (1.0 - rates[idx] / rates[max(0, idx - 12)]) * 100 if yr > 0 else 0.0
        print(f"{yr:6d} {rates[idx]:14.0f} {cum_production[idx] / 1e6:12.3f} {annual_decline:15.1f}%")
```

![Production decline profile showing rate and cumulative production over 10 years](figures/decline_curve.png)

## 4.8 Reservoir Uncertainty and Its Impact on Optimization

### 4.8.1 Key Uncertain Parameters

Reservoir parameters are inherently uncertain, and this uncertainty propagates directly into production forecasts:

| Parameter | Typical Uncertainty Range | Impact |
|-----------|--------------------------|--------|
| Permeability | Factor of 2–5 | Directly affects PI and rate |
| Net pay | ±20–50% | Directly affects PI |
| OOIP / OGIP | ±30–50% | Determines reserves and field life |
| Skin factor | ±5 skin units | Affects rate, especially early life |
| Aquifer strength | Factor of 2–10 | Determines pressure support |
| Relative permeability | ±30% | Affects water breakthrough timing |
| Bubble/dew point | ±5–10% | Affects phase behavior and recovery |

### 4.8.2 Probabilistic Reserves

Reserves are classified probabilistically:

- **P90 (Proved):** 90% probability that actual production will equal or exceed this estimate (conservative)
- **P50 (Probable):** 50% probability — the best estimate
- **P10 (Possible):** 10% probability — the optimistic case

For production optimization, the P50 case is typically used for base-case modeling, while P90 and P10 bound the optimization range.

### 4.8.3 Sensitivity to Reservoir Pressure

As the reservoir depletes, the IPR shifts — the maximum rate decreases and the curve changes shape. The production optimization model must track this shift over time:

- **Early life** (high $P_r$): Large rate potential; optimization focuses on facility capacity
- **Mid life** ($P_r$ near $P_b$): Gas-oil ratio increases; compression becomes a constraint
- **Late life** (low $P_r$): Rate is reservoir-limited; artificial lift becomes necessary

## 4.9 Gas Condensate Reservoirs

### 4.9.1 Retrograde Condensation Effect

Gas condensate reservoirs present a unique challenge: as pressure drops below the dew point, liquid condenses in the reservoir pore space. This condensate is typically immobile (trapped by capillary forces) and reduces the gas relative permeability, creating a "condensate bank" near the wellbore.

The productivity reduction can be severe — 50–80% reduction in gas PI — and is not captured by simple IPR models. Accurate modeling requires compositional simulation with relative permeability effects.

### 4.9.2 Mitigation Strategies

- **Pressure maintenance:** Gas injection to keep reservoir pressure above the dew point
- **Lean gas cycling:** Inject lean gas (methane) to revaporize condensate
- **Hydraulic fracturing:** Create large-area flow paths that bypass the condensate bank
- **Reduced drawdown:** Limit well rate to minimize near-wellbore condensation

## 4.10 Multi-Well and Multi-Reservoir Systems

### 4.10.1 Commingled Production

When multiple reservoir zones produce into a common wellbore, the total rate is:

$$
q_{\text{total}} = \sum_{j=1}^{N_z} J_j(P_{r,j} - P_{wf})
$$

subject to the constraint that all zones share the same bottomhole pressure $P_{wf}$.

### 4.10.2 Well Allocation

In a multi-well system with shared facilities, production must be allocated to satisfy:

- Individual well constraints (maximum rate, minimum BHP, maximum GOR, maximum water cut)
- Facility constraints (separator capacity, compressor capacity, water handling capacity)
- Export constraints (pipeline capacity, specification limits)

This allocation problem is the foundation of the short-term production optimization discussed in Chapter 19.

## 4.11 Summary

Key points from this chapter:

- **Darcy's law** and the radial flow equation provide the physical basis for well productivity. The productivity index $J$ encapsulates rock properties, fluid properties, and completion quality.
- **IPR curves** (linear for undersaturated oil, Vogel for saturated oil, back-pressure/LIT for gas) define the rate that the reservoir can deliver at each bottomhole pressure.
- **Reservoir drive mechanisms** (solution gas, gas cap, water drive) determine the rate of pressure decline and ultimate recovery.
- **Material balance** links cumulative production to pressure decline and provides estimates of original hydrocarbons in place.
- **Decline curve analysis** (Arps equations) provides a simple but effective method for forecasting production when detailed reservoir simulation is unavailable.
- **NODAL analysis** provides the framework for integrating reservoir performance with well and facility performance — the operating point is where the IPR and VFP curves intersect.
- **NeqSim** models the reservoir through `SimpleReservoir` and well streams, providing the inflow boundary conditions for process simulation.

## Exercises

1. **Exercise 4.1:** A vertical well has the following properties: $k = 50$ mD, $h = 20$ m, $r_e = 500$ m, $r_w = 0.108$ m, $S = 2$, $B_o = 1.25$, $\mu_o = 1.5$ cP. Calculate the productivity index in Sm³/d/bar. What is the maximum oil rate if $P_r = 300$ bara?

2. **Exercise 4.2:** Using Vogel's method, construct an IPR curve for a well with $P_r = 250$ bara, $P_b = 180$ bara, and $J = 20$ Sm³/d/bar (above bubble point). Plot $P_{wf}$ vs. $q_o$ from 0 to 250 bara.

3. **Exercise 4.3:** A gas well has the following multi-rate test data:

   | $q_g$ (MSm³/d) | $P_{wf}$ (bara) |
   |-----------------|-----------------|
   | 0.5 | 245 |
   | 1.0 | 235 |
   | 1.5 | 220 |
   | 2.0 | 200 |

   If $P_r = 250$ bara, determine the back-pressure equation coefficients $C$ and $n$. What is the absolute open flow (AOF)?

4. **Exercise 4.4:** A volumetric gas reservoir has initial conditions $P_i = 300$ bara, $T = 100$°C, and OGIP = 50 GSm³. Using NeqSim to calculate $Z$ at each pressure, construct a $P/Z$ vs. $G_p$ plot. At what cumulative production does the reservoir pressure drop to 100 bara?

5. **Exercise 4.5:** A well produces 3000 Sm³/d oil initially and declines hyperbolically with $D_i = 0.0008$/day and $b = 0.5$. Calculate the cumulative production after 5 years. What is the rate at that time? How long until the rate drops to the economic limit of 50 Sm³/d?

6. **Exercise 4.6:** Set up a NODAL analysis in NeqSim for a single well flowing into a separator at 40 bara. The well has a Vogel IPR with $q_{o,\max} = 1500$ Sm³/d and $P_r = 200$ bara. The tubing performance (VFP) can be modeled using `PipeBeggsAndBrills`. Find the operating point.

7. **Exercise 4.7 (Advanced):** For a system of three wells producing into a common manifold at 30 bara, each with different IPR parameters, use NeqSim to find the individual well rates that maximize total oil production subject to a total gas handling constraint of 2 MSm³/day.

## References

1. Vogel, J. V. (1968). Inflow performance relationships for solution-gas drive wells. *Journal of Petroleum Technology*, 20(1), 83–92.
2. Rawlins, E. L., & Schellhardt, M. A. (1935). *Backpressure Data on Natural Gas Wells and Their Application to Production Practices*. Monograph 7, USBM.
3. Arps, J. J. (1945). Analysis of decline curves. *Transactions of the AIME*, 160(1), 228–247.
4. Joshi, S. D. (1988). Augmentation of well productivity with slant and horizontal wells. *Journal of Petroleum Technology*, 40(6), 729–739.
5. Schilthuis, R. J. (1936). Active oil and reservoir energy. *Transactions of the AIME*, 118(1), 33–52.
6. Gilbert, W. E. (1954). Flowing and gas-lift well performance. *API Drilling and Production Practice*, 126–157.
7. Mach, J., Proano, E., & Brown, K. E. (1979). A nodal approach for applying systems analysis to the flowing and artificial lift oil or gas well. *Paper SPE 8025*.
8. Ahmed, T. (2016). *Reservoir Engineering Handbook* (5th ed.). Gulf Professional Publishing.
9. Dake, L. P. (1978). *Fundamentals of Reservoir Engineering*. Elsevier.
10. Economides, M. J., Hill, A. D., Ehlig-Economides, C., & Zhu, D. (2013). *Petroleum Production Systems* (2nd ed.). Prentice Hall.


## Figures

![Figure 4.1: Fig01 Ipr Curves](figures/ch04_fig01_ipr_curves.png)

*Figure 4.1: Fig01 Ipr Curves*

![Figure 4.2: Fig02 Gor Vs Pressure](figures/ch04_fig02_gor_vs_pressure.png)

*Figure 4.2: Fig02 Gor Vs Pressure*

![Figure 4.3: Fig03 Density Vs Depth](figures/ch04_fig03_density_vs_depth.png)

*Figure 4.3: Fig03 Density Vs Depth*

![Figure 4.4: Fig04 Rel Perm Curves](figures/ch04_fig04_rel_perm_curves.png)

*Figure 4.4: Fig04 Rel Perm Curves*
