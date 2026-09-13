# Advanced Topics and Emerging Technologies

<!-- Chapter metadata -->
<!-- Notebooks: ch22_pareto_optimization.ipynb, ch22_sqp_example.ipynb, ch22_data_reconciliation.ipynb, ch22_network_optimization.ipynb -->
<!-- Estimated pages: 30 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Formulate and solve multi-objective optimization problems using Pareto front methods, including weighted-sum and epsilon-constraint approaches
2. Apply Sequential Quadratic Programming (SQP) to constrained nonlinear process optimization problems
3. Interface NeqSim process models with external optimizers (SciPy, NLopt) through the `ProcessSimulationEvaluator`
4. Implement data reconciliation and model calibration using `SteadyStateDetector`, `DataReconciliationEngine`, and `BatchParameterEstimator`
5. Design and execute batch parameter sweep studies using the `BatchStudy` class
6. Formulate and solve pipeline network optimization problems with choke allocation and multi-well routing

---

## 32.1 Introduction

The preceding chapters have presented the core techniques of production optimization — process simulation, steady-state optimization, dynamic simulation, digital twins, and debottlenecking. This chapter explores advanced topics that push beyond routine optimization into frontier applications: multi-objective trade-off analysis, constrained nonlinear programming, integration with external optimization toolboxes, data-driven model calibration, large-scale parameter sweeps, and network-level optimization.

These topics share a common theme: they require going beyond single-objective, unconstrained, single-model optimization to handle the *real complexity* of production systems — multiple competing objectives, hard physical constraints, noisy measured data, large parameter spaces, and interconnected networks of wells, pipelines, and processing equipment.

Each section introduces the mathematical formulation, presents the NeqSim API, and demonstrates the technique with both Java and Python code examples.

---

## 32.2 Multi-Objective Optimization

Real production optimization rarely involves a single objective. Operators must simultaneously balance production rate, energy efficiency, product quality, equipment life, emissions, and cost. These objectives often conflict: maximizing production rate increases energy consumption; minimizing emissions may reduce throughput; minimizing cost may sacrifice product quality.

**Multi-objective optimization** provides a rigorous framework for exploring these trade-offs and presenting decision-makers with the set of *non-dominated* solutions — the Pareto front.

### 32.2.1 Pareto Dominance and the Pareto Front

Given two objective functions $f_1(x)$ and $f_2(x)$ to be minimized, a solution $x^a$ **dominates** another solution $x^b$ if:

$$
f_1(x^a) \leq f_1(x^b) \quad \text{and} \quad f_2(x^a) \leq f_2(x^b)
$$

with at least one strict inequality. The set of all non-dominated solutions forms the **Pareto front** — a curve (or surface, for three or more objectives) representing the best achievable trade-offs.

$$
\mathcal{P} = \{ x \in \mathcal{X} \mid \nexists \, x' \in \mathcal{X} : x' \text{ dominates } x \}
$$

No point on the Pareto front can improve one objective without worsening at least one other. The choice of operating point along the front is a *management decision*, not a mathematical one.

### 32.2.2 The optimizePareto() API in NeqSim

NeqSim's `ProductionOptimizer` provides the `optimizePareto()` method for generating Pareto fronts. The method takes a process system, a configuration, and a list of objective definitions:

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
ProcessSystem process = new ProcessSystem();
process.add(feed);
process.add(separator);
process.add(compressor);
process.run();
ProductionOptimizer optimizer = new ProductionOptimizer();
List<OptimizationObjective> objectives = Arrays.asList(
    new OptimizationObjective("production", proc -> ((StreamInterface) proc.getUnit("Feed")).getFlowRate("kg/hr"), 1.0, ObjectiveType.MAXIMIZE),
    new OptimizationObjective("power", proc -> ((Compressor) proc.getUnit("Compressor")).getPower("kW"), 1.0, ObjectiveType.MINIMIZE));
OptimizationConfig config = new OptimizationConfig(50000.0,200000.0).rateUnit("kg/hr").maxIterations(20).paretoGridSize(5);
ParetoResult pareto = optimizer.optimizePareto(process, feed, config, objectives, Collections.emptyList());
List<ParetoPoint> front = pareto.getParetoFront();
logger.info("Non-dominated sampled points: {}", front.size());
// Selection from this set requires an explicit operational/economic preference.
```

The `ParetoResult` contains:

| Method | Description |
|--------|-------------|
| `getParetoFront()` | List of non-dominated points |
| `getKneePoint()` | The point with maximum curvature (balanced trade-off) |
| `getAllPoints()` | All evaluated points (including dominated) |
| `getObjectiveNames()` | Names of the objectives |

### 32.2.3 Knee Point Detection

The **knee point** is the Pareto solution where the marginal rate of trade-off changes most sharply — it represents the "best compromise" between objectives. Mathematically, it is the point of maximum curvature on the Pareto front:

$$
\kappa(x) = \frac{|f_1''(x) f_2'(x) - f_1'(x) f_2''(x)|}{(f_1'^2(x) + f_2'^2(x))^{3/2}}
$$

The knee point is significant because small improvements in either objective beyond this point require disproportionately large sacrifices in the other objective.

NeqSim computes the knee point automatically using a normalized distance method: for each Pareto point, compute its perpendicular distance to the line connecting the two extreme points. The knee is the point with the maximum distance.

### 32.2.4 Standard Objective Definitions

Common objectives in production optimization:

| Objective | Direction | Typical Evaluator |
|-----------|-----------|-------------------|
| Oil production rate | Maximize | `feed.getFlowRate("bbl/day")` |
| Gas production rate | Maximize | `gasExport.getFlowRate("MSm3/day")` |
| Total production | Maximize | Sum of oil + gas equivalent |
| Compressor power | Minimize | `compressor.getPower("kW")` |
| Specific energy | Minimize | Power / production rate |
| Gas dew point | Minimize | `gasExport.getDewPointTemperature("C")` |
| CO₂ emissions | Minimize | Fuel gas × emission factor |
| OPEX | Minimize | Energy cost + chemical cost |
| Revenue | Maximize | Product rates × prices |

### 32.2.5 Weighted-Sum Method

The simplest approach to multi-objective optimization is the **weighted-sum method**, which converts the multi-objective problem to a single objective:

$$
\min_x \quad \sum_{k=1}^{K} w_k \hat{f}_k(x)
$$

where $\hat{f}_k$ is the normalized objective and $w_k$ are weights satisfying $\sum w_k = 1$. By varying the weights, different points on the Pareto front are obtained.

The weighted-sum method has the advantage of simplicity and can use any single-objective optimizer. However, it has a well-known limitation: it cannot find points on non-convex portions of the Pareto front.

### 32.2.6 Epsilon-Constraint Method

The **epsilon-constraint method** overcomes the limitation of the weighted-sum method by optimizing one objective while constraining the others:

$$
\min_x \quad f_1(x)
$$

$$
\text{subject to:} \quad f_k(x) \leq \epsilon_k, \quad k = 2, \ldots, K
$$

By systematically varying the $\epsilon_k$ bounds, the entire Pareto front — including non-convex regions — is traced out.

### 32.2.7 Python Example — Pareto Front Visualization

```python
from pathlib import Path
Path("figures").mkdir(parents=True, exist_ok=True)
import jpype
import numpy as np
import matplotlib.pyplot as plt
jneqsim = jpype.JPackage("neqsim")
fluid = jneqsim.thermo.system.SystemSrkEos(313.15, 50.0)
fluid.addComponent("methane", 0.90)
fluid.addComponent("ethane", 0.10)
fluid.setMixingRule("classic")
feed = jneqsim.process.equipment.stream.Stream("Feed", fluid)
feed.setFlowRate(100000.0, "kg/hr")
compressor = jneqsim.process.equipment.compressor.Compressor("Compressor", feed)
compressor.setOutletPressure(150.0, "bara")
compressor.setPolytropicEfficiency(0.78)
compressor.setUsePolytropicCalc(True)
process = jneqsim.process.processmodel.ProcessSystem()
process.add(feed)
process.add(compressor)
process.run()
ProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer
OptimizationConfig = ProductionOptimizer.OptimizationConfig
Objective = ProductionOptimizer.OptimizationObjective
Direction = ProductionOptimizer.ObjectiveType
optimizer = ProductionOptimizer()
objectives = jpype.java.util.ArrayList([
    Objective("production", lambda proc: proc.getUnit("Feed").getFlowRate("kg/hr"),
              1.0, Direction.MAXIMIZE),
    Objective("power", lambda proc: proc.getUnit("Compressor").getPower("kW"),
              1.0, Direction.MINIMIZE)])
config = (OptimizationConfig(50000.0, 200000.0).rateUnit("kg/hr")
          .maxIterations(20).paretoGridSize(7))
pareto = optimizer.optimizePareto(process, feed, config, objectives, None)
front = pareto.getParetoFront()
production = [float(p.getObjectiveValues()["production"]) for p in front]
power = [float(p.getObjectiveValues()["power"]) for p in front]
plt.figure(figsize=(7, 4))
plt.scatter(production, power)
plt.xlabel("Feed flow (kg/hr)")
plt.ylabel("Compressor power (kW)")
plt.title("Sampled non-dominated process states")
plt.grid(True, alpha=0.3)
plt.savefig("figures/pareto_front.png", dpi=150, bbox_inches="tight")
print("Non-dominated points:", len(front))
```

This produces a scatter plot of the Pareto front, clearly showing the trade-off between production rate and energy consumption. The knee point identifies the operating condition that balances both objectives.

---

## 32.3 Sequential Quadratic Programming (SQP)

For constrained nonlinear optimization problems with continuous variables and smooth objective/constraint functions, **Sequential Quadratic Programming (SQP)** is one of the most efficient and widely-used algorithms. NeqSim provides a dedicated `SQPoptimizer` class for this purpose.

### 32.3.1 The SQP Algorithm

SQP solves the general nonlinear program:

$$
\min_x \quad f(x)
$$

$$
\text{s.t.} \quad g_i(x) = 0, \quad i = 1, \ldots, m_e
$$

$$
h_j(x) \geq 0, \quad j = 1, \ldots, m_i
$$

$$
x^L \leq x \leq x^U
$$

At each iteration $k$, SQP linearizes the constraints and forms a quadratic approximation of the Lagrangian:

$$
\mathcal{L}(x, \lambda, \mu) = f(x) - \lambda^T g(x) - \mu^T h(x)
$$

The resulting **QP sub-problem** is:

$$
\min_d \quad \nabla f(x_k)^T d + \frac{1}{2} d^T B_k d
$$

$$
\text{s.t.} \quad \nabla g_i(x_k)^T d + g_i(x_k) = 0
$$

$$
\nabla h_j(x_k)^T d + h_j(x_k) \geq 0
$$

$$
x^L - x_k \leq d \leq x^U - x_k
$$

where $d = x_{k+1} - x_k$ is the search direction and $B_k$ is a BFGS approximation of the Hessian of the Lagrangian.

The solution of this QP gives the search direction. An **Armijo backtracking line search** on the $L_1$ exact penalty merit function:

$$
\phi(x; \sigma) = f(x) + \sigma \sum_i |g_i(x)| + \sigma \sum_j \max(0, -h_j(x))
$$

ensures global convergence. The penalty parameter $\sigma$ is adjusted dynamically.

### 32.3.2 Convergence — KKT Conditions

SQP converges when the **Karush–Kuhn–Tucker (KKT) conditions** are satisfied to within tolerance:

$$
\nabla f(x^*) - \sum_i \lambda_i^* \nabla g_i(x^*) - \sum_j \mu_j^* \nabla h_j(x^*) = 0
$$

$$
g_i(x^*) = 0, \quad h_j(x^*) \geq 0, \quad \mu_j^* \geq 0, \quad \mu_j^* h_j(x^*) = 0
$$

The KKT conditions are necessary for local optimality. Under regularity conditions (constraint qualification), they are also sufficient.

### 32.3.3 The SQPoptimizer Class

NeqSim's `SQPoptimizer` implements the SQP algorithm with the following features:

- **BFGS quasi-Newton Hessian approximation** with damped updates for positive definiteness
- **Active-set QP solver** for bound and linear inequality constraints
- **L1 exact penalty merit function** for global convergence
- **Finite-difference gradient estimation** (user can provide analytical gradients)
- **Variable bounds** enforced via projection

```java
import neqsim.process.util.optimizer.SQPoptimizer;

// Create optimizer with 2 variables
SQPoptimizer sqp = new SQPoptimizer(2);

// Set objective function: f(x) = (x[0] - 3)^2 + (x[1] - 2)^2
sqp.setObjectiveFunction(new SQPoptimizer.ObjectiveFunc() {
    public double evaluate(double[] x) {
        return Math.pow(x[0] - 3.0, 2) + Math.pow(x[1] - 2.0, 2);
    }
});

// Add inequality constraint: x[0] + x[1] >= 4
sqp.addInequalityConstraint(new SQPoptimizer.ConstraintFunc() {
    public double evaluate(double[] x) {
        return x[0] + x[1] - 4.0;  // >= 0 means x[0]+x[1] >= 4
    }
});

// Add equality constraint: x[0] - x[1] = 1
sqp.addEqualityConstraint(new SQPoptimizer.ConstraintFunc() {
    public double evaluate(double[] x) {
        return x[0] - x[1] - 1.0;  // = 0
    }
});

// Set bounds
sqp.setVariableBounds(
    new double[]{0.0, 0.0},     // lower bounds
    new double[]{10.0, 10.0}    // upper bounds
);

// Set initial point
sqp.setInitialPoint(new double[]{5.0, 5.0});

// Solve
SQPoptimizer.OptimizationResult result = sqp.solve();

