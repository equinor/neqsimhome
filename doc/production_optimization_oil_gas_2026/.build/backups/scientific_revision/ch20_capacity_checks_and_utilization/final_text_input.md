# Capacity Checks and Equipment Utilization

<!-- Chapter metadata -->
<!-- Notebooks: ch18_facility_capacity_check.ipynb, ch18_bottleneck_analysis.ipynb, ch18_capacity_sensitivity.ipynb -->
<!-- Estimated pages: 30 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Define and distinguish between design capacity, maximum rated capacity, actual throughput, and utilization factor for process equipment
2. Calculate separator capacity limits using the Souders-Brown equation (gas capacity), liquid retention time, and gas-liquid interface area criteria
3. Determine compressor capacity limits from surge, stonewall, power, and driver constraints, and locate the operating point on a compressor map
4. Evaluate heat exchanger capacity limits including duty, temperature approach, tube velocity, and flow-induced vibration constraints
5. Calculate valve capacity using the $C_v$ coefficient and assess rangeability and percent opening
6. Assess pipeline capacity from erosional velocity, pressure drop, and MAOP (maximum allowable operating pressure) constraints
7. Perform equipment utilization calculations and identify the facility bottleneck as the equipment with the highest utilization factor
8. Build a complete facility capacity model in NeqSim, extract capacity metrics from each equipment item, generate utilization reports, and run sensitivity analyses

---

## 20.1 Introduction

Production optimization requires a thorough understanding of how close each piece of equipment is operating to its maximum capacity. As reservoir conditions change — declining reservoir pressure, increasing water cut, changing gas-oil ratio — the operating point of every equipment item shifts. Equipment that was comfortably within its design envelope at plateau production may become a bottleneck years later, or conversely, equipment designed for peak conditions may be grossly underutilized during the early years.

**Capacity checking** is the systematic process of comparing the actual operating duty of each equipment item against its maximum rated capacity. The ratio of actual to maximum is the **utilization factor**:

$$
U_i = \frac{Q_{i,\text{actual}}}{Q_{i,\text{max}}}
$$

where $U_i$ is the utilization factor for equipment item $i$, $Q_{i,\text{actual}}$ is the actual throughput or duty, and $Q_{i,\text{max}}$ is the maximum allowable throughput or duty.

The highest reported utilization identifies the most loaded declared criterion. It is a throughput bottleneck only if it becomes active along the chosen production change; reservoir supply, lower bounds and coupled constraints can govern instead. If all upper-limit loads scale linearly with a common feed multiplier and ratings stay fixed, a screening estimate is:

$$
Q_{\text{system}} = \frac{Q_{\text{target}}}{\max(U_i)}
$$

The inverse-utilization expression is not valid for nonlinear pressure loss, changing phase split, surge minima or missing constraint coverage. Solve and replay the increased-flow candidate before accepting a facility capacity.

This chapter provides the theoretical foundation for capacity checking across all major equipment types found in oil and gas production facilities, then demonstrates how to implement these checks using NeqSim process simulation.

### 20.1.1 Why Capacity Checks Matter

Capacity checks are performed routinely throughout the life of a production facility for several reasons:

1. **Production forecasting**: Predicting when equipment will become a bottleneck allows proactive debottlenecking or modification planning
2. **Upside evaluation**: Quantifying spare capacity in each equipment item reveals the potential for tie-back of satellite fields or infill wells
3. **Safety compliance**: Ensuring that no equipment operates beyond its maximum rated capacity is a safety and regulatory requirement
4. **Energy efficiency**: Equipment operating far from its design point often has poor efficiency (e.g., compressors operating near surge with significant recycle)
5. **Maintenance planning**: High utilization may accelerate equipment degradation, requiring adjusted inspection intervals

### 20.1.2 Capacity Definitions

It is essential to use precise terminology when discussing capacity:

| Term | Definition | Symbol |
|------|-----------|--------|
| Design capacity | The throughput for which the equipment was originally designed | $Q_{\text{des}}$ |
| Maximum rated capacity | The highest throughput the equipment can achieve while meeting all performance and safety constraints | $Q_{\text{max}}$ |
| Nameplate capacity | The capacity stated on the manufacturer's nameplate (often similar to design capacity) | $Q_{\text{NP}}$ |
| Actual throughput | The current operating throughput | $Q_{\text{act}}$ |
| Available capacity | The difference between maximum rated and actual: $Q_{\text{max}} - Q_{\text{act}}$ | $Q_{\text{avail}}$ |
| Utilization factor | The ratio of actual to maximum rated capacity: $Q_{\text{act}} / Q_{\text{max}}$ | $U$ |
| Turndown ratio | The ratio of maximum to minimum operable throughput: $Q_{\text{max}} / Q_{\text{min}}$ | $TR$ |

The **maximum rated capacity** is generally the binding constraint, not the design capacity. Equipment may be able to operate above its design capacity if all safety, mechanical, and process constraints are satisfied. Conversely, operational constraints (fouling, mechanical wear, control valve limitations) may reduce the effective maximum below the design value.

---

## 20.2 Separator Capacity

Separators are the most common equipment type in oil and gas facilities and often become the bottleneck in aging fields as water cut and gas-oil ratio change. Separator capacity is governed by three independent criteria; the **minimum** of the three determines the overall separator capacity.

### 20.2.1 Gas Handling Capacity — Souders-Brown Equation

The gas handling capacity of a separator is limited by the requirement to prevent liquid carry-over in the gas outlet. The maximum allowable gas velocity is given by the **Souders-Brown equation** (also called the K-factor method):

$$
v_{\text{gas,max}} = K_{\text{SB}} \cdot \sqrt{\frac{\rho_L - \rho_G}{\rho_G}}
$$

where $v_{\text{gas,max}}$ is the maximum allowable superficial gas velocity (m/s), $K_{\text{SB}}$ is the Souders-Brown coefficient (m/s), $\rho_L$ is the liquid density (kg/m³), and $\rho_G$ is the gas density (kg/m³).

The Souders-Brown coefficient depends on the type of separator and internal devices:

| Separator Type | $K_{\text{SB}}$ (m/s) | Typical Application |
|---------------|----------------------|---------------------|
| Vertical, no internals | 0.04–0.06 | Scrubbers, test separators |
| Vertical, wire mesh demister | 0.07–0.11 | Inlet separators, production separators |
| Vertical, vane pack demister | 0.10–0.15 | High-efficiency gas scrubbers |
| Horizontal, half-full | 0.12–0.17 | Production separators, HP separators |
| Horizontal, wire mesh demister | 0.15–0.21 | Two-phase separators |
| Horizontal, vane pack | 0.18–0.25 | High-capacity separators |

The maximum gas flow rate is then:

$$
Q_{\text{gas,max}} = v_{\text{gas,max}} \cdot A_{\text{gas}}
$$

where $A_{\text{gas}}$ is the cross-sectional area available for gas flow. For a horizontal separator with a liquid level occupying a fraction $h/D$ of the diameter, the gas area is calculated from the segment geometry.

The gas capacity utilization factor is:

$$
U_{\text{gas}} = \frac{Q_{\text{gas,actual}}}{Q_{\text{gas,max}}} = \frac{v_{\text{gas,actual}}}{v_{\text{gas,max}}}
$$

When $U_{\text{gas}} > 1.0$, liquid droplet carry-over is expected to increase significantly, leading to poor separation performance.

### 20.2.2 Liquid Handling Capacity — Retention Time

The liquid handling capacity is determined by the requirement to provide sufficient residence time for gas bubbles to rise out of the liquid phase and for water droplets to settle from the oil phase. The minimum retention time depends on the fluid properties and desired separation quality:

$$
t_{\text{ret}} = \frac{V_{\text{liq}}}{Q_{\text{liq}}}
$$

where $V_{\text{liq}}$ is the liquid volume in the separator (m³) and $Q_{\text{liq}}$ is the volumetric liquid flow rate (m³/s).

Typical minimum retention times:

| Service | Oil Retention Time (min) | Water Retention Time (min) |
|---------|------------------------|---------------------------|
| HP separator, light oil (API > 30) | 1–3 | 1–2 |
| HP separator, medium oil (20 < API < 30) | 3–5 | 2–3 |
| LP separator, light oil | 2–4 | 2–3 |
| LP separator, medium/heavy oil | 5–10 | 3–5 |
| Three-phase separator | 5–10 | 5–15 |
| Test separator | 3–5 | 3–5 |

The maximum liquid flow rate is:

$$
Q_{\text{liq,max}} = \frac{V_{\text{liq}}}{t_{\text{ret,min}}}
$$

And the liquid capacity utilization:

$$
U_{\text{liq}} = \frac{Q_{\text{liq,actual}}}{Q_{\text{liq,max}}} = \frac{t_{\text{ret,min}}}{t_{\text{ret,actual}}}
$$

### 20.2.3 Gas-Liquid Interface Area (Degassing Criterion)

For horizontal separators, the gas-liquid interface area also limits capacity. Gas bubbles must traverse the liquid depth and reach the interface before being swept to the liquid outlet. The critical parameter is the **interface area loading**:

$$
\sigma_{\text{GL}} = \frac{Q_{\text{liq}}}{A_{\text{GL}}}
$$

where $A_{\text{GL}}$ is the gas-liquid interface area (m² for a horizontal cylindrical vessel at a given liquid level) and $\sigma_{\text{GL}}$ is the interface area loading (m³/m²·s). The maximum allowable interface loading depends on the oil API gravity and gas-oil ratio:

$$
\sigma_{\text{GL,max}} \approx 0.005 \text{ to } 0.015 \text{ m}^3/\text{m}^2\cdot\text{s}
$$

The interface area for a horizontal cylinder with liquid filling fraction $f = h/D$ is:

$$
A_{\text{GL}} = L \cdot D \cdot \sin\left(\cos^{-1}(1 - 2f)\right)
$$

where $L$ is the separator length (tan-to-tan) and $D$ is the internal diameter.

### 20.2.4 Combined Separator Utilization

The overall separator utilization is the **maximum** of the three individual criteria:

$$
U_{\text{sep}} = \max(U_{\text{gas}}, U_{\text{liq}}, U_{\text{GL}})
$$

