# Well Performance and Artificial Lift

**Running the examples.** Start the source-workspace Python session described in Chapter 1, then run this chapter's Python blocks in reading order. Java blocks form a separate sequence using the same NeqSim build; carry forward objects from preceding Java blocks. The release execution records are in `verification/`; a successful run establishes API compatibility, while physical validation also requires the checks discussed in the text.

<!-- Chapter metadata -->
<!-- Notebooks: ch05_tubing_performance.ipynb, ch05_gas_lift_design.ipynb, ch05_vfp_generation.ipynb -->
<!-- Estimated pages: 22 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Calculate pressure traverses in vertical and deviated wellbores using multiphase flow correlations
2. Describe and apply the Beggs and Brill multiphase flow correlation for well tubing performance
3. Analyze wellhead choke performance under critical and subcritical flow conditions
4. Design continuous gas lift systems including valve spacing and injection rate optimization
5. Understand the fundamentals of ESP and rod pump artificial lift methods
6. Interpret well test data (buildup, drawdown) and extract reservoir parameters
7. Generate VFP tables using NeqSim for integration with reservoir simulators and production optimization models
8. Select tubing sizes based on rate, pressure, and flow regime analysis

## 5.1 Introduction

The well is the conduit between the reservoir and the surface facility. Its performance — specifically, the pressure loss from bottomhole to wellhead — determines how much of the reservoir's delivery potential can actually be captured at the surface. A well with excessive tubing friction, inadequate tubing size, or severe liquid loading may deliver only a fraction of the rate that the IPR would allow.

This chapter develops the theory and NeqSim tools for well performance analysis. We begin with multiphase flow in tubing — the core calculation that determines the tubing pressure profile — then cover choke performance, artificial lift (with emphasis on gas lift), well testing, and VFP table generation.

The link to Chapter 4 is direct: the well's VFP curve intersects the IPR curve to give the operating point (NODAL analysis). The link to Chapter 6 is equally direct: the wellhead pressure must overcome the flowline, riser, and topside back-pressure.

## 5.2 Multiphase Flow in Wellbores

### 5.2.1 The Challenge of Multiphase Flow

Flow in production wells is almost always multiphase — oil, gas, and often water flow simultaneously through the tubing. The simultaneous presence of multiple phases creates several complexities not found in single-phase flow:

- **Slippage:** Gas travels faster than liquid due to buoyancy, creating a difference between the in-situ gas volume fraction and the flowing gas fraction (holdup)
- **Flow patterns:** The phases arrange themselves in different patterns (bubble, slug, churn, annular) depending on rates and properties
- **Changing properties:** As pressure decreases up the well, gas evolves from solution, changing the flow rates, densities, and viscosities continuously
- **Hydrostatic head:** The liquid holdup determines the effective mixture density, which controls the gravity pressure drop — the dominant pressure loss in most wells

### 5.2.2 Pressure Gradient Components

The total pressure gradient in vertical multiphase flow has three components:

$$
-\frac{dP}{ds} = \underbrace{\rho_m g \sin\theta}_{\text{gravity}} + \underbrace{\frac{f \rho_m v_m^2}{2d}}_{\text{friction}} + \underbrace{\rho_m v_m \frac{dv_m}{ds}}_{\text{acceleration}}
$$

where:

- $s$ = distance along the upward flow path [m]; $\theta>0$ uphill; $f$ is the Darcy friction factor. The displayed expression is a homogeneous-mixture balance. Slip correlations use holdup density for gravity and their own friction/acceleration closures, not one interchangeable density for every term.
- $\rho_m$ = homogeneous-mixture density [kg/m³]
- $g$ = gravitational acceleration [m/s²]
- $\theta$ = pipe inclination from horizontal [degrees]
- $f$ = friction factor [-]
- $v_m$ = mixture velocity [m/s]
- $d$ = pipe internal diameter [m]

In a typical production well:

| Component | Fraction of Total $\Delta P$ |
|-----------|----------------------------|
| Gravity (hydrostatic) | 70–90% |
| Friction | 10–25% |
| Acceleration | 0–5% |

The dominance of the gravity term means that the liquid holdup — which determines $\rho_m$ — is the most important parameter to predict accurately.

### 5.2.3 Flow Pattern Maps

The flow pattern in vertical upward flow depends on the superficial velocities of gas and liquid:

| Flow Pattern | Description | Occurrence |
|-------------|-------------|-----------|
| Bubble flow | Discrete gas bubbles in liquid | Low gas rates |
| Slug flow | Alternating liquid slugs and gas pockets (Taylor bubbles) | Moderate gas rates |
| Churn flow | Chaotic oscillating flow | Transition region |
| Annular flow | Gas core with liquid film on wall | High gas rates |

The Taitel-Dukler (1980) and Barnea (1987) flow pattern maps provide mechanistic criteria for predicting the transitions between patterns.

![Figure 5.1: Flow patterns in vertical upward multiphase flow](figures/flow_patterns_vertical.png)

### 5.2.4 Liquid Holdup

The liquid holdup $H_L$ is the fraction of the pipe cross-section occupied by liquid:

$$
H_L = \frac{A_L}{A} = 1 - H_g
$$

The mixture density is then:

$$
\rho_m = \rho_L H_L + \rho_g (1 - H_L)
$$

The holdup differs from the input liquid fraction (no-slip holdup) because of gas-liquid slippage:

$$
\lambda_L = \frac{q_L}{q_L + q_g} \neq H_L
$$

In vertical upward flow, $H_L > \lambda_L$ because gas rises faster than liquid.

## 5.3 The Beggs and Brill Correlation

### 5.3.1 Overview

The Beggs and Brill (1973) correlation is one of the most widely used methods for multiphase pressure drop in pipes. It was developed from laboratory data in pipes of 1-inch and 1.5-inch diameter at various inclinations, and it handles all pipe angles from horizontal to vertical.

The correlation follows these steps:

1. Calculate the Froude number and input liquid fraction
2. Determine the flow pattern (segregated, intermittent, distributed)
3. Calculate the liquid holdup using the flow pattern-specific correlation
4. Correct the holdup for pipe inclination
5. Calculate the friction factor with a multiphase correction
6. Sum the gravity and friction pressure gradients

### 5.3.2 Flow Pattern Determination

The Beggs and Brill flow pattern boundaries depend on two parameters:

$$
N_{Fr} = \frac{v_m^2}{gd} \qquad \text{(Froude number)}
$$

$$
\lambda_L = \frac{v_{sL}}{v_m} \qquad \text{(input liquid fraction)}
$$

where $v_{sL}$ is the superficial liquid velocity, $v_{sg}$ is the superficial gas velocity, and $v_m = v_{sL} + v_{sg}$.

The transition boundaries $L_1$, $L_2$, $L_3$, and $L_4$ are calculated as:

$$
L_1 = 316 \lambda_L^{0.302}
$$

$$
L_2 = 0.0009252 \lambda_L^{-2.4684}
$$

$$
L_3 = 0.10 \lambda_L^{-1.4516}
$$

$$
L_4 = 0.5 \lambda_L^{-6.738}
$$

### 5.3.3 Holdup Calculation

For each flow pattern, the horizontal holdup $H_L(0)$ is calculated from:

$$
H_L(0) = \frac{a \lambda_L^b}{N_{Fr}^c}
$$

where the constants $a$, $b$, $c$ depend on the flow pattern:

| Flow Pattern | $a$ | $b$ | $c$ |
|-------------|-----|-----|-----|
| Segregated | 0.980 | 0.4846 | 0.0868 |
| Intermittent | 0.845 | 0.5351 | 0.0173 |
| Distributed | 1.065 | 0.5824 | 0.0609 |

The inclination correction factor $\psi$ adjusts for non-horizontal pipe:

$$
H_L(\theta) = H_L(0) \cdot \psi
$$

$$
\psi = 1 + C\left[\sin(1.8\theta) - \frac{1}{3}\sin^3(1.8\theta)\right]
$$

where $C$ depends on the flow pattern, liquid velocity number, and Froude number.

### 5.3.4 Friction Factor

The two-phase friction factor uses the Moody friction factor corrected for multiphase effects:

$$
f_{tp} = f_n \cdot e^s
$$

where $f_n$ is the no-slip friction factor (from the Moody chart or Colebrook equation) and $s$ is an empirical correction.

## 5.4 NeqSim Implementation: Well Tubing Performance

### 5.4.1 PipeBeggsAndBrills for Well Flow

