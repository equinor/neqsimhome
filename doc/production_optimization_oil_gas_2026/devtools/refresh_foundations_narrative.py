from pathlib import Path
import re
BOOK=Path(__file__).resolve().parents[1]

sections={
1:r'''### Current NeqSim workflow and reproducibility

This revision uses NeqSim source commit `6cc8026202a5d3f9383c9abd1d97d448993813f9`
(12 September 2026). A release date alone cannot identify a simulation: preserve
the equation of state, mixing rule, composition, units, component database and
calculation settings with the source revision. The source-workspace bootstrap
below deliberately loads `target/classes`; using a previously installed Python
package can otherwise hide new Java functionality.\cite{neqsim2026update}

The newer workflow connects three kinds of evidence. Thermodynamic experiments
qualify the fluid; hydraulic and equipment models define feasible operation;
optimization searches that feasible region. `PVTRegression` combines laboratory
experiment objectives with bounded parameters and separate hold-out validation.
`ProcessAutomation` exposes discoverable input/output addresses and units.
Typed energy ports, `EnergyBus` and `EnergyNetworkSolver` allocate available
power and report unmet demand. These capabilities support traceable decisions
only when the model's scope and numerical checks accompany each result.

When reading a worked example, distinguish an **input assumption**, a
**calculated result**, a **regression check** and an **independent measurement**.
A generated compressor curve is an assumed teaching map; an automatically sized
separator is a preliminary design; a converged optimizer is a numerical result.
None of those descriptions by itself establishes vendor qualification or
operability outside the conditions actually examined.

''',
3:r'''### 3.6.6 Calibration, validation and the current PVT interface

The September 2026 PVT workflow starts with an immutable laboratory data basis,
an untuned fluid and experiments that run independently. Register only measured
quantities in the calibration objective. The current regression interface
distinguishes the observables shown below; units are part of the data contract.
Validate array lengths, finite values and observation ordering before passing
the arrays to Java.\cite{neqsim2026update}

| Current method | Observable and required basis |
|---|---|
| `addCCEData` | Pressure (bar), relative volume $V/V_{sat}$, optional Y-factor, temperature (K) |
| `addCVDData` | Pressure (bar), liquid dropout (volume %), gas Z, temperature (K) |
| `addDLEData` | Pressure (bar), solution GOR (Sm³/Sm³), oil FVF (m³/Sm³), density (kg/m³), temperature (K) |
| `addSeparatorData` | Stage GOR, oil FVF, API gravity, stage pressure (bar), stage and reservoir temperatures (K) |
| `addViscosityData` | Pressure (bara), dynamic viscosity (Pa s), temperature (K), explicit phase name |

Choose a small set of physically relevant `RegressionParameter` values with
documented bounds. `runRegression()` returns a `RegressionResult` containing
the tuned fluid, parameter values, objectives and uncertainty diagnostics.
Library default bounds and a low objective are not acceptance criteria.
Inspect structured residuals, parameters at their bounds and correlations
between fitted parameters; these reveal whether the data actually constrain
the fitted model. Preserve unused experiments for hold-out predictions with
the parameter set frozen. Re-fitting after looking at those observations
turns them into calibration data.

`PVTReportGenerator` assembles results using `addCCE`, `addCVD`, `addDLE` and
`addSeparatorTest`, then `generateMarkdownReport()`. Its reservoir metadata
setter uses bara and **°C**, whereas regression experiment temperatures use K.
The handoff should retain raw and prepared data, the base and tuned fluids,
parameter bounds, residual plots, hold-out outcomes and the approved operating
envelope. The current regression package has no `EclipseEOSExporter`; use the
dedicated black-oil export or E300 import workflow for supported file exchange.

''',
8:r'''### Hydraulic evidence: geometry, thermal model and feasible points

In the current `PipeBeggsAndBrills` interface, `setLength` takes metres and
`setElevation` is outlet elevation minus inlet elevation, also in metres.
A rising production riser therefore has a positive elevation change. A
20 km flowline requires `setLength(20000.0)`, and geometric consistency requires
$|\Delta z|\le L$. Confusing kilometres and metres can understate friction by
three orders of magnitude and make a riser geometrically impossible.

`PipingRouteBuilder` can translate a line-list route into serial hydraulic
segments. Record the measured length, internal diameter, roughness, elevation,
fitting treatment, heat-transfer coefficient and ambient temperature for each
segment. Recalculate fluid properties along the route and compare pressure and
temperature profiles after refining the segmentation. A final pressure alone
cannot show where acceleration, liquid accumulation or a thermal pinch controls
the result.\cite{neqsim2026update}

A forward calculation fixes inlet pressure and rate. If its pressure becomes
nonphysical before the outlet, that rate is infeasible for the stated boundary
conditions. Preserve it as a failed point in the sensitivity table; never
substitute the last finite pressure. A deliverability calculation instead varies
the rate to meet outlet pressure and requires a bracketed solution. Steady-state
holdup and flow-regime screening do not establish slug frequency, restart
inventory or transient stability.

''',
10:r'''### From equilibrium separation to equipment performance

![Conceptual AI-generated illustration of a horizontal separator, showing the inlet region, liquid inventory and overhead gas outlet. The cutaway explains separation paths and is not a mechanical drawing or vendor performance guarantee.](figures/separator_cutaway_2026.png)

The equilibrium `Separator` determines phase splitting. The physical vessel and
its internals require a second layer of evidence. Configure those inputs through
`SeparatorMechanicalDesign`: operating-pressure envelope, K-factor, retention
time, inlet-pipe diameter, inlet-device type, demister type and internal sections.
This facade delegates performance settings to the separator while keeping the
mechanical description together.\cite{neqsim2026update}

The newer primary-separation classes distinguish an inlet vane, vane with mesh,
and inlet cyclones. Demisting models distinguish mesh, vane and cyclone behavior,
including pressure drop and carry-over; drainage-aware models add a separate
drainage limitation. A vessel can satisfy average gas velocity and still fail
at the inlet, demister drainage, liquid residence time or outlet nozzle.
Consequently, report the governing mechanism alongside the maximum utilization.

Automatic sizing supplies an initial candidate. Freeze dimensions before a
capacity sweep; resizing at every rate would move the constraint with the
operating point. Constraint profiles named for a company or standard are
software presets whose current values must be checked against the applicable
project requirements. They are not evidence that a vessel complies with an
entire design code. Calibration of carry-over and carry-under requires
appropriate droplet, emulsion and measured performance data.

''',
14:r'''### Compressor maps, drivers and energy availability

![Conceptual AI-generated illustration of a compression train with gas compression, cooling and driver equipment. It introduces process and shaft-load connections; geometry and displayed equipment do not represent an OEM map or mechanical design.](figures/compression_train_2026.png)

A compressor's required pressure rise and its driver's available shaft power
are separate constraints. Current NeqSim models support generated teaching maps,
explicit vendor-map data, speed limits, power limits and capacity reporting.
`GasTurbineUnit` adds package performance, ambient derating, fuel consumption,
emissions and overload reporting; attaching a calculated compressor load makes
the demand follow the process. Catalog entries are screening data, so a design
decision must carry its vendor revision and guarantee conditions.\cite{neqsim2026update}

Keep chart conventions explicit: actual inlet volume flow, head unit and
efficiency unit. In the illustrated `addCurve` interface, efficiency arrays are
in percent; compressor efficiency setters use fractions. Generated maps must
be labeled synthetic and must not be used as measured surge data. For an
off-design comparison, hold the installed map and driver rating fixed, rerun
the process and inspect the active capacity constraint. A successful flash or
an optimizer return alone does not establish surge margin or a feasible speed.

The energy-network implementation extends a scalar power budget: typed ports
can connect electrical supply, a motor, a mechanical shaft and a compressor.
Allocation reports distinguish requested, served and unmet demand. This makes
power shortage visible in production optimization instead of allowing every
consumer to assume the full plant rating simultaneously.

''',
18:r'''### 18.15 Typed energy allocation: an explicit shortage example

An energy balance and an allocation policy answer different questions. A balance
asks whether supply equals demand; an allocation policy determines which loads
are served when it does not. `EnergyBus` separates offered power, requested
power, served demand, unmet demand and curtailed supply. `EnergyNetworkSolver`
makes this allocation a flowsheet operation. Typed ports distinguish electrical,
mechanical, chemical and thermal energy; utility quality and temperature levels
must also be considered when transferring heat.\cite{neqsim2026update}

The following executable example offers 10 MW to loads requesting 8 MW and
8 MW at equal priority. Proportional allocation serves 5 MW to each and reports
6 MW unmet demand. These are prescribed teaching inputs and an algebraic
allocation check, not a power-system stability study.
<!-- @neqsim:claim test: src/test/java/neqsim/process/equipment/stream/EnergyBusAllocationTest.java -->

```python
energy = jneqsim.process.equipment.stream
bus = energy.EnergyBus("Platform electrical bus", energy.EnergyType.ELECTRICAL)
producer = energy.EnergyPort("Generation", energy.EnergyType.ELECTRICAL,
                            energy.EnergyPortDirection.OUTPUT, energy.EnergyPortMode.CALCULATED)
loads = [energy.EnergyPort(name, energy.EnergyType.ELECTRICAL,
                          energy.EnergyPortDirection.INPUT, energy.EnergyPortMode.SPECIFICATION)
         for name in ("Compression", "Water injection")]
producer.connect(bus)
producer.setDuty(10.0e6)
for load in loads:
    load.connect(bus)
    load.setRequestedPower(8.0e6)
solver = jneqsim.process.equipment.energy.EnergyNetworkSolver("Energy allocation", bus)
solver.run()
report = solver.getReports().get(0)
for load in loads:
    print(load.getName(), "served (MW):", load.getPowerMagnitude() / 1e6)
print("Unmet demand (MW):", report.getUnmetDemand() / 1e6)
assert abs(report.getUnmetDemand() - 6.0e6) < 1.0
```

Reducing throughput is one response to this shortage; dispatching a generator,
reducing a flexible utility load or changing compressor duty are alternatives.
Priority policies belong to the operating philosophy and should be explicit.
Dynamic shaft inertia, stored energy, ramp limits and repeated time-step
evaluation require the corresponding dynamic models. An algebraic allocation
does not establish frequency response or protection coordination.

'''}

