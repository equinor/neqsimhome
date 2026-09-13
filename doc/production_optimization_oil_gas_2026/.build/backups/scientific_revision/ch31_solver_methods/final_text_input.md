# Numerical Methods and Solver Convergence

<!-- Chapter metadata -->
<!-- Notebooks: ch29_flash_convergence.ipynb, ch29_recycle_diagnostics.ipynb, ch29_solver_benchmarks.ipynb -->
<!-- Estimated pages: 42 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Describe the Rachford–Rice flash calculation algorithm, including successive substitution and Newton's method for solving the isothermal flash, and explain the convergence criteria used in NeqSim's `TPflash`, `PHflash`, and `PSflash` solvers
2. Explain how cubic equations of state (SRK, Peng–Robinson) yield multiple compressibility-factor roots, and describe the root-selection logic and volume-translation corrections applied in NeqSim
3. Characterize the sequential modular approach to process simulation, including stream tearing for recycle loops, and apply convergence acceleration methods (Wegstein, Broyden) to improve convergence speed
4. Configure the NeqSim `Recycle` class for recycle loop convergence, select appropriate tolerance and damping parameters, and diagnose non-convergence using the `ConvergenceDiagnostics` API
5. Set up and troubleshoot `Adjuster` specifications that interact with recycle loops, and understand the secant method used for adjuster convergence
6. Explain the inside-out, bubble-point, and Newton tray-by-tray distillation column solvers in NeqSim, interpret solver metrics (mass residual, energy residual, iteration count), and select the appropriate solver for a given separation problem

---

## 31.1 Introduction

Every optimization calculation described in the preceding chapters — from flash equilibrium in Chapter 2 to multi-scenario production optimization in Chapter 28 — ultimately depends on the convergence of numerical algorithms. The optimizer calls the process simulator thousands of times during a search; if any single call fails to converge, the optimization stalls or returns an incorrect result. Understanding the numerical methods inside the simulator is therefore essential for any engineer who uses simulation-based optimization.

This chapter examines the numerical methods that form the computational engine of NeqSim and, more broadly, of all equation-of-state process simulators. We proceed from the innermost calculation — the thermodynamic flash — outward through the process simulation layers:

1. **Flash calculations** (Sections 31.2–31.3): Solving phase equilibrium for a given feed at specified conditions
2. **Sequential modular solution** (Sections 31.4–31.5): Solving the equipment network by propagating streams through units, with recycle convergence for closed loops
3. **Specification convergence** (Section 31.6): Using adjusters to meet target specifications
4. **Distillation columns** (Section 31.7): Multi-stage vapor-liquid equilibrium with reflux and reboil
5. **Dynamic simulation** (Section 31.8): Time integration for transient behavior

Each section explains the algorithm, derives the key equations, describes NeqSim's implementation, and provides guidance on convergence troubleshooting. The goal is not to turn the production engineer into a numerical analyst, but to provide sufficient understanding to diagnose convergence failures, select appropriate solver parameters, and know when to seek expert help.

---

## 31.2 Flash Calculation Algorithms

The **flash calculation** is the most fundamental computation in process simulation. Given a feed of known composition $z_i$ ($i = 1, \ldots, C$ components) at specified conditions (typically temperature $T$ and pressure $P$), the flash determines:

- How many phases are present
- The mole fraction of each phase ($\beta$ for vapor, $1 - \beta$ for liquid in a two-phase flash)
- The composition of each phase ($y_i$ for vapor, $x_i$ for liquid)

The flash is called hundreds of times per process simulation — for every stream, every equipment unit outlet, every iteration of a recycle loop. Its speed and reliability are therefore critical.

### 31.2.1 The Rachford–Rice Equation

For a two-phase vapor-liquid flash at specified $T$ and $P$, the equilibrium is governed by the K-values:

$$
K_i = \frac{y_i}{x_i} = \frac{\phi_i^L(T, P, x)}{\phi_i^V(T, P, y)}
$$

where $\phi_i^L$ and $\phi_i^V$ are the fugacity coefficients of component $i$ in the liquid and vapor phases, computed from the equation of state.

Given the K-values, the material balance and equilibrium conditions can be combined into the **Rachford–Rice equation**:

$$
h(\beta) = \sum_{i=1}^{C} \frac{z_i (K_i - 1)}{1 + \beta(K_i - 1)} = 0
$$

where $\beta$ is the vapor fraction (moles of vapor divided by total moles). This is a single nonlinear equation in one unknown ($\beta$), with the constraint $0 \leq \beta \leq 1$ for a two-phase solution.

The phase compositions are recovered from $\beta$ and the K-values:

$$
x_i = \frac{z_i}{1 + \beta(K_i - 1)}, \quad y_i = K_i x_i
$$

### 31.2.2 Successive Substitution

The simplest algorithm for solving the flash is **successive substitution** (SS):

1. Estimate initial K-values (Wilson correlation):
$$
K_i^{(0)} = \frac{P_{c,i}}{P} \exp\left[ 5.373(1 + \omega_i)\left(1 - \frac{T_{c,i}}{T}\right) \right]
$$
2. Check $h(0)$ and $h(1)$ for a physical two-phase bracket, then solve for $\beta$ with a safeguarded method. A boundary phase state requires stability assessment rather than forcing an interior root.
3. Compute phase compositions $x_i$, $y_i$ from $\beta$ and $K_i$
4. Evaluate fugacity coefficients $\phi_i^L(T, P, x)$ and $\phi_i^V(T, P, y)$ from the EOS
5. Update K-values:
$$
K_i^{(n+1)} = \frac{\phi_i^L(T, P, x^{(n)})}{\phi_i^V(T, P, y^{(n)})}
$$
6. Check convergence: $\sum_i (K_i^{(n+1)} - K_i^{(n)})^2 < \epsilon$
7. If not converged, return to step 2

Successive substitution is robust and reliable far from the critical point. However, it converges only linearly — each iteration reduces the error by a constant factor. Near the critical point, where the K-values approach unity ($K_i \to 1$), the convergence factor approaches 1 and the algorithm stalls.

### 31.2.3 Newton's Method for Flash

For faster convergence, NeqSim uses **Newton's method** applied to the full set of equilibrium equations. The unknown vector is $\mathbf{u} = (\ln K_1, \ln K_2, \ldots, \ln K_C, \beta)$ and the equation system is:

$$
F_i(\mathbf{u}) = \ln K_i + \ln \phi_i^V(T, P, y) - \ln \phi_i^L(T, P, x) = 0, \quad i = 1, \ldots, C
$$

$$
F_{C+1}(\mathbf{u}) = \sum_{i=1}^{C} \frac{z_i(K_i - 1)}{1 + \beta(K_i - 1)} = 0
$$

Newton's method iterates:

$$
\mathbf{u}^{(n+1)} = \mathbf{u}^{(n)} - \mathbf{J}^{-1} \mathbf{F}(\mathbf{u}^{(n)})
$$

where $\mathbf{J}$ is the Jacobian matrix $\partial F_i / \partial u_j$. The Jacobian requires derivatives of the fugacity coefficients with respect to composition, which are computed analytically from the EOS.

Near a nonsingular smooth root, exact Newton steps converge quadratically. Singular critical-point equations, damping, finite precision and phase changes can reduce that rate. This makes it much faster than successive substitution near the solution, but it requires a good initial guess to avoid divergence. The pinned implementation uses successive-substitution and derivative-based paths with safeguards; the switching criteria depend on the solver and state. The equations above explain the mathematical methods, not a universal fixed 3–5-iteration schedule.

### 31.2.4 Multi-Phase Flash

When more than two phases may be present (e.g., vapor-liquid-liquid equilibrium for water-hydrocarbon systems), the flash becomes more complex. The Rachford–Rice equation generalizes to multiple phases:

$$
h_j(\boldsymbol{\beta}) = \sum_{i=1}^{C} \frac{z_i (K_{ij} - 1)}{1 + \sum_{k=1}^{\Pi-1} \beta_k (K_{ik} - 1)} = 0, \quad j = 1, \ldots, \Pi - 1
$$

