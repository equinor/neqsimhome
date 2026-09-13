# Debottlenecking and Capacity Management

<!-- Chapter metadata -->
<!-- Notebooks: ch21_debottlenecking_workflow.ipynb, ch21_capacity_dashboard.ipynb, ch21_whatif_analysis.ipynb -->
<!-- Estimated pages: 35 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Explain the concept of debottlenecking and its role in extending field life and maximizing production
2. Describe the NeqSim Capacity Constraint Framework including the `CapacityConstrainedEquipment` interface, `CapacityConstraint` class, and `EquipmentCapacityStrategy` plugin architecture
3. Use `ProcessSystem.findBottleneck()` and related methods to systematically identify the limiting equipment in a production facility
4. Apply the `autoSize()` method on separators, compressors, valves, pipelines, and pumps to automatically generate capacity constraints from design calculations
5. Perform what-if debottlenecking studies by selectively disabling constraints and re-optimizing
6. Build utilization dashboards using `getCapacityUtilizationSummary()` with color-coded visualization
7. Implement a complete Python debottlenecking workflow in NeqSim with sensitivity analysis and matplotlib visualization

---

## 21.1 Introduction

A facility can be limited by one or several active constraints, or by upstream supply, commercial demand or utility availability. The most loaded equipment is not necessarily a unique throughput bottleneck. As reservoir conditions evolve — declining reservoir pressure, rising water cut, changing gas-oil ratio, increasing sand production — the identity of the bottleneck shifts. A compressor that had ample margin at plateau production may become the limiting factor when suction pressure drops. A separator designed for low water cut may be overwhelmed when water breakthrough occurs. A pipeline sized for dry gas may hit erosional velocity limits as condensate drops out.

**Debottlenecking** is the systematic process of:

1. **Identifying** the current bottleneck
2. **Quantifying** the production gain from removing it
3. **Evaluating** the cost and feasibility of the modification
4. **Implementing** the change and verifying the result

The production gain from removing a bottleneck can be dramatic. The gain and investment depend on the field, the binding constraint and the modification scope; establish them from the actual study rather than applying a generic percentage. The key to successful debottlenecking is *systematic identification* — not guessing which equipment is limiting, but rigorously computing the utilization of every item and identifying the true constraint.

This chapter presents a comprehensive debottlenecking methodology built on NeqSim's Capacity Constraint Framework. The framework provides:

- **Standardized capacity evaluation** across all equipment types
- **Automated bottleneck detection** at the process system level
- **What-if analysis** through selective constraint manipulation
- **Utilization dashboards** for ongoing capacity monitoring

### 21.1.1 The Debottlenecking Cycle

Debottlenecking is not a one-time activity but a continuous cycle that repeats throughout the field life:

$$
\text{Model} \rightarrow \text{Identify Bottleneck} \rightarrow \text{Evaluate Options} \rightarrow \text{Implement} \rightarrow \text{Verify} \rightarrow \text{Repeat}
$$

Each cycle removes one bottleneck, but removing it typically reveals the *next* bottleneck — the equipment that was previously the second-most constrained. The cycle continues until either (a) the production target is met, (b) no further economic debottlenecking is possible, or (c) a fundamental constraint (e.g., reservoir deliverability, export pipeline capacity) is reached.

### 21.1.2 Hard vs Soft Constraints

Not all constraints are equal. A critical distinction in debottlenecking is between:

| Constraint Type | Description | Consequence of Exceeding | Example |
|----------------|-------------|-------------------------|---------|
| **Hard** | Cannot be exceeded — equipment trips or fails | Equipment damage, safety hazard | Compressor surge, vessel MAWP |
| **Soft** | Can be temporarily exceeded with penalty | Reduced efficiency, accelerated wear | Compressor recycle, separator carry-over |
| **Design** | Information only — original design basis | No immediate consequence | Design flow rate, design temperature |

Hard constraints define declared absolute limits. Soft constraints define a preferred operating envelope, and design constraints provide a reporting reference. A hard constraint can sometimes be relieved by changing upstream conditions or reallocating load; otherwise an equipment modification may be needed. Classify each limit from its actual technical basis and keep the protective-system limits separate from economic preferences.

---

## 21.2 Capacity Constraint Framework in NeqSim

NeqSim provides a capacity constraint framework in the `neqsim.process.equipment.capacity` package. Equipment derived from the process base class can store constraints, while equipment-specific methods and registered strategies determine which physical limits are actually evaluated.

### Java Example Setup

The Java operation fragments in this chapter use the following shared fixture. Copy the imports and class once, then replace the body of `runExample()` with one fragment and run the class. Each example starts with a fresh synthetic separator–compressor process. Auto-sizing establishes an assumed screening capacity; replace those capacities with installed ratings for a plant study. API signature summaries are printed as plain text and are not standalone programs.

```java
import java.util.*;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import neqsim.thermo.system.*;
import neqsim.process.processmodel.*;
import neqsim.process.equipment.*;
import neqsim.process.equipment.stream.*;
import neqsim.process.equipment.separator.*;
import neqsim.process.equipment.compressor.*;
import neqsim.process.equipment.pipeline.*;
import neqsim.process.equipment.pump.*;
import neqsim.process.equipment.valve.*;
import neqsim.process.equipment.capacity.*;
import neqsim.process.equipment.capacity.CapacityConstraint.ConstraintType;
import neqsim.process.optimization.valuechain.*;

public class CapacityExample {
    private static final Logger logger = LogManager.getLogger(CapacityExample.class);
    private static SystemInterface fluid, reservoirFluid;
    private static Stream feed;
    private static StreamInterface gasStream, oilStream, wellStream;
    private static Separator separator, hpSep;
    private static Compressor compressor, comp;
    private static ProcessSystem process;
    private static Separator equipment;
    private static BottleneckResult bottleneck;
    private static CapacityConstraint speedConstraint;

    private static void setup() {
        fluid = new SystemSrkEos(303.15, 70.0);
        fluid.addComponent("methane", 0.70);
        fluid.addComponent("ethane", 0.10);
        fluid.addComponent("n-decane", 0.20);
        fluid.setMixingRule("classic");
        reservoirFluid = fluid.clone();
        feed = new Stream("Feed", fluid);
        feed.setFlowRate(10000.0, "kg/hr");
        separator = new Separator("Fixture Separator", feed);
        compressor = new Compressor("Fixture Compressor", separator.getGasOutStream());
        compressor.setOutletPressure(150.0, "bara");
        compressor.setIsentropicEfficiency(0.75);
        process = new ProcessSystem();
        process.add(feed);
        process.add(separator);
        process.add(compressor);
        process.run();
        separator.autoSize(1.20);
        compressor.autoSize(1.15);
        separator.enableAllConstraints();
        compressor.enableAllConstraints();
        gasStream = separator.getGasOutStream();
        oilStream = separator.getLiquidOutStream();
        wellStream = feed;
        hpSep = separator;
        comp = compressor;
        equipment = separator;
        bottleneck = process.findBottleneck();
        speedConstraint = new CapacityConstraint("speed", "RPM", ConstraintType.HARD);
    }

    public static void main(String[] args) {
        setup();
        runExample();
    }

    private static void runExample() {
        // Insert one Java operation fragment from this chapter here.
        logger.info("Fixture bottleneck: {}", process.findBottleneck());
    }
}
```

### 21.2.1 Architecture Overview

The framework consists of four key components:

1. **`CapacityConstrainedEquipment`** — An interface that any equipment can implement to participate in capacity analysis
2. **`CapacityConstraint`** — A data class representing a single constraint with design value, maximum value, current value, and utilization
3. **`EquipmentCapacityStrategy`** — A plugin interface for equipment-specific capacity evaluation logic
4. **`EquipmentCapacityStrategyRegistry`** — A registry of strategy plugins, pre-loaded with 18 built-in strategies

```text
┌──────────────────────────────┐
│  ProcessSystem               │
│  ├─ findBottleneck()         │
│  ├─ getCapacityUtilization() │
│  ├─ getConstrainedEquipment()│
│  └─ disableAllConstraints()  │
└──────────┬───────────────────┘
           │ queries
           ▼
┌──────────────────────────────┐
│  CapacityConstrainedEquipment│  ← Interface
│  ├─ getCapacityConstraints() │
│  ├─ getBottleneckConstraint()│
│  ├─ getMaxUtilization()      │
│  ├─ isOverloaded()           │
│  └─ isHardLimitExceeded()    │
└──────────┬───────────────────┘
           │ contains
           ▼
┌──────────────────────────────┐
│  CapacityConstraint          │
│  ├─ name, unit               │
│  ├─ type (HARD/SOFT/DESIGN)  │
│  ├─ designValue, maxValue    │
│  ├─ valueSupplier            │
│  ├─ warningThreshold         │
│  └─ getUtilization()         │
└──────────────────────────────┘
```

### 21.2.2 The CapacityConstrainedEquipment Interface

The `CapacityConstrainedEquipment` interface defines the contract for any equipment that participates in capacity analysis:

```text
public interface CapacityConstrainedEquipment {
    // Query capacity analysis state
    boolean isCapacityAnalysisEnabled();
    void setCapacityAnalysisEnabled(boolean enabled);

    // Get all constraints
    Map<String, CapacityConstraint> getCapacityConstraints();

    // Bottleneck identification
    CapacityConstraint getBottleneckConstraint();

    // Utilization queries
    double getMaxUtilization();
    boolean isOverloaded();
    boolean isHardLimitExceeded();

    // Constraint management
    int disableAllConstraints();
    int enableAllConstraints();
}
```