The limiting criterion depends on the operating conditions. For a gas-dominated field, $U_{\text{gas}}$ typically governs. For a mature field with high water cut, $U_{\text{liq}}$ often becomes the bottleneck.

### 20.2.5 NeqSim Separator Capacity Calculation

NeqSim provides the physical properties needed to evaluate separator capacity. The following example calculates the gas handling capacity of an HP separator:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import math

# Define wellstream fluid
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 70.0, 65.0)
fluid.addComponent("nitrogen", 0.005)
fluid.addComponent("CO2", 0.025)
fluid.addComponent("methane", 0.600)
fluid.addComponent("ethane", 0.080)
fluid.addComponent("propane", 0.045)
fluid.addComponent("i-butane", 0.015)
fluid.addComponent("n-butane", 0.025)
fluid.addComponent("i-pentane", 0.012)
fluid.addComponent("n-pentane", 0.010)
fluid.addComponent("n-hexane", 0.008)
fluid.addComponent("n-heptane", 0.005)
fluid.addComponent("n-octane", 0.003)
fluid.addComponent("water", 0.167)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

# Create process model
feed = jneqsim.process.equipment.stream.Stream("Wellstream", fluid)
feed.setFlowRate(2500.0, "kg/hr")
feed.setTemperature(70.0, "C")
feed.setPressure(65.0, "bara")

separator = jneqsim.process.equipment.separator.ThreePhaseSeparator(
    "HP Separator", feed
)

process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(separator)
process.run()

# Extract physical properties for capacity calculation
gas_out = separator.getGasOutStream()
oil_out = separator.getOilOutStream()
water_out = separator.getWaterOutStream()

rho_gas = gas_out.getFluid().getDensity("kg/m3")
rho_oil = oil_out.getFluid().getDensity("kg/m3")
rho_water = water_out.getFluid().getDensity("kg/m3")

Q_gas_actual = gas_out.getFluid().getFlowRate("m3/sec")
Q_oil_actual = oil_out.getFluid().getFlowRate("m3/sec")
Q_water_actual = water_out.getFluid().getFlowRate("m3/sec")

print(f"Gas density:   {rho_gas:.2f} kg/m³")
print(f"Oil density:   {rho_oil:.2f} kg/m³")
print(f"Water density: {rho_water:.2f} kg/m³")

# Separator geometry (example: horizontal, ID=2.4 m, L=8.0 m)
D_sep = 2.4   # m, internal diameter
L_sep = 8.0   # m, tan-to-tan length
liquid_fraction = 0.50  # liquid fills 50% of diameter

# Gas cross-sectional area (upper half for 50% liquid level)
A_gas = (math.pi * D_sep**2 / 4.0) * (1.0 - liquid_fraction)

# Souders-Brown calculation
K_SB = 0.15  # m/s, horizontal separator with wire mesh demister
v_gas_max = K_SB * math.sqrt((rho_oil - rho_gas) / rho_gas)
Q_gas_max = v_gas_max * A_gas

v_gas_actual = Q_gas_actual / A_gas
U_gas = Q_gas_actual / Q_gas_max

print(f"\n--- Gas Capacity ---")
print(f"Max gas velocity:  {v_gas_max:.2f} m/s")
print(f"Actual gas vel.:   {v_gas_actual:.2f} m/s")
print(f"Gas utilization:   {U_gas:.1%}")

# Liquid retention time calculation
V_liquid = (math.pi * D_sep**2 / 4.0) * liquid_fraction * L_sep
Q_liq_total = Q_oil_actual + Q_water_actual
t_ret_actual = V_liquid / Q_liq_total if Q_liq_total > 0 else float('inf')
t_ret_min = 180.0  # seconds (3 minutes)
U_liq = t_ret_min / t_ret_actual if t_ret_actual > 0 else 0

print(f"\n--- Liquid Capacity ---")
print(f"Liquid volume:     {V_liquid:.2f} m³")
print(f"Actual ret. time:  {t_ret_actual:.1f} s")
print(f"Min ret. time:     {t_ret_min:.1f} s")
print(f"Liquid utilization: {U_liq:.1%}")

# Overall separator utilization
U_sep = max(U_gas, U_liq)
bottleneck = "Gas capacity" if U_gas > U_liq else "Liquid capacity"
print(f"\n--- Overall ---")
print(f"Separator utilization: {U_sep:.1%}")
print(f"Limiting criterion:    {bottleneck}")
```

This pattern — running a NeqSim process simulation, then extracting fluid properties to compute equipment-specific capacity metrics — is the fundamental approach used throughout this chapter.

![Separator capacity diagram showing gas velocity profile and liquid retention zones](figures/separator_capacity_diagram.png)

---

## 20.3 Compressor Capacity

Compressor capacity limits are more complex than separator limits because compressors have multiple simultaneous constraints. A compressor operating point must lie within the **compressor operating envelope** bounded by surge, stonewall (choke), maximum speed, minimum speed, and power limits.

### 20.3.1 Surge Limit

Surge occurs when the volumetric flow rate through the compressor falls below the minimum required for stable aerodynamic operation. At surge, the pressure ratio across the compressor temporarily collapses, flow reverses momentarily, then reestablishes — this cycle repeats at 1–10 Hz causing severe mechanical damage.

The surge line on a compressor map defines the minimum flow at each speed. The **surge margin** is defined as:

$$
SM = \frac{Q_{\text{actual}} - Q_{\text{surge}}}{Q_{\text{surge}}} \times 100\%
$$

A typical minimum surge margin is 10%, meaning the actual flow must be at least 10% above the surge flow at the current speed. The surge utilization factor (proximity to surge) is:

$$
U_{\text{surge}} = \frac{Q_{\text{surge}} \cdot (1 + SM_{\text{min}}/100)}{Q_{\text{actual}}}
$$

When $U_{\text{surge}} > 1.0$, the compressor would operate below the minimum surge margin, requiring recycle to maintain stable operation.

### 20.3.2 Stonewall (Choke) Limit

Stonewall occurs when the gas velocity at the compressor impeller throat approaches sonic velocity. Beyond this point, further increases in inlet flow produce no additional increase in discharge pressure. The choke boundary depends on speed, gas properties and corrected map coordinates. Use the applicable vendor map; a single speed-independent flow limit is only a declared screening approximation.

The stonewall utilization is:

$$
U_{\text{SW}} = \frac{Q_{\text{actual}}}{Q_{\text{stonewall}}}
$$

### 20.3.3 Power Limit

The absorbed shaft power must not exceed the driver (gas turbine or electric motor) rated power:

$$
W_{\text{shaft}} = \frac{\dot{m} \cdot \Delta h_{\text{isen}}}{\eta_{\text{isen}}} + W_{\text{mech\ losses}}
$$

where $\dot{m}$ is the mass flow rate, $\Delta h_{\text{isen}}$ is the isentropic enthalpy rise, $\eta_{\text{isen}}$ is the isentropic efficiency, and $W_{\text{mech\ losses}}$ includes bearing and seal losses (typically 1–3% of shaft power).

The power utilization is:

$$
U_{\text{power}} = \frac{W_{\text{shaft}}}{W_{\text{driver,max}}}
$$

For gas turbine drivers, $W_{\text{driver,max}}$ varies with ambient temperature — a gas turbine rated at 30 MW at ISO conditions (15°C) may only deliver 25 MW at 35°C. This is called **ambient temperature derating** and is a crucial consideration for hot climates:

$$
W_{\text{GT,derated}} = W_{\text{GT,ISO}} \cdot \left(1 - \alpha \cdot (T_{\text{amb}} - T_{\text{ISO}})\right)
$$

where $\alpha$ is the derating coefficient, typically 0.5–0.8% per °C for aeroderivative gas turbines.

### 20.3.4 Speed Limits

Centrifugal compressors have a maximum speed (set by mechanical stress in the impeller) and a minimum speed (below which aerodynamic instabilities occur). The speed range typically spans from 70% to 105% of design speed. At any given speed, the compressor has a unique head-flow characteristic.

### 20.3.5 Available Head vs Required Head

The compressor must deliver sufficient head to overcome the system resistance. The **polytropic head** is:

$$
H_p = Z_{\text{avg}} \cdot R \cdot T_1 \cdot \frac{n}{n-1} \cdot \left[\left(\frac{P_2}{P_1}\right)^{(n-1)/n} - 1\right] \cdot \frac{1}{M}
$$

where $n$ is the polytropic exponent, $R$ is the universal gas constant, $T_1$ is the suction temperature, $M$ is the molecular weight, and $Z_{\text{avg}}$ is the average compressibility factor.

The system resistance curve (required head vs flow at a given suction and discharge pressure) intersects the compressor characteristic curve at the operating point. As conditions change, the required head changes and the operating point moves.

The head utilization factor is:

$$
U_{\text{head}} = \frac{H_{p,\text{required}}}{H_{p,\text{available}}}
$$

### 20.3.6 Combined Compressor Utilization

The overall compressor utilization considers all constraints:

$$
U_{\text{comp}} = \max(U_{\text{surge}}, U_{\text{SW}}, U_{\text{power}}, U_{\text{head}})
$$

In practice, the power limit is often the binding constraint for export compressors, while the surge limit governs during turndown operations.

### 20.3.7 NeqSim Compressor Capacity Analysis

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define suction gas
suction_gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, 30.0)
suction_gas.addComponent("nitrogen", 0.01)
suction_gas.addComponent("CO2", 0.02)
suction_gas.addComponent("methane", 0.88)
suction_gas.addComponent("ethane", 0.06)
suction_gas.addComponent("propane", 0.02)
suction_gas.addComponent("n-butane", 0.01)
suction_gas.setMixingRule("classic")

# Build the compressor model
feed = jneqsim.process.equipment.stream.Stream("Compressor Suction", suction_gas)
feed.setFlowRate(5.0, "MSm3/day")
feed.setTemperature(30.0, "C")
feed.setPressure(30.0, "bara")

compressor = jneqsim.process.equipment.compressor.Compressor("Export Compressor", feed)
compressor.setOutletPressure(120.0)  # bara
compressor.setPolytropicEfficiency(0.78)

process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(compressor)
process.run()

# Extract compressor performance
power_actual = compressor.getPower() / 1e6  # MW
head_actual = compressor.getPolytropicFluidHead()  # kJ/kg, solved fluid head
T_discharge = compressor.getOutletStream().getTemperature("C")
compression_ratio = 120.0 / 30.0

print(f"Compression ratio:    {compression_ratio:.2f}")
print(f"Shaft power:          {power_actual:.2f} MW")
print(f"Discharge temperature: {T_discharge:.1f} °C")

# Capacity assessment
W_driver_max = 15.0  # MW, gas turbine rating at 15°C
T_ambient = 25.0     # °C, current ambient
alpha_derate = 0.006 # 0.6% per °C
W_driver_derated = W_driver_max * (1.0 - alpha_derate * (T_ambient - 15.0))

U_power = power_actual / W_driver_derated
print(f"\nDriver rated power (ISO):     {W_driver_max:.1f} MW")
print(f"Driver derated power ({T_ambient}°C): {W_driver_derated:.2f} MW")
print(f"Power utilization:            {U_power:.1%}")

# Surge margin check (using typical surge flow = 70% of design flow)
Q_design = 5.5  # MSm3/day, design point
Q_surge = 0.70 * Q_design  # typical surge flow at design speed
Q_actual = 5.0
SM = (Q_actual - Q_surge) / Q_actual * 100
SM_min = 10.0  # % minimum surge margin

print(f"\nSurge flow:      {Q_surge:.2f} MSm³/day")
print(f"Surge margin:    {SM:.1f}%")
print(f"Min surge margin: {SM_min:.1f}%")
print(f"Surge OK:         {'Yes' if SM > SM_min else 'NO — RECYCLE REQUIRED'}")
```

