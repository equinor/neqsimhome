
# Subsea Production Systems

<!-- Chapter metadata -->
<!-- Notebooks: ch06_subsea_tieback_analysis.ipynb, ch06_subsea_boosting.ipynb -->
<!-- Estimated pages: 20 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Describe the major components of a subsea production system and their functions
2. Explain the pressure and temperature constraints that govern subsea field development
3. Compare subsea vs. dry tree completion strategies for offshore fields
4. Model subsea wells and flowlines using NeqSim's subsea classes
5. Estimate SURF (Subsea, Umbilicals, Risers, Flowlines) costs for concept screening
6. Evaluate subsea processing options including boosting, separation, and compression
7. Optimize field layout by analyzing tieback distances and pressure budgets

## 7.1 Introduction to Subsea Production

Subsea production systems enable the exploitation of offshore hydrocarbon reservoirs by placing wellheads, flow control equipment, and increasingly sophisticated processing equipment on the seabed. Since the first commercial subsea completion was installed in the Gulf of Mexico in 1961, the technology has evolved dramatically — modern subsea systems operate in water depths exceeding 3,000 meters with tieback distances of over 100 kilometers.

The fundamental advantage of subsea production is economic: rather than building a fixed or floating platform above every well cluster, subsea systems tie remote wells back to an existing host facility or an onshore plant. This shared infrastructure model dramatically reduces the capital investment required to develop marginal or remote fields.

However, subsea production introduces engineering challenges that do not arise with conventional dry tree completions:

- **Pressure loss** in long flowlines and risers reduces the natural driving force for production
- **Temperature loss** along the seabed exposes the produced fluid to hydrate, wax, and slug flow risks
- **Intervention difficulty** makes reliability and design margins critical — a failed subsea component may require a vessel costing \$500,000/day to repair
- **Flow assurance** challenges are more severe due to cold seabed temperatures and long transport distances

This chapter examines the architecture, design, and optimization of subsea production systems, with NeqSim providing the computational tools for pressure-temperature analysis, tieback feasibility studies, and cost estimation.

![Overview of a subsea production system showing wells, trees, manifolds, flowlines, and host facility](figures/subsea_system_overview.png)

## 7.2 Subsea Architecture and Components

### 7.2.1 Subsea Christmas Trees

The subsea tree (also known as a Christmas tree or wet tree) is the primary well control device installed on the seabed. It sits atop the wellhead and provides:

- **Flow control** — master valves and wing valves regulate production
- **Well shut-in** — fail-safe closed valves for emergency and planned shutdowns
- **Chemical injection points** — for hydrate inhibitor, corrosion inhibitor, and scale inhibitor injection
- **Monitoring** — pressure and temperature sensors for well surveillance
- **Intervention access** — through-bore access for wireline or coiled tubing operations

Two main configurations exist:

| Feature | Vertical Tree | Horizontal Tree |
|---------|--------------|-----------------|
| Master valve orientation | Vertical bore | Horizontal bore |
| Tubing hanger location | In the tree | In the wellhead |
| Tree retrieval | Requires tubing pull | Independent of tubing |
| Bore access | Through tree | Through tree cap |
| Typical application | Moderate depth | Deepwater, HP/HT |
| Well intervention | More complex | Simpler |
| Cost (typical) | \$15–25M | \$20–35M |

Horizontal trees have become the standard for deepwater developments because they allow the tree to be installed and retrieved independently of the tubing string, simplifying intervention operations.

### 7.2.2 Subsea Manifolds

A subsea manifold collects production from multiple wells and routes it into a common flowline. Key design parameters include:

- **Number of slots** — typically 4 to 8 well connections
- **Pressure rating** — matched to the maximum shut-in tubing head pressure (SITHP)
- **Bore size** — determines flow capacity; typically 4" to 6" production bores
- **Valve configuration** — individual well isolation and crossover capability
- **Weight and footprint** — affects installation vessel requirements

Manifolds enable the commingling of production, reducing the number of flowlines required from the subsea field to the host. For example, a field with 12 wells and two 6-slot manifolds requires only 2 production flowlines rather than 12 individual well flowlines.

### 7.2.3 Templates and Foundations

Subsea templates are structural frames installed on the seabed to guide the positioning of wells, trees, and manifolds. Templates provide:

- **Well slot positioning** — precise spacing for drilling and completion
- **Structural support** — for trees, manifolds, and jumpers
- **Mudmat or suction anchor foundations** — resist lateral and vertical loads
- **Pipeline end terminations (PLETs)** — connection points for flowlines

