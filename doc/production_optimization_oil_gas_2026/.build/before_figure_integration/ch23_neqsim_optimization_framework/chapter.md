# The NeqSim Optimization Framework

<!-- Chapter metadata -->
<!-- Notebooks: ch25_optimization_framework_demo.ipynb, ch25_custom_objectives.ipynb, ch25_pareto_optimization.ipynb -->
<!-- Estimated pages: 35 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Describe the three-layer architecture of the NeqSim optimization framework — simulation engine, constraint engine, and optimizer — and explain how they interact during an optimization run
2. Use the `ProcessAutomation` API to discover, read, and write simulation variables by string address, including area-qualified addresses for multi-area plants
3. Explain the role of the `CapacityConstrainedEquipment` interface and distinguish between HARD, SOFT, and DESIGN constraint types
4. Configure and auto-size equipment constraints using `autoSize()` and explicit equipment constraint limits
5. Set up and execute a production optimization using `ProductionOptimizer` with appropriate search algorithm selection for single-variable and multi-variable problems
6. Interpret `OptimizationResult` diagnostics including bottleneck identification, infeasibility diagnosis, and iteration history export
7. Define custom optimization objectives and constraints that combine throughput maximization with energy minimization or emissions targets
8. Integrate compressor performance curves with the optimizer via `CompressorChartGenerator` to enforce surge margin and operating envelope constraints

---

## 23.1 Introduction

Every process simulator can solve a fixed problem: given a feed composition, flow rate, and equipment configuration, calculate the outlet conditions. But production optimization asks a fundamentally different question — *what is the best operating point?* Answering this requires varying decision variables (flow rates, pressures, temperatures), re-solving the simulation at each trial point, and checking whether all equipment constraints are satisfied.

General-purpose optimization libraries (SciPy, MATLAB, GAMS) can perform the search, but they know nothing about separators, compressors, or surge margins. Conversely, a process simulator knows its equipment intimately but has no built-in optimizer. The gap between the two is bridged by an **optimization framework** — a software layer that:

1. Exposes simulation variables through a stable, machine-readable API
2. Captures equipment capacity limits as formal constraints
3. Orchestrates search algorithms that call the simulator as a black-box evaluator

NeqSim addresses this with three interlocking subsystems, illustrated in Figure 23.1:

![The three-layer architecture of the NeqSim optimization framework. The ProcessSystem provides the simulation engine, CapacityConstrainedEquipment provides the constraint engine, and ProductionOptimizer provides the search algorithms.](figures/fig25_1_architecture.png)

- **Simulation engine** — the `ProcessSystem` (and `ProcessModel` for multi-area plants) that solves mass, energy, and momentum balances across all equipment units
- **Constraint engine** — the `CapacityConstrainedEquipment` interface that endows every equipment unit with knowledge of its own operating limits
- **Optimizer** — the `ProductionOptimizer` and `ProcessOptimizationEngine` classes that explore the decision-variable space, query the simulator, and respect all constraints

This chapter explains how each layer works and how they combine into a coherent optimization framework. Earlier chapters have introduced optimization theory (Chapter 22) and production optimization workflows (Chapter 24). Here, we focus on the software architecture — the classes, interfaces, and APIs that make it all work — so that the reader can extend the framework for site-specific problems.

### 23.1.1 Design Philosophy

The framework follows several deliberate design principles:

**Backward compatibility.** Capacity constraints are disabled by default. A legacy `ProcessSystem` that has never heard of constraints runs exactly as before. Constraints become active only when explicitly enabled through `autoSize()`, `enableAllConstraints()`, or explicit constraint configuration. This allows existing models to be upgraded incrementally.

**Separation of concerns.** Equipment calculates its own utilization — the separator knows its K-factor, the compressor knows its surge margin — but the equipment does not decide what to do about it. The optimizer reads constraint status from all equipment, computes a composite feasibility score, and adjusts decision variables accordingly. This separation means new equipment types automatically participate in optimization simply by implementing the `CapacityConstrainedEquipment` interface.

**String-addressable automation.** The `ProcessAutomation` API exposes equipment and connected-stream properties through short addresses, such as `HP Sep.gasOutStream.density`. Discover the address, access type and unit before each update. This supports Python clients, structured configuration and agent-generated studies without requiring knowledge of internal object chains.

---

## 23.2 The ProcessSystem as an Optimization Model

At the heart of every NeqSim optimization lies a `ProcessSystem` — a directed graph of equipment units connected by streams. Understanding how this graph is structured is essential for understanding how the optimizer propagates changes and evaluates constraints.

### 23.2.1 Topology and Equipment Registration

A `ProcessSystem` maintains an ordered list of equipment units. Each unit is added with `process.add(unit)`, and the system enforces unique names:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
Compressor = jneqsim.process.equipment.compressor.Compressor
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# Create fluid
fluid = SystemSrkEos(273.15 + 25.0, 60.0)
fluid.addComponent("methane", 0.85)
fluid.addComponent("ethane", 0.10)
fluid.addComponent("propane", 0.05)
fluid.setMixingRule("classic")

# Build process
feed = Stream("feed", fluid)
feed.setFlowRate(100000.0, "kg/hr")
separator = Separator("HP separator", feed)
compressor = Compressor("export compressor", separator.getGasOutStream())
compressor.setOutletPressure(150.0, "bara")
compressor.setUsePolytropicCalc(True)
compressor.setPolytropicEfficiency(0.78)
export = Stream("export", compressor.getOutletStream())

process = ProcessSystem()
process.add(feed)
process.add(separator)
process.add(compressor)
process.add(export)
process.run()
```

When `process.run()` is called, the system executes each unit in registration order, propagating outlet conditions from one unit to the inlet of the next. This sequential execution model is the foundation for optimization: the optimizer changes a decision variable (e.g., feed flow rate), calls `process.run()`, and reads the resulting equipment states.

### 23.2.2 Stream Introspection

Every `ProcessEquipmentInterface` exposes its connected streams through two methods:

```python
inlets = separator.getInletStreams()    # returns List<StreamInterface>
outlets = separator.getOutletStreams()  # returns List<StreamInterface>
```

This allows the optimizer — or any analysis tool — to walk the process graph programmatically. For example, tracing from the bottleneck equipment backward through inlet streams identifies the upstream path that controls the bottleneck.

### 23.2.3 Multi-Area Plants with ProcessModel

Large production facilities (platforms, onshore plants) are typically divided into process areas: inlet separation, compression, dehydration, export. In NeqSim, each area is modeled as a separate `ProcessSystem`, and the areas are combined into a `ProcessModel`:

```python
ProcessModel = jneqsim.process.processmodel.ProcessModel
# Reuse the solved equipment in explicitly named areas for this example.
separation_system = ProcessSystem()
separation_system.add(feed)
separation_system.add(separator)
compression_system = ProcessSystem()
compression_system.add(compressor)
export_system = ProcessSystem()
export_system.add(export)
plant = ProcessModel()
plant.add("Separation", separation_system)
plant.add("Compression", compression_system)
plant.add("Export", export_system)
plant.run()
```

The `ProcessModel.run()` method iterates over all areas until the cross-boundary streams converge. This iterative convergence is essential for processes with recycles that span area boundaries (e.g., compressor anti-surge recycle back to the inlet separator).

For optimization, the multi-area structure has an important consequence: **constraint propagation is global**. The bottleneck may be in the compression area, but the remedy may be to reduce the feed rate in the separation area. The optimizer must see all equipment across all areas simultaneously, which is why the `ProcessAutomation` API supports area-qualified addresses (Section 23.3).

### 23.2.4 Why Topology Matters for Optimization

The process topology determines the **coupling structure** of the optimization problem. In a linear topology (feed → separator → compressor → cooler → export), changing the feed rate affects all downstream equipment monotonically. The optimizer can use efficient single-variable search methods such as binary search or golden-section search.

In a topology with recycles, the response to a change in one variable may be non-monotonic — increasing feed rate may initially improve throughput but eventually cause the recycle to diverge, producing a discontinuous objective function. Anti-surge recycle on a compressor is a common example: as the compressor approaches surge, the anti-surge controller opens the recycle valve, which increases the compressor inlet flow and may push the upstream separator toward its liquid-handling limit. The optimizer must handle this coupling robustness challenge, which is why `ProductionOptimizer` provides multiple search algorithms (Section 23.5).

A practical consequence is that the engineer should consider the process topology when selecting a search algorithm. Linear topologies favor `BINARY_FEASIBILITY` or `GOLDEN_SECTION_SCORE` for speed. Topologies with recycles or parallel trains often require `NELDER_MEAD_SCORE` or `PARTICLE_SWARM_SCORE` for robustness. Table 23.2 in Section 23.5 provides detailed guidance.

---

## 23.3 The ProcessAutomation API

The `ProcessAutomation` class is the bridge between the optimizer and the simulation. Rather than requiring programmatic navigation of Java objects, it provides a flat, string-addressable interface for reading and writing simulation variables.

### 23.3.1 Core Operations

The API is obtained from a `ProcessSystem` or `ProcessModel`:

```python
ProcessAutomation = jneqsim.process.automation.ProcessAutomation

