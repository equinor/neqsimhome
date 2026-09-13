# Dynamic Simulation and Process Control

<!-- Chapter metadata -->
<!-- Notebooks: ch20_dynamic_separator_control.ipynb, ch20_compressor_antisurge.ipynb, ch20_depressurization.ipynb -->
<!-- Estimated pages: 25 -->

## Learning Objectives

After reading this chapter, the reader will be able to:

1. Explain why dynamic simulation is essential for production optimization — including startup, shutdown, transient analysis, upset response, slug handling, and compressor trip scenarios
2. Formulate the ordinary differential equations (ODEs) governing mass, energy, and momentum balances for dynamic process models, and identify the role of holdup, time constants, and dead time
3. Describe the principles of P, PI, and PID controllers, and apply classical tuning methods (Ziegler–Nichols, Cohen–Coon, IMC) to determine controller parameters
4. Design cascade, feedforward, ratio, and split-range control schemes for common oil and gas production processes
5. Configure and tune level control in separators, pressure control with compressors, and temperature control with heat exchangers
6. Explain anti-surge control system architecture and the principles of compressor surge protection
7. Model depressurization and blowdown scenarios and interpret the resulting pressure–temperature–time profiles
8. Set up dynamic simulations in NeqSim using the `runTransient` method, PID controllers, and measurement devices (PT, TT, LT, FT transmitters)
9. Implement dynamic separator level control, compressor anti-surge control, and depressurization modeling in NeqSim

---

## 29.1 Introduction

The previous chapters of this book have focused primarily on **steady-state** process simulation — computing the equilibrium operating point of a production system given fixed inlet conditions and set points. Steady-state models answer the question: *What will the process look like when everything has settled?*

Real production systems, however, are never truly at steady state. Reservoir conditions change over months and years. Well rates fluctuate over hours and days. Slugs arrive at irregular intervals. Equipment trips occur without warning. Startups and shutdowns impose large, rapid changes on the process. Operators adjust set points in response to changing production targets or quality deviations.

**Dynamic simulation** extends process modeling to capture how the system evolves over time. It answers the question: *What happens during the transition from one operating state to another, and how fast does the system respond?*

Dynamic simulation is critical for production optimization because:

- **Startup and shutdown sequences** must be planned to avoid equipment damage, flaring, and safety trips. The order and timing of valve openings, compressor starts, and heater ramp-up are determined through dynamic simulation.
- **Transient analysis** reveals whether the process can handle disturbances — a sudden increase in water cut, a slug arriving at the separator, or a change in gas composition — without violating safety or quality limits.
- **Controller design and tuning** requires a dynamic model. PID controller parameters (gain, integral time, derivative time) are tuned using the dynamic response of the process.
- **Emergency depressurization** analysis determines how fast a vessel can be blown down and whether the minimum design metal temperature is violated during rapid cooling.
- **Compressor surge protection** requires millisecond-level response modeling to verify that the anti-surge system can prevent surge during rapid load changes.

This chapter presents the fundamentals of dynamic simulation and process control, then demonstrates how to implement dynamic models using NeqSim's transient simulation capabilities.

### 29.1.1 Steady-State vs Dynamic Simulation

The fundamental difference between steady-state and dynamic simulation lies in the treatment of time and accumulation:

| Aspect | Steady-State | Dynamic |
|--------|-------------|---------|
| Time | Not considered | Independent variable |
| Accumulation | Zero (in = out) | Non-zero (in − out = accumulation) |
| Equations | Algebraic (AE) | Differential-algebraic (DAE) |
| Holdup | Not tracked | Tracked (mass, energy, momentum) |
| Controllers | Set points achieved instantly | Response depends on tuning |
| Disturbances | Single operating point | Time-varying inputs |
| Computation | One solution | Solution at every timestep |

In steady-state simulation, the material balance for any unit is:

$$
\sum \dot{m}_{\text{in}} = \sum \dot{m}_{\text{out}}
$$

In dynamic simulation, this becomes:

$$
\frac{dM}{dt} = \sum \dot{m}_{\text{in}} - \sum \dot{m}_{\text{out}}
$$

where $M$ is the total mass holdup in the equipment.

---

## 29.2 Dynamic Modeling Fundamentals

### 29.2.1 Conservation Equations

The dynamic behavior of any process unit is governed by three fundamental conservation laws applied to a control volume.

**Mass balance** for each component $i$:

$$
\frac{d(M x_i)}{dt} = \sum_k \dot{m}_{k,\text{in}} x_{i,k,\text{in}} - \sum_j \dot{m}_{j,\text{out}} x_{i,j,\text{out}}
$$

where $M$ is the total mass in the vessel, $x_i$ is the mass fraction of component $i$, and the sums run over all inlet streams $k$ and outlet streams $j$.

**Energy balance**:

$$
\frac{d(M u)}{dt} = \sum_k \dot{m}_{k,\text{in}} h_{k,\text{in}} - \sum_j \dot{m}_{j,\text{out}} h_{j,\text{out}} + \dot{Q} - \dot{W}
$$

where $u$ is the specific internal energy, $h$ is the specific enthalpy, $\dot{Q}$ is the heat transfer rate (positive into the system), and $\dot{W}$ is the work rate (positive out of the system).

**Momentum balance** (simplified for pipe flow):

$$
\frac{\partial (\rho v)}{\partial t} + \frac{\partial (\rho v^2)}{\partial z} = -\frac{\partial P}{\partial z} - \rho g \sin\theta - \frac{f \rho v |v|}{2D}
$$

where $\rho$ is the fluid density, $v$ is the velocity, $P$ is pressure, $g$ is gravitational acceleration, $\theta$ is the pipe inclination, $f$ is the Darcy friction factor, and $D$ is the pipe diameter.

### 29.2.2 Holdup and Inventory

The **holdup** (or inventory) is the total amount of material stored within a process unit at any instant. In a separator, the liquid holdup determines the liquid level:

$$
V_L = \frac{M_L}{\rho_L}
$$

The liquid level $h$ depends on the vessel geometry. For a horizontal cylindrical vessel of diameter $D$ and length $L$:

$$
V_L = L \left[ \frac{D^2}{4} \cos^{-1}\left(1 - \frac{2h}{D}\right) - \left(\frac{D}{2} - h\right)\sqrt{h(D-h)} \right]
$$

The time derivative of the level is related to the net liquid flow:

$$
\frac{dh}{dt} = \frac{\dot{m}_{L,\text{in}} - \dot{m}_{L,\text{out}}}{\rho_L A_{\text{cross}}(h)}
$$

Here $A_{\text{cross}}(h)=dV_L/dh=2L\sqrt{h(D-h)}$ is the horizontal free-surface area. This simplified level balance assumes constant liquid density and negligible interphase mass transfer; the NeqSim example below instead integrates component inventory and energy before flashing.

### 29.2.3 Time Constants and Dead Time

The dynamic response of process equipment is characterized by two fundamental parameters:

**Time constant** ($\tau$): The time required for the output to reach 63.2% of its final value after a step change in input. A residence-time scale, distinct from a level-loop time constant, is:

$$
t_{\mathrm{res}} = \frac{V_L}{\dot{V}_L}
$$

For 10 m³ of liquid inventory and 100 m³/hr liquid throughput, this ratio is a residence time of 360 s. It is not generally the level-loop time constant: with fixed withdrawal, level integrates the inlet–outlet mismatch and has no finite open-loop settling time. A first-order level time constant requires a specified level-dependent outlet relation or an identified closed-loop model \cite{skogestad2003simc}.

**Dead time** ($\theta$): The time delay between a change in input and the first observable response in the output. Dead time arises from transport delays (fluid flowing through a pipe), measurement delays (sensor response time), and computational delays (controller scan interval). For a pipeline:

$$
\theta = \frac{L_{\text{pipe}}}{v_{\text{fluid}}}
$$

The ratio $\theta / \tau$ is a critical parameter for controller design. Systems with $\theta / \tau > 1$ are inherently difficult to control because the controller is always responding to outdated information.

### 29.2.4 Linearization and Transfer Functions

For controller design, the nonlinear dynamic equations are often linearized around a steady-state operating point. A first-order system with dead time has the transfer function:

$$
G(s) = \frac{K_p e^{-\theta s}}{\tau s + 1}
$$

where $K_p$ is the process gain, $\tau$ is the time constant, $\theta$ is the dead time, and $s$ is the Laplace variable.

A second-order system (e.g., two tanks in series) has:

$$
G(s) = \frac{K_p e^{-\theta s}}{(\tau_1 s + 1)(\tau_2 s + 1)}
$$

These transfer functions form the basis for analytical controller tuning methods described in Section 29.3.

---

## 29.3 Process Control Fundamentals

### 29.3.1 The Feedback Control Loop

A feedback control loop consists of four elements:

1. **Sensor/transmitter** — measures the controlled variable (PV, process variable)
2. **Controller** — compares PV with the set point (SP) and computes a control action
3. **Final control element** — actuates the control action (typically a control valve)
4. **Process** — the physical system being controlled

The error signal is:

$$
e(t) = \text{SP}(t) - \text{PV}(t)
$$

The controller manipulates the output (OP) to drive the error toward zero.

![Feedback control loop showing sensor, controller, final element, and process](figures/feedback_control_loop.png)

### 29.3.2 PID Controller

The Proportional–Integral–Derivative (PID) controller is the workhorse of industrial process control. PID is widely used in regulatory process control. The ideal PID controller output is:

$$
\text{OP}(t) = K_c \left[ e(t) + \frac{1}{T_i} \int_0^t e(\tau) \, d\tau + T_d \frac{de(t)}{dt} \right] + \text{OP}_{\text{bias}}
$$

where:

- $K_c$ is the **controller gain** (proportional action)
- $T_i$ is the **integral time** (seconds) — eliminates steady-state offset
- $T_d$ is the **derivative time** (seconds) — provides anticipatory action
- $\text{OP}_{\text{bias}}$ is the controller output at zero error

**Proportional-only (P)** control: $T_i = \infty$, $T_d = 0$. Fast but leaves a permanent offset.

**Proportional-integral (PI)** control: $T_d = 0$. Eliminates offset. Used for most flow, pressure, and level loops.

**Full PID** control: All three terms active. Used for temperature loops and other processes with significant dead time.

| Controller Type | Advantages | Disadvantages | Typical Applications |
|----------------|-----------|---------------|---------------------|
| P | Fast, stable, simple | Permanent offset | Buffer tank levels |
| PI | No offset, robust | Slower than P, integral windup | Flow, pressure, level |
| PID | Anticipatory, handles dead time | Sensitive to noise, complex tuning | Temperature, composition |

### 29.3.3 Controller Tuning Methods

Controller tuning determines the values of $K_c$, $T_i$, and $T_d$ for a specific process. The three most widely used classical methods are:

**Ziegler–Nichols open-loop method.** Apply a step change to the controller output and measure the process response. Fit a first-order-plus-dead-time (FOPDT) model: $K_p$, $\tau$, $\theta$.

| Controller | $K_c$ | $T_i$ | $T_d$ |
|-----------|-------|-------|-------|
| P | $\frac{\tau}{K_p \theta}$ | — | — |
| PI | $\frac{0.9 \tau}{K_p \theta}$ | $3.33 \theta$ | — |
| PID | $\frac{1.2 \tau}{K_p \theta}$ | $2.0 \theta$ | $0.5 \theta$ |

**Cohen–Coon method.** Similar to Ziegler–Nichols but with corrections that give better performance when $\theta / \tau$ is large:

$$
K_c = \frac{1}{K_p} \frac{\tau}{\theta} \left( \frac{4}{3} + \frac{\theta}{4\tau} \right)
$$

$$
T_i = \theta \frac{32 + 6\theta/\tau}{13 + 8\theta/\tau}
$$

$$
T_d = \theta \frac{4}{11 + 2\theta/\tau}
$$

**SIMC PI tuning.** For a stable FOPDT process with gain $K_p$, time constant $\tau$ and delay $\theta$, use the following PI starting values \cite{skogestad2003simc}:

$$
K_c=\frac{\tau}{K_p(\lambda+\theta)},\qquad
T_i=\min[\tau,4(\lambda+\theta)],\qquad T_d=0.
$$

The desired response time $\lambda$ is a tuning choice; choosing it at least as large as the effective delay is a conservative starting point, not a universal stability guarantee. The sign must produce negative feedback. Integrating processes require the integrating-process gain form. Derivative tuning depends on the identified lag structure and PID implementation; adding $T_d=\theta/2$ to this PI rule is not the SIMC rule.

### 29.3.4 Controller Action — Direct vs Reverse

A controller can be **direct-acting** or **reverse-acting**:

- **Direct acting**: Measurement rises and the manipulated output rises. Both an opening gas outlet valve for pressure control and an opening liquid outlet valve for level control normally require this action.
- **Reverse acting**: Measurement rises and the manipulated output falls; for example, a heating-duty command falls when outlet temperature rises.

The preceding mathematical PID uses $e=SP-PV$. NeqSim's `ControllerDeviceBaseClass` internally uses $PV-SP$; `setReverseActing(False)` therefore gives direct action for positive gain. The level transmitter returns a fraction from 0 to 1, so a 50% level setpoint is `0.5`, not `50`. Test the sign of the complete actuator–process path with a small perturbation; valve fail position alone does not determine the required feedback sign.

---

## 29.4 Advanced Control Strategies

### 29.4.1 Cascade Control

In cascade control, the output of a **primary (master) controller** becomes the set point of a **secondary (slave) controller**. This improves rejection of disturbances that affect the secondary variable before they reach the primary variable.

**Example**: Separator level control using cascade. The primary controller is a level controller (LC) that adjusts the set point of a secondary flow controller (FC) on the liquid outlet. The flow loop rapidly tracks the flow setpoint requested by the level controller and rejects disturbances in the outlet path.

$$
\text{LC output} \xrightarrow{\text{SP}} \text{FC} \xrightarrow{\text{OP}} \text{Valve}
$$

A secondary loop several times faster than the primary is a useful design aim; identify both responses and check their interaction. An outlet flow controller rejects outlet-pressure and valve disturbances. It does not detect an incoming slug before the level changes unless a separate feedforward measurement supplies that information.

### 29.4.2 Feedforward Control

Feedforward control measures a disturbance before it affects the controlled variable and takes preemptive corrective action. Combined with feedback (feedforward + feedback), it provides the best disturbance rejection.

**Example**: The flow rate of a multiphase well fluctuates. A feedforward signal from the wellhead flow transmitter adjusts the separator liquid outlet valve before the level is affected.

$$
\text{OP}_{\text{ff}} = -\frac{G_d(s)}{G_p(s)} D(s)
$$

where $G_d$ is the disturbance transfer function and $G_p$ is the process transfer function.

### 29.4.3 Ratio Control

Ratio control maintains a fixed ratio between two flow rates. Common applications:

- Chemical injection (inhibitor-to-production-fluid ratio)
- Air-to-fuel ratio for gas turbines and fired heaters
- Water-to-oil ratio in desalters

$$
\text{SP}_{\text{slave}} = R \cdot \text{PV}_{\text{wild flow}}
$$

where $R$ is the desired ratio.

### 29.4.4 Split-Range Control

In split-range control, a single controller output drives two (or more) final control elements over different portions of its range. A common example is pressure control where:

- 0–50% output: modulates gas sales valve (normal pressure regulation)
- 50–100% output: opens flare valve (overpressure relief)

A designed split-range sequence can coordinate these valves. This regulatory strategy is separate from independent pressure relief and shutdown functions; a numerical output split alone establishes neither smooth transitions nor protection adequacy.

---

## 29.5 Separator Level Control

Separator level control is the most fundamental control loop in oil and gas production facilities. The separator must maintain the liquid level within a target range to ensure:

- Adequate gas–liquid separation (level too high reduces gas residence time)
- Adequate liquid retention time (level too low reduces separation quality)
- Continuous liquid outlet flow (level too low causes gas blowthrough)
- No liquid carryover to gas systems (level too high)

### 29.5.1 Averaging vs Tight Level Control

The control philosophy for separator level depends on the downstream process:

**Averaging level control** uses low controller gain to absorb flow disturbances. The level is allowed to vary within a wide band, and the outlet flow remains relatively smooth. This is preferred when the downstream process (e.g., a heater or another separator) is sensitive to flow disturbances.

$$
K_c = \frac{2 \Delta F_{\max}}{(h_{\max} - h_{\min}) K_v}
$$

where $\Delta F_{\max}$ is the maximum flow disturbance, $h_{\max}$ and $h_{\min}$ define the allowable level band, and $K_v$ is the valve gain.

**Tight level control** uses high controller gain to maintain the level close to the set point. The outlet flow varies aggressively to absorb any disturbance. This is used when the downstream process can tolerate flow variability but the level must be controlled tightly (e.g., to prevent trips on high or low level).

### 29.5.2 NeqSim Implementation — Separator Level Control

The following example checks a NeqSim two-component SRK vessel with explicit inventory initialization, VU flashes and a PI controller acting on prescribed liquid withdrawal. Gas withdrawal is fixed. The 2.0 kg/s feed rises to 2.4 kg/s for 20 s; this is a defined feed pulse, not a pipeline slug prediction. The controller output is a liquid mass-flow command in kg/s, with gain 0.10 kg/s per percentage point of level, integral time 30 s and bounds 0–6 kg/s. It is not a valve-hydraulics or pressure-control model. Each time step uses a new calculation identity, because controllers suppress repeated execution for the same identity \cite{neqsim2026update}.

