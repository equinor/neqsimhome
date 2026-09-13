# Field Development Planning

<!-- Chapter metadata -->
<!-- Notebooks: ch19_vfp_generation.ipynb, ch19_multi_scenario.ipynb, ch19_field_digital_twin.ipynb -->
<!-- Estimated pages: 38 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Explain why traditional single-composition VFP tables are inadequate for fields with changing GOR and water cut
2. Generate multi-scenario VFP tables spanning the full (rate × pressure × water cut × GOR) design space
3. Use the FluidMagicInput, RecombinationFlashGenerator, and MultiScenarioVFPGenerator classes in NeqSim
4. Export VFP tables in Eclipse VFPEXP format for reservoir simulation coupling
5. Design field development workflows that integrate PVT, reservoir, well, and process modeling
6. Build a field development digital twin connecting reservoir depletion to surface facility performance
7. Implement VFP generation and multi-scenario analysis in Python

---

## 28.1 Introduction

Field development planning requires predicting how wells and facilities will perform over the field's lifetime — typically 20–30 years. During this period, the produced fluid properties change dramatically:

- **GOR increases** as reservoir pressure declines below the bubble point, liberating solution gas
- **Water cut rises** as the aquifer encroaches or water injection breaks through
- **Reservoir pressure drops**, reducing the driving force for flow
- **Fluid composition shifts** — heavier components become more concentrated in the liquid phase

These changes mean that a VFP table generated at a single fluid composition becomes increasingly inaccurate over time. A table calculated at initial conditions (GOR = 500 Sm³/Sm³, WC = 5%) may be completely wrong when the well is producing at GOR = 3000 Sm³/Sm³ and WC = 40%.

This chapter introduces **multi-scenario VFP generation** — the creation of VFP tables that span the full range of expected fluid conditions throughout the field's life. We present NeqSim's VFP generation framework:

1. **FluidMagicInput** — imports reference fluid and configures GOR/WC ranges
2. **RecombinationFlashGenerator** — generates physically consistent fluids at any GOR and water cut by recombining separated gas and oil phases
3. **MultiScenarioVFPGenerator** — sweeps the 4D parameter space (rate × pressure × WC × GOR) with parallel execution
4. **Eclipse VFPEXP export** — writes tables in the format consumed by reservoir simulators

We then extend to field development digital twins that unify PVT, reservoir, well, and process modeling into a single workflow.

### 28.1.1 Why Traditional VFP Fails

Consider a typical North Sea oil field. At initial conditions, the reservoir produces undersaturated oil with:
- GOR = 200 Sm³/Sm³
- Water cut = 2%
- Reservoir pressure = 380 bara (well above bubble point at 250 bara)

A VFP table generated at these conditions works well for the first few years. But after 10 years:
- GOR = 1500 Sm³/Sm³ (reservoir below bubble point, free gas in reservoir)
- Water cut = 35% (water injection breakthrough)
- Reservoir pressure = 220 bara

The original VFP table now underestimates wellhead pressure loss (because the actual fluid is lighter with more gas but carries more water) and gives wrong operating points in the reservoir simulator. The production forecast diverges from reality.

**The solution:** Generate VFP tables that include GOR and water cut as additional dimensions, so the reservoir simulator can interpolate to the correct fluid conditions at each timestep.

### 28.1.2 The Multi-Scenario VFP Workflow

The workflow has five stages:

1. **Reference fluid import** — from Eclipse E300 (FluidMagic), PVT report, or NeqSim fluid definition
2. **Phase separation** — flash the reference fluid at standard conditions to get gas and oil compositions
3. **Recombination** — mix gas and oil at different ratios to generate fluids at target GOR values, then add water for target water cuts
4. **Process simulation** — for each (rate, pressure, WC, GOR) combination, run the well/pipeline process model to find the required inlet pressure
5. **Export** — write the 4D VFP table in Eclipse VFPEXP format

```text
Reference Fluid ──→ FluidMagicInput ──→ RecombinationFlashGenerator
                         │                         │
                    GOR/WC ranges            Fluid at each
                                            (GOR, WC) point
                                                 │
                                                 ▼
                              MultiScenarioVFPGenerator
                                    │
                            4D sweep: rate × THP × WC × GOR
                                    │
                                    ▼
                               VFPTable ──→ Eclipse VFPEXP export
```

---

## 28.2 Multi-Scenario VFP Generation

### 28.2.1 FluidMagicInput: Reference Fluid Configuration

The `FluidMagicInput` class is the entry point for VFP generation. It holds the reference fluid composition and configures the GOR and water cut ranges to explore.

**From an Eclipse E300 file** (the most common workflow):

**Execution scope:** requires the named local E300 fluid file with a validated composition and characterization.

```java pattern: requires a validated local FLUID.E300 reference-fluid file
import neqsim.process.util.optimizer.FluidMagicInput;
import java.nio.file.Paths;

// Import reference fluid from E300/FluidMagic export
FluidMagicInput input = FluidMagicInput.fromE300File(Paths.get("FLUID.E300"));

// Configure ranges from Eclipse 100 simulation results
// GOR range from FGOR summary vector
input.setGORRange(250, 10000);   // Sm3/Sm3

// Water cut range from FWCT summary vector
input.setWaterCutRange(0.05, 0.60);  // fraction

// Number of sampling points
input.setNumberOfGORPoints(6);
input.setNumberOfWaterCutPoints(5);

// GOR spacing: LOGARITHMIC recommended for wide ranges
input.setGorSpacing(FluidMagicInput.GORSpacing.LOGARITHMIC);

// Flash to standard conditions to separate gas and oil
input.separateToStandardConditions();
```

**From a NeqSim fluid** (when no E300 file is available):

```java
import neqsim.process.util.optimizer.FluidMagicInput;
import neqsim.thermo.system.SystemInterface;
import neqsim.thermo.system.SystemSrkEos;

// Create reference fluid
SystemInterface refFluid = new SystemSrkEos(273.15 + 80.0, 200.0);
refFluid.addComponent("nitrogen", 0.5);
refFluid.addComponent("CO2", 2.0);
refFluid.addComponent("methane", 65.0);
refFluid.addComponent("ethane", 8.0);
refFluid.addComponent("propane", 5.0);
refFluid.addComponent("i-butane", 1.5);
refFluid.addComponent("n-butane", 3.0);
refFluid.addComponent("n-pentane", 2.0);
refFluid.addComponent("n-hexane", 1.5);
refFluid.addComponent("n-heptane", 4.0);
refFluid.addComponent("n-octane", 3.5);
refFluid.addComponent("n-decane", 2.0);
refFluid.addComponent("water", 2.0);
refFluid.setMixingRule("classic");
refFluid.setMultiPhaseCheck(true);

// Build FluidMagicInput from fluid
FluidMagicInput input = FluidMagicInput.builder()
    .referenceFluid(refFluid)
    .gorRange(200, 8000)
    .waterCutRange(0.02, 0.50)
    .numberOfGORPoints(6)
    .numberOfWaterCutPoints(5)
    .build();

input.separateToStandardConditions();
```

### 28.2.2 RecombinationFlashGenerator: Phase Recombination

The `RecombinationFlashGenerator` creates physically consistent fluids at any GOR and water cut by recombining the separated gas and oil phases from the reference fluid.

**The recombination algorithm:**

Starting with the gas phase (composition $y_i$, molar volume $V_g^{std}$) and oil phase (composition $x_i$, molar volume $V_o^{std}$) at standard conditions:

1. **Calculate moles ratio for target GOR:**

$$
\frac{n_{gas}}{n_{oil}} = \frac{\text{GOR}_{target}}{\text{GOR}_{ref}} \cdot \frac{n_{gas,ref}}{n_{oil,ref}}
$$

where the reference GOR comes from the original flash at standard conditions.

2. **Mix gas and oil:**

$$
z_i = \frac{n_{gas} \cdot y_i + n_{oil} \cdot x_i}{n_{gas} + n_{oil}}
$$

3. **Add water for target water cut:**

$$
n_{water} = \frac{\text{WC} \cdot Q_{liquid}}{(1 - \text{WC}) \cdot V_w^{std} \cdot \rho_w}
$$

4. **Flash the recombined fluid** at the target temperature and pressure to get the feed stream composition.

This approach is physically meaningful because it mimics what happens in the reservoir:
- **Low GOR** = high drawdown, more liquid production relative to gas
- **High GOR** = gas cap expansion or depleted reservoir, more gas relative to liquid
- **Higher water cut** = aquifer encroachment, additional water mixed with hydrocarbon

**Code example:**

```java
import neqsim.process.util.optimizer.RecombinationFlashGenerator;

RecombinationFlashGenerator flashGen = new RecombinationFlashGenerator(input);

// Generate a fluid at GOR = 1500 Sm3/Sm3, WC = 20%
SystemInterface fluid = flashGen.generateFluid(
    1500.0,     // target GOR [Sm3/Sm3]
    0.20,       // water cut [fraction]
    10000.0,    // mass-flow normalization [kg/hr]; this is not a stock-tank liquid rate
    353.15,     // temperature [K] (80°C)
    50.0);      // pressure [bara]

// The fluid cache avoids regenerating the same composition
String stats = flashGen.getCacheStatistics();
```

