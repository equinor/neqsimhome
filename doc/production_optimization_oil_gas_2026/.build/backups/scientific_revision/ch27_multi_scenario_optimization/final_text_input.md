# Multi-Scenario and Stochastic Optimization

<!-- Chapter metadata -->
<!-- Notebooks: ch28_scenario_optimization.ipynb, ch28_monte_carlo_npv.ipynb, ch28_tornado_analysis.ipynb -->
<!-- Estimated pages: 42 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Explain why single-point (deterministic) optimization is insufficient for production systems subject to reservoir, market, and operational uncertainties, and articulate the value of robust, scenario-based decision-making
2. Categorize the principal sources of uncertainty in oil and gas production systems — reservoir, well, facility, market, and environmental — and assess their relative impact on key performance indicators
3. Formulate a scenario-based optimization problem with probability-weighted objectives and scenario-dependent constraints, and distinguish expected-value, minimax, and minimax-regret formulations
4. Use the NeqSim `ScenarioRequest` and `ScenarioKpi` APIs to define, execute, and compare multiple operating scenarios programmatically, including multi-scenario VFP generation
5. Design and execute a Monte Carlo simulation for production optimization using NeqSim, incorporating Latin Hypercube Sampling, P10/P50/P90 quantification, and tornado-diagram sensitivity analysis
6. Apply stochastic programming and real-options concepts to sequential production decisions under uncertainty, including facility sizing, phased development, and deferral options

---

## 27.1 Introduction

The optimization methods developed in Chapters 22 through 26 share a common assumption: the input data — fluid composition, reservoir pressure, equipment performance, commodity prices — are known with certainty. In practice, this assumption is never satisfied. Reservoir volumes carry geological uncertainty; well productivity depends on unmapped heterogeneity; equipment degrades unpredictably; and commodity prices fluctuate with global markets. A production plan that is optimal under one set of assumptions may perform poorly — or even become infeasible — when reality deviates from those assumptions.

This chapter addresses the question: *how should we optimize production when the future is uncertain?*

The answer lies in **multi-scenario** and **stochastic** optimization — techniques that explicitly represent uncertainty through multiple possible futures (scenarios) and seek decisions that perform well across the range of outcomes rather than being finely tuned to a single prediction. These techniques are well established in operations research, financial engineering, and reservoir management, but their application to *surface production optimization* — where NeqSim operates — is less commonly discussed in the literature.

A deterministic base case cannot establish the probability of negative NPV or the value of more information. Those claims require declared joint input distributions, physically consistent production profiles, cash-flow timing and explicit sampling error. Section 27.11 supplies a reproducible reservoir-tank example instead of assuming a risk percentage or sensitivity ranking.

The chapter proceeds as follows. Section 27.2 catalogues the sources of uncertainty in production systems. Section 27.3 develops the mathematical framework for scenario-based optimization. Sections 27.4 and 27.5 introduce the NeqSim APIs for scenario execution and multi-scenario VFP generation. Sections 27.6 and 27.7 cover Monte Carlo simulation and sensitivity analysis. Sections 27.8 through 27.10 address robust optimization, stochastic programming, and real options. Section 27.11 presents a comprehensive case study, and Section 27.12 summarizes the chapter.

---

## 27.2 Sources of Uncertainty in Production Systems

Uncertainty in oil and gas production systems originates from multiple domains. A structured taxonomy helps the engineer identify which uncertainties matter most for a given decision and select appropriate quantification methods. Table 27.1 categorizes the principal uncertainty sources.

**Table 27.1.** Sources of uncertainty in production systems, categorized by domain.

| Domain | Uncertainty Parameter | Illustrative range requiring calibration | Impact on Production |
|--------|----------------------|---------------|---------------------|
| **Reservoir** | Gas/oil initially in place (GIP/STOIIP) | ±30–50% pre-appraisal | Total recoverable volume |
| | Aquifer strength and connectivity | Weak to strong | Pressure support, water breakthrough timing |
| | Permeability distribution | Log-normal, CV 0.5–2.0 | Well productivity, sweep efficiency |
| | Relative permeability curves | ±20% on endpoints | Water cut evolution, gas breakthrough |
| | Reservoir compartmentalization | Connected vs. isolated | Drainage area per well |
| **Wells** | Productivity index (PI/J) | ±20–40% | Deliverability per well |
| | Water breakthrough time | ±1–5 years | Water handling load |
| | Sand production onset | Uncertain | Rate limits, workovers |
| | Artificial lift performance | ±10–20% on efficiency | Net production rate |
| **Facilities** | Equipment degradation (fouling, erosion) | 5–30% capacity loss over life | Processing capacity |
| | Compressor efficiency decline | Service-specific; no annual rate established here | Gas handling, power consumption |
| | Separator internals condition | Variable | Separation efficiency, carryover |
| | Heat exchanger fouling factor | 0.0001–0.001 m²K/W | Approach temperature, capacity |
| **Market** | Oil price (Brent) | ±30–60 $/bbl range | Revenue, NPV |
| | Gas price (NBP, Henry Hub) | ±1–3 $/MMBtu | Revenue, gas monetization |
| | Exchange rates | ±10–20% | Local-currency costs |
| | Carbon tax/ETS price | 0–150 $/tCO₂ | Operating cost, emissions penalties |
| **Environment** | Metocean conditions | Seasonal, extreme events | Flow assurance, uptime |
| | Ambient temperature | ±15°C seasonal | Cooling capacity, air-cooled HX |
| | Pipeline arrival temperature | ±5–10°C | Hydrate risk, wax deposition |
| | Seabed temperature | ±2°C | Insulation requirements |

### 27.2.1 Reservoir Uncertainty

Reservoir uncertainty is often the dominant source of uncertainty in field development decisions and early-life production optimization. The gas or oil initially in place (GIP/STOIIP) is typically characterized by a probability distribution — often triangular or log-normal — with P10, P50, and P90 estimates derived from geological and geophysical interpretation. This uncertainty propagates directly into recoverable volumes and production profiles.

Aquifer strength determines the pressure support available to the reservoir. A strong aquifer maintains reservoir pressure but brings early water breakthrough; a weak aquifer allows pressure depletion but delays water production. The uncertainty in aquifer parameters (size, permeability, connectivity) translates into uncertainty in the timing and magnitude of water production — a critical input to facility sizing.

Permeability heterogeneity affects well-to-well variation in productivity. In a development with six wells, the highest-productivity well may produce three to five times the rate of the lowest, depending on the degree of heterogeneity. This has direct implications for well allocation optimization: the optimal choke settings depend on the relative productivities, which are uncertain.

### 27.2.2 Well Uncertainty

Well productivity combines reservoir uncertainty (permeability, skin) with completion uncertainty (stimulation effectiveness, gravel pack quality). The productivity index $J$ is typically uncertain by ±20–40% even after a well test, because the test duration is insufficient to establish a stable drainage area.

Water breakthrough timing is a function of reservoir geometry, aquifer behavior, and well placement — all uncertain. Early water breakthrough can overwhelm the water treatment system, forcing production curtailment; late breakthrough allows extended plateau production. The uncertainty in breakthrough time is often the controlling factor in water handling facility sizing.

### 27.2.3 Facility and Equipment Uncertainty

Equipment performance degrades over time. Compressor efficiency declines due to fouling and erosion; heat exchanger capacity decreases due to fouling; separator internals may be damaged or plugged. The rate of degradation is uncertain and depends on fluid properties (sand content, corrosive species), operating conditions, and maintenance effectiveness.

These uncertainties affect the *capacity constraints* that bound the optimization problem. A separator designed for 100,000 kg/hr may effectively handle only 85,000 kg/hr after five years of fouling — but the actual degradation is uncertain.

