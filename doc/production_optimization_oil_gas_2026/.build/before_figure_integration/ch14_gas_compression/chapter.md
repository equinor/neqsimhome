# Gas Compression Systems

**Running the examples.** Start the source-workspace Python session described in Chapter 1, then run this chapter's Python blocks in reading order. Java blocks form a separate sequence using the same NeqSim build; carry forward objects from preceding Java blocks. The release execution records are in `verification/`; a successful run establishes API compatibility, while physical validation also requires the checks discussed in the text.

<!-- Chapter metadata -->
<!-- Notebooks: 01_single_stage_compression.ipynb, 02_multistage_compression.ipynb, 03_compression_power_analysis.ipynb, 04_recompression_train.ipynb -->
<!-- Estimated pages: 30 -->


### Compressor maps, drivers and energy availability

![Conceptual AI-generated illustration of a compression train with gas compression, cooling and driver equipment. It introduces process and shaft-load connections; geometry and displayed equipment do not represent an OEM map or mechanical design.](figures/compression_train_2026.png)

A compressor's required pressure rise and its driver's available shaft power
are separate constraints. Current NeqSim models support generated teaching maps,
explicit vendor-map data, speed limits, power limits and capacity reporting.
`GasTurbineUnit` adds package performance, ambient derating, fuel consumption,
emissions and overload reporting; attaching a calculated compressor load makes
the demand follow the process. Catalog entries are screening data, so a design
decision must carry its vendor revision and guarantee conditions.\cite{neqsim2026update}

Keep chart conventions explicit: actual inlet volume flow, head unit and
efficiency unit. In the illustrated `addCurve` interface, efficiency arrays are
in percent; compressor efficiency setters use fractions. Generated maps must
be labeled synthetic and must not be used as measured surge data. For an
off-design comparison, hold the installed map and driver rating fixed, rerun
the process and inspect the active capacity constraint. A successful flash or
an optimizer return alone does not establish surge margin or a feasible speed.

The energy-network implementation extends a scalar power budget: typed ports
can connect electrical supply, a motor, a mechanical shaft and a compressor.
Allocation reports distinguish requested, served and unmet demand. This makes
power shortage visible in production optimization instead of allowing every
consumer to assume the full plant rating simultaneously.


## Learning Objectives

After reading this chapter, the reader will be able to:

1. Explain why gas compression is critical for production optimization
2. Derive and apply the thermodynamic equations for isentropic and polytropic compression
3. Calculate compressor power, discharge temperature, and efficiency for real gases
4. Design multi-stage compression systems with intercooling
5. Select appropriate compression ratio and number of stages
6. Model compression systems in NeqSim using the Compressor class
7. Evaluate different compressor types and driver options for specific applications
8. Design complete compression system packages including scrubbers, coolers, and anti-surge

## 14.1 The Role of Compression in Production

Gas compression is one of the most energy-intensive and capital-intensive operations in oil and gas production. Compressors are found throughout the production system, serving multiple critical functions:

### 14.1.1 Compression Applications

**Recompression (gas gathering)**:
Low-pressure gas from separator stages (2–15 bara) must be compressed to pipeline or export pressure (70–200 bara). This is often the largest power consumer on a platform, requiring multi-stage compression with intercooling. As reservoir pressure declines, more compression stages may be needed, and compressor modifications or additions become a critical production optimization lever.

**Export compression**:
Gas must be compressed to the export pipeline pressure, which may be 100–200 bara for long-distance subsea pipelines. Export compressors handle the full gas production rate and operate at high suction pressures (typically 40–80 bara from the HP separator).

**Gas lift compression**:
Gas is compressed and injected into the production tubing to reduce the flowing gradient and maintain well flow rates. Gas lift pressures are typically 100–200 bara, and the gas lift rate per well is 50,000–200,000 Sm$^3$/day.

**Gas injection (pressure maintenance)**:
Produced gas is reinjected into the reservoir to maintain reservoir pressure and improve oil recovery. Injection pressures can be very high (200–500 bara), often requiring 3–4 compression stages.

**Booster compression**:
As reservoir pressure declines, wellhead pressure drops below the minimum required for the process. Wellhead or subsea boosting compressors increase the wellhead pressure to maintain production rates. This is a growing application, particularly for subsea compression.

**Flare gas recovery**:
Low-pressure gas that would otherwise be flared is compressed for use as fuel or for export. These compressors handle variable-composition gas at very low suction pressures (0.5–2 bara).

### 14.1.2 Compression and Production Rate

The relationship between compression and production rate is fundamental. As reservoir pressure declines, the available pressure at the topside facility decreases. Without compression upgrades, the production rate declines because:

1. Wellhead flowing pressure decreases, reducing the pressure differential driving flow
2. Separator pressure cannot be reduced below the compressor suction pressure
3. The GOR typically increases as reservoir pressure falls below the bubble point

Adding compression capacity — either by installing new compressors, upgrading existing machines, or adding stages — directly increases the production plateau duration and total recovery. The value of compression is measured in barrels of additional oil recovered and cubic meters of additional gas delivered.

## 14.2 Compressor Types

### 14.2.1 Centrifugal Compressors

Centrifugal compressors are the workhorse of the oil and gas industry for medium to high flow rates. They convert kinetic energy (velocity) to pressure energy (static pressure) through an impeller and diffuser arrangement.

**Operating principle**: Gas enters the impeller eye axially, is accelerated by the rotating impeller blades to high velocity, and then decelerates in the stationary diffuser, converting kinetic energy to pressure. Multiple impellers (stages) can be arranged in series on a single shaft to achieve higher pressure ratios.

**Characteristics**:
- Flow range: 500–300,000 m$^3$/hr (actual)
- Pressure ratio per stage: 1.2–1.8 (per impeller)
- Overall pressure ratio: up to 10:1 per casing (multi-stage)
- Speed: 3,000–15,000 rpm (higher for small machines)
- Efficiency: 75–88% polytropic
- Continuous, oil-free compression
- Smooth, non-pulsating flow

**Advantages**: High reliability, low maintenance, compact for high flow rates, suitable for variable speed operation, oil-free gas path.

**Limitations**: Susceptible to surge at low flow; stonewall (choke) at high flow; performance sensitive to gas molecular weight and temperature.

### 14.2.2 Axial Compressors

Axial compressors pass gas along the shaft axis through alternating rows of rotating blades (rotors) and stationary vanes (stators). Each rotor-stator pair constitutes one stage.

**Characteristics**:
- Very high flow rates: > 100,000 m$^3$/hr
- Pressure ratio per stage: 1.05–1.3
- Total pressure ratio: 4–12 (10–20 stages)
- Very high efficiency: 85–92% polytropic
- Used primarily as gas turbine compressor sections

Axial compressors are rarely used as standalone process compressors in oil and gas due to their limited pressure ratio per stage, but they dominate in gas turbine applications.

### 14.2.3 Reciprocating Compressors

Reciprocating compressors use pistons in cylinders to compress gas by volume reduction. They are positive-displacement machines.

**Characteristics**:
- Flow range: 10–10,000 m$^3$/hr (actual)
- Pressure ratio per stage: up to 4:1
- Very high discharge pressures achievable: > 700 bara
- Efficiency: 80–95% mechanical
- Pulsating flow (requires dampeners)

**Advantages**: High pressure ratio per stage, handles varying composition well, efficient at high pressure ratios, good for low flow rates.

**Limitations**: Pulsating flow, higher maintenance (valves, piston rings), larger footprint and weight for equivalent flow, not suitable for very high flow rates.

### 14.2.4 Screw Compressors

Screw compressors use two intermeshing helical rotors to trap and compress gas. They are positive-displacement machines with continuous (non-pulsating) flow.

**Characteristics**:
- Flow range: 100–40,000 m$^3$/hr
- Pressure ratio: up to 5:1 per stage
- Speed: 3,000–6,000 rpm
- Oil-injected or dry (oil-free) variants
- Suitable for wet or dirty gas

**Applications in oil and gas**: Flare gas recovery, low-pressure booster service, wet gas compression (liquid-tolerant designs).

### 14.2.5 Selection Guidelines

| Parameter | Centrifugal | Reciprocating | Screw |
|-----------|------------|---------------|-------|
| Flow (m$^3$/hr) | 500–300,000 | 10–10,000 | 100–40,000 |
| Pressure (bara) | < 350 | < 700 | < 40 |
| PR per stage | 1.2–1.8 | 2–4 | 2–5 |
| Efficiency | 75–88% | 80–95% | 70–85% |
| Reliability | Very high | Moderate | High |
| Maintenance | Low | High | Moderate |
| Weight/size | Moderate | Large | Compact |
| Offshore use | Primary | Limited | Growing |

*Table 14.1: Comparison of compressor types for oil and gas applications.*

## 14.3 Compressor Thermodynamics

### 14.3.1 Ideal (Isentropic) Compression

The minimum work required to compress gas from state 1 to state 2 is the isentropic (reversible, adiabatic) work. For an ideal gas with constant specific heat ratio $\gamma = C_p/C_v$, the isentropic compression follows:

$$\frac{T_{2s}}{T_1} = \left(\frac{P_2}{P_1}\right)^{(\gamma-1)/\gamma}$$

The specific isentropic work (per unit mass) is:

$$w_s = h_{2s} - h_1 = C_p T_1 \left[\left(\frac{P_2}{P_1}\right)^{(\gamma-1)/\gamma} - 1\right]$$

The isentropic head (energy per unit mass, expressed in meters of fluid column or kJ/kg) is:

$$H_s = \frac{\gamma}{\gamma - 1} \frac{Z_1 R T_1}{MW} \left[\left(\frac{P_2}{P_1}\right)^{(\gamma-1)/\gamma} - 1\right]$$

where $Z_1$ is the compressibility factor at suction, $R = 8.314$ J/(mol·K), $T_1$ is suction temperature (K), and $MW$ is the gas molecular weight (kg/kmol).

### 14.3.2 Isentropic Efficiency

Real compressors are irreversible — friction, turbulence, and other losses cause the actual discharge temperature and enthalpy to exceed the isentropic values. The isentropic efficiency quantifies this:

$$\eta_s = \frac{h_{2s} - h_1}{h_2 - h_1} = \frac{\text{Isentropic work}}{\text{Actual work}}$$

Typical isentropic efficiencies for centrifugal compressors range from 72–85%, depending on the design, operating point, and gas properties.

The actual discharge temperature is:

$$T_2 = T_1 + \frac{T_1}{\eta_s}\left[\left(\frac{P_2}{P_1}\right)^{(\gamma-1)/\gamma} - 1\right]$$

### 14.3.3 Polytropic Compression

For centrifugal compressors, the polytropic analysis is preferred over isentropic because:

1. **Polytropic efficiency is nearly constant** across different pressure ratios for the same machine, while isentropic efficiency varies
2. **Polytropic paths are additive** — the total polytropic head of multiple stages equals the sum of individual stage heads
3. **Polytropic analysis** allows direct comparison between different machines and stages

The polytropic process follows:

$$Pv^n = \text{constant}$$

where $n$ is the polytropic exponent, related to the polytropic efficiency by:

$$\frac{n-1}{n} = \frac{1}{\eta_p} \cdot \frac{\gamma - 1}{\gamma}$$

or equivalently:

$$\frac{n}{n-1} = \frac{\gamma}{\gamma-1} \cdot \eta_p$$

The polytropic head is:

$$H_p = \frac{n}{n - 1} \frac{Z_{\text{avg}} R T_1}{MW} \left[\left(\frac{P_2}{P_1}\right)^{(n-1)/n} - 1\right]$$

where $Z_{\text{avg}} = (Z_1 + Z_2)/2$ is the average compressibility factor.

The polytropic discharge temperature is:

$$T_2 = T_1 \left(\frac{P_2}{P_1}\right)^{(n-1)/n}$$

### 14.3.4 Schultz Correction

For real gases at high pressures, the ideal gas relations for polytropic analysis require correction. The Schultz method provides correction factors $f$ and $X$ and $Y$ that account for real gas behavior:

The polytropic head with Schultz correction is:

$$H_p = \frac{Z_1 R T_1}{MW} \cdot \frac{f}{\eta_p} \cdot \frac{\gamma_s}{\gamma_s - 1} \left[\left(\frac{P_2}{P_1}\right)^{(n-1)/n} - 1\right]$$

where:

$$X = \frac{T}{v}\left(\frac{\partial v}{\partial T}\right)_P - 1$$

$$Y = \frac{-P}{v}\left(\frac{\partial v}{\partial P}\right)_T$$

$$f = \frac{Y}{X + 1}$$

The correction factor $f$ accounts for the deviation of the real gas from ideal behavior along the polytropic path. For natural gas at moderate pressures (< 100 bara), $f$ is close to 1.0. At higher pressures or near the critical point, $f$ can deviate significantly and must be evaluated from the equation of state.

### 14.3.5 Relationship Between Isentropic and Polytropic Efficiency

The two efficiency definitions are related but not equal:

$$\eta_s = \frac{r^{(\gamma-1)/\gamma} - 1}{r^{(\gamma-1)/(\gamma \eta_p)} - 1}$$

where $r = P_2/P_1$ is the pressure ratio. Key observations:

- $\eta_p > \eta_s$ for compression (the polytropic efficiency always exceeds the isentropic for compression)
- The difference increases with pressure ratio
- At low pressure ratios ($r < 1.5$), $\eta_p \approx \eta_s$
- For typical centrifugal compressors: $\eta_p = 75$–$85\%$ corresponds to $\eta_s = 72$–$82\%$

| Pressure Ratio | $\eta_p$ (%) | $\eta_s$ (%) | Difference |
|----------------|-------------|-------------|------------|
| 1.5 | 80.0 | 79.2 | 0.8% |
| 2.0 | 80.0 | 78.0 | 2.0% |
| 3.0 | 80.0 | 75.5 | 4.5% |
| 4.0 | 80.0 | 73.2 | 6.8% |
| 5.0 | 80.0 | 71.2 | 8.8% |

*Table 14.2: Comparison of polytropic and isentropic efficiency for $\gamma = 1.3$ at different pressure ratios. Polytropic efficiency is constant; isentropic efficiency decreases with pressure ratio.*

## 14.4 Compressor Power Calculation

### 14.4.1 Gas Power

The gas power (also called gas horsepower or absorbed power) is the power transferred from the compressor to the gas:

$$\dot{W}_{\text{gas}} = \dot{m} \cdot H_p = \dot{m} \cdot \frac{n}{n-1} \cdot \frac{Z_{\text{avg}} R T_1}{MW} \left[\left(\frac{P_2}{P_1}\right)^{(n-1)/n} - 1\right]$$

where $\dot{m}$ is the mass flow rate (kg/s).

Alternatively, using the isentropic approach:

$$\dot{W}_{\text{gas}} = \frac{\dot{m}}{\eta_s} (h_{2s} - h_1)$$

For real gas calculations with NeqSim, the enthalpy difference $(h_2 - h_1)$ is obtained directly from the equation of state, providing more accurate results than the ideal gas approximation.

### 14.4.2 Shaft Power and Driver Power

The shaft power accounts for mechanical losses (bearings, seals):

$$\dot{W}_{\text{shaft}} = \frac{\dot{W}_{\text{gas}}}{\eta_{\text{mech}}}$$

where $\eta_{\text{mech}} \approx 0.97$–$0.99$ for centrifugal compressors.

The driver power (total power from the motor or gas turbine) includes additional losses:

$$\dot{W}_{\text{driver}} = \frac{\dot{W}_{\text{shaft}}}{\eta_{\text{driver}}} + W_{\text{auxiliaries}}$$

Typical driver efficiencies:
- Gas turbine: 28–40% (thermal efficiency, fuel to shaft)
- Electric motor: 94–97%
- Steam turbine: 25–35%

### 14.4.3 Discharge Temperature

The discharge temperature is critical for:
- Material selection (high-temperature gaskets, seals)
- Downstream equipment design
- Polymerization risk (for gases with reactive components)
- API 617 limits: typically < 200°C for carbon steel, < 260°C for alloy

$$T_2 = T_1 \left(\frac{P_2}{P_1}\right)^{(n-1)/n}$$

where $(n-1)/n = (\gamma - 1)/(\gamma \cdot \eta_p)$ for polytropic analysis.

For a typical natural gas ($\gamma = 1.3$, $\eta_p = 0.80$) compressed from 20°C with a pressure ratio of 3.0:

$$T_2 = 293 \times 3.0^{0.3/(1.3 \times 0.80)} = 293 \times 3.0^{0.288} = 293 \times 1.375 = 403 \text{ K} = 130°C$$

## 14.5 Multi-Stage Compression

### 14.5.1 Why Multi-Stage?

Single-stage compression is limited by the maximum allowable discharge temperature and the aerodynamic design limits of the compressor. Multi-stage compression with intercooling is used when:

1. **Temperature limit**: Discharge temperature would exceed material limits (typically 150–200°C)
2. **Efficiency**: Intercooling between stages reduces the work of compression by cooling the gas closer to the isentropic path
3. **High overall pressure ratio**: Pressure ratios above 4–6 per stage are generally impractical for centrifugal compressors
4. **Real gas effects**: At very high pressures, the compressibility factor changes significantly, requiring stage-by-stage analysis

### 14.5.2 Optimal Staging

For minimum total compression power, the pressure ratio should be divided equally among stages with perfect intercooling (cooling back to suction temperature):

$$r_{\text{stage}} = \left(\frac{P_{\text{discharge}}}{P_{\text{suction}}}\right)^{1/N_{\text{stages}}}$$

This equal-ratio staging minimizes the total work because the specific volume (and hence the work per unit pressure rise) is minimized at each stage by intercooling.

The total compression power with $N$ stages and perfect intercooling is:

$$\dot{W}_{\text{total}} = N \cdot \dot{m} \cdot \frac{n}{n-1} \cdot \frac{Z_1 R T_1}{MW} \left[r_{\text{stage}}^{(n-1)/n} - 1\right]$$

The power saving from multi-stage compression compared to single-stage compression (without intercooling) is significant:

| Overall PR | 1 Stage | 2 Stages | 3 Stages | 4 Stages |
|-----------|---------|----------|----------|----------|
| 4 | 100% | 88% | — | — |
| 9 | 100% | 82% | 78% | — |
| 16 | 100% | 78% | 73% | 71% |
| 25 | 100% | 76% | 70% | 67% |