# For a single ProcessSystem
auto = ProcessAutomation(process)

# For a multi-area ProcessModel
auto = ProcessAutomation(plant)
```

The four core operations are:

| Method | Purpose | Returns |
|--------|---------|---------|
| `getUnitList()` | List all equipment names | `List<String>` |
| `getVariableList(unitName)` | List all variables for one unit | `List<SimulationVariable>` |
| `getVariableValue(address, unit)` | Read a variable value | `double` |
| `setVariableValue(address, value, unit)` | Write an INPUT variable | `void` |

### 23.3.2 SimulationVariable: INPUT vs OUTPUT

Each variable returned by `getVariableList()` is a `SimulationVariable` object that describes:

- **Name** — the variable name (e.g., `"temperature"`, `"outletPressure"`)
- **Address** — the dot-notation path (e.g., `"HP separator.gasOutStream.temperature"`)
- **Type** — `INPUT` (writable) or `OUTPUT` (read-only)
- **Default unit** — the SI unit for the variable
- **Description** — a human-readable description

The distinction between INPUT and OUTPUT is fundamental. An INPUT variable can be set by the optimizer (e.g., compressor outlet pressure, valve opening). An OUTPUT variable is computed by the simulation (e.g., gas outlet temperature, power consumption). The optimizer reads OUTPUT variables to evaluate objectives and constraints, and writes INPUT variables as decision variables.

### 23.3.3 Address Format and Examples

Addresses use dot notation with the pattern `unitName.property` or `unitName.streamPort.property`:

```python
# Equipment-level properties
auto.getVariableValue("export compressor.outletPressure", "bara")
auto.getVariableValue("export compressor.power", "kW")

# Stream-port properties
auto.getVariableValue("HP separator.gasOutStream.temperature", "C")
auto.getVariableValue("HP separator.gasOutStream.flowRate", "kg/hr")
auto.getVariableValue("HP separator.liquidOutStream.density", "kg/m3")
```

### 23.3.4 Area-Qualified Addresses

For `ProcessModel` (multi-area), addresses include the area name separated by `::`:

```python
# Get area list
areas = auto.getAreaList()  # ["Separation", "Compression", "Export"]

# Area-qualified read
temp = auto.getVariableValue("Separation::HP separator.gasOutStream.temperature", "C")

# Area-qualified write
auto.setVariableValue("Compression::export compressor.outletPressure", 150.0, "bara")
```

This naming convention ensures that equipment with the same name in different areas can be addressed unambiguously.

### 23.3.5 Self-Healing Automation

When an address is misspelled or slightly wrong, the standard `getVariableValue` throws an exception. The **self-healing** variant provides fuzzy matching, auto-correction, and diagnostic information — essential for robust optimization loops and AI-driven workflows:

```python
# Safe get — returns JSON with value on success, diagnostics on failure
result_json = auto.getVariableValueSafe("hp separator.temperature", "C")
# Returns: {"status":"auto_corrected",
#           "originalAddress":"hp separator.temperature",
#           "correctedAddress":"HP separator.temperature",
#           "value":25.0, "unit":"C"}

# Safe set — validates physical bounds before applying
set_json = auto.setVariableValueSafe("export compressor.outletPressure", 150.0, "bara")
```

The `AutomationDiagnostics` subsystem tracks all operations and learns from past corrections:

```python
diag = auto.getDiagnostics()
report = diag.getLearningReport()  # operation stats, error patterns, corrections
```

Key capabilities of the self-healing system include:

- **Fuzzy name matching** — finds the closest unit or property name when the exact match fails (edit distance ≤ 2)
- **Auto-correction caching** — remembers corrections so that the same misspelling is fixed instantly on subsequent calls
- **Physical bounds validation** — rejects obviously wrong values (e.g., negative absolute pressure, temperature below absolute zero) before they corrupt the simulation
- **Operation tracking** — maintains success/failure statistics for troubleshooting

### 23.3.6 Discovery Workflow

A typical discovery workflow for setting up an optimization proceeds as follows:

```python
# Step 1: List all equipment
for unit_name in auto.getUnitList():
    eq_type = auto.getEquipmentType(unit_name)
    print(f"{unit_name} ({eq_type})")

# Step 2: List variables for the equipment of interest
for var in auto.getVariableList("export compressor"):
    print(f"  {var.getAddress()}  [{var.getType()}]  ({var.getDefaultUnit()})")

# Step 3: Read current values
pressure = auto.getVariableValue("export compressor.outletPressure", "bara")
power = auto.getVariableValue("export compressor.power", "kW")
print(f"Outlet pressure: {pressure:.1f} bara, Power: {power:.0f} kW")
```

This discovery process is how the optimizer identifies which variables are manipulable (INPUT type) and which are observable (OUTPUT type), forming the decision variables and objective/constraint evaluators for the optimization problem.

### 23.3.7 The evaluate() Optimization Primitive

The plain `process.run()` method returns `void`, so an agent or optimizer that calls it must separately inspect the run status, the convergence report, and every equipment constraint to decide whether a trial point is usable. `ProcessAutomation` collapses that bookkeeping into a single primitive, `evaluate()`, that applies a batch of setpoints, runs the model to convergence, gates feasibility, and reads back the requested objectives — returning **one schema-versioned JSON object that never throws**:

```python
import json
auto = ProcessAutomation(plant)
# Explicit Java collections avoid ambiguous JPype overload resolution.
setpoints = jpype.java.util.LinkedHashMap()
setpoints.put("Compression::export compressor.outletPressure", 150.0)
readbacks = jpype.java.util.ArrayList()
readbacks.add("Compression::export compressor.power")
evaluation = json.loads(str(auto.evaluate(
    setpoints, "bara", readbacks, "kW", 30, 5.0e-3)))
print(json.dumps(evaluation, indent=2))
```

Gate every optimizer trial on the single `feasible` flag — it is `true` only when the run did not throw, the model converged, no unit failed, and **every** setpoint was accepted. A bad address or an out-of-bounds value lands in `setpointsRejected` (good setpoints are still applied) and a bad read-back lands in `readbackErrors`, both without throwing, so a single malformed candidate degrades one trial instead of crashing the loop. The companion method `getAdjustableParameters()` enumerates the bounded decision space (each adjustable variable with its lower and upper limits) that the agent may perturb, and `getUtilizationSnapshotJson()` (Section 23.11.2) provides the matching capacity observation. Together, `getAdjustableParameters()` → `evaluate()` → `getUtilizationSnapshotJson()` form the action–reward–observation triple that the `AgenticProcessOptimizer` (Section 23.10) automates.

---

## 23.4 The CapacityConstrainedEquipment Interface

The `CapacityConstrainedEquipment` interface is the contract that allows any equipment to participate in constraint-based optimization. It answers a simple but critical question: *how close is this equipment to its operating limits?*

### 23.4.1 Interface Design

Every equipment class that implements `CapacityConstrainedEquipment` provides:

```text
getCapacityConstraints()       → Map<String, CapacityConstraint>
getBottleneckConstraint()      → CapacityConstraint
getMaxUtilization()            → double  (0.0 = idle, 1.0 = at design)
isCapacityExceeded()           → boolean
isHardLimitExceeded()          → boolean
getAvailableMargin()           → double  (headroom before bottleneck)
addCapacityConstraint(c)       → void
removeCapacityConstraint(name) → boolean
disableAllConstraints()        → int
enableAllConstraints()         → int
```

The interface returns a map of named constraints, each a `CapacityConstraint` object that tracks a specific limit. The bottleneck constraint is the one with the highest utilization.

### 23.4.2 Constraint Types

Each `CapacityConstraint` has a `ConstraintType` that determines its severity:

| Type | Meaning | Example | Behavior when exceeded |
|------|---------|---------|----------------------|
| **HARD** | Absolute physical or mechanical limit that cannot be exceeded | Compressor maximum speed, valve fully open, separator MAWP | Equipment trip or failure; optimizer treats as infeasible |
| **SOFT** | Design-basis limit that may be temporarily exceeded with degraded performance | Design flow rate, recommended retention time | Optimizer penalizes but may accept; efficiency reduced |
| **DESIGN** | Informational design-basis value | Nameplate capacity, design duty | No enforcement; used for reporting and trending |

The three-tier classification allows the optimizer to distinguish between hard physical limits (which render a solution infeasible) and soft economic/performance limits (which degrade the objective function score).

### 23.4.3 The CapacityConstraint Object

A `CapacityConstraint` encapsulates:

- **Name** — e.g., `"gasLoadFactor"`, `"speed"`, `"valveOpening"`
- **Unit** — the engineering unit (m/s, RPM, %)
- **Design value** — the nominal design-basis limit
- **Maximum value** — the absolute maximum (for HARD constraints)
- **Warning threshold** — fraction of design value at which a warning fires (typically 0.9)
- **Current value** — dynamically computed from simulation state via a supplier function
- **Utilization** — the ratio $U = v_\text{current} / v_\text{design}$
- **Shadow price** — the marginal economic value of relaxing the constraint by one unit, set with `setShadowPrice(double)` and read with `getShadowPrice()`. The shadow price is zero by default and is populated by economic tools such as the `DebottleneckingAdvisor` (Chapter 21) so that binding constraints can be ranked by the value of the production they unlock.

The utilization is defined as:

$$
U = \frac{v_\text{current}}{v_\text{design}}
$$

where $v_\text{current}$ is the current operating value and $v_\text{design}$ is the design-basis value. A utilization of 1.0 means the equipment is operating exactly at its design limit. Values above 1.0 indicate the equipment is operating beyond its design capacity.

### 23.4.4 The autoSize() Method

The `autoSize()` method is a convenience function that creates appropriate capacity constraints based on the current operating conditions and a safety factor:

```python
# A synthetic sizing demonstration for the equipment built above.
separator.autoSize(1.2)
compressor.autoSize(1.2)
# Fixed-pressure power screening; synthetic auto-size maps are not installed data.
compressor.getCompressorChart().setUseCompressorChart(False)
compressor.setSolveSpeed(False)
compressor.setUsePolytropicCalc(True)
for entry in compressor.getCapacityConstraints().entrySet():
    entry.getValue().setEnabled(str(entry.getKey()) == "power")

