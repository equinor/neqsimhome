
# Oil Processing and Stabilization

<!-- Chapter metadata -->
<!-- Notebooks: 01_multistage_separation_optimization.ipynb, 02_rvp_tvp_calculations.ipynb, 03_stabilizer_column.ipynb -->
<!-- Estimated pages: 22 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Design multi-stage separation trains and optimize separator pressure staging
2. Explain the principles of oil dewatering and desalting processes
3. Calculate Reid vapor pressure (RVP) and true vapor pressure (TVP) using NeqSim
4. Model crude oil stabilization using flash drums and stabilizer columns
5. Evaluate crude oil export quality specifications and blending strategies
6. Implement multi-stage separation optimization in NeqSim with ProcessSystem
7. Apply heat integration principles to oil processing facilities

## 11.1 Introduction to Oil Processing

The oil processing train on an offshore platform or onshore facility serves a critical function: transforming the raw well stream into a stabilized crude oil that meets export specifications. The well fluid arriving at the first-stage separator is a complex multiphase mixture of oil, gas, water, and sometimes sand. Through a series of carefully designed separation, heating, and stabilization steps, the oil phase is progressively conditioned to achieve the required vapor pressure, water content, and salt content for pipeline transport or tanker loading.

The design and optimization of the oil processing system has a direct impact on production revenue. Every mole of intermediate hydrocarbon (C$_3$–C$_6$) that remains in the oil phase rather than flashing to the gas phase increases oil production volume and revenue — provided the crude still meets vapor pressure specifications. Conversely, excessive light ends in the oil cause transportation hazards and quality penalties. The art of oil processing optimization lies in maximizing liquid recovery while meeting all quality constraints.

This chapter covers the complete oil processing chain from first-stage separation through export, with emphasis on the thermodynamic principles that govern each unit operation and their implementation in NeqSim.

![Schematic of a typical offshore oil processing train showing multi-stage separation, dewatering, and stabilization](figures/oil_processing_train_overview.png)

*Figure 11.1: Overview of a typical offshore oil processing train. Well fluid enters the HP separator and progresses through MP and LP separation stages, with gas routed to compression and oil to dewatering and stabilization before export.*

## 11.2 Multi-Stage Separation

### 11.2.1 Principles of Stage-Wise Separation

When a reservoir fluid is produced to surface conditions, the pressure reduction from reservoir pressure (typically 200–400 bara) to export/storage pressure (1–3 bara) causes dissolved gas to evolve from the oil. If this pressure reduction occurs in a single flash from well pressure to atmospheric, the resulting violent liberation of gas entrains significant quantities of intermediate and heavy hydrocarbons into the vapor phase, reducing the stock-tank oil recovery.

Multi-stage separation addresses this problem by performing the pressure reduction in discrete steps, each in a separate vessel. At each stage, the gas that evolves is removed and routed to compression, while the oil passes to the next lower-pressure stage. The fundamental thermodynamic principle is that a gradual, staged pressure reduction allows lighter components (C$_1$, C$_2$) to evolve preferentially while retaining more of the intermediate components (C$_3$–C$_6$) in the liquid phase.

The number of equilibrium stages and their operating pressures are the key design variables. In practice:

- **Two-stage separation** (HP + stock tank): Simple, low CAPEX, common for small fields
- **Three-stage separation** (HP + LP + stock tank): Most common offshore configuration
- **Four-stage separation** (HP + MP + LP + stock tank): Large facilities, heavy oils

The incremental oil recovery from adding stages follows a law of diminishing returns:

| Configuration | Typical Oil Recovery Increase vs. Single Flash |
|---------------|------------------------------------------------|
| 2-stage | 10–20% |
| 3-stage | 15–25% |
| 4-stage | 17–28% |
| 5-stage | 18–29% |

*Table 11.1: Typical incremental oil recovery from multi-stage separation compared to single-stage flash. Values depend strongly on fluid composition and conditions.*

### 11.2.2 Optimal Pressure Staging — Rule of Thumb

A widely used heuristic for selecting intermediate separator pressures is the **equal pressure ratio** rule. For an $n$-stage separation train with inlet pressure $P_1$ and final (stock-tank) pressure $P_n$, the optimal intermediate pressures follow a geometric progression:

$$r = \left(\frac{P_1}{P_n}\right)^{1/(n-1)}$$

where $r$ is the pressure ratio per stage, and the intermediate pressures are:

$$P_k = P_1 \cdot r^{-(k-1)}, \quad k = 1, 2, \ldots, n$$

For a typical 3-stage system with HP at 70 bara and stock tank at 1.01 bara:

$$r = \left(\frac{70}{1.01}\right)^{1/2} = \sqrt{69.3} \approx 8.32$$

This gives intermediate pressures of approximately 70, 8.4, and 1.01 bara.

While this rule provides an excellent starting point, the true optimal pressures depend on the fluid composition, temperature profile, and economic factors. Heavy oils with high GOR benefit from more moderate pressure ratios, while lean condensates may require different staging. Rigorous optimization using process simulation always improves upon the equal-ratio heuristic.

### 11.2.3 Rigorous Optimization of Separator Pressures

