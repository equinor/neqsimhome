# Subsea Production Systems

**Running the examples.** Start the source-workspace Python session described in Chapter 1, then run this chapter's Python blocks in reading order. Java blocks form a separate sequence using the same NeqSim build; carry forward objects from preceding Java blocks. The release execution records are in `verification/`; a successful run establishes API compatibility, while physical validation also requires the checks discussed in the text.

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
8. Select between subsea field architecture configurations for different development scenarios

## 7.1 Introduction to Subsea Production

Subsea production systems enable the exploitation of offshore hydrocarbon reservoirs by placing wellheads, flow control equipment, and increasingly sophisticated processing equipment on the seabed. Since the first commercial subsea completion was installed in the Gulf of Mexico in 1961, the technology has evolved dramatically — modern subsea systems operate in water depths exceeding 3,000 meters with tieback distances of over 100 kilometers.

The fundamental advantage of subsea production is economic: rather than building a fixed or floating platform above every well cluster, subsea systems tie remote wells back to an existing host facility or an onshore plant. This shared infrastructure model dramatically reduces the capital investment required to develop marginal or remote fields.

However, subsea production introduces engineering challenges that do not arise with conventional dry tree completions:

- **Pressure loss** in long flowlines and risers reduces the natural driving force for production
- **Temperature loss** along the seabed exposes the produced fluid to hydrate, wax, and slug flow risks
- **Intervention difficulty** makes reliability and design margins critical — a failed subsea component may require a vessel costing \$500,000/day to repair
- **Flow assurance** challenges are more severe due to cold seabed temperatures and long transport distances

This chapter examines the architecture, design, and optimization of subsea production systems, with NeqSim providing the computational tools for pressure-temperature analysis, tieback feasibility studies, and cost estimation.

![Figure 7.1: Overview of a subsea production system showing wells, trees, manifolds, flowlines, and host facility](figures/subsea_system_overview.png)

## 7.2 Subsea Architecture and Components

### 7.2.1 Subsea Christmas Trees

The subsea tree (also known as a Christmas tree or wet tree) is the primary well control device installed on the seabed. It sits atop the wellhead and provides:

- **Flow control** — master valves and wing valves regulate production
- **Well shut-in** — fail-safe closed valves for emergency and planned shutdowns
- **Chemical injection points** — for hydrate inhibitor, corrosion inhibitor, and scale inhibitor injection
- **Monitoring** — pressure and temperature sensors for well surveillance
- **Intervention access** — through-bore access for wireline or coiled tubing operations

Two main configurations exist:

| Feature | Conventional vertical tree | Conventional horizontal tree |
|---------|----------------------------|------------------------------|
| Production master valves | In the vertical production bore | In lateral production bores |
| Tubing hanger | In the wellhead below the tree | In the tree body |
| Installation sequence | Hanger/tubing before tree | Tree before hanger/tubing |
| Tree retrieval | Tree can normally be removed above the landed hanger | Normally requires tubing/hanger retrieval first |
| Tubing intervention | Requires the configured vertical access/barrier arrangement | Tubing can be retrieved through the tree without first removing it |

These are conventional configurations; vendor variants and barrier requirements determine the actual installation and intervention sequence. Water depth, cost and pressure rating alone do not select a tree type.\cite{foundationIADCtree}

#### Tree Valve Functions

A subsea tree incorporates multiple valves in a specific arrangement that provides both flow regulation and well barrier functionality per NORSOK D-010:

- **Master valves** (upper and lower): Located in the vertical bore, these are the primary well barrier element. The lower master valve (LMV) is actuated hydraulically and is fail-safe closed — it closes automatically on loss of hydraulic supply. The upper master valve (UMV) provides redundancy.
- **Wing valves** (production and annulus): Located in the horizontal bore, the production wing valve (PWV) provides isolation; normal throttling is performed by the production choke. The annulus wing valve provides access to the annulus for pressure monitoring and chemical injection.
- **Swab valve**: Located at the top of the vertical bore, the swab valve allows wireline or coiled tubing access for well intervention. It is normally closed during production.
- **Crossover valve**: Connects the production bore to the annulus bore, enabling circulating operations during well cleanout or stimulation.
- **Choke valve**: An adjustable restriction downstream of the wing valve that controls the well flow rate. Modern subsea chokes are electrically actuated with position feedback for precise flow control.

The tubing head pressure (THP) — measured at the tree — is the key production surveillance parameter for subsea wells. It represents the pressure available to drive the fluid through the production system. The THP declines over field life as reservoir pressure depletes and water cut increases, and monitoring THP trends is essential for production optimization and well intervention planning:

$$
P_{THP} = P_{BHP} - \Delta P_{tubing,friction} - \rho_{fluid} \cdot g \cdot h_{TVD}
$$

where $P_{BHP}$ is the bottomhole flowing pressure, $\Delta P_{tubing,friction}$ is the frictional pressure drop in the tubing, $\rho_{fluid}$ is the average fluid density, $g$ is gravitational acceleration, and $h_{TVD}$ is the true vertical depth.

### 7.2.2 Subsea Manifolds

A subsea manifold collects production from multiple wells and routes it into a common flowline. Key design parameters include:

- **Number of slots** — typically 4 to 8 well connections
- **Pressure rating** — matched to the maximum shut-in tubing head pressure (SITHP)
- **Bore size** — determines flow capacity; typically 4" to 6" production bores
- **Valve configuration** — individual well isolation and crossover capability
- **Weight and footprint** — affects installation vessel requirements

Manifolds enable the commingling of production, reducing the number of flowlines required from the subsea field to the host. For example, a field with 12 wells and two 6-slot manifolds requires only 2 production flowlines rather than 12 individual well flowlines.

#### Header Sizing and Pressure Drop