# Preserve the resulting ratings, but use fixed outlet pressure in later searches.
compressor.getCompressorChart().setUseCompressorChart(False)
print("Separator constraints:", list(separator.getCapacityConstraints().keySet()))
print("Compressor constraints:", list(compressor.getCapacityConstraints().keySet()))
```

The safety factor (1.2 in this example) sets the design value at the specified multiple of the current operating value. This means the equipment is sized so that its current operating point is at $1/1.2 = 83\%$ utilization, leaving 17% headroom.

Calling `autoSize()` without arguments uses a default safety factor of 1.0 (design = current), which is useful for modeling existing equipment with known nameplate capacity.

### 23.4.5 Constraint Presets

For standardized constraint values, the framework provides company-specific and standards-based presets:

```python
# Presets are equipment-specific; discover the available constraint names.
separator.useEquinorConstraints()
print(list(separator.getCapacityConstraints().keySet()))
# Installed, approved ratings must replace synthetic presets in plant studies.
```

These presets load constraint parameters from reference data (design codes, company technical requirements) rather than computing them from current conditions. This is appropriate when modeling existing facilities where the design-basis constraints are known from the original equipment datasheets.

The preset mechanism reads from CSV design data files (`TechnicalRequirements_Process.csv`) stored in the NeqSim resources directory. Engineers can extend these files with additional company standards or equipment-specific overrides. This data-driven approach means that constraint values can be updated without modifying Java code — a significant advantage for multi-asset operations where different facilities may follow different design standards.

### 23.4.6 Equipment-Specific Constraints

Table 23.1 summarizes the constraints defined by each equipment type.

**Table 23.1.** Capacity constraints by equipment type.

| Equipment | Constraint | Type | Unit | Physical Basis |
|-----------|-----------|------|------|----------------|
| **Separator** | Gas load factor (K-factor) | SOFT | m/s | Souders-Brown liquid entrainment limit |
| | Liquid retention time | SOFT | s | Required settling/coalescence time |
| | Liquid level | HARD | % | Overflow or carryover at high/low level |
| | Gas velocity | HARD | m/s | Erosion or re-entrainment limit |
| **Compressor** | Speed | HARD | RPM | Mechanical limit of shaft/bearings |
| | Power | HARD | kW | Driver power rating |
| | Surge margin | HARD | % | Minimum flow before surge instability |
| | Discharge temperature | SOFT | °C | Material and seal temperature limits |
| | Polytropic efficiency | DESIGN | — | Design-basis efficiency |
| **Valve** | Valve opening | HARD | % | Fully open (100%) = maximum capacity |
| | $C_v$ utilization | SOFT | — | Rangeability limit |
| | Choked flow | HARD | — | Sonic velocity at vena contracta |
| **Pipeline** | Erosional velocity | HARD | m/s | API RP 14E erosional velocity limit |
| | Pressure drop | SOFT | bar/km | Delivery pressure constraint |
| | Flow-induced vibration | SOFT | m/s | Vibration onset velocity |
| **Heat Exchanger** | LMTD approach | SOFT | °C | Minimum approach temperature |
| | Fouling factor | SOFT | m²K/W | Excess fouling reduces capacity |
| | Tube velocity | HARD | m/s | Erosion and vibration limit |
| | Pressure drop | SOFT | bar | Allowable shell/tube pressure drop |

### 23.4.7 Enabling and Disabling Constraints

By default, constraints are **disabled** for backward compatibility. They can be controlled at multiple levels:

```python
separator.enableAllConstraints()
separator.disableAllConstraints()
separator.setCapacityAnalysisEnabled(False)
constraints = separator.getCapacityConstraints()
constraints["gasLoadFactor"].setEnabled(True)
# Restore declared scope after demonstrating disablement.
separator.setCapacityAnalysisEnabled(True)
separator.enableAllConstraints()
```

This granularity allows engineers to enable only the constraints relevant to a specific analysis. For example, a gas capacity study might enable only gas-handling constraints while disabling liquid-side constraints.

---

## 23.5 The ProductionOptimizer

The `ProductionOptimizer` is the central class that orchestrates production optimization. It takes a `ProcessSystem`, a set of decision variables, objectives, and constraints, and returns an `OptimizationResult` with the optimal operating point.

### 23.5.1 OptimizationConfig Builder

The optimization is configured through a builder-pattern `OptimizationConfig`:

```python
ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer
OptimizationConfig = ProductionOptimizer.OptimizationConfig
SearchMode = ProductionOptimizer.SearchMode

# Configure the optimization
config = (OptimizationConfig(50000.0, 200000.0)   # min and max rate (kg/hr)
    .tolerance(100.0)                               # convergence tolerance
    .searchMode(SearchMode.BINARY_FEASIBILITY)     # search algorithm
    .maxIterations(30)                               # iteration limit
    .rateUnit("kg/hr"))                              # unit for rate bounds
