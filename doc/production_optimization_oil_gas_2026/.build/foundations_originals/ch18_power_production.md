# Power Production and Energy Sources for Oil and Gas Processing

## Introduction

Power generation and energy supply are fundamental to oil and gas production operations. Every piece of rotating equipment—compressors, pumps, fans, and auxiliary systems—requires a driver, and the choice, sizing, and efficiency of these drivers directly impacts production capacity, operating costs, emissions, and facility uptime. In the context of production optimization, power availability is often the binding constraint that limits throughput, particularly on offshore platforms where power generation capacity is fixed and shared among multiple process trains.

The energy intensity of upstream production has grown steadily as fields mature: declining reservoir pressures demand more compression power, rising water cuts require larger injection and handling systems, and tighter environmental regulations impose efficiency targets that older equipment struggles to meet. On the Norwegian Continental Shelf alone, upstream facilities consume roughly 7 TWh of electricity equivalent per year, with gas turbines accounting for over 80% of direct CO$_2$ emissions. Understanding how power systems interact with process constraints is therefore not merely an engineering exercise—it is central to both economic optimization and decarbonization strategy.

This chapter examines the full spectrum of power production and energy sources used in upstream oil and gas facilities, with emphasis on their role as capacity constraints in production optimization. We cover gas turbine prime movers, electric motor drives, waste heat recovery, combined cycle configurations, fuel gas systems, Organic Rankine Cycles, electrification from shore power, and power system reliability. Throughout, we demonstrate how NeqSim models these systems and integrates power constraints into the production optimization framework.

## Gas Turbines as Prime Movers

### The Brayton Cycle: Thermodynamic Foundations

Gas turbines operate on the Brayton (or Joule) cycle, an open-cycle process consisting of four idealized steps:

1. **Isentropic compression** (process 1→2) — Ambient air is compressed from state 1 to state 2
2. **Constant-pressure heat addition** (process 2→3) — Fuel combustion raises the temperature at constant pressure
3. **Isentropic expansion** (process 3→4) — Hot gas expands through the turbine, producing shaft work
4. **Constant-pressure heat rejection** (process 4→1) — Exhaust gas is expelled to the atmosphere

For an ideal Brayton cycle with a perfect gas, the thermal efficiency depends solely on the pressure ratio:

$$
\eta_{th,ideal} = 1 - \frac{1}{r_p^{(\gamma-1)/\gamma}}
$$

where $r_p = P_2/P_1$ is the compressor pressure ratio and $\gamma = c_p/c_v$ is the ratio of specific heats (approximately 1.4 for air). At a pressure ratio of 20, the ideal efficiency is about 57%, but real gas turbines achieve considerably less due to irreversibilities in the compressor, combustor, and turbine sections.

The net specific work output of a real gas turbine, accounting for compressor and turbine isentropic efficiencies, is:

$$
W_{GT} = \dot{m}_{air} \cdot c_p \cdot T_1 \left[\frac{r_p^{(\gamma-1)/\gamma} - 1}{\eta_c} - \eta_t\left(1 - \frac{1}{r_p^{(\gamma-1)/\gamma}}\right) \cdot \frac{T_3}{T_1}\right]
$$

where $\dot{m}_{air}$ is the air mass flow rate, $T_1$ is the compressor inlet temperature (K), $T_3$ is the turbine inlet temperature (K), $\eta_c$ is the compressor isentropic efficiency (typically 0.85–0.90), and $\eta_t$ is the turbine isentropic efficiency (typically 0.88–0.92). This equation reveals the two fundamental design levers: increasing $T_3/T_1$ (higher firing temperature) and optimizing $r_p$ for maximum net work at a given temperature ratio.

![Brayton cycle T-s diagram showing ideal (1-2s-3-4s) and real (1-2-3-4) processes](figures/brayton_cycle_ts.png)

### Isentropic vs. Polytropic Efficiency

Gas turbine manufacturers and process engineers use two different efficiency definitions, and confusing them leads to significant errors in power calculations:

**Isentropic (adiabatic) efficiency** compares actual work to the work of a reversible adiabatic process between the same pressures:

$$
\eta_{is} = \frac{h_{2s} - h_1}{h_2 - h_1} \quad \text{(compressor)} \qquad \eta_{is} = \frac{h_3 - h_4}{h_3 - h_{4s}} \quad \text{(turbine)}
$$

**Polytropic efficiency** represents the efficiency of an infinitesimally small compression or expansion step, and is independent of the overall pressure ratio:

$$
\eta_p = \frac{(\gamma - 1)/\gamma}{(n - 1)/n}
$$

where $n$ is the polytropic exponent. Polytropic efficiency is preferred for comparing machines of different pressure ratios because it represents the inherent aerodynamic quality of the blading. A compressor with 87% polytropic efficiency at a pressure ratio of 15 will have a lower isentropic efficiency than the same machine at a pressure ratio of 5, even though the aerodynamic performance is identical.

For gas turbine compressor sections, typical polytropic efficiencies are 88–92%, while isentropic efficiencies range from 83–88% depending on the pressure ratio. In NeqSim, both efficiency definitions are supported when modeling compressor and turbine stages.

### Compressor-Turbine Matching

In a single-shaft gas turbine, the compressor and turbine are mechanically coupled and must operate at the same speed. The matching condition requires that the turbine produces exactly the work consumed by the compressor plus the net output:

$$
W_{turbine} = W_{compressor} + W_{net} + W_{mechanical\ losses}
$$

At part-load, the operating point moves along the compressor map. The gas generator speed decreases, reducing both air flow and pressure ratio. The turbine inlet temperature also decreases to maintain the energy balance. This matching behavior means that gas turbine part-load efficiency drops significantly—a turbine operating at 50% load may have 15–25% lower thermal efficiency than at full load.

In twin-shaft (free power turbine) designs, the gas generator and power turbine operate at independent speeds. The gas generator adjusts its speed and firing temperature to match the load, while the power turbine speed can vary to match the driven equipment (e.g., a compressor). This is particularly advantageous for compressor drives where the process demands variable speed.

### Part-Load Performance

Gas turbine part-load performance is a critical consideration for production optimization because process demands fluctuate with production rate, well arrivals, and ambient conditions. The part-load heat rate increases approximately as:

$$
HR_{part} \approx HR_{full} \times \left(\frac{P_{full}}{P_{actual}}\right)^{0.3}
$$

This means operating two turbines at 75% load is less fuel-efficient than operating one at 100% load and one on standby—a key consideration for the power management system. In practice, operators use "one-and-a-half" strategies: one turbine at full load and the second at minimum load (spinning reserve), ramping up only when needed.

### Gas Turbine Selection for Oil and Gas

The selection of gas turbine type depends on application, site conditions, and operational requirements:

**Aeroderivative gas turbines** (derived from aircraft engines) are preferred for offshore platforms and FPSOs due to:
- Compact size and low weight (power-to-weight ratio 3–5 times better than industrial frames)
- High simple-cycle efficiency (38–44% at ISO conditions)
- Rapid startup (minutes vs. hours for industrial frames)
- Modular maintenance via gas generator swap-out (24–72 hours vs. weeks for in-situ overhaul)
- Good part-load efficiency due to variable geometry

**Industrial frame gas turbines** are preferred for large onshore facilities and LNG plants:
- Higher power output per unit (up to 350+ MW)
- Lower cost per installed MW
- Longer maintenance intervals (32,000–48,000 hours between hot gas path inspections)
- Designed for continuous base-load operation

Common offshore gas turbine models and their characteristics:

| Model | Manufacturer | Power (MW, ISO) | Efficiency (%) | Weight (t) | Application |
|-------|-------------|----------------|----------------|-----------|-------------|
| LM2500+ | GE | 30–33 | 37–39 | 4.7 | Widely used NCS, UKCS |
| LM6000 | GE | 40–47 | 41–43 | 8.0 | Large platforms, FPSOs |
| Trent 60 | Rolls-Royce | 58–64 | 42–44 | 9.5 | High-power applications |
| SGT-A65 (ex-Avon) | Siemens Energy | 16–22 | 33–36 | 3.6 | Compact platforms |
| SGT-A35 (ex-RB211) | Siemens Energy | 34–38 | 38–40 | 6.2 | Medium platforms |
| LM9000 | GE | 66–75 | 44 | 10.0 | Next-generation FPSO |

### Ambient Temperature Effects and ISO Correction

Gas turbine output is strongly affected by ambient temperature, which impacts air density and thus mass flow through the compressor. Manufacturers rate gas turbines at ISO conditions: 15°C, 60% relative humidity, sea level (101.325 kPa). The actual power at site conditions is:

$$
P_{actual} = P_{ISO} \times \frac{T_{ISO}}{T_{ambient}} \times \frac{P_{ambient}}{P_{ISO,atm}} \times K_{humidity}
$$

where temperatures are in Kelvin, pressures in absolute units, and $K_{humidity}$ is a humidity correction factor (typically 0.98–1.02). A simplified empirical correction for aeroderivatives is:

$$
P_{actual} \approx P_{ISO} \times \left(\frac{288.15}{T_{ambient}}\right)^{n}
$$