### 27.2.4 Market Uncertainty

Oil and gas prices are perhaps the most visible uncertainty in field economics. Price volatility affects not only NPV calculations but also operational decisions — at low prices, marginal wells may be shut in; at high prices, debottlenecking investments become attractive.

The emergence of carbon pricing adds a new dimension of market uncertainty. A field development optimized for zero carbon cost may look very different from one optimized for 100 $/tCO₂ — particularly for gas-intensive developments where flaring and venting penalties are significant.

### 27.2.5 Environmental Uncertainty

Ambient and seabed temperature affect flow assurance conditions (hydrate formation, wax deposition) and cooling system performance (air-cooled heat exchanger capacity). Metocean conditions (waves, currents, wind) affect platform availability and subsea operations. These uncertainties are often characterized by seasonal distributions and extreme-value statistics.

---

## 27.3 Scenario-Based Optimization

### 27.3.1 Defining Scenarios

A **scenario** is a consistent set of assumptions about uncertain parameters. For production optimization, a scenario typically specifies:

- Reservoir parameters (pressure, GIP, aquifer strength)
- Well parameters (productivity indices, water cuts, GORs)
- Facility parameters (equipment efficiencies, degradation state)
- Economic parameters (commodity prices, cost escalation)
- Environmental parameters (ambient temperature, seabed temperature)

Scenarios are constructed to span the range of plausible futures. The simplest approach uses three scenarios — low, base, and high — for each uncertain parameter. For $n$ uncertain parameters, a full factorial design produces $3^n$ scenarios, which becomes impractical for large $n$. In practice, scenarios are selected using:

- **Expert judgment**: A small number (3–10) of internally consistent scenarios representing distinct futures (e.g., "high resource, low price" vs. "low resource, high price")
- **Experimental design**: Latin Hypercube or Sobol sequences that sample the parameter space efficiently
- **Scenario trees**: Branching structures where uncertainty is revealed sequentially over time

### 27.3.2 Mathematical Formulation

The scenario-based optimization problem can be stated as:

$$
\max_{x} \sum_{s=1}^{S} p_s \cdot f(x, \xi_s) \quad \text{s.t.} \quad g(x, \xi_s) \leq 0, \; \forall s
$$

where:

- $x$ is the vector of decision variables (choke settings, flow rates, equipment sizes)
- $\xi_s$ is the parameter vector for scenario $s$
- $p_s$ is the probability weight of scenario $s$ (with $\sum p_s = 1$)
- $f(x, \xi_s)$ is the objective function (e.g., production rate, NPV) evaluated under scenario $s$
- $g(x, \xi_s) \leq 0$ are the constraints (equipment capacities) under scenario $s$

The critical feature is that the constraints must be satisfied in *every* scenario — the same decision $x$ must satisfy every included scenario. This is not a guarantee for unrepresented futures or the entire continuous uncertainty set. This is more conservative than optimizing for the expected scenario alone.

### 27.3.3 Expected Value Optimization

The simplest approach is **expected value optimization**, which maximizes the probability-weighted average of the objective:

$$
\max_{x} \; \mathbb{E}[f(x, \xi)] = \sum_{s=1}^{S} p_s \cdot f(x, \xi_s)
$$

This is appropriate when the decision-maker is risk-neutral — indifferent between a certain outcome of $\bar{f}$ and a lottery with expected value $\bar{f}$. Risk attitude is a declared decision preference; project size and irreversibility alone do not determine it.

### 27.3.4 Minimax (Worst-Case) Optimization

The **minimax** formulation maximizes the worst-case outcome:

$$
\max_{x} \; \min_{s=1,\ldots,S} f(x, \xi_s)
$$

This is extremely conservative — it sacrifices expected performance to protect against the worst scenario. It is appropriate when the downside risk is catastrophic (e.g., safety-critical decisions) but overly pessimistic for routine production optimization.

### 27.3.5 Minimax Regret

A more balanced approach is **minimax regret**, which minimizes the maximum "missed opportunity" across scenarios:

$$
\min_{x} \; \max_{s=1,\ldots,S} \left[ f(x_s^*, \xi_s) - f(x, \xi_s) \right]
$$

where $x_s^*$ is the optimal decision if scenario $s$ were known with certainty. The regret for decision $x$ in scenario $s$ is the difference between what could have been achieved (with perfect foresight) and what was actually achieved. Minimax regret seeks a decision that is "close to optimal" in every scenario, even if it is optimal in none.

### 27.3.6 Conditional Value at Risk (CVaR)

For economic objectives (NPV, revenue), **Conditional Value at Risk** (CVaR) provides a coherent measure of downside risk:

$$
\max_{x} \; \text{CVaR}_\alpha[f(x, \xi)] = \max_{x} \; \mathbb{E}\left[ f(x, \xi) \mid f(x, \xi) \leq \text{VaR}_\alpha \right]
$$

Here $\alpha$ is a lower-tail probability, such as 0.05, rather than the usual upper-tail loss confidence of 0.95. The conditional-mean notation applies to continuous distributions; for atoms use the threshold formulation in Chapter 22. CVaR maximizes the average outcome in the worst $\alpha$ fraction of scenarios. It is less conservative than minimax (which focuses on a single worst case) but more conservative than expected value.

---

## 27.4 The ScenarioRequest API in NeqSim

NeqSim provides a structured API for defining, executing, and comparing multiple scenarios through the `ProductionOptimizer.ScenarioRequest` class and the associated `ScenarioKpi` and `ScenarioComparisonResult` classes.

### 27.4.1 Creating Scenario Requests

A `ScenarioRequest` encapsulates a named scenario with its own process system, feed stream and optimization configuration. Keep probability weights explicitly in the application-level decision analysis. Multiple scenarios can be created and passed to the optimizer for batch evaluation:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import jpype

# Import NeqSim classes
SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
ThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve
Compressor = jneqsim.process.equipment.compressor.Compressor
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer

def build_scenario(name, flow_rate, pressure, temperature, water_cut):
    """Build a process system for a given scenario."""
    fluid = SystemSrkEos(temperature + 273.15, pressure)
    fluid.addComponent("methane", 0.70 * (1.0 - water_cut))
    fluid.addComponent("ethane", 0.10 * (1.0 - water_cut))
    fluid.addComponent("propane", 0.05 * (1.0 - water_cut))
    fluid.addComponent("nC10", 0.10 * (1.0 - water_cut))
    fluid.addComponent("water", water_cut)
    fluid.setMixingRule("classic")
    fluid.setMultiPhaseCheck(True)

    feed = Stream("feed", fluid)
    feed.setFlowRate(flow_rate, "kg/hr")

    separator = Separator("HP separator", feed)
    valve = ThrottlingValve("choke", separator.getGasOutStream())
    valve.setOutletPressure(25.0, "bara")
    compressor = Compressor("compressor", valve.getOutletStream())
    compressor.setOutletPressure(80.0, "bara")

    process = ProcessSystem()
    process.add(feed)
    process.add(separator)
    process.add(valve)
    process.add(compressor)
    process.run()

    return process, feed

# Define five scenarios spanning the uncertainty space
scenarios_def = [
    ("Low rate, low WC",   60000.0, 55.0, 30.0, 0.05),
    ("Base case",          80000.0, 60.0, 35.0, 0.10),
    ("High rate",         100000.0, 65.0, 35.0, 0.10),
    ("High water cut",     80000.0, 55.0, 40.0, 0.30),
    ("Late life depleted", 50000.0, 40.0, 45.0, 0.40),
]

probabilities = [0.15, 0.40, 0.20, 0.15, 0.10]