*Table 14.3: Relative compression power for multi-stage compression with intercooling, normalized to single-stage power. $\gamma = 1.3$, perfect intercooling to inlet temperature.*

### 14.5.3 Practical Staging Considerations

In practice, the staging is not purely based on thermodynamic optimization but also considers:

- **Compressor casing limits**: Each casing may contain 2–8 impellers with a maximum head per casing
- **Intercooler limitations**: Ambient air temperature limits the achievable intercooling
- **Process integration**: Intermediate pressures may be fixed by sidestream injection from separator stages
- **Liquid knock-out**: Intercooled gas may form condensate that must be separated before the next stage

The number of stages for a recompression train is often determined by matching the required suction pressures to the separator operating pressures:

| Separator Stage | Pressure (bara) | Compression Stage |
|-----------------|-----------------|-------------------|
| LP separator | 2–4 | 1st stage suction |
| MP separator | 8–15 | 2nd stage suction (sidestream) |
| HP separator | 40–80 | 3rd stage suction or export |

*Table 14.4: Typical matching of separator stages to compression stages.*

## 14.6 Compression System Design

### 14.6.1 Suction Scrubber

A suction scrubber (knock-out drum) upstream of each compression stage removes entrained liquids and solids that would damage the compressor. Key design requirements:

- **Liquid removal efficiency**: > 99% for droplets above 10 μm
- **Pressure drop**: < 0.1 bar
- **Demister type**: Wire mesh pad or vane-type mist eliminator
- **Liquid retention**: Sufficient surge volume for level control (typically 1–3 minutes)
- **Sizing**: Based on Souders–Brown correlation for maximum gas velocity

$$v_{\text{max}} = K_s \sqrt{\frac{\rho_l - \rho_g}{\rho_g}}$$

where $K_s = 0.06$–$0.12$ m/s for vertical scrubbers with wire mesh demister.

### 14.6.2 Intercooler and After-Cooler

Gas leaving a compression stage is hot and must be cooled before entering the next stage (intercooler) or downstream equipment (after-cooler). Design considerations:

- **Cooling medium**: Air coolers (ambient + 15–25°C approach) or water coolers (seawater + 5–10°C approach)
- **Outlet temperature**: Typically 30–45°C for air cooling; 20–35°C for water cooling
- **Condensate formation**: Cooling may condense water and heavy hydrocarbons, requiring a downstream separator
- **Pressure drop**: 0.3–1.0 bar per cooler (affects compressor power)

### 14.6.3 Anti-Surge System

Centrifugal compressors have a minimum stable flow rate called the surge limit. Operating below this flow rate causes flow reversal, violent vibration, and potential damage. The anti-surge system prevents surge by:

1. **Monitoring**: Measuring suction and discharge pressures and flow rate
2. **Control**: Opening a recycle valve to maintain flow above the surge limit
3. **Protection**: Trip the compressor if surge is detected

The anti-surge control line is set 10–15% to the right of the surge line (in head vs. flow coordinates) to provide a safety margin. The recycle valve must open fast enough to prevent surge during rapid load changes (typically < 2 seconds for full stroke).

The surge control parameter is often defined as:

$$\text{SM} = \frac{Q_{\text{actual}} - Q_{\text{surge}}}{Q_{\text{surge}}} \times 100\%$$

where SM is the surge margin (%). A typical operating target is SM > 10%.

### 14.6.4 Variable Speed Drive

Variable speed drives (VSDs) on electric motors or variable turbine speed provide the most efficient way to control centrifugal compressor output. The affinity laws relate speed to performance:

$$Q \propto N, \quad H \propto N^2, \quad W \propto N^3$$

where $Q$ is volumetric flow, $H$ is head, $W$ is power, and $N$ is rotational speed. These are exact for dynamically similar conditions (discussed in detail in Chapter 13).

## 14.7 Compressor Drivers

### 14.7.1 Gas Turbines

Gas turbines are the predominant compressor drivers on offshore platforms due to their:
- High power density (MW per tonne)
- Ability to use produced gas as fuel
- Combined heat and power capability (waste heat recovery)
- Wide power range: 5–50+ MW per unit

Key performance parameters:
- Heat rate: 9,000–14,000 kJ/kWh
- Thermal efficiency: 25–40% (simple cycle)
- Exhaust temperature: 450–550°C (available for waste heat recovery)
- Availability: 95–98%

The fuel gas consumption is:

$$\dot{m}_{\text{fuel}} = \frac{\dot{W}_{\text{shaft}} \times \text{HR}}{LHV}$$

where HR is the heat rate (kJ/kWh) and LHV is the lower heating value of the fuel gas (kJ/kg).

### 14.7.2 Electric Motors

Electric motor drives are increasingly preferred for:
- Higher efficiency (94–97% vs. 25–40% for gas turbines)
- Lower emissions (no direct combustion)
- Lower maintenance
- Precise speed control with VSD
- Reduced weight and footprint

The trend toward electrification of offshore platforms favors electric motor drives powered by shore power or dedicated gas turbine generators.

### 14.7.3 Driver Selection

| Factor | Gas Turbine | Electric Motor |
|--------|-------------|----------------|
| Efficiency | 25–40% | 94–97% |
| Fuel/power | Fuel gas | Electrical grid |
| Emissions | Direct | Indirect (at generation) |
| Weight | Heavy | Moderate |
| Maintenance | High | Low |
| Speed control | Variable | VSD required |
| CAPEX | High | Moderate |
| OPEX | High (fuel) | Low |

*Table 14.5: Comparison of gas turbine and electric motor drives for compressors.*

### 14.7.4 Modeling the Driver in NeqSim

In NeqSim a gas-turbine driver is modeled explicitly with the `GasTurbineUnit` class (package `neqsim.process.equipment.powergeneration.gasturbine`), which is attached to one or more compressors as power consumers:

The current compressor constraint API is `updatePowerConstraint(ratingKW)`. Its argument is kW even though `getPower()` returns W. The generated capacity constraint includes the default overload allowance; a study requiring a strict driver limit must explicitly set its maximum and verify the selected operating point.

```python
# Illustrative 30 MW package, not an OEM performance guarantee.
gtpkg = jneqsim.process.equipment.powergeneration.gasturbine
spec = gtpkg.GasTurbineSpec("Teaching turbine", gtpkg.GasTurbineSpec.TurbineType.AERODERIVATIVE,
                          30.0e6, 9500.0, 90.0, 773.15, 25.0, 100.0, "Synthetic teaching basis")
fuel_gas = jneqsim.thermo.system.SystemSrkEos(298.15, 25.0)
for name, fraction in [("methane", 0.90), ("ethane", 0.06), ("propane", 0.03), ("CO2", 0.01)]:
    fuel_gas.addComponent(name, fraction)
fuel_gas.setMixingRule("classic")
fuel_stream = jneqsim.process.equipment.stream.Stream("Fuel gas", fuel_gas)
fuel_stream.setFlowRate(500.0, "kg/hr")
fuel_stream.run()
gas_turbine = gtpkg.GasTurbineUnit("GT-001", fuel_stream, spec)
gas_turbine.setAmbient(288.15, 1.01325)
gas_turbine.setDemandedPower(20.0e6)
gas_turbine.run()
print("Available shaft power (MW):", gas_turbine.getAvailablePowerW() / 1e6)
print("Demanded shaft power (MW):", gas_turbine.getDemandedPowerW() / 1e6)
print("Thermal efficiency:", gas_turbine.getThermalEfficiency())
print("Fuel demand (kg/hr):", gas_turbine.getFuelMassFlowKgPerHr())
print("Power shortfall (MW):", gas_turbine.getPowerShortfallW() / 1e6)
# Link a calculated compressor load instead of prescribing shaft demand.
gas_feed = jneqsim.process.equipment.stream.Stream("Compression feed", fuel_gas.clone())
gas_feed.setFlowRate(50000.0, "kg/hr")
gas_feed.run()
compressor = jneqsim.process.equipment.compressor.Compressor("Driven compressor", gas_feed)
compressor.setOutletPressure(100.0)
compressor.setIsentropicEfficiency(0.78)
compressor.run()
gt = gtpkg.GasTurbineUnit("GT-A", fuel_stream, spec)
gt.setAmbient(288.15, 1.01325)
gt.addPowerConsumer(compressor)
gt.run()
print("Driven load (MW):", gt.getDemandedPowerW() / 1e6)
print("Fuel (kg/hr):", gt.getFuelMassFlowKgPerHr())
```

The driver reports available power, fuel burn, and emissions, and can act as the binding generation constraint for the production optimizer. The full driver model — performance maps, degradation, emissions, and power allocation — is covered in Chapter 18 (*Power Production*).

## 14.8 NeqSim Implementation

### 14.8.1 Single-Stage Compression

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define gas composition
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, 10.0)
gas.addComponent("nitrogen", 1.0)
gas.addComponent("CO2", 2.5)
gas.addComponent("methane", 82.0)
gas.addComponent("ethane", 6.0)
gas.addComponent("propane", 4.0)
gas.addComponent("i-butane", 1.0)
gas.addComponent("n-butane", 2.0)
gas.addComponent("i-pentane", 0.5)
gas.addComponent("n-pentane", 0.5)
gas.addComponent("n-hexane", 0.5)
gas.setMixingRule("classic")