where $n \approx 1.5$ for aeroderivatives and $n \approx 1.3$ for industrial frames. A 10°C increase in ambient temperature typically reduces gas turbine output by 5–8% for aeroderivatives and 3–5% for industrial frames. On a platform with 50 MW installed capacity, a hot summer day can reduce available power by 3–4 MW—potentially the difference between meeting production targets and forced curtailment.

Altitude also reduces output: each 300 m of elevation reduces air density by approximately 3.5%, with a corresponding reduction in power output. This is relevant for high-altitude onshore facilities in regions like the Andes or Central Asia.

### Fuel Gas Consumption

The fuel gas consumption rate is directly related to power output and thermal efficiency:

$$
\dot{m}_{fuel} = \frac{P_{shaft}}{\eta_{th} \times LHV_{fuel}}
$$

where $LHV_{fuel}$ is the lower heating value of the fuel gas (typically 46,000–50,000 kJ/kg for treated natural gas). Fuel gas is sourced from the process gas stream, so higher fuel consumption reduces the saleable gas volume—a direct link between power generation efficiency and production economics. On a typical Norwegian platform, fuel gas consumption is 3–7% of total gas production.

### NeqSim Gas Turbine Modeling

NeqSim provides the `GasTurbine` class for modeling gas turbine performance in process simulations:

```python
from neqsim import jneqsim

# Create fuel gas stream
fuel_gas = jneqsim.thermo.system.SystemSrkEos(288.15, 20.0)
fuel_gas.addComponent("methane", 0.90)
fuel_gas.addComponent("ethane", 0.06)
fuel_gas.addComponent("propane", 0.03)
fuel_gas.addComponent("CO2", 0.01)
fuel_gas.setMixingRule("classic")

fuel_stream = jneqsim.process.equipment.stream.Stream("Fuel Gas", fuel_gas)
fuel_stream.setFlowRate(500.0, "kg/hr")
fuel_stream.setTemperature(25.0, "C")
fuel_stream.setPressure(20.0, "bara")

# Create gas turbine
GasTurbine = jneqsim.process.equipment.powergeneration.GasTurbine
gas_turbine = GasTurbine("GT-001", fuel_stream)

# Set design parameters
gas_turbine.setIsentropicEfficiency(0.88)
gas_turbine.setCombustionTemperature(1200.0 + 273.15)  # K
gas_turbine.setPressureRatio(18.0)
gas_turbine.setAmbientTemperature(15.0 + 273.15)       # K
gas_turbine.setAmbientPressure(1.01325)                 # bara

# Run simulation
gas_turbine.run()

# Retrieve results
power_output = gas_turbine.getPower("MW")
efficiency = gas_turbine.getThermalEfficiency()
exhaust_temp = gas_turbine.getExhaustTemperature() - 273.15  # C

print(f"Gas turbine power output: {power_output:.2f} MW")
print(f"Thermal efficiency: {efficiency*100:.1f}%")
print(f"Exhaust temperature: {exhaust_temp:.0f} C")
```

### Gas Turbine Performance at Varying Ambient Temperature

```python
from neqsim import jneqsim
import matplotlib.pyplot as plt

GasTurbine = jneqsim.process.equipment.powergeneration.GasTurbine

# Sweep ambient temperature from -20 to +40 C
ambient_temps = list(range(-20, 42, 2))
power_results = []
efficiency_results = []

for t_amb in ambient_temps:
    fuel_gas = jneqsim.thermo.system.SystemSrkEos(288.15, 25.0)
    fuel_gas.addComponent("methane", 0.92)
    fuel_gas.addComponent("ethane", 0.05)
    fuel_gas.addComponent("propane", 0.02)
    fuel_gas.addComponent("nitrogen", 0.01)
    fuel_gas.setMixingRule("classic")

    fuel_stream = jneqsim.process.equipment.stream.Stream("Fuel", fuel_gas)
    fuel_stream.setFlowRate(600.0, "kg/hr")
    fuel_stream.setTemperature(25.0, "C")
    fuel_stream.setPressure(25.0, "bara")

    gt = GasTurbine("GT-sweep", fuel_stream)
    gt.setIsentropicEfficiency(0.88)
    gt.setCombustionTemperature(1473.15)
    gt.setPressureRatio(20.0)
    gt.setAmbientTemperature(t_amb + 273.15)
    gt.setAmbientPressure(1.01325)
    gt.run()

    power_results.append(gt.getPower("MW"))
    efficiency_results.append(gt.getThermalEfficiency() * 100.0)

# Plot results
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(ambient_temps, power_results, 'b-o', label='Power output')
ax1.set_xlabel('Ambient temperature (C)')
ax1.set_ylabel('Power output (MW)', color='b')
ax2 = ax1.twinx()
ax2.plot(ambient_temps, efficiency_results, 'r-s', label='Efficiency')
ax2.set_ylabel('Thermal efficiency (%)', color='r')
ax1.set_title('Gas Turbine Performance vs. Ambient Temperature')
ax1.grid(True)
fig.tight_layout()
plt.savefig('figures/gt_ambient_performance.png', dpi=150, bbox_inches='tight')
plt.show()
```

![Gas turbine power output and efficiency as a function of ambient temperature](figures/gt_ambient_performance.png)

## Heat Recovery Steam Generators (HRSG)

### Waste Heat Recovery Principles

Gas turbine exhaust typically exits at 400–550°C, representing 55–70% of the fuel's energy content. A Heat Recovery Steam Generator (HRSG) captures this waste heat to produce steam for:

- **Power generation** via steam turbines (combined cycle)
- **Process heating** — reboiler duty, glycol regeneration, oil heating
- **Steam injection** — enhanced oil recovery

The HRSG thermal balance is:

$$
Q_{HRSG} = \dot{m}_{exhaust} \times c_p \times (T_{exhaust,in} - T_{stack})
$$

where $T_{stack}$ is the minimum stack temperature (typically 120–170°C to avoid acid dew point corrosion from sulfur compounds in the fuel gas).

### Single-Pressure, Dual-Pressure, and Triple-Pressure HRSG

HRSG configurations are classified by the number of steam pressure levels:

**Single-pressure HRSG** produces steam at one pressure level (typically 30–60 bara). This is the simplest and most common offshore configuration, but it leaves a significant temperature gap between the exhaust gas and the steam generation temperature, limiting heat recovery.

**Dual-pressure HRSG** adds a low-pressure (LP) steam generation level (typically 3–8 bara) below the high-pressure (HP) level. The LP section recovers additional heat from the lower-temperature portion of the exhaust, increasing total heat recovery by 10–15%. The LP steam can drive a separate turbine section or provide process heat.

**Triple-pressure HRSG** (with or without reheat) is standard for large onshore combined cycle plants. It adds an intermediate-pressure (IP) level and may include reheating of the HP steam after partial expansion. Triple-pressure reheat HRSGs achieve the highest combined cycle efficiencies (>60%) but are too complex and heavy for most offshore applications.

### Pinch Point and Approach Temperature

Two critical thermal design parameters govern HRSG performance:

**Pinch point** ($\Delta T_{pp}$) is the minimum temperature difference between the exhaust gas and the saturated steam temperature at the evaporator. Typical values are 8–25°C. A smaller pinch point increases heat recovery but requires more heat transfer area (larger, heavier, more expensive HRSG):

$$
\Delta T_{pp} = T_{gas,evap\ exit} - T_{sat}
$$

**Approach temperature** ($\Delta T_{app}$) is the difference between the saturation temperature and the feedwater temperature entering the evaporator:

$$
\Delta T_{app} = T_{sat} - T_{feedwater,evap\ entry}
$$

Typical approach temperatures are 5–15°C. Too small an approach temperature risks steaming in the economizer, which can cause water hammer and tube damage.

The steam production rate from an HRSG can be estimated from:

$$
\dot{m}_{steam} = \frac{\dot{m}_{exhaust} \cdot c_p \cdot (T_{exhaust} - T_{stack})}{h_{steam} - h_{feedwater}}
$$

where $h_{steam}$ and $h_{feedwater}$ are the specific enthalpies of the superheated steam and subcooled feedwater, respectively.

### Supplementary Firing

Supplementary (duct) firing injects additional fuel into the HRSG duct upstream of the heat transfer sections. Because the exhaust gas contains 13–15% oxygen (far more than needed for combustion), additional fuel can be burned with nearly 100% efficiency—much higher than the 30–40% efficiency of the gas turbine itself.

Supplementary firing is used to:
- Boost steam production during peak power demand periods
- Maintain steam supply when gas turbine load decreases
- Provide operational flexibility for combined heat and power (CHP) applications

The penalty is increased fuel consumption and emissions, but the marginal efficiency for the supplementary firing portion is very high (near 100% conversion to useful heat).

### HRSG Performance Curves

HRSG performance varies with gas turbine load because exhaust temperature and mass flow change together. At reduced gas turbine load:
- Exhaust mass flow decreases roughly proportional to power output
- Exhaust temperature decreases (single-shaft units) or remains roughly constant (twin-shaft units)
- Steam production decreases, reducing bottoming cycle power

For twin-shaft aeroderivatives, the nearly constant exhaust temperature at reduced load is advantageous because it maintains reasonable HRSG effectiveness even at part-load. This characteristic makes aeroderivative combined cycles more attractive for variable-load offshore applications than industrial frame combined cycles.