scenario_requests = []
for (name, flow, pres, temp, wc), prob in zip(scenarios_def, probabilities):
    process, feed = build_scenario(name, flow, pres, temp, wc)
    config = (ProductionOptimizer.OptimizationConfig(30000.0, 120000.0)
              .rateUnit("kg/hr").maxIterations(20)
              .searchMode(ProductionOptimizer.SearchMode.BINARY_FEASIBILITY))
    scenario = ProductionOptimizer.ScenarioRequest(
        name, process, feed, config, None, None
    )
    scenario_requests.append(scenario)

print(f"Created {len(scenario_requests)} scenarios")
for req, prob in zip(scenario_requests, probabilities):
    print(f"  {req.getName()}: probability = {prob:.2f}")
```

### 27.4.2 Scenario KPIs and Comparison

The `ScenarioKpi` class defines the metrics used to evaluate and compare scenarios. Built-in KPIs include the optimal rate, optimization score, and named objective values. The `compareScenarios()` method runs the optimizer on each scenario and returns a structured comparison:

```python
# Scenario probabilities are study metadata, not constructor arguments.
optimizer = ProductionOptimizer()
comparison = optimizer.compareScenarios(
    jpype.java.util.ArrayList(scenario_requests),
    jpype.java.util.ArrayList([ProductionOptimizer.ScenarioKpi.optimalRate("kg/hr")]))
print(str(comparison))
```

### 27.4.3 Probability-Weighted Expected Performance

Using the scenario comparison results, the expected performance across all scenarios is computed as:

$$
\bar{f} = \sum_{s=1}^{S} p_s \cdot f_s^*
$$

Here each $f_s^*$ uses a separately optimized decision. Its weighted mean is a wait-and-see (perfect-information/adaptive) value, not the achievable expected value of one here-and-now decision. To evaluate one decision $x$, use $f(x,\xi_s)$ in every term. The corresponding variance summarizes spread:

$$
\sigma^2 = \sum_{s=1}^{S} p_s \cdot (f_s^* - \bar{f})^2
$$

A decision with high $\bar{f}$ but low $\sigma$ is preferred to one with the same $\bar{f}$ but higher $\sigma$, as it is more robust to uncertainty.

---

## 27.5 Multi-Scenario VFP Generation

### 27.5.1 The Role of VFP Tables

Vertical Flow Performance (VFP) tables are lookup tables that relate wellbore flowing conditions — typically bottomhole flowing pressure as a function of tubing head pressure, liquid rate, water cut, GOR, and artificial lift rate. They are used in reservoir simulation to couple the surface network model with the reservoir model without running the full multiphase flow calculation at every timestep.

VFP tables must cover the range of conditions expected during the field life. Since future conditions are uncertain, multiple VFP tables are needed — one for each combination of water cut, GOR, and pressure depletion scenario. The `MultiScenarioVFPGenerator` automates this process.

### 27.5.2 Generating VFP Tables Across Parameter Ranges

The `MultiScenarioVFPGenerator` creates VFP tables by running the NeqSim wellbore model across a grid of operating conditions:

```python
MultiScenarioVFPGenerator = jneqsim.process.util.optimizer.MultiScenarioVFPGenerator

# Define the parameter ranges for VFP generation
water_cuts = [0.0, 0.10, 0.20, 0.30, 0.50, 0.70]
gors = [500.0, 1000.0, 2000.0, 4000.0]   # Sm3/Sm3
rates = [5000.0, 10000.0, 20000.0, 40000.0, 60000.0]  # kg/hr
thps = [20.0, 30.0, 40.0, 50.0, 60.0, 80.0]  # bara (tubing head pressures)

# Build VFP table structure
vfp_table = MultiScenarioVFPGenerator.VFPTable(
    jpype.JArray(jpype.JDouble)(rates),
    jpype.JArray(jpype.JDouble)(thps),
    jpype.JArray(jpype.JDouble)(water_cuts),
    jpype.JArray(jpype.JDouble)(gors)
)

print(f"VFP table dimensions:")
print(f"  Rates: {len(rates)} points")
print(f"  THP: {len(thps)} points")
print(f"  Water cuts: {len(water_cuts)} points")
print(f"  GORs: {len(gors)} points")
print(f"  Total evaluations: {len(rates) * len(thps) * len(water_cuts) * len(gors)}")
```

### 27.5.3 Use in Reservoir Simulation Coupling

The generated VFP tables serve as the interface between the reservoir simulator and the surface network. During a coupled simulation:

1. The reservoir simulator calculates bottomhole conditions for each well
2. The VFP table interpolates to find the wellhead conditions
3. The surface network model (NeqSim `ProcessSystem`) receives the wellhead streams
4. Facility constraints are evaluated and fed back to the well allocation optimizer

This coupling allows reservoir uncertainty (pressure depletion, water breakthrough) to propagate through the production system and be captured in the multi-scenario analysis. Qualified tables support interpolation only inside their tested axes and physical validity range. Additional scenarios alone do not validate extrapolation, well hydraulics or convergence of the coupling.

### 27.5.4 Scenario-Dependent VFP Selection

In a multi-scenario reservoir simulation, different scenarios may require different VFP tables:

- **Pressure depletion scenarios**: Early-life (high reservoir pressure) vs. late-life (depleted)
- **Water breakthrough scenarios**: Pre-breakthrough (dry gas/oil) vs. post-breakthrough (high water cut)
- **GOR evolution scenarios**: Solution gas drive (increasing GOR) vs. gas cap expansion

The scenario framework links each reservoir scenario to the appropriate VFP table, ensuring consistent treatment of uncertainty across the reservoir and surface models.

---

## 27.6 Monte Carlo Simulation for Production Optimization

### 27.6.1 The Monte Carlo Approach

Monte Carlo simulation replaces the discrete set of scenarios with a large number of random samples drawn from the uncertainty distributions. For each sample, the production system is simulated and the performance metric (production rate, NPV, etc.) is recorded. The ensemble of results provides a full probability distribution of the performance metric, from which P10, P50, and P90 quantiles are extracted.

The Monte Carlo algorithm for production optimization is:

1. Define the uncertain parameters and their probability distributions
2. Generate $N$ samples from the joint distribution (typically $N = 200$–$1000$)
3. For each sample $k = 1, \ldots, N$:
   a. Set the uncertain parameters to the sampled values
   b. Run the NeqSim process simulation
   c. Evaluate the performance metric $f_k$
4. Compute statistics: mean, standard deviation, P10, P50, P90
5. Construct histograms and cumulative distribution functions

### 27.6.2 Latin Hypercube Sampling

Simple random sampling requires many iterations to adequately cover the parameter space, especially in high dimensions. **Latin Hypercube Sampling** (LHS) provides better coverage with fewer samples by ensuring that each parameter's marginal distribution is evenly sampled.

For $N$ samples of $d$ parameters, LHS divides each parameter's range into $N$ equal-probability intervals and draws exactly one sample from each interval, then randomly pairs the intervals across parameters. This stratifies each marginal probability scale, not necessarily the physical value scale. Apply inverse marginal CDFs and a justified dependence model; random pairing represents independent inputs.

The benefit of LHS depends on the response and dependence structure. There is no general fivefold sample reduction, particularly for rare events, discontinuities or tail quantiles. Compare independent replicated designs at the required precision \cite{jcgm101mc}.

### 27.6.3 Python Implementation with NeqSim

The following example demonstrates a Monte Carlo analysis of a gas processing facility with uncertain feed rate, feed pressure, and water cut:

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import qmc

import jpype
jneqsim = jpype.JPackage("neqsim")

SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
Compressor = jneqsim.process.equipment.compressor.Compressor
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# --- Define uncertain parameters ---
param_ranges = {
    "feed_rate_kg_hr":  (50000.0, 120000.0),    # Low to high production
    "feed_pressure_bara": (35.0, 75.0),          # Depletion range
    "water_cut":         (0.02, 0.45),           # Early to late life
    "feed_temperature_C": (25.0, 50.0),          # Seasonal variation
    "compressor_eff":    (0.70, 0.85),           # Degradation range
}

n_params = len(param_ranges)
n_samples = 200

# --- Latin Hypercube Sampling ---
sampler = qmc.LatinHypercube(d=n_params, seed=42)
lhs_unit = sampler.random(n=n_samples)

# Scale to parameter ranges
param_names = list(param_ranges.keys())
samples = np.zeros((n_samples, n_params))
for j, name in enumerate(param_names):
    low, high = param_ranges[name]
    samples[:, j] = qmc.scale(lhs_unit[:, j:j+1], low, high).flatten()

# --- Monte Carlo loop ---
results = {
    "gas_production_kg_hr": [],
    "compressor_power_kW": [],
    "separator_gas_rate_kg_hr": [],
}

for i in range(n_samples):
    feed_rate = samples[i, 0]
    feed_pres = samples[i, 1]
    water_cut = samples[i, 2]
    feed_temp = samples[i, 3]
    comp_eff  = samples[i, 4]

    try:
        # Build and run the process for this sample
        fluid = SystemSrkEos(feed_temp + 273.15, feed_pres)
        fluid.addComponent("methane", 0.75 * (1.0 - water_cut))
        fluid.addComponent("ethane", 0.08 * (1.0 - water_cut))
        fluid.addComponent("propane", 0.04 * (1.0 - water_cut))
        fluid.addComponent("nC10", 0.08 * (1.0 - water_cut))
        fluid.addComponent("water", water_cut)
        fluid.setMixingRule("classic")
        fluid.setMultiPhaseCheck(True)

        feed = Stream("feed", fluid)
        feed.setFlowRate(feed_rate, "kg/hr")

        sep = Separator("HP sep", feed)

        comp = Compressor("export compressor", sep.getGasOutStream())
        comp.setOutletPressure(120.0, "bara")
        comp.setIsentropicEfficiency(comp_eff)

        process = ProcessSystem()
        process.add(feed)
        process.add(sep)
        process.add(comp)
        process.run()

        gas_rate = sep.getGasOutStream().getFlowRate("kg/hr")
        comp_power = comp.getPower("kW")

        results["gas_production_kg_hr"].append(gas_rate)
        results["compressor_power_kW"].append(comp_power)
        results["separator_gas_rate_kg_hr"].append(gas_rate)

    except Exception as e:
        # Record NaN for failed simulations
        results["gas_production_kg_hr"].append(np.nan)
        results["compressor_power_kW"].append(np.nan)
        results["separator_gas_rate_kg_hr"].append(np.nan)

    if (i + 1) % 50 == 0:
        print(f"  Completed {i + 1}/{n_samples} simulations")

# --- Post-processing ---
gas_prod = np.array(results["gas_production_kg_hr"])
gas_prod = gas_prod[~np.isnan(gas_prod)]

p10 = np.percentile(gas_prod, 10)
p50 = np.percentile(gas_prod, 50)
p90 = np.percentile(gas_prod, 90)

print(f"\nGas Production (kg/hr):")
print(f"  P10 = {p10:.0f}")
print(f"  P50 = {p50:.0f}")
print(f"  P90 = {p90:.0f}")
print(f"  Mean = {np.mean(gas_prod):.0f}")
print(f"  Std  = {np.std(gas_prod):.0f}")
```