Template design must account for seabed soil conditions, current loads, installation tolerances, and the weight of installed equipment. A typical 4-slot template weighs 300–600 tonnes.

### 7.2.4 Jumpers and Connections

Jumpers are short pipe sections that connect subsea trees to manifolds, or manifolds to flowlines. They accommodate installation tolerances and thermal expansion:

- **Rigid jumpers** — steel pipe, typically 6"–10" diameter, with mechanical connectors
- **Flexible jumpers** — multi-layered flexible pipe, used where large deflections are expected
- **Typical length** — 20 to 100 meters

Connection systems include:

| Connection Type | Application | Advantages |
|----------------|-------------|------------|
| Mechanical (clamp) | Tree to jumper | Diver or ROV installable |
| Collet connector | Flowline to PLET | High-integrity metal seal |
| Hydraulic (MQC) | Manifold to tree | Rapid make/break |
| Weld | Flowline to PLET | Highest integrity |

### 7.2.5 Umbilicals

Umbilicals are composite cables that deliver hydraulic fluid, electrical power, chemical injection, and communication signals from the host facility to subsea equipment. A modern umbilical typically contains:

- **Hydraulic lines** — for valve actuation (LP and HP supply), typically 2–4 tubes
- **Electrical conductors** — for power supply and signal transmission
- **Chemical injection tubes** — for MEG, methanol, corrosion inhibitor, scale inhibitor
- **Fiber optic cables** — for high-bandwidth communication and distributed sensing

Umbilical design is critical for long tieback distances. The hydraulic response time — the time for a pressure signal to travel from the host to a subsea valve — increases with distance and can exceed 30 minutes for tiebacks longer than 50 km, affecting emergency shutdown response times.

![Typical subsea field layout showing trees, manifold, flowlines, umbilical, and riser connection to FPSO](figures/subsea_field_layout.png)

## 7.3 Subsea vs. Dry Tree Completions

The choice between subsea (wet tree) and dry tree completions is one of the most consequential decisions in offshore field development. It affects capital cost, operating cost, production efficiency, intervention frequency, and ultimately recovery factor.

### 7.3.1 Dry Tree Platforms

Dry tree completions place the wellheads on the platform deck, providing direct access for wireline, coiled tubing, and workover operations. Platform types that support dry trees include:

- **Fixed platforms** — jacket or gravity-based structures in shallow water (< 300 m)
- **Compliant towers** — for moderate water depths (300–600 m)
- **Tension Leg Platforms (TLPs)** — taut-moored for deepwater (500–1,500 m)
- **Spars** — deep-draft cylindrical hulls (500–2,500 m)

The primary advantage of dry trees is well access. Wireline and coiled tubing operations that cost \$200,000 and take 2 days from a platform may cost \$5,000,000 and take 3 weeks from a subsea intervention vessel.

### 7.3.2 Decision Criteria

| Factor | Favors Subsea | Favors Dry Tree |
|--------|--------------|-----------------|
| Water depth > 1,500 m | ✓ | |
| Small/marginal field | ✓ | |
| Satellite development | ✓ | |
| High intervention frequency | | ✓ |
| HP/HT reservoir | | ✓ (easier access) |
| Remote location | ✓ (tieback to existing host) | |
| Long field life (> 25 years) | | ✓ |
| Harsh metocean conditions | ✓ (equipment protected on seabed) | |

### 7.3.3 Impact on Recovery Factor

Industry data suggests that dry tree completions achieve recovery factors 3–8% higher than subsea completions for the same reservoir, primarily because:

- More frequent well intervention enables better reservoir management
- Easier installation of artificial lift (gas lift, ESPs)
- Lower wellhead back-pressure (no long flowlines)
- More production/injection wells can be economically justified

This recovery factor difference must be weighed against the capital cost difference, which often favors subsea for smaller fields or tiebacks to existing infrastructure.

## 7.4 Pressure and Temperature Constraints

### 7.4.1 The Pressure Budget

The pressure budget is the fundamental framework for subsea system design. It traces the available pressure from the reservoir to the first-stage separator:

$$
P_{res} = P_{sep} + \Delta P_{IPR} + \Delta P_{tubing} + \Delta P_{choke} + \Delta P_{flowline} + \Delta P_{riser}
$$

where:

- $P_{res}$ is the average reservoir pressure [bara]
- $P_{sep}$ is the first-stage separator pressure [bara]
- $\Delta P_{IPR}$ is the pressure drop across the reservoir (inflow performance) [bar]
- $\Delta P_{tubing}$ is the tubing pressure loss from bottomhole to tree [bar]
- $\Delta P_{choke}$ is the choke pressure drop [bar]
- $\Delta P_{flowline}$ is the subsea flowline pressure loss [bar]
- $\Delta P_{riser}$ is the riser pressure loss (including hydrostatic head) [bar]

At the start of field life, when reservoir pressure is high, the pressure budget has significant margin. As the reservoir depletes, the available driving pressure decreases, and the flowline and riser pressure drops become an increasing fraction of the total. Eventually, the natural driving force is insufficient and artificial lift or subsea boosting is required.

### 7.4.2 Temperature Constraints

Temperature management is equally critical in subsea systems:

- **Hydrate formation** — if the fluid temperature drops below the hydrate equilibrium temperature at the flowing pressure, solid hydrates can form and block the flowline
- **Wax deposition** — if the temperature drops below the wax appearance temperature (WAT), wax crystals nucleate and deposit on pipe walls
- **Arrival temperature** — the topside process requires a minimum arrival temperature for effective separation and hydrate prevention
- **Cooldown time** — during an unplanned shutdown, the fluid in the flowline cools toward the seabed temperature; the time to reach the hydrate formation temperature is the available time for remediation

The temperature profile along a subsea flowline depends on:

$$
T(x) = T_{sea} + (T_{inlet} - T_{sea}) \cdot e^{-\frac{\pi D U x}{\dot{m} C_p}}
$$

where:

- $T(x)$ is the fluid temperature at distance $x$ along the flowline [K]
- $T_{sea}$ is the seabed temperature [K]
- $T_{inlet}$ is the inlet temperature [K]
- $D$ is the pipe outer diameter [m]
- $U$ is the overall heat transfer coefficient [W/m²·K]
- $\dot{m}$ is the mass flow rate [kg/s]
- $C_p$ is the specific heat capacity [J/kg·K]

### 7.4.3 NeqSim Pressure-Temperature Analysis

NeqSim's `PipeBeggsAndBrills` class calculates both pressure and temperature profiles along subsea flowlines and risers:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define a typical subsea production fluid
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 70.0, 200.0)
fluid.addComponent("nitrogen", 0.8)
fluid.addComponent("CO2", 3.5)
fluid.addComponent("methane", 65.0)
fluid.addComponent("ethane", 8.5)
fluid.addComponent("propane", 5.0)
fluid.addComponent("i-butane", 1.0)
fluid.addComponent("n-butane", 2.5)
fluid.addComponent("i-pentane", 1.0)
fluid.addComponent("n-pentane", 1.5)
fluid.addComponent("n-hexane", 2.0)
fluid.addComponent("n-heptane", 4.0)
fluid.addComponent("n-octane", 3.0)
fluid.addComponent("water", 2.2)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

# Create feed stream at wellhead conditions
Stream = jneqsim.process.equipment.stream.Stream
wellstream = Stream("Subsea Wellstream", fluid)
wellstream.setFlowRate(80000.0, "kg/hr")
wellstream.setTemperature(70.0, "C")
wellstream.setPressure(180.0, "bara")

# Model 15 km subsea flowline
PipeBeggsAndBrills = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills
flowline = PipeBeggsAndBrills("Subsea Flowline", wellstream)
flowline.setPipeWallRoughness(5.0e-5)
flowline.setLength(15000.0)           # m (15 km)
flowline.setElevation(0.0)         # horizontal
flowline.setDiameter(0.254)        # 10-inch ID in meters
flowline.setNumberOfIncrements(50)
flowline.setConstantSurfaceTemperature(277.15)  # 4°C seabed temperature

# Build and run
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
process = ProcessSystem()
process.add(wellstream)
process.add(flowline)
process.run()