where $\Pi$ is the number of phases and $K_{ij} = \phi_i^{\text{ref}} / \phi_i^j$ are the K-values relative to a reference phase.

NeqSim handles multi-phase flash by first performing a stability analysis (Section 31.2.5) to determine the number of phases, then solving the multi-phase Rachford–Rice system. The `setMultiPhaseCheck(True)` flag on the fluid system enables this capability.

### 31.2.5 Stability Analysis

Before performing a flash, it is necessary to determine whether the feed is stable as a single phase or will split into multiple phases. The **tangent plane distance** (TPD) criterion provides this test:

$$
\text{TPD}(\mathbf{w}) = \sum_{i=1}^{C} w_i \left[ \ln w_i + \ln \phi_i(\mathbf{w}) - \ln z_i - \ln \phi_i(\mathbf{z}) \right]
$$

If $\text{TPD}(\mathbf{w}) < 0$ for any trial composition $\mathbf{w}$, the single phase is unstable and the feed will split. The stability analysis searches for the global minimum of TPD, which is a challenging global optimization problem. NeqSim uses multiple initial guesses (pure components, Wilson K-value estimates) to increase the probability of finding all unstable phases.

### 31.2.6 NeqSim Flash Solvers

NeqSim provides several flash specifications, each solving for different pairs of state variables:

| Flash Type | Specified Variables | Unknown | Primary Use |
|-----------|-------------------|---------|-------------|
| `TPflash` | Temperature, Pressure | Phase split, compositions | Standard flash |
| `PHflash` | Pressure, Enthalpy | Temperature, phase split | Adiabatic operations |
| `PSflash` | Pressure, Entropy | Temperature, phase split | Isentropic operations |
| `TVflash` | Temperature, Volume | Pressure, phase split | Fixed-volume systems |

The `PHflash` and `PSflash` are nested calculations: an outer loop iterates on temperature until the enthalpy or entropy matches the target, with a `TPflash` at each trial temperature. The current `PHflash` includes heat-capacity derivative corrections and safeguarded temperature updates, with a second-order option. The precise algorithm is specification- and path-dependent; check target enthalpy/entropy independently after the solve.

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
ThermodynamicOperations = jneqsim.thermodynamicoperations.ThermodynamicOperations

# Create a gas condensate fluid
fluid = SystemSrkEos(273.15 + 25.0, 100.0)
fluid.addComponent("methane", 0.80)
fluid.addComponent("ethane", 0.07)
fluid.addComponent("propane", 0.04)
fluid.addComponent("nC5", 0.03)
fluid.addComponent("nC10", 0.04)
fluid.addComponent("CO2", 0.02)
fluid.setMixingRule("classic")

# TP flash — the fundamental calculation
ops = ThermodynamicOperations(fluid)
ops.TPflash()
fluid.initProperties()

print("TP Flash at 25°C, 100 bara:")
print(f"  Vapor fraction: {fluid.getBeta():.4f}")
print(f"  Number of phases: {fluid.getNumberOfPhases()}")
print(f"  Gas density: {fluid.getPhase('gas').getDensity('kg/m3'):.2f} kg/m³")
print(f"  Liquid density: {fluid.getPhase('oil').getDensity('kg/m3'):.2f} kg/m³")

# Independent phase and component checks at the TP solution.
import numpy as np
def phase_checks(system):
    z=np.array(system.getMolarComposition(),dtype=float)
    reconstructed=np.zeros(len(z))
    for phase_index in range(system.getNumberOfPhases()):
        phase=system.getPhase(phase_index)
        x=np.array([phase.getComponent(i).getx() for i in range(len(z))])
        assert abs(x.sum()-1)<1e-8 and np.all(x>=0)
        reconstructed += float(system.getBeta(phase_index))*x
    assert np.max(np.abs(z-reconstructed))<1e-7
    if system.getNumberOfPhases()==2:
        for i in range(len(z)):
            fugacity_terms=[float(system.getPhase(j).getComponent(i).getx()*
                system.getPhase(j).getComponent(i).getFugacityCoefficient())
                for j in range(2)]
            if min(fugacity_terms)>1e-12:
                assert abs(np.log(fugacity_terms[0]/fugacity_terms[1]))<1e-5
phase_checks(fluid)

# PH flash — for adiabatic mixing or expansion
target_enthalpy = fluid.getEnthalpy("J/mol")
fluid.setPressure(50.0, "bara")  # Pressure drop
ops.PHflash(target_enthalpy, "J/mol")
fluid.initProperties()

print(f"\nPH Flash at 50 bara (isenthalpic):")
print(f"  Temperature: {fluid.getTemperature('C'):.2f} °C")
print(f"  Vapor fraction: {fluid.getBeta():.4f}")

phase_checks(fluid)
enthalpy_residual=abs(float(fluid.getEnthalpy('J/mol'))-target_enthalpy)
assert enthalpy_residual/max(abs(target_enthalpy),1.0)<1e-7
assert fluid.getPressure('bara')==50.0
print('Accepted PH relative enthalpy residual',enthalpy_residual/max(abs(target_enthalpy),1.0))
```

### 31.2.7 Convergence Criteria

Declare acceptance criteria explicitly: normalized component balances, phase composition sums, fugacity equality for non-negligible components, and the specified enthalpy/entropy residual. Internal stopping tolerances differ by solver path and are not a universal promise of 8–10 significant digits. Numerical residual accuracy also does not establish EOS accuracy against measurements. The separate benchmark notebook supplies independent property comparisons; report both errors.

---

## 31.3 Equation of State Root Finding

### 31.3.1 The Cubic EOS

The Soave–Redlich–Kwong (SRK) and Peng–Robinson (PR) equations of state can be written in the general cubic form:

$$
P = \frac{RT}{V - b} - \frac{a(T)}{(V + \epsilon b)(V + \sigma b)}
$$

where $a(T)$ is the attraction parameter (temperature-dependent), $b$ is the co-volume parameter, and $(\epsilon, \sigma)$ are constants specific to the EOS: $(0, 1)$ for SRK and $(1 - \sqrt{2}, 1 + \sqrt{2})$ for PR.

Here $V$ in the EOS is molar volume, so the compressibility factor is $Z = PV/(RT)$:

$$
Z^3 + c_2 Z^2 + c_1 Z + c_0 = 0
$$

where the coefficients $c_0, c_1, c_2$ depend on the reduced attraction and co-volume parameters:

$$
A = \frac{a P}{R^2 T^2}, \quad B = \frac{bP}{RT}
$$

### 31.3.2 Multiple Roots and Root Selection

For a fixed composition and temperature/pressure, the cubic can have one or three real roots. Where three admissible roots exist, the smallest real root corresponds to the liquid compressibility factor $Z^L$, the largest to the vapor compressibility factor $Z^V$, and the intermediate root is unphysical (thermodynamically unstable).

The root-finding algorithm must:

1. Solve the cubic analytically (Cardano's formula) or numerically (companion matrix eigenvalues)
2. Identify the physical roots (reject negative $Z$ and $Z < B$)
3. Select the correct root for each phase based on the Gibbs energy criterion:
$$
G_{\text{res}} = nRT \left[ (Z - 1) - \ln(Z - B) - \frac{A}{(\sigma - \epsilon)B} \ln \frac{Z + \sigma B}{Z + \epsilon B} \right]
$$
The phase with the lower molar Gibbs energy is the stable phase.

Root multiplicity is not equivalent to mixture phase stability. A metastable cubic root can exist even when the equilibrium system is single phase; mixture phase splitting requires composition-dependent fugacities and stability analysis. NeqSim’s EOS phase solver uses numerical volume/root logic, so do not infer its implementation from Cardano’s formula alone.

### 31.3.3 Volume Translation

Cubic equations of state are known to predict liquid densities with systematic errors of 5–15%. **Volume translation** corrects this by shifting the molar volume:

$$
V_{\text{corrected}} = V_{\text{EOS}} - c
$$

where $c$ is the volume shift parameter, typically fitted to match the saturated liquid density at a reference temperature. The Peneloux correction for SRK uses:

$$
c_i = 0.40768 \frac{RT_{c,i}}{P_{c,i}} (0.29441 - Z_{RA,i})
$$

where $Z_{RA}$ is the Rackett compressibility factor. A thermodynamically consistent, composition-linear constant Péneloux translation can preserve phase equilibrium while changing volumes. Temperature-dependent or other translation formulations require consistent property derivatives; the statement is not universal for every density correction.

### 31.3.4 Near-Critical Root Finding

Near the critical point, the three roots of the cubic merge and root identification becomes numerically delicate. The algorithm may select the wrong root, leading to a density jump or a failed flash. Use phase stability, finite physical volumes and continuity checks near critical conditions. The current EOS implementation uses ordinary double precision; no arbitrary-precision root-solving guarantee is made. Density continuity can help diagnose a branch switch, but must not suppress a genuine phase transition.

---

## 31.4 Sequential Modular Approach

### 31.4.1 The Sequential Modular Concept

NeqSim uses the **sequential modular** (SM) approach to solve process flowsheets. In this approach, each equipment unit is solved independently as a module: given the inlet stream(s), the module computes the outlet stream(s). The modules are executed in sequence, following the material flow from feed to products.

For a topologically ordered acyclic flowsheet with no implicit specification feedback and independently converged equipment, one process pass can suffice — each module receives its final inlet streams on the first execution. The `ProcessSystem.run()` method simply iterates through the equipment list in order:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
Compressor = jneqsim.process.equipment.compressor.Compressor
Cooler = jneqsim.process.equipment.heatexchanger.Cooler
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# Acyclic flowsheet — converges in one pass
fluid = SystemSrkEos(273.15 + 80.0, 60.0)
fluid.addComponent("methane", 0.85)
fluid.addComponent("ethane", 0.10)
fluid.addComponent("propane", 0.05)
fluid.setMixingRule("classic")

feed = Stream("feed", fluid)
feed.setFlowRate(50000.0, "kg/hr")

sep = Separator("HP separator", feed)
comp = Compressor("compressor", sep.getGasOutStream())
comp.setOutletPressure(120.0, "bara")
cooler = Cooler("aftercooler", comp.getOutletStream())
cooler.setOutTemperature(273.15 + 35.0)

process = ProcessSystem()
process.add(feed)
process.add(sep)
process.add(comp)
process.add(cooler)
process.run()

print(f"Compressor power: {comp.getPower('kW'):.1f} kW")
print(f"Cooler duty: {cooler.getDuty() / 1000:.1f} kW")
print(f"Outlet temperature: {cooler.getOutletStream().getTemperature('C'):.1f} °C")
```