### 27.6.4 Convergence Diagnostics

For independent identically distributed samples with finite variance, the mean's standard error is $s/\sqrt{N}$. Quantile precision additionally depends on the density near the quantile: asymptotically $\operatorname{SE}(\hat q_p)\approx\sqrt{p(1-p)/N}/f_Y(q_p)$. No universal $N=200$ rule guarantees a percentage error. LHS requires an appropriate variance estimator or independent randomized replications; ordinary IID formulas do not automatically apply.

Use independent repeated seeds and confidence intervals for each decision-relevant output, including failure probability. A stable running median does not demonstrate stable tails. State the percentile convention: this chapter uses **CDF percentiles**, so P10 is the lower 10th percentile and P90 the upper 90th percentile. Petroleum reserves reporting often uses exceedance probabilities with reversed labels; never mix the conventions.

---

## 27.7 Sensitivity Analysis and Tornado Diagrams

### 27.7.1 One-at-a-Time Sensitivity

Sensitivity analysis identifies which uncertain parameters have the greatest impact on the performance metric. The simplest approach is **one-at-a-time** (OAT) sensitivity: fix all parameters at their base values, vary one parameter from its low to high value, and record the change in the objective. Repeat for each parameter.

For a parameter $\xi_j$ with range $[\xi_j^L, \xi_j^H]$ and base value $\xi_j^B$:

$$
\Delta f_j^{-} = f(\xi_j^L) - f(\xi_j^B) \quad \text{(downside swing)}
$$

$$
\Delta f_j^{+} = f(\xi_j^H) - f(\xi_j^B) \quad \text{(upside swing)}
$$

Use the range of the low/base/high responses to describe an OAT swing. Summing absolute endpoint deviations overstates the range when both endpoints lie on the same side of the base. OAT does not quantify interactions or global variance contributions.

### 27.7.2 Tornado Diagram

A **tornado diagram** ranks the parameters by their impact, with the most influential parameter at the top. The horizontal bars show the downside and upside swings, centered on the base case value. The resulting figure resembles a tornado — widest at the top, narrowing toward the bottom.

```python
from pathlib import Path
Path("figures").mkdir(parents=True, exist_ok=True)
import numpy as np
import matplotlib.pyplot as plt

import jpype
jneqsim = jpype.JPackage("neqsim")

SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
Compressor = jneqsim.process.equipment.compressor.Compressor
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

def evaluate_gas_production(feed_rate, feed_pres, water_cut, temperature, comp_eff):
    """Run process simulation and return gas production rate."""
    fluid = SystemSrkEos(temperature + 273.15, feed_pres)
    fluid.addComponent("methane", 0.75 * (1.0 - water_cut))
    fluid.addComponent("ethane", 0.08 * (1.0 - water_cut))
    fluid.addComponent("propane", 0.04 * (1.0 - water_cut))
    fluid.addComponent("nC10", 0.08 * (1.0 - water_cut))
    fluid.addComponent("water", water_cut)
    fluid.setMixingRule("classic")
    fluid.setMultiPhaseCheck(True)

    feed = Stream("feed", fluid)
    feed.setFlowRate(feed_rate, "kg/hr")
    sep = Separator("HP sep", feed)
    comp = Compressor("compressor", sep.getGasOutStream())
    comp.setOutletPressure(120.0, "bara")
    comp.setIsentropicEfficiency(comp_eff)

    process = ProcessSystem()
    process.add(feed)
    process.add(sep)
    process.add(comp)
    process.run()
    return sep.getGasOutStream().getFlowRate("kg/hr")

# Base case parameters
base = {"feed_rate": 80000, "feed_pres": 55, "water_cut": 0.15,
        "temperature": 35, "comp_eff": 0.78}

# Low/high ranges for each parameter
ranges = {
    "Feed rate (kg/hr)":     ("feed_rate",   50000, 120000),
    "Feed pressure (bara)":  ("feed_pres",   35,    75),
    "Water cut (-)":         ("water_cut",   0.02,  0.45),
    "Temperature (°C)":      ("temperature", 25,    50),
    "Compressor efficiency": ("comp_eff",    0.70,  0.85),
}

# Evaluate base case
base_result = evaluate_gas_production(**base)

# One-at-a-time sensitivity
tornado_data = []
for label, (param, low, high) in ranges.items():
    params_low = dict(base); params_low[param] = low
    params_high = dict(base); params_high[param] = high
    result_low = evaluate_gas_production(**params_low)
    result_high = evaluate_gas_production(**params_high)
    tornado_data.append({
        "label": label,
        "low": result_low - base_result,
        "high": result_high - base_result,
        "swing": abs(result_high - result_low),
    })

# Sort by total swing (descending)
tornado_data.sort(key=lambda x: x["swing"], reverse=True)

# Plot tornado diagram
fig, ax = plt.subplots(figsize=(10, 6))
labels = [d["label"] for d in tornado_data]
lows = [d["low"] for d in tornado_data]
highs = [d["high"] for d in tornado_data]
y_pos = range(len(labels))

ax.barh(y_pos, highs, align="center", color="#2196F3", label="Upside", height=0.6)
ax.barh(y_pos, lows, align="center", color="#F44336", label="Downside", height=0.6)
ax.set_yticks(y_pos)
ax.set_yticklabels(labels)
ax.set_xlabel("Change in gas production (kg/hr)")
ax.set_title("Tornado Diagram — Sensitivity of Gas Production")
ax.axvline(x=0, color="black", linewidth=0.8)
ax.legend(loc="lower right")
ax.invert_yaxis()
plt.tight_layout()
plt.savefig("figures/fig28_tornado.png", dpi=150, bbox_inches="tight")
plt.show()
```