![Compressor operating map showing surge line, stonewall, and operating point](figures/compressor_capacity_map.png)

---

## 20.4 Heat Exchanger Capacity

Heat exchangers have several capacity constraints that must be simultaneously satisfied.

### 20.4.1 Thermal Duty Limit

The maximum thermal duty depends on the heat transfer area, overall heat transfer coefficient, and available temperature driving force:

$$
Q_{\text{max}} = U \cdot A \cdot \Delta T_{\text{LMTD,max}}
$$

where $U$ is the overall heat transfer coefficient (W/m²·K), $A$ is the heat transfer area (m²), and $\Delta T_{\text{LMTD,max}}$ is the log mean temperature difference at maximum conditions.

The thermal duty utilization is:

$$
U_{\text{duty}} = \frac{Q_{\text{actual}}}{Q_{\text{max}}}
$$

Fouling reduces the effective $U$ over time, progressively increasing the duty utilization even at constant throughput.

### 20.4.2 Temperature Approach Limit

The **minimum temperature approach** (MTA) — the smallest temperature difference between the two streams at any point in the exchanger — must remain above a minimum value to ensure stable heat transfer and avoid temperature cross:

$$
\Delta T_{\mathrm{end,min}}=\min(T_{h,in}-T_{c,out},T_{h,out}-T_{c,in})
$$

For a single-phase countercurrent exchanger with constant heat capacities, the minimum occurs at one terminal. With phase change or variable heat capacity, inspect the internal temperature profile for a tighter pinch.

Illustrative approach targets, to be replaced by service-specific design requirements:

| Service | Minimum Temperature Approach (°C) |
|---------|----------------------------------|
| Gas-gas | 10–20 |
| Gas-liquid | 5–15 |
| Liquid-liquid | 5–10 |
| Condensing (shell side) | 3–5 |
| Reboiler | 10–20 |

When the temperature approach drops below the minimum, the exchanger is at its thermal capacity limit even if the mechanical design can handle more flow.

### 20.4.3 Tube Velocity Limit

Excessive tube-side velocity causes erosion, vibration, and excessive pressure drop. The maximum allowable velocity depends on the fluid and tube material:

Select tube velocity limits from the material, service, fouling/solids loading, pressure drop and vibration assessment. The petroleum-piping $C/\sqrt{\rho}$ screening rule is not a universal heat-exchanger tube limit.

Illustrative velocity ranges:

| Fluid | Maximum Tube Velocity (m/s) |
|-------|----------------------------|
| Cooling water | 1.5–2.5 |
| Hydrocarbon liquid | 1.0–3.0 |
| Process gas | 15–30 |
| Steam (condensing) | 10–25 |

The velocity utilization is:

$$
U_{\text{vel}} = \frac{v_{\text{tube,actual}}}{v_{\text{tube,max}}}
$$

### 20.4.4 Shell-Side Flow-Induced Vibration

On the shell side, cross-flow over tube bundles can excite tubes into vibration if the flow velocity exceeds a critical threshold. Matching the vortex-shedding frequency to a tube natural frequency gives a resonance-screening velocity:

$$
v_{\text{crit}} = \frac{f_n \cdot d_o}{S_t}
$$

where $f_n$ is the tube natural frequency (Hz), $d_o$ is the tube outside diameter (m), and $S_t$ is the Strouhal number (typically 0.2–0.5 depending on geometry).

This condition alone does not establish safety: fluidelastic instability, turbulent buffeting, damping and support geometry need separate checks. Flow-induced vibration can cause rapid tube failure and is typically checked during design against TEMA guidelines. The vibration utilization is:

$$
U_{\text{vib}} = \frac{v_{\text{shell,actual}}}{v_{\text{crit}}}
$$

### 20.4.5 Pressure Drop Limit

Excessive pressure drop across the heat exchanger may limit throughput, particularly for low-pressure gas services. The maximum allowable pressure drop is set during design and depends on the available system pressure and downstream equipment requirements.

$$
U_{\Delta P} = \frac{\Delta P_{\text{actual}}}{\Delta P_{\text{max,allow}}}
$$

### 20.4.6 Combined Heat Exchanger Utilization

$$
U_{\text{HX}} = \max(U_{\text{duty}}, U_{\text{vel}}, U_{\text{vib}}, U_{\Delta P})
$$

In many practical situations, fouling-induced duty limitation is the governing constraint, particularly for crude oil coolers and produced water coolers.

### 20.4.7 NeqSim Heat Exchanger Capacity Check

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Hot side: process gas to be cooled
hot_fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 90.0, 50.0)
hot_fluid.addComponent("methane", 0.85)
hot_fluid.addComponent("ethane", 0.08)
hot_fluid.addComponent("propane", 0.04)
hot_fluid.addComponent("n-butane", 0.02)
hot_fluid.addComponent("n-pentane", 0.01)
hot_fluid.setMixingRule("classic")

hot_stream = jneqsim.process.equipment.stream.Stream("Hot Gas", hot_fluid)
hot_stream.setFlowRate(50000.0, "kg/hr")
hot_stream.setTemperature(90.0, "C")
hot_stream.setPressure(50.0, "bara")

# Cold side: cooling medium
cold_fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 20.0, 5.0)
cold_fluid.addComponent("water", 1.0)
cold_fluid.setMixingRule("classic")

cold_stream = jneqsim.process.equipment.stream.Stream("Cooling Water", cold_fluid)
cold_stream.setFlowRate(80000.0, "kg/hr")
cold_stream.setTemperature(20.0, "C")
cold_stream.setPressure(5.0, "bara")

# Heat exchanger
hx = jneqsim.process.equipment.heatexchanger.HeatExchanger("Gas Cooler")
hx.setFeedStream(0, hot_stream)
hx.setFeedStream(1, cold_stream)
hx.setUAvalue(50000.0)  # W/K, overall UA

process = jneqsim.process.processmodel.ProcessSystem()
process.add(hot_stream)
process.add(cold_stream)
process.add(hx)
process.run()

# Extract results
T_hot_out = hx.getOutStream(0).getTemperature("C")
T_cold_out = hx.getOutStream(1).getTemperature("C")
duty = hx.getDuty() / 1e3  # kW

# Temperature approach (countercurrent)
DT_hot_end = hot_stream.getTemperature("C") - T_cold_out
DT_cold_end = T_hot_out - cold_stream.getTemperature("C")
DT_min = min(DT_hot_end, DT_cold_end)

print(f"Duty:              {duty:.1f} kW")
print(f"Hot inlet:         {hot_stream.getTemperature('C'):.1f} °C")
print(f"Hot outlet:        {T_hot_out:.1f} °C")
print(f"Cold inlet:        {cold_stream.getTemperature('C'):.1f} °C")
print(f"Cold outlet:       {T_cold_out:.1f} °C")
print(f"Min temp approach: {DT_min:.1f} °C")

# Capacity assessment
UA_design = 50000.0  # W/K (clean)
UA_fouled = UA_design * 0.80  # 20% fouling reduction
DT_min_limit = 5.0  # °C

U_duty = duty / (UA_design * 50.0 / 1e3)  # simplified check
U_approach = DT_min_limit / DT_min if DT_min > 0 else float('inf')

