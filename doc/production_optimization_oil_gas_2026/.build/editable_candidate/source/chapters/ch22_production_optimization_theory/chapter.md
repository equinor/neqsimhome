# Production Optimization Theory and Methods

<!-- Chapter metadata -->
<!-- Notebooks: ch19_separator_pressure_optimization.ipynb, ch19_gas_lift_allocation.ipynb, ch19_compressor_setpoint_optimization.ipynb -->
<!-- Estimated pages: 28 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Formulate a production optimization problem with objective function, decision variables, and constraints
2. Classify optimization problems in oil and gas production (well allocation, gas lift, separator pressure, compressor set points, routing)
3. Apply NODAL analysis principles to identify the optimal operating point for individual wells and integrated production systems
4. Describe gradient-based, derivative-free, evolutionary, and surrogate-based optimization methods and their suitability for different problem types
5. Formulate and solve multi-objective optimization problems balancing competing goals (production rate, gas export quality, energy consumption)
6. Explain real-time optimization (RTO) architecture and the differences between steady-state and dynamic optimization
7. Implement parametric sweeps and optimization routines using NeqSim for separator pressure optimization, gas lift allocation, and compressor set point optimization
8. Understand robust optimization under uncertainty and integrated asset modeling concepts

---

## 22.1 Introduction

Production optimization is the systematic process of finding operating conditions that maximize a chosen objective (typically production rate, revenue, or recovery factor) while satisfying all equipment, safety, and contractual constraints. It is both a theoretical discipline — rooted in mathematical programming — and a practical operational activity performed daily on producing fields.

The fundamental question of production optimization is deceptively simple:

> *Given the current state of the reservoir, wells, and facilities, what are the best operating set points?*

The difficulty lies in the complexity of the system: a typical offshore platform may have 10–30 wells, 20–50 process equipment items, hundreds of control valves, and thousands of possible combinations of set points. The process is nonlinear, coupled, and constrained. Reservoir behavior is uncertain. Equipment degrades over time. Contractual obligations impose hard limits.

This chapter presents the mathematical foundations of production optimization, surveys the main algorithmic approaches, and demonstrates practical optimization workflows using NeqSim process simulation.

### 22.1.1 The Role of Process Simulation in Optimization

Process simulation is the engine that drives production optimization. Given a set of decision variables (pressures, temperatures, flow rates, valve positions), the process simulator computes:

- The resulting production rates (oil, gas, water, condensate)
- The quality of the products (gas dew point, oil BS&W, water quality)
- The energy consumption (compressor power, pump power, heating/cooling duties)
- Whether all equipment constraints are satisfied (capacity limits from Chapter 18)

The optimizer explores the decision variable space, calling the simulator at each point to evaluate the objective function, and iteratively moves toward the optimum.

$$
\text{Optimizer} \xrightarrow{\text{set points}} \text{Process Simulator} \xrightarrow{\text{performance}} \text{Optimizer}
$$

### 22.1.2 Scope of Production Optimization

Production optimization spans multiple timescales:

| Timescale | Optimization Task | Decision Variables | Frequency |
|-----------|-------------------|-------------------|-----------|
| Minutes | Well choke adjustment | Individual well chokes | Real-time |
| Hours | Gas lift allocation | Gas lift rates per well | Several times daily |
| Days | Separator pressure optimization | Stage pressures | Daily to weekly |
| Weeks | Routing optimization | Well-to-manifold assignments | Weekly to monthly |
| Months | Compressor configuration | Number of stages, speeds | Seasonal |
| Years | Facility modification | Equipment upgrades | Annual review |

This chapter focuses primarily on the daily-to-weekly operational optimization timescale, where process simulation is most directly applicable.

---

## 22.2 Mathematical Formulation

### 22.2.1 The General Optimization Problem

A production optimization problem has the standard form:

$$
\max_{x} \quad f(x)
$$

$$
\text{subject to:} \quad g_i(x) \leq 0, \quad i = 1, \ldots, m
$$

$$
h_j(x) = 0, \quad j = 1, \ldots, p
$$

$$
x^L \leq x \leq x^U
$$

where:

- $x \in \mathbb{R}^n$ is the vector of **decision variables** (set points, valve positions, flow rates)
- $f(x)$ is the **objective function** (production rate, revenue, efficiency)
- $g_i(x) \leq 0$ are **inequality constraints** (equipment capacity limits, quality specifications)
- $h_j(x) = 0$ are **equality constraints** (material balances, energy balances — typically handled implicitly by the process simulator)
- $x^L$ and $x^U$ are the **lower and upper bounds** on the decision variables

### 22.2.2 Objective Functions

The choice of objective function defines what "optimal" means. Common objectives in production optimization include:

**Maximum oil production rate:**

$$
f(x) = Q_{\text{oil}}(x) \quad [\text{Sm}^3/\text{day}]
$$

**Maximum revenue:**

$$
f(x) = P_{\text{oil}} \cdot Q_{\text{oil}}(x) + P_{\text{gas}} \cdot Q_{\text{gas}}(x) - C_{\text{opex}}(x)
$$

where $P_{\text{oil}}$ and $P_{\text{gas}}$ are the prices of oil and gas, and $C_{\text{opex}}$ includes energy costs, chemical injection costs, etc.

**Maximum recovery factor:**

$$
f(x) = \frac{\int_0^T Q_{\text{oil}}(x, t) \, dt}{\text{STOIIP}}
$$

**Minimum specific energy consumption:**

$$
f(x) = \frac{W_{\text{total}}(x)}{Q_{\text{oil}}(x) + Q_{\text{gas,export}}(x)} \quad [\text{kWh/Sm}^3]
$$

### 22.2.3 Decision Variables

Common decision variables in production optimization:

| Category | Decision Variables | Typical Range |
|----------|-------------------|---------------|
| Well control | Wellhead choke opening (%) | 0–100% |
| Gas lift | Gas lift rate per well (MSm³/d) | 0–0.5 |
| Separation | Stage pressures (bara) | 5–80 |
| Compression | Compressor speed (rpm) or set point | 70–105% of design |
| Heat exchange | Cooling medium flow rate | 50–120% of design |
| Routing | Well-to-manifold assignment | Binary (0/1) |

### 22.2.4 Constraints

Constraints represent physical, safety, and contractual limits:

**Equipment capacity constraints** (from Chapter 18):

$$
U_i(x) \leq U_{i,\text{max}}, \quad \text{for all equipment } i
$$

**Quality constraints:**

$$
\text{HHV}(x) \geq \text{HHV}_{\text{min}} \quad \text{(gas heating value)}
$$

$$
\text{HCDP}(x) \leq \text{HCDP}_{\text{max}} \quad \text{(hydrocarbon dew point)}
$$

$$
\text{H}_2\text{S}(x) \leq \text{H}_2\text{S}_{\text{max}} \quad \text{(hydrogen sulfide content)}
$$

**Contractual constraints:**

$$
Q_{\text{gas,export}}(x) \geq Q_{\text{DCQ}} \quad \text{(daily contracted quantity)}
$$

**Safety constraints:**

$$
P_i(x) \leq P_{i,\text{MAOP}}, \quad T_i(x) \leq T_{i,\text{max}}
$$

---

## 22.3 NODAL Analysis and System Optimization

### 22.3.1 NODAL Analysis Fundamentals

NODAL analysis (also called systems analysis) is a foundational technique for production optimization. It views the entire production system — reservoir, well, flowline, and facility — as a network of nodes connected by pressure-drop elements. At any node, the pressure from the upstream elements (inflow) must equal the pressure from the downstream elements (outflow).

The **inflow performance relationship** (IPR) describes the reservoir deliverability:

$$
Q = J \cdot (P_R - P_{wf}) \quad \text{(for undersaturated oil)}
$$

or for gas wells using the backpressure equation:

$$
Q = C \cdot (P_R^2 - P_{wf}^2)^n
$$

where $Q$ is the flow rate, $J$ is the productivity index, $P_R$ is the reservoir pressure, $P_{wf}$ is the bottomhole flowing pressure, $C$ is the backpressure coefficient, and $n$ is the backpressure exponent (0.5–1.0).

The **tubing performance relationship** (TPR) or vertical lift performance (VLP) describes the pressure loss from bottomhole to wellhead:

$$
P_{wf} = P_{wh} + \Delta P_{\text{gravity}} + \Delta P_{\text{friction}} + \Delta P_{\text{acceleration}}
$$

The operating point is found at the intersection of the IPR and TPR curves — the point where the reservoir can deliver fluid at the same rate that the tubing can transport it.

### 22.3.2 System Node Selection

The choice of solution node affects the optimization. Common node locations:

| Node Location | Inflow Curve | Outflow Curve |
|--------------|-------------|---------------|
| Bottomhole | IPR | TPR + flowline + facility |
| Wellhead | IPR + tubing | Flowline + facility |
| Separator inlet | IPR + tubing + flowline | Separator + downstream |
| Export | Entire upstream | Pipeline + sales |

### 22.3.3 Multi-Well System Optimization

For a multi-well system converging at a common manifold, the optimization problem becomes:

$$
\max \quad \sum_{w=1}^{N_w} Q_{\text{oil},w}(P_{wh,w}, Q_{\text{GL},w})
$$

subject to:

$$
\sum_{w=1}^{N_w} Q_{\text{gas},w} \leq Q_{\text{gas,max}} \quad \text{(gas handling capacity)}
$$

$$
\sum_{w=1}^{N_w} Q_{\text{liq},w} \leq Q_{\text{liq,max}} \quad \text{(liquid handling capacity)}
$$

$$
\sum_{w=1}^{N_w} Q_{\text{GL},w} \leq Q_{\text{GL,total}} \quad \text{(total available gas lift)}
$$

This is a resource allocation problem — distributing scarce resources (gas lift gas, processing capacity) among competing wells to maximize total production.

### 22.3.4 NeqSim NODAL Analysis Example

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Simple NODAL analysis: find operating point for a gas well