![Tornado diagram showing the sensitivity of gas production to uncertain input parameters. Feed rate and water cut dominate the sensitivity, while compressor efficiency has relatively minor impact.](figures/fig28_tornado.png)

### 27.7.3 Spider Plots

A **spider plot** (or sensitivity plot) shows the objective function value as each parameter is varied continuously from its low to high value, with all other parameters at their base values. Unlike the tornado diagram, which shows only the endpoints, the spider plot reveals nonlinearities — a parameter whose spider curve is concave has diminishing marginal impact, while a convex curve has increasing impact.

Spider plots are constructed by evaluating the objective at 5–10 evenly spaced values of each parameter. The horizontal axis is normalized (0 = low, 1 = high) to allow all parameters to be plotted on the same axes.

### 27.7.4 Interpreting Sensitivity Results

The sensitivity analysis serves three purposes:

1. **Prioritization**: Parameters with large swings deserve detailed uncertainty characterization (better data, more scenarios). Parameters with small swings can be fixed at their base values, reducing the dimensionality of the Monte Carlo analysis.

2. **Risk mitigation**: The parameter ranking guides risk mitigation strategies. A large price sensitivity does not prove that hedging is more valuable than appraisal; compare feasible mitigation costs, residual risk and the value of information. If water cut dominates gas production uncertainty, investing in subsea water separation may be warranted.

3. **Screening**: For complex systems with many uncertain parameters, the tornado analysis identifies the 3–5 parameters that dominate the uncertainty. Subsequent detailed analysis (Monte Carlo, stochastic programming) can focus on these critical parameters.

---

## 27.8 Robust Optimization

### 27.8.1 Concept and Motivation

**Robust optimization** seeks decisions that perform well across all plausible scenarios, rather than optimizing for a single expected scenario. The key distinction from expected-value optimization is the treatment of constraints: in robust optimization, the constraints must be satisfied in *every* scenario within a defined uncertainty set.

The general form is:

$$
\max_{x} \; f_0(x) \quad \text{s.t.} \quad g_j(x, \xi) \leq 0, \; \forall \xi \in \mathcal{U}, \; j = 1, \ldots, m
$$

where $\mathcal{U}$ is the uncertainty set — the range of parameter values considered plausible.

### 27.8.2 Safety Margins

A practical approach to robust optimization is to add **safety margins** to deterministic constraints. Instead of requiring the compressor power to be below the rated maximum $W_{\max}$, the robust constraint requires:

$$
W_{\text{comp}}(x, \xi) \leq W_{\max} - \Delta W \quad \forall \xi \in \mathcal{U}
$$

where $\Delta W$ is the safety margin. The challenge is selecting appropriate margins — too large wastes capacity, too small risks constraint violation.

An engineering approach is to set the safety margin as a multiple of the standard deviation of the constraint function across the uncertainty set:

$$
\Delta W = k \cdot \sigma_W
$$

A mean-plus-$k\sigma$ rule is a distributional chance-constraint approximation, not robust feasibility over a bounded set. Under a known Gaussian model, one-sided coverage is $\Phi(k)$: about 93.3% at 1.5 and 97.7% at 2.0. Non-Gaussian tails, uncertain moments and multiple constraints require separate treatment.

### 27.8.3 Application to Facility Constraints

In production optimization, robust constraints are particularly relevant for:

- **Gas handling capacity**: Must accommodate the range of GOR scenarios
- **Water treatment capacity**: Must accommodate early water breakthrough scenarios
- **Compression power**: Must accommodate degradation and high-temperature scenarios
- **Separator sizing**: Must accommodate the range of feed rates and compositions

Enforce the chosen limits explicitly in every required NeqSim scenario. A `SOFT` penalty can influence the objective but does not establish robust feasibility or a minimum safety margin.

### 27.8.4 RobustOptimizationStudy in NeqSim

NeqSim packages the scenario-based robustness evaluation in `RobustOptimizationStudy` (package `neqsim.process.fielddevelopment.integrated`). The study evaluates a candidate decision across a set of scenarios — supplied explicitly or drawn from a sampler — and returns the percentile spread and the fraction of scenarios in which the decision stays feasible:

```python
RobustOptimizationStudy = jneqsim.process.optimization.valuechain.RobustOptimizationStudy
study = RobustOptimizationStudy()
for inputs in ([3.0, 0.85, 250.0], [2.2, 0.78, 240.0], [3.8, 0.90, 255.0]):
    study.addScenario(inputs)
study.setRequiredConfidence(0.90)
# Explicit algebraic toy evaluator demonstrates the uncertainty API.
def scenario_value(decision, scenario):
    rate = float(decision[0])
    return RobustOptimizationStudy.ScenarioOutcome(
        rate * scenario[0] * scenario[1], rate <= scenario[2])
result = study.evaluateDecision([200.0], scenario_value)
print(result.getP10(), result.getP50(), result.getP90(), result.getFeasibleFraction())
```

Instead of enumerating scenarios, a `ScenarioSampler` can generate them stochastically with `setSampler(sampler, count)` and a fixed `setSeed(...)` for reproducibility. The `RobustResult` exposes `getP10()`, `getP50()`, `getP90()`, `getMean()`, `getFeasibleFraction()`, and `getDecision()`. When several candidate decisions are compared, `selectRobust(...)` returns the one that maximizes the chosen percentile while honouring the required confidence — a finite-scenario selection rule whose returned decision still needs independent replay, coverage checks and an explicit percentile convention. A sampled feasible fraction is not a confidence bound.

### 27.8.5 Parallel Scenario Evaluation with ParallelSweep

Robustness and Monte Carlo studies multiply the number of simulation runs by the scenario count, so NeqSim provides `ParallelSweep` to evaluate independent cases concurrently:

```python
ParallelSweep = jneqsim.process.optimization.valuechain.ParallelSweep
sweep = ParallelSweep().setParallelism(2)
scenario_inputs = jpype.java.util.ArrayList()
for pressure in (40.0, 60.0, 80.0):
    scenario_inputs.add(jpype.JArray(jpype.JDouble)([pressure]))
# A serialization-only toy example. Each real simulation worker must build its own model.
outputs = sweep.run(scenario_inputs, lambda inputs: jpype.JDouble(inputs[0] * 2.0))
print(list(outputs))
```