print(f"\nApproach utilization: {U_approach:.1%}")
print(f"Approach OK: {'Yes' if DT_min > DT_min_limit else 'NO — at thermal limit'}")
```

---

## 20.5 Valve Capacity

Control valves are critical capacity elements — a valve that is fully open (100% travel) cannot provide any further control action, and the system capacity is limited by the valve flow coefficient.

### 20.5.1 Valve Flow Coefficient ($C_v$)

The flow coefficient $C_v$ relates the valve flow rate to the pressure drop across it. For liquids:

$$
Q = C_v \cdot f(\ell) \cdot \sqrt{\frac{\Delta P}{\rho / \rho_{\text{ref}}}}
$$

For the customary US $C_v$ convention, use $Q$ in US gal/min and $\Delta P$ in psi with specific gravity relative to water; SI flow needs the corresponding conversion factor. Here $f(\ell)$ is the valve characteristic function at travel (opening) $\ell$, $\Delta P$ is the pressure drop, and $\rho_{\text{ref}}$ is the reference density (water at 15°C).

For gases (ISA/IEC 60534 method):

$$
W = N_8 \cdot C_v \cdot F_P \cdot Y \cdot \sqrt{x_{\mathrm{sizing}} \cdot \rho_1 \cdot P_1}
$$

Here $x_{\mathrm{sizing}}=\min(\Delta P/P_1,F_kx_{TP})$ accounts for choking; $Y$, $F_P$, $x_{TP}$ and the unit constant must come from the selected valve-sizing convention. $W$ is the mass flow rate, $N_8$ is a numerical constant, $F_P$ is the piping geometry factor, $Y$ is the expansion factor, $x$ is the pressure drop ratio $\Delta P / P_1$, and $\rho_1$ is the upstream density.

### 20.5.2 Percent Opening and Rangeability

The **percent opening** indicates how far the valve is open:

$$
f(\ell)=\frac{C_{v,\mathrm{required}}}{C_{v,\mathrm{max}}},\qquad \ell=f^{-1}\left(\frac{C_{v,\mathrm{required}}}{C_{v,\mathrm{max}}}\right)
$$

Only a linear inherent characteristic gives travel equal to the $C_v$ ratio. Evaluate the installed characteristic, trim, noise/cavitation and required authority; 20–80% is an illustrative preferred operating band, not a universal rule \cite{emerson2023valves}. Outside this range:

- **Below 20%**: Poor controllability — small changes in opening produce large changes in flow; valve plug may chatter
- **Above 80%**: Approaching full open — limited remaining control authority; cannot handle upsets

The valve capacity utilization is:

$$
U_{\text{valve}} = \frac{C_{v,\text{required}}}{C_{v,\text{max}}}
$$

### 20.5.3 Rangeability

The **rangeability** of a valve is the ratio of maximum to minimum controllable flow:

$$
R = \frac{Q_{\text{max,controllable}}}{Q_{\text{min,controllable}}}
$$

Typical rangeabilities:

| Valve Type | Typical Rangeability |
|-----------|---------------------|
| Globe, equal percentage | 30:1 to 50:1 |
| Globe, linear | 20:1 to 30:1 |
| Butterfly | 15:1 to 20:1 |
| Ball, V-port | 100:1 to 200:1 |
| Ball, full bore | 10:1 to 15:1 |

### 20.5.4 Choked Flow (Critical Flow)

For gas service, the flow becomes choked when the pressure drop ratio exceeds a critical value:

$$
x_{\mathrm{choked}}=\frac{\Delta P_{\mathrm{choked}}}{P_1}=F_kx_{TP}
$$

where $F_k$ is the ratio of specific heats factor and $x_{TP}$ is the terminal pressure drop ratio. Beyond this point, increasing the pressure drop produces no additional flow — the valve is at its absolute maximum capacity.

### 20.5.5 Wellhead Choke Capacity

Wellhead chokes are a special case of flow control devices that limit well production rate. Chokes may be fixed (bean type) or adjustable. The flow through a choke is described by:

$$
Q = C_d \cdot A \cdot \sqrt{\frac{2 \cdot \Delta P}{\rho}}
$$

where $C_d$ is the discharge coefficient (typically 0.75–0.85 for subsea chokes) and $A$ is the choke bean area. For critical (sonic) flow through the choke:

$$
\frac{P_2}{P_1} \leq \left(\frac{2}{k+1}\right)^{k/(k-1)}
$$

the flow rate depends only on upstream conditions and is independent of downstream pressure. This is the maximum flow capacity of the choke.

The choke utilization is:

$$
U_{\text{choke}} = \frac{Q_{\text{actual}}}{Q_{\text{choked}}}
$$

If $U_{\text{choke}} \approx 1.0$, the well is producing at maximum choke capacity and cannot increase production without changing the choke size.

### 20.5.6 NeqSim Valve Capacity Check

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Check control valve capacity
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 60.0, 65.0)
fluid.addComponent("methane", 0.85)
fluid.addComponent("ethane", 0.08)
fluid.addComponent("propane", 0.04)
fluid.addComponent("n-butane", 0.03)
fluid.setMixingRule("classic")

feed = jneqsim.process.equipment.stream.Stream("Valve Inlet", fluid)
feed.setFlowRate(3.0, "MSm3/day")
feed.setTemperature(60.0, "C")
feed.setPressure(65.0, "bara")

valve = jneqsim.process.equipment.valve.ThrottlingValve("HP-LP Valve", feed)
valve.setOutletPressure(25.0)  # Large pressure drop

ps = jneqsim.process.processmodel.ProcessSystem()
ps.add(feed)
ps.add(valve)
ps.run()

# Check for choked flow condition
P_in = feed.getPressure("bara")
P_out = valve.getOutletStream().getPressure("bara")
ratio = P_out / P_in

print(f"Inlet pressure:    {P_in:.1f} bara")
print(f"Outlet pressure:   {P_out:.1f} bara")
print(f"Pressure ratio:    {ratio:.3f}")
print(f"Outlet temperature: {valve.getOutletStream().getTemperature('C'):.1f} °C")

if ratio < 0.55:
    print("WARNING: Close to or at choked flow conditions!")
else:
    print("Subcritical flow — valve has margin for additional pressure drop")
```

---

## 20.6 Pipeline Capacity

Pipeline capacity is governed by pressure drop, velocity limits, and the maximum allowable operating pressure (MAOP).

### 20.6.1 Erosional Velocity

The API RP 14E density-based velocity expression is an empirical screening criterion, not a general erosion-rate model or assurance against sand erosion/corrosion:

$$
v_{\text{eros}} = \frac{C}{\sqrt{\rho_m}}
$$

The customary expression uses velocity in ft/s and density in lb/ft³. If an illustrative $C_{US}=150$ is selected, convert consistently: $v_{SI}=0.3048C_{US}\sqrt{16.01846}/\sqrt{\rho_{SI}}$ in m/s. A bare value of 150 is not the same coefficient in SI. Select the applicable criterion and service limits independently; this example does not qualify sand/corrosion erosion.

The velocity utilization is:

$$
U_{\text{vel}} = \frac{v_{\text{actual}}}{v_{\text{eros}}}
$$

For multiphase flow, the mixture velocity is:

$$
v_m = v_{\text{SG}} + v_{\text{SL}} = \frac{Q_G}{A} + \frac{Q_L}{A}
$$

where $v_{\text{SG}}$ and $v_{\text{SL}}$ are the superficial gas and liquid velocities.

### 20.6.2 Pressure Drop Limit

The available pressure drop in a pipeline is:

$$
\Delta P_{\text{available}} = P_{\text{upstream}} - P_{\text{downstream,min}}
$$

Here $P_{\text{downstream,min}}$ is the minimum required arrival pressure. This ratio requires a strictly positive available pressure drop. If the inlet is already below the arrival requirement, report infeasibility explicitly rather than dividing by a nonpositive allowance. The pressure drop utilization is:

$$
U_{\Delta P} = \frac{\Delta P_{\text{actual}}}{\Delta P_{\text{available}}}
$$

### 20.6.3 Maximum Allowable Operating Pressure (MAOP)

The MAOP is the maximum pressure at which the pipeline may be operated, determined by the mechanical design, material grade, wall thickness, and safety factors. The inlet pressure must not exceed the MAOP:

$$
U_{\text{MAOP}} = \frac{P_{\text{inlet}}}{P_{\text{MAOP}}}
$$

### 20.6.4 NeqSim Pipeline Capacity Check

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import math

# Multiphase pipeline
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 60.0, 80.0)
fluid.addComponent("methane", 0.70)
fluid.addComponent("ethane", 0.05)
fluid.addComponent("propane", 0.03)
fluid.addComponent("n-heptane", 0.10)
fluid.addComponent("water", 0.12)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

feed = jneqsim.process.equipment.stream.Stream("Pipeline Inlet", fluid)
feed.setFlowRate(150000.0, "kg/hr")
feed.setTemperature(60.0, "C")
feed.setPressure(80.0, "bara")

# Pipeline model
pipe = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills("Export Pipeline", feed)
pipe.setPipeWallRoughness(5e-5)
pipe.setLength(25000.0)       # m = 25 km
pipe.setDiameter(0.3048)      # m (12-inch)
pipe.setAngle(0.0)            # horizontal
pipe.setNumberOfIncrements(20)

process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(pipe)
process.run()

# Extract results
P_out = pipe.getOutletStream().getPressure("bara")
dP = 80.0 - P_out

# Velocity check
rho_mix = feed.getFluid().getDensity("kg/m3")
A_pipe = math.pi * 0.3048**2 / 4.0
Q_vol = 150000.0 / 3600.0 / rho_mix
v_actual = Q_vol / A_pipe

C_eros = 150.0  # erosional constant
v_eros = 0.3048 * C_eros * math.sqrt(16.01846337 / rho_mix)

P_MAOP = 100.0  # bara
P_downstream_min = 40.0  # bara

U_vel = v_actual / v_eros
U_dP = dP / (80.0 - P_downstream_min)
U_MAOP = 80.0 / P_MAOP