# Read arrival conditions
arrival_T = flowline.getOutletStream().getTemperature("C")
arrival_P = flowline.getOutletStream().getPressure("bara")
delta_P = wellstream.getPressure("bara") - arrival_P
print(f"Arrival temperature: {arrival_T:.1f} °C")
print(f"Arrival pressure: {arrival_P:.1f} bara")
print(f"Pressure drop: {delta_P:.1f} bar")
```

## 7.5 Tieback Distance Analysis

### 7.5.1 Maximum Tieback Distance

The maximum tieback distance is determined by the intersection of three constraints:

1. **Pressure constraint** — the available pressure drop in the flowline (total pressure budget minus tubing, choke, and riser losses) limits distance
2. **Temperature constraint** — the arrival temperature must remain above the hydrate equilibrium temperature (with safety margin) or the WAT
3. **Cooldown constraint** — the time for the fluid to cool below the hydrate temperature during a shutdown must exceed the minimum intervention time

For a given set of operating conditions, the maximum tieback distance is:

$$
L_{max} = \min\left(L_{max,\Delta P}, \, L_{max,T_{arr}}, \, L_{max,t_{cool}}\right)
$$

### 7.5.2 Tieback Feasibility Study with NeqSim

A tieback feasibility study systematically evaluates production rate and arrival conditions over a range of flowline lengths:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import json

# Fluid definition (as above - reused from Section 7.4.3)
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 70.0, 200.0)
fluid.addComponent("nitrogen", 0.8)
fluid.addComponent("CO2", 3.5)
fluid.addComponent("methane", 65.0)
fluid.addComponent("ethane", 8.5)
fluid.addComponent("propane", 5.0)
fluid.addComponent("i-butane", 1.0)
fluid.addComponent("n-butane", 2.5)
fluid.addComponent("i-pentane", 1.0)
fluid.addComponent("n-pentane", 1.5)
fluid.addComponent("n-hexane", 2.0)
fluid.addComponent("n-heptane", 4.0)
fluid.addComponent("n-octane", 3.0)
fluid.addComponent("water", 2.2)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

Stream = jneqsim.process.equipment.stream.Stream
PipeBeggsAndBrills = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# Parametric study: vary tieback distance
distances_km = [5, 10, 15, 20, 30, 40, 50]
results = []

for dist in distances_km:
    test_fluid = fluid.clone()
    feed = Stream("Feed", test_fluid)
    feed.setFlowRate(80000.0, "kg/hr")
    feed.setTemperature(70.0, "C")
    feed.setPressure(180.0, "bara")

    pipe = PipeBeggsAndBrills("Flowline", feed)
    pipe.setPipeWallRoughness(5.0e-5)
    pipe.setLength(float(dist) * 1000.0)
    pipe.setElevation(0.0)
    pipe.setDiameter(0.254)
    pipe.setNumberOfIncrements(50)
    pipe.setConstantSurfaceTemperature(277.15)

    proc = ProcessSystem()
    proc.add(feed)
    proc.add(pipe)
    proc.run()

    arrival_T = pipe.getOutletStream().getTemperature("C")
    arrival_P = pipe.getOutletStream().getPressure("bara")
    results.append({
        "distance_km": dist,
        "arrival_T_C": round(arrival_T, 1),
        "arrival_P_bara": round(arrival_P, 1),
        "dP_bar": round(180.0 - arrival_P, 1)
    })

# Print results table
print(f"{'Distance (km)':>14} {'Arrival T (°C)':>15} {'Arrival P (bara)':>17} {'dP (bar)':>10}")
for r in results:
    print(f"{r['distance_km']:>14} {r['arrival_T_C']:>15.1f} {r['arrival_P_bara']:>17.1f} {r['dP_bar']:>10.1f}")
```

![Arrival temperature and pressure vs. tieback distance for the reference case](figures/tieback_distance_analysis.png)

### 7.5.3 Typical Tieback Distances

Industry experience provides benchmarks for achievable tieback distances:

| Fluid Type | Typical Max Distance (uninsulated) | With Insulation | With Boosting |
|-----------|-----------------------------------|-----------------|---------------|
| Dry gas | 80–150 km | 150–200 km | > 200 km |
| Wet gas / condensate | 30–60 km | 50–80 km | 80–120 km |
| Light oil (GOR > 200) | 20–40 km | 30–50 km | 50–80 km |
| Heavy/waxy oil | 5–15 km | 10–25 km | 25–50 km |

These distances assume typical pipe sizes (8"–14"), seabed temperatures of 2–5°C, and host separator pressures of 20–40 bara.

## 7.6 Subsea Processing

### 7.6.1 Motivation for Subsea Processing

Subsea processing addresses the declining pressure budget as reservoirs deplete. By placing processing equipment — pumps, separators, or compressors — on the seabed, the effective tieback distance is extended and production is maintained longer without topside modifications.

The key drivers for subsea processing are:

- **Pressure boosting** — adds energy to overcome flowline friction and riser hydrostatic head
- **Separation** — removes water or gas on the seabed to reduce flowline hydraulic load
- **Gas compression** — compresses gas to maintain delivery pressure as reservoir pressure declines
- **Sand management** — removes sand before it enters flowlines

### 7.6.2 Subsea Boosting (Multiphase Pumps)