### 28.2.3 MultiScenarioVFPGenerator: 4D VFP Generation

The `MultiScenarioVFPGenerator` sweeps the four-dimensional parameter space and finds the required inlet pressure for each combination:

**Table dimensions:**

| Dimension | Symbol | Typical Range | Points |
|-----------|--------|--------------|--------|
| Flow rate | $Q$ | 1,000–80,000 Sm³/d | 6–10 |
| Outlet pressure (THP) | $P_{out}$ | 20–100 bara | 4–6 |
| Water cut | WC | 0.02–0.60 | 4–6 |
| GOR | GOR | 200–10,000 Sm³/Sm³ | 5–8 |

Total points: 8 × 5 × 5 × 6 = **1,200** process simulations.

**The binary search algorithm:**

For each (rate, THP, WC, GOR) combination, the generator finds the minimum inlet pressure $P_{in}$ that achieves the target flow rate at the specified outlet pressure. It uses binary search:

1. Set $P_{low}$ = `minInletPressure`, $P_{high}$ = `maxInletPressure`
2. Try $P_{mid} = (P_{low} + P_{high}) / 2$
3. Run the process simulation with feed at $P_{mid}$
4. If outlet pressure > target THP: $P_{high} = P_{mid}$ (too much pressure)
5. If outlet pressure < target THP: $P_{low} = P_{mid}$ (not enough pressure)
6. Repeat until $|P_{high} - P_{low}| <$ `pressureTolerance`

If the process cannot achieve the target flow at any inlet pressure, the point is marked as **infeasible**.

**Setting up the generator:**

```java
import neqsim.process.util.optimizer.MultiScenarioVFPGenerator;
import neqsim.process.processmodel.ProcessSystem;
import java.util.function.Supplier;

// Process factory: creates a fresh process for each parallel worker
Supplier<ProcessSystem> processFactory = () -> {
    // Build a representative process model (well + flowline + riser)
    SystemInterface fluid = new SystemSrkEos(273.15 + 80.0, 200.0);
    fluid.addComponent("methane", 70.0);
    fluid.addComponent("ethane", 8.0);
    fluid.addComponent("propane", 4.0);
    fluid.addComponent("n-butane", 2.0);
    fluid.addComponent("n-heptane", 8.0);
    fluid.addComponent("n-decane", 5.0);
    fluid.addComponent("water", 3.0);
    fluid.setMixingRule("classic");
    fluid.setMultiPhaseCheck(true);

    Stream feed = new Stream("Feed", fluid);
    feed.setFlowRate(10000.0, "kg/hr");
    PipeBeggsAndBrills tubing = new PipeBeggsAndBrills("Tubing", feed);
    tubing.setLength(2500.0);
    tubing.setAngle(90.0);
    tubing.setDiameter(0.1016);
    tubing.setNumberOfIncrements(30);

    PipeBeggsAndBrills flowline = new PipeBeggsAndBrills("Flowline", tubing.getOutletStream());
    flowline.setLength(10000.0);
    flowline.setAngle(0.0);
    flowline.setDiameter(0.2032);
    flowline.setNumberOfIncrements(20);

    ProcessSystem process = new ProcessSystem();
    process.add(feed);
    process.add(tubing);
    process.add(flowline);
    process.add(new Stream("Export Outlet", flowline.getOutletStream()));
    return process;
};

// Create VFP generator
MultiScenarioVFPGenerator vfpGen = new MultiScenarioVFPGenerator(
    processFactory,
    "Feed",        // inlet stream name
    "Export Outlet" // actual outlet stream (pressure target)
);

// Attach flash generator for fluid composition at each GOR/WC
vfpGen.setFlashGenerator(flashGen);

// Configure table axes
vfpGen.setFlowRateUnit("kg/hr");
vfpGen.setInletTemperature(358.15);
vfpGen.setFlowRates(new double[]{5000.0,10000.0,20000.0});
vfpGen.setOutletPressures(new double[]{30.0,50.0});
vfpGen.setWaterCuts(new double[]{0.05});
vfpGen.setGORs(new double[]{300.0,1000.0});




// Binary search settings
vfpGen.setMinInletPressure(20.0);    // bara
vfpGen.setMaxInletPressure(350.0);   // bara
vfpGen.setPressureTolerance(0.5);    // bara

// Parallel execution
vfpGen.setEnableParallel(false);
vfpGen.setNumberOfWorkers(8);

// Generate
MultiScenarioVFPGenerator.VFPTable table = vfpGen.generateVFPTable();
```

### 28.2.4 VFPTable: Results Access and Analysis

The `VFPTable` class stores the 4D array of inlet pressures:

```java
// Access individual points
double requiredInletPressure = table.getBHP(2, 1, 0, 1);
// Legacy getter name; this is the inlet pressure for the declared process model.

// Check feasibility
int feasible = table.getFeasibleCount();
int total = table.getTotalPoints();
logger.info(String.format("Feasible: %d/%d (%.1f%%)%n",
    feasible, total, 100.0 * feasible / total));

// Print a slice (fixed WC and GOR)
table.printSlice(0, 1);  // WC index 0, GOR index 3
```

### 28.2.5 Eclipse VFPEXP Format Export

The generated table is exported in Eclipse VFPEXP format for direct use in reservoir simulators:

```java
// Preserve the process-screening semantics in the file name and content.
java.nio.file.Files.write(Paths.get("production_screening.txt"),
    vfpGen.toDiagnosticString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
```

The exported file contains:

```text
-- VFP table generated by NeqSim MultiScenarioVFPGenerator
-- Date: 2026-04-18
-- Reference fluid: FLUID.E300
-- Process: Tubing (2500m) + Flowline (10km)
VFPEXP
-- Table 1
1  2026-04-18  'OIL'  'SM3/DAY'  'BARA'  'BARA'  /
-- Flow rates (Sm3/d)
 5000 10000 20000 30000 50000 70000 /
-- THP values (bara)
 30 40 50 60 80 /
-- Water cut values (fraction)
 0.05 0.15 0.30 0.45 0.60 /
-- GOR values (Sm3/Sm3)
 300 600 1200 2500 5000 10000 /
-- BHP values (bara) for each (rate, THP, WC, GOR) combination
...
```

---

## 28.3 Reservoir Simulation Coupling

### 28.3.1 Eclipse VFPEXP Integration

The VFPEXP keyword in Eclipse defines the relationship between wellbore flowing pressure, tubing head pressure, flow rate, water cut, and GOR. The reservoir simulator interpolates within this table at each timestep to determine the well operating point.

**Eclipse DATA file integration:**

```text
-- Include the NeqSim-generated VFP table
INCLUDE
  'production_vfp.inc' /

-- Reference the VFP table in well control
WCONPROD
-- Well    Status  Mode   Rate   Resv   BHP    THP   VFP#
  'PROD-1'  OPEN   ORAT   5000   1*     100    30     1   /
  'PROD-2'  OPEN   ORAT   3000   1*     100    40     1   /
/
```

### 28.3.2 Automatic Interpolation

The reservoir simulator interpolates across all four VFP dimensions at each timestep:

$$
P_{BHP} = f(Q, P_{THP}, \text{WC}(t), \text{GOR}(t))
$$

where $\text{WC}(t)$ and $\text{GOR}(t)$ change with time as the reservoir depletes. Multi-linear interpolation is used:

$$
P_{BHP} \approx \sum_{i,j,k,l} w_{ijkl} \cdot P_{BHP}^{(i,j,k,l)}
$$

where $w_{ijkl}$ are the interpolation weights determined by the current well conditions relative to the table grid points.

This means the VFP table must have sufficient resolution in each dimension to avoid interpolation errors:

| Dimension | Minimum Points | Recommended Points | Rationale |
|-----------|---------------|-------------------|-----------|
| Flow rate | 5 | 8–10 | Non-linear friction |
| THP | 3 | 5–6 | Linear-ish behavior |
| Water cut | 4 | 5–6 | Non-linear density/viscosity |
| GOR | 4 | 6–8 | Highly non-linear phase behavior |

### 28.3.3 WCONPROD Well Control

The `WCONPROD` keyword specifies well operating mode and constraints. The VFP table number links each well to its performance model:

- **ORAT mode:** Target oil rate, BHP from VFP table
- **GRAT mode:** Target gas rate
- **LRAT mode:** Target liquid rate (oil + water)
- **RESV mode:** Target reservoir voidage rate
- **BHP mode:** Fixed bottomhole pressure (VFP gives achievable rate)

---

## 28.4 Fluid Property Sensitivity Across GOR and Water Cut

### 28.4.1 How Fluid Properties Change with GOR