logger.info("Optimal x: " + Arrays.toString(result.getOptimalPoint()));
logger.info("Optimal f: " + result.getOptimalValue());
logger.info("Converged: " + result.isConverged());
logger.info("Iterations: " + result.getIterations());
```

### 32.3.4 When to Use SQP vs ProductionOptimizer

| Criterion | SQP | ProductionOptimizer |
|-----------|-----|---------------------|
| Problem type | Smooth, continuous NLP | General (smooth or noisy) |
| Variables | Continuous only | Continuous + discrete |
| Constraints | Equality + inequality + bounds | Capacity constraints + custom |
| Convergence | Fast (superlinear near optimum) | Moderate (derivative-free) |
| Global optimality | Local only | May find global via multi-start |
| Gradients | Required (finite-diff OK) | Not required |
| Problem size | 10–100 variables | 1–20 variables typical |
| Typical use | Detailed NLP with many constraints | Production set point optimization |

**Use SQP when**: the problem is well-posed, smooth, has many constraints, and you need fast convergence to a local optimum. Typical applications include optimal compressor staging, heat integration, and column design.

**Use ProductionOptimizer when**: the problem has noisy simulation evaluations, discrete decisions (on/off equipment), or you need capacity constraint integration. Typical applications include well rate allocation, separator pressure optimization, and gas lift allocation.

### 32.3.5 Python SQP Example

```python
SQPoptimizer = jneqsim.process.util.optimizer.SQPoptimizer
# Dimensionless decisions: flow / 100000 kg/hr and suction pressure / 50 bara.
def solved_state(x):
    feed.setFlowRate(float(x[0]) * 100000.0, "kg/hr")
    feed.setPressure(float(x[1]) * 50.0, "bara")
    compressor.setOutletPressure(150.0, "bara")
    process.run()
    return float(compressor.getPower("kW"))

def production_objective(x):
    solved_state(x)
    return -float(x[0])

def power_margin(x):
    return (5000.0 - solved_state(x)) / 5000.0

sqp = SQPoptimizer(2)
sqp.setObjectiveFunction(production_objective)
sqp.addInequalityConstraint(power_margin)
sqp.setVariableBounds([0.5, 0.8], [2.0, 1.6])
sqp.setInitialPoint([0.5, 1.0])
sqp.setMaxIterations(60)
result = sqp.solve()
selected = result.getOptimalPoint()
final_power = solved_state(selected)
print("SQP converged:", result.isConverged(), "KKT residual:", result.getKktError())
print("Final flow (kg/hr):", feed.getFlowRate("kg/hr"), "power (kW):", final_power)
if not result.isConverged() or not np.isfinite(final_power) or final_power > 5001.0:
    print("Rejected SQP candidate; retaining a separately solved feasible baseline")
    selected = [0.5, 1.0]
    final_power = solved_state(selected)
assert np.isfinite(final_power) and final_power <= 5001.0
print("Retained flow kg/hr:", feed.getFlowRate("kg/hr"), "power kW:", final_power)
# Check convergence and the physical residual before accepting a deployment decision.
```

---

## 32.4 External Optimizer Integration

While NeqSim provides built-in optimization capabilities, many practitioners prefer using established optimization toolboxes — SciPy (Python), NLopt, MATLAB, or commercial solvers. The `ProcessSimulationEvaluator` class provides a standardized interface for connecting NeqSim process models to external optimizers.

### 32.4.1 The ProcessSimulationEvaluator Interface

The `ProcessSimulationEvaluator` wraps a NeqSim `ProcessSystem` as a **black-box function** that maps decision variables to objective and constraint values:

```java
ProcessSimulationEvaluator evaluator = new ProcessSimulationEvaluator(process);
evaluator.addParameterWithSetter("flow", (proc, value) -> ((StreamInterface) proc.getUnit("Feed")).setFlowRate(value,"kg/hr"), 50000.0,200000.0,"kg/hr");
evaluator.addParameterWithSetter("suction", (proc, value) -> ((StreamInterface) proc.getUnit("Feed")).setPressure(value,"bara"), 40.0,80.0,"bara");
evaluator.addObjective("production", proc -> ((StreamInterface) proc.getUnit("Feed")).getFlowRate("kg/hr"), ProcessSimulationEvaluator.ObjectiveDefinition.Direction.MAXIMIZE);
evaluator.addConstraintUpperBound("power", proc -> ((Compressor) proc.getUnit("Compressor")).getPower("kW"),5000.0);
double[] x = {100000.0,60.0};
ProcessSimulationEvaluator.EvaluationResult result = evaluator.evaluate(x);
logger.info("Objective {}, feasible {}, converged {}", result.getObjective(),result.isFeasible(),result.isSimulationConverged());
```

### 32.4.2 SciPy Integration

The `ProcessSimulationEvaluator` integrates naturally with SciPy's optimization routines:

```python
from scipy.optimize import minimize, differential_evolution
# The address-based automation facade applies inputs and solves before extraction.
import json
auto = process.getAutomation()
def evaluate_state(x):
    inputs = jpype.java.util.LinkedHashMap()
    inputs.put("Feed.flowRate", float(x[0]) * 100000.0)
    inputs.put("Feed.pressure", float(x[1]) * 50.0)
    requested = jpype.java.util.ArrayList(["Compressor.power"])
    report = json.loads(str(auto.evaluate(inputs, None, requested, "kW", 30, 0.005)))
    power = float(compressor.getPower("kW"))
    if not np.isfinite(power):
        raise RuntimeError("Non-finite compressor power")
    return power

def penalty_objective(x):
    return -float(x[0]) + 100.0 * max(0.0, (evaluate_state(x) - 5000.0) / 5000.0)

bounds = [(0.5, 2.0), (0.8, 1.6)]
res_lbfgsb = minimize(penalty_objective, [1.0, 1.0], method="L-BFGS-B", bounds=bounds)
res_de = differential_evolution(penalty_objective, bounds, seed=42, maxiter=20, popsize=5)
res_slsqp = minimize(lambda x: -float(x[0]), [1.0, 1.0], method="SLSQP", bounds=bounds,
    constraints={"type": "ineq", "fun": lambda x: (5000.0-evaluate_state(x))/5000.0})
for name, answer in [("L-BFGS-B", res_lbfgsb), ("DE", res_de), ("SLSQP", res_slsqp)]:
    power = evaluate_state(answer.x)  # full-model replay at each reported answer
    print(name, "success=", answer.success, "flow kg/hr=", answer.x[0]*100000.0,
          "power kW=", power, "power-feasible=", power <= 5001.0)
```

### 32.4.3 NLopt Integration

For advanced algorithms not available in SciPy, NLopt provides a wider selection:

**Execution scope:** optional NLopt package is required.

```python pattern: optional NLopt package is required
try:
    import nlopt

    def nlopt_objective(x, grad):
        return penalty_objective(x)

    opt = nlopt.opt(nlopt.LN_BOBYQA, 2)  # BOBYQA: derivative-free
    opt.set_lower_bounds([0.5, 0.8])
    opt.set_upper_bounds([2.0, 1.6])
    opt.set_min_objective(nlopt_objective)
    opt.set_maxeval(200)

    x_opt = opt.optimize([1.0, 1.0])
    print(f"BOBYQA: x = {x_opt}, f = {-opt.last_optimum_value():.1f}")

except ImportError:
    print("NLopt not installed - skipping")
```

### 32.4.4 Gradient Estimation via Finite Differences

When external optimizers require gradient information, the `ProcessSimulationEvaluator` can estimate gradients via central finite differences:

$$
\frac{\partial f}{\partial x_i} \approx \frac{f(x + h e_i) - f(x - h e_i)}{2h}
$$

where $h$ is the step size (typically $10^{-4}$ to $10^{-2}$ times the variable range) and $e_i$ is the $i$-th unit vector.

```java
evaluator.setFiniteDifferenceStep(0.001);
evaluator.setUseRelativeStep(true);
double[] gradient = evaluator.estimateGradient(x);
logger.info("Forward finite-difference objective gradient: {}", Arrays.toString(gradient));
```

The step size is critical: too small and numerical noise dominates; too large and the linear approximation is poor. A good rule of thumb is $h \approx \sqrt{\epsilon_{\text{machine}}} \cdot |x_i|$ for forward differences and $h \approx \epsilon_{\text{machine}}^{1/3} \cdot |x_i|$ for central differences.

### 32.4.5 Comparison of External Optimizer Approaches

The following table summarizes when to use each external optimizer:

| Optimizer | Algorithm | Type | Best For |
|-----------|-----------|------|----------|
| SciPy L-BFGS-B | Quasi-Newton | Local, gradient-based | Smooth problems, 10-100 variables |
| SciPy SLSQP | SQP | Local, gradient-based | Equality + inequality constraints |
| SciPy differential_evolution | Evolutionary | Global, derivative-free | Non-convex, discrete-ish problems |
| SciPy dual_annealing | Simulated annealing | Global, derivative-free | Highly multimodal landscapes |
| NLopt BOBYQA | Model-based | Local, derivative-free | Noisy simulations, bound constraints |
| NLopt COBYLA | Model-based | Local, derivative-free | Noisy, with nonlinear constraints |
| NLopt ISRES | Evolutionary | Global, derivative-free | Small to medium stochastic NLPs |
| Pyomo/IPOPT | Interior point | Local, gradient-based | Large-scale NLP via algebraic modeling |

**General guidelines:**

- For problems with <5 variables and noisy simulations: use **BOBYQA** or **differential_evolution**
- For smooth problems with 5-50 variables and constraints: use **SLSQP** or **L-BFGS-B**
- For highly multimodal problems: use **differential_evolution** or **dual_annealing** with multi-start
- When gradients are available (e.g., via adjoint methods): use **L-BFGS-B** or **IPOPT**

### 32.4.6 Surrogate-Assisted Optimization

For computationally expensive process simulations, **surrogate models** (also called metamodels or response surfaces) can accelerate optimization by replacing the expensive simulation with a fast approximation:

1. **Design of Experiments**: Sample the design space using Latin Hypercube Sampling (LHS)
2. **Build surrogate**: Fit a Gaussian Process (Kriging), Radial Basis Function (RBF), or polynomial response surface
3. **Optimize surrogate**: Find the optimum of the fast surrogate
4. **Validate**: Run the original simulation at the surrogate optimum
5. **Infill**: Add the new point and update the surrogate (adaptive sampling)

This approach is particularly useful when each NeqSim simulation takes minutes (e.g., large platform models with recycles, dynamic simulations, or multi-phase pipeline calculations).

```python
from scipy.interpolate import RBFInterpolator
from scipy.stats.qmc import LatinHypercube
sampler = LatinHypercube(d=2, seed=42)
limits = np.array(bounds)
X = sampler.random(n=20) * (limits[:, 1]-limits[:, 0]) + limits[:, 0]
Y = np.array([evaluate_state(x) for x in X])
# Thin-plate spline avoids an arbitrary multiquadric shape parameter.
rbf = RBFInterpolator(X, Y, kernel="thin_plate_spline")
res = minimize(lambda x: -float(x[0]), [1.0, 1.0], method="SLSQP", bounds=bounds,
    constraints={"type": "ineq", "fun": lambda x: (5000.0-float(rbf(np.asarray(x)[None,:])[0]))/5000.0})
predicted = float(rbf(res.x[None,:])[0])
actual = evaluate_state(res.x)
print("Surrogate candidate flow kg/hr:", res.x[0]*100000.0)
print("Predicted/actual power kW:", predicted, actual)
print("Accepted power constraint:", actual <= 5001.0)
# A failed full-model check triggers more samples and another search.
```

### 32.4.7 JSON Problem Export

For interoperability with optimization frameworks written in other languages, the `ProcessSimulationEvaluator` can export the problem definition as JSON:

```java
Map<String,Object> definition = evaluator.getProblemDefinition();
String json = new com.google.gson.GsonBuilder().setPrettyPrinting().create().toJson(definition);
logger.info("Problem definition: {}",json);
```

This enables building optimization services where the NeqSim model runs as a server and the optimizer runs as a separate process, communicating via JSON messages.

---

## 32.5 Data Reconciliation and Model Calibration

A process model is only as good as its calibration. When a model is built from design data, it represents the *intended* process. To use the model for optimization, it must be calibrated to represent the *actual* process — accounting for fouling, degradation, measurement biases, and real fluid properties.

### 32.5.1 Steady-State Detection

Before performing data reconciliation, it is essential to verify that the plant is at steady state. Reconciling transient data produces meaningless results. NeqSim provides the `SteadyStateDetector` class based on the R-statistic method:

The R-statistic for a time series $\{y_1, y_2, \ldots, y_N\}$ is:

$$
R = \frac{1}{N-1} \sum_{k=1}^{N-1} \frac{(y_k - \bar{y})(y_{k+1} - \bar{y})}{s_y^2}
$$

where $\bar{y}$ is the mean and $s_y^2$ is the variance. For a truly random (steady-state) process, $R \approx 0$. For a process with trends (transient), $R \rightarrow 1$.

```java
import neqsim.process.util.reconciliation.*;
SteadyStateDetector detector = new SteadyStateDetector();
SteadyStateVariable pressure = detector.addVariable("Pressure").setUnit("bara");
for (int index=0; index<60; index++) { pressure.addValue(60.0); }
SteadyStateResult steady = detector.evaluate();
logger.info("Synthetic constant signal steady: {}; R-statistic {}", steady.isAtSteadyState(),pressure.getRStatistic());
// Site signals require timestamps, quality flags, a declared window and tolerances.
```

### 32.5.2 Data Reconciliation Engine

Once steady state is confirmed, the **Data Reconciliation Engine** adjusts measured values to satisfy mass and energy balances. The formulation is a **weighted least squares** problem:

$$
\min_{\hat{y}} \quad \sum_{i=1}^{n} \frac{(y_i - \hat{y}_i)^2}{\sigma_i^2}
$$

$$
\text{subject to:} \quad A \hat{y} = 0 \quad \text{(conservation balances)}
$$

where $y_i$ are the raw measurements, $\hat{y}_i$ are the reconciled values, and $\sigma_i^2$ are the measurement variances (from instrument specifications).

```java
DataReconciliationEngine engine = new DataReconciliationEngine();
// Synthetic readings and one-standard-deviation uncertainties, all kg/hr.
engine.addVariable(new ReconciliationVariable("Feed",100000.0,2000.0));
engine.addVariable(new ReconciliationVariable("Gas",70000.0,1500.0));
engine.addVariable(new ReconciliationVariable("Oil",28000.0,1000.0));
engine.addVariable(new ReconciliationVariable("Water",5000.0,500.0));
engine.addConstraint(new double[]{1.0,-1.0,-1.0,-1.0},"Mass balance");
ReconciliationResult reconciled = engine.reconcile();
if (!reconciled.isConverged()) { throw new IllegalStateException(reconciled.getErrorMessage()); }
logger.info("Reconciled feed {} kg/hr; residuals {}", engine.getVariable("Feed").getReconciledValue(),Arrays.toString(reconciled.getConstraintResidualsAfter()));
```

### 32.5.3 Gross Error Detection

The reconciliation engine also performs **gross error detection** using the measurement test based on the normalized residuals:

$$
z_i = \frac{y_i - \hat{y}_i}{\sigma_i \sqrt{1 - r_{ii}}}
$$

where $r_{ii}$ is the diagonal element of the residual projection matrix. If $|z_i| > z_{\alpha/2}$ (typically 1.96 for 95% confidence), the measurement is flagged as having a gross error — indicating a sensor fault, calibration drift, or data entry error.

```java
logger.info("Global test passed: {}",reconciled.isGlobalTestPassed());
for (ReconciliationVariable suspect : reconciled.getGrossErrors()) {
    logger.warn("Suspect {} normalized residual {}",suspect.getName(),suspect.getNormalizedResidual());
}
```

### 32.5.4 Batch Parameter Estimation

The `BatchParameterEstimator` class tunes model parameters to match multiple data points simultaneously using **Levenberg-Marquardt** optimization. This is the primary tool for model calibration:

$$
\min_\theta \quad \sum_{k=1}^{N_{\text{data}}} \sum_{j=1}^{N_{\text{meas}}} w_j \left( y_{j,k}^{\text{meas}} - y_{j,k}^{\text{model}}(\theta) \right)^2
$$

where $\theta$ is the vector of tunable parameters, $y_{j,k}^{\text{meas}}$ are measured values, and $y_{j,k}^{\text{model}}(\theta)$ are model predictions.

```java
import neqsim.process.calibration.BatchParameterEstimator;
import neqsim.process.calibration.BatchResult;
// Recovery experiment using synthetic observations generated at known efficiency.
compressor.setUsePolytropicCalc(true);
compressor.setPolytropicEfficiency(0.78);
feed.setFlowRate(100000.0,"kg/hr");
feed.setPressure(60.0,"bara");
BatchParameterEstimator estimator = new BatchParameterEstimator(process);
estimator.addTunableParameter("Compressor.polytropicEfficiency","-",0.60,0.90,0.72);
estimator.addMeasuredVariable("Compressor.outletStream.temperature","C",1.0);
for (double discharge : new double[]{130.0,150.0,170.0}) {
    compressor.setOutletPressure(discharge,"bara");
    process.run();
    Map<String,Double> conditions = new HashMap<String,Double>();
    conditions.put("Compressor.outletPressure",discharge);
    Map<String,Double> observations = new HashMap<String,Double>();
    observations.put("Compressor.outletStream.temperature",compressor.getOutletStream().getTemperature("C"));
    estimator.addDataPoint(conditions,observations);
}
compressor.setPolytropicEfficiency(0.72);
estimator.setMaxIterations(40);
BatchResult fit = estimator.solve();
logger.info("Converged {}, estimated efficiency {}, RMSE {}",fit.isConverged(),fit.getEstimate(0),fit.getRMSE());
if (!Double.isFinite(fit.getEstimate(0))) { throw new IllegalStateException("Non-finite fitted efficiency"); }
// Synthetic recovery tests exercise the estimator; independent plant data are still required.
// Separator diameter is not identified by equilibrium outlet temperature in this model.
```

The Levenberg-Marquardt algorithm solves the normal equations:

$$
(J^T W J + \lambda I) \Delta\theta = J^T W (y^{\text{meas}} - y^{\text{model}})
$$

where $J$ is the Jacobian of model predictions with respect to parameters, $W$ is the weight matrix, and $\lambda$ is the damping parameter that transitions between steepest descent ($\lambda$ large) and Gauss-Newton ($\lambda$ small).

### 32.5.5 Model Calibration Workflow

A complete model calibration workflow:

**Execution scope:** requires measured time series, reconciler constraints and calibration data.

```python pattern: requires measured time series, reconciler constraints and calibration data
import jpype
jneqsim = jpype.JPackage("neqsim")
import numpy as np