`run(inputs, evaluator)` returns one result per input vector in the same order, allowing the percentile and tornado post-processing of Sections 27.6–28.7 to scale to thousands of cases. Concurrency performance depends on JVM memory, model cost, shared resources and worker count; benchmark a sequential reference before claiming speed-up.

---

## 27.9 Stochastic Programming

### 27.9.1 Two-Stage Stochastic Programming

Many production optimization decisions have a sequential structure: some decisions must be made *before* uncertainty is resolved (first-stage, or "here-and-now" decisions), while others can be adapted *after* observing the actual outcome (second-stage, or "wait-and-see" decisions).

**First-stage decisions** (design):
- Facility capacity (separator size, compressor power rating)
- Pipeline diameter
- Number of well slots
- Platform topsides weight

**Second-stage decisions** (operations):
- Choke settings
- Gas lift allocation
- Compressor operating point
- Well shut-in decisions

The two-stage stochastic program is:

$$
\max_{x} \; c^T x + \sum_{s=1}^{S} p_s \cdot Q(x, \xi_s)
$$

where $x$ is the first-stage decision, $c^T x$ is the first-stage contribution (e.g., negative CAPEX), and $Q(x, \xi_s)$ is the optimal second-stage value (e.g., NPV from operations) under scenario $s$:

$$
Q(x, \xi_s) = \max_{y_s} \; d^T y_s \quad \text{s.t.} \quad T_s x + W_s y_s \leq h_s
$$

Here $y_s$ is the second-stage decision (operations) for scenario $s$, and the constraints couple the first-stage design with the second-stage operations.

### 27.9.2 Application to Facility Sizing

A common application is facility sizing under demand uncertainty. The first-stage decision is the installed capacity of each processing unit (separator, compressor, water treatment). The second-stage decision is the operating point for each scenario:

- **High demand scenario**: All wells at maximum rate, facility at full capacity
- **Base scenario**: Moderate production, comfortable margins
- **Low demand scenario**: Some wells shut in, facility under-utilized

The stochastic program balances the cost of over-sizing (higher CAPEX) against the cost of under-sizing (lost production in high-demand scenarios). Whether the stochastic design is larger or smaller than a base-case design depends on the scenario distribution, costs and recourse options; no universal direction follows.

### 27.9.3 Recourse and Flexibility

Recourse is the ability to adapt later decisions using information actually available then. Its value compares otherwise identical models with and without that flexibility. The following different quantity is the **expected value of perfect information**, comparing fully anticipative wait-and-see decisions with the nonanticipative stochastic solution:

$$
\text{EVPI} = \sum_{s=1}^{S} p_s \cdot V_s^* - V_{\text{SP}}
$$

where $V_s^*$ is the optimal value with perfect information about scenario $s$, and $V_{\text{SP}}$ is the optimal value of the stochastic program. The **Expected Value of Perfect Information** (EVPI) represents the maximum amount the decision-maker should pay for perfect forecasting.

Similarly, the **Value of the Stochastic Solution** (VSS) measures the benefit of solving the stochastic program rather than using the expected-value solution:

$$
\text{VSS} = V_{\text{SP}} - V_{\text{EV}}
$$

where $V_{\text{EV}}$ is the expected value obtained by optimizing for the mean scenario and then evaluating across all scenarios.

---

## 27.10 Real Options in Production Optimization

### 27.10.1 The Real Options Framework

Traditional NPV analysis treats investment decisions as now-or-never: the project is either sanctioned or rejected. In reality, many production decisions have **option value** — the ability to delay, expand, contract, or abandon the project as information is revealed.

Key real options in production optimization include:

- **Option to defer**: Wait for more reservoir data or better market conditions before committing to development
- **Option to expand**: Design the facility with expansion capacity (e.g., extra well slots, oversized piping) that can be activated if the reservoir is larger than expected
- **Option to contract**: Reduce production (shut in marginal wells) if prices decline
- **Option to switch**: Change operating mode (e.g., from gas export to gas injection for pressure support)
- **Option to abandon**: Cease production if operating costs exceed revenue

### 27.10.2 Decision Trees with NeqSim Evaluation

Real options analysis can be implemented using decision trees where each node represents a decision or an uncertainty resolution, and each terminal node is evaluated using a NeqSim process simulation:

```text
Year 0: Invest in Phase 1 development
├── Year 3: Reservoir larger than expected (p=0.3)
│   ├── Expand Phase 2 → NeqSim NPV calculation
│   └── Maintain Phase 1 → NeqSim NPV calculation
├── Year 3: Reservoir as expected (p=0.5)
│   └── Maintain Phase 1 → NeqSim NPV calculation
└── Year 3: Reservoir smaller than expected (p=0.2)
    ├── Continue → NeqSim NPV calculation
    └── Abandon → Residual value
```

At each terminal node, the NeqSim simulation computes the production profile, operating costs, and cash flows under the specific scenario. The tree is solved by backward induction: at each decision node, the optimal action is selected; at each chance node, the expected value is computed.

### 27.10.3 Valuing Flexibility

The option value is the difference between the decision-tree value (with flexibility) and the static NPV (without flexibility):

$$
V_{\text{option}} = V_{\text{tree}} - V_{\text{static}}
$$

This option value quantifies the benefit of designing the system with built-in flexibility. For production optimization, it justifies investments in:

- **Modular facilities** that can be expanded incrementally
- **Oversized infrastructure** (pipelines, risers) that accommodates upside scenarios
- **Flexible equipment** (variable-speed compressors, adjustable chokes)

Calculate flexibility value for the specified information timing, admissible decisions and costs. No generic percentage of static NPV is established here.

---

## 27.11 Case Study: Field Development Under Price and Reservoir Uncertainty

This section presents a comprehensive case study integrating the concepts from this chapter. A gas field development decision is analyzed under three sources of uncertainty: gas initially in place (GIP), gas price, and facility CAPEX.

### 27.11.1 Physical and Economic Basis

The illustrative dry-gas resource is triangular with lower endpoint 65, mode 100 and upper endpoint 145 GSm³. These are distribution parameters, not P10/P50/P90. The two facility capacities are 6 and 10 GSm³/year with assumed time-zero CAPEX of 12,000 and 18,000 MNOK. A 1 GSm³ resource cannot sustain the previous multi-GSm³/year plateau; production must close against the actual sampled inventory.

Each sample runs a NeqSim `SimpleReservoir` at constant 100°C, initialized at 250 bara with pure methane and SRK. A declared rate-control rule tapers withdrawal towards 50 bara; NeqSim solves the fixed-volume pressure at each annual step. This is an isothermal tank and assumed operating policy, not a calibrated reservoir-well-facility forecast. It has no aquifer, tubing, compressor or resource replacement. The imposed temperature entails an external heat supply; an adiabatic energy balance is not claimed.

Gas price is triangular (0.8, 1.5, 2.5) NOK/Sm³ and CAPEX multiplier is triangular (0.85, 1.0, 1.4). All three inputs are assumed independent. The cash-flow calculation is **pre-tax**, with CAPEX at time zero, annual OPEX at 2% of installed CAPEX and year-end sales over 25 years, discounted at 8%. It is not a Norwegian fiscal model. Each plan uses the same 200 stratified samples; this reduces comparison noise but does not establish tail confidence.

### 27.11.2 Monte Carlo with NeqSim Depletion