Understanding the physical basis for multi-scenario VFP is essential for field development engineers. As GOR changes, the fluid properties change dramatically:

**Density:** At low GOR (mostly oil), the mixture density is high (600–800 kg/m³). As GOR increases, the gas fraction rises, and the mixture density drops. This reduces hydrostatic head in the tubing (less pressure support from the fluid column) but also reduces frictional losses.

$$
\rho_m = \rho_l H_l + \rho_g (1 - H_l)
$$

where $H_l$ is the liquid holdup (fraction of pipe cross-section occupied by liquid), which depends on flow regime, velocity, and pipe inclination.

**Viscosity:** Oil viscosity is typically 0.5–50 cP at downhole conditions. Gas viscosity is much lower (0.01–0.03 cP). As GOR increases, the effective mixture viscosity decreases, reducing friction but also changing the flow regime.

**Surface tension:** The gas-oil surface tension decreases as GOR increases (more light components in the oil phase). Lower surface tension means smaller bubbles, more dispersed flow, and different holdup correlations.

**Phase envelope:** At high GOR, the fluid phase envelope shifts toward the gas side. The cricondenbar and cricondentherm change, affecting the conditions at which liquid drops out in the pipeline (retrograde condensation). This is critical for pipeline sizing and slug catcher design.

### 28.4.2 How Fluid Properties Change with Water Cut

Water cut affects the flow differently than GOR:

**Emulsion viscosity:** Oil-water mixtures form emulsions with viscosities far higher than either pure phase. At the inversion point (typically WC = 50–70%), the emulsion viscosity can peak at 10–100× the oil viscosity:

$$
\mu_{emulsion} = \mu_c \cdot \left(1 + 2.5 \phi + 6.2 \phi^2\right)
$$

where $\mu_c$ is the continuous phase viscosity and $\phi$ is the dispersed phase volume fraction (Krieger-Dougherty model).

**Liquid loading:** Water is denser than oil (1000 vs. 700–900 kg/m³). Higher water cut increases the liquid density and thus the hydrostatic pressure drop in vertical tubing. This increases the BHP required to lift fluids to the surface.

**Slugging tendency:** Water cut changes affect the flow regime. At intermediate water cuts (20–50%), severe slugging can occur, particularly in hilly terrain or riser bases. The VFP table captures the average steady-state behavior, but slugging transients require dynamic simulation.

### 28.4.3 Combined Effects: The VFP Surface Shape

The VFP surface (BHP vs. rate at fixed THP) has a characteristic shape that changes with GOR and water cut:

- **Low GOR, low WC:** Nearly linear VFP curve. BHP increases smoothly with rate.
- **High GOR, low WC:** Flatter curve (gas-dominated flow has less friction). The minimum stable rate (liquid loading limit) appears.
- **Low GOR, high WC:** Steeper curve (heavy emulsion). Higher BHP needed at all rates.
- **High GOR, high WC:** Complex behavior — gas lift effect from high GOR partially compensates for the heavier water column.

Understanding these shapes helps reservoir engineers:
1. Predict when wells will die (BHP exceeds reservoir pressure)
2. Identify the need for artificial lift (gas lift or ESP)
3. Optimize choke settings to maximize field production

## 28.5 VFP Configuration and Best Practices

### 28.5.1 GOR Range Selection

The GOR range should span from initial conditions to the highest GOR expected at end of field life:

- **Minimum GOR:** Initial GOR from PVT report (or slightly lower to handle transient startup)
- **Maximum GOR:** From reservoir simulation forecast at abandonment

**GOR spacing options:**

**LINEAR** — equal spacing between values:

$$
\text{GOR}_i = \text{GOR}_{min} + i \cdot \frac{\text{GOR}_{max} - \text{GOR}_{min}}{N - 1}
$$

Best when the GOR range is narrow (e.g., 500–2000 Sm³/Sm³).

**LOGARITHMIC** — geometric spacing (recommended for wide ranges):

$$
\text{GOR}_i = \text{GOR}_{min} \cdot \left(\frac{\text{GOR}_{max}}{\text{GOR}_{min}}\right)^{i/(N-1)}
$$

Best when GOR spans an order of magnitude or more (e.g., 200–10,000 Sm³/Sm³), because:
- Phase behavior changes rapidly at low GOR (near bubble point)
- Phase behavior changes slowly at very high GOR (mostly gas)

```java
// LOGARITHMIC spacing for wide GOR range
input.setGorSpacing(FluidMagicInput.GORSpacing.LOGARITHMIC);
input.setGORRange(200, 10000);
input.setNumberOfGORPoints(8);
// Eight geometrically spaced values including both endpoints.
```

### 28.4.2 Water Cut Range Configuration

Water cut ranges from initial (often near zero) to maximum expected:

```java
input.setWaterCutRange(0.02, 0.60);
input.setNumberOfWaterCutPoints(5);
// Generates: 0.02, 0.165, 0.31, 0.455, 0.60
```

**Important considerations:**
- Include a near-zero water cut for initial conditions
- Include the economic water cut limit (typically 70–90%)
- Water cut affects density, viscosity, and emulsion formation

### 28.4.3 Pressure Search Parameters

The binary search for inlet pressure requires bounds:

```java
vfpGen.setMinInletPressure(15.0);     // bara — minimum physically possible
vfpGen.setMaxInletPressure(400.0);    // bara — above reservoir pressure
vfpGen.setPressureTolerance(0.5);     // bara — accuracy of result
```

**Guidelines:**
- `minInletPressure` should be below the minimum expected wellhead pressure
- `maxInletPressure` should be above the initial reservoir pressure
- `pressureTolerance` of 0.5–1.0 bara is usually sufficient
- Tighter tolerance increases computation time (more binary search iterations)

### 28.4.4 Performance Guidelines

The computation time depends on the number of points and the complexity of the process model:

| Total Points | Process Complexity | Sequential Time | Parallel Time (8 cores) |
|-------------|-------------------|----------------|----------------------|
| 500 | Simple (tubing only) | ~5 min | ~1 min |
| 1,000 | Medium (tubing + flowline) | ~15 min | ~3 min |
| 2,000 | Complex (full process) | ~60 min | ~10 min |
| 5,000 | Complex with recycle | ~3 hr | ~30 min |

**Optimization tips:**
- Use `setEnableParallel(true)` for production runs
- The `RecombinationFlashGenerator` caches fluids — repeated (GOR, WC) pairs are free
- Start with a coarse grid (few points per dimension) to validate the process model
- Refine the grid in regions where the VFP surface changes rapidly

### 28.4.5 Input Validation

Before launching a large VFP generation run, validate the setup:

```java
// Validate that the process runs successfully at a few test points
ProcessSystem testProcess = processFactory.get();
testProcess.run();
double testPressure = ((StreamInterface) testProcess.getUnit("Export Outlet")).getPressure("bara");
logger.info("Test outlet pressure: " + testPressure + " bara");

// Verify the flash generator produces reasonable fluids
SystemInterface testFluid = flashGen.generateFluid(1000.0, 0.20, 10000.0, 353.15, 50.0);
testFluid.initProperties();
logger.info("Test fluid components: " + testFluid.getNumberOfComponents());
logger.info("Test fluid density: " + testFluid.getDensity("kg/m3") + " kg/m3");
```

---

## 28.5 Use Cases

### 28.5.1 Facility Debottlenecking Across Fluid Scenarios

As field fluid properties change, facility bottlenecks shift. A separator designed for GOR = 500 may become undersized at GOR = 3000 (much more gas). Multi-scenario VFP tables reveal:

- **At what GOR does the compressor become the bottleneck?** — The VFP table shows the maximum rate achievable at each GOR
- **How does water cut affect export pipeline capacity?** — Higher WC means more liquid holdup and higher friction
- **When should the choke setting change?** — VFP curves at different WC/GOR show the optimal pressure split

### 28.5.2 Well Design Optimization

Tubing size selection depends on the range of expected conditions:

```java
// Compare explicit internal diameters; nominal pipe sizes require wall-thickness data.
for (double diameter : new double[]{0.076, 0.102}) {
    ProcessSystem diameterCase = processFactory.get();
    ((PipeBeggsAndBrills) diameterCase.getUnit("Tubing")).setDiameter(diameter);
    MultiScenarioVFPGenerator diameterGenerator = new MultiScenarioVFPGenerator(diameterCase, "Feed", "Export Outlet");
    diameterGenerator.setFlashGenerator(flashGen);
    diameterGenerator.setFlowRateUnit("kg/hr");
    diameterGenerator.setInletTemperature(358.15);
    diameterGenerator.setFlowRates(new double[]{5000.0,10000.0,20000.0});
    diameterGenerator.setOutletPressures(new double[]{30.0,50.0});
    diameterGenerator.setWaterCuts(new double[]{0.05});
    diameterGenerator.setGORs(new double[]{300.0,1000.0});
    diameterGenerator.setMinInletPressure(20.0);
    diameterGenerator.setMaxInletPressure(350.0);
    diameterGenerator.setEnableParallel(false);
    MultiScenarioVFPGenerator.VFPTable diameterTable = diameterGenerator.generateVFPTable();
    logger.info("Internal diameter {} m: {} of {} feasible sampled points", diameter,
        diameterTable.getFeasibleCount(), diameterTable.getTotalPoints());
}
```