```

The constructor takes the lower and upper bounds for the primary decision variable (typically feed flow rate). The builder methods add optional configuration:

| Method | Purpose | Default |
|--------|---------|---------|
| `tolerance(value)` | Convergence criterion — stop when interval < tolerance | 1.0 |
| `searchMode(mode)` | Search algorithm selection | `BINARY_FEASIBILITY` |
| `maxIterations(n)` | Maximum optimizer iterations | 50 |
| `rateUnit(unit)` | Engineering unit for rate bounds | `"kg/hr"` |
| `defaultUtilizationLimit(limit)` | Equipment utilization limit (0–1) | 0.95 |

### 23.5.2 Search Algorithms

The optimizer provides five search algorithms, each suited to different problem characteristics:

**BINARY_FEASIBILITY.** The simplest and fastest algorithm. It performs binary search on the decision variable, checking whether each trial point is feasible (all equipment within limits). Assumes that feasibility is monotonically decreasing with increasing rate — i.e., higher rates are always harder to achieve. Converges in $O(\log_2(n))$ iterations where $n = (x_\text{max} - x_\text{min})/\text{tolerance}$. Best for straightforward throughput maximization on linear topologies.

**GOLDEN_SECTION_SCORE.** Applies golden-section search to a composite score that combines throughput, constraint satisfaction, and penalty terms. Unlike binary search, it can handle non-monotonic responses where the best operating point is not at the feasibility boundary. Requires the objective to be **unimodal** (single peak). Converges in $O(\log_\varphi(n))$ iterations where $\varphi = 1.618$ is the golden ratio.

The golden-section method brackets the optimum by evaluating two interior points per iteration at positions:

$$
x_1 = a + (1 - \varphi^{-1})(b - a), \quad x_2 = a + \varphi^{-1}(b - a)
$$

where $[a, b]$ is the current interval and $\varphi = (1 + \sqrt{5})/2$ is the golden ratio. The interval shrinks by factor $\varphi^{-1} \approx 0.618$ each iteration.

**NELDER_MEAD_SCORE.** The Nelder-Mead simplex algorithm operates in the space of all decision variables simultaneously. It maintains a simplex (triangle in 2D, tetrahedron in 3D) and applies reflection, expansion, contraction, and shrinkage operations to navigate toward the optimum. No gradient computation is required, making it robust for noisy or discontinuous objectives. Effective for 2–10 decision variables.

**PARTICLE_SWARM_SCORE.** A population-based metaheuristic that maintains a swarm of candidate solutions. Each particle adjusts its position based on its own best-known position and the swarm's best-known position. Well-suited for non-convex problems with multiple local optima. More computationally expensive (each iteration evaluates the entire swarm) but provides global search capability.

**GRADIENT_DESCENT_SCORE.** Steepest ascent with finite-difference gradients and Armijo backtracking line search. Computes the gradient using central differences:

$$
\frac{\partial f}{\partial x_i} \approx \frac{f(x + h \, e_i) - f(x - h \, e_i)}{2h}
$$

where $h$ is a perturbation step and $e_i$ is the $i$-th unit vector. The Armijo condition ensures sufficient decrease in the step size. Suitable for smooth, well-behaved problems with 5–20+ decision variables where gradient information significantly accelerates convergence.

Table 23.2 provides guidance for algorithm selection.

**Table 23.2.** Search algorithm selection guide.

| Algorithm | Variables | Global? | Gradient-free? | Best for |
|-----------|----------|---------|----------------|----------|
| `BINARY_FEASIBILITY` | 1 | No | Yes | Simple throughput maximization |
| `GOLDEN_SECTION_SCORE` | 1 | No | Yes | Non-monotonic single-variable |
| `NELDER_MEAD_SCORE` | 2–10 | No | Yes | Multi-variable, noisy objectives |
| `PARTICLE_SWARM_SCORE` | 1–20 | Yes | Yes | Multi-modal, non-convex |
| `GRADIENT_DESCENT_SCORE` | 5–20+ | No | No | Smooth, high-dimensional |

### 23.5.3 Running an Optimization

The complete workflow for a single-variable throughput maximization:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer
OptimizationConfig = ProductionOptimizer.OptimizationConfig
SearchMode = ProductionOptimizer.SearchMode

# Assume 'process' and 'feed' are already built and run
optimizer = ProductionOptimizer()

# Configure: search between 50,000 and 200,000 kg/hr
config = (OptimizationConfig(50000.0, 200000.0)
    .tolerance(100.0)
    .searchMode(SearchMode.BINARY_FEASIBILITY)
    .maxIterations(30)
    .rateUnit("kg/hr"))

# Run the optimization
result = optimizer.optimize(process, feed, config, None, None)

# Read results
print(f"Optimal rate:  {result.getOptimalRate():.0f} {result.getRateUnit()}")
print(f"Feasible:      {result.isFeasible()}")
print(f"Bottleneck:    {(result.getBottleneck().getName() if result.getBottleneck() else "none")}")
print(f"Utilization:   {result.getBottleneckUtilization() * 100:.1f}%")
print(f"Iterations:    {result.getIterations()}")
```

The `optimize()` method signature is:

```text
optimize(process, feedStream, config, objectives, constraints)
```

where `objectives` and `constraints` are optional lists of `OptimizationObjective` and `OptimizationConstraint` objects (Section 23.7). When both are `None`, the optimizer defaults to maximizing the feed flow rate subject to all equipment capacity constraints.

### 23.5.4 Multi-Variable Optimization

For problems with multiple decision variables (e.g., simultaneous optimization of flow rate and compressor outlet pressure), the optimizer uses `ManipulatedVariable` objects:

```python
ManipulatedVariable = ProductionOptimizer.ManipulatedVariable

# Define decision variables
variables = jpype.java.util.ArrayList([
    ManipulatedVariable("flowRate", 50000, 200000, "kg/hr",
        lambda proc, val: proc.getUnit("feed").setFlowRate(val, "kg/hr")),
    ManipulatedVariable("pressure", 100, 200, "bara",
        lambda proc, val: proc.getUnit("export compressor").setOutletPressure(val))
])

config = (OptimizationConfig(0, 1)  # bounds are per-variable for multi-var
    .searchMode(SearchMode.NELDER_MEAD_SCORE)
    .maxIterations(100))

OptimizationObjective = ProductionOptimizer.OptimizationObjective
ObjectiveType = ProductionOptimizer.ObjectiveType
objectives = jpype.java.util.ArrayList()
objectives.add(OptimizationObjective("throughput",
    lambda proc: proc.getUnit("feed").getFlowRate("kg/hr"),
    1.0, ObjectiveType.MAXIMIZE))
result = optimizer.optimize(process, variables, config, objectives, None)
decision_vars = result.getDecisionVariables()
for name, value in decision_vars.items():
    print(f"  {name} = {value:.1f}")
```

### 23.5.5 Warm Start and Caching

The optimizer includes several performance features that are critical for production-grade applications:

**Warm start.** When optimizing repeatedly (e.g., for different scenarios or time steps in a production profile), the optimizer can use the result of the previous optimization as the starting point for the next one. This dramatically reduces the number of iterations needed for convergence when successive problems are similar.

**LRU caching.** The most expensive operation in simulation-based optimization is the process simulation call (`process.run()`). The optimizer maintains a least-recently-used (LRU) cache of recently evaluated points. If the optimizer revisits a previously evaluated point (common in simplex-based methods), the cached result is returned without re-running the simulation.

**Parallel evaluation.** For population-based methods (particle swarm), multiple candidate points can be evaluated simultaneously. The optimizer uses a thread pool to evaluate independent process simulations in parallel, with each thread operating on a cloned copy of the `ProcessSystem`.

**Stagnation detection.** The optimizer monitors the improvement in objective value over successive iterations. If the improvement falls below a threshold for a configurable number of consecutive iterations, the optimizer terminates early, avoiding wasted computation on marginal improvements.

---

## 23.6 OptimizationResult and Diagnostics

The `OptimizationResult` object returned by the optimizer is a rich container of information about the solution, the search process, and the constraint status.

### 23.6.1 Core Result Fields

| Method | Returns | Description |
|--------|---------|-------------|
| `getOptimalRate()` | `double` | The optimal value of the primary decision variable |
| `getRateUnit()` | `String` | Engineering unit for the optimal rate |
| `isFeasible()` | `boolean` | Whether all constraints are satisfied |
| `getScore()` | `double` | Composite objective score at the optimum |
| `getIterations()` | `int` | Number of optimizer iterations used |
| `getBottleneck()` | `ProcessEquipmentInterface` | The binding equipment constraint |
| `getBottleneckUtilization()` | `double` | Utilization of the bottleneck (fraction) |

### 23.6.2 Utilization Records

The `getUtilizationRecords()` method returns a list of `UtilizationRecord` objects, one for each equipment item evaluated. Each record contains:

- **Equipment name** — the name of the equipment unit
- **Capacity duty** — the current operating duty
- **Capacity max** — the maximum rated capacity
- **Utilization** — the ratio of duty to max
- **Utilization limit** — the maximum allowable utilization (typically 0.95)

This provides a complete snapshot of the facility utilization at the optimal operating point, useful for capacity reports and visualization.

### 23.6.3 Infeasibility Diagnosis

When the optimizer returns an infeasible result (`isFeasible() == false`), the `getInfeasibilityDiagnosis()` method provides a structured explanation:

```python
if not result.isFeasible():
    diagnosis = result.getInfeasibilityDiagnosis()
    print(diagnosis)
```

The diagnosis identifies:
- **Utilization violations** — equipment items exceeding their utilization limit, with the amount over-limit
- **Hard constraint violations** — equipment constraints that are physically impossible to satisfy at the requested rate
- **Soft constraint violations** — constraints that are exceeded but not necessarily fatal

This diagnostic is invaluable for troubleshooting. Rather than simply reporting "infeasible," the optimizer tells the engineer *why* the requested throughput cannot be achieved and *which equipment* is the limiting factor.

### 23.6.4 Iteration History

The `getIterationHistory()` method returns a list of `IterationRecord` objects that trace the optimizer's search path. Each record includes the trial rate, bottleneck, utilization, feasibility status, and score at that iteration. This history can be exported for analysis:

```python
# Export as JSON for analysis
json_str = result.exportIterationHistoryAsJson()
with open("optimization_history.json", "w") as f:
    f.write(json_str)

# Export as CSV for spreadsheet analysis
csv_str = result.exportIterationHistoryAsCsv()
with open("optimization_history.csv", "w") as f:
    f.write(csv_str)
```