## Combined Cycle Power Systems

### Plant-Level Heat and Power Balance

A combined cycle plant consists of one or more gas turbines, each with an HRSG, feeding steam to one or more steam turbines. The overall thermal efficiency is:

$$
\eta_{CC} = \eta_{GT} + \eta_{ST} \times (1 - \eta_{GT}) = \eta_{GT} + \eta_{bottoming} \times (1 - \eta_{GT})
$$

where $\eta_{GT}$ is the gas turbine (topping cycle) efficiency and $\eta_{bottoming}$ is the steam cycle (bottoming cycle) efficiency. For a gas turbine at 38% and a bottoming cycle at 33%, the combined cycle efficiency is:

$$
\eta_{CC} = 0.38 + 0.33 \times (1 - 0.38) = 0.38 + 0.205 = 0.585 \approx 59\%
$$

This represents a 55% improvement over the simple cycle gas turbine alone. State-of-the-art onshore combined cycle plants (e.g., GE HA class, Siemens HL class) now exceed 63% net efficiency.

### Combined Cycle Configurations

Combined cycle plants are typically described by their gas-turbine-to-steam-turbine ratio:

**1+1 configuration**: One gas turbine and one steam turbine. Common for smaller installations (30–100 MW total). Offers lower CAPEX but has lower flexibility—the entire plant must shut down for gas turbine maintenance.

**2+1 configuration**: Two gas turbines feeding one steam turbine. The most common configuration for medium to large plants (100–500 MW). Provides better availability (one gas turbine can maintain partial load) and better part-load efficiency since the steam turbine can operate at higher load percentage when only one gas turbine is running.

**3+1 configuration**: Three gas turbines with one steam turbine. Used for very large installations. Provides high redundancy but with diminishing returns on availability improvement.

### Offshore Combined Cycle Applications

Combined cycle on offshore platforms is less common than onshore due to weight, space, and complexity constraints. However, several FPSO and large platform designs have incorporated combined cycle to reduce fuel consumption and emissions:

- Steam turbines add 1–5 MW of power from waste heat
- Overall efficiency improves from 35–40% (simple cycle) to 45–50%
- CO$_2$ reduction of 20–30% compared to simple cycle for the same power output
- Weight penalty of the steam system must be justified by fuel savings over field life

The economic case for offshore combined cycle depends on the fuel gas value, CO$_2$ tax rate, and platform lifetime. At Norwegian CO$_2$ tax rates (currently exceeding 900 NOK/tonne including EU ETS), the payback period for combined cycle offshore is often 3–5 years.

### NeqSim Combined Cycle Modeling

```python
from neqsim import jneqsim

GasTurbine = jneqsim.process.equipment.powergeneration.GasTurbine
SteamTurbine = jneqsim.process.equipment.powergeneration.SteamTurbine
HRSG = jneqsim.process.equipment.powergeneration.HRSG

# --- Gas turbine setup ---
fuel_gas = jneqsim.thermo.system.SystemSrkEos(288.15, 25.0)
fuel_gas.addComponent("methane", 0.91)
fuel_gas.addComponent("ethane", 0.05)
fuel_gas.addComponent("propane", 0.02)
fuel_gas.addComponent("CO2", 0.015)
fuel_gas.addComponent("nitrogen", 0.005)
fuel_gas.setMixingRule("classic")

fuel_stream = jneqsim.process.equipment.stream.Stream("Fuel Gas", fuel_gas)
fuel_stream.setFlowRate(600.0, "kg/hr")
fuel_stream.setTemperature(25.0, "C")
fuel_stream.setPressure(25.0, "bara")

gas_turbine = GasTurbine("GT-001", fuel_stream)
gas_turbine.setIsentropicEfficiency(0.88)
gas_turbine.setCombustionTemperature(1473.15)
gas_turbine.setPressureRatio(20.0)
gas_turbine.setAmbientTemperature(288.15)
gas_turbine.setAmbientPressure(1.01325)
gas_turbine.run()

# --- HRSG setup ---
hrsg = HRSG("HRSG-001")
hrsg.setExhaustStream(gas_turbine.getExhaustStream())
hrsg.setSteamPressure(40.0, "bara")
hrsg.setSteamTemperature(673.15)
hrsg.setMinStackTemperature(423.15)
hrsg.run()

# --- Steam turbine ---
steam_turbine = SteamTurbine("ST-001")
steam_turbine.setInletStream(hrsg.getSteamOutStream())
steam_turbine.setOutletPressure(0.08, "bara")
steam_turbine.setIsentropicEfficiency(0.85)
steam_turbine.run()

# --- Combined cycle results ---
gt_power = gas_turbine.getPower("MW")
st_power = steam_turbine.getPower("MW")
total_power = gt_power + st_power
print(f"Gas turbine power: {gt_power:.2f} MW")
print(f"Steam turbine power: {st_power:.2f} MW")
print(f"Total combined cycle power: {total_power:.2f} MW")
print(f"Combined cycle efficiency gain: {st_power/gt_power*100:.1f}% additional power")
```

## Steam Turbines and Steam Systems

### Steam Turbine Types

| Type | Application | Back Pressure | Efficiency |
|------|------------|---------------|------------|
| Condensing | Maximum power extraction | Vacuum (0.05–0.1 bara) | 30–38% |
| Back-pressure | Process steam + power | 3–40 bara | 20–28% |
| Extraction | Variable steam/power | Multiple pressures | 25–35% |

Back-pressure steam turbines are common in oil and gas facilities where process steam is needed simultaneously with power. The steam passes through the turbine, generating power, then exits at a useful pressure for heating duties.

### Steam Balance and Optimization

In a facility with both power and heating demands, the steam balance determines how much power can be generated. The optimization problem becomes:

$$
\max \sum_{j} P_{ST,j} \quad \text{subject to} \quad \sum_{j} \dot{m}_{steam,j} \leq \dot{m}_{HRSG} \quad \text{and} \quad \dot{Q}_{process} \leq \sum_{k} \dot{m}_k h_k
$$

where the total steam production must satisfy both power generation and process heating requirements. During winter (high heating demand), less steam is available for power generation, potentially limiting compressor capacity and thus production.

## Electric Motor Drives

### Motor Types and Selection

Electric motors provide an alternative to gas turbine drives, with several advantages:

- **Higher efficiency** — Electric motors achieve 93–97% efficiency vs. 30–42% for gas turbines
- **Lower emissions** — Zero direct CO$_2$ emissions at point of use (if grid-powered)
- **Precise speed control** — Variable Frequency Drives (VFDs) enable continuous speed adjustment
- **Lower maintenance** — Fewer moving parts, no combustion system
- **Instant startup** — No warm-up or ramp-up time required

The selection of motor type depends on power rating, speed requirements, and control strategy:

| Motor Type | Power Range | Efficiency | Speed Control | Typical Application |
|-----------|------------|------------|---------------|---------------------|
| Induction (squirrel cage) | 0.1–30 MW | 93–97% | VFD required | General purpose, pumps |
| Synchronous | 1–100 MW | 95–98% | Direct or VFD | Large compressor drives |
| Permanent magnet (PM) | 0.5–15 MW | 96–98% | VFD required | High-speed compressors |
| High-speed induction | 0.5–15 MW | 94–97% | Integrated VFD | Gearless compressor drives |

**Induction motors** are the workhorses of industrial applications. The rotor speed is slightly below synchronous speed, with the difference (slip) proportional to load. They are robust, inexpensive, and available in very large sizes, but require a VFD for speed control.

**Synchronous motors** operate at exactly synchronous speed and can provide or absorb reactive power (power factor correction). For large compressor drives above 10 MW, synchronous motors are often preferred because of their higher efficiency and ability to improve the facility power factor.

**Permanent magnet motors** use rare-earth magnets in the rotor, eliminating rotor losses and enabling very high efficiency. They are increasingly used for high-speed compressor drives where direct coupling (no gearbox) is desired, particularly in subsea applications.

### Variable Frequency Drives and the Affinity Laws

Variable Frequency Drives (VFDs) convert fixed-frequency AC power to variable-frequency AC, enabling continuous speed control of AC motors. For centrifugal machines (compressors, pumps, fans), the relationship between speed and performance follows the affinity laws:

$$
P \propto N^3, \quad Q \propto N, \quad H \propto N^2
$$

where $P$ is power, $Q$ is volumetric flow rate, $H$ is head (pressure rise), and $N$ is rotational speed. These relationships have profound implications for energy efficiency:

- Reducing speed by 10% reduces power consumption by approximately 27%
- Reducing speed by 20% reduces power consumption by approximately 49%
- Reducing speed by 50% reduces power consumption by approximately 87%

### Energy Savings: VFD vs. Throttle vs. Recycle Control

When process demand drops below design capacity, there are three main strategies:

**Throttle control** — A control valve downstream of the machine adds artificial resistance. The machine operates at full speed, with the excess pressure dropped across the valve. Energy is wasted as valve pressure drop.

**Recycle (spillback) control** — Excess flow is recycled from discharge back to suction. The machine operates at full speed and near-design flow, but the useful output is reduced. Energy is wasted compressing gas that is immediately expanded back.