Subsea multiphase pumps are the most widely deployed form of subsea processing. They boost the total well stream — gas, oil, and water — without prior separation. Key technologies include:

| Technology | Principle | Typical dP | GVF Tolerance |
|-----------|-----------|------------|---------------|
| Helico-axial (Framo) | Axial impellers with helical design | 30–100 bar | Up to 95% |
| Twin-screw (Leistritz) | Positive displacement screw pump | 20–80 bar | Up to 100% |
| Counter-rotating axial | Counter-rotating impeller stages | 20–60 bar | Up to 90% |

Subsea boosting has been commercially proven on multiple Norwegian Continental Shelf (NCS) fields including Åsgard (2015), Gullfaks (2015), and Vigdis (2007).

### 7.6.3 Subsea Separation

Subsea separation separates the produced fluid into gas and liquid phases on the seabed. The separated streams are transported in dedicated flowlines:

- **Gas** — flows to the host at higher velocity but lower frictional loss per unit mass
- **Liquid** — can be boosted by a less complex liquid pump

The Tordis subsea separation system (installed 2007) demonstrated subsea separation and water reinjection, removing water on the seabed and reinjecting it into a disposal well, reducing the hydraulic load on the flowline and topside produced water treatment.

### 7.6.4 Subsea Wet Gas Compression

Subsea wet gas compression is the most technically challenging form of subsea processing. The Åsgard subsea compression system (2015) was the world's first installation, compressing wet gas (gas with entrained liquid droplets) on the seabed at 300 m water depth.

Key design challenges include:

- Liquid handling in compressor impellers
- Anti-surge control without fast-acting recycle valves
- Long-distance electrical power supply (up to 600 MW at 36 kV)
- Reliability requirements (5+ year uninterrupted operation target)

### 7.6.5 Modeling Subsea Boosting with NeqSim

The effect of subsea boosting on production can be modeled by inserting a pressure increase between the flowline and riser:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define fluid
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 60.0, 150.0)
fluid.addComponent("methane", 72.0)
fluid.addComponent("ethane", 8.0)
fluid.addComponent("propane", 5.0)
fluid.addComponent("n-butane", 2.5)
fluid.addComponent("n-pentane", 1.5)
fluid.addComponent("n-hexane", 2.0)
fluid.addComponent("n-heptane", 3.0)
fluid.addComponent("n-octane", 2.5)
fluid.addComponent("water", 3.5)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

Stream = jneqsim.process.equipment.stream.Stream
PipeBeggsAndBrills = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills
Compressor = jneqsim.process.equipment.compressor.Compressor
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# Wellhead stream
wellstream = Stream("Wellstream", fluid)
wellstream.setFlowRate(60000.0, "kg/hr")
wellstream.setTemperature(60.0, "C")
wellstream.setPressure(120.0, "bara")

# Subsea flowline (30 km)
flowline = PipeBeggsAndBrills("Subsea Flowline", wellstream)
flowline.setPipeWallRoughness(5.0e-5)
flowline.setLength(30000.0)
flowline.setElevation(0.0)
flowline.setDiameter(0.254)
flowline.setNumberOfIncrements(50)
flowline.setConstantSurfaceTemperature(277.15)

# Subsea booster (modeled as a compressor for pressure increase)
booster = Compressor("Subsea Booster", flowline.getOutletStream())
booster.setOutletPressure(100.0)  # boost back up to 100 bara

# Riser (500 m water depth, vertical)
riser = PipeBeggsAndBrills("Riser", booster.getOutletStream())
riser.setPipeWallRoughness(5.0e-5)
riser.setLength(600.0)       # ~600 m riser length
riser.setElevation(500.0)  # 500 m water depth
riser.setDiameter(0.254)
riser.setNumberOfIncrements(20)
riser.setConstantSurfaceTemperature(280.15)

# Build process
process = ProcessSystem()
process.add(wellstream)
process.add(flowline)
process.add(booster)
process.add(riser)
process.run()