NeqSim implements the Beggs and Brill correlation in the `PipeBeggsAndBrills` class, which can model both horizontal pipelines and vertical/deviated wells:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Create reservoir fluid
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 90.0, 200.0)
fluid.addComponent("nitrogen", 0.5)
fluid.addComponent("CO2", 2.0)
fluid.addComponent("methane", 70.0)
fluid.addComponent("ethane", 7.5)
fluid.addComponent("propane", 4.0)
fluid.addComponent("i-butane", 1.0)
fluid.addComponent("n-butane", 2.0)
fluid.addComponent("i-pentane", 0.5)
fluid.addComponent("n-pentane", 0.4)
fluid.addComponent("n-hexane", 0.6)
fluid.addComponent("n-heptane", 3.5)
fluid.addComponent("n-octane", 3.0)
fluid.addComponent("n-nonane", 2.5)
fluid.addComponent("n-decane", 2.0)
fluid.setMixingRule("classic")

# Set up well stream at bottomhole conditions
Stream = jneqsim.process.equipment.stream.Stream
bh_stream = Stream("Bottomhole Stream", fluid)
bh_stream.setFlowRate(20000.0, "kg/hr")  # feasible teaching base; sweep higher rates separately
bh_stream.setTemperature(90.0, "C")
bh_stream.setPressure(200.0, "bara")

# Create vertical well tubing (Beggs and Brill)
PipeBeggsAndBrills = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills
well_tubing = PipeBeggsAndBrills("Production Tubing", bh_stream)
well_tubing.setPipeWallRoughness(2.5e-5)             # m (smooth tubing)
well_tubing.setLength(3000.0)                         # m (measured depth)
well_tubing.setElevation(3000.0)                     # m (positive = outlet above inlet)
well_tubing.setDiameter(0.1016)                       # m (4-inch tubing)
well_tubing.setNumberOfIncrements(50)                 # Calculation segments

# Build and run process
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
process = ProcessSystem()
process.add(bh_stream)
process.add(well_tubing)
process.run()

# Extract results
outlet = well_tubing.getOutletStream()
print(f"Bottomhole pressure: {bh_stream.getPressure('bara'):.1f} bara")
print(f"Wellhead pressure:   {outlet.getPressure('bara'):.1f} bara")
print(f"Pressure drop:       {bh_stream.getPressure('bara') - outlet.getPressure('bara'):.1f} bar")
print(f"Bottomhole temp:     {bh_stream.getTemperature('C'):.1f} C")
print(f"Wellhead temp:       {outlet.getTemperature('C'):.1f} C")
```

### 5.4.2 Pressure Traverse Calculation

To generate a pressure traverse (pressure vs. depth profile), the well can be run at multiple conditions or the internal profile can be examined:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Create fluid
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 90.0, 250.0)
fluid.addComponent("methane", 75.0)
fluid.addComponent("ethane", 8.0)
fluid.addComponent("propane", 4.0)
fluid.addComponent("n-butane", 2.5)
fluid.addComponent("n-pentane", 1.0)
fluid.addComponent("n-heptane", 5.0)
fluid.addComponent("n-octane", 3.0)
fluid.addComponent("n-decane", 1.5)
fluid.setMixingRule("classic")

# Generate VFP data for different flow rates
Stream = jneqsim.process.equipment.stream.Stream
PipeBeggsAndBrills = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

flow_rates = [20000.0, 40000.0, 60000.0, 80000.0, 100000.0]  # kg/hr

print(f"{'Flow Rate (kg/hr)':>18} {'BHP (bara)':>12} {'WHP (bara)':>12} {'dP (bar)':>10}")
print("-" * 54)

for rate in flow_rates:
    stream = Stream("BH Stream", fluid.clone())
    stream.setFlowRate(rate, "kg/hr")
    stream.setTemperature(90.0, "C")
    stream.setPressure(250.0, "bara")

    tubing = PipeBeggsAndBrills("Tubing", stream)
    tubing.setPipeWallRoughness(2.5e-5)
    tubing.setLength(2500.0)
    tubing.setElevation(2500.0)
    tubing.setDiameter(0.1016)
    tubing.setNumberOfIncrements(40)

    process = ProcessSystem()
    process.add(stream)
    process.add(tubing)
    try:
        process.run()
    except Exception as error:
        print("Infeasible fixed-rate tubing case:", str(error).splitlines()[0])
        continue

    whp = tubing.getOutletStream().getPressure("bara")
    dp = 250.0 - whp
    print(f"{rate:18.0f} {250.0:12.1f} {whp:12.1f} {dp:10.1f}")
```

![Figure 5.2: Pressure traverse curves for different tubing flow rates](figures/pressure_traverse.png)

### 5.4.3 Deviated Well Modeling

For deviated wells, the elevation is less than the measured depth. The relationship is:

$$
\text{TVD} = \sum_i \Delta L_i \cos(\alpha_i)
$$

where $\Delta L_i$ is the measured depth increment and $\alpha_i$ is the local inclination from vertical. In NeqSim:

```python
# Deviated well: 3500 m MD but only 2800 m TVD
well_tubing = PipeBeggsAndBrills("Deviated Tubing", bh_stream)
well_tubing.setLength(3500.0)          # Measured depth
well_tubing.setElevation(2800.0)      # True vertical depth (positive = upward)
well_tubing.setDiameter(0.1016)
well_tubing.setPipeWallRoughness(2.5e-5)
well_tubing.setNumberOfIncrements(50)
```

## 5.5 Wellhead Choke Performance

### 5.5.1 Purpose of Wellhead Chokes

Wellhead chokes serve multiple purposes:

- **Rate control:** Regulate the production rate to meet allocation targets
- **Back-pressure management:** Protect downstream equipment from high pressures
- **Sand control:** Limit drawdown to prevent sand production
- **Slugging prevention:** Maintain stable flow by keeping downstream pressure stable
- **Critical flow:** Prevent downstream pressure fluctuations from propagating to the reservoir

### 5.5.2 Critical vs. Subcritical Flow

When the pressure ratio across a choke reaches a critical value, the flow velocity at the choke throat reaches the local speed of sound, and the flow becomes critical (choked). Under critical flow:

- The flow rate depends only on upstream conditions (pressure, temperature, composition)
- Downstream pressure fluctuations cannot propagate upstream
- The critical pressure ratio is approximately:

$$
\frac{P_2}{P_1} = \left(\frac{2}{\gamma + 1}\right)^{\gamma/(\gamma - 1)}
$$

For natural gas with $\gamma \approx 1.3$, the critical pressure ratio is approximately 0.55.

### 5.5.3 Choke Flow Equations

For single-phase gas, the flow through a choke follows:

$$
q_g = C_d A \sqrt{\frac{2\gamma}{\gamma - 1} \frac{P_1}{\rho_1}\left[\left(\frac{P_2}{P_1}\right)^{2/\gamma} - \left(\frac{P_2}{P_1}\right)^{(\gamma+1)/\gamma}\right]}
$$

Here $q_g$ is actual volumetric flow at the upstream state in m³/s, not standard gas volume; $P_1$ is absolute Pa, $\rho_1$ is kg/m³ and $A$ is m². This ideal-gas, constant-$\gamma$ nozzle relation applies above the critical downstream/upstream pressure ratio. Below it, evaluate the bracket at the critical ratio; mass flow then remains capacity-limited. Real control valves require tested flow coefficients and expansion/recovery factors.

For multiphase flow through chokes, the Sachdeva or Perkins correlations are commonly used. NeqSim provides choke modeling through the valve classes:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Choke valve modeling
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 70.0, 80.0)
fluid.addComponent("methane", 80.0)
fluid.addComponent("ethane", 8.0)
fluid.addComponent("propane", 4.0)
fluid.addComponent("n-butane", 2.0)
fluid.addComponent("n-heptane", 3.0)
fluid.addComponent("water", 3.0)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

Stream = jneqsim.process.equipment.stream.Stream
ThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# Well stream upstream of choke
well_stream = Stream("Wellhead Stream", fluid)
well_stream.setFlowRate(50000.0, "kg/hr")
well_stream.setTemperature(70.0, "C")
well_stream.setPressure(80.0, "bara")

# Wellhead choke
choke = ThrottlingValve("WH Choke", well_stream)
choke.setOutletPressure(40.0, "bara")

# Build and run
process = ProcessSystem()
process.add(well_stream)
process.add(choke)
process.run()