The iteration history is particularly useful for:
- **Debugging** — verifying that the optimizer is converging as expected
- **Visualization** — plotting the search trajectory on top of the feasibility landscape
- **Performance tuning** — identifying whether the convergence tolerance or maximum iterations should be adjusted

### 23.6.5 Objective Values

For multi-objective problems, `getObjectiveValues()` returns a map of objective names to their values at the optimum:

```python
obj_values = result.getObjectiveValues()
for name, value in obj_values.items():
    print(f"  {name}: {value:.2f}")
```

This allows the engineer to see the trade-off between competing objectives at the chosen operating point.

---

## 23.7 Custom Objectives and Constraints

The default behavior of `ProductionOptimizer` is to maximize feed throughput subject to equipment capacity constraints. But real production optimization problems often involve richer objectives — maximize revenue (not just volume), minimize energy consumption, limit emissions, or balance multiple competing goals.

### 23.7.1 The OptimizationObjective Interface

An `OptimizationObjective` defines a quantity to optimize:

```python
OptimizationObjective = ProductionOptimizer.OptimizationObjective
ObjectiveType = ProductionOptimizer.ObjectiveType

# Maximize throughput
throughput_obj = OptimizationObjective(
    "throughput",
    lambda proc: proc.getUnit("export").getFlowRate("kg/hr"),
    1.0,  # weight
    ObjectiveType.MAXIMIZE
)

# Minimize compressor power
power_obj = OptimizationObjective(
    "power",
    lambda proc: proc.getUnit("export compressor").getPower("kW"),
    0.3,  # weight (lower than throughput)
    ObjectiveType.MINIMIZE
)
```

Each objective has:
- **Name** — a unique identifier
- **Evaluator** — a function that takes a `ProcessSystem` and returns a `double`
- **Weight** — relative importance for composite scoring
- **Type** — `MAXIMIZE` or `MINIMIZE`

When multiple objectives are provided, the optimizer forms a **composite score** as a weighted sum. For minimization objectives, the sign is reversed so that maximizing the composite score simultaneously maximizes MAXIMIZE objectives and minimizes MINIMIZE objectives:

$$
S = \sum_{i \in \text{MAX}} w_i \cdot \hat{f}_i - \sum_{j \in \text{MIN}} w_j \cdot \hat{f}_j
$$

where $\hat{f}$ represents the normalized objective value and $w$ is the weight.

### 23.7.2 The OptimizationConstraint Interface

An `OptimizationConstraint` defines a limit on a process-level metric:

```python
OptimizationConstraint = ProductionOptimizer.OptimizationConstraint
ConstraintSeverity = ProductionOptimizer.ConstraintSeverity

# Maximum total compressor power
power_limit = OptimizationConstraint.lessThan(
    "total_power",
    lambda proc: proc.getUnit("export compressor").getPower("kW"),
    15000.0,  # kW limit
    ConstraintSeverity.HARD,
    100.0,    # penalty weight
    "Total compressor power must not exceed 15 MW"
)

# Minimum export pressure
pressure_floor = OptimizationConstraint.greaterThan(
    "export_pressure",
    lambda proc: proc.getUnit("export").getPressure("bara"),
    70.0,  # bara minimum
    ConstraintSeverity.HARD,
    50.0,
    "Export pressure must be at least 70 bara"
)
```

The `lessThan` and `greaterThan` factory methods provide a clean API for the two most common constraint patterns. Each constraint has a severity (`HARD` or `SOFT`) and a penalty weight that determines how severely violations are penalized in the composite score.

### 23.7.3 Example: Combined Throughput and Emissions Optimization

A practical example combines throughput maximization with a CO₂ emissions constraint:

```python
# Synthetic electrically driven export-gas case.
# Emissions intensity is an explicit scenario assumption, not a plant measurement.
gas_throughput = OptimizationObjective("gas_export",
    lambda proc: proc.getUnit("export").getFlowRate("kg/hr"),
    1.0, ObjectiveType.MAXIMIZE)
def calculate_emissions(proc):
    power_kW = proc.getUnit("export compressor").getPower("kW")
    return power_kW * 8760.0 * 0.10 / 1000.0  # t CO2/year, 0.10 kg/kWh
co2_limit = OptimizationConstraint.lessThan("co2_emissions",
    calculate_emissions, 50000.0, ConstraintSeverity.HARD, 200.0,
    "Illustrative annual electricity-related CO2 budget")
objectives = jpype.java.util.ArrayList([gas_throughput])
extra_constraints = jpype.java.util.ArrayList([co2_limit])
config = (OptimizationConfig(50000.0, 200000.0)
          .rateUnit("kg/hr").maxIterations(30)
          .searchMode(SearchMode.GOLDEN_SECTION_SCORE))
result = optimizer.optimize(process, feed, config, objectives, extra_constraints)
print(result.isFeasible(), result.getOptimalRate(), calculate_emissions(process))
```

This formulation finds the maximum oil throughput that stays within the emissions cap — a problem that is becoming increasingly relevant as carbon pricing and emission trading schemes affect production planning.

### 23.7.4 Multi-Objective Pareto Optimization

For problems where no single weighting of objectives is clearly superior, the optimizer supports Pareto front generation:

```python
objectives = jpype.java.util.ArrayList([gas_throughput, power_obj])
config.paretoGridSize(5)
pareto_result = optimizer.optimizePareto(process, feed, config,
    objectives, jpype.java.util.ArrayList([power_limit]))
for point in pareto_result.getParetoFront():
    values = point.getObjectiveValues()
    print("Gas (kg/hr):", values["gas_export"], "Power (kW):", values["power"])
```

The Pareto front reveals the trade-off between objectives, allowing the engineer to make an informed decision about where to operate. The optimizer also identifies the **knee point** — the Pareto-optimal solution with the best balance between objectives.

---

## 23.8 The ProcessOptimizationEngine (Level 2)

While `ProductionOptimizer` provides the core optimization algorithms, the `ProcessOptimizationEngine` adds a higher-level API that wraps common optimization workflows into single-method calls.

### 23.8.1 Purpose and Scope

The `ProcessOptimizationEngine` is designed for the engineer who wants to answer specific questions without assembling the full optimizer configuration:

- "What is the maximum throughput of this facility?"
- "What happens if I increase inlet pressure by 5 bar?"
- "Generate a lift curve for these operating conditions."

It combines the simulation engine, constraint evaluation, and optimization into unified methods:

```python
ProcessOptimizationEngine = jneqsim.process.util.optimizer.ProcessOptimizationEngine

engine = ProcessOptimizationEngine(process)
engine.setSearchAlgorithm(ProcessOptimizationEngine.SearchAlgorithm.GOLDEN_SECTION)
engine.setMaxIterations(50)
```

### 23.8.2 Key Methods

**findMaximumThroughput()** — Finds the maximum flow rate that satisfies all equipment constraints for given inlet and outlet boundary conditions:

```python
engine.setFeedStreamName("feed")
engine.setOutletStreamName("export")
inlet_pressure, outlet_pressure = 60.0, 150.0  # bara
min_flow, max_flow = 50000.0, 200000.0          # kg/hr
engine_result = engine.findMaximumThroughput(
    inlet_pressure, outlet_pressure, min_flow, max_flow)
print(f"Maximum throughput: {engine_result.getOptimalValue():.0f} kg/hr")
# Replay explicitly for this engine before reading equipment outputs.
feed.setFlowRate(engine_result.getOptimalValue(), "kg/hr")
process.run()
```

**evaluateAllConstraints()** — Returns a `ConstraintReport` summarizing every equipment constraint in the process, without optimization:

```python
report = engine.evaluateAllConstraints()
for item in report.getEquipmentStatuses():
    print(item.getEquipmentName(), item.getBottleneckConstraint(),
          item.getUtilization(), item.isWithinLimits())
```

**analyzeSensitivity()** — Perturbs each decision variable by a small amount and measures the change in the objective, producing a local sensitivity report:

```python
sensitivity = engine.analyzeSensitivity(
    engine_result.getOptimalValue(), inlet_pressure, outlet_pressure)
print(str(sensitivity))
```

**generateLiftCurve()** — Sweeps over arrays of pressures, temperatures, water cuts, and GORs to generate a multi-dimensional lift curve:

```python
pressures = jpype.JArray(jpype.JDouble)([50.0, 60.0, 70.0])  # bara
temperatures = jpype.JArray(jpype.JDouble)([298.15])  # K
# Fixed composition and mass-flow basis; this is not a well VFP table.
capacity_table = engine.generateCapacityScreening(
    pressures, temperatures, 150.0, 50000.0, 200000.0)
for point in capacity_table.getPoints():
    print(point.getInletPressure(), point.getTemperature(), point.getMaxFlowRate())
```