The manifold production header must be sized to handle the commingled flow from all connected wells without excessive pressure drop. The header diameter is typically determined by limiting the erosional velocity per API RP 14E:

$$
v_{erosional} = \frac{C}{\sqrt{\rho_{mix}}}
$$

Here a field-unit coefficient such as $C=100$ uses density in lb/ft³ and produces velocity in ft/s; its SI-equivalent coefficient is about 122 when density is kg/m³ and velocity m/s. These coefficients are screening conventions, not a solids-erosion or corrosion model. For a 6-well manifold producing 10,000 bbl/d per well of a 35° API crude with GOR of 500 Sm³/Sm³, the header bore is typically 8"–10" nominal diameter.

The pressure drop through the manifold includes losses from header friction, branch connections, valves, and flow turns. A well-designed manifold contributes 1–3 bar of pressure drop — small relative to the flowline losses but significant when pressure budgets are tight.

#### Pigging Loops

In multi-well manifolds, pigging loops are incorporated to allow pipeline pigs to pass through the production header for wax removal, corrosion inhibitor distribution, and pipeline inspection. A pigging loop is a U-shaped section of pipe with pig launcher and receiver connections. The loop allows the pig to traverse the full length of the flowline from the manifold to the host, bypassing the manifold internals.

Pigging capability is essential for fields with waxy crudes or long tiebacks where regular wax management is required. Round-trip pigging (launching from the host and returning) requires additional infrastructure but enables intelligent pigging for corrosion assessment per DNV-RP-F116.

#### Manifold Layout Configurations

The arrangement of wells relative to manifolds defines the field topology:

| Configuration | Description | Advantages | Disadvantages |
|--------------|-------------|------------|---------------|
| Daisy chain | Wells connected in series along a single flowline | Minimal flowline, simple | Single point of failure, pressure accumulation |
| Hub-and-spoke | Wells radiate from a central manifold | Independent well access, flexible | Longer total jumper length |
| Dual-header | Manifold has separate test and production headers | Built-in well testing | Higher manifold cost and complexity |
| Modular | Stackable manifold modules added as field develops | Phased investment | Connection complexity between modules |

The choice of manifold configuration depends on the number of wells, phasing of development (wells drilled over several years), seabed topology, and the need for future expansion.

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

### 7.2.5 Umbilicals and Subsea Control Systems

Umbilicals are composite cables that deliver hydraulic fluid, electrical power, chemical injection, and communication signals from the host facility to subsea equipment. A modern umbilical typically contains:

- **Hydraulic lines** — for valve actuation (LP and HP supply), typically 2–4 tubes
- **Electrical conductors** — for power supply and signal transmission
- **Chemical injection tubes** — for MEG, methanol, corrosion inhibitor, scale inhibitor
- **Fiber optic cables** — for high-bandwidth communication and distributed sensing

Hydraulic pressure-wave propagation and actuator response are different quantities. The first scales roughly as $L/a$ using the wave speed of the fluid/tube system. Filling, draining, line compliance, fluid viscosity, restrictions and actuator volume govern the much longer stroke/charging time. Local accumulators and subsea control logic can supply the required action without waiting to charge the complete long line. Determine shutdown time from the actual actuator/control circuit and barrier function.

#### Electro-Hydraulic Control

The subsea control system is the nervous system of the production system. The dominant technology is the multiplexed electro-hydraulic (MUX E/H) system, which combines:

- **Hydraulic power** — separate pressure circuits serve the qualified actuator functions. Many production valves use hydraulic opening and spring closure; do not assume an HP supply universally powers fail-safe closure. Verify spring/accumulator energy, ambient pressure compensation, leakage and loss-of-supply behavior for each function.
- **Electrical power** — typically 600V AC or 3.3 kV AC for subsea distribution, powering subsea control modules (SCMs), choke actuators, condition monitoring sensors, and subsea electronic modules (SEMs).
- **Signal transmission** — digital communication over electrical conductors or fiber optics. Modern systems use fiber optics for high-bandwidth telemetry including condition monitoring data, distributed temperature sensing (DTS), and acoustic sand detection.

Each subsea tree has a subsea control module (SCM) that receives commands from the master control station (MCS) on the host facility and executes valve operations locally. The SCM contains redundant electronics (dual SEM cards) for reliability.

#### Power Delivery to Subsea Equipment

For subsea processing equipment (pumps, compressors, separators), the power requirements far exceed what conventional umbilicals can deliver. Power delivery options include:

- **Medium-voltage AC** (up to 36 kV): Suitable for subsea pumps up to ~15 MW at distances up to ~50 km
- **High-voltage AC** (66–145 kV): Required for large subsea compression systems (20–50 MW)
- **High-voltage DC (HVDC)**: Emerging technology for ultra-long distances (>100 km), minimizing reactive power losses

Variable speed drives (VSDs) are located either topside (with the variable-frequency power transmitted through the umbilical) or subsea (with fixed-frequency power transmitted and converted locally). Subsea VSDs reduce cable losses but add subsea complexity.

#### Chemical Injection

Chemical injection through umbilical tubes is essential for flow assurance management:

| Chemical | Purpose | Typical Rate | Injection Point |
|----------|---------|-------------|-----------------|
| Methanol (MeOH) | Hydrate inhibition | 0.5–5 m³/hr | Tree, manifold, flowline |
| Mono-ethylene glycol (MEG) | Hydrate inhibition (regenerable) | 1–10 m³/hr | Tree, manifold |
| Scale inhibitor | Prevent mineral scale | 5–50 L/hr | Downhole, tree |
| Corrosion inhibitor | Protect carbon steel | 5–50 L/hr | Tree, flowline |
| Wax inhibitor | Prevent wax deposition | 0.5–2 m³/hr | Wellhead, flowline |
| Asphaltene inhibitor | Prevent asphaltene deposition | 1–20 L/hr | Downhole |