assert 0.0 < P_out < 80.0
assert abs(pipe.getOutletStream().getFlowRate("kg/hr")-150000.0) < 1e-5
print(f"Outlet pressure:       {P_out:.1f} bara")
print(f"Pressure drop:         {dP:.1f} bar")
print(f"Mixture velocity:      {v_actual:.2f} m/s")
print(f"Erosional velocity:    {v_eros:.1f} m/s")
print(f"\nVelocity utilization:  {U_vel:.1%}")
print(f"Pressure drop util.:   {U_dP:.1%}")
print(f"MAOP utilization:      {U_MAOP:.1%}")
```

---

## 20.7 Pump Capacity

Pumps have constraints analogous to compressors but applied to incompressible fluids.

### 20.7.1 Flow Rate Limits

Centrifugal pumps have minimum and maximum flow constraints:

- **Minimum flow**: Below this, recirculation patterns within the impeller cause heating, cavitation, and vibration. Typically 10–30% of best efficiency point (BEP) flow.
- **Maximum flow**: Pump curve drops to zero head; approaching this point, efficiency falls rapidly and cavitation risk increases.

### 20.7.2 Net Positive Suction Head (NPSH)

The available NPSH must exceed the required NPSH to prevent cavitation:

$$
\text{NPSH}_A = \frac{P_{\text{suction}} - P_{\text{vap}}}{\rho g} + \frac{v^2}{2g} + z_{\text{suction}}
$$

$$
\text{NPSH}_A > \text{NPSH}_R \cdot (1 + \text{margin})
$$

A typical NPSH margin is 0.5 m or 10% above NPSH_R, whichever is greater.

The NPSH utilization:

$$
U_{\text{NPSH}} = \frac{\text{NPSH}_R}{\text{NPSH}_A}
$$

### 20.7.3 Power and Driver Limits

Similar to compressors:

$$
W_{\text{pump}} = \frac{Q \cdot \Delta P}{\eta_{\text{pump}}}
$$

$$
U_{\text{power}} = \frac{W_{\text{pump}}}{W_{\text{driver,max}}}
$$

### 20.7.4 Combined Pump Utilization

$$
U_{\text{pump}} = \max\left(U_{\text{flow}}, U_{\text{NPSH}}, U_{\text{power}}\right)
$$

---

## 20.8 Facility-Level Bottleneck Identification

### 20.8.1 System Capacity Analysis Methodology

A facility-level capacity check involves computing the utilization factor for every equipment item and identifying the bottleneck:

1. **Build the process model**: Create a NeqSim ProcessSystem with all major equipment
2. **Run the simulation**: Solve the process at the current operating conditions
3. **Extract physical properties**: Obtain densities, flow rates, temperatures, pressures from each stream
4. **Compute equipment utilization**: Apply the capacity equations for each equipment type
5. **Identify the bottleneck**: The equipment with the highest utilization factor limits the system
6. **Report spare capacity**: For each equipment, report the headroom available

The system capacity is:

$$
Q_{\text{system,max}} = \frac{Q_{\text{current}}}{\max_i(U_i)}
$$

And the system spare capacity is:

$$
\text{Spare capacity} = Q_{\text{system,max}} - Q_{\text{current}} = Q_{\text{current}} \cdot \left(\frac{1}{\max_i(U_i)} - 1\right)
$$

### 20.8.2 Bottleneck Shifting

An important concept in capacity analysis is **bottleneck shifting**: when the primary bottleneck is resolved (e.g., through debottlenecking, equipment upgrade, or process modification), a different equipment item becomes the new bottleneck. System capacity increases only until the next-most-utilized equipment reaches its limit.

This leads to the concept of a **capacity staircase**: each debottlenecking step removes one constraint and unlocks additional capacity up to the next limit. The economic value of each step must be evaluated against its cost.

![Capacity staircase showing sequential bottleneck removal](figures/capacity_staircase.png)

### 20.8.3 Utilization Report Format

A standard facility utilization report should contain:

| Equipment Tag | Equipment Type | Utilization (%) | Limiting Criterion | Spare Capacity | Status |
|--------------|---------------|-----------------|-------------------|---------------|--------|
| V-100 | HP Separator | 78% | Gas capacity | 22% | Normal |
| V-200 | LP Separator | 92% | Liquid retention | 8% | Warning |
| K-100 | Export Compressor | 85% | Power | 15% | Normal |
| E-100 | Gas Cooler | 63% | Duty | 37% | Normal |
| PV-100 | Pressure Control Valve | 71% | Cv opening | 29% | Normal |
| Pipeline | Export Pipeline | 55% | Pressure drop | 45% | Normal |

A traffic-light color scheme is typically used:

- **Green** ($U < 80\%$): Normal operation with adequate spare capacity
- **Yellow** ($80\% \leq U < 95\%$): Approaching limit — monitor closely
- **Red** ($U \geq 95\%$): At or near capacity limit — action required

---

## 20.9 Comprehensive Worked Example: Facility Capacity Check

This section presents a complete worked example of a facility capacity check for a gas-condensate production platform. The facility processes a three-phase wellstream through HP separation, LP separation, gas compression, gas cooling, and export.

### 20.9.1 Facility Description

The facility consists of:

- **HP Separator** (V-100): Horizontal, 3-phase, ID = 2.8 m, L = 10.0 m
- **LP Separator** (V-200): Horizontal, 2-phase, ID = 2.2 m, L = 7.0 m
- **Export Compressor** (K-100): Centrifugal, two-stage with intercooler
- **Gas Cooler** (E-100): Shell-and-tube, UA = 120,000 W/K
- **Export Pipeline**: 20-inch, 80 km to shore

### 20.9.2 NeqSim Process Model

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import math
import json

# ─── Define wellstream fluid ───
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 80.0, 70.0)
fluid.addComponent("nitrogen", 0.008)
fluid.addComponent("CO2", 0.030)
fluid.addComponent("methane", 0.550)
fluid.addComponent("ethane", 0.070)
fluid.addComponent("propane", 0.040)
fluid.addComponent("i-butane", 0.015)
fluid.addComponent("n-butane", 0.025)
fluid.addComponent("i-pentane", 0.012)
fluid.addComponent("n-pentane", 0.010)
fluid.addComponent("n-hexane", 0.015)
fluid.addComponent("n-heptane", 0.020)
fluid.addComponent("n-octane", 0.010)
fluid.addComponent("water", 0.195)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

# ─── Build Process Model ───
feed = jneqsim.process.equipment.stream.Stream("Wellstream", fluid)
feed.setFlowRate(350000.0, "kg/hr")
feed.setTemperature(80.0, "C")
feed.setPressure(70.0, "bara")

# HP Separator
hp_sep = jneqsim.process.equipment.separator.ThreePhaseSeparator(
    "HP Separator V-100", feed
)

# Gas from HP separator goes to export compressor
compressor = jneqsim.process.equipment.compressor.Compressor(
    "Export Compressor K-100", hp_sep.getGasOutStream()
)
compressor.setOutletPressure(150.0)
compressor.setPolytropicEfficiency(0.76)

# Compressed gas goes through cooler
# Use a heater (negative duty) as cooler for simplicity
cooler = jneqsim.process.equipment.heatexchanger.Heater(
    "Gas Cooler E-100", compressor.getOutletStream()
)
cooler.setOutTemperature(273.15 + 40.0)

# Cooled gas to export pipeline
pipeline = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills(
    "Export Pipeline", cooler.getOutletStream()
)
pipeline.setPipeWallRoughness(5e-5)
pipeline.setLength(80.0)
pipeline.setDiameter(0.508)  # 20-inch
pipeline.setAngle(0.0)
pipeline.setNumberOfIncrements(50)

# Build and run
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(hp_sep)
process.add(compressor)
process.add(cooler)
process.add(pipeline)
process.run()

print("=== Process Simulation Results ===")
print(f"Feed rate:          {feed.getFlowRate('kg/hr'):.0f} kg/hr")
print(f"HP sep gas rate:    {hp_sep.getGasOutStream().getFlowRate('kg/hr'):.0f} kg/hr")
print(f"Compressor power:   {compressor.getPower()/1e6:.2f} MW")
print(f"Cooler outlet T:    {cooler.getOutletStream().getTemperature('C'):.1f} °C")
print(f"Pipeline outlet P:  {pipeline.getOutletStream().getPressure('bara'):.1f} bara")
```

### 20.9.3 Equipment Utilization Calculations

```python
# ══════════════════════════════════════════════════
# FACILITY CAPACITY CHECK
# ══════════════════════════════════════════════════

utilization_report = []

# --- HP Separator V-100 ---
D_hp = 2.8   # m
L_hp = 10.0  # m
liq_frac_hp = 0.50

rho_gas_hp = hp_sep.getGasOutStream().getFluid().getDensity("kg/m3")
rho_oil_hp = hp_sep.getOilOutStream().getFluid().getDensity("kg/m3")
Q_gas_hp = hp_sep.getGasOutStream().getFluid().getFlowRate("m3/sec")

A_gas_hp = (math.pi * D_hp**2 / 4.0) * (1.0 - liq_frac_hp)
K_SB_hp = 0.15
v_max_hp = K_SB_hp * math.sqrt((rho_oil_hp - rho_gas_hp) / rho_gas_hp)
Q_max_hp = v_max_hp * A_gas_hp
U_gas_hp = Q_gas_hp / Q_max_hp

Q_oil_hp = hp_sep.getOilOutStream().getFluid().getFlowRate("m3/sec")
Q_water_hp = hp_sep.getWaterOutStream().getFluid().getFlowRate("m3/sec")
V_liq_hp = (math.pi * D_hp**2 / 4.0) * liq_frac_hp * L_hp
t_ret_hp = V_liq_hp / (Q_oil_hp + Q_water_hp) if (Q_oil_hp + Q_water_hp) > 0 else 9999
t_ret_min_hp = 180.0
U_liq_hp = t_ret_min_hp / t_ret_hp

U_hp_sep = max(U_gas_hp, U_liq_hp)
limit_hp = "Gas capacity" if U_gas_hp > U_liq_hp else "Liquid retention"

utilization_report.append({
    "tag": "V-100",
    "type": "HP Separator",
    "utilization": U_hp_sep,
    "limiting_criterion": limit_hp,
    "spare_capacity": 1.0 - U_hp_sep
})

# --- Export Compressor K-100 ---
W_comp = compressor.getPower() / 1e6  # MW
W_driver = 25.0  # MW, gas turbine rated power
T_amb = 20.0
alpha = 0.006
W_driver_derated = W_driver * (1.0 - alpha * (T_amb - 15.0))
U_comp_power = W_comp / W_driver_derated

utilization_report.append({
    "tag": "K-100",
    "type": "Export Compressor",
    "utilization": U_comp_power,
    "limiting_criterion": "Power",
    "spare_capacity": 1.0 - U_comp_power
})

# --- Gas Cooler E-100 ---
# Temperature approach as capacity metric
T_hot_in = compressor.getOutletStream().getTemperature("C")
T_hot_out = cooler.getOutletStream().getTemperature("C")
T_cw_in = 15.0  # °C, seawater
T_cw_out = 30.0  # °C, estimate
DT_approach = T_hot_out - T_cw_in
DT_approach_min = 5.0
U_hx = DT_approach_min / DT_approach if DT_approach > 0 else 1.0

utilization_report.append({
    "tag": "E-100",
    "type": "Gas Cooler",
    "utilization": U_hx,
    "limiting_criterion": "Temperature approach",
    "spare_capacity": 1.0 - U_hx
})

# --- Export Pipeline ---
P_pipeline_out = pipeline.getOutletStream().getPressure("bara")
P_delivery_min = 50.0
dP_pipeline = 150.0 - P_pipeline_out
dP_available = 150.0 - P_delivery_min
U_pipeline = dP_pipeline / dP_available

utilization_report.append({
    "tag": "Pipeline",
    "type": "Export Pipeline",
    "utilization": U_pipeline,
    "limiting_criterion": "Pressure drop",
    "spare_capacity": 1.0 - U_pipeline
})

# ── Print utilization report ──
print("\n" + "=" * 80)
print("FACILITY UTILIZATION REPORT")
print("=" * 80)
print(f"{'Tag':<12} {'Type':<22} {'Util.':<10} {'Limit':<22} {'Spare':<10} {'Status'}")
print("-" * 80)

for item in utilization_report:
    u = item["utilization"]
    status = "GREEN" if u < 0.80 else ("YELLOW" if u < 0.95 else "RED")
    print(f"{item['tag']:<12} {item['type']:<22} {u:<10.1%} "
          f"{item['limiting_criterion']:<22} {item['spare_capacity']:<10.1%} {status}")

# Identify bottleneck
bottleneck = max(utilization_report, key=lambda x: x["utilization"])
print(f"\n>>> BOTTLENECK: {bottleneck['tag']} ({bottleneck['type']}) "
      f"at {bottleneck['utilization']:.1%} utilization")
print(f"    Limiting criterion: {bottleneck['limiting_criterion']}")

max_production = 350000.0 / bottleneck["utilization"]
print(f"    Maximum system throughput: {max_production:.0f} kg/hr "
      f"({max_production/350000.0:.1%} of current)")
```