# Well IPR parameters (backpressure equation)
P_res = 250.0  # bara, reservoir pressure
C_ipr = 0.0035  # backpressure coefficient (MSm3/d)/(bara^2)^n
n_ipr = 0.85    # backpressure exponent

# Define gas composition
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 90.0, 200.0)
gas.addComponent("methane", 0.88)
gas.addComponent("ethane", 0.06)
gas.addComponent("propane", 0.03)
gas.addComponent("CO2", 0.02)
gas.addComponent("nitrogen", 0.01)
gas.setMixingRule("classic")

# IPR: calculate flow rate vs bottomhole pressure
import math

P_wf_range = [50, 75, 100, 125, 150, 175, 200, 225]
Q_ipr = []
for P_wf in P_wf_range:
    Q = C_ipr * (P_res**2 - P_wf**2)**n_ipr
    Q_ipr.append(Q)

print("IPR (Reservoir Deliverability):")
print(f"{'P_wf (bara)':<15} {'Q (MSm³/d)':<15}")
for P, Q in zip(P_wf_range, Q_ipr):
    print(f"{P:<15.0f} {Q:<15.2f}")

# VLP/TPR: use NeqSim pipe model for wellbore pressure drop
# At each flow rate, compute the required bottomhole pressure
# to deliver that rate to the wellhead
P_wh_target = 80.0  # bara, required wellhead pressure

Q_tpr = []
P_wf_tpr = []

for Q_test in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
    fl = jneqsim.thermo.system.SystemSrkEos(273.15 + 90.0, P_wh_target)
    fl.addComponent("methane", 0.88)
    fl.addComponent("ethane", 0.06)
    fl.addComponent("propane", 0.03)
    fl.addComponent("CO2", 0.02)
    fl.addComponent("nitrogen", 0.01)
    fl.setMixingRule("classic")

    stream = jneqsim.process.equipment.stream.Stream("Well Flow", fl)
    stream.setFlowRate(Q_test, "MSm3/day")
    stream.setTemperature(90.0, "C")
    stream.setPressure(P_wh_target, "bara")

    # Wellbore modeled as a vertical pipe
    wellbore = jneqsim.process.equipment.pipeline.PipeBeggsAndBrills(
        "Wellbore", stream
    )
    wellbore.setPipeWallRoughness(2.5e-5)
    wellbore.setLength(3.0)       # km (3000 m TVD)
    wellbore.setDiameter(0.1016)  # 4-inch tubing
    wellbore.setAngle(-90.0)      # vertical (negative = downward)
    wellbore.setNumberOfIncrements(20)

    ps = jneqsim.process.processmodel.ProcessSystem()
    ps.add(stream)
    ps.add(wellbore)
    ps.run()

    # The outlet of this "upward" model gives the bottomhole pressure
    P_bh = wellbore.getOutletStream().getPressure("bara")
    Q_tpr.append(Q_test)
    P_wf_tpr.append(P_bh)

print("\nTPR (Tubing Performance):")
print(f"{'Q (MSm³/d)':<15} {'P_wf required (bara)':<20}")
for Q, P in zip(Q_tpr, P_wf_tpr):
    print(f"{Q:<15.1f} {P:<20.1f}")

