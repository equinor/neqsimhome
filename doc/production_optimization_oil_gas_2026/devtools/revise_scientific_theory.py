"""Scientific correction and accepted native gas-lift allocation fixture for Chapter 22."""
import json
import re
from pathlib import Path
BOOK=Path(__file__).resolve().parents[1]
p=next((BOOK/'chapters').glob('ch22_*/chapter.md'))
original=p.read_text(encoding='utf-8-sig')
backup=BOOK/'.build/backups/scientific_revision'/p.parent.name/'theory_input.md'
backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists(): backup.write_text(original,encoding='utf-8')
t=backup.read_text(encoding='utf-8')
changes=[]
def r(old,new):
    global t
    if old not in t: raise AssertionError(old[:140])
    t=t.replace(old,new); changes.append({'before':old,'after':new})

r('Chapter 18','Chapter 20')
r(r'f(x) = \frac{W_{\text{total}}(x)}{Q_{\text{oil}}(x) + Q_{\text{gas,export}}(x)} \quad [\text{kWh/Sm}^3]',r'E_{\mathrm{gas}}(x) = \frac{24 W_{\mathrm{total}}(x)}{Q_{\mathrm{gas,export}}(x)} \quad [\mathrm{kWh/Sm^3}]')
r('### 22.2.3 Decision Variables','Here power is in kW and export gas rate is in Sm³/day at a declared reference state. Minimize this quantity, or maximize its negative in the general formulation. Do not add oil and gas standard volumes without an explicitly defined equivalent-product basis.\n\n### 22.2.3 Decision Variables')
r('The choice of solution node affects the optimization.', 'Changing the solution node changes the bookkeeping and numerical conditioning, but a consistently converged physical model gives the same operating point.')
r('Newton\'s method has quadratic convergence near the optimum but requires computing (or approximating) the Hessian.', 'Newton\'s method has local quadratic convergence to a stationary point under a nonsingular Hessian and appropriate regularity/initialization; this alone does not establish a maximum.')
r('Approximate the Hessian iteratively from gradient information. The BFGS update:', 'For minimization define $F=-f$ when the original objective is maximized. Approximate the Hessian of $F$ (or of its Lagrangian for constrained SQP) with BFGS; positive definiteness requires a positive curvature denominator, often enforced by damping:')
r(r'$y_k = \nabla f(x_{k+1}) - \nabla f(x_k)$',r'$y_k = \nabla F(x_{k+1}) - \nabla F(x_k)$')
r(r'\frac{1}{2} d^T H_k d + \nabla f(x_k)^T d',r'\frac{1}{2} d^T H_k d + \nabla F(x_k)^T d')
r('SQP is the workhorse of constrained nonlinear optimization', 'Include linearized equality constraints and the variable bounds in each SQP subproblem. SQP is a widely used approach to constrained nonlinear optimization')
r('Derivative-free methods do not require gradient information and are robust for noisy, discontinuous, or black-box objective functions — common in process simulation.', 'Derivative-free methods avoid explicit derivatives. Noise and discontinuities can still corrupt comparisons and termination; select a method and evaluation precision suited to the model.')
r('The algorithm does not compute derivatives and handles noisy objective functions well. However, it is a local method and may converge to a local optimum.', 'Nelder–Mead is a local search heuristic; ordinary implementations have no general convergence guarantee, especially for noisy or discontinuous simulations. Independently evaluate the returned point and compare starts.')
r('Convergence is guaranteed under mild conditions.', 'Stationarity results require specific polling, regularity and sufficient-decrease assumptions; arbitrary noisy black-box evaluations do not satisfy them automatically.')
r('Low ($O(n^2)$ per iteration)', 'Usually 1–2 new evaluations; up to $n$ additional evaluations for shrinkage')
r('The **expected improvement** (EI) acquisition function balances exploitation', 'For a minimization objective, the **expected improvement** (EI) acquisition function balances exploitation')
r('where $\\hat{f}(x)$ is the surrogate prediction,', 'For a maximization objective reverse the improvement sign. At zero predictive standard deviation use the limiting positive improvement rather than dividing by zero. Here $\\hat{f}(x)$ is the surrogate prediction,')
r('For production optimization, a typical RSM workflow would use a Central Composite Design (CCD) or Box-Behnken design, requiring $2^n + 2n + 1$ simulation runs (e.g., 27 runs for 3 variables).', 'A full-factorial central composite design with one center point uses $2^n+2n+1$ runs: 15 for three variables. Replicated center points add runs; a Box–Behnken design has a different construction. Verify full rank and use independent validation points beyond the minimum coefficient count.')
r('The objective is typically to maximize the oil production rate (equivalently, minimize the total gas flashed) or maximize the stock tank oil API gravity.', 'Specify the objective as stabilized oil mass, stock-tank volume or economic value. Minimizing gas mass can be equivalent to maximizing retained hydrocarbon mass on a fixed-feed basis, but maximizing oil standard volume or API gravity is a different objective.')
r(r'\right)^{1/N}',r'\right)^{1/(N-1)}')
r('$N$ is the number of stages,', '$N$ is the number of pressure levels including the first separator and stock tank,')
r('Process simulation with optimization finds the true optimum.', 'Simulation evaluates the chosen physical model; a search must still demonstrate feasibility, resolution and its local or global scope.')
r('Light fluids (high GOR) tend to have lower optimal pressures, while heavier fluids have higher optimal pressures.', 'The direction of the optimum-pressure shift must be evaluated for the actual composition, heavy-end characterization and product basis; GOR alone is insufficient.')
r('The optimum occurs where the marginal oil revenue equals the marginal gas lift cost:', 'At a differentiable interior optimum, marginal oil revenue equals marginal lift-gas cost; at a bound the corresponding KKT inequality applies:')
r('where $\\lambda$ is the Lagrange multiplier associated with the total gas lift constraint.', 'Here the equal-slope relation applies to wells strictly inside their allocation bounds when the shared budget is active. Wells at a bound satisfy inequalities. Concavity and separability make these KKT conditions sufficient; interacting wells require a coupled network solve.')
r('### 22.6.4 NeqSim Gas Lift Performance Curve', '### 22.6.4 Checked NeqSim Gas-Lift Allocation\n\nThe current native curve and network allocator solve a bounded empirical response problem. Coefficients below are assumed classroom inputs, not a simulated tubing response or field calibration. The code checks the gas budget, per-well bounds, independently recomputed oil objective and interior marginal slopes, then compares with an exhaustive allocation grid \\cite{neqsim2026update}.')
start=t.index('```python',t.index('### 22.6.4'))
end=t.index('\n```',start)+4
code='''```python
import numpy as np
import jpype
jneqsim = jpype.JPackage("neqsim")
Curve = jneqsim.process.fielddevelopment.integrated.GasLiftPerformanceCurve
Allocator = jneqsim.process.fielddevelopment.integrated.GasLiftNetworkOptimizer
# Sm3/day for both phase rates; a multiplies sqrt(lift rate), b is a rate ratio.
parameters = {"A": (800.0, 3.0, 0.002),
              "B": (500.0, 4.5, 0.004),
              "C": (1200.0, 2.0, 0.0015)}
curves = {name: Curve(base, a, b, 200000.0)
          for name, (base, a, b) in parameters.items()}
allocator = Allocator()
for name, curve in curves.items():
    allocator.addWell(name, curve)
budget = 150000.0
allocation = allocator.allocate(budget)
rates = {name: float(allocation.getLiftRates().get(name)) for name in curves}
assert all(0.0 < q < 200000.0 for q in rates.values())
assert abs(sum(rates.values()) - budget) < 0.1
def oil(name, q):
    base, a, b = parameters[name]
    return base + a*np.sqrt(q) - b*q
replayed_oil = sum(oil(name, q) for name, q in rates.items())
assert abs(replayed_oil - allocation.getTotalOil()) < 1e-6
slopes = [parameters[name][1]/(2*np.sqrt(q)) - parameters[name][2]
          for name, q in rates.items()]
assert max(slopes)-min(slopes) < 1e-7
# Independent 1,000 Sm3/day grid; unused gas is allowed through qC <= remainder.
# All three curves have positive slope over this budget, so an optimum uses it all.
grid_best = -np.inf
for qA in np.arange(0.0, budget+1.0, 1000.0):
    for qB in np.arange(0.0, budget-qA+1.0, 1000.0):
        qC = budget-qA-qB
        grid_best = max(grid_best, oil("A",qA)+oil("B",qB)+oil("C",qC))
assert replayed_oil >= grid_best-1e-5
assert replayed_oil-grid_best < 1.0  # grid-resolution check, Sm3/day oil
print("Accepted lift allocation (Sm3/day):", rates)
print(f"Oil {replayed_oil:.3f} Sm3/day; grid {grid_best:.3f} Sm3/day")
```
'''
t=t[:start]+code+t[end:]
changes.append({'topic':'Replaced unevaluated fluid and invented gas-lift boost with native allocation, KKT and exhaustive-grid checks'})
r('![Gas lift performance curves for three wells showing diminishing returns]', '![Conceptual gas-lift performance curves; the checked native allocation uses the explicitly stated empirical coefficients]')
r('By varying $\\epsilon_k$, the entire Pareto front (including non-convex regions) can be traced.', 'A sufficiently resolved epsilon sweep with globally solved subproblems can reach unsupported non-convex portions. A finite sampled sweep is an approximation; remove dominated points and report resolution.')
r(r'R = \frac{1}{N} \sum_{i=1}^{N} \left(\frac{y_i - \bar{y}}{\sigma_y}\right)^2',r'R = \frac{\sum_{i=2}^{N}(y_i-y_{i-1})^2}{2\sum_{i=1}^{N}(y_i-\bar y)^2}')
r('If $R$ is below a threshold (typically 1.0–2.0), the process is considered at steady state.', 'This is the successive-difference variance divided by the ordinary sample variance, as implemented in the current NeqSim detector. Independent stationary noise gives a ratio near one; a smooth drift can give a small ratio. A constant window is a special zero-variance case. Combine calibrated ratio, variance and slope limits; the ratio alone is not proof of steady state. The alternative expression using a window\'s own standardized squared deviations is essentially constant and cannot detect a trend.')
r('Acceptable MPE is typically < 5% for flow rates and < 2% for temperatures and pressures.', 'Choose tolerances from measurement uncertainty and decision sensitivity. Relative errors require a nonzero physically meaningful reference; percent error in degrees Celsius is not invariant to temperature scale. Use kelvin differences or an explicit temperature tolerance.')
r('This prevents oscillation and ensures the plant transitions smoothly to the new optimum.', 'Move limits reduce the size of each requested change but do not prove closed-loop stability or a safe transient path.')
r('Typical RTO benefits in offshore production are 2–5% increase in oil production or 3–8% reduction in energy consumption. For a platform producing 50,000 bbl/day, a 3% improvement at $70/bbl is approximately $105,000 per day — easily justifying the investment.', 'For an assumed 50,000 bbl/day platform, a hypothetical 3% uplift at 70 USD/bbl is 105,000 USD/day gross revenue. No such uplift is validated by this calculation. Use a matched baseline and account for uncertainty, transition losses and incremental costs before claiming net RTO benefit.')
r('This **minimax** (or worst-case) formulation ensures the solution is feasible and performs adequately even under the worst-case realization of uncertainty.', 'The worst-case objective alone does not enforce feasibility. Add $g_i(x,\\xi)\\le0$ and $h_j(x,\\xi)=0$ for every $\\xi\\in\\Xi$ and retain the variable bounds. Finite scenario checks establish only scenario feasibility unless a separate argument covers the full uncertainty set.')
r('This allows the optimizer to take calculated risks where the potential upside justifies occasional constraint violations.', 'Use chance constraints only for quantities whose allowable violation probability has an explicit decision basis. They do not authorize violation of hard mechanical or safety limits. State whether confidence is individual or joint and quantify finite-sample uncertainty.')
r(r'\text{CVaR}_\beta(x) = \frac{1}{1-\beta} \int_\beta^1 q_\alpha(f(x, \xi)) \, d\alpha',r'\operatorname{CVaR}_\beta(L)=\min_\eta\left\{\eta+\frac{\mathbb E[(L-\eta)_+]}{1-\beta}\right\},\qquad L=-f(x,\xi)')
r('where $q_\\alpha$ is the $\\alpha$-quantile of the objective function distribution. CVaR provides a more conservative objective than the mean but is less extreme than the worst case, making it a popular choice for practical robust optimization.', 'Minimize this upper-tail loss measure, or equivalently maximize the lower-tail reward. Maximizing the upper tail of production would favor good outcomes and is not a conservative objective. The auxiliary threshold formulation also handles distributions with atoms \\cite{rockafellar2000cvar}.')
r('| Approach | Description | Accuracy | Speed |', '| Approach | Description | Coupling error | Computational character |')
r('| Sequential | Run reservoir → well → facility in sequence | Low (no feedback) | Fast |', '| Sequential | One upstream-to-downstream pass | Feedback mismatch may remain | One pass |')
r('| Iterative | Iterate between models until convergence | Medium | Medium |', '| Iterative | Iterate models to a declared residual | Controlled by convergence tolerance | Multiple model runs |')
r('| Fully coupled | Solve all models simultaneously | High | Slow |', '| Fully coupled | Solve the assembled equations | Controlled by solver tolerance | Depends on system size and conditioning |')
r('even 10,000 evaluations complete in minutes.', '10,000 serial evaluations require about 17 minutes to 2.8 hours before overhead.')
r('**Barrier method:** Add a barrier that prevents the optimizer from approaching constraint boundaries:', '**Barrier method:** For positive $\\mu_i$ and strictly feasible $g_i<0$, the following reciprocal barrier tends to minus infinity at a constraint boundary. Its parameter sequence controls how closely a maximizer approaches an active limit:')
r('### 22.12.2 Common Pitfalls', '### 22.12.5 Common Pitfalls')
r('### 22.12.3 Software Tools for Production Optimization', '### 22.12.6 Software Tools for Production Optimization')
# Add conservation to the literal multi-stage separation calculation.
r('    oil_rate = st_sep.getLiquidOutStream().getFlowRate("kg/hr")\n    return oil_rate', '''    outlets = [hp_sep.getGasOutStream(), hp_sep.getWaterOutStream(),
               lp_sep.getGasOutStream(), st_sep.getGasOutStream(),
               st_sep.getLiquidOutStream()]
    mass_out = sum(float(s.getFlowRate("kg/hr")) for s in outlets)
    assert abs(mass_out-feed.getFlowRate("kg/hr"))/200000.0 < 1e-8
    h_out = sum(float(s.getFluid().getEnthalpy()) for s in outlets)
    h_in = float(feed.getFluid().getEnthalpy())
    assert abs(h_out-h_in)/max(abs(h_in), 1.0) < 1e-6
    oil_rate = float(st_sep.getLiquidOutStream().getFlowRate("kg/hr"))
    assert 0.0 < oil_rate < 200000.0
    return oil_rate''')