**VFD speed control** — The machine speed is reduced to match the actual demand. The affinity laws ensure that power consumption decreases with the cube of speed, providing the lowest energy consumption at any partial-load condition.

For a centrifugal compressor operating at 70% of design flow, the approximate power consumption under each strategy is:

| Control Method | Power Consumption (% of design) |
|---------------|-------------------------------|
| VFD speed control | ~34% (cube law) |
| Throttle control | ~80% |
| Recycle control | ~100% |

The energy savings from VFD operation are dramatic—on a 15 MW compressor operating at 70% average load, a VFD saves approximately 7 MW compared to recycle control, corresponding to roughly $3–5 million per year in fuel gas savings (depending on gas price and efficiency).

VFDs also provide additional operational benefits:
- **Soft starting** — Reduced electrical inrush and mechanical stress
- **Anti-surge integration** — Smooth speed adjustment near surge boundary
- **Process control** — Direct flow/pressure control without recycle valve losses

### Power Factor and Electrical System Design

The total electrical load on a platform or facility determines the required power generation capacity:

$$
P_{total} = \sum_{i=1}^{n} P_{motor,i} \times \frac{SF_i}{\eta_i \times PF_i}
$$

where $SF$ is the service factor (typically 1.0–1.15), $\eta$ is motor efficiency, and $PF$ is the power factor. VFDs introduce harmonic distortion into the electrical system, which must be managed through input line reactors, harmonic filters, or multi-pulse rectifier designs (12-pulse or 18-pulse) to comply with IEEE 519 harmonic limits.

## Fuel Gas Systems

### Fuel Gas Conditioning Requirements

Gas turbines are sensitive to fuel gas quality. The fuel gas system must condition process gas to meet strict specifications through:

1. **Liquid knockout** — A scrubber or coalescing filter removes entrained liquids and aerosols. Liquid carryover into the combustor causes hot spots, flame instability, and thermal shock damage to nozzles and liners.

2. **Heating** — Fuel gas must be superheated above its hydrocarbon dew point (typically by 28°C or more) to prevent condensation in fuel control valves and manifolds. A fuel gas heater (using waste heat or electric heating) raises the temperature to 30–60°C.

3. **Pressure regulation** — Fuel pressure must be maintained within a narrow band, typically 20–35 barg for aeroderivative turbines. A pressure control valve with downstream pressure transmitter ensures stable supply.

4. **Filtration** — Particulate filters (typically 5 μm) remove solid contaminants that could erode or plug fuel nozzles.

### Fuel Gas Quality Parameters

| Parameter | Typical Limit | Consequence of Violation |
|-----------|--------------|--------------------------|
| Wobbe Index | 35–55 MJ/Sm$^3$ | Combustion instability, emissions |
| H$_2$S content | < 20 ppmv | Hot corrosion of turbine blades |
| Liquid content | Superheat > 28°C | Flame-out, nozzle damage |
| Supply pressure | 20–35 barg | Insufficient for combustion nozzles |
| Temperature | 0–60°C | Condensation or coking |
| Na + K | < 0.01 ppmw | Turbine blade corrosion |
| V + Pb | < 0.01 ppmw | Ash deposition, corrosion |

The **Wobbe Index** is the key interchangeability parameter for gas turbines. It is defined as the higher heating value divided by the square root of the specific gravity:

$$
WI = \frac{HHV}{\sqrt{SG}} = \frac{HHV}{\sqrt{MW_{gas}/MW_{air}}}
$$

A constant Wobbe Index ensures constant heat input to the combustor for a given fuel valve position, regardless of fuel composition changes. This is important for platforms where the fuel gas composition changes as the reservoir depletes or when switching between different fuel sources.

### Dual-Fuel Operation

Some gas turbines (particularly industrial frames) can operate on both gas and liquid fuel (diesel). Dual-fuel capability provides:
- Backup fuel supply if gas fuel is temporarily unavailable (e.g., during plant startup before process gas is available)
- Flexibility to optimize fuel costs when liquid fuels are cheaper
- Emergency power generation during gas system upsets

The fuel system includes separate fuel manifolds, nozzles optimized for each fuel type, and a transfer mechanism to switch between fuels (either under load or during a brief shutdown). Offshore platforms commonly carry a diesel inventory for initial startup and emergency backup, even when normal operation uses process gas.

### NeqSim Fuel Gas Modeling

```python
from neqsim import jneqsim

# Model fuel gas conditioning and quality checking
fuel_gas = jneqsim.thermo.system.SystemSrkEos(288.15, 25.0)
fuel_gas.addComponent("methane", 0.88)
fuel_gas.addComponent("ethane", 0.06)
fuel_gas.addComponent("propane", 0.03)
fuel_gas.addComponent("CO2", 0.02)
fuel_gas.addComponent("nitrogen", 0.01)
fuel_gas.setMixingRule("classic")

# Flash to check phase behavior
ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fuel_gas)
ops.TPflash()
fuel_gas.initProperties()

# Calculate heating value using NeqSim
molar_mass = fuel_gas.getMolarMass() * 1000  # g/mol
sg = molar_mass / 28.97  # Specific gravity relative to air

# Fuel gas consumption for 30 MW gas turbine at 38% efficiency
gt_power_kw = 30000.0
gt_efficiency = 0.38
lhv_fuel = 48000.0  # kJ/kg for methane-rich fuel gas
fuel_rate = gt_power_kw / (gt_efficiency * lhv_fuel)  # kg/s
fuel_rate_kg_hr = fuel_rate * 3600.0
print(f"Fuel gas consumption: {fuel_rate_kg_hr:.0f} kg/hr")
print(f"Fuel gas specific gravity: {sg:.3f}")
print(f"Fuel gas molar mass: {molar_mass:.1f} g/mol")
```

### Fuel Gas as Production Optimization Variable

The fuel gas take-off from the process gas stream creates a direct link between power generation and sales gas production:

$$
Q_{sales} = Q_{total} - Q_{fuel} - Q_{flare} - Q_{lift}
$$

where $Q_{fuel}$ is the fuel gas consumption. Improving gas turbine efficiency by 1% can increase saleable gas by 0.3–0.5% of total production—a significant economic impact over field life. This is one reason why combined cycle and platform electrification projects have attractive economics even with high upfront costs.

## CO$_2$ Emissions from Power Generation

### Emission Factor Calculation

The CO$_2$ emissions from gas turbine operation are calculated from the carbon content of the fuel:

$$
E_{CO_2} = \dot{m}_{fuel} \times EF_{CO_2}
$$

where $EF_{CO_2}$ is the emission factor. For pure methane combustion:

$$
CH_4 + 2O_2 \rightarrow CO_2 + 2H_2O
$$

The stoichiometric emission factor is $44/16 = 2.75$ kg CO$_2$ per kg methane. For a typical North Sea fuel gas with ethane and propane, the composite emission factor is approximately 2.7–2.8 kg CO$_2$ per kg fuel.

### Scope 1 vs. Scope 2 Emissions

The Greenhouse Gas Protocol distinguishes between:

**Scope 1 (direct emissions)** — CO$_2$ from fuel combustion on site. This includes gas turbine exhaust, flaring, and emergency diesel generators. For a typical offshore platform, Scope 1 emissions are 50,000–300,000 tonnes CO$_2$ per year, dominated by gas turbine exhaust (70–90% of total).

**Scope 2 (indirect emissions from purchased energy)** — CO$_2$ associated with electricity imported from external sources. For an electrified platform receiving power from shore, Scope 1 emissions drop to near zero, but Scope 2 emissions depend on the carbon intensity of the onshore electricity grid. In Norway, where hydropower dominates, the grid emission factor is approximately 8–20 g CO$_2$/kWh, compared to 400–500 g CO$_2$/kWh for gas-fired electricity.

This distinction is critical for platform electrification decisions: replacing a 35%-efficient offshore gas turbine with Norwegian hydropower reduces total lifecycle emissions by over 95%.

### Norwegian CO$_2$ Tax and EU ETS

Norwegian offshore operators face a combined carbon cost from two mechanisms:

1. **Norwegian CO$_2$ tax** — Applied to all fuel gas combustion on the NCS, currently approximately 600 NOK/tonne CO$_2$ (2024)
2. **EU Emissions Trading System (EU ETS)** — Requires purchase of allowances, currently approximately 70 EUR/tonne CO$_2$

The combined carbon cost is approximately 900–1,000 NOK/tonne CO$_2$ (~90 USD/tonne), among the highest in the world. For a platform emitting 150,000 tonnes CO$_2$/year, the annual carbon cost is approximately 135 million NOK (~13 million USD). This substantial cost directly incentivizes:
- Higher gas turbine efficiency (combined cycle)
- Waste heat recovery
- Platform electrification from shore
- Reduced flaring and methane emissions

### Emissions Intensity and Carbon Reporting

The emissions intensity (kg CO$_2$ per barrel of oil equivalent) is a key sustainability metric used for benchmarking and regulatory reporting:

$$
CI = \frac{E_{CO_2,annual}}{Q_{production,annual}}
$$