### 31.4.2 Stream Tearing for Recycle Loops

When the flowsheet contains a recycle — a stream that loops back from a downstream unit to an upstream unit — the sequential modular approach requires iteration. The recycle stream must be "torn" (assigned an initial guess) to break the circular dependency, and the flowsheet must be solved repeatedly until the torn stream converges.

The tearing and convergence strategy is:

1. **Identify recycle streams**: The user specifies which streams are recycles
2. **Initialize the torn stream**: Estimate composition, temperature, pressure, and flow rate
3. **Execute the flowsheet**: Run all modules in sequence
4. **Compare**: Check if the computed recycle stream matches the assumed (torn) values
5. **Update the torn stream**: Apply a convergence acceleration method
6. **Repeat** until the difference falls below the tolerance

### 31.4.3 Convergence Acceleration

**Direct substitution** is the simplest update rule: set the next guess equal to the computed value. This is equivalent to successive substitution and converges linearly — slowly for tight recycles.

**Wegstein acceleration** improves convergence by extrapolating:

$$
x^{(n+1)} = x^{(n)} + \frac{1}{1 - q} \left[ g(x^{(n)}) - x^{(n)} \right]
$$

where $g(x)$ is the function that maps the assumed recycle to the computed recycle, and $q$ is the Wegstein acceleration parameter:

$$
q = \frac{g(x^{(n)}) - g(x^{(n-1)})}{x^{(n)} - x^{(n-1)}}
$$

Here $q$ is the secant slope of $g$, not the alternative Wegstein mixing-factor convention. Guard near-zero denominators and bound the extrapolated step. Two evaluations initialize the slope; step limiting reduces risk but does not guarantee convergence.

**Broyden's method** generalizes the secant method to multiple variables. It maintains an approximation to the Jacobian $\mathbf{J}$ and updates it rank-1 at each iteration:

$$
\mathbf{J}^{(n+1)} = \mathbf{J}^{(n)} + \frac{(\Delta \mathbf{f}^{(n)} - \mathbf{J}^{(n)} \Delta \mathbf{x}^{(n)}) (\Delta \mathbf{x}^{(n)})^T}{(\Delta \mathbf{x}^{(n)})^T \Delta \mathbf{x}^{(n)}}
$$

Under appropriate local smoothness and nonsingularity conditions, Broyden's method can converge super-linearly and is effective for multi-variable recycle convergence, but it requires storing and updating the Jacobian approximation.

---

## 31.5 Recycle Loop Convergence

### 31.5.1 The NeqSim Recycle Class

The `Recycle` class in NeqSim implements the torn-stream convergence for recycle loops. It acts as a special "equipment" unit that compares the computed recycle stream with the assumed stream and updates the assumed stream for the next iteration:

```python
import jpype
import numpy as np
jneqsim = jpype.JPackage("neqsim")
SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
Stream = jneqsim.process.equipment.stream.Stream
Mixer = jneqsim.process.equipment.mixer.Mixer
Cooler = jneqsim.process.equipment.heatexchanger.Cooler
Separator = jneqsim.process.equipment.separator.Separator
Splitter = jneqsim.process.equipment.splitter.Splitter
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
ThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve
# Actual direct-substitution recycle iteration, with a 35% gas recycle.
# This records each NeqSim equipment evaluation rather than inventing residuals.
recycle_fluid = SystemSrkEos(303.15, 40.0)
for name, fraction in [("methane", 0.65), ("ethane", 0.15), ("propane", 0.10), ("n-butane", 0.10)]:
    recycle_fluid.addComponent(name, fraction)
recycle_fluid.setMixingRule("classic")
feed = Stream("Fresh feed", recycle_fluid)
feed.setFlowRate(50000.0, "kg/hr")
feed.run()
tear = Stream("Recycle tear", recycle_fluid.clone())
tear.setFlowRate(1000.0, "kg/hr")
tear.setTemperature(40.0, "C")
tear.run()
mixer = Mixer("Recycle mixer")
mixer.addStream(feed)
mixer.addStream(tear)
cooler_loop = Cooler("Loop cooler", mixer.getOutletStream())
cooler_loop.setOutTemperature(293.15)
separator = Separator("Loop separator", cooler_loop.getOutletStream())
splitter_loop = Splitter("Gas recycle split", separator.getGasOutStream())
splitter_loop.setSplitFactors([0.35, 0.65])
flow_errors, temp_errors, comp_errors = [], [], []
for iteration in range(60):
    old_flow = float(tear.getFlowRate("kg/hr"))
    old_temperature = float(tear.getTemperature("K"))
    old_composition = np.asarray(tear.getFluid().getMolarComposition(), dtype=float)
    mixer.run();cooler_loop.run()
    # Fresh separator avoids its native 1e-6 cache masking a 1e-7 tear test.
    separator=Separator('Loop separator',cooler_loop.getOutletStream())
    separator.run()
    splitter_loop=Splitter('Gas recycle split',separator.getGasOutStream())
    splitter_loop.setSplitFactors([0.35,0.65]);splitter_loop.run()
    updated = splitter_loop.getSplitStream(0)
    new_flow = float(updated.getFlowRate("kg/hr"))
    new_temperature = float(updated.getTemperature("K"))
    new_composition = np.asarray(updated.getFluid().getMolarComposition(), dtype=float)
    # Normalize different quantities before comparing them on a common axis.
    flow_errors.append(abs(new_flow - old_flow) / 50000.0)
    temp_errors.append(abs(new_temperature - old_temperature) / 303.15)
    comp_errors.append(float(np.max(np.abs(new_composition - old_composition))))
    tear.setThermoSystem(updated.getThermoSystem().clone())
    if max(flow_errors[-1], temp_errors[-1], comp_errors[-1]) < 1e-7:
        break
assert max(flow_errors[-1], temp_errors[-1], comp_errors[-1]) < 1e-7, "Recycle did not converge"
max_iters = len(flow_errors)
iterations = list(range(1, max_iters + 1))
print(f"Measured recycle convergence: {max_iters} iterations; flow={new_flow:.5f} kg/hr")
print(f"Final normalized residuals: flow={flow_errors[-1]:.3g}, T={temp_errors[-1]:.3g}, composition={comp_errors[-1]:.3g}")

products=[separator.getLiquidOutStream(),splitter_loop.getSplitStream(1)]
for s in products+[feed]: s.getFluid().initProperties()
mass_out=sum(float(s.getFlowRate('kg/hr')) for s in products)
mass_error=abs(mass_out-50000.0)/50000.0
h_in=float(feed.getFluid().getEnthalpy())
h_out=sum(float(s.getFluid().getEnthalpy()) for s in products)
energy_error=abs(h_out-h_in-float(cooler_loop.getDuty()))/max(abs(h_in),abs(h_out),1.0)
assert mass_error<1e-7 and energy_error<1e-7,(mass_error,energy_error)
for i in range(feed.getFluid().getNumberOfComponents()):
    ni=float(feed.getFluid().getComponent(i).getNumberOfmoles())
    no=sum(float(s.getFluid().getComponent(i).getNumberOfmoles()) for s in products)
    assert abs(no-ni)/float(feed.getFluid().getTotalNumberOfMoles())<1e-7
print('Accepted recycle boundary',mass_error,energy_error)
```