```python
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import qmc, triang
import jpype
jneqsim = jpype.JPackage("neqsim")
Path("figures").mkdir(parents=True,exist_ok=True)

def depletion_profile(gip_GSm3,capacity_GSm3_year,years=25):
    """Isothermal dry-gas material-balance tank; explicitly assumed withdrawal rule."""
    fluid=jneqsim.thermo.system.SystemSrkEos(373.15,250.0)
    fluid.addComponent('methane',1.0)
    fluid.setMixingRule('classic')
    probe=jneqsim.process.equipment.reservoir.SimpleReservoir('Unit-volume tank')
    probe.setReservoirFluid(fluid.clone(),1.0,0.0,0.0)
    reservoir_volume=gip_GSm3*1e9/float(probe.getGasInPlace('Sm3'))
    reservoir=jneqsim.process.equipment.reservoir.SimpleReservoir('Depletion tank')
    reservoir.setReservoirFluid(fluid,reservoir_volume,0.0,0.0)
    reservoir.setLowPressureLimit(1.0,'bara')
    producer=reservoir.addGasProducer('Gas production')
    reservoir.run()
    state=reservoir.getReservoirFluid()
    mass0=float(state.getTotalNumberOfMoles()*state.getMolarMass())
    initial_gip=float(reservoir.getGasInPlace('GSm3'))
    assert abs(initial_gip/gip_GSm3-1.0)<1e-8
    withdrawn=0.0;relative_errors=[];productions=[];pressures=[]
    for year in range(years):
        pressure=float(state.getPressure('bara'))
        # Assumed deliverability control: taper rate towards a 50 bara abandonment pressure.
        # This rule is not an IPR or a tubing solution; the tank pressure is solved by TV flash.
        supply_fraction=max(0.0,min(1.0,(pressure-50.0)/200.0))
        remaining=float(reservoir.getGasInPlace('GSm3'))
        annual=min(capacity_GSm3_year*supply_fraction,0.12*remaining)
        producer.setFlowRate(max(annual*1e9/365.0,1e-6),'Sm3/day')
        producer.run()
        dt=365.0*86400.0
        m_rate=float(producer.getFlowRate('kg/sec'))
        produced=float(producer.getFlowRate('Sm3/day'))*365.0/1e9
        withdrawn+=m_rate*dt
        reservoir.runTransient(dt,jpype.JClass('java.util.UUID').randomUUID())
        mass=float(state.getTotalNumberOfMoles()*state.getMolarMass())
        error=abs(mass-(mass0-withdrawn))/mass0
        assert error<1e-9
        assert mass>0.0 and 49.0<float(state.getPressure('bara'))<=250.0
        assert abs(state.getTemperature('K')-373.15)<1e-8
        relative_errors.append(error);productions.append(produced)
        pressures.append(float(state.getPressure('bara')))
    recovery=sum(productions)/initial_gip
    assert 0.0<recovery<1.0
    return {'production_GSm3':productions,'pressure_bara':pressures,
            'recovery_fraction':recovery,'gip_GSm3':initial_gip,
            'max_relative_mass_error':max(relative_errors)}

n_mc=200
u=qmc.LatinHypercube(d=3,seed=42).random(n_mc)
def triangular_quantiles(values,low,mode,high):
    return triang.ppf(values,(mode-low)/(high-low),loc=low,scale=high-low)
gip_samples=triangular_quantiles(u[:,0],65.,100.,145.)
price_samples=triangular_quantiles(u[:,1],.8,1.5,2.5)
capex_samples=triangular_quantiles(u[:,2],.85,1.,1.4)
plans={"Conservative":(6.,12000.),"Aggressive":(10.,18000.)}
outputs={}
discount=(1.08)**(-np.arange(1,26))
for name,(capacity,base_capex) in plans.items():
    records=[]
    for i in range(n_mc):
        profile=depletion_profile(float(gip_samples[i]),capacity)
        production=np.array(profile["production_GSm3"])
        installed=base_capex*capex_samples[i]
        cash=production*price_samples[i]*1000.0-.02*installed
        npv=float(-installed+cash@discount)
        assert np.isfinite(npv)
        records.append({"npv_MNOK":npv,**profile})
    outputs[name]=records
summary={}
for name,records in outputs.items():
    npvs=np.array([v["npv_MNOK"] for v in records])
    summary[name]={"N":len(records),"npv_cdf_P10_P50_P90_MNOK":
                   np.percentile(npvs,[10,50,90]).tolist(),
                   "probability_negative_sample":float(np.mean(npvs<0)),
                   "mean_npv_MNOK":float(npvs.mean()),
                   "recovery_cdf_P10_P50_P90":np.percentile(
                     [v["recovery_fraction"] for v in records],[10,50,90]).tolist(),
                   "total_gas_cdf_P10_P50_P90_GSm3":np.percentile(
                     [sum(v["production_GSm3"]) for v in records],[10,50,90]).tolist(),
                   "max_relative_mass_error":max(
                     v["max_relative_mass_error"] for v in records)}
summary["gip_cdf_P10_P50_P90_GSm3"]=np.percentile(gip_samples,[10,50,90]).tolist()
Path("ch27_depletion_monte_carlo.json").write_text(
    json.dumps({"summary":summary,"samples":outputs},indent=2))
print(json.dumps(summary,indent=2))
fig,axes=plt.subplots(1,2,figsize=(11,4))
for name,records in outputs.items():
    values=np.array([v["npv_MNOK"] for v in records])
    axes[0].hist(values,bins=25,alpha=.5,label=name)
    axes[1].plot(np.sort(values),np.arange(1,n_mc+1)/n_mc,label=name)
for ax in axes:
    ax.set_xlabel("Pre-tax NPV (MNOK)");ax.grid(alpha=.3);ax.legend()
axes[0].set_ylabel("Sample count");axes[1].set_ylabel("Empirical CDF")
fig.tight_layout()
fig.savefig("figures/ch27_verified_resource_npv.png",dpi=170,bbox_inches="tight")
plt.close(fig)
```

![Pre-tax NPV from 200 common LHS scenarios per plan, using a NeqSim isothermal gas tank and the declared annual withdrawal rule](figures/ch27_verified_resource_npv.png)

The figure compares the distribution under the stated resource and economic assumptions. Every annual withdrawal closes against the simulated tank inventory to relative mass error below $10^{-9}$; temperature and positive pressure are checked. The saved result reports resource, recovery and cumulative production percentiles alongside NPV, so economic results cannot be detached from their resource basis. A plan's larger production capacity accelerates withdrawal but also increases assumed CAPEX and OPEX. The balance of those effects, not a presumed risk ranking, determines the sampled NPV.

### 27.11.3 Decision and Remaining Qualification

Use the printed distributions to compare these two **fixed policies**, not to claim a robust optimum or a real option. Check annual-step sensitivity, probability distributions/dependence, operating costs and abandonment rules before an investment interpretation. A conditional expansion requires a separate nonanticipative decision tree with the expansion cost and information time. Neither the old arbitrary 10–20% option value nor a presumed hedging/appraisal ranking is supported by this example.

<!-- scientific-evidence test=devtools/scientific_uncertainty_probe.py baseline=verification/scientific_revision/ch27_depletion_probe.json -->

---

<!-- September 2026 source update -->
## Scenario isolation and current constraint evidence

A scenario is a complete model state: composition, rates, thermodynamic method, topology, equipment availability, installed limits and utility budgets. Reusing an unchanged flow vector after a limit or lineup change is not a valid cache hit. The current plant evidence contracts require stable identities and current calculation provenance, and the selected optimization point must be replayed against the active scenario \cite{neqsim2026update}.

Report scenario success, physical feasibility and evidence completeness separately. A finite but overloaded scenario is useful adverse-case evidence. A scenario with failed convergence or missing capacity evidence is unresolved and must not be ranked as if its absent load were zero. Preserve all failed samples with explicit causes in uncertainty studies; dropping them changes the sampled population and can bias percentiles.

For parallel execution, each worker needs an independent process model and decision state. Concurrency tests should reproduce a sequential reference before runtime claims are made. Record seed, composition, input ranges, solver settings and the number of successful/failed evaluations with every uncertainty or operating-envelope figure.