# Results
outlet = choke.getOutletStream()
print(f"Upstream pressure:  {well_stream.getPressure('bara'):.1f} bara")
print(f"Downstream pressure: {outlet.getPressure('bara'):.1f} bara")
print(f"Pressure ratio:     {outlet.getPressure('bara') / well_stream.getPressure('bara'):.3f}")
print(f"Downstream temperature: {outlet.getTemperature('C'):.1f} C")
print(f"Temperature drop (JT): {well_stream.getTemperature('C') - outlet.getTemperature('C'):.1f} C")
```

### 5.5.4 Joule-Thomson Cooling

An adiabatic valve with negligible net kinetic/potential-energy change is isenthalpic. A positive Joule–Thomson coefficient gives cooling during pressure reduction; the coefficient can change sign. The following local linear estimate is suitable only for a small pressure interval; use a PH flash over a large letdown:

$$
T_2-T_1 \simeq \mu_{JT}(P_2-P_1)
$$

where $\mu_{JT}$ is the Joule-Thomson coefficient [°C/bar]. For natural gas at typical wellhead conditions, $\mu_{JT}$ is approximately 0.3–0.5 °C/bar. This cooling is important for:

- **Hydrate risk:** The temperature downstream of the choke may fall below the hydrate formation temperature
- **Wax deposition:** Cooling may promote wax formation
- **Phase behavior:** Additional gas may condense from the cooled fluid

## 5.6 Gas Lift

### 5.6.1 Gas Lift Fundamentals

Gas lift is the most common artificial lift method in offshore production. It works by injecting gas into the tubing at depth to reduce the hydrostatic head of the fluid column, thereby lowering the flowing bottomhole pressure and increasing the production rate.

The injected gas reduces the mixture density in the tubing:

$$
\rho_m = \rho_L H_L + \rho_g (1 - H_L)
$$

As the gas injection rate increases, $H_L$ decreases, reducing $\rho_m$ and the hydrostatic pressure drop. However, the friction pressure drop increases with the total gas rate. There is an optimum gas injection rate that minimizes the total wellhead pressure required (or maximizes the well production rate).

### 5.6.2 Gas Lift Performance Curve

The gas lift performance curve shows the well's production rate as a function of gas injection rate. It has a characteristic shape:

1. **No gas lift:** The natural flow rate (may be zero if the well cannot flow naturally)
2. **Increasing injection:** Rate increases as hydrostatic head is reduced
3. **Optimum injection:** Maximum production rate — further injection increases friction more than it reduces hydrostatic pressure
4. **Over-injection:** Rate decreases due to excessive friction (and compression costs increase)

The optimum injection rate is typically determined by:

$$
\frac{\partial q_{\text{oil}}}{\partial q_{\text{inj}}} = \frac{C_{\text{gas}}}{C_{\text{oil}}}
$$

where $C_{\text{gas}}$ is the cost of injection gas and $C_{\text{oil}}$ is the value of incremental oil. For a smooth concave response with positive marginal injection cost and an interior optimum, the economic injection rate is below the rate-maximizing injection. Bound-active wells or nonconcave responses require explicit constrained optimization; equal slopes apply only to unconstrained wells.

![Figure 5.3: Analytical gas-lift illustration with an explicit marginal cost-equivalent assumption](figures/gas_lift_performance.png)

<!-- scientific-illustration:gas_lift_performance.png -->
The declared response has diminishing incremental oil yield. With the stated cost-equivalent slope of 5 m³ oil per thousand standard m³ lift gas, the stationary net-benefit injection is 77.71 thousand standard m³/d. This synthetic trade-off is checked by differentiation; it is not a calibrated lift curve, a current market-price forecast or a native gas-lift allocation result.
<!-- /scientific-illustration -->

### 5.6.3 Gas Lift Valve Spacing

Gas lift valves are installed at intervals along the tubing string. Their spacing determines the:

- **Unloading sequence:** Valves are opened sequentially from top to bottom during startup to displace the kill fluid
- **Operating depth:** The deepest valve (operating valve) is the point where gas enters the tubing during normal production
- **Injection pressure:** Higher injection depth requires higher surface injection pressure

The spacing calculation uses the available injection pressure and the pressure gradient of the gas lift gas and the production fluid. A typical spacing procedure:

1. Plot the static fluid gradient (tubing filled with kill fluid)
2. Plot the injection gas gradient from the surface
3. The first valve is placed where the gas gradient intersects the fluid gradient minus a margin
4. Each subsequent valve is placed based on the operating envelope and a pressure drop margin (typically 20–35 kPa per valve)

Table 5.1 shows typical gas lift design parameters:

| Parameter | Typical Range |
|-----------|--------------|
| Surface injection pressure | 80–180 bara |
| Number of valves | 4–8 |
| Valve spacing | 200–600 m |
| Gas injection rate per well | 20,000–100,000 Sm³/d |
| Gas-liquid ratio increase | 50–200% above natural |
| Operating valve depth | 70–90% of well TVD |

### 5.6.4 Gas Lift Modeling in NeqSim

NeqSim models gas lift by mixing the lift gas with the production stream at the injection point:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Production fluid (low pressure, needs gas lift)
prod_fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 80.0, 120.0)
prod_fluid.addComponent("nitrogen", 0.3)
prod_fluid.addComponent("CO2", 1.5)
prod_fluid.addComponent("methane", 50.0)
prod_fluid.addComponent("ethane", 6.0)
prod_fluid.addComponent("propane", 4.0)
prod_fluid.addComponent("n-butane", 3.0)
prod_fluid.addComponent("n-pentane", 2.0)
prod_fluid.addComponent("n-hexane", 2.5)
prod_fluid.addComponent("n-heptane", 5.0)
prod_fluid.addComponent("n-octane", 5.0)
prod_fluid.addComponent("n-nonane", 4.0)
prod_fluid.addComponent("n-decane", 4.7)
prod_fluid.addComponent("water", 12.0)
prod_fluid.setMixingRule("classic")
prod_fluid.setMultiPhaseCheck(True)

# Gas lift gas (export gas recycled for lift)
lift_gas_fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 40.0, 120.0)
lift_gas_fluid.addComponent("nitrogen", 1.0)
lift_gas_fluid.addComponent("CO2", 2.0)
lift_gas_fluid.addComponent("methane", 90.0)
lift_gas_fluid.addComponent("ethane", 5.0)
lift_gas_fluid.addComponent("propane", 2.0)
lift_gas_fluid.setMixingRule("classic")

Stream = jneqsim.process.equipment.stream.Stream
Mixer = jneqsim.process.equipment.mixer.Mixer
PipeBeggsAndBrills = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# Production stream at gas lift injection point (downhole)
prod_stream = Stream("Production Stream", prod_fluid)
prod_stream.setFlowRate(15000.0, "kg/hr")  # conservative gas-lift teaching base
prod_stream.setTemperature(80.0, "C")
prod_stream.setPressure(120.0, "bara")

# Gas lift injection stream
lift_stream = Stream("Gas Lift", lift_gas_fluid)
lift_stream.setFlowRate(5000.0, "kg/hr")       # ~50,000 Sm3/d
lift_stream.setTemperature(50.0, "C")
lift_stream.setPressure(120.0, "bara")

# Mix at injection point
mixer = Mixer("GL Injection Point")
mixer.addStream(prod_stream)
mixer.addStream(lift_stream)

# Tubing above injection point
tubing = PipeBeggsAndBrills("Upper Tubing", mixer.getOutletStream())
tubing.setPipeWallRoughness(2.5e-5)
tubing.setLength(2000.0)
tubing.setElevation(2000.0)
tubing.setDiameter(0.1016)
tubing.setNumberOfIncrements(40)

# Build and run
process = ProcessSystem()
process.add(prod_stream)
process.add(lift_stream)
process.add(mixer)
process.add(tubing)
process.run()

# Results
whp = tubing.getOutletStream().getPressure("bara")
wht = tubing.getOutletStream().getTemperature("C")
print(f"Wellhead pressure: {whp:.1f} bara")
print(f"Wellhead temperature: {wht:.1f} C")
print(f"Total flow rate: {tubing.getOutletStream().getFlowRate('kg/hr'):.0f} kg/hr")
```

### 5.6.5 Gas Lift Optimization

The gas lift optimization problem involves allocating a limited gas supply among multiple wells to maximize total oil production:

$$
\max \sum_{i=1}^{N_w} q_{o,i}(q_{\text{inj},i})
$$

subject to:

$$
\sum_{i=1}^{N_w} q_{\text{inj},i} \leq Q_{\text{available}}
$$

This is solved by equalizing the marginal oil gain per unit of injected gas across all wells:

$$
\frac{\partial q_{o,1}}{\partial q_{\text{inj},1}} = \frac{\partial q_{o,2}}{\partial q_{\text{inj},2}} = \ldots = \frac{\partial q_{o,N_w}}{\partial q_{\text{inj},N_w}}
$$

This equal-slope criterion is a classic optimization result that ensures no gas can be reallocated from one well to another to increase total production.

## 5.7 Electric Submersible Pumps (ESP)

### 5.7.1 ESP Fundamentals

An ESP is a multistage centrifugal pump installed downhole, powered by an electric motor connected to the surface by an armored cable. Key characteristics:

| Parameter | Typical Range |
|-----------|--------------|
| Rate capacity | 50–80,000 bbl/d |
| Head per stage | 3–15 m |
| Number of stages | 20–500 |
| Motor power | 30–1500 kW |
| Operating temperature | up to 175°C |
| Free gas tolerance | up to 30% (with gas handlers) |
| Run life | 1–5 years |

### 5.7.2 ESP Performance

The ESP pump performance is described by three curves at constant speed:

1. **Head-capacity (H-Q):** Head developed vs. flow rate — decreasing curve
2. **Efficiency (η-Q):** Pump efficiency vs. flow rate — parabolic, with peak at best efficiency point (BEP)
3. **Power (P-Q):** Power consumption vs. flow rate — generally increasing

The ESP is selected to operate near its BEP for maximum efficiency and minimum wear.

### 5.7.3 ESP Sizing

The required number of stages is:

$$
N_{\text{stages}} = \frac{\Delta P_{\text{required}}}{\rho_L g \cdot H_{\text{per stage}}}
$$

where $\Delta P_{\text{required}}$ is the total dynamic head including:

- Friction loss in tubing
- Hydrostatic head from pump depth to wellhead
- Wellhead pressure requirement
- Minus the flowing bottomhole pressure (from IPR)

### 5.7.4 ESP Considerations for Production Optimization

- At fixed speed an ESP operates at the intersection of its head–flow curve with the system curve; changing backpressure changes rate. A variable-speed drive provides an additional control variable
- Gas slugging can cause ESP shutdowns (gas lock)
- Power consumption is a significant operating cost (especially offshore)
- Workover to replace a failed ESP is expensive — run life prediction is critical

## 5.8 Rod Pump (Sucker Rod Pump)

### 5.8.1 Fundamentals

The sucker rod pump is the most common artificial lift method for onshore oil wells. It consists of a surface pumping unit (beam pump), a string of sucker rods, and a downhole positive displacement pump.

Key characteristics:

| Parameter | Typical Range |
|-----------|--------------|
| Rate capacity | 5–5,000 bbl/d |
| Depth limit | up to 4,000 m |
| Power | 5–100 kW |
| GOR tolerance | Limited (gas interference) |
| Primary application | Onshore, low to moderate rate |

### 5.8.2 Rod Pump Performance

The theoretical pump displacement is:

$$
q_{\text{theory}} = \frac{\pi}{4} d_p^2 \cdot S_p \cdot N \cdot 1440
$$

where:

- $d_p$ = plunger diameter [m]
- $S_p$ = effective plunger stroke length [m]
- $N$ = pumping speed [strokes/min]
- 1440 converts min to day

The actual rate is less than theoretical due to gas interference, fluid slippage, and rod stretch:

$$
q_{\text{actual}} = \eta_{\text{vol}} \cdot q_{\text{theory}}
$$

where $\eta_{\text{vol}}$ is the volumetric efficiency (typically 50–90%).

### 5.8.3 NeqSim Implementation: SuckerRodPump

NeqSim models the beam pump directly with the `SuckerRodPump` equipment class (package `neqsim.process.equipment.pump`). The geometry and operating speed are set with fluent setters and the class returns both theoretical and effective displacement plus the polished-rod load used for surface-unit sizing:

```python
SuckerRodPump = jneqsim.process.equipment.pump.SuckerRodPump

rodpump = SuckerRodPump("rod pump", well_stream)
rodpump.setPlungerDiameter(0.0381)          # 1.5 in plunger [m]
rodpump.setStrokeLength(1.68)               # effective stroke [m]
rodpump.setStrokesPerMinute(8.0)
rodpump.setVolumetricEfficiency(0.80)
rodpump.setPumpDepth(1800.0)                # [m]
rodpump.setFluidDensity(850.0)              # [kg/m3]
rodpump.setRodWeightPerLength(35.0 / 9.80665)  # kg/m from assumed buoyant 35 N/m
rodpump.setDischargePressure(100.0)         # bara, above this 80 bara inlet
rodpump.run()

print("Theoretical:", rodpump.getTheoreticalDisplacement("m3/day"))
print("Actual:", rodpump.getActualDisplacement("m3/day"))
print("Polished rod load:", rodpump.getPolishedRodLoad(), "N")
import math
displacement_m3_day = math.pi * 0.0381**2 / 4.0 * 1.68 * 8.0 * 1440.0
assert abs(rodpump.getTheoreticalDisplacement("m3/day") / displacement_m3_day - 1.0) < 1e-12
assert abs(rodpump.getActualDisplacement("m3/day") / displacement_m3_day - 0.80) < 1e-12
assert rodpump.getPolishedRodLoad() > 0.0
```

`getTheoreticalDisplacement` uses actual displacement volume, not a standard-state fluid conversion. The accepted unit strings are `m3/sec` and `m3/day`; an unsupported `Sm3/day` string silently returned m3/s in this source version. The displacement and rod-load checks are geometry/load screening; this one-stream pump object does not establish a complete reservoir-to-surface lift solution. The method evaluates the swept-volume formula above, `getActualDisplacement` applies the volumetric efficiency, and `getPolishedRodLoad` combines fluid load and rod weight for the peak surface load.

### 5.8.4 Hydraulic Jet Pumps in NeqSim

For deviated or high-temperature wells where rod pumps and ESPs are unsuitable, the hydraulic `JetPump` class (package `neqsim.process.equipment.pump`) models a nozzle–throat–diffuser ejector driven by a high-pressure power fluid. It is characterised by the nozzle-to-throat **area ratio** and the power-fluid pressure:

```python
JetPump = jneqsim.process.equipment.pump.JetPump

jet = JetPump("jet pump", prod_stream)
jet.setAreaRatio(0.30)                       # nozzle area / throat area
jet.setPowerFluidPressure(250.0)             # [bara]
jet.setOperatingFlowRatio(0.8)               # produced / power-fluid flow
jet.setPowerFluidDensity(1000.0)             # [kg/m3]
jet.run()

print("Head ratio:", jet.getHeadRatio())
print("Discharge pressure:", jet.getDischargePressure(), "bara")
print("Efficiency:", jet.getEfficiency())
print("Produced rate (actual m3/day):", jet.getProducedRate("m3/day"))
assert prod_stream.getPressure("bara") < jet.getDischargePressure() < 250.0
assert 0.0 < jet.getEfficiency() < 1.0
assert jet.getProducedRate("m3/day") > 0.0
```

The dimensionless `getHeadRatio()` (also available pointwise via `headRatioAt(M)`) and `getEfficiency()` describe the classic jet-pump performance envelope, while `getDischargePressure()` and `getProducedRate()` give the operating point for the surrounding network.

## 5.9 Well Testing

### 5.9.1 Pressure Drawdown Test

A drawdown test measures the pressure response when a well is opened at a constant rate after being shut in. The semi-log analysis for radial flow gives:

$$
P_{wf} = P_i - \frac{162.6 q B \mu}{kh}\left[\log t + \log\frac{k}{\phi \mu c_t r_w^2} - 3.23 + 0.87S\right]
$$

A plot of $P_{wf}$ vs. $\log t$ gives a straight line with slope:

$$
m = \frac{162.6 q B \mu}{kh}
$$

from which $kh$ (permeability-thickness product) is determined.

### 5.9.2 Pressure Buildup Test (Horner Analysis)

A buildup test measures the pressure recovery after shutting in a producing well. The Horner analysis plots $P_{ws}$ vs. $\log[(t_p + \Delta t)/\Delta t]$:

$$
P_{ws} = P_i - \frac{162.6 q B \mu}{kh} \log\frac{t_p + \Delta t}{\Delta t}
$$

where $t_p$ is the producing time before shut-in and $\Delta t$ is the shut-in time. The straight line portion gives:

- **Slope $m$:** Yields $kh$ and hence permeability
- **Intercept:** Yields reservoir pressure $P^*$ (extrapolated to infinite shut-in time)
- **Skin factor:** From the pressure at 1 hour on the straight line:

$$
S = 1.151\left[\frac{P_{1hr} - P_{wf}}{m} - \log\frac{k}{\phi \mu c_t r_w^2} + 3.23\right]
$$

### 5.9.3 Drill Stem Test (DST)

A DST is performed during drilling to evaluate the productivity of a formation. It consists of:

1. Opening the well for a flow period
2. Shutting in for a buildup period
3. Opening again for a second flow period
4. Final shut-in and buildup

The multiple flow and shut-in periods provide redundant data for reservoir characterization and fluid sampling.

### 5.9.4 Pressure Derivative Analysis

The pressure derivative method, introduced by Bourdet et al. (1983), is the primary diagnostic tool for modern well test interpretation. Rather than relying on identifying straight lines on semi-log plots — which can be ambiguous — the pressure derivative reveals flow regimes through characteristic slope patterns on a log-log diagnostic plot.

The pressure derivative is defined as:

$$
\Delta P' = \frac{d(\Delta P)}{d(\ln \Delta t)} = \Delta t \frac{d(\Delta P)}{d(\Delta t)}
$$

On a log-log plot of $\Delta P$ and $\Delta P'$ versus $\Delta t$, various flow regimes appear as characteristic signatures:

| Flow Regime | Pressure Change $\Delta P$ | Derivative $\Delta P'$ |
|-------------|---------------------------|------------------------|
| Wellbore storage | Unit slope (45°) | Unit slope (45°) |
| Radial flow (infinite acting) | Logarithmic increase | Horizontal stabilization |
| Linear flow (fracture) | Half slope (1/2) | Half slope (1/2) |
| Bilinear flow (finite-conductivity fracture) | Quarter slope (1/4) | Quarter slope (1/4) |
| Spherical/hemispherical flow | — | Negative half slope (-1/2) |
| Closed boundary (depletion) | Unit slope (late time) | Unit slope (late time) |
| Constant pressure boundary | Flattening | Derivative drops to zero |
| Sealing fault | Derivative doubles | Step increase |

The diagnostic workflow is:

1. **Plot** $\Delta P$ and $\Delta P'$ on a log-log scale
2. **Identify** flow regimes from the derivative signature
3. **Select** the appropriate analysis model (radial, fractured, dual-porosity, bounded)
4. **Perform** the corresponding straight-line or type-curve analysis
5. **Verify** the interpretation with a simulation match

The radial flow period — identified by a horizontal derivative — is the key segment from which permeability is extracted. The stabilized derivative level $m'$ relates to transmissibility:

$$
kh = \frac{70.6 \, q \, B \, \mu}{m'}
$$

where $m'$ is the stabilized derivative value (in field units with pressure in psi and rate in STB/d).

![Figure 5.4: Log-log diagnostic plot showing wellbore storage, radial flow, and boundary effects](figures/log_log_diagnostic.png)

### 5.9.5 Wellbore Storage and Skin Effects

Wellbore storage occurs because the wellbore itself acts as a fluid container. When the well is shut in at surface, flow from the formation continues because the fluid in the wellbore compresses (or expands) and the liquid level adjusts. This masks the early-time reservoir response.

The wellbore storage coefficient $C$ depends on the dominant storage mechanism:

**Compressibility-dominated storage** (wells filled with single-phase fluid):

$$
C = V_w \, c_w
$$

where $V_w$ is the wellbore volume [bbl] and $c_w$ is the wellbore fluid compressibility [psi$^{-1}$].

**Liquid-level change** (wells with a gas-liquid interface):

$$
C = \frac{144 \, A_{wb}}{5.615 \, \rho_L}
$$

where $A_{wb}$ is the wellbore cross-sectional area [ft²] and $\rho_L$ is the liquid density [lb/ft³]. This mechanism gives a much larger storage coefficient and longer storage duration.

During the wellbore storage period, pressure change is linear in time:

$$
\Delta P = \frac{qB}{24C} \, \Delta t
$$

On the log-log diagnostic plot, both $\Delta P$ and $\Delta P'$ follow a unit-slope line during storage. The end of the storage period occurs at approximately:

$$
\Delta t_{end} \approx \frac{(60 + 3.5S) \, C}{kh / \mu}
$$

where $S$ is the skin factor. Large skin values (damaged wells) or large storage coefficients significantly extend the storage period, potentially masking the radial flow regime entirely in short tests.

The **skin factor** $S$ quantifies the additional pressure drop in the near-wellbore region compared to the ideal case. Positive skin indicates damage or flow restriction; negative skin indicates stimulation (e.g., fracturing). Typical values:

| Condition | Skin Factor $S$ |
|-----------|-----------------|
| Heavily damaged | +10 to +50 |
| Mildly damaged | +2 to +10 |
| Undamaged (open hole) | 0 |
| Acidized | -1 to -3 |
| Hydraulically fractured | -3 to -7 |

The additional pressure drop due to skin is:

$$
\Delta P_{skin} = \frac{141.2 \, q \, B \, \mu}{kh} \cdot S
$$

This pressure drop acts as a fixed "tax" on the well's deliverability and directly reduces the well's IPR. Reducing skin through stimulation can have a dramatic effect on production rate.

### 5.9.6 Fitting Deliverability from Test Data in NeqSim

Once a multi-rate or multi-point test is available, NeqSim converts the raw rate/pressure pairs into a usable inflow model with `WellTestMatcher` (package `neqsim.process.fielddevelopment.integrated`). The matcher fits either a productivity index or a Vogel inflow and returns a `WellDeliverabilityCurve` that can be evaluated at any flowing pressure:

```python
integ = jneqsim.process.fielddevelopment.integrated
WellTestMatcher = integ.WellTestMatcher

matcher = WellTestMatcher()
matcher.addTestPoint(1200.0, 180.0)        # rate [Sm3/day], flowing pressure [bara]
matcher.addTestPoint(2100.0, 150.0)
matcher.addTestPoint(2800.0, 120.0)

match = matcher.fitVogel()                 # or matcher.fitProductivityIndex()
print("Reservoir pressure:", match.getReservoirPressure(), "bara")
print("RMS error:", match.getRmsError())

curve = match.getCurve()                    # WellDeliverabilityCurve
print("AOFP:", curve.getAbsoluteOpenFlowPotential(), "Sm3/day")
print("Rate at 100 bara:", curve.rateAt(100.0), "Sm3/day")
```

A `WellDeliverabilityCurve` can also be built directly from tabulated points
(`WellDeliverabilityCurve(pressureBara[], rateSm3PerDay[])`) or analytically with
`WellDeliverabilityCurve.fromVogel(aofpSm3PerDay, shutInPressureBara)`. The curve exposes
`rateAt(pBara)`, `slopeAt(pBara)`, `getShutInPressure()`, and
`getAbsoluteOpenFlowPotential()`, and is the inflow object consumed by the integrated
production model of Chapter 28.

## 5.10 VFP Table Generation

### 5.10.1 What Are VFP Tables?

Vertical Flow Performance (VFP) tables are multidimensional lookup tables that describe the relationship between well flow rate and the pressure at a reference depth (typically the wellhead or bottomhole) as a function of:

- Flow rate
- Tubing head pressure (or bottomhole pressure)
- Water cut
- Gas-oil ratio (or gas-liquid ratio)
- Artificial lift parameter (gas lift injection rate, ESP speed)

VFP tables are used by reservoir simulators to model well performance without running a full multiphase flow calculation at every timestep.

### 5.10.2 VFP Table Structure

A typical VFP table has the following dimensions:

| Dimension | Typical Values |
|-----------|---------------|
| Flow rate | 5–20 values spanning the rate range |
| Tubing head pressure | 3–8 values |
| Water cut | 0%, 20%, 40%, 60%, 80% |
| GOR | 3–5 values |
| Gas lift rate | 0, 20k, 40k, 60k, 80k, 100k Sm³/d |

The total number of table entries can be large: 15 × 5 × 5 × 4 × 6 = 9,000 pressure calculations.

### 5.10.3 VFP Generation with NeqSim

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import json

# Define fluid
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 90.0, 250.0)
fluid.addComponent("nitrogen", 0.5)
fluid.addComponent("CO2", 2.0)
fluid.addComponent("methane", 70.0)
fluid.addComponent("ethane", 7.0)
fluid.addComponent("propane", 4.0)
fluid.addComponent("n-butane", 2.5)
fluid.addComponent("n-pentane", 1.5)
fluid.addComponent("n-hexane", 1.0)
fluid.addComponent("n-heptane", 4.0)
fluid.addComponent("n-octane", 3.0)
fluid.addComponent("n-decane", 2.5)
fluid.addComponent("water", 2.0)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

# VFP parameters
well_depth = 2500.0          # m TVD
tubing_id = 0.1016           # m (4-inch)
roughness = 2.5e-5           # m
flow_rates = [10000, 20000, 40000, 60000, 80000, 100000]  # kg/hr
whp_values = [20.0, 30.0, 40.0, 50.0]                     # bara

Stream = jneqsim.process.equipment.stream.Stream
PipeBeggsAndBrills = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

vfp_table = []

for whp in whp_values:
    for rate in flow_rates:
        # Set up well from BHP to WHP
        stream = Stream("BH", fluid.clone())
        stream.setFlowRate(rate, "kg/hr")
        stream.setTemperature(90.0, "C")
        stream.setPressure(300.0, "bara")  # Start high, will iterate

        tubing = PipeBeggsAndBrills("Tubing", stream)
        tubing.setPipeWallRoughness(roughness)
        tubing.setLength(well_depth)
        tubing.setElevation(well_depth)
        tubing.setDiameter(tubing_id)
        tubing.setNumberOfIncrements(40)

        process = ProcessSystem()
        process.add(stream)
        process.add(tubing)
        process.run()

        calculated_whp = tubing.getOutletStream().getPressure("bara")
        bhp = stream.getPressure("bara")

        vfp_table.append({
            "flow_rate_kg_hr": rate,
            "whp_target_bara": whp,
            "bhp_bara": bhp,
            "whp_calculated_bara": calculated_whp,
        })