### 31.5.2 Tolerance and Convergence Criteria

Use the current API’s actual residual definitions \cite{neqsim2026update}. `getErrorFlow()` is legacy: below 1 kg/s it is an absolute kg/s change, while at or above 1 kg/s it is a percentage change. `getAbsoluteFlowChange()` is consistently kg/hr. Temperature and pressure errors are sums of phase-relative percentage changes; composition error sums absolute first-phase mole-fraction changes. Default tolerance fields are 0.01, not a universal normalized $10^{-4}$ criterion.

Set explicit tolerances and independently compare component flows, total mass and energy. The optional absolute-flow criterion is an **OR** with the legacy flow test; it does not replace the temperature, pressure or composition checks. An internally small tear residual alone cannot certify whole-flowsheet closure.

### 31.5.3 Damping

When the recycle loop is poorly conditioned — the computed stream is very sensitive to changes in the assumed stream — direct substitution can oscillate or diverge. **Damping** reduces the step size:

$$
x^{(n+1)} = (1 - \alpha) x^{(n)} + \alpha \cdot g(x^{(n)})
$$

where $\alpha \in (0, 1]$ is the damping factor. A value of $\alpha = 0.5$ means the update is a 50/50 blend of the old and new values. Smaller $\alpha$ can damp oscillation but cannot stabilize every divergent mapping; a scalar positive slope greater than one remains divergent for any positive under-relaxation.

Acceleration and adaptive settings belong to the configured recycle solver. `RecycleController` coordinates recycle priorities and convergence; do not treat it as a promise of this particular damping schedule.

### 31.5.4 Maximum Iterations and Failure Modes

The maximum number of recycle iterations is configurable (default: 100 in NeqSim). Failure behavior depends on the execution path; current implicit-loop convergence can throw an exception. In all cases reject the last iterate as an accepted process solution unless independent convergence and balance checks pass. Common failure modes include:

| Failure Mode | Symptom | Remedy |
|-------------|---------|--------|
| Oscillation | Error alternates high/low | Reduce damping factor |
| Slow convergence | Error decreases but slowly | Use Wegstein or Broyden acceleration |
| Divergence | Error increases each iteration | Check flowsheet topology; reduce initial flow rate |
| Stalled | Error stuck at finite value | Check if specification is physically impossible |

### 31.5.5 Convergence Diagnostics

The `ConvergenceDiagnostics` class provides detailed information about the convergence behavior of recycle loops:

```python
# Inspect the actual, normalized tear residuals recorded above.
for name, values in [("flow", flow_errors), ("temperature", temp_errors),
                     ("composition", comp_errors)]:
    print(name, "iterations:", len(values), "final normalized residual:", values[-1])
assert max(flow_errors[-1], temp_errors[-1], comp_errors[-1]) < 1e-7
```

---

## 31.6 Adjuster and Specification Convergence

### 31.6.1 The Adjuster Concept

An **Adjuster** manipulates a decision variable (e.g., a valve opening, a stream flow rate, a heater duty) to drive a target variable (e.g., a stream temperature, a product specification) to a specified value. In optimization terms, the adjuster solves:

$$
\text{Find } u \text{ such that } h(u) = h_{\text{target}}
$$

where $u$ is the manipulated variable, $h(u)$ is the measured variable (computed by running the flowsheet with $u$), and $h_{\text{target}}$ is the target value.

### 31.6.2 The Secant Method

NeqSim uses the **secant method** to converge the adjuster. Starting from two initial guesses $u^{(0)}$ and $u^{(1)}$ (typically ±10% of the initial value), the secant method updates:

$$
u^{(n+1)} = u^{(n)} - \frac{h(u^{(n)}) - h_{\text{target}}}{h(u^{(n)}) - h(u^{(n-1)})} \cdot (u^{(n)} - u^{(n-1)})
$$

This is essentially a finite-difference approximation to Newton's method, avoiding the need for explicit derivatives. The scalar secant method has local order approximately 1.618 for a smooth simple root; discontinuities, clipping and inaccurate inner solves invalidate that result.

### 31.6.3 Adjuster Configuration in NeqSim

```python
import jpype
import numpy as np
jneqsim = jpype.JPackage("neqsim")
SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
Stream = jneqsim.process.equipment.stream.Stream
Mixer = jneqsim.process.equipment.mixer.Mixer
Cooler = jneqsim.process.equipment.heatexchanger.Cooler
Separator = jneqsim.process.equipment.separator.Separator
Splitter = jneqsim.process.equipment.splitter.Splitter
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
ThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve
# Adjuster example: Adjust valve outlet pressure to hit target temperature
fluid2 = SystemSrkEos(273.15 + 60.0, 100.0)
fluid2.addComponent("methane", 0.85)
fluid2.addComponent("ethane", 0.10)
fluid2.addComponent("propane", 0.05)
fluid2.setMixingRule("classic")

feed2 = Stream("HP Gas", fluid2)
feed2.setFlowRate(50000.0, "kg/hr")
feed2.setTemperature(60.0, "C")
feed2.setPressure(100.0, "bara")

valve = ThrottlingValve("JT Valve", feed2)
valve.setOutletPressure(40.0)  # initial guess

# Adjuster: vary valve outlet pressure to achieve target outlet temperature = 40 C
adjuster = jneqsim.process.equipment.util.Adjuster("Temp Adjuster")
adjuster.setTargetVariable(valve.getOutletStream(), "temperature", 40.0, "C")
# Current Adjuster supports custom targets through the functional callback.
temperature_reader = jpype.JProxy("java.util.function.Function", dict={"apply": lambda equipment: float(equipment.getTemperature("C"))})
adjuster.setTargetValueCalculator(temperature_reader)
adjuster.setAdjustedVariable(valve, "pressure", "bara")
# A valve's pressure setpoint belongs to the equipment, not its outlet stream.
pressure_getter = jpype.JProxy("java.util.function.Function", dict={"apply": lambda equipment: float(equipment.getOutletPressure())})
pressure_setter = jpype.JProxy("java.util.function.BiConsumer", dict={"accept": lambda equipment, value: equipment.setOutletPressure(float(value))})
adjuster.setAdjustedValueGetter(pressure_getter)
adjuster.setAdjustedValueSetter(pressure_setter)
adjuster.setMaxAdjustedValue(95.0)
adjuster.setMinAdjustedValue(5.0)
adjuster.setTolerance(1e-5)

process2 = ProcessSystem()
process2.add(feed2)
process2.add(valve)
process2.add(adjuster)
process2.run()

outlet_T = float(valve.getOutletStream().getTemperature("C"))
outlet_P = float(valve.getOutletStream().getPressure("bara"))
print(f"Target temperature:   40.0 °C")
print(f"Achieved temperature: {outlet_T:.2f} °C")
print(f"Required outlet pressure: {outlet_P:.2f} bara")
print(f"\nThe adjuster found the valve pressure that produces the target JT cooling.")
assert abs(outlet_T - 40.0) < 0.05, "Adjuster must satisfy the stated target"

assert 5.0<=outlet_P<=95.0 and abs(outlet_T-40.0)<1e-4
assert abs(valve.getOutletStream().getFlowRate('kg/hr')-50000.0)<1e-5
assert abs(valve.getOutletStream().getFluid().getEnthalpy()-feed2.getFluid().getEnthalpy())/max(abs(feed2.getFluid().getEnthalpy()),1.0)<1e-6
# Final independent valve replay at the accepted pressure.
replay_valve=ThrottlingValve('Independent JT replay',feed2)
replay_valve.setOutletPressure(outlet_P);replay_valve.run()
assert abs(replay_valve.getOutletStream().getTemperature('C')-40.0)<1e-4
```