The objective function for separator pressure optimization is typically to maximize stock-tank oil production rate (in Sm$^3$/d or bbl/d) subject to constraints on:

- Vapor pressure of the export crude (RVP or TVP specification)
- Minimum separator pressure for gas compression suction
- Maximum separator temperature (metallurgy limits)
- Gas flaring or compression capacity limits

Mathematically, for an $n$-stage train:

$$\max_{P_2, P_3, \ldots, P_{n-1}} \quad Q_{\text{oil,ST}}(P_2, P_3, \ldots, P_{n-1})$$

subject to:

$$\text{RVP}(P_2, \ldots, P_{n-1}) \leq \text{RVP}_{\text{spec}}$$
$$P_k \geq P_{k,\text{min}}, \quad k = 2, \ldots, n-1$$

The optimization landscape is generally smooth and unimodal for liquid recovery, making gradient-based methods effective. However, the interaction with vapor pressure constraints can create binding constraints that shift the optimum.

### 11.2.4 Temperature Effects in Separation

Separator temperature significantly affects oil recovery. Higher temperatures reduce oil viscosity and promote better gas–liquid separation (especially water–oil separation in the first stage), but also increase the vapor pressure of the oil and can cause excessive vaporization of intermediate components.

The temperature at each stage is determined by:

1. **Joule–Thomson cooling**: Pressure reduction across chokes cools the fluid
2. **Heat addition**: Heating coils or heat exchangers upstream of separators
3. **Heat loss**: Ambient cooling in flowlines and vessels

The temperature drop across a choke valve for a two-phase mixture can be estimated from the isenthalpic flash. For a typical North Sea oil, the JT coefficient is approximately 3–5°C per 10 bar pressure drop.

## 11.3 Oil Dewatering and Desalting

### 11.3.1 Water-in-Oil Emulsions

Raw crude oil typically contains 5–30% produced water as a dispersed phase, forming a water-in-oil (W/O) emulsion stabilized by natural surfactants — asphaltenes, resins, naphthenic acids, and fine solid particles. The stability of these emulsions depends on:

- **Interfacial film strength**: Asphaltenes form rigid films around water droplets
- **Droplet size distribution**: Smaller droplets are more stable
- **Continuous phase viscosity**: Higher viscosity retards droplet coalescence
- **Temperature**: Higher temperature reduces viscosity and weakens interfacial films
- **Water cut**: Very low or very high water cuts are easier to treat than intermediate ranges (20–40%)

The target specification for export crude is typically less than 0.5% BS&W (basic sediment and water), with many contracts specifying less than 0.1%.

### 11.3.2 Gravity Separation

The primary mechanism for water removal is gravity settling, governed by Stokes' law for the terminal velocity of a spherical water droplet in the oil phase:

$$v_t = \frac{d^2 (\rho_w - \rho_o) g}{18 \mu_o}$$

where $d$ is the droplet diameter, $\rho_w$ and $\rho_o$ are the water and oil densities, $g$ is gravitational acceleration, and $\mu_o$ is the oil dynamic viscosity.

For typical North Sea crude at separator conditions:

| Parameter | Value |
|-----------|-------|
| Oil density | 800–850 kg/m$^3$ |
| Water density | 1020–1050 kg/m$^3$ |
| Oil viscosity | 2–10 mPa·s |
| Droplet diameter | 100–500 μm |
| Settling velocity | 0.5–15 mm/s |

*Table 11.2: Typical parameters for gravity separation of water from crude oil.*

The retention time required for adequate water separation is:

$$t_{\text{ret}} = \frac{h_{\text{oil}}}{v_t}$$

where $h_{\text{oil}}$ is the oil pad height in the separator. Typical retention times range from 3 to 15 minutes depending on oil properties and the required outlet water cut.

### 11.3.3 Electrostatic Coalescers

For final dewatering to meet export specifications, electrostatic coalescers are almost universally employed. These devices apply a high-voltage AC or DC electric field (typically 1–2 kV/cm) across the emulsion, which:

1. **Induces dipoles** in water droplets, causing attraction between adjacent droplets
2. **Deforms droplets**, stretching them toward neighboring drops
3. **Thins the interfacial film**, promoting coalescence
4. **Chain formation**: Droplets align in the field direction, creating chains that coalesce rapidly

The electrostatic force between two spherical droplets of radius $a$ separated by distance $d$ in a uniform field $E_0$ is:

$$F_e \propto \epsilon_o E_0^2 a^2 \left(\frac{a}{d}\right)^4$$

The strong dependence on both field strength and droplet proximity explains why electrostatic coalescers are most effective as a polishing step after bulk gravity separation has already removed the majority of the water.

### 11.3.4 Desalting

Crude oil contains dissolved salts (primarily NaCl, CaCl$_2$, and MgCl$_2$) in the residual water phase. These salts cause corrosion in downstream refinery equipment, particularly in crude distillation unit overhead systems where HCl is formed by hydrolysis:

$$\text{CaCl}_2 + \text{H}_2\text{O} \rightarrow \text{Ca(OH)}_2 + 2\text{HCl}$$

Export specifications typically require salt content below 10–50 PTB (pounds of salt per thousand barrels of oil). Desalting is accomplished by:

1. **Wash water injection**: Fresh water (3–7% by volume) is mixed with the crude
2. **Mixing**: A mixing valve creates a fine dispersion of wash water in oil
3. **Electrostatic coalescing**: The desalter separates the diluted brine from oil
4. **Brine rejection**: The water phase containing dissolved salts is routed to water treatment

The salt removal efficiency depends on the mixing intensity (quantified by the pressure drop across the mixing valve, typically 0.5–1.5 bar) and the number of stages. Two-stage desalting can achieve 95–99% salt removal.

## 11.4 Crude Oil Stabilization

### 11.4.1 Purpose of Stabilization

Crude oil leaving the last separation stage still contains dissolved light hydrocarbons (primarily C$_1$–C$_4$) and dissolved gases (CO$_2$, H$_2$S). If exported in this condition, the crude would:

- Exceed vapor pressure specifications for pipeline transport or tanker loading
- Create safety hazards due to gas evolution during storage and handling
- Produce uncontrolled emissions of volatile organic compounds (VOCs)
- Risk cargo tank overpressure during marine transport

Stabilization removes these light components to meet the required vapor pressure specification, typically expressed as Reid Vapor Pressure (RVP) or True Vapor Pressure (TVP).

### 11.4.2 Flash Stabilization

The simplest stabilization method is flash stabilization, where the oil is heated and flashed at reduced pressure. The increased temperature shifts the vapor–liquid equilibrium to favor gas evolution, removing light ends. A typical flash stabilization system consists of:

1. **Heat exchanger**: Oil is heated to 60–90°C using hot produced water or waste heat
2. **Flash drum**: Heated oil flashes at 1–3 bara
3. **Cooler**: Stabilized oil is cooled for export

Flash stabilization is simple and reliable but has limited flexibility — there is no way to control the sharpness of the separation between light components (which should leave) and intermediate components (which should stay). This means that achieving a low RVP requires either high temperature (expensive, may cause thermal degradation) or excessive loss of C$_4$–C$_5$ to the gas phase (lost revenue).

### 11.4.3 Stabilizer Column

A stabilizer column provides a much sharper separation between light and intermediate components. It operates as a distillation column with:

- **Reboiler**: Provides heat to strip light ends from the oil
- **Overhead condenser**: Partially condenses overhead vapor, returning reflux
- **Trays or packing**: 10–20 theoretical stages
- **Feed entry**: Typically at the middle of the column

The key advantage of a stabilizer column over flash stabilization is the ability to make a sharp cut between C$_3$ and C$_4$. The column overhead product is rich in C$_1$–C$_3$ (and H$_2$S, CO$_2$), while the bottoms product is a stabilized crude with controlled C$_4$+ content. This allows meeting the RVP specification with minimum loss of valuable intermediate components.

Design parameters for a typical stabilizer column:

| Parameter | Typical Range |
|-----------|---------------|
| Number of trays | 10–25 |
| Operating pressure | 5–15 bara |
| Feed temperature | 80–120°C |
| Reboiler temperature | 150–250°C |
| Reflux ratio | 0.5–2.0 |
| Overhead temperature | 40–70°C |

*Table 11.3: Typical design parameters for a crude oil stabilizer column.*

The reboiler duty is the largest energy consumer in the oil processing system and is a prime candidate for heat integration with other process streams.

### 11.4.4 Reboiler Considerations

The reboiler type and heat source significantly affect stabilizer performance and economics:

- **Fired heater**: Direct heating with fuel gas; high-temperature capability but safety concerns
- **Hot oil circuit**: Indirect heating using a closed-loop thermal oil system
- **Heat medium (glycol/water)**: Lower temperature applications
- **Waste heat recovery**: Utilizing gas turbine exhaust or compressor intercooler heat

The reboiler temperature determines the bottoms composition and hence the RVP. Higher reboiler temperatures produce a more stable crude but consume more energy and risk thermal cracking of heavy components if temperatures exceed approximately 340°C.

## 11.5 Vapor Pressure Specifications

### 11.5.1 Reid Vapor Pressure (RVP)

Reid Vapor Pressure is the vapor pressure of a liquid measured at 37.8°C (100°F) using the standardized test method ASTM D323 (or the automated version, ASTM D5191). The test uses a specific apparatus with a vapor-to-liquid volume ratio of 4:1, which means the measured RVP is not the true equilibrium vapor pressure but is slightly lower due to the vapor space dilution effect.

For an ideal multicomponent mixture, the RVP can be estimated from Raoult's law:

$$\text{RVP} \approx \sum_i x_i P_i^{\text{sat}}(37.8°C)$$

where $x_i$ is the liquid mole fraction and $P_i^{\text{sat}}$ is the pure component vapor pressure at 37.8°C.

However, this approximation ignores:
- Non-ideal mixing (activity coefficient effects)
- The vapor–liquid redistribution in the RVP apparatus (V/L = 4)
- Dissolved gases (which fully vaporize in the apparatus)

An accurate RVP calculation therefore requires a full flash calculation at the test conditions, accounting for the specific vapor-to-liquid ratio of the apparatus.

### 11.5.2 True Vapor Pressure (TVP)

True Vapor Pressure is the actual equilibrium vapor pressure of the liquid at its storage temperature, without the dilution effect of the RVP test apparatus. TVP is always higher than RVP and is the thermodynamically correct measure of volatility.