### 20.9.4 Interpreting the Results

The utilization report provides a snapshot of the facility's operating state. Several key observations can be drawn:

1. **The bottleneck equipment** limits the entire facility — increasing production beyond this point requires either debottlenecking the equipment or accepting degraded performance
2. **Equipment with low utilization** represents over-design or spare capacity that could accommodate tie-backs
3. **The gap between the bottleneck and the second-most-utilized equipment** indicates how much additional capacity is unlocked by debottlenecking the primary constraint

---

## 20.10 Sensitivity Analysis: Capacity vs Production Rate

A critical application of capacity checking is understanding how utilization changes as production conditions evolve. This is typically done by running the process model at multiple production rates and plotting utilization curves.

### 20.10.1 Production Rate Sweep

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import math

# Flow rate sweep from 50% to 130% of current production
flow_factors = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
base_flow = 350000.0  # kg/hr

results = []

for factor in flow_factors:
    flow_rate = base_flow * factor

    # Rebuild and run the process at each flow rate
    fl = jneqsim.thermo.system.SystemSrkEos(273.15 + 80.0, 70.0)
    fl.addComponent("nitrogen", 0.008)
    fl.addComponent("CO2", 0.030)
    fl.addComponent("methane", 0.550)
    fl.addComponent("ethane", 0.070)
    fl.addComponent("propane", 0.040)
    fl.addComponent("i-butane", 0.015)
    fl.addComponent("n-butane", 0.025)
    fl.addComponent("i-pentane", 0.012)
    fl.addComponent("n-pentane", 0.010)
    fl.addComponent("n-hexane", 0.015)
    fl.addComponent("n-heptane", 0.020)
    fl.addComponent("n-octane", 0.010)
    fl.addComponent("water", 0.195)
    fl.setMixingRule("classic")
    fl.setMultiPhaseCheck(True)

    fd = jneqsim.process.equipment.stream.Stream("Feed", fl)
    fd.setFlowRate(flow_rate, "kg/hr")
    fd.setTemperature(80.0, "C")
    fd.setPressure(70.0, "bara")

    sep = jneqsim.process.equipment.separator.ThreePhaseSeparator("Sep", fd)
    comp = jneqsim.process.equipment.compressor.Compressor(
        "Comp", sep.getGasOutStream()
    )
    comp.setOutletPressure(150.0)
    comp.setPolytropicEfficiency(0.76)

    ps = jneqsim.process.processmodel.ProcessSystem()
    ps.add(fd)
    ps.add(sep)
    ps.add(comp)
    ps.run()

    # Calculate utilization metrics
    rho_g = sep.getGasOutStream().getFluid().getDensity("kg/m3")
    rho_o = sep.getOilOutStream().getFluid().getDensity("kg/m3")
    Q_g = sep.getGasOutStream().getFluid().getFlowRate("m3/sec")
    A_gas = (math.pi * 2.8**2 / 4.0) * 0.50
    v_max = 0.15 * math.sqrt((rho_o - rho_g) / rho_g)
    U_sep_gas = (Q_g / A_gas) / v_max

    W_comp = comp.getPower() / 1e6
    W_drv = 25.0 * (1.0 - 0.006 * (20.0 - 15.0))
    U_comp = W_comp / W_drv

    results.append({
        "factor": factor,
        "flow_kghr": flow_rate,
        "U_separator": U_sep_gas,
        "U_compressor": U_comp,
    })

# Display results table
print(f"{'Flow Factor':<14} {'Flow (kg/hr)':<14} {'Sep. Util.':<14} {'Comp. Util.':<14}")
print("-" * 56)
for r in results:
    print(f"{r['factor']:<14.1f} {r['flow_kghr']:<14.0f} "
          f"{r['U_separator']:<14.1%} {r['U_compressor']:<14.1%}")
```

### 20.10.2 Interpreting the Sensitivity Plot

The resulting utilization-vs-production-rate plot reveals several important features:

- **The crossover point**: The production rate at which the bottleneck shifts from one equipment to another. Below this rate, one piece of equipment is the constraint; above it, a different one takes over. This crossover rate is an important design parameter.
- **The capacity limit**: The production rate at which any equipment reaches 100% utilization. This is the absolute maximum throughput of the facility.
- **The sensitivity (slope)**: The slope of each utilization curve indicates how strongly each equipment responds to changes in production rate. Equipment with steep slopes will become constraints rapidly as production increases; equipment with shallow slopes has more inherent margin.
- **The margin at current conditions**: The vertical distance between each equipment's utilization and 100% represents the remaining capacity margin. Small margins indicate fragile operation — any perturbation (fouling, off-design composition, ambient temperature increase) could push the equipment beyond its limit.

Understanding these features enables operations engineers to anticipate future bottlenecks rather than react to them after they occur.

![Equipment utilization vs production rate showing bottleneck crossover](figures/utilization_vs_production.png)

### 20.10.3 Impact of Changing Water Cut

As a field matures, the water cut increases. This dramatically affects separator liquid capacity while having little effect on compressor capacity:

```python
# Water cut sensitivity
water_cuts = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]

for wc in water_cuts:
    # Adjust composition to reflect higher water cut
    # This is a simplified approach; in practice, the
    # total fluid rate may also change
    oil_fraction = 0.195 * (1.0 - wc)  # hydrocarbon fraction decreases
    water_fraction = 0.195 + wc * 0.40  # water fraction increases

    # ... rebuild and run process (similar to above)
    # ... compute utilization
    pass  # Full implementation follows the pattern above