The key methods serve different purposes:

- **`getCapacityConstraints()`** returns all constraints as an unmodifiable map. The constraints are lazily initialized — they are created the first time this method is called.
- **`getBottleneckConstraint()`** returns the single constraint with the highest utilization. This is the constraint most likely to limit throughput.
- **`getMaxUtilization()`** returns the utilization of the bottleneck constraint as a fraction (1.0 = 100% of design capacity).
- **`isOverloaded()`** returns `true` if any constraint exceeds 100% utilization.
- **`isHardLimitExceeded()`** returns `true` when a declared HARD constraint violates its maximum or minimum. This reports the modeled limit; it does not replace a protective system or an independent safety assessment.

### 21.2.3 The CapacityConstraint Class

Each constraint is represented by a `CapacityConstraint` object with the following properties:

| Property | Type | Description |
|----------|------|-------------|
| `name` | `String` | Constraint identifier (e.g., "speed", "gasLoadFactor") |
| `unit` | `String` | Engineering unit (e.g., "RPM", "m/s", "%") |
| `type` | `ConstraintType` | HARD, SOFT, or DESIGN |
| `designValue` | `double` | The design basis value (100% utilization) |
| `maxValue` | `double` | The absolute maximum (for HARD constraints) |
| `valueSupplier` | `DoubleSupplier` | Lambda that returns the current value |
| `warningThreshold` | `double` | Fraction at which to warn (default 0.9 = 90%) |
| `enabled` | `boolean` | Whether this constraint is active |
| `shadowPrice` | `double` | Marginal economic value of relaxing the constraint (default 0) |

The utilization is calculated as:

$$
U = \frac{V_{\text{current}}}{V_{\text{design}}}
$$

where $V_{\text{current}}$ is the value returned by the `valueSupplier` and $V_{\text{design}}$ is the `designValue`. For minimum constraints, the ratio is the declared minimum divided by the current value; the direction of violation is therefore reversed. Missing or non-finite measurements require a separate evidence check. Utilization is capped at 9.99 (999%) to prevent unbounded values when the design value is near zero.

The three constraint types define different severity levels:

$$
\text{Constraint severity} = \begin{cases}
\text{HARD} & \text{if exceeding causes trip/failure} \\
\text{SOFT} & \text{if exceeding reduces performance} \\
\text{DESIGN} & \text{information only}
\end{cases}
$$

A constraint is constructed using a fluent builder pattern:

```java
CapacityConstraint speedConstraint = new CapacityConstraint(
        "speed", "RPM", ConstraintType.HARD)
    .setDesignValue(10000.0)
    .setMaxValue(11000.0)
    .setWarningThreshold(0.9)
    .setValueSupplier(() -> compressor.getSpeed());
```

Each constraint can also carry a **shadow price** — the marginal economic value of relaxing the limit by one unit:

```java
double shadowPriceNokPerRpm = 250.0; // assumed marginal value for this example
speedConstraint.setShadowPrice(shadowPriceNokPerRpm);  // fluent, returns the constraint
double price = speedConstraint.getShadowPrice();         // 0.0 by default
```

The shadow price is zero until populated by an economic tool. The `DebottleneckingAdvisor` (Section 21.9.5) writes shadow prices back onto the binding constraints so that the same constraint objects used for capacity checking also rank the value of the production each bottleneck withholds.

### 21.2.4 The ConstraintType Enum

The `ConstraintType` enum classifies constraints by their severity:

```text
public enum ConstraintType {
    HARD,    // Cannot exceed — causes trip or equipment damage
    SOFT,    // Can exceed temporarily — reduced efficiency or life
    DESIGN   // Information only — original design basis
}
```

Additionally, a `ConstraintSeverity` enum provides finer granularity for the optimizer:

| Severity | Description | Optimizer Behavior |
|----------|-------------|-------------------|
| `CRITICAL` | Equipment damage or safety hazard | Stop immediately |
| `HARD` | Exceeds design limits | Mark solution infeasible |
| `SOFT` | Exceeds recommended limits | Apply penalty to objective |
| `ADVISORY` | Information only | No impact |

### 21.2.5 Universal Constraint Storage in ProcessEquipmentBaseClass

A powerful design decision in NeqSim is that **all** equipment types inherit constraint storage from `ProcessEquipmentBaseClass`. This means every one of the 144+ equipment types — from simple valves to complex distillation columns — can hold and report capacity constraints without requiring any modification to the equipment class itself.

The base class provides:

```text
// Selected public method signatures (bodies omitted).
public void addCapacityConstraint(CapacityConstraint constraint);
public Map<String, CapacityConstraint> getCapacityConstraints();
public CapacityConstraint getBottleneckConstraint();
public double getMaxUtilization();
public boolean isOverloaded();
public boolean isHardLimitExceeded();
public int disableAllConstraints();
```

Equipment subclasses override `initializeCapacityConstraints()` to populate equipment-specific constraints. For example, `ThrottlingValve` creates constraints for Cv utilization, volume flow, valve opening percentage, and acoustic-induced vibration (AIV).

### 21.2.6 Equipment Capacity Strategy Plugins

The 18 built-in `EquipmentCapacityStrategy` plugins provide specialized capacity evaluation logic for different equipment types:

| # | Strategy | Equipment | Key Constraints |
|---|----------|-----------|----------------|
| 1 | `CompressorCapacityStrategy` | Compressor | Speed, power, surge margin, discharge T |
| 2 | `SeparatorCapacityStrategy` | Separator | Gas load factor, liquid retention, level |
| 3 | `PipeCapacityStrategy` | Pipeline | Velocity, erosion ratio, pressure drop |
| 4 | `ValveCapacityStrategy` | Valve | Cv utilization, opening %, AIV |
| 5 | `HeatExchangerCapacityStrategy` | Heat exchanger | Duty, approach T, tube velocity |
| 6 | `PumpCapacityStrategy` | Pump | NPSH margin, power, flow rate |
| 7 | `ExpanderCapacityStrategy` | Expander | Speed, power, efficiency |
| 8 | `EjectorCapacityStrategy` | Ejector | Entrainment ratio, motive pressure |
| 9 | `MixerCapacityStrategy` | Mixer | Pressure balance, flow imbalance |
| 10 | `SplitterCapacityStrategy` | Splitter | Split ratio, total flow |
| 11 | `TankCapacityStrategy` | Tank/vessel | Level, throughput, overflow |
| 12 | `DistillationColumnCapacityStrategy` | Column | Flooding, weeping, jet flooding |
| 13 | `ReactorCapacityStrategy` | Reactor | Conversion, temperature, residence time |
| 14 | `PowerGenerationCapacityStrategy` | Gas/steam turbine | Power output, firing T, speed |
| 15 | `SubseaEquipmentCapacityStrategy` | Subsea tree/manifold | Pressure rating, flow, erosion |
| 16 | `FilterAdsorberCapacityStrategy` | Filter/adsorber | Differential pressure, loading |
| 17 | `ElectrolyzerCapacityStrategy` | Electrolyzer | Current density, efficiency |
| 18 | `WellFlowCapacityStrategy` | Well | Flowing BHP, velocity, erosion |

All 18 strategies are automatically registered in the `EquipmentCapacityStrategyRegistry` singleton. Custom strategies can be added:

```java
EquipmentCapacityStrategyRegistry registry =
    EquipmentCapacityStrategyRegistry.getInstance();
registry.register(new SeparatorCapacityStrategy() {
    @Override
    public int getPriority() { return 10; }
});
```

### 21.2.7 Constraint Enablement

Constraints are **disabled by default** until explicitly enabled. This design prevents capacity analysis from interfering with basic process simulation. There are several ways to enable constraints:

```java
// Option 1: Enable with Equinor-standard constraint sets
equipment.useEquinorConstraints();

// Option 2: Enable with API-standard constraint sets
equipment.useAPIConstraints();

// Option 3: Enable all constraints
equipment.enableAllConstraints();

// Option 4: Enable capacity analysis (equipment-level)
equipment.setCapacityAnalysisEnabled(true);
```

On `Separator`, `useEquinorConstraints()` and `useAPIConstraints()` enable different named subsets of the existing constraints. They do not read the applicable project requirements or certify the vessel. Inspect each enabled constraint, assign its approved limit and units, and verify that its value supplier represents the current operating point.

---

## 21.3 Systematic Bottleneck Identification

With the capacity constraint framework in place, identifying the bottleneck becomes a straightforward computation. NeqSim provides several methods on `ProcessSystem` for system-level capacity analysis.

### 21.3.1 Finding the Bottleneck

The primary method for bottleneck identification is `ProcessSystem.findBottleneck()`, which returns a `BottleneckResult` containing the limiting equipment, constraint, and utilization:

```java
// Use the populated process from the shared fixture.
process.run();

// Find the bottleneck
BottleneckResult result = process.findBottleneck();

if (result.hasBottleneck()) {
    logger.info("Bottleneck: " + result.getEquipmentName());
    logger.info("Constraint: " + result.getConstraintName());
    logger.info("Utilization: " +
        String.format("%.1f%%", result.getUtilization() * 100));
    logger.info("Type: " + result.getConstraint().getType());
} else {
    logger.info("No bottleneck found (no constraints defined)");
}
```

