# Well and Network Optimization

<!-- Chapter metadata -->
<!-- Notebooks: ch27_well_network_demo.ipynb, ch27_ipr_vfp_construction.ipynb, ch27_6well_optimization.ipynb -->
<!-- Estimated pages: 38 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Formulate the well allocation problem as a constrained optimization — maximizing total production subject to facility constraints — and identify the decision variables, objective function, and constraints
2. Construct Inflow Performance Relationship (IPR) curves using the Vogel, Fetkovich, and Jones equations, and couple them with tubing performance for nodal analysis
3. Generate Vertical Flow Performance (VFP) tables using NeqSim's `MultiScenarioVFPGenerator` and explain their role in well allocation and reservoir simulation
4. Build and solve a production network using NeqSim's `LoopedPipeNetwork`, including wells with IPR models, tubing, chokes, and multiphase flowlines
5. Optimize choke positions to maximize total production under facility constraints, accounting for critical vs. subcritical flow regimes and back-pressure coupling between wells
6. Apply gas lift optimization techniques to allocate limited lift gas among multiple wells for maximum incremental oil production

---

## 26.1 Introduction

The previous chapters addressed optimization of the *processing facility* — separators, compressors, heat exchangers, and their interconnections. But the fluid that enters the facility originates from *wells*, and the wells themselves are coupled to each other through the gathering network and the facility constraints. The well allocation problem — how much to produce from each well — is often the single most impactful optimization decision on a production platform.

Consider a platform with six producing wells connected through a subsea gathering network to a single processing facility. Each well has a different reservoir pressure, water cut, gas-oil ratio, and productivity. The facility has a finite gas handling capacity, a finite water treatment capacity, and a finite compression capacity. Which wells should produce at maximum rate? Which should be choked back? Should any be shut in?

This is a constrained optimization problem where:

- **Decision variables** are the choke positions (or equivalently, the flow rates) of each well
- **Objective function** is total oil production (or total revenue, or total hydrocarbon production)
- **Constraints** are the capacity limits of each piece of processing equipment, the minimum wellhead pressure for each well, and any contractual or regulatory limits

The challenge is that the wells are *coupled* — producing more from one well increases the back-pressure on the gathering network, which reduces the production from other wells. The optimization must account for this hydraulic coupling, which requires a network model that solves the coupled pressure-flow equations simultaneously.

This chapter develops the theory and NeqSim implementation of well and network optimization. We begin with the well models — IPR (Section 26.3) and VFP (Section 26.4) — then introduce the `LoopedPipeNetwork` solver (Section 26.5), and finally address optimization algorithms for choke control (Section 26.6), gas lift (Section 26.7), and multi-well allocation (Section 26.9).

### 26.1.1 Scope and Assumptions

The well and network optimization developed here is **surface-constrained** — we optimize well rates subject to surface facility limits, taking the reservoir deliverability (IPR) as given. The reservoir itself is not optimized; we do not consider long-term recovery factor or reservoir pressure maintenance in this chapter. Those topics belong to reservoir engineering and integrated asset modeling, which are introduced briefly in Chapter 19 and covered in dedicated reservoir engineering texts.

We also assume **steady-state** operation — each optimization snapshot represents a quasi-steady operating point. Transient effects (slugging, well cleanup, startup) are important but are handled by dynamic simulation (Chapter 20) rather than the steady-state network solver.

---

## 26.2 The Well Allocation Problem

### 26.2.1 Mathematical Formulation

The well allocation problem can be stated as a nonlinear constrained optimization:

$$
\max_{q_1, q_2, \ldots, q_{N_w}} \sum_{i=1}^{N_w} q_{o,i}(q_i)
$$

subject to:

$$
\sum_{i=1}^{N_w} q_{g,i}(q_i) \leq Q_{g,\text{max}} \quad \text{(gas handling capacity)}
$$

$$
\sum_{i=1}^{N_w} q_{w,i}(q_i) \leq Q_{w,\text{max}} \quad \text{(water handling capacity)}
$$

$$
W_{\text{comp}}\left(\sum_{i=1}^{N_w} q_{g,i}\right) \leq W_{\text{comp,max}} \quad \text{(compression power)}
$$

$$
q_{i,\text{min}} \leq q_i \leq q_{i,\text{max}} \quad \forall i = 1, \ldots, N_w \quad \text{(well rate bounds)}
$$

where:

- $q_i$ is the total fluid production rate from well $i$
- $q_{o,i}$, $q_{g,i}$, $q_{w,i}$ are the oil, gas, and water rates from well $i$ (functions of $q_i$ through the well's GOR and water cut)
- $Q_{g,\text{max}}$ and $Q_{w,\text{max}}$ are the facility gas and water handling capacities
- $W_{\text{comp}}$ is the compression power as a function of total gas rate
- $q_{i,\text{min}}$ and $q_{i,\text{max}}$ are bounds on individual well rates (minimum for flow stability, maximum from reservoir deliverability)

### 26.2.2 Why the Problem Is Nonlinear

The objective and constraints are nonlinear for several reasons:

1. **IPR nonlinearity.** The relationship between bottomhole flowing pressure and flow rate is nonlinear (Vogel equation, Fetkovich equation).
2. **Multiphase flow nonlinearity.** The pressure drop in the tubing and flowline depends nonlinearly on flow rate, GOR, and water cut.
3. **Back-pressure coupling.** The manifold pressure depends on the total flow from all wells, which in turn affects the flowing pressure and deliverability of each well.
4. **Compression curve nonlinearity.** Compressor power is a nonlinear function of suction pressure, discharge pressure, and flow rate.

These nonlinearities mean that simple linear programming (LP) is insufficient. The problem requires nonlinear programming (NLP) or, more practically, iterative simulation-based optimization where the network model evaluates the coupled system at each trial point.

### 26.2.3 Decision Variables

The natural decision variables depend on the control mechanism:

| Control Mechanism | Decision Variable | Typical Range |
|------------------|-------------------|---------------|
| Choke valve | Choke opening (%) or Cv | 0–100% |
| Gas lift | Injection rate per well (Sm³/d) | 0 to max available |
| ESP frequency | Pump speed (Hz) | Min to max rated |
| Wellhead pressure setpoint | Pressure (bara) | Min stable to max |

In this chapter, we focus on choke valves and gas lift as the primary control mechanisms.

---

## 26.3 Inflow Performance Relationships

The **Inflow Performance Relationship (IPR)** describes the relationship between the bottomhole flowing pressure $p_{wf}$ and the production rate $q$ for a given well. It captures the deliverability of the reservoir-to-wellbore system.

### 26.3.1 Darcy (Linear) IPR

For single-phase oil flow above the bubble point pressure, the IPR is linear:

$$
q_o = J (p_r - p_{wf})
$$

where $J$ is the productivity index (m³/d/bar or bbl/d/psi) and $p_r$ is the average reservoir pressure. This is the simplest IPR model, valid when the flowing pressure is above the bubble point everywhere in the reservoir.

### 26.3.2 Vogel's Equation

When the flowing pressure falls below the bubble point, dissolved gas comes out of solution and creates a two-phase flow region near the wellbore. **Vogel's equation** (1968) accounts for this effect:

$$
\frac{q_o}{q_{o,\text{max}}} = 1 - 0.2 \left(\frac{p_{wf}}{p_r}\right) - 0.8 \left(\frac{p_{wf}}{p_r}\right)^2
$$

where $q_{o,\text{max}}$ is the absolute open-flow potential (rate at $p_{wf} = 0$). This can be rearranged to give rate as a function of flowing pressure:

$$
q_o = q_{o,\text{max}} \left[1 - 0.2 \frac{p_{wf}}{p_r} - 0.8 \left(\frac{p_{wf}}{p_r}\right)^2\right]
$$

### 26.3.3 Fetkovich's Equation

**Fetkovich's equation** (1973) provides a more flexible empirical model:

$$
q_o = C (p_r^2 - p_{wf}^2)^n
$$

where $C$ is the deliverability coefficient and $n$ is the deliverability exponent (0.5 ≤ $n$ ≤ 1.0). For $n = 1$, this reduces to a form similar to Darcy flow for gas wells. For $n = 0.5$, it represents fully turbulent (non-Darcy) flow.

### 26.3.4 Jones Equation (Rate-Dependent Skin)

For wells where non-Darcy flow near the wellbore is significant (high-rate gas wells, gravel-packed wells), the **Jones equation** provides a rate-dependent IPR:

$$
p_r - p_{wf} = a q + b q^2
$$

where $a$ is the laminar (Darcy) flow coefficient and $b$ is the turbulent (non-Darcy) flow coefficient. The first term represents viscous pressure drop; the second represents inertial pressure drop near the wellbore.

### 26.3.5 IPR Construction in NeqSim

NeqSim supports IPR curves through the well and network modeling framework. A well's IPR is defined by specifying the model type and parameters:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
LoopedPipeNetwork = jneqsim.process.equipment.network.LoopedPipeNetwork
network = LoopedPipeNetwork("Production Network")
# API construction example: AOFP is kg/s here, not standard volume/day.
network.addSourceNode("Reservoir-A", 250.0, 0.0)
network.addJunctionNode("Wellbore-A")
network.addWellIPRVogel("Reservoir-A", "Wellbore-A", "Well-A", 5.0)
print(network.getNodeNames())
```

To construct IPR curves for visualization and analysis:

```python
from pathlib import Path
Path("figures").mkdir(parents=True, exist_ok=True)
import numpy as np
import matplotlib.pyplot as plt

def vogel_ipr(p_r, q_max, p_wf_array):
    """Calculate Vogel IPR for an array of flowing pressures."""
    q = q_max * (1.0 - 0.2 * (p_wf_array / p_r) - 0.8 * (p_wf_array / p_r)**2)
    return np.maximum(q, 0.0)

def fetkovich_ipr(p_r, C, n, p_wf_array):
    """Calculate Fetkovich IPR for an array of flowing pressures."""
    q = C * (p_r**2 - p_wf_array**2)**n
    return np.maximum(q, 0.0)

# Well parameters
p_r = 250.0  # bara
q_max_vogel = 5000.0  # Sm3/d
C_fetk = 0.5
n_fetk = 0.8

p_wf = np.linspace(0, p_r, 100)

q_vogel = vogel_ipr(p_r, q_max_vogel, p_wf)
q_fetk = fetkovich_ipr(p_r, C_fetk, n_fetk, p_wf)

plt.figure(figsize=(8, 6))
plt.plot(q_vogel, p_wf, 'b-', linewidth=2, label='Vogel')
plt.plot(q_fetk, p_wf, 'r--', linewidth=2, label='Fetkovich')
plt.xlabel('Production Rate (Sm³/d)')
plt.ylabel('Bottomhole Flowing Pressure (bara)')
plt.title('Inflow Performance Relationships')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim(left=0)
plt.ylim(bottom=0)
plt.tight_layout()
plt.savefig('figures/fig27_1_ipr_curves.png', dpi=150, bbox_inches='tight')
plt.show()
```

![Inflow Performance Relationship curves for a well using Vogel and Fetkovich equations, showing the nonlinear decline in flowing pressure with increasing production rate.](figures/fig27_1_ipr_curves.png)

### 26.3.6 Nodal Analysis: Coupling IPR with Tubing Performance

The actual well production rate is determined by the intersection of the IPR curve (reservoir deliverability) with the **Tubing Performance Relationship (TPR)** — the curve of required bottomhole pressure vs. rate for a given tubing configuration, wellhead pressure, and fluid properties.

The TPR is calculated using multiphase flow correlations (Section 26.4) and represents the minimum bottomhole pressure needed to lift the fluid to the surface at a given rate:

$$
p_{wf,\text{required}} = p_{wh} + \Delta p_{\text{gravity}} + \Delta p_{\text{friction}} - \Delta p_{\text{acceleration}}
$$

The operating point is where IPR and TPR intersect:

$$
p_{wf,\text{IPR}}(q) = p_{wf,\text{TPR}}(q)
$$

This intersection gives the natural flow rate of the well at the specified wellhead pressure.

### 26.3.7 WellFlow Equipment and Deliverability Curves

The IPR helper above operates at the network level. For a well that participates directly in a process flowsheet, the `WellFlow` equipment (package `neqsim.process.equipment.reservoir`) carries the inflow model on the unit itself and couples it to the rest of the simulation. Any of the four standard inflow models can be assigned:

**Execution scope:** This integration pattern requires wellstream and calibrated IPR test inputs. It is not a standalone validated process calculation.

```python pattern: requires wellstream and calibrated IPR test inputs
WellFlow = jneqsim.process.equipment.reservoir.WellFlow

well = WellFlow("Well-A", wellstream)
well.setVogelParameters(qTest, pwfTest, reservoirP)        # Vogel
# well.setFetkovichParameters(c, n, reservoirP)            # Fetkovich
# well.setBackpressureParameters(a, b, reservoirP)         # Rawlins–Schellhardt
# well.setTableInflow(bhp_array, rate_array)               # tabulated IPR

well.useWellConstraints()                                  # fluent; enables limits
well.setMaxDrawdown(40.0, "bara")
well.setMinBottomHolePressure(120.0, "bara")
well.setOutletPressure(90.0, "bara")
well.run()

print("BHP:", well.getBottomHolePressure(), "bara")
print("Drawdown:", well.getDrawdown(), "bara")
print("PI:", well.getWellProductionIndex())
```

When `useWellConstraints()` is active, the well reports drawdown and minimum-BHP utilization through the same capacity-constraint framework as the rest of the facility, so sand-control or coning limits enter the bottleneck analysis of Chapter 21. `WellFlow` also supports multi-layer commingled completions via `addLayer(name, stream, reservoirPressure, productivityIndex)` with a `setFlowMode(FlowMode)` selector, and fracture-containment screening through `setFracturePressure(...)` / `isFractureContained(bhp)`.

For lighter-weight studies that do not need a full flowsheet, `WellDeliverabilityCurve` (package `neqsim.process.fielddevelopment.integrated`) represents the IPR as a reusable curve object:

```python
WellDeliverabilityCurve = jneqsim.process.fielddevelopment.integrated.WellDeliverabilityCurve

# From a Vogel description (AOFP and shut-in pressure)
curve = WellDeliverabilityCurve.fromVogel(6000.0, 250.0)

q = curve.rateAt(120.0)            # rate at 120 bara flowing pressure
slope = curve.slopeAt(120.0)       # local deliverability slope
aofp = curve.getAbsoluteOpenFlowPotential()
```

When only well-test points are available, `WellTestMatcher` fits the curve to the data:

```python
WellTestMatcher = jneqsim.process.fielddevelopment.integrated.WellTestMatcher

matcher = WellTestMatcher()
matcher.addTestPoint(3200.0, 180.0)
matcher.addTestPoint(4500.0, 150.0)
matcher.addTestPoint(5300.0, 120.0)

match = matcher.fitVogel()         # or matcher.fitProductivityIndex()
fitted = match.getCurve()
print("Reservoir pressure:", match.getReservoirPressure(),
      "RMS error:", match.getRmsError())
```

The fitted `WellDeliverabilityCurve` is then consumed directly by the `IntegratedProductionModel` (Section 26.9) and the gas-lift and network optimizers that follow.

---

## 26.4 Vertical Flow Performance and VFP Tables

### 26.4.1 Multiphase Flow in Tubing

The pressure distribution in the production tubing is governed by the steady-state energy equation for multiphase flow:

$$
\frac{dp}{dz} = \frac{g \rho_m \sin\theta}{g_c} + \frac{f \rho_m v_m^2}{2 d} + \rho_m v_m \frac{dv_m}{dz}
$$

where the three terms represent the gravitational, frictional, and accelerational pressure gradients, respectively. Here $\rho_m$ is the mixture density, $v_m$ is the mixture velocity, $d$ is the tubing internal diameter, $f$ is the friction factor, $\theta$ is the inclination angle, and $z$ is the distance along the flow path.

Several empirical and mechanistic correlations solve this equation for multiphase conditions. The **Beggs and Brill** correlation (1973) is the most widely used and is implemented in NeqSim through the `PipeBeggsAndBrills` class.

### 26.4.2 VFP Table Structure

A **Vertical Flow Performance (VFP) table** pre-computes the bottomhole flowing pressure (or tubing head pressure) as a function of:

- Flow rate $q$
- GOR (gas-oil ratio) or total GOR
- Water cut $f_w$
- Artificial lift quantity (gas lift rate, ESP frequency)
- Tubing head pressure $p_{th}$ (for VFPPROD tables) or bottomhole pressure (for VFPINJ tables)

VFP tables are extensively used in reservoir simulators (Eclipse, OPM, IX) to represent the well and tubing performance without re-solving the multiphase flow equations at every timestep. The table is generated once (or periodically updated) and then interpolated during the reservoir simulation.

### 26.4.3 VFP Table Generation with NeqSim

NeqSim provides the `MultiScenarioVFPGenerator` for systematic VFP table generation across scenarios of varying GOR, water cut, and other parameters:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
Stream = jneqsim.process.equipment.stream.Stream
PipeBeggsAndBrills = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# Create a base fluid
fluid = SystemSrkEos(273.15 + 80.0, 200.0)
fluid.addComponent("methane", 0.50)
fluid.addComponent("ethane", 0.05)
fluid.addComponent("propane", 0.03)
fluid.addComponent("n-hexane", 0.07)
fluid.addComponent("n-octane", 0.15)
fluid.addComponent("water", 0.20)
fluid.setMixingRule("classic")

# Create a well tubing model
feed = Stream("Well feed", fluid)
feed.setFlowRate(100000.0, "kg/hr")
feed.setTemperature(80.0, "C")
feed.setPressure(200.0, "bara")

tubing = PipeBeggsAndBrills("Tubing", feed)
tubing.setPipeWallRoughness(2.5e-5)
tubing.setLength(3000.0)            # 3000 m measured depth
tubing.setElevation(-3000.0)        # vertical well
tubing.setDiameter(0.1016)          # 4-inch tubing

process = ProcessSystem()
process.add(feed)
process.add(tubing)
process.run()

# Read outlet conditions (tubing head)
outlet = tubing.getOutletStream()
thp = outlet.getPressure("bara")
print(f"Tubing head pressure: {thp:.1f} bara")
```

For generating a complete VFP table, the flow rate is swept across a range while recording the resulting tubing head pressure:

**Execution scope:** This integration pattern requires tubing-specific valid flow envelope and rejection handling. It is not a standalone validated process calculation.

```python pattern: requires tubing-specific valid flow envelope and rejection handling
from pathlib import Path
Path("figures").mkdir(parents=True, exist_ok=True)
import numpy as np

# Sweep flow rates to build VFP curve
flow_rates = np.linspace(20000, 300000, 15)  # kg/hr
thp_results = []

for q in flow_rates:
    feed.setFlowRate(float(q), "kg/hr")
    process.run()
    thp_val = tubing.getOutletStream().getPressure("bara")
    thp_results.append(thp_val)

thp_results = np.array(thp_results)

plt.figure(figsize=(8, 6))
plt.plot(flow_rates / 1000, thp_results, 'b-o', linewidth=2)
plt.xlabel('Flow Rate (tonnes/hr)')
plt.ylabel('Tubing Head Pressure (bara)')
plt.title('VFP Curve — 4" Tubing, 3000 m TVD')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('figures/fig27_2_vfp_curve.png', dpi=150, bbox_inches='tight')
plt.show()
```

![VFP curve showing tubing head pressure as a function of flow rate for a 3000 m vertical well with 4-inch tubing.](figures/fig27_2_vfp_curve.png)

### 26.4.4 Role of VFP Tables in Well Allocation

VFP tables serve two roles in well allocation:

1. **In the network solver.** The `LoopedPipeNetwork` uses VFP tables (or the underlying tubing model) to determine the flowing pressures and deliverability of each well at the current network conditions.
2. **In reservoir simulation.** VFP tables allow the reservoir simulator to quickly evaluate well deliverability without re-running multiphase flow calculations, enabling efficient long-term forecasting.

The accuracy of VFP tables depends on the resolution of the tabulated parameters and the quality of the underlying multiphase flow model. For wells with complex trajectories, severe slugging, or unusual fluid properties, higher-resolution tables or direct coupling to the flow model may be needed.

---

## 26.5 The LoopedPipeNetwork in NeqSim

### 26.5.1 Network Architecture

The `LoopedPipeNetwork` class in NeqSim provides a comprehensive production network solver that handles the coupled pressure-flow equations for a system of wells, flowlines, manifolds, and processing facilities. The solver uses a Newton-Raphson iterative scheme to simultaneously satisfy mass balance at each node and pressure-flow relationships in each element.

The network is built by adding elements of different types:

| Method | Element Type | Description |
|--------|-------------|-------------|
| `addWellIPR()` | Well source | Well with IPR model (PI, Vogel, Fetkovich) |
| `addTubing()` | Vertical pipe | Well tubing with multiphase flow |
| `addChoke()` | Flow restriction | Choke valve with Cv model |
| `addMultiphasePipe()` | Horizontal pipe | Flowline with Beggs & Brill |
| `addCompressor()` | Pressure booster | Compressor in the network |
| `addManifold()` | Junction node | Commingling point for multiple streams |
| `addSink()` | Outlet boundary | Processing facility entry point |

### 26.5.2 Building a Simple Network

The following example builds a three-well production network with subsea flowlines converging at a manifold, then a single export line to the processing platform:

```python
# A complete source-gas gathering calculation with explicit nodes and pipe identities.
SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
fluid = SystemSrkEos(313.15, 90.0)
fluid.addComponent("methane", 0.90)
fluid.addComponent("ethane", 0.10)
fluid.setMixingRule("classic")
network = LoopedPipeNetwork("Gathering Network")
network.addSourceNode("Supply-A", 90.0, 10000.0)
network.addJunctionNode("Manifold")
network.addFixedPressureSinkNode("Platform", 85.0)  # bara backpressure
network.setFluidTemplate(fluid)
network.setNodeFluid("Supply-A", fluid)
network.addPipe("Supply-A", "Manifold", "Flowline-A", 5000.0, 0.20)
network.addPipe("Manifold", "Platform", "Export", 10000.0, 0.25)
network.setSolverType(LoopedPipeNetwork.SolverType.NEWTON_RAPHSON)
network.run()
assert network.isConverged()
print(network.getNetworkReport())
print("Mass balance residual:", network.getMassBalanceError())
```

### 26.5.3 Back-Pressure Coupling

A critical feature of the network solver is that it captures **back-pressure coupling** between wells. When Well-A increases its production, it increases the pressure at the manifold, which in turn increases the wellhead pressure required for Well-B and Well-C, reducing their deliverability.

This coupling means that the sum of the individual wells' maximum rates (in isolation) exceeds the total network capacity:

$$
\sum_{i=1}^{N_w} q_{i,\text{max,isolated}} > Q_{\text{total,network}}
$$

The network solver finds the consistent solution where all pressures and flows satisfy both the IPR curves and the multiphase flow equations simultaneously. This coupled solution is essential for meaningful well allocation optimization.

### 26.5.4 Solver Convergence

The Newton-Raphson solver in `LoopedPipeNetwork` typically converges in 5–15 iterations for well-conditioned networks. Convergence can be checked:

```python
converged = network.isConverged()
iterations = network.getIterationCount()
residual = network.getMaxResidual()
print(f"Converged: {converged}, Iterations: {iterations}, Residual: {residual:.2e}")
```

Convergence difficulties may arise when:

- A well is near its minimum stable flow rate
- The network has very long flowlines with high pressure drops
- The manifold pressure is near the wellhead pressure of a marginal well
- Phase transitions (bubble point) occur within the flowline

In these cases, the solver may need relaxation or a different initial guess. Consult Chapter 29 for advanced solver strategies.

---

## 26.6 Choke Optimization

### 26.6.1 Choke Valve Model

The production rate through a choke valve is governed by the valve equation:

$$
q = C_v f(x) \sqrt{\frac{\Delta P}{\rho}}
$$

where $C_v$ is the valve flow coefficient (characterizing the fully-open valve), $f(x)$ is the valve characteristic function ($x$ is the opening fraction, 0 to 1), $\Delta P$ is the pressure drop across the valve, and $\rho$ is the fluid density.

### 26.6.2 Critical vs. Subcritical Flow

At sufficiently high pressure ratios, the flow through the choke becomes **critical** (sonic) — the flow rate no longer increases with further reduction in downstream pressure. The critical pressure ratio is approximately:

$$
\frac{p_{\text{downstream}}}{p_{\text{upstream}}} \leq \left(\frac{2}{\gamma + 1}\right)^{\gamma / (\gamma - 1)}
$$

For natural gas ($\gamma \approx 1.3$), the critical pressure ratio is approximately 0.55.

In critical flow, the choke acts as a **decoupler** — upstream pressure variations do not propagate downstream, and vice versa. This has important implications for network optimization:

- Wells in critical flow are independent of downstream back-pressure changes
- Optimization of wells in critical flow requires only adjusting the choke opening, not re-solving the entire network
- Wells in subcritical flow are coupled to the network and require simultaneous solution

### 26.6.3 Choke Optimization Strategy

The choke optimization problem is: given the network configuration and facility constraints, find the choke openings $x_1, x_2, \ldots, x_{N_w}$ that maximize total oil production:

$$
\max_{x_1, \ldots, x_{N_w}} \sum_{i=1}^{N_w} q_{o,i}(x_i, \mathbf{p})
$$

subject to facility constraints (gas handling, water handling, compression power) and individual well bounds.

The difficulty is that the pressures $\mathbf{p}$ depend on all the choke openings through the network equations. A change in one choke affects the pressures everywhere in the network.

A practical optimization approach is:

1. **Start from current operating point.** Read the current choke positions and production rates.
2. **Compute marginal oil gain.** For each well, estimate the incremental oil gained by opening the choke slightly (marginal rate of return).
3. **Rank wells by marginal gain.** The well with the highest marginal oil gain per unit of constraint consumption should be opened first.
4. **Iterate.** Open the best well slightly, re-solve the network, re-evaluate marginals, and repeat until all constraints are active.

This is the **equal marginal allocation** principle: at the optimum, the marginal return (oil per unit of gas handling capacity consumed, for example) should be equal across all wells.

**Execution scope:** This integration pattern algorithm requires caller well identities base rates and choke adapters. It is not a standalone validated process calculation.

```python pattern: algorithm requires caller well identities base rates and choke adapters
# Simplified choke optimization loop
def optimize_chokes(network, facility_gas_max, n_steps=20):
    """Optimize choke positions for maximum oil, subject to gas constraint."""
    well_names = network.getWellNames()

    for step in range(n_steps):
        # Evaluate marginal gains
        marginals = {}
        for well in well_names:
            current_cv = network.getChokeCv(well)
            # Small perturbation
            network.setChokeCv(well, current_cv * 1.05)
            network.run()
            dq_oil = network.getWellOilRate(well) - base_oil[well]
            dq_gas = network.getWellGasRate(well) - base_gas[well]
            # Restore
            network.setChokeCv(well, current_cv)

            if dq_gas > 0:
                marginals[well] = dq_oil / dq_gas  # oil per unit gas
            else:
                marginals[well] = float('inf')

        # Open the well with highest marginal return
        best_well = max(marginals, key=marginals.get)
        current_cv = network.getChokeCv(best_well)
        network.setChokeCv(best_well, current_cv * 1.10)
        network.run()

        # Check gas constraint
        total_gas = network.getTotalGasRate()
        if total_gas > facility_gas_max:
            # Revert and stop
            network.setChokeCv(best_well, current_cv)
            network.run()
            break

    return network
```

---

## 26.7 Gas Lift Optimization

### 26.7.1 Gas Lift Mechanism

Gas lift is an artificial lift method where gas is injected into the tubing through gas lift valves (or mandrels) at one or more depths. The injected gas reduces the effective fluid density in the tubing, reducing the hydrostatic head and thus the required bottomhole flowing pressure. This allows the well to produce at a higher rate (or to produce at all, in cases where natural flow has ceased).

### 26.7.2 Gas Lift Performance Curve

The relationship between gas lift injection rate $q_{gl}$ and oil production rate $q_o$ follows a characteristic diminishing-returns curve:

$$
q_{o} = q_{o,\text{max}} \left(1 - e^{-\alpha \cdot q_{gl}}\right)
$$

where $q_{o,\text{max}}$ is the maximum achievable oil rate with unlimited gas lift and $\alpha$ is a well-specific constant that depends on the well depth, tubing size, reservoir deliverability, and fluid properties.

The curve has three important regions:

1. **Low injection rate:** Each unit of injected gas produces a significant increment of oil. The gas lift is highly efficient.
2. **Optimal injection rate:** The point of maximum economic return, balancing the value of incremental oil against the cost of compression for the lift gas.
3. **High injection rate:** Diminishing returns — additional gas produces minimal incremental oil. Beyond a critical rate, friction effects from excessive gas velocity actually reduce oil production.

![Gas lift performance curve showing oil production rate as a function of gas lift injection rate, with the three characteristic regions marked.](figures/fig27_3_gaslift_curve.png)

### 26.7.3 Multi-Well Gas Lift Allocation

When multiple wells share a common source of lift gas (the gas compression system), the allocation problem is:

$$
\max_{q_{gl,1}, \ldots, q_{gl,N_w}} \sum_{i=1}^{N_w} q_{o,i}(q_{gl,i})
$$

subject to:

$$
\sum_{i=1}^{N_w} q_{gl,i} \leq Q_{gl,\text{available}}
$$

By the Lagrangian optimality condition, the optimal allocation is achieved when the marginal oil gain per unit of lift gas is equal across all wells:

$$
\frac{dq_{o,1}}{dq_{gl,1}} = \frac{dq_{o,2}}{dq_{gl,2}} = \cdots = \frac{dq_{o,N_w}}{dq_{gl,N_w}} = \lambda
$$

where $\lambda$ is the Lagrange multiplier representing the shadow price of lift gas. This is the **equal slope** principle for gas lift allocation.

### 26.7.4 Gas Lift Optimization Algorithm

The equal-slope principle leads to a practical algorithm:

1. **Compute gas lift performance curves** for each well (using NeqSim multiphase flow or measured data)
2. **Sort wells by initial marginal gain** (derivative of oil rate with respect to gas lift rate at zero injection)
3. **Allocate gas incrementally** to the well with the highest current marginal gain
4. **Re-evaluate marginals** after each increment (they decrease due to diminishing returns)
5. **Stop** when the total gas allocation equals the available supply

### 26.7.5 GasLiftNetworkOptimizer in NeqSim

NeqSim implements the equal-slope algorithm directly through `GasLiftPerformanceCurve` and `GasLiftNetworkOptimizer` (package `neqsim.process.fielddevelopment.integrated`). Each well is described by a performance curve — either from a measured lift-rate/oil-rate table or from a fitted exponential — and the optimizer distributes a fixed total lift-gas supply to maximize field oil:

```python
GasLiftPerformanceCurve = jneqsim.process.fielddevelopment.integrated.GasLiftPerformanceCurve
GasLiftNetworkOptimizer = jneqsim.process.fielddevelopment.integrated.GasLiftNetworkOptimizer

# Build per-well performance curves from lift-rate / oil-rate samples
curve_a = GasLiftPerformanceCurve(
    [0.0, 0.5e6, 1.0e6, 1.5e6, 2.0e6],     # lift gas (Sm3/d)
    [2400.0, 3200.0, 3700.0, 3950.0, 4050.0])  # oil (Sm3/d)
curve_b = GasLiftPerformanceCurve(
    [0.0, 0.5e6, 1.0e6, 1.5e6, 2.0e6],
    [1800.0, 2600.0, 3100.0, 3350.0, 3450.0])

optimizer = GasLiftNetworkOptimizer()
optimizer.addWell("Well-A", curve_a)
optimizer.addWell("Well-B", curve_b)

result = optimizer.allocate(2.5e6)
print("Lift allocation:", dict(result.getLiftRates()))
print("Oil rates:", dict(result.getOilRates()))
print("Total oil:", result.getTotalOil(), "Sm3/d")
print("Total lift used:", result.getTotalLift(), "Sm3/d")
```

The `AllocationResult` exposes `getLiftRates()`, `getOilRates()`, `getTotalOil()`, and `getTotalLift()`. Each `GasLiftPerformanceCurve` independently provides `oilRateAt(liftRate)`, `incrementalSlope(liftRate)`, `optimalLiftRate()`, `getMaxLiftRate()`, and `getBaseOilRate()` for plotting and diagnostics. Because the optimizer equalizes `incrementalSlope` across wells, the allocation it returns satisfies the equal-slope optimality condition derived above.

This greedy algorithm converges to the global optimum because the gas lift performance curves are concave (diminishing returns).

```python
import numpy as np

def gas_lift_allocation(wells, total_gas_available, n_increments=100):
    """
    Allocate gas lift optimally among wells using equal marginal principle.

    wells: list of dicts with 'name', 'q_max', 'alpha'
    total_gas_available: total lift gas available (Sm3/d)
    """
    increment = total_gas_available / n_increments
    allocation = {w['name']: 0.0 for w in wells}

    for _ in range(n_increments):
        # Compute marginal gain for each well
        best_well = None
        best_marginal = 0.0

        for w in wells:
            q_gl = allocation[w['name']]
            # Marginal: d(q_o)/d(q_gl) = q_max * alpha * exp(-alpha * q_gl)
            marginal = w['q_max'] * w['alpha'] * np.exp(-w['alpha'] * q_gl)
            if marginal > best_marginal:
                best_marginal = marginal
                best_well = w['name']

        if best_well is not None:
            allocation[best_well] += increment

    # Calculate resulting oil rates
    results = {}
    for w in wells:
        q_gl = allocation[w['name']]
        q_oil = w['q_max'] * (1.0 - np.exp(-w['alpha'] * q_gl))
        results[w['name']] = {'gas_lift': q_gl, 'oil_rate': q_oil}

    return results

# Example: Three wells competing for 500,000 Sm3/d of lift gas
wells = [
    {'name': 'Well-A', 'q_max': 3000.0, 'alpha': 0.000008},
    {'name': 'Well-B', 'q_max': 2500.0, 'alpha': 0.000012},
    {'name': 'Well-C', 'q_max': 1800.0, 'alpha': 0.000006},
]

results = gas_lift_allocation(wells, 500000.0)
for name, r in results.items():
    print(f"  {name}: GL = {r['gas_lift']:.0f} Sm3/d, "
          f"Oil = {r['oil_rate']:.0f} Sm3/d")
```

---

## 26.8 Network Constraints and Back-Pressure Effects

### 26.8.1 Manifold Pressure Constraints

In a subsea gathering system, the manifold pressure is determined by the balance between the inflow from the wells and the outflow through the export riser/pipeline. Increasing the total production rate increases the manifold pressure because:

- More fluid must be transported through the export line, requiring a higher driving pressure
- The friction losses in the export line increase with the square of the velocity

The manifold pressure in turn affects all connected wells — higher manifold pressure means higher wellhead pressure, which reduces the pressure drawdown on each well and thus the deliverability.

### 26.8.2 Riser Base Pressure

For platforms with risers, the riser base pressure adds to the manifold pressure requirement. The riser must overcome both friction and the hydrostatic head of the fluid column. For deep-water applications (1000+ m water depth), the riser head can be 50–100 bara, significantly affecting the network pressure balance.

### 26.8.3 Topside Separator Pressure

The separator pressure at the platform sets the downstream boundary condition for the gathering network. Reducing the separator pressure reduces the back-pressure on all wells, increasing total production. However, separator pressure cannot be reduced below:

- The minimum pressure for gas export compression (suction pressure limit)
- The bubble point pressure at separator temperature (to maintain single-phase liquid oil)
- The pressure required for downstream equipment operation

The optimal separator pressure balances well deliverability against downstream processing requirements and is typically a key optimization variable.

### 26.8.4 Quantifying Back-Pressure Effects

The back-pressure sensitivity can be quantified by the **deliverability index** $\partial q_{\text{total}} / \partial p_{\text{sep}}$, which measures how much total production changes per unit change in separator pressure:

$$
\frac{\partial Q_{\text{total}}}{\partial p_{\text{sep}}} = \sum_{i=1}^{N_w} \frac{\partial q_i}{\partial p_{\text{sep}}}
$$

This sensitivity is negative (lower separator pressure yields more production) and its magnitude depends on the network geometry and well characteristics. Typical values range from 50–500 Sm³/d per bar for oil-producing platforms.

```python
# Read current gathering-network results on their mass-flow basis.
for name in network.getPipeNames():
    print(name, network.getPipeFlowRate(name), "kg/s",
          network.getPipeVelocity(name), "m/s")
print("Platform pressure:", network.getNodePressure("Platform"), "bara")
```

---

## 26.9 Multi-Well Optimization Algorithms

### 26.9.1 Equal Marginal Allocation

The **equal marginal principle** states that at the optimum, the marginal value of production from each well (oil gained per unit of constraining resource consumed) should be equal across all wells. For a gas-handling constraint:

$$
\frac{\partial q_{o,i} / \partial q_i}{\partial q_{g,i} / \partial q_i} = \lambda_g \quad \forall i
$$

where $\lambda_g$ is the shadow price of gas handling capacity. Wells with high oil cut and low GOR have high marginal value — they contribute more oil per unit of gas capacity consumed — and should be produced preferentially.

### 26.9.2 Sequential Rate Bumping

A practical implementation of the equal marginal principle is **sequential rate bumping**:

1. Start with all wells at minimum stable rate
2. Compute the marginal value for each well (incremental oil per incremental constraint consumption)
3. Increase the rate of the well with the highest marginal value by a small increment
4. Re-solve the network to account for back-pressure coupling
5. Re-evaluate marginals
6. Repeat until a constraint is reached

This algorithm naturally handles multiple constraints — as the gas handling constraint tightens, the algorithm shifts production toward wells with lower GOR. As the water handling constraint tightens, it shifts toward wells with lower water cut.

### 26.9.3 Network LP/NLP Formulation

For larger networks (10+ wells) with many constraints, formal mathematical programming is more efficient than sequential bumping. The network optimization can be formulated as a **nonlinear program (NLP)**:

$$
\max_{\mathbf{x}} \quad f(\mathbf{x})
$$

subject to:

$$
\mathbf{g}(\mathbf{x}) \leq \mathbf{0} \quad \text{(inequality constraints)}
$$

$$
\mathbf{h}(\mathbf{x}) = \mathbf{0} \quad \text{(network equations)}
$$

$$
\mathbf{x}_L \leq \mathbf{x} \leq \mathbf{x}_U \quad \text{(bounds)}
$$

where $\mathbf{x}$ is the vector of decision variables (choke positions), $f$ is the objective (total oil rate), $\mathbf{g}$ represents facility constraints, and $\mathbf{h}$ represents the network pressure-flow equations.

The NLP can be solved using gradient-based methods (SQP, interior point) if the Jacobian of the network equations is available, or using derivative-free methods (Nelder-Mead, pattern search) if the network solver is treated as a black box.

### 26.9.4 Integration with ProductionOptimizer

NeqSim's `ProductionOptimizer` (Chapter 25) can be applied to well network optimization by defining the network as the `ProcessSystem` and the choke positions as decision variables:

```python
# For facility-aware network allocation, supply an explicit candidate evaluator.
# ProductionOptimizer itself takes ProcessSystem/ProcessModel, not a network constructor.
# This executable allocation example uses the supplied gas-lift response curves.
allocation = GasLiftNetworkOptimizer()
allocation.addWell("Well-A", curve_a)
allocation.addWell("Well-B", curve_b)
answer = allocation.allocate(2.5e6)
assert answer.getTotalLift() <= 2.5e6 * (1 + 1e-9)
print("Allocated oil:", answer.getTotalOil(), "Sm3/day")
```

### 26.9.5 NetworkAllocationOptimizer and the IntegratedProductionModel

For the pure allocation problem — splitting a fixed total (lift gas, water-injection volume, or a shared compression duty) across several legs to maximize a single objective — NeqSim provides the lightweight `NetworkAllocationOptimizer` (package `neqsim.process.fielddevelopment.integrated`). It takes the total to be allocated and the number of legs, accepts per-leg bounds, and drives a user-supplied evaluator:

```python
NetworkAllocationOptimizer = jneqsim.process.optimization.valuechain.NetworkAllocationOptimizer
allocation_optimizer = NetworkAllocationOptimizer(2.5e6, 3)
for leg in range(3):
    allocation_optimizer.setBounds(leg, 0.0, 1.2e6)
allocation_optimizer.setTolerance(1e-4)
# Explicit diminishing-return utility; illustrative, not simulated oil production.
def allocation_value(values):
    score = sum((i + 1.0) * (max(0.0, float(value)) ** 0.5)
               for i, value in enumerate(values))
    return NetworkAllocationOptimizer.AllocationResult(values, score, True)
answer = allocation_optimizer.optimize(allocation_value)
print(list(answer.getAllocation()), answer.getObjective(), answer.isFeasible())
```

When the wells and network are described physically rather than as black-box curves, the `IntegratedProductionModel` couples reservoir drives, well deliverability curves, and the export node into a single converged solution. It is solved with a Newton method (`NetworkNewtonSolver`) over the network nodes and branches:

```python
MaterialBalanceGasDrive = jneqsim.process.fielddevelopment.integrated.MaterialBalanceGasDrive
driveA = MaterialBalanceGasDrive(250.0, 5.0e9, 0.90)
driveB = MaterialBalanceGasDrive(220.0, 3.0e9, 0.90)
curveA = WellDeliverabilityCurve.fromVogel(2.0e6, 250.0)
curveB = WellDeliverabilityCurve.fromVogel(1.5e6, 220.0)
IntegratedProductionModel = jneqsim.process.fielddevelopment.integrated.IntegratedProductionModel

model = IntegratedProductionModel("Field")
model.addWell("Well-A", driveA, curveA)     # ReservoirDrive + WellDeliverabilityCurve
model.addWell("Well-B", driveB, curveB)
model.setExportPressure(90.0)               # bara
model.setHydrocarbonPrice(3.0)              # per Sm3
model.setEnergyIntensity(0.12)              # kWh/Sm3
model.setEmissionIntensity(0.02)            # kg CO2/Sm3

solve = model.solve()
print("Converged:", solve.isConverged(), "in", solve.getIterations(), "iters")
print("Field rate:", solve.getFieldRate(), "Sm3/d")
print("Well rates:", dict(solve.getWellRates()))
print("Revenue:", solve.getRevenue(), "energy:", solve.getEnergyKWhPerDay(), "kWh/d")
```

`IntegratedSolveResult` reports `isConverged()`, `getIterations()`, `getFieldRate()`, `getWellRates()`, `getNodePressures()`, `getRevenue()`, `getEnergyKWhPerDay()`, and `getEmissionsKgPerDay()`. The model can also project a full production profile with `runProfile(years, dtYears)`, which honours reservoir-pressure depletion through the attached `ReservoirDrive` objects (material-balance gas drive, oil-tank drive, or aquifer drive). The same `IntegratedProductionModel` is the foundation for the reservoir-to-market optimization of Chapter 28.

---

## 26.10 Subsea Network Optimization

Subsea production systems introduce additional challenges and optimization variables compared to platform-based wells.

### 26.10.1 Long Tiebacks

Long subsea tiebacks (20–100+ km) have high pressure losses in the flowline, which significantly reduces well deliverability. The pressure budget must accommodate:

- Hydrostatic head in the riser
- Friction losses in the tieback flowline
- Arrival pressure at the host facility

For long tiebacks, the arrival pressure often limits production before any facility equipment constraint is reached. Subsea boosting (pumps or compressors on the seabed) can recover the pressure lost in the flowline.

### 26.10.2 Subsea Boosting

Subsea multiphase boosting increases the pressure available for transport, effectively extending the economic reach of a tieback. The booster pump or compressor is modeled as a pressure-increasing element in the network:

$$
p_{\text{out}} = p_{\text{in}} + \Delta p_{\text{boost}}
$$

The optimization must determine the optimal boost pressure, balancing incremental production against booster power consumption and reliability considerations. Subsea equipment has limited intervention options, so reliability-driven constraints are more restrictive than for topside equipment.

### 26.10.3 Manifold Routing

When multiple wells connect to multiple manifolds with routing options (switchable flowlines), the routing decision becomes a discrete optimization variable. The network solver must evaluate different routing configurations to find the one that maximizes total production.

### 26.10.4 Flow Assurance Constraints

Subsea networks have flow assurance constraints that do not apply to topside systems:

- **Hydrate avoidance:** The fluid temperature must remain above the hydrate equilibrium temperature at the pipeline pressure, or sufficient inhibitor must be injected.
- **Wax deposition:** The fluid temperature must remain above the wax appearance temperature, or pigging frequency must be adequate.
- **Minimum flow rate:** Below a minimum rate, the fluid cools excessively in the flowline, violating hydrate or wax constraints.

These constraints effectively impose a **minimum production rate** on each well or flowline, which interacts with the optimization:

$$
q_i \geq q_{i,\text{min,flow-assurance}} \quad \text{or} \quad q_i = 0 \quad \text{(shut-in)}
$$

The discrete choice between "produce above minimum" and "shut in" makes the optimization a mixed-integer problem.

---

## 26.11 Case Study: 6-Well Platform Optimization

This comprehensive case study demonstrates multi-well optimization on a platform receiving production from six subsea wells with different characteristics.

### 26.11.1 Well Characteristics

| Well | Reservoir Pressure (bara) | $q_{o,\text{max}}$ (Sm³/d) | GOR (Sm³/Sm³) | Water Cut (%) | IPR Model |
|------|--------------------------|---------------------------|---------------|---------------|-----------|
| P-1 | 280 | 4500 | 120 | 5 | Vogel |
| P-2 | 260 | 3800 | 180 | 15 | Vogel |
| P-3 | 245 | 3200 | 250 | 30 | Vogel |
| P-4 | 300 | 5000 | 100 | 8 | Vogel |
| P-5 | 230 | 2800 | 200 | 45 | Vogel |
| P-6 | 270 | 4200 | 150 | 12 | Vogel |

### 26.11.2 Facility Constraints

| Constraint | Capacity | Unit |
|-----------|----------|------|
| Gas handling (separator + compressor) | 3,500,000 | Sm³/d |
| Water treatment | 8,000 | Sm³/d |
| Export compression power | 18 | MW |
| Oil export | 25,000 | Sm³/d |

### 26.11.3 Unconstrained Production

If all wells produce at their maximum rate (no facility constraints), the total production would be:

$$
Q_{o,\text{unconstrained}} = \sum_{i=1}^{6} q_{o,i,\text{max}} = 4500 + 3800 + 3200 + 5000 + 2800 + 4200 = 23{,}500 \text{ Sm³/d}
$$

With corresponding gas and water production that may exceed facility constraints.

### 26.11.4 Constrained Optimization

The optimization identifies which wells to choke and by how much:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import numpy as np

LoopedPipeNetwork = jneqsim.process.equipment.network.LoopedPipeNetwork

# Build the 6-well network
network = LoopedPipeNetwork("Platform Network")

# Create fluid and configure network...
# (fluid creation and network setup as shown in Section 26.5)

# Well data
wells = [
    {"name": "P-1", "Pr": 280.0, "qmax": 4500.0, "GOR": 120, "WC": 0.05},
    {"name": "P-2", "Pr": 260.0, "qmax": 3800.0, "GOR": 180, "WC": 0.15},
    {"name": "P-3", "Pr": 245.0, "qmax": 3200.0, "GOR": 250, "WC": 0.30},
    {"name": "P-4", "Pr": 300.0, "qmax": 5000.0, "GOR": 100, "WC": 0.08},
    {"name": "P-5", "Pr": 230.0, "qmax": 2800.0, "GOR": 200, "WC": 0.45},
    {"name": "P-6", "Pr": 270.0, "qmax": 4200.0, "GOR": 150, "WC": 0.12},
]

# Compute marginal value: oil per unit gas capacity consumed
for w in wells:
    # Oil production per total fluid (accounting for water)
    oil_fraction = 1.0 - w["WC"]
    # Gas per unit oil
    gas_per_oil = w["GOR"]
    # Marginal value: oil gained per unit gas consumed
    w["marginal_value"] = oil_fraction / gas_per_oil

# Rank wells by marginal value (highest first)
wells_ranked = sorted(wells, key=lambda w: w["marginal_value"], reverse=True)

print("Well Ranking by Marginal Value (oil per gas capacity):")
print(f"{'Rank':<6} {'Well':<8} {'GOR':<8} {'WC':<8} {'Marginal':>10}")
for i, w in enumerate(wells_ranked, 1):
    print(f"{i:<6} {w['name']:<8} {w['GOR']:<8} "
          f"{w['WC']:<8.0%} {w['marginal_value']:>10.4f}")
```

### 26.11.5 Optimization Results

The optimization reveals:

- **Wells P-4 and P-1** should produce at or near maximum rate — they have low GOR and low water cut, giving the highest oil production per unit of constraint consumption.
- **Well P-6** should produce at high rate — moderate GOR and low water cut.
- **Well P-3** should be significantly choked — high GOR (250 Sm³/Sm³) consumes disproportionate gas handling capacity.
- **Well P-5** should be choked or considered for shut-in — high water cut (45%) consumes water treatment capacity while contributing relatively little oil.
- **Well P-2** produces at moderate rate — intermediate GOR and water cut.

| Well | Unconstrained Rate | Optimized Rate | Choke Status | Limiting Factor |
|------|-------------------|----------------|-------------|-----------------|
| P-4 | 5,000 | 4,800 | Nearly full open | — |
| P-1 | 4,500 | 4,300 | Nearly full open | — |
| P-6 | 4,200 | 3,800 | Slightly choked | Gas handling |
| P-2 | 3,800 | 2,900 | Choked | Gas handling |
| P-3 | 3,200 | 1,800 | Heavily choked | Gas handling |
| P-5 | 2,800 | 1,200 | Heavily choked | Water treatment |
| **Total** | **23,500** | **18,800** | — | Gas handling (active) |

The optimized total oil production is 18,800 Sm³/d — a 20% reduction from the unconstrained sum, but this is the maximum achievable within facility limits. Attempting to produce 23,500 Sm³/d would violate both the gas handling and water treatment constraints.

### 26.11.6 Sensitivity Analysis

The case study reveals important sensitivities:

**Gas handling capacity expansion:** Increasing gas handling by 10% (to 3,850,000 Sm³/d) allows an additional 1,200 Sm³/d of oil production — primarily by relaxing the choke on Wells P-3 and P-2.

**Separator pressure reduction:** Reducing separator pressure from 65 to 55 bara increases total oil by approximately 800 Sm³/d by improving well deliverability across all wells.

**Well P-5 shut-in:** Shutting in Well P-5 and redistributing its gas capacity to other wells produces almost the same total oil with significantly less water to treat. This may be the preferred strategy when water treatment is the binding constraint.

---


<!-- September 2026 source update -->
## Network-to-facility boundaries and qualified well curves

The newest VFP contract separates network/facility pressure requirements from qualified well bottomhole pressure. A gathering-network outlet condition or process capacity table cannot be relabelled as BHP. Establish the well datum, tubing geometry, thermal boundary conditions, friction and hydrostatic losses, fluid recombination and standard phase-volume rate before constructing a reservoir-compatible table \cite{neqsim2026update}.

Gas-lift allocation also requires two distinct balances: injected lift gas and produced reservoir gas. An allocation curve is usable only over its stated valid range and operating boundary conditions. Separator pressure changes can alter every well's backpressure and therefore invalidate a previously fitted allocation curve. After allocating gas, replay the coupled well/network/facility state and check compressor, separator, export and shared-resource restrictions together.

The polynomial and equal-slope examples in this chapter are optimization demonstrations. Their numerical response is not a replacement for calibrated tubing hydraulics. Preserve that distinction when producing a forecast or comparing a platform-pressure change with an artificial-lift investment.

---

## 26.12 Summary

This chapter has developed the theory and practice of well and network optimization for production facilities:

- **The well allocation problem** is a nonlinear constrained optimization where the decision variables are well rates or choke positions, the objective is total oil production, and the constraints are facility equipment capacities.
- **Inflow Performance Relationships** (Vogel, Fetkovich, Jones) describe well deliverability as a function of flowing pressure. Coupling IPR with tubing performance (nodal analysis) determines the natural flow rate for a given wellhead pressure.
- **VFP tables** pre-compute tubing performance across a range of conditions, enabling efficient well modeling in network solvers and reservoir simulators. NeqSim generates these tables through `MultiScenarioVFPGenerator` and `PipeBeggsAndBrills`.
- **The `LoopedPipeNetwork`** solves coupled pressure-flow equations for multi-well gathering systems, capturing the critical back-pressure coupling that makes individual well optimization insufficient.
- **Choke optimization** adjusts well choke valves to maximize total production. The valve Cv model, critical vs. subcritical flow regimes, and the equal marginal allocation principle provide the theoretical foundation.
- **Gas lift optimization** allocates limited lift gas among wells using the equal-slope principle — at the optimum, the marginal oil gain per unit of lift gas should be equal across all wells.
- **Network constraints** — manifold pressure, riser base pressure, and separator pressure — couple the wells and create back-pressure effects that must be captured by the network solver.
- **Subsea networks** add long tieback pressure losses, subsea boosting, and flow assurance constraints (hydrate, wax) that impose minimum flow rates and mixed-integer decisions.

The case study demonstrated that well allocation optimization can recover significant production compared to naive equal-rate or proportional-rate strategies, particularly when wells have different GOR and water cut characteristics.

---

## Exercises

**Exercise 26.1.** A well has a reservoir pressure of 300 bara and the following test data: at $p_{wf} = 200$ bara, $q_o = 2{,}500$ Sm³/d. (a) Using Vogel's equation, calculate $q_{o,\text{max}}$. (b) Calculate the production rate at $p_{wf} = 150$ bara. (c) Plot the IPR curve from $p_{wf} = 0$ to $p_{wf} = 300$ bara.

**Exercise 26.2.** Two wells share a common manifold and export pipeline to a platform. Well-1 has $q_{o,\text{max}} = 4000$ Sm³/d and GOR = 150 Sm³/Sm³. Well-2 has $q_{o,\text{max}} = 3000$ Sm³/d and GOR = 300 Sm³/Sm³. The facility gas handling limit is 800,000 Sm³/d. (a) Calculate the unconstrained total oil production. (b) Using the equal marginal principle, determine the optimal allocation between the two wells. (c) What is the optimized total oil rate?

**Exercise 26.3.** Write a Python script using NeqSim to build a 3-well gathering network with the `LoopedPipeNetwork` class. The wells have reservoir pressures of 250, 270, and 230 bara, maximum rates of 3000, 4000, and 2500 Sm³/d (Vogel IPR), tubing depths of 3000, 3500, and 2800 m, and flowline lengths of 5, 8, and 3 km to a common manifold. Solve the network for separator pressures of 50, 60, 70, and 80 bara and plot total oil production vs. separator pressure.

**Exercise 26.4.** Three wells require gas lift. Their performance curves are described by $q_o = q_{o,\text{max}}(1 - e^{-\alpha q_{gl}})$ with parameters: Well-A ($q_{o,\text{max}} = 2000$ Sm³/d, $\alpha = 10^{-5}$ d/Sm³), Well-B ($q_{o,\text{max}} = 3000$ Sm³/d, $\alpha = 8 \times 10^{-6}$ d/Sm³), Well-C ($q_{o,\text{max}} = 1500$ Sm³/d, $\alpha = 1.5 \times 10^{-5}$ d/Sm³). Total available lift gas is 300,000 Sm³/d. (a) Determine the optimal allocation using the equal-slope principle. (b) Compare with equal allocation (100,000 Sm³/d each). (c) What is the incremental oil production from optimal vs. equal allocation?

**Exercise 26.5.** A subsea well is connected to a host platform 25 km away through a 10-inch flowline. The well's maximum rate is 5000 Sm³/d of oil with GOR = 200 Sm³/Sm³ and water cut = 20%. The seawater temperature is 4°C and the hydrate formation temperature at pipeline pressure is 18°C. (a) Using NeqSim, calculate the arrival temperature as a function of flow rate (from 1000 to 5000 Sm³/d). (b) Determine the minimum flow rate to maintain the fluid above the hydrate temperature. (c) If this minimum flow exceeds the economically optimal rate, what mitigation options exist?

**Exercise 26.6.** Consider the 6-well case study from Section 26.11. The water treatment capacity is increased from 8,000 to 12,000 Sm³/d through a modular expansion. (a) Re-optimize the well allocation with the new water constraint. (b) Which wells benefit most from the expansion? (c) What is the incremental oil production? (d) Is the expansion justified if the incremental oil is valued at $70/bbl and the expansion costs $15M with a 3-year payback requirement?

---

## References

1. Beggs, H.D. (2003). *Production Optimization Using NODAL Analysis*. 2nd ed. OGCI Publications.
2. Brown, K.E. (1984). *The Technology of Artificial Lift Methods, Volume 4*. PennWell Publishing.
3. Economides, M.J., Hill, A.D., Ehlig-Economides, C., and Zhu, D. (2013). *Petroleum Production Systems*. 2nd ed. Prentice Hall.
4. Guo, B., Lyons, W.C., and Ghalambor, A. (2007). *Petroleum Production Engineering: A Computer-Assisted Approach*. Elsevier.
5. Brill, J.P. and Mukherjee, H. (1999). *Multiphase Flow in Wells*. SPE Monograph Vol. 17.
6. Beggs, H.D. and Brill, J.P. (1973). "A Study of Two-Phase Flow in Inclined Pipes." *Journal of Petroleum Technology*, 25(5), 607–617.
7. Vogel, J.V. (1968). "Inflow Performance Relationships for Solution-Gas Drive Wells." *Journal of Petroleum Technology*, 20(1), 83–92.
8. Fetkovich, M.J. (1973). "The Isochronal Testing of Oil Wells." SPE Paper 4529. Fall Meeting of SPE.
9. Jones, L.G., Blount, E.M., and Glaze, O.H. (1976). "Use of Short Term Multiple Rate Flow Tests to Predict Performance of Wells Having Turbulence." SPE Paper 6133.
10. Bai, Y. and Bai, Q. (2019). *Subsea Engineering Handbook*. 2nd ed. Gulf Professional Publishing.
11. Mokhatab, S., Poe, W.A., and Mak, J.Y. (2019). *Handbook of Natural Gas Transmission and Processing*. 4th ed. Gulf Professional Publishing.
12. Jansen, J.D. (2017). *Nodal Analysis of Oil and Gas Production Systems*. SPE Textbook Series Vol. 14.
13. API RP 14E (2007). *Recommended Practice for Design and Installation of Offshore Production Platform Piping Systems*. American Petroleum Institute.
14. Schlumberger (2014). *PIPESIM User Guide: Steady-State Multiphase Flow Simulator*. Schlumberger Information Solutions.
15. Litvak, M.L. and Darlow, B.L. (1995). "Surface Network and Well Tubinghead Pressure Constraints in Compositional Simulation." SPE Paper 29125.


## Figures

![Figure 26.1: Choke Sensitivity](figures/ch27_choke_sensitivity.png)

*Figure 26.1: Choke Sensitivity*

![Figure 26.2: Manifold Pressure Sweep](figures/ch27_manifold_pressure_sweep.png)

*Figure 26.2: Manifold Pressure Sweep*
