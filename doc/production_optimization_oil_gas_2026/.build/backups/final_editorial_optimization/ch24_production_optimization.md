# Production Optimization

<!-- Chapter metadata -->
<!-- Notebooks: ch18_throughput_optimization.ipynb, ch18_bottleneck_analysis.ipynb, ch18_multi_objective_pareto.ipynb, ch18_scenario_comparison.ipynb, ch18_realtime_optimization_loop.ipynb -->
<!-- Estimated pages: 55 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Define the production optimization problem mathematically with objective functions, decision variables, and equipment capacity constraints
2. Explain how equipment capacity constraints arise from separator K-factors, compressor maps, valve $C_v$ curves, pipeline erosional velocity, and pump NPSH requirements
3. Use the NeqSim `CapacityConstrainedEquipment` interface to define multi-constraint models on process equipment, including HARD, SOFT, and DESIGN constraint types
4. Configure equipment constraints automatically using `autoSize()` and manage constraint presets (`useEquinorConstraints()`, `useAPIConstraints()`, `useAllConstraints()`)
5. Perform facility-level bottleneck analysis using `ProcessSystem.findBottleneck()`, `getCapacityUtilizationSummary()`, and `getEquipmentNearCapacityLimit()`
6. Configure and run the `ProductionOptimizer` with five search algorithms (BINARY_FEASIBILITY, GOLDEN_SECTION_SCORE, NELDER_MEAD_SCORE, PARTICLE_SWARM_SCORE, GRADIENT_DESCENT_SCORE)
7. Use the `OptimizationConfig` builder to set tolerances, utilization limits, stagnation detection, warm start, LRU caching, and parallel evaluations
8. Interpret `OptimizationResult` objects including optimal rate, bottleneck identification, iteration history, infeasibility diagnosis, and JSON/CSV export
9. Define custom objectives (`OptimizationObjective`) and custom constraints (`OptimizationConstraint`) for application-specific optimization formulations
10. Use the `ProcessOptimizationEngine` (Level 2 unified engine) for sensitivity analysis, lift curve generation, and strategy-based constraint evaluation
11. Solve multi-objective optimization problems using `optimizePareto()` with weighted-sum scalarization and Pareto front analysis
12. Integrate compressor performance curves with the optimization framework, including surge margin constraints and `CompressorChartGenerator`
13. Compare operating scenarios using `ScenarioRequest`, `ScenarioKpi`, and `compareScenarios()`
14. Implement real-time optimization loops combining process simulation, constraint checking, and periodic re-optimization
15. Troubleshoot common optimization failures including infeasibility, stagnation, and shifting bottlenecks

---

## 24.1 Introduction

Production optimization is the systematic process of finding the operating conditions that maximize a chosen objective — typically production rate, revenue, or energy efficiency — while satisfying all equipment, safety, and contractual constraints. It is both a theoretical discipline rooted in mathematical programming and a practical operational activity performed daily on producing oil and gas fields.

The fundamental question is deceptively simple:

> *Given the current state of the reservoir, wells, and facilities, what is the maximum achievable production rate, and which equipment limits it?*

The difficulty lies in the complexity of the system. A typical offshore platform may have 10–30 wells, 20–50 process equipment items, hundreds of control valves, and thousands of possible combinations of operating set points. The process is nonlinear, coupled, and constrained. Reservoir behavior is uncertain. Equipment degrades over time. Contractual obligations impose hard limits on product specifications.

This chapter presents a comprehensive treatment of production optimization using NeqSim's built-in optimization framework. We begin with the mathematical formulation of capacity constraints (Section 24.2), then introduce the `CapacityConstrainedEquipment` interface that makes every piece of process equipment self-aware of its limits (Section 24.3). The `autoSize()` integration (Section 24.4) and facility-level bottleneck analysis (Section 24.5) provide the constraint evaluation layer. Sections 24.6–24.8 cover the `ProductionOptimizer` API in full detail — configuration, search algorithms, and result interpretation. The `ProcessOptimizationEngine` (Section 24.9) provides a higher-level unified engine. Multi-objective optimization, scenario comparison, compressor curve integration, and real-time optimization are covered in Sections 24.10–24.14. The chapter concludes with best practices, troubleshooting guidance, and exercises.

### 24.1.1 The Role of Process Simulation in Optimization

Process simulation is the engine that drives production optimization. Given a set of decision variables (pressures, temperatures, flow rates, valve positions), the process simulator computes the resulting production rates, product qualities, energy consumption, and — crucially — whether all equipment constraints are satisfied.

$$
\text{Optimizer} \xrightarrow{\text{set points}} \text{Process Simulator} \xrightarrow{\text{performance + feasibility}} \text{Optimizer}
$$

The optimizer explores the decision variable space, calling the simulator at each candidate point to evaluate the objective function and check feasibility, then iteratively moves toward the optimum. The efficiency of this loop depends on:

- **Simulation speed**: Each evaluation requires running the full process model
- **Constraint evaluation**: Every equipment item must be checked against its capacity limits
- **Caching**: Redundant evaluations should be avoided
- **Algorithm choice**: The search algorithm determines how many evaluations are needed

NeqSim's optimization framework automates this entire loop, providing a single API call that handles simulation execution, constraint evaluation, caching, and convergence control.

### 24.1.2 Optimization Timescales

| Timescale | Optimization Task | Decision Variables | Frequency |
|-----------|-------------------|-------------------|-----------|
| Minutes | Well choke adjustment | Individual well chokes | Real-time |
| Hours | Gas lift allocation | Gas lift rates per well | Several times daily |
| Days | Separator pressure optimization | Stage pressures | Daily to weekly |
| Weeks | Routing optimization | Well-to-manifold assignments | Weekly to monthly |
| Months | Compressor configuration | Number of stages, speeds | Seasonal |
| Years | Facility modification planning | Equipment upgrades, tie-backs | Annual review |

This chapter focuses primarily on the daily-to-monthly operational optimization timescale, where process simulation is most directly applicable.

### 24.1.3 Production Optimization as a Life-of-Field Problem

The production optimization problem changes continuously over the life of a field:

**Early life (plateau production):** Reservoir pressure is high, and the wells can deliver more fluid than the facilities can process. The bottleneck is typically topside equipment — separator capacity, compressor power, or pipeline pressure drop. Optimization focuses on maximizing throughput up to equipment limits.

**Mid-life (declining reservoir pressure):** As reservoir pressure declines, the wellhead pressure decreases and the gas-to-oil ratio (GOR) changes. The compression ratio increases, requiring more compressor power per unit of export gas. The bottleneck may shift from separator capacity to compressor power.

**Late life (high water cut / low pressure):** Water production increases, consuming separator and pump capacity. Reservoir pressure is low, requiring maximum compression and possibly gas lift. Multiple equipment items may be simultaneously near their limits. Optimization becomes a complex multi-constraint problem.

This life-cycle evolution means that the **bottleneck identity shifts over time**, and the optimal operating strategy must evolve accordingly. A production optimization system that identifies the current bottleneck and quantifies the spare capacity of other equipment enables proactive planning for future constraints.

### 24.1.4 Economic Value of Production Optimization

The economic impact of production optimization is substantial. Even small improvements in production efficiency translate to large revenue gains:

**Illustrative gross-revenue calculation:** at an assumed 100,000 bbl/day, 70 USD/bbl, 365 operating days and a hypothetical 2% uplift, incremental revenue is 51.1 million USD/year. This is not a measured optimization benefit or net project value. Subtract incremental operating cost, capital, downtime and applicable fiscal charges before judging an investment. No generic percentage uplift is established by this example.

The value compounds when optimization prevents costly equipment trips, reduces flaring, and extends the economic life of the field by maintaining production during the decline phase.

---

## 24.2 Equipment Capacity Constraints: Theory

Every piece of process equipment has physical limits that cannot be exceeded without risking damage, safety hazards, or loss of function. Understanding these limits mathematically is the foundation of production optimization.

### 24.2.1 The Utilization Factor

The **utilization factor** provides a unified metric for comparing how close any equipment item is to its capacity limit:

$$
U_i = \frac{Q_{i,\text{actual}}}{Q_{i,\text{max}}}
$$

where $U_i$ is the utilization factor for equipment item $i$, $Q_{i,\text{actual}}$ is the actual operating duty, and $Q_{i,\text{max}}$ is the maximum allowable duty. The highest reported utilization identifies a candidate limiting check. Only when each relevant load scales linearly with feed and its limit remains fixed does the following approximate throughput extrapolation apply:

$$
Q_{\text{system,max}} = \frac{Q_{\text{current}}}{\max_i(U_i)}
$$

### 24.2.2 Constraint Classification

Not all constraints are equal. NeqSim classifies constraints into three severity levels:

| Type | Description | Consequence of Violation | Example |
|------|-------------|-------------------------|---------|
| **HARD** | Absolute equipment limits | Trip, mechanical failure, safety hazard | Compressor overspeed, PSV capacity |
| **SOFT** | Efficiency or operational limits | Reduced efficiency, accelerated wear | Design flow rate, temperature approach |
| **DESIGN** | Design basis values | Information only — no operational impact | Nameplate capacity, design point |

This classification enables the optimizer to distinguish between constraints that make a solution physically impossible (HARD) and those that merely make it suboptimal (SOFT).

### 24.2.3 Separator Capacity Constraints

Separator capacity is governed by three independent criteria — the minimum of the three determines the overall separator capacity.

**Gas handling capacity** is limited by the Souders-Brown equation (Souders and Brown, 1934):

$$
v_{\text{gas,max}} = K_{\text{SB}} \cdot \sqrt{\frac{\rho_L - \rho_G}{\rho_G}}
$$

where $K_{\text{SB}}$ is the Souders-Brown coefficient (m/s), $\rho_L$ is the liquid density (kg/m³), and $\rho_G$ is the gas density (kg/m³). The coefficient depends on device loading, droplet size, pressure and fluid properties. The following broad classroom ranges are not vendor guarantees or design-code limits:

| Separator Configuration | $K_{\text{SB}}$ (m/s) | Typical Application |
|------------------------|----------------------|---------------------|
| Vertical, no internals | 0.04–0.06 | Scrubbers, test separators |
| Vertical, wire mesh demister | 0.07–0.11 | Inlet separators |
| Horizontal, half-full | 0.12–0.17 | Production separators |
| Horizontal, wire mesh demister | 0.15–0.21 | Two-phase separators |
| Horizontal, vane pack | 0.18–0.25 | High-capacity separators |

The maximum gas flow rate through the separator is:

$$
Q_{\text{gas,max}} = v_{\text{gas,max}} \cdot A_{\text{gas}}
$$

where $A_{\text{gas}}$ is the free gas cross-section. For a horizontal cylinder, liquid height fraction is not area fraction. With radius $r=D/2$ and height $0\le h\le D$,

$$
\begin{aligned}
A_L(h)&=r^2\cos^{-1}\!\left(\frac{r-h}{r}\right)
 -(r-h)\sqrt{2rh-h^2},\\
A_{\text{gas}}&=\pi r^2-A_L(h).
\end{aligned}
$$

The simple half-area result holds at $h=D/2$; apply the segment geometry elsewhere.

The gas load factor utilization is:

$$
U_{\text{gas}} = \frac{v_{\text{gas,actual}}}{v_{\text{gas,max}}} = \frac{Q_{\text{gas,actual}}}{Q_{\text{gas,max}}}
$$

When $U_{\text{gas}} > 1.0$, liquid droplet carry-over increases significantly, leading to poor separation performance and downstream contamination.

**Liquid handling capacity** is determined by the minimum retention time required for gas bubbles to rise out of the liquid phase and for water droplets to settle:

$$
t_{\text{ret}} = \frac{V_{\text{liq}}}{Q_{\text{liq}}}
$$

where $V_{\text{liq}}$ is the liquid volume in the separator (m³) and $Q_{\text{liq}}$ is the total liquid volumetric flow rate (m³/s). Illustrative retention-time ranges, requiring fluid-specific settling/coalescence evidence:

| Service | Oil Retention Time (min) | Water Retention Time (min) |
|---------|------------------------|---------------------------|
| HP separator, light oil (API > 30) | 1–3 | 1–2 |
| HP separator, medium oil | 3–5 | 2–3 |
| LP separator, light oil | 2–4 | 2–3 |
| Three-phase separator | 5–10 | 5–15 |

The liquid capacity utilization is:

$$
U_{\text{liq}} = \frac{t_{\text{ret,min}}}{t_{\text{ret,actual}}} = \frac{Q_{\text{liq,actual}} \cdot t_{\text{ret,min}}}{V_{\text{liq}}}
$$

**Gas-liquid interface area** provides a third constraint for horizontal separators, limiting the rate at which gas can disengage from the liquid:

$$
\sigma_{\text{GL}} = \frac{Q_{\text{liq}}}{A_{\text{GL}}}, \qquad U_{\text{GL}} = \frac{\sigma_{\text{GL}}}{\sigma_{\text{GL,max}}}
$$

The admissible interface loading requires a stated disengagement model or test basis. No universal value follows from API gravity and GOR alone.

The overall separator utilization is the maximum of all active criteria:

$$
U_{\text{sep}} = \max(U_{\text{gas}}, U_{\text{liq}}, U_{\text{GL}})
$$

The limiting criterion depends on operating conditions. For a gas-dominated field, $U_{\text{gas}}$ typically governs. For a mature field with high water cut, $U_{\text{liq}}$ often becomes the bottleneck. This shifting behavior is precisely what makes automated bottleneck detection valuable — it identifies the active constraint without manual calculation.

### 24.2.4 Compressor Capacity Constraints

Compressors have multiple simultaneous constraints forming an operating envelope. The compressor operating point must lie within the region bounded by the surge line, stonewall (choke) line, maximum speed, minimum speed, and power limit curves.

- **Surge limit** (HARD): Minimum flow for aerodynamic stability. Surge can cause oscillatory flow reversal and damage; its frequency depends on the compressor and connected volumes. The surge margin is defined as:

$$
SM = \frac{Q_{\text{actual}} - Q_{\text{surge}}}{Q_{\text{surge}}} \times 100\%
$$

A 10% margin is an assumed teaching value on this surge-flow denominator basis; use the vendor/controller definition and requirement. Operating below this margin requires anti-surge recycle, which wastes energy but protects the compressor.

- **Power limit** (HARD): Shaft power must not exceed driver capacity. For gas turbine drivers, the available power decreases with ambient temperature (derating):

$$
W_{\text{shaft}} = \frac{\dot{m} \cdot \Delta h_{\text{isen}}}{\eta_{\text{isen}}} + W_{\text{mech\ losses}}
$$

$$
W_{\text{GT,derated}} = W_{\text{GT,ISO}} \cdot \left(1 - \alpha \cdot (T_{\text{amb}} - T_{\text{ISO}})\right)
$$

where $\alpha$ is the derating coefficient, typically 0.5–0.8% per °C for aeroderivative gas turbines. The power utilization is:

$$
U_{\text{power}} = \frac{W_{\text{shaft}}}{W_{\text{driver,derated}}}
$$

- **Speed limit** (HARD): Maximum impeller rotational speed is set by mechanical stress limits. Use the manufacturer's mechanical speed limit; tip speed alone does not define a universal failure threshold.

- **Stonewall (choke) limit**: Maximum volumetric throughput when the gas velocity at the impeller throat approaches sonic velocity. Beyond this point, no further increase in flow is possible regardless of downstream pressure reduction.

- **Discharge temperature limit** (SOFT): Excessive discharge temperature accelerates seal and lubricant degradation. Use the applicable seal, material and lubricant temperature limits; no universal dry-gas-seal limit is implied.

The polytropic head relates compression ratio to gas properties:

$$
H_p = Z_{\text{avg}} \cdot \frac{R}{M} \cdot T_1 \cdot \frac{n}{n-1} \cdot \left[\left(\frac{P_2}{P_1}\right)^{(n-1)/n} - 1\right]
$$

where $n$ is the polytropic exponent, $R$ is the universal gas constant, $T_1$ is suction temperature, $M$ is molecular weight, and $Z_{\text{avg}}$ is the average compressibility factor.

The combined compressor utilization considers all constraints:

$$
U_{\text{comp}} = \max(U_{\text{surge}}, U_{\text{power}}, U_{\text{speed}}, U_{\text{stonewall}}, U_{\text{T,discharge}})
$$

In practice, the power limit is often the binding constraint for export compressors (especially in hot climates where gas turbine derating is significant), while the surge limit governs during turndown operations.

### 24.2.5 Valve Capacity Constraints

Control valves are characterized by their flow coefficient $C_v$, which relates flow rate to pressure drop across the valve. For liquid flow (ISA/IEC 60534):

$$
Q = N_1 F_P C_v \sqrt{\frac{\Delta P_{\mathrm{sizing}}}{\rho/\rho_0}}
$$

For gas flow under subcritical conditions:

$$
W = N_6 F_P C_v Y \sqrt{x_{\mathrm{sizing}}P_1\rho_1}
$$

Here $F_P$ is the piping geometry factor, $x=\Delta P/P_1$, $x_{\mathrm{sizing}}=\min(x,F_\gamma x_{TP})$, and $Y=1-x_{\mathrm{sizing}}/(3F_\gamma x_{TP})$. For liquid service use the lesser of the actual and liquid-choking pressure drop; recovery factor $F_L$ belongs in that choking calculation, not as a general multiplier on subcritical flow. The constants $N_1,N_6$ depend on the stated unit system. See the manufacturer sizing procedure \cite{emerson2023valves}.

A coefficient-capacity ratio compares required $C_v$ to maximum installed $C_v$:

$$
U_{\text{valve}} = \frac{C_{v,\text{required}}}{C_{v,\text{max}}}
$$

The coefficient ratio is not travel unless the installed characteristic is linear. A 20–80% travel window is an illustrative control-authority assumption, not a universal requirement. Below 20%, the valve is nearly closed and may exhibit instability. Above 80%, there is insufficient control authority to handle disturbances. A fully open valve (100%) provides no control margin and limits system throughput — any increase in flow would require a larger valve.

For well-service chokes, use a named multiphase/choked-flow model with a defined phase-volume basis and calibrated discharge coefficient. A single arbitrary multiplier on a single-phase $C_v$ expression does not establish flashing or critical-flow capacity.

### 24.2.6 Pipeline Capacity Constraints

Pipelines are constrained by multiple criteria, any of which can limit throughput.

**Erosional velocity** (API RP 14E): An empirical velocity screen can flag a need for further assessment; satisfying it does not establish freedom from erosion, corrosion or sand damage:

$$
v_{\text{eros}} = \frac{C}{\sqrt{\rho_m}}
$$

where $C$ is the empirical constant (100–300 in field units, with C = 100 being the most conservative) and $\rho_m$ is the mixture density (lb/ft³ in US customary or kg/m³ with adjusted $C$). The velocity utilization is:

$$
U_{\text{vel}} = \frac{v_{\text{actual}}}{v_{\text{eros}}}
$$

**Flow-Induced Vibration (FIV)**: For multiphase flow, vibration assessment must include excitation, support stiffness, geometry and fatigue response. DNV-RP-F101 addresses corroded pipelines, not vibration screening. The following normalized indicators are illustrative only; apply the relevant Energy Institute guidance or another explicitly qualified method \cite{dnvf101scope,eivibration}: 

- **Likelihood of Failure (LOF)**: $\rho_m v_m^2 / \text{LOF}_{\text{limit}}$
- **Force RMS**: $F_{\text{RMS}} / F_{\text{RMS,limit}}$, where $F_{\text{RMS}}$ is the root-mean-square force from slug impact