# Create feed stream
feed = jneqsim.process.equipment.stream.Stream("Compressor Inlet", gas)
feed.setFlowRate(50000.0, "kg/hr")
feed.setTemperature(30.0, "C")
feed.setPressure(10.0, "bara")

# Create compressor
compressor = jneqsim.process.equipment.compressor.Compressor(
    "1st Stage Compressor", feed)
compressor.setOutletPressure(30.0)
compressor.setPolytropicEfficiency(0.80)
compressor.setUsePolytropicCalc(True)

# Build and run
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(compressor)
process.run()

# Report results
print("=== Single-Stage Compression Results ===")
print(f"Suction T/P:   {feed.getTemperature('C'):.1f} C / "
      f"{feed.getPressure():.1f} bara")
print(f"Discharge T/P: "
      f"{compressor.getOutletStream().getTemperature('C'):.1f} C / "
      f"{compressor.getOutletStream().getPressure():.1f} bara")
print(f"Pressure ratio: {compressor.getOutletStream().getPressure() / feed.getPressure():.2f}")
print(f"Polytropic eff: {compressor.getPolytropicEfficiency() * 100:.1f}%")
print(f"Power:         {compressor.getPower() / 1000.0:.1f} kW")
print(f"Polytropic head: {compressor.getPolytropicFluidHead():.1f} kJ/kg")
```

### 14.8.2 Multi-Stage Compression with Intercooling

This example demonstrates a 3-stage recompression train with intercooling, representing a typical offshore recompression system:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define LP gas from separator
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 40.0, 2.5)
gas.addComponent("nitrogen", 0.8)
gas.addComponent("CO2", 3.0)
gas.addComponent("methane", 78.0)
gas.addComponent("ethane", 7.0)
gas.addComponent("propane", 5.0)
gas.addComponent("i-butane", 1.5)
gas.addComponent("n-butane", 2.5)
gas.addComponent("i-pentane", 0.7)
gas.addComponent("n-pentane", 0.5)
gas.addComponent("n-hexane", 0.5)
gas.addComponent("n-heptane", 0.3)
gas.addComponent("water", 0.2)
gas.setMixingRule("classic")
gas.setMultiPhaseCheck(True)

# Feed stream
feed = jneqsim.process.equipment.stream.Stream(
    "LP Gas Feed", gas)
feed.setFlowRate(30000.0, "kg/hr")
feed.setTemperature(40.0, "C")
feed.setPressure(2.5, "bara")

# ============================================================
# Stage 1: 2.5 -> 8.0 bara
# ============================================================
comp1 = jneqsim.process.equipment.compressor.Compressor(
    "1st Stage Compressor", feed)
comp1.setOutletPressure(8.0)
comp1.setPolytropicEfficiency(0.78)
comp1.setUsePolytropicCalc(True)

cooler1 = jneqsim.process.equipment.heatexchanger.Heater(
    "1st Intercooler", comp1.getOutletStream())
cooler1.setOutTemperature(273.15 + 35.0)

scrub1 = jneqsim.process.equipment.separator.Separator(
    "1st Scrubber", cooler1.getOutletStream())

# ============================================================
# Stage 2: 8.0 -> 25.0 bara
# ============================================================
comp2 = jneqsim.process.equipment.compressor.Compressor(
    "2nd Stage Compressor", scrub1.getGasOutStream())
comp2.setOutletPressure(25.0)
comp2.setPolytropicEfficiency(0.80)
comp2.setUsePolytropicCalc(True)

cooler2 = jneqsim.process.equipment.heatexchanger.Heater(
    "2nd Intercooler", comp2.getOutletStream())
cooler2.setOutTemperature(273.15 + 35.0)

scrub2 = jneqsim.process.equipment.separator.Separator(
    "2nd Scrubber", cooler2.getOutletStream())

# ============================================================
# Stage 3: 25.0 -> 75.0 bara
# ============================================================
comp3 = jneqsim.process.equipment.compressor.Compressor(
    "3rd Stage Compressor", scrub2.getGasOutStream())
comp3.setOutletPressure(75.0)
comp3.setPolytropicEfficiency(0.82)
comp3.setUsePolytropicCalc(True)

after_cooler = jneqsim.process.equipment.heatexchanger.Heater(
    "After Cooler", comp3.getOutletStream())
after_cooler.setOutTemperature(273.15 + 35.0)

# Build process
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(comp1)
process.add(cooler1)
process.add(scrub1)
process.add(comp2)
process.add(cooler2)
process.add(scrub2)
process.add(comp3)
process.add(after_cooler)
process.run()

# Report results
print("=" * 70)
print("3-STAGE RECOMPRESSION TRAIN RESULTS")
print("=" * 70)

stages = [
    ("1st Stage", comp1, cooler1),
    ("2nd Stage", comp2, cooler2),
    ("3rd Stage", comp3, after_cooler)
]

total_power = 0.0
for name, comp, cooler in stages:
    pr = comp.getOutletStream().getPressure() / comp.getInletStream().getPressure()
    power = comp.getPower() / 1000.0
    total_power += power
    print(f"\n{name}:")
    print(f"  Suction:    {comp.getInletStream().getTemperature('C'):.1f} C / "
          f"{comp.getInletStream().getPressure():.1f} bara")
    print(f"  Discharge:  {comp.getOutletStream().getTemperature('C'):.1f} C / "
          f"{comp.getOutletStream().getPressure():.1f} bara")
    print(f"  PR:         {pr:.2f}")
    print(f"  Power:      {power:.0f} kW")
    print(f"  After cool: {cooler.getOutletStream().getTemperature('C'):.1f} C")

print(f"\n{'=' * 70}")
print(f"TOTAL COMPRESSION POWER: {total_power:.0f} kW "
      f"({total_power/1000:.1f} MW)")
print(f"Overall PR: {75.0/2.5:.1f}")
print(f"{'=' * 70}")
```

### 14.8.3 Pressure Ratio Sensitivity Study

This example shows how compressor power and discharge temperature vary with pressure ratio:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import matplotlib.pyplot as plt

# Define gas
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, 10.0)
gas.addComponent("methane", 85.0)
gas.addComponent("ethane", 6.0)
gas.addComponent("propane", 4.0)
gas.addComponent("n-butane", 2.0)
gas.addComponent("CO2", 2.0)
gas.addComponent("nitrogen", 1.0)
gas.setMixingRule("classic")

pressure_ratios = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
powers = []
temperatures = []

for pr in pressure_ratios:
    fluid = gas.clone()
    feed = jneqsim.process.equipment.stream.Stream("Feed", fluid)
    feed.setFlowRate(20000.0, "kg/hr")
    feed.setTemperature(30.0, "C")
    feed.setPressure(10.0, "bara")

    comp = jneqsim.process.equipment.compressor.Compressor("Comp", feed)
    comp.setOutletPressure(10.0 * pr)
    comp.setPolytropicEfficiency(0.80)
    comp.setUsePolytropicCalc(True)

    process = jneqsim.process.processmodel.ProcessSystem()
    process.add(feed)
    process.add(comp)
    process.run()

    powers.append(comp.getPower() / 1000.0)
    temperatures.append(comp.getOutletStream().getTemperature("C"))

# Plot results
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.plot(pressure_ratios, powers, 'bo-', linewidth=2, markersize=8)
ax1.set_xlabel("Pressure Ratio", fontsize=12)
ax1.set_ylabel("Compressor Power (kW)", fontsize=12)
ax1.set_title("Compressor Power vs. Pressure Ratio", fontsize=14)
ax1.grid(True, alpha=0.3)

ax2.plot(pressure_ratios, temperatures, 'rs-', linewidth=2, markersize=8)
ax2.axhline(y=150, color='k', linestyle='--', label='Typical T limit')
ax2.set_xlabel("Pressure Ratio", fontsize=12)
ax2.set_ylabel("Discharge Temperature (°C)", fontsize=12)
ax2.set_title("Discharge Temperature vs. Pressure Ratio", fontsize=14)
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("figures/compression_pr_sensitivity.png", dpi=150,
            bbox_inches="tight")
plt.show()
```

![Compressor power and discharge temperature vs. pressure ratio](figures/compression_pr_sensitivity.png)

*Figure 14.1: Compressor power (left) and discharge temperature (right) as functions of pressure ratio for a single-stage centrifugal compressor. The dashed line indicates the typical discharge temperature limit of 150°C, which constrains the maximum practical pressure ratio per stage.*

### 14.8.4 Effect of Gas Composition on Compression

Gas molecular weight significantly affects compressor performance. At comparable temperature, pressure ratio and efficiency, heavier gases generally require less specific head per unit mass; compressibility and heat capacity also affect the result. A fixed mass-flow comparison must be distinguished from a fixed standard-volume-flow comparison:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Compare compression of different gases
compositions = {
    "Lean gas (MW~18)": {"methane": 90, "ethane": 5, "propane": 2,
                          "CO2": 2, "nitrogen": 1},
    "Rich gas (MW~22)": {"methane": 75, "ethane": 10, "propane": 6,
                          "n-butane": 3, "n-pentane": 1,
                          "CO2": 3, "nitrogen": 2},
    "Very rich (MW~26)": {"methane": 60, "ethane": 12, "propane": 10,
                           "n-butane": 6, "n-pentane": 3,
                           "n-hexane": 2, "CO2": 4, "nitrogen": 3}
}

print(f"{'Gas Type':<22} {'MW':>6} {'Power':>10} {'T_out':>8} {'Head':>10}")
print("-" * 60)

for name, comp_dict in compositions.items():
    fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, 10.0)
    for component, fraction in comp_dict.items():
        fluid.addComponent(component, float(fraction))
    fluid.setMixingRule("classic")

    feed = jneqsim.process.equipment.stream.Stream("Feed", fluid)
    feed.setFlowRate(20000.0, "kg/hr")
    feed.setTemperature(30.0, "C")
    feed.setPressure(10.0, "bara")

    comp = jneqsim.process.equipment.compressor.Compressor("Comp", feed)
    comp.setOutletPressure(30.0)
    comp.setPolytropicEfficiency(0.80)
    comp.setUsePolytropicCalc(True)

    process = jneqsim.process.processmodel.ProcessSystem()
    process.add(feed)
    process.add(comp)
    process.run()

    mw = feed.getFluid().getMolarMass() * 1000  # kg/kmol
    power = comp.getPower() / 1000.0
    t_out = comp.getOutletStream().getTemperature("C")
    head = comp.getPolytropicFluidHead()

    print(f"{name:<22} {mw:>6.1f} {power:>8.0f} kW {t_out:>6.1f} C "
          f"{head:>8.1f} kJ/kg")
```