The choice between methanol and MEG for hydrate inhibition is a major design decision. Methanol is simpler (no regeneration required) but consumed continuously, making it expensive for high water-cut or long-distance fields. MEG can be regenerated and recycled but requires a topside MEG reclamation unit.

![Figure 7.2: Conceptual manifold-centered subsea tieback layout](figures/subsea_field_layout.png)

<!-- scientific-illustration:subsea_field_layout.png -->
The wells connect to a common manifold and a trunk line to the host. This is a hub layout, not a daisy-chain topology; line lengths, elevations and pressure-loss models are needed for hydraulic analysis.
<!-- /scientific-illustration -->

## 7.3 Subsea Field Architectures

The spatial arrangement of wells, manifolds, flowlines, and risers defines the subsea field architecture. The choice of architecture profoundly affects capital cost, operability, reliability, and the ability to phase development over time.

### 7.3.1 Architecture Types

**Satellite wells** are individual subsea trees connected directly to the host facility by dedicated flowlines. This is the simplest architecture and is used for developments with 1–3 wells or wells that are widely spaced and cannot be economically grouped.

**Cluster manifold** architecture groups 4–8 wells around a central manifold, with the manifold connected to the host by one or two production flowlines and an umbilical. This is the most common configuration for medium-sized fields.

**Daisy chain** architecture connects wells or manifolds in series along a single flowline. Each well or manifold tees into the flowline, which runs from the most distant well to the host. This minimizes flowline length but means that all wells share a common flowline — a blockage or failure in the flowline affects all upstream wells.

**Subsea to shore** eliminates the offshore host facility entirely, routing subsea production through long-distance flowlines directly to an onshore processing plant. This architecture is used for gas fields near coastlines (e.g., Ormen Lange in Norway, 120 km tieback to Nyhamna).

**Template-based** architecture uses a drilling template that integrates well slots, manifold functions, and pipeline connections into a single structure. This is common in the North Sea where fields are developed with a large number of closely spaced wells.

### 7.3.2 Architecture Comparison

| Architecture | Typical Wells | Tieback Distance | CAPEX | Flexibility | Reliability |
|-------------|--------------|-----------------|-------|-------------|-------------|
| Satellite | 1–3 | 2–20 km | Low per well, high per bbl | Low | High (independent) |
| Cluster manifold | 4–12 | 5–50 km | Medium | Medium | Medium |
| Daisy chain | 3–8 | 10–40 km | Low (shared flowline) | Low | Low (common mode) |
| Subsea to shore | 4–20+ | 50–200 km | High (long flowlines) | Low | Medium |
| Template | 4–30+ | 0.5–15 km | High (template structure) | High | High |

### 7.3.3 Selection Criteria

The choice of architecture is driven by:

- **Reservoir geometry**: Elongated reservoirs suit daisy-chain; compact reservoirs suit cluster manifolds
- **Number of wells and phasing**: Template architectures are efficient for large, fully defined developments; modular manifolds suit phased drilling campaigns
- **Distance to host**: Compare the extra flowlines, shared-capacity limits and intervention strategy; there is no universal 15 km economic cutoff
- **Seabed terrain**: Rough seabed or steep slopes may dictate flowline routing and manifold placement
- **Flow assurance**: High wax or hydrate risk may favor architectures with pigging capability (cluster manifold with pigging loop) over daisy chain (difficult to pig)
- **Expansion potential**: If additional wells may be drilled later, the architecture should accommodate future tie-ins

## 7.4 Subsea vs. Dry Tree Completions

The choice between subsea (wet tree) and dry tree completions is one of the most consequential decisions in offshore field development. It affects capital cost, operating cost, production efficiency, intervention frequency, and ultimately recovery factor.

### 7.4.1 Dry Tree Platforms

Dry tree completions place the wellheads on the platform deck, providing direct access for wireline, coiled tubing, and workover operations. Platform types that support dry trees include:

- **Fixed platforms** — jacket or gravity-based structures in shallow water (< 300 m)
- **Compliant towers** — for moderate water depths (300–600 m)
- **Tension Leg Platforms (TLPs)** — taut-moored for deepwater (500–1,500 m)
- **Spars** — deep-draft cylindrical hulls (500–2,500 m)

The primary advantage of dry trees is well access. Wireline and coiled tubing operations that cost \$200,000 and take 2 days from a platform may cost \$5,000,000 and take 3 weeks from a subsea intervention vessel.

### 7.4.2 Decision Criteria

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

### 7.4.3 Impact on Recovery Factor

Tree architecture can affect intervention access, backpressure and economically available wells. A universal 3–8% recovery uplift is unsupported; assess the same reservoir and development constraints before attributing a recovery difference to tree type. Potential mechanisms include:

- More frequent well intervention enables better reservoir management
- Easier installation of artificial lift (gas lift, ESPs)
- Lower wellhead back-pressure (no long flowlines)
- More production/injection wells can be economically justified

This recovery factor difference must be weighed against the capital cost difference, which often favors subsea for smaller fields or tiebacks to existing infrastructure.

## 7.5 Pressure and Temperature Constraints

### 7.5.1 The Pressure Budget

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

Rearranging the pressure budget from the wellhead perspective, the pressure available to drive the fluid through the production system is the wellhead pressure minus the separator pressure:

$$
P_{wellhead} = P_{separator} + \Delta P_{flowline} + \Delta P_{riser} + \Delta P_{choke}
$$

This form is useful for tieback analysis: for a given wellhead pressure (determined by reservoir conditions and well performance), the maximum tieback distance is limited by the sum of flowline, riser, and choke pressure drops. As tieback distance increases, $\Delta P_{flowline}$ grows, leaving less margin for the choke and eventually requiring reduced flow rates or subsea boosting.

### 7.5.2 Temperature Constraints

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

### 7.5.3 NeqSim Pressure-Temperature Analysis

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