$$
U_{\text{FIV}} = \max\left(\frac{\rho_m v_m^2}{\text{LOF}_{\text{limit}}}, \frac{F_{\text{RMS}}}{F_{\text{RMS,limit}}}\right)
$$

**Pressure drop**: The available pressure drop between the upstream vessel and the receiving facility limits the flow:

$$
U_{\Delta P} = \frac{\Delta P_{\text{actual}}}{\Delta P_{\text{available}}}
$$

For long subsea pipelines, the available pressure drop may be the primary constraint. The Beggs-and-Brill correlation (or equivalent) computes the frictional and gravitational pressure drop:

$$
-\frac{dP}{dL} = \frac{f_D \rho_f v_m^2}{2D} + \rho_h g \sin\theta + \rho_a v_m \frac{dv_m}{dL}
$$

The coordinate follows the flow, with positive inclination uphill. The schematic momentum equation distinguishes holdup density $\rho_h$ from friction/acceleration effective densities; Beggs–Brill applies its own holdup and slip correlations.

**MAOP**: enforce the applicable operating pressure limit and separately assess the design code's transient/protection requirements.

The overall pipeline utilization is:

$$
U_{\text{pipe}} = \max(U_{\text{vel}}, U_{\text{FIV}}, U_{\Delta P}, U_{\text{MAOP}})
$$

### 24.2.7 Pump Capacity Constraints

Pumps are limited by three primary constraints:

**Net Positive Suction Head (NPSH)**: The available NPSH must exceed the required NPSH to avoid cavitation:

$$
\text{NPSH}_A = \frac{P_{s,\mathrm{abs}}-P_v}{\rho g}+\frac{v_s^2}{2g}
$$

$$
U_{\text{NPSH}} = \frac{\text{NPSH}_R}{\text{NPSH}_A}
$$

Pressure and velocity here are at the suction flange on the pump reference datum; an elevation term is added only when converting from another measurement datum. Required NPSH commonly denotes a specified head-drop test criterion, not zero cavitation. Set the application-specific margin using the pump vendor and applicable guidance. Cavitation causes rapid impeller erosion, loss of head, and increased vibration.

**Power**: Pump power consumption is:

$$
W_{\text{electrical}} = \frac{Q \Delta P}{\eta_{\text{pump}} \eta_{\text{motor}}}, \qquad U_{\text{power}} = \frac{Q\Delta P/\eta_{\text{pump}}}{W_{\text{driver,shaft,max}}}
$$

**Pump curve operating range**: The pump must operate within the stable region of its head-flow curve. At very low flow ("minimum continuous flow"), internal recirculation causes vibration and heating. At very high flow, NPSH requirements increase rapidly.

### 24.2.8 Heat Exchanger Capacity Constraints

Heat exchangers are constrained by thermal duty and pressure drop:

$$
Q = U \cdot A \cdot \Delta T_{\text{LMTD}} \cdot F_t
$$

where $U$ is the overall heat transfer coefficient, $A$ is the heat transfer area, $\Delta T_{\text{LMTD}}$ is the log-mean temperature difference, and $F_t$ is the LMTD correction factor for multi-pass configurations.

Fouling reduces the effective $U$ value over time, reducing the available duty. The fouling utilization is:

$$
\frac{1}{U_{\mathrm{fouled}}}=\frac{1}{U_{\mathrm{clean}}}+R_f, \qquad
U_{\mathrm{duty}}=\frac{Q_{\mathrm{required}}}{U_{\mathrm{fouled}}A\Delta T_{\mathrm{LMTD}}F_t}
$$

The approach temperature ($T_{\text{hot,out}} - T_{\text{cold,in}}$ or $T_{\text{hot,in}} - T_{\text{cold,out}}$) is a practical constraint — a small positive approach leaves little thermal driving force and may require large area. A large approach alone does not diagnose undersizing; compare duty and both stream energy balances. Check both terminal differences and internal pinch points when heat capacity or phase state varies.

### 24.2.9 Equipment Capacity Support Matrix

Table 24.1 summarizes which equipment types can restrict production and what constraints apply:

| Equipment Type | Constraint Parameters | Active Bottleneck Scenario | NeqSim Class |
|---------------|----------------------|---------------------------|-------------|
| Separator | gasLoadFactor, liquidRetentionTime | High GOR → gas capacity; High WC → liquid capacity | `ThreePhaseSeparator`, `Separator` |
| Compressor | speed, power, surgeMargin, dischargeTemp | Low reservoir P → high ratio → power limit | `Compressor` |
| Pump | npshMargin, power, flowRate | High water cut → pump capacity | `Pump` |
| Valve | valveOpening, cvUtilization | High flow → valve wide open | `ThrottlingValve` |
| Pipeline | velocity, pressureDrop, FIV_LOF, FIV_FRMS | Long tieback → pressure drop limit | `PipeBeggsAndBrills` |
| Heater/Cooler | duty, approachTemperature | Fouling → reduced UA → duty limit | `Heater`, `HeatExchanger` |

---

## 24.3 The CapacityConstrainedEquipment Interface

NeqSim provides a standardized interface — `CapacityConstrainedEquipment` — that enables any process equipment to declare its capacity constraints. This interface is the foundation of automated bottleneck detection and optimization.

### 24.3.1 Interface Design

The `CapacityConstrainedEquipment` interface defines the contract that all capacity-aware equipment must implement:

```java
public interface CapacityConstrainedEquipmentExcerpt {
    // Query constraints
    Map<String, CapacityConstraint> getCapacityConstraints();
    CapacityConstraint getBottleneckConstraint();

    // Utilization metrics
    double getMaxUtilization();
    double getMaxUtilizationPercent();
    double getAvailableMargin();

    // Violation checks
    boolean isCapacityExceeded();
    boolean isHardLimitExceeded();
    boolean isNearCapacityLimit();

    // Enable/disable
    boolean isCapacityAnalysisEnabled();
    void setCapacityAnalysisEnabled(boolean enabled);

    // Summary
    Map<String, Double> getUtilizationSummary();
}
```

### 24.3.2 The CapacityConstraint Class

Each individual constraint is represented by a `CapacityConstraint` object with a fluent builder API:

```java
import neqsim.thermo.system.*;
import neqsim.process.processmodel.*;
import neqsim.process.equipment.stream.*;
import neqsim.process.equipment.separator.*;
import neqsim.process.equipment.compressor.*;
import neqsim.process.equipment.valve.*;
import neqsim.process.equipment.pipeline.*;
import neqsim.process.equipment.pump.*;
import neqsim.process.equipment.capacity.*;
import neqsim.process.util.optimizer.*;
import neqsim.process.util.optimizer.ProductionOptimizer.*;
import neqsim.process.automation.*;
import neqsim.process.processmodel.lifecycle.*;
import java.util.*;
import org.apache.logging.log4j.*;
Logger logger = LogManager.getLogger("ProductionBook");
SystemInterface gas = new SystemSrkEos(313.15, 60.0);
gas.addComponent("methane", 0.90);
gas.addComponent("ethane", 0.10);
gas.setMixingRule("classic");
Stream feed = new Stream("Feed", gas);
feed.setFlowRate(100000.0, "kg/hr");
Separator separator = new Separator("HP Sep", feed);
Compressor compressor = new Compressor("Compressor", separator.getGasOutStream());
compressor.setOutletPressure(150.0, "bara");
compressor.setPolytropicEfficiency(0.78);
compressor.setUsePolytropicCalc(true);
ProcessSystem process = new ProcessSystem();
process.add(feed);
process.add(separator);
process.add(compressor);
process.run();
CapacityConstraint speedConstraint = new CapacityConstraint("speed", "RPM",
    CapacityConstraint.ConstraintType.HARD).setDesignValue(10000.0).setMaxValue(11000.0)
    .setWarningThreshold(0.9).setDescription("Declared demonstration speed limit")
    .setValueSupplier(() -> compressor.getSpeed());
```

The constraint tracks:

- **Design value**: The rated operating value (e.g., 10,000 RPM)
- **Max value**: The absolute maximum (e.g., 11,000 RPM mechanical limit)
- **Current value**: Obtained from a live supplier function
- **Warning threshold**: Fraction of design that triggers an alert (default 0.9)
- **Utilization**: Computed as $U = \text{currentValue} / \text{designValue}$

### 24.3.3 Constraint Types and Severity

NeqSim supports a four-level severity hierarchy for fine-grained optimizer control:

| Severity | Description | Optimizer Behavior |
|----------|-------------|-------------------|
| `CRITICAL` | Equipment damage or safety hazard (surge, overspeed) | Immediately rejects solution |
| `HARD` | Exceeds design limits (max power, max flow) | Marks solution infeasible |
| `SOFT` | Exceeds recommended range (efficiency targets) | Applies penalty to objective |
| `ADVISORY` | Information only (design point deviation) | No impact on optimization |

### 24.3.4 Constraints Disabled by Default

For backward compatibility, capacity constraints are **disabled by default** in NeqSim. Equipment tracks its constraints internally, but they do not affect system-level bottleneck analysis or optimization until explicitly enabled. This design ensures that existing simulations continue to work without modification.

### 24.3.5 Enabling Constraints

Constraints can be enabled at multiple levels:

**Individual equipment:**

```java
compressor.enableAllConstraints();
// Constraints and limits require explicit equipment-specific configuration; no standard-compliance preset is implied.
```

**System-wide:**

```java
process.enableAllConstraints();
```

**Python equivalent:**

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

fluid = jneqsim.thermo.system.SystemSrkCPAstatoil(273.15 + 70.0, 65.0)
fluid.addComponent("methane", 0.70)
fluid.addComponent("ethane", 0.08)
fluid.addComponent("propane", 0.05)
fluid.addComponent("n-butane", 0.03)
fluid.addComponent("n-heptane", 0.08)
fluid.addComponent("water", 0.06)
fluid.setMixingRule(10)
fluid.setMultiPhaseCheck(True)
fluid.setMultiPhaseCheck(True)

feed = jneqsim.process.equipment.stream.Stream("feed", fluid)
feed.setFlowRate(200000.0, "kg/hr")

sep = jneqsim.process.equipment.separator.ThreePhaseSeparator("HP Sep", feed)
comp = jneqsim.process.equipment.compressor.Compressor("Export Comp",
    sep.getGasOutStream())
comp.setOutletPressure(150.0)
comp.setPolytropicEfficiency(0.78)
comp.setUsePolytropicCalc(True)

process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(sep)
process.add(comp)
process.run()

# Auto-size with 20% design margin
sep.autoSize(1.2)
comp.autoSize(1.2)
# Fixed-pressure power screening; synthetic auto-size maps are not installed data.
comp.getCompressorChart().setUseCompressorChart(False)
comp.setSolveSpeed(False)
comp.setUsePolytropicCalc(True)
for entry in comp.getCapacityConstraints().entrySet():
    entry.getValue().setEnabled(str(entry.getKey()) == "power")


print(f"Separator utilization: {sep.getMaxUtilizationPercent():.1f}%")
print(f"Compressor utilization: {comp.getMaxUtilizationPercent():.1f}%")

process.enableAllConstraints()
print("Enabled constraints for the explicitly built process")
```

### 24.3.6 Disabling for What-If Studies

For what-if debottlenecking studies, constraints can be selectively disabled to explore the effect of removing a particular limitation:

```java
// Disable all constraints for unconstrained throughput study
process.disableAllConstraints();

// Exclude specific equipment from capacity analysis entirely
separator.setCapacityAnalysisEnabled(false);
```

This is particularly useful for answering questions like: "What would the system throughput be if we upgraded the compressor driver to 30 MW?"

---

## 24.4 The autoSize() Integration

The `autoSize()` method provides a one-call mechanism to configure equipment capacity constraints automatically based on the current operating point and a design margin factor.

### 24.4.1 How autoSize() Works

When called with a margin factor (e.g., 1.2 for 20% margin), `autoSize()`:

1. Runs the equipment at the current operating point
2. Extracts the key performance parameters
3. Creates capacity constraints with the design value set to the current value multiplied by the margin factor
4. Registers the constraints with the equipment

This simulates the common engineering practice of sizing equipment with a design margin above the expected operating conditions.

### 24.4.2 Equipment-Specific autoSize Behavior

**Separator:**

```java
separator.autoSize(1.2);
// Creates: gasLoadFactor constraint with designValue = currentKFactor * 1.2
```

**Compressor:**

```java
compressor.autoSize(1.2);
compressor.getCompressorChart().setUseCompressorChart(false);
compressor.setSolveSpeed(false);
compressor.setUsePolytropicCalc(true);
for (Map.Entry<String,CapacityConstraint> entry : compressor.getCapacityConstraints().entrySet()) { entry.getValue().setEnabled(entry.getKey().equals("power")); }
// Creates: speed, power, surgeMargin constraints
// Also generates compressor performance curves via CompressorChartGenerator
```

**Valve:**

```java
ThrottlingValve valve = new ThrottlingValve("Example valve", feed);
valve.setOutletPressure(50.0);
valve.run();
valve.autoSize(1.2);
```

**Pipeline:**

```java
PipeBeggsAndBrills pipeline = new PipeBeggsAndBrills("Example pipe", feed);
pipeline.setLength(1000.0);
pipeline.setDiameter(0.25);
pipeline.setAngle(0.0);
pipeline.run();
pipeline.autoSize(1.2);
```

**Pump:**

```java
SystemInterface liquid = new SystemSrkEos(298.15, 5.0);
liquid.addComponent("n-heptane", 1.0);
liquid.setMixingRule("classic");
Stream pumpFeed = new Stream("Pump feed", liquid);
pumpFeed.setFlowRate(10000.0, "kg/hr");
pumpFeed.run();
Pump pump = new Pump("Example pump", pumpFeed);
pump.setOutletPressure(10.0);
pump.run();
pump.autoSize(1.2);
```

### 24.4.3 Complete autoSize Example

```java
// Build process model
SystemInterface fluid = new SystemSrkEos(273.15 + 70.0, 65.0);
fluid.addComponent("methane", 0.70);
fluid.addComponent("ethane", 0.08);
fluid.addComponent("propane", 0.05);
fluid.addComponent("n-butane", 0.03);
fluid.addComponent("n-heptane", 0.08);
fluid.addComponent("water", 0.06);
fluid.setMixingRule("classic");
fluid.setMultiPhaseCheck(true);

Stream feed = new Stream("feed", fluid);
feed.setFlowRate(200000.0, "kg/hr");

ThreePhaseSeparator sep = new ThreePhaseSeparator("HP Sep", feed);
Compressor comp = new Compressor("Export Comp", sep.getGasOutStream());
comp.setOutletPressure(150.0);
comp.setPolytropicEfficiency(0.78);
comp.setUsePolytropicCalc(true);

ProcessSystem process = new ProcessSystem();
process.add(feed);
process.add(sep);
process.add(comp);
process.run();

// Auto-size all equipment with 20% design margin
sep.autoSize(1.2);
comp.autoSize(1.2);
comp.getCompressorChart().setUseCompressorChart(false);
comp.setSolveSpeed(false);
comp.setUsePolytropicCalc(true);
for (Map.Entry<String,CapacityConstraint> entry : comp.getCapacityConstraints().entrySet()) { entry.getValue().setEnabled(entry.getKey().equals("power")); }

// Now all equipment has capacity constraints
logger.info("Sep max util: " + sep.getMaxUtilizationPercent() + "%");
logger.info("Comp max util: " + comp.getMaxUtilizationPercent() + "%");
```

**Python equivalent:**

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

fluid = jneqsim.thermo.system.SystemSrkCPAstatoil(273.15 + 70.0, 65.0)
fluid.addComponent("methane", 0.70)
fluid.addComponent("ethane", 0.08)
fluid.addComponent("propane", 0.05)
fluid.addComponent("n-butane", 0.03)
fluid.addComponent("n-heptane", 0.08)
fluid.addComponent("water", 0.06)
fluid.setMixingRule(10)
fluid.setMultiPhaseCheck(True)
fluid.setMultiPhaseCheck(True)

feed = jneqsim.process.equipment.stream.Stream("feed", fluid)
feed.setFlowRate(200000.0, "kg/hr")

sep = jneqsim.process.equipment.separator.ThreePhaseSeparator("HP Sep", feed)
comp = jneqsim.process.equipment.compressor.Compressor("Export Comp",
    sep.getGasOutStream())
comp.setOutletPressure(150.0)
comp.setPolytropicEfficiency(0.78)
comp.setUsePolytropicCalc(True)

process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(sep)
process.add(comp)
process.run()

# Auto-size with 20% design margin
sep.autoSize(1.2)
comp.autoSize(1.2)
# Fixed-pressure power screening; synthetic auto-size maps are not installed data.
comp.getCompressorChart().setUseCompressorChart(False)
comp.setSolveSpeed(False)
comp.setUsePolytropicCalc(True)
for entry in comp.getCapacityConstraints().entrySet():
    entry.getValue().setEnabled(str(entry.getKey()) == "power")


print(f"Separator utilization: {sep.getMaxUtilizationPercent():.1f}%")
print(f"Compressor utilization: {comp.getMaxUtilizationPercent():.1f}%")
```

### 24.4.4 Reinitializing After Parameter Changes

If equipment parameters are changed after `autoSize()` (e.g., a different compressor speed or separator dimensions), the constraints must be reinitialized:

```java
comp.setMaximumSpeed(12000.0);  // Changed from auto-sized value
comp.reinitializeCapacityConstraints();
```

This recalculates all constraint design values and supplier functions to reflect the new equipment configuration.

---

## 24.5 Facility-Level Bottleneck Analysis

With capacity constraints defined on individual equipment, NeqSim provides system-level methods to identify bottlenecks and quantify spare capacity across the entire facility.

### 24.5.1 ProcessSystem Bottleneck Methods

The `ProcessSystem` class provides several methods for bottleneck analysis:

```java
BottleneckResult capacityResult = process.findBottleneck();
logger.info("Bottleneck {} utilization {}", capacityResult.getEquipmentName(), capacityResult.getUtilization());
Map<String, Double> utilizationSummary = process.getCapacityUtilizationSummary();
List<String> nearLimit = process.getEquipmentNearCapacityLimit();
boolean anyOverloaded = process.isAnyEquipmentOverloaded();
boolean anyHardViolation = process.isAnyHardLimitExceeded();
List<neqsim.process.equipment.capacity.CapacityConstrainedEquipment> constrained = process.getConstrainedEquipment();
```

### 24.5.2 Python Bottleneck Analysis

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# After building and running the process...
process.run()

# Find the bottleneck
bottleneck = process.getBottleneck()
if bottleneck is not None:
    print(f"Bottleneck: {bottleneck.getName()}")
    print(f"Utilization: {process.getBottleneckUtilization():.1%}")

# Detailed bottleneck result
result = process.findBottleneck()
print(f"Limiting constraint: {result.getConstraintName()}")

# Utilization summary for all equipment
summary = {str(name): float(percent)/100.0 for name, percent in
               process.getCapacityUtilizationSummary().items()}  # native map is percent
for name, util in summary.items():
    status = "GREEN" if util < 0.80 else ("YELLOW" if util < 0.95 else "RED")
    print(f"  {name}: {util:.1%}  [{status}]")

# Equipment near capacity limit
near_limit = process.getEquipmentNearCapacityLimit()
for eq in near_limit:
    print(f"  WARNING: {eq} near capacity limit")

# Safety check
if process.isAnyHardLimitExceeded():
    print("ALARM: Hard constraint violated!")