SteadyStateDetector = jneqsim.process.util.reconciliation.SteadyStateDetector
DataReconciliationEngine = jneqsim.process.util.reconciliation.DataReconciliationEngine
BatchParameterEstimator = jneqsim.process.calibration.BatchParameterEstimator

# Step 1: Check steady state
detector = SteadyStateDetector()
# ... add measurement time series ...
if not detector.evaluate().isAtSteadyState():
    print("WARNING: Plant not at steady state")

# Step 2: Reconcile measurements
engine = DataReconciliationEngine()
# ... add measurements and constraints ...
engine.reconcile()

# Step 3: Tune model parameters
estimator = BatchParameterEstimator(process)
estimator.addTunableParameter(
    "Compressor.polytropicEfficiency", "-", 0.6, 0.9, 0.75)
estimator.addMeasuredVariable(
    "Compressor.outletStream.temperature", "C", 1.0)

# Use reconciled values as data points
measurements = jneqsim.java.util.HashMap()
measurements.put("Compressor.outletStream.temperature",
    jneqsim.java.lang.Double(float(engine.getVariable(
        "Compressor Outlet Temperature").getReconciledValue())))
estimator.addDataPoint(measurements)

fit = estimator.solve()
print(f"Calibrated efficiency: "
      f"{fit.getEstimate('Compressor.polytropicEfficiency'):.3f}")
```

---

## 32.6 Batch Studies and Parallel Computing

Production optimization often requires evaluating the process model at hundreds or thousands of different operating conditions — for sensitivity analysis, screening studies, design space exploration, or Monte Carlo simulation. The `BatchStudy` class provides efficient infrastructure for these parameter sweep studies.

### 32.6.1 The BatchStudy Class

`BatchStudy` manages the execution of multiple simulation cases with different parameter values:

```java
BatchStudy study = BatchStudy.builder(process)
    .vary("Feed.flowRate",50000.0,200000.0,4)
    .vary("Compressor.outletPressure",120.0,200.0,3)
    .addObjective("flow",BatchStudy.Objective.MAXIMIZE, proc -> ((StreamInterface) proc.getUnit("Feed")).getFlowRate("kg/hr"))
    .addObjective("power",BatchStudy.Objective.MINIMIZE, proc -> ((Compressor) proc.getUnit("Compressor")).getPower("kW"))
    .parallelism(1).name("Compression envelope").build();
BatchStudy.BatchStudyResult batch = study.run();
if (batch.getFailureCount()!=0) { throw new IllegalStateException(batch.getSummary()); }
logger.info("Cases run {}",batch.getTotalCases());
```

### 32.6.2 Study Types

The `BatchStudy` class supports several study types:

| Study Type | Method | Cases | Description |
|-----------|--------|-------|-------------|
| Full factorial | `runFullFactorial()` | $\prod n_i$ | All combinations of parameter values |
| One-at-a-time | `runOneAtATime()` | $\sum (n_i - 1) + 1$ | Vary each parameter individually |
| Latin Hypercube | `runLatinHypercube(N)` | $N$ | Space-filling design |
| Random | `runRandom(N)` | $N$ | Random sampling within bounds |

For two parameters with 7 and 5 levels:
- Full factorial: $7 \times 5 = 35$ cases
- One-at-a-time: $(7-1) + (5-1) + 1 = 11$ cases
- Latin Hypercube: user-specified $N$ (e.g., 20)

### 32.6.3 Multi-Objective Ranking

When a batch study evaluates multiple objectives, the results can be ranked using Pareto dominance:

```java
List<BatchStudy.CaseResult> nonDominated = batch.getParetoFront("flow","power");
for (BatchStudy.CaseResult candidate : nonDominated) {
    logger.info("Parameters {} objectives {}",candidate.parameters.values,candidate.objectiveValues);
}
// Non-dominated candidates have no unique preference rank without a decision rule.
```

### 32.6.4 Result Aggregation

For large batch studies, statistical aggregation summarizes results:

```java
double[] powers = batch.getSuccessfulResults().stream().mapToDouble(candidate -> candidate.objectiveValues.get("power")).toArray();
java.util.DoubleSummaryStatistics statistics = Arrays.stream(powers).summaryStatistics();
logger.info("Design-grid power minimum {}, mean {}, maximum {} kW",statistics.getMin(),statistics.getAverage(),statistics.getMax());
// These equally weighted design points are not a probability distribution or a P10/P90 reserve assessment.
```

### 32.6.5 Python Batch Study Example

```python
BatchStudy = jneqsim.process.util.optimizer.BatchStudy
study = (BatchStudy.builder(process)
    .vary("Feed.flowRate", 50000.0, 200000.0, 4)
    .vary("Compressor.outletPressure", 120.0, 200.0, 3)
    .addObjective("power_kW", BatchStudy.Objective.MINIMIZE,
                  lambda case: float(case.getUnit("Compressor").getPower("kW")))
    .parallelism(1).name("Compression envelope").build())
results = study.run()
assert results.getFailureCount() == 0
print(results.getSummary())
cases = results.getSuccessfulResults()
flows = [float(case.parameters.values["Feed.flowRate"]) for case in cases]
pressures = [float(case.parameters.values["Compressor.outletPressure"]) for case in cases]
powers = [float(case.objectiveValues["power_kW"]) for case in cases]
plt.figure(figsize=(7, 4))
plt.scatter(flows, pressures, c=powers, s=100)
plt.xlabel("Feed flow (kg/hr)")
plt.ylabel("Compressor discharge pressure (bara)")
plt.colorbar(label="Power (kW)")
plt.title("Full-model compression sweep")
plt.savefig("figures/batch_study_contours.png", dpi=150, bbox_inches="tight")
```

---

## 32.7 Pipeline Network Optimization

Oil and gas production often involves networks of wells connected through manifolds, pipelines, and processing facilities. Optimizing such networks requires specialized algorithms that handle the coupled hydraulic and thermodynamic behavior of the interconnected system.

### 32.7.1 The Network Optimization Problem

A pipeline network optimization problem can be formulated as:

$$
\max_{q, p} \quad \sum_{w \in \mathcal{W}} q_w \quad \text{(total production)}
$$

$$
\text{s.t.} \quad p_w^{\text{res}} - J_w q_w = p_w^{\text{wh}} \quad \forall w \in \mathcal{W} \quad \text{(IPR)}
$$

$$
p_w^{\text{wh}} - \Delta p_{w,m}(q_w) = p_m \quad \forall (w,m) \quad \text{(flowline pressure drop)}
$$

$$
\sum_{w \in \mathcal{W}_m} q_w = Q_m \quad \forall m \in \mathcal{M} \quad \text{(manifold balance)}
$$

$$
p_m - \Delta p_{m,f}(Q_m) = p_f \quad \forall (m,f) \quad \text{(trunkline pressure drop)}
$$

$$
q_w^{\min} \leq q_w \leq q_w^{\max} \quad \forall w \in \mathcal{W} \quad \text{(well rate limits)}
$$

$$
Q_m \leq Q_m^{\max} \quad \forall m \in \mathcal{M} \quad \text{(manifold capacity)}
$$

where $q_w$ is the flow rate from well $w$, $p_w^{\text{res}}$ is the reservoir pressure, $J_w$ is the productivity index, and $\Delta p$ denotes pressure drops through the network.

This is a nonlinear optimization problem because the pressure drops are nonlinear functions of flow rate (Beggs and Brill, Hazen-Williams, or Darcy-Weisbach correlations).

### 32.7.2 Choke Allocation Optimization

A key sub-problem is **choke allocation** — determining the optimal choke setting for each well to maximize total production while respecting facility constraints:

$$
\max_{C_v} \quad \sum_{w=1}^{N_w} q_w(C_{v,w})
$$

$$
\text{s.t.} \quad \sum_{w=1}^{N_w} q_w(C_{v,w}) \leq Q_{\text{facility}}
$$

$$
C_{v,w}^{\min} \leq C_{v,w} \leq C_{v,w}^{\max}
$$

$$
\text{GOR}_w(C_{v,w}) \leq \text{GOR}_{\max} \quad \text{(if gas-constrained)}
$$

$$
\text{WC}_w(C_{v,w}) \leq \text{WC}_{\max} \quad \text{(if water-constrained)}
$$

### 32.7.3 Multi-Objective Network Optimization

Network optimization is often multi-objective, balancing:
- **Total oil production** — to be maximized
- **Total gas production** — may be constrained by gas handling capacity
- **Total water production** — to be minimized (reduce water treatment load)
- **Gas lift consumption** — to be minimized
- **Backpressure** — to be minimized for well deliverability

A weighted-sum formulation combines these:

$$
\max_{q} \quad w_{\text{oil}} \sum q_{\text{oil},w} - w_{\text{gas}} \sum q_{\text{gas},w} - w_{\text{water}} \sum q_{\text{water},w} - w_{\text{GL}} \sum q_{\text{GL},w}
$$

The weights reflect the relative value (or cost) of each fluid. Varying the weights traces out the Pareto front.

### 32.7.4 Sparse Matrix Solvers for Large Networks

For large networks with hundreds of wells and manifolds, the Jacobian matrix of the network equations is **sparse** — each equation involves only a few variables (the flow rates and pressures in its immediate vicinity). Exploiting sparsity is essential for computational efficiency.

The network equations can be written in matrix form:

$$
F(x) = 0
$$

where $x = [q_1, \ldots, q_{N_w}, p_1, \ldots, p_{N_n}]^T$ contains all flow rates and nodal pressures. Newton's method requires solving:

$$
J(x_k) \Delta x = -F(x_k)
$$

where $J = \partial F / \partial x$ is the Jacobian. For a tree-structured network:

$$
\text{nnz}(J) \approx 3N \quad \text{vs} \quad N^2 \text{ for dense}
$$

where $N$ is the total number of unknowns and nnz is the number of non-zero entries. This means sparse solvers (LU decomposition with fill-in reduction, iterative methods like GMRES) achieve $O(N)$ scaling vs $O(N^3)$ for dense solvers.

### 32.7.5 Python Network Optimization Example

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Build a simple 3-well network
Stream = jneqsim.process.equipment.stream.Stream
ThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve
Mixer = jneqsim.process.equipment.mixer.Mixer
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# Declared feed compositions; the labels below do not recombine an exact stock-tank GOR/water cut.
wells = []
chokes = []
for i, (gor, wc) in enumerate([(200, 0.1), (350, 0.25), (150, 0.05)]):
    fluid_i = jneqsim.thermo.system.SystemSrkEos(273.15 + 80, 250.0)
    fluid_i.addComponent("methane", 0.6)
    fluid_i.addComponent("ethane", 0.05)
    fluid_i.addComponent("n-heptane", 0.25)
    fluid_i.addComponent("water", wc)
    fluid_i.setMixingRule("classic")
    fluid_i.setMultiPhaseCheck(True)

    well = Stream(f"Well-{i+1}", fluid_i)
    well.setFlowRate(50000.0, "kg/hr")
    well.setPressure(250.0, "bara")
    well.setTemperature(80.0, "C")
    wells.append(well)

    choke = ThrottlingValve(f"Choke-{i+1}", well)
    choke.setOutletPressure(80.0, "bara")
    chokes.append(choke)

# Mix into manifold
mixer = Mixer("Manifold")
for choke in chokes:
    mixer.addStream(choke.getOutletStream())

# Build process
process = ProcessSystem()
for w in wells:
    process.add(w)
for c in chokes:
    process.add(c)
process.add(mixer)
process.run()

# Demonstrate why fixed feed rates cannot identify a production-maximizing choke pressure.
def fixed_feed_throughput(choke_pressures):
    for i, p in enumerate(choke_pressures):
        chokes[i].setOutletPressure(float(p), "bara")
    process.run()

    # Total mass flow (simplified - full version would separate phases)
    total = sum(float(c.getOutletStream().getFlowRate("kg/hr"))
                for c in chokes)
    return -total  # negative for minimization

bounds = [(40.0, 120.0)] * 3
x0 = [80.0, 80.0, 80.0]

result = minimize(fixed_feed_throughput, x0, method='L-BFGS-B', bounds=bounds)
optimal_pressures = result.x

print("Numerically selected choke pressures for a constant mass-flow objective:")
for i, p in enumerate(optimal_pressures):
    print(f"  Well-{i+1}: {p:.1f} bara")
print(f"Total production: {-result.fun:.0f} kg/hr")

assert abs(-result.fun - 150000.0) < 1.0
print("No production optimum is identified: all three feed rates were prescribed.")
# Couple calibrated WellFlow inflow and tubing hydraulics before optimizing deliverability.
```