The larger tubing will have more feasible points (lower friction), but the smaller tubing may be preferred for low rates (avoid liquid loading).

### 28.5.3 Production Forecasting with Changing Fluid Properties

The VFP table enables accurate production forecasting by the reservoir simulator:

1. At each timestep, the simulator calculates the current GOR and water cut from the reservoir model
2. It interpolates the VFP table to get $P_{BHP}(Q, P_{THP}, WC, GOR)$
3. The intersection of the VFP curve with the IPR gives the well operating point
4. This determines the production rate, which feeds back to the reservoir model

Without multi-scenario VFP, the simulator uses a single VFP curve that becomes increasingly wrong — leading to optimistic production forecasts in the early years and pessimistic forecasts later.

---

## 28.6 Complete VFP Generation Example

### 28.6.1 Full Java Example

```java
import neqsim.process.util.optimizer.FluidMagicInput;
import neqsim.process.util.optimizer.RecombinationFlashGenerator;
import neqsim.process.util.optimizer.MultiScenarioVFPGenerator;
import neqsim.process.equipment.stream.Stream;
import neqsim.process.equipment.pipeline.PipeBeggsAndBrills;
import neqsim.process.processmodel.ProcessSystem;
import neqsim.thermo.system.SystemInterface;
import neqsim.thermo.system.SystemSrkEos;
import java.util.function.Supplier;

public class VFPGenerationExample {
    private static final org.apache.logging.log4j.Logger logger = org.apache.logging.log4j.LogManager.getLogger(VFPGenerationExample.class);

    /** Process factory that creates a fresh well + flowline model. */
    static Supplier<ProcessSystem> createProcessFactory() {
        return () -> {
            SystemInterface fluid = new SystemSrkEos(273.15 + 85.0, 200.0);
            fluid.addComponent("nitrogen", 0.4);
            fluid.addComponent("CO2", 1.8);
            fluid.addComponent("methane", 68.0);
            fluid.addComponent("ethane", 7.5);
            fluid.addComponent("propane", 4.5);
            fluid.addComponent("i-butane", 1.0);
            fluid.addComponent("n-butane", 2.5);
            fluid.addComponent("n-pentane", 1.5);
            fluid.addComponent("n-hexane", 1.2);
            fluid.addComponent("n-heptane", 4.5);
            fluid.addComponent("n-octane", 3.5);
            fluid.addComponent("n-decane", 2.1);
            fluid.addComponent("water", 1.5);
            fluid.setMixingRule("classic");
            fluid.setMultiPhaseCheck(true);

            Stream feed = new Stream("Feed", fluid);
    feed.setFlowRate(10000.0, "kg/hr");
            feed.setFlowRate(30000.0, "kg/hr");
            feed.setTemperature(85.0, "C");
            feed.setPressure(200.0, "bara");

            // Well tubing (2800 m vertical)
            PipeBeggsAndBrills tubing =
                new PipeBeggsAndBrills("Tubing", feed);
            tubing.setLength(2800.0);
            tubing.setAngle(90.0);
            tubing.setDiameter(0.1016);
            tubing.setPipeWallRoughness(2.5e-5);
            tubing.setNumberOfIncrements(25);

            // Subsea flowline (12 km)
            PipeBeggsAndBrills flowline =
                new PipeBeggsAndBrills("Export", tubing.getOutletStream());
            flowline.setLength(12000.0);
            flowline.setAngle(0.0);
            flowline.setDiameter(0.2032);
            flowline.setPipeWallRoughness(4.5e-5);
            flowline.setNumberOfIncrements(20);

            ProcessSystem process = new ProcessSystem();
            process.add(feed);
            process.add(tubing);
            process.add(flowline);
    process.add(new Stream("Export Outlet", flowline.getOutletStream()));
            return process;
        };
    }

    public static void main(String[] args) throws Exception {
        // Step 1: Reference fluid
        SystemInterface refFluid = new SystemSrkEos(273.15 + 85.0, 200.0);
        refFluid.addComponent("nitrogen", 0.4);
        refFluid.addComponent("CO2", 1.8);
        refFluid.addComponent("methane", 68.0);
        refFluid.addComponent("ethane", 7.5);
        refFluid.addComponent("propane", 4.5);
        refFluid.addComponent("i-butane", 1.0);
        refFluid.addComponent("n-butane", 2.5);
        refFluid.addComponent("n-pentane", 1.5);
        refFluid.addComponent("n-hexane", 1.2);
        refFluid.addComponent("n-heptane", 4.5);
        refFluid.addComponent("n-octane", 3.5);
        refFluid.addComponent("n-decane", 2.1);
        refFluid.addComponent("water", 1.5);
        refFluid.setMixingRule("classic");
        refFluid.setMultiPhaseCheck(true);

        // Step 2: Configure FluidMagicInput
        FluidMagicInput input = new FluidMagicInput(refFluid);
        input.setGORRange(300, 8000);
        input.setWaterCutRange(0.05, 0.55);
        input.setNumberOfGORPoints(6);
        input.setNumberOfWaterCutPoints(5);
        input.setGorSpacing(FluidMagicInput.GORSpacing.LOGARITHMIC);
        input.separateToStandardConditions();

        // Step 3: Flash generator
        RecombinationFlashGenerator flashGen =
            new RecombinationFlashGenerator(input);

        // Step 4: VFP generator
        MultiScenarioVFPGenerator vfpGen = new MultiScenarioVFPGenerator(
            createProcessFactory(), "Feed", "Export Outlet");
        vfpGen.setFlashGenerator(flashGen);

        vfpGen.setFlowRateUnit("kg/hr");
vfpGen.setInletTemperature(358.15);
vfpGen.setFlowRates(new double[]{5000.0,10000.0,20000.0});
vfpGen.setOutletPressures(new double[]{30.0,50.0});
vfpGen.setWaterCuts(new double[]{0.05});
vfpGen.setGORs(new double[]{300.0,1000.0});
        
        
        

        vfpGen.setMinInletPressure(20.0);
        vfpGen.setMaxInletPressure(350.0);
        vfpGen.setPressureTolerance(0.5);
        vfpGen.setEnableParallel(false);
        vfpGen.setNumberOfWorkers(8);

        // Step 5: Generate
        MultiScenarioVFPGenerator.VFPTable table =
            vfpGen.generateVFPTable();

        logger.info(String.format("Feasible: %d/%d%n",
            table.getFeasibleCount(), table.getTotalPoints()));

        // Step 6: Print a slice
        table.printSlice(0, 1);  // WC=5%, GOR=1000

        // Step 7: Export diagnostic process screening, not a well VFP deck
        java.nio.file.Files.write(java.nio.file.Paths.get("production_screening.txt"),
            vfpGen.toDiagnosticString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
        logger.info("Process screening diagnostics exported to production_screening.txt");
    }
}
```

### 28.6.2 Full Python Example

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import json

# Import classes
FluidMagicInput = jneqsim.process.util.optimizer.FluidMagicInput
RecombinationFlashGenerator = jneqsim.process.util.optimizer.RecombinationFlashGenerator
MultiScenarioVFPGenerator = jneqsim.process.util.optimizer.MultiScenarioVFPGenerator
Stream = jneqsim.process.equipment.stream.Stream
PipeBeggsAndBrills = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
SystemSrkEos = jneqsim.thermo.system.SystemSrkEos

# --- Step 1: Reference Fluid ---
ref_fluid = SystemSrkEos(273.15 + 85.0, 200.0)
ref_fluid.addComponent("nitrogen", 0.4)
ref_fluid.addComponent("CO2", 1.8)
ref_fluid.addComponent("methane", 68.0)
ref_fluid.addComponent("ethane", 7.5)
ref_fluid.addComponent("propane", 4.5)
ref_fluid.addComponent("i-butane", 1.0)
ref_fluid.addComponent("n-butane", 2.5)
ref_fluid.addComponent("n-pentane", 1.5)
ref_fluid.addComponent("n-hexane", 1.2)
ref_fluid.addComponent("n-heptane", 4.5)
ref_fluid.addComponent("n-octane", 3.5)
ref_fluid.addComponent("n-decane", 2.1)
ref_fluid.addComponent("water", 1.5)
ref_fluid.setMixingRule("classic")
ref_fluid.setMultiPhaseCheck(True)