The `findBottleneck()` method iterates over all equipment implementing `CapacityConstrainedEquipment`, queries their bottleneck constraint, and returns the one with the highest utilization.

For simpler use cases, the legacy `getBottleneck()` method returns just the equipment:

```java
ProcessEquipmentInterface bottleneck = process.getBottleneck();
double utilization = process.getBottleneckUtilization();
```

### 21.3.2 The BottleneckResult Class

The `BottleneckResult` class provides detailed information about the identified bottleneck:

```text
public class BottleneckResult {
    ProcessEquipmentInterface getEquipment();    // The bottleneck equipment
    String getEquipmentName();                    // Equipment name
    CapacityConstraint getConstraint();           // The limiting constraint
    String getConstraintName();                   // Constraint name
    double getUtilization();                      // Utilization as fraction
    boolean hasBottleneck();                      // Whether a bottleneck was found
    boolean isExceeded();                       // Utilization > 1.0
    String toString();                          // Human-readable summary
}
```

### 21.3.3 Capacity Utilization Summary

For a complete overview of all equipment utilization, use `getCapacityUtilizationSummary()`:

```java
Map<String, Double> utilization = process.getCapacityUtilizationSummary();

// Print sorted by utilization (highest first)
utilization.entrySet().stream()
    .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
    .forEach(entry -> logger.info(String.format("%-30s %6.1f%%\n",
        entry.getKey(), entry.getValue() * 100)));
```

This returns a map from equipment name to maximum utilization fraction. Only equipment with `isCapacityAnalysisEnabled() == true` and at least one enabled constraint is included.

Example output:

```text
HP Compressor                   92.3%
HP Separator                    87.5%
Export Pipeline                 76.2%
LP Separator                    65.1%
Inlet Cooler                    54.8%
```

### 21.3.4 Early Warning — Equipment Near Capacity

The `getEquipmentNearCapacityLimit()` method identifies equipment approaching their warning threshold (default 90%):

```java
List<String> nearLimit = process.getEquipmentNearCapacityLimit();
if (!nearLimit.isEmpty()) {
    logger.info("WARNING: Equipment near capacity:");
    for (String name : nearLimit) {
        logger.info("  - " + name);
    }
}
```

For custom thresholds, pass the desired fraction:

```java
List<String> above80 = new ArrayList<String>();
for (Map.Entry<String, Double> item : process.getCapacityUtilizationSummary().entrySet()) {
    if (item.getValue() > 0.80) { above80.add(item.getKey()); }
}
logger.info("Equipment above 80 percent: {}", above80);
```

### 21.3.5 Overload Detection

Two boolean methods provide quick checks for constraint violations:

```java
// Any equipment above 100% of design capacity?
boolean overloaded = process.isAnyEquipmentOverloaded();

// Any HARD constraint violated (trip/safety condition)?
boolean hardViolation = process.isAnyHardLimitExceeded();

if (hardViolation) {
    logger.info("CRITICAL: Hard limit exceeded - check equipment!");
}
```

The distinction matters: `isAnyEquipmentOverloaded()` checks if any constraint (hard, soft, or design) exceeds 100%, while `isAnyHardLimitExceeded()` specifically checks HARD-type constraints against their maximum value. A soft constraint at 105% is an overload but not a hard limit violation.

### 21.3.6 Querying Constrained Equipment

To get a list of all equipment that has capacity constraints:

```java
List<CapacityConstrainedEquipment> constrained =
    process.getConstrainedEquipment();
logger.info("Number of constrained equipment: " + constrained.size());
```

### 21.3.7 Active Constraint Identification Workflow

A typical debottlenecking workflow combines these methods:

```java
// Step 1: Run the process simulation
process.run();

// Step 2: Check for hard limit violations (safety first)
if (process.isAnyHardLimitExceeded()) {
    logger.info("ALERT: Hard constraints violated!");
    // Investigate immediately
}

// Step 3: Identify the bottleneck
BottleneckResult bottleneck = process.findBottleneck();
logger.info("Bottleneck: " + bottleneck.toString());

// Step 4: Review overall utilization
Map<String, Double> util = process.getCapacityUtilizationSummary();

// Step 5: Check early warning list
List<String> nearLimit = process.getEquipmentNearCapacityLimit();
logger.info("Equipment above its configured warning threshold: " + nearLimit);
```

### 21.3.8 Tracking Bottleneck Migration with BottleneckTracker

A single `findBottleneck()` call captures the binding constraint at one operating point. Over a production sweep, a field-life profile, or a real-time monitoring loop, the bottleneck **migrates** from one equipment item to another (Section 21.3, "Bottleneck Shifting"). The `BottleneckTracker` (package `neqsim.process.equipment.capacity`) records a time series of `BottleneckResult` snapshots and analyses how the limiting constraint moves:

```java
BottleneckTracker tracker = new BottleneckTracker();

for (double rate = 0.5; rate <= 1.3; rate += 0.05) {
    feed.setFlowRate(10000.0 * rate, "kg/hr");
    process.run();
    tracker.record(rate, "rate=" + rate, process.findBottleneck());
}

logger.info(tracker.getTimelineSummary());
logger.info("Distinct bottlenecks: "
    + tracker.getDistinctBottleneckEquipment());
logger.info("Migration events: " + tracker.getMigrationCount());
logger.info("Peak utilization: "
    + tracker.getPeakUtilizationPercent() + "%");
```

Each call to `record(time[, label], BottleneckResult)` returns a `Snapshot` exposing `getTime()`, `getLabel()`, `getEquipmentName()`, `getConstraintName()`, `getUtilizationPercent()`, and `isExceeded()`. The tracker derives:

- `getMigrationEvents()` / `getMigrationCount()` — the points at which the binding equipment changed
- `getDistinctBottleneckEquipment()` — the set of all equipment that limited the facility at some point
- `getPeakSnapshot()` / `getPeakUtilizationPercent()` — the most stressed point in the series
- `getTimelineSummary()` — a human-readable trace, and `toJson()` for export

This converts a sequence of point-in-time capacity checks into a debottlenecking narrative: it shows *which* equipment to address first and *at what production level* the next constraint takes over, which is exactly the information needed to sequence the staged investments analysed in Section 21.9.

---

## 21.4 autoSize for Capacity Assessment

The `autoSize(double designMargin)` method available on most equipment types performs a design calculation based on the current operating conditions, then automatically creates capacity constraints from the calculated design values. This is the most convenient way to populate constraints for debottlenecking analysis.

### 21.4.1 The autoSize Concept

The `autoSize` method calculates what the equipment *should* be sized for given its current inlet conditions, then creates constraints based on those calculated values plus a design margin:

$$
V_{\text{design}} = V_{\text{calculated}} \times (1 + m)
$$

where $V_{\text{calculated}}$ is the value computed from design equations (e.g., Souders-Brown for separators) and $m$ is the design margin. The API argument is the multiplicative factor $1+m$: pass `autoSize(1.20)` for a 20% margin, not `autoSize(0.20)`. The latter can create an undersized screening design.

After `autoSize`, inspect the populated and enabled capacity constraints before querying the bottleneck. Auto-sizing covers the implemented design rules; it does not supply every missing vendor rating or validate an installed plant.

### 21.4.2 Separator autoSize

For separators, `autoSize` computes the gas load factor constraint from the Souders-Brown equation:

```java
Separator hpSep = new Separator("HP Separator", feed);
process.add(hpSep);
process.run();

// Auto-size with 20% design margin
hpSep.autoSize(1.20);

// Now constraints are populated
Map<String, CapacityConstraint> constraints = hpSep.getCapacityConstraints();
CapacityConstraint gasLoad = constraints.get("gasLoadFactor");
logger.info("Gas load K-factor: " + gasLoad.getCurrentValue() + " m/s");
logger.info("Design K-factor:   " + gasLoad.getDesignValue() + " m/s");
logger.info("Utilization:       " +
    String.format("%.1f%%", gasLoad.getUtilization() * 100));
```

The separator's `autoSize` creates constraints for:

| Constraint | Unit | Type | Basis |
|-----------|------|------|-------|
| `gasLoadFactor` | m/s | SOFT | Souders-Brown K-factor |
| `liquidRetentionTime` | s | SOFT | Minimum residence time |
| `liquidLevel` | % | DESIGN | Normal operating level |

### 21.4.3 Compressor autoSize

For compressors, `autoSize` creates constraints from the compressor operating point relative to its characteristic curves:

```java
Compressor comp = new Compressor("HP Compressor", gasStream);
comp.setOutletPressure(150.0, "bara");
process.add(comp);
process.run();

comp.autoSize(1.15);  // Multiplicative factor: 15% design margin

Map<String, CapacityConstraint> constraints = comp.getCapacityConstraints();
```

The compressor's `autoSize` creates constraints for:

| Constraint | Unit | Type | Basis |
|-----------|------|------|-------|
| `speed` | RPM | HARD | Maximum rated speed |
| `power` | kW | HARD | Driver rated power |
| `surgeMargin` | % | HARD | Minimum surge margin |
| `dischargeTemperature` | °C | SOFT | Maximum discharge temperature |
| `polytropicHead` | kJ/kg | DESIGN | Design head |