## 14.9 Worked Example: 3-Stage Recompression Train Design

**Problem**: Design a recompression train for an offshore platform that must compress 150,000 Sm$^3$/hr of gas from 2.0 bara to 75 bara. The gas composition is: CH$_4$ 78%, C$_2$H$_6$ 7%, C$_3$H$_8$ 5%, iC$_4$ 1.5%, nC$_4$ 2.5%, iC$_5$ 0.7%, nC$_5$ 0.5%, CO$_2$ 3%, N$_2$ 0.8%, H$_2$O 1%. Cooling water is available at 18°C.

**Design basis**:
- Maximum discharge temperature per stage: 150°C
- Intercooler outlet temperature: 35°C
- Polytropic efficiency: 78% (1st stage), 80% (2nd stage), 82% (3rd stage)
- Mechanical efficiency: 98%

**Step 1**: Determine the number of stages. Overall pressure ratio = 75/2 = 37.5. Equal ratio per stage = $37.5^{1/3} = 3.35$. This gives intermediate pressures of 6.7 and 22.4 bara.

**Step 2**: Check discharge temperatures. With $\gamma \approx 1.3$ and $\eta_p = 0.78$–$0.82$, the discharge temperatures are approximately 120–135°C — within limits.

**Step 3**: Model in NeqSim (see code in Section 14.8.2, adapted with these specific parameters).

**Step 4**: Verify results and iterate if necessary.

## 14.10 Summary

This chapter has covered the thermodynamics, design, and simulation of gas compression systems:

1. **Compression applications** span recompression, export, gas lift, injection, and flare gas recovery. Compression capacity directly impacts production rates and plateau duration.

2. **Centrifugal compressors** dominate offshore applications due to reliability and compactness. Reciprocating compressors are preferred for very high pressures and low flow rates.

3. **Polytropic analysis** is preferred over isentropic for centrifugal compressors because polytropic efficiency is nearly independent of pressure ratio.

4. **Multi-stage compression** with intercooling reduces total power, limits discharge temperature, and is required for high overall pressure ratios.

5. **System design** must include suction scrubbers, intercoolers/after-coolers, and anti-surge protection.

6. **NeqSim's Compressor class** accurately models real-gas compression including both isentropic and polytropic calculations, and integrates seamlessly with the ProcessSystem framework.

7. **Gas composition** significantly affects compression power and head; performance changes with declining reservoir pressure and increasing GOR must be tracked.

## 14.11 Compressor Capacity Constraints in NeqSim

### 14.11.1 The CapacityConstrainedEquipment Interface

In production optimization, it is essential to know *when* equipment reaches its limits. NeqSim provides the `CapacityConstrainedEquipment` interface — a standardized API that lets any process equipment declare its capacity constraints and report utilization. The `Compressor` class implements this interface, enabling automated bottleneck detection and optimization routines.

The interface provides three core capabilities:

1. **Constraint declaration** — each piece of equipment defines named constraints with design values, current operating values, and utilization ratios
2. **Utilization tracking** — a single `getMaxUtilization()` call returns the highest utilization across all active constraints (the binding constraint)
3. **Optimization integration** — the `ProductionOptimizer` automatically discovers all `CapacityConstrainedEquipment` in a `ProcessSystem` and uses their constraints to determine the maximum achievable production rate

```java
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
Logger logger = LogManager.getLogger("BookChapter14");
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
import neqsim.process.equipment.compressor.*;
// The interface methods (simplified)
public interface CapacityConstrainedEquipment {
    Map<String, CapacityConstraint> getCapacityConstraints();
    double getMaxUtilization();           // highest utilization across all constraints
    boolean isCapacityAnalysisEnabled();
    void setCapacityAnalysisEnabled(boolean enabled);
    void enableConstraints();
}
```

### 14.11.2 Compressor Constraint Types

A centrifugal compressor has multiple physical limits that can constrain production. NeqSim models each of these as a named `CapacityConstraint`:

| Constraint Name | Physical Limit | Typical Design Value | Type |
|----------------|---------------|---------------------|------|
| `speed` | Maximum rotational speed | 10,000–15,000 rpm | HARD |
| `power` | Maximum driver power | 5–50 MW | HARD |
| `surgeMargin` | Minimum surge margin | 10–15% | HARD |
| `stonewallMargin` | Choke flow limit | 5–10% margin | HARD |
| `minSpeed` | Minimum stable speed | 60–70% of max | SOFT |
| `ratedPower` | Continuous rated power | 80–90% of max | DESIGN |
| `dischargeTemperature` | Maximum discharge T | 150–200°C | HARD |

Each constraint has a **type** that determines how the optimizer treats it:

- **HARD** — the constraint must never be violated; the optimizer treats it as an absolute limit
- **SOFT** — the constraint can be temporarily exceeded but triggers a warning
- **DESIGN** — the constraint represents the normal design operating range; operating beyond it reduces equipment life but is physically possible

The utilization for each constraint is calculated as:

$$u_i = \frac{x_{\text{current},i}}{x_{\text{design},i}}$$

and the overall compressor utilization is the maximum across all active constraints:

$$u_{\text{max}} = \max_i \left( u_i \right)$$

When $u_{\text{max}} \geq 1.0$, the compressor is at capacity and is a production bottleneck.

### 14.11.3 Setting Up Compressor Constraints

Compressor constraints can be configured explicitly or through the `autoSize()` method:

**Manual constraint setup (Java):**

```java
Compressor comp = new Compressor("Export Compressor", feed);
comp.setOutletPressure(120.0);
comp.setPolytropicEfficiency(0.82);
comp.setUsePolytropicCalc(true);

// Set explicit constraints
comp.setMaximumSpeed(11500.0);       // rpm
comp.updatePowerConstraint((25.0e6) / 1000.0);        // kW (25 MW)
comp.getAntiSurge().setSurgeControlFactor(1.10);           // 10% minimum
comp.reinitializeCapacityConstraints();            // Activate constraint tracking

process.add(comp);
process.run();
Compressor compressor = comp;
```

**Automatic sizing with `autoSize()` (Java):**

```java
// First run the process to establish the operating point
process.run();

// autoSize creates constraints based on current operating point + design margin
comp.autoSize(1.2);  // 20% design margin above current operating point
```

The `autoSize(designMargin)` method:
1. Reads the current operating speed, power, and head from the compressor
2. Creates constraints at `designMargin × currentValue` for each parameter
3. Generates a compressor performance chart at the design point (if no chart exists)
4. Sets up surge and stonewall margins based on the chart
5. Enables capacity analysis for this compressor

After `autoSize()`, the compressor's utilization will be approximately $1/\text{designMargin}$ at the current operating point. For a design margin of 1.2 (20%), the utilization at the design point is $1/1.2 \approx 83\%$, providing operational margin for turndown and uprate.

### 14.11.4 Reinitializing Constraints After Chart Setup

If you set up a compressor chart manually (from vendor data or generated), you must reinitialize the capacity constraints to ensure they reflect the chart's operating envelope:

```java
// Set up chart first
CompressorChartGenerator generator = new CompressorChartGenerator(comp);
comp.setCompressorChart(generator.generateCompressorChart("normal curves", 5));

// Now reinitialize constraints based on the chart
comp.reinitializeCapacityConstraints();
```

This recalculates the surge and stonewall margins based on the actual chart data rather than the simplified estimates from `autoSize()`.

### 14.11.5 Querying Compressor Utilization

```java
// After process.run()
double utilization = comp.getMaxUtilization();
Map<String, CapacityConstraint> constraints = comp.getCapacityConstraints();

for (Map.Entry<String, CapacityConstraint> entry : constraints.entrySet()) {
    CapacityConstraint c = entry.getValue();
    logger.info(entry.getKey() + ": "
        + c.getCurrentValue() + " / " + c.getDesignValue()
        + " = " + String.format("%.1f%%", c.getUtilization() * 100));
}
```

## 14.12 Compressor Performance Curves and Optimization

### 14.12.1 Why Performance Curves Matter