```

### 24.5.3 Bottleneck Shifting

An important concept is **bottleneck shifting**: when the primary bottleneck is resolved, a different equipment item becomes the new bottleneck. This leads to the **capacity staircase** pattern (Figure 24.1), where each debottlenecking step unlocks capacity up to the next constraint.

The bottleneck shift can be detected by running what-if studies with constraints selectively disabled:

```python
# What if we upgrade the compressor driver?
comp.setCapacityAnalysisEnabled(False)
process.run()
new_bottleneck = process.getBottleneck()
print(f"With compressor unconstrained, new bottleneck: {new_bottleneck.getName()}")
comp.setCapacityAnalysisEnabled(True)  # Restore
```

### 24.5.4 Utilization Report Generation

A standard facility utilization report presents all equipment with traffic-light color coding:

| Status | Utilization Range | Action |
|--------|------------------|--------|
| **GREEN** | $U < 80\%$ | Normal operation, adequate spare capacity |
| **YELLOW** | $80\% \leq U < 95\%$ | Approaching limit — monitor closely |
| **RED** | $U \geq 95\%$ | At or near capacity — action required |

```python
# Generate formatted utilization report
print("=" * 80)
print("FACILITY UTILIZATION REPORT")
print("=" * 80)
print(f"{'Equipment':<25} {'Util (%)':<12} {'Constraint':<20} {'Status'}")
print("-" * 80)

summary = {str(name): float(percent)/100.0 for name, percent in

               process.getCapacityUtilizationSummary().items()}  # native map is percent
for name in sorted(summary.keys(), key=lambda k: summary[k], reverse=True):
    util = summary[name]
    status = "GREEN" if util < 0.80 else ("YELLOW" if util < 0.95 else "RED")
    print(f"{name:<25} {util*100:<12.1f} {'—':<20} {status}")
```

---

## 24.6 The ProductionOptimizer API

The `ProductionOptimizer` is NeqSim's primary tool for finding the maximum feasible production rate (or optimizing any custom objective) subject to equipment capacity constraints. It automates the simulation-evaluate-search loop.

### 24.6.1 Architecture Overview

The optimizer follows a classic pattern:

1. **Configure** the optimization problem (bounds, tolerances, algorithm, constraints)
2. **Execute** the search, which iteratively adjusts the decision variable(s), runs the process model, evaluates constraints, and records history
3. **Return** an `OptimizationResult` containing the optimal operating point, bottleneck identification, convergence history, and diagnostic information

```text
OptimizationConfig  ─┐
                     │
  Objectives ────────┤
                     ├──►  ProductionOptimizer.optimize()  ──►  OptimizationResult
  Constraints ───────┤         ▲         │                         │
                     │         │         ▼                         ├── optimalRate
  ProcessSystem ─────┘   (iterate)  process.run()                 ├── bottleneck
                                    evaluateConstraints()          ├── iterationHistory
                                    computeScore()                 └── infeasibilityDiagnosis
```

### 24.6.2 OptimizationConfig Builder

The `OptimizationConfig` class uses a fluent builder pattern for configuration:

```java
OptimizationConfig config = new OptimizationConfig(50000.0, 300000.0)  // bounds
    .rateUnit("kg/hr")
    .tolerance(500.0)                          // convergence tolerance
    .maxIterations(40)                         // iteration limit
    .searchMode(SearchMode.BINARY_FEASIBILITY)
    .defaultUtilizationLimit(0.95)             // global 95% limit
    .utilizationLimitForType(Compressor.class, 0.90)  // 90% for compressors
    .utilizationLimitForName("HP Separator", 0.92)    // 92% for specific equipment
    .stagnationIterations(5)                   // detect stagnation after 5 iterations
    .maxCacheSize(500)                         // LRU simulation cache
    .enableCaching(true)
    .parallelEvaluations(true)                 // enable parallel evaluations
    .parallelThreads(4);                       // 4 threads
```

**Python equivalent:**

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer
OptimizationConfig = ProductionOptimizer.OptimizationConfig
SearchMode = ProductionOptimizer.SearchMode
Compressor = jneqsim.process.equipment.compressor.Compressor

config = OptimizationConfig(50000.0, 300000.0) \
    .rateUnit("kg/hr") \
    .tolerance(500.0) \
    .maxIterations(40) \
    .searchMode(SearchMode.GOLDEN_SECTION_SCORE) \
    .defaultUtilizationLimit(0.95) \
    .utilizationLimitForType(Compressor, 0.90) \
    .utilizationLimitForName("HP Separator", 0.92)
```

Table 24.2 summarizes all configuration parameters:

| Parameter | Method | Default | Description |
|-----------|--------|---------|-------------|
| Lower/upper bound | Constructor args | Required | Search range for decision variable |
| Rate unit | `rateUnit()` | `"kg/hr"` | Unit string for reporting |
| Tolerance | `tolerance()` | 1e-3 | Convergence tolerance in rate units |
| Max iterations | `maxIterations()` | 30 | Maximum optimizer iterations |
| Search mode | `searchMode()` | BINARY_FEASIBILITY | Algorithm selection |
| Default utilization limit | `defaultUtilizationLimit()` | 0.95 | Global equipment limit |
| Per-type limit | `utilizationLimitForType()` | — | Limit for equipment class |
| Per-name limit | `utilizationLimitForName()` | — | Limit for specific equipment |
| Stagnation iterations | `stagnationIterations()` | 5 | Detect lack of progress |
| Max cache size | `maxCacheSize()` | 1000 | LRU cache for simulation results |
| Enable caching | `enableCaching()` | true | Use simulation result cache |
| Initial guess | `initialGuess()` | null | Warm start point |
| Parallel evaluations | `parallelEvaluations()` | false | Multi-threaded evaluation |
| Parallel threads | `parallelThreads()` | Available CPUs | Thread count for parallelism |
| Reject invalid sims | `rejectInvalidSimulations()` | true | Reject NaN/negative results |
| Random seed | `randomSeed()` | 0 | Seed for stochastic algorithms |
| Swarm size | `swarmSize()` | 8 | PSO particle count |
| Pareto grid size | `paretoGridSize()` | 11 | Weight grid for Pareto front |

### 24.6.3 Configuration Validation

Before running optimization, validate the configuration to catch errors early:

```java
config.validate();
// This method returns void and throws IllegalArgumentException for an invalid configuration.
```

Common validation errors include:
- Lower bound ≥ upper bound
- Utilization limit outside [0, 1] range
- Negative tolerance or max iterations
- PSO swarm size < 2

### 24.6.4 Running the Optimizer

The basic optimization call takes a `ProcessSystem`, a feed stream, a configuration, and optional objectives and constraints:

```java
ProductionOptimizer optimizer = new ProductionOptimizer();

OptimizationResult result = optimizer.optimize(
    process,       // ProcessSystem with equipment constraints
    feed,          // Stream whose flow rate is the decision variable
    config,        // OptimizationConfig
    null,    // List<OptimizationObjective> (null for default throughput)
    null    // List<OptimizationConstraint> (null for equipment-only)
);
```

With no explicit objectives, score-based modes have zero objective score. Rate-only `BINARY_FEASIBILITY` still seeks the highest feasible rate; supply an objective for all score-based searches. When `constraints` is null, only equipment capacity constraints (from `CapacityConstrainedEquipment`) are checked.

**Complete Python example:**

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Build process model
fluid = jneqsim.thermo.system.SystemSrkCPAstatoil(273.15 + 70.0, 65.0)
fluid.addComponent("methane", 0.70)
fluid.addComponent("ethane", 0.08)
fluid.addComponent("propane", 0.05)
fluid.addComponent("n-butane", 0.03)
fluid.addComponent("n-heptane", 0.08)
fluid.addComponent("water", 0.06)
fluid.setMixingRule(10)
fluid.setMultiPhaseCheck(True)
fluid.setMultiPhaseCheck(True)

feed = jneqsim.process.equipment.stream.Stream("feed", fluid)
feed.setFlowRate(200000.0, "kg/hr")

sep = jneqsim.process.equipment.separator.ThreePhaseSeparator("HP Sep", feed)
comp = jneqsim.process.equipment.compressor.Compressor("Export Comp",
    sep.getGasOutStream())
comp.setOutletPressure(150.0)
comp.setPolytropicEfficiency(0.78)
comp.setUsePolytropicCalc(True)

process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(sep)
process.add(comp)
process.run()

# Auto-size and enable constraints
sep.autoSize(1.2)
comp.autoSize(1.2)
# Fixed-pressure power screening; synthetic auto-size maps are not installed data.
comp.getCompressorChart().setUseCompressorChart(False)
comp.setSolveSpeed(False)
comp.setUsePolytropicCalc(True)
for entry in comp.getCapacityConstraints().entrySet():
    entry.getValue().setEnabled(str(entry.getKey()) == "power")


# Configure optimizer
ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer
OptimizationConfig = ProductionOptimizer.OptimizationConfig
SearchMode = ProductionOptimizer.SearchMode

config = OptimizationConfig(50000.0, 400000.0) \
    .rateUnit("kg/hr") \
    .tolerance(500.0) \
    .maxIterations(30) \
    .searchMode(SearchMode.GOLDEN_SECTION_SCORE)

# Run optimization
optimizer = ProductionOptimizer()
result = optimizer.optimize(process, feed, config, None, None)

# Report results
print(f"Optimal rate:     {result.getOptimalRate():.0f} {result.getRateUnit()}")
print(f"Feasible:         {result.isFeasible()}")
print(f"Bottleneck:       {result.getBottleneck().getName()}")
print(f"Bottleneck util:  {result.getBottleneckUtilization():.1%}")
print(f"Iterations:       {result.getIterations()}")
```

---

## 24.7 Search Algorithms

NeqSim supports five optimization algorithms, each suited to different problem characteristics.

### 24.7.1 BINARY_FEASIBILITY

The simplest and fastest algorithm. It performs a binary search on the decision variable, checking only whether each candidate operating point is feasible (all equipment within utilization limits).

**Assumptions:**
- Feasibility is monotonically decreasing with increasing rate (i.e., higher rates are more constrained)
- Single decision variable only
- No objective function evaluation needed — it finds the maximum feasible rate

**Algorithm:**
1. Set $a = \text{lower bound}$, $b = \text{upper bound}$
2. Set $m = (a + b) / 2$
3. Evaluate feasibility at $m$
4. If feasible: $a = m$; if infeasible: $b = m$
5. Repeat until $b - a < \text{tolerance}$

**Convergence:** $O(\log_2((b-a)/\text{tolerance}))$ iterations.

**When to use:** Single-variable throughput maximization with monotonic behavior.

### 24.7.2 GOLDEN_SECTION_SCORE

Uses golden-section search on a composite score that combines the objective function with constraint penalty terms:

$$
S(x) = \sum_j w_j \cdot f_j(x) - \lambda \sum_i \max(0, g_i(x))
$$

where $f_j$ are objective functions with weights $w_j$, $g_i$ are constraint violations, and $\lambda$ is the penalty weight.

**Assumptions:**
- The score function is **unimodal** (single peak) over the search interval
- Single decision variable

**Convergence:** Reduces the interval by the golden ratio $\phi = (\sqrt{5} - 1)/2 \approx 0.618$ each iteration, giving $O(\log_{1/\phi}((b-a)/\text{tolerance}))$ iterations.

**When to use:** Non-monotonic single-variable optimization where the optimal point is in the interior of the feasible region (not at a constraint boundary).

### 24.7.3 NELDER_MEAD_SCORE

The Nelder-Mead simplex algorithm for multi-dimensional optimization. Does not require gradients; works well for 2–10 decision variables.

**Algorithm:**
1. Initialize a simplex of $n+1$ vertices in $n$-dimensional space
2. At each iteration, reflect the worst vertex through the centroid
3. If the reflected point is better, try expansion; if worse, try contraction
4. If contraction fails, shrink the simplex toward the best vertex
5. Terminate when the simplex is smaller than the tolerance

**When to use:** Multi-variable optimization (e.g., simultaneous optimization of separator pressure and compressor speed) with 2–10 decision variables.

### 24.7.4 PARTICLE_SWARM_SCORE

Particle swarm optimization (PSO) for global search. Good for non-convex problems with multiple local optima.

**Algorithm:**
1. Initialize a swarm of particles at random positions within the bounds
2. Each particle has a velocity and remembers its personal best position
3. At each iteration, update velocity using personal best and global best:

$$
v_i^{t+1} = w \cdot v_i^t + c_1 r_1 (p_i^{\text{best}} - x_i^t) + c_2 r_2 (g^{\text{best}} - x_i^t)
$$

4. Update position: $x_i^{t+1} = x_i^t + v_i^{t+1}$
5. Evaluate fitness and update personal/global bests

**Configuration:**
```java
config.swarmSize(20)           // Number of particles
    .inertiaWeight(0.7)        // Momentum factor w
    .cognitiveWeight(1.5)      // Personal best attraction c1
    .socialWeight(1.5)         // Global best attraction c2
    .randomSeed(42);           // Reproducibility
```

**When to use:** Non-convex problems with multiple local optima, global exploration before local refinement.

### 24.7.5 GRADIENT_DESCENT_SCORE

Steepest ascent with finite-difference gradients and Armijo backtracking line search.

**Algorithm:**
1. Start at the initial guess (or midpoint of bounds)
2. Compute gradient via central finite differences:

$$
\frac{\partial f}{\partial x_i} \approx \frac{f(x + h e_i) - f(x - h e_i)}{2h}
$$

3. Perform Armijo backtracking line search to find step size
4. Update: $x^{t+1} = x^t + \alpha \nabla f(x^t)$
5. Terminate when gradient magnitude < tolerance or max iterations reached

**When to use:** Smooth, concave maximization scores with several variables (5–20+). Fastest convergence near the optimum for well-conditioned problems.

### 24.7.6 Algorithm Comparison

Table 24.3 compares the five algorithms:

| Algorithm | Variables | Gradient-Free | Global guarantee | Convergence | Best For |
|-----------|-----------|--------------|--------|-------------|----------|
| BINARY_FEASIBILITY | 1 | Yes | N/A | Fast | Max feasible throughput |
| GOLDEN_SECTION_SCORE | 1 | Yes | No | Moderate | Unimodal single-variable |
| NELDER_MEAD_SCORE | 2–10 | Yes | No | Moderate | Multi-variable, derivative-free |
| PARTICLE_SWARM_SCORE | 1–20 | Yes | No | Slow | Multi-modal, non-convex |
| GRADIENT_DESCENT_SCORE | 5–20+ | No | No | Fast | Smooth, convex, many variables |

---

## 24.8 Optimization Results and Diagnostics

### 24.8.1 The OptimizationResult Object

The `OptimizationResult` returned by `optimize()` contains comprehensive information:

```java
// Optimal operating point
double optRate = result.getOptimalRate();
String unit = result.getRateUnit();
boolean feasible = result.isFeasible();
double score = result.getScore();

// Bottleneck identification
ProcessEquipmentInterface bottleneck = result.getBottleneck();
double bnUtil = result.getBottleneckUtilization();

// All equipment utilizations
List<UtilizationRecord> records = result.getUtilizationRecords();
for (UtilizationRecord rec : records) {
    logger.info(String.format("  %s: %.1f%% (limit: %.1f%%)%n",
        rec.getEquipmentName(),
        rec.getUtilization() * 100,
        rec.getUtilizationLimit() * 100));
}

// Decision variables (for multi-variable optimization)
Map<String, Double> decisions = result.getDecisionVariables();

// Objective values
Map<String, Double> objectives = result.getObjectiveValues();

// Constraint statuses
List<ConstraintStatus> statuses = result.getConstraintStatuses();
for (ConstraintStatus cs : statuses) {
    if (cs.violated()) {
        logger.info(String.format("  VIOLATED: %s (margin=%.4f)%n",
            cs.getName(), cs.getMargin()));
    }
}

// Convergence information
int iterations = result.getIterations();
List<IterationRecord> history = result.getIterationHistory();
```

### 24.8.2 Infeasibility Diagnosis

When the optimizer cannot find a feasible solution, `getInfeasibilityDiagnosis()` provides a structured diagnostic report:

```java
if (!result.isFeasible()) {
    logger.info(result.getInfeasibilityDiagnosis());
}
```

This produces output like:

```text
INFEASIBILITY DIAGNOSIS
=======================

Utilization Violations:
  - Export Compressor: 8.3% over limit (util=98.3%, limit=90.0%)
  - HP Separator: 2.1% over limit (util=97.1%, limit=95.0%)

Hard Constraint Violations:
  - compressor_power: margin=-0.0543 (Shaft power exceeds driver capacity)
```

### 24.8.3 Iteration History and Export

The optimizer records every iteration for analysis and visualization:

```python
# Export iteration history as JSON
json_str = result.exportIterationHistoryAsJson()
with open("optimization_history.json", "w") as f:
    f.write(json_str)

# Export as CSV for plotting
csv_str = result.exportIterationHistoryAsCsv()
with open("optimization_history.csv", "w") as f:
    f.write(csv_str)

# Detailed CSV with per-equipment utilization
detailed_csv = result.exportDetailedIterationHistoryAsCsv()
with open("optimization_detailed.csv", "w") as f:
    f.write(detailed_csv)
```

The CSV can be loaded into pandas for plotting convergence curves (Figure 24.2):

```python
from pathlib import Path
Path("figures").mkdir(parents=True, exist_ok=True)
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("optimization_history.csv")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

ax1.plot(df["Iteration"], df["Rate"], "b-o", label="Feed rate")
ax1.set_ylabel("Feed Rate (kg/hr)")
ax1.legend()

ax2.plot(df["Iteration"], df["BottleneckUtilization"] * 100, "r-s",
         label="Bottleneck utilization")
ax2.axhline(y=95, color="k", linestyle="--", label="Limit (95%)")
ax2.set_xlabel("Iteration")
ax2.set_ylabel("Utilization (%)")
ax2.legend()

plt.suptitle("Figure 24.2: Optimization Convergence History")
plt.tight_layout()
plt.savefig("figures/optimization_convergence.png", dpi=150)
```

### 24.8.4 JSON Summary Export

For integration with APIs and dashboards, the optimizer provides a lightweight JSON summary:

```java
OptimizationSummary optimizationSummary = optimizer.quickOptimize(process, feed, "kg/hr", null);
logger.info("Rate {} {}, feasible {}", optimizationSummary.getMaxRate(), optimizationSummary.getRateUnit(), optimizationSummary.isFeasible());
```

---

## 24.9 The ProcessOptimizationEngine (Level 2)

The `ProcessOptimizationEngine` is a higher-level unified engine that provides additional optimization capabilities beyond the basic `ProductionOptimizer`.

### 24.9.1 Engine Capabilities

```java
ProcessOptimizationEngine engine = new ProcessOptimizationEngine(process);
engine.setFeedStreamName("feed");
engine.setOutletStreamName("Export Comp");
ProcessOptimizationEngine.OptimizationResult engineResult = engine.findMaximumThroughput(65.0, 150.0, 50000.0, 300000.0);
ProcessOptimizationEngine.ConstraintReport report = engine.evaluateAllConstraints();
ProcessOptimizationEngine.SensitivityResult sens = engine.analyzeSensitivity(100000.0, 65.0, 150.0);
ProcessOptimizationEngine.LiftCurveData curve = engine.generateCapacityScreening(new double[]{50.0,65.0,80.0},
    new double[]{343.15}, 150.0, 50000.0, 300000.0);