# Print VFP table
print(f"{'Rate (kg/hr)':>14} {'WHP calc (bara)':>16} {'BHP (bara)':>12}")
print("-" * 44)
for entry in vfp_table[:12]:  # First 12 entries
    print(f"{entry['flow_rate_kg_hr']:14.0f} "
          f"{entry['whp_calculated_bara']:16.1f} "
          f"{entry['bhp_bara']:12.1f}")
```

![Figure 5.5: Illustrative pressure-rate curves at four assumed wellhead pressures](figures/vfp_curves.png)

<!-- scientific-illustration:vfp_curves.png -->
The parallel curves illustrate an imposed boundary-pressure shift. They are not calculated or measured VFP tables; the executed well examples include hydraulic solution checks and an explicit operating domain.
<!-- /scientific-illustration -->

### 5.10.4 VFP Tables in Reservoir Simulators

Reservoir simulators (Eclipse, INTERSECT, tNavigator, CMG) use VFP tables as the well model — at each timestep, the simulator looks up the required bottomhole pressure for the current well rate and conditions rather than running a full multiphase flow calculation. This is computationally efficient because:

- A VFP table takes nanoseconds to interpolate, while a Beggs and Brill calculation takes milliseconds
- A field model may have hundreds of wells simulated over thousands of timesteps
- The VFP table encodes the full wellbore hydraulics including tubing geometry, deviation, and artificial lift

The parameters that must be varied to build a complete VFP table depend on the well type:

| Parameter | Oil Producer | Gas Producer | Gas Lift Well | ESP Well |
|-----------|-------------|-------------|--------------|----------|
| Flow rate | Oil rate (STB/d) | Gas rate (Mscf/d) | Oil rate | Oil rate |
| THP | Yes | Yes | Yes | Yes |
| Water cut | Yes (0–95%) | Optional | Yes | Yes |
| GOR | Yes | N/A | Yes | Optional |
| Artificial lift | N/A | N/A | Gas injection rate | Pump frequency |

For a typical oil producer, a well-constructed VFP table might have:
- 10–15 flow rates spanning from near-zero to maximum rate
- 5–8 tubing head pressures covering the operating range
- 5–6 water cut values (0%, 20%, 40%, 60%, 80%, 95%)
- 4–5 GOR values around the expected range

This gives up to 15 × 7 × 6 × 5 = 3,150 entries per table — each requiring a full multiphase flow calculation.

### 5.10.5 VFP Table Quality and Interpolation

The quality of VFP tables directly affects the accuracy of reservoir simulation results. Key quality considerations include:

**Parameter spacing:** Table entries should be spaced to capture the nonlinear behavior of multiphase flow. Finer spacing is needed where the VFP curves have high curvature (at low rates for oil wells, near the transition between liquid-loaded and stable flow for gas wells).

**Interpolation method:** Most reservoir simulators use multi-dimensional linear interpolation in the VFP table. Because multiphase pressure drop is nonlinear with respect to rate, linear interpolation can introduce errors if the rate spacing is too coarse. Some simulators support logarithmic interpolation in rate, which is more accurate.

**Extrapolation hazards:** If the simulator requests a BHP at conditions outside the VFP table range, it must extrapolate — which can produce physically unreasonable results. Common problems include:
- Rate exceeding the maximum table entry → BHP extrapolated to unrealistically low values
- Water cut exceeding the maximum table entry → incorrect BHP, especially at high water cuts where behavior changes rapidly
- GOR below the minimum → BHP may be overestimated (dead oil assumption)

**Table consistency:** A physical multiphase VFP curve can be non-monotonic: decreasing hydrostatic head at low rate competes with increasing friction at high rate. Do not force monotonicity to hide this behavior. Check each branch for hydraulic convergence, units and interpolation error; assess dynamic stability separately before choosing an operating point.

**Updating VFP tables:** As reservoir pressure declines, the fluid composition at the wellbore changes (lower GOR, higher water cut). VFP tables should be regenerated periodically — typically every few years of simulation time — or the table dimensions should cover the full expected range.

## 5.11 Tubing Size Selection

### 5.11.1 The Tubing Size Tradeoff

Tubing size selection involves a fundamental tradeoff:

- **Large tubing:** Lower friction but higher hydrostatic head at low rates (liquid loading risk); also higher capital cost
- **Small tubing:** Higher friction but lower liquid loading risk at low rates; lower cost

The optimal tubing size depends on the expected production profile:

| Tubing OD (inches) | ID (inches) | Typical Application |
|--------------------|-----------|--------------------|
| 2-3/8 | 1.995 | Gas wells, low-rate oil wells |
| 2-7/8 | 2.441 | Standard oil wells |
| 3-1/2 | 2.992 | High-rate oil wells |
| 4-1/2 | 3.958 | Very high-rate wells, gas lift |
| 5-1/2 | 4.892 | HPHT wells, dual completion |

### 5.11.2 Liquid Loading and Turner Critical Velocity

Liquid loading is one of the most significant operational problems in gas well production. It occurs when the gas velocity in the tubing falls below the minimum velocity required to continuously transport liquid (water or condensate) droplets to surface. Turner et al. (1969) developed the critical velocity correlation by modeling the balance between aerodynamic drag and gravity on liquid droplets:

$$
v_{cr} = 6.56 \frac{[\sigma(\rho_l - \rho_g)]^{0.25}}{\rho_g^{0.5}}
$$

where:

- $v_{cr}$ is the critical (minimum) gas velocity [m/s]
- $\sigma$ is the liquid-gas surface tension [N/m]
- $\rho_l$ is the liquid density [kg/m³]
- $\rho_g$ is the gas density [kg/m³]

The coefficient6.56 is the SI conversion of the commonly used1.91 field-unit droplet-screening form, including its approximate20% empirical uplift; without that uplift the coefficient is about 5.46. The field expression uses ft/s, dyn/cm and lb/ft³ and must not be paired with the SI definitions above. For $\sigma=0.06$N/m, $\rho_l=1000$kg/m³ and $\rho_g=50$kg/m³, the uplifted SI expression gives2.55m/s. This is a vertical droplet-screening model, not a general criterion for film reversal, deviated wells or transient unloading.\cite{turner1969}

The corresponding critical gas flow rate for a given tubing size is:

$$
q_{cr} = v_{cr} \cdot \frac{\pi d^2}{4}
$$

If the production rate drops below this critical rate, the well will begin to load up. The symptoms of liquid loading include:

- Erratic wellhead pressure and flow rate (heading)
- Increasing casing-tubing pressure differential
- Declining production rate
- Intermittent flow (well produces in slugs)
- Eventually, the well dies (stops flowing)

The implication for tubing size selection is clear: **smaller tubing maintains higher velocities at lower rates, delaying the onset of liquid loading.** However, smaller tubing creates higher friction at peak rates. The designer must consider the full production life:

| Production Phase | Rate | Preferred Tubing |
|-----------------|------|------------------|
| Early life (high rate) | High | Larger tubing (lower friction) |
| Mid life | Declining | Compromise size |
| Late life (low rate) | Low | Smaller tubing (avoid loading) |

For wells that will experience a wide range of rates, velocity strings (smaller tubing installed inside existing tubing) or plunger lift can extend the well's flowing life.

A useful rule of thumb: select the tubing size such that the expected minimum flowing rate is 20–30% above the Turner critical rate for that tubing diameter.

### 5.11.3 Tubing Size Analysis with NeqSim

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Compare 3.5-inch vs 4.5-inch tubing for the same well
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 90.0, 200.0)
fluid.addComponent("methane", 70.0)
fluid.addComponent("ethane", 8.0)
fluid.addComponent("propane", 4.0)
fluid.addComponent("n-butane", 2.0)
fluid.addComponent("n-heptane", 8.0)
fluid.addComponent("n-decane", 5.0)
fluid.addComponent("water", 3.0)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

Stream = jneqsim.process.equipment.stream.Stream
PipeBeggsAndBrills = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

tubing_sizes = {
    "3.5-inch (ID=0.076m)": 0.0760,
    "4.5-inch (ID=0.102m)": 0.1016,
}

flow_rate = 60000.0  # kg/hr

print(f"{'Tubing Size':>25} {'WHP (bara)':>12} {'dP (bar)':>10}")
print("-" * 50)

for name, diameter in tubing_sizes.items():
    stream = Stream("BH", fluid.clone())
    stream.setFlowRate(flow_rate, "kg/hr")
    stream.setTemperature(90.0, "C")
    stream.setPressure(200.0, "bara")

    tubing = PipeBeggsAndBrills("Tubing", stream)
    tubing.setPipeWallRoughness(2.5e-5)
    tubing.setLength(2500.0)
    tubing.setElevation(2500.0)
    tubing.setDiameter(diameter)
    tubing.setNumberOfIncrements(40)

    process = ProcessSystem()
    process.add(stream)
    process.add(tubing)
    try:
        process.run()
    except Exception as error:
        print("Infeasible fixed-rate tubing case:", str(error).splitlines()[0])
        continue

    whp = tubing.getOutletStream().getPressure("bara")
    dp = 200.0 - whp
    print(f"{name:>25} {whp:12.1f} {dp:10.1f}")
```