# --- Step 2: FluidMagicInput ---
fmi = FluidMagicInput(ref_fluid)
fmi.setGORRange(300, 8000)
fmi.setWaterCutRange(0.05, 0.55)
fmi.setNumberOfGORPoints(6)
fmi.setNumberOfWaterCutPoints(5)
fmi.setGorSpacing(FluidMagicInput.GORSpacing.LOGARITHMIC)
fmi.separateToStandardConditions()

# --- Step 3: Flash Generator ---
flash_gen = RecombinationFlashGenerator(fmi)

# --- Step 4: Process Factory (Python lambda wrapping Java) ---
def create_process():
    fluid = SystemSrkEos(273.15 + 85.0, 200.0)
    fluid.addComponent("nitrogen", 0.4)
    fluid.addComponent("CO2", 1.8)
    fluid.addComponent("methane", 68.0)
    fluid.addComponent("ethane", 7.5)
    fluid.addComponent("propane", 4.5)
    fluid.addComponent("i-butane", 1.0)
    fluid.addComponent("n-butane", 2.5)
    fluid.addComponent("n-pentane", 1.5)
    fluid.addComponent("n-hexane", 1.2)
    fluid.addComponent("n-heptane", 4.5)
    fluid.addComponent("n-octane", 3.5)
    fluid.addComponent("n-decane", 2.1)
    fluid.addComponent("water", 1.5)
    fluid.setMixingRule("classic")
    fluid.setMultiPhaseCheck(True)

    feed = Stream("Feed", fluid)
    feed.setFlowRate(30000.0, "kg/hr")
    feed.setTemperature(85.0, "C")
    feed.setPressure(200.0, "bara")

    tubing = PipeBeggsAndBrills("Tubing", feed)
    tubing.setLength(2800.0)
    tubing.setAngle(90.0)
    tubing.setDiameter(0.1016)
    tubing.setPipeWallRoughness(2.5e-5)
    tubing.setNumberOfIncrements(25)

    flowline = PipeBeggsAndBrills("Flowline", tubing.getOutletStream())
    flowline.setLength(12000.0)
    flowline.setAngle(0.0)
    flowline.setDiameter(0.2032)
    flowline.setPipeWallRoughness(4.5e-5)
    flowline.setNumberOfIncrements(20)

    process = ProcessSystem()
    process.add(feed)
    process.add(tubing)
    process.add(flowline)
    process.add(Stream("Export", flowline.getOutletStream()))
    return process

# For sequential execution, pass a single process
process = create_process()
vfp_gen = MultiScenarioVFPGenerator(process, "Feed", "Export")
vfp_gen.setFlashGenerator(flash_gen)
vfp_gen.setFlowRateUnit("kg/hr")
vfp_gen.setInletTemperature(358.15)

# Configure axes
import jpype
vfp_gen.setFlowRates(jpype.JArray(jpype.JDouble)([5000.0, 10000.0, 20000.0]))
vfp_gen.setOutletPressures(jpype.JArray(jpype.JDouble)([30.0, 50.0]))
vfp_gen.setWaterCuts(jpype.JArray(jpype.JDouble)([0.05]))
vfp_gen.setGORs(jpype.JArray(jpype.JDouble)([300.0, 1000.0]))

vfp_gen.setMinInletPressure(20.0)
vfp_gen.setMaxInletPressure(350.0)
vfp_gen.setPressureTolerance(1.0)
vfp_gen.setEnableParallel(False)  # Sequential for Python

# Generate
table = vfp_gen.generateVFPTable()
print(f"Feasible: {table.getFeasibleCount()}/{table.getTotalPoints()}")

# Print a slice
table.printSlice(0, 1)  # WC=5%, GOR=1000

# Export
from pathlib import Path
Path("production_screening.txt").write_text(str(vfp_gen.toDiagnosticString()), encoding="utf-8")
print("Process screening diagnostics exported")

feed = process.getUnit("Feed")
fluid = ref_fluid
create_base_process = create_process
```

---

## 28.8 Field Development Digital Twin

### 28.8.1 The Concept of a Field Development Digital Twin

A field development digital twin is not a single model — it is a **connected system of models** that reflects the physical field at every layer. The twin continuously evolves as the field matures, incorporating new data from drilling, production, and maintenance.

The key distinction from traditional field planning:

| Traditional Approach | Digital Twin Approach |
|---------------------|----------------------|
| Static VFP tables | Dynamic VFP tables updated with current fluid |
| Manual model updates | Automated model calibration against production data |
| Separate PVT/reservoir/well/process models | Integrated model with shared state |
| Quarterly production forecasts | Continuous forecasting |
| Reactive optimization | Proactive, model-based optimization |

### 28.8.2 Unified PVT → Reservoir → Well → Process Workflow

A field development digital twin connects all the modeling layers:

```text
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐
│   PVT Model     │────→│ Reservoir Model   │────→│  Well Model    │
│ (EOS, kij, Tc)  │     │ (Eclipse/OPM)     │     │ (VFP tables)   │
└─────────────────┘     └──────────────────┘     └────────────────┘
                                                        │
                                                        ▼
                         ┌──────────────────┐     ┌────────────────┐
                         │  Facility Model  │←────│ Network Model  │
                         │  (ProcessSystem) │     │ (LoopedPipe)   │
                         └──────────────────┘     └────────────────┘
                                │
                                ▼
                         ┌──────────────────┐
                         │    Economics      │
                         │ (NPV, Cash Flow) │
                         └──────────────────┘
```

**The feedback loop:** As the reservoir depletes, the VFP tables change. The well model feeds new rates to the facility model, which determines if the facility can handle the new fluid. The economics model evaluates whether the field remains profitable.

### 28.8.3 Model Calibration and History Matching

The digital twin must be calibrated against actual production data. This involves:

1. **PVT calibration:** Match EOS predictions against PVT lab data (differential liberation, constant composition expansion, separator tests)
2. **Well model calibration:** Adjust tubing roughness, IPR productivity index, and choke discharge coefficient to match well test data
3. **Reservoir model history matching:** Adjust permeability, porosity, and aquifer strength to match observed pressure and production history
4. **Facility model validation:** Verify separator pressures, compressor duty, and export conditions against measured plant data

**Execution scope:** This integration pattern requires a qualified well model and actual well-test data. It is not a standalone validated process calculation.

```python pattern: requires a qualified well model and actual well-test data
# Example: calibrate well model against a well test
# Well test data: Q = 15,000 Sm3/d at BHP = 280 bara, WHP = 65 bara

measured_bhp = 280.0  # bara
measured_whp = 65.0   # bara
measured_rate = 15000.0  # Sm3/d

# Run NeqSim well model
feed.setFlowRate(measured_rate * 1.0, "Sm3/day")
feed.setPressure(measured_bhp, "bara")
process.run()
predicted_whp = flowline.getOutletStream().getPressure("bara")

# Calibration error
error = abs(predicted_whp - measured_whp)
print(f"Predicted WHP: {predicted_whp:.1f} bara")
print(f"Measured WHP:  {measured_whp:.1f} bara")
print(f"Error:         {error:.1f} bara")

# If error > 2 bara, adjust tubing roughness or pipe diameter
```

### 28.8.4 NetworkSolver Integration

The `LoopedPipeNetwork` from Chapter 15 can serve as the well model, directly providing the well operating points to the reservoir simulator:

**Execution scope:** This integration pattern network assembly requires field-specific nodes and verified boundary data. It is not a standalone validated process calculation.

```python pattern: network assembly requires field-specific nodes and verified boundary data
import jpype
jneqsim = jpype.JPackage("neqsim")

# Build the production network (from Chapter 15)
LoopedPipeNetwork = jneqsim.process.equipment.network.LoopedPipeNetwork
SolverType = LoopedPipeNetwork.SolverType

network = LoopedPipeNetwork("Field Network")
network.setFluidTemplate(fluid)

# Add wells, tubing, chokes, flowlines (as in Chapter 15)
# ... (well configuration code) ...

network.setSolverType(SolverType.NEWTON_RAPHSON)
network.setTolerance(1e-6)

# Time-stepping loop (simplified digital twin)
import numpy as np

years = np.arange(0, 25, 1)  # 25-year field life
reservoir_pressure = 380.0     # Initial reservoir pressure (bara)
decline_rate = 0.05            # 5% per year

results = []
for year in years:
    # Update reservoir pressure (simplified decline)
    Pr = reservoir_pressure * np.exp(-decline_rate * year)

    # Update all well IPRs with current reservoir pressure
    for well_name in ["A", "B", "C"]:
        ipr = network.getPipe(f"IPR-{well_name}")
        ipr.setReservoirPressure(Pr * 1e5)  # Convert to Pa

    # Solve network
    network.run()

    # Extract total production
    summary = network.getSolutionSummary()
    total_flow = float(summary.get("totalSinkFlow"))

    results.append({
        "year": year,
        "Pr_bara": Pr,
        "total_production_kg_s": total_flow
    })

    print(f"Year {year:2d}: Pr = {Pr:.0f} bara, "
          f"Production = {total_flow:.1f} kg/s")