The lift curve is a tabulated response surface that maps operating conditions to maximum throughput — the same data used for production optimization in reservoir simulation models.

### 23.8.3 Equipment Capacity Strategies

Internally, the `ProcessOptimizationEngine` uses an `EquipmentCapacityStrategyRegistry` with 18 built-in strategies that know how to evaluate capacity for specific equipment types (separators, compressors, valves, heat exchangers, pipelines, etc.). When the engine evaluates constraints, it looks up the appropriate strategy for each equipment item and delegates the capacity calculation.

This strategy pattern makes the engine extensible: new equipment types can participate in optimization by registering a custom capacity strategy.

---

## 23.9 Integration with CompressorChartGenerator

Compressors are often the most critical constraint in gas processing and export systems. The `CompressorChartGenerator` creates performance curves that integrate directly with the optimization framework.

### 23.9.1 Generating Performance Curves

After running a process simulation with a compressor, the chart generator creates curves based on the compressor's operating point:

```python
CompressorChartGenerator = jneqsim.process.equipment.compressor.CompressorChartGenerator

generator = CompressorChartGenerator(compressor)
generator.setChartType("interpolate and extrapolate")

# Generate multi-speed curves
chart = generator.generateCompressorChart("normal", 5)  # 5 speed lines
compressor.setCompressorChart(chart)
```

The generated chart provides:
- **Head vs. flow** curves at multiple speeds
- **Efficiency vs. flow** curves at multiple speeds
- **Surge line** — the minimum flow at each speed below which surge instability occurs
- **Stonewall line** — the maximum flow at each speed where choked flow occurs

### 23.9.2 Surge Margin as a Constraint

When a compressor has a performance chart, the `autoSize()` method automatically creates a **surge margin constraint**:

```python
compressor.autoSize(1.2)
# Fixed-pressure power screening; synthetic auto-size maps are not installed data.
compressor.getCompressorChart().setUseCompressorChart(False)
compressor.setSolveSpeed(False)
compressor.setUsePolytropicCalc(True)
for entry in compressor.getCapacityConstraints().entrySet():
    entry.getValue().setEnabled(str(entry.getKey()) == "power")

constraints = compressor.getCapacityConstraints()
surge_constraint = constraints["surgeMargin"]
print(f"Surge margin: {surge_constraint.getCurrentValue():.1f}%")
```

The surge margin is defined as:

$$
M_\text{surge} = \frac{Q_\text{actual} - Q_\text{surge}}{Q_\text{surge}} \times 100\%
$$

where $Q_\text{actual}$ is the current flow rate and $Q_\text{surge}$ is the surge flow at the current speed. A negative surge margin means the compressor is operating in surge — a HARD constraint violation.

During optimization, as the optimizer increases the feed flow rate, the compressor flow rate increases and the surge margin improves. However, other constraints (power, discharge temperature) may tighten. The optimizer balances all constraints simultaneously to find the optimal operating point.

### 23.9.3 Operating Point Tracking

The compressor chart allows the optimizer to track the operating point on the performance map throughout the optimization:

```python
# After optimization, check compressor operating point
head = compressor.getPolytropicFluidHead()
flow = compressor.getInletStream().getFlowRate("Am3/hr")
efficiency = compressor.getPolytropicEfficiency()
speed = compressor.getSpeed()

print(f"Operating point: Q={flow:.0f} Am3/hr, H={head:.1f} kJ/kg")
print(f"Speed: {speed:.0f} RPM, Efficiency: {efficiency:.1%}")
```

This integration means the optimization respects not just the compressor's rated limits but its actual performance characteristics at any operating point — a level of fidelity that is essential for accurate production optimization in gas-dominated systems.

### 23.9.4 Curve Templates

For early-phase studies where detailed vendor data is not available, the generator provides predefined curve templates:

```python
# Use a standard centrifugal compressor template
chart = generator.generateFromTemplate("CENTRIFUGAL_STANDARD", 9)  # 9 speed lines
```

Available templates include `CENTRIFUGAL_STANDARD`, `CENTRIFUGAL_HIGH_FLOW`, and `CENTRIFUGAL_HIGH_HEAD`, each representing typical performance characteristics for different compressor designs. The templates are based on published correlations for centrifugal compressor performance and can serve as reasonable approximations for concept-level studies.

Advanced options on the chart generator include Reynolds number correction for off-design efficiency, Mach number limitation for stonewall flow, and multistage surge correction for multi-section compressors:

```python
generator.setUseReynoldsCorrection(True)
generator.setUseMachCorrection(True)
generator.setUseMultistageSurgeCorrection(True)
generator.setNumberOfStages(3)
generator.setImpellerDiameter(0.35)  # meters
```

These corrections improve the fidelity of the performance map at operating points far from the design condition, which is precisely where the optimizer explores during throughput maximization.

---

## 23.10 The AgenticProcessOptimizer

The classic `ProductionOptimizer` (Section 23.5) and the external-solver bridges expect the engineer to assemble a configuration object, supply evaluator functions, and interpret a Java result. The `AgenticProcessOptimizer` (package `neqsim.process.automation`) is a higher-level, **closed-loop optimizer purpose-built for machine-learning and autonomous-agent workflows**. It works entirely in terms of string addresses, a never-throwing schema-versioned JSON contract, and a replayable optimization trajectory, so an agent can build and solve an optimization problem directly from the output of `getAdjustableParameters()`.

### 23.10.1 Obtaining and Configuring the Optimizer

The optimizer is created from the automation facade and configured with a fluent API:

```python
auto = ProcessAutomation(plant)
opt = auto.newOptimizer()                      # returns an AgenticProcessOptimizer

# Decision space (per-variable bounds and units)
opt.addVariable("Compression::export compressor.outletPressure", 80.0, 200.0, "bara")
# ... or auto-fill bounded variables from the process adjusters:
# n = opt.useAdjustableParameters()

# Objective (address-based)
opt.minimize("Compression::export compressor.power", "kW")

# Hard inequality constraint, folded in as a weighted quadratic penalty
opt.addConstraintLessOrEqual("Compression::export compressor.power", 15000.0, "kW", 1.0e4)

opt.setSeed(42).setMaxEvaluations(80)
```

The principal configuration methods are summarized in Table 23.3.

**Table 23.3.** `AgenticProcessOptimizer` configuration API.

| Method | Purpose |
|--------|---------|
| `addVariable(addr, lo, hi, unit)` | Add a bounded decision variable by address |
| `useAdjustableParameters()` | Auto-fill bounded variables from process adjusters; returns the count added |
| `minimize(addr, unit)` / `maximize(addr, unit)` | Set an address-based objective |
| `setObjective(addr, Sense, unit)` | Set objective with an explicit `Sense` (MINIMIZE/MAXIMIZE) |
| `addWatch(addr, unit)` | Track an observable that is not the objective |
| `addConstraintLessOrEqual(addr, limit, unit, penaltyWeight)` | $g(x) \le \text{limit}$ as a penalty |
| `addConstraintGreaterOrEqual(addr, limit, unit, penaltyWeight)` | $g(x) \ge \text{limit}$ as a penalty |
| `setMaxEvaluations(n)` | Evaluation budget |
| `setConvergenceTolerance(tol)` | Simplex stop tolerance |
| `setSeed(long)` | Seed for deterministic, reproducible runs |

### 23.10.2 The Search Algorithm

Internally, `AgenticProcessOptimizer` runs a **bounded Nelder\u2013Mead simplex** with deterministic, seeded random initialization. A flowsheet behind `evaluate()` is a noisy, feasibility-gated black box with no usable analytic gradient, so a derivative-free method is the appropriate choice. The same seed and the same problem produce an identical trajectory, which makes experiments reproducible. Hard constraints are folded into the objective as weighted quadratic penalties:

$$
\tilde{f}(x) = f(x) + \sum_k w_k \, \max\bigl(0,\; g_k(x) - L_k\bigr)^2
$$

where $f$ is the (sign-adjusted) objective, $g_k$ is the constraint read-back, $L_k$ its limit, and $w_k$ its penalty weight. Infeasible trials are still logged but pushed to the back of the ranking by their large penalty.

Each trial sets the decision variables, calls the `evaluate()` primitive (Section 23.3.7) for one gated run, then reads the objective and constraints individually. A malformed candidate degrades exactly one trial instead of crashing the loop, and `optimize()` itself never throws.

### 23.10.3 Running the Optimizer and Reading Results