Typical values range from 5–15 kg CO$_2$/boe for efficient modern platforms with electrification to 50–100+ kg CO$_2$/boe for aging platforms with declining production. The global upstream industry average is approximately 15–20 kg CO$_2$/boe.

### NeqSim Emissions Tracking

```python
# Track CO2 emissions and carbon cost
fuel_rate_kg_hr = 500.0
co2_emission_factor = 2.75  # kg CO2 per kg fuel gas
ch4_slip = 0.02             # 2% methane slip
ch4_gwp = 28                # 100-year GWP for methane

# Calculate emissions
co2_direct = fuel_rate_kg_hr * co2_emission_factor
ch4_emissions_co2eq = fuel_rate_kg_hr * ch4_slip * ch4_gwp
total_co2eq_kg_hr = co2_direct + ch4_emissions_co2eq

# Annual totals
hours_per_year = 8760 * 0.95  # 95% uptime
annual_co2_tonnes = total_co2eq_kg_hr * hours_per_year / 1000.0

# Carbon cost (Norwegian NCS)
no_co2_tax_nok_per_tonne = 600.0
eu_ets_eur_per_tonne = 70.0
eur_to_nok = 11.5
total_carbon_cost_nok = annual_co2_tonnes * (
    no_co2_tax_nok_per_tonne + eu_ets_eur_per_tonne * eur_to_nok)

# Emissions intensity
production_boe_per_day = 50000
annual_boe = production_boe_per_day * 365
emissions_intensity = annual_co2_tonnes * 1000 / annual_boe

print(f"Annual CO2-eq emissions: {annual_co2_tonnes:.0f} tonnes")
print(f"Annual carbon cost: {total_carbon_cost_nok/1e6:.1f} MNOK")
print(f"Emissions intensity: {emissions_intensity:.1f} kg CO2/boe")
```

## Power as a Capacity Constraint

### The Power Availability Problem

On many offshore platforms, power generation capacity is the ultimate binding constraint on production. The total facility power demand includes:

| Consumer | Typical Load | % of Total |
|----------|-------------|------------|
| Gas compression | 40–70% | Dominant consumer |
| Water injection pumps | 10–20% | Increases with water cut |
| Oil export pumps | 3–8% | Varies with export route |
| Process utilities (cooling, heating) | 5–15% | Climate dependent |
| Drilling/workover | 5–15% | Intermittent |
| Living quarters, safety systems | 2–5% | Base load |

As the field matures, several trends converge to create a power crunch:

1. **Declining reservoir pressure** requires more gas compression power
2. **Increasing water cut** requires more water injection/handling power
3. **Gas turbine degradation** reduces available power output over time (2–5% between overhauls)
4. **Higher ambient temperature** (seasonal) reduces gas turbine capacity
5. **Increased gas-oil ratio** produces more gas per barrel of oil, requiring more compression

### Power Demand Curves and Production Rate

The relationship between production rate and power demand is nonlinear. Gas compression power increases faster than production rate because higher flow rates create higher pressure drops in the flowline and separator, requiring more compression work. The approximate relationship is:

$$
P_{comp} \approx k \cdot Q^{1.2-1.5}
$$

where $k$ depends on the specific system and operating conditions. This means a 10% increase in production rate requires a 12–15% increase in compression power. Water injection power scales more linearly with water production rate.

### Seasonal Variation

Power availability varies seasonally due to ambient temperature effects on gas turbines. On the Norwegian Continental Shelf:
- **Winter** (-5 to +5°C): Gas turbines produce 105–115% of ISO rating
- **Summer** (15 to 25°C): Gas turbines produce 90–100% of ISO rating

This 15–25% seasonal swing in available power can create summer bottlenecks on platforms operating near capacity limits. Some operators plan maintenance shutdowns during summer when power margins are tightest, while others curtail production.

### Power Management During Startup and Trips

Platform startup requires careful power management because process loads ramp up sequentially while gas turbines need load to reach operating temperature and efficiency. Typical startup sequences:

1. Emergency diesel generator starts first (safety systems, lighting)
2. First gas turbine started on diesel/imported fuel gas
3. Process systems brought online sequentially (separation → compression → injection)
4. Remaining gas turbines started as load increases
5. Steady-state operation reached over 12–48 hours

During a gas turbine trip, load shedding must act within milliseconds to prevent cascade failure. The load shedding controller sheds non-essential consumers in priority order while maintaining frequency and voltage within acceptable limits.

### Modeling Power Constraints in NeqSim

NeqSim integrates power constraints into the production optimization framework through the `CapacityConstrainedEquipment` interface:

```python
from neqsim import jneqsim

ProcessSystem = jneqsim.process.processmodel.ProcessSystem
Compressor = jneqsim.process.equipment.compressor.Compressor
ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer

# Build process with multiple power consumers
process = ProcessSystem()
# ... (add feed, separators, etc.)

# Compressor with power constraint
comp = Compressor("Export Compressor", gas_stream)
comp.setOutletPressure(150.0, "bara")
comp.setMaximumPower(15000.0)  # 15 MW driver limit (HARD constraint)
comp.setMaximumSpeed(11000.0)  # RPM limit
process.add(comp)

process.run()

# Check power utilization
power_used = comp.getPower("kW")
max_power = 15000.0
utilization = power_used / max_power
print(f"Compressor power: {power_used:.0f} kW ({utilization*100:.1f}% of driver)")

# Run production optimization with power as constraint
OptConfig = ProductionOptimizer.OptimizationConfig
config = OptConfig(5000.0, 50000.0).rateUnit("kg/hr") \
    .defaultUtilizationLimit(0.95) \
    .searchMode(ProductionOptimizer.SearchMode.BINARY_FEASIBILITY)

result = ProductionOptimizer.optimize(process, feed, config)
print(f"Optimal rate: {result.getOptimalRate():.0f} kg/hr")
print(f"Bottleneck: {result.getBottleneck().getName()}")
```

### Multi-Driver Power Allocation

When multiple gas turbines supply power to multiple consumers through a shared electrical grid, the power allocation problem becomes:

$$
\max \sum_{w} Q_w \quad \text{subject to} \quad \sum_{c} P_c(Q) + \sum_{p} P_p(Q) + P_{aux} \leq \sum_{g} P_{GT,g}(T_{amb})
$$

where the total power demand from compressors ($P_c$), pumps ($P_p$), and auxiliaries ($P_{aux}$) must not exceed the total generation capacity of all gas turbines ($P_{GT,g}$), which itself depends on ambient temperature. This whole-facility power balance creates coupling between otherwise independent process trains.

### The GasTurbineUnit Driver Model

NeqSim models the prime mover explicitly with the `GasTurbineUnit` class (package `neqsim.process.equipment.powergeneration.gasturbine`). Unlike a fixed power limit on a single compressor, `GasTurbineUnit` represents a real driver: it has a rated capacity that varies with ambient conditions and degradation, it aggregates the demand of one or more power consumers, and it reports fuel burn and emissions:

```python
gtpkg = jneqsim.process.equipment.powergeneration.gasturbine
GasTurbineUnit = gtpkg.GasTurbineUnit

gt = GasTurbineUnit("GT-A", fuelGasStream, spec)
gt.setAmbient(273.15 + 15.0, 1.01325)        # ISO conditions (K, bara)
gt.addPowerConsumer(exportCompressor)         # turbine drives the compressor
gt.addPowerConsumer(injectionCompressor)
gt.run()

print("Available power:", gt.getAvailablePowerW() / 1e6, "MW")
print("Load fraction:", gt.getLoadFraction())
print("Thermal efficiency:", gt.getThermalEfficiency())
print("Fuel burn:", gt.getFuelMassFlowKgPerHr(), "kg/hr")
print("CO2:", gt.getCO2EmissionKgPerHr(), "kg/hr",
      "(", gt.getCO2IntensityKgPerMWh(), "kg/MWh )")
print("Overloaded:", gt.isOverloaded())
```

The driver couples directly to the demand side: `addPowerConsumer(Compressor)` (or a generic `PowerDemandConsumer`) sums the shaft-power requirement, while the supply side derates with `setAmbient(...)`, `setDegradation(...)`, and the `GasTurbinePerformanceMap` set through `setPerformanceMap(...)`. Diagnostics include `getLoadFraction()`, `getEffectiveHeatRateKJPerKWh()`, `getExhaustTemperatureK()` (for the waste-heat recovery of the HRSG section), `isOverloaded()`, `isBelowMinLoad()`, and `getPowerShortfallW()`. Emissions reporting (`getCO2EmissionKgPerHr`, `getCO2IntensityKgPerMWh`, `getNOxEmissionKgPerS`, `getMethaneSlipKgPerS`) feeds the CO$_2$-tax term of the value-chain objective (Chapter 32). When `setEnforcePowerLimit(true)` is set, the unit caps allocated power (`getPowerAllocationW()`) at its available capacity so the optimizer treats the turbine itself as the binding generation constraint.

## Power System Reliability

### Redundancy Philosophy

Power system reliability is critical because power failure on an offshore platform can lead to process shutdown, flaring, and potentially unsafe conditions. The design philosophy follows established redundancy criteria:

**N+1 redundancy** means one more generating unit than required for normal operation. For a platform needing 50 MW, an N+1 configuration with three 25 MW turbines (2 running + 1 standby) ensures that any single turbine failure does not cause production loss.