The surge margin constraint is critical — it defines the minimum distance from the surge line:

$$
\text{Surge Margin} = \frac{Q_{\text{actual}} - Q_{\text{surge}}}{Q_{\text{surge}}} \times 100\%
$$

A compressor operating with less than 10% surge margin is dangerously close to surge and requires immediate attention.

### 21.4.4 Valve autoSize

For throttling valves, `autoSize` creates constraints from the Cv sizing calculation:

```java
ThrottlingValve valve = new ThrottlingValve("Choke Valve", wellStream);
valve.setOutletPressure(60.0, "bara");
process.add(valve);
process.run();

valve.autoSize(1.20);

Map<String, CapacityConstraint> constraints = valve.getCapacityConstraints();
CapacityConstraint cvUtil = constraints.get("cvUtilization");
CapacityConstraint opening = constraints.get("valveOpening");
```

Valve constraints include:

| Constraint | Unit | Type | Basis |
|-----------|------|------|-------|
| `cvUtilization` | - | HARD | Ratio of required Cv to installed Cv |
| `valveOpening` | % | SOFT | Percentage opening |
| `volumeFlow` | m³/hr | DESIGN | Maximum volume flow capacity |
| `AIV` | kW | SOFT | Acoustic-induced vibration power |

The valve opening constraint warns when the valve is nearly fully open (limited control authority) or nearly closed (poor rangeability):

$$
\text{Valve OK if:} \quad 10\% \leq \text{Opening} \leq 90\%
$$

### 21.4.5 Pipeline autoSize

For pipelines, `autoSize` selects a standard diameter from velocity criteria and reruns the pressure calculation. The example uses a short teaching line. For a long export route, a velocity-based diameter may fail the arrival-pressure requirement; establish a feasible hydraulic diameter separately before accepting it.

```java
PipeBeggsAndBrills pipeline = new PipeBeggsAndBrills("Export Pipeline", gasStream);
pipeline.setPipeWallRoughness(5e-5);
pipeline.setLength(1000.0);  // 1 km teaching line, length is in metres
pipeline.setDiameter(0.3048);  // 12-inch
process.add(pipeline);
process.run();

pipeline.autoSize(1.15);

Map<String, CapacityConstraint> constraints = pipeline.getCapacityConstraints();
```

Pipeline constraints include:

| Constraint | Unit | Type | Basis |
|-----------|------|------|-------|
| `velocity` | m/s | SOFT | Maximum gas velocity |
| `pressureDrop` | bar | DESIGN | Total pressure-drop reference, when configured |
| `volumeFlow` | m3/hr | DESIGN | Outlet volume-flow reference, when configured |
| `LOF` | - | SOFT | Flow-induced vibration screening index |
| `FRMS` | - (API label) | SOFT | Vibration-intensity screening result |
| `AIV` | kW | SOFT | Acoustic-power screening result |

The velocity calculation can use an erosional-velocity correlation; inspect the selected velocity method instead of assuming a separate erosional-ratio constraint exists:

$$
v_e = \frac{C}{\sqrt{\rho_m}}
$$

where $C$ is an empirical, unit-dependent coefficient and $\rho_m$ is the mixture density. Record the coefficient and its unit convention explicitly; an imperial coefficient must not be inserted unchanged into an SI calculation. The constraint ratio is $v_{\text{actual}} / v_e$. This screening ratio does not calculate erosion from sand or corrosion.

### 21.4.6 Pump autoSize

For pumps, `autoSize` creates constraints from hydraulic and mechanical limits:

```java
Pump pump = new Pump("Export Pump", oilStream);
pump.setOutletPressure(80.0, "bara");
process.add(pump);
process.run();

pump.autoSize(1.20);
```

Pump constraints include:

| Constraint | Unit | Type | Basis |
|-----------|------|------|-------|
| `npshMargin` | m | HARD | Available NPSH minus required NPSH |
| `power` | kW | HARD | Driver rated power |
| `flowRate` | m³/hr | DESIGN | Design volume flow |
| `differentialHead` | m | DESIGN | Design differential head |

The NPSH margin constraint is critical for cavitation prevention:

$$
\text{NPSH Margin} = \text{NPSH}_A - \text{NPSH}_R
$$

where $\text{NPSH}_A$ is the available net positive suction head and $\text{NPSH}_R$ is the required value. A negative margin indicates cavitation.

### 21.4.7 Using autoSize Results for Debottlenecking

The typical workflow for debottlenecking assessment using `autoSize`:

```java
// Build process
ProcessSystem process = new ProcessSystem();
Stream feed = new Stream("Feed", fluid);
Separator hpSep = new Separator("HP Sep", feed);
Compressor comp = new Compressor("HP Comp", hpSep.getGasOutStream());
comp.setOutletPressure(150.0, "bara");
process.add(feed);
process.add(hpSep);
process.add(comp);
process.run();

// Auto-size all equipment
hpSep.autoSize(1.20);
comp.autoSize(1.15);

// Find the bottleneck
BottleneckResult result = process.findBottleneck();
logger.info("Bottleneck: " + result.getEquipmentName());
logger.info("Constraint: " + result.getConstraintName());
logger.info("Utilization: " +
    String.format("%.1f%%", result.getUtilization() * 100));
```

---

## 21.5 What-If Analysis with Constraint Control

The most powerful aspect of the capacity constraint framework for debottlenecking is the ability to selectively disable constraints and re-optimize. This answers the question: *"If we remove this bottleneck, how much more can we produce?"*

### 21.5.1 Disabling Individual Constraints

To test the effect of removing a specific constraint:

```java
// Get the bottleneck constraint
BottleneckResult bottleneck = process.findBottleneck();
CapacityConstraint limitingConstraint = bottleneck.getConstraint();

// Disable it
limitingConstraint.setEnabled(false);

// Re-run and check the new bottleneck
process.run();
BottleneckResult newBottleneck = process.findBottleneck();

logger.info("Previous bottleneck: " + bottleneck.getEquipmentName()
    + " (" + bottleneck.getConstraintName() + ")");
logger.info("New bottleneck:      " + newBottleneck.getEquipmentName()
    + " (" + newBottleneck.getConstraintName() + ")");
```

### 21.5.2 Disabling All Constraints on Equipment

To simulate replacing an entire piece of equipment with a larger one:

```java
// Disable all constraints on the bottleneck equipment
CapacityConstrainedEquipment bottleneckEquip =
    (CapacityConstrainedEquipment) bottleneck.getEquipment();
int disabled = bottleneckEquip.disableAllConstraints();
logger.info("Disabled " + disabled + " constraints on "
    + bottleneck.getEquipmentName());
```

### 21.5.3 Process-Wide Constraint Disable

The following diagnostic disables capacity checks and reruns the same imposed feed. Disabling checks does not change the equipment geometry, solve reservoir deliverability, or increase production. A separate bounded optimization is needed to quantify any rate change, and the omitted limits must be restored for the accepted case.

```java
// Disable ALL constraints on ALL equipment
int totalDisabled = process.disableAllConstraints();
logger.info("Disabled " + totalDisabled + " constraints system-wide");

// Re-run the same fixed feed with capacity reporting disabled
process.run();
double imposedFeedRate =
    feed.getFlowRate("kg/hr");
```

### 21.5.4 Full Exclusion from Capacity Analysis

For equipment that should not participate in capacity analysis at all (e.g., utility equipment, test separators):

```java
// Exclude equipment from all capacity analysis
equipment.setCapacityAnalysisEnabled(false);
```

When `capacityAnalysisEnabled` is `false`, the equipment is excluded from `findBottleneck()`, `getCapacityUtilizationSummary()`, `getEquipmentNearCapacityLimit()`, and all other system-level capacity queries.

### 21.5.5 Comparison of Disable Methods

| Method | Scope | Effect | Use Case |
|--------|-------|--------|----------|
| `constraint.setEnabled(false)` | Single constraint | Skips this constraint in utilization | Test removing one limit |
| `equipment.disableAllConstraints()` | All constraints on one equipment | Returns count of disabled | Simulate equipment upgrade |
| `process.disableAllConstraints()` | All constraints in system | Returns total count | Diagnose the effect of omitted checks |
| `equipment.setCapacityAnalysisEnabled(false)` | Equipment level | Excludes from all analysis | Ignore utility equipment |

### 21.5.6 Debottlenecking Waterfall Analysis

A particularly effective way to visualize debottlenecking potential is the **waterfall chart**, which shows the cumulative production gain as each bottleneck is removed in sequence:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer
import jpype
jneqsim = jpype.JPackage("neqsim")

fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 70.0, 65.0)
fluid.addComponent("methane", 0.70)
fluid.addComponent("ethane", 0.08)
fluid.addComponent("propane", 0.05)
fluid.addComponent("n-butane", 0.03)
fluid.addComponent("n-heptane", 0.08)
fluid.addComponent("water", 0.06)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

feed = jneqsim.process.equipment.stream.Stream("feed", fluid)
feed.setFlowRate(200000.0, "kg/hr")

sep = jneqsim.process.equipment.separator.ThreePhaseSeparator("HP Sep", feed)
comp = jneqsim.process.equipment.compressor.Compressor("Export Comp",
    sep.getGasOutStream())