### 32.7.6 Gas Lift Allocation

Gas lift is one of the most common artificial lift methods. The optimization problem is to allocate a limited supply of lift gas among multiple wells to maximize total oil production. Each well has a **gas lift performance curve (GLPC)** showing oil rate as a function of gas lift rate — typically S-shaped with an optimal point beyond which additional gas lift actually reduces production (due to excessive gas friction in the tubing).

The gas lift allocation problem:

$$
\max_{q_{\text{GL}}} \quad \sum_{w=1}^{N_w} q_{\text{oil},w}(q_{\text{GL},w})
$$

$$
\text{s.t.} \quad \sum_{w=1}^{N_w} q_{\text{GL},w} \leq Q_{\text{GL}}^{\text{available}}
$$

$$
q_{\text{GL},w} \geq 0 \quad \forall w
$$

The key insight is that at the optimum, the **marginal oil gain per unit gas lift** should be equal across all wells. This is the equal-slope principle:

$$
\frac{dq_{\text{oil},1}}{dq_{\text{GL},1}} = \frac{dq_{\text{oil},2}}{dq_{\text{GL},2}} = \cdots = \frac{dq_{\text{oil},N_w}}{dq_{\text{GL},N_w}}
$$

This can be solved analytically when the GLPC curves are fitted with simple functions (e.g., parabolic), or numerically for general curves.

```python
from scipy.optimize import minimize
import numpy as np

# Synthetic analytic gas-lift response curves; not NeqSim well simulation results.
# Format: oil_rate = f(gas_lift_rate)
def glpc_well1(qgl):
    return 5000 * (1 - np.exp(-qgl / 50000)) - 0.01 * qgl

def glpc_well2(qgl):
    return 3000 * (1 - np.exp(-qgl / 30000)) - 0.005 * qgl

def glpc_well3(qgl):
    return 7000 * (1 - np.exp(-qgl / 80000)) - 0.008 * qgl

glpc = [glpc_well1, glpc_well2, glpc_well3]
Q_gl_available = 150000.0  # Sm3/d total lift gas

# Objective: maximize total oil (minimize negative)
def total_oil(qgl_alloc):
    return -sum(f(q) for f, q in zip(glpc, qgl_alloc))

# Constraint: total gas lift <= available
constraint = {'type': 'ineq',
              'fun': lambda x: Q_gl_available - sum(x)}

bounds = [(0, Q_gl_available)] * 3
x0 = [Q_gl_available / 3] * 3

result = minimize(total_oil, x0, method='SLSQP',
                  bounds=bounds, constraints=constraint)

print("Gas lift allocation (Sm3/d):")
for i, q in enumerate(result.x):
    oil = glpc[i](q)
    print(f"  Well-{i+1}: GL = {q:.0f}, Oil = {oil:.0f} bbl/d")
print(f"Total oil: {-result.fun:.0f} bbl/d")
print(f"Gas utilization: {sum(result.x) / Q_gl_available * 100:.1f}%")
```

### 32.7.7 Robust Network Optimization Under Uncertainty

Production networks operate under significant uncertainty: reservoir deliverability declines, well productivity indices change, water cuts increase, and equipment performance degrades. A **robust optimization** formulation seeks solutions that perform well across a range of scenarios:

$$
\max_{q} \min_{s \in \mathcal{S}} \quad f(q, s)
$$

where $\mathcal{S}$ is the set of uncertainty scenarios. This max-min formulation maximizes the worst-case performance.

Alternatively, a **chance-constrained** formulation allows a small probability of constraint violation:

$$
\max_q \quad E[f(q, \xi)]
$$

$$
\text{s.t.} \quad P[g_j(q, \xi) \leq 0] \geq 1 - \alpha_j \quad \forall j
$$

where $\xi$ represents the uncertain parameters and $\alpha_j$ is the acceptable violation probability (typically 5% or 10%).

In practice, robust optimization for production networks is implemented via:
1. Generate $N_s$ uncertainty scenarios (e.g., varying PI, water cut, GOR)
2. Evaluate the network at each scenario
3. Optimize using the worst-case or expected-value objective
4. Verify feasibility across scenarios

---

## 32.8 Real-Time Optimization (RTO)

**Real-Time Optimization** closes the loop between process models and plant operations by continuously re-optimizing set points as conditions change. An RTO system executes the following cycle:

### 32.8.1 The RTO Cycle

The RTO cycle runs every 15–60 minutes:

1. **Data collection**: Read current measurements from the plant historian
2. **Steady-state detection**: Confirm the plant is at steady state using R-statistic or similar methods (Section 32.5.1)
3. **Data reconciliation**: Reconcile measurements to satisfy mass/energy balances (Section 32.5.2)
4. **Parameter estimation**: Update key model parameters (efficiency, fouling factors, etc.) to match current conditions (Section 32.5.4)
5. **Optimization**: Solve the optimization problem using the calibrated model
6. **Implementation**: Send optimized set points to the DCS/APC layer

### 32.8.2 Steady-State vs Dynamic RTO

| Feature | Steady-State RTO | Dynamic RTO (D-RTO) |
|---------|-----------------|---------------------|
| Model type | Steady-state simulation | Dynamic model |
| Update frequency | 15-60 min | 1-5 min |
| Disturbance handling | Waits for steady state | Optimizes during transients |
| Implementation | Mature, widely used | Emerging |
| Computational cost | Low (one simulation) | High (trajectory optimization) |

### 32.8.3 Integration Architecture

```text
┌─────────────────────────────────────────────────────┐
│                   Plant Historian                      │
│              (OSIsoft PI / Aspen IP.21)                 │
└──────────┬──────────────────────────────┬──────────────┘
           │ Raw measurements             │ Set points
           ▼                              ▲
┌──────────────────────┐     ┌──────────────────────────┐
│  Steady-State         │     │ Advanced Process Control  │
│  Detection           │     │ (APC / MPC)               │
└──────────┬───────────┘     └──────────▲───────────────┘
           │                            │ Optimized targets
           ▼                            │
┌──────────────────────┐     ┌──────────┴───────────────┐
│  Data Reconciliation  │────>│  RTO Optimizer            │
│  & Parameter Est.     │     │  (NeqSim + SciPy/SQP)    │
└──────────────────────┘     └──────────────────────────┘
```

### 32.8.4 Implementation Considerations

Key practical considerations for RTO:

- **Model fidelity**: The model must be accurate enough that optimized set points improve real production. A model with systematic bias will optimize to the wrong point.
- **Constraint handling**: RTO must respect all safety and operational constraints. Hard constraints (equipment trips) must never be violated. Soft constraints (product specs) allow temporary excursions.
## 32.8 Real-Time Optimization

Production optimization is not a one-time activity — it is a continuous process that must adapt to changing reservoir conditions, equipment status, market prices, and operational constraints. Real-Time Optimization (RTO) closes the loop between calibrated process models and plant operations, automatically re-optimizing set points as conditions change.

### 32.8.1 The RTO Architecture

A real-time optimization system consists of four layers that execute at progressively longer time scales:

| Layer | Function | Execution Frequency | Tools |
|-------|----------|-------------------|-------|
| **Regulatory control** | Maintain PID set points | 0.1–1 second | DCS |
| **Advanced Process Control (APC)** | Multi-variable control, constraint pushing | 1–5 minutes | Model Predictive Control |
| **Real-Time Optimization** | Economic optimization of set points | 15–60 minutes | Steady-state process model |
| **Planning / Scheduling** | Production allocation, maintenance planning | Daily–weekly | Reservoir + facilities model |

The key principle is **temporal decomposition**: fast dynamics are handled by lower layers, while slow economic optimization is handled by upper layers. Each layer treats the layers below it as a reliable tracking system and the layers above as slowly varying set point targets.

### 32.8.2 Model Predictive Control (MPC) Fundamentals

Model Predictive Control (MPC) is the enabling technology for the APC layer. MPC uses a dynamic model of the process to predict future behavior over a finite horizon and computes a sequence of control moves that minimizes a cost function while respecting constraints.

The standard MPC formulation solves at each sampling instant:

$$
\min_{\Delta u_0, \ldots, \Delta u_{M-1}} \quad \sum_{k=1}^{P} \|y_{k|t} - y_{\text{ref}}\|_Q^2 + \sum_{k=0}^{M-1} \|\Delta u_k\|_R^2
$$

subject to:

$$
y_{k+1|t} = A \, y_{k|t} + B \, \Delta u_k \quad \text{(prediction model)}
$$

$$
u_{\min} \leq u_k \leq u_{\max} \quad \text{(manipulated variable limits)}
$$

$$
y_{\min} \leq y_k \leq y_{\max} \quad \text{(controlled variable limits)}
$$

$$
\Delta u_{\min} \leq \Delta u_k \leq \Delta u_{\max} \quad \text{(rate-of-change limits)}
$$

where:

- $y_{k|t}$ is the predicted output at future time $k$, given current time $t$
- $y_{\text{ref}}$ is the target reference trajectory (set point from the RTO layer)
- $\Delta u_k$ is the control move (change in manipulated variable) at step $k$
- $P$ is the prediction horizon (how far ahead the controller looks)
- $M$ is the control horizon ($M \leq P$; beyond $M$, $\Delta u = 0$)
- $Q$ and $R$ are weighting matrices for output tracking and control effort, respectively

The MPC solves this quadratic program (QP) at each sample time, applies only the first control move $\Delta u_0$, then re-solves at the next sample — the **receding horizon** principle. This provides feedback: if the model prediction is imperfect, the next measurement corrects the prediction and the controller adapts.

### 32.8.3 Economic MPC for Production Optimization

Standard MPC drives outputs to fixed set points. **Economic MPC (EMPC)** replaces the tracking objective with a direct economic objective:

$$
\min_{\Delta u} \quad -\sum_{k=1}^{P} \left[ p_{\text{oil}} \cdot q_{\text{oil},k} + p_{\text{gas}} \cdot q_{\text{gas},k} - c_{\text{energy}} \cdot W_k \right]
$$

subject to the same dynamic model and constraint equations.

Here the objective directly maximizes revenue minus energy cost, where $p_{\text{oil}}$ and $p_{\text{gas}}$ are commodity prices, $q_{\text{oil},k}$ and $q_{\text{gas},k}$ are predicted oil and gas production rates, and $W_k$ is the predicted energy consumption (compressor power, pump power, etc.). The EMPC continuously pushes the process to its economic optimum while respecting all operational constraints — it inherently handles the trade-off between production maximization and constraint management.

Key advantages of EMPC over the traditional RTO + APC cascade:

- **Unified layer** — eliminates the interface between steady-state RTO and dynamic APC
- **Transient exploitation** — can exploit transient dynamics for economic benefit (e.g., temporarily exceeding a soft constraint during a slug event)
- **Faster response** — reacts to price changes and disturbances within the MPC execution cycle (minutes) rather than waiting for the RTO cycle (hours)

### 32.8.4 Closed-Loop Architecture with NeqSim Digital Twin

In a closed-loop RTO implementation using NeqSim as the digital twin:

1. **Data acquisition**: Plant measurements (pressures, temperatures, flow rates, compositions) are collected from the DCS/historian at regular intervals (1–5 minutes)
2. **Steady-state detection**: The `SteadyStateDetector` (Section 32.5.1) determines whether the plant is in a sufficiently steady state for model update
3. **Data reconciliation**: The `DataReconciliationEngine` (Section 32.5.2) validates and reconciles measurements against the NeqSim process model, detecting gross errors and sensor faults
4. **Model calibration**: The `BatchParameterEstimator` (Section 32.5.4) tunes key model parameters (equipment efficiencies, heat transfer coefficients, valve characteristics) to match the reconciled plant data
5. **Optimization**: The calibrated NeqSim model is optimized using `SQPoptimizer` or external optimizers (Section 32.3) to find the economically optimal operating point within the current constraint set
6. **Set point deployment**: The optimal set points are sent to the APC/DCS layer, with rate limits and feasibility checks to ensure smooth transitions
7. **Monitoring**: Key performance indicators (production rate, specific energy, constraint margins) are tracked to verify that the optimization is delivering the expected benefit

This cycle repeats at the RTO execution frequency (typically every 15–60 minutes). The steady-state detection step is critical — running the optimizer during a transient (slug arrival, well startup, compressor trip) would produce misleading results.

### 32.8.5 Practical Considerations for RTO Deployment

Deploying RTO in a production environment requires attention to several practical challenges:

- **Model fidelity**: The NeqSim process model must be sufficiently accurate to capture the key economic trade-offs. A model that is detailed enough for design but too slow for real-time execution (> 30 seconds) may need simplification (reduced component list, lumped equipment).
- **Robustness**: The optimizer must converge reliably even with noisy or incomplete data. Use warm-starting (initialize from previous solution), bounded variables, and fallback to previous set points if optimization fails.
- **Constraint handling**: Distinguish between hard constraints (safety-related: MAWP, trip limits) that must never be violated and soft constraints (operational: target temperatures, efficiency goals) that can be temporarily exceeded.
- **Move suppression**: Limit the rate of set point changes to avoid disturbing the APC layer. Typical limits: ±2% per cycle for pressures, ±5% for flow rates.
- **Fallback**: If RTO fails to converge or produces infeasible results, revert to the previous set points.

---


<!-- September 2026 source update -->
## Qualification of advanced optimization and surrogate workflows

An advanced optimizer or surrogate inherits the limitations of its training and evaluation model. Preserve the thermodynamic method, composition envelope, phase transitions, equipment limits, validity range and failed samples in the training record. A low average interpolation error does not establish reliable behaviour near an active compressor-map or export-quality restriction.

The current plant evidence classes freeze existing physics results and their provenance; they are not new general-purpose predictive models. Their scale benchmarks qualify particular evidence paths or synthetic fixtures, rather than demonstrating complete industrial optimization for every plant topology. Do not extrapolate a single elapsed time into a generic performance claim \cite{neqsim2026update}.

Use a surrogate to propose or screen candidates, then replay the selected candidate with the full NeqSim process model. Compare the objective and every active constraint against the surrogate prediction, record discrepancies, and reject unavailable or stale evidence. A model-assisted policy should revert to a validated feasible baseline when its domain or evidence checks fail. The same distinction applies to reinforcement learning: an offline simulation policy is not demonstrated plant control.

---

## 32.9 Summary

This chapter has explored advanced optimization topics that extend beyond routine production optimization:

1. **Multi-objective optimization** using `optimizePareto()` generates Pareto fronts that reveal trade-offs between competing objectives, with automatic knee point detection identifying balanced operating points

2. **Sequential Quadratic Programming** via `SQPoptimizer` provides fast, efficient solving of constrained nonlinear programs with equality and inequality constraints, BFGS Hessian updates, and KKT convergence guarantees

3. **External optimizer integration** through `ProcessSimulationEvaluator` connects NeqSim to SciPy (L-BFGS-B, differential evolution, SLSQP), NLopt, and other toolboxes, with surrogate-assisted optimization for expensive simulations

4. **Data reconciliation and model calibration** using `SteadyStateDetector`, `DataReconciliationEngine`, and `BatchParameterEstimator` ground models in reality by detecting steady state, reconciling measurements, identifying sensor faults, and tuning parameters to plant data

5. **Batch studies** via `BatchStudy` enable efficient parameter sweeps, sensitivity analyses, and design space exploration with statistical aggregation and multi-objective ranking

6. **Pipeline network optimization** applies specialized algorithms to the coupled hydraulic problem of multi-well, multi-manifold production networks with choke allocation and gas lift optimization

7. **Real-Time Optimization** closes the loop between calibrated models and plant operations, continuously re-optimizing set points as conditions change

These techniques form the toolkit for advanced production optimization practitioners, enabling them to handle the full complexity of real production systems — multiple objectives, hard constraints, uncertain data, and interconnected networks.

The remaining sections of this chapter extend the optimization framework into the rapidly evolving domain of artificial intelligence and machine learning, covering physics-informed surrogates, hybrid simulation architectures, reinforcement learning, uncertainty quantification, and agentic interfaces.

8. **Physics-informed surrogate models** replace computationally expensive first-principles simulations with trained neural networks that embed governing equations, enabling real-time optimization and large-scale ensemble studies

9. **Hybrid physics-AI simulation** architectures allow surrogate equipment units to coexist with full-physics units in the same flowsheet, with conservation enforcement and automatic fallback when surrogates exceed their validity domain

10. **Reinforcement learning** formulates production optimization as a sequential decision problem where an agent learns to control valve positions, compressor speeds, and separator pressures through interaction with a process simulation environment

11. **Equipment utilization metrics** provide structured observation and reward signals for AI optimization, translating physical capacity constraints into quantitative feedback that guides both human operators and autonomous agents

12. **Uncertainty quantification** for AI-driven optimization ensures that surrogate predictions and RL policy recommendations carry confidence bounds, enabling risk-aware decision-making and building operator trust

13. **Agentic AI and natural language interfaces** allow operators and engineers to interact with simulation tools through conversational protocols, democratizing access to optimization capabilities

14. **Computational performance characterization** establishes that modern equation-of-state-based simulators execute fast enough for direct use in AI training loops, eliminating the assumption that surrogates are always needed

---

## 32.10 Physics-Informed Surrogate Models for Process Simulation

### 32.10.1 The Computational Challenge

Integrated production optimization requires coupling reservoir simulation, multiphase wellbore flow, surface process facilities, and export pipeline hydraulics into a single model. Each evaluation of this coupled system may require minutes to hours of computation, depending on fidelity. When such a model serves as the objective function for an optimizer that requires hundreds or thousands of evaluations, the total wall-clock time becomes prohibitive. Real-time optimization demands that model evaluations complete within seconds; large-scale ensemble studies (Monte Carlo uncertainty quantification, robust optimization) may require $10^4$–$10^6$ evaluations.

Surrogate models — also called metamodels, emulators, or response surfaces — approximate the input-output behaviour of the expensive simulation using a computationally cheaper mathematical representation. Traditional surrogates include polynomial response surfaces, kriging (Gaussian process regression), and radial basis functions. While effective for low-dimensional problems, these methods struggle with the high-dimensional, nonlinear, multi-output nature of process simulations.

The emergence of deep learning has transformed surrogate modeling by providing architectures capable of approximating complex, high-dimensional functions with millions of parameters. More importantly, *physics-informed* approaches embed domain knowledge directly into the learning process, improving generalization, reducing data requirements, and ensuring that predictions respect fundamental physical laws.

### 32.10.2 Physics-Informed Neural Networks (PINNs)

Physics-Informed Neural Networks (Raissi et al., 2019) embed the governing partial differential equations directly into the neural network loss function. Consider a general PDE of the form:

$$
\mathcal{N}[u(x, t); \lambda] = 0, \quad x \in \Omega, \quad t \in [0, T]
$$

where $\mathcal{N}$ is a nonlinear differential operator parameterized by $\lambda$, and $u(x, t)$ is the solution. A PINN approximates $u$ with a neural network $u_\theta(x, t)$ and minimizes a composite loss:

$$
\mathcal{L}(\theta) = w_d \mathcal{L}_{\text{data}} + w_r \mathcal{L}_{\text{residual}} + w_b \mathcal{L}_{\text{boundary}}
$$

where:

$$
\mathcal{L}_{\text{data}} = \frac{1}{N_d} \sum_{i=1}^{N_d} \| u_\theta(x_i, t_i) - u_i^{\text{obs}} \|^2
$$

$$
\mathcal{L}_{\text{residual}} = \frac{1}{N_r} \sum_{j=1}^{N_r} \| \mathcal{N}[u_\theta(x_j, t_j)] \|^2
$$

$$
\mathcal{L}_{\text{boundary}} = \frac{1}{N_b} \sum_{k=1}^{N_b} \| u_\theta(x_k, t_k) - g(x_k, t_k) \|^2
$$

The physics residual term $\mathcal{L}_{\text{residual}}$ is computed using automatic differentiation, enabling exact evaluation of spatial and temporal derivatives. The key advantage is that PINNs work even with sparse observational data — the physics residual provides supervisory signal everywhere in the domain.

For production optimization, the governing equations include conservation of mass, momentum, and energy:

$$
\frac{\partial (\rho_\alpha S_\alpha)}{\partial t} + \nabla \cdot (\rho_\alpha \mathbf{v}_\alpha) = q_\alpha, \quad \alpha \in \{\text{oil, gas, water}\}
$$

Training a PINN on these equations produces a surrogate that respects conservation laws by construction, even when extrapolating beyond the training data.

### 32.10.3 Operator Learning: DeepONet and Fourier Neural Operators

While PINNs solve a single instance of a PDE, *operator learning* methods learn the mapping from input functions (boundary conditions, initial conditions, source terms) to solution functions. This enables prediction across entire families of problems without re-training.

**DeepONet** (Lu et al., 2021) represents the solution operator $\mathcal{G}: u \mapsto s$ using a branch network (encoding the input function) and a trunk network (encoding the evaluation location):

$$
\mathcal{G}_\theta(u)(y) = \sum_{k=1}^{p} b_k(u) \cdot t_k(y)
$$

where $b_k$ are outputs of the branch network and $t_k$ are outputs of the trunk network. For example, a trained DeepONet can predict the pressure profile along a pipeline for any inlet condition, flow rate, or fluid composition — without re-solving the multiphase flow equations.

**Fourier Neural Operators** (Li et al., 2021) learn in the frequency domain, applying learned spectral filters:

$$
(\mathcal{K}v)(x) = \mathcal{F}^{-1}\left( R_\phi \cdot \mathcal{F}(v) \right)(x)
$$

where $\mathcal{F}$ denotes the Fourier transform and $R_\phi$ is a learned weight matrix in frequency space. FNOs achieve resolution-invariant learning — a model trained on coarse grids can predict on fine grids without retraining.

### 32.10.4 Surrogate Training Workflow

A systematic workflow for building process simulation surrogates proceeds as follows:

1. **Design of experiments**: Use Latin Hypercube Sampling (LHS) to distribute training points efficiently across the input space. For $d$ input dimensions with $N$ points, LHS ensures coverage of all one-dimensional projections:

$$
x_i^{(j)} = \frac{\pi_j(i) - U_{ij}}{N}, \quad i = 1, \ldots, N, \quad j = 1, \ldots, d
$$

where $\pi_j$ is a random permutation and $U_{ij} \sim \text{Uniform}(0,1)$.

2. **Run the physics simulator**: Execute NeqSim at each design point to generate input-output pairs. The simulator provides thermodynamically consistent results including phase equilibria, transport properties, and equipment performance.

3. **Train the surrogate**: Fit the neural network using the training set. For physics-informed models, include the physics residual in the loss function. Use Adam optimizer with learning rate scheduling and early stopping.

4. **Validate**: Evaluate on a held-out test set (typically 20% of the data). Report $R^2$, mean absolute error, and maximum error. Check that physics constraints are satisfied (mass balance closure, second law compliance).

5. **Deploy**: Embed the trained model in the optimization loop, replacing the expensive simulator call. Monitor for out-of-distribution inputs.

### 32.10.5 Computational Performance Enabling AI

The feasibility of surrogate training depends critically on how fast the physics simulator can generate training data. Modern equation-of-state-based simulators such as NeqSim achieve remarkable throughput on commodity hardware. Flash calculations (the core thermodynamic operation) execute in 1–6 ms depending on the number of components, while full process simulations complete in approximately 20 ms on a warm JVM.

At these speeds, generating $10^5$ training samples for a full-process surrogate requires approximately 33 minutes — well within the practical range for daily retraining as operating conditions evolve. For flash-only surrogates, $10^5$ samples can be generated in roughly 2 minutes. This performance eliminates the common assumption that large-scale training data generation is impractical with first-principles simulators.

### 32.10.6 Domain-Specific Surrogates

Different components of the production system benefit from tailored surrogate architectures:

- **Flash surrogates**: Input: $(T, P, z_1, \ldots, z_{n_c})$; Output: phase fractions $(\beta_g, \beta_l)$, phase densities, enthalpies, viscosities. The phase boundary (bubble/dew point curve) presents a discontinuity that requires careful architecture design — mixture-of-experts or classification-then-regression approaches handle this well.

- **Equipment surrogates**: A compressor surrogate maps inlet conditions (T, P, flow, composition) to outlet conditions, power consumption, and efficiency. The surrogate must respect the second law of thermodynamics: outlet temperature must exceed inlet temperature for compression, and power must be positive.

- **Process surrogates**: An entire separation train — from wellhead to export — can be approximated as a single surrogate mapping operating set points to production rates and quality specifications. This is the highest-level surrogate and enables the fastest optimization, but requires the most training data due to the larger input/output dimensionality.

---

## 32.11 Hybrid Physics-AI Simulation Architectures

### 32.11.1 The Selective Fidelity Concept

Not every unit operation in a process flowsheet demands the same computational effort. A simple mixer requires only mass and energy balance — a trivial calculation. A rigorous flash calculation inside a distillation column tray, however, may iterate through dozens of Newton-Raphson steps. The insight behind hybrid physics-AI architectures is to replace only the computationally expensive units with trained surrogates while keeping cheap units at full physics fidelity.

This selective fidelity approach requires that surrogate units present the same interface as their physics-based counterparts. The surrogate must accept inlet stream(s), compute outlet stream(s), and report performance metrics — exactly as a physics-based unit does. The process system that orchestrates the simulation should be agnostic to whether a particular unit uses rigorous thermodynamics or a neural network inference.

### 32.11.2 Surrogate Equipment Architecture

A surrogate equipment unit implements the same process equipment interface as a physics-based unit:

**Execution scope:** conceptual adapter requiring trained ONNX model, stream fields, domain checks and conservation implementation.

```java pattern: conceptual adapter requiring trained ONNX model, stream fields, domain checks and conservation implementation
// Conceptual architecture: a surrogate compressor
public class SurrogateCompressor extends ProcessEquipmentBaseClass {
    private ONNXModel model;          // Trained neural network
    private double[] inputRangeMin;   // Valid input domain (lower bounds)
    private double[] inputRangeMax;   // Valid input domain (upper bounds)
    private boolean outsideDomain;    // Extrapolation warning flag

    @Override
    public void run() {
        // Extract features from inlet stream
        double[] features = extractFeatures(inletStream);

        // Check if inputs are within training domain
        outsideDomain = checkDomain(features);
        if (outsideDomain) {
            log.warn("Surrogate input outside training domain");
        }

        // Neural network inference (~0.1 ms vs ~5 ms for physics)
        double[] prediction = model.predict(features);

        // Apply predictions to outlet stream
        applyPredictions(outletStream, prediction);

        // Enforce mass conservation (correction step)
        enforceConservation(inletStream, outletStream);
    }
}
```