TVP is critical for:
- Tank breathing loss calculations
- Marine cargo tank design
- Environmental emission estimates
- Safety (flash point correlation)

The relationship between TVP and RVP depends on the oil composition but can be approximated as:

$$\text{TVP}(T) \approx \text{RVP} \times \exp\left[\frac{C_1}{T_{\text{RVP}}} - \frac{C_1}{T}\right]$$

where $C_1$ is a fluid-dependent constant and temperatures are in Kelvin.

### 11.5.3 Export Specifications

Crude oil export specifications vary by market and transportation mode:

| Specification | Pipeline | Tanker (ISGOTT) | Refinery Gate |
|---------------|----------|------------------|---------------|
| RVP (kPa) | < 65–100 | < 80–100 | < 82 |
| TVP at 50°C (kPa) | — | < 101.3 | — |
| BS&W (vol%) | < 0.5 | < 0.5 | < 0.1 |
| Salt (PTB) | < 50 | < 20 | < 10 |
| H$_2$S (ppm wt) | < 20 | < 50 | < 100 |
| Temp (°C) | < 60 | < 60 | Ambient |

*Table 11.4: Typical crude oil export specifications for different transportation modes.*

## 11.6 NeqSim Implementation

### 11.6.1 Multi-Stage Separation in NeqSim

NeqSim provides comprehensive support for modeling multi-stage separation through its `ProcessSystem` framework. Each separator stage is modeled as a `ThreePhaseSeparator` or `Separator` connected by streams, with gas outlet streams routed to compression and oil outlet streams routed to the next separation stage.

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define a typical North Sea crude oil
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 80.0, 70.0)
fluid.addComponent("nitrogen", 0.5)
fluid.addComponent("CO2", 2.1)
fluid.addComponent("methane", 35.0)
fluid.addComponent("ethane", 5.2)
fluid.addComponent("propane", 4.1)
fluid.addComponent("i-butane", 1.2)
fluid.addComponent("n-butane", 2.5)
fluid.addComponent("i-pentane", 1.3)
fluid.addComponent("n-pentane", 1.8)
fluid.addComponent("n-hexane", 3.5)
fluid.addComponent("n-heptane", 5.0)
fluid.addComponent("n-octane", 8.0)
fluid.addComponent("n-nonane", 6.5)
fluid.addComponent("nC10", 5.0)
fluid.addComponent("nC11", 18.3)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

# Create feed stream
feed = jneqsim.process.equipment.stream.Stream("Well Stream", fluid)
feed.setFlowRate(5000.0, "kg/hr")
feed.setTemperature(80.0, "C")
feed.setPressure(70.0, "bara")

# HP Separator (1st stage)
hp_sep = jneqsim.process.equipment.separator.ThreePhaseSeparator(
    "HP Separator", feed)

# Valve to MP
valve_hp_mp = jneqsim.process.equipment.valve.ThrottlingValve(
    "HP-MP Valve", hp_sep.getOilOutStream())
valve_hp_mp.setOutletPressure(15.0)

# MP Separator (2nd stage)
mp_sep = jneqsim.process.equipment.separator.ThreePhaseSeparator(
    "MP Separator", valve_hp_mp.getOutletStream())

# Valve to LP
valve_mp_lp = jneqsim.process.equipment.valve.ThrottlingValve(
    "MP-LP Valve", mp_sep.getOilOutStream())
valve_mp_lp.setOutletPressure(2.5)

# LP Separator (3rd stage)
lp_sep = jneqsim.process.equipment.separator.ThreePhaseSeparator(
    "LP Separator", valve_mp_lp.getOutletStream())

# Build and run process
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(hp_sep)
process.add(valve_hp_mp)
process.add(mp_sep)
process.add(valve_mp_lp)
process.add(lp_sep)
process.run()