```

### 28.8.5 Production Scheduling and Well Sequencing

Production scheduling optimizes the sequence and timing of well operations. Key decisions include:

- **Well start-up sequence:** Which wells to bring online first?
  - High-PI wells first → maximize early production for NPV
  - Low-WC wells first → delay water handling facility investment
  - Platform wells first → minimize subsea infrastructure cost

- **Choke management strategy:** How to adjust chokes as reservoir pressure declines?
  - Fixed choke opening → production declines naturally
  - Rate-controlled choking → maintain target rate until choke is fully open
  - Pressure-controlled → maintain minimum THP for flow assurance

- **Gas lift allocation:** How to redistribute lift gas as some wells die?
  - Marginal gas lift optimization: allocate gas to wells with highest incremental oil per unit gas
  - Total gas constraint: limited by compressor capacity

- **Workover timing:** When to pull tubing or replace ESPs?
  - When lost production × time > workover cost
  - Seasonal considerations (weather windows for subsea operations)

These decisions are made by running the network model at discrete time steps, adjusting well parameters at each step, and evaluating the economic outcome.

### 28.8.6 Concept Screening with VFP Tables

Multi-scenario VFP tables enable rapid screening of development concepts:

**Concept 1: Direct tieback to existing platform (30 km)**

```python
# Process factory: 30 km flowline + riser
def concept_1_factory():
    process = create_base_process()
    flowline = process.getUnit("Flowline")
    flowline.setLength(30000.0)
    return process

vfp_concept1 = MultiScenarioVFPGenerator(concept_1_factory(), "Feed", "Export")
vfp_concept1.setFlashGenerator(flash_gen)
vfp_concept1.setFlowRateUnit("kg/hr")
vfp_concept1.setInletTemperature(358.15)
vfp_concept1.setFlowRates(jpype.JArray(jpype.JDouble)([5000.0, 10000.0, 20000.0]))
vfp_concept1.setOutletPressures(jpype.JArray(jpype.JDouble)([30.0, 50.0]))
vfp_concept1.setWaterCuts(jpype.JArray(jpype.JDouble)([0.05]))
vfp_concept1.setGORs(jpype.JArray(jpype.JDouble)([300.0, 1000.0]))
vfp_concept1.setMinInletPressure(20.0)
vfp_concept1.setMaxInletPressure(350.0)
vfp_concept1.setEnableParallel(False)
feasible_1 = vfp_concept1.generateVFPTable().getFeasibleCount()
```

**Concept 2: Short tieback with subsea boosting (8 km)**

```python
# Process factory: subsea booster + 8 km flowline
def concept_2_factory():
    process = create_base_process()
    flowline = process.getUnit("Flowline")
    flowline.setLength(8000.0)
    # This comparison changes flowline length only; no booster is modeled.
    return process

vfp_concept2 = MultiScenarioVFPGenerator(concept_2_factory(), "Feed", "Export")
vfp_concept2.setFlashGenerator(flash_gen)
vfp_concept2.setFlowRateUnit("kg/hr")
vfp_concept2.setInletTemperature(358.15)
vfp_concept2.setFlowRates(jpype.JArray(jpype.JDouble)([5000.0, 10000.0, 20000.0]))
vfp_concept2.setOutletPressures(jpype.JArray(jpype.JDouble)([30.0, 50.0]))
vfp_concept2.setWaterCuts(jpype.JArray(jpype.JDouble)([0.05]))
vfp_concept2.setGORs(jpype.JArray(jpype.JDouble)([300.0, 1000.0]))
vfp_concept2.setMinInletPressure(20.0)
vfp_concept2.setMaxInletPressure(350.0)
vfp_concept2.setEnableParallel(False)
feasible_2 = vfp_concept2.generateVFPTable().getFeasibleCount()
```

**Concept 3: Standalone FPSO (minimal pipeline)**

```python
# Process factory: short riser only
def concept_3_factory():
    process = create_base_process()
    flowline = process.getUnit("Flowline")
    flowline.setLength(500.0)  # Riser only
    return process

vfp_concept3 = MultiScenarioVFPGenerator(concept_3_factory(), "Feed", "Export")
vfp_concept3.setFlashGenerator(flash_gen)
vfp_concept3.setFlowRateUnit("kg/hr")
vfp_concept3.setInletTemperature(358.15)
vfp_concept3.setFlowRates(jpype.JArray(jpype.JDouble)([5000.0, 10000.0, 20000.0]))
vfp_concept3.setOutletPressures(jpype.JArray(jpype.JDouble)([30.0, 50.0]))
vfp_concept3.setWaterCuts(jpype.JArray(jpype.JDouble)([0.05]))
vfp_concept3.setGORs(jpype.JArray(jpype.JDouble)([300.0, 1000.0]))
vfp_concept3.setMinInletPressure(20.0)
vfp_concept3.setMaxInletPressure(350.0)
vfp_concept3.setEnableParallel(False)
feasible_3 = vfp_concept3.generateVFPTable().getFeasibleCount()

# Compare feasibility across concepts
print(f"Concept 1 (30 km tieback):    {feasible_1} feasible points")
print(f"Concept 2 (8 km route only):   {feasible_2} feasible points")
print(f"Concept 3 (short route):             {feasible_3} feasible points")
```

The concept with the most feasible points across the full GOR/WC range will deliver the most robust production over the field life.

### 28.8.7 Late-Life Operations

Late-life field operations present unique challenges:

**High water cut** — When water cut exceeds 80–90%, the well may not be economic:

**Execution scope:** This integration pattern requires configured network tubing elements and water-cut data. It is not a standalone validated process calculation.

```python pattern: requires configured network tubing elements and water-cut data
# Check if well is economic at current water cut
for well_name in wells:
    tubing = network.getPipe(f"Tubing-{well_name}")
    wc = tubing.getWaterCut()
    flow = network.getPipeFlowRate(f"Tubing-{well_name}")
    oil_flow = flow * (1.0 - wc)

    if oil_flow < min_economic_oil_rate:
        print(f"Well {well_name}: WC={wc:.0%}, "
              f"Oil={oil_flow:.1f} kg/s — UNECONOMIC")
```

**Declining pressure** — Below a critical reservoir pressure, natural flow ceases and artificial lift becomes necessary:

$$
P_r^{critical} = P_{WH} + \Delta P_{tubing}(Q_{min}) + \Delta P_{choke}(Q_{min})
$$

**Turndown limits** — Separator and compressor turndown limits may prevent processing the reduced flow rates. The process model (from earlier chapters) determines these limits.

**Abandonment criteria** — The field is abandoned when:
1. Net revenue < operating cost for all wells
2. Production rate < minimum for fiscal compliance
3. Integrity issues require costly remediation
4. Environmental or regulatory requirements change

The digital twin monitors these criteria continuously, providing early warning of approaching economic limits.

### 28.8.8 Integrated Reservoir-to-Market Optimization

The feedback loop sketched in Section 28.8.2 is realized in NeqSim by the `IntegratedProductionModel` and `ReservoirToMarketOptimizer` (package `neqsim.process.fielddevelopment.integrated`). The integrated model couples each well's reservoir drive and deliverability curve to a shared export node, while the optimizer searches the choke settings that maximize a market-facing objective subject to a facility capacity:

```python
MaterialBalanceGasDrive = jneqsim.process.fielddevelopment.integrated.MaterialBalanceGasDrive
WellDeliverabilityCurve = jneqsim.process.fielddevelopment.integrated.WellDeliverabilityCurve
driveA = MaterialBalanceGasDrive(250.0, 5.0e9, 0.90)
driveB = MaterialBalanceGasDrive(220.0, 3.0e9, 0.90)
curveA = WellDeliverabilityCurve.fromVogel(2.0e6, 250.0)
curveB = WellDeliverabilityCurve.fromVogel(1.5e6, 220.0)
IntegratedProductionModel = jneqsim.process.fielddevelopment.integrated.IntegratedProductionModel
ReservoirToMarketOptimizer = jneqsim.process.fielddevelopment.integrated.ReservoirToMarketOptimizer

model = IntegratedProductionModel("Field")
model.addWell("Well-A", driveA, curveA)     # ReservoirDrive + WellDeliverabilityCurve
model.addWell("Well-B", driveB, curveB)
model.setExportPressure(90.0)               # bara
model.setHydrocarbonPrice(3.0)              # per Sm3
model.setEnergyIntensity(0.12)              # kWh/Sm3
model.setEmissionIntensity(0.02)            # kg CO2/Sm3

optimizer = ReservoirToMarketOptimizer(model)
optimizer.setFacilityCapacity(40000.0)      # Sm3/d export limit
optimizer.setMaxIterations(60)

result = optimizer.optimize()
print("Feasible:", result.isFeasible(),
      "objective:", result.getObjectiveValue())
print("Field rate:", result.getFieldRate(), "Sm3/d",
      "revenue:", result.getRevenue())