```python
from pathlib import Path
import json
import jpype
import numpy as np
import matplotlib.pyplot as plt
jneqsim = jpype.JPackage("neqsim")
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
Path("figures").mkdir(exist_ok=True)
def dynamic_case(dt, slug=False):
    fluid = jneqsim.thermo.system.SystemSrkEos(313.15, 30.0)
    fluid.addComponent("methane", 0.5)
    fluid.addComponent("n-heptane", 0.5)
    fluid.setMixingRule("classic")
    inlet = Stream("Dynamic feed", fluid)
    inlet.setFlowRate(2.0, "kg/sec")
    inlet.run()
    vessel = Separator("Inventory vessel", inlet)
    vessel.setInternalDiameter(1.0)
    vessel.setSeparatorLength(3.0)
    vessel.setLiquidLevel(0.5)
    vessel.run()
    vessel.setCalculateSteadyState(False)
    vessel.initializeTransientCalculation()
    gasout = vessel.getGasOutStream()
    liquidout = vessel.getLiquidOutStream()
    basegas = float(gasout.getFlowRate("kg/sec"))
    baseliquid = float(liquidout.getFlowRate("kg/sec"))
    LT = jneqsim.process.measurementdevice.LevelTransmitter("LT", vessel)
    controller = jneqsim.process.controllerdevice.ControllerDeviceBaseClass()
    controller.setTransmitter(LT)
    setpoint = float(vessel.getLiquidLevel())
    controller.setControllerSetPoint(setpoint)
    controller.setReverseActing(False)
    controller.setControllerParameters(0.10, 30.0, 0.0)
    controller.setOutputLimits(0.0, 6.0)
    command = baseliquid
    identity = jpype.java.util.UUID.randomUUID()
    inventory = vessel.getThermoSystem()
    mass0 = float(inventory.getTotalNumberOfMoles()*inventory.getMolarMass())
    energy0 = float(inventory.getInternalEnergy())
    balance_mass = balance_energy = 0.0
    max_mass = max_energy = 0.0
    series = []
    for step in range(round(120.0/dt)):
        t = step*dt
        identity = jpype.java.util.UUID.randomUUID()
        pulse = 3.0 if slug else 2.4
        inlet.setFlowRate(pulse if 20.0 <= t < 40.0 else 2.0, "kg/sec")
        inlet.run()
        controller.runTransient(command, dt, identity)
        command = min(6.0, max(0.0, float(controller.getResponse())))
        gasout.setFlowRate(basegas, "kg/sec")
        liquidout.setFlowRate(command, "kg/sec")
        gasout.run()
        liquidout.run()
        net_mass = float(inlet.getFlowRate("kg/sec")-gasout.getFlowRate("kg/sec")-liquidout.getFlowRate("kg/sec"))
        net_energy = float(inlet.getFluid().getEnthalpy()-gasout.getFluid().getEnthalpy()-liquidout.getFluid().getEnthalpy())
        balance_mass += dt*net_mass
        balance_energy += dt*net_energy
        vessel.runTransient(dt, identity)
        inventory = vessel.getThermoSystem()
        mass = float(inventory.getTotalNumberOfMoles()*inventory.getMolarMass())
        energy = float(inventory.getInternalEnergy())
        mass_error = abs(mass-mass0-balance_mass)/mass0
        energy_error = abs(energy-energy0-balance_energy)/max(abs(energy0),1.0)
        max_mass = max(max_mass, mass_error)
        max_energy = max(max_energy, energy_error)
        row = [t+dt, float(vessel.getLiquidLevel()), float(inventory.getPressure("bara")), float(inventory.getTemperature("C")), mass, command]
        assert all(np.isfinite(row)) and 0.0 < row[1] < 1.0
        series.append(row)
    assert max_mass < 1e-10 and max_energy < 1e-5
    globals()["sep"] = vessel  # inspected by the later instrumentation examples
    return dict(dt=dt, mass0_kg=mass0, energy0_J=energy0,
                setpoint_fraction=setpoint, base_liquid_kg_s=baseliquid,
                max_mass_relative_residual=max_mass, max_energy_relative_residual=max_energy,
                series=series)

coarse = dynamic_case(0.5)
fine = dynamic_case(0.25)
coarse_rows = np.asarray(coarse["series"])
fine_rows = np.asarray(fine["series"])
assert np.max(np.abs(coarse_rows[:, 1]-fine_rows[1::2, 1])) < 0.001
assert np.max(np.abs(coarse_rows[:, 2]-fine_rows[1::2, 2])) < 0.01
assert abs(fine_rows[-1, 1]-fine["setpoint_fraction"]) < 0.002
assert np.max(fine_rows[:, 5]) > fine["base_liquid_kg_s"]
print("Initial inventory kg:", fine["mass0_kg"])
print("Final time, level fraction, pressure bara, temperature C, mass kg, liquid kg/s:")
print(fine_rows[-1].tolist())
print("Maximum relative mass/energy residuals:",
      fine["max_mass_relative_residual"], fine["max_energy_relative_residual"])
with open("ch29_inventory_checks.json", "w") as handle:
    json.dump({"coarse": coarse, "fine": fine}, handle, indent=2)
fig, axes = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
for ax, column, label in zip(axes, [1, 2, 5],
        ["Liquid level / diameter", "Pressure (bara)", "Liquid withdrawal (kg/s)"]):
    ax.plot(fine_rows[:, 0], fine_rows[:, column], label="dt = 0.25 s")
    ax.plot(coarse_rows[:, 0], coarse_rows[:, column], "--", label="dt = 0.5 s")
    ax.set_ylabel(label)
    ax.grid(True, alpha=0.3)
axes[0].axhline(0.5, color="black", linewidth=0.8)
axes[0].legend()
axes[-1].set_xlabel("Time (s)")
fig.tight_layout()
fig.savefig("figures/ch29_verified_level_inventory.png", dpi=180)
# Continue the instrument examples with the final vessel from the fine run.
process = ProcessSystem()
process.add(sep)
PT100 = jneqsim.process.measurementdevice.PressureTransmitter(
    "PT-100", sep.getGasOutStream())
PT100.setUnit("bara")
```

![Checked NeqSim liquid inventory, pressure and withdrawal with timestep comparison](figures/ch29_verified_level_inventory.png)

The initial inventory is 696.53 kg. The feed pulse adds liquid and gas; direct-acting PI control increases liquid withdrawal and returns the liquid level to within 0.2 percentage points of its initial value by 120 s. Gas withdrawal remains fixed, so the pressure rises to about 30.64 bara rather than returning to 30 bara. This distinction makes the modeled control boundary visible.

The code integrates the actual boundary mass and enthalpy rates independently of the vessel inventory update. Required relative residuals are below $10^{-10}$ for mass and $10^{-5}$ for energy, normalized by initial mass and absolute initial internal energy. Halving the timestep must change the aligned liquid-level fraction by less than 0.001 and pressure by less than 0.01 bar. These are numerical acceptance criteria for this case; they are not plant validation or proof of trip protection.

<!-- @neqsim:claim
  test: devtools/scientific_optimization_probe.py
  baseline: verification/scientific_revision/ch29_dynamic_probe.json
-->

---

## 29.6 Pressure Control Systems

### 29.6.1 Design Considerations for Controller Selection

Before configuring any control loop, the engineer must consider the dynamic characteristics of the process and the performance requirements. Table 29.1 summarizes the recommended controller types for the most common loops in oil and gas production facilities.

| Process Variable | Controller Type | Rationale | Typical Performance |
|-----------------|----------------|-----------|-------------------|
| Separator level | PI (averaging) | Absorb flow disturbances | ±15% of span, 5–10 min settling |
| Separator pressure | PI | Moderate speed, no offset | ±1 bara, 1–3 min settling |
| Compressor suction pressure | PI | Fast response needed | ±0.5 bara, 30–60 s settling |
| Export gas temperature | PID | Large dead time | ±2°C, 5–15 min settling |
| Gas dehydration T | PID | Significant lag | ±1°C, 10–20 min settling |
| Chemical injection flow | P or PI | Flow loops are fast | ±2%, < 30 s settling |
| Furnace/heater outlet T | PID with cascade | Multiple lags | ±1°C, 5–10 min settling |

The choice between PI and PID is primarily determined by the dead-time-to-time-constant ratio ($\theta/\tau$). As a rule of thumb:

- $\theta/\tau < 0.2$: PI is sufficient; derivative action adds little benefit
- $0.2 < \theta/\tau < 0.5$: PID provides noticeable improvement
- For delay-dominated processes, consider slower robust PI tuning or a validated predictor; derivative action cannot remove a pure transport delay.

### 29.6.2 Separator Pressure Control

Separator pressure is typically controlled by manipulating the gas outlet valve. The process dynamics depend on the gas volume above the liquid (the vapor space):

$$
V_g \frac{dP}{dt} = \dot{m}_{g,\text{in}} \frac{ZRT}{M_w} - \dot{m}_{g,\text{out}} \frac{ZRT}{M_w}
$$

where $V_g$ is the vapor space volume, $Z$ is the gas compressibility factor, $R$ is the universal gas constant, $T$ is temperature, and $M_w$ is the gas molecular weight.

The vapor space acts as a capacitance — larger vapor spaces provide more damping and slower pressure dynamics. For fixed gas volume, temperature, composition and compressibility, define the gas capacitance $C_P=\partial M_g/\partial P=V_gM_w/(ZRT)$ in kg/Pa. If the local outlet relation is $\delta\dot m_{out}=K_P\delta P+K_u\delta u$, then

$$
\tau_P=\frac{C_P}{K_P},\qquad K_P=\left(\frac{\partial\dot m_{out}}{\partial P}\right)_u.
$$

Here $K_P$ has units kg/(s Pa), giving $\tau_P$ in seconds. A raw valve $C_v$ cannot replace this derivative without its dimensional flow equation. Variable temperature, real-gas compressibility, liquid level and phase transfer require the coupled inventory/energy equations.

### 29.6.3 Compressor Suction Pressure Control

When a compressor draws gas from a separator, the compressor speed or a suction throttle valve can be used to control the suction pressure. The dynamics of this loop include:

- The gas volume between the separator and compressor (pipe volume acts as a buffer)
- The compressor speed response time (ramp rate, typically 1–5%/s for variable-speed drives)
- The process lag from the separator pressure controller

The transfer function from compressor speed to suction pressure is approximately:

$$
G(s) = \frac{K_p e^{-\theta s}}{(\tau_1 s + 1)(\tau_2 s + 1)}
$$

where $\tau_1$ is the piping volume time constant, $\tau_2$ is the compressor speed response time, and $\theta$ accounts for the measurement and communication delay (typically 1–3 seconds for modern digital systems).

### 29.6.4 Back-Pressure Control on Export Systems

Export pipelines operate at a specified delivery pressure. A back-pressure controller at the platform maintains the required export pressure by adjusting the export compressor speed or a letdown valve.

---

## 29.7 Temperature Control

Temperature control in oil and gas production is typically slower than pressure or level control because heat transfer processes have larger time constants. Common temperature control applications include:

- **Inlet heater control**: Maintain wellstream temperature above hydrate formation temperature by adjusting heat input
- **Separator temperature**: Control operating temperature for optimal gas–liquid separation
- **Gas dehydration**: Control contactor temperature for TEG units
- **Export gas temperature**: Cool gas to pipeline specification
- **Heat exchanger outlet temperature**: Control cooling water or hot oil flow

The dynamic model for a shell-and-tube heat exchanger with the process fluid on the tube side is:

$$
M_t C_{p,t} \frac{dT_t}{dt} = \dot{m}_t C_{p,t} (T_{t,\text{in}} - T_t) + U A (T_s - T_t)
$$

$$
M_s C_{p,s} \frac{dT_s}{dt} = \dot{m}_s C_{p,s} (T_{s,\text{in}} - T_s) - U A (T_s - T_t)
$$

where subscripts $t$ and $s$ refer to the tube-side and shell-side fluids, $U$ is the overall heat transfer coefficient, $A$ is the heat transfer area, and $M$ is the fluid mass in each side.

Derivative action can help compensate a resolved secondary lag, but amplifies measurement noise and does not cancel pure dead time. Choose PI or filtered PID from an identified model and verify disturbance rejection.

---

## 29.8 Anti-Surge Control Systems

### 29.8.1 Compressor Surge Phenomenon

Compressor surge is a violent, potentially destructive flow reversal that occurs when the compressor discharge pressure exceeds the maximum that the compressor can develop at the current flow rate and speed. It manifests as:

- Rapid flow oscillations (forward–reverse cycling)
- Loud banging or pulsation
- Extreme mechanical vibration
- Shaft thrust reversal
- Rapid temperature rise

Surge occurs when the operating point crosses the **surge line** on the compressor map — the locus of minimum stable flow at each speed or head level.

![Compressor map showing operating point, surge line, and anti-surge control line](figures/ch20_compressor_map_antisurge.png)

### 29.8.2 Anti-Surge Control Architecture

The anti-surge control system prevents the compressor from reaching the surge line by opening a **recycle valve** when the operating point approaches the surge limit:

1. **Surge line**: The locus of minimum stable flow (from the compressor manufacturer)
2. **Surge control line (SCL)**: Offset from the surge line by a safety margin (typically 10% of surge flow)
3. **Surge trip line**: Close to the actual surge line — trips the compressor if reached
4. **Anti-surge controller**: A specialized PID controller that modulates the recycle valve

The anti-surge controller calculates a **surge parameter** $S$ from the compressor operating conditions:

$$
S = \frac{Q_{\text{actual}}}{Q_{\text{surge}}}
$$

where $Q_{\text{actual}}$ is the actual volumetric flow and $Q_{\text{surge}}$ is the flow at the surge line for the current head. When $S < 1 + \text{margin}$, the controller opens the recycle valve.

### 29.8.3 NeqSim Recycle Topology and Mass Closure

This steady-state example recycles 25% of cooled discharge and exports 75%. It checks recycle mass closure. It contains no installed surge map, recycle-valve actuator response or transient compressor model, and therefore does not demonstrate anti-surge protection.

```python
import jpype
jneqsim = jpype.JPackage("neqsim")
import numpy as np
import matplotlib.pyplot as plt

# --- Gas fluid ---
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, 20.0)
gas.addComponent("methane", 0.85)
gas.addComponent("ethane", 0.10)
gas.addComponent("propane", 0.03)
gas.addComponent("CO2", 0.02)
gas.setMixingRule("classic")

# --- Process equipment ---
Stream = jneqsim.process.equipment.stream.Stream
Compressor = jneqsim.process.equipment.compressor.Compressor
Cooler = jneqsim.process.equipment.heatexchanger.Cooler
ThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve
Mixer = jneqsim.process.equipment.mixer.Mixer
Recycle = jneqsim.process.equipment.util.Recycle
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

# Build compression with recycle
feed = Stream("compressor feed", gas)
feed.setFlowRate(100000.0, "kg/hr")
feed.setTemperature(30.0, "C")
feed.setPressure(20.0, "bara")

# Recycle mixer (combines fresh feed with recycle)
recycle_stream = feed.clone("recycle stream")
recycle_stream.setFlowRate(0.0, "kg/hr")

mixer = Mixer("suction mixer")
mixer.addStream(feed)
mixer.addStream(recycle_stream)

compressor = Compressor("1st stage compressor", mixer.getOutletStream())
compressor.setOutletPressure(60.0, "bara")
compressor.setPolytropicEfficiency(0.78)

aftercooler = Cooler("aftercooler", compressor.getOutletStream())
aftercooler.setOutTemperature(273.15 + 35.0)

# Anti-surge recycle valve
Splitter = jneqsim.process.equipment.splitter.Splitter
splitter = Splitter("product/recycle split", aftercooler.getOutletStream())
splitter.setSplitFactors([0.75, 0.25])
asv = ThrottlingValve("anti-surge valve", splitter.getSplitStream(1))
asv.setOutletPressure(20.0, "bara")

recycle = Recycle("ASV recycle")
recycle.addStream(asv.getOutletStream())
recycle.setOutletStream(recycle_stream)

process = ProcessSystem()
process.add(feed)
process.add(mixer)
process.add(compressor)
process.add(aftercooler)
process.add(splitter)
process.add(asv)
process.add(recycle)

# Run steady state
process.run()

product_rate = float(splitter.getSplitStream(0).getFlowRate("kg/hr"))
assert abs(product_rate-100000.0)/100000.0 < 1e-4
assert float(compressor.getPower("kW")) > 0.0
print(f"Product mass closure: {product_rate:.2f} kg/hr")
print(f"Compressor power: {compressor.getPower('MW'):.2f} MW")
print(f"Polytrophic head: {compressor.getPolytropicFluidHead():.1f} kJ/kg")
print(f"Discharge temperature: "
      f"{compressor.getOutletStream().getTemperature('C'):.1f} °C")
```

### 29.8.4 Dynamic Anti-Surge Response

In a real anti-surge system, the controller must respond within 100–500 ms to prevent surge. The key performance requirements are:

| Parameter | Typical Requirement |
|-----------|-------------------|
| Controller scan time | 20–50 ms |
| Valve stroke time (full open) | 1–2 seconds |
| Detection to response time | < 300 ms |
| Recycle valve $C_v$ | Sized for 100% of surge flow at minimum $\Delta P$ |
| Safety margin | 10–15% of surge flow |

The anti-surge controller is typically a PI controller with high gain and short integral time:

$$
K_c = 3\text{–}5, \quad T_i = 2\text{–}5 \text{ s}
$$

The derivative term is usually not used because the surge signal is inherently noisy.

---

## 29.9 Depressurization and Blowdown

### 29.9.1 Why Depressurization Matters

Emergency depressurization (EDP) is the controlled venting of pressurized equipment to a flare or vent system in response to a fire or gas release. The objectives are:

1. **Reduce the stress**: Lower the vessel pressure (and hence wall stress) before the metal temperature rises to the point of rupture
2. **Minimize hydrocarbon inventory**: Reduce the amount of flammable material available to feed a fire
3. **Achieve the scenario-specific pressure target**: establish the pressure–time requirement from the governing design basis, current applicable standard, fire/rupture analysis and equipment limits. API 521 gives guidance for depressuring-system design; 50% pressure, 6.9 barg and 15 min are not interchangeable universal requirements. This chapter has not verified a NORSOK clause for such a blanket rule \cite{api521scope}.

### 29.9.2 Physics of Blowdown

For a rigid, well-mixed vessel, with no inlet, no shaft work and negligible kinetic/potential energy, the appropriate open-system equations are

$$
\frac{dM}{dt}=-\dot m_{out},\qquad
\frac{d(Mu)}{dt}=-\dot m_{out}h_{out}+\dot Q_{wall}.
$$

For an ideal gas with constant heat capacities, $u=c_vT$, $h=c_pT$, and $P=MR_sT/V$:

$$
\frac{dT}{dt}=-(\gamma-1)\frac{\dot m_{out}}{M}T
+\frac{\dot Q_{wall}}{Mc_v},\qquad
\frac{1}{P}\frac{dP}{dt}=\frac{1}{M}\frac{dM}{dt}+\frac{1}{T}\frac{dT}{dt}.
$$

Here $\gamma=c_p/c_v$ and $R_s=R/M_w$. The vessel cools because the escaping stream removes enthalpy while the remaining inventory stores internal energy. This occurs even for an ideal gas whose Joule–Thomson coefficient is zero. The valve's approximately isenthalpic expansion is a separate process. Omitting the temperature term from the pressure derivative while simultaneously modeling cooling is inconsistent.

Real-gas blowdown requires the EOS, changing phase composition, outlet flow law and heat transfer. Fluid temperature alone is not metal temperature: a thermal wall model and stress/fracture assessment are needed for a material-temperature decision. API 521 provides the relevant design framework \cite{api521scope}.

### 29.9.3 Checked NeqSim Depressurization Simulation

The 1 m diameter, 3 m long SRK vessel starts at 80 bara and 40 °C with 95/5 mol% methane/ethane. A valve with declared $C_v=1$ discharges to 1.01325 bara for 120 s. Heat input is zero and wall dynamics are omitted. A $10^{-6}$ kg/s inlet regularizes this implementation's zero-flow stream properties; its total contribution is below one part per million of initial inventory and is included in both balances. This is a numerically checked approximation to isolation, not a validated emergency-depressuring design. The flow law is evaluated before each explicit inventory step.