The key design principles are:

1. **Interface compatibility**: The surrogate extends the same base class as the physics unit, ensuring that the process system can execute it without special handling.
2. **Domain awareness**: The surrogate stores the input range of its training data and flags when inputs fall outside this domain. This addresses the fundamental extrapolation risk of neural network models.
3. **Conservation correction**: After the neural network produces its prediction, a post-processing step adjusts the outlet to exactly satisfy mass balance, reporting any energy residual.

### 32.11.3 The Cascading Inconsistency Problem

The most subtle challenge in hybrid simulation arises at the interface between physics-based and surrogate units. Consider a flowsheet where a physics-based separator feeds a surrogate compressor, which in turn feeds a physics-based cooler.

The physics-based separator produces an outlet stream with thermodynamically consistent properties — phase equilibrium, enthalpy, entropy, and density all satisfy the equation of state. The surrogate compressor approximates the outlet conditions, but unless it was trained with perfect accuracy, the outlet stream may not be exactly thermodynamically consistent. When this slightly inconsistent stream enters the physics-based cooler, the cooler's rigorous flash calculation must resolve the inconsistency, potentially introducing errors or convergence difficulties.

The cascading inconsistency problem worsens through the flowsheet. Each physics-surrogate-physics interface introduces a small error, and these errors can compound. The solutions include:

- **Re-flash at interfaces**: After a surrogate produces its output, run a rigorous flash calculation on the outlet stream to restore thermodynamic consistency. This adds cost ($\sim$1–5 ms per interface) but guarantees consistency.
- **Tolerance-based fallback**: Monitor the mass and energy balance residuals at each interface. If the residual exceeds a configurable tolerance (e.g., 0.1% mass balance error), fall back to the full physics calculation for that unit.
- **Ensemble averaging**: Use an ensemble of surrogates and take the average prediction. Ensemble predictions tend to be better calibrated and reduce the variance of individual model errors.

### 32.11.4 Conservation Enforcement

Mass conservation is non-negotiable in process simulation. The surrogate correction step ensures exact mass balance:

$$
\dot{m}_{\text{out}} = \dot{m}_{\text{in}} \quad \text{(total mass)}
$$

$$
\dot{m}_{\text{out},i} = \dot{m}_{\text{in},i} \cdot \frac{\hat{y}_i}{\sum_j \hat{y}_j} \quad \text{(per-component)}
$$

where $\hat{y}_i$ is the surrogate's predicted outlet composition for component $i$, normalized to ensure closure. The energy residual is computed and reported:

$$
\Delta \dot{Q} = \dot{m}_{\text{out}} h_{\text{out}} - \dot{m}_{\text{in}} h_{\text{in}} - \dot{W}
$$

where $h$ denotes specific enthalpy and $\dot{W}$ is shaft work. If $|\Delta \dot{Q}|$ exceeds the tolerance, the system falls back to the physics-based calculation.

### 32.11.5 Model Interchange and Deployment

Standardized model interchange formats enable separation of the training environment (typically Python with PyTorch, TensorFlow, or JAX) from the deployment environment (Java-based process simulator). The Open Neural Network Exchange (ONNX) format provides a common representation:

1. **Train** the surrogate model in Python using PyTorch or TensorFlow
2. **Export** the trained model to ONNX format
3. **Load** the ONNX model in the Java runtime using an inference library (e.g., ONNX Runtime for Java)
4. **Inference**: The Java-side surrogate equipment calls the ONNX model's `predict()` method during its `run()` execution

The ONNX model is accompanied by metadata describing the training domain (input ranges, output ranges, training error statistics), enabling the surrogate to detect out-of-distribution inputs at runtime.

### 32.11.6 When to Use Surrogates vs Full Physics

The decision to deploy surrogates depends on the computational bottleneck and accuracy requirements. For systems where the full process simulation completes in tens of milliseconds, the speedup from surrogates may not justify the added complexity. Surrogates offer the greatest benefit when:

- The simulation contains rigorous distillation columns (multiple equilibrium stages, each requiring a flash calculation)
- The optimization loop requires $>10^5$ evaluations (Monte Carlo, reinforcement learning)
- Real-time constraints demand sub-millisecond response
- The same simulation is evaluated repeatedly with small input variations (parametric studies)

For straightforward separation and compression processes where full-physics evaluation takes $\sim$20 ms, direct optimization without surrogates is often practical (Section 32.16).

---

## 32.12 Reinforcement Learning for Multi-Variable Production Optimization

### 32.12.1 The RL Formulation

Production optimization can be formulated as a Markov Decision Process (MDP), the mathematical framework underlying reinforcement learning. An agent interacts with the process environment by observing its state, taking actions, and receiving rewards:

$$
\text{MDP} = (\mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma)
$$

where $\mathcal{S}$ is the state space, $\mathcal{A}$ the action space, $\mathcal{P}: \mathcal{S} \times \mathcal{A} \times \mathcal{S} \to [0,1]$ the transition probability, $\mathcal{R}: \mathcal{S} \times \mathcal{A} \to \mathbb{R}$ the reward function, and $\gamma \in [0,1)$ the discount factor. The agent learns a policy $\pi: \mathcal{S} \to \mathcal{A}$ that maximizes the expected cumulative discounted reward:

$$
J(\pi) = \mathbb{E}_\pi \left[ \sum_{t=0}^{\infty} \gamma^t r_t \right]
$$

In the production optimization context:

- **State** $\mathcal{S}$: Process conditions (temperatures, pressures, flow rates, compositions) and equipment operating points. A typical North Sea process facility has 30–100 measurable state variables.
- **Action** $\mathcal{A}$: Control variables including valve positions (0–100%), compressor speeds (5,000–12,000 rpm), separator pressures (10–200 bara), flow routing decisions, and injection rates.
- **Reward** $\mathcal{R}$: The economic objective penalized by constraint violations and energy costs.

### 32.12.2 Observation Space Design

The observation space must capture sufficient information for the agent to make optimal decisions. Raw process measurements can be augmented with derived features that encode equipment utilization and system-level constraints:

$$
\mathbf{s}_t = \left[ T_1, P_1, \dot{m}_1, \ldots, u_{\text{comp}}, u_{\text{sep}}, u_{\text{valve}}, \ldots \right]
$$

where $u_i$ denotes the utilization ratio of equipment $i$ (Section 32.13). Feature selection based on equipment utilization metrics reduces the dimensionality while preserving the most operationally relevant information. Normalizing all observations to the range $[0, 1]$ using physical bounds (minimum and maximum operating values) stabilizes training.

### 32.12.3 Action Space Design

The action space for production optimization is typically continuous and multi-dimensional. Each action variable is normalized to $[-1, 1]$ for the agent and mapped to physical units at the environment boundary:

$$
a_{\text{physical}} = a_{\text{min}} + \frac{a_{\text{agent}} + 1}{2} (a_{\text{max}} - a_{\text{min}})
$$

Typical action variables and their ranges include:

| Variable | Physical Range | Agent Range |
|----------|---------------|-------------|
| Separator pressure | 30–120 bara | $[-1, 1]$ |
| Compressor speed | 5,000–12,000 rpm | $[-1, 1]$ |
| Valve opening | 0–100% | $[-1, 1]$ |
| Gas lift rate | 0–200,000 Sm³/d | $[-1, 1]$ |

### 32.12.4 Reward Shaping

The reward function translates the multi-objective production optimization problem into a scalar signal that the RL agent can maximize. A well-designed reward captures the economic objective while penalizing constraint violations and encouraging balanced equipment utilization:

$$
r_t = w_{\text{prod}} \cdot Q_t - w_{\text{energy}} \cdot P_{\text{comp},t} - w_{\text{penalty}} \cdot \sum_{i} \max(0, u_{i,t} - 1) + w_{\text{balance}} \cdot \sigma(\mathbf{u}_t)^{-1}
$$

where:
- $Q_t$ is the production rate (oil or gas, normalized)
- $P_{\text{comp},t}$ is the total compression power (energy cost)
- $u_{i,t}$ is the utilization ratio of equipment $i$ (values exceeding 1.0 indicate constraint violations)
- $\sigma(\mathbf{u}_t)$ is the standard deviation of utilization ratios (low values indicate balanced loading)
- $w_{\text{prod}}, w_{\text{energy}}, w_{\text{penalty}}, w_{\text{balance}}$ are weighting coefficients

The penalty term uses a ReLU-style formulation: zero when all equipment operates within capacity ($u_i \leq 1$), and linearly increasing for violations. This creates a smooth gradient that guides the agent away from infeasible regions.

### 32.12.5 Algorithms for Continuous Control

Two classes of algorithms dominate continuous-action RL:

**Proximal Policy Optimization (PPO)** (Schulman et al., 2017) is an on-policy algorithm that constrains policy updates using a clipped surrogate objective:

$$
\mathcal{L}^{\text{CLIP}}(\theta) = \mathbb{E}_t \left[ \min\left( r_t(\theta) \hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) \hat{A}_t \right) \right]
$$

where $r_t(\theta) = \pi_\theta(a_t | s_t) / \pi_{\theta_{\text{old}}}(a_t | s_t)$ is the probability ratio and $\hat{A}_t$ is the estimated advantage. PPO is robust, easy to tune, and parallelizable.

**Soft Actor-Critic (SAC)** is an off-policy algorithm that maximizes both reward and entropy:

$$
J(\pi) = \sum_{t=0}^{T} \mathbb{E} \left[ r(s_t, a_t) + \alpha \mathcal{H}(\pi(\cdot | s_t)) \right]
$$

The entropy bonus $\alpha \mathcal{H}$ encourages exploration and prevents premature convergence to suboptimal policies. SAC achieves better sample efficiency than PPO by reusing past experience via a replay buffer.

### 32.12.6 Computational Feasibility

The computational feasibility of RL for production optimization depends on the environment step time. At approximately 1.5 ms per RL step (including simulation evaluation and gradient computation), a moderate-complexity process facility achieves roughly 669 steps per second. The resulting training budgets are:

| Training steps | Wall-clock time |
|---------------|-----------------|
| $10^5$ | ~2.5 minutes |
| $10^6$ | ~25 minutes |
| $10^7$ | ~4.2 hours |

PPO and SAC typically converge within $10^5$–$10^7$ steps, placing the total training time between minutes and hours. This makes direct-simulation RL practical without pre-training surrogates — the process simulator itself serves as the RL environment.

### 32.12.7 Steady-State vs Dynamic RL

Two operating paradigms exist for RL in production optimization:

- **Steady-state RL**: The agent applies actions (set points) and the environment runs a full steady-state convergence (`run()`). Each episode consists of sequential set point decisions. This is appropriate for quasi-steady operating point optimization where transient dynamics are fast relative to the optimization cycle.

- **Dynamic RL**: The agent interacts with the transient simulator (`runTransient(dt)`) at each control interval. The environment maintains continuous state between steps. This formulation is appropriate for startup/shutdown optimization, disturbance rejection, and operations where exploiting transient dynamics offers economic benefit.

### 32.12.8 Multi-Agent Architectures

Large production facilities with multiple process areas (separation, compression, dehydration, export) present a choice between centralized and decentralized RL architectures:

- **Centralized**: A single agent observes the entire plant state and controls all actuators. This captures all interactions but scales poorly with plant size (curse of dimensionality).
- **Decentralized**: Separate agents control separate process areas, communicating only through shared stream variables. This scales better but may miss cross-area optimization opportunities.
- **Hierarchical**: A high-level agent sets production targets for each area; local agents optimize within their areas to meet the targets. This combines the benefits of both approaches.

### 32.12.9 Sim-to-Real Transfer

Physics-based simulation environments hold a structural advantage over purely data-driven surrogates for RL training. The simulator captures thermodynamic equilibrium, conservation laws, and equipment performance curves — relationships that transfer directly to the real plant. The remaining sim-to-real gap arises from:

- **Model calibration uncertainty**: Equipment efficiencies, fouling factors, and heat transfer coefficients may differ between model and plant
- **Unmeasured disturbances**: Slug flow, composition variations, and ambient temperature changes
- **Equipment degradation**: Gradual performance deterioration not captured in the model

Domain randomization — varying model parameters during training to expose the agent to a range of possible plant conditions — is the standard technique for improving transfer robustness.

---

## 32.13 Equipment Utilization as AI Reward Signals

### 32.13.1 From Physical Constraints to Numerical Metrics

Every piece of process equipment has physical capacity limits that define its operating envelope. Compressors are limited by power, surge margin, and maximum speed; separators by gas velocity and liquid retention time; heat exchangers by duty and tube-side pressure drop; valves by their flow coefficient ($C_v$); and pipelines by erosional velocity and pressure drop.

The *utilization ratio* quantifies how close equipment operates to its rated capacity:

$$
u_i = \frac{X_{\text{actual},i}}{X_{\text{rated},i}}
$$

where $X_{\text{actual}}$ is the current operating value and $X_{\text{rated}}$ is the equipment's design capacity. When $u_i < 1$, the equipment has spare capacity; when $u_i = 1$, it is at its limit; when $u_i > 1$, the operating point exceeds the rated capacity (a constraint violation in optimization terms).

### 32.13.2 Capacity Constraint Framework

A systematic capacity constraint framework computes utilization ratios for all equipment types in the process:

| Equipment | Constraint | Utilization Metric |
|-----------|-----------|-------------------|
| Compressor | Power | $u = P_{\text{actual}} / P_{\text{rated}}$ |
| Compressor | Surge | $u = Q_{\text{surge}} / Q_{\text{actual}}$ |
| Separator | Gas capacity | $u = v_{\text{gas}} / v_{\text{max}}$ (Souders-Brown) |
| Separator | Liquid retention | $u = \tau_{\text{min}} / \tau_{\text{actual}}$ |
| Heat exchanger | Duty | $u = Q_{\text{actual}} / Q_{\text{design}}$ |
| Valve | Flow capacity | $u = C_{v,\text{required}} / C_{v,\text{installed}}$ |
| Pipeline | Velocity | $u = v_{\text{actual}} / v_{\text{erosional}}$ |

The system-level *bottleneck* is the equipment with the highest utilization ratio. Identifying the bottleneck is essential for optimization because it determines which constraint is currently limiting total production.

### 32.13.3 Bottleneck Analysis for AI

A bottleneck analyzer ranks all equipment by utilization and classifies the system state:

1. **Identify the primary bottleneck**: The equipment with the highest utilization ratio
2. **Compute headroom**: For each equipment, $h_i = 1 - u_i$ represents the fractional spare capacity
3. **Generate debottlenecking recommendations**: Based on the bottleneck type, suggest specific actions (increase compressor speed, reduce separator pressure, adjust valve opening)

These outputs translate directly into AI reward decomposition. Instead of a monolithic reward signal, each equipment's utilization contributes a component:

$$
r_{\text{constraint}} = - \sum_{i=1}^{N_{\text{equip}}} w_i \cdot \max(0, u_i - u_{\text{target},i})
$$

where $u_{\text{target},i}$ is typically 0.9–0.95 (allowing a safety margin below the rated capacity). The bottleneck analyzer identifies which component is currently limiting, enabling the RL agent to focus its exploration on the most impactful control variables.

### 32.13.4 From Utilization to Actionable Decisions

The mapping from utilization metrics to control actions provides a structured way to guide optimization:

- **High gas compressor utilization** ($u > 0.95$): Reduce gas throughput, divert gas to flare (last resort), or shed load from lower-priority wells
- **High separator liquid utilization** ($u > 0.95$): Reduce liquid loading by choking back high-water-cut wells, or increase separator pressure to flash more gas
- **Imbalanced utilization** (high variance in $\sigma(\mathbf{u})$): Some equipment is overloaded while others are underutilized — rebalance by adjusting routing or set points

These heuristic translations serve as initialization strategies for RL agents (curriculum learning) and as interpretability aids for operators reviewing AI recommendations.

### 32.13.5 Economic Reward with the Value-Chain Objective

The constraint-penalty reward of Section 32.13.3 keeps the agent feasible, but the *driving* term of the reward should be monetary. NeqSim provides `EconomicParameters` and `ValueChainObjective` (package `neqsim.process.fielddevelopment.integrated`) to convert a flowsheet's export rates and power draw into a single net-value-per-day signal that already accounts for energy cost and carbon:

```python
exportGasSm3PerDay, exportOilSm3PerDay, totalPowerKw = 1.0e6, 250.0, 5000.0
# Declared synthetic scenario values; replace with solved process outputs.
EconomicParameters = jneqsim.process.optimization.valuechain.EconomicParameters
ValueChainObjective = jneqsim.process.optimization.valuechain.ValueChainObjective

econ = (EconomicParameters()
        .setGasPrice(3.0)                       # NOK/Sm3
        .setOilPrice(4500.0)                    # NOK/Sm3
        .setPowerCost(0.6)                      # NOK/kWh
        .setCo2Tax(1200.0)                      # NOK/tonne
        .setCo2IntensityTonnePerMWh(0.20)
        .setDiscountRate(0.08))

objective = ValueChainObjective(econ)
value = objective.evaluate(exportGasSm3PerDay, exportOilSm3PerDay, totalPowerKw)
reward = value.getNetValueNokPerDay()           # revenue − energy − carbon cost

print("Synthetic scenario net value NOK/day:", reward)
```

The `ValueResult` decomposes the reward into `getRevenueNokPerDay()`, `getEnergyCostNokPerDay()`, `getCarbonCostNokPerDay()`, `getCo2TonnePerDay()`, and `getNetValueNokPerDay()`, so an RL reward can be shaped from interpretable economic components rather than a single opaque number. The combined reward used in practice is

$$
r = \underbrace{V_{\text{net}}(\text{export, power})}_{\text{ValueChainObjective}} \; - \; \underbrace{\sum_i w_i \max(0, u_i - u_{\text{target},i})}_{\text{utilization penalty}}
$$

pairing the economic driver with the utilization snapshot penalty (Chapter 23). For multi-year investment timing rather than instantaneous operation, `LifeOfFieldOptimizer(nYears, econ)` enumerates installation-year combinations of candidate `Investment` items and returns the discounted-cash-flow optimum via `optimize(evaluator)`, with `presentValueOfAnnualCashFlow(...)` on the objective discounting each year's net value back to present.

---

## 32.14 Uncertainty Quantification for AI-Driven Optimization

### 32.14.1 Why Uncertainty Quantification Matters

AI models — whether surrogates for process simulation or RL policies for optimal control — produce point predictions. In safety-critical production optimization, operators need to know *how confident* the AI is in its recommendation. An RL agent that recommends increasing separator pressure by 10 bar should be accompanied by a confidence assessment: is this a well-explored region of the operating space, or is the agent extrapolating into unfamiliar territory?

Uncertainty in AI predictions arises from two sources:

- **Epistemic uncertainty** (model uncertainty): Due to limited training data. Reducible by collecting more data or exploring more of the operating space.
- **Aleatoric uncertainty** (data uncertainty): Due to inherent randomness in the process (measurement noise, stochastic disturbances). Irreducible by the model.

Distinguishing these two types enables targeted uncertainty reduction — acquiring training data in high-epistemic-uncertainty regions while accepting that aleatoric uncertainty sets a floor on prediction accuracy.

### 32.14.2 Monte Carlo Dropout

The simplest approach to UQ in neural networks is Monte Carlo (MC) dropout. During training, dropout randomly zeroes a fraction $p$ of neuron activations to prevent overfitting. During inference, dropout is *kept active*, and the network is evaluated $M$ times:

$$
\hat{y}_m = f_\theta(x; \text{mask}_m), \quad m = 1, \ldots, M
$$

The predictive mean and variance are:

$$
\mu(x) = \frac{1}{M} \sum_{m=1}^{M} \hat{y}_m, \qquad \sigma^2(x) = \frac{1}{M} \sum_{m=1}^{M} (\hat{y}_m - \mu)^2
$$

MC dropout provides approximate Bayesian inference (Gal & Ghahramani, 2016) with minimal implementation effort — the only requirement is to keep dropout active during prediction. Typical practice uses $M = 50$–$100$ forward passes, increasing inference time by the same factor.

### 32.14.3 Ensemble Methods

Training an ensemble of $K$ models on bootstrapped subsets of the training data (or with different random initializations) provides a more robust uncertainty estimate:

$$
\mu(x) = \frac{1}{K} \sum_{k=1}^{K} f_{\theta_k}(x), \qquad \sigma^2(x) = \frac{1}{K} \sum_{k=1}^{K} \left( f_{\theta_k}(x) - \mu(x) \right)^2
$$

Deep ensembles (Lakshminarayanan et al., 2017) have been shown to outperform MC dropout in calibration and sharpness. The computational cost scales linearly with ensemble size, but ensemble members can be trained in parallel.

For process simulation surrogates, an ensemble of 5–10 models provides well-calibrated uncertainty estimates with manageable computational overhead. At inference time, all ensemble members are evaluated and the spread of predictions directly communicates model confidence.

### 32.14.4 Conformal Prediction

Conformal prediction (Angelopoulos & Bates, 2023) provides distribution-free prediction intervals with finite-sample coverage guarantees. Given a calibration dataset $\{(x_i, y_i)\}_{i=1}^{n}$ and a desired coverage level $1 - \alpha$:

1. Compute conformity scores: $s_i = |y_i - \hat{y}_i|$ for each calibration point
2. Compute the quantile: $q = \text{Quantile}(s_1, \ldots, s_n; \lceil(1-\alpha)(n+1)\rceil / n)$
3. Prediction interval: $C(x_{\text{new}}) = [\hat{y}_{\text{new}} - q, \, \hat{y}_{\text{new}} + q]$

The remarkable property of conformal prediction is that the coverage guarantee $\mathbb{P}(y_{\text{new}} \in C(x_{\text{new}})) \geq 1 - \alpha$ holds regardless of the model architecture, training procedure, or data distribution. The only assumption is exchangeability of the calibration and test data.

For production optimization surrogates, conformal prediction converts any point-prediction model into one that provides calibrated confidence intervals — a critical requirement for operator trust.

### 32.14.5 Bayesian Deep Learning

The most principled approach to UQ places distributions over network weights rather than using point estimates. The posterior distribution $p(\mathbf{w} | \mathcal{D})$ is computed via Bayes' theorem:

$$
p(\mathbf{w} | \mathcal{D}) = \frac{p(\mathcal{D} | \mathbf{w}) \, p(\mathbf{w})}{p(\mathcal{D})}
$$

Predictions marginalize over the posterior:

$$
p(y | x, \mathcal{D}) = \int p(y | x, \mathbf{w}) \, p(\mathbf{w} | \mathcal{D}) \, d\mathbf{w}
$$

Since exact inference is intractable for neural networks, approximate methods such as variational inference (learning a tractable approximation $q_\phi(\mathbf{w}) \approx p(\mathbf{w} | \mathcal{D})$) or Hamiltonian Monte Carlo (sampling from the posterior) are used. Bayesian neural networks provide the most theoretically grounded uncertainty estimates but at significant computational cost.

### 32.14.6 Embedding UQ in Optimization

Uncertainty-aware optimization uses the uncertainty estimates to make risk-informed decisions:

- **Expected value optimization**: $\min_x \mathbb{E}[f(x, w)]$ — optimize the average outcome under uncertainty
- **Robust optimization**: $\min_x \max_{w \in \mathcal{W}} f(x, w)$ — optimize the worst case within the uncertainty set
- **Chance-constrained optimization**: $\min_x f(x)$ subject to $\mathbb{P}(g(x, w) \leq 0) \geq 1 - \alpha$ — ensure constraints are satisfied with probability at least $1 - \alpha$

For production operations, the choice between these formulations depends on the consequence of constraint violation. Safety-critical constraints (pressure relief, flammability limits) warrant robust or high-probability chance-constrained treatment. Economic constraints (throughput targets) can tolerate expected-value optimization.

### 32.14.7 Communicating Uncertainty to Operators

The value of UQ depends on effective communication to human decision-makers. Practical approaches include:

- **Confidence intervals**: Display recommended set points with ±ranges (e.g., "Separator pressure: 75 ± 3 bar")
- **Traffic-light indicators**: Green (high confidence, well-explored region), yellow (moderate confidence, limited data), red (low confidence, extrapolation)
- **Probability of constraint violation**: "Probability of exceeding compressor power limit: 4.2%"
- **Scenario comparison**: Show optimistic, expected, and pessimistic outcomes side by side

Building trust in AI recommendations requires transparency about what the model knows and does not know. Operators are more likely to adopt AI guidance when uncertainty is honestly communicated.

---

## 32.15 Agentic AI and Natural Language Interfaces for Simulation

### 32.15.1 The Paradigm Shift

Traditional process simulation requires deep expertise in both the physical domain and the simulation software. An engineer must know which equation of state to select, how to configure equipment parameters, which solver settings to adjust, and how to interpret convergence diagnostics. This creates a significant barrier to entry and limits the pool of practitioners who can leverage simulation-based optimization.

Large language models (LLMs) are fundamentally changing this dynamic. When equipped with structured access to simulation tools, LLMs can translate natural-language questions into valid simulation configurations, execute them, interpret the results, and present recommendations in plain language. This shifts the interaction paradigm from "configure a simulation" to "ask a question."

### 32.15.2 Model Context Protocol (MCP)

The Model Context Protocol (MCP) provides a standardized interface between LLMs and external tools, including process simulators. The simulator exposes its capabilities as a set of *tools*, each with a structured schema describing inputs, outputs, and constraints:

```json
{
  "name": "runFlash",
  "description": "Run a thermodynamic flash calculation",
  "parameters": {
    "components": "Fluid composition as name:molefraction pairs",
    "temperature": {"type": "number", "unit": "C or K"},
    "pressure": {"type": "number", "unit": "bara, kPa, psi"},
    "eos": "Equation of state: SRK, PR, CPA, GERG2008",
    "flashType": "TP, PH, PS, dewPointT, bubblePointT"
  }
}
```

The LLM discovers available tools, understands their parameters from the schema descriptions, and constructs valid requests. A tool catalog might include:

- **Flash calculations**: TP-flash, dew/bubble point, phase envelope
- **Process simulation**: Build and run flowsheets from JSON specifications
- **Component search**: Find valid component names in the database
- **Property tables**: Generate temperature or pressure sweeps of fluid properties
- **Input validation**: Check parameters before execution

### 32.15.3 Validation Before Execution

A critical layer in the agentic architecture is input validation. Before any simulation runs, the validation tool checks:

- **Physical feasibility**: Temperature above absolute zero, pressure positive, compositions summing to unity
- **Component validity**: All component names exist in the thermodynamic database
- **EOS compatibility**: The selected equation of state supports the specified components
- **Equipment constraints**: Operating parameters within physically meaningful ranges

Validation returns structured error messages with remediation hints — not cryptic exception traces. For example: "Component 'methan' not found. Did you mean 'methane'? (edit distance: 1)."

### 32.15.4 Self-Healing Automation

Beyond validation, advanced simulation interfaces include self-healing capabilities:

- **Fuzzy name matching**: When equipment or variable names do not match exactly, the system computes edit distance and suggests corrections. Corrections are cached and reused, so the system learns from past mistakes.
- **Auto-correction**: Common errors (case sensitivity, whitespace, abbreviations) are automatically resolved without user intervention.
- **Physical bounds validation**: When setting simulation variables, the system checks whether the value falls within physically reasonable bounds (e.g., temperature between −273°C and 1000°C, efficiency between 0 and 1).
- **Operation tracking**: The system logs all operations, success/failure rates, and common error patterns, generating a learning report that helps developers improve the interface.

### 32.15.5 Workflow Example

Consider an operator investigating the effect of increasing first-stage separator pressure:

1. **Operator**: "What happens to gas export rate and compressor power if I increase HP separator pressure from 70 to 80 bar?"
2. **LLM agent**: Constructs a process simulation with the current operating conditions, runs two cases (70 bar and 80 bar), extracts the relevant outputs
3. **Validation**: Checks that the proposed pressure is within equipment MAWP and that the change does not trigger safety interlocks
4. **Execution**: Runs both simulations (~20 ms each)
5. **Interpretation**: "Increasing HP separator pressure from 70 to 80 bar reduces gas export rate by 2.3% (from 3.45 to 3.37 MSm³/d) and decreases compressor power by 8.7% (from 12.4 to 11.3 MW). The net effect is a reduction in specific energy consumption from 3.59 to 3.35 kWh/kSm³. The separator gas velocity drops from 88% to 81% of the Souders-Brown limit, providing additional margin."
6. **Recommendation**: "The trade-off favours the higher pressure when energy cost exceeds 0.15 NOK/kWh, which is the current case. Recommend trial at 78 bar (intermediate step) with monitoring of export dew point specification."