logger.info("Capacity screening points {}", curve.getPoints().size());
```

### 24.9.2 Equipment Capacity Strategy Registry

The engine uses a pluggable strategy pattern for constraint evaluation. Each equipment type has a corresponding `EquipmentCapacityStrategy` that knows how to compute utilization:

```java
EquipmentCapacityStrategyRegistry registry = EquipmentCapacityStrategyRegistry.getInstance();
logger.info("Registered capacity strategies: {}", registry.getStrategyCount());
for (EquipmentCapacityStrategy strategy : registry.getAllStrategies()) {
    logger.info("Strategy {}", strategy.getClass().getSimpleName());
}
```

### 24.9.3 Constraint Report

The constraint report provides a comprehensive view of all equipment constraints:

```python
ProcessOptimizationEngine = jneqsim.process.util.optimizer.ProcessOptimizationEngine
engine = ProcessOptimizationEngine(process)
engine.setFeedStreamName("feed")
engine.setOutletStreamName("Export Comp")
report = engine.evaluateAllConstraints()
for equipment in report.getEquipmentStatuses():
    print(equipment.getEquipmentName(), equipment.getUtilization(), equipment.isWithinLimits())
    for constraint in equipment.getConstraints():
        print(constraint.getName(), constraint.getCurrentValue(), constraint.getUtilization())
```

### 24.9.4 Sensitivity Analysis

The `analyzeSensitivity()` method perturbs each constraint parameter by ±10% and measures the change in optimal throughput, revealing which constraints have the largest impact:

```python
sensitivity = engine.analyzeSensitivity(feed.getFlowRate("kg/hr"),
                                        feed.getPressure("bara"), 150.0)
print("Flow sensitivity:", sensitivity.getFlowGradient())
print("Tightest constraint:", sensitivity.getTightestConstraint())
```

This sensitivity identifies local production effects under the model assumptions. Investment ranking additionally requires upgrade costs, interactions and independently replayed feasible cases.

### 24.9.5 Lift Curve Generation

A **lift curve** (also called a system performance curve) shows the relationship between production rate and wellhead flowing pressure. This is essential for integrated reservoir-facility optimization:

```python
# Fixed-composition process capacity; temperatures are kelvin.
pressures = [40.0, 60.0, 80.0]
temperatures = [343.15]
curve = engine.generateCapacityScreening(pressures, temperatures,
                                        150.0, 50000.0, 300000.0)
for point in curve.getPoints():
    print(point.getInletPressure(), point.getTemperature(), point.getMaxFlowRate())

# Native NaN is a rejected search result; compare with a separate bounded grid.
# Grid maxima are only maxima among these sampled rates.
import numpy as np
capacity_grid = []
for point in curve.getPoints():
    accepted_rates = []
    for trial in np.linspace(50000.0, 300000.0, 21):
        feed.setPressure(float(point.getInletPressure()), "bara")
        feed.setTemperature(float(point.getTemperature()), "K")
        feed.setFlowRate(float(trial), "kg/hr")
        process.run()
        statuses = engine.evaluateAllConstraints().getEquipmentStatuses()
        if all(item.isWithinLimits() for item in statuses):
            accepted_rates.append(float(trial))
    assert accepted_rates, "No accepted grid point in this declared domain"
    capacity_grid.append({"pressure_bara": float(point.getInletPressure()),
        "native_candidate_kg_hr": float(point.getMaxFlowRate()),
        "grid_maximum_kg_hr": max(accepted_rates), "grid_spacing_kg_hr": 12500.0})
    print(capacity_grid[-1])
```

The table shows screened mass capacity at fixed composition and declared inlet conditions. It is not a bottomhole-to-wellhead hydraulic relation, and intersection with an IPR alone does not establish a coupled stable well solution.

### 24.9.6 Integrating with Reservoir Models

Reservoir VFP export requires a separately solved, complete BHP grid and consistent datum/phase-volume axes. Generic process-capacity screening cannot be directly exported as VFP:

```python
from pathlib import Path
rows = ["inlet_pressure_bara,temperature_K,max_mass_flow_kghr"]
for point in curve.getPoints():
    rows.append(f"{point.getInletPressure()},{point.getTemperature()},{point.getMaxFlowRate()}")
Path("process_capacity.csv").write_text("\n".join(rows), encoding="utf-8")
```

A complete coupling must additionally solve the well hydraulics and match each exchanged pressure and phase rate at the same physical boundary.

---

## 24.10 Custom Objectives and Constraints

### 24.10.1 Custom Objectives

The default optimizer maximizes feed flow rate, but custom objectives enable optimization of any process metric:

**Java:**

```java
OptimizationObjective throughput = new OptimizationObjective("throughput",
    proc -> ((StreamInterface) proc.getUnit("feed")).getFlowRate("kg/hr"), 1.0, ObjectiveType.MAXIMIZE);
OptimizationObjective minPower = new OptimizationObjective("power",
    proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 0.3, ObjectiveType.MINIMIZE);
List<OptimizationObjective> objectives = Arrays.asList(throughput, minPower);
```

**Python (using JPype interface):**

```python
from jpype import JImplements, JOverride

OptimizationObjective = ProductionOptimizer.OptimizationObjective
ObjectiveType = ProductionOptimizer.ObjectiveType

@JImplements("java.util.function.ToDoubleFunction")
class ThroughputEvaluator:
    @JOverride
    def applyAsDouble(self, proc):
        return proc.getUnit("outlet").getFlowRate("kg/hr")

throughput = OptimizationObjective("throughput",
    ThroughputEvaluator(), 1.0, ObjectiveType.MAXIMIZE)
```

### 24.10.2 Custom Process-Level Constraints

In addition to equipment capacity constraints, you can define process-level constraints:

```java
OptimizationConstraint maxPower = OptimizationConstraint.lessThan("compressor_power",
    proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 25.0,
    ProductionOptimizer.ConstraintSeverity.HARD, 100.0, "Declared power ceiling (MW)");
// Operating temperature is not a dew point; compute a separate property test for a dew-point specification.
OptimizationConstraint maxTemperature = OptimizationConstraint.lessThan("discharge_temperature",
    proc -> ((Compressor) proc.getUnit("Export Comp")).getOutletStream().getTemperature("C"), 180.0,
    ProductionOptimizer.ConstraintSeverity.SOFT, 10.0, "Illustrative discharge temperature preference");
List<OptimizationConstraint> constraints = Arrays.asList(maxPower, maxTemperature);
```

**Python:**

```python
from jpype import JImplements, JOverride

OptimizationConstraint = ProductionOptimizer.OptimizationConstraint
ConstraintSeverity = ProductionOptimizer.ConstraintSeverity

@JImplements("java.util.function.ToDoubleFunction")
class TotalPowerMetric:
    @JOverride
    def applyAsDouble(self, proc):
        return proc.getUnit("Export Comp").getPower() / 1e6

max_power = OptimizationConstraint.lessThan(
    "total_power", TotalPowerMetric(), 25.0,
    ConstraintSeverity.HARD, 100.0,
    "Total compressor power must not exceed 25 MW")

constraints = [max_power]
```

---

## 24.11 Multi-Objective Optimization

Real-world production optimization often involves competing objectives — maximize throughput while minimizing energy consumption, maximize oil rate while meeting gas export quality. NeqSim supports Pareto multi-objective optimization.

### 24.11.1 Pareto Front Generation

The `optimizePareto()` method generates a Pareto front by solving multiple single-objective problems with different weight combinations:

```java
List<OptimizationObjective> objectives = Arrays.asList(
    new OptimizationObjective("throughput",
        proc -> ((StreamInterface) proc.getUnit("feed")).getFlowRate("kg/hr"),
        1.0, ObjectiveType.MAXIMIZE),
    new OptimizationObjective("power",
        proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"),
        1.0, ObjectiveType.MINIMIZE)
);

OptimizationConfig config = new OptimizationConfig(50000.0, 300000.0)
    .searchMode(SearchMode.GOLDEN_SECTION_SCORE)
    .paretoGridSize(5).maxIterations(20);  // 15 weight combinations

ParetoResult pareto = optimizer.optimizePareto(
    process, feed, config, objectives, constraints);

// Access Pareto front points
List<ParetoPoint> front = pareto.getParetoFront();
for (ParetoPoint point : front) {
    logger.info(String.format("Rate=%.0f kg/hr, Power=%.1f MW, Feasible=%s%n",
        point.getObjectiveValues().get("throughput"),
        point.getObjectiveValues().get("power"),
        point.isFeasible()));
}

// Get the knee point (best compromise)
// Select a preferred Pareto point using an explicit decision rule; no knee-point helper exists in this revision.
```

### 24.11.2 Pareto Front Visualization

```python
from pathlib import Path
import matplotlib.pyplot as plt
Path("figures").mkdir(exist_ok=True)
Objective = ProductionOptimizer.OptimizationObjective
Direction = ProductionOptimizer.ObjectiveType
objectives = jpype.java.util.ArrayList([
    Objective("throughput", lambda proc: proc.getUnit("feed").getFlowRate("kg/hr"),
              1.0, Direction.MAXIMIZE),
    Objective("power", lambda proc: proc.getUnit("Export Comp").getPower("MW"),
              1.0, Direction.MINIMIZE)])
pareto_config = (OptimizationConfig(50000.0, 300000.0).rateUnit("kg/hr")
    .searchMode(SearchMode.GOLDEN_SECTION_SCORE).maxIterations(20).paretoGridSize(5))
pareto = optimizer.optimizePareto(process, feed, pareto_config, objectives, None)
rates, powers = [], []
for point in pareto.getParetoFront():
    values = point.getObjectiveValues()
    rates.append(float(values["throughput"]))
    powers.append(float(values["power"]))
plt.figure(figsize=(7, 4))
plt.scatter(rates, powers)
plt.xlabel("Mass throughput (kg/hr)")
plt.ylabel("Compressor power (MW)")
plt.title("Non-dominated points for the declared synthetic model")
plt.grid(True, alpha=0.3)
plt.savefig("figures/pareto_front.png", dpi=150, bbox_inches="tight")
```

### 24.11.3 Weighted-Sum Scalarization

The Pareto method uses weighted-sum scalarization to convert the multi-objective problem into a series of single-objective problems:

$$
\text{maximize} \quad S(x) = \sum_{j=1}^{k} w_j \cdot \hat{f}_j(x)
$$

where $\hat{f}_j$ is the normalized objective value (scaled to [0, 1]) and $w_j$ is the weight for objective $j$. The Pareto grid generates $N$ weight vectors $\{w_1, \ldots, w_N\}$ with $\sum_j w_j = 1$.

**Limitation:** Weighted-sum scalarization cannot find points on non-convex regions of the Pareto front. For non-convex problems, consider the $\epsilon$-constraint method (available via external optimizer integration).

### 24.11.4 Interpreting the Pareto Front

The Pareto front provides several key insights:

1. **Trade-off quantification**: The slope of the Pareto front at any point gives the "exchange rate" between objectives. For example, if increasing throughput by 10,000 kg/hr requires an additional 2 MW of compression power, the exchange rate is 2 MW per 10,000 kg/hr, or 0.2 kWh/kg.

2. **Knee point**: A knee, if present under a stated normalization, is one possible compromise — a point where further improvement in one objective requires a disproportionately large sacrifice in the other. This is often the most practical operating point.

3. **Extreme solutions**: The endpoints of the Pareto front show the best achievable value for each individual objective.

4. **Decision support**: By presenting the Pareto front to decision-makers, they can select the preferred trade-off based on current priorities (e.g., production is more valuable in summer when demand is high, energy efficiency is more important when gas prices are high).

### 24.11.5 Three-Objective Example

For problems with three or more objectives, the Pareto front becomes a surface or hyper-surface:

```java
// Explicit separator outlets avoid invented export equipment names.
List<OptimizationObjective> threeObjectives = Arrays.asList(
    new OptimizationObjective("oil_rate", proc -> ((ThreePhaseSeparator) proc.getUnit("HP Sep")).getOilOutStream().getFlowRate("Sm3/day"), 1.0, ObjectiveType.MAXIMIZE),
    new OptimizationObjective("gas_rate", proc -> ((ThreePhaseSeparator) proc.getUnit("HP Sep")).getGasOutStream().getFlowRate("MSm3/day"), 1.0, ObjectiveType.MAXIMIZE),
    new OptimizationObjective("power", proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 1.0, ObjectiveType.MINIMIZE));
config.paretoGridSize(3).maxIterations(15);
ParetoResult threeObjectiveResult = optimizer.optimizePareto(process, feed, config, threeObjectives, constraints);
```

With three objectives, the number of Pareto evaluations grows as $O(N^{k-1})$ where $k$ is the number of objectives and $N$ is the grid size. For 3 objectives with grid size 21, this is $21^2 = 441$ optimizations — significant but tractable.

---

## 24.12 Scenario Comparison

Production optimization often involves comparing alternative operating scenarios — different separator pressures, compressor configurations, or well routing strategies.

### 24.12.1 ScenarioRequest and ScenarioKpi

```java
List<ScenarioRequest> scenarios = new ArrayList<ScenarioRequest>();
for (double pressure : new double[]{50.0, 65.0, 80.0}) {
    ProcessSystem scenarioProcess = process.copy();
    StreamInterface scenarioFeed = (StreamInterface) scenarioProcess.getUnit("feed");
    scenarioFeed.setPressure(pressure, "bara");
    OptimizationConfig scenarioConfig = new OptimizationConfig(50000.0, 300000.0)
        .rateUnit("kg/hr").maxIterations(20).searchMode(SearchMode.BINARY_FEASIBILITY);
    scenarios.add(new ScenarioRequest("Suction " + pressure, scenarioProcess, scenarioFeed, scenarioConfig, null, null));
}
for (ScenarioResult scenario : optimizer.optimizeScenarios(scenarios)) {
    logger.info("{}: {} kg/hr, feasible {}", scenario.getName(),
        scenario.getResult().getOptimalRate(), scenario.getResult().isFeasible());
}
```

**Python:**

```python
# Simplified scenario comparison using a loop
scenarios = [
    {"name": "Baseline", "sep_pressure": 65.0},
    {"name": "High P",   "sep_pressure": 80.0},
    {"name": "Low P",    "sep_pressure": 50.0},
]

results = []
for scenario in scenarios:
    # Rebuild process at new conditions
    feed.setPressure(scenario["sep_pressure"], "bara")
    process.run()

    gas_rate = sep.getGasOutStream().getFlowRate("MSm3/day")
    power = comp.getPower() / 1e6
    bn_util = process.getBottleneckUtilization()

    results.append({
        "Scenario": scenario["name"],
        "Sep P (bara)": scenario["sep_pressure"],
        "Gas Rate (MSm3/d)": f"{gas_rate:.2f}",
        "Power (MW)": f"{power:.1f}",
        "Bottleneck Util (%)": f"{bn_util*100:.1f}",
    })

# Print comparison table
import pandas as pd
df = pd.DataFrame(results)
print(df.to_string(index=False))
```

---

## 24.13 Compressor Curves and Optimization

Compressor performance curves are essential for realistic optimization because they define the relationship between flow, head, efficiency, and speed. Without curves, the optimizer cannot evaluate surge margin or stonewall proximity, and the power calculation reverts to a fixed-efficiency model that overestimates the operating range.

A centrifugal compressor map typically presents polytropic head $H_p$ versus actual inlet volumetric flow $Q_{act}$ at several speed lines. Each speed line has a surge point (minimum stable flow), a design point, and a stonewall (choke) limit. The compressor must operate between these boundaries:

$$
Q_{surge}(N) \leq Q_{act} \leq Q_{stonewall}(N)
$$

where $N$ is the shaft speed (rpm). The surge margin is commonly defined as:

$$
SM = \frac{Q_{operating}-Q_{surge}}{Q_{surge}} \geq SM_{min}
$$

with $SM_{min}$ specified by the vendor/control design on this denominator basis; a universal 10–15% API requirement is not established here. Operating below this margin risks surge — a violent flow reversal that can damage impellers and seals.

### 24.13.1 CompressorChartGenerator

NeqSim can auto-generate compressor performance curves from a design point using fan laws (affinity laws) and typical stage characteristics:

```java
// Generate screening curves from an already solved design point.
comp.getCompressorChart().setUseCompressorChart(false);
comp.setOutletPressure(150.0);
process.run();
CompressorChartGenerator chartGen = new CompressorChartGenerator(comp);
chartGen.generateCompressorChart("midpoint");
comp.setMaximumSpeed(comp.getSpeed() * 1.15);
// Vendor performance data and units must replace these synthetic design curves.
```

The generator creates a multi-speed map covering 70-105% of design speed, with each speed line containing surge, design, and stonewall points. The affinity laws approximate dynamically similar points with unchanged geometry and inlet density; compressible Mach/Reynolds and gas-property effects limit their application:

$$
\frac{Q_2}{Q_1} = \frac{N_2}{N_1}, \quad \frac{H_{p,2}}{H_{p,1}} = \left(\frac{N_2}{N_1}\right)^2, \quad \frac{W_2}{W_1} = \left(\frac{N_2}{N_1}\right)^3
$$

### 24.13.2 AutoSize with Compressor Curves

When `autoSize()` is called on a compressor with `useCompressorChart(true)`, it automatically:

1. Generates performance curves at the current operating point
2. Creates speed, power, and surge margin constraints
3. Sets the design values with the specified margin factor

```java
comp.getCompressorChart().setUseCompressorChart(true);
comp.autoSize(1.2);
comp.getCompressorChart().setUseCompressorChart(false);
comp.setSolveSpeed(false);
comp.setUsePolytropicCalc(true);
for (Map.Entry<String,CapacityConstraint> entry : comp.getCapacityConstraints().entrySet()) { entry.getValue().setEnabled(entry.getKey().equals("power")); }

// After autoSize, the compressor has these constraints:
Map<String, CapacityConstraint> chartConstraints = comp.getCapacityConstraints();
// "speed" -> designValue = currentSpeed * 1.2
// "power" -> designValue = currentPower * 1.2
// "surgeMargin" -> designValue = 10% (minimum surge margin)
```

### 24.13.3 Reinitializing After Chart Changes

If the compressor chart or operating conditions change significantly (e.g., different gas composition due to field maturation, or a speed change due to driver re-rating), the constraints must be re-initialized:

```java
// Change the maximum speed
comp.setMaximumSpeed(12000.0);

// Must reinitialize constraints to reflect new speed limit
comp.reinitializeCapacityConstraints();

// Now optimization will respect the new speed envelope
```

This is particularly important when the optimizer is being used for life-of-field studies where gas composition changes over time. At fixed pressure ratio and inlet temperature, increasing molecular weight generally reduces specific compression head in the constant-property expression; declining suction pressure increases the pressure ratio. These competing effects and the corrected map must be evaluated together. The optimizer detects this via the surge margin constraint.

### 24.13.4 Realistic Search Bounds

When optimizing with compressor curves, the search bounds should respect the physical operating envelope:

```python
# Query chart-derived constraint margins; curve units belong to the chart basis.
for name, constraint in comp.getCapacityConstraints().items():
    print(name, constraint.getCurrentValue(), constraint.getUnit(), constraint.getUtilization())
# Use a declared mass-flow envelope for this synthetic screening study.
config = (OptimizationConfig(50000.0, 300000.0).rateUnit("kg/hr")
          .searchMode(SearchMode.BINARY_FEASIBILITY).maxIterations(25))