```python
def blowdown_case(dt):
    fluid=jneqsim.thermo.system.SystemSrkEos(313.15,80.0)
    fluid.addComponent("methane",0.95)
    fluid.addComponent("ethane",0.05)
    fluid.setMixingRule("classic")
    inlet=Stream("Isolated inlet",fluid)
    inlet.setFlowRate(1000.0,"kg/hr")
    inlet.run()
    vessel=Separator("Blowdown vessel",inlet)
    vessel.setInternalDiameter(1.0)
    vessel.setSeparatorLength(3.0)
    vessel.setLiquidLevel(0.0)
    vessel.run()
    gasout=vessel.getGasOutStream()
    liquidout=vessel.getLiquidOutStream()
    valve=jneqsim.process.equipment.valve.ThrottlingValve("BDV",gasout)
    valve.setOutletPressure(1.01325,"bara")
    valve.setCv(1.0)
    valve.run()
    vessel.setCalculateSteadyState(False)
    vessel.initializeTransientCalculation()
    valve.setCalculateSteadyState(False)
    inlet.setFlowRate(1.0e-6,"kg/sec")
    inlet.run()
    inventory=vessel.getThermoSystem()
    mass0=float(inventory.getTotalNumberOfMoles()*inventory.getMolarMass())
    energy0=float(inventory.getInternalEnergy())
    mass_out=energy_out=0.0
    max_mass=max_energy=0.0
    series=[]
    for step in range(round(120.0/dt)):
        identity=jpype.java.util.UUID.randomUUID()
        valve.runTransient(dt,identity)
        liquidout.setFlowRate(0.0,"kg/sec")
        gasout.run()
        flow=float(gasout.getFlowRate("kg/sec"))
        mass_out+=dt*(flow-float(inlet.getFlowRate("kg/sec")))
        energy_out+=dt*float(gasout.getFluid().getEnthalpy()-inlet.getFluid().getEnthalpy())
        vessel.runTransient(dt,identity)
        inventory=vessel.getThermoSystem()
        mass=float(inventory.getTotalNumberOfMoles()*inventory.getMolarMass())
        energy=float(inventory.getInternalEnergy())
        max_mass=max(max_mass,abs(mass-mass0+mass_out)/mass0)
        max_energy=max(max_energy,abs(energy-energy0+energy_out)/abs(energy0))
        series.append([(step+1)*dt,float(inventory.getPressure("bara")),float(inventory.getTemperature("C")),mass,flow])
    return dict(dt=dt,mass0_kg=mass0,max_mass_relative_residual=max_mass,
                max_energy_relative_residual=max_energy,series=series)

bd_coarse = blowdown_case(0.5)
bd_fine = blowdown_case(0.25)
bc = np.asarray(bd_coarse["series"])
bf = np.asarray(bd_fine["series"])
for case in [bd_coarse, bd_fine]:
    assert case["max_mass_relative_residual"] < 1e-10
    assert case["max_energy_relative_residual"] < 1e-3
assert np.max(np.abs(bc[:, 1]-bf[1::2, 1])) < 0.05
assert np.max(np.abs(bc[:, 2]-bf[1::2, 2])) < 0.1
assert np.all(np.diff(bf[:, 1]) < 0.0)
assert bf[-1, 1] < 80.0 and bf[-1, 2] < 40.0
assert 120.0e-6/bd_fine["mass0_kg"] < 1e-6
print("Final blowdown time s, pressure bara, fluid C, inventory kg, outlet kg/s:")
print(bf[-1].tolist())
with open("ch29_blowdown_checks.json", "w") as handle:
    json.dump({"coarse": bd_coarse, "fine": bd_fine}, handle, indent=2)
fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
for ax, column, label in zip(axes, [1, 2], ["Pressure (bara)", "Fluid temperature (C)"]):
    ax.plot(bf[:, 0], bf[:, column], label="dt = 0.25 s")
    ax.plot(bc[:, 0], bc[:, column], "--", label="dt = 0.5 s")
    ax.set_ylabel(label)
    ax.grid(True, alpha=0.3)
axes[0].legend()
axes[-1].set_xlabel("Time (s)")
fig.tight_layout()
fig.savefig("figures/ch29_verified_blowdown.png", dpi=180)
```

![Checked real-gas vessel depressurization with timestep comparison](figures/ch29_verified_blowdown.png)

The fine-grid calculation reduces pressure to about 52.98 bara and fluid temperature to 9.12 °C after 120 s. The independent inventory checks require relative mass closure below $10^{-10}$ and energy closure below $10^{-3}$. Halving the step from 0.5 to 0.25 s must change pressure by less than 0.05 bar and temperature by less than 0.1 °C at aligned times. These checks qualify the numerical trajectory over the stated 120 s interval; they do not establish a 15-minute target, wall temperature, MDMT compliance or flare-system adequacy.

<!-- @neqsim:claim
  test: devtools/scientific_optimization_probe.py
  baseline: verification/scientific_revision/ch29_blowdown_probe.json
-->

---

## 29.10 Dynamic Slug Handling

### 29.10.1 Slug Flow in Pipelines

Slug flow is one of the most challenging dynamic phenomena in offshore production. Slugs are large liquid masses that travel intermittently through pipelines, causing:

- Sudden surges of liquid at the receiving separator
- Rapid pressure fluctuations
- Level control upsets
- Potential for liquid carryover to gas systems

The two main types of slugs are:

**Hydrodynamic slugs** arise from the inherent instability of stratified flow. They are relatively short (10–100 pipe diameters) and frequent.

**Terrain-induced slugs** (riser slugging) occur at low points in the pipeline profile, especially at the base of a riser. Liquid accumulates at the low point until the gas pressure behind it overcomes the hydrostatic head. These slugs can be enormous — holding the entire liquid inventory of the riser — and arrive at irregular, long intervals.

Severe-slug periods depend on upstream gas compressibility, liquid accumulation, geometry, backpressure and operating rates. A dimensional ratio such as gas velocity divided by riser height is not a qualified frequency correlation. Use a validated transient flow model or measured arrival history for separator sizing.

### 29.10.2 Slug Catcher and Separator Sizing

The separator (or slug catcher) must have sufficient liquid surge volume to absorb the slug without tripping on high level. The required surge volume is:

$$
V_{\text{surge,required}}=\max_t\left[0,\int_0^t\left(\dot V_{L,in}(s)-\dot V_{L,out}(s)\right)ds\right]
$$

Use actual liquid volumes at consistent separator conditions. Include the base inflow as well as the excess slug volume, the available level band, phase transfer and the time-dependent downstream withdrawal. The constant-density integral is a sizing approximation.

### 29.10.3 Control Strategies for Slug Handling

Several control strategies help manage slugs:

1. **Robust averaging level control** with a wide level band and low gain allows the separator level to absorb the slug without transmitting flow disturbances downstream
2. **Feed-forward from pipeline instrumentation** detects an approaching slug (e.g., through gamma densitometry or pressure signature analysis) and pre-adjusts the separator level to create additional surge volume
3. **Active slug control** at the wellhead or riser base modulates the choke valve to suppress riser slugging before it develops. This technique, pioneered on North Sea platforms, can eliminate severe slugging entirely
4. **Split-range outlet control** provides additional liquid handling capacity during slug events by opening a bypass valve when the primary outlet valve reaches its limit

The combination of slug catcher sizing and control strategy must be validated through dynamic simulation. The simulation must capture the slug arrival profile (flow rate vs time), the separator level dynamics, and the downstream system response. A poorly tuned level controller can amplify slug-induced disturbances rather than attenuating them.

### 29.10.4 NeqSim Dynamic Slug Response Example

The following bounded stress test reuses the checked vessel and increases its total-feed pulse to 3 kg/s. Both gas and liquid components increase; a measured liquid-only slug would require a separate composition/flow trajectory. The declared limit is a 0.60 liquid-level fraction.

```python
# A prescribed total-feed pulse tests vessel response, not slug generation.
slug = dynamic_case(0.25, slug=True)
slug_rows = np.asarray(slug["series"])
assert slug["max_mass_relative_residual"] < 1e-10
assert slug["max_energy_relative_residual"] < 1e-5
assert np.max(slug_rows[:, 1]) < 0.60
plt.figure(figsize=(8, 4))
plt.plot(slug_rows[:, 0], slug_rows[:, 1], label="3 kg/s pulse from 20 to 40 s")
plt.axhline(0.5, color="black", linestyle="--", label="Level setpoint")
plt.axhline(0.60, color="red", linestyle=":", label="Declared test limit")
plt.xlabel("Time (s)")
plt.ylabel("Liquid level / diameter")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("figures/ch29_verified_feed_pulse.png", dpi=180)
print("Peak level fraction:", float(np.max(slug_rows[:, 1])))
```

![Checked vessel response to the prescribed feed pulse](figures/ch29_verified_feed_pulse.png)

---

## 29.11 Measurement Devices in NeqSim

NeqSim provides a comprehensive set of measurement device classes that mirror real plant instrumentation:

| Device | NeqSim Class | Measurement | Typical Tag |
|--------|-------------|-------------|-------------|
| Pressure transmitter | `PressureTransmitter` | Pressure (bara, barg, psi) | PT-xxx |
| Temperature transmitter | `TemperatureTransmitter` | Temperature (°C, K, °F) | TT-xxx |
| Level transmitter | `LevelTransmitter` | Level fraction (empty unit string); multiply by vessel height for m | LT-xxx |
| Volume flow transmitter | `VolumeFlowTransmitter` | Volumetric flow (m³/hr) | FT-xxx |
| Differential pressure | Difference of two pressure measurements | Explicit upstream-minus-downstream pressure | PDT-xxx |

### 29.11.1 Transmitter Configuration

Every transmitter should be configured with:

```python
# Range configuration
PT100.setMaximumValue(100.0)    # Upper range value (URV)
PT100.setMinimumValue(0.0)      # Lower range value (LRV)
PT100.setUnit("bara")           # Engineering unit
```

The transmitter output is the measured value in engineering units. In a real plant, the transmitter would convert this to a 4–20 mA signal; in NeqSim, the value is directly available via `getMeasuredValue()`.

### 29.11.2 Complete Instrumented Process Example

A well-instrumented separator system typically has the following instruments:

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# ... (assume separator 'sep' is already built and added to process) ...

PressureTransmitter = jneqsim.process.measurementdevice.PressureTransmitter
TemperatureTransmitter = jneqsim.process.measurementdevice.TemperatureTransmitter
LevelTransmitter = jneqsim.process.measurementdevice.LevelTransmitter
VolumeFlowTransmitter = jneqsim.process.measurementdevice.VolumeFlowTransmitter