### 31.6.4 Adjuster-Recycle Interaction

When adjusters and recycles coexist in a flowsheet, the convergence becomes more complex. The adjuster iterates on the manipulated variable, but each adjuster evaluation requires a full flowsheet solution, which includes the recycle convergence. This creates a **nested iteration** structure:

- **Outer loop**: Adjuster iterations (secant method)
  - **Inner loop**: Recycle convergence (direct substitution / Wegstein)
    - **Innermost**: Flash calculations (successive substitution / Newton)

The nested structure means that convergence of the outer loop depends on the accuracy of the inner loop. If the recycle does not converge tightly, the adjuster receives noisy evaluations and may fail to converge. As a general rule:

- Scale residuals into comparable target-error units and show that inner-loop error is small relative to the target tolerance; a factor of ten can be a starting heuristic
- Converge the recycle fully before evaluating the adjuster residual
- Limit the adjuster step size to avoid stepping past the recycle convergence basin

---

## 31.7 Distillation Column Solvers

### 31.7.1 The Distillation Problem

A fixed-pressure equilibrium stage commonly has $2C+3$ MESH equations: $C$ component balances, $C$ equilibrium relations, two composition sums and one energy balance. The count changes with chosen variables, reactions, phases, hydraulics and boundary specifications. Pressure-drop equations are additional when pressure is not prescribed.

The system is too large and tightly coupled for the sequential modular approach — each stage depends on the stages above and below through the interlinking vapor and liquid streams. Specialized algorithms are needed.

### 31.7.2 Bubble-Point Method

The **bubble-point method** (Wang–Henke, 1966) is the simplest column solver. It assumes that the temperatures on each stage can be determined from the bubble-point condition of the liquid leaving that stage:

$$
\sum_{i=1}^{C} K_i(T_j, P_j) \cdot x_{i,j} = 1, \quad j = 1, \ldots, N
$$

The component material balances are linearized into a tridiagonal system (the Thomas algorithm) and solved for the liquid compositions $x_{i,j}$. The temperatures are then updated from the bubble-point condition, and the energy balance provides the stage duties (condenser, reboiler). The method iterates between material balance, bubble-point temperature, and energy balance until convergence.

The bubble-point method is robust for ideal and near-ideal systems (narrow-boiling mixtures) but can be slow or fail for wide-boiling mixtures and systems with strong non-ideality.

### 31.7.3 Inside-Out Method

The **inside-out** method (Boston and Sullivan, 1974) is the workhorse of modern process simulators. It uses a simplified thermodynamic model inside an inner loop to solve the column equations quickly, then updates the simplified model parameters from the rigorous EOS in an outer loop.

The inner loop uses:
- Simple K-value correlations (e.g., $\ln K_i = A_i + B_i / T$) fitted to match the rigorous EOS at the current conditions
- The Thomas algorithm for the tridiagonal material balance
- Direct energy balance solution for temperatures

The outer loop:
1. Evaluates rigorous EOS properties at the current column profile
2. Re-fits the simplified K-value parameters
3. Returns to the inner loop

The inside-out method converges rapidly because the inner loop captures the major effects (material balance, energy balance) while the outer loop handles the thermodynamic nonlinearity. Iteration counts depend on initialization, properties and the particular algorithm; no timing or iteration benchmark is implied by this description.

### 31.7.4 Newton Tray-by-Tray (Naphtali–Sandholm)

The **Newton tray-by-tray** method (Naphtali and Sandholm, 1971) applies Newton's method to the full system of $N \times (2C + 3)$ equations simultaneously. The Jacobian is block-tridiagonal (each stage couples only to its neighbors), enabling efficient solution by block elimination.

This method has the fastest convergence rate (quadratic) but requires the most computational effort per iteration (Jacobian evaluation and factorization). It is preferred for:

- Highly non-ideal systems (azeotropic, reactive distillation)
- Three-phase columns (vapor-liquid-liquid)
- Columns with many side-draws or side-feeds

### 31.7.5 NeqSim Column Solver Selection

The pinned `DistillationColumn.SolverType` includes `DIRECT_SUBSTITUTION`, `DAMPED_SUBSTITUTION`, `INSIDE_OUT`, `MATRIX_INSIDE_OUT`, `WEGSTEIN`, `SUM_RATES`, `NEWTON`, `NAPHTALI_SANDHOLM`, `MESH_RESIDUAL` and `AUTO`. `NEWTON` is a tray-temperature accelerator, whereas `NAPHTALI_SANDHOLM` addresses full MESH blocks. Algorithm names do not guarantee convergence order on a particular case \cite{neqsim2026update}.

**Execution scope:** This integration pattern requires a fully specified column feed pressures and operating specifications. It is not a standalone validated process calculation.

```python pattern: requires a fully specified column feed pressures and operating specifications
import jpype
jneqsim = jpype.JPackage("neqsim")

DistillationColumn = jneqsim.process.equipment.distillation.DistillationColumn

column = DistillationColumn("deethanizer", 15, True, True)
column.addFeedStream(feed_stream, 7)

# Select a current solver enum; compare enabled physical residual gates.
column.setSolverType(DistillationColumn.SolverType.INSIDE_OUT)
column.run()

# Check convergence metrics
print(f"Converged: {column.solved()}")
print(f"Iterations: {column.getLastIterationCount()}")
print(f"Mass residual: {column.getLastMassResidual():.2e}")
print(f"Energy residual: {column.getLastEnergyResidual():.2e}")
```

**Table 31.1.** Distillation column solver comparison.

| Solver | Convergence Rate | Robustness | Best For |
|--------|-----------------|-----------|----------|
| `DIRECT_SUBSTITUTION` | Linear | High | Ideal/near-ideal mixtures, initial exploration |
| `DAMPED_SUBSTITUTION` | Typically linear; no quadratic guarantee | Case-dependent | Damping oscillating substitutions |
| `INSIDE_OUT` | Case-dependent | Case-dependent | Test with matched physical acceptance gates |

### 31.7.6 Convergence Metrics

Check `solved()` and `getSolveStatus()`, plus temperature, component, energy and raw MESH residual diagnostics. `RIGOROUS_CONVERGED` means the **enabled** gates passed; product reconciliation or fallback states are distinct. Explicitly enable required energy and MESH gates, specify their tolerances, and independently reconcile feed, side draws, products and applied duties. A temperature-converged profile is insufficient. Chapter 33 supplies a duty-specified, balance-checked example.