```python
import json

result = opt.optimize()              # OptimizationResult, never throws
print("success:", result.isSuccess())
print("best objective:", result.getBestObjective())
print("best setpoints:", dict(result.getBestSetpoints()))

# Full schema-versioned JSON including the trajectory tape
report = json.loads(str(opt.optimizeToJson()))
```

Every evaluated point is logged as a `Trial` (setpoints, read-backs, raw objective, penalty, feasibility, and minimized score) accessible through `result.getTrajectory()` and embedded in the result JSON. This trajectory is the (state, action, reward) tape used for offline reinforcement learning, surrogate-model fitting, and agent post-mortems.

### 23.10.4 Machine-Readable Self-Rating

Before committing an evaluation budget, an agent can query the optimizer's own capability self-assessment:

```python
readiness = json.loads(str(opt.getReadinessJson()))
```

`getReadinessJson()` rates each capability `full`, `partial`, or `none`. The never-throwing JSON contract, deterministic seeding, bounded action space, reward shaping, constraint handling, trajectory logging, and feasibility gating are all rated `full`; gradient information is `none`; the global-optimum guarantee is `partial`; and parallel evaluation is `none`. This self-rating lets an autonomous planner decide whether `AgenticProcessOptimizer` is the right tool for a given problem or whether a global or gradient-based method should be used instead.

---

## 23.11 Multi-Area Optimization and the Utilization Snapshot

Production facilities are modeled as multi-area `ProcessModel` plants (Section 23.2.3). Two additions in this framework make a full plant directly optimizable.

### 23.11.1 ProcessModelOptimizationView

`ProcessModelOptimizationView` (package `neqsim.process.util.optimizer`) wraps a `ProcessModel` and exposes plant-wide constraint introspection through the same interface the optimizer uses for a single `ProcessSystem`:

```python
ProcessModelOptimizationView = jneqsim.process.util.optimizer.ProcessModelOptimizationView

view = ProcessModelOptimizationView(plant)            # or (plant, maxIterations, tolerance)
view.run(None)                                         # solve all areas to convergence

bottleneck = view.getBottleneck()                      # plant-wide limiting unit
print("Bottleneck:", (bottleneck.getName() if bottleneck else "none"),
      f"{view.getBottleneckUtilization() * 100:.1f}%")
print("Any overloaded:", view.isAnyEquipmentOverloaded())
print("Any hard limit exceeded:", view.isAnyHardLimitExceeded())

for eq in view.getConstrainedEquipment():
    print(eq.getName(), eq.getMaxUtilization())
```

The view aggregates `getUnitOperations()` and `getConstrainedEquipment()` across all areas, so the plant-wide bottleneck \u2014 which may be in the compression area while the remedy is in separation \u2014 is identified in a single call via `findBottleneck()`.

### 23.11.2 The Utilization Snapshot

Both `ProcessSystem` and `ProcessModel` expose `getUtilizationSnapshotJson()`, a **side-effect-free** observation of plant capacity. It never calls `run()`; it only reads the utilization already computed by each unit's capacity constraints, so it is cheap to call on every optimization step:

```python
import json

snapshot = json.loads(str(plant.getUtilizationSnapshotJson()))
print("bottleneck:", snapshot["bottleneck"])
print("any overloaded:", snapshot["anyOverloaded"])
for unit in snapshot["units"]:
    print(unit["area"], unit["name"], unit["maxUtilizationPercent"],
          unit["limitingConstraint"])
```

Per unit the snapshot reports `name`, `type`, `maxUtilization` (0\u20131), `maxUtilizationPercent`, `limitingConstraint`, `feasible`, `hardLimitExceeded`, `power_kW` (for compressors and pumps), and a `constraints[]` breakdown; for a `ProcessModel` each unit also carries its `area`. Plant-wide it gives `bottleneck`, `anyOverloaded`, and `anyHardLimitExceeded`.

This snapshot is the **observation** half of a closed-loop optimization: the observation is `getUtilizationSnapshotJson()`, the action is the setpoint batch passed to `evaluate()`, and the reward is an objective read-back penalized whenever `anyOverloaded` is true or any unit's `maxUtilization` exceeds 1. The `BottleneckTracker` (Chapter 21) consumes successive snapshots to record how the binding constraint migrates as operating conditions change.

---

## 23.12 Architecture Summary and Extension Points

### 23.12.1 Component Diagram

Figure 23.2 illustrates the relationships between the key classes in the optimization framework.

![Component diagram showing the relationships between ProcessSystem, ProcessAutomation, CapacityConstrainedEquipment, CapacityConstraint, ProductionOptimizer, OptimizationConfig, OptimizationResult, ProcessOptimizationEngine, and CompressorChartGenerator.](figures/fig25_2_component_diagram.png)

The framework is organized in three tiers:

1. **Simulation tier** — `ProcessSystem`, `ProcessModel`, `ProcessAutomation` — provides the model, its topology, and variable access
2. **Constraint tier** — `CapacityConstrainedEquipment`, `CapacityConstraint`, `EquipmentCapacityStrategy` — provides equipment-level constraint knowledge
3. **Optimization tier** — `ProductionOptimizer`, `ProcessOptimizationEngine`, `OptimizationConfig`, `OptimizationResult` — provides search algorithms and result reporting

### 23.12.2 Pluggable Search Algorithms

The `SearchMode` enum can be extended with new algorithms by adding a new enum value and implementing the corresponding search logic in `ProductionOptimizer`. The framework's architecture separates the search algorithm from the objective evaluation and constraint checking, so a new algorithm need only call the existing `evaluateAtRate()` method to query the simulation.

### 23.12.3 Custom Constraints

New constraint types can be added at two levels:

**Equipment-level constraints** are added by implementing `CapacityConstrainedEquipment` on a new equipment class and defining `CapacityConstraint` objects in the `autoSize()` method. This is the preferred approach for constraints that are intrinsic to the equipment's physics.

**Process-level constraints** are added by creating `OptimizationConstraint` objects with custom evaluator functions. This is the preferred approach for constraints that span multiple equipment items (e.g., total facility power, export pipeline back-pressure) or are defined by external requirements (e.g., contractual delivery rates, regulatory limits).

### 23.12.4 External Optimizer Integration

For problems that require specialized solvers (e.g., mixed-integer programming, stochastic optimization), the framework provides integration points through the `ProcessSimulationEvaluator` class. This class wraps a `ProcessSystem` as a callable function that external optimizers (SciPy, IPOPT, pyomo) can evaluate:

```python
# Address-based evaluator for external Python optimizers.
auto = ProcessAutomation(process)
def evaluate_external(flow_kghr, pressure_bara):
    points = jpype.java.util.LinkedHashMap()
    # Mixed units: default flow is kg/hr and pressure is bara.
    points.put("feed.flowRate", float(flow_kghr))
    points.put("export compressor.outletPressure", float(pressure_bara))
    outputs = jpype.java.util.ArrayList(["export compressor.power"])
    return json.loads(str(auto.evaluate(points, None, outputs, "kW", 30, 5e-3)))
print(evaluate_external(100000.0, 150.0))
```

The `OptimizationConstraint` objects can be exported to `ConstraintDefinition` format for use with external solvers, maintaining consistency between the internal and external optimization paths.

### 23.12.5 SQP Integration

For constrained nonlinear programming with gradient information, the `SQPoptimizer` class provides a Sequential Quadratic Programming solver that uses NeqSim's simulation as the function evaluator. The SQP solver approximates the Hessian of the Lagrangian using BFGS updates and solves a quadratic programming subproblem at each iteration:

$$
\min_{d} \; \nabla f(x_k)^T d + \frac{1}{2} d^T B_k d
\quad \text{s.t.} \quad
\nabla g_j(x_k)^T d + g_j(x_k) \leq 0, \quad j = 1, \ldots, m
$$

where $d$ is the search direction, $B_k$ is the BFGS approximation to the Hessian, $f$ is the objective function, and $g_j$ are the inequality constraints. This provides faster convergence than derivative-free methods for smooth, well-conditioned problems.

---


<!-- September 2026 source update -->

![Conceptual sequence linking decisions, full-model solution, evidence checks and final-point replay](figures/optimization_evidence_loop_2026.svg)

The loop links the selected decision to one solved process state and its evidence. A candidate advances only when the required results are current, complete and applicable; replay closes the link between the reported optimum and the model readbacks.

## September 2026 execution and acceptance contract

Three interfaces in this chapter serve different purposes. `ProcessAutomation.evaluate()` applies setpoints, solves and returns requested readbacks. `AgenticProcessOptimizer` provides a bounded, address-based search that may use penalties. `ProductionOptimizer` provides equipment-aware optimization with explicit objectives and constraints. A successful address operation or search termination does not itself establish installed-equipment capacity, whole-plant coverage or permission to operate \cite{neqsim2026update}.