print("\nThe operating point is found at the intersection of IPR and TPR curves.")
```

![NODAL analysis showing IPR and TPR intersection at the operating point](figures/nodal_analysis_operating_point.png)

---

## 22.4 Optimization Methods

### 22.4.1 Classification of Methods

Optimization methods can be classified along several dimensions:

| Criterion | Categories |
|-----------|-----------|
| Derivative usage | Gradient-based, derivative-free, hybrid |
| Search strategy | Local, global |
| Solution type | Deterministic, stochastic |
| Number of objectives | Single-objective, multi-objective |
| Variable type | Continuous, discrete, mixed-integer |

The choice of method depends on the problem characteristics:

- **Smooth, unimodal problems** → Gradient-based methods (fastest convergence)
- **Noisy or discontinuous problems** → Derivative-free methods
- **Problems with many local optima** → Global methods (evolutionary, simulated annealing)
- **Expensive simulations** → Surrogate-based methods
- **Mixed continuous/discrete variables** → Mixed-integer methods or evolutionary algorithms

### 22.4.2 Gradient-Based Methods

Gradient-based methods use the first (and sometimes second) derivatives of the objective function to determine the search direction. They converge rapidly near the optimum but require smooth, differentiable objective functions.

**Steepest ascent (gradient ascent):**

$$
x_{k+1} = x_k + \alpha_k \cdot \nabla f(x_k)
$$

where $\alpha_k$ is the step size (determined by line search) and $\nabla f$ is the gradient of the objective function.

**Newton's method:**

$$
x_{k+1} = x_k - H^{-1}(x_k) \cdot \nabla f(x_k)
$$

where $H$ is the Hessian matrix of second derivatives. Newton's method has quadratic convergence near the optimum but requires computing (or approximating) the Hessian.

**Quasi-Newton methods (BFGS, L-BFGS):**

Approximate the Hessian iteratively from gradient information. The BFGS update:

$$
H_{k+1} = H_k + \frac{y_k y_k^T}{y_k^T s_k} - \frac{H_k s_k s_k^T H_k}{s_k^T H_k s_k}
$$

where $s_k = x_{k+1} - x_k$ and $y_k = \nabla f(x_{k+1}) - \nabla f(x_k)$.

**Sequential Quadratic Programming (SQP):**

For constrained optimization, SQP solves a sequence of quadratic subproblems:

$$
\min_{d} \quad \frac{1}{2} d^T H_k d + \nabla f(x_k)^T d
$$

$$
\text{s.t.} \quad \nabla g_i(x_k)^T d + g_i(x_k) \leq 0
$$

SQP is the workhorse of constrained nonlinear optimization and is used in commercial real-time optimizers.

**Gradient estimation for simulation-based optimization:**

When the objective function is evaluated by a process simulator (not an analytical formula), gradients must be estimated numerically using finite differences:

$$
\frac{\partial f}{\partial x_i} \approx \frac{f(x + \epsilon e_i) - f(x)}{\epsilon}
$$

where $\epsilon$ is a small perturbation and $e_i$ is the unit vector in direction $i$. This requires $n$ additional simulation runs for $n$ decision variables (or $2n$ for central differences).

### 22.4.3 Derivative-Free Methods

Derivative-free methods do not require gradient information and are robust for noisy, discontinuous, or black-box objective functions — common in process simulation.

**Nelder-Mead Simplex Method:**

The Nelder-Mead algorithm maintains a simplex (a geometric figure with $n+1$ vertices in $n$ dimensions) and iteratively moves the worst vertex toward better regions using reflection, expansion, contraction, and shrinkage operations.

The algorithm does not compute derivatives and handles noisy objective functions well. However, it is a local method and may converge to a local optimum.

**Powell's Method (Conjugate Direction Method):**

Performs sequential one-dimensional line searches along conjugate directions, gradually aligning the search directions with the principal axes of the objective function.

**Pattern Search (Generalized Pattern Search):**

Evaluates the objective at a set of points forming a pattern (e.g., coordinate directions) around the current best point. If an improvement is found, the pattern moves; otherwise, the step size is reduced. Convergence is guaranteed under mild conditions.

**Comparison of derivative-free methods:**

| Method | Function Evaluations | Global/Local | Handles Noise | Handles Constraints |
|--------|---------------------|-------------|---------------|---------------------|
| Nelder-Mead | Low ($O(n^2)$ per iteration) | Local | Yes | Penalty function |
| Powell | Moderate | Local | Moderate | Penalty function |
| Pattern search | Moderate | Local | Yes | Direct handling |
| COBYLA | Low | Local | Yes | Direct handling |

### 22.4.4 Evolutionary Algorithms

Evolutionary algorithms are population-based global optimization methods inspired by natural selection. They maintain a population of candidate solutions and evolve them through selection, crossover, and mutation.

**Genetic Algorithm (GA):**

1. **Initialize**: Random population of $N$ candidate solutions
2. **Evaluate**: Compute objective function for each individual
3. **Select**: Choose parents proportional to fitness
4. **Crossover**: Combine parent genes to create offspring

$$
x_{\text{child}} = \alpha \cdot x_{\text{parent1}} + (1 - \alpha) \cdot x_{\text{parent2}}
$$

5. **Mutate**: Random perturbation with probability $p_m$

$$
x_{\text{mutated}} = x + \sigma \cdot \mathcal{N}(0, 1)
$$

6. **Replace**: Worst individuals replaced by offspring
7. **Repeat** until convergence or maximum generations

**Particle Swarm Optimization (PSO):**

Each particle has a position $x_i$ and velocity $v_i$. At each iteration:

$$
v_i^{k+1} = w \cdot v_i^k + c_1 \cdot r_1 \cdot (p_{\text{best},i} - x_i^k) + c_2 \cdot r_2 \cdot (g_{\text{best}} - x_i^k)
$$

$$
x_i^{k+1} = x_i^k + v_i^{k+1}
$$

where $w$ is the inertia weight, $c_1$ and $c_2$ are cognitive and social parameters, $r_1$ and $r_2$ are random numbers in $[0, 1]$, $p_{\text{best},i}$ is the personal best of particle $i$, and $g_{\text{best}}$ is the global best.

**Differential Evolution (DE):**

Creates mutant vectors by combining differences between randomly selected population members:

$$
v_i = x_{r1} + F \cdot (x_{r2} - x_{r3})
$$

where $F$ is the mutation factor (typically 0.5–1.0) and $r1, r2, r3$ are randomly chosen distinct indices.

**Comparison of evolutionary algorithms:**

| Algorithm | Population Size | Convergence Speed | Global Search | Tuning Complexity |
|-----------|----------------|-------------------|---------------|-------------------|
| GA | 50–200 | Moderate | Good | Moderate (crossover, mutation rates) |
| PSO | 20–100 | Fast | Good | Low (w, c₁, c₂) |
| DE | 30–100 | Fast | Very good | Low (F, CR) |

### 22.4.5 Surrogate-Based Optimization

When each simulation is computationally expensive (minutes to hours), surrogate-based optimization builds an approximate model (surrogate) of the objective function from a limited number of simulation evaluations, then optimizes the surrogate cheaply.

The workflow is:

1. **Design of Experiments (DoE)**: Sample the decision variable space using Latin Hypercube Sampling (LHS)
2. **Evaluate**: Run the process simulator at each sample point
3. **Build surrogate**: Fit a response surface model (polynomial, kriging, radial basis functions, neural network)
4. **Optimize**: Find the optimum of the surrogate model
5. **Validate**: Run the simulator at the predicted optimum to verify
6. **Infill**: Add new sample points where the surrogate is uncertain (expected improvement criterion) and repeat

**Common surrogate models:**

| Model | Complexity | Interpolation | Uncertainty Estimate |
|-------|-----------|--------------|---------------------|
| Polynomial (quadratic) | Low | No | No |
| Kriging (Gaussian Process) | Medium | Yes | Yes |
| Radial Basis Functions | Medium | Yes | No |
| Neural Network | High | Depends | Ensemble-based |

The **expected improvement** (EI) acquisition function balances exploitation (sampling where the predicted value is good) with exploration (sampling where uncertainty is high):

$$
\text{EI}(x) = (f_{\text{best}} - \hat{f}(x)) \cdot \Phi\left(\frac{f_{\text{best}} - \hat{f}(x)}{\hat{s}(x)}\right) + \hat{s}(x) \cdot \phi\left(\frac{f_{\text{best}} - \hat{f}(x)}{\hat{s}(x)}\right)
$$

where $\hat{f}(x)$ is the surrogate prediction, $\hat{s}(x)$ is the prediction uncertainty, $\Phi$ is the standard normal CDF, and $\phi$ is the standard normal PDF.

### 22.4.6 Response Surface Methodology (RSM)

Response Surface Methodology is a widely used surrogate approach in process optimization. A second-order polynomial model is fitted to the simulation data:

$$
\hat{f}(x) = \beta_0 + \sum_{i=1}^{n} \beta_i x_i + \sum_{i=1}^{n} \beta_{ii} x_i^2 + \sum_{i < j} \beta_{ij} x_i x_j
$$

The coefficients $\beta$ are determined by least-squares regression from the DoE data. For $n$ decision variables, the quadratic model has $\frac{(n+1)(n+2)}{2}$ coefficients, requiring at least that many simulation runs.

RSM is effective when:
- The response is approximately quadratic over the region of interest
- The number of decision variables is small ($n \leq 8$)
- The simulation is deterministic (no noise)

For production optimization, a typical RSM workflow would use a Central Composite Design (CCD) or Box-Behnken design, requiring $2^n + 2n + 1$ simulation runs (e.g., 27 runs for 3 variables).

### 22.4.7 Comparison of Optimization Methods for Production Systems

| Problem Characteristics | Recommended Method | Rationale |
|------------------------|-------------------|-----------|
| 1–2 variables, quick simulation | Parametric sweep + visual inspection | Simple and intuitive |
| 3–5 variables, smooth response | Nelder-Mead or Powell | Fast convergence, few evaluations |
| 3–5 variables, noisy | Pattern search or COBYLA | Robust to noise |
| 5–15 variables, multiple optima | DE or PSO with local refinement | Global exploration + local precision |
| Expensive simulation (> 1 min) | Kriging + expected improvement | Minimum simulation evaluations |
| Discrete routing decisions | GA or mixed-integer programming | Handles binary/integer variables |
| Multiple conflicting objectives | NSGA-II or weighted sum sweep | Generates Pareto front |

---

## 22.5 Separator Pressure Optimization

### 22.5.1 The Problem

Multi-stage separation systems (typically 2–4 stages) flash the wellstream at successively lower pressures to maximize liquid recovery. The stage pressures are the primary decision variables. The objective is typically to maximize the oil production rate (equivalently, minimize the total gas flashed) or maximize the stock tank oil API gravity.

The classic **equal pressure ratio rule** provides a good initial estimate:

$$
r = \left(\frac{P_1}{P_{\text{stock tank}}}\right)^{1/N}
$$

$$
P_k = P_1 \cdot r^{-(k-1)}, \quad k = 1, 2, \ldots, N
$$

where $P_1$ is the first-stage pressure, $P_{\text{stock tank}}$ is the stock tank pressure (typically 1 atm), $N$ is the number of stages, and $r$ is the pressure ratio per stage.

However, the true optimum depends on the fluid composition and is generally not exactly the equal-ratio solution. Process simulation with optimization finds the true optimum.

### 22.5.2 NeqSim Separator Pressure Optimization

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

def simulate_two_stage_separation(P1, P2):
    """
    Simulate two-stage separation and return stock tank oil rate.

    Parameters
    ----------
    P1 : float
        First stage separator pressure (bara)
    P2 : float
        Second stage separator pressure (bara)

    Returns
    -------
    float
        Stock tank oil flow rate (kg/hr)
    """
    fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 70.0, P1)
    fluid.addComponent("nitrogen", 0.005)
    fluid.addComponent("CO2", 0.020)
    fluid.addComponent("methane", 0.450)
    fluid.addComponent("ethane", 0.070)
    fluid.addComponent("propane", 0.050)
    fluid.addComponent("i-butane", 0.020)
    fluid.addComponent("n-butane", 0.035)
    fluid.addComponent("i-pentane", 0.020)
    fluid.addComponent("n-pentane", 0.015)
    fluid.addComponent("n-hexane", 0.025)
    fluid.addComponent("n-heptane", 0.040)
    fluid.addComponent("n-octane", 0.030)
    fluid.addComponent("n-nonane", 0.020)
    fluid.addComponent("nC10", 0.010)
    fluid.addComponent("water", 0.190)
    fluid.setMixingRule("classic")
    fluid.setMultiPhaseCheck(True)

    # Stage 1: HP Separator
    feed = jneqsim.process.equipment.stream.Stream("Feed", fluid)
    feed.setFlowRate(200000.0, "kg/hr")
    feed.setTemperature(70.0, "C")
    feed.setPressure(P1, "bara")

    hp_sep = jneqsim.process.equipment.separator.ThreePhaseSeparator(
        "HP Sep", feed
    )

    # Valve between stages
    valve = jneqsim.process.equipment.valve.ThrottlingValve(
        "HP-LP Valve", hp_sep.getOilOutStream()
    )
    valve.setOutletPressure(P2)

    # Stage 2: LP Separator
    lp_sep = jneqsim.process.equipment.separator.Separator(
        "LP Sep", valve.getOutletStream()
    )

    # Stock tank valve
    st_valve = jneqsim.process.equipment.valve.ThrottlingValve(
        "ST Valve", lp_sep.getLiquidOutStream()
    )
    st_valve.setOutletPressure(1.01325)  # atmospheric

    # Stock tank separator
    st_sep = jneqsim.process.equipment.separator.Separator(
        "Stock Tank", st_valve.getOutletStream()
    )

    process = jneqsim.process.processmodel.ProcessSystem()
    process.add(feed)
    process.add(hp_sep)
    process.add(valve)
    process.add(lp_sep)
    process.add(st_valve)
    process.add(st_sep)
    process.run()

    oil_rate = st_sep.getLiquidOutStream().getFlowRate("kg/hr")
    return oil_rate


# ── Parametric sweep: vary P2 at fixed P1 ──
P1_fixed = 60.0  # bara
P2_values = [2, 4, 6, 8, 10, 12, 15, 18, 20, 25, 30]

print(f"HP Separator pressure: {P1_fixed} bara")
print(f"{'LP Sep P (bara)':<18} {'ST Oil (kg/hr)':<18}")
print("-" * 36)

best_P2 = None
best_oil = 0

for P2 in P2_values:
    try:
        oil = simulate_two_stage_separation(P1_fixed, P2)
        if oil > best_oil:
            best_oil = oil
            best_P2 = P2
        print(f"{P2:<18.0f} {oil:<18.1f}")
    except Exception as e:
        print(f"{P2:<18.0f} {'FAILED':<18}")

print(f"\nOptimal LP pressure: {best_P2} bara")
print(f"Maximum ST oil rate: {best_oil:.1f} kg/hr")
```

### 22.5.3 Two-Dimensional Pressure Sweep

For a two-stage system, both pressures can be varied simultaneously:

```python
# 2D sweep: vary both P1 and P2
P1_values = [30, 40, 50, 60, 70, 80]
P2_values = [3, 5, 8, 10, 15, 20]

print(f"{'P1 (bara)':<12} {'P2 (bara)':<12} {'ST Oil (kg/hr)':<18}")
print("-" * 42)

best_result = {"P1": 0, "P2": 0, "oil": 0}

for P1 in P1_values:
    for P2 in P2_values:
        if P2 >= P1:
            continue  # P2 must be less than P1
        try:
            oil = simulate_two_stage_separation(P1, P2)
            if oil > best_result["oil"]:
                best_result = {"P1": P1, "P2": P2, "oil": oil}
            print(f"{P1:<12.0f} {P2:<12.0f} {oil:<18.1f}")
        except Exception:
            print(f"{P1:<12.0f} {P2:<12.0f} {'FAILED':<18}")

print(f"\nOptimal: P1={best_result['P1']} bara, "
      f"P2={best_result['P2']} bara, "
      f"Oil={best_result['oil']:.1f} kg/hr")
```

![Contour plot of stock tank oil rate vs first and second stage pressures](figures/separator_pressure_contour.png)

The contour plot reveals the objective function landscape. The optimum is typically a broad, flat region, meaning the solution is not highly sensitive to small changes in pressure — a desirable feature for practical operation.

### 22.5.4 Effect of Fluid Composition