### 7.5.4 Complete Subsea Tieback Model

A comprehensive tieback model includes the well tubing, choke, subsea flowline, and riser — the full pressure path from bottomhole to topside separator. This NeqSim example models each segment:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Define production fluid
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 85.0, 280.0)
fluid.addComponent("nitrogen", 0.6)
fluid.addComponent("CO2", 2.8)
fluid.addComponent("methane", 62.0)
fluid.addComponent("ethane", 7.5)
fluid.addComponent("propane", 5.0)
fluid.addComponent("i-butane", 1.2)
fluid.addComponent("n-butane", 2.8)
fluid.addComponent("i-pentane", 1.0)
fluid.addComponent("n-pentane", 1.5)
fluid.addComponent("n-hexane", 2.5)
fluid.addComponent("n-heptane", 4.5)
fluid.addComponent("n-octane", 3.5)
fluid.addComponent("water", 5.1)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

Stream = jneqsim.process.equipment.stream.Stream
PipeBeggsAndBrills = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills
ThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# --- Bottomhole stream ---
bhp_stream = Stream("Bottomhole", fluid)
bhp_stream.setFlowRate(60000.0, "kg/hr")
bhp_stream.setTemperature(85.0, "C")
bhp_stream.setPressure(280.0, "bara")

# --- Well tubing (3500 m MD, ~3200 m TVD) ---
tubing = PipeBeggsAndBrills("Well Tubing", bhp_stream)
tubing.setPipeWallRoughness(2.5e-5)
tubing.setLength(3500.0)              # 3.5 km measured depth
tubing.setElevation(3200.0)       # positive = outlet above inlet
tubing.setDiameter(0.1143)         # 4.5-inch tubing ID
tubing.setNumberOfIncrements(30)
tubing.setConstantSurfaceTemperature(285.15) # geothermal average ~12 C

# --- Subsea choke ---
choke = ThrottlingValve("Subsea Choke", tubing.getOutletStream())
choke.setOutletPressure(110.0)     # below the calculated upstream wellhead pressure

# --- Subsea flowline (20 km horizontal on seabed) ---
flowline = PipeBeggsAndBrills("Subsea Flowline", choke.getOutletStream())
flowline.setPipeWallRoughness(5.0e-5)
flowline.setLength(20000.0)
flowline.setElevation(0.0)
flowline.setDiameter(0.254)        # 10-inch
flowline.setNumberOfIncrements(50)
flowline.setConstantSurfaceTemperature(277.15)  # 4 C seabed

# --- Riser (400 m water depth) ---
riser = PipeBeggsAndBrills("Production Riser", flowline.getOutletStream())
riser.setPipeWallRoughness(5.0e-5)
riser.setLength(500.0)               # ~500 m riser length
riser.setElevation(400.0)          # 400 m vertical rise
riser.setDiameter(0.254)
riser.setNumberOfIncrements(15)
riser.setConstantSurfaceTemperature(280.15)

riser.setHeatTransferCoefficient(5.0)  # assumed insulated-pipe U, W/(m2 K)
# --- Build and run ---
process = ProcessSystem()
process.add(bhp_stream)
process.add(tubing)
process.add(choke)
process.add(flowline)
process.add(riser)
process.run()

# --- Report pressure budget ---
P_bhp = bhp_stream.getPressure("bara")
P_wh = tubing.getOutletStream().getPressure("bara")
P_choke_out = choke.getOutletStream().getPressure("bara")
P_fl_out = flowline.getOutletStream().getPressure("bara")
P_topside = riser.getOutletStream().getPressure("bara")
T_topside = riser.getOutletStream().getTemperature("C")
assert 0.0 < P_choke_out <= P_wh, "A passive choke cannot add pressure"