print("Choke settings:", list(result.getChokeSettings()))
print("Well rates:", dict(result.getWellRates()))
```

The optimizer's `OptimizationResult` reports `isFeasible()`, `getObjectiveValue()`, `getFieldRate()`, `getRevenue()`, `getChokeSettings()`, `getWellRates()`, and `getEvaluations()`, and serializes to JSON via `toJson()`. Because the reservoir drives deplete as cumulative production accumulates, calling `model.runProfile(years, dtYears)` projects the optimized field forward in time, yielding a `ProductionProfile` whose points carry rate, revenue, energy, emissions, and reservoir pressure — the quantitative backbone of the digital-twin forecast. The reservoir-to-market objective also underpins the life-of-field value-chain economics treated in Chapter 32.

---

## 28.8 Python Implementation

### 28.8.1 VFP Generation in Python

The complete Python workflow for VFP generation:

```python
from pathlib import Path
Path("figures").mkdir(parents=True, exist_ok=True)
import jpype
jneqsim = jpype.JPackage("neqsim")
import numpy as np
import matplotlib.pyplot as plt

# Classes
FluidMagicInput = jneqsim.process.util.optimizer.FluidMagicInput
RecombinationFlashGenerator = jneqsim.process.util.optimizer.RecombinationFlashGenerator
SystemSrkEos = jneqsim.thermo.system.SystemSrkEos

# Create reference fluid
ref = SystemSrkEos(273.15 + 80.0, 250.0)
ref.addComponent("methane", 70.0)
ref.addComponent("ethane", 8.0)
ref.addComponent("propane", 4.0)
ref.addComponent("n-butane", 2.5)
ref.addComponent("n-pentane", 1.5)
ref.addComponent("n-heptane", 6.0)
ref.addComponent("n-octane", 4.0)
ref.addComponent("n-decane", 2.0)
ref.addComponent("water", 2.0)
ref.setMixingRule("classic")
ref.setMultiPhaseCheck(True)

# Setup
fmi = FluidMagicInput(ref)
fmi.setGORRange(200, 5000)
fmi.setWaterCutRange(0.0, 0.50)
fmi.setNumberOfGORPoints(5)
fmi.setNumberOfWaterCutPoints(4)
fmi.setGorSpacing(FluidMagicInput.GORSpacing.LOGARITHMIC)
fmi.separateToStandardConditions()

flash_gen = RecombinationFlashGenerator(fmi)

# Generate fluids at different GOR values and plot density
gors = [200, 500, 1000, 2000, 5000]
densities = []
for gor in gors:
    fl = flash_gen.generateFluid(float(gor), 0.10, 10000.0, 353.15, 50.0)
    fl.initProperties()
    densities.append(fl.getDensity("kg/m3"))

fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogx(gors, densities, 'bo-', markersize=8)
ax.set_xlabel("GOR (Sm³/Sm³)")
ax.set_ylabel("Mixture Density (kg/m³)")
ax.set_title("Fluid Density vs. GOR at 80°C, 50 bara, WC=10%")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("figures/density_vs_gor.png", dpi=150, bbox_inches="tight")
plt.show()
```

### 28.8.2 Plotting VFP Surfaces

```python
from pathlib import Path
Path("figures").mkdir(parents=True, exist_ok=True)
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Assume VFP table has been generated (table object from Section 28.6.2)
# Extract BHP data for a fixed WC and GOR
flow_rates = list(table.getFlowRates())
thp_values = list(table.getOutletPressures())

# Get BHP values for WC=5% (index 0), GOR=1000 (index 1)
bhp_data = np.zeros((len(flow_rates), len(thp_values)))
for i in range(len(flow_rates)):
    for j in range(len(thp_values)):
        bhp_data[i, j] = table.getBHP(i, j, 0, 1)

# Plot as surface
Q, P = np.meshgrid(flow_rates, thp_values, indexing='ij')

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(Q / 1000, P, bhp_data, cmap='viridis', alpha=0.8)

ax.set_xlabel("Mass flow (×1000 kg/hr)")
ax.set_ylabel("Outlet pressure (bara)")
ax.set_zlabel("Required inlet pressure (bara)")
ax.set_title("Process screening: inlet pressure vs mass flow and outlet pressure\n(WC=5%, GOR=1000 Sm³/Sm³)")
fig.colorbar(surf, shrink=0.5, label="Required inlet pressure (bara)")
plt.tight_layout()
plt.savefig("figures/vfp_surface.png", dpi=150, bbox_inches="tight")
plt.show()
```

### 28.8.3 Multi-Scenario Comparison

```python
from pathlib import Path
Path("figures").mkdir(parents=True, exist_ok=True)
import matplotlib.pyplot as plt
import numpy as np

# Compare VFP curves at different GOR values (fixed WC=5%, outlet pressure=50 bara)
flow_rates = list(table.getFlowRates())
gor_values = list(table.getGORs())
gor_labels = [f"GOR={gor:g}" for gor in gor_values]

fig, ax = plt.subplots(figsize=(10, 6))

for g_idx, (gor, label) in enumerate(zip(gor_values, gor_labels)):
    bhp_values = []
    for r_idx in range(len(flow_rates)):
        bhp = table.getBHP(r_idx, 1, 0, g_idx)  # THP index=1 (40 bara), WC index=1
        bhp_values.append(bhp)

    ax.plot(np.array(flow_rates) / 1000, bhp_values, 'o-',
            label=label, linewidth=2, markersize=6)

ax.set_xlabel("Mass flow (×1000 kg/hr)")
ax.set_ylabel("Required inlet pressure (bara)")
ax.set_title("Process screening at different GOR values\n(WC=5%, outlet pressure=50 bara)")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("figures/vfp_gor_comparison.png", dpi=150, bbox_inches="tight")
plt.show()
```

---

## 28.10 Quality Assurance and Validation of VFP Tables

### 28.10.1 Common VFP Generation Errors

VFP tables are only useful if they are physically correct. Common errors include:

1. **Non-monotonic BHP:** For a given THP, WC, and GOR, BHP should increase monotonically with flow rate. If BHP decreases at higher rates, the binary search may have found a local minimum rather than the true solution. This typically indicates a flow regime transition (from slug to annular) that the correlation handles poorly.

2. **Negative pressure gradients:** Some combinations produce negative hydrostatic gradients (gas column lighter than expected). This is physically possible for high-GOR wells but may indicate a fluid composition error.

3. **Infeasible corners:** High-rate, high-WC, low-GOR combinations may require BHP above the reservoir pressure. These points are correctly marked as infeasible, but too many infeasible points (>30%) suggests the table grid extends beyond the physical operating envelope.

4. **Temperature convergence:** For long flowlines with significant heat exchange, the temperature profile affects fluid properties. If the process model uses a fixed temperature, the VFP table may be inaccurate for low-rate cases (longer residence time, more cooling).

### 28.10.2 Validation Against Well Test Data

Every VFP table should be validated against at least two measured operating points:

**Execution scope:** This integration pattern requires supplied well-test data and qualified interpolation routine. It is not a standalone validated process calculation.

```python pattern: requires supplied well-test data and qualified interpolation routine
# Validation: compare VFP prediction against well test
# Well test: Q = 12,000 Sm3/d, THP = 45 bara, WC = 12%, GOR = 800
# Measured BHP = 215 bara

# Interpolate from VFP table
predicted_bhp = interpolate_vfp(table, Q=12000, THP=45, WC=0.12, GOR=800)
measured_bhp = 215.0

error_pct = abs(predicted_bhp - measured_bhp) / measured_bhp * 100
print(f"Predicted BHP: {predicted_bhp:.1f} bara")
print(f"Measured BHP:  {measured_bhp:.1f} bara")
print(f"Error:         {error_pct:.1f}%")