The current `ProductionOptimizer` always reapplies and solves the selected decision vector without cached evidence before returning. It may replay earlier feasible points if the first selection fails physical feasibility; final solve exceptions propagate. Preserve the replayed flow, equipment readbacks and result diagnostics together. Do not quote the best objective from the search tape alongside readbacks from another point.

For rate-only monotonic feasibility searches, use `BINARY_FEASIBILITY`. For golden-section, swarm or other score-based searches, supply an explicit objective. `null`/`None` objectives produce a zero objective score; they do not implicitly maximize throughput. The distinction matters when comparing algorithms.

`UtilizationCoverageReport` and `PlantUtilizationSnapshot` complement these optimizers. They represent declared coverage, evidence identity and validity, rather than inventing constraints from a sparse flowsheet. The new separator, pipeline, shared-resource and common-shaft adapters collect narrowly defined post-solve evidence. Read their unavailable status as a data gap, not as an unconstrained green operating point.

When integrating an external solver, use a fresh process instance per concurrent candidate or a rigorously managed state boundary. Record the exact NeqSim commit, variable units, objective scaling and termination reason. Recompute the selected point with the full process model and report its balances and constraint margins before treating the solver output as an engineering recommendation.

---

## 23.13 Summary

This chapter has presented the NeqSim optimization framework — a three-layer architecture that combines process simulation, equipment capacity constraints, and optimization algorithms into a coherent system for production optimization.

The key concepts are:

1. **ProcessSystem and ProcessModel** provide the simulation engine. The topology of the process graph determines the coupling structure of the optimization problem. Multi-area plants use `ProcessModel` with iterative cross-boundary convergence.

2. **ProcessAutomation** provides a stable, string-addressable API for reading and writing simulation variables. Self-healing automation with fuzzy matching and auto-correction makes the API robust for programmatic use. The discovery workflow (list units → list variables → read/write) enables systematic optimization setup.

3. **CapacityConstrainedEquipment** gives every equipment item knowledge of its operating limits. Constraints are typed (HARD, SOFT, DESIGN) and can be created automatically via `autoSize()` or configured from documented equipment ratings. Constraints are disabled by default for backward compatibility.

4. **ProductionOptimizer** orchestrates the search for optimal operating points. Five search algorithms cover the spectrum from simple binary search to global particle swarm optimization. The builder-pattern `OptimizationConfig` provides a clean configuration API, and `OptimizationResult` delivers rich diagnostics including infeasibility diagnosis and iteration history.

5. **Custom objectives and constraints** extend the framework beyond throughput maximization to multi-objective optimization combining production, energy, and emissions targets. Pareto front generation with knee-point detection supports decision-making under competing objectives.

6. **ProcessOptimizationEngine** wraps common workflows (maximum throughput, sensitivity analysis, lift curve generation) into single-method calls, reducing the barrier to entry for routine optimization tasks.

7. **CompressorChartGenerator** integration ensures that compressor-limited systems are optimized with full performance-map fidelity, including surge margin enforcement and operating point tracking.

8. **The evaluate() primitive and AgenticProcessOptimizer** turn a flowsheet into a steppable optimization target. `evaluate()` applies a setpoint batch, runs to convergence, gates feasibility, and reads back objectives in one never-throwing JSON call; `AgenticProcessOptimizer` wraps it in a bounded, seeded Nelder\u2013Mead search with quadratic-penalty constraints, a replayable trajectory tape, and a machine-readable readiness self-rating \u2014 a closed-loop optimizer designed for autonomous-agent and machine-learning workflows.

9. **ProcessModelOptimizationView and the utilization snapshot** extend optimization to full multi-area plants. The view exposes plant-wide bottleneck and constraint introspection, while `getUtilizationSnapshotJson()` provides a cheap, side-effect-free capacity observation that serves as the observation half of a closed-loop optimization loop and feeds the `BottleneckTracker`.

The framework is designed for extensibility: new search algorithms, new constraint types, and new equipment classes can be integrated without modifying existing code. For problems that exceed the built-in capabilities, the `ProcessSimulationEvaluator` provides a bridge to external optimization libraries.

---

## Exercises

**Exercise 23.1.** *ProcessAutomation discovery.* Build a three-stage separation process (HP separator at 60 bara, MP separator at 20 bara, LP separator at 3 bara) with a rich gas feed. Use `ProcessAutomation` to list all equipment units and their variable counts. Identify which variables are INPUT type and which are OUTPUT type. Verify that setting an INPUT variable and re-running the simulation changes the OUTPUT variables.

**Exercise 23.2.** *Constraint classification.* For the three-stage separation process in Exercise 23.1, call `autoSize(1.2)` on all three separators. List all constraints created, classify them as HARD, SOFT, or DESIGN, and explain the physical basis for each classification. What is the bottleneck equipment at the nominal flow rate?

**Exercise 23.3.** *Algorithm comparison.* Set up a single-variable throughput optimization on the three-stage separation process. Run the optimization with all five search algorithms (BINARY_FEASIBILITY, GOLDEN_SECTION_SCORE, NELDER_MEAD_SCORE, PARTICLE_SWARM_SCORE, GRADIENT_DESCENT_SCORE). Compare the number of iterations, the optimal rate found, and the total computation time. Which algorithm is most efficient for this linear topology?

**Exercise 23.4.** *Multi-variable optimization.* Add an export compressor to the process from Exercise 23.1. Define two decision variables: feed flow rate and compressor outlet pressure. Use NELDER_MEAD_SCORE to optimize a composite objective of 70% throughput + 30% efficiency. Report the optimal operating point and compare it to the throughput-only optimum.

**Exercise 23.5.** *Infeasibility diagnosis.* Set the upper bound of the optimization in Exercise 23.3 to a very high value (e.g., 10× the feasible maximum). Run the optimization and examine the `getInfeasibilityDiagnosis()` output. Which equipment items are violated? By how much? Propose a debottlenecking action for the limiting equipment.

**Exercise 23.6.** *Custom emissions constraint.* Define a custom `OptimizationConstraint` that limits the total compressor power to 10 MW (a proxy for CO₂ emissions). Run the throughput optimization with and without this constraint. How much production is lost due to the power cap? Calculate the implied abatement cost in USD/tonne CO₂ assuming a gas price of 8 USD/MMBtu and a compressor-specific CO₂ emission factor of 0.2 tonnes/MWh.

**Exercise 23.7.** *Pareto front generation.* For the process with export compressor, define two competing objectives: maximize throughput and minimize specific energy consumption (kWh/tonne of product). Generate a 15-point Pareto front using `optimizePareto()`. Plot the Pareto front and identify the knee point. What is the throughput penalty for operating at minimum specific energy versus maximum throughput?

**Exercise 23.8.** *Compressor chart integration.* Generate a multi-speed compressor chart using `CompressorChartGenerator` with the `"CENTRIFUGAL_STANDARD"` template. Apply the chart to the export compressor and re-run the optimization. Compare the optimal rate with and without the performance chart. Explain why the chart-based result differs (if it does) by examining the surge margin and efficiency at the operating point.

---

## References

1. Edgar, T.F., Himmelblau, D.M. and Lasdon, L.S. (2001) *Optimization of Chemical Processes*, 2nd edn, McGraw-Hill.
2. Biegler, L.T. (2010) *Nonlinear Programming: Concepts, Algorithms, and Applications to Chemical Processes*, SIAM.
3. Nelder, J.A. and Mead, R. (1965) A simplex method for function minimization. *The Computer Journal*, 7(4), pp. 308–313.
4. Kennedy, J. and Eberhart, R. (1995) Particle swarm optimization. *Proceedings of IEEE International Conference on Neural Networks*, pp. 1942–1948.
5. Nocedal, J. and Wright, S.J. (2006) *Numerical Optimization*, 2nd edn, Springer.
6. Kiefer, J. (1953) Sequential minimax search for a maximum. *Proceedings of the American Mathematical Society*, 4(3), pp. 502–506.
7. API RP 14E (2007) *Recommended Practice for Design and Installation of Offshore Production Platform Piping Systems*, 5th edn, American Petroleum Institute.
8. NORSOK P-001 (2006) *Process Design*, Standards Norway.
9. Campbell, J.M. (2014) *Gas Conditioning and Processing*, 9th edn, Campbell Petroleum Series.
10. Botros, K.K. and Henderson, J.F. (1994) Developments in centrifugal compressor surge control. *ASME Journal of Turbomachinery*, 116(2), pp. 240–249.
11. Arora, J.S. (2017) *Introduction to Optimum Design*, 4th edn, Academic Press.
12. Gill, P.E., Murray, W. and Wright, M.H. (1981) *Practical Optimization*, Academic Press.