**Spinning reserve** is the online generating capacity above current load that can be loaded within seconds. Typical spinning reserve requirements are 10–15% of total load, or one unit's worth of generating capacity, whichever is larger.

**Cold reserve** is the offline generating capacity that can be started within minutes to hours. Gas turbines can typically start from cold in 5–15 minutes (aeroderivative) or 20–60 minutes (industrial frame).

### Design Standards for Power Margin

| Operating Mode | Required Margin | Standard Reference |
|---------------|----------------|-------------------|
| Normal production, all generators | 10–15% spare capacity | IEC 61892, NORSOK E-001 |
| N-1 (one generator out) | Must sustain essential loads | NORSOK E-001 |
| Peak (drilling + production) | May require load shedding | Facility-specific |
| Emergency | Safety-critical loads only | IEC 61892 |

### Load Shedding Philosophy

During power system disturbances (generator trip, cable fault), automatic load shedding protects the power system by disconnecting non-essential loads in priority order:

| Priority | Loads | Shed Timing |
|----------|-------|------------|
| 1 (shed first) | Drilling drives, workover equipment | Immediate (< 100 ms) |
| 2 | Non-essential HVAC, lighting, cranes | Within 100 ms |
| 3 | Water injection pumps | Within 500 ms |
| 4 | Secondary/recompression stages | Within 1 s |
| 5 (shed last) | Primary separation, safety systems | Protected, never shed |

The load shedding strategy must maintain process safety while minimizing production loss. NeqSim's dynamic simulation capability can model transient responses to power system disturbances, including the effect of losing specific compressor stages or pump sets.

### FMEA for Power Systems

Failure Mode and Effects Analysis (FMEA) systematically identifies potential failure modes and their production impact:

| Component | Failure Mode | Effect on Production | Mitigation |
|-----------|-------------|---------------------|------------|
| Gas turbine | Unplanned trip | Loss of generation, load shed | N+1 redundancy, auto-start standby |
| VFD | Output failure | Loss of driven equipment | Bypass contactor (fixed speed) |
| Transformer | Winding fault | Section de-energized | Dual transformer feeds |
| Subsea cable | Insulation failure | Total platform blackout | Backup gas turbines, battery UPS |
| Fuel gas system | Low pressure | Gas turbine trip | Fuel gas accumulator, backup supply |

### Reliability Metrics

| Metric | Typical Value | Best-in-Class |
|--------|--------------|---------------|
| Gas turbine availability | 95–97% | >98% |
| MTBF | 10,000–25,000 hrs | >30,000 hrs |
| MTTR | 100–500 hrs | <48 hrs (modular swap) |
| Unplanned trips per year | 2–6 | <1 |
| Power system availability | 99.5–99.8% | >99.9% |

An unplanned gas turbine trip on a single-train facility can shut down production entirely. The lost production cost typically exceeds $0.5–2 million per day, making power system reliability a critical factor in facility design and maintenance planning.

### Redundancy Optimization

The optimal redundancy level balances capital cost against lost production risk:

$$
C_{total} = C_{CAPEX}(n_{GT}) + E[C_{lost\_production}(n_{GT}, MTBF, MTTR)]
$$

where $n_{GT}$ is the number of gas turbines and the expected lost production cost depends on failure rates and repair times. Monte Carlo simulation is typically used to evaluate different redundancy strategies (N+1, N+2, 2×100%, etc.).

## Platform Electrification and Power from Shore

### Drivers for Electrification

The oil and gas industry is increasingly electrifying offshore platforms by replacing gas turbines with power from shore (PFS). The business case rests on:

- **Emissions reduction** — Eliminates 50–80% of direct platform CO$_2$ emissions
- **Efficiency gain** — Shore-based CCGT at 55–60% vs. offshore simple cycle at 30–40%
- **Reduced maintenance** — Fewer rotating machines, no offshore combustion systems
- **Noise reduction** — Significant improvement in working environment
- **Regulatory compliance** — Meeting increasingly stringent NCS emissions targets

### AC vs. HVDC Transmission

The choice between AC and HVDC transmission depends on cable length and power rating:

**AC transmission** is simpler and cheaper for short distances (<80–100 km). However, AC cables have significant capacitive charging current that reduces the usable power transfer capacity. The charging current increases with cable length and voltage:

$$
I_{charging} = \omega \cdot C \cdot V \cdot L
$$

where $C$ is the cable capacitance per km, $V$ is the voltage, and $L$ is the cable length. For long submarine cables, reactive compensation (onshore and/or offshore) is needed.

**HVDC transmission** eliminates capacitive losses and allows power transfer over any distance. HVDC is preferred for cable lengths exceeding 80–100 km. Voltage Source Converter (VSC-HVDC) technology provides:
- Compact offshore converter stations
- Black-start capability (can start an offshore grid without existing power)
- Independent control of active and reactive power
- Multi-terminal capability for connecting multiple platforms

### Cable Sizing and Rating

Submarine power cables are typically rated at:
- 33–66 kV AC for short-distance, lower-power applications
- 132–220 kV AC for medium distances
- ±150 to ±320 kV DC for long-distance HVDC

Cable thermal rating depends on conductor cross-section, insulation type (XLPE for AC, mass-impregnated or XLPE for DC), installation depth, and seabed thermal resistivity. Typical ratings are 50–300 MW per cable.

### Onshore Renewable Integration

When shore power is sourced from renewable generation (hydropower, wind), the CO$_2$ reduction is maximized. The effective emission factor for electrified platforms depends on the marginal generation mix:

- **Norwegian grid** (hydropower dominated): 8–20 g CO$_2$/kWh
- **UK grid** (mixed, increasing renewables): 150–250 g CO$_2$/kWh
- **Gas-fired CCGT on shore**: 350–400 g CO$_2$/kWh

Even with gas-fired shore power, the higher efficiency of onshore CCGT (55–60%) compared to offshore simple cycle (30–40%) yields a net CO$_2$ reduction of 30–45%.

### Norwegian NCS Electrification Examples

Norway leads the world in offshore platform electrification:

**Johan Sverdrup** — The largest electrification project to date. Phase 1 (2019) receives 100 MW from shore via a 200 km DC cable. Phase 2 added another 100 MW. The platform has near-zero direct CO$_2$ emissions, saving approximately 460,000 tonnes CO$_2$/year. Onshore power is sourced from Norwegian hydroelectric generation.

**Troll** — Troll A was electrified from shore in 1996, making it one of the first fully electric platforms. Troll B and C subsequently received partial electrification. The Troll field's power-intensive gas compression is well-suited to electric drive with VFDs.

**Martin Linge** — Receives all power from shore via a single cable. The facility was designed from the start as an all-electric platform, with no gas turbines installed.

**Utsira High area** — A joint electrification project connecting multiple fields (Edvard Grieg, Ivar Aasen, Gina Krog) to a shared shore power hub, demonstrating area-wide electrification economics.

### Impact on Production Optimization

Electrification fundamentally changes the production optimization landscape:

1. **Power constraint relaxed** — Shore power typically provides more capacity than gas turbines
2. **Speed control standard** — VFDs become the default for all motor-driven equipment
3. **Fuel gas availability** — Gas previously burned as fuel is now available for export (3–7% production uplift)
4. **New constraint: cable capacity** — Subsea power cable rating becomes the limiting factor
5. **Reliability change** — Single-point-of-failure on cable vs. distributed generation

### NeqSim Modeling for Electrified Platforms

```python
# Electrified platform with VFD-driven compressors
from neqsim import jneqsim

Compressor = jneqsim.process.equipment.compressor.Compressor
ChartGen = jneqsim.process.equipment.compressor.CompressorChartGenerator

# Compressor with VFD — efficient partial-load operation
comp = Compressor("Export Compressor", gas_stream)
comp.setOutletPressure(150.0, "bara")
comp.setPolytropicEfficiency(0.82)
comp.setUsePolytropicCalc(True)

# Generate compressor performance chart for variable speed
chart_gen = ChartGen(comp)
chart_gen.setChartType("interpolate and extrapolate")
chart = chart_gen.generateCompressorChart("normal curves", 5)
comp.setCompressorChart(chart)
comp.getCompressorChart().setUseCompressorChart(True)

# VFD enables wide speed range operation
comp.setMaximumSpeed(11000.0)
comp.setMinimumSpeed(5500.0)

process.run()

# Compare power consumption: VFD at 70% flow vs full speed recycle
power_vfd = comp.getPower("kW")
print(f"Power at reduced speed (VFD): {power_vfd:.0f} kW")
```

## Waste Heat Recovery and Organic Rankine Cycle (ORC)

### Low-Grade Waste Heat Opportunity

Many processes in oil and gas facilities reject heat at temperatures too low for conventional steam Rankine cycles (below 300°C) but too high to simply waste. Sources include:
- Gas turbine exhaust downstream of an HRSG (150–200°C)
- Compressor intercooler and aftercooler duty
- Hot produced water
- Flare gas energy recovery

### Organic Rankine Cycle Principle

An Organic Rankine Cycle (ORC) uses a low-boiling-point organic working fluid instead of water, enabling power generation from heat sources at 80–300°C. Common working fluids include:

| Working Fluid | Boiling Point (°C) | Critical Temp (°C) | Heat Source Range |
|--------------|-------------------|--------------------|--------------------|
| R245fa | 15 | 154 | 80–150°C |
| Isopentane | 28 | 187 | 100–200°C |
| Toluene | 111 | 319 | 200–350°C |
| Cyclohexane | 81 | 281 | 150–300°C |
| R1233zd(E) | 19 | 166 | 80–160°C |

The ORC thermal efficiency is limited by the Carnot bound and working fluid properties:

$$
\eta_{ORC} = \frac{W_{net}}{Q_{in}} \approx 10\text{--}20\%
$$

While ORC efficiency is modest compared to steam cycles, it converts otherwise wasted heat into useful electricity. For a platform with multiple gas turbines, ORC can generate 1–5 MW of additional power, equivalent to 5–15% fuel gas savings.

### Working Fluid Selection

The choice of working fluid depends on the heat source temperature, safety requirements (offshore environments demand non-toxic, non-flammable fluids where possible), environmental impact (low GWP and ODP), and thermodynamic performance. The ideal working fluid has:
- Critical temperature matched to the heat source
- High latent heat of vaporization
- Low viscosity (good heat transfer, low pumping power)
- Dry or isentropic expansion characteristic (no wet expansion into two-phase region)

### ORC Applications in Oil and Gas

ORC systems are increasingly deployed for:
- Waste heat from gas turbine exhaust (after HRSG, low-temperature tail)
- Hot oil/gas cooling duty recovery
- Geothermal co-production heat
- Produced water heat recovery in high-water-cut fields

The economic viability depends on the heat source temperature, available duty, and the value of the recovered electricity (driven by fuel gas price and CO$_2$ tax). At Norwegian carbon prices, ORC payback periods of 3–7 years are typical for suitable waste heat sources.

## Heat Integration and Pinch Analysis

### Identifying Heat Recovery Opportunities

Oil and gas facilities have numerous hot streams (compressor discharge, turbine exhaust) and cold streams (crude oil heating, glycol regeneration) that can be integrated to reduce energy consumption. Pinch analysis identifies the minimum heating and cooling utility requirements:

$$
Q_{H,min} = \sum_{cold} \Delta H_{cold} - \sum_{hot} \Delta H_{hot,above\ pinch}
$$

$$
Q_{C,min} = \sum_{hot} \Delta H_{hot} - \sum_{cold} \Delta H_{cold,below\ pinch}
$$

### NeqSim Heat Integration

NeqSim provides the `PinchAnalysis` class for systematic heat integration:

```python
from neqsim import jneqsim

PinchAnalysis = jneqsim.process.equipment.heatexchanger.heatintegration.PinchAnalysis

# Define hot and cold streams
pinch = PinchAnalysis("Platform Heat Integration")

# Hot streams (need cooling)
pinch.addHotStream("Comp Discharge", 150.0, 40.0, 2000.0)
pinch.addHotStream("GT Exhaust", 500.0, 150.0, 8000.0)
pinch.addHotStream("Produced Water", 80.0, 40.0, 1500.0)

# Cold streams (need heating)
pinch.addColdStream("Crude Heating", 20.0, 60.0, 1500.0)
pinch.addColdStream("Glycol Regen", 100.0, 200.0, 3000.0)
pinch.addColdStream("Fuel Gas Heating", 10.0, 50.0, 500.0)

# Set minimum approach temperature
pinch.setMinApproachTemperature(10.0)

# Run analysis
pinch.run()

# Results
print(f"Pinch temperature: {pinch.getPinchTemperatureC():.1f} C")
print(f"Min heating utility: {pinch.getMinimumHeatingUtility():.0f} kW")
print(f"Min cooling utility: {pinch.getMinimumCoolingUtility():.0f} kW")
```

## Dynamic Power Management

### Power Management Optimization

Real-time power management optimizes the allocation of available generation capacity. The economic dispatch problem assigns load to multiple generators to minimize total fuel consumption while meeting total demand:

$$
\min \sum_g C_{fuel,g}(P_g) \quad \text{subject to} \quad \sum_g P_g = \sum_l P_l + P_{losses}
$$

Combined with production optimization, the overall problem becomes:

$$
\max \left[ Revenue(Q_{production}) - C_{fuel}(P_{generation}) - C_{carbon}(E_{CO_2}) \right]
$$

where the carbon cost term ($C_{carbon}$) has become increasingly significant under Norwegian and EU regulatory frameworks.

### Generator Loading Strategy

With multiple gas turbines of potentially different types and ages, the optimal loading strategy considers:
- **Equal loading** — Simplest approach, equalizes wear across units
- **Base-load/peaking** — Most efficient unit runs at full load, others modulate
- **Merit order** — Units dispatched in order of increasing heat rate (most efficient first)
- **Condition-based** — Loading reflects maintenance status and remaining time to overhaul

## Practical Design Considerations

### Offshore Platform Power System Layout

A typical North Sea platform power system consists of:

- **3–4 gas turbine generators** — 20–35 MW each (aeroderivative)
- **Main switchboard** — 11–13.8 kV, 50 Hz (60 Hz for some Gulf of Mexico installations)
- **VFD sections** — For variable-speed compressor and pump drives
- **Emergency diesel generator** — 1–3 MW for safety-critical loads
- **UPS systems** — For control and safety instrumentation

### Design Power Budget

The design power budget must account for:

1. **Steady-state process loads** — Normal operation, all consumers running
2. **Startup transients** — Motor starting currents (6–8× rated for direct-on-line start)
3. **Future expansion** — Typically 10–20% growth margin
4. **Degradation allowance** — Gas turbine power output degrades 2–5% between overhauls
5. **Ambient temperature margin** — Derate for maximum expected site temperature

### Key Design Standards

| Standard | Scope |
|----------|-------|
| IEC 61892 | Mobile and fixed offshore units — Electrical installations |
| NORSOK E-001 | Electrical systems (Norwegian Continental Shelf) |
| API RP 14F | Design and installation of electrical systems |
| IEEE 45 | Electric installations on shipboard |
| IEC 62271 | High-voltage switchgear and controlgear |
| ISO 3977 | Gas turbines — Procurement |
| IEEE 519 | Harmonic control in electrical power systems |
| IEC 61800 | Adjustable speed electrical power drive systems |

## Case Study: Power-Constrained Platform Optimization

### Problem Statement

An aging North Sea platform has the following power configuration:
- 3 × LM2500+ aeroderivative gas turbines, each rated 30 MW (ISO)
- Summer ambient temperature derate: 25 MW per unit at 25°C
- Normal operation: 2 running + 1 standby (N+1 redundancy)
- Available power: 50 MW (2 × 25 MW)

The facility power consumers include:
- Gas export compression: 32 MW (variable with flow)
- Water injection pumps: 8 MW (increasing with water cut)
- Oil export pumps: 3 MW
- Utilities: 5 MW (fixed)
- Total demand at design rate: 48 MW (96% of available)

As water cut increases from 40% to 60%, water injection power increases to 12 MW, pushing total demand to 52 MW—exceeding available capacity.

### NeqSim Optimization Approach

```python
from neqsim import jneqsim

ProcessSystem = jneqsim.process.processmodel.ProcessSystem
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.ThreePhaseSeparator
Compressor = jneqsim.process.equipment.compressor.Compressor
Pump = jneqsim.process.equipment.pump.Pump

# Create fluid (oil + gas + water)
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 80.0, 100.0)
fluid.addComponent("methane", 0.45)
fluid.addComponent("ethane", 0.05)
fluid.addComponent("propane", 0.03)
fluid.addComponent("n-butane", 0.02)
fluid.addComponent("n-hexane", 0.05)
fluid.addComponent("C7", 0.20)
fluid.addComponent("water", 0.20)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

# Build process
process = ProcessSystem()

feed = Stream("Well Feed", fluid)
feed.setFlowRate(200000.0, "kg/hr")
process.add(feed)

hp_sep = Separator("HP Separator", feed)
process.add(hp_sep)

# Gas compression — main power consumer
comp = Compressor("Gas Export Compressor", hp_sep.getGasOutStream())
comp.setOutletPressure(150.0, "bara")
comp.setMaximumPower(40000.0)  # 40 MW available for compression
process.add(comp)

# Water injection pump
wi_pump = Pump("Water Injection Pump", hp_sep.getWaterOutStream())
wi_pump.setOutletPressure(250.0, "bara")
process.add(wi_pump)

process.run()

# Report power balance
comp_power = comp.getPower("kW")
pump_power = wi_pump.getPower("kW")
total_power = comp_power + pump_power + 8000  # 8 MW fixed loads
available = 50000  # 50 MW available

print(f"Compression power: {comp_power/1000:.1f} MW")
print(f"WI pump power: {pump_power/1000:.1f} MW")
print(f"Total demand: {total_power/1000:.1f} MW")
print(f"Available: {available/1000:.1f} MW")
print(f"Power margin: {(available-total_power)/1000:.1f} MW")
```

### Optimization Results

The production optimizer identifies the maximum feed rate that keeps total facility power within the 50 MW limit. As water cut increases, the optimal production rate decreases because more power is consumed by water handling, leaving less for gas compression.