comp.setOutletPressure(150.0)
comp.setPolytropicEfficiency(0.78)

process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(sep)
process.add(comp)
process.run()

# Auto-size with 20% design margin
sep.autoSize(1.2)
comp.autoSize(1.2)

print(f"Separator utilization: {sep.getMaxUtilizationPercent():.1f}%")
print(f"Compressor utilization: {comp.getMaxUtilizationPercent():.1f}%")

from pathlib import Path
Path("figures").mkdir(parents=True, exist_ok=True)
import matplotlib.pyplot as plt
import numpy as np

# Run sequential debottleneck analysis
bottlenecks = []
current_rate = float(feed.getFlowRate("kg/hr"))
base_rate = current_rate

for step in range(8):
    result = process.findBottleneck()
    if not result.hasBottleneck():
        break

    # Record current bottleneck
    name = str(result.getEquipmentName())
    constraint = str(result.getConstraintName())

    # Disable it
    result.getConstraint().setEnabled(False)
    config = (ProductionOptimizer.OptimizationConfig(50000.0, 300000.0).rateUnit("kg/hr")
              .searchMode(ProductionOptimizer.SearchMode.BINARY_FEASIBILITY))
    optimum = ProductionOptimizer().optimize(process, feed, config, None, None)
    process.run()

    new_rate = float(feed.getFlowRate("kg/hr"))
    gain = new_rate - current_rate
    bottlenecks.append({
        'equipment': name,
        'constraint': constraint,
        'gain': gain,
        'cumulative': new_rate
    })
    current_rate = new_rate

# Create waterfall chart
fig, ax = plt.subplots(figsize=(12, 6))
labels = ['Current'] + [b['equipment'] for b in bottlenecks] + ['Maximum']
values = [base_rate] + [b['gain'] for b in bottlenecks]
cumulative = [base_rate]
for b in bottlenecks:
    cumulative.append(b['cumulative'])
cumulative.append(cumulative[-1])

# Color-code: base=blue, gains=green, total=darkblue
colors = ['steelblue'] + ['forestgreen'] * len(bottlenecks) + ['navy']

bottoms = [0] + cumulative[:-1]
ax.bar(range(len(labels)), [base_rate] + [b['gain'] for b in bottlenecks] + [0],
       bottom=[0] + [cumulative[i] for i in range(len(bottlenecks))] + [0],
       color=colors, edgecolor='white')

ax.set_xlabel('Debottlenecking Step')
ax.set_ylabel('Production Rate (kg/hr)')
ax.set_title('Debottlenecking Waterfall Analysis')
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha='right')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('figures/waterfall_debottleneck.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\nTotal potential gain: {current_rate - base_rate:.0f} kg/hr "
      f"({(current_rate/base_rate - 1)*100:.1f}% increase)")
```

This waterfall analysis reveals not just the first bottleneck, but the entire **bottleneck sequence** — the ordered list of constraints that must be removed to progressively increase production. Often, removing the first bottleneck yields 60-80% of the total potential gain, with diminishing returns for subsequent debottlenecks.

### 21.5.7 Practical Debottlenecking Workflow

A structured debottlenecking study follows these steps:

```text
1. Build and run process model at current conditions
2. autoSize all equipment to create capacity constraints
3. Identify current bottleneck (findBottleneck)
4. Disable bottleneck constraint
5. Re-optimize process with ProductionOptimizer
6. Quantify production gain (ΔQ)
7. Re-enable constraint, identify next bottleneck
8. Repeat steps 4-7 for each potential debottleneck
9. Rank debottlenecking options by ΔQ/cost ratio
```

The production gain from removing a bottleneck is:

$$
\Delta Q = Q_{\text{debottlenecked}} - Q_{\text{current}}
$$

The debottlenecking value is:

$$
\text{Value} = \frac{\Delta Q \times \text{Price} \times \text{Time}}{\text{CAPEX}_{\text{modification}}}
$$

---

## 21.6 Utilization Summary Dashboard

Effective debottlenecking requires clear visualization of equipment utilization across the entire facility. NeqSim's `getCapacityUtilizationSummary()` method provides the data foundation for building utilization dashboards.

### 21.6.1 Building Utilization Bar Charts

The utilization summary provides all the data needed for a horizontal bar chart showing equipment utilization:

```java
Map<String, Double> utilization = process.getCapacityUtilizationSummary();

// Color coding based on utilization level
for (Map.Entry<String, Double> entry : utilization.entrySet()) {
    double u = entry.getValue();
    String status;
    if (u > 1.0) {
        status = "OVERLOADED";
    } else if (u > 0.90) {
        status = "NEAR LIMIT";
    } else if (u > 0.75) {
        status = "MODERATE";
    } else {
        status = "OK";
    }
    logger.info(String.format("%-25s %6.1f%%  [%s]\n",
        entry.getKey(), u * 100, status));
}
```

### 21.6.2 Color-Coded Status Visualization

The recommended color scheme for utilization visualization:

| Utilization Range | Color | Status | Action |
|------------------|-------|--------|--------|
| 0–75% | Green | OK | Normal operation |
| 75–90% | Yellow | Moderate | Monitor, plan for growth |
| 90–100% | Orange | Near limit | Active monitoring, consider debottlenecking |
| >100% | Red | Overloaded | Immediate action required |

### 21.6.3 Near-Limit Early Warning System

An early warning system can be implemented using `getEquipmentNearCapacityLimit()` with different thresholds:

```java
// Thresholds are explicit filters of the current utilization summary.
List<String> tier1 = new ArrayList<String>();
List<String> tier2 = new ArrayList<String>();
List<String> tier3 = new ArrayList<String>();
for (Map.Entry<String, Double> item : process.getCapacityUtilizationSummary().entrySet()) {
    if (item.getValue() > 0.95) { tier1.add(item.getKey()); }
    if (item.getValue() > 0.85) { tier2.add(item.getKey()); }
    if (item.getValue() > 0.75) { tier3.add(item.getKey()); }
}
logger.info("Critical above 95 percent: {}", tier1);
logger.info("Warning above 85 percent: {}", tier2);
logger.info("Watch above 75 percent: {}", tier3);
```

### 21.6.4 Equipment Prioritization for Investment

The utilization data enables objective prioritization of upgrade investments:

$$
\text{Priority Score}_i = U_i \times \frac{\Delta Q_i}{\text{CAPEX}_i}
$$

where $U_i$ is the current utilization, $\Delta Q_i$ is the potential production gain from debottlenecking, and $\text{CAPEX}_i$ is the estimated modification cost.

Equipment with the highest priority scores should be considered first for debottlenecking investment. This is a heuristic screening score with units of rate per currency. It does not replace NPV, engineering judgment, uncertainty analysis, installation feasibility or the interactions between modifications.

---

## 21.7 Python Debottlenecking Workflow

This section presents a complete Python workflow for debottlenecking analysis using NeqSim.

### 21.7.1 Building the Process Model

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import matplotlib.pyplot as plt
import numpy as np

# Create fluid
fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 60.0, 80.0)
fluid.addComponent("methane", 0.72)
fluid.addComponent("ethane", 0.08)
fluid.addComponent("propane", 0.05)
fluid.addComponent("n-butane", 0.03)
fluid.addComponent("n-pentane", 0.02)
fluid.addComponent("water", 0.10)
fluid.setMixingRule("classic")
fluid.setMultiPhaseCheck(True)

# Build process
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
Compressor = jneqsim.process.equipment.compressor.Compressor
ThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve
Heater = jneqsim.process.equipment.heatexchanger.Heater
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

feed = Stream("Feed", fluid)
feed.setFlowRate(150000.0, "kg/hr")
feed.setTemperature(60.0, "C")
feed.setPressure(80.0, "bara")

hp_sep = Separator("HP Separator", feed)

compressor = Compressor("HP Compressor", hp_sep.getGasOutStream())
compressor.setOutletPressure(150.0, "bara")

cooler = Heater("After-cooler", compressor.getOutletStream())
cooler.setOutTemperature(273.15 + 40.0)

choke = ThrottlingValve("Wellhead Choke", feed)
choke.setOutletPressure(80.0, "bara")

process = ProcessSystem()
process.add(feed)
process.add(hp_sep)
process.add(compressor)
process.add(cooler)
process.run()
```

### 21.7.2 Auto-Sizing and Bottleneck Identification

```python
# Auto-size all equipment with design margins
hp_sep.autoSize(1.20)       # Multiplicative factor: 20% margin
compressor.autoSize(1.15)   # Multiplicative factor: 15% margin

# Find the bottleneck
result = process.findBottleneck()
if result.hasBottleneck():
    print(f"Bottleneck: {result.getEquipmentName()}")
    print(f"Constraint: {result.getConstraintName()}")
    print(f"Utilization: {result.getUtilization() * 100:.1f}%")
    print(f"Type: {result.getConstraint().getType()}")

# Get full utilization summary
utilization = process.getCapacityUtilizationSummary()
print("\n=== Equipment Utilization ===")
for name in utilization.keySet():
    u = utilization.get(name)
    print(f"  {str(name):<25s} {u * 100:6.1f}%")
```

### 21.7.3 What-If Analysis