# Results
topside_P = riser.getOutletStream().getPressure("bara")
topside_T = riser.getOutletStream().getTemperature("C")
booster_power = booster.getPower("kW")
print(f"Topside arrival pressure: {topside_P:.1f} bara")
print(f"Topside arrival temperature: {topside_T:.1f} °C")
print(f"Subsea booster power: {booster_power:.0f} kW")
```

## 7.7 Subsea Well Design with NeqSim

### 7.7.1 The SubseaWell Class

NeqSim provides the `SubseaWell` class for modeling subsea well completions, including mechanical design calculations per API 5C3 and NORSOK D-010:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Create a production fluid
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 90.0, 350.0)
fluid.addComponent("methane", 70.0)
fluid.addComponent("ethane", 8.0)
fluid.addComponent("propane", 5.0)
fluid.addComponent("n-butane", 2.0)
fluid.addComponent("n-pentane", 1.5)
fluid.addComponent("n-heptane", 5.0)
fluid.addComponent("n-octane", 3.5)
fluid.addComponent("water", 5.0)
fluid.setMixingRule("classic")

Stream = jneqsim.process.equipment.stream.Stream
stream = Stream("Well Stream", fluid)
stream.setFlowRate(50000.0, "kg/hr")
stream.setTemperature(90.0, "C")
stream.setPressure(250.0, "bara")
stream.run()

# Create subsea well
SubseaWell = jneqsim.process.equipment.subsea.SubseaWell
well = SubseaWell("Producer-1", stream)
well.setWellType(SubseaWell.WellType.OIL_PRODUCER)
well.setMeasuredDepth(3800.0)           # Total measured depth [m]
well.setWaterDepth(350.0)               # Water depth [m]
well.setMaxWellheadPressure(345.0)      # Maximum WHSP [bara]
well.setReservoirPressure(400.0)        # Initial reservoir pressure [bara]
well.setProductionCasingOD(9.625)       # 9-5/8" casing
well.setProductionCasingDepth(3800.0)   # Casing set depth [m]
well.setTubingOD(5.5)                   # 5-1/2" tubing
well.setTubingWeight(23.0)              # lb/ft
well.setTubingGrade("L80")             # API 5CT grade
well.setHasDHSV(True)                   # Downhole safety valve
well.setPrimaryBarrierElements(3)       # NORSOK D-010
well.setSecondaryBarrierElements(3)     # NORSOK D-010
well.setDrillingDays(45.0)             # Drilling duration
well.setCompletionDays(25.0)           # Completion duration

# Run mechanical design
well.initMechanicalDesign()
WellMechanicalDesign = jneqsim.process.mechanicaldesign.subsea.WellMechanicalDesign
design = well.getMechanicalDesign()
design.calcDesign()
design.calculateCostEstimate()

# Print results
json_output = design.toJson()
print(json_output)
```

### 7.7.2 Casing Design per API 5C3

The mechanical design calculation follows API Bull 5C3 for casing strength:

**Burst rating:**

$$
P_{burst} = \frac{0.875 \times 2 \times Y_p \times t}{D_o}
$$

**Collapse rating** (for the yield strength collapse regime):

$$
P_{collapse} = 2 \times Y_p \left(\frac{D_o/t - 1}{(D_o/t)^2}\right)
$$

**Tension rating:**

$$
F_{tension} = Y_p \times A_s
$$

where:

- $Y_p$ is the minimum yield strength [psi]
- $t$ is the wall thickness [in]
- $D_o$ is the outer diameter [in]
- $A_s$ is the cross-sectional area of the pipe body [in²]

Design factors per NORSOK D-010:

| Load Case | Design Factor |
|-----------|--------------|
| Burst (production casing) | 1.10 |
| Collapse (production casing) | 1.10 |
| Tension | 1.30 |
| Triaxial (VME) | 1.25 |

## 7.8 SURF Cost Estimation

### 7.8.1 Cost Components

SURF (Subsea, Umbilicals, Risers, Flowlines) costs typically represent 30–50% of the total development cost for a subsea field. The main cost components are:

| Component | Typical Cost Range | Key Cost Drivers |
|----------|-------------------|------------------|
| Subsea trees | \$15–35M each | Pressure rating, bore size, controls |
| Manifold | \$25–60M each | Number of slots, pressure rating |
| Flowlines | \$1,500–5,000/m | Diameter, insulation, installation method |
| Umbilicals | \$200–1,000/m | Number of cores, length |
| Risers (flexible) | \$3,000–8,000/m | Diameter, water depth |
| Risers (steel catenary) | \$2,000–5,000/m | Diameter, fatigue design |
| Installation | 30–60% of hardware | Vessel day rates, weather |

### 7.8.2 Cost Estimation Approach

NeqSim's `WellMechanicalDesign` class includes parametric cost estimation for subsea wells. For the complete SURF cost, a structured estimation approach combines well costs with infrastructure costs:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Subsea field parameters
n_wells = 6
n_manifolds = 2
flowline_length_km = 20.0
umbilical_length_km = 22.0
riser_length_m = 400.0
water_depth_m = 350.0