This analysis quantifies the economic impact of water cut increase and provides the basis for evaluating interventions:
- Install a 4th gas turbine (CAPEX vs. production gain)
- Electrify water injection pumps with shore power cable
- Implement gas lift to reduce wellhead pressure and compression power
- Upgrade to higher-efficiency compressor drivers (VFD-driven electric motors)
- Install ORC on gas turbine exhaust for additional 2–3 MW

### Power Demand vs. Production Profile

```python
import matplotlib.pyplot as plt

# Simulate power demand at varying production rates
production_rates = [100, 120, 140, 160, 180, 200, 220]  # MSm3/d gas
comp_power_mw = [12, 15.5, 19.5, 24, 29, 34.5, 41]     # MW
pump_power_mw = [6, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0]      # MW
total_power = [c + p + 5 for c, p in zip(comp_power_mw, pump_power_mw)]

fig, ax = plt.subplots(figsize=(10, 6))
ax.fill_between(production_rates, 0, comp_power_mw,
                alpha=0.3, label='Gas compression')
ax.fill_between(production_rates, comp_power_mw,
                [c + p for c, p in zip(comp_power_mw, pump_power_mw)],
                alpha=0.3, label='Water injection')
ax.fill_between(production_rates,
                [c + p for c, p in zip(comp_power_mw, pump_power_mw)],
                total_power, alpha=0.3, label='Utilities')
ax.axhline(y=50, color='r', linestyle='--', linewidth=2,
           label='Available power (50 MW)')
ax.set_xlabel('Gas Production Rate (MSm3/d)')
ax.set_ylabel('Power Demand (MW)')
ax.set_title('Power Demand vs. Production Rate')
ax.legend()
ax.grid(True)
plt.savefig('figures/power_demand_profile.png', dpi=150, bbox_inches='tight')
plt.show()
```

![Power demand breakdown as a function of gas production rate showing the 50 MW available power limit](figures/power_demand_profile.png)

## Summary

Power generation and energy management are integral to production optimization in oil and gas facilities. Key takeaways:

1. **Gas turbines** are the dominant prime movers offshore, with the Brayton cycle efficiency fundamentally limited by pressure ratio and turbine inlet temperature. Aeroderivative turbines (LM2500, LM6000, Trent 60) are preferred for their compact size, high efficiency, and modular maintenance.

2. **Ambient temperature** is a major performance variable—a 10°C increase reduces aeroderivative output by 5–8%, creating summer production bottlenecks. ISO correction methods must be applied when comparing turbine performance.

3. **Combined cycle** configurations with HRSG and steam turbine can increase thermal efficiency from 35–40% to 50–60%, with dual-pressure and triple-pressure HRSG designs maximizing heat recovery through optimal pinch point and approach temperature design.

4. **Electric motors with VFDs** provide dramatically better partial-load efficiency than gas turbine drives, following the affinity law $P \propto N^3$. A 10% speed reduction saves 27% power—significant savings for variable-demand applications.

5. **Fuel gas systems** require careful conditioning (heating, filtration, pressure regulation) to meet gas turbine quality requirements (Wobbe Index, superheat, contaminant limits). Fuel gas consumption is a direct deduction from saleable production.

6. **Platform electrification** from shore power (AC for short distances, HVDC for >80 km) eliminates 50–80% of direct CO$_2$ emissions and is economically driven by the combined Norwegian CO$_2$ tax and EU ETS carbon cost of ~900 NOK/tonne. Johan Sverdrup, Troll, and Martin Linge demonstrate proven electrification on the NCS.

7. **CO$_2$ emissions** must be tracked as Scope 1 (direct combustion) and Scope 2 (purchased electricity), with carbon intensity metrics (kg CO$_2$/boe) used for benchmarking and regulatory reporting.

8. **Power availability** is often the binding constraint on production, with gas compression dominating the demand profile. Power demand scales nonlinearly with production rate ($P \propto Q^{1.2-1.5}$ for compression).

9. **Power system reliability** requires N+1 redundancy, spinning reserve, and automatic load shedding. FMEA analysis identifies single points of failure, and modular gas turbine designs enable rapid recovery.

10. **Waste heat recovery** via ORC extends energy recovery from low-grade heat sources (150–300°C), adding 1–5 MW at modest cost where suitable heat sources exist.

11. **NeqSim provides** integrated modeling of gas turbines, HRSG, steam turbines, combined cycle, and production optimization through the `GasTurbine`, `SteamTurbine`, `HRSG`, `PinchAnalysis`, and `ProductionOptimizer` classes, enabling power-constrained facility optimization.

## Exercises

1. A platform has two LM6000 gas turbines rated at 43 MW each (ISO). Calculate the available power at 30°C ambient (sea level) using the ISO correction formula. Determine if two compressors at 25 MW each plus 10 MW of auxiliary loads can operate simultaneously with N+1 redundancy (one turbine on standby).

2. Using NeqSim, model a gas turbine and calculate the thermal efficiency at pressure ratios of 10, 15, 20, 25, and 30. Plot efficiency vs. pressure ratio and compare with the ideal Brayton cycle. Explain why the optimal pressure ratio for maximum net work differs from the optimal pressure ratio for maximum efficiency.

3. Design a combined cycle system for a gas processing plant using NeqSim. Compare single-pressure and dual-pressure HRSG configurations. Quantify the annual fuel gas savings, CO$_2$ reduction, and carbon cost avoidance under Norwegian NCS fiscal terms.

4. A centrifugal compressor driven by a 15 MW motor operates at 70% of design flow for 60% of the year. Compare annual energy costs for: (a) recycle control at fixed speed, (b) suction throttle control, (c) VFD speed control following the affinity laws. Assume electricity cost of 0.10 USD/kWh.

5. Model a power-constrained platform with increasing water cut (30%, 50%, 70%). Plot the maximum oil production rate vs. water cut showing the power-limited production envelope. Identify the water cut at which gas compression becomes power-limited.

6. Evaluate the economics of platform electrification: compare the NPV of continued gas turbine operation vs. installation of a 100 MW HVDC subsea power cable from shore, considering fuel gas savings, CO$_2$ tax (Norwegian rate: 600 NOK/tonne + EU ETS at 70 EUR/tonne), cable CAPEX, and reliability implications.

7. A gas turbine operating on fuel gas with 5% CO$_2$ content produces exhaust at 480°C. An HRSG with a 15°C pinch point and 10°C approach temperature generates steam at 40 bara. Calculate the steam production rate and the power output from a condensing steam turbine operating at 85% isentropic efficiency and exhausting at 0.08 bara.

## References

1. ISO 3977, "Gas turbines — Procurement," International Organization for Standardization.
2. IEC 61892, "Mobile and fixed offshore units — Electrical installations," International Electrotechnical Commission.
3. NORSOK E-001, "Electrical systems," Standards Norway.
4. API RP 14F, "Design and Installation of Electrical Systems for Fixed and Floating Offshore Petroleum Facilities," American Petroleum Institute.
5. Kehlhofer, R., et al., *Combined-Cycle Gas & Steam Turbine Power Plants*, 3rd ed., PennWell, 2009.
6. Walsh, P.P. and Fletcher, P., *Gas Turbine Performance*, 2nd ed., Blackwell Science, 2004.
7. Botros, K.K. and Campbell, J.M., "Fundamentals of Gas Turbine Metering and Performance," Pipeline Simulation Interest Group, 2008.
8. Norwegian Petroleum Directorate, "Guidelines for Power from Shore to the Norwegian Continental Shelf," 2020.
9. Saravanamuttoo, H.I.H., et al., *Gas Turbine Theory*, 7th ed., Pearson, 2017.
10. IEEE 519, "Standard for Harmonic Control in Electric Power Systems," Institute of Electrical and Electronics Engineers.
11. IEC 61800 series, "Adjustable speed electrical power drive systems," International Electrotechnical Commission.
12. Quoilin, S., et al., "Techno-economic survey of Organic Rankine Cycle (ORC) systems," *Renewable and Sustainable Energy Reviews*, 22, 168–186, 2013.
13. Norwegian Environment Agency, "Climate Cure 2030: Measures and Instruments for Achieving Norwegian Climate Goals," 2020.
14. Linnhoff, B. and Hindmarsh, E., "The pinch design method for heat exchanger networks," *Chemical Engineering Science*, 38(5), 745–763, 1983.
15. GE Gas Power, "LM2500 Aeroderivative Gas Turbine Data Sheet," General Electric, 2023.
16. Statnett, "Subsea Cable Technology for Offshore Electrification," Technical Report, 2021.


## Figures

![Figure 18.1: Co2 Emissions](figures/ch30_co2_emissions.png)

*Figure 18.1: Co2 Emissions*

![Figure 18.2: Fuel Consumption](figures/ch30_fuel_consumption.png)

*Figure 18.2: Fuel Consumption*

![Figure 18.3: Gt Ambient Temp](figures/ch30_gt_ambient_temp.png)

*Figure 18.3: Gt Ambient Temp*

![Figure 18.4: Power Demand Pie](figures/ch30_power_demand_pie.png)

*Figure 18.4: Power Demand Pie*