```python
# Record baseline production
baseline_flow = float(feed.getFlowRate("kg/hr"))

# Disable bottleneck constraint
bottleneck_constraint = result.getConstraint()
bottleneck_constraint.setEnabled(False)

# Re-run to find new operating point
process.run()
debottlenecked_flow = float(feed.getFlowRate("kg/hr"))

# Calculate gain
delta_q = debottlenecked_flow - baseline_flow
print(f"\nBaseline production:      {baseline_flow:.0f} kg/hr")
print(f"Debottlenecked production: {debottlenecked_flow:.0f} kg/hr")
print(f"Production gain:           {delta_q:.0f} kg/hr ({delta_q/baseline_flow*100:.1f}%)")

# Re-enable and find next bottleneck
bottleneck_constraint.setEnabled(True)
```

### 21.7.4 Utilization Dashboard Visualization

```python
from pathlib import Path
Path("figures").mkdir(parents=True, exist_ok=True)
# Get utilization data
utilization = process.getCapacityUtilizationSummary()
names = [str(k) for k in utilization.keySet()]
values = [float(utilization.get(k)) * 100 for k in utilization.keySet()]

# Sort by utilization
sorted_idx = np.argsort(values)
names = [names[i] for i in sorted_idx]
values = [values[i] for i in sorted_idx]

# Color-code bars
colors = []
for v in values:
    if v > 100:
        colors.append('#d32f2f')    # Red - overloaded
    elif v > 90:
        colors.append('#f57c00')    # Orange - near limit
    elif v > 75:
        colors.append('#fbc02d')    # Yellow - moderate
    else:
        colors.append('#388e3c')    # Green - OK

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(names, values, color=colors, edgecolor='black', linewidth=0.5)
ax.axvline(x=100, color='red', linestyle='--', linewidth=1.5, label='Design Capacity')
ax.axvline(x=90, color='orange', linestyle=':', linewidth=1.0, label='Warning (90%)')
ax.set_xlabel('Utilization (%)')
ax.set_title('Equipment Capacity Utilization Dashboard')
ax.legend(loc='lower right')
ax.set_xlim(0, max(values) * 1.1)

for bar, val in zip(bars, values):
    ax.text(val + 1, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}%', va='center', fontsize=9)

plt.tight_layout()
plt.savefig('figures/utilization_dashboard.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 21.7.5 Sensitivity Analysis — Flow Rate vs Bottleneck

A key analysis in debottlenecking is understanding how the bottleneck changes as production rate varies:

```python
from pathlib import Path
Path("figures").mkdir(parents=True, exist_ok=True)
# Sweep feed flow rate
flow_rates = np.linspace(50000, 250000, 20)  # kg/hr
bottleneck_names = []
bottleneck_utils = []

for flow in flow_rates:
    feed.setFlowRate(float(flow), "kg/hr")
    process.run()

    result = process.findBottleneck()
    if result.hasBottleneck():
        bottleneck_names.append(str(result.getEquipmentName()))
        bottleneck_utils.append(float(result.getUtilization()) * 100)
    else:
        bottleneck_names.append("None")
        bottleneck_utils.append(0.0)

# Plot bottleneck utilization vs flow rate
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(flow_rates / 1000, bottleneck_utils, 'b-o', linewidth=2)
ax1.axhline(y=100, color='red', linestyle='--', label='Design Capacity')
ax1.set_xlabel('Feed Flow Rate (t/hr)')
ax1.set_ylabel('Bottleneck Utilization (%)', color='blue')
ax1.set_title('Bottleneck Utilization vs Production Rate')
ax1.grid(True, alpha=0.3)
ax1.legend()

# Annotate bottleneck transitions
prev_name = bottleneck_names[0]
for i, name in enumerate(bottleneck_names):
    if name != prev_name:
        ax1.axvline(x=flow_rates[i]/1000, color='gray', linestyle=':', alpha=0.7)
        ax1.text(flow_rates[i]/1000, 50, f'→ {name}', rotation=90,
                 va='center', fontsize=8, color='gray')
        prev_name = name

plt.tight_layout()
plt.savefig('figures/bottleneck_sensitivity.png', dpi=150, bbox_inches='tight')
plt.show()
```

This sensitivity plot reveals critical information: at what production rate does the bottleneck shift from one equipment item to another? This determines the sequence of debottlenecking projects needed to reach different production targets.

---

## 21.8 Constraint Preset Libraries

Different operating companies and industry standards define different constraint values for the same equipment types. NeqSim supports switchable constraint presets through the `useEquinorConstraints()` and `useAPIConstraints()` methods.

### 21.8.1 Equinor Constraints

The separator method selects a broader constraint subset, including gas load, K-value, droplet cut size, inlet momentum and liquid retention. The name identifies a library preset, not a verified copy of an operating company's current project requirements:

```java
separator.useEquinorConstraints();
// Inspect the resulting constraints; this preset is not a compliance certificate.
```

Record the following evidence before treating a selected preset as an installed-equipment check:

| Limit | Required basis |
|---|---|
| Separator gas load and droplet removal | Vessel geometry, internals and fluid properties |
| Liquid retention | Working inventory and actual outlet volume rate |
| Compressor operating region | Vendor map, speed, gas basis and control settings |
| Pipeline capacity | Route, internal diameter, wall condition and arrival requirements |
| Valve capacity and controllability | Trim data, service conditions and available pressure drop |

### 21.8.2 API Constraints

The separator API preset enables gas load, K-value and oil/water retention constraints. It does not enable every check required by an API equipment standard:

```java
separator.useAPIConstraints();
// Inspect the resulting constraints; this preset is not a compliance certificate.
```

Select the governing equipment standard and edition independently, then map its applicable requirements to explicit model inputs and checks. A library preset cannot substitute for that applicability review.

### 21.8.3 Custom Constraint Presets

For company-specific or project-specific requirements, constraints can be set manually:

```java
// Create custom constraints
CapacityConstraint customGasLoad = new CapacityConstraint(
    "gasLoadFactor", "m/s", ConstraintType.SOFT)
    .setDesignValue(0.12)     // Custom K-factor
    .setMaxValue(0.15)        // Absolute max
    .setWarningThreshold(0.88)
    .setValueSupplier(() -> separator.getGasLoadFactor());  // Warn at 88%

separator.addCapacityConstraint(customGasLoad);
```

---

## 21.9 Debottlenecking Economics

The value of debottlenecking must be assessed against the cost of modification. This section provides the economic framework for prioritizing debottlenecking projects.

### 21.9.1 Production Gain Quantification

The incremental production from removing a bottleneck is:

$$
\Delta Q_{\text{oil}} = Q_{\text{debottlenecked}} - Q_{\text{current}}
$$

The annual revenue gain is:

$$
\Delta R = \Delta Q_{\text{oil}} \times P_{\text{oil}} \times 365 \times \eta_{\text{uptime}}
$$

where $P_{\text{oil}}$ is the oil price and $\eta_{\text{uptime}}$ is the production uptime fraction (typically 0.90–0.95 for offshore platforms).

### 21.9.2 Debottlenecking NPV

The Net Present Value of a debottlenecking project:

$$
\text{NPV} = -\text{CAPEX}_{\text{mod}} + \sum_{t=1}^{T} \frac{\Delta R_t - \Delta \text{OPEX}_t}{(1+r)^t}
$$

where $\text{CAPEX}_{\text{mod}}$ is the modification cost, $T$ is the remaining field life, and $r$ is the discount rate.

### 21.9.3 Priority Ranking

Debottlenecking options should be ranked by the ratio of NPV to CAPEX (profitability index):

$$
\text{PI}=\frac{\mathrm{PV}(\text{incremental net operating cash flows})}{\mathrm{CAPEX}_{mod}}=1+\frac{\mathrm{NPV}}{\mathrm{CAPEX}_{mod}}
$$

For this single initial-outlay definition, PI > 1 is equivalent to positive NPV. A high ratio alone does not determine project priority: mutually exclusive options, capital rationing, uncertainty and shutdown losses matter. The ratio NPV/CAPEX is sometimes used as a separate ranking measure and has a zero, rather than one, break-even threshold.

### 21.9.4 Screening with Python

```python
import numpy as np

# Debottlenecking options from capacity analysis
options = [
    {"name": "Uprate HP compressor driver", "capex_mnok": 45, "delta_q_bpd": 8000},
    {"name": "Add cyclone inlet to HP sep",  "capex_mnok": 15, "delta_q_bpd": 4500},
    {"name": "Add 3rd hydrocyclone",         "capex_mnok": 25, "delta_q_bpd": 3000},
    {"name": "VSD on LP compressor",         "capex_mnok": 60, "delta_q_bpd": 6000},
    {"name": "Drag reduction agent",         "capex_mnok": 5,  "delta_q_bpd": 2000},
]

oil_price_usd_bbl = 70.0
uptime = 0.93
remaining_years = 10
discount_rate = 0.08
nok_per_usd = 10.5

print(f"{'Option':<35s} {'CAPEX':>8s} {'ΔQ':>8s} {'NPV':>8s} {'PI':>6s}")
print("-" * 70)