# Report results
print("=== Multi-Stage Separation Results ===")
print(f"HP gas rate:  {hp_sep.getGasOutStream().getFlowRate('kg/hr'):.1f} kg/hr")
print(f"MP gas rate:  {mp_sep.getGasOutStream().getFlowRate('kg/hr'):.1f} kg/hr")
print(f"LP gas rate:  {lp_sep.getGasOutStream().getFlowRate('kg/hr'):.1f} kg/hr")
print(f"Oil out rate: {lp_sep.getOilOutStream().getFlowRate('kg/hr'):.1f} kg/hr")
print(f"Oil out temp: {lp_sep.getOilOutStream().getTemperature('C'):.1f} C")
```

### 11.6.2 Separator Pressure Optimization

The following example demonstrates a systematic optimization of separator pressures in a 3-stage separation train. The objective is to maximize stock-tank oil flow rate by varying the MP separator pressure:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import matplotlib.pyplot as plt

def run_three_stage_separation(fluid_template, mp_pressure):
    """Run 3-stage separation with given MP pressure, return oil rate."""
    fluid = fluid_template.clone()

    feed = jneqsim.process.equipment.stream.Stream("Feed", fluid)
    feed.setFlowRate(10000.0, "kg/hr")
    feed.setTemperature(80.0, "C")
    feed.setPressure(70.0, "bara")

    hp_sep = jneqsim.process.equipment.separator.Separator("HP Sep", feed)

    valve1 = jneqsim.process.equipment.valve.ThrottlingValve(
        "Valve 1", hp_sep.getLiquidOutStream())
    valve1.setOutletPressure(mp_pressure)

    mp_sep = jneqsim.process.equipment.separator.Separator(
        "MP Sep", valve1.getOutletStream())

    valve2 = jneqsim.process.equipment.valve.ThrottlingValve(
        "Valve 2", mp_sep.getLiquidOutStream())
    valve2.setOutletPressure(1.5)

    lp_sep = jneqsim.process.equipment.separator.Separator(
        "LP Sep", valve2.getOutletStream())

    process = jneqsim.process.processmodel.ProcessSystem()
    process.add(feed)
    process.add(hp_sep)
    process.add(valve1)
    process.add(mp_sep)
    process.add(valve2)
    process.add(lp_sep)
    process.run()

    return lp_sep.getLiquidOutStream().getFlowRate("kg/hr")

# Define fluid
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 80.0, 70.0)
fluid.addComponent("nitrogen", 0.3)
fluid.addComponent("CO2", 1.5)
fluid.addComponent("methane", 40.0)
fluid.addComponent("ethane", 6.0)
fluid.addComponent("propane", 4.0)
fluid.addComponent("i-butane", 1.5)
fluid.addComponent("n-butane", 2.5)
fluid.addComponent("i-pentane", 1.5)
fluid.addComponent("n-pentane", 2.0)
fluid.addComponent("n-hexane", 4.0)
fluid.addComponent("n-heptane", 6.0)
fluid.addComponent("n-octane", 8.0)
fluid.addComponent("nC10", 22.7)
fluid.setMixingRule("classic")

# Sweep MP pressure
mp_pressures = [3, 5, 7, 10, 12, 15, 18, 20, 25, 30, 35, 40]
oil_rates = []

for p in mp_pressures:
    rate = run_three_stage_separation(fluid, float(p))
    oil_rates.append(rate)
    print(f"MP = {p:5.1f} bara -> Oil rate = {rate:.1f} kg/hr")

# Plot optimization curve
plt.figure(figsize=(10, 6))
plt.plot(mp_pressures, oil_rates, 'bo-', linewidth=2, markersize=8)
plt.xlabel("MP Separator Pressure (bara)", fontsize=12)
plt.ylabel("Stock-Tank Oil Rate (kg/hr)", fontsize=12)
plt.title("3-Stage Separation Optimization", fontsize=14)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("figures/mp_pressure_optimization.png", dpi=150,
            bbox_inches="tight")
plt.show()
```

![Optimization curve showing stock-tank oil rate vs. MP separator pressure](figures/mp_pressure_optimization.png)

*Figure 11.2: Stock-tank oil recovery as a function of intermediate (MP) separator pressure for a 3-stage separation train. The optimum is typically found at 8–12 bara for this fluid composition.*

### 11.6.3 RVP and TVP Calculations

NeqSim can calculate both RVP and TVP through appropriate flash calculations. The RVP calculation requires mimicking the ASTM D323 test procedure by performing a flash at 37.8°C with a vapor-to-liquid volume ratio of 4:1:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

def calculate_tvp(oil_stream, temperature_C):
    """Calculate True Vapor Pressure at given temperature."""
    fluid = oil_stream.getFluid().clone()
    fluid.setTemperature(temperature_C + 273.15)

    ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid)
    ops.bubblePointPressureFlash(False)

    return fluid.getPressure("bara") * 100.0  # Convert to kPa

def calculate_rvp(oil_stream):
    """Estimate RVP using bubble point at 37.8 C (100 F).

    Note: A rigorous RVP requires a constrained V/L=4 flash,
    but the bubble point provides a good engineering estimate.
    """
    return calculate_tvp(oil_stream, 37.8)

# Example: Calculate RVP and TVP for stabilized crude
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 60.0, 2.0)
fluid.addComponent("methane", 0.1)
fluid.addComponent("ethane", 0.3)
fluid.addComponent("propane", 1.5)
fluid.addComponent("i-butane", 2.0)
fluid.addComponent("n-butane", 4.0)
fluid.addComponent("i-pentane", 3.5)
fluid.addComponent("n-pentane", 5.0)
fluid.addComponent("n-hexane", 10.0)
fluid.addComponent("n-heptane", 15.0)
fluid.addComponent("n-octane", 20.0)
fluid.addComponent("nC10", 38.6)
fluid.setMixingRule("classic")

stream = jneqsim.process.equipment.stream.Stream("Oil", fluid)
stream.setFlowRate(1000.0, "kg/hr")
stream.run()

rvp = calculate_rvp(stream)
tvp_50 = calculate_tvp(stream, 50.0)
tvp_60 = calculate_tvp(stream, 60.0)