```

### 24.13.5 Anti-Surge Control in Optimization

In dynamic simulation contexts, the optimizer must account for anti-surge controller (ASC) behavior. If the ASC recycles gas to prevent surge, this recycled gas consumes compressor capacity that is then unavailable for production. The effective throughput is:

$$
Q_{production} = Q_{total} - Q_{recycle}
$$

When optimizing a facility with compressor recycle, the optimizer should target $Q_{production}$ rather than total compressor throughput. The NeqSim `Recycle` equipment element models this relationship, and the capacity constraint system accounts for the recycled fraction when computing utilization.

---

## 24.14 Multi-Variable Optimization

Many real-world optimization problems have multiple decision variables that must be optimized simultaneously. A typical offshore platform may have 3-8 decision variables: separator pressures (HP, LP, test), compressor speeds, valve positions, and recycle rates. These variables are coupled — changing the HP separator pressure affects downstream compressor load, which affects available power for other services.

The curse of dimensionality means that exhaustive grid search becomes impractical quickly. A grid with 10 points per variable and 5 variables requires $10^5 = 100{,}000$ process simulations, each taking 1-10 seconds. Intelligent search algorithms (Nelder-Mead, PSO, gradient descent) typically converge in 50-500 evaluations, reducing computation time from days to minutes.

### 24.14.1 ManipulatedVariable Definition

Each decision variable is defined with bounds, units, and an applicator function that maps the variable value to the process model:

```java
List<ManipulatedVariable> variables = Arrays.asList(
    new ManipulatedVariable("flowRate", 50000, 300000, "kg/hr",
        (proc, val) -> {
            ((StreamInterface) proc.getUnit("feed")).setFlowRate(val, "kg/hr");
        }),
    new ManipulatedVariable("sepPressure", 40, 90, "bara",
        (proc, val) -> {
            ((StreamInterface) proc.getUnit("feed")).setPressure(val, "bara");
        }),
    new ManipulatedVariable("compOutP", 120, 180, "bara",
        (proc, val) -> {
            ((Compressor) proc.getUnit("Export Comp")).setOutletPressure(val);
        })
);

OptimizationConfig config = new OptimizationConfig(0, 1)  // bounds ignored for multi-var
    .searchMode(SearchMode.NELDER_MEAD_SCORE)
    .maxIterations(30);

OptimizationResult result = optimizer.optimize(
    process, variables, config, objectives, constraints);

Map<String, Double> optimal = result.getDecisionVariables();
logger.info("Optimal flow: " + optimal.get("flowRate") + " kg/hr");
logger.info("Optimal sep P: " + optimal.get("sepPressure") + " bara");
logger.info("Optimal comp P: " + optimal.get("compOutP") + " bara");
```

The bounds on each variable should reflect physically meaningful ranges. For separator pressure, the lower bound is typically set by downstream compression capacity and the upper bound by the wellhead flowing pressure minus pipeline friction losses. For compressor outlet pressure, the lower bound is the export pipeline operating pressure and the upper bound is the mechanical design pressure of the discharge piping.

### 24.14.2 Choosing the Right Algorithm

For multi-variable problems, algorithm selection depends on the problem dimension, smoothness, and whether local optima are expected:

| Number of Variables | Recommended Algorithm | Rationale |
|--------------------|-----------------------|-----------|
| 1 | BINARY_FEASIBILITY or GOLDEN_SECTION | Fast, exact for monotonic/unimodal |
| 2–5 | NELDER_MEAD_SCORE | Gradient-free, handles moderate dimensions |
| 5–10 | NELDER_MEAD_SCORE or GRADIENT_DESCENT_SCORE | NM for rough terrain, GD for smooth |
| 10–20 | GRADIENT_DESCENT_SCORE | Requires smoothness, but scales well |
| Non-convex (any dim) | PARTICLE_SWARM_SCORE | Global search, avoids local optima |

For production optimization, the objective function landscape is typically smooth (small parameter changes produce small output changes) but may have multiple local optima when equipment switching occurs (e.g., a standby compressor kicking in at a threshold flow rate). When such discontinuities are expected, PARTICLE_SWARM_SCORE is preferred despite its higher computational cost.

---

## 24.15 Advanced Features

### 24.15.1 Stagnation Detection

The optimizer detects when no progress is being made:

```java
config.stagnationIterations(5);  // Terminate if no improvement in 5 iterations
```

When stagnation is detected, the optimizer returns the best solution found so far rather than continuing to waste evaluation budget.

### 24.15.2 Warm Start

Provide an initial guess to accelerate convergence, especially useful when re-optimizing after small changes:

```java
config.initialGuess(new double[]{180000.0});  // Start near previous optimal
```

### 24.15.3 LRU Cache

The optimizer caches simulation results to avoid redundant evaluations:

```java
config.enableCaching(true);
config.maxCacheSize(500);  // Cache up to 500 simulation results
```

This is especially valuable for PSO and Nelder-Mead where particles/vertices may revisit similar regions.

### 24.15.4 Parallel Evaluations

For PSO and other population-based algorithms, evaluations can run in parallel:

```java
config.parallelEvaluations(true);
config.parallelThreads(8);  // Use 8 threads
```

**Warning:** Parallel evaluations require that the `ProcessSystem` can be safely cloned and run in separate threads. This is generally true for NeqSim process models but may not work with custom equipment that holds shared mutable state.

### 24.15.5 Reproducibility

For consistent results across runs:

```java
config.randomSeed(42);       // Fixed seed
config.useFixedSeed(true);   // Ensure reproducibility
```

For diverse exploration in parallel runs:

```java
config.useFixedSeed(false);  // Time-based seed for each run
```

### 24.15.6 Constraint Presets

Convenience presets enable selected configured checks; they do not certify industry-standard values or installed equipment ratings:

```java
config.defaultUtilizationLimit(0.60);
// Equipment names are explicit identities in this process.
config.utilizationLimitForName("Export Comp", 0.85);
```

Ambient derating must be supplied from the actual driver map. A preset name does not create that map or qualify a seasonal power allowance.

### 24.15.7 Optimization History and Auditing

The optimizer maintains a complete history of every evaluation for post-analysis and auditing:

```java
OptimizationResult result = optimizer.optimize(process, feed, config, objectives, constraints);
for (IterationRecord entry : result.getIterationHistory()) {
    logger.info("Rate {}, score {}, feasible {}", entry.getRate(), entry.getScore(), entry.isFeasible());
}
String csv = result.exportIterationHistoryAsCsv();
String json = result.exportIterationHistoryAsJson();
```

The history is invaluable for debugging convergence issues, identifying search space features (multiple local optima, flat regions), and demonstrating to regulators that the optimization was conducted rigorously.

---

## 24.16 External Optimizer Integration

For problems that require specialized optimization algorithms not available in NeqSim, the `ProcessSimulationEvaluator` provides a bridge to external solvers.

### 24.16.1 ProcessSimulationEvaluator

This class wraps a NeqSim `ProcessSystem` as a callable function for external optimizers:

```java
ProcessSimulationEvaluator evaluator = new ProcessSimulationEvaluator(process);
evaluator.addParameterWithSetter("flow", (proc, value) -> ((StreamInterface) proc.getUnit("feed")).setFlowRate(value, "kg/hr"), 50000.0, 300000.0, "kg/hr");
evaluator.addObjective("throughput", proc -> ((StreamInterface) proc.getUnit("feed")).getFlowRate("kg/hr"), ProcessSimulationEvaluator.ObjectiveDefinition.Direction.MAXIMIZE);
evaluator.addConstraintUpperBound("power", proc -> ((Compressor) proc.getUnit("Export Comp")).getPower("MW"), 25.0);
ProcessSimulationEvaluator.EvaluationResult evaluation = evaluator.evaluate(new double[]{200000.0});
logger.info("Objective {}, feasible {}, converged {}", evaluation.getObjective(), evaluation.isFeasible(), evaluation.isSimulationConverged());
```

### 24.16.2 Integration with SciPy

For advanced optimization algorithms not available in NeqSim (interior point, SLSQP, trust-region), SciPy provides a comprehensive collection:

```python
hp_sep = sep
from scipy.optimize import minimize, differential_evolution
import numpy as np
import jpype
jneqsim = jpype.JPackage("neqsim")

# Build NeqSim process model
# ... (as shown in earlier examples)

# ─── Approach 1: Local optimizer (L-BFGS-B) ───
def neqsim_objective(x):
    """Negative throughput (SciPy minimizes)."""
    feed.setFlowRate(float(x[0]), "kg/hr")
    process.run()

    # Check constraints
    if process.isAnyHardLimitExceeded():
        return 1e10  # Infeasible penalty

    # Return negative throughput (minimizing)
    return -feed.getFlowRate("kg/hr")

x0 = np.array([200000.0])
bounds = [(50000, 400000)]
result = minimize(neqsim_objective, x0, method='L-BFGS-B', bounds=bounds,
                  options={'maxiter': 50, 'ftol': 1e-6})

print(f"L-BFGS-B candidate objective: {-result.fun:.0f} kg/hr")
print(f"Iterations: {result.nit}, Function evaluations: {result.nfev}")

# ─── Approach 2: Global optimizer (Differential Evolution) ───
result_de = differential_evolution(neqsim_objective, bounds,
                                    maxiter=30, seed=42, tol=0.01)

print(f"DE candidate objective: {-result_de.fun:.0f} kg/hr")

# ─── Approach 3: Multi-variable with SLSQP ───
def multi_objective(x):
    """Minimize negative oil rate (maximize oil) subject to constraints."""
    flow, sep_p = x
    feed.setFlowRate(float(flow), "kg/hr")
    feed.setPressure(float(sep_p), "bara")
    process.run()

    if process.isAnyHardLimitExceeded():
        return 1e10

    oil_rate = hp_sep.getOilOutStream().getFlowRate("Sm3/day")
    return -oil_rate

def power_constraint(x):
    """Power must be below 25 MW (inequality: g(x) >= 0)."""
    flow, sep_p = x
    feed.setFlowRate(float(flow), "kg/hr")
    feed.setPressure(float(sep_p), "bara")
    process.run()
    return 25.0 - comp.getPower() / 1e6  # Must be >= 0

x0 = np.array([200000.0, 65.0])
bounds = [(50000, 400000), (40, 90)]
constraints = {'type': 'ineq', 'fun': power_constraint}

result_slsqp = minimize(multi_objective, x0, method='SLSQP',
                         bounds=bounds, constraints=constraints)

print(f"SLSQP candidate: flow={result_slsqp.x[0]:.0f} kg/hr, "
      f"sep_P={result_slsqp.x[1]:.1f} bara")

# Reapply and solve the selected SLSQP candidate before reading equipment outputs.
multi_objective(result_slsqp.x)

# Optimizer termination and physical feasibility are separate acceptance gates.
scipy_candidates = []
for name, answer, objective in (("L-BFGS-B", result, neqsim_objective),
                                ("DE", result_de, neqsim_objective),
                                ("SLSQP", result_slsqp, multi_objective)):
    objective_value = float(objective(answer.x))
    candidate_power = float(comp.getPower("MW"))
    feasible = (not process.isAnyHardLimitExceeded() and
                (name != "SLSQP" or candidate_power <= 25.000001))
    accepted = bool(answer.success and feasible)
    scipy_candidates.append({"method": name, "success": bool(answer.success),
                             "feasible": feasible, "accepted": accepted,
                             "flow_kg_hr": float(feed.getFlowRate("kg/hr")),
                             "power_MW": candidate_power,
                             "objective": objective_value})
    print(name, "accepted candidate" if accepted else "rejected candidate",
          "(local/grid-independent global optimality is not established)")
```

### 24.16.3 Integration with NLopt

For users who prefer NLopt's extensive algorithm collection:

**Execution scope:** This integration pattern optional NLopt package is required.

```python pattern: optional NLopt package is required
import nlopt
import numpy as np

def nlopt_objective(x, grad):
    """NLopt objective function (maximizing throughput)."""
    feed.setFlowRate(float(x[0]), "kg/hr")
    process.run()

    if process.isAnyHardLimitExceeded():
        return -1e10  # NLopt maximizes

    return feed.getFlowRate("kg/hr")

opt = nlopt.opt(nlopt.GN_DIRECT_L, 1)  # DIRECT algorithm, 1 variable
opt.set_lower_bounds([50000.0])
opt.set_upper_bounds([400000.0])
opt.set_max_objective(nlopt_objective)
opt.set_maxeval(100)
opt.set_xtol_rel(1e-4)

x_opt = opt.optimize([200000.0])
print(f"NLopt DIRECT optimal: {x_opt[0]:.0f} kg/hr")
```

### 24.16.4 SQP Optimizer

For constrained nonlinear programming within NeqSim's Java framework, the `SQPoptimizer` provides a sequential quadratic programming solver:

```java
SQPoptimizer sqp = new SQPoptimizer(1);
// Dimensionless throughput variable; every constraint evaluation solves the process.
sqp.setObjectiveFunction(x -> -x[0]);
sqp.addInequalityConstraint(x -> {
    feed.setFlowRate(x[0] * 100000.0, "kg/hr");
    process.run();
    return (25.0 - comp.getPower("MW")) / 25.0;
});
sqp.setVariableBounds(new double[]{0.5}, new double[]{3.0});
sqp.setInitialPoint(new double[]{1.0});
SQPoptimizer.OptimizationResult sqpResult = sqp.solve();
feed.setFlowRate(sqpResult.getOptimalPoint()[0] * 100000.0, "kg/hr");
process.run();
logger.info("SQP converged {}, final power {} MW", sqpResult.isConverged(), comp.getPower("MW"));
```

---

## 24.17 Separator Pressure Optimization

Separator pressure is one of the most impactful optimization variables because it simultaneously affects:
- Gas compression ratio (and therefore compressor power)
- Flash gas volume
- Oil vapor pressure
- Water separation efficiency
- Downstream equipment duties

### 24.17.1 The Trade-Off

At high separator pressure:
- Less flash gas is released → smaller gas compressor → less power
- Higher oil vapor pressure → may exceed pipeline specification
- Water settling must be evaluated from density difference, viscosity, droplet distribution and residence time; its direction is not determined by pressure alone

At low separator pressure:
- More gas released → more sales gas but more compression power
- Lower oil vapor pressure → better oil quality
- The resulting gas composition determines heating value; the direction must be calculated on a common reference basis
- More liquid shrinkage → less oil volume

The optimal separator pressure balances these competing effects to maximize total production value (oil + gas revenue minus energy cost).

### 24.17.2 Pressure Optimization Example

```python
hp_sep = sep
from pathlib import Path
Path("figures").mkdir(parents=True, exist_ok=True)
import jpype
jneqsim = jpype.JPackage("neqsim")
import numpy as np
import matplotlib.pyplot as plt

# Build process model
# ... (as shown earlier)

# Sweep separator pressure
pressures = np.arange(30, 100, 2.5)  # bara
oil_rates = []
gas_rates = []
comp_powers = []
oil_process_pressures = []

for p in pressures:
    feed.setPressure(float(p), "bara")
    process.run()

    oil_rates.append(hp_sep.getOilOutStream().getFlowRate("Sm3/day"))
    gas_rates.append(hp_sep.getGasOutStream().getFlowRate("MSm3/day"))
    comp_powers.append(comp.getPower() / 1e6)

    # Operating liquid pressure; this is not Reid vapor pressure.
    oil_fluid = hp_sep.getOilOutStream().getFluid()
    oil_process_pressures.append(oil_fluid.getPressure("bara"))

# Calculate total revenue
oil_price = 70.0  # USD/bbl
gas_price = 8.0   # USD/MMBtu
power_cost = 0.05  # USD/kWh

revenues = []
for i in range(len(pressures)):
    oil_rev = oil_rates[i] * 6.29 * oil_price / 1000  # kUSD/day
    gas_rev = gas_rates[i] * 1.0e6 * 38.0 / 1055.05585262 * gas_price / 1000   # kUSD/day; illustrative GCV=38 MJ/Sm3
    energy_cost = comp_powers[i] * 1000 * 24 * power_cost / 1000  # kUSD/day
    net = oil_rev + gas_rev - energy_cost
    revenues.append(net)

# Find optimal pressure
idx_opt = np.argmax(revenues)
print(f"Optimal separator pressure: {pressures[idx_opt]:.1f} bara")
print(f"At optimum: Oil={oil_rates[idx_opt]:.0f} Sm3/d, "
      f"Gas={gas_rates[idx_opt]:.2f} MSm3/d, "
      f"Power={comp_powers[idx_opt]:.1f} MW")
print(f"Net revenue: {revenues[idx_opt]:.0f} kUSD/day")

# Plot
fig, axes = plt.subplots(2, 2, figsize=(12, 9))

axes[0,0].plot(pressures, oil_rates, 'b-', linewidth=2)
axes[0,0].axvline(x=pressures[idx_opt], color='r', linestyle='--')
axes[0,0].set_xlabel("Separator Pressure (bara)")
axes[0,0].set_ylabel("Oil Rate (Sm3/day)")
axes[0,0].set_title("Oil Rate vs Separator Pressure")
axes[0,0].grid(True, alpha=0.3)

axes[0,1].plot(pressures, gas_rates, 'g-', linewidth=2)
axes[0,1].axvline(x=pressures[idx_opt], color='r', linestyle='--')
axes[0,1].set_xlabel("Separator Pressure (bara)")
axes[0,1].set_ylabel("Gas Rate (MSm3/day)")
axes[0,1].set_title("Gas Rate vs Separator Pressure")
axes[0,1].grid(True, alpha=0.3)

axes[1,0].plot(pressures, comp_powers, 'm-', linewidth=2)
axes[1,0].axvline(x=pressures[idx_opt], color='r', linestyle='--')
axes[1,0].set_xlabel("Separator Pressure (bara)")
axes[1,0].set_ylabel("Compressor Power (MW)")
axes[1,0].set_title("Compressor Power vs Separator Pressure")
axes[1,0].grid(True, alpha=0.3)

axes[1,1].plot(pressures, revenues, 'k-', linewidth=2)
axes[1,1].axvline(x=pressures[idx_opt], color='r', linestyle='--',
                   label=f'Optimal: {pressures[idx_opt]:.0f} bara')