for opt in options:
    annual_revenue_mnok = (opt["delta_q_bpd"] * oil_price_usd_bbl * 365
                           * uptime * nok_per_usd / 1e6)
    # Simple NPV (no OPEX change assumed)
    pv_factor = sum(1/(1+discount_rate)**t for t in range(1, remaining_years+1))
    npv = -opt["capex_mnok"] + annual_revenue_mnok * pv_factor
    pi = npv / opt["capex_mnok"]

    print(f"  {opt['name']:<33s} {opt['capex_mnok']:>6.0f}  "
          f"{opt['delta_q_bpd']:>6.0f}  {npv:>7.0f}  {pi:>5.1f}")
```

### 21.9.5 Economic Ranking with DebottleneckingAdvisor

NeqSim provides `DebottleneckingAdvisor` (package `neqsim.process.optimization.valuechain`) to rank explicitly supplied modification candidates under consistent economic assumptions and associate the resulting value estimates with capacity constraints. The annual incremental value in the example is an assumed input; the advisor does not simulate the extra production automatically.

The advisor is configured with an `EconomicParameters` object (shared with the value-chain tools of Chapter 32) and one `DebottleneckCandidate` per option:

```java
EconomicParameters econ = new EconomicParameters()
    .setOilPrice(4500.0)        // NOK/Sm3
    .setDiscountRate(0.08)
    .setCurrency("NOK");

DebottleneckingAdvisor advisor = new DebottleneckingAdvisor(econ);

// addCandidate(name, targetEquipment, capexNok, firstYear, lastYear,
//              annualIncrementalValueNok, CapacityConstraint (nullable))
advisor.addCandidate(new DebottleneckingAdvisor.DebottleneckCandidate(
    "Uprate HP compressor driver", "HP compressor",
    45.0e6, 1, 10, 190.0e6,
    compressor.getCapacityConstraints().get("power")));

advisor.addCandidate(new DebottleneckingAdvisor.DebottleneckCandidate(
    "Add cyclone inlet to HP sep", "HP separator",
    15.0e6, 1, 10, 105.0e6, null));

List<DebottleneckingAdvisor.Recommendation> ranked = advisor.evaluate();
for (DebottleneckingAdvisor.Recommendation r : ranked) {
    logger.info(String.format("%-32s NPV=%,.0f  BCR=%.2f  payback=%.1f yr  %s%n",
        r.getCandidate().getName(), r.getNpvNok(), r.getBenefitCostRatio(),
        r.getPaybackYears(), r.isAttractive() ? "ATTRACTIVE" : "reject"));
}
```

`evaluate()` returns the recommendations sorted by descending NPV. Each `Recommendation` exposes `getNpvNok()`, `getPvBenefitsNok()`, `getBenefitCostRatio()`, `getPaybackYears()`, and `isAttractive()` (NPV > 0). Calling `applyShadowPrices()` then propagates the marginal value of each binding constraint back to the corresponding `CapacityConstraint` object (Section 21.2.3), so that a later utilization report shows not only *how loaded* each equipment item is but *how much production value* its limit is currently withholding. The full result set is available as JSON via `toJson()` for inclusion in a debottlenecking study.

---

## 21.10 Case Study — Offshore Platform Debottlenecking

Consider an aging North Sea platform originally designed for 120,000 bbl/d oil production. After 15 years, reservoir pressure has declined from 350 bara to 220 bara, water cut has increased from 5% to 35%, and gas-oil ratio has risen from 150 to 280 Sm³/Sm³. The operator wants to evaluate debottlenecking options to maintain the 80,000 bbl/d plateau target.

### 21.10.1 Approach

1. Build the full topside process model in NeqSim
2. AutoSize all equipment using original design specifications
3. Run the model at current reservoir conditions
4. Identify the bottleneck sequence
5. Evaluate debottlenecking options with cost estimates

### 21.10.2 Process Model Setup

The topside process consists of:

- **Inlet separation**: 3-phase HP separator (design: 120,000 bbl/d, 80 bara)
- **Gas compression**: 2-stage compression (HP: 80→150 bara, LP: 10→80 bara)
- **Water treatment**: Hydrocyclone package (design: 15,000 m³/d)
- **Oil export**: Export pump and pipeline (30 km, 16-inch)
- **Gas export**: Export compressor and pipeline (120 km, 24-inch)

```java
// A synthetic mass-flow case; field barrels require a separate density basis.
ProcessSystem topside = new ProcessSystem();
Stream wellStream = new Stream("Well Stream", reservoirFluid.clone());
wellStream.setFlowRate(100000.0, "kg/hr");
Separator hpSep = new Separator("HP Separator", wellStream);
Compressor hpComp = new Compressor("HP Compressor", hpSep.getGasOutStream());
hpComp.setOutletPressure(150.0, "bara");
hpComp.setIsentropicEfficiency(0.75);
topside.add(wellStream);
topside.add(hpSep);
topside.add(hpComp);
topside.run();
hpSep.autoSize(1.20);
hpComp.autoSize(1.15);
logger.info("Screening bottleneck: {}", topside.findBottleneck());
```

### 21.10.3 Bottleneck Sequence Analysis

The following assumed planning data illustrate a possible bottleneck sequence. They are not outputs of the small executable fixture in this chapter; a full model and installed ratings are needed to reproduce them:

| Production Rate (bbl/d) | Bottleneck | Constraint | Utilization |
|------------------------|-----------|-----------|-------------|
| 60,000 | None | — | <75% all |
| 70,000 | HP Compressor | Power | 82% |
| 80,000 | HP Compressor | Power | 98% |
| 90,000 | HP Compressor | Power | 112% (overloaded) |
| After HP Comp fix | HP Separator | Gas load factor | 95% |
| After both fixes | Water treatment | Hydrocyclone capacity | 91% |

### 21.10.4 Key Findings

| Rank | Equipment | Constraint | Utilization | Fix | Est. Cost (MNOK) |
|------|-----------|-----------|-------------|-----|------------------|
| 1 | HP Compressor | Power | 98% | Uprate driver | 45 |
| 2 | HP Separator | Gas load factor | 91% | Add cyclone inlet | 15 |
| 3 | Water treatment | Hydrocyclone capacity | 87% | Add 3rd hydrocyclone | 25 |
| 4 | LP Compressor | Surge margin | 82% | Variable speed drive | 60 |
| 5 | Export pipeline | Velocity | 78% | Drag reduction agent | 5 |

The assumed data suggest checking compressor power first. They do not establish the production gain or investment ranking; that requires solved before/after cases with all other constraints retained.

### 21.10.5 Recommended Debottlenecking Sequence

The candidate list is a planning exercise, not a computed NPV ranking. Separator internals, drag-reducer compatibility, compressor uprating and water-treatment expansion must each be checked against the active constraint. An option that does not relieve an active constraint may produce no extra saleable production.

For the assumed costs above, separator internals (15 MNOK), liquid-service DRA equipment (5 MNOK) and a driver uprate (45 MNOK) total 65 MNOK. Including the assumed hydrocyclone expansion adds 25 MNOK, bringing the total to 90 MNOK. No production gain, profitability index or payback is established for this hypothetical platform until currency-consistent incremental cash flows are supplied.

---

## 21.11 Debottlenecking Economics

### 21.11.1 Cost-Benefit Analysis Framework

Debottlenecking investments must be evaluated against the incremental revenue they generate. The fundamental economic metric is the **debottlenecking value ratio** — the ratio of incremental production value to modification cost:

$$
\text{Gross value ratio}=\frac{365\,\eta_{up}\,\Delta Q\,P_{oil}\,T_{remaining}}{C_{modification}}
$$

where $\Delta Q$ is the production gain [bbl/d], $P_{\text{oil}}$ is the oil price [$/bbl], $T_{\text{remaining}}$ is the remaining field life [years], and $C_{\text{modification}}$ is the total installed cost of the modification [$]. Use one currency throughout. This undiscounted gross-revenue ratio omits incremental OPEX, decline, tax, shutdown losses and timing, so it is not an investment acceptance criterion.

### 21.11.2 Simple Payback Period

The **simple payback period** is the most commonly used screening metric for debottlenecking projects:

$$
T_{\text{payback}} = \frac{C_{\text{modification}}}{\Delta Q \times P_{\text{oil}} \times 365}
$$

For an explicitly assumed exchange rate of 10 NOK/USD, a 45 MNOK uprate and an assumed additional 5000 bbl/day at USD 70/bbl give a **gross-revenue-only** payback:

$$
T_{gross}=\frac{45\times10^6}{5000\times70\times10\times365}
=0.0352\ \mathrm{year}=12.9\ \mathrm{days}.
$$

The calculation is an arithmetic check, not a project forecast. Actual net payback includes incremental OPEX, downtime, uptime, decline and taxes; the assumed production gain must first be established by reservoir and facility models. The exchange rate is a teaching input, not a current market quote.

### 21.11.3 NPV and IRR for Debottlenecking Modifications

For larger investments or when timing of cash flows matters, the **Net Present Value (NPV)** provides a more rigorous assessment:

$$
\text{NPV} = -C_0 + \sum_{t=1}^{N} \frac{\Delta Q_t \times P_t - \Delta\text{OPEX}_t}{(1 + r)^t}
$$

where $C_0$ is the initial investment, $\Delta Q_t$ is the incremental annual produced volume in year $t$, not a daily rate (it may decline as the reservoir depletes), $P_t$ is the oil price in year $t$, $\Delta\text{OPEX}_t$ is the incremental operating cost (maintenance, energy, chemicals), and $r$ is the discount rate.

The **Internal Rate of Return (IRR)** is the discount rate at which NPV = 0. IRR is meaningful only when a valid cash-flow root exists; nonconventional cash flows may have multiple or no IRRs. Use NPV at the declared discount rate as the primary comparison rather than assuming a generic high return.

### 21.11.4 Typical Debottlenecking Costs

The following assumed cost and schedule ranges are classroom screening inputs, not sourced 2024 NCS estimates or vendor quotations. Establish project location, price year, currency, estimate class, installation scope, shutdown losses and uncertainty before use:

| Modification | Typical Cost (MNOK) | Shutdown Required | Lead Time |
|-------------|---------------------|------------------|-----------|
| Rerate compressor driver (uprate turbine) | 30–80 | Yes (2–4 weeks) | 12–18 months |
| Add variable speed drive to compressor | 40–80 | Yes (3–5 weeks) | 14–20 months |
| Upgrade separator internals (inlet device) | 8–20 | Yes (1–2 weeks) | 6–12 months |
| Add parallel separator (new vessel) | 80–200 | Partial | 18–30 months |
| Add 3rd hydrocyclone stage | 15–35 | Yes (1–2 weeks) | 8–14 months |
| Pipeline looping (offshore, per km) | 40–80/km | No | 18–24 months |
| Drag reducing agent (DRA) injection system | 3–8 | No | 3–6 months |
| Heat exchanger bundle replacement | 10–25 | Yes (1–2 weeks) | 6–12 months |
| Add fin-fan cooler bank | 20–50 | No | 10–16 months |
| Choke valve replacement (higher Cv) | 2–5 | Brief (hours) | 2–4 months |

**Key observations:**

- Modifications that do not require a production shutdown (DRA injection, pipeline looping, fin-fan addition) carry lower implementation risk and can often be justified with shorter payback periods
- Separator internal upgrades (e.g., replacing a basic inlet device with an inlet cyclone) offer high production gains at relatively low cost, giving them excellent value ratios
- Large capital items (new vessels, new compressor trains) typically require 2–3 years of planning and fabrication and are justified only when the remaining field life exceeds 10 years

### 21.11.5 Automated Capacity Report Generation

NeqSim's capacity constraint framework enables automated generation of debottlenecking reports. The following Python workflow scans all equipment, identifies constraints near their limits, and produces a prioritized debottlenecking summary:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import json

ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# Assume 'process' is an existing, converged ProcessSystem

# Step 1: Get utilization for all equipment
utilization = process.getCapacityUtilizationSummary()

# Step 2: Identify equipment near capacity limits (>80%)
near_limit = process.getEquipmentNearCapacityLimit()

# Step 3: Find the bottleneck at current operating point
bottleneck = process.findBottleneck()

# Step 4: Build debottlenecking report
report = {
    "facility": "Platform X",
    "date": "2025-01-15",
    "total_production_kg_hr": float(process.getUnit("Feed").getFlowRate("kg/hr")),
    "bottleneck": {
        "equipment": str(bottleneck.getEquipmentName()) if bottleneck.hasBottleneck() else "None",
        "constraint": str(bottleneck.getConstraintName()) if bottleneck.hasBottleneck() else "N/A",
        "utilization_pct": round(float(bottleneck.getUtilization()) * 100, 1) if bottleneck.hasBottleneck() else 0
    },
    "equipment_utilization": {},
    "near_limit_equipment": [str(e) for e in near_limit],
}

for name in utilization.keySet():
    report["equipment_utilization"][str(name)] = round(float(utilization.get(name)) * 100, 1)

print(json.dumps(report, indent=2))
```