The optimal stage pressures depend strongly on the fluid composition. Light fluids (high GOR) tend to have lower optimal pressures, while heavier fluids have higher optimal pressures. In practice, the stage pressures should be re-optimized whenever the fluid composition changes significantly — for example, after a new well is tied in or as the reservoir depletes.

---

## 22.6 Gas Lift Optimization

### 22.6.1 Gas Lift Fundamentals

Gas lift is an artificial lift method in which gas is injected into the production tubing to reduce the hydrostatic gradient and increase the well's production rate. The production rate initially increases with gas lift injection rate, reaches a maximum, and then decreases at very high injection rates due to increased friction:

$$
Q_{\text{oil}}(Q_{\text{GL}}) = Q_{\text{oil,natural}} + \Delta Q(Q_{\text{GL}})
$$

The **gas lift performance curve** (GLPC) for each well shows the oil production rate as a function of gas lift injection rate. The curve has a characteristic shape: concave, with diminishing returns at higher injection rates.

### 22.6.2 Single-Well Gas Lift Optimization

For a single well, the optimal gas lift rate maximizes the economic benefit:

$$
\max_{Q_{\text{GL}}} \quad P_{\text{oil}} \cdot Q_{\text{oil}}(Q_{\text{GL}}) - C_{\text{GL}} \cdot Q_{\text{GL}}
$$

where $C_{\text{GL}}$ is the cost of compressing and injecting the gas lift gas.

The optimum occurs where the marginal oil revenue equals the marginal gas lift cost:

$$
P_{\text{oil}} \cdot \frac{dQ_{\text{oil}}}{dQ_{\text{GL}}} = C_{\text{GL}}
$$

### 22.6.3 Multi-Well Gas Lift Allocation

When multiple wells share a limited supply of gas lift gas, the allocation problem is:

$$
\max_{Q_{\text{GL},w}} \quad \sum_{w=1}^{N_w} Q_{\text{oil},w}(Q_{\text{GL},w})
$$

$$
\text{subject to:} \quad \sum_{w=1}^{N_w} Q_{\text{GL},w} \leq Q_{\text{GL,total}}
$$

$$
Q_{\text{GL},w} \geq 0, \quad w = 1, \ldots, N_w
$$

The optimal solution allocates gas lift gas to the wells with the highest marginal response (steepest GLPC slope) first. This is the **equal marginal rate of return** principle:

$$
\frac{dQ_{\text{oil},1}}{dQ_{\text{GL},1}} = \frac{dQ_{\text{oil},2}}{dQ_{\text{GL},2}} = \cdots = \frac{dQ_{\text{oil},N_w}}{dQ_{\text{GL},N_w}} = \lambda
$$

where $\lambda$ is the Lagrange multiplier associated with the total gas lift constraint.

### 22.6.4 NeqSim Gas Lift Performance Curve

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

def gas_lift_performance(Q_GL_MSm3d, P_res, PI, P_wh, depth_km):
    """
    Simulate gas lift well and return oil production rate.

    Parameters
    ----------
    Q_GL_MSm3d : float
        Gas lift injection rate (MSm³/day)
    P_res : float
        Reservoir pressure (bara)
    PI : float
        Productivity index (Sm³/day/bar)
    P_wh : float
        Wellhead pressure (bara)
    depth_km : float
        Well depth (km)

    Returns
    -------
    float
        Oil production rate (Sm³/day)
    """
    # Reservoir fluid
    oil = jneqsim.thermo.system.SystemSrkEos(273.15 + 80.0, P_res)
    oil.addComponent("methane", 0.30)
    oil.addComponent("ethane", 0.05)
    oil.addComponent("propane", 0.04)
    oil.addComponent("n-butane", 0.03)
    oil.addComponent("n-pentane", 0.03)
    oil.addComponent("n-hexane", 0.05)
    oil.addComponent("n-heptane", 0.10)
    oil.addComponent("n-octane", 0.15)
    oil.addComponent("n-nonane", 0.10)
    oil.addComponent("nC10", 0.15)
    oil.setMixingRule("classic")
    oil.setMultiPhaseCheck(True)

    # Approximate flow rate from simple IPR
    # For this demonstration, we estimate Pwf iteratively
    # In practice, this would be a coupled reservoir-wellbore solve
    P_wf_est = P_wh + 30.0  # initial estimate
    Q_oil_est = PI * (P_res - P_wf_est)  # Sm3/day, approximate

    feed = jneqsim.process.equipment.stream.Stream("Reservoir Fluid", oil)
    feed.setFlowRate(max(Q_oil_est * 0.8, 100), "Am3/hr")
    feed.setTemperature(80.0, "C")
    feed.setPressure(P_wf_est, "bara")

    # The gas lift reduces the effective mixture density in the tubing,
    # lowering the required Pwf and increasing the flow rate
    # For demonstration, model the impact as increased flow:
    Q_boost = Q_GL_MSm3d * 500.0  # simplified: each MSm3/d of GL adds ~500 Sm3/d of oil
    Q_diminishing = Q_boost * (1.0 / (1.0 + Q_GL_MSm3d / 0.3))  # diminishing returns

    Q_total = Q_oil_est + Q_diminishing

    return Q_total

# Generate gas lift performance curves for three wells
wells = [
    {"name": "Well A", "P_res": 220, "PI": 15.0, "P_wh": 35, "depth": 2.5},
    {"name": "Well B", "P_res": 180, "PI": 25.0, "P_wh": 35, "depth": 3.0},
    {"name": "Well C", "P_res": 250, "PI": 10.0, "P_wh": 35, "depth": 2.0},
]

Q_GL_range = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60]

print("Gas Lift Performance Curves")
print("=" * 70)
header = f"{'Q_GL (MSm³/d)':<16}"
for w in wells:
    header += f"{w['name'] + ' (Sm³/d)':<20}"
print(header)
print("-" * 70)

well_curves = {w["name"]: [] for w in wells}

for Q_GL in Q_GL_range:
    line = f"{Q_GL:<16.2f}"
    for w in wells:
        Q_oil = gas_lift_performance(
            Q_GL, w["P_res"], w["PI"], w["P_wh"], w["depth"]
        )
        well_curves[w["name"]].append(Q_oil)
        line += f"{Q_oil:<20.1f}"
    print(line)

# Simple gas lift allocation using equal slope criterion
Q_GL_total = 0.60  # MSm³/day total available
print(f"\nTotal gas lift available: {Q_GL_total} MSm³/day")
print("Optimal allocation (equal marginal return):")

# Compute marginal responses (finite difference)
for w in wells:
    curve = well_curves[w["name"]]
    marginals = []
    for i in range(1, len(Q_GL_range)):
        dQ = (curve[i] - curve[i-1]) / (Q_GL_range[i] - Q_GL_range[i-1])
        marginals.append(dQ)
    print(f"  {w['name']}: marginal response at 0.1 MSm³/d = "
          f"{marginals[1]:.0f} Sm³/d per MSm³/d GL")
```

![Gas lift performance curves for three wells showing diminishing returns](figures/gas_lift_performance_curves.png)

### 22.6.5 Practical Considerations

Real gas lift optimization must account for:

1. **Minimum and maximum injection rates** per well (valve design constraints)
2. **Unloading requirements**: Some wells need a minimum injection rate to remain unloaded
3. **Compressor capacity**: Gas lift compressor power limits the total available gas
4. **Gas lift gas quality**: Impurities can cause hydrate or corrosion issues in GL valves
5. **Interdependence**: Wells sharing a manifold influence each other's wellhead pressure

---

## 22.7 Compressor Set Point Optimization

### 22.7.1 The Problem

Compressor systems (particularly multi-stage systems with parallel trains) have multiple set points that can be optimized:

- **Suction pressure**: Affects compression ratio, power, and upstream separator operation
- **Discharge pressure**: Must meet pipeline delivery pressure
- **Speed**: Variable-speed drives allow head-capacity trade-off
- **Recycle valve opening**: Recycle wastes energy but maintains surge margin
- **Load sharing**: In parallel compressor trains, the load split can be optimized

The objective is typically to minimize total compressor power while meeting the required flow and pressure:

$$
\min_{x} \quad W_{\text{total}}(x) = \sum_{k=1}^{N_{\text{stages}}} W_k(x)
$$

subject to:

$$
P_{\text{discharge}}(x) \geq P_{\text{pipeline}}
$$

$$
Q_{\text{surge},k}(x) \leq Q_k(x) \leq Q_{\text{stonewall},k}(x), \quad \forall k
$$

$$
W_k(x) \leq W_{\text{driver},k}, \quad \forall k
$$

### 22.7.2 NeqSim Compressor Optimization

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

def compressor_power(P_suction, P_discharge, flow_MSm3d):
    """
    Calculate compressor power for given suction/discharge pressures.

    Returns power in MW.
    """
    gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, P_suction)
    gas.addComponent("nitrogen", 0.01)
    gas.addComponent("CO2", 0.02)
    gas.addComponent("methane", 0.87)
    gas.addComponent("ethane", 0.06)
    gas.addComponent("propane", 0.03)
    gas.addComponent("n-butane", 0.01)
    gas.setMixingRule("classic")

    feed = jneqsim.process.equipment.stream.Stream("Feed", gas)
    feed.setFlowRate(flow_MSm3d, "MSm3/day")
    feed.setTemperature(30.0, "C")
    feed.setPressure(P_suction, "bara")

    comp = jneqsim.process.equipment.compressor.Compressor("Comp", feed)
    comp.setOutletPressure(P_discharge)
    comp.setPolytropicEfficiency(0.78)

    ps = jneqsim.process.processmodel.ProcessSystem()
    ps.add(feed)
    ps.add(comp)
    ps.run()

    return comp.getPower() / 1e6  # MW


# Optimize suction pressure (trade-off: lower P_suct gives more
# reservoir drawdown but requires more compressor power)
P_discharge_req = 120.0  # bara, pipeline delivery
flow = 4.0  # MSm³/day

P_suction_range = [20, 25, 30, 35, 40, 45, 50, 55, 60]

print("Compressor Suction Pressure Optimization")
print("=" * 50)
print(f"{'P_suction (bara)':<20} {'Power (MW)':<15} {'CR':<10}")
print("-" * 45)

for P_s in P_suction_range:
    try:
        power = compressor_power(P_s, P_discharge_req, flow)
        cr = P_discharge_req / P_s
        print(f"{P_s:<20.0f} {power:<15.2f} {cr:<10.1f}")
    except Exception:
        print(f"{P_s:<20.0f} {'FAILED':<15}")

print("\nLower suction pressure → more oil production but more power.")
print("Optimal is where marginal oil value = marginal power cost.")
```