axes[1,1].set_xlabel("Separator Pressure (bara)")
axes[1,1].set_ylabel("Net Revenue (kUSD/day)")
axes[1,1].set_title("Net Revenue vs Separator Pressure")
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.suptitle("Figure 24.6: Separator Pressure Optimization", fontsize=14)
plt.tight_layout()
plt.savefig("figures/sep_pressure_optimization.png", dpi=150)
```

---

## 24.18 Data Reconciliation

Before optimization, it is often necessary to reconcile measured plant data with the process model to ensure the model is representative. A model that doesn't match current plant conditions will produce misleading optimization recommendations.

### 24.18.1 The Data Reconciliation Problem

Data reconciliation adjusts measured values to satisfy conservation equations (mass, energy, momentum) while minimizing the deviation from measurements, weighted by measurement uncertainty:

$$
\min_{x} \quad \sum_{i} \left(\frac{x_i - y_i}{\sigma_i}\right)^2
$$

subject to:

$$
f(x) = 0 \quad \text{(conservation equations)}
$$

where $x_i$ are the reconciled values, $y_i$ are the measured values, and $\sigma_i$ are the measurement standard deviations. This is a constrained weighted least-squares problem.

### 24.18.2 Steady-State Detection

Steady-state RTO requires sufficiently settled data for its model. Dynamic optimization can treat transients explicitly when the dynamic model and constraints are qualified; transient data are not suitable inputs to an unmodified steady-state reconciliation.

The `SteadyStateDetector` determines whether the process is at steady state before running optimization:

```java
import neqsim.process.util.reconciliation.*;
SteadyStateDetector detector = new SteadyStateDetector();
SteadyStateVariable pressure = detector.addVariable("pressure").setUnit("bara");
for (int sample = 0; sample < 60; sample++) { pressure.addValue(65.0); }
SteadyStateResult steady = detector.evaluate();
logger.info("Synthetic constant-pressure window at steady state: {}", steady.isAtSteadyState());
```

The current implementation computes window variance, the successive-difference variance ratio and a regression slope in units per sample. Independent stationary noise gives a ratio near one; drift may give a small ratio. It does not establish an absence of oscillations with a general autocorrelation test. Set limits from signal noise and the process settling time, and use a declared regular sampling interval. A coefficient of variation is unsuitable for Celsius temperature or a near-zero mean because it depends on the arbitrary zero of the scale; use an absolute temperature variability limit instead. Chapter 32 checks the native ratio against an independent calculation, while Chapter 30 demonstrates explicit drift, oscillation and missing-data rejection.

### 24.18.3 DataReconciliationEngine

The `DataReconciliationEngine` adjusts model parameters to match plant measurements:

```java
import neqsim.process.util.reconciliation.*;
DataReconciliationEngine reconciler = new DataReconciliationEngine();
// Synthetic readings with standard-deviation uncertainties, all kg/hr.
reconciler.addVariable(new ReconciliationVariable("feed",200000.0,2000.0));
reconciler.addVariable(new ReconciliationVariable("gas",150000.0,1500.0));
reconciler.addVariable(new ReconciliationVariable("oil",48000.0,1000.0));
reconciler.addVariable(new ReconciliationVariable("water",5000.0,500.0));
reconciler.addConstraint(new double[]{1.0,-1.0,-1.0,-1.0},"Mass balance");
ReconciliationResult reconciliation = reconciler.reconcile();
if (!reconciliation.isConverged()) { throw new IllegalStateException(reconciliation.getErrorMessage()); }
logger.info("Chi-square {}, global test passed {}",reconciliation.getChiSquareStatistic(),reconciliation.isGlobalTestPassed());
logger.info("Mass-balance residuals kg/hr: {}",Arrays.toString(reconciliation.getConstraintResidualsAfter()));
```

### 24.18.4 Gross Error Detection

If reconciliation fails the chi-square test, a gross measurement error may be present. The identification process uses the **measurement test** (MT) method:

1. Remove each measurement in turn
2. Re-run reconciliation without the suspect measurement
3. If the chi-square test passes, the removed measurement is likely the gross error

```java
for (ReconciliationVariable suspect : reconciliation.getGrossErrors()) {
    logger.warn("Suspect {} normalized residual {}",suspect.getName(),suspect.getNormalizedResidual());
}
```

### 24.18.5 Model Tuning After Reconciliation

After reconciliation, adjust the process model to match the reconciled values before optimization:

**Execution scope:** This integration pattern requires historian reconciliation and scheduled-run infrastructure.

```python pattern: requires historian reconciliation and scheduled-run infrastructure
# Get reconciled values
rec_P = reconciler.getReconciledValue("feed_pressure")
rec_T = reconciler.getReconciledValue("feed_temperature")
rec_flow = reconciler.getReconciledValue("gas_flow")

# Update model
feed.setPressure(rec_P, "bara")
feed.setTemperature(rec_T, "C")
feed.setFlowRate(rec_flow, "kg/hr")
process.run()

# Now optimize with reconciled model
result = optimizer.optimize(process, feed, config, None, None)
```

---

## 24.19 Real-Time Optimization Loop

### 24.19.1 Architecture

A real-time optimization (RTO) loop continuously updates the process model with plant data and re-optimizes at regular intervals:

```text
Plant Data ──► Steady-State Detection ──► Data Reconciliation ──► Model Update
                                                                      │
                                                                      ▼
           ◄── Implement Set Points ◄── Optimization ◄── Constraint Check
```

### 24.19.2 Implementation

**Execution scope:** This integration pattern requires historian reconciliation and scheduled-run infrastructure.

```python pattern: requires historian reconciliation and scheduled-run infrastructure
import jpype
jneqsim = jpype.JPackage("neqsim")
import time

ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer
OptimizationConfig = ProductionOptimizer.OptimizationConfig
SearchMode = ProductionOptimizer.SearchMode

# Build and configure process model (done once)
# ... (as shown in earlier examples)

optimizer = ProductionOptimizer()
config = OptimizationConfig(50000.0, 400000.0) \
    .rateUnit("kg/hr") \
    .tolerance(500.0) \
    .searchMode(SearchMode.BINARY_FEASIBILITY) \
    .maxIterations(20)

# Optimization loop (runs every 15 minutes in production)
optimization_interval = 900  # seconds
last_optimal_rate = None

while True:
    try:
        # Step 1: Read current plant data
        current_pressure = read_from_historian("PT-100")  # bara
        current_temperature = read_from_historian("TT-100")  # C
        current_flow = read_from_historian("FT-100")  # kg/hr

        # Step 2: Update model with current conditions
        feed.setPressure(current_pressure, "bara")
        feed.setTemperature(current_temperature, "C")
        feed.setFlowRate(current_flow, "kg/hr")
        process.run()

        # Step 3: Check constraints at current operating point
        if process.isAnyHardLimitExceeded():
            print("ALARM: Hard constraint violated at current conditions!")
            # Reduce production immediately

        # Step 4: Re-optimize
        result = optimizer.optimize(process, feed, config, None, None)

        if result.isFeasible():
            new_optimal = result.getOptimalRate()
            if last_optimal_rate is not None:
                change_pct = abs(new_optimal - last_optimal_rate) / last_optimal_rate * 100
                if change_pct > 2.0:  # Only report significant changes
                    print(f"New optimal rate: {new_optimal:.0f} kg/hr "
                          f"({change_pct:+.1f}% change)")
                    print(f"Bottleneck: {result.getBottleneck().getName()} "
                          f"at {result.getBottleneckUtilization():.1%}")
            last_optimal_rate = new_optimal
        else:
            print("No feasible solution found at current conditions")
            print(result.getInfeasibilityDiagnosis())

        # Step 5: Wait for next cycle
        time.sleep(optimization_interval)

    except Exception as e:
        print(f"Optimization error: {e}")
        time.sleep(60)  # Retry after 1 minute
```

### 24.19.3 Integration with Plant Historian

NeqSim can integrate with OSIsoft PI or Aspen IP.21 historians for real-time data:

**Execution scope:** requires installed historian tagreader client and authenticated site data.

```python pattern: requires installed historian tagreader client and authenticated site data
# Using neqsim tagreader (see Chapter 21 for full details)
import jpype
jneqsim = jpype.JPackage("neqsim")

# Configure plant data source
tagreader = jneqsim.util.database.tagreader.TAGReader()
tagreader.setDataSource("PI")
tagreader.setServerName("pi-server.plant.local")

# Read current values
current_P = tagreader.readTag("HP-SEP-PT-001", "bara")
current_T = tagreader.readTag("HP-SEP-TT-001", "C")
current_F = tagreader.readTag("FEED-FT-001", "kg/hr")
```

---

## 24.20 Worked Example: Complete Optimization Workflow

This section presents a complete worked example of a gas-condensate facility optimization, from model building through optimization and result analysis.

### 24.20.1 Problem Description

A gas-condensate production platform processes 250,000 kg/hr of wellstream through:
- HP Separator (V-100): Horizontal, 3-phase
- Export Compressor (K-100): Centrifugal with performance curves
- Gas Cooler (E-100): Shell-and-tube
- Export Pipeline: 20-inch, 80 km to shore

**Objective:** Find the maximum production rate subject to all equipment constraints, assuming equipment was designed with 20% margin above the current operating point.

### 24.20.2 Full Python Implementation

```python
from pathlib import Path
Path("figures").mkdir(parents=True, exist_ok=True)
import jpype
jneqsim = jpype.JPackage("neqsim")
import json

# ─── Step 1: Build process model ───
fluid = jneqsim.thermo.system.SystemSrkCPAstatoil(273.15 + 75.0, 65.0)
fluid.addComponent("nitrogen", 0.008)
fluid.addComponent("CO2", 0.025)
fluid.addComponent("methane", 0.580)
fluid.addComponent("ethane", 0.075)
fluid.addComponent("propane", 0.042)
fluid.addComponent("i-butane", 0.015)
fluid.addComponent("n-butane", 0.022)
fluid.addComponent("i-pentane", 0.012)
fluid.addComponent("n-pentane", 0.010)
fluid.addComponent("n-hexane", 0.014)
fluid.addComponent("n-heptane", 0.018)
fluid.addComponent("n-octane", 0.009)
fluid.addComponent("water", 0.170)
fluid.setMixingRule(10)
fluid.setMultiPhaseCheck(True)

feed = jneqsim.process.equipment.stream.Stream("Wellstream", fluid)
feed.setFlowRate(250000.0, "kg/hr")
feed.setTemperature(75.0, "C")
feed.setPressure(65.0, "bara")

hp_sep = jneqsim.process.equipment.separator.ThreePhaseSeparator(
    "HP Separator V-100", feed)

comp = jneqsim.process.equipment.compressor.Compressor(
    "Export Compressor K-100", hp_sep.getGasOutStream())
comp.setOutletPressure(150.0)
comp.setPolytropicEfficiency(0.77)
comp.setUsePolytropicCalc(True)

cooler = jneqsim.process.equipment.heatexchanger.Heater(
    "Gas Cooler E-100", comp.getOutletStream())
cooler.setOutTemperature(273.15 + 40.0)

export_ko = jneqsim.process.equipment.separator.Separator(
    "Export cooler knockout", cooler.getOutletStream())
pipeline = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills(
    "Export Pipeline", export_ko.getGasOutStream())
pipeline.setPipeWallRoughness(5e-5)
pipeline.setLength(80000.0)  # m: declared 80 km horizontal export line
pipeline.setDiameter(0.508)
pipeline.setAngle(0.0)
pipeline.setNumberOfIncrements(10)

process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(hp_sep)
process.add(comp)
process.add(cooler)
process.add(export_ko)
process.add(pipeline)

# A fresh knockout avoids reuse of tiny cached phase withdrawals during sweeps.
def run_facility():
    global export_ko
    export_ko = jneqsim.process.equipment.separator.Separator(
        "Export cooler knockout", cooler.getOutletStream())
    process.replaceUnit("Export cooler knockout", export_ko)
    pipeline.setInletStream(export_ko.getGasOutStream())
    process.run()

run_facility()

# Check axial discretization at the declared lower/base/upper sweep rates.
# This is a mesh check, not an independent validation of Beggs-Brill physics.
pipeline_mesh = []
for check_rate in (125000.0, 250000.0, 350000.0):
    feed.setFlowRate(check_rate, "kg/hr")
    states = []
    for increments in (10, 20):
        pipeline.setNumberOfIncrements(increments)
        run_facility()
        states.append((float(pipeline.getOutletStream().getPressure("bara")),
                       float(pipeline.getOutletStream().getTemperature("K"))))
    pressure_error = abs(states[0][0]-states[1][0])
    temperature_error = abs(states[0][1]-states[1][1])
    assert pressure_error < 0.2 and temperature_error < 0.1, states
    pipeline_mesh.append({"rate_kg_hr": check_rate,
                          "pressure_difference_bar": pressure_error,
                          "temperature_difference_K": temperature_error})
pipeline.setNumberOfIncrements(10)
feed.setFlowRate(250000.0, "kg/hr")
run_facility()
print("Step 1: Process model built and mesh checked", pipeline_mesh)
print(f"  Feed rate: {feed.getFlowRate('kg/hr'):.0f} kg/hr")
print(f"  Compressor power: {comp.getPower()/1e6:.2f} MW")

# ─── Step 2: Auto-size equipment ───
hp_sep.autoSize(1.2)
comp.autoSize(1.2)
# Fixed-pressure power screening; synthetic auto-size maps are not installed data.
comp.getCompressorChart().setUseCompressorChart(False)
comp.setSolveSpeed(False)
comp.setUsePolytropicCalc(True)
for entry in comp.getCapacityConstraints().entrySet():
    entry.getValue().setEnabled(str(entry.getKey()) == "power")

# Retain the declared 0.508 m installed bore; velocity-only autoSize is not hydraulic sizing.
pipeline.initMechanicalDesign()

print("\nStep 2: Equipment auto-sized with 20% margin")
summary = {str(name): float(percent)/100.0 for name, percent in
               process.getCapacityUtilizationSummary().items()}  # native map is percent
for name, util in summary.items():
    print(f"  {name}: {util*100:.1f}%")

# ─── Step 3: Configure and run optimizer ───
ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer
OptimizationConfig = ProductionOptimizer.OptimizationConfig
SearchMode = ProductionOptimizer.SearchMode

config = OptimizationConfig(100000.0, 500000.0) \
    .rateUnit("kg/hr") \
    .tolerance(1000.0) \
    .maxIterations(30) \
    .searchMode(SearchMode.GOLDEN_SECTION_SCORE) \
    .defaultUtilizationLimit(0.95)

optimizer = ProductionOptimizer()
result = optimizer.optimize(process, feed, config, None, None)

# ─── Step 4: Report results ───
print("\n" + "=" * 60)
print("OPTIMIZATION RESULTS")
print("=" * 60)
print(f"Returned feed rate:  {result.getOptimalRate():.0f} kg/hr")
print(f"Rate unit:          {result.getRateUnit()}")
print(f"Feasible:           {result.isFeasible()}")
print(f"Score:              {result.getScore():.4f}")
print(f"Iterations:         {result.getIterations()}")

if result.getBottleneck() is not None:
    print(f"Bottleneck:         {result.getBottleneck().getName()}")
    print(f"Bottleneck util:    {result.getBottleneckUtilization():.1%}")

print("\nEquipment Utilization at Optimum:")
for rec in result.getUtilizationRecords():
    over = " [OVER LIMIT]" if rec.getUtilization() > rec.getUtilizationLimit() else ""
    print(f"  {rec.getEquipmentName()}: {rec.getUtilization()*100:.1f}% "
          f"(limit: {rec.getUtilizationLimit()*100:.0f}%){over}")

if not result.isFeasible():
    print("\nInfeasibility Diagnosis:")
    print(result.getInfeasibilityDiagnosis())

# ─── Step 5: Export history ───
with open("optimization_history.json", "w") as f:
    f.write(result.exportIterationHistoryAsJson())

print("\nOptimization history exported to optimization_history.json")

# ─── Step 6: Generate production rate sweep ───
print("\n" + "=" * 60)
print("PRODUCTION RATE SWEEP")
print("=" * 60)

factors = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]
base_flow = 250000.0

print(f"{'Factor':<8} {'Rate (kg/hr)':<14} {'Comp Power (MW)':<18} {'Bottleneck':<20} {'Util (%)'}")
print("-" * 75)

sweep_data = {"factors": [], "rates": [], "powers": [], "utils": []}

for factor in factors:
    flow = base_flow * factor
    feed.setFlowRate(flow, "kg/hr")
    run_facility()

    bn = process.getBottleneck()
    bn_name = bn.getName() if bn else "None"
    bn_util = process.getBottleneckUtilization()
    power_mw = comp.getPower() / 1e6

    sweep_data["factors"].append(factor)
    sweep_data["rates"].append(flow)
    sweep_data["powers"].append(power_mw)
    sweep_data["utils"].append(bn_util)

    status = "OK" if bn_util < 0.95 else "LIMIT" if bn_util < 1.0 else "EXCEEDED"
    print(f"{factor:<8.1f} {flow:<14.0f} {power_mw:<18.2f} {bn_name:<20} {bn_util*100:.1f} [{status}]")

# ─── Step 7: Visualization ───
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Utilization vs production factor
axes[0,0].plot(sweep_data["factors"], [u*100 for u in sweep_data["utils"]],
               'b-o', linewidth=2)
axes[0,0].axhline(y=95, color='r', linestyle='--', label='95% limit')
axes[0,0].set_xlabel("Production Factor")
axes[0,0].set_ylabel("Bottleneck Utilization (%)")
axes[0,0].set_title("Bottleneck Utilization vs Production Rate")
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Plot 2: Compressor power vs production factor
axes[0,1].plot(sweep_data["factors"], sweep_data["powers"], 'g-s', linewidth=2)
axes[0,1].set_xlabel("Production Factor")
axes[0,1].set_ylabel("Compressor Power (MW)")
axes[0,1].set_title("Compressor Power vs Production Rate")
axes[0,1].grid(True, alpha=0.3)

# Plot 3: All equipment utilizations at optimum
if result.isFeasible():
    equip_names = []
    equip_utils = []
    equip_limits = []
    for rec in result.getUtilizationRecords():
        equip_names.append(rec.getEquipmentName())
        equip_utils.append(rec.getUtilization() * 100)
        equip_limits.append(rec.getUtilizationLimit() * 100)

    x = range(len(equip_names))
    axes[1,0].bar(x, equip_utils, color='steelblue', label='Utilization')
    axes[1,0].plot(x, equip_limits, 'rv--', label='Limit')
    axes[1,0].set_xticks(x)
    axes[1,0].set_xticklabels(equip_names, rotation=30, ha='right')
    axes[1,0].set_ylabel("Utilization (%)")
    axes[1,0].set_title("Equipment Utilization at Optimum")
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3, axis='y')

# Plot 4: Convergence history
axes[1,1].text(0.5, 0.5, "See optimization_history.json\nfor detailed convergence data",
               ha='center', va='center', transform=axes[1,1].transAxes, fontsize=12)
axes[1,1].set_title("Convergence History")

plt.suptitle("Figure 24.5: Gas-Condensate Facility Optimization Results",
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig("figures/facility_optimization_results.png", dpi=150, bbox_inches='tight')
print("\nFigure saved to figures/facility_optimization_results.png")
```

---

## 24.21 Gas Lift Optimization

Gas lift optimization is one of the most common and impactful production optimization applications. It involves distributing a limited supply of lift gas among multiple wells to maximize total oil production.

### 24.21.1 The Gas Lift Allocation Problem

The gas lift optimization problem is:

$$
\max_{q_1, \ldots, q_N} \quad \sum_{i=1}^{N} Q_{\text{oil},i}(q_i)
$$

subject to:

$$
\sum_{i=1}^{N} q_i \leq Q_{\text{gas,available}}
$$

$$
q_i^{\min} \leq q_i \leq q_i^{\max} \quad \forall i
$$

where $Q_{\text{oil},i}(q_i)$ is the oil production from well $i$ as a function of gas lift injection rate $q_i$, and $Q_{\text{gas,available}}$ is the total available lift gas.

The key insight is that each well has a **gas lift performance curve** (GLPC) — the relationship between injection rate and oil production. These curves are typically concave: the marginal benefit of additional lift gas decreases with increasing injection rate.

### 24.21.2 Equal-Slope Allocation

For concave GLPCs, the optimal allocation follows the **equal-slope criterion**: at the optimum, the marginal oil production per unit of lift gas is equal for all active wells:

$$
\frac{dQ_{\text{oil},i}}{dq_i} = \frac{dQ_{\text{oil},j}}{dq_j} \quad \forall \text{active wells } i, j
$$

This is a direct consequence of the Karush-Kuhn-Tucker (KKT) conditions for the Lagrangian formulation.

### 24.21.3 Implementation with NeqSim

**Execution scope:** This integration pattern requires calibrated gas-lift well models and allocation callbacks.

```python pattern: requires calibrated gas-lift well models and allocation callbacks
import jpype
jneqsim = jpype.JPackage("neqsim")
import numpy as np

# Define wells with gas lift performance curves
# Each well: (reservoir P, PI, GOR, WC, depth)
wells = [
    {"name": "Well-A", "Pres": 250, "PI": 15.0, "GOR": 120, "WC": 0.30},
    {"name": "Well-B", "Pres": 220, "PI": 12.0, "GOR": 150, "WC": 0.45},
    {"name": "Well-C", "Pres": 280, "PI": 18.0, "GOR": 100, "WC": 0.20},
    {"name": "Well-D", "Pres": 200, "PI": 10.0, "GOR": 180, "WC": 0.55},
]

# Total available lift gas
total_gas = 2.0  # MSm3/day

# Compute GLPC for each well using NeqSim pipeline model
def compute_glpc(well_params, gas_rates):
    """Compute oil rate vs gas lift rate for a single well."""
    oil_rates = []
    for gl_rate in gas_rates:
        # Build wellbore model with gas lift
        fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 80.0, well_params["Pres"])
        fluid.addComponent("methane", 0.75)
        fluid.addComponent("n-heptane", 0.20)
        fluid.addComponent("water", 0.05)
        fluid.setMixingRule("classic")
        fluid.setMultiPhaseCheck(True)

        # ... (configure wellbore model with gas lift)
        # This is simplified — a full implementation would use
        # PipeBeggsAndBrills with gas lift injection point

        oil_rates.append(compute_oil_rate(well_params, gl_rate))
    return np.array(oil_rates)