# Separator pressure
PT_sep = PressureTransmitter("PT-2100", sep.getGasOutStream())
PT_sep.setUnit("bara")
PT_sep.setMaximumValue(100.0)
PT_sep.setMinimumValue(0.0)

# Separator temperature
TT_sep = TemperatureTransmitter("TT-2100", sep.getGasOutStream())
TT_sep.setUnit("C")

# Separator level
LT_sep = LevelTransmitter("LT-2100", sep)
LT_sep.setUnit("")

# Gas outlet flow
FT_gas = VolumeFlowTransmitter("FT-2101", sep.getGasOutStream())
FT_gas.setUnit("m3/hr")

# Liquid outlet flow
FT_liq = VolumeFlowTransmitter("FT-2102", sep.getLiquidOutStream())
FT_liq.setUnit("m3/hr")

# Add all to process
for device in [PT_sep, TT_sep, LT_sep, FT_gas, FT_liq]:
    process.add(device)
```

---

## 29.12 Dynamic Simulation Workflow

### 29.12.1 Step-by-Step Methodology

A systematic approach to dynamic simulation in NeqSim follows these steps:

1. **Build the steady-state model** first. Verify that the process converges and gives physically reasonable results. All equipment, streams, and unit operations must be configured.

2. **Set equipment dimensions** for any vessel that participates in level dynamics. The separator `setInternalDiameter()` and `setSeparatorLength()` must be set to compute the liquid holdup vs level relationship.

3. **Add measurement devices**. Configure the range and units for each transmitter. Place transmitters on the correct equipment or stream.

4. **Add controllers**. Configure the set point, gain, integral time, and derivative time. Attach each controller to a transmitter (measurement) and a final control element (valve).

5. **Run steady state** with `process.run()`. Verify that all measurements read sensible values and all controllers are initialized at their set points.

6. **Activate inventory dynamics** explicitly with `setCalculateSteadyState(False)` for the vessel and appropriate dynamic equipment, initialize inventory, and verify that mass actually accumulates. A call to `runTransient(dt)` can delegate to a steady-state run when this flag is unchanged. Then run the transient steps. Choose a timestep that is:
   - Small enough for numerical stability (typically 0.1–1.0 s for process dynamics)
   - Small enough for the fastest controller (anti-surge may need 0.05 s)
   - Large enough to keep computation time manageable

7. **Introduce disturbances** at known times and observe the response. Record time histories of all relevant variables.

8. **Analyze results**: settling time, overshoot, offset, oscillation frequency. Compare with design requirements.

### 29.12.2 Timestep Selection Guidelines

| Application | Recommended $\Delta t$ (s) | Rationale |
|------------|--------------------------|-----------|
| Separator level dynamics | 1.0 | Time constant minutes to hours |
| Pressure control | 0.5–1.0 | Time constant seconds to minutes |
| Temperature dynamics | 1.0–5.0 | Slow response |
| Anti-surge control | 0.05–0.1 | Must resolve ms-level dynamics |
| Blowdown | 0.1–0.5 | Rapid pressure change |
| Pipeline slug transient | 1.0–5.0 | Slug period seconds to minutes |

### 29.12.3 Common Pitfalls

**Pitfall 1: No steady-state initialization.** Always call `process.run()` before `runTransient()`. Starting a dynamic simulation from an unconverged state leads to large initial transients that obscure the actual disturbance response.

**Pitfall 2: Controller reverse/direct action wrong.** If a controller drives the process away from the set point instead of toward it, the action is wrong. Check the sign of the process gain and the controller reverse-acting flag.

**Pitfall 3: Integral windup.** When a controller saturates (output hits its limit), the integral term continues accumulating. When the constraint is removed, the controller overshoots dramatically. Ensure anti-windup logic is included.

**Pitfall 4: Timestep too large.** If the simulation oscillates wildly or diverges, reduce the timestep. A good rule of thumb: $\Delta t \leq 0.1 \cdot \tau_{\min}$, where $\tau_{\min}$ is the smallest time constant in the system.

**Pitfall 5: Missing `initProperties()` after flash.** After any flash calculation (`TPflash`, `PHflash`, `PSflash`), you must call `fluid.initProperties()` before reading transport properties like viscosity or thermal conductivity. The `init(3)` method alone does not initialize transport properties. Without `initProperties()`, methods like `getViscosity()` and `getThermalConductivity()` may return zero, causing incorrect heat transfer and pressure drop calculations.

**Pitfall 6: Ignoring measurement device dynamics.** Real transmitters have filtering, damping, and scan rates that affect the controller's perception of the process. A controller tuned on the "true" process variable may oscillate when connected through a realistic transmitter with a 3-second filter constant. Always include representative transmitter dynamics in your simulation.

### 29.12.4 Verification and Validation

Dynamic simulation results must be verified and validated before they can be used for engineering decisions:

- **Verification**: Check that conservation laws are satisfied at every timestep. The total mass and energy in the system should equal the initial inventory plus net inflows minus net outflows. A mass balance error exceeding 0.1% over the simulation period typically indicates a numerical problem or an incorrect model configuration.
- **Validation**: Compare simulation results against plant data from the DCS historian during known upset events. For control system studies, overlay the simulated controller response with the actual DCS recording. Key validation metrics include: time to first peak, peak overshoot and settling time, with tolerances justified by measurement uncertainty and the consequence of the modeled decision.

---

## 29.13 Multi-Loop Interaction and Decoupling

### 29.13.1 Loop Interaction in Separators

In a three-phase separator, the pressure, oil level, and water level control loops interact because:

- Opening the gas valve to reduce pressure also affects the liquid levels (flash equilibrium shifts)
- Opening the oil valve to reduce oil level changes the pressure (liquid volume displaced by gas)
- Water level and oil level are coupled through the interface

The **Relative Gain Array (RGA)** quantifies the degree of interaction:

$$
\Lambda = K \circ (K^{-1})^T
$$

where $K$ is the steady-state gain matrix and $\circ$ denotes element-wise multiplication.

For a 2×2 system:

$$
\lambda_{11} = \frac{1}{1 - K_{12}K_{21}/(K_{11}K_{22})}
$$

If $\lambda_{11} \approx 1$, there is little interaction and the loops can be tuned independently. If $\lambda_{11}$ deviates significantly from 1, decoupling or sequential tuning is necessary.

### 29.13.2 Sequential Loop Tuning

For interacting loops, tune the fastest loop first (usually pressure), then the next fastest (level), then the slowest (temperature). Each successive loop sees the previous loops as disturbances that are being controlled.

---

## 29.14 Integration with Production Optimization

Dynamic simulation connects to production optimization in several ways:

### 29.14.1 Feasibility Checking

Steady-state optimization finds the theoretical best operating point, but dynamic simulation verifies that the process can actually reach that point and remain stable. A separator pressure that maximizes oil recovery may be dynamically infeasible if it causes level control instability or compressor surge.

### 29.14.2 Transition Planning

When moving from one optimized operating point to another (e.g., changing separator pressure from 50 to 45 bara), dynamic simulation determines:

- The transition trajectory (ramp rate, intermediate set points)
- Whether protective systems will trip during the transition
- The time required to reach the new steady state

### 29.14.3 Upset Recovery

Dynamic simulation identifies the most effective recovery strategy after upsets:

- How quickly should the compressor be restarted after a trip?
- What is the optimal ramp-up rate for production after a planned shutdown?
- How should the slug catcher level be managed to minimize flaring?

### 29.14.4 Controller Performance Monitoring

In a digital twin framework (Chapter 21), the dynamic model runs in parallel with the real process. Comparing the model's predicted dynamic response with the actual response reveals:

- Controllers that are detuned (actual response slower than model)
- Controllers that are too aggressive (oscillation in plant but not in model)
- Transmitters that have drifted or failed
- Valves that are sticking or have changed $C_v$

### 29.14.5 Layered Control Architecture

The integration follows a layered architecture where each layer operates on a progressively longer time horizon:

| Layer | Time Horizon | Update Rate | Function |
|-------|-------------|-------------|----------|
| Safety/ESD | Immediate | Milliseconds | Emergency shutdown, fire and gas |
| Regulatory control (PID) | Seconds to minutes | 0.1–1 s | Maintain set points |
| Supervisory control (MPC) | Minutes to hours | 1–5 min | Multi-variable coordination |
| Real-time optimization (RTO) | Hours | 15–60 min | Economic optimization |
| Planning | Days to months | Daily/weekly | Production scheduling |

Each layer assumes that the layer below it is functioning correctly. Dynamic simulation validates the performance of the lower layers (PID, supervisory) so that the upper layers (RTO, planning) can rely on them. This hierarchical decomposition is the key to practical production optimization: the steady-state optimizer (Chapter 19) computes the economic optimum, MPC ensures the facility tracks those targets while respecting constraints, and the regulatory PID loops maintain second-by-second stability.

---


<!-- reviewed-notebook-results:start -->
## Reproduced Calculation Results

These examples use the stated fluid recipes and operating assumptions. Curves represent NeqSim calculations unless a caption identifies an analytical illustration, assumed equipment map or synthetic data.

![Illustrative level response to a feed-rate step. Illustrative Python inventory and control model](figures/ch20_level_controller_response.png)

Separator Level: liquid level spans 50–54.98 % across the plotted cases. Valve Position: valve opening spans 50–67.48 % across the plotted cases.

In the illustrative Python inventory balance, a higher level commands a larger outlet opening, removing the excess inventory after the feed step. The trajectory explains controller action; it is not a NeqSim transient vessel validation. Use a validated vessel inventory and energy model before transferring controller gains to plant equipment.

![Illustrative level control: proportional-gain comparison. Illustrative Python inventory and control model](figures/ch20_pid_tuning_comparison.png)

Kp = 50.0: liquid level spans 50–64.48 % across the plotted cases. Kp = 200.0: liquid level spans 50–54.98 % across the plotted cases.

Increasing the proportional gain makes the illustrative controller respond more strongly to a level error. The smaller excursion here is conditional on the simplified process response and absence of realistic actuator limits and noise. Repeat the tuning study with valve travel, measurement delay and plant dynamics before deployment.

Selected numerical ranges from the plotted cases:

| Quantity / series | Minimum | Maximum | Unit |
|---|---:|---:|---|
| Separator Level: liquid level | 50 | 54.98 | % |
| Kp = 50.0: liquid level | 50 | 64.48 | % |

Ranges describe the sampled cases; they are not independent validation tolerances.
<!-- reviewed-notebook-results:end -->

## Summary

This chapter has covered the fundamental principles and practical implementation of dynamic simulation and process control for oil and gas production optimization:

1. **Dynamic simulation** extends steady-state modeling by tracking how process variables evolve over time, governed by mass, energy, and momentum conservation with non-zero accumulation terms.

2. **Process dynamics** are characterized by time constants (speed of response), dead time (transport/measurement delays), and the process gain. The ratio of dead time to time constant ($\theta/\tau$) determines how difficult a process is to control.

3. **PID controllers** provide the foundation for industrial process control. The proportional term provides immediate response, the integral term eliminates steady-state offset, and the derivative term provides anticipatory action.

4. **Classical tuning methods** — Ziegler–Nichols, Cohen–Coon, and IMC — provide systematic approaches to determining controller parameters from process identification experiments. IMC tuning with an adjustable closed-loop time constant offers the best balance of performance and robustness.

5. **Advanced control strategies** — cascade, feedforward, ratio, and split-range control — extend the capabilities of single-loop PID control for complex production processes.

6. **Separator level control** is the most fundamental control loop, with the choice between averaging and tight control depending on downstream process sensitivity. NeqSim's dynamic simulation capability allows testing of various tuning parameters and disturbance scenarios.

7. **Anti-surge control** protects compressors from destructive surge by monitoring the operating point relative to the surge line and rapidly opening a recycle valve when needed. Response time requirements are stringent — sub-second detection and actuation.

8. **Depressurization modeling** predicts the pressure–temperature trajectory during emergency blowdown, verifying that the target pressure is reached within the required time and that minimum temperatures do not violate material limits.

9. **Dynamic slug handling** requires robust level control with appropriate surge volume, feed-forward detection, and potentially active slug suppression at the riser base.

10. **Measurement devices** in NeqSim (PT, TT, LT, FT) mirror real plant instrumentation and connect the process model to the control system.

11. **The dynamic simulation workflow** follows a systematic sequence: steady-state first, then dimensions, instrumentation, controllers, initialization, disturbance testing, and analysis.

12. **Dynamic simulation integrates with production optimization** through feasibility checking, transition planning, upset recovery analysis, and controller performance monitoring within a digital twin framework.

## 29.13 Integration of Control Systems with Production Optimization

The previous sections described individual controllers and dynamic simulation techniques. This section addresses how these control elements integrate with the broader production optimization framework — specifically through NeqSim's named controller architecture, the ProcessAutomation API for string-addressable variable access, and self-healing automation for robust real-time optimization loops.

### 29.13.1 Named Controllers

In a real process plant, every controller has a unique **tag name** (e.g., "LC-100" for a level controller, "PC-200" for a pressure controller). NeqSim mirrors this practice by allowing multiple controllers to be attached to any equipment via tag names:

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

import neqsim.process.controllerdevice.*;
Stream feedStream = feed;
// Java: Attach multiple controllers by tag name
ThrottlingValve valve = new ThrottlingValve("V-100", feedStream);

ControllerDeviceBaseClass levelController = new ControllerDeviceBaseClass();
levelController.setKp(2.0);
levelController.setTi(120.0);
levelController.setControllerSetPoint(0.5);

ControllerDeviceBaseClass pressureController = new ControllerDeviceBaseClass();
pressureController.setKp(1.5);
pressureController.setControllerSetPoint(50.0);

// Named registration
valve.addController("LC-100", levelController);
valve.addController("PC-200", pressureController);

// Retrieval by tag
ControllerDeviceInterface lc = valve.getController("LC-100");
Collection<ControllerDeviceInterface> all = valve.getControllers();
```