print("=== Subsea Tieback Pressure Budget ===")
print(f"Bottomhole pressure:     {P_bhp:.1f} bara")
print(f"Wellhead pressure:       {P_wh:.1f} bara  (tubing dP = {P_bhp - P_wh:.1f} bar)")
print(f"After choke:             {P_choke_out:.1f} bara  (choke dP = {P_wh - P_choke_out:.1f} bar)")
print(f"Flowline outlet:         {P_fl_out:.1f} bara  (flowline dP = {P_choke_out - P_fl_out:.1f} bar)")
print(f"Topside arrival:         {P_topside:.1f} bara  (riser dP = {P_fl_out - P_topside:.1f} bar)")
print(f"Topside arrival temp:    {T_topside:.1f} C")
```

## 7.6 Tieback Distance Analysis

### 7.6.1 Maximum Tieback Distance

The maximum tieback distance is determined by the intersection of three constraints:

1. **Pressure constraint** — the available pressure drop in the flowline (total pressure budget minus tubing, choke, and riser losses) limits distance
2. **Temperature constraint** — the arrival temperature must remain above the hydrate equilibrium temperature (with safety margin) or the WAT
3. **Cooldown constraint** — the time for the fluid to cool below the hydrate temperature during a shutdown must exceed the minimum intervention time

For a given set of operating conditions, the maximum tieback distance is:

$$
L_{max} = \min\left(L_{max,\Delta P}, \, L_{max,T_{arr}}, \, L_{max,t_{cool}}\right)
$$

The pressure-limited distance can be estimated from the Beggs and Brill correlation or simplified as:

$$
L_{max,\Delta P} = \frac{2\Delta P_{available}D}{\lambda\rho_{mix}v^2}
$$

where $\Delta P_{available}$ is the pressure budget allocated to the flowline, $D$ is the diameter, $\lambda$ is the friction factor, $\rho_{mix}$ is the mixture density, and $v$ is the mixture velocity. At fixed velocity this relation is linear in diameter. At fixed volumetric rate, substitution of $v=4Q/(\pi D^2)$ gives a $D^5$ dependence if density and friction factor remain constant. Multiphase holdup, friction-factor changes, acceleration and elevation invalidate treating the resulting factor of 32 as a general design rule.

The temperature-limited distance is derived from the exponential temperature decay equation:

$$
L_{max,T_{arr}} = -\frac{\dot{m} C_p}{\pi D U} \ln\left(\frac{T_{min} - T_{sea}}{T_{inlet} - T_{sea}}\right)
$$

where $T_{min}$ is the minimum acceptable arrival temperature (hydrate equilibrium temperature plus safety margin).

### 7.6.2 Tieback Feasibility Study with NeqSim

A tieback feasibility study systematically evaluates production rate and arrival conditions over a range of flowline lengths:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import json

# Fluid definition (as above - reused from Section 7.5.3)
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

    pipe.setHeatTransferCoefficient(5.0)  # assumed insulated-pipe U, W/(m2 K)
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



### 7.6.3 Typical Tieback Distances

The following broad ranges are orientation examples, not demonstrated capability or acceptance limits. A particular tieback requires a field-specific thermal, hydraulic and shutdown assessment:

| Fluid Type | Typical Max Distance (uninsulated) | With Insulation | With Boosting |
|-----------|-----------------------------------|-----------------|---------------|
| Dry gas | 80–150 km | 150–200 km | > 200 km |
| Wet gas / condensate | 30–60 km | 50–80 km | 80–120 km |
| Light oil (GOR > 200) | 20–40 km | 30–50 km | 50–80 km |
| Heavy/waxy oil | 5–15 km | 10–25 km | 25–50 km |

These distances assume typical pipe sizes (8"–14"), seabed temperatures of 2–5°C, and host separator pressures of 20–40 bara.

## 7.7 Subsea Processing

### 7.7.1 Motivation for Subsea Processing

Subsea processing addresses the declining pressure budget as reservoirs deplete. By placing processing equipment — pumps, separators, or compressors — on the seabed, the effective tieback distance is extended and production is maintained longer without topside modifications.

The key drivers for subsea processing are:

- **Pressure boosting** — adds energy to overcome flowline friction and riser hydrostatic head
- **Separation** — removes water or gas on the seabed to reduce flowline hydraulic load
- **Gas compression** — compresses gas to maintain delivery pressure as reservoir pressure declines
- **Sand management** — removes sand before it enters flowlines

### 7.7.2 Subsea Boosting (Multiphase Pumps)

Subsea multiphase pumps are the most widely deployed form of subsea processing. They boost the total well stream — gas, oil, and water — without prior separation. Key technologies include:

| Technology | Principle | Typical dP | GVF Tolerance | Power Range |
|-----------|-----------|------------|---------------|-------------|
| Helico-axial (Framo/OneSubsea) | Axial impellers with helical design | 30–100 bar | Up to 95% | 2–12 MW |
| Twin-screw (Leistritz/Bornemann) | Positive displacement screw pump | 20–80 bar | Up to 100% | 1–5 MW |
| Counter-rotating axial | Counter-rotating impeller stages | 20–60 bar | Up to 90% | 2–8 MW |
| Electrical submersible pump (ESP) | Centrifugal multistage | 50–200 bar | Up to 70% | 0.5–3 MW |

**Helico-axial pumps** are the dominant technology for subsea boosting. The Framo helico-axial pump uses a combination of an axial impeller and a helical inducer to handle gas–liquid mixtures. The impeller accelerates the fluid, and a diffuser converts kinetic energy to pressure. Multiple stages (typically 4–12) are stacked to achieve the required differential pressure. The key advantage is tolerance of high gas volume fractions (GVF up to 95%) without the slugging and vibration problems that affect conventional centrifugal pumps.

**Twin-screw pumps** are positive displacement machines that can cover a broad gas-volume-fraction range when designed for it. Sustained operation near 100% gas may require liquid recirculation for sealing and cooling; duration, temperature rise, differential pressure and sand loading must remain within the vendor envelope. Two intermeshing screws trap and transport fluid volumes along the screw axis. They are particularly suited for low-flow, high-differential-pressure applications and viscous fluids. However, they have lower volumetric capacity than helico-axial pumps and are more sensitive to sand erosion.

Vigdis multiphase pumping started in May2021. Åsgard and Gullfaks started different subsea compression technologies in 2015; they should not be listed as equivalent pump deployments.\cite{foundationVigdis2021,foundationGullfaks2015}

### 7.7.3 Subsea Separation and Water Injection

Subsea separation separates the produced fluid into gas and liquid phases on the seabed. The separated streams are transported in dedicated flowlines:

- **Gas** — flows to the host at higher velocity but lower frictional loss per unit mass
- **Liquid** — can be boosted by a less complex liquid pump

The Tordis subsea separation system (installed 2007) demonstrated subsea separation and water reinjection, removing water on the seabed and reinjecting it into a disposal well, reducing the hydraulic load on the flowline and topside produced water treatment.

Subsea water separation and reinjection (SSBI) offers substantial benefits for high water-cut fields:

- Reduces the volume of fluid transported through flowlines by 30–60%
- Reduces topside produced water treatment requirements
- Enables reinjection for pressure support close to the producing wells
- Extends field life by reducing the hydraulic load that limits production rate

Design challenges for subsea separators include limited space for gravity settling (compact separators use cyclonic or pipe separator technology), sand handling, and the need for subsea water treatment before reinjection (to avoid reservoir plugging).

### 7.7.4 Subsea Wet Gas Compression

Åsgard began subsea gas compression in September2015 with gas/liquid separation before compression. Gullfaks began wet-gas compression in October2015 without that upstream phase separation. Their different liquid-handling architectures determine compressor qualification and auxiliary equipment. Åsgard phase2 was completed in 2025.\cite{foundationAsgard2015,foundationGullfaks2015,foundationAsgard2025}

The subsea compression station at Åsgard consists of two parallel compression trains, each with an inlet liquid knockout drum (subsea scrubber), a centrifugal compressor driven by a high-speed electric motor, an anti-surge recycle system, and a subsea cooler downstream of the compressor.

Wet gas compression differs fundamentally from dry gas compression:

| Parameter | Dry Gas Compression | Wet Gas Compression |
|-----------|-------------------|-------------------|
| Inlet liquid content | < 0.1% by volume | 1–5% by volume |
| Compressor type | Standard centrifugal | Modified centrifugal with erosion-resistant internals |
| Anti-surge control | Conventional recycle | Fast-acting recycle with liquid management |
| Downstream cooling | Gas cooler only | Multiphase cooler |
| Power supply | Topside | Long-distance subsea electrical cable |

Key design challenges include:

- Liquid handling in compressor impellers
- Anti-surge control without fast-acting recycle valves
- Long-distance electrical power supply (up to 60 MW at 36 kV)
- Reliability requirements (5+ year uninterrupted operation target)

### 7.7.5 Subsea Power Distribution

Powering subsea processing equipment requires a subsea electrical infrastructure that is itself a major engineering system:

- **Subsea transformers**: Step voltage up for long-distance transmission, step down for local distribution
- **Subsea switchgear**: Circuit breakers and contactors for equipment isolation and protection
- **Subsea variable speed drives (VSD)**: Control pump and compressor speed for flow matching
- **Subsea power cables**: Medium- or high-voltage cables from host to subsea distribution

The total power demand for a subsea processing station can range from 5 MW (single pump) to 60 MW (compression and pumping), making power delivery one of the most challenging aspects of subsea processing.

### 7.7.6 Technology Readiness and Deployment

Technology qualification applies to a specific design and operating envelope. Use a dated qualification dossier and field-reference list; counts and generic TRLs for an entire technology family can hide differences in pressure, fluid, power, intervention and duty. The dated operator examples above establish deployment history, not blanket qualification for a new field.

### 7.7.7 Modeling Subsea Boosting with NeqSim

A screening estimate of subsea boosting can insert a pressure increase between the flowline and riser. This example uses a compressor as a thermodynamic pressure-raising proxy for the defined multiphase fluid. It is not a qualified wet-gas compressor or multiphase-pump performance model; detailed design needs phase handling, vendor maps, and an appropriate machine model:

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

flowline.setHeatTransferCoefficient(5.0)  # assumed insulated-pipe U, W/(m2 K)
# Subsea booster (modeled as a compressor for pressure increase)
booster = Compressor("Subsea Booster", flowline.getOutletStream())
booster.setOutletPressure(150.0)  # pressure increase above the flowline inlet
booster.setPolytropicEfficiency(0.75)
booster.setUsePolytropicCalc(True)

# Riser (500 m water depth, vertical)
riser = PipeBeggsAndBrills("Riser", booster.getOutletStream())
riser.setPipeWallRoughness(5.0e-5)
riser.setLength(600.0)       # ~600 m riser length
riser.setElevation(500.0)  # 500 m water depth
riser.setDiameter(0.254)
riser.setNumberOfIncrements(20)
riser.setConstantSurfaceTemperature(280.15)

riser.setHeatTransferCoefficient(5.0)  # assumed insulated-pipe U, W/(m2 K)
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
assert booster_power > 0.0, "A booster must consume positive shaft power"
print(f"Topside arrival pressure: {topside_P:.1f} bara")
print(f"Topside arrival temperature: {topside_T:.1f} °C")
print(f"Subsea booster power: {booster_power:.0f} kW")
```