Compressor performance curves (also called *maps* or *characteristics*) define the relationship between flow, head, speed, and efficiency. Without curves, NeqSim models a compressor at a fixed efficiency — adequate for steady-state design but insufficient for optimization studies where:

- The operating point moves along the curve as production rates change
- Efficiency varies with flow and speed
- Surge and stonewall limits constrain the operating envelope
- Speed variation (VFD) affects power consumption non-linearly

### 14.12.2 The CompressorChartGenerator

NeqSim's `CompressorChartGenerator` creates realistic performance curves from a single design point, using the physics of centrifugal compressor aerodynamics:

```java
// Generate curves at the current design point
CompressorChartGenerator generator = new CompressorChartGenerator(compressor);
CompressorChartInterface chart = generator.generateCompressorChart("normal curves", 5);

// Apply to compressor
compressor.setCompressorChart(chart);
// Generated charts already use interpolation and extrapolation.
```

The `generateCompressorChart(type, nCurves)` method:

1. Calculates the design head, flow, and efficiency from the compressor's current operating state
2. Generates `nCurves` speed lines (typically 5–7) spanning from ~70% to ~115% of design speed
3. For each speed line, calculates head and efficiency vs. flow using standard aerodynamic correlations
4. Marks the surge point (flow at minimum stable operation) and stonewall point (choked flow) on each curve
5. Returns a `CompressorChartInterface` that the compressor uses during simulation

### 14.12.3 Affinity Laws in NeqSim

The performance curves obey the fan/affinity laws, which relate performance at different speeds:

**Flow scales linearly with speed:**

$$Q_2 = Q_1 \cdot \frac{N_2}{N_1}$$

**Head scales with speed squared:**

$$H_2 = H_1 \cdot \left(\frac{N_2}{N_1}\right)^2$$

**Power scales with speed cubed:**

$$W_2 = W_1 \cdot \left(\frac{N_2}{N_1}\right)^3$$

These relationships are exact for incompressible flow and approximate for compressible flow at moderate pressure ratios (PR < 3). NeqSim's chart generator uses the affinity laws to scale the design-point curve to other speeds, with corrections for compressibility effects.

The practical implication is dramatic: reducing speed by 10% reduces power by approximately 27% ($0.9^3 = 0.729$). This makes variable-speed operation extremely attractive for energy optimization.

### 14.12.4 Setting Maximum Speed

The maximum speed should be set above the design operating speed to allow the compressor to handle increased flow or pressure ratio during production optimization:

```java
// Set max speed 15% above current operating speed
double designSpeed = compressor.getSpeed();
compressor.setMaximumSpeed(designSpeed * 1.15);
```

A typical margin is 10–15% above the design-point speed. The optimizer can then increase the compressor speed (and hence flow/head capacity) up to this maximum when seeking to increase production.

### 14.12.5 Using Curves with the ProductionOptimizer

When a compressor has a performance chart, the `ProductionOptimizer` uses it to:

1. **Determine the current operating point** on the chart (head, flow, speed, efficiency)
2. **Check if the operating point is within the surge-stonewall envelope** — if not, the optimizer adjusts conditions to move the point back into the stable region
3. **Calculate the actual efficiency** at the operating point (not the fixed design efficiency)
4. **Determine available capacity** — how much more flow or head the compressor can deliver before hitting a constraint

```java
ProductionOptimizer optimizer = new ProductionOptimizer();
ProductionOptimizer.OptimizationResult optimum = optimizer.optimizeThroughput(
    process, feed, 5000.0, 30000.0, "kg/hr", null);
logger.info("Feasible: {}, rate: {} kg/hr", optimum.isFeasible(), optimum.getOptimalRate());
```

### 14.12.6 Performance Curve Equations

The head-flow relationship for a centrifugal compressor at a given speed can be approximated by a second-order polynomial:

$$H(Q) = a_0 + a_1 Q + a_2 Q^2$$

where:
- $H$ is the polytropic head [kJ/kg]
- $Q$ is the actual volumetric flow [m³/hr]
- $a_0$, $a_1$, $a_2$ are curve-fit coefficients

The efficiency-flow relationship is typically a peaked curve:

$$\eta(Q) = \eta_{\max} - b \left(\frac{Q - Q_{\text{BEP}}}{Q_{\text{BEP}}}\right)^2$$

where $Q_{\text{BEP}}$ is the best efficiency point (BEP) flow and $b$ is a shape parameter. The BEP flow is typically 80–90% of the stonewall (choke) flow.

The surge line across multiple speed curves can be approximated by:

$$H_{\text{surge}} = c_0 + c_1 Q_{\text{surge}}^2$$

which forms a roughly parabolic envelope on the left side of the compressor map.

## 14.13 Compressor Optimization Guide

### 14.13.1 Variable Frequency Drive (VFD) and Multi-Speed Configuration

Variable frequency drives enable continuous speed variation, providing the most efficient method of flow control for centrifugal compressors. In NeqSim, VFD behavior is modeled by allowing the compressor speed to vary within the defined speed range:

```java
// Configure VFD-equipped compressor
compressor.setMaximumSpeed(11500.0);  // Maximum VFD speed
compressor.setMinimumSpeed(7000.0);   // Minimum stable speed (~60% of max)

// The optimizer can now vary speed to find optimal operating point
```

The power saving from speed reduction compared to throttling (inlet guide vane or suction valve) is significant:

| Flow Reduction | Throttle Power (% of design) | VFD Power (% of design) | Savings |
|---------------|------------------------------|------------------------|---------|
| 10% | 90% | 73% | 17% |
| 20% | 82% | 51% | 31% |
| 30% | 76% | 34% | 42% |
| 40% | 72% | 22% | 50% |

*Table 14.6: Power comparison between throttling and VFD control at reduced flows. VFD follows the cubic affinity law ($W \propto N^3$).*

### 14.13.2 CompressorOptimizationHelper

For complex multi-compressor systems, NeqSim provides the `CompressorOptimizationHelper` utility that coordinates optimization across multiple machines:

```java
// Separate parallel-machine setup; an optimizer needs independent split decisions.
Stream feedA = new Stream("Train A feed", fluid.clone());
Stream feedB = new Stream("Train B feed", fluid.clone());
feedA.setFlowRate(10000.0, "kg/hr");
feedB.setFlowRate(10000.0, "kg/hr");
feedA.run();
feedB.run();
Compressor compA = new Compressor("Train A", feedA);
Compressor compB = new Compressor("Train B", feedB);
compA.setOutletPressure(120.0);
compB.setOutletPressure(120.0);
compA.run();
compB.run();
logger.info("Parallel baseline power: {} kW", compA.getPower("kW") + compB.getPower("kW"));
```

### 14.13.3 Single-Variable Optimization

The simplest optimization adjusts a single compressor's speed or pressure to maximize throughput or minimize power:

**Minimize power at fixed throughput:**

$$\min_{N} \quad W(N) = \dot{m} \cdot H_p(Q(N)) / \eta_p(Q(N))$$

$$\text{subject to:} \quad N_{\min} \leq N \leq N_{\max}$$

$$\quad Q_{\text{surge}}(N) \leq Q(N) \leq Q_{\text{stonewall}}(N)$$

**Maximize throughput at fixed power:**

$$\max_{P_{\text{out}}} \quad \dot{m}(P_{\text{out}})$$

$$\text{subject to:} \quad W \leq W_{\max}$$

$$\quad T_{\text{discharge}} \leq T_{\max}$$

### 14.13.4 Multi-Variable Optimization Strategy

For multi-stage compression, a two-stage optimization strategy is effective:

**Stage 1: Pressure distribution** — Optimize intermediate pressures to minimize total power. For $N$ stages with overall pressure ratio $r_{\text{total}}$:

$$\min_{r_1, r_2, \ldots, r_N} \quad \sum_{i=1}^{N} W_i(r_i)$$

$$\text{subject to:} \quad \prod_{i=1}^{N} r_i = r_{\text{total}}$$

$$\quad T_{\text{discharge},i} \leq T_{\max}$$

**Stage 2: Speed optimization** — For each stage, optimize speed (if VFD-equipped) to operate at best efficiency:

$$\min_{N_i} \quad W_i(N_i, r_i) \quad \text{for each stage } i$$

The combined optimization typically achieves 5–15% power savings compared to equal-ratio staging with fixed-speed operation.

### 14.13.5 Driver Curves Integration

Gas turbine and electric motor drivers have their own performance characteristics that constrain the compressor. The driver power available depends on:

- **Gas turbine**: Power decreases with increasing ambient temperature (typically 0.5–1.0% per °C above ISO conditions of 15°C). On a hot day, the compressor may be driver-limited before it reaches its aerodynamic limit.
- **Electric motor**: Power is essentially constant but limited by the motor rating and VFD capacity.

$$W_{\text{GT,available}} = W_{\text{GT,rated}} \cdot f(T_{\text{ambient}}) \cdot f(\text{altitude}) \cdot f(\text{fuel type})$$

In NeqSim, the driver limit is set through `setMaximumPower()`:

```java
// Gas turbine with 25 MW rated power at ISO conditions
// De-rate for ambient temperature of 30°C
double ambientTemp = 30.0;  // °C
double isoRating = 25.0e6;  // W
double derating = 1.0 - 0.007 * (ambientTemp - 15.0);  // ~0.7%/°C
comp.updatePowerConstraint((isoRating * derating) / 1000.0);  // ~22.4 MW available
```