If the column fails to converge, the most common causes are:

1. **Insufficient stages**: The specified separation cannot be achieved with the given number of stages
2. **Poor feed tray location**: The feed tray should be at the stage where the feed composition best matches the column profile
3. **Extreme reflux or reboil specifications**: Very high or very low reflux ratios can cause numerical difficulties
4. **Trace components**: Components at very low concentrations (< 1 ppm) can cause scaling problems in the Jacobian

---

## 31.8 Dynamic Simulation Integration

### 31.8.1 From Steady State to Dynamic

The preceding sections address steady-state simulation, where all time derivatives are zero. **Dynamic simulation** introduces time-varying behavior — pressure transients, level changes, temperature excursions — that occurs during startup, shutdown, load changes, and disturbances.

The dynamic model adds accumulation terms to the steady-state equations:

$$
\frac{d(M_i)}{dt} = F_{\text{in},i} - F_{\text{out},i} + R_i \quad \text{(component material balance)}
$$

$$
\frac{d(U)}{dt} = H_{\text{in}} - H_{\text{out}} + Q \quad \text{(energy balance)}
$$

where $M_i$ is the moles of component $i$ in the holdup, $U$ is the internal energy, and $R_i$ is the reaction rate.

### 31.8.2 Time Integration Methods

Explicit Euler is one supported integration strategy and illustrates the time-discretization issue:

$$
\mathbf{x}^{(n+1)} = \mathbf{x}^{(n)} + \Delta t \cdot \mathbf{f}(\mathbf{x}^{(n)}, t^{(n)})
$$

where $\mathbf{x}$ is the state vector (holdups, temperatures, pressures) and $\mathbf{f}$ is the right-hand side of the ODE system (material and energy balance derivatives). The explicit method is simple to implement and does not require matrix factorization, but its stability is limited by the time step:

$$
|1+\Delta t\,\lambda_j|<1\quad\text{for every decaying linear mode }j
$$

Here $\lambda_j$ are Jacobian eigenvalues. For real negative eigenvalues this reduces to $\Delta t<2/\max_j|\lambda_j|$; complex modes require the full stability-region condition. For stiff systems (e.g., fast pressure dynamics coupled with slow composition changes), the maximum stable time step can be very small.

**Backward Euler and the trapezoidal rule** are A-stable on the linear test equation, not unconditionally accurate or convergent for every nonlinear problem. The pinned source provides `ExplicitEulerIntegrator`, `RK4Integrator`, `AdaptiveRK45Integrator` and `BDFIntegrator`, plus a process semi-implicit mode. Strategy support is equipment-dependent: selecting one does not retrofit every unit with a new differential model. Check dynamic capability/activation reports and perform time-step refinement and independent inventory/energy budgets \cite{neqsim2026update}.

### 31.8.3 NeqSim runTransient() Method

The `ProcessSystem.runTransient()` method advances the dynamic simulation by one time step:

**Execution scope:** This integration pattern requires initialized dynamic equipment inventories and controller setup. It is not a standalone validated process calculation.

```python pattern: requires initialized dynamic equipment inventories and controller setup
# Dynamic simulation example
sep.setCalculateSteadyState(False)
dt = 1.0  # Time step in seconds
total_time = 600.0  # 10 minutes
n_steps = int(total_time / dt)

for step in range(n_steps):
    process.runTransient(dt)
    # The ProcessSystem runs all controller and measurement devices each step
    if step % 60 == 0:
        t_current = step * dt
        sep_level = sep.getLiquidLevel()
        print(f"  t = {t_current:.0f} s, separator level = {sep_level:.3f} m")
```

### 31.8.4 Controller-Equipment Interaction

Execution order depends on equipment, attached controllers and the selected process stepping mode. A measurement at the start of a step can control that step’s boundary flow; it does not necessarily impose a full one-step sensor delay. Distinguish sampled-data zero-order hold, actual transport delay and algebraic recycle ordering. Use a fresh identifier for each physical step and do not integrate the same inventory twice. Chapter 29 demonstrates the order used in its checked vessel calculation.

### 31.8.5 Time Step Selection

The appropriate time step depends on the fastest dynamics in the system:

| Dynamic Phenomenon | Characteristic Time | Suggested $\Delta t$ |
|-------------------|-------------------|---------------------|
| Pressure wave in pipe | 0.01–1 s | Not modeled (steady-state pressure) |
| Valve dynamics | 1–10 s | 0.1–1.0 s |
| Separator level | 10–300 s | 1–10 s |
| Temperature transient | 60–3600 s | 5–60 s |
| Composition change | 300–3600 s | 10–60 s |

As a rule of thumb, the time step should be 5–10× smaller than the fastest characteristic time of interest. Using a time step that is too large causes instability (oscillation or divergence); using one that is too small wastes computation time.

---

## 31.9 Initial Guess and Convergence Behavior

### 31.9.1 The Importance of Initial Estimates

The convergence of iterative methods — flash calculations, recycle loops, column solvers — depends strongly on the quality of the initial guess. A good initial guess:

- Falls within the convergence basin of the desired solution
- Is close enough that the iterative method converges in few iterations
- Avoids spurious solutions (e.g., trivial solutions where all K-values equal unity)

### 31.9.2 Flash Initialization

For TP flash, the Wilson correlation provides excellent initial K-values for hydrocarbon systems at moderate conditions. For more challenging systems (near-critical, highly asymmetric), NeqSim uses:

1. **Wilson K-values** as the primary initialization
2. **Ideal K-values** ($K_i = P_i^{\text{sat}} / P$) as a backup for low-pressure systems
3. **Previous solution** — when running a sequence of flashes (e.g., along a pipeline), the converged K-values from the previous point provide an excellent starting point for the next

### 31.9.3 Recycle Initialization

For recycle loops, the initial guess of the torn stream can significantly affect convergence. Strategies include:

- **Design basis**: Use the design flow rate, temperature, and composition as the initial guess
- **Previous converged solution**: If running the flowsheet for a different operating point, start from the previous converged state
- **Ramp-up**: Start with a small recycle flow rate and gradually increase it, converging the flowsheet at each step

### 31.9.4 Continuation Methods

For parametric studies (e.g., varying the feed rate from 50,000 to 120,000 kg/hr in steps of 10,000), **continuation** uses the converged solution at one parameter value as the initial guess for the next. This dramatically improves convergence reliability, because the solution changes smoothly with the parameter.

Continuation is particularly effective for:

- VFP table generation (varying pressure, rate, water cut in small steps)
- Sensitivity analyses (varying one parameter at a time)
- Production optimization (the optimizer typically varies decision variables by small increments)

### 31.9.5 Phase Identification Initialization

A particularly challenging aspect of flash initialization is **phase identification** — determining whether a given root of the cubic EOS represents a liquid or vapor phase. Near the critical point, the density difference between liquid and vapor vanishes, and the standard criterion (liquid = smallest $Z$ root, vapor = largest $Z$ root) becomes ambiguous.

Phase labels must be checked against composition, density and stability. No fixed pseudo-critical density threshold establishes all mixture phase identities, especially near a critical point where density differences vanish. For water/hydrocarbon systems distinguish the aqueous phase by composition and the enabled phase model; do not infer it from a generic “liquid” label alone.

### 31.9.6 Warm-Starting Optimization

In the context of production optimization, where the simulator is called repeatedly with small changes to decision variables, **warm-starting** carries forward the entire converged state — not just the K-values, but also the recycle stream values, column profiles, and controller states. Measure speed and accepted residuals on the actual model. Warm starts can select a metastable branch or retain stale equipment state, so independent final replay remains necessary.

Warm-starting is implicit in NeqSim's `ProcessSystem` when `run()` is called repeatedly on the same process object. The equipment retains its state between calls, and each new call starts from the previous converged state. A serial optimizer may reuse a process with carefully reset inputs; independent scenarios and acceptance replay should use isolated fresh models or verified restored states. Never share mutable equipment between concurrent evaluations.

---

## 31.10 Convergence Diagnostics and Troubleshooting