## 7.8 Subsea Well Design with NeqSim

### 7.8.1 The SubseaWell Class

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

### 7.8.2 Casing Design per API 5C3

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

Illustrative screening design-factor inputs are listed below; they have not been traced to a NORSOK D-010 clause and must not be used as a compliance table. Actual casing assessment includes load combinations, temperature, corrosion allowance, connection capacity and the applicable standard edition:

| Load Case | Design Factor |
|-----------|--------------|
| Burst (production casing) | 1.10 |
| Collapse (production casing) | 1.10 |
| Tension | 1.30 |
| Triaxial (VME) | 1.25 |

## 7.9 SURF Cost Estimation

### 7.9.1 Cost Components

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

### 7.9.2 Cost Estimation Approach

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

### 7.9.3 Cost Sensitivity

The dominant cost drivers for SURF systems are:

- **Water depth** — affects riser length, installation vessel requirements, and equipment ratings
- **Tieback distance** — flowline and umbilical costs scale linearly with distance
- **Number of wells** — each well requires a tree, connections, and control system
- **Pipe diameter** — larger pipes cost more per meter but may enable higher production
- **Insulation** — wet insulation (syntactic foam) adds \$500–2,000/m; pipe-in-pipe adds \$2,000–5,000/m

![Figure 7.3: Illustrative allocation of an assumed 720 MNOK SURF budget](figures/surf_cost_breakdown.png)

<!-- scientific-illustration:surf_cost_breakdown.png -->
The slices are assigned teaching inputs, not vendor quotations or a cost estimate for a specified development. Use a dated quantity and cost basis, installation scope and uncertainty model for investment analysis.
<!-- /scientific-illustration -->

## 7.10 Field Layout Optimization

### 7.10.1 Layout Considerations

The subsea field layout — the spatial arrangement of wells, manifolds, flowlines, and risers — affects both capital cost and production performance:

- **Well spacing** — too close risks interference; too far increases jumper lengths
- **Manifold location** — should minimize total jumper and flowline lengths
- **Flowline routing** — must avoid geohazards, existing infrastructure, and excessive free spans
- **Riser connection** — the point where the flowline transitions to a riser affects both cost and flow assurance

### 7.10.2 Optimization Approach

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