print(f"RVP (at 37.8°C): {rvp:.1f} kPa")
print(f"TVP at 50°C:     {tvp_50:.1f} kPa")
print(f"TVP at 60°C:     {tvp_60:.1f} kPa")
```

### 11.6.4 Stabilizer Column Modeling

A crude oil stabilizer column can be modeled in NeqSim using the `DistillationColumn` class. The following example demonstrates a complete stabilizer with reboiler and condenser:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define unstabilized crude
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 90.0, 8.0)
fluid.addComponent("methane", 2.0)
fluid.addComponent("ethane", 1.5)
fluid.addComponent("propane", 3.0)
fluid.addComponent("i-butane", 2.0)
fluid.addComponent("n-butane", 4.0)
fluid.addComponent("i-pentane", 3.0)
fluid.addComponent("n-pentane", 4.5)
fluid.addComponent("n-hexane", 8.0)
fluid.addComponent("n-heptane", 12.0)
fluid.addComponent("n-octane", 18.0)
fluid.addComponent("nC10", 42.0)
fluid.setMixingRule("classic")

# Create feed stream
feed = jneqsim.process.equipment.stream.Stream("Stabilizer Feed", fluid)
feed.setFlowRate(5000.0, "kg/hr")
feed.setTemperature(90.0, "C")
feed.setPressure(8.0, "bara")

# Create stabilizer column
# Parameters: name, numberOfTrays, hasCondenser, hasReboiler
stabilizer = jneqsim.process.equipment.distillation.DistillationColumn(
    "Crude Stabilizer", 12, True, True)
stabilizer.addFeedStream(feed, 6)  # Feed at tray 6

# Set condenser and reboiler specifications
stabilizer.setCondenserTemperature(273.15 + 45.0)
stabilizer.getReboiler().setHeatInput(500000.0)  # W

# Build process
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(stabilizer)
process.run()

# Report results
overhead = stabilizer.getCondenser().getGasOutStream()
bottoms = stabilizer.getReboiler().getLiquidOutStream()

print("=== Stabilizer Results ===")
print(f"Overhead gas rate:  {overhead.getFlowRate('kg/hr'):.1f} kg/hr")
print(f"Overhead temp:      {overhead.getTemperature('C'):.1f} C")
print(f"Bottoms oil rate:   {bottoms.getFlowRate('kg/hr'):.1f} kg/hr")
print(f"Bottoms temp:       {bottoms.getTemperature('C'):.1f} C")
print(f"Reboiler duty:      {stabilizer.getReboiler().getDuty()/1e3:.1f} kW")
```

## 11.7 Oil Export Quality and Blending

### 11.7.1 Crude Oil Quality Parameters

Beyond vapor pressure and water content, crude oil quality is characterized by several parameters that affect its market value:

- **API gravity**: Measures the oil density relative to water. Light crudes (>35° API) command premium prices; heavy crudes (<25° API) are discounted.

$$\text{API} = \frac{141.5}{\text{SG}_{60°F}} - 131.5$$

- **Sulfur content**: Sweet crudes (<0.5 wt% S) trade at a premium over sour crudes (>1.5 wt% S)
- **TAN (Total Acid Number)**: High-TAN crudes (>0.5 mg KOH/g) cause naphthenic acid corrosion
- **Wax content**: Affects pour point and pumpability
- **Asphaltene content**: Affects stability and emulsion tendency

### 11.7.2 Blending Optimization

On multi-well platforms or in commingled pipelines, the export crude is a blend of production from several reservoirs with different properties. Blending optimization seeks to maximize the value of the commingled stream while meeting all quality constraints.

For simple blending of $n$ streams, the blend properties can be estimated using mixing rules:

**Volume-additive properties** (API gravity, density):

$$\rho_{\text{blend}} = \sum_i f_i \rho_i$$

where $f_i$ is the volume fraction of stream $i$.

**Non-linear properties** (RVP):

$$\text{RVP}_{\text{blend}}^{1.25} = \sum_i x_i \text{RVP}_i^{1.25}$$

This is the Chevron blending index correlation, which provides a reasonable approximation for RVP blending. For rigorous calculations, the entire blend must be flashed in NeqSim.

## 11.8 Heat Integration in Oil Processing

### 11.8.1 Energy Consumers and Sources

The oil processing system contains both heat sources and heat sinks that can be integrated to reduce overall energy consumption:

**Heat sources (hot streams):**
- Compressed gas after compressor stages (120–180°C)
- Stabilizer overhead vapor (40–70°C)
- Produced water (60–90°C)
- Gas turbine exhaust (450–550°C)

**Heat sinks (cold streams):**
- Crude oil heating before stabilizer (ambient to 90°C)
- Reboiler duty for stabilizer column (150–250°C)
- Gas dehydration reboiler (180–204°C)

### 11.8.2 Pinch Analysis

Heat integration between these streams follows the principles of pinch analysis. The minimum approach temperature ($\Delta T_{\text{min}}$) is typically 10–20°C for liquid–liquid exchangers and 20–30°C for gas–liquid exchangers in oil processing applications.

The composite curves for a typical offshore facility show a pinch temperature around 80–100°C, with significant opportunity for recovery above the pinch (using compressed gas heat to preheat crude) and below the pinch (using produced water to preheat dehydration feed).

## 11.9 Oil Metering

### 11.9.1 Fiscal Metering Requirements

Accurate oil metering is essential for fiscal allocation and custody transfer. The typical offshore fiscal metering system includes:

1. **Prover loop**: Calibrates the flow meter using a known-volume piston or ball prover
2. **Turbine or ultrasonic meter**: Measures volumetric flow rate
3. **Densitometer**: Measures oil density for mass calculation
4. **Sampling system**: Continuous or grab samples for water cut, composition analysis
5. **Temperature and pressure transmitters**: For standard volume correction

The oil flow rate at standard conditions is calculated from:

$$Q_{\text{std}} = Q_{\text{actual}} \times \text{CTL} \times \text{CPL}$$

where CTL is the correction for temperature (thermal expansion) and CPL is the correction for pressure (compressibility). These factors are calculated per API MPMS Chapter 11.1.

### 11.9.2 Allocation Metering

Multi-well platforms require allocation metering to distribute total export revenue among individual wells or reservoirs. Allocation systems typically use:

- **Test separators**: Periodic well testing through a dedicated test separator
- **Multiphase flow meters**: Continuous monitoring of individual well production
- **Virtual metering**: Process simulation–based estimates using well models

NeqSim can support virtual metering by modeling the relationship between wellhead conditions and separator outlet rates for each well.

## 11.10 Worked Example: Complete Oil Processing Optimization

This comprehensive example brings together all the concepts in this chapter to optimize a complete oil processing system for a North Sea field.

**Problem statement**: A platform processes 15,000 Sm$^3$/d of crude oil from a reservoir at 250 bara and 95°C. The well stream GOR is 120 Sm$^3$/Sm$^3$ and water cut is 25%. Design and optimize a 3-stage separation train to maximize oil recovery while meeting an RVP specification of 82 kPa.

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Step 1: Define the reservoir fluid
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 95.0, 250.0)
fluid.addComponent("nitrogen", 0.45)
fluid.addComponent("CO2", 1.87)
fluid.addComponent("methane", 36.52)
fluid.addComponent("ethane", 6.78)
fluid.addComponent("propane", 4.35)
fluid.addComponent("i-butane", 1.28)
fluid.addComponent("n-butane", 2.65)
fluid.addComponent("i-pentane", 1.22)
fluid.addComponent("n-pentane", 1.58)
fluid.addComponent("n-hexane", 3.45)
fluid.addComponent("n-heptane", 5.22)
fluid.addComponent("n-octane", 7.85)
fluid.addComponent("n-nonane", 5.66)
fluid.addComponent("nC10", 21.12)
fluid.addComponent("water", 15.0)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

# Step 2: Build the separation train
feed = jneqsim.process.equipment.stream.Stream("Well Stream", fluid)
feed.setFlowRate(50000.0, "kg/hr")
feed.setTemperature(85.0, "C")
feed.setPressure(65.0, "bara")

# HP Separator
hp_sep = jneqsim.process.equipment.separator.ThreePhaseSeparator(
    "HP Separator", feed)

# HP to MP valve
valve1 = jneqsim.process.equipment.valve.ThrottlingValve(
    "HP-MP Valve", hp_sep.getOilOutStream())
valve1.setOutletPressure(10.0)

# MP Separator
mp_sep = jneqsim.process.equipment.separator.ThreePhaseSeparator(
    "MP Separator", valve1.getOutletStream())

# MP to LP valve
valve2 = jneqsim.process.equipment.valve.ThrottlingValve(
    "MP-LP Valve", mp_sep.getOilOutStream())
valve2.setOutletPressure(2.0)

# LP Separator
lp_sep = jneqsim.process.equipment.separator.ThreePhaseSeparator(
    "LP Separator", valve2.getOutletStream())

# Step 3: Assemble process system
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(hp_sep)
process.add(valve1)
process.add(mp_sep)
process.add(valve2)
process.add(lp_sep)
process.run()

# Step 4: Report results
print("=" * 60)
print("MULTI-STAGE SEPARATION RESULTS")
print("=" * 60)
print(f"\nHP Separator (P = {hp_sep.getPressure():.1f} bara):")
print(f"  Gas rate:   {hp_sep.getGasOutStream().getFlowRate('kg/hr'):.0f} kg/hr")
print(f"  Oil rate:   {hp_sep.getOilOutStream().getFlowRate('kg/hr'):.0f} kg/hr")
print(f"  Water rate: {hp_sep.getWaterOutStream().getFlowRate('kg/hr'):.0f} kg/hr")

print(f"\nMP Separator (P = {mp_sep.getPressure():.1f} bara):")
print(f"  Gas rate:   {mp_sep.getGasOutStream().getFlowRate('kg/hr'):.0f} kg/hr")
print(f"  Oil rate:   {mp_sep.getOilOutStream().getFlowRate('kg/hr'):.0f} kg/hr")

print(f"\nLP Separator (P = {lp_sep.getPressure():.1f} bara):")
print(f"  Gas rate:   {lp_sep.getGasOutStream().getFlowRate('kg/hr'):.0f} kg/hr")
print(f"  Oil rate:   {lp_sep.getOilOutStream().getFlowRate('kg/hr'):.0f} kg/hr")