### 22.7.3 Two-Stage Compression Optimization

For a two-stage compression system with an intercooler, the interstage pressure can be optimized:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

def two_stage_power(P_suct, P_inter, P_disch, flow_MSm3d):
    """
    Simulate two-stage compression with intercooling.
    Returns total power in MW.
    """
    gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, P_suct)
    gas.addComponent("methane", 0.90)
    gas.addComponent("ethane", 0.06)
    gas.addComponent("propane", 0.03)
    gas.addComponent("n-butane", 0.01)
    gas.setMixingRule("classic")

    feed = jneqsim.process.equipment.stream.Stream("Feed", gas)
    feed.setFlowRate(flow_MSm3d, "MSm3/day")
    feed.setTemperature(30.0, "C")
    feed.setPressure(P_suct, "bara")

    # Stage 1
    comp1 = jneqsim.process.equipment.compressor.Compressor("Stage 1", feed)
    comp1.setOutletPressure(P_inter)
    comp1.setPolytropicEfficiency(0.78)

    # Intercooler
    cooler = jneqsim.process.equipment.heatexchanger.Heater(
        "Intercooler", comp1.getOutletStream()
    )
    cooler.setOutTemperature(273.15 + 35.0)

    # Stage 2
    comp2 = jneqsim.process.equipment.compressor.Compressor(
        "Stage 2", cooler.getOutletStream()
    )
    comp2.setOutletPressure(P_disch)
    comp2.setPolytropicEfficiency(0.76)

    ps = jneqsim.process.processmodel.ProcessSystem()
    ps.add(feed)
    ps.add(comp1)
    ps.add(cooler)
    ps.add(comp2)
    ps.run()

    W1 = comp1.getPower() / 1e6
    W2 = comp2.getPower() / 1e6
    return W1 + W2, W1, W2


# Sweep interstage pressure
P_s = 25.0    # bara, suction
P_d = 150.0   # bara, discharge
Q = 5.0       # MSm³/day

# Theoretical optimal: geometric mean
P_inter_opt_theory = (P_s * P_d) ** 0.5
print(f"Theoretical optimal interstage P: {P_inter_opt_theory:.1f} bara")

P_inter_range = [35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]

print(f"\n{'P_inter (bara)':<18} {'W_total (MW)':<15} {'W1 (MW)':<12} {'W2 (MW)':<12}")
print("-" * 57)

best_P = 0
best_W = 999

for P_i in P_inter_range:
    try:
        W_tot, W1, W2 = two_stage_power(P_s, P_i, P_d, Q)
        if W_tot < best_W:
            best_W = W_tot
            best_P = P_i
        print(f"{P_i:<18.0f} {W_tot:<15.2f} {W1:<12.2f} {W2:<12.2f}")
    except Exception:
        print(f"{P_i:<18.0f} {'FAILED':<15}")

print(f"\nOptimal interstage pressure: {best_P} bara")
print(f"Minimum total power:        {best_W:.2f} MW")
```

The theoretical optimum for equal-efficiency stages is the geometric mean of the suction and discharge pressures. In practice, differences in efficiency between stages, intercooler effectiveness, and gas property variations cause the true optimum to deviate slightly from this theoretical value.

![Two-stage compressor power vs interstage pressure](figures/interstage_pressure_optimization.png)

---

## 22.8 Multi-Objective Optimization

### 22.8.1 Concept

Many production optimization problems have multiple competing objectives. For example:

- **Maximize oil production** vs **minimize energy consumption**
- **Maximize gas export volume** vs **maximize gas heating value**
- **Maximize recovery factor** vs **minimize water handling cost**

In multi-objective optimization, there is generally no single solution that optimizes all objectives simultaneously. Instead, there is a **Pareto front** — a set of solutions where no objective can be improved without worsening another.

### 22.8.2 Pareto Optimality

A solution $x^*$ is **Pareto optimal** if there is no other feasible solution $x$ such that:

$$
f_k(x) \geq f_k(x^*) \quad \forall k, \quad \text{and} \quad f_j(x) > f_j(x^*) \quad \text{for some } j
$$

The set of all Pareto-optimal solutions is the **Pareto front** in objective space.

### 22.8.3 Solution Approaches

**Weighted Sum Method:**

Convert multiple objectives into a single objective using weights:

$$
\max_x \quad \sum_{k=1}^{K} w_k \cdot f_k(x), \quad \text{where} \quad \sum_{k=1}^{K} w_k = 1, \quad w_k \geq 0
$$

By varying the weights, different points on the Pareto front are obtained. This is simple but cannot find solutions on non-convex portions of the Pareto front.

**$\epsilon$-Constraint Method:**

Optimize one objective while constraining the others:

$$
\max_x \quad f_1(x) \quad \text{s.t.} \quad f_k(x) \geq \epsilon_k, \quad k = 2, \ldots, K
$$

By varying $\epsilon_k$, the entire Pareto front (including non-convex regions) can be traced.

**Evolutionary Multi-Objective Optimization (NSGA-II):**

The Non-dominated Sorting Genetic Algorithm II (NSGA-II) maintains a population of solutions and uses non-dominated sorting and crowding distance to evolve toward the Pareto front in a single run.

### 22.8.4 Example: Oil Rate vs Power Consumption

```python
# Multi-objective: sweep separator pressure and record both
# oil rate and compressor power

import jpype
jneqsim = jpype.JPackage("neqsim")

P_sep_range = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
pareto_points = []

for P_sep in P_sep_range:
    fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 75.0, P_sep)
    fluid.addComponent("methane", 0.50)
    fluid.addComponent("ethane", 0.06)
    fluid.addComponent("propane", 0.04)
    fluid.addComponent("n-butane", 0.03)
    fluid.addComponent("n-hexane", 0.05)
    fluid.addComponent("n-heptane", 0.08)
    fluid.addComponent("n-octane", 0.10)
    fluid.addComponent("nC10", 0.05)
    fluid.addComponent("water", 0.09)
    fluid.setMixingRule("classic")
    fluid.setMultiPhaseCheck(True)

    fd = jneqsim.process.equipment.stream.Stream("Feed", fluid)
    fd.setFlowRate(200000.0, "kg/hr")
    fd.setTemperature(75.0, "C")
    fd.setPressure(P_sep, "bara")

    sep = jneqsim.process.equipment.separator.ThreePhaseSeparator("Sep", fd)

    comp = jneqsim.process.equipment.compressor.Compressor(
        "Comp", sep.getGasOutStream()
    )
    comp.setOutletPressure(120.0)
    comp.setPolytropicEfficiency(0.77)

    ps = jneqsim.process.processmodel.ProcessSystem()
    ps.add(fd)
    ps.add(sep)
    ps.add(comp)

    try:
        ps.run()
        oil_rate = sep.getOilOutStream().getFlowRate("kg/hr")
        power = comp.getPower() / 1e6  # MW
        pareto_points.append({
            "P_sep": P_sep,
            "oil_rate": oil_rate,
            "power": power
        })
    except Exception:
        pass

print("Multi-Objective Results: Oil Rate vs Compressor Power")
print("=" * 60)
print(f"{'P_sep (bara)':<15} {'Oil Rate (kg/hr)':<20} {'Power (MW)':<15}")
print("-" * 50)
for pt in pareto_points:
    print(f"{pt['P_sep']:<15.0f} {pt['oil_rate']:<20.1f} {pt['power']:<15.2f}")