# Optimize allocation using equal-slope method
gas_rates = np.linspace(0, 1.0, 50)  # MSm3/day per well

# Compute GLPCs
glpcs = {}
for well in wells:
    glpcs[well["name"]] = compute_glpc(well, gas_rates)

# Iterative equal-slope allocation
# (In practice, use ProductionOptimizer with multi-variable config)
```

### 24.21.4 Network-Level Gas Lift Optimization with ProcessOptimizationEngine

For more complex networks where wells interact through manifold back-pressure:

**Execution scope:** This integration pattern requires calibrated gas-lift well models and allocation callbacks.

```python pattern: requires calibrated gas-lift well models and allocation callbacks
# Build full network model in NeqSim
# ... (wells → manifold → separator → compressor)

# Configure multi-variable optimization
variables = []
for well in wells:
    variables.append(
        ManipulatedVariable(f"GL_{well['name']}", 0.0, 0.8, "MSm3/day",
            lambda proc, val, w=well: set_gas_lift(proc, w, val))
    )

# Add constraint: total gas lift <= available
total_gl_constraint = OptimizationConstraint.lessThan(
    "total_gas_lift",
    lambda proc: sum_gas_lift(proc),
    total_gas,
    ConstraintSeverity.HARD, 100.0,
    "Total gas lift must not exceed available supply")

config = OptimizationConfig(0, 1) \
    .searchMode(SearchMode.NELDER_MEAD_SCORE) \
    .maxIterations(100)

result = optimizer.optimize(process, variables, config,
    [oil_objective], [total_gl_constraint])

# Report optimal allocation
optimal = result.getDecisionVariables()
for well in wells:
    key = f"GL_{well['name']}"
    print(f"  {well['name']}: {optimal[key]:.3f} MSm3/day")
```

---

## 24.22 Batch Studies and Parameter Sweeps

For systematic exploration of operating conditions, NeqSim supports batch studies that automate parameter sweeps.

### 24.22.1 Production Rate Sweep

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import json

# Sweep feed rate from 50% to 140% of design
base_flow = 250000.0
factors = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]

sweep_results = []
for factor in factors:
    flow = base_flow * factor
    feed.setFlowRate(flow, "kg/hr")
    run_facility()

    summary = {str(unit.getName()): float(unit.getMaxUtilization())
               for unit in process.getUnitOperations()}
    bn = process.getBottleneck()

    sweep_results.append({
        "factor": factor,
        "flow_kghr": flow,
        "bottleneck": bn.getName() if bn else "None",
        "bottleneck_util": process.getBottleneckUtilization(),
        "utilizations": dict(summary),
    })

# Print results table
print(f"{'Factor':<8} {'Flow (kg/hr)':<14} {'Bottleneck':<25} {'Util (%)':<10}")
print("-" * 60)
for r in sweep_results:
    print(f"{r['factor']:<8.1f} {r['flow_kghr']:<14.0f} "
          f"{r['bottleneck']:<25} {r['bottleneck_util']*100:<10.1f}")
```

### 24.22.2 Multi-Parameter Sensitivity

```python
import itertools
import math
import numpy as np

# Independently test each attempted state, including rejected native flash points.
def facility_balance_residuals():
    residuals = {"mass_relative": 0.0, "component_relative": 0.0,
                 "energy_relative": 0.0, "domain_valid": True}
    for unit in process.getUnitOperations():
        if str(unit.getClass().getSimpleName()) == "Stream":
            continue
        ins, outs = list(unit.getInletStreams()), list(unit.getOutletStreams())
        if not ins or not outs:
            continue
        for stream in ins + outs:
            stream.getFluid().initProperties()
            residuals["domain_valid"] &= (stream.getFlowRate("kg/hr") >= 0 and
                stream.getPressure("bara") > 0 and stream.getTemperature("K") > 0)
        mi = sum(float(st.getFlowRate("kg/hr")) for st in ins)
        mo = sum(float(st.getFlowRate("kg/hr")) for st in outs)
        residuals["mass_relative"] = max(residuals["mass_relative"], abs(mo-mi)/mi)
        names = {str(st.getFluid().getComponent(k).getComponentName())
                 for st in ins+outs for k in range(st.getFluid().getNumberOfComponents())}
        scale = sum(float(st.getFluid().getTotalNumberOfMoles()) for st in ins)
        for name in names:
            ni = sum(float(st.getFluid().getComponent(name).getNumberOfmoles()) for st in ins)
            no = sum(float(st.getFluid().getComponent(name).getNumberOfmoles()) for st in outs)
            residuals["component_relative"] = max(residuals["component_relative"], abs(no-ni)/scale)
        kind = str(unit.getClass().getSimpleName())
        if kind == "Compressor":
            residuals["domain_valid"] &= ins[0].getFluid().getNumberOfPhases() == 1
        # Pipeline thermal boundary is not independently checked by this budget.
        if kind == "PipeBeggsAndBrills":
            continue
        work = float(unit.getPower()) if kind == "Compressor" else float(unit.getDuty()) if kind in ("Heater", "Cooler") else 0.0
        hin = sum(float(st.getFluid().getEnthalpy()) for st in ins)
        hout = sum(float(st.getFluid().getEnthalpy()) for st in outs)
        err = abs(hout-hin-work)/max(abs(hin), abs(hout), abs(work), 1.0)
        residuals["energy_relative"] = max(residuals["energy_relative"], err)
    return residuals

sep_pressures = [50.0, 60.0, 70.0, 80.0]
comp_pressures = [120.0, 140.0, 160.0, 180.0]
results_matrix = []
for rate, sep_p, comp_p in itertools.product(
        [250000.0, 350000.0], sep_pressures, comp_pressures):
    feed.setFlowRate(rate, "kg/hr")
    feed.setPressure(sep_p, "bara")
    comp.setOutletPressure(comp_p)
    run_facility()
    residuals = facility_balance_residuals()
    accepted = (residuals["domain_valid"] and residuals["mass_relative"] < 1e-6 and
                residuals["component_relative"] < 1e-6 and residuals["energy_relative"] < 1e-5)
    deficit = (float(cooler.getOutletStream().getFlowRate("kg/hr")) -
               sum(float(st.getFlowRate("kg/hr")) for st in export_ko.getOutletStreams()))
    results_matrix.append({"rate_kg_hr": rate, "sep_P": sep_p, "comp_P": comp_p,
        "power_MW": float(comp.getPower("MW")), "accepted": bool(accepted),
        "knockout_mass_deficit_kg_hr": deficit, "residuals": residuals})
    print(results_matrix[-1])

assert len(results_matrix) == 32
rejected = [row for row in results_matrix if not row["accepted"]]
assert len(rejected) == 2
assert all(row["sep_P"] == 80.0 and row["comp_P"] == 140.0 for row in rejected)
assert abs(rejected[0]["knockout_mass_deficit_kg_hr"] - 0.407180316) < 1e-4
best_by_rate = {}
for rate in (250000.0, 350000.0):
    accepted_rows = [r for r in results_matrix if r["accepted"] and r["rate_kg_hr"] == rate]
    best_by_rate[rate] = min(accepted_rows, key=lambda row: row["power_MW"])
best = best_by_rate[250000.0]  # compare pressures at a common production rate
feed.setFlowRate(best["rate_kg_hr"], "kg/hr")
feed.setPressure(best["sep_P"], "bara")
comp.setOutletPressure(best["comp_P"])
run_facility()
assert abs(comp.getPower("MW")-best["power_MW"]) < 1e-5
assert facility_balance_residuals()["mass_relative"] < 1e-6
Path("ch24_pressure_grid_acceptance.json").write_text(json.dumps(results_matrix, indent=2))
print("Lowest-power accepted sampled pressure settings at each fixed rate:", best_by_rate)
print("Rejected states remain in the record; no complete-grid or global optimum is claimed.")
```

![Figure 24.1: Acceptance and compressor power for all32 attempted pressure states](figures/ch24_pressure_grid_acceptance.png)

**Discussion (Figure 24.1).** Thirty states satisfy the declared1ppm mass/component and10ppm enthalpy acceptance checks. The80bara feed/140bara discharge combination fails the material check at both rates: the native phase extraction loses0.407180kg/h at250t/h and0.570052kg/h at350t/h, or2.345ppm. Fresh separators and repeated equilibrium flashes reproduce the deficit. These are rejected numerical states; the gray cells do not imply a physical operating prohibition. Here acceptance means numerical material/energy consistency. Equipment-capacity and export-pressure requirements are separate gates, so the lowest-power sampled state is a sensitivity result, not an approved operating setpoint. Compare power at a common feed rate and use only accepted states for the sampled selection. Resolve the trace-phase extraction discrepancy before using either rejected point for design or claiming an optimum across the entire grid.


---

## 24.23 Debottlenecking Studies

Debottlenecking is the systematic process of identifying and removing capacity constraints to increase production. NeqSim's constraint framework enables structured debottlenecking analysis.

### 24.23.1 The Debottlenecking Staircase

When the primary bottleneck is resolved, a different equipment item becomes the new bottleneck. This creates a **capacity staircase** (Figure 24.4):

```text
Production Rate
     ▲
     │              ┌──────── Equipment C limit
     │         ┌────┘
     │    ┌────┘          Equipment B limit
     │────┘
     │              Equipment A limit (current bottleneck)
     └──────────────────────────────►
            Debottlenecking Steps
```

Each step represents the resolution of one constraint and the throughput gain until the next constraint becomes active.

### 24.23.2 Systematic Debottlenecking with NeqSim

```python
config = (OptimizationConfig(50000.0, 300000.0).rateUnit("kg/hr")
          .searchMode(SearchMode.BINARY_FEASIBILITY).maxIterations(25))
optimizer = ProductionOptimizer()
import jpype
jneqsim = jpype.JPackage("neqsim")

# Step 1: Find current maximum and bottleneck
result_baseline = optimizer.optimize(process, feed, config, None, None)
print(f"Current max: {result_baseline.getOptimalRate():.0f} kg/hr")
print(f"Bottleneck: {result_baseline.getBottleneck().getName()}")

# Step 2: Systematically remove each bottleneck and find the next
debottleneck_results = []
disabled_equipment = []

for step in range(5):  # Up to 5 debottlenecking steps
    # Get current bottleneck
    bn = process.getBottleneck()
    if bn is None:
        break

    bn_name = bn.getName()
    bn_util = process.getBottleneckUtilization()

    # Record the bottleneck
    current_max = optimizer.optimize(process, feed, config, None, None)

    debottleneck_results.append({
        "step": step,
        "bottleneck": bn_name,
        "utilization": bn_util,
        "max_rate": current_max.getOptimalRate(),
    })

    # Disable a check for a diagnostic screen; this does not model a physical upgrade.
    bn.setCapacityAnalysisEnabled(False)
    disabled_equipment.append(bn)

    # Re-optimize to find the next bottleneck
    run_facility()

# Step 3: Print debottlenecking staircase
print("\nConstraint-mask sensitivity (no physical upgrade credit):")
print(f"{'Step':<6} {'Bottleneck':<25} {'Max Rate (kg/hr)':<18} {'Gain (%)'}")
print("-" * 70)
prev_rate = 0
for r in debottleneck_results:
    gain = ((r["max_rate"] - prev_rate) / prev_rate * 100) if prev_rate > 0 else 0
    print(f"{r['step']:<6} {r['bottleneck']:<25} {r['max_rate']:<18.0f} {gain:.1f}")
    prev_rate = r["max_rate"]

# Step 4: Restore all constraints
for eq in disabled_equipment:
    eq.setCapacityAnalysisEnabled(True)
```

### 24.23.3 Cost-Benefit Analysis of Debottlenecking Options

For each debottlenecking step, estimate the cost and revenue impact:

```python
# These assumed saleable oil gains are independent of the constraint-mask screen.
# No physical production increase or capital-project benefit is inferred above.
economic_screens = []
for name, capex, assumed_oil_gain in [
    ("Separator internals", 15.0, 1000.0),
    ("Compressor driver", 45.0, 1500.0),
    ("Cooler area", 8.0, 500.0),
    ("Parallel pipeline", 250.0, 3000.0),
]:
    gross = assumed_oil_gain * 70.0 * 350.0 / 1e6  # MUSD/year
    capital_ratio = capex / (gross * 10.0)  # MNOK; assumed10 NOK/USD
    economic_screens.append({"name": name, "capex_MNOK": capex,
        "oil_gain_bbl_day": assumed_oil_gain,
        "gross_MUSD_per_year": gross,
        "gross_revenue_capital_years": capital_ratio})
    print(name, "assumed oil gain bbl/day:", assumed_oil_gain,
          "gross revenue MUSD/year:", gross,
          "capital/gross-revenue ratio years:", capital_ratio)
# Deduct OPEX, taxes, decline, downtime and time value before claiming payback/NPV.
```

---

## 24.24 Flaring Minimization and Emissions Optimization

Flaring minimization is increasingly important as regulatory regimes tighten worldwide. Use dated, jurisdiction-specific tax and allowance prices when valuing emissions; this chapter does not supply a current fiscal tariff. The voluntary World Bank Zero Routine Flaring initiative targets routine oil-production flaring by 2030; it distinguishes routine disposal from safety and other non-routine events \cite{worldbankzrf}.

### 24.24.1 Sources of Flaring

Routine flaring occurs when produced gas exceeds the gas handling capacity of the facility. The main sources are:

1. **Flash gas from separators** — gas released when oil pressure is reduced
2. **Compressor downtime** — gas that cannot be compressed due to equipment trips
3. **Startup and shutdown** — off-spec gas during transient operations
4. **Safety relief** — emergency pressure relief (not optimizable)

The optimizable flaring comes primarily from the first two sources. If the gas compressor capacity constrains production before any other equipment, flaring can be avoided by reducing the oil production rate until gas handling capacity matches. This is a classic multi-objective trade-off: oil revenue versus flaring penalty.

### 24.24.2 Flaring as an Optimization Objective

**Execution scope:** This integration pattern requires a fully defined flare driver and emissions model.

```python pattern: requires a fully defined flare driver and emissions model
# Define flaring cost objective
flare_rate_evaluator = lambda proc: proc.getUnit("Flare").getFlowRate("kg/hr")

flare_objective = OptimizationObjective(
    "minimize_flaring",
    flare_rate_evaluator,
    False,         # Minimize (not maximize)
    1000.0,        # Weight: CO2 tax equivalent
    "Minimize flaring volume (regulatory compliance)")
```

### 24.24.3 Zero-Flare Operating Point

The zero-flare constraint forces the optimizer to find the highest production rate that generates no routine flaring:

**Execution scope:** This integration pattern requires a fully defined flare driver and emissions model.

```python pattern: requires a fully defined flare driver and emissions model
zero_flare_constraint = OptimizationConstraint(
    "zero_flare",
    flare_rate_evaluator,
    ConstraintSeverity.HARD, 0.0,
    "No routine flaring permitted")
```

The production cost of a no-routine-flaring constraint is case-specific. Calculate it with the full gas balance and available recovery/export routes; no generic 15–25% loss is established here.

### 24.24.4 Emissions Accounting Integration

The optimizer can track CO₂ equivalent emissions for each evaluated operating point:

**Execution scope:** This integration pattern requires a fully defined flare driver and emissions model.

```python pattern: requires a fully defined flare driver and emissions model
def calculate_emissions(process):
    """Calculate total CO2e emissions for the current operating point."""
    # Compressor fuel gas (gas turbine driver)
    fuel_gas = comp.getFuelGasRate("Sm3/hr")
    co2_from_fuel = fuel_gas * 2.0  # approx 2 kg CO2/Sm3 natural gas

    # Flaring emissions
    flare_gas = process.getUnit("Flare").getFlowRate("Sm3/hr")
    co2_from_flare = flare_gas * 2.5  # includes incomplete combustion factor

    # Total in tonnes/hour
    return (co2_from_fuel + co2_from_flare) / 1000.0

emissions_objective = OptimizationObjective(
    "minimize_emissions",
    calculate_emissions,
    False, 500.0,
    "Minimize total CO2e emissions")
```

This creates a three-way Pareto front between oil production, gas sales, and emissions — a decision surface that management can use to set corporate emission reduction targets.

---

## 24.25 Best Practices

### 24.25.1 Setting Realistic Equipment Limits

The quality of optimization results depends critically on the accuracy of equipment limits:

1. **Use actual equipment data**: Where available, use vendor data sheets, performance test results, and operating history to set constraint values rather than generic design margins.

2. **Account for degradation**: Equipment performance degrades over time. Compressor efficiency decreases, heat exchangers foul, valve seats erode. Periodically re-calibrate limits.

3. **Distinguish design from operational limits**: Design limits (nameplate values) may be conservative. Operational limits (verified through testing or experience) are more appropriate for optimization.

4. **Include all relevant constraints**: Missing a constraint can lead the optimizer to an infeasible operating point. Better to include too many constraints (with ADVISORY severity for informational ones) than too few.

### 24.25.2 Appropriate Utilization Margins

Illustrative screening margins by equipment type. These are not operating permissions; establish applicable ratings and transient allowance independently:

| Equipment | Recommended Limit | Rationale |
|-----------|------------------|-----------|
| Separator | 90–95% | Gas carry-over increases sharply above 100% |
| Compressor | 85–90% | Power limit margin for ambient temperature variation |
| Heat exchanger | 85–90% | Fouling margin; approach temperature sensitivity |
| Valve | 80% | Control authority preservation |
| Pipeline | 90–95% | Erosional velocity margin |
| Pump | 85–90% | NPSH margin for process upsets |

### 24.25.3 Equipment-Specific Utilization Limits

Use `utilizationLimitForName()` and `utilizationLimitForType()` to set appropriate limits:

```java
config.defaultUtilizationLimit(0.95)                    // Global default
    .utilizationLimitForType(Compressor.class, 0.88)    // Tighter for compressors
    .utilizationLimitForType(ThrottlingValve.class, 0.80) // Tighter for valves
    .utilizationLimitForName("Old Compressor K-101", 0.82); // Specific equipment
```