oil_out = lp_sep.getOilOutStream()
print(f"\nExport Oil Properties:")
print(f"  Temperature: {oil_out.getTemperature('C'):.1f} C")
print(f"  Flow rate:   {oil_out.getFlowRate('kg/hr'):.0f} kg/hr")
```

## 11.11 Summary

This chapter has covered the complete oil processing chain from multi-stage separation through crude oil stabilization and export. The key takeaways are:

1. **Multi-stage separation** dramatically increases oil recovery compared to single-stage flash. The equal pressure ratio rule provides an excellent starting point, but rigorous optimization using NeqSim can improve recovery by 1–3%.

2. **Dewatering and desalting** are essential for meeting export specifications. Electrostatic coalescers are the standard technology for final polishing, while wash water injection achieves salt removal.

3. **Crude stabilization** using a stabilizer column provides a sharper separation between light ends and valuable intermediates compared to simple flash drums, reducing losses and improving product value.

4. **Vapor pressure calculations** (RVP and TVP) in NeqSim use bubble point flash calculations and can accurately predict whether export specifications are met.

5. **Heat integration** between the gas compression, stabilizer, and oil heating systems can significantly reduce the overall energy consumption of the facility.

6. **NeqSim's ProcessSystem** framework allows complete oil processing trains to be modeled, optimized, and analyzed in an integrated simulation environment.

## Exercises

**Exercise 11.1**: For a fluid with the following composition (mole%): C$_1$ 45, C$_2$ 7, C$_3$ 5, iC$_4$ 1.5, nC$_4$ 3, iC$_5$ 2, nC$_5$ 2.5, C$_6$ 4, C$_7$+ 30 — compare the stock-tank oil recovery for 2-stage, 3-stage, and 4-stage separation with HP pressure of 80 bara and stock-tank pressure of 1.01 bara. Use the equal pressure ratio method to set intermediate pressures.

**Exercise 11.2**: For the 3-stage separation train in Exercise 11.1, optimize the intermediate separator pressures to maximize stock-tank oil recovery. Plot oil recovery vs. intermediate pressure(s) and identify the optimum.

**Exercise 11.3**: Calculate the RVP and TVP at 50°C for the stabilized crude from Exercise 11.2. Determine if the crude meets an RVP specification of 82 kPa. If not, propose and model a stabilization scheme using NeqSim.

**Exercise 11.4**: A platform produces two crudes with the following properties: Crude A (32° API, RVP = 55 kPa, 8000 Sm$^3$/d) and Crude B (25° API, RVP = 35 kPa, 5000 Sm$^3$/d). Calculate the blended export crude API gravity and estimate the blended RVP.

**Exercise 11.5**: Design a crude oil stabilizer column with 15 theoretical stages for the LP separator oil from the worked example. The target RVP is 65 kPa. Determine the required reboiler duty and the overhead gas composition.

**Exercise 11.6**: Develop a heat integration scheme for the oil processing facility in the worked example. Identify heat sources and sinks, construct composite curves, and calculate the potential energy savings.

## References

1. Arnold, K. and Stewart, M. (2008). *Surface Production Operations, Vol. 1: Design of Oil Handling Systems and Facilities*, 3rd ed. Gulf Professional Publishing.
2. Manning, F.S. and Thompson, R.E. (1991). *Oilfield Processing, Vol. 2: Crude Oil*. PennWell Books.
3. Abdel-Aal, H.K., Aggour, M.A., and Fahim, M.A. (2003). *Petroleum and Gas Field Processing*. CRC Press.
4. Campbell, J.M. (2014). *Gas Conditioning and Processing, Vol. 2: The Equipment Modules*, 9th ed. Campbell Petroleum Series.
5. ASTM D323 (2020). Standard Test Method for Vapor Pressure of Petroleum Products (Reid Method).
6. API MPMS Chapter 11.1 (2004). Temperature and Pressure Volume Correction Factors for Generalized Crude Oils, Refined Products, and Lubricating Oils.
7. ISGOTT (2006). *International Safety Guide for Oil Tankers and Terminals*, 5th ed. Witherby Seamanship.
8. Lyons, W.C. and Plisga, G.J. (2005). *Standard Handbook of Petroleum and Natural Gas Engineering*, 2nd ed. Gulf Professional Publishing.
9. Devold, H. (2013). *Oil and Gas Production Handbook: An Introduction to Oil and Gas Production, Transport, Refining and Petrochemical Industry*, 3rd ed. ABB Oil and Gas.
10. Solbraa, E. (2002). Measurement and modelling of absorption of carbon dioxide into methyldiethanolamine solutions at high pressures. PhD thesis, Norwegian University of Science and Technology.


## Figures

![Figure 11.1: Fig10 1 Rvp Vs Temperature](figures/fig10_1_rvp_vs_temperature.png)

*Figure 11.1: Fig10 1 Rvp Vs Temperature*

![Figure 11.2: Fig10 2 Api Vs Pressure](figures/fig10_2_api_vs_pressure.png)

*Figure 11.2: Fig10 2 Api Vs Pressure*

![Figure 11.3: Fig10 3 Multistage Oil Quality](figures/fig10_3_multistage_oil_quality.png)

*Figure 11.3: Fig10 3 Multistage Oil Quality*

![Figure 11.4: Fig10 4 Gas Shrinkage](figures/fig10_4_gas_shrinkage.png)

*Figure 11.4: Fig10 4 Gas Shrinkage*