print("\nLower separator pressure → more oil recovery but more compressor power.")
print("The Pareto front represents the trade-off frontier.")
```

![Pareto front showing trade-off between oil rate and compressor power](figures/pareto_front_oil_vs_power.png)

---

## 22.9 Real-Time Optimization (RTO)

### 22.9.1 Architecture

Real-time optimization (RTO) is the automated, continuous optimization of a production facility using live plant data. The standard RTO architecture consists of four layers:

1. **Data validation**: Clean and reconcile plant measurements (gross error detection, data reconciliation)
2. **Parameter estimation**: Update the process model to match current plant conditions (model tuning)
3. **Optimization**: Solve the optimization problem using the updated model
4. **Implementation**: Send optimized set points to the control system

$$
\text{Plant} \xrightarrow{\text{measurements}} \text{Data Validation} \xrightarrow{\text{clean data}} \text{Model Update} \xrightarrow{\text{tuned model}} \text{Optimizer} \xrightarrow{\text{set points}} \text{DCS}
$$

### 22.9.2 Steady-State vs Dynamic RTO

**Steady-state RTO** assumes the plant is at (or near) steady state. It runs periodically (every 15–60 minutes) when the plant has settled:

- Advantages: Simpler models, faster computation, well-understood theory
- Limitations: Cannot handle transient conditions, must wait for steady state

**Dynamic RTO** uses dynamic models that capture transient behavior:

- Advantages: Can optimize during transients, faster response
- Limitations: More complex models, higher computational cost, harder to validate

### 22.9.3 Steady-State Detection

Before running steady-state RTO, the system must verify that the plant is at steady state. A common test is the **R-statistic** applied to key process variables:

$$
R = \frac{1}{N} \sum_{i=1}^{N} \left(\frac{y_i - \bar{y}}{\sigma_y}\right)^2
$$

If $R$ is below a threshold (typically 1.0–2.0), the process is considered at steady state.

### 22.9.4 Data Reconciliation

Measurement errors are inevitable. Data reconciliation adjusts measured values to satisfy material and energy balances while minimizing the total adjustment:

$$
\min_{x} \quad \sum_{i} \left(\frac{x_i - y_i}{\sigma_i}\right)^2
$$

subject to:

$$
A \cdot x = 0 \quad \text{(material balance)}
$$

where $y_i$ is the measured value, $x_i$ is the reconciled value, and $\sigma_i$ is the measurement uncertainty.

### 22.9.5 Model Update (Parameter Estimation)

The process model parameters (e.g., well productivity indices, heat transfer coefficients, compressor efficiencies) are adjusted to minimize the discrepancy between model predictions and reconciled measurements:

$$
\min_{\theta} \quad \sum_{i} \left(\frac{x_i^{\text{model}}(\theta) - x_i^{\text{plant}}}{\sigma_i}\right)^2
$$

where $\theta$ is the vector of model parameters.

This step is critical: an optimization based on an inaccurate model will produce poor set points, potentially worse than the current operation.

### 22.9.6 Implementation Challenges

Real-time optimization faces several practical challenges that must be addressed for successful deployment:

**Model fidelity**: The process model must be accurate enough to predict the effect of set point changes. This requires regular validation against plant data and parameter re-tuning. A common metric is the **model prediction error** for key variables:

$$
\text{MPE}_i = \frac{|y_i^{\text{model}} - y_i^{\text{plant}}|}{y_i^{\text{plant}}} \times 100\%
$$

Acceptable MPE is typically < 5% for flow rates and < 2% for temperatures and pressures.

**Steady-state assumption**: Standard RTO requires steady-state conditions, but real plants are rarely truly at steady state. Frequent disturbances (slug flow, well cycling, compressor surging) can prevent the RTO from running. In practice, the steady-state detection logic must be tuned to balance responsiveness with robustness.

**Move suppression**: The optimizer may suggest large set point changes that are impractical or destabilizing. Move suppression limits the maximum change per RTO cycle:

$$
\lvert x_{k+1} - x_k\rvert \leq \Delta x_{\text{max}}
$$

This prevents oscillation and ensures the plant transitions smoothly to the new optimum.

**Operator acceptance**: RTO recommendations must be understandable and trustworthy. Operators need to see *why* a change is recommended and *what will happen* if they implement it. This requires clear visualization of the current vs. optimized state and the expected benefits.

### 22.9.7 RTO Performance Metrics

The value of RTO is measured by comparing actual production with the pre-RTO baseline:

$$
\text{RTO Benefit} = \sum_{d=1}^{N_{\text{days}}} \left[f(x_{\text{RTO},d}) - f(x_{\text{baseline},d})\right]
$$

Typical RTO benefits in offshore production are 2–5% increase in oil production or 3–8% reduction in energy consumption. For a platform producing 50,000 bbl/day, a 3% improvement at $70/bbl is approximately $105,000 per day — easily justifying the investment.

---

## 22.10 Robust Optimization Under Uncertainty

### 22.10.1 Sources of Uncertainty

Production optimization operates under significant uncertainty:

| Source | Examples | Impact |
|--------|----------|--------|
| Reservoir | Pressure, fluid composition, water cut | Well deliverability |
| Measurements | Flow rates, pressures, temperatures | Model accuracy |
| Equipment | Compressor efficiency, fouling, degradation | Capacity limits |
| Environment | Ambient temperature, sea conditions | Driver power, cooling |
| Market | Oil/gas prices, contract terms | Objective function |

### 22.10.2 Robust Formulation

Rather than optimizing for a single scenario, robust optimization seeks solutions that perform well across a range of uncertain conditions:

$$
\max_x \quad \min_{\xi \in \Xi} \quad f(x, \xi)
$$

where $\xi$ represents the uncertain parameters and $\Xi$ is the uncertainty set. This **minimax** (or worst-case) formulation ensures the solution is feasible and performs adequately even under the worst-case realization of uncertainty.

### 22.10.3 Stochastic Optimization

An alternative is **stochastic optimization**, which maximizes the expected value of the objective:

$$
\max_x \quad \mathbb{E}_{\xi}[f(x, \xi)] = \int f(x, \xi) \cdot p(\xi) \, d\xi
$$

In practice, this is approximated by sampling:

$$
\max_x \quad \frac{1}{N_s} \sum_{s=1}^{N_s} f(x, \xi_s)
$$

where $\xi_1, \ldots, \xi_{N_s}$ are samples from the uncertainty distribution.

### 22.10.4 Chance Constraints

Constraints that must be satisfied with a specified probability:

$$
P(g_i(x, \xi) \leq 0) \geq 1 - \alpha_i
$$

where $\alpha_i$ is the acceptable violation probability (e.g., 5%). This allows the optimizer to take calculated risks where the potential upside justifies occasional constraint violations.

### 22.10.5 Practical Uncertainty Handling in NeqSim

In practice, robust optimization with NeqSim involves running the process model at multiple uncertainty realizations. A straightforward approach is:

1. **Define the uncertainty space**: Identify the key uncertain parameters (e.g., gas composition ±10%, ambient temperature ±15°C, well PI ±20%) and their probability distributions
2. **Generate scenarios**: Sample $N_s$ scenarios from the joint uncertainty distribution (e.g., Latin Hypercube Sampling with $N_s = 50–200$)
3. **Evaluate each scenario**: For each candidate set of decision variables $x$, run the NeqSim process model at all $N_s$ scenarios
4. **Compute robust objective**: Use the mean, worst-case, or conditional value-at-risk (CVaR) across scenarios as the objective

The CVaR (also called Expected Shortfall) at confidence level $\beta$ is:

$$
\text{CVaR}_\beta(x) = \frac{1}{1-\beta} \int_\beta^1 q_\alpha(f(x, \xi)) \, d\alpha
$$

where $q_\alpha$ is the $\alpha$-quantile of the objective function distribution. CVaR provides a more conservative objective than the mean but is less extreme than the worst case, making it a popular choice for practical robust optimization.

---

## 22.11 Integrated Asset Modeling

### 22.11.1 Concept

Integrated asset modeling (IAM) couples reservoir simulation, well models, and surface facility models into a single optimization framework. This allows optimization across the entire production system — from reservoir to export — capturing the interactions between subsurface and surface:

$$
\text{Reservoir} \longleftrightarrow \text{Wells} \longleftrightarrow \text{Flowlines} \longleftrightarrow \text{Facilities} \longleftrightarrow \text{Export}
$$

### 22.11.2 Coupling Approaches

| Approach | Description | Accuracy | Speed |
|----------|------------|----------|-------|
| Sequential | Run reservoir → well → facility in sequence | Low (no feedback) | Fast |
| Iterative | Iterate between models until convergence | Medium | Medium |
| Fully coupled | Solve all models simultaneously | High | Slow |

The iterative approach is most common in practice: the reservoir model provides well deliverability curves, the facility model determines the operating pressures, and these are exchanged iteratively until convergence.

### 22.11.3 NeqSim in Integrated Asset Models

NeqSim serves as the facility model component in IAM:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# This function would be called by an outer IAM loop
# with wellhead conditions from the reservoir model

def facility_model(wellhead_conditions):
    """
    Run the facility model for given wellhead conditions.

    Parameters
    ----------
    wellhead_conditions : list of dict
        Each dict has keys: 'name', 'flow_kghr', 'T_C', 'P_bara',
        'composition' (dict of component: mole fraction)

    Returns
    -------
    dict
        Facility outputs: export gas rate, oil rate, power, etc.
    """
    # Example with a single well for simplicity
    wc = wellhead_conditions[0]

    fluid = jneqsim.thermo.system.SystemSrkEos(
        273.15 + wc['T_C'], wc['P_bara']
    )
    for comp, frac in wc['composition'].items():
        fluid.addComponent(comp, frac)
    fluid.setMixingRule("classic")
    fluid.setMultiPhaseCheck(True)

    feed = jneqsim.process.equipment.stream.Stream("Well Feed", fluid)
    feed.setFlowRate(wc['flow_kghr'], "kg/hr")
    feed.setTemperature(wc['T_C'], "C")
    feed.setPressure(wc['P_bara'], "bara")

    # Build facility model
    sep = jneqsim.process.equipment.separator.ThreePhaseSeparator(
        "HP Sep", feed
    )
    comp = jneqsim.process.equipment.compressor.Compressor(
        "Export Comp", sep.getGasOutStream()
    )
    comp.setOutletPressure(120.0)
    comp.setPolytropicEfficiency(0.77)

    ps = jneqsim.process.processmodel.ProcessSystem()
    ps.add(feed)
    ps.add(sep)
    ps.add(comp)
    ps.run()

    results = {
        'gas_export_kghr': sep.getGasOutStream().getFlowRate("kg/hr"),
        'oil_rate_kghr': sep.getOilOutStream().getFlowRate("kg/hr"),
        'water_rate_kghr': sep.getWaterOutStream().getFlowRate("kg/hr"),
        'compressor_power_MW': comp.getPower() / 1e6,
        'export_pressure_bara': comp.getOutletStream().getPressure("bara"),
        'separator_pressure_bara': wc['P_bara'],
    }
    return results

# Example call
wc = [{
    'name': 'Well-1',
    'flow_kghr': 150000.0,
    'T_C': 75.0,
    'P_bara': 60.0,
    'composition': {
        'methane': 0.55, 'ethane': 0.07, 'propane': 0.04,
        'n-butane': 0.03, 'n-hexane': 0.05, 'n-heptane': 0.08,
        'n-octane': 0.06, 'water': 0.12
    }
}]

output = facility_model(wc)
print("Facility Model Output:")
for key, val in output.items():
    print(f"  {key}: {val:.2f}")
```

---

## 22.12 Practical Implementation Considerations

### 22.12.1 Computational Performance

Process simulation-based optimization requires many simulation evaluations. Typical counts:

| Method | Evaluations for 5 Variables | Evaluations for 10 Variables |
|--------|---------------------------|------------------------------|
| Gradient (finite diff.) | 50–200 | 200–1,000 |
| Nelder-Mead | 100–500 | 500–5,000 |
| Pattern search | 100–1,000 | 1,000–10,000 |
| GA (pop=50, gen=50) | 2,500 | 2,500 |
| PSO (pop=30, iter=50) | 1,500 | 1,500 |
| Surrogate (Kriging) | 50–200 | 100–500 |

For a NeqSim process model that runs in 0.1–1.0 seconds, even 10,000 evaluations complete in minutes. However, for more complex models (dynamic simulation, detailed columns), surrogate-based approaches become attractive.

### 22.12.2 Local vs Global Optima

Production optimization problems are generally **non-convex** — they may have multiple local optima. Gradient-based and simplex methods find local optima, which may not be the global optimum.

Strategies to handle multiple optima:

1. **Multi-start**: Run the local optimizer from multiple random starting points
2. **Global search first, local refinement**: Use an evolutionary algorithm to explore broadly, then refine with a gradient method
3. **Domain knowledge**: Use engineering insight to narrow the search space and choose good starting points

### 22.12.3 Constraint Handling

Several approaches exist for handling constraints in simulation-based optimization:

**Penalty method:** Add a penalty term to the objective for constraint violations:

$$
f_{\text{penalized}}(x) = f(x) - \sum_i \mu_i \cdot \max(0, g_i(x))^2
$$

**Barrier method:** Add a barrier that prevents the optimizer from approaching constraint boundaries:

$$
f_{\text{barrier}}(x) = f(x) + \sum_i \frac{1}{\mu_i \cdot g_i(x)}
$$

**Direct constraint handling:** Some algorithms (COBYLA, SQP, pattern search with constraint projection) handle constraints directly without modification of the objective.

### 22.12.4 Optimization Workflow Summary

A practical production optimization workflow using NeqSim:

1. **Define the decision variables**: Which set points to optimize (pressures, flows, temperatures)
2. **Define the objective**: What to maximize or minimize (production, revenue, efficiency)
3. **Define constraints**: Equipment limits (Chapter 18), quality specs, safety limits
4. **Build the process model**: Create a NeqSim ProcessSystem that takes decision variables as inputs
5. **Select an optimizer**: Start with parametric sweep for 1–2 variables; use Nelder-Mead or pattern search for 3–5 variables; consider evolutionary methods for 5+ variables or discrete variables
6. **Run the optimization**: Iterate until convergence
7. **Validate the result**: Check that the optimum is physically reasonable, satisfies all constraints, and is robust to small perturbations
8. **Implement**: Communicate optimized set points to operations

### 22.12.2 Common Pitfalls

Several pitfalls frequently undermine production optimization efforts:

1. **Optimizing the model, not the plant**: The optimizer finds the optimum of the model. If the model does not accurately represent the plant, the recommended set points may degrade actual performance. Model validation is essential.

2. **Ignoring operational constraints**: The mathematical optimum may violate practical constraints that were not included in the model (e.g., operator preferences, environmental limits, regulatory requirements). Always review optimized set points with operations before implementation.

3. **Over-fitting to current conditions**: Optimal set points derived for today's conditions may not remain optimal if conditions change (e.g., weather, well interventions). Periodic re-optimization is necessary.

4. **Neglecting transition costs**: Moving from the current operating point to the optimized point incurs transition costs (production losses during re-stabilization, control system transients). These should be weighed against the steady-state benefit.

5. **Single-objective tunnel vision**: Focusing exclusively on one objective (e.g., maximum oil rate) may sacrifice important secondary objectives (equipment life, energy efficiency, emissions). Multi-objective formulations provide a more complete picture.

### 22.12.3 Software Tools for Production Optimization

Production optimization in the oil and gas industry employs a range of software tools:

| Tool Category | Examples | Typical Use |
|--------------|---------|-------------|
| Process simulators | NeqSim, HYSYS, UniSim, PRO/II | Steady-state process modeling |
| Network models | GAP, Prosper, OLGA | Well and flowline network |
| RTO platforms | ROMeo, Aspen RT-Opt | Real-time steady-state optimization |
| Optimization libraries | SciPy, MATLAB fmincon, Gurobi | Algorithm implementation |
| Digital twin platforms | Cognite, AVEVA | Integrated data + model + optimization |

NeqSim is particularly suited for optimization studies because:
- It provides a scriptable Python API for programmatic optimization loops
- Flash calculations and process simulations are fast (typically < 1 second)
- It handles multiphase systems (oil, gas, water) natively
- The `ProcessSystem` class can be rebuilt and re-run programmatically in optimization loops

---

## 22.13 Case Study: Platform Production Optimization

### 22.13.1 Problem Description

Consider a platform producing from 5 wells with:

- HP separator at variable pressure (30–80 bara)
- Two export compressors (20 MW each, variable speed)
- Gas export pipeline requiring 120 bara delivery
- Total gas handling capacity of 8 MSm³/day
- Total liquid handling capacity of 500 m³/hr

The goal is to maximize oil production by optimizing the HP separator pressure while respecting all equipment constraints.

### 22.13.2 Implementation

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

def platform_production(P_sep):
    """
    Simulate platform production at given separator pressure.
    Returns dict with production rates and constraint metrics.
    """
    fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 75.0, P_sep)
    fluid.addComponent("nitrogen", 0.005)
    fluid.addComponent("CO2", 0.025)
    fluid.addComponent("methane", 0.480)
    fluid.addComponent("ethane", 0.065)
    fluid.addComponent("propane", 0.040)
    fluid.addComponent("i-butane", 0.015)
    fluid.addComponent("n-butane", 0.025)
    fluid.addComponent("i-pentane", 0.015)
    fluid.addComponent("n-pentane", 0.012)
    fluid.addComponent("n-hexane", 0.020)
    fluid.addComponent("n-heptane", 0.035)
    fluid.addComponent("n-octane", 0.025)
    fluid.addComponent("n-nonane", 0.015)
    fluid.addComponent("nC10", 0.010)
    fluid.addComponent("water", 0.213)
    fluid.setMixingRule("classic")
    fluid.setMultiPhaseCheck(True)

    feed = jneqsim.process.equipment.stream.Stream("Platform Feed", fluid)
    feed.setFlowRate(400000.0, "kg/hr")
    feed.setTemperature(75.0, "C")
    feed.setPressure(P_sep, "bara")

    sep = jneqsim.process.equipment.separator.ThreePhaseSeparator("HP Sep", feed)

    comp = jneqsim.process.equipment.compressor.Compressor(
        "Export Comp", sep.getGasOutStream()
    )
    comp.setOutletPressure(120.0)
    comp.setPolytropicEfficiency(0.77)

    ps = jneqsim.process.processmodel.ProcessSystem()
    ps.add(feed)
    ps.add(sep)
    ps.add(comp)
    ps.run()

    oil = sep.getOilOutStream().getFlowRate("kg/hr")
    gas = sep.getGasOutStream().getFlowRate("kg/hr")
    water = sep.getWaterOutStream().getFlowRate("kg/hr")
    power = comp.getPower() / 1e6

    return {
        "P_sep": P_sep,
        "oil_kghr": oil,
        "gas_kghr": gas,
        "water_kghr": water,
        "power_MW": power,
        "power_ok": power <= 40.0,  # 2 x 20 MW
    }


# Sweep separator pressure
print("Platform Production vs Separator Pressure")
print("=" * 75)
print(f"{'P_sep':<10} {'Oil (kg/hr)':<15} {'Gas (kg/hr)':<15} "
      f"{'Power (MW)':<14} {'Power OK':<10}")
print("-" * 64)

best = {"oil_kghr": 0}

for P in range(30, 81, 5):
    try:
        r = platform_production(float(P))
        if r["oil_kghr"] > best["oil_kghr"] and r["power_ok"]:
            best = r
        print(f"{r['P_sep']:<10.0f} {r['oil_kghr']:<15.1f} "
              f"{r['gas_kghr']:<15.1f} {r['power_MW']:<14.2f} "
              f"{'OK' if r['power_ok'] else 'EXCEEDED':<10}")
    except Exception:
        print(f"{P:<10.0f} {'FAILED'}")