## 5.12 Nodal Analysis

### 5.12.1 Concept

Nodal analysis is the systematic method of determining a well's operating point by decomposing the production system into inflow and outflow components at a chosen solution node — typically the bottomhole. The operating point is the intersection of the IPR curve (inflow from reservoir to node) and the VFP curve (outflow from node to surface).

At the solution node (bottomhole), two pressure relationships must be satisfied simultaneously:

**Inflow (IPR):** The relationship between flowing bottomhole pressure $P_{wf}$ and rate $q$, determined by reservoir deliverability (Vogel, Darcy, or composite IPR from Chapter 4).

**Outflow (VFP):** The bottomhole pressure required to lift the fluid to surface at rate $q$, given the tubing geometry, wellhead pressure, and fluid properties (calculated using the Beggs and Brill correlation from Section 5.3).

The operating point is where:

$$
P_{wf,\text{IPR}}(q) = P_{wf,\text{VFP}}(q)
$$

![Figure 5.6: Illustrative nodal intersection for specified inflow and outflow curves](figures/nodal_analysis.png)

<!-- scientific-illustration:nodal_analysis.png -->
The plotted intersection illustrates the common-node pressure condition. It is not a measured well test or a calibrated production forecast; the chapter notebook solves the declared hydraulic case separately.
<!-- /scientific-illustration -->

### 5.12.2 Sensitivity Analysis

Nodal analysis is most powerful as a sensitivity tool — changing one variable at a time to quantify its effect on the operating point:

- **Tubing size:** Larger tubing shifts the VFP curve down (lower required BHP), increasing rate — but only if friction dominates. At low rates, larger tubing may shift the curve up due to liquid holdup.
- **Wellhead pressure:** Lower THP shifts the VFP curve down, directly increasing rate. This shows the benefit of first-stage separator pressure optimization.
- **Water cut:** Higher water cut steepens the VFP curve (heavier fluid column) and shifts the IPR curve down (lower PI), reducing rate significantly.
- **Skin factor:** Higher skin shifts the IPR curve to the left (lower rate for same drawdown). Stimulation shifts it right.
- **Gas lift injection:** Shifts the VFP curve down by reducing mixture density, increasing rate until the friction penalty dominates.

### 5.12.3 Multiple Operating Points

In some cases, particularly for high-GOR oil wells or gas-lifted wells, the IPR and VFP curves may intersect at two points. For the reduced scalar dynamic model $d q/dt=K[P_{\mathrm{IPR}}(q)-P_{\mathrm{VFP}}(q)]$ with $K>0$, a root is locally stable only if $d(P_{\mathrm{IPR}}-P_{\mathrm{VFP}})/dq<0$. This often makes a low-rate root unstable and a higher-rate root stable, but the ordering alone is not a proof. Wellbore storage, multiphase transients and controllers can change the stability; startup must be assessed dynamically.

This has practical implications for well startup: the well may need to be kicked off (e.g., with nitrogen or by briefly increasing gas lift) to pass through the unstable region and reach the stable operating point.

## 5.13 Completion Effects on Well Performance

### 5.13.1 Skin Factor Decomposition

The total skin factor measured from well tests is a composite of several independent components:

$$
S_{total} = S_d + S_{pp} + S_{\theta} + S_{perf} + S_c
$$

where:

- $S_d$ = **Mechanical (damage) skin:** Caused by drilling fluid invasion, fines migration, scale, or asphaltene deposition near the wellbore. Typically 0 to +30.
- $S_{pp}$ = **Partial penetration skin:** When the perforated interval is less than the full reservoir thickness, flow convergence toward the open interval creates additional pressure drop. Can be +5 to +50 for highly partial completions.
- $S_{\theta}$ = **Deviation skin:** Deviated wellbores expose more reservoir area, which is a negative skin contribution. For high-angle wells, $S_{\theta}$ can be -2 to -5.
- $S_{perf}$ = **Perforation skin:** Depends on perforation density (shots/ft), penetration depth, phasing angle, and crushed zone. Can range from -1 (ideal perforations) to +20 (poor perforations in damaged zone).
- $S_c$ = **Completion skin:** Additional pressure drop from screens, gravel packs, or other completion hardware.

Understanding the decomposition is critical for optimization — there is no value in stimulating a well if the skin is dominated by partial penetration (which requires deepening the completion or adding perforations).

### 5.13.2 Gravel Pack and Frac-Pack Completions

In unconsolidated formations prone to sand production, gravel-pack completions are used to prevent sand while maintaining well productivity.

For an annulus replacing formation material, the incremental skin relative to the original formation is $(k/k_{gp}-1)\ln(r_{gp}/r_w)$. If the pack is an additional serial resistance, use the full pack resistance instead; perforation/convergence damage is a separate contribution.

**Gravel pack (GP):** A screen is placed across the interval, and sized gravel is packed between the screen and the formation. The skin contribution from the gravel pack depends on gravel permeability ($k_{gp}$, typically 50–200 D) and annular thickness:

$$
S_{gp} = \left(\frac{k}{k_{gp}}-1\right)\ln\frac{r_{gp}}{r_w}
$$

Because $k_{gp} \gg k$, the gravel-pack skin is usually small (0.5–3) for a properly designed pack. However, impaired gravel (contaminated during placement) can give much higher skin.

**Frac-pack:** A hydraulic fracture is created and propped with gravel, connecting the perforation tunnels to the formation with a high-conductivity channel. Frac-packs typically achieve negative total skin (-1 to -4) and are preferred in moderate-permeability formations (10–500 mD) where standard gravel packs would impose unacceptable skin.

The completion's effect on the IPR is direct: the effective skin factor determines the additional drawdown consumed by the completion. For a well producing at 5,000 STB/d with $kh/\mu = 10,000$ mD·ft/cp, each unit of skin consumes $141.2(5000)B/10000=70.6B$ psi, or $4.87B$ bar, with $B$ in reservoir bbl/STB. For $B=1.2$, this is5.84 bar per skin unit.

### 5.13.3 Impact on IPR

The completion skin modifies the IPR equation. For the Darcy (straight-line) IPR:

$$
q = \frac{kh}{141.2 B \mu \left[\ln(r_e/r_w) - 0.75 + S\right]} (P_r - P_{wf})
$$

The denominator increases with skin, reducing the productivity index. A skin reduction from $S = +10$ to $S = +2$ can increase PI by 30–50% in typical wells, making stimulation (acidizing, hydraulic fracturing) one of the highest-return investments in production optimization.

## 5.14 Flowing Bottomhole Pressure Surveys

### 5.14.1 Gradient Surveys

Flowing gradient surveys measure pressure and temperature at multiple depths in a producing well using a wireline or slickline-conveyed gauge. The resulting pressure-depth profile (gradient survey) provides:

- **Flowing gradient:** The slope $dP/dz$ at each depth, which reflects the local mixture density and friction
- **Gas entry points:** Sudden gradient changes indicate gas influx from gas lift valves or the formation
- **Liquid level:** In wells with a gas cap in the annulus, the gradient transition from gas to liquid indicates the dynamic liquid level
- **Flow regime identification:** Smooth gradients suggest stable flow; erratic gradients suggest slug flow

A flowing gradient survey in a gas-lifted well typically shows:

1. A steep gradient below the operating valve (heavy, unassisted fluid)
2. A gradient change at the gas lift injection depth
3. A lighter gradient above the operating valve (gas-lifted fluid)

### 5.14.2 Interpretation and Flow Regime Identification

The measured pressure gradient can be compared to theoretical gradients for different flow regimes:

$$
\left(\frac{dP}{dz}\right)_{\text{measured}} = \rho_m g + f \frac{\rho_m v_m^2}{2d}
$$

If the measured gradient exceeds the hydrostatic gradient of the wellbore fluid, friction is significant. If it falls below the static liquid gradient, gas is present (reduced holdup).

Gradient surveys taken at different rates provide particularly valuable data for calibrating multiphase flow models — the gradient at each depth varies with rate because the holdup and flow regime change. This data can be used to tune the Beggs and Brill correlation parameters or select between alternative correlations.

### 5.14.3 Production Logging

Production logging tools (PLT) combine pressure and temperature gauges with flow measurement sensors (spinners, capacitance probes, optical probes) to determine the flow contribution from each zone in a commingled completion. The zonal flow rates are essential for:

- Identifying watered-out zones for water shut-off
- Detecting crossflow between zones
- Quantifying zonal productivity for selective stimulation
- Validating reservoir simulation models


<!-- reviewed-notebook-results:start -->
## Reproduced Calculation Results