# Explicitly select polytropic mode and verify compressor mass/energy in the single-stage function.
r('    comp.setPolytropicEfficiency(0.78)\n', '    comp.setPolytropicEfficiency(0.78)\n    comp.setUsePolytropicCalc(True)\n')
r('    return comp.getPower() / 1e6  # MW', '''    assert abs(comp.getOutletStream().getFlowRate("kg/hr")
               - feed.getFlowRate("kg/hr"))/feed.getFlowRate("kg/hr") < 1e-10
    dh = comp.getOutletStream().getFluid().getEnthalpy()-feed.getFluid().getEnthalpy()
    assert abs(dh-comp.getPower())/max(abs(comp.getPower()),1.0) < 1e-5
    assert comp.getPower() > 0.0
    return comp.getPower() / 1e6  # MW''')
r('print("\\nLower suction pressure → more oil production but more power.")\nprint("Optimal is where marginal oil value = marginal power cost.")', 'print("\\nThis fixed-rate sweep quantifies compression power only.")\nprint("A coupled well/separator model is needed to establish any production benefit.")')
r('The theoretical optimum for equal-efficiency stages is the geometric mean of the suction and discharge pressures.', 'The equal-ratio optimum assumes equal inlet temperatures, equal efficiencies, constant gas properties and negligible intercooler pressure loss. The geometric mean is therefore a reference estimate; this example has unequal inlet temperatures and efficiencies.')
markers=lambda x: re.findall(r'<!-- reviewed-notebook-results:start -->.*?<!-- reviewed-notebook-results:end -->',x,re.S)
assert markers(t)==markers(original)
p.write_text(t,encoding='utf-8')
(BOOK/'verification/scientific_revision/theory_corrections.json').write_text(json.dumps(changes,indent=2,ensure_ascii=False),encoding='utf-8')
print(f'Applied {len(changes)} scientific corrections')