This automated approach enables regular (weekly or monthly) capacity assessments without manual engineering effort, ensuring that debottlenecking opportunities are identified as soon as they arise.

---


<!-- September 2026 source update -->
## Debottlenecking with a reproducible constraint ladder

The latest plant-evidence layer changes the deliverable of a debottlenecking study. For each proposed modification, retain the baseline state, the changed design or operating variable, the current solved state, and the complete ranked list of applicable constraints. When compressor power is relaxed, a receiving-pressure or shared-power restriction may become controlling. The new bottleneck is meaningful only if both the old and new restrictions retain stable identities and comparable evidence \cite{neqsim2026update}.

Do not rank capital projects from `autoSize()` margins alone. Replace synthetic ratings with installed-equipment provenance, then repeat the process calculation. For a shared driver or electrical bus, reconcile all declared participants before assessing budget headroom. A missing participant is unavailable evidence; it is not a zero-power load. For a separator, retained vessel dimensions and internals assumptions must accompany changes in gas load, liquid residence and phase availability.

The recommended decision table contains baseline throughput, replayed candidate throughput, incremental power, binding restriction, remaining margin, evidence coverage and uncertainty. A project that increases a numerical optimum but makes the next restriction unavailable should remain unresolved until that evidence gap is closed.

---


<!-- reviewed-notebook-results:start -->
## Reproduced Calculation Results

These examples use the stated fluid recipes and operating assumptions. Curves represent NeqSim calculations unless a caption identifies an analytical illustration, assumed equipment map or synthetic data.

![Initial Bottleneck: Compressor Stage 2. Illustrative arithmetic capacity cascade](figures/ch21_debottleneck_cascade.png)

Utilization spans 84–97.78 % across the plotted cases. Utilization spans 78.97–96.25 % across the plotted cases.

This arithmetic cascade increases a selected equipment rating, then scales assumed loads until the next unit becomes limiting. The diagram explains bottleneck migration; it is not a flowsheet simulation of an equipment retrofit. Use the cascade to prioritize full-process reruns, with pressure, phase split and power recalculated after each change.

Selected numerical ranges from the plotted cases:

| Quantity / series | Minimum | Maximum | Unit |
|---|---:|---:|---|
| Utilization | 84 | 97.78 | % |

Ranges describe the sampled cases; they are not independent validation tolerances.
<!-- reviewed-notebook-results:end -->

## 21.9 Summary

This chapter presented a systematic approach to debottlenecking and capacity management using NeqSim's Capacity Constraint Framework. The key concepts are:

1. **Capacity constraints** are standardized through the `CapacityConstrainedEquipment` interface, with 18 built-in strategy plugins covering all major equipment types
2. **Bottleneck identification** is automated through `ProcessSystem.findBottleneck()` and related methods
3. **autoSize** creates constraints from design calculations, enabling quick capacity assessment of existing equipment
4. **What-if analysis** through selective constraint disabling quantifies the production gain from each potential debottleneck
5. **Utilization dashboards** provide visual tracking of equipment capacity status across the facility
6. **Sensitivity analysis** reveals how the bottleneck shifts with changing production conditions

The debottlenecking workflow presented here — identify, quantify, evaluate, implement — can deliver significant production increases at a fraction of the cost of new facilities.

---

## Exercises

1. **Constraint Classification**: For each of the following equipment limits, classify as HARD, SOFT, or DESIGN: (a) compressor maximum speed, (b) separator design flow rate, (c) heat exchanger approach temperature, (d) vessel maximum allowable working pressure, (e) valve Cv utilization at 85%.

2. **Bottleneck Identification**: Given a process with three separators at 78%, 92%, and 65% utilization and two compressors at 88% and 95% utilization, identify the bottleneck and calculate the system capacity if the target throughput is 100,000 kg/hr.

3. **autoSize Application**: Build a NeqSim process model with a feed stream, separator, compressor, and cooler. Apply `autoSize` to all equipment and generate a utilization summary. Increase the feed rate by 20% and identify which equipment becomes the bottleneck.

4. **What-If Debottlenecking**: Starting from Exercise 3, disable the bottleneck constraint and re-run. What is the new bottleneck? Calculate the total production gain from removing both the first and second bottleneck.

5. **Sensitivity Study**: Create a Python script that sweeps the feed flow rate from 50% to 150% of design and plots the bottleneck utilization and equipment name as a function of flow rate. At what flow rate does the bottleneck shift from one equipment to another?

6. **Utilization Dashboard**: Build a complete utilization dashboard for a gas compression platform with inlet separator, three compression stages, inter-stage coolers, scrubbers, and export pipeline. Color-code by status and identify the top three upgrade priorities.

7. **Economic Evaluation**: For the platform in Exercise 6, estimate the production gain from debottlenecking each of the top three constraints. If oil price is $70/bbl and the modifications cost 20, 45, and 80 MNOK respectively, calculate the gross and net payback for each option using an explicitly assumed exchange rate, uptime and incremental operating cost.

---

## References

1. The hypothetical platform assumptions in this chapter are teaching data; no internal company report has been supplied or used as evidence.
2. API Recommended Practice 14E (2007). *Recommended Practice for Design and Installation of Offshore Production Platform Piping Systems*. American Petroleum Institute.
3. Campbell, J.M. (2014). *Gas Conditioning and Processing*, Vol. 2, 9th Edition. Campbell Petroleum Series.
4. Ludwig, E.E. (1999). *Applied Process Design for Chemical and Petrochemical Plants*, Vol. 1–3. Gulf Professional Publishing.
5. Lieberman, N. (2009). *Process Equipment Malfunctions: Techniques to Identify and Correct Plant Problems*. McGraw-Hill.
6. Smith, R. (2016). *Chemical Process Design and Integration*, 2nd Edition. Wiley.