The naming convention is essential for:

- **Plant-model mapping** — tags in the digital twin match tags in the DCS/SCADA
- **Multi-controller equipment** — some equipment requires cascade or split-range control
- **Controller auditing** — enumerate all controllers to verify tuning and configuration
- **Automated optimization** — agents can iterate over controllers by tag to adjust setpoints

During dynamic simulation, the `ProcessSystem` explicitly runs all controller devices and measurement devices at each timestep of `runTransient()`:

```java
// During runTransient(), the ProcessSystem iterates:
// 1. Run all measurement devices (PT, TT, LT, FT) — read current process values
// 2. Run all controller devices — compute control actions from measurements
// 3. Run all equipment — apply control actions and advance one timestep
```

### 29.13.2 The ProcessAutomation API

For programmatic access to simulation variables — essential for AI agents, optimization loops, and digital twin integration — NeqSim provides the `ProcessAutomation` facade. This API uses **dot-notation string addresses** to read and write any variable in the process, eliminating the need to navigate Java class hierarchies:

```java
// Java: String-addressable variable access
ProcessAutomation auto = process.getAutomation();

// Discover what's available
List<String> units = auto.getUnitList();  // ["Feed Gas", "HP Sep", "Compressor"]
String eqType = auto.getEquipmentType("HP Sep");  // "Separator"

// List all variables for a unit
List<SimulationVariable> vars = auto.getVariableList("HP Sep");
for (SimulationVariable v : vars) {
    logger.info(v.getAddress() + " [" + v.getType() + "] " + v.getDescription());
    // "HP Sep.gasOutStream.temperature [OUTPUT] Gas outlet temperature"
    // Discover the actual access type; separator pressure is read-only in this facade.
}

// Read values with unit conversion
double T = auto.getVariableValue("HP Sep.gasOutStream.temperature", "C");
double P = auto.getVariableValue("HP Sep.pressure", "bara");
double flow = auto.getVariableValue("HP Sep.gasOutStream.flowRate", "kg/hr");

// Write inputs (only INPUT-type variables) and re-run
auto.setVariableValue("Compressor.outletPressure", 150.0, "bara");
process.run();  // Propagate changes through the flowsheet
```

For multi-area `ProcessModel` plants, variables are addressed with area-qualified names:

```java
ProcessModel plant = new ProcessModel();
plant.add("Separation", process);
ProcessAutomation plantAuto = plant.getAutomation();
List<String> areas = plantAuto.getAreaList();  // ["Separation", "Compression"]

// Area-qualified addresses
double T = plantAuto.getVariableValue("Separation::HP Sep.gasOutStream.temperature", "C");
plantAuto.setVariableValue("Separation::Compressor.outletPressure", 170.0, "bara");
plant.run();
```

The key distinction between INPUT and OUTPUT variables is critical:

| Type | Meaning | Example | Can Be Written |
|------|---------|---------|---------------|
| **INPUT** | Adjustable parameter | Compressor outlet pressure, valve opening | Yes |
| **OUTPUT** | Calculated result | Temperature, flow rate, duty | No (read-only) |

### 29.13.3 Self-Healing Automation

In real-time optimization loops, variable addresses may be misspelled, equipment may be renamed during model updates, or an operator may request a setpoint outside physical bounds. The **self-healing automation** system handles these issues gracefully:

```java
ProcessAutomation auto = process.getAutomation();

// Safe get — returns JSON with value on success, or diagnostics on failure
String result = auto.getVariableValueSafe("hp separator.temperature", "C");
// Returns: {"status":"auto_corrected",
//           "originalAddress":"hp separator.temperature",
//           "correctedAddress":"HP Sep.temperature",
//           "value":25.0, "unit":"C"}

// Safe set — validates physical bounds + fuzzy address matching
String setResult = auto.setVariableValueSafe("Compressor.outletPressure", 150.0, "bara");
// Returns: {"status":"success","address":"Compressor.outletPressure","value":150.0}

// If a physically impossible value is requested:
String badResult = auto.setVariableValueSafe("Compressor.outletPressure", -50.0, "bara");
// Returns: {"status":"validation_error","message":"Pressure must be positive",
//           "validRange":{"min":1.0,"max":1000.0}}
```

The `AutomationDiagnostics` class powers the self-healing capabilities:

- **Fuzzy name matching** — finds the closest unit/property when the exact name is wrong (edit distance ≤ 2)
- **Auto-correction cache** — remembers past corrections for instant reuse in subsequent calls
- **Physical bounds validation** — validates temperature, pressure, and efficiency ranges before setting
- **Operation tracking** — tracks success/failure rates and generates recommendations

```java
AutomationDiagnostics diag = auto.getDiagnostics();
String report = diag.getLearningReport();
// Reports: total operations, success rate, common errors, learned corrections
```

### 29.13.4 Real-Time Optimization Loop with Constraint Checking

The ProcessAutomation API enables a robust real-time optimization loop that:

1. **Reads** current plant values from the historian
2. **Updates** the NeqSim model to match plant conditions
3. **Optimizes** setpoints subject to equipment constraints
4. **Validates** the proposed changes against physical bounds
5. **Writes** approved changes back to the DCS