### 32.15.6 Implications for Production Optimization

Agentic AI interfaces have profound implications for production optimization:

- **Democratization**: Operations personnel without simulation expertise can explore what-if scenarios and receive quantitative answers. This extends the reach of simulation-based optimization beyond the process engineering team.
- **Speed**: A question that previously required hours of manual model setup, execution, and analysis can be answered in seconds.
- **Consistency**: The LLM agent applies the same rigorous methodology every time — proper flash initialization, mixing rule selection, property initialization — eliminating the variability of manual setups.
- **Autonomous optimization**: AI agents can be tasked with broad objectives ("find the operating point that maximizes production within all equipment limits") and autonomously explore the design space using iterative simulation.
- **Documentation**: Every interaction is logged, creating an audit trail of analysis queries, simulation inputs, and results. This supports regulatory compliance and knowledge management.

The combination of fast physics-based simulation, structured tool interfaces, and natural language understanding creates a new paradigm for production optimization — one where the barrier to entry is lowered without sacrificing rigor.

---

## 32.16 Computational Requirements for AI Training on Process Simulators

### 32.16.1 Feasibility of Direct Simulation for AI

A recurring question in applying AI to process optimization is whether first-principles simulators are fast enough for direct use in training loops. If each simulation evaluation takes minutes, generating the $10^4$–$10^7$ samples needed for modern AI methods becomes impractical. However, modern equation-of-state-based simulators achieve per-evaluation times in the millisecond range, fundamentally changing the cost-benefit analysis of surrogate models versus direct simulation.

### 32.16.2 Flash Calculation Scaling

The core thermodynamic operation — flash calculation — determines the computational floor for process simulation. Flash execution time scales approximately as:

$$
t_{\text{flash}} \propto n_c^2
$$

where $n_c$ is the number of components. The quadratic scaling arises from the mixing rule evaluation, which requires $n_c \times n_c$ binary interaction parameter lookups and combining rules. Benchmarks on a standard single-core CPU (warm JVM, steady-state conditions) yield:

| System | Components | Flash Time |
|--------|-----------|------------|
| Lean gas (methane, ethane, propane, CO₂, N₂) | 5 | ~1 ms |
| Natural gas (C₁–C₅, CO₂, N₂, H₂S, H₂O) | 9 | ~3 ms |
| Oil-gas-water (C₁–C₇+, CO₂, N₂, H₂O) | 13 | ~5 ms |

These timings include full phase stability analysis, phase split calculation, and property evaluation (density, enthalpy, entropy, fugacities).

### 32.16.3 Process Equipment Performance

Building on the flash calculation, individual equipment unit operations add execution time for mass/energy balance solving, iterative convergence (compressors, heat exchangers), and stream splitting/mixing:

| Operation | Typical Time |
|-----------|-------------|
| Single separator (2-phase) | ~0.6 ms |
| Three-phase separator | ~1.5 ms |
| Single-stage compressor | ~2 ms |
| Heat exchanger | ~1.5 ms |
| Two-stage separation | ~13 ms |
| Compression train (3 stages + cooling) | ~5 ms |
| Full process (2-stage sep + 3-stage comp + cooling) | ~20 ms |

The full-process time of ~20 ms includes all equipment evaluations, stream propagation, and convergence of any recycles. This establishes the computational cost per training sample for the broadest class of surrogate or RL training.

### 32.16.4 Training Data Generation Rates

Given the per-evaluation times, the wall-clock time for training data generation can be projected:

| Samples | Flash-only (~3 ms) | Full-process (~20 ms) |
|---------|--------------------|-----------------------|
| $10^3$ | ~3 seconds | ~20 seconds |
| $10^4$ | ~30 seconds | ~3.3 minutes |
| $10^5$ | ~5 minutes | ~33 minutes |
| $10^6$ | ~50 minutes | ~5.5 hours |

For physics-informed neural networks targeting flash calculation surrogates, $10^4$–$10^5$ training points are typically sufficient for accurate interpolation within the training domain. NeqSim generates these in seconds to minutes — fast enough for daily or even hourly surrogate retraining as operating conditions change.

### 32.16.5 Reinforcement Learning Training Budgets

RL algorithms require many environment interaction steps, but each step involves a single simulation evaluation plus lightweight gradient computation. At approximately 1.5 ms per step (including simulation and agent update), the achievable throughput is roughly 669 steps per second. Training budgets translate to:

| Steps | Wall-Clock Time |
|-------|----------------|
| $10^5$ (fast convergence) | ~2.5 minutes |
| $10^6$ (typical PPO/SAC) | ~25 minutes |
| $10^7$ (complex problems) | ~4.2 hours |

These timings demonstrate that RL with direct process simulation is practical for daily optimization cycles. An RL agent can be retrained overnight (or during shift changes) with the latest model calibration, then deployed for the next operating period.

### 32.16.6 Parallel and Batch Execution

Training data generation is embarrassingly parallel — each evaluation is independent. Thread-safe execution requires deep-copying the process system for each thread, ensuring no shared mutable state:

**Execution scope:** requires a declared training design and a calibrated chart-equipped base process.

```python pattern: requires a declared training design and a calibrated chart-equipped base process
import concurrent.futures
import copy

def evaluate_sample(base_process, sample):
    """Evaluate a single training sample using a deep copy of the process."""
    process = base_process.copy()
    # Apply sample parameters
    process.getUnit("Feed").setPressure(sample["sep_pressure"], "bara")
    process.getUnit("Compressor").setSpeed(sample["comp_speed"])
    process.run()
    return {
        "gas_rate": process.getUnit("Gas Export").getFlowRate("MSm3/day"),
        "power": process.getUnit("Compressor").getPower("MW"),
    }

# Execute the explicitly prepared sample list; independent Java copies per worker.
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(evaluate_sample, base_process, s) for s in samples]
    results = [f.result() for f in futures]
```

With 8 threads and 20 ms per evaluation, throughput increases from 50 to approximately 400 evaluations per second, generating $10^5$ samples in about 4 minutes.

### 32.16.7 Active Learning for Efficient Data Generation

Instead of uniformly sampling the input space, active learning focuses computational effort where it matters most:

1. **Initial phase**: Generate a small initial dataset ($\sim 10^3$ points) using Latin Hypercube Sampling
2. **Train initial surrogate**: Fit the model and compute uncertainty estimates (Section 32.14)
3. **Acquisition function**: Select the next batch of points where uncertainty is highest or where the surrogate predicts near-constraint boundaries
4. **Evaluate and retrain**: Run the simulator at the selected points, add to the training set, and retrain the surrogate
5. **Iterate**: Repeat until the surrogate meets accuracy requirements

Active learning typically achieves the same surrogate accuracy with 3–10× fewer training samples compared to uniform sampling. For computationally expensive simulations, this translates directly to reduced training time.

### 32.16.8 Dataset Size Guidelines

The required dataset size depends on the dimensionality of the problem, the complexity of the response surface, and the presence of discontinuities (phase boundaries):

| Application | Input Dimensions | Recommended Samples | Generation Time (NeqSim) |
|------------|-----------------|--------------------|-----------------------|
| Flash surrogate (lean gas) | 7 (T, P, 5 compositions) | $10^4$ | ~30 seconds |
| Flash surrogate (rich gas) | 11 (T, P, 9 compositions) | $5 \times 10^4$ | ~2.5 minutes |
| Equipment surrogate | 5–8 | $10^4$ | ~3 minutes |
| Full-process surrogate | 10–20 | $10^5$ | ~33 minutes |
| RL training environment | N/A (online) | $10^6$ steps | ~25 minutes |

These figures establish that modern process simulators are fast enough for direct integration with AI training workflows, challenging the assumption that surrogate pre-training is always necessary.

---

## Exercises

1. **Pareto Front**: Build a NeqSim process with a separator and compressor. Define two objectives: maximize gas production and minimize compressor power. Generate a Pareto front with at least 20 points and identify the knee point. Interpret the trade-off.

2. **SQP Optimization**: Use the `SQPoptimizer` to find the separator pressure and compressor outlet pressure that maximize production subject to: (a) compressor power ≤ 5 MW, (b) gas export dew point ≤ −5°C, (c) separator pressure between 30 and 120 bara.

3. **SciPy Integration**: Wrap a NeqSim process model in a `ProcessSimulationEvaluator` and solve the optimization problem from Exercise 2 using three different SciPy methods: L-BFGS-B, SLSQP, and differential evolution. Compare the results and computation times.

4. **Data Reconciliation**: Given the following measurements for a three-phase separator: feed = 100 t/hr (±2%), gas = 65 t/hr (±3%), oil = 28 t/hr (±5%), water = 9 t/hr (±10%). Reconcile these measurements and check for gross errors.

5. **Parameter Estimation**: Create a process model with a compressor. Add three data points with measured inlet/outlet temperatures and pressures. Use `BatchParameterEstimator` to estimate the polytropic efficiency. How does the estimated value compare to the assumed value?

6. **Batch Study**: Run a full factorial study over separator pressure (5 levels) and compressor outlet pressure (5 levels). Create contour plots of production rate and specific energy consumption. Identify the operating region that simultaneously achieves >90% of maximum production and <110% of minimum specific energy.

7. **Network Optimization**: Build a 3-well network model in Python. Optimize the choke settings to maximize total oil production. Add a gas handling constraint and observe how the optimal solution changes. Plot the Pareto front of oil production vs gas production.

8. **Gas Lift Allocation**: Three wells have the following gas lift performance curves. Given 200,000 Sm³/d of available lift gas, determine the optimal allocation. Verify the equal-slope condition. How does the allocation change if the total lift gas drops to 100,000 Sm³/d?

9. **Surrogate Optimization**: Build a 2D response surface for production rate as a function of separator pressure and compressor speed. Use a 25-point Latin Hypercube design, fit an RBF surrogate, and optimize the surrogate. Compare the surrogate optimum with the result from direct optimization.

10. **PINN for Flash Prediction**: Train a physics-informed neural network to predict gas fraction and density for a methane-ethane-propane mixture. Use 1,000 NeqSim flash evaluations as training data and embed the Rachford-Rice equation as a physics constraint. Compare the PINN's accuracy and speed against direct flash calculation on 10,000 test points. Evaluate: (a) interpolation accuracy (within training bounds), (b) extrapolation behaviour (10% beyond training bounds), and (c) mass conservation violation.

11. **RL for Separator-Compressor Optimization**: Formulate the separator pressure and compressor speed optimization as a reinforcement learning problem. Define the state space (3 measurements), action space (2 continuous variables), and a reward function that balances production rate against compressor power. Implement a simple policy gradient agent and train for 50,000 steps using NeqSim as the environment. Compare the RL solution with the SQP solution from Exercise 2. What are the advantages and disadvantages of each approach?

12. **Uncertainty Quantification**: Train an ensemble of 5 neural network surrogates for the flash calculation from Exercise 10. Compute prediction intervals using (a) ensemble spread and (b) conformal prediction with 90% coverage. Generate 500 test points and verify the empirical coverage of both methods. Which method produces tighter intervals while maintaining the coverage guarantee?

13. **Computational Scaling Study**: Measure the flash calculation time for systems with 3, 5, 7, 9, 11, and 15 components using NeqSim. Fit a power law $t = a \cdot n_c^b$ and determine the exponent $b$. Use the fitted model to estimate: (a) how many training samples can be generated in 1 hour for each system, (b) the feasibility of direct RL training ($10^6$ steps) for each system, and (c) the break-even point where surrogate pre-training becomes worthwhile.

---

## References

1. Miettinen, K. (1999). *Nonlinear Multiobjective Optimization*. Kluwer Academic Publishers.
2. Nocedal, J. & Wright, S.J. (2006). *Numerical Optimization*, 2nd Edition. Springer.
3. Biegler, L.T. (2010). *Nonlinear Programming: Concepts, Algorithms, and Applications to Chemical Processes*. SIAM.
4. Crowe, C.M. (1996). Data Reconciliation — Progress and Challenges. *Journal of Process Control*, 6(2-3), 89–98.
5. Narasimhan, S. & Jordache, C. (2000). *Data Reconciliation and Gross Error Detection*. Gulf Professional Publishing.
6. Kosmidis, V.D., Perkins, J.D., & Pistikopoulos, E.N. (2005). A Mixed Integer Optimization Formulation for the Well Scheduling Problem on Petroleum Fields. *Computers & Chemical Engineering*, 29(7), 1523–1541.
7. Bieker, H.P., Slupphaug, O., & Johansen, T.A. (2007). Real-Time Production Optimization of Oil and Gas Production Systems: A Technology Survey. *SPE Production & Operations*, 22(4), 382–391.
8. Conn, A.R., Scheinberg, K., & Vicente, L.N. (2009). *Introduction to Derivative-Free Optimization*. SIAM.
9. Raissi, M., Perdikaris, P. & Karniadakis, G.E. (2019). Physics-informed neural networks. *Journal of Computational Physics*, 378, 686–707.
10. Karniadakis, G.E., et al. (2021). Physics-informed machine learning. *Nature Reviews Physics*, 3, 422–440.
11. Lu, L., et al. (2021). Learning nonlinear operators via DeepONet. *Nature Machine Intelligence*, 3, 218–229.
12. Li, Z., et al. (2021). Fourier Neural Operator for parametric PDEs. *ICLR 2021*.
13. Schulman, J., et al. (2017). Proximal Policy Optimization Algorithms. *arXiv:1707.06347*.
14. Angelopoulos, A.N. & Bates, S. (2023). Conformal prediction: A gentle introduction. *Foundations and Trends in Machine Learning*, 16(4), 494–591.
15. Schweidtmann, A.M., et al. (2019). Deterministic global process optimization via neural networks. *Computers & Chemical Engineering*, 121, 67–84.
16. Towers, M., et al. (2023). Gymnasium. Farama Foundation.
17. Faria, R.R., et al. (2022). Where reinforcement learning meets process control. *Processes*, 10(11), 2311.


## Figures

![Figure 32.1: Pareto Front](figures/ch22_pareto_front.png)

*Figure 32.1: Pareto Front*

![Figure 32.2: Scenario Comparison](figures/ch22_scenario_comparison.png)

*Figure 32.2: Scenario Comparison*