print("Water cut sensitivity analysis would show separator liquid")
print("utilization increasing sharply with water cut while compressor")
print("utilization remains relatively constant.")
```

---

## 20.11 Debottlenecking Strategies

When a bottleneck is identified, several strategies can be considered:

### 20.11.1 Separator Debottlenecking

| Strategy | Effect | Typical Capacity Increase |
|----------|--------|--------------------------|
| Upgrade internals (mesh to vane pack) | Increases $K_{\text{SB}}$ | 30–50% gas capacity |
| Install cyclonic inlet device | Better inlet separation | 10–20% |
| Raise liquid level | More liquid volume, less gas area | Trades gas for liquid capacity |
| Lower liquid level | More gas area, less liquid volume | Trades liquid for gas capacity |
| Add parallel separator | Doubles total capacity | 100% (for identical vessel) |
| Reduce retention time requirement | Allows higher liquid throughput | Variable |

### 20.11.2 Compressor Debottlenecking

| Strategy | Effect | Typical Capacity Increase |
|----------|--------|--------------------------|
| Suction pressure optimization | Reduces compression ratio, saves power | 5–15% |
| Intercooler improvement | Lower interstage temperature, less power | 3–8% |
| Impeller re-wheel | Changed characteristic | Variable |
| Add parallel compressor | Doubles flow capacity | 100% |
| Driver upgrade | Higher power available | Variable |
| Anti-surge valve optimization | Reduced recycle flow | 5–15% flow increase |

### 20.11.3 Heat Exchanger Debottlenecking

| Strategy | Effect | Typical Capacity Increase |
|----------|--------|--------------------------|
| Online cleaning | Restores U to design value | 10–30% |
| Tube insert (turbulator) | Increases tube-side h | 20–40% |
| Enhanced tubes (finned, twisted) | Higher heat transfer area | 20–50% |
| Add parallel exchanger | Doubles capacity | 100% |
| Increase cooling medium flow | Improves temperature approach | 10–20% |

---

## 20.12 Capacity Monitoring and Trending

### 20.12.1 Real-Time Capacity Dashboard

In modern operations, capacity utilization is calculated in real time using process simulation models updated with live plant data. The key elements of a capacity monitoring system are:

1. **Data acquisition**: Real-time measurements (flow, pressure, temperature, level) from the plant DCS via OPC or PI/IP.21 historian interfaces
2. **Data validation**: Gross error detection and data reconciliation to ensure measurement quality (see Chapter 19 for data reconciliation methods)
3. **Model update**: Process simulation model parameters (efficiency, UA values, well PI) updated with current conditions using parameter estimation
4. **Capacity calculation**: Utilization factors computed for each equipment item using the methods described in Sections 20.2–20.7
5. **Trending**: Historical trends of utilization displayed on operator screens to identify developing constraints before they become bottlenecks
6. **Alerting**: Automatic alerts when utilization exceeds configurable warning thresholds (e.g., amber at 85%, red at 95%)
7. **Reporting**: Daily and weekly capacity reports summarizing bottleneck status, spare capacity, and recommended actions

A well-designed capacity dashboard provides operators with immediate situational awareness of the facility's operating margins, enabling proactive rather than reactive management of constraints.

### 20.12.2 Capacity Trending Over Field Life

Plotting utilization factors over the field life reveals the long-term evolution of constraints:

$$
U_i(t) = \frac{Q_{i,\text{actual}}(t)}{Q_{i,\text{max}}(t)}
$$

Note that both the numerator and denominator can change over time — the actual throughput changes with production rate and fluid composition, while the maximum capacity changes with fluid properties (e.g., gas density affects separator K-factor).

![Capacity utilization trends over field life showing bottleneck evolution](figures/utilization_trend_field_life.png)

---

## 20.13 Flare and Relief System Capacity

An often-overlooked but safety-critical capacity check is the flare and relief system. Every pressure vessel has a pressure safety valve (PSV) that must be capable of relieving the worst-case overpressure scenario.

### 20.13.1 Relief Valve Capacity

The required relief rate depends on the relief scenario (fire case, blocked outlet, control valve failure, etc.). The relief valve must have sufficient capacity:

$$
U_{\text{PSV}} = \frac{W_{\text{relief,required}}}{W_{\text{PSV,rated}}}
$$

where $W_{\text{relief,required}}$ is the required relief rate (kg/hr) for the governing scenario and $W_{\text{PSV,rated}}$ is the certified capacity of the installed PSV.

If $U_{\text{PSV}} > 1.0$, the relief valve is undersized for the current conditions — a serious safety concern.

### 20.13.2 Flare Header Capacity

The flare header (pipe network connecting PSVs to the flare tip) has a maximum capacity limited by the allowable back-pressure at the relief valves. Excessive back-pressure reduces PSV capacity and can prevent valves from opening:

Allowable built-up and superimposed backpressure depend on relief-valve type, overpressure allowance, service and certified manufacturer data. The often quoted 10% conventional and 50% balanced-bellows values are not universal acceptance limits; use the applicable sizing/design basis and capacity corrections.

The flare header utilization is:

$$
U_{\text{flare}} = \frac{\Delta P_{\text{header,actual}}}{\Delta P_{\text{header,max}}}
$$

When new equipment is tied into an existing facility, the flare header capacity must be re-verified.

### 20.13.3 NeqSim Relief Valve Sizing

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import math

# Calculate required relief rate for a blocked outlet scenario
# on the HP separator

fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 80.0, 75.0)
fluid.addComponent("methane", 0.60)
fluid.addComponent("ethane", 0.08)
fluid.addComponent("propane", 0.05)
fluid.addComponent("n-butane", 0.03)
fluid.addComponent("n-heptane", 0.10)
fluid.addComponent("water", 0.14)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

# At relief conditions (10% above design pressure)
P_design = 75.0  # bara
P_relief = P_design * 1.10  # bara, relief pressure

feed = jneqsim.process.equipment.stream.Stream("Relief Stream", fluid)
feed.setFlowRate(350000.0, "kg/hr")
feed.setTemperature(80.0, "C")
feed.setPressure(P_relief, "bara")

process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.run()

# Gas properties at relief conditions for API 520 sizing
ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid)
ops.TPflash()
fluid.initProperties()

rho_gas_relief = fluid.getPhase("gas").getDensity("kg/m3")
MW_gas = fluid.getPhase("gas").getMolarMass() * 1000  # g/mol
Z_relief = fluid.getPhase("gas").getZ()
k = fluid.getPhase("gas").getCp() / fluid.getPhase("gas").getCv()

print(f"Relief pressure:    {P_relief:.1f} bara")
print(f"Gas density:        {rho_gas_relief:.2f} kg/m³")
print(f"Gas MW:             {MW_gas:.1f} g/mol")
print(f"Z at relief:        {Z_relief:.4f}")
print(f"k (Cp/Cv):          {k:.3f}")

# API 520 orifice area calculation (simplified)
W_relief = 250000.0  # kg/hr, worst-case blocked outlet
T_relief = 273.15 + 80.0  # K
C_API = 0.0394 * k * (2.0/(k+1.0))**((k+1.0)/(k-1.0))

A_required = W_relief / (C_API * P_relief * 100 *
    math.sqrt(MW_gas / (Z_relief * T_relief)))

print(f"\nRequired PSV orifice area: {A_required:.4f} m² (simplified)")
print(f"PSV rated capacity check should use detailed API 520 method")
```

---

## 20.14 Advanced Topics

### 20.14.1 Interaction Effects Between Equipment

Equipment capacity limits are not independent. For example:

- **Separator pressure affects compressor capacity**: Lowering separator pressure increases the compression ratio, requiring more power. If the compressor is power-limited, the separator pressure cannot be lowered further.
- **Compressor recycle affects cooler duty**: Increased compressor recycle (to maintain surge margin at low flow) increases the gas flow through the cooler, potentially exceeding its duty.
- **Pipeline back-pressure affects compressor discharge pressure**: If the pipeline pressure drop increases (due to higher flow or liquid accumulation), the required compressor discharge pressure increases.

These interactions mean that the capacity check must be performed on the **integrated system**, not on individual equipment in isolation.

### 20.14.2 Monte Carlo Capacity Assessment

When input parameters are uncertain (fluid composition, ambient temperature, fouling state), a Monte Carlo approach can be used to generate a probabilistic capacity assessment:

$$
\widehat P(\text{most loaded criterion}=i)=\frac{N_i}{N_{\mathrm{valid}}}
$$

Here $N_i$ counts valid trials assigned to criterion $i$, with a declared tie rule. Report invalid/unsolved trials separately and never silently remove them from reliability estimates. Specify the sampled distributions, correlations and sampling error; a design grid is not automatically a probability sample.

This approach yields the **probability distribution of system capacity** and identifies which equipment is most likely to become the bottleneck under various scenarios.

### 20.14.3 Multi-Period Capacity Planning

Production profiles change over the field life. A multi-period capacity analysis evaluates the utilization at each time step of the production forecast:

1. For each year $t$ in the production forecast:
   - Set the fluid composition and flow rate to the predicted values
   - Run the process simulation
   - Compute utilization for all equipment
2. Identify when each equipment first reaches its capacity limit
3. Plan debottlenecking investments accordingly

This is a key input to the **facilities management plan** and influences decisions on tie-back timing, debottlenecking investments, and end-of-life operations.

### 20.14.4 Dynamic Capacity Assessment

Steady-state capacity checks assume the plant is at equilibrium. In practice, transient events (well startup, slug arrival, compressor trip) can temporarily exceed equipment capacity. Dynamic capacity assessment uses transient simulation to verify that equipment can handle worst-case dynamic loads:

- **Slug arrival at separator**: Liquid level surges above the high-level alarm. The separator must have sufficient liquid volume to absorb the slug without carryover. The slug absorption capacity is:

$$
\max_t\int_0^t(\dot V_{L,in}-\dot V_{L,out})\,ds\leq V_{HH}-V_{initial}
$$

Use a consistent actual-liquid basis and include base flow, excess slug inflow and time-varying withdrawal. Capacity utilization alone cannot determine the volume that can be absorbed. If the net accumulated liquid exceeds the available level-band volume, slug mitigation measures (slug catcher, topside de-slugging control) are required.

- **Compressor trip**: Sudden loss of compression capacity. The remaining compressor(s) must handle the full flow or production must be curtailed. The fastest relevant pressure, flow or trip-limit excursion determines the available response time for the control system.

- **Power generation failure**: Loss of a gas turbine generator reduces available power. Critical loads (safety systems, emergency lighting, communication) must be powered by the emergency generator. The time to shed non-critical loads and stabilize the electrical system determines the maximum allowable transient power demand.

- **Well kick-in**: Starting a new well introduces a step change in flow rate and potentially a slug of liquid. The separator and downstream equipment must have sufficient capacity to handle the transient without tripping safety systems.

Dynamic capacity checks are typically performed as part of the HAZOP and design verification process. They complement the steady-state utilization analysis by ensuring the facility can safely ride through foreseeable transient events.

---


<!-- reviewed-notebook-results:start -->
## Reproduced Calculation Results

These examples use the stated fluid recipes and operating assumptions. Curves represent NeqSim calculations unless a caption identifies an analytical illustration, assumed equipment map or synthetic data.

![Equipment Capacity Utilization at Nominal Feed Rate](figures/ch18_utilization_bar_chart.png)

At the nominal 50 t/hr feed, the reported equipment utilization spans 28.9–83.3 percent of the stated screening capacities.

The separator and pipeline capacities are inferred by auto-sizing, and the compressor uses only its inferred power rating with the synthetic map disabled. These percentages are screening margins relative to generated capacities. Replace the generated capacities with installed ratings before setting operating limits.

![Equipment Utilization vs Feed Rate](figures/ch18_utilization_vs_feed_rate.png)

HP Separator: capacity utilization spans 33.23–132.9 % across the plotted cases. Export Compressor: capacity utilization spans 33.33–133.3 % across the plotted cases.

Phase flows and compressor work increase with feed rate; the denominator is held at the design capacity established before the sweep. A capacity boundary is visible only when the rate sweep crosses 100 percent. Select the highest rate that meets every declared limit and then check the returned stream pressures.

Selected numerical ranges from the plotted cases:

| Quantity / series | Minimum | Maximum | Unit |
|---|---:|---:|---|
| Capacity Utilization | 28.86 | 83.33 | % |
| HP Separator: capacity utilization | 33.23 | 132.9 | % |

Ranges describe the sampled cases; they are not independent validation tolerances.
<!-- reviewed-notebook-results:end -->

## Summary

This chapter presented the theoretical foundation and practical methods for checking equipment capacity and computing utilization factors across all major equipment types in oil and gas production facilities.

**Key takeaways:**

1. **Separator capacity** is governed by three independent criteria: gas handling (Souders-Brown), liquid retention time, and gas-liquid interface area. The binding criterion depends on the gas-oil ratio and water cut.

2. **Compressor capacity** is limited by surge, stonewall, power, and head constraints. The operating point must lie within the compressor envelope; power limits often govern for export compressors.

3. **Heat exchanger capacity** depends on thermal duty, temperature approach, tube velocity, shell-side vibration, and pressure drop. Fouling progressively reduces capacity over time.

4. **Valve capacity** is determined by the $C_v$ coefficient, and valves should operate between 20% and 80% opening for good controllability.

5. **Pipeline capacity** is constrained by erosional velocity, pressure drop, and MAOP limits.

6. **Pump capacity** is limited by available NPSH, driver power, and the intersection of the pump curve with the system resistance curve.

7. **Flare and relief systems** must be checked whenever new equipment is added to ensure relief valves and flare headers can handle worst-case overpressure scenarios.