```python
import jpype
jneqsim = jpype.JPackage("neqsim")

# Build a simple process model
gas = jneqsim.thermo.system.SystemSrkEos(273.15 + 30.0, 60.0)
gas.addComponent("methane", 0.88)
gas.addComponent("ethane", 0.06)
gas.addComponent("propane", 0.04)
gas.addComponent("CO2", 0.02)
gas.setMixingRule("classic")

Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
Compressor = jneqsim.process.equipment.compressor.Compressor
Cooler = jneqsim.process.equipment.heatexchanger.Cooler
ProcessSystem = jneqsim.process.processmodel.ProcessSystem

feed = Stream("Feed Gas", gas)
feed.setFlowRate(80000.0, "kg/hr")
feed.setTemperature(30.0, "C")
feed.setPressure(60.0, "bara")

sep = Separator("HP Sep", feed)
compressor = Compressor("Export Compressor")
compressor.setInletStream(sep.getGasOutStream())
compressor.setOutletPressure(150.0)

cooler = Cooler("Aftercooler")
cooler.setInletStream(compressor.getOutletStream())
cooler.setOutletTemperature(273.15 + 35.0)

process = ProcessSystem()
process.add(feed)
process.add(sep)
process.add(compressor)
process.add(cooler)
process.run()

# --- Use ProcessAutomation API ---
auto = process.getAutomation()

# Discover all units
units = list(auto.getUnitList())
print(f"Equipment units: {units}")

# List variables for the compressor
vars_list = list(auto.getVariableList("Export Compressor"))
print(f"\nCompressor variables:")
for v in vars_list:
    print(f"  {v.getAddress()} [{v.getType()}] = {v.getDefaultUnit()}")

# Read key output variables
T_comp_out = auto.getVariableValue("Export Compressor.outletStream.temperature", "C")
power_kW = auto.getVariableValue("Export Compressor.power", "kW")
T_cooler_out = auto.getVariableValue("Aftercooler.outletStream.temperature", "C")
print(f"\nCompressor outlet T: {T_comp_out:.1f} °C")
print(f"Compressor power:    {power_kW:.0f} kW")
print(f"Cooler outlet T:     {T_cooler_out:.1f} °C")

# Optimization sweep: vary compressor discharge pressure
print("\n=== Compressor Discharge Pressure Optimization ===")
print(f"{'P_out (bara)':>14} {'Power (kW)':>12} {'T_out (°C)':>12} {'T_cooled (°C)':>14}")
print("-" * 54)
for P_out in [120, 130, 140, 150, 160, 170, 180]:
    auto.setVariableValue("Export Compressor.outletPressure", float(P_out), "bara")
    process.run()
    power = auto.getVariableValue("Export Compressor.power", "kW")
    T_out = auto.getVariableValue("Export Compressor.outletStream.temperature", "C")
    T_cool = auto.getVariableValue("Aftercooler.outletStream.temperature", "C")
    print(f"{P_out:>14} {power:>12.0f} {T_out:>12.1f} {T_cool:>14.1f}")

# Self-healing: try a misspelled address
print("\n=== Self-Healing Automation ===")
result = auto.getVariableValueSafe("export compressor.power", "kW")
print(f"Safe get result: {result}")
```

This example demonstrates the complete workflow: build the process, discover variables via the automation API, read outputs, sweep input parameters for optimization, and verify self-healing with a misspelled address.

---


<!-- September 2026 source update -->
## Keep steady-state evidence separate from dynamic protection

The current strict common-shaft and pipeline adapters qualify specific steady-state solved quantities. They do not qualify transient overspeed, surge during a trip, water hammer, slug arrival, start-up or shutdown. A complete steady-state snapshot is therefore an input to a dynamic study, not a validation of its protective behaviour \cite{neqsim2026update}.

For each dynamic example record the initial inventory/state, controller modes, time step, boundary trajectories and equipment model assumptions. Check component and energy accumulation as well as inlet/outlet balances. Repeating the run with a smaller time step should preserve the decision-driving peak, integral and settling behaviour within a declared tolerance.

When an optimizer supplies supervisory setpoints, rate-limit and validate the transition in the control model. Preserve independent trip and operating constraints. An address-based optimization interface changes simulation inputs; it does not itself provide a plant control-system connection or operational authority.

---

## Exercises

**Exercise 29.1** — *Separator Level Controller Tuning*

Build a dynamic model of a horizontal separator (D = 2.0 m, L = 6.0 m) processing a gas-condensate fluid at 50 bara. Implement a PI level controller on the liquid outlet valve. Apply a +30% step change in feed rate and measure the response for three different tuning sets:
(a) $K_c = 0.5$, $T_i = 300$ s (averaging control)
(b) $K_c = 2.0$, $T_i = 60$ s (moderate control)
(c) $K_c = 5.0$, $T_i = 30$ s (tight control)
Plot the level response for all three cases on the same graph. Discuss the trade-off between level deviation and outlet flow variability.

**Exercise 29.2** — *Pressure Controller Design*

A separator operates at 45 bara with gas flowing to a compressor. The gas volume above the liquid is 20 m³. Using NeqSim, estimate the time constant and process gain for the pressure loop. Apply IMC tuning with $\lambda = 2\theta$ and simulate the response to a 10% increase in gas production. What is the maximum pressure excursion? How long until the pressure returns to within 0.5 bara of the set point?

**Exercise 29.3** — *Cascade Level Control*

Implement cascade control for the separator in Exercise 29.1: the primary LC adjusts the set point of a secondary FC on the liquid outlet. Compare the disturbance rejection (slug arriving at $t = 300$ s, doubling the liquid inflow for 60 seconds) between:
(a) Simple PI level control
(b) Cascade LC/FC control
Plot both responses. Under what conditions does cascade control provide a significant advantage?

**Exercise 29.4** — *Depressurization Analysis*

Model the blowdown of a vessel (D = 2.5 m, L = 8.0 m) initially at 180 bara and 90°C containing a rich gas (methane 65%, ethane 15%, propane 10%, n-butane 5%, n-pentane 5%). Run the blowdown through a BDV with $C_v = 300$. Determine:
(a) Time to reach 50% of initial pressure
(b) Time to reach 6.9 barg
(c) Minimum gas temperature during blowdown
(d) Whether the minimum temperature violates a MDMT of -46°C
Plot pressure and temperature vs time.

**Exercise 29.5** — *Anti-Surge Controller*

Build a single-stage compressor model with suction at 20 bara and discharge at 60 bara. The compressor processes 100,000 kg/hr of lean gas. Simulate a 50% step reduction in suction flow (simulating a partial trip of upstream wells). Without an anti-surge controller, observe the surge indicator. Then implement an anti-surge PI controller ($K_c = 4$, $T_i = 3$ s) on a recycle valve and show that the operating point is kept above the surge line.

**Exercise 29.6** — *Dynamic Slug Response*

Model a separator receiving slug flow. The base case is 30,000 kg/hr steady liquid flow. At $t = 5$ min, a slug arrives: the liquid flow increases to 120,000 kg/hr for 2 minutes, then returns to 30,000 kg/hr. Using a separator with D = 3.0 m, L = 10 m, determine:
(a) The maximum level excursion with averaging control ($K_c = 0.8$, $T_i = 200$ s)
(b) Whether the high-level alarm (2.0 m) is reached
(c) What controller tuning would be needed to keep the level below 2.0 m

**Exercise 29.7** — *Multi-Loop Interaction*

Consider a two-phase separator with pressure control (gas valve) and level control (liquid valve). Compute the steady-state gain matrix by perturbing each valve by ±5% and measuring the change in pressure and level. Calculate the relative gain array $\Lambda$. Is there significant loop interaction? What pairing does the RGA suggest? Simulate both loops together and compare the response with the loops tuned individually vs sequentially.

---

## References

1. Seborg, D.E., Edgar, T.F., Mellichamp, D.A., and Doyle, F.J. (2016). *Process Dynamics and Control*, 4th edn. Hoboken, NJ: John Wiley & Sons.
2. Ogunnaike, B.A. and Ray, W.H. (1994). *Process Dynamics, Modeling, and Control*. New York: Oxford University Press.
3. Luyben, W.L. (1990). *Process Modeling, Simulation, and Control for Chemical Engineers*, 2nd edn. New York: McGraw-Hill.
4. Skogestad, S. and Postlethwaite, I. (2005). *Multivariable Feedback Control: Analysis and Design*, 2nd edn. Chichester: John Wiley & Sons.
5. Smith, C.A. and Corripio, A.B. (2005). *Principles and Practice of Automatic Process Control*, 3rd edn. Hoboken, NJ: John Wiley & Sons.
6. Hasan, A.R. and Kabir, C.S. (2002). *Fluid Flow and Heat Transfer in Wellbores*. Richardson, TX: Society of Petroleum Engineers.
7. API Standard 521 (2014). *Pressure-Relieving and Depressuring Systems*, 6th edn. Washington, DC: American Petroleum Institute.
8. NORSOK S-001 (2018). *Technical Safety*. Standards Norway.
9. Elliott, D.G. (2004). "Blowdown of Pressure Vessels." In *Handbook of Chemical Engineering Calculations*, 3rd edn (ed. N.P. Chopey). New York: McGraw-Hill.
10. Statoil (2017). *Anti-Surge Control Philosophy*. Equinor Internal Technical Standard TR2066.
11. Mokhatab, S. and Poe, W.A. (2012). *Handbook of Natural Gas Transmission and Processing*, 2nd edn. Burlington, MA: Gulf Professional Publishing.
12. Hedne, P. and Lunde, H. (1993). "Anti-Surge Control Systems for Turbocompressors." *Journal of Turbomachinery*, 115(3), pp. 719–727.
13. Foss, B. (2012). "Process Control in Conventional Oil and Gas Fields — Challenges and Opportunities." *Control Engineering Practice*, 20(10), pp. 1058–1064.
14. Havre, K. and Dalsmo, M. (2001). "Active Feedback Control as a Solution to Severe Slugging." *SPE Production & Facilities*, 17(3), pp. 195–203.