## 7.11 Subsea Coolers and Subsea Processing Integration

In some fields, particularly those with high reservoir temperatures or gas condensate fluids, a subsea cooler may be installed to reduce the fluid temperature before entering long flowlines. The reduced temperature decreases the specific volume of the gas phase, reducing velocity and friction pressure drop.

However, subsea cooling must be balanced against flow assurance risks — lower temperatures bring the fluid closer to hydrate and wax formation conditions. The optimal subsea cooler exit temperature is typically:

$$
T_{cooler,out} = T_{hydrate}(P_{cooler,out}) + \Delta T_{margin}
$$

where $\Delta T_{margin}$ is a safety margin, typically 5–10°C above the hydrate equilibrium temperature.

## 7.12 NeqSim Implementation Summary

The key NeqSim classes used for subsea production system analysis are:

| NeqSim Class | Application |
|-------------|-------------|
| `SubseaWell` | Subsea well definition, completion parameters |
| `WellMechanicalDesign` | Casing design (API 5C3), barrier verification (NORSOK D-010), cost estimation |
| `PipeBeggsAndBrills` | Multiphase flow in flowlines, risers, and well tubing |
| `Stream` | Define wellhead and arrival conditions |
| `Compressor` | Model subsea boosting pressure increase |
| `ThrottlingValve` | Model subsea choke for flow control |
| `Separator` | Topside separation (for pressure budget endpoint) |
| `ProcessSystem` | Compose the complete subsea-to-topside system |
| `ThermodynamicOperations` | Hydrate equilibrium calculations for flow assurance |


<!-- reviewed-notebook-results:start -->
## Reproduced Calculation Results

These examples use the stated fluid recipes and operating assumptions. Curves represent NeqSim calculations unless a caption identifies an analytical illustration, assumed equipment map or synthetic data.

![Figure 7.4: Pressure Profile Along Subsea Pipeline](figures/ch06_fig01_pressure_profile.png)

Pipeline Pressure: pressure spans 146.5–150 bara across the plotted cases.

Friction and elevation redistribute pressure along the subsea route; changing density and phase holdup alters the local gradient. The arrival pressure determines how much pressure is available for the riser and receiving plant, rather than constituting a free design input. Use the surveyed elevation profile, verify the pressure budget and refine segmentation until the arrival pressure is stable.

![Figure 7.5: Isothermal Hydraulic Case: Temperature Held Constant. Specified isothermal boundary; no seabed heat-transfer calculation](figures/ch06_fig02_temperature_profile.png)

Fluid Temperature: temperature remains 70 °C across the plotted cases.

This notebook holds each pipeline segment at the specified 70 degree Celsius temperature; heat transfer to the seabed is not solved. The flat profile is an isothermal boundary assumption and cannot quantify normal-operation cooling or shutdown margin. Enable and calibrate a thermal model before using arrival temperature to select insulation or hydrate protection.

![Figure 7.6: Hydrate Formation Risk Assessment - T-P Overlay. Calculated hydrate equilibrium overlaid with the assumed isothermal operating path](figures/ch06_fig03_hydrate_risk.png)

Hydrate Equilibrium Curve: pressure spans 20–200 bara across the plotted cases. Pipeline Operating Conditions: pressure spans 146.5–150 bara across the plotted cases.

The hydrate curve is a separate NeqSim equilibrium calculation; the operating points use the isothermal pipeline assumption. The 70 degree Celsius path is comfortably warmer than equilibrium in this constructed example, but its apparent margin does not account for actual seabed heat loss. Recompute the operating path with heat transfer and evaluate cooldown and free-water availability before selecting protection.

![Figure 7.7: Illustrative Horizontal Flow-Regime Map. Conceptual regime boundaries, not a validated mechanistic flow map](figures/ch06_fig04_flow_regime_map.png)

Superficial Liquid Velocity spans 0.001–0.03144 m/s across the plotted cases.

Superficial gas and liquid velocities characterize the competing inertia, buoyancy and phase-continuity mechanisms that form flow regimes. A horizontal regime map is a screening tool and may not describe inclined sections, risers or transient severe slugging. Use regime labels within the correlation’s domain and assess liquid accumulation and transient slugging for the actual route.

![Figure 7.8: Illustrative subsea pressure budget. Prescribed pressure-budget entries](figures/ch06_fig05_pressure_budget.png)

The assumed pressure allocation starts at 300 bara reservoir pressure and ends at 176 bara separation pressure. The individual losses are prescribed budget entries rather than a solved network balance.

The total well-to-platform pressure difference is consumed by tubing lift, choke loss, flowline friction and riser elevation. A negative passive choke loss or a booster with negative power exposes an inconsistent model boundary rather than a production benefit. Check each pressure contribution and the sign of equipment work before allocating additional backpressure or evaluating subsea boosting.

Selected numerical ranges from the plotted cases:

| Quantity / series | Minimum | Maximum | Unit |
|---|---:|---:|---|
| Pipeline Pressure: pressure | 146.5 | 150 | bara |
| Fluid Temperature: temperature | 70 | 70 | °C |
| Hydrate Equilibrium Curve: pressure | 20 | 200 | bara |
| Superficial Liquid Velocity | 0.001 | 0.03144 | m/s |

Ranges describe the sampled cases; they are not independent validation tolerances.
<!-- reviewed-notebook-results:end -->

## 7.13 Summary

Key points from this chapter:

- Subsea production systems enable the development of offshore fields by placing wellheads and equipment on the seabed with tiebacks to host facilities
- The major components are subsea trees, manifolds, flowlines, risers, and umbilicals
- Subsea tree valve functions (master, wing, swab, choke) provide both flow control and well barrier integrity per NORSOK D-010
- Manifold design includes header sizing for commingled flow, pigging loops for pipeline maintenance, and layout configurations (hub-spoke, daisy chain, dual-header)
- The pressure budget — from reservoir to separator — determines the maximum production rate and tieback distance; the wellhead pressure must overcome flowline, riser, and choke pressure drops
- Temperature management is critical to prevent hydrate and wax formation in subsea flowlines
- Subsea field architectures (satellite, cluster manifold, daisy chain, subsea to shore) each have distinct advantages depending on field size, distance, and phasing
- Subsea processing technologies — multiphase pumping (helico-axial, twin-screw), separation, and wet gas compression — extend field life and tieback distances
- Power delivery to subsea processing equipment is a major design challenge, requiring medium- or high-voltage subsea electrical systems
- Umbilicals deliver hydraulic control, electrical power, and chemical injection (methanol, MEG, scale inhibitor) to subsea equipment
- NeqSim's `SubseaWell`, `PipeBeggsAndBrills`, and `ProcessSystem` classes enable comprehensive subsea system modeling from bottomhole to topside
- SURF costs typically represent 30–50% of total subsea development costs and are dominated by flowline length and water depth
- Field layout optimization balances cost, production, and flow assurance objectives



<!-- foundations-scientific-verification -->

### Verification of the worked examples

The completed subsea pipe/cooler calculations are checked for material conservation and valid pressures and temperatures. The thermal example states its chosen overall heat-transfer coefficient; the audit does not calibrate heat loss, multiphase holdup or vendor equipment performance. Published operator reports distinguish the actual Åsgard, Gullfaks and Vigdis technologies and startup dates; cost and casing factors are explicitly screening inputs.\cite{foundationAsgard2015,foundationGullfaks2015,foundationVigdis2021}

The calculation and literal-code records are in `verification/scientific_revision/ch07_manuscript_physics.json`; the chapter scope and code hashes are indexed in `foundations_review.json`.

<!-- /foundations-scientific-verification -->

## Exercises

1. **Exercise 7.1:** For the reference fluid in Section 7.5.3, calculate the pressure and temperature at the end of a 25 km subsea flowline for pipe diameters of 8", 10", and 12". Plot the results and identify the minimum acceptable diameter if the arrival temperature must be at least 20°C above the hydrate equilibrium temperature.

2. **Exercise 7.2:** Using the subsea well model in Section 7.8.1, modify the water depth from 350 m to 1,500 m and recalculate the well cost estimate. What is the approximate cost increase per meter of additional water depth?

3. **Exercise 7.3:** A subsea field has 8 wells producing a gas condensate fluid (GOR = 3,000 Sm³/Sm³). The water depth is 800 m and the distance to the host is 35 km. Using NeqSim, model the complete system (wells → manifold → flowline → riser → separator at 60 bara) and determine: (a) the total pressure drop, (b) the arrival temperature, (c) whether subsea boosting is needed.

4. **Exercise 7.4:** Perform a SURF cost estimate for the field in Exercise 7.3 using the parametric cost model in Section 7.9.2. Calculate the SURF cost for two alternative layouts: (a) one manifold with all 8 wells, and (b) two manifolds with 4 wells each connected by a gathering flowline.

5. **Exercise 7.5:** Repeat the tieback distance analysis in Section 7.6.2 with and without subsea boosting (50 bar pressure increase). Plot the additional distance achievable with boosting as a function of flowline diameter.

6. **Exercise 7.6:** Estimate the hydraulic response time for a subsea control system with a 60 km umbilical. Assume a 3/8" hydraulic tube, 345 bar working pressure, and standard hydraulic fluid. Discuss the implications for emergency shutdown system design.

7. **Exercise 7.7:** Compare the pressure budgets for a satellite well (10 km direct tieback) and a manifold well (5 km jumper to manifold, then 15 km flowline) for the same wellhead conditions. Which architecture delivers lower topside arrival pressure, and why?

8. **Exercise 7.8:** A late-life subsea field has declining wellhead pressures (from 180 bara to 80 bara over 10 years). Using the subsea boosting model from Section 7.7.7, determine the year at which boosting becomes necessary to maintain a topside arrival pressure of 30 bara through a 20 km flowline and 400 m riser.

## References

1. Bai, Y. and Bai, Q. (2019). *Subsea Engineering Handbook*, 2nd Edition. Gulf Professional Publishing.
2. Gudmestad, O.T. (2015). *Marine Technology and Operations: Theory & Practice*. WIT Press.
3. Zhen, L. and Songhurst, B. (2018). "Subsea processing: The next step in subsea field development." *Journal of Petroleum Technology*, 70(3), 44–52.
4. NORSOK D-010 (2021). *Well Integrity in Drilling and Well Operations*, Rev. 5. Standards Norway.
5. API Bull 5C3 (2008). *Bulletin on Formulas and Calculations for Casing, Tubing, Drill Pipe and Line Pipe Properties*. American Petroleum Institute.
6. DNV-RP-F101 (2019). *Corroded Pipelines*. Det Norske Veritas.
7. Sangesland, S. (2018). "Subsea well technology." Chapter in *Petroleum Production Engineering*, Elsevier.
8. Eriksson, K. and Høvik, J. (2017). "Subsea compression — technology development and qualification." *OTC*, Paper OTC-27893.
9. API RP 14E (1991). *Recommended Practice for Design and Installation of Offshore Production Platform Piping Systems*, 5th Edition.
10. DNV-RP-F116 (2015). *Integrity Management of Submarine Pipeline Systems*. Det Norske Veritas.
11. Akers, T. and Amin, A. (2014). "Subsea multiphase pumping: Technology update." *SPE*, Paper SPE-170238.
12. Gjerdseth, A.C., Faanes, A., and Ramberg, R. (2012). "The world's first subsea compression system — from design to operation." *OTC*, Paper OTC-23427.

<!-- Chapter-level references are merged into master refs.bib -->