# Parametric cost estimates (MNOK, 2024 basis)
tree_cost = 25.0      # per tree
manifold_cost = 40.0   # per manifold
flowline_cost_per_km = 15.0   # includes installation
umbilical_cost_per_km = 8.0
riser_cost_per_m = 0.005      # flexible riser

# Calculate SURF cost
surf_cost = (
    n_wells * tree_cost +
    n_manifolds * manifold_cost +
    flowline_length_km * flowline_cost_per_km +
    umbilical_length_km * umbilical_cost_per_km +
    riser_length_m * riser_cost_per_m * 2  # production + gas lift
)

print(f"Subsea trees:   {n_wells * tree_cost:.0f} MNOK")
print(f"Manifolds:      {n_manifolds * manifold_cost:.0f} MNOK")
print(f"Flowlines:      {flowline_length_km * flowline_cost_per_km:.0f} MNOK")
print(f"Umbilicals:     {umbilical_length_km * umbilical_cost_per_km:.0f} MNOK")
print(f"Risers:         {riser_length_m * riser_cost_per_m * 2:.0f} MNOK")
print(f"Total SURF:     {surf_cost:.0f} MNOK")
```

### 7.8.3 Cost Sensitivity

The dominant cost drivers for SURF systems are:

- **Water depth** — affects riser length, installation vessel requirements, and equipment ratings
- **Tieback distance** — flowline and umbilical costs scale linearly with distance
- **Number of wells** — each well requires a tree, connections, and control system
- **Pipe diameter** — larger pipes cost more per meter but may enable higher production
- **Insulation** — wet insulation (syntactic foam) adds \$500–2,000/m; pipe-in-pipe adds \$2,000–5,000/m

![SURF cost breakdown for a typical deepwater subsea development](figures/surf_cost_breakdown.png)

## 7.9 Field Layout Optimization

### 7.9.1 Layout Considerations

The subsea field layout — the spatial arrangement of wells, manifolds, flowlines, and risers — affects both capital cost and production performance:

- **Well spacing** — too close risks interference; too far increases jumper lengths
- **Manifold location** — should minimize total jumper and flowline lengths
- **Flowline routing** — must avoid geohazards, existing infrastructure, and excessive free spans
- **Riser connection** — the point where the flowline transitions to a riser affects both cost and flow assurance

### 7.9.2 Optimization Approach

Field layout optimization is typically a multi-objective problem:

$$
\min_{x} \left[ C_{SURF}(x), \, -Q_{prod}(x), \, R_{flow\text{-}assurance}(x) \right]
$$

where $x$ is the vector of layout variables (well positions, manifold locations, pipe routes), $C_{SURF}$ is the SURF cost, $Q_{prod}$ is the total production, and $R$ is a flow assurance risk metric.

In practice, the optimization is performed in stages:
1. **Reservoir-driven well placement** — optimized by reservoir engineers for drainage
2. **Manifold clustering** — group wells into manifold clusters to minimize inter-connections
3. **Routing and sizing** — optimize pipe routes, diameters, and insulation levels
4. **Flow assurance verification** — confirm the layout meets hydrate, wax, and slugging criteria

## 7.10 Subsea Coolers and Subsea Processing Integration

In some fields, particularly those with high reservoir temperatures or gas condensate fluids, a subsea cooler may be installed to reduce the fluid temperature before entering long flowlines. The reduced temperature decreases the specific volume of the gas phase, reducing velocity and friction pressure drop.

However, subsea cooling must be balanced against flow assurance risks — lower temperatures bring the fluid closer to hydrate and wax formation conditions. The optimal subsea cooler exit temperature is typically:

$$
T_{cooler,out} = T_{hydrate}(P_{cooler,out}) + \Delta T_{margin}
$$

where $\Delta T_{margin}$ is a safety margin, typically 5–10°C above the hydrate equilibrium temperature.

## 7.11 NeqSim Implementation Summary

The key NeqSim classes used for subsea production system analysis are:

| NeqSim Class | Application |
|-------------|-------------|
| `SubseaWell` | Subsea well definition, completion parameters |
| `WellMechanicalDesign` | Casing design (API 5C3), barrier verification (NORSOK D-010), cost estimation |
| `PipeBeggsAndBrills` | Multiphase flow in flowlines and risers |
| `Stream` | Define wellhead and arrival conditions |
| `Compressor` | Model subsea boosting pressure increase |
| `Separator` | Topside separation (for pressure budget endpoint) |
| `ProcessSystem` | Compose the complete subsea-to-topside system |
| `ThermodynamicOperations` | Hydrate equilibrium calculations for flow assurance |

## 7.12 Summary

Key points from this chapter:

- Subsea production systems enable the development of offshore fields by placing wellheads and equipment on the seabed with tiebacks to host facilities
- The major components are subsea trees, manifolds, flowlines, risers, and umbilicals
- The pressure budget — from reservoir to separator — determines the maximum production rate and tieback distance
- Temperature management is critical to prevent hydrate and wax formation in subsea flowlines
- Subsea processing (boosting, separation, compression) extends field life and tieback distances
- NeqSim's `SubseaWell` and `PipeBeggsAndBrills` classes enable subsea system modeling
- SURF costs typically represent 30–50% of total subsea development costs and are dominated by flowline length and water depth
- Field layout optimization balances cost, production, and flow assurance objectives

## Exercises

1. **Exercise 7.1:** For the reference fluid in Section 7.4.3, calculate the pressure and temperature at the end of a 25 km subsea flowline for pipe diameters of 8", 10", and 12". Plot the results and identify the minimum acceptable diameter if the arrival temperature must be at least 20°C above the hydrate equilibrium temperature.

2. **Exercise 7.2:** Using the subsea well model in Section 7.7.1, modify the water depth from 350 m to 1,500 m and recalculate the well cost estimate. What is the approximate cost increase per meter of additional water depth?

3. **Exercise 7.3:** A subsea field has 8 wells producing a gas condensate fluid (GOR = 3,000 Sm³/Sm³). The water depth is 800 m and the distance to the host is 35 km. Using NeqSim, model the complete system (wells → manifold → flowline → riser → separator at 60 bara) and determine: (a) the total pressure drop, (b) the arrival temperature, (c) whether subsea boosting is needed.

4. **Exercise 7.4:** Perform a SURF cost estimate for the field in Exercise 7.3 using the parametric cost model in Section 7.8.2. Calculate the SURF cost for two alternative layouts: (a) one manifold with all 8 wells, and (b) two manifolds with 4 wells each connected by a gathering flowline.

5. **Exercise 7.5:** Repeat the tieback distance analysis in Section 7.5.2 with and without subsea boosting (50 bar pressure increase). Plot the additional distance achievable with boosting as a function of flowline diameter.

6. **Exercise 7.6:** Estimate the hydraulic response time for a subsea control system with a 60 km umbilical. Assume a 3/8" hydraulic tube, 345 bar working pressure, and standard hydraulic fluid. Discuss the implications for emergency shutdown system design.

## References

1. Bai, Y. and Bai, Q. (2019). *Subsea Engineering Handbook*, 2nd Edition. Gulf Professional Publishing.
2. Gudmestad, O.T. (2015). *Marine Technology and Operations: Theory & Practice*. WIT Press.
3. Zhen, L. and Songhurst, B. (2018). "Subsea processing: The next step in subsea field development." *Journal of Petroleum Technology*, 70(3), 44–52.
4. NORSOK D-010 (2021). *Well Integrity in Drilling and Well Operations*, Rev. 5. Standards Norway.
5. API Bull 5C3 (2008). *Bulletin on Formulas and Calculations for Casing, Tubing, Drill Pipe and Line Pipe Properties*. American Petroleum Institute.
6. DNV-RP-F101 (2019). *Corroded Pipelines*. Det Norske Veritas.
7. Sangesland, S. (2018). "Subsea well technology." Chapter in *Petroleum Production Engineering*, Elsevier.
8. Eriksson, K. and Høvik, J. (2017). "Subsea compression — technology development and qualification." *OTC*, Paper OTC-27893.

<!-- Chapter-level references are merged into master refs.bib -->


## Figures

![Figure 7.1: Fig01 Pressure Profile](figures/ch06_fig01_pressure_profile.png)

*Figure 7.1: Fig01 Pressure Profile*

![Figure 7.2: Fig02 Temperature Profile](figures/ch06_fig02_temperature_profile.png)

*Figure 7.2: Fig02 Temperature Profile*

![Figure 7.3: Fig03 Hydrate Risk](figures/ch06_fig03_hydrate_risk.png)

*Figure 7.3: Fig03 Hydrate Risk*

![Figure 7.4: Fig04 Flow Regime Map](figures/ch06_fig04_flow_regime_map.png)

*Figure 7.4: Fig04 Flow Regime Map*

![Figure 7.5: Fig05 Pressure Budget](figures/ch06_fig05_pressure_budget.png)

*Figure 7.5: Fig05 Pressure Budget*