# Acceptance: < 5% error for well test conditions
assert error_pct < 5.0, f"VFP validation failed: {error_pct:.1f}% error"
```

### 28.10.3 Sensitivity to EOS Selection

The choice of equation of state affects the generated VFP table because it changes the fluid properties (density, viscosity, phase fractions) at each point:

| EOS | Best For | GOR Sensitivity | Water Handling |
|-----|----------|----------------|----------------|
| SRK | General hydrocarbon systems | Good for gas-dominated | Basic |
| PR | Oil systems (better liquid density) | Good across range | Basic |
| SRK-CPA | Systems with methanol/MEG | Good | Excellent (associating fluids) |
| PR-MC | Heavy oil (Mathias-Copeman) | Less accurate at high GOR | Basic |

For field development studies, the EOS should match the one used in the reservoir simulation model to ensure consistency between the reservoir and well models.

### 28.10.4 VFP Table Refresh Strategy

VFP tables should be regenerated when:
- **New PVT data** becomes available (new wells, additional lab analysis)
- **Reservoir model update** changes the expected GOR/WC evolution
- **Facility modifications** change the process model (new compression, new pipeline)
- **History match update** reveals the current tables are inaccurate (>10% error on BHP prediction)

A practical refresh strategy:
- **Pre-development:** Generate tables from exploration well PVT data (wide ranges)
- **First oil +1 year:** Refine with production data and updated PVT model
- **Every 2–3 years:** Regenerate based on reservoir model updates
- **Major modification:** Regenerate immediately (new wells, new infrastructure)

---


<!-- September 2026 source update -->
## The current VFP export boundary

`MultiScenarioVFPGenerator` calculates required process inlet pressures for configured outlet conditions. Its legacy `getBHP()` name does not establish a bottomhole-pressure datum. At the current revision, `toVFPEXPString()` and `exportVFPEXP()` produce diagnostic process-screening text; they do not produce reservoir deck keywords. Use `toDiagnosticString()` and a `.txt` output when retaining these generic process results \cite{neqsim2026update}.

`EclipseVFPExporter` has a different role: it formats supplied, qualified flowing BHP at a declared well datum. A complete production grid has axes for standard phase-volume flow, THP, water ratio, gas ratio and artificial lift. The Java pressure-array order is `[flow][THP][water ratio][gas ratio][ALQ]`, while each deck row uses one-based THP/water/gas/lift indices followed by all flow values. The exporter validates structure and conversions; the caller qualifies the physical well model.

Default input units are Sm³/day and bara even when FIELD output is requested. METRIC and FIELD output must match the surrounding reservoir deck. In FIELD tables gas rate and GRAT use Mscf/day, and GOR uses Mscf/STB. Do not substitute kg/hr, actual volume, gauge pressure or a process mass-capacity optimum. Standard-volume reference conditions must already match those of the reservoir model.

All axis entries and BHP cells must be finite, positive where required and dimensionally complete. Infeasible values remain unavailable in diagnostic results and must not be interpolated, copied or filled into a deck silently. Select and validate a feasible grid before export. Neither a correctly serialized file nor the synthetic serialization examples constitute execution in a reservoir simulator or validation of field well performance.

For a field-development decision, retain three independent artifacts: a calibrated well-model validation, a complete process-capacity/quality assessment, and an exporter contract check. This prevents an attractive process-screening result from becoming an unjustified production forecast.

---


<!-- reviewed-notebook-results:start -->
## Reproduced Calculation Results

These examples use the stated fluid recipes and operating assumptions. Curves represent NeqSim calculations unless a caption identifies an analytical illustration, assumed equipment map or synthetic data.

![VFP Curves: Bottomhole Pressure vs Flow Rate](figures/ch19_vfp_curves.png)

WHP = 40 bara: bottomhole pressure spans 53.79–216.9 bara across the plotted cases. WHP = 60 bara: bottomhole pressure spans 79.81–230.2 bara across the plotted cases.

The upward production model solves bottomhole pressure to meet each imposed wellhead pressure at a specified rate. The resulting surface is a production lift requirement, not a downward injection calculation. Keep the upward elevation convention and outlet-pressure residual checks with every exported VFP point.

![Upward production VFP surface](figures/ch19_vfp_surface.png)

The sixty upward-flow solutions span 53.79–272.22 bara required bottomhole pressure. The largest difference between solved and specified wellhead pressure is 0.0119 bar.

The surface combines sixty NeqSim solutions across five wellhead pressures and twelve flow rates. Interpolation is justified only within this sampled fluid, temperature and geometry envelope. Use the accompanying CSV and verify boundary residuals before linking the table to a reservoir model.

Selected numerical ranges from the plotted cases:

| Quantity / series | Minimum | Maximum | Unit |
|---|---:|---:|---|
| WHP = 40 bara: bottomhole pressure | 53.79 | 216.9 | bara |

Ranges describe the sampled cases; they are not independent validation tolerances.
<!-- reviewed-notebook-results:end -->

## 28.11 Summary

Key points from this chapter:

- **Traditional single-composition VFP tables** become increasingly inaccurate as GOR and water cut change during field life. Multi-scenario VFP tables spanning the full (rate × pressure × WC × GOR) space are essential for accurate production forecasting.
- **FluidMagicInput** imports reference fluid from E300 files or NeqSim fluid objects and configures GOR/WC ranges with linear or logarithmic spacing.
- **RecombinationFlashGenerator** creates physically consistent fluids at any GOR and water cut by recombining separated gas, oil, and water phases — mimicking actual reservoir behavior.
- **MultiScenarioVFPGenerator** sweeps the 4D parameter space using binary search for inlet pressure and parallel execution for performance. A typical 1200-point table runs in minutes on 8 cores.
- **Eclipse VFPEXP export** enables direct coupling with reservoir simulators, where the `WCONPROD` keyword references the VFP table number.
- **Fluid property sensitivity** — GOR primarily affects density and gas fraction; water cut affects emulsion viscosity and hydrostatic head. Both must be captured in the VFP table.
- **GOR spacing** should be logarithmic for wide ranges (200–10,000 Sm³/Sm³) to capture the rapid phase behavior changes near the bubble point.
- **The field development digital twin** connects PVT → reservoir → well network → process facility → economics in a unified workflow, enabling life-of-field production optimization.
- **Model calibration** against well test data and production history is essential — validate VFP predictions within 5% of measured BHP.
- **Concept screening** with multi-scenario VFP tables allows rapid comparison of development alternatives (tieback distance, subsea boosting, standalone FPSO).
- **Late-life operations** (high water cut, declining pressure, turndown limits) are modeled by updating the network and process models at each time step.
- **Quality assurance** — check for monotonicity, validate against well tests, and refresh tables when the reservoir model is updated.

---

## Exercises

1. **Exercise 28.1:** Create a FluidMagicInput from a NeqSim fluid with 10 components. Set GOR range 500–6000 Sm³/Sm³ with logarithmic spacing (6 points) and WC range 0.05–0.50 (5 points). Generate fluids at the four corners of the (GOR, WC) space and report the mixture density at 80°C, 50 bara.

2. **Exercise 28.2:** Build a simple process model (tubing + flowline) and generate a VFP table with 5 flow rates × 4 THPs × 3 water cuts × 4 GORs (= 240 points). Report the number of feasible points and the computation time.

3. **Exercise 28.3:** Export the VFP table from Exercise 28.2 in Eclipse VFPEXP format. Write a Python script that reads the exported file and plots the BHP vs. rate curves for each GOR at fixed WC = 0.20 and THP = 40 bara.

4. **Exercise 28.4:** Compare VFP tables generated with 3.5-inch and 4.5-inch tubing. At what GOR does the smaller tubing become infeasible for rates above 30,000 Sm³/d? Plot the feasibility boundary in the (rate, GOR) plane.

5. **Exercise 28.5:** Implement a simplified field development digital twin in Python: start with reservoir pressure = 350 bara, decline at 3% per year for 20 years. At each year, solve the well network from Chapter 15 and record total production. Plot production rate and cumulative production vs. time.

6. **Exercise 28.6 (Advanced):** Generate multi-scenario VFP tables for three different tubing sizes (2-7/8", 3-1/2", 4-1/2") across the full GOR and WC range. Determine which tubing size maximizes cumulative production over a 20-year field life, accounting for the fact that larger tubing allows higher initial rates but may load up at low rates later in life.

7. **Exercise 28.7 (Advanced):** Build a complete field development evaluation workflow: (a) generate multi-scenario VFP tables, (b) couple with a simple material balance reservoir model, (c) run 20-year production forecast, (d) calculate NPV at oil price = 70 USD/bbl and gas price = 0.30 USD/Sm³, (e) perform Monte Carlo uncertainty analysis on GIP, recovery factor, and prices.

---

## References

1. Brill, J. P., & Mukherjee, H. (1999). *Multiphase Flow in Wells*. SPE Monograph Series, Vol. 17.
2. Economides, M. J., Hill, A. D., Ehlig-Economides, C., & Zhu, D. (2013). *Petroleum Production Systems* (2nd ed.). Prentice Hall.
3. Dale, S. (2007). Use of VFP tables in integrated production modelling. SPE Paper 109138, *SPE Asia Pacific Oil and Gas Conference*, Jakarta.
4. Beggs, H. D., & Brill, J. P. (1973). A study of two-phase flow in inclined pipes. *Journal of Petroleum Technology*, 25(5), 607–617.
5. Standing, M. B. (1981). *Volumetric and Phase Behavior of Oil Field Hydrocarbon Systems* (9th ed.). SPE.
6. Whitson, C. H., & Brulé, M. R. (2000). *Phase Behavior*. SPE Monograph Series, Vol. 20.
7. Schlumberger (2023). *Eclipse Technical Description*. Schlumberger Information Solutions.
8. Todini, E., & Pilati, S. (1988). A gradient algorithm for the analysis of pipe networks. In *Computer Applications in Water Supply*, Vol. 1. Research Studies Press.
9. NORSOK P-002 (2014). Process system design. Standards Norway.
10. Norwegian Petroleum Directorate (2019). *Resource Classification System*. NPD.