### 24.25.4 Algorithm Selection Guidelines

| Problem Characteristic | Recommended Algorithm |
|----------------------|----------------------|
| Single variable, monotonic | BINARY_FEASIBILITY |
| Single variable, unimodal score | GOLDEN_SECTION_SCORE |
| 2–5 variables, smooth | NELDER_MEAD_SCORE |
| 5–20 variables, smooth | GRADIENT_DESCENT_SCORE |
| Any dimensionality, non-convex | PARTICLE_SWARM_SCORE |
| Quick feasibility check | BINARY_FEASIBILITY with 10 iterations |

---

## 24.26 Troubleshooting

### 24.26.1 No Feasible Solution

**Symptom:** `result.isFeasible() == false` even at the minimum flow rate.

**Diagnosis:**
```python
# Check infeasibility at minimum rate
feed.setFlowRate(config.getLowerBound(), "kg/hr")
run_facility()

if process.isAnyHardLimitExceeded():
    print("System is infeasible even at minimum rate!")
    for eq in process.getConstrainedEquipment():
        if eq.isHardLimitExceeded():
            bn = eq.getBottleneckConstraint()
            print(f"  {eq.getName()}: {bn.getName()} = {bn.getCurrentValue():.2f} "
                  f"(max = {bn.getMaxValue():.2f})")
```

**Common causes:**
1. Equipment limits set too tight
2. Process conditions changed (higher compression ratio, more water)
3. Incorrect constraint configuration (wrong units, wrong direction)

**Resolution:**
- Check the ratings and bounds; change a limit only when its engineering basis supports the change
- Use `disableAllConstraints()` to find the unconstrained optimum, then re-enable constraints one by one to identify the binding limitation
- Check constraint units and values

### 24.26.2 Changing Bottleneck

**Symptom:** The bottleneck shifts between equipment during optimization iterations.

**This is normal behavior** — as the flow rate changes, different equipment items become limiting. The optimizer handles this automatically.

**If the bottleneck oscillates without convergence:**
1. Reduce the tolerance
2. Increase max iterations
3. Try GOLDEN_SECTION_SCORE instead of BINARY_FEASIBILITY (smoother convergence)

### 24.26.3 Slow Optimization

**Symptom:** Optimization takes many iterations or runs slowly.

**Common causes and solutions:**

| Cause | Solution |
|-------|----------|
| Too many process equipment | Simplify model (remove non-constraining equipment) |
| Tight tolerance | Increase tolerance (e.g., 100 kg/hr instead of 1 kg/hr) |
| Large search range | Narrow bounds based on engineering judgment |
| No caching | Enable LRU cache: `config.enableCaching(true)` |
| Sequential evaluation | Enable parallel: `config.parallelEvaluations(true)` |

### 24.26.4 Stagnation

**Symptom:** Optimizer makes no progress for many iterations.

**Solution:** Configure stagnation detection:
```java
config.stagnationIterations(5);  // Stop after 5 iterations without improvement
```

Alternatively, try a different algorithm — PSO can escape local optima that trap Nelder-Mead.

### 24.26.5 Numerical Issues

**Symptom:** NaN or unreasonable values in results.

**Solution:**
```java
config.rejectInvalidSimulations(true);
// This search-screening option supplements explicit final feasibility and replay checks.
```

Also verify:
- Fluid composition sums to 1.0
- Pressure and temperature are physically reasonable
- Compressor ratio is within compressor chart range

---

## 24.27 Mathematical Summary

### 24.27.1 The Production Optimization Problem

The complete mathematical formulation of the NeqSim production optimization problem is:

$$
\max_{x} \quad f(x) = \sum_{j=1}^{k} w_j \cdot \hat{f}_j(x)
$$

subject to:

**Equipment capacity constraints (from CapacityConstrainedEquipment):**

$$
U_i(x) \leq U_{i,\text{limit}} \quad \forall i \in \mathcal{E}
$$

**Hard process constraints:**

$$
g_m(x) \leq 0 \quad \forall m \in \mathcal{H}
$$

**Soft process constraints (penalized):**

$$
f_{\text{penalized}}(x) = f(x) - \sum_{m \in \mathcal{S}} \lambda_m \cdot \max(0, g_m(x))
$$

**Bound constraints:**

$$
x^L \leq x \leq x^U
$$

where:
- $x$ is the vector of decision variables (flow rates, pressures, temperatures)
- $f_j(x)$ are the objective functions (production rate, power, quality)
- $w_j$ are objective weights
- $U_i(x)$ is the utilization of equipment $i$
- $U_{i,\text{limit}}$ is the utilization limit for equipment $i$
- $\mathcal{E}$ is the set of capacity-constrained equipment
- $\mathcal{H}$ is the set of hard constraints
- $\mathcal{S}$ is the set of soft constraints
- $\lambda_m$ is the penalty weight for soft constraint $m$

### 24.27.2 Composite Score Function

A penalty score combines normalized objectives and violation measures. Define

$$
\begin{aligned}
F(x) &= \sum_j w_j\hat f_j(x), \\
P(x) &= \sum_m\lambda_m\max(0,g_m(x)), \\
V(x) &= \sum_i\max(0,U_i(x)-U_{i,\mathrm{limit}}).
\end{aligned}
$$

A schematic conditional score is then

$$
S(x)=\begin{cases}
F(x), & \text{feasible}, \\
F(x)-P(x)-\Lambda V(x), & \text{infeasible}.
\end{cases}
$$

Here feasibility means that every enabled hard constraint and equipment utilization limit is satisfied. Soft-constraint treatment depends on the chosen scoring configuration; the expression illustrates the penalty concept rather than every implementation branch.

A finite penalty weight $\Lambda$ does **not** generally ensure that every feasible candidate outranks every infeasible candidate: such a guarantee requires additional objective and violation bounds. Acceptance therefore uses explicit feasibility checks and the final full-model replay, with a recorded failure when a valid final state cannot be established. A favorable scalar score alone is insufficient.

---


<!-- reviewed-notebook-results:start -->
## Reproduced Calculation Results

These examples use the stated fluid recipes and operating assumptions. Curves represent NeqSim calculations unless a caption identifies an analytical illustration, assumed equipment map or synthetic data.

![Figure 24.2: Binary Search Convergence for Maximum Throughput](figures/ch18_optimization_convergence.png)

Feed Rate spans 60–80 t/hr across the plotted cases. Bottleneck Utilization spans 86.96–115.9 % across the plotted cases.

Bisection retains a feasible lower rate and an infeasible upper rate, halving their separation after each process evaluation. The final lower bound is a conservative approximation to the declared capacity boundary. Preserve both endpoints and the stopping tolerance with the reported capacity.

![Figure 24.3: Optimal Throughput by Algorithm](figures/ch18_algorithm_comparison.png)

Binary and golden-section searches return 69.0000 and 68.9998 t/hr. Independent reruns give maximum utilizations of 100.000 and 100.000 percent.

The two searches use the same process and capacity definitions; the second panel reruns utilization at each returned optimum. A reported convergence flag is insufficient unless the returned rate also satisfies the physical constraints. Use the independently checked utilization and pressure alongside the search result.

Selected numerical ranges from the plotted cases:

| Quantity / series | Minimum | Maximum | Unit |
|---|---:|---:|---|
| Feed Rate | 60 | 80 | t/hr |

Ranges describe the sampled cases; they are not independent validation tolerances.
<!-- reviewed-notebook-results:end -->

## Summary

This chapter presented a comprehensive treatment of production optimization using NeqSim's built-in optimization framework, covering theory, implementation, and practical application.

**Key takeaways:**

1. **Equipment capacity constraints** are defined using the `CapacityConstrainedEquipment` interface, which supports HARD, SOFT, and DESIGN constraint types with a four-level severity hierarchy (CRITICAL, HARD, SOFT, ADVISORY).

2. **The `autoSize()` method** automatically creates capacity constraints with design margins for separators (gasLoadFactor), compressors (speed, power, surgeMargin), valves (valveOpening, cvUtilization), pipelines (velocity, pressureDrop, FIV), and pumps (npshMargin, power, flowRate).

3. **Constraints are disabled by default** for backward compatibility. Enable them using `enableAllConstraints()` on the equipment or process. Disable for what-if studies using `disableAllConstraints()` or `setCapacityAnalysisEnabled(false)`.

4. **Facility-level bottleneck analysis** is performed using `ProcessSystem.findBottleneck()`, `getCapacityUtilizationSummary()`, `getEquipmentNearCapacityLimit()`, `isAnyEquipmentOverloaded()`, and `isAnyHardLimitExceeded()`.

5. **The `ProductionOptimizer`** provides five search algorithms: BINARY_FEASIBILITY for fast monotonic search, GOLDEN_SECTION_SCORE for unimodal single-variable problems, NELDER_MEAD_SCORE for derivative-free multi-variable optimization, PARTICLE_SWARM_SCORE for global search, and GRADIENT_DESCENT_SCORE for smooth high-dimensional problems.

6. **`OptimizationConfig`** uses a fluent builder API for configuration including tolerances, utilization limits (global, per-type, per-name), stagnation detection, warm start, LRU caching, and parallel evaluations.

7. **`OptimizationResult`** provides the optimal rate, bottleneck identification, utilization records, constraint statuses, iteration history, infeasibility diagnosis, and JSON/CSV export capabilities.

8. **Custom objectives and constraints** are defined using `OptimizationObjective` (with weight and MAXIMIZE/MINIMIZE direction) and `OptimizationConstraint` (with lessThan/greaterThan, HARD/SOFT severity).

9. **Multi-objective optimization** is supported via `optimizePareto()` with weighted-sum scalarization, producing a Pareto front with an explicit decision rule for selecting a preferred point.

10. **The `ProcessOptimizationEngine`** (Level 2) provides higher-level capabilities including `findMaximumThroughput()`, `evaluateAllConstraints()`, `analyzeSensitivity()`, `generateLiftCurve()`, and registered `EquipmentCapacityStrategy` plugins with auto-discovery.

11. **Compressor curves** integrate with optimization through `CompressorChartGenerator`, enabling realistic surge margin and speed constraints. Use `reinitializeCapacityConstraints()` after changing compressor parameters.

12. **Scenario comparison** using `compareScenarios()` enables systematic evaluation of alternative operating strategies.

13. **External optimizer integration** via `ProcessSimulationEvaluator` bridges NeqSim to SciPy, NLopt, or any external solver.

14. **Real-time optimization** combines steady-state detection, data reconciliation, model update, and periodic re-optimization in a continuous loop.

The capacity constraint framework and optimization algorithms presented in this chapter form the computational backbone of modern production optimization. By combining rigorous process simulation with automated constraint evaluation and efficient search algorithms, NeqSim enables engineers to find optimal operating conditions that maximize production while respecting all physical, safety, and contractual constraints — a capability that directly translates to improved field economics and operational excellence.

---


<!-- September 2026 source update -->
## Current optimizer replay and screening-table semantics

At the September 2026 source revision, `ProductionOptimizer` returns a freshly replayed decision vector and corresponding feasibility evidence. This resolves the case in which the search's best point and the mutable process previously represented different operating states. Applications must still check feasibility and preserve any final-solve exception; a search history entry is not an accepted result by itself \cite{neqsim2026update}.

The interpretation of pressure/flow tables also matters. `ProcessOptimizationEngine.generateCapacityScreening(pressures, temperatures)` performs fixed-composition mass-throughput screening. The five-argument overload accepts explicit outlet-pressure and lower/upper mass-flow limits. It does not recombine a fluid at arbitrary water cut/GOR, solve a well datum pressure, or certify a global optimum. Legacy `generateLiftCurve(P,T,WC,GOR)` accepts only the supported singleton zero composition placeholders; nonzero/multiple composition axes now fail explicitly.

A process-capacity maximum is not flowing bottomhole pressure. Generic process tables should be exported as diagnostic JSON, CSV or formatted text. Reservoir `VFPPROD`/`VFPINJ` output is a separate contract: supply a complete, finite, positive BHP grid to `EclipseVFPExporter`, state the datum and phase-volume basis, preserve all axes and use compatible METRIC or FIELD units. The exporter formats supplied pressures; it does not qualify the well hydraulics. See Chapter 28 for the distinction and the current source export contract \cite{neqsim2026update}.

Finally, synthetic auto-sizing and disabled constraints are study assumptions. Preserve them alongside each optimum so that a reader can distinguish an installed-plant recommendation from an algorithm demonstration.

---

## Exercises

**Exercise 24.1** — *Capacity Constraint Configuration*
A gas processing plant has a compressor with the following limits: maximum speed 11,500 RPM (HARD), maximum power 22 MW (HARD), minimum surge margin 10% (HARD), maximum discharge temperature 180°C (SOFT). Write the Java code to create `CapacityConstraint` objects for each limit using the fluent builder API. Include appropriate severity levels, units, and descriptions.

**Exercise 24.2** — *autoSize and Bottleneck Analysis*
Build a NeqSim process model with a three-phase separator and compressor. Auto-size both with a 15% design margin. Print the utilization summary and identify the bottleneck. Then increase the feed rate by 20% and report how the utilization and bottleneck change.

**Exercise 24.3** — *Binary Search vs Golden Section*
Using the same process model, run the `ProductionOptimizer` twice — once with `BINARY_FEASIBILITY` and once with `GOLDEN_SECTION_SCORE`. Compare: (a) the optimal rate found, (b) the number of iterations, (c) the convergence history. Plot both convergence curves on the same graph.

**Exercise 24.4** — *Multi-Variable Optimization*
Define three manipulated variables: feed flow rate (100,000–400,000 kg/hr), separator pressure (40–90 bara), and compressor outlet pressure (120–180 bara). Use NELDER_MEAD_SCORE to find the combination that maximizes oil production rate while keeping all equipment within 95% utilization. Report the optimal values of all three variables.

**Exercise 24.5** — *Custom Objective: Minimize Specific Power*
Define a custom objective that minimizes the specific compressor power (MW per MSm³/day of gas produced). This represents energy efficiency optimization. Use GOLDEN_SECTION_SCORE with the feed rate as the decision variable. What is the feed rate that minimizes specific power, and how does it compare to the maximum throughput found in Exercise 24.3?

**Exercise 24.6** — *Pareto Front: Throughput vs Power*
Set up a two-objective optimization: maximize throughput and minimize compressor power. Generate a Pareto front with 15 points. Plot the Pareto front and identify the knee point. At the knee point, what is the throughput and power, and how do they compare to the extreme solutions (max throughput only, min power only)?

**Exercise 24.7** — *Scenario Comparison*
Compare three operating scenarios for a gas-condensate platform:
- Scenario A: HP separator at 65 bara, compressor to 150 bara
- Scenario B: HP separator at 55 bara, compressor to 140 bara
- Scenario C: HP separator at 75 bara, compressor to 160 bara

For each scenario, report the gas rate, oil rate, compressor power, and bottleneck. Which scenario gives the best overall performance?

**Exercise 24.8** — *What-If: Equipment Upgrade*
Starting from the bottleneck identified in Exercise 24.2, disable the capacity constraints on the bottleneck equipment (forming an unconstrained screening counterfactual). Re-run the optimizer to find the new maximum throughput and new bottleneck. Report this as an upper-bound counterfactual. Then specify a finite upgraded rating and replay all constraints before claiming an upgrade benefit.

**Exercise 24.9** — *Infeasibility Diagnosis*
Set the utilization limits to 70% for all equipment (unrealistically tight). Run the optimizer. Examine the `getInfeasibilityDiagnosis()` output and explain which constraints are violated and by how much. What is the minimum utilization limit that yields a feasible solution?

**Exercise 24.10** — *Real-Time Optimization Loop*
Implement a simplified real-time optimization loop that:
1. Reads feed pressure from a list (simulating historian data): [65, 63, 61, 58, 55, 52, 50] bara (declining reservoir pressure)
2. At each data point, re-optimizes the production rate
3. Records the optimal rate, bottleneck, and bottleneck utilization at each step
4. Plots the optimal rate vs time (feed pressure) and identifies when the bottleneck shifts

**Exercise 24.11** — *Warm Start Performance*
Run the optimizer with GOLDEN_SECTION_SCORE three times:
- Without warm start (default initialization)
- With warm start set to 80% of the true optimum
- With warm start set to the true optimum from a previous run

Compare the number of iterations required in each case. By what factor does warm start reduce iterations?

**Exercise 24.12** — *Stagnation Detection*
Configure PSO with a swarm of 5 particles and run optimization on a simple two-equipment process. Set `stagnationIterations(3)` and observe when the optimizer terminates due to stagnation. Plot the best score vs iteration and mark the stagnation point. Increase the swarm to 15 particles and repeat — does stagnation still occur?

---

## References

1. Arnold, K.E. and Stewart, M.I. (2008). *Surface Production Operations, Volume 1: Design of Oil Handling Systems and Facilities*, 3rd edn. Burlington, MA: Gulf Professional Publishing.
2. Campbell, J.M. (2014). *Gas Conditioning and Processing, Volume 2: The Equipment Modules*, 9th edn. Norman, OK: Campbell Petroleum Series.
3. Nocedal, J. and Wright, S.J. (2006). *Numerical Optimization*, 2nd edn. New York: Springer.
4. Kennedy, J. and Eberhart, R. (1995). "Particle Swarm Optimization." *Proceedings of ICNN'95*, vol. 4, pp. 1942–1948.
5. Nelder, J.A. and Mead, R. (1965). "A Simplex Method for Function Minimization." *The Computer Journal*, 7(4), pp. 308–313.
6. Souders, M. and Brown, G.G. (1934). "Design of Fractionating Columns: I. Entrainment and Capacity." *Industrial & Engineering Chemistry*, 26(1), pp. 98–103.
7. API RP 14E (1991). *Recommended Practice for Design and Installation of Offshore Production Platform Piping Systems*, 5th edn. Washington, DC: American Petroleum Institute.
8. Bieker, H.P., Slupphaug, O., and Johansen, T.A. (2007). "Real-Time Production Optimization of Oil and Gas Production Systems: A Technology Survey." *SPE Production & Operations*, 22(4), pp. 382–391.
9. Foss, B. (2012). "Process Control in Conventional Oil and Gas Fields — Challenges and Opportunities." *Control Engineering Practice*, 20(10), pp. 1058–1064.
10. Campos, S.R.V., Teixeira, A.F., Vieira, L.M., and Sunjerga, S. (2010). "Urucu Field Integrated Production Optimization." *SPE 128546*, SPE Intelligent Energy Conference, Utrecht.
11. Saputelli, L., Nikolaou, M., and Economides, M.J. (2005). "Self-Learning Reservoir Management." *SPE Reservoir Evaluation & Engineering*, 8(6), pp. 534–547.
12. ISA/IEC 60534 (2005). *Industrial-Process Control Valves*. Research Triangle Park, NC: International Society of Automation.
13. NORSOK P-002 (2023, corrected 2024). *Process System Design*. Lysaker: Standards Norway.
14. GPSA Engineering Data Book (2012). 13th edn. Tulsa, OK: Gas Processors Suppliers Association.
15. Mokhatab, S. and Poe, W.A. (2012). *Handbook of Natural Gas Transmission and Processing*, 2nd edn. Burlington, MA: Gulf Professional Publishing.
16. Conn, A.R., Scheinberg, K., and Vicente, L.N. (2009). *Introduction to Derivative-Free Optimization*. Philadelphia: SIAM.
17. Ehrgott, M. (2005). *Multicriteria Optimization*, 2nd edn. Berlin: Springer.