These examples use the stated fluid recipes and operating assumptions. Curves represent NeqSim calculations unless a caption identifies an analytical illustration, assumed equipment map or synthetic data.

![Figure 5.7: Vertical Lift Performance (VLP) Curves - Different Tubing Sizes](figures/ch05_fig01_vlp_curves.png)

Tubing ID = 3.0 inch: wellhead pressure spans 33.92–122 bara across the plotted cases. Tubing ID = 4.0 inch: wellhead pressure spans 33.83–121.7 bara across the plotted cases.

Tubing pressure loss combines hydrostatic head, wall friction and acceleration; changing diameter alters friction and liquid transport. A diameter that reduces friction at high rate may increase liquid loading or change the low-rate operating branch. Compare feasible IPR intersections for each diameter and reject trials with nonpositive outlet pressure or inconsistent upward elevation sign.

![Figure 5.8: Coupled operating point](figures/ch05_fig02_operating_point.png)

The coupled solution gives 59.518 t/hr at 175.60 bara bottomhole pressure. The calculated wellhead pressure is 49.999 bara against a 50 bara target. Gaps retain undefined phase quantities or hydraulic states that fail the stated operating boundary; they are not interpolated.

The operating point is the rate at which reservoir deliverability and the tubing pressure requirement satisfy the same bottom-hole boundary. The root residual quantifies whether the selected rate actually delivers the required wellhead pressure; visual proximity alone is insufficient. Check the pressure residual, BHP greater than WHP for upward production, and sensitivity to IPR and hydraulic-correlation uncertainty.

![Figure 5.9: Illustrative gas-lift response model. Illustrative analytical gas-lift response, not a NeqSim well simulation](figures/ch05_fig03_gas_lift_optimization.png)

Oil Production Rate spans 2000–5158 bbl/d across the plotted cases.

Injected gas reduces the hydrostatic density of the wellbore mixture while increasing friction and surface gas handling. Improved lift pressure does not by itself establish incremental oil production; a rate gain requires a coupled inflow solution and sufficient gas capacity. Optimize gas allocation using incremental oil or value per unit injection gas, including compression demand and total gas availability.

![Figure 5.10: Wellhead Pressure vs Flow Rate at Different Water Mole Fractions](figures/ch05_fig04_watercut_effect.png)

0 mol% water: wellhead pressure spans 33.83–121.7 bara across the plotted cases. 10 mol% water: wellhead pressure spans 35.75–119.1 bara across the plotted cases.

Increasing water fraction changes mixture density, liquid holdup and friction while reducing the oil fraction of the produced stream. At a fixed total mass rate, oil production and available lifting margin can both deteriorate as water cut rises. Track oil, gas and water rates separately and recompute the coupled well operating point at each water-cut case.

Selected numerical ranges from the plotted cases:

| Quantity / series | Minimum | Maximum | Unit |
|---|---:|---:|---|
| Tubing ID = 3.0 inch: wellhead pressure | 33.92 | 122 | bara |
| NeqSim tubing + reservoir PI: wellhead pressure | 7.808 | 159.1 | bara |
| Oil Production Rate | 2000 | 5158 | bbl/d |
| 0 mol% water: wellhead pressure | 33.83 | 121.7 | bara |

Ranges describe the sampled cases; they are not independent validation tolerances.
<!-- reviewed-notebook-results:end -->

## 5.15 Summary

Key points from this chapter:

- **Multiphase flow** in wells is characterized by gravity-dominated pressure loss, with liquid holdup as the critical parameter. The Beggs and Brill correlation handles all pipe inclinations and flow patterns.
- **Wellhead chokes** regulate production and provide critical flow isolation. The Joule-Thomson cooling across the choke must be considered for hydrate and wax risk assessment.
- **Gas lift** is the most common offshore artificial lift method. The optimization problem is to allocate limited injection gas among wells to maximize total production — solved by the equal-marginal-gain criterion.
- **ESP and rod pumps** provide alternatives for wells that cannot flow naturally. ESPs handle high rates; rod pumps are standard for low-rate onshore wells.
- **Well testing** (drawdown, buildup, DST) provides the permeability, skin, and reservoir pressure needed for IPR construction.
- **VFP tables** capture the well's multiphase flow performance in a lookup table format for use in reservoir simulators and optimization models.
- **Tubing size selection** balances friction loss against liquid loading risk, with the optimal size depending on the expected production rate range.
- **NeqSim's `PipeBeggsAndBrills`** class provides the core multiphase flow calculation for all well performance modeling.



<!-- foundations-scientific-verification -->

### Verification of the worked examples

The completed wellbore trials are checked for finite positive pressure and temperature, material conservation and the upward pressure-loss direction; infeasible imposed-rate trials remain identified. The rod-pump displacement is checked against swept geometry, and the jet-pump example checks pressure and efficiency domains. These reduced lift models do not constitute a coupled power-fluid, reservoir and surface design; the Turner coefficient is separately checked for its stated unit convention.\cite{turner1969}

The calculation and literal-code records are in `verification/scientific_revision/ch05_manuscript_physics.json`; the chapter scope and code hashes are indexed in `foundations_review.json`.

<!-- /foundations-scientific-verification -->

## Exercises

1. **Exercise 5.1:** Using NeqSim, calculate the wellhead pressure for a vertical well producing 50,000 kg/hr through 4-inch tubing from a depth of 3,000 m TVD. The bottomhole pressure is 250 bara and the temperature is 95°C. Use the gas condensate composition from Chapter 2.

2. **Exercise 5.2:** For the well in Exercise 5.1, generate a complete set of pressure traverse curves for flow rates from 10,000 to 100,000 kg/hr. Plot BHP vs. rate for a fixed WHP of 30 bara to create a VFP curve. On the same plot, overlay the Vogel IPR from Chapter 4 to find the operating point.

3. **Exercise 5.3:** Model a wellhead choke that reduces pressure from 80 bara to 30 bara. Calculate the Joule-Thomson temperature drop and determine if the downstream temperature is below the hydrate formation temperature for the gas composition.

4. **Exercise 5.4:** Compare the wellhead pressures for 2-7/8", 3-1/2", and 4-1/2" tubing at flow rates of 20,000, 40,000, 60,000, and 80,000 kg/hr. Identify which tubing size gives the best wellhead pressure at each rate.

5. **Exercise 5.5:** Design a gas lift system for a well with the following data: well TVD = 2,800 m, reservoir pressure = 180 bara, PI = 20 Sm³/d/bar, tubing ID = 4 inches, available gas injection pressure at surface = 120 bara. Calculate the gas lift performance curve (oil rate vs. gas injection rate) and identify the optimum injection rate.

6. **Exercise 5.6:** Generate a VFP table with dimensions: 6 flow rates × 4 WHPs × 3 water cuts (0%, 30%, 60%) for a 3,000 m well with 4-inch tubing. Report the table as a formatted data structure suitable for import into a reservoir simulator.

7. **Exercise 5.7 (Advanced):** For a three-well gas lift system sharing a compressor with 150,000 Sm³/d total injection capacity, each well has a different gas lift performance curve. Determine the optimal allocation of injection gas using the equal-marginal-gain method. Compare with equal allocation and maximum-rate-first allocation.

## References

1. Beggs, H. D., & Brill, J. P. (1973). A study of two-phase flow in inclined pipes. *Journal of Petroleum Technology*, 25(5), 607–617.
2. Hagedorn, A. R., & Brown, K. E. (1965). Experimental study of pressure gradients occurring during continuous two-phase flow in small-diameter vertical conduits. *Journal of Petroleum Technology*, 17(4), 475–484.
3. Turner, R. G., Hubbard, M. G., & Dukler, A. E. (1969). Analysis and prediction of minimum flow rate for the continuous removal of liquids from gas wells. *Journal of Petroleum Technology*, 21(11), 1475–1482.
4. Taitel, Y., & Dukler, A. E. (1980). Modelling flow pattern transitions for steady upward gas-liquid flow in vertical tubes. *AIChE Journal*, 26(3), 345–354.
5. Brown, K. E. (1984). *The Technology of Artificial Lift Methods*, Vol. 4: Production Optimization. PennWell Books.
6. Takacs, G. (2009). *Gas Lift Manual*. PennWell Books.
7. Lea, J. F., Nickens, H. V., & Wells, M. R. (2008). *Gas Well Deliquification* (2nd ed.). Gulf Professional Publishing.
8. Horne, R. N. (1995). *Modern Well Test Analysis: A Computer-Aided Approach* (2nd ed.). Petroway Inc.
9. Economides, M. J., Hill, A. D., Ehlig-Economides, C., & Zhu, D. (2013). *Petroleum Production Systems* (2nd ed.). Prentice Hall.
10. Brill, J. P., & Mukherjee, H. (1999). *Multiphase Flow in Wells*. SPE Monograph Series, Vol. 17.