### 14.13.6 Anti-Surge Control in Optimization Context

When the optimizer reduces the suction flow (e.g., due to declining well rates), the compressor operating point moves toward the surge line. The anti-surge controller opens the recycle valve to maintain the surge margin, but recycled gas consumes power without adding useful compression.

The net useful throughput is:

$$\dot{m}_{\text{useful}} = \dot{m}_{\text{total}} - \dot{m}_{\text{recycle}}$$

The specific power consumption increases sharply near surge:

$$\text{SPC} = \frac{W}{\dot{m}_{\text{useful}}} = \frac{W}{\dot{m}_{\text{total}} - \dot{m}_{\text{recycle}}}$$

This creates a practical minimum throughput below which the compressor becomes uneconomic. The optimizer should account for this by including the recycle flow in the objective function:

$$\min \quad W(Q) \quad \text{subject to:} \quad Q > Q_{\text{surge}} + \Delta Q_{\text{margin}}$$

If the optimizer finds that the compressor must recycle more than 20–30% of its flow, it may be more efficient to reduce speed (if VFD-equipped) or switch to a smaller machine.

## 14.14 Python Implementation: Complete Compressor Optimization

### 14.14.1 Building a Compressor with Performance Curves

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import matplotlib.pyplot as plt
import numpy as np

# ============================================================
# Step 1: Define gas and process
# ============================================================
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, 10.0)
gas.addComponent("nitrogen", 1.0)
gas.addComponent("CO2", 2.5)
gas.addComponent("methane", 82.0)
gas.addComponent("ethane", 6.0)
gas.addComponent("propane", 4.0)
gas.addComponent("i-butane", 1.0)
gas.addComponent("n-butane", 2.0)
gas.addComponent("i-pentane", 0.5)
gas.addComponent("n-pentane", 0.5)
gas.addComponent("n-hexane", 0.5)
gas.setMixingRule("classic")

Stream = jneqsim.process.equipment.stream.Stream
Compressor = jneqsim.process.equipment.compressor.Compressor
CompressorChartGenerator = jneqsim.process.equipment.compressor.CompressorChartGenerator
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

feed = Stream("Compressor Inlet", gas)
feed.setFlowRate(50000.0, "kg/hr")
feed.setTemperature(30.0, "C")
feed.setPressure(10.0, "bara")

comp = Compressor("1st Stage Compressor", feed)
comp.setOutletPressure(30.0)
comp.setPolytropicEfficiency(0.80)
comp.setUsePolytropicCalc(True)

process = ProcessSystem()
process.add(feed)
process.add(comp)
process.run()

# ============================================================
# Step 2: Generate compressor performance curves
# ============================================================
generator = CompressorChartGenerator(comp)
chart = generator.generateCompressorChart("normal curves", 5)
comp.setCompressorChart(chart)

# Set chart to interpolate for off-design operation
# Generated charts already use interpolation and extrapolation.

# Set max speed 15% above current operating point
design_speed = comp.getSpeed()
comp.setMaximumSpeed(design_speed * 1.15)

# Re-run with chart active
process.run()

# ============================================================
# Step 3: Report results with chart
# ============================================================
print("=== Compressor with Performance Chart ===")
print(f"Operating speed: {comp.getSpeed():.0f} rpm")
print(f"Maximum speed:   {comp.getMaximumSpeed():.0f} rpm")
print(f"Power:           {comp.getPower()/1e3:.1f} kW")
print(f"Polytropic head: {comp.getPolytropicFluidHead():.1f} kJ/kg")
print(f"Polytropic eff:  {comp.getPolytropicEfficiency()*100:.1f}%")
print(f"Discharge T:     {comp.getOutletStream().getTemperature('C'):.1f} °C")
print(f"Pressure ratio:  "
      f"{comp.getOutletStream().getPressure()/comp.getInletStream().getPressure():.2f}")
```

### 14.14.2 Using ProductionOptimizer with Compressor Constraints

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Build a compression system with capacity constraints
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 35.0, 5.0)
gas.addComponent("methane", 80.0)
gas.addComponent("ethane", 8.0)
gas.addComponent("propane", 5.0)
gas.addComponent("n-butane", 3.0)
gas.addComponent("CO2", 3.0)
gas.addComponent("nitrogen", 1.0)
gas.setMixingRule("classic")

Stream = jneqsim.process.equipment.stream.Stream
Compressor = jneqsim.process.equipment.compressor.Compressor
Heater = jneqsim.process.equipment.heatexchanger.Heater
Separator = jneqsim.process.equipment.separator.Separator
CompressorChartGenerator = jneqsim.process.equipment.compressor.CompressorChartGenerator
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# Two-stage compression: 5 -> 15 -> 45 bara
feed = Stream("Feed Gas", gas)
feed.setFlowRate(40000.0, "kg/hr")
feed.setTemperature(35.0, "C")
feed.setPressure(5.0, "bara")

# Stage 1
comp1 = Compressor("1st Stage", feed)
comp1.setOutletPressure(15.0)
comp1.setPolytropicEfficiency(0.78)
comp1.setUsePolytropicCalc(True)

cooler1 = Heater("Intercooler", comp1.getOutletStream())
cooler1.setOutTemperature(273.15 + 35.0)

scrub = Separator("Interstage Scrubber", cooler1.getOutletStream())

# Stage 2
comp2 = Compressor("2nd Stage", scrub.getGasOutStream())
comp2.setOutletPressure(45.0)
comp2.setPolytropicEfficiency(0.80)
comp2.setUsePolytropicCalc(True)

process = ProcessSystem()
process.add(feed)
process.add(comp1)
process.add(cooler1)
process.add(scrub)
process.add(comp2)
process.run()

# Generate performance curves for both stages
gen1 = CompressorChartGenerator(comp1)
comp1.setCompressorChart(gen1.generateCompressorChart("normal curves", 5))
# Generated charts already use interpolation and extrapolation.

gen2 = CompressorChartGenerator(comp2)
comp2.setCompressorChart(gen2.generateCompressorChart("normal curves", 5))
# Generated charts already use interpolation and extrapolation.

# Auto-size with 20% design margin
comp1.autoSize(1.2)
comp2.autoSize(1.2)

# Re-run to update
process.run()

# Report utilization
print("=== Two-Stage Compression with Capacity Constraints ===")
for name, comp in [("1st Stage", comp1), ("2nd Stage", comp2)]:
    util = comp.getMaxUtilization()
    power = comp.getPower() / 1e3
    print(f"\n{name}:")
    print(f"  Power:       {power:.0f} kW")
    print(f"  Utilization: {util*100:.1f}%")
    print(f"  Speed:       {comp.getSpeed():.0f} rpm")

total_power = comp1.getPower()/1e3 + comp2.getPower()/1e3
print(f"\nTotal compression power: {total_power:.0f} kW ({total_power/1e3:.2f} MW)")
```

### 14.14.3 Plotting Compressor Operating Point on Performance Map

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import matplotlib.pyplot as plt
import numpy as np

# After building and running the compressor (as in 12.14.1)...
# Assume comp is a Compressor with a chart set up

# Extract the operating point
actual_flow = comp.getInletStream().getFlowRate("Am3/hr")
actual_head = comp.getPolytropicFluidHead()  # kJ/kg
actual_speed = comp.getSpeed()

# Create a conceptual compressor map
# (In practice, extract curve data from the chart object)
flows = np.linspace(0.3 * actual_flow, 1.5 * actual_flow, 100)

# Simplified head-flow curves at different speeds
fig, ax = plt.subplots(figsize=(10, 7))

speed_fractions = [0.70, 0.80, 0.90, 1.00, 1.10]
colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd']

for sf, color in zip(speed_fractions, colors):
    # Affinity law scaling
    q = flows * sf
    h = actual_head * sf**2 * (1.0 - 0.3 * ((flows/actual_flow - 1.0))**2)
    label = f"{sf*100:.0f}% speed ({sf*actual_speed:.0f} rpm)"
    ax.plot(q, h, '-', color=color, linewidth=1.5, label=label)

# Plot operating point
ax.plot(actual_flow, actual_head, 'ko', markersize=12, zorder=5,
        label=f'Operating point')
ax.annotate(f'  Design: {actual_flow:.0f} am³/hr\n  Head: {actual_head:.1f} kJ/kg',
            xy=(actual_flow, actual_head), fontsize=10,
            xytext=(actual_flow * 1.05, actual_head * 1.05),
            arrowprops=dict(arrowstyle='->', color='black'))

# Surge line (approximate)
surge_flows = np.array([sf * actual_flow * 0.55 for sf in speed_fractions])
surge_heads = np.array([actual_head * sf**2 * 1.15 for sf in speed_fractions])
ax.plot(surge_flows, surge_heads, 'r--', linewidth=2, label='Surge line')