8. **The utilization factor** $U = Q_{\text{actual}} / Q_{\text{max}}$ provides a unified metric across all equipment types. The equipment with the highest utilization is the bottleneck.

9. **Facility-level bottleneck identification** requires running the complete process model and computing utilization for all equipment simultaneously, because equipment interactions create coupling effects.

10. **Sensitivity analysis** (production rate sweep, water cut impact, ambient temperature variation) reveals how the bottleneck shifts with changing operating conditions — essential for planning debottlenecking investments.

11. **Debottlenecking strategies** range from low-cost operational changes (optimizing levels, set points) to moderate investments (upgrading internals, cleaning) to major capital projects (adding parallel equipment).

12. **Real-time capacity monitoring** using updated process models provides continuous visibility into the facility's operating margins, enabling proactive management of constraints.

The methods presented in this chapter form the constraint evaluation layer for production optimization (Chapter 19). Every optimization algorithm requires a way to check whether a candidate operating point is feasible — the utilization factor calculations developed here provide exactly that capability. The systematic approach of computing $U = Q_{\text{actual}} / Q_{\text{max}}$ for each equipment item and identifying the highest utilization as the bottleneck is a powerful framework that applies regardless of facility type — onshore plants, offshore platforms, FPSOs, or subsea processing systems.

As production facilities age and field conditions evolve, regular capacity assessment becomes increasingly important. Early-life operation is typically well within design capacity, but as water cut increases, compressor efficiency degrades, and heat exchangers foul, the margins narrow. Proactive capacity management — combining the techniques of this chapter with the optimization methods of Chapter 19 — enables operators to extract maximum value from existing infrastructure while maintaining safe operation.

6. **The facility bottleneck** is the equipment with the highest utilization factor. The system maximum throughput is $Q_{\text{max}} = Q_{\text{current}} / U_{\text{bottleneck}}$.

7. **Sensitivity analysis** reveals how the bottleneck shifts with changing production rate, water cut, or ambient conditions, enabling proactive debottlenecking.

8. **NeqSim process simulation** provides the fluid properties and process conditions needed to perform rigorous capacity calculations on integrated production systems.

---


<!-- September 2026 source update -->
## Capacity coverage and strict evidence

A capacity report must answer two questions before it ranks equipment: which restrictions were expected, and which of those restrictions were actually evaluated? `UtilizationCoverageReport` now records declared equipment and constraint identities independently of discovery. Missing equipment, missing constraints, absent ratings, default screening limits and failed suppliers remain visible. Unknown values are `NaN` in Java and `null` in JSON; they must never be converted into zero utilization \cite{neqsim2026update}.

Completion has a narrow meaning: evidence is available for the declared scope. It does not establish process convergence, operating feasibility, mechanical integrity or whole-plant completeness. A deliberately disabled constraint remains an auditable row. Similarly, `autoSize()` establishes a synthetic design basis for a screening exercise; it is not evidence of the installed capacity of an existing vessel or compressor.

The strict separator, pipeline and shared-resource adapters are post-solve evidence collectors. `PlantSeparatorEvidence` records the supported separator metrics only when their declared geometry, phase availability and validity conditions are satisfied. `PlantSharedResourceEvidence` checks participant-complete compressor/pump shaft demand or solved `EnergyBus` electrical demand against the authoritative aggregate. `PlantCommonShaftEvidence` checks a declared steady-state casing/driver/shaft group, including common speed, power balance, torque and casing map margins. They freeze existing results and do not introduce new equipment physics.

Use an explicit evidence ledger in capacity studies:

| Question | Required report field | Interpretation |
|---|---|---|
| What is limited? | Stable equipment/constraint identity | Distinguishes similarly named trains |
| On what basis? | Unit, phase/rate basis, geometry and provenance | Makes limits comparable |
| Is the value current? | Calculation identity and convergence | Prevents stale acceptance |
| What is missing? | Coverage diagnostics and disabled rows | Prevents empty “all clear” reports |
| Is the candidate feasible? | Signed margin and severity | Separates availability from compliance |

The following intentional missing-equipment example is a small executable regression of this principle. Its successful outcome is an incomplete report, not a feasible plant:

```python
import json
import jpype
jneqsim = jpype.JPackage("neqsim")
Coverage = jneqsim.process.util.optimizer.UtilizationCoverageReport
coverage = (Coverage.builder("Book capacity example")
            .expectConstraint("Compression", "Missing compressor", "power")
            .build())
assert not coverage.isComplete()
diagnostics = [str(item) for item in coverage.getDiagnostics()]
assert any("MISSING_EQUIPMENT" in item for item in diagnostics)
print(json.dumps(json.loads(str(coverage.toJson())), indent=2))
```
<!-- @neqsim:claim
  test: src/test/java/neqsim/process/util/optimizer/UtilizationCoverageReportTest.java
-->

---

## Exercises

**Exercise 20.1** — *Separator Gas Capacity*
A horizontal HP separator (ID = 3.0 m, L = 12.0 m) operates at 55 bara and 75°C with a gas of density 48 kg/m³ and oil density 720 kg/m³. The liquid level occupies 55% of the diameter. Using $K_{\text{SB}} = 0.14$ m/s for a wire mesh demister, calculate (a) the maximum gas velocity, (b) the maximum gas volumetric flow rate, and (c) the gas utilization factor if the actual gas flow rate is 1.8 m³/s.

**Exercise 20.2** — *Compressor Power Utilization*
An export compressor compresses 4.2 MSm³/day of gas from 28 bara, 25°C to 135 bara with a polytropic efficiency of 0.77. The gas has molecular weight 19.5 kg/kmol and $Z_{\text{avg}} = 0.92$. The driver is a 20 MW gas turbine with ambient derating of 0.7%/°C above 15°C. Calculate (a) the approximate shaft power using the polytropic head equation, and (b) the power utilization factor at 30°C ambient temperature.

**Exercise 20.3** — *Heat Exchanger Approach Temperature*
A gas cooler has UA = 80,000 W/K. The hot gas enters at 120°C and exits at 45°C. Cooling water enters at 18°C. Calculate (a) the duty, (b) the cooling water outlet temperature (assume $\dot{m}_{cw} \cdot C_p = 100,000$ W/K), (c) the minimum temperature approach, and (d) whether the exchanger is at its thermal limit (MTA limit = 5°C).

**Exercise 20.4** — *Valve Sizing Check*
A control valve has $C_{v,\text{max}} = 350$. At current conditions (gas flow 80,000 kg/hr, upstream pressure 65 bara, downstream pressure 55 bara), the required $C_v$ is 245. Assume a linear inherent characteristic and fixed pressure conditions. Calculate (a) the percent opening, (b) whether the valve is within the recommended 20–80% range, and (c) the maximum flow the valve can handle at these pressure conditions.

**Exercise 20.5** — *Pipeline Erosional Velocity*
A 16-inch (ID = 0.387 m) multiphase pipeline carries a mixture with $\rho_m = 180$ kg/m³ at 120,000 kg/hr. Using $C_{US}=150$ with the stated imperial-to-SI conversion, calculate (a) the erosional velocity, (b) the actual mixture velocity, and (c) the velocity utilization factor.

**Exercise 20.6** — *Facility Bottleneck Identification*
A facility has the following utilization factors: HP Separator 72%, LP Separator 88%, Compressor 81%, Gas Cooler 55%, Export Pipeline 67%. (a) Identify the bottleneck. (b) Calculate the maximum system throughput as a percentage of current production under proportional-load scaling, then explain why a fresh nonlinear process solve is still required. (c) If the LP Separator is debottlenecked to 60% utilization, what is the new bottleneck and new maximum throughput?

**Exercise 20.7** — *NeqSim Capacity Sweep*
Using NeqSim, build a process model consisting of a three-phase separator and a compressor. Sweep the feed flow rate from 200,000 to 500,000 kg/hr in 50,000 kg/hr increments. For each case, calculate the separator gas utilization and compressor power utilization. Plot both utilization curves on the same graph and identify the crossover point where the bottleneck shifts.

**Exercise 20.8** — *Water Cut Impact Analysis*
For the process model in Exercise 20.7, fix the total mass flow at 350,000 kg/hr and vary the water mole fraction from 0.05 to 0.50 (adjusting the methane fraction to maintain total = 1.0). Calculate how the separator liquid utilization changes with water cut. At what water cut does the separator liquid capacity become the bottleneck?

---

## References

1. Arnold, K.E. and Stewart, M.I. (2008). *Surface Production Operations, Volume 1: Design of Oil Handling Systems and Facilities*, 3rd edn. Burlington, MA: Gulf Professional Publishing.
2. Campbell, J.M. (2014). *Gas Conditioning and Processing, Volume 2: The Equipment Modules*, 9th edn. Norman, OK: Campbell Petroleum Series.
3. Bothamley, M. (2013). "Gas/Liquid Separators — Quantifying Separation Performance." *Oil and Gas Facilities*, 2(4), pp. 21–29.
4. Souders, M. and Brown, G.G. (1934). "Design of Fractionating Columns: I. Entrainment and Capacity." *Industrial & Engineering Chemistry*, 26(1), pp. 98–103.
5. API RP 14E (2007). *Recommended Practice for Design and Installation of Offshore Production Platform Piping Systems*, 5th edn. Washington, DC: American Petroleum Institute.
6. GPSA Engineering Data Book (2012). 13th edn. Tulsa, OK: Gas Processors Suppliers Association.
7. Mokhatab, S. and Poe, W.A. (2012). *Handbook of Natural Gas Transmission and Processing*, 2nd edn. Burlington, MA: Gulf Professional Publishing.
8. Guo, B., Lyons, W.C., and Ghalambor, A. (2007). *Petroleum Production Engineering*. Burlington, MA: Elsevier.
9. ISA/IEC 60534 (2005). *Industrial-Process Control Valves*. Research Triangle Park, NC: International Society of Automation.
10. NORSOK P-002 (2014). *Process System Design*. Lysaker: Standards Norway.
11. Svrcek, W.Y. and Monnery, W.D. (1993). "Design Two-Phase Separators Within the Right Limits." *Chemical Engineering Progress*, 89(10), pp. 53–60.
12. Lieberman, N.P. (2009). *Troubleshooting Process Plant Control*. Tulsa, OK: PennWell.