### 31.10.1 Diagnosing Non-Convergence

When a simulation fails to converge, the engineer must diagnose the root cause before attempting remedies. The `ConvergenceDiagnostics` class in NeqSim provides structured information:

- **Which component failed?** Flash, recycle, adjuster, or column?
- **What is the error trajectory?** Decreasing (convergence is slow), oscillating (damping needed), or increasing (divergence)?
- **Where in the flowsheet?** Which equipment unit produced anomalous results?

### 31.10.2 Common Failure Modes

**Table 31.2.** Common convergence failures and remedies.

| Failure Mode | Symptoms | Root Cause | Remedy |
|-------------|----------|-----------|--------|
| Flash non-convergence near critical point | K-values ≈ 1, slow SS convergence | Phases nearly identical | Use Newton solver, wider initial K-value range |
| Trivial solution | All K-values = 1, single phase | Wrong phase identification | Restart with Wilson K-values, check stability |
| Recycle oscillation | Alternating high/low values | Large gain in recycle loop | Add damping ($\alpha = 0.3$–$0.5$) |
| Recycle divergence | Exponentially growing error | Positive feedback in loop | Reduce initial flow, check topology |
| Adjuster failure | Target not reached after max iter | Target infeasible or discontinuous | Widen search range, check physical feasibility |
| Column non-convergence | Large mass/energy residuals | Poor initial profile, extreme specs | Increase stages, adjust reflux ratio, change solver |
| Negative flow rates | Unphysical intermediate results | Bad initial guess | Re-initialize with design conditions |
| Temperature crossover | Hot side colder than cold side | Heat exchanger approach violated | Increase area, reduce duty specification |

### 31.10.3 Remedies

**Relaxation**: Blend the new iterate with the old iterate to reduce step size. This is the most universally applicable remedy. A relaxation factor of 0.3–0.5 is a good starting point; increase it toward 1.0 as convergence improves.

**Stepping**: Instead of jumping to the target conditions, approach them in small steps. For example, if the feed pressure drops from 100 to 30 bara, run intermediate cases at 80, 60, and 40 bara. Each intermediate solution provides the initial guess for the next step, keeping the iteration within the convergence basin.

**Alternative algorithms**: If the default solver fails, try an alternative. For flash, switch from SS to Newton or vice versa. For columns, switch from inside-out to sequential or damped. Different algorithms have different convergence basins, so an alternative may succeed where the default fails.

**Reduced tolerance**: For intermediate calculations (not the final result), a looser tolerance may be acceptable. This allows the outer loop to proceed even if the inner loop is not perfectly converged. For example, during the early iterations of a recycle loop, a flash tolerance of $10^{-6}$ (instead of $10^{-10}$) may suffice.

**Problem simplification**: Remove non-essential components (trace species), simplify the EOS (SRK instead of CPA), or reduce the number of stages in a column. Solve the simplified problem, then use its solution as the initial guess for the full problem. This "bootstrap" approach is particularly effective for complex flowsheets where the default initialization fails.

**Bounding and scaling**: Ensure that all variables have physically reasonable bounds (e.g., temperature between 200 K and 600 K, pressure between 1 and 500 bara). Scaling the variables so that their typical magnitudes are $O(1)$ improves the conditioning of the Jacobian and helps iterative methods converge.

---

## 31.11 Performance Optimization

### 31.11.1 Computational Cost of Flash Calculations

The flash calculation is the dominant computational cost in process simulation. A single TP flash requires:

- 1–3 EOS evaluations for the initial successive substitution iterations
- 2–5 Newton iterations (each requiring a Jacobian evaluation)
- Each EOS evaluation involves $O(C^2)$ operations for mixing rules

Count actual flash calls and measure warmed, repeated timings for the specified model, component list and machine. Equipment and flash iterations do not imply a universal 5,000-call count or fixed millisecond latency. Report failed cases separately from accepted evaluations.

### 31.11.2 Caching Strategies

Many flash calculations in a process simulation are redundant — the same feed at the same conditions is flashed multiple times during recycle convergence. **Caching** stores the results of previous flashes and returns the cached result if the same inputs are encountered again.

NeqSim implements caching at the stream level: if a stream's conditions (composition, temperature, pressure) have not changed since the last flash, the previous results are reused. The benefit and cache thresholds are equipment-specific. This revision found that a separator’s $10^{-6}$ state cache could obscure a tighter $10^{-7}$ recycle check; the notebook now allocates a fresh separator per tear iteration and independently checks closure.

### 31.11.3 Reducing Unnecessary Recalculations

In production optimization, the optimizer often evaluates neighboring points in the decision-variable space — e.g., feed rates of 79,000 and 81,000 kg/hr. The process solution at 79,000 kg/hr is an excellent initial guess for 81,000 kg/hr. By carrying forward the converged state (temperatures, compositions, K-values) from one evaluation to the next, the number of iterations per evaluation is dramatically reduced.

This strategy is automatically implemented in NeqSim when the `ProcessSystem` is re-run without resetting — the equipment retains its state from the previous run.

### 31.11.4 Parallel Execution

For Monte Carlo and multi-scenario analyses, the individual evaluations are independent and can be run in parallel. NeqSim supports parallel scenario evaluation through the `optimizeScenariosParallel()` method in `ProductionOptimizer`. Measure scaling on isolated model copies under bounded thread/JVM counts; no universal speedup follows from the number of cores.

### 31.11.5 Profiling Simulation Performance

When simulation performance is a bottleneck, profiling identifies the hotspots. Common bottlenecks include:

- **Unnecessary multi-phase checks**: If the fluid is known to be single-phase gas, disabling `setMultiPhaseCheck(False)` avoids the stability analysis overhead
- **Over-converged recycles**: Choose recycle tolerances from allowed objective/constraint error, particularly near active limits; decision-step size alone does not establish an adequate tolerance
- **Excessive property calculations**: Calling `initProperties()` computes all transport properties (viscosity, thermal conductivity); initialize the required thermodynamic state and explicitly check the requested property; benchmark before suppressing transport initialization
- **Large component lists**: Each additional component increases flash cost quadratically; lumping can reduce cost but requires renewed property and phase-behavior validation

---


<!-- September 2026 source update -->
## Choose a solver with a measurable acceptance contract

Compare algorithms on the same objective, bounds, constraint set, fluid model and stopping tolerance. Score-based searches with empty objective lists have zero objective score; they cannot be compared with explicitly defined throughput maximization as if the optimization problems were identical. Binary feasibility requires a suitable monotonic region, while non-monotonic maps or disconnected feasible regions require a broader search strategy \cite{neqsim2026update}.

The current `ProductionOptimizer` replays its selected point without cached evidence. External solver integrations must implement an equivalent final evaluation. Measure both numerical termination and physical acceptance: finite state, process convergence, balances, constraint margins, declared evidence coverage and reproducibility. Cache timing should distinguish unchanged states from changed constraints or equipment lineups.

Pressure/flow screening remains a process calculation. The current `generateCapacityScreening()` interface makes its fixed-composition, mass-throughput basis explicit. It is not a numerical shortcut for a qualified well VFP model; reservoir deck formatting requires supplied BHP and the separate axis/unit contract described in Chapter 28.

---


<!-- reviewed-notebook-results:start -->
## Reproduced Calculation Results

These examples use the stated fluid recipes and operating assumptions. Curves represent NeqSim calculations unless a caption identifies an analytical illustration, assumed equipment map or synthetic data.

![TP Flash Computation Time vs Pressure. Observed timings from this execution environment](figures/ch29_flash_convergence.png)

T = 25.0 °C: flash time spans 1.383–94.48 ms across the plotted cases. T = 50.0 °C: flash time spans 0.4345–185.3 ms across the plotted cases.

Phase splitting changes the nonlinear work required by the TP flash, while JVM warm-up and concurrent machine load also affect elapsed time. These measurements illustrate computational variability and are not a controlled performance benchmark. Repeat warm runs with fixed composition and resource conditions before drawing speed conclusions.