print(f"\nOptimal separator pressure: {best['P_sep']:.0f} bara")
print(f"Maximum oil production:     {best['oil_kghr']:.1f} kg/hr")
print(f"Compressor power:           {best['power_MW']:.2f} MW")
```

---


<!-- reviewed-notebook-results:start -->
## Reproduced Calculation Results

These examples use the stated fluid recipes and operating assumptions. Curves represent NeqSim calculations unless a caption identifies an analytical illustration, assumed equipment map or synthetic data.

![Objective Function: Production Rate vs Feed Rate](figures/ch19_objective_function_landscape.png)

Export Rate: export gas rate spans 15–75 t/hr across the plotted cases. Max Utilization: max equipment utilization spans 27.78–138.9 % across the plotted cases.

The simulated export rate grows with feed, but the fixed capacity denominators cause utilization to cross the allowable boundary. The useful optimum is the last feasible rate, not the largest export value plotted. Check a feasible point and a neighboring infeasible point to bracket the production limit.

![Sensitivity Tornado: Equipment Capacity Impact on Max Production](figures/ch19_sensitivity_tornado.png)

The baseline bisection result is 53.848 t/hr. The largest negative throughput change in the single-rating sensitivity is -10.664 t/hr; the largest positive change is 0.254 t/hr.

Each sensitivity changes one assumed equipment rating and repeats the process-based feasibility search. A rating increase yields no throughput benefit if another unit already controls production. Prioritize the constraint with a demonstrated throughput response and verify the economics of the resulting upgrade.

Selected numerical ranges from the plotted cases:

| Quantity / series | Minimum | Maximum | Unit |
|---|---:|---:|---|
| Export Rate: export gas rate | 15 | 75 | t/hr |

Ranges describe the sampled cases; they are not independent validation tolerances.
<!-- reviewed-notebook-results:end -->

## Summary

This chapter presented the theoretical foundations and practical methods for production optimization in oil and gas facilities.

**Key takeaways:**

1. **Optimization formulation** requires a clear definition of objective function, decision variables, and constraints. The objective is typically to maximize production or revenue subject to equipment capacity, quality, and safety constraints.

2. **NODAL analysis** provides the foundation for system-level production optimization by coupling reservoir deliverability with well and facility performance curves.

3. **Gradient-based methods** (SQP, quasi-Newton) converge fastest for smooth problems. **Derivative-free methods** (Nelder-Mead, pattern search) are robust for noisy, black-box simulators. **Evolutionary algorithms** (GA, PSO, DE) explore globally but require more function evaluations.

4. **Surrogate-based optimization** is essential when each simulation is expensive — build a cheap approximate model and optimize it instead.

5. **Separator pressure optimization** maximizes liquid recovery by finding the optimal flash pressures. The equal-ratio rule provides a starting point; simulation-based optimization finds the true optimum.

6. **Gas lift allocation** distributes limited gas lift gas to maximize total oil production using the equal-marginal-return principle.

7. **Compressor set point optimization** minimizes energy consumption while maintaining required discharge pressure and respecting surge and power limits.

8. **Multi-objective optimization** handles competing objectives (e.g., production vs energy) and generates Pareto-optimal trade-off curves.

9. **Real-time optimization** automates the optimization cycle using live plant data, model updating, and set point implementation through the DCS.

10. **Robust optimization** accounts for uncertainty in reservoir, measurement, and equipment parameters to ensure reliable performance under varying conditions.

11. **Integrated asset modeling** couples reservoir, well, and facility models to capture the full system behavior. Iterative coupling between NeqSim facility models and reservoir models is the most practical approach for field-wide optimization.

12. **Practical implementation** requires careful attention to model fidelity, operator acceptance, move suppression, and transition management. The best mathematical optimum is useless if it cannot be safely implemented on the plant.

The choice of optimization method depends fundamentally on the problem structure. For the common case of optimizing 2–5 continuous variables (separator pressures, compressor set points) with a fast process simulator like NeqSim, simple parametric sweeps or derivative-free methods like Nelder-Mead are often sufficient and transparent. For larger problems with discrete decisions (routing, equipment selection) or multiple conflicting objectives, more sophisticated methods — evolutionary algorithms, surrogate models, or multi-objective optimization — become necessary.

The integration of process simulation with optimization is a powerful paradigm that enables engineers to move beyond trial-and-error approaches to systematic, quantitative decision-making. As digital twin technology matures and real-time data becomes more accessible, the methods presented in this chapter will increasingly be applied in automated, closed-loop optimization systems that continuously seek the best operating conditions for production facilities.

---


<!-- September 2026 source update -->
## Numerical optimum, physical feasibility and model scope

Production optimization now has a stronger distinction between a numerical candidate and an accepted process state. `ProductionOptimizer` replays the selected decision vector on the full model without relying on cached evidence before returning. Reported feasibility and live equipment readbacks therefore refer to that replayed point. If a selected point becomes physically infeasible, recorded feasible candidates are reconsidered in deterministic order; a failed final solve is an error, not a successful stale answer \cite{neqsim2026update}.

This guarantee does not make an unregistered restriction disappear. The objective, installed limits, flow basis, composition, convergence tolerance and evidence coverage remain the modeler's responsibility. Binary feasibility assumes a suitable monotonic feasible interval. Score-based searches require an explicit objective: an empty objective list has zero objective score and is not a declaration to maximize production.

The gas-lift allocation formulas in this chapter are illustrative response curves. They explain the equal-marginal-return principle, but they do not calculate tubing hydraulics and are not validated NeqSim well predictions. For design work replace them with qualified well-performance curves or a coupled reservoir/well/network calculation, and preserve lift-gas and produced-gas bases separately. Likewise, a grid of oil-rate/power results is only a candidate set; a Pareto frontier requires removal of dominated points.

---

## Exercises

**Exercise 22.1** — *Optimization Formulation*
A gas field produces through 4 wells into a common separator. Formulate the mathematical optimization problem to maximize total gas production subject to: (a) separator gas capacity of 6 MSm³/day, (b) individual well maximum rate of 2 MSm³/day, (c) export pipeline pressure of 100 bara. Identify the decision variables, objective function, and all constraints. State whether each constraint is an equality or inequality.

**Exercise 22.2** — *Separator Pressure Optimization*
Using NeqSim, build a three-stage separation model (HP, MP, LP) for a fluid with 40% methane, 15% C₃–C₆, 30% C₇+, and 15% water. Sweep the HP pressure from 30 to 80 bara and the MP pressure from 5 to 25 bara (with LP fixed at 2 bara). Generate a contour plot of stock tank oil rate and find the optimal HP and MP pressures. Compare your result with the equal pressure ratio rule.

**Exercise 22.3** — *Gas Lift Allocation*
Three wells have the following gas lift performance data (oil rate in Sm³/d vs gas lift rate in MSm³/d):

| Q_GL | Well 1 | Well 2 | Well 3 |
|------|--------|--------|--------|
| 0.00 | 800 | 1200 | 500 |
| 0.10 | 1100 | 1500 | 750 |
| 0.20 | 1300 | 1700 | 950 |
| 0.30 | 1420 | 1850 | 1080 |
| 0.40 | 1500 | 1950 | 1160 |
| 0.50 | 1550 | 2020 | 1210 |

Total gas lift available: 0.90 MSm³/d. Find the optimal allocation using the equal marginal return criterion. What is the total oil production at the optimum?

**Exercise 22.4** — *Gradient Estimation*
Write a Python function that estimates the gradient of a NeqSim process simulation objective function using forward finite differences. Apply it to the separator pressure optimization problem (Exercise 22.2) with perturbation sizes of $\epsilon = 0.1$, 1.0, and 5.0 bara. Discuss the effect of perturbation size on gradient accuracy.

**Exercise 22.5** — *Compressor Interstage Optimization*
A three-stage compression system operates from 5 bara (suction) to 200 bara (discharge) with intercooling to 35°C between stages. Using NeqSim, sweep the two interstage pressures and find the combination that minimizes total power. Compare with the theoretical equal pressure ratio result. How much power (in %) is saved compared to the worst combination?

**Exercise 22.6** — *Multi-Objective Trade-Off*
For the platform model in Section 22.13, add gas export quality (gas molecular weight, as a proxy for heating value) as a second objective. Generate the Pareto front of oil production rate vs gas molecular weight by varying the separator pressure from 25 to 75 bara. Discuss the trade-off: does maximizing oil rate degrade gas quality?

**Exercise 22.7** — *Robust Optimization*
The platform model has uncertain ambient temperature ($T_{\text{amb}} \in [10, 35]$ °C) affecting gas turbine power. For each of 5 separator pressures (35, 45, 55, 65, 75 bara), evaluate the compressor power at $T_{\text{amb}} = 10, 20, 30, 35$ °C. Find the separator pressure that maximizes oil production while ensuring the compressor power never exceeds 40 MW at any ambient temperature. This is the robust optimal solution.

---

## References

1. Biegler, L.T. (2010). *Nonlinear Programming: Concepts, Algorithms, and Applications to Chemical Processes*. Philadelphia, PA: SIAM.
2. Edgar, T.F., Himmelblau, D.M., and Lasdon, L.S. (2001). *Optimization of Chemical Processes*, 2nd edn. New York: McGraw-Hill.
3. Nocedal, J. and Wright, S.J. (2006). *Numerical Optimization*, 2nd edn. New York: Springer.
4. Conn, A.R., Scheinberg, K., and Vicente, L.N. (2009). *Introduction to Derivative-Free Optimization*. Philadelphia, PA: SIAM.
5. Deb, K. (2001). *Multi-Objective Optimization Using Evolutionary Algorithms*. Chichester: John Wiley & Sons.
6. Forrester, A.I.J., Sóbester, A., and Keane, A.J. (2008). *Engineering Design via Surrogate Modelling*. Chichester: John Wiley & Sons.
7. Bieker, H.P., Slupphaug, O., and Johansen, T.A. (2007). "Real-Time Production Optimization of Oil and Gas Production Systems: A Technology Survey." *SPE Production & Operations*, 22(4), pp. 382–391.
8. Foss, B. (2012). "Process Control in Conventional Oil and Gas Fields — Challenges and Opportunities." *Control Engineering Practice*, 20(10), pp. 1058–1064.
9. Kosmidis, V.D., Perkins, J.D., and Pistikopoulos, E.N. (2004). "Optimization of Well Oil Rate Allocations in Petroleum Field Operations." *Industrial & Engineering Chemistry Research*, 43(14), pp. 3513–3527.
10. Sharma, R., Fjalestad, K., and Glemmestad, B. (2011). "Optimization of Lift Gas Allocation in a Gas Lifted Oil Field as Non-Linear Optimization Problem." *Modeling, Identification and Control*, 32(3), pp. 115–123.
11. Camponogara, E. and Nakashima, P.H.R. (2006). "Solving a Gas-Lift Optimization Problem by Dynamic Programming." *European Journal of Operational Research*, 174(2), pp. 1220–1246.
12. Nwachukwu, A. and Jeong, H. (2018). "Surrogate-Based Optimization for Production Forecasting and Optimization." *SPE Journal*, 23(4), pp. 1242–1263.
13. Dale, S.I. and Smith, R. (1995). "Process Optimization." In *Kirk-Othmer Encyclopedia of Chemical Technology*. New York: John Wiley & Sons.
14. Saputelli, L.A., Nikolaou, M., and Economides, M.J. (2005). "Real-Time Reservoir Management: A Multiscale Adaptive Optimization and Control Framework." *SPE 94035*.