ax.set_xlabel("Actual Volume Flow (am³/hr)", fontsize=12)
ax.set_ylabel("Polytropic Head (kJ/kg)", fontsize=12)
ax.set_title("Compressor Performance Map", fontsize=14)
ax.legend(fontsize=10, loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_xlim(0, actual_flow * 1.6)
ax.set_ylim(0, actual_head * 1.5)

plt.tight_layout()
plt.savefig("figures/compressor_performance_map.png", dpi=150,
            bbox_inches="tight")
plt.show()
```

![Compressor performance map showing operating point and speed lines](figures/compressor_performance_map.png)

*Figure 14.2: Compressor performance map with head vs. flow curves at five speed lines. The operating point (black dot) sits on the 100% speed line. The red dashed line indicates the surge limit. The optimizer can vary the speed between the minimum and maximum speed lines to adjust throughput while maintaining adequate surge margin.*

### 14.14.4 Speed Sensitivity Analysis

The following example demonstrates how compressor power varies with speed at fixed discharge pressure, illustrating the cubic power law:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import matplotlib.pyplot as plt
import numpy as np

gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, 10.0)
gas.addComponent("methane", 85.0)
gas.addComponent("ethane", 6.0)
gas.addComponent("propane", 4.0)
gas.addComponent("n-butane", 2.0)
gas.addComponent("CO2", 2.0)
gas.addComponent("nitrogen", 1.0)
gas.setMixingRule("classic")

Stream = jneqsim.process.equipment.stream.Stream
Compressor = jneqsim.process.equipment.compressor.Compressor
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# Sweep flow rates to simulate speed variation effects
flow_rates = np.linspace(15000, 60000, 10)  # kg/hr
powers = []
efficiencies = []

for flow in flow_rates:
    fluid = gas.clone()
    f = Stream("Feed", fluid)
    f.setFlowRate(float(flow), "kg/hr")
    f.setTemperature(30.0, "C")
    f.setPressure(10.0, "bara")

    c = Compressor("Comp", f)
    c.setOutletPressure(30.0)
    c.setPolytropicEfficiency(0.80)
    c.setUsePolytropicCalc(True)

    p = ProcessSystem()
    p.add(f)
    p.add(c)
    p.run()

    powers.append(c.getPower() / 1e3)  # kW
    efficiencies.append(c.getPolytropicEfficiency() * 100)

# Theoretical cubic law reference
flow_norm = np.array(flow_rates) / flow_rates[5]
power_cubic = powers[5] * flow_norm**3

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.plot(flow_rates/1000, powers, 'bo-', linewidth=2, markersize=6,
         label='NeqSim calculation')
ax1.plot(flow_rates/1000, power_cubic, 'r--', linewidth=1.5,
         label='Cubic law (affinity)')
ax1.set_xlabel("Mass Flow Rate (t/hr)", fontsize=12)
ax1.set_ylabel("Compressor Power (kW)", fontsize=12)
ax1.set_title("Power vs. Flow Rate", fontsize=14)
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3)

ax2.plot(flow_rates/1000, efficiencies, 'gs-', linewidth=2, markersize=6)
ax2.set_xlabel("Mass Flow Rate (t/hr)", fontsize=12)
ax2.set_ylabel("Polytropic Efficiency (%)", fontsize=12)
ax2.set_title("Efficiency vs. Flow Rate", fontsize=14)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("figures/compressor_speed_sensitivity.png", dpi=150,
            bbox_inches="tight")
plt.show()
```

![Compressor power and efficiency vs. flow rate](figures/compressor_speed_sensitivity.png)

*Figure 14.3: Compressor power (left) and efficiency (right) vs. mass flow rate. The blue markers show NeqSim real-gas calculations; the red dashed line shows the theoretical cubic affinity law scaling. At fixed polytropic efficiency, power scales linearly with mass flow (at constant pressure ratio), while with performance curves and speed variation, the cubic law dominates.*

## 14.15 Integration with Production Optimization Framework

### 14.15.1 Compressors as Production Bottlenecks

In a declining field, the compressor is often the first equipment to reach capacity. As wellhead pressure drops:

1. The suction pressure to the first-stage compressor decreases
2. The pressure ratio per stage increases (assuming fixed discharge pressure)
3. The required head per stage increases
4. The volumetric flow at suction conditions increases (same mass flow, lower density)
5. Eventually, the compressor hits one of its limits: maximum speed, maximum power, or surge

The production rate must then be reduced to keep the compressor within its operating envelope. This is the production bottleneck.

### 14.15.2 Identifying the Binding Constraint

The `ProductionOptimizer` in NeqSim automatically identifies which compressor constraint is binding at the maximum production rate:

```python
ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer
optimizer = ProductionOptimizer()
result = optimizer.optimizeThroughput(process, feed, 10000.0, 60000.0, "kg/hr", None)
print("Feasible:", result.isFeasible(), "Rate (kg/hr):", result.getOptimalRate())
print(ProductionOptimizer.formatUtilizationTable(result.getUtilizationRecords()))
```

### 14.15.3 Compressor Upgrade Analysis

A common production optimization study evaluates the benefit of compressor upgrades:

| Upgrade Option | NeqSim Approach | Typical Benefit |
|---------------|-----------------|-----------------|
| Increased speed (VFD) | Increase `setMaximumSpeed()` | 10–20% more flow |
| Re-wheel (new impellers) | Increase polytropic efficiency | 3–5% power reduction |
| Additional stage | Add compressor to `ProcessSystem` | Extends plateau 2–5 years |
| Driver upgrade | Increase `setMaximumPower()` | Removes power bottleneck |
| Parallel compressor | Add second compressor in parallel | Doubles capacity |

Each option is modeled by modifying the compressor parameters in NeqSim and re-running the optimizer to determine the new maximum production rate and the incremental oil/gas recovery.

## Exercises

**Exercise 14.1**: Calculate the isentropic and polytropic efficiency for a compressor with suction at 30°C, 10 bara and discharge at 125°C, 30 bara. The gas is methane ($\gamma = 1.31$).

**Exercise 14.2**: Design a 2-stage compression system with intercooling to compress 10,000 kg/hr of natural gas from 3 bara to 40 bara. Use NeqSim to calculate the power, discharge temperatures, and intercooler duties. Compare with the ideal gas calculations.

**Exercise 14.3**: For the 3-stage recompression train in Section 14.8.2, investigate the effect of intercooling temperature on total power. Plot total power vs. intercooler outlet temperature for temperatures from 20°C to 60°C.

**Exercise 14.4**: Compare the compression power for lean gas ($\text{MW} = 18$), medium gas ($\text{MW} = 22$), and rich gas ($\text{MW} = 26$) at the same mass flow rate and pressure ratio. Explain the results in terms of the polytropic head equation.

**Exercise 14.5**: Calculate the fuel gas consumption (in Sm$^3$/hr and MW thermal) for a gas turbine driving a 15 MW compressor, assuming gas turbine efficiency of 33% and fuel gas LHV of 48 MJ/kg.

**Exercise 14.6**: Design an anti-surge system for a centrifugal compressor with a design flow of 50,000 m$^3$/hr (actual) at 10 bara suction and 30 bara discharge. The surge flow is 60% of design flow. Calculate the recycle rate required to maintain a 10% surge margin at 50% turndown.

**Exercise 14.7**: A platform requires 3 MW of recompression power. Compare the total system efficiency (gas-in to compressed-gas-out) for: (a) gas turbine drive using platform fuel gas, (b) electric motor drive powered by an on-site gas turbine generator, (c) electric motor drive with shore power. Include all conversion losses.

## References

1. Brown, R.N. (2005). *Compressors: Selection and Sizing*, 3rd ed. Gulf Professional Publishing.
2. API Standard 617 (2022). Axial and Centrifugal Compressors and Expander-Compressors, 8th ed. American Petroleum Institute.
3. Bloch, H.P. (2006). *A Practical Guide to Compressor Technology*, 2nd ed. John Wiley & Sons.
4. Schultz, J.M. (1962). The polytropic analysis of centrifugal compressors. *Journal of Engineering for Power*, 84(1), 69–82.
5. Sandberg, M.R. and Colby, G.M. (2013). Limitations of ASME PTC 10 in accurately evaluating centrifugal compressor thermodynamic performance. *Proceedings of the 42nd Turbomachinery Symposium*, Texas A&M.
6. GPSA Engineering Data Book (2004). 12th ed. Gas Processors Suppliers Association.
7. Campbell, J.M. (2014). *Gas Conditioning and Processing, Vol. 2*, 9th ed. Campbell Petroleum Series.
8. Boyce, M.P. (2012). *Gas Turbine Engineering Handbook*, 4th ed. Butterworth-Heinemann.
9. Bloch, H.P. and Soares, C. (1998). *Process Plant Machinery*, 2nd ed. Butterworth-Heinemann.
10. NORSOK P-002 (2014). Process System Design. Standards Norway.
11. ISO 5389 (2005). Turbocompressors — Performance test code. International Organization for Standardization.


## Figures

![Figure 14.1: Fig12 1 Power Vs Ratio](figures/fig12_1_power_vs_ratio.png)

*Figure 14.1: Fig12 1 Power Vs Ratio*

![Figure 14.2: Fig12 2 Compressor Curve](figures/fig12_2_compressor_curve.png)

*Figure 14.2: Fig12 2 Compressor Curve*

![Figure 14.3: Fig12 3 Multistage Profile](figures/fig12_3_multistage_profile.png)

*Figure 14.3: Fig12 3 Multistage Profile*

![Figure 14.4: Fig12 4 Power Comparison](figures/fig12_4_power_comparison.png)

*Figure 14.4: Fig12 4 Power Comparison*

![Figure 14.5: Fig12 5 Discharge Temperature](figures/fig12_5_discharge_temperature.png)

*Figure 14.5: Fig12 5 Discharge Temperature*