![Effect of Initial Temperature Guess. Observed timings from this execution environment](figures/ch29_initial_guess_effect.png)

Flash Time spans 0.4578–17.6 ms across the plotted cases. Flash Time spans 0.4276–23.8 ms across the plotted cases.

Each initial state is flashed before moving to the common target state, so the target flash starts from an actual thermodynamic solution. Warm-start timing depends on both the initial phase state and the machine runtime. Choose physically nearby initial states, and compare repeated median timings rather than a single outlier.

![Recycle Loop Convergence — Direct Substitution](figures/ch29_recycle_convergence.png)

The actual NeqSim tear-stream iteration meets the stated 10⁻⁷ normalized-residual criterion in 14 iterations. Residuals are measured from successive flow, temperature and composition updates; exact zeros use a 10⁻¹⁶ display floor on the logarithmic axis.

Direct substitution feeds the newly computed recycle flow, temperature and composition back into the next NeqSim equipment evaluation. A decreasing tear-stream residual supports internal consistency but does not establish experimental accuracy. Check material and energy balances after convergence and independently verify any adjusted target.

![Flash Computation Time vs Number of Components. Observed timings from this execution environment](figures/ch29_component_scaling.png)

2 comp (C1-C3): flash time spans 0.2668–42.16 ms across the plotted cases. 4 comp: flash time spans 0.3023–17.06 ms across the plotted cases.

Adding components changes the dimension and phase behavior of the flash problem. The plotted runtime differences contain machine and phase-state effects as well as component-count effects. Use repeated, matched-state tests when selecting a fluid reduction strategy for computational speed.

Selected numerical ranges from the plotted cases:

| Quantity / series | Minimum | Maximum | Unit |
|---|---:|---:|---|
| T = 25.0 °C: flash time | 1.383 | 94.48 | ms |
| Flash Time | 0.4578 | 17.6 | ms |
| Flow change / fresh-feed flow: normalized residual | 1e-16 | 0.2659 | - |
| 2 comp (C1-C3): flash time | 0.2668 | 42.16 | ms |

Ranges describe the sampled cases; they are not independent validation tolerances.
<!-- reviewed-notebook-results:end -->

## 31.12 Summary

This chapter has examined the numerical methods that underpin every process simulation and production optimization in NeqSim. The key points are:

1. **Flash calculations** are the innermost and most frequently called numerical procedure. The Rachford–Rice equation reduces the two-phase flash to a single-variable root-finding problem. Successive substitution is robust but slow; Newton's method is fast but needs a good initial guess; NeqSim uses a hybrid of both.

2. **Cubic EOS root finding** requires careful handling of multiple roots, with root selection based on Gibbs energy minimization. Volume translation corrects liquid density predictions without affecting phase equilibrium.

3. **The sequential modular approach** solves process flowsheets by executing equipment modules in sequence. Recycle loops require iterative convergence, with direct substitution as the baseline and Wegstein or Broyden acceleration for faster convergence.

4. **Recycle convergence** is controlled by tolerance, damping, and maximum iterations. The `ConvergenceDiagnostics` class helps identify whether convergence is slow, oscillating, or diverging, and suggests appropriate remedies.

5. **Adjusters** use the secant method to hit target specifications. When combined with recycles, the nested iteration structure requires careful tolerance management — inner-loop uncertainty must be small relative to the target tolerance after consistent scaling.

6. **Distillation column solvers** range from the simple bubble-point method to the sophisticated inside-out algorithm. Solver selection depends on the system non-ideality and the number of stages. Convergence metrics (mass and energy residuals) indicate whether the solution is reliable.

7. **Dynamic simulation** adds time integration to the steady-state equations. Explicit Euler integration is simple but requires small time steps for stability. Controller scan order and transport delays must be represented explicitly and checked during tuning.

8. **Performance optimization** — caching, continuation, parallel execution, and component lumping — can reduce computation time, with speedup established by matched accepted-case benchmarks, making simulation-based optimization practical for industrial applications.

The engineer who understands these numerical foundations is better equipped to diagnose convergence failures, select solver parameters, and design optimization workflows that are both robust and efficient.

---

## Exercises

1. **Flash convergence comparison.** Create a gas condensate fluid (methane 0.70, ethane 0.10, propane 0.06, nC5 0.05, nC10 0.07, CO₂ 0.02) and perform TP flash at 25°C and pressures of 50, 100, 150, 200, 250, and 300 bara. For each pressure, record the number of flash iterations and the vapor fraction. Plot both quantities against pressure and explain the convergence behavior near the cricondenbar.

2. **Recycle convergence.** Build a simple recycle loop: feed mixer → heater → separator → recycle gas back to mixer. Run the process with (a) no damping, (b) damping factor 0.5, and (c) Wegstein acceleration. Compare the number of iterations to convergence and the final error for each method. Plot the recycle stream temperature vs. iteration number for all three methods.

3. **Adjuster interaction.** Add an adjuster to the recycle loop from Exercise 2 that adjusts the heater duty to achieve a separator temperature of 60°C. Run the process with recycle tolerance of $10^{-3}$ and $10^{-6}$. How does the recycle tolerance affect the adjuster convergence?

4. **Distillation solver comparison.** Set up a 20-stage deethanizer column with a 5-component feed (methane 0.30, ethane 0.25, propane 0.20, nC4 0.15, nC5 0.10) and compare the `DIRECT_SUBSTITUTION`, `DAMPED_SUBSTITUTION`, and `INSIDE_OUT` solvers in terms of iteration count, mass residual, and computation time.

5. **Monte Carlo performance.** Implement the Monte Carlo analysis from Chapter 27, Section 27.11, and measure the total computation time for $N = 50, 100, 200, 500$. Plot computation time vs. $N$ and extrapolate to determine the maximum practical $N$ for a 10-minute computation budget.

6. **Convergence diagnostics.** Deliberately create a convergence failure by setting an impossible specification (e.g., an adjuster target outside a rigorously scanned achievable range with bounded inputs). Use the `ConvergenceDiagnostics` class to identify the failure mode and explain the diagnostic output.

---

## References

Boston, J. F. and Sullivan, S. L. (1974). A new class of solution methods for multicomponent, multistage separation processes. *Canadian Journal of Chemical Engineering*, 52(1), 52–63.

Michelsen, M. L. (1982a). The isothermal flash problem. Part I. Stability. *Fluid Phase Equilibria*, 9(1), 1–19.

Michelsen, M. L. (1982b). The isothermal flash problem. Part II. Phase-split calculation. *Fluid Phase Equilibria*, 9(1), 21–40.

Naphtali, L. M. and Sandholm, D. P. (1971). Multicomponent separation calculations by linearization. *AIChE Journal*, 17(1), 148–153.

Peneloux, A., Rauzy, E., and Freze, R. (1982). A consistent correction for Redlich–Kwong–Soave volumes. *Fluid Phase Equilibria*, 8(1), 7–23.

Rachford, H. H. and Rice, J. D. (1952). Procedure for use of electronic digital computers in calculating flash vaporization hydrocarbon equilibrium. *Journal of Petroleum Technology*, 4(10), 19–20.

Soave, G. (1972). Equilibrium constants from a modified Redlich–Kwong equation of state. *Chemical Engineering Science*, 27(6), 1197–1203.

Wang, J. C. and Henke, G. E. (1966). Tridiagonal matrix for distillation. *Hydrocarbon Processing*, 45(8), 155–163.

Wegstein, J. H. (1958). Accelerating convergence of iterative processes. *Communications of the ACM*, 1(6), 9–13.

Whitson, C. H. and Brulé, M. R. (2000). *Phase Behavior*. SPE Monograph Series, Vol. 20. Society of Petroleum Engineers.

Peng, D. Y. and Robinson, D. B. (1976). A new two-constant equation of state. *Industrial and Engineering Chemistry Fundamentals*, 15(1), 59–64.

Broyden, C. G. (1965). A class of methods for solving nonlinear simultaneous equations. *Mathematics of Computation*, 19(92), 577–593.