---


<!-- reviewed-notebook-results:start -->
## Reproduced Calculation Results

These examples use the stated fluid recipes and operating assumptions. Curves represent NeqSim calculations unless a caption identifies an analytical illustration, assumed equipment map or synthetic data.

![Compressor Utilization by Scenario](figures/ch28_scenario_utilization.png)

Base Case (opt: 185 t/hr): compressor utilization spans 5.038–131 % across the plotted cases. High GOR (opt: 152 t/hr): compressor utilization spans 6.201–161.2 % across the plotted cases.

Changing feed composition changes the gas mass sent to compression and therefore the power required per unit total feed. The same total feed rate has different feasibility in the three recipe scenarios; the water-enriched recipe is not a measured stock-tank water cut. Use the limiting credible composition or explicit scenario probabilities to select a robust target.

![Multi-Scenario Optimization Comparison](figures/ch28_scenario_comparison.png)

Optimal Rate (1000 kg/hr): optimal rate spans 151.7–243.3 1000 kg/hr across the plotted cases. Utilization at Optimum (%): compressor utilization spans 93.2–94.56 % across the plotted cases.

The reported rates are the largest sampled points below the stated 95 percent power-utilization threshold. The remaining margin includes the spacing of the sampled rate grid. Refine the grid or bisect each scenario boundary before comparing small capacity differences.

Selected numerical ranges from the plotted cases:

| Quantity / series | Minimum | Maximum | Unit |
|---|---:|---:|---|
| Base Case (opt: 185 t/hr): compressor utilization | 5.038 | 131 | % |
| Optimal Rate (1000 kg/hr): optimal rate | 151.7 | 243.3 | 1000 kg/hr |

Ranges describe the sampled cases; they are not independent validation tolerances.
<!-- reviewed-notebook-results:end -->

## 27.12 Summary

This chapter addressed the critical challenge of making production optimization decisions under uncertainty. Key takeaways include:

1. **Uncertainty is pervasive** in production systems, originating from reservoir parameters, well performance, equipment degradation, commodity prices, and environmental conditions. Ignoring uncertainty leads to decisions that appear optimal but may perform poorly in practice.

2. **Scenario-based optimization** represents uncertainty through a finite set of scenarios with assigned probabilities. The NeqSim `ScenarioRequest` and `ScenarioKpi` APIs provide a structured framework for defining, executing, and comparing scenarios.

3. **Multi-scenario VFP tables** extend the VFP methodology of Chapter 27 to cover the full range of uncertain parameters, enabling consistent coupling between reservoir and surface models under uncertainty.

4. **Monte Carlo simulation** with Latin Hypercube Sampling provides full probability distributions (P10/P50/P90) of production metrics. Sample size must be justified from precision of the relevant tails and failure probabilities; stratification alone supplies no universal guarantee.

5. **Tornado diagrams** rank uncertain parameters by their impact on the objective, guiding both data collection priorities and risk mitigation strategies.

6. **Robust optimization** adds safety margins to ensure feasibility across all scenarios; **stochastic programming** handles sequential decisions with recourse; and **real options** quantify the value of built-in flexibility.

The expected-value, minimax, and CVaR formulations provide a spectrum of risk attitudes, from risk-neutral through risk-averse. The choice of formulation should reflect the decision-maker's risk tolerance and the reversibility of the decision. For irreversible capacity investments, conservative formulations are warranted; for operational decisions that can be revised weekly, expected-value optimization is often adequate.

---

## Exercises

1. **Scenario construction.** A gas field has three uncertain parameters: GIP (low: 0.5, base: 1.0, high: 1.5 GSm³), gas price (low: 0.8, base: 1.5, high: 2.5 NOK/Sm³), and CAPEX multiplier (low: 0.85, base: 1.0, high: 1.3). Construct a set of 5 representative scenarios with probability weights that capture the key risk combinations. Explain why you chose those specific scenarios over a full factorial design.

2. **Monte Carlo convergence.** Implement the Monte Carlo analysis of Section 27.6.3 with $N = 50, 100, 200, 500$. Plot the P50 gas production estimate as a function of $N$ and determine the minimum $N$ required for the P50 estimate to stabilize within ±2% of its final value.

3. **Tornado analysis.** Using the code from Section 27.7.2, add two additional uncertain parameters: discharge pressure (range: 100–150 bara) and separator pressure (range: 40–80 bara). Re-run the tornado analysis and discuss whether these additional parameters change the parameter ranking.

4. **Robust vs. expected-value optimization.** For the gas processing facility of Section 27.6.3, compare the optimal feed rate under (a) expected-value optimization (maximize mean gas production) and (b) lower-tail reward optimization (maximize the CDF P10 gas production) with separately enforced scenario feasibility. Which approach gives a higher feed rate, and why?

5. **Two-stage facility sizing.** A platform must be designed with gas handling capacity $Q_g$ (first-stage decision) to serve wells whose total gas production is uncertain: low (40,000 kg/hr), base (70,000 kg/hr), or high (100,000 kg/hr) with probabilities 0.2, 0.5, 0.3. The time-zero capacity cost is 500 USD per (kg/hr) installed. Assume 8,000 equivalent discounted operating hours; each unserved kg has a 0.10 USD opportunity cost. Apply that time factor to convert the loss rate into comparable present value. Formulate and solve the two-stage stochastic program to find the optimal capacity $Q_g$.

6. **Real options valuation.** A subsea tieback can be developed in Phase 1 (4 wells, CAPEX = 5,000 MNOK) with an option to add Phase 2 (4 more wells, incremental CAPEX = 4,000 MNOK) after 3 years if reservoir performance confirms the high GIP scenario (probability 0.35). Calculate the option value of the phased approach compared to (a) developing all 8 wells immediately and (b) developing only 4 wells with no expansion option. Use a discount rate of 8% and assume each well produces 2 GSm³/year at a gas price of 1.5 NOK/Sm³.

---

## References

Birge, J. R. and Louveaux, F. (2011). *Introduction to Stochastic Programming*, 2nd edn. Springer.

Bratvold, R. B. and Begg, S. H. (2010). *Making Good Decisions*. Society of Petroleum Engineers.

Dixit, A. K. and Pindyck, R. S. (1994). *Investment under Uncertainty*. Princeton University Press.

Jonsbraten, T. W., Wets, R. J.-B., and Woodruff, D. L. (1998). A class of stochastic programs with decision dependent randomization. *Annals of Operations Research*, 82, 83–106.

Kall, P. and Mayer, J. (2005). *Stochastic Linear Programming: Models, Theory, and Computation*. Springer.

Kullawan, K., Bratvold, R. B., and Bickel, J. E. (2014). A decision analytic approach to gas field development under geological uncertainty. *Journal of Petroleum Science and Engineering*, 120, 31–46.

Lund, M. W. (2000). Valuing flexibility in offshore petroleum projects. *Annals of Operations Research*, 99(1), 325–349.

Rockafellar, R. T. and Uryasev, S. (2000). Optimization of conditional value-at-risk. *Journal of Risk*, 2(3), 21–42.

Sahinidis, N. V. (2004). Optimization under uncertainty: state-of-the-art and opportunities. *Computers and Chemical Engineering*, 28(6–7), 971–983.

Smith, J. E. and McCardle, K. F. (1999). Options in the real world: lessons learned in evaluating oil and gas investments. *Operations Research*, 47(1), 1–15.

Trigeorgis, L. (1996). *Real Options: Managerial Flexibility and Strategy in Resource Allocation*. MIT Press.

Van Essen, G. M., Van den Hof, P. M. J., and Jansen, J. D. (2011). Hierarchical long-term and short-term production optimization. *SPE Journal*, 16(1), 191–199.