for number,section in sections.items():
    p=next((BOOK/'chapters').glob('ch%02d*/chapter.md'%number))
    t=p.read_text(encoding='utf-8')
    if section.splitlines()[0] in t:continue
    if number in (1,8,10,14):
        position=t.index('\n## ')
    elif number==3:
        position=t.index('## 3.7 ')
    else:
        position=t.index('## 18.14 ') if '## 18.14 ' in t else len(t)
    t=t[:position]+'\n\n'+section+t[position:]
    if number==3:
        t=t.replace(r'\frac{\text{GOR} \cdot \rho_o^{\text{sc}} / M_o}{P^{\text{sc}} / (Z^{\text{sc}} R T^{\text{sc}})}',r'\text{GOR}\,\frac{P^{\text{sc}}M_o}{Z^{\text{sc}} R T^{\text{sc}}\rho_o^{\text{sc}}}')
        t=t.replace('Contamination below 5% is generally acceptable.','An acceptable contamination limit depends on the fluid, contaminant, intended observable and laboratory correction uncertainty.')
        t=t.replace('Acceptable tolerances for tuned models:','Illustrative teaching targets for tuned models, to be replaced by project-specific criteria and laboratory uncertainty:')
        t=t.replace('$B_o$ is always greater than 1','$B_o$ is commonly greater than 1 for live reservoir oils')
        t=t.replace('## 3.6.6 Calibration','### 3.6.6 Calibration') if '## 3.6.6 Calibration' in t and '### 3.6.6 Calibration' not in t else t
    if number==18:
        t=t.replace(r'\frac{r_p^{(\gamma-1)/\gamma} - 1}{\eta_c} - \eta_t\left(1 - \frac{1}{r_p^{(\gamma-1)/\gamma}}\right) \cdot \frac{T_3}{T_1}',r'\eta_t\left(1 - \frac{1}{r_p^{(\gamma-1)/\gamma}}\right) \cdot \frac{T_3}{T_1} - \frac{r_p^{(\gamma-1)/\gamma} - 1}{\eta_c}')
        t=t.replace('The net specific work output of a real gas turbine','The net shaft-power output of a real gas turbine')
    p.write_text(t,encoding='utf-8')
