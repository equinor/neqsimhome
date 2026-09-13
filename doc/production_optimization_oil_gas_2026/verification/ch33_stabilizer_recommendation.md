# Bounded Chapter 33 NGL stripper recommendation

Three configurations were evaluated. The final configuration passed explicit finite-value, positive-product-flow, overall material-balance, and overall energy-balance checks. No chapter was edited, and no further column probes were run after this configuration.

The tested example is a **snapshot study of one equilibrium contacting tray above a reboiler**, with no condenser. It uses the actual liquid produced by the current Chapter 33 Areas 1–3; it is not an industrial deethanizer or evidence of any sales/storage specification.

## Tested result

| Quantity | Result |
|---|---:|
| Java maximum heap | 512 MB |
| Actual cold-separator liquid | 85,367.8708 kg/h |
| Cold-separator liquid state | −76.8431 °C, 20 bara |
| Conditioned feed state | −30 °C, 20 bara |
| Conditioned feed vapor mole fraction | 0.382611 |
| Column top / bottom pressure | 19.5 / 20 bara |
| Reboiler temperature | 40 °C |
| Feed heater duty | 4,553.9830 kW |
| Reboiler duty | 4,579.2016 kW |
| Overhead gas | 40,953.9827 kg/h at −8.4067 °C |
| Liquid bottoms | 44,413.8881 kg/h at 40 °C |
| Bottoms methane / ethane | 2.0731 / 20.7441 mol% |
| Overall relative mass imbalance | 1.53 × 10⁻¹² |
| Overall energy imbalance / reboiler duty | 1.09 × 10⁻⁷ |
| Solver | DIRECT_SUBSTITUTION, 11 iterations |
| Measured column solve time | 0.187 s |
| Reported status | RIGOROUS_CONVERGED, solved() = true |

Energy convergence is explicitly enforced with tolerance 1e−4 and temperature tolerance 1e−5 K. The default mass tolerance was retained; independent reported closure is far tighter. **The MESH gate was not enabled**: its reported infinity norm is 0.41056, dominated by the energy component. Consequently this result establishes the stated finite-product and whole-column balance checks under the active solver gates, not full MESH-residual validation. Retain this qualification if the example is published. The product still contains methane and substantial ethane, so label it light-end stripping rather than deethanization or export-grade stabilization.

## Minimal tested example

This is the same calculation as the successful probe; run after the three upstream process areas have been solved. The cloned liquid intentionally captures that operating point, so it must be recreated for each upstream sensitivity case.

```python
import math

Stream = jneqsim.process.equipment.stream.Stream
Valve = jneqsim.process.equipment.valve.ThrottlingValve
Heater = jneqsim.process.equipment.heatexchanger.Heater
DistillationColumn = jneqsim.process.equipment.distillation.DistillationColumn

feed = Stream("NGL Stabilizer Feed", cold_sep.getLiquidOutStream().getFluid().clone())
feed.run()
feed_control = Valve("Stabilizer Feed Letdown", feed)
feed_control.setOutletPressure(20.0, "bara")  # No letdown at this 20-bara base case.
feed_control.run()
feed_heater = Heater("Stabilizer Feed Heater", feed_control.getOutletStream())
feed_heater.setOutTemperature(-30.0, "C")
feed_heater.run()

stripper = DistillationColumn("NGL Stabilizer", 1, True, False)
stripper.addFeedStream(feed_heater.getOutletStream(), 1)
stripper.setTopPressure(19.5)
stripper.setBottomPressure(20.0)
stripper.getReboiler().setOutTemperature(273.15 + 40.0)
stripper.setSolverType(DistillationColumn.SolverType.DIRECT_SUBSTITUTION)
stripper.setMaxNumberOfIterations(80, True)
stripper.setTemperatureTolerance(1e-5)
stripper.setEnthalpyBalanceTolerance(1e-4)
stripper.setEnforceEnergyBalanceTolerance(True)
stripper.run()

overhead = stripper.getGasOutStream()
bottoms = stripper.getReboiler().getLiquidOutStream()
column_feed = feed_heater.getOutletStream()
rates = [s.getFlowRate("kg/hr") for s in (column_feed, overhead, bottoms)]
enthalpies = [s.getFluid().getEnthalpy() for s in (column_feed, overhead, bottoms)]
duty = stripper.getReboiler().getDuty()  # W
assert stripper.solved(), stripper.getConvergenceDiagnostics()
assert all(math.isfinite(x) for x in rates + enthalpies + [duty])
assert all(x > 0 for x in rates)
mass_error = abs(rates[0] - rates[1] - rates[2]) / rates[0]
energy_error = abs(enthalpies[0] + duty - enthalpies[1] - enthalpies[2]) / abs(duty)
assert mass_error < 0.001 and energy_error < 0.001
print(stripper.getConvergenceDiagnostics())
print(f"Overhead {rates[1]:.2f} kg/h; bottoms {rates[2]:.2f} kg/h")
print(f"Heater {feed_heater.getDuty()/1000:.2f} kW; reboiler {duty/1000:.2f} kW")
print(f"Relative mass/energy imbalance: {mass_error:.3g}, {energy_error:.3g}")
```

The model calls and settings above were executed in `devtools/probe_ch33_stabilizer.py`. The additional concise finite/positive checks summarize the recorded outputs; the rewritten display block itself has not been run as a book fence. If inserted, include it in the author's normal literal-fence audit.

## Evidence and rejected configurations

- Successful raw record: `verification/ch33_stabilizer_probe_1stage_19.5bar_-30C_40C.json`; stdout log: `verification/ch33_stabilizer_probe_third.log`.
- Upstream code SHA-256: `2d39122c860d6ae11d1edb66607dfb2597863cdffb3c34197f59f461914a9282`.
- First trial: five stages, 8–8.5 bara, feed 50 °C, reboiler 105 °C. Rejected: zero liquid product and invalid bottom-stream enthalpy despite solved() reporting true.
- Second trial: five stages, 19.5–20 bara, feed −30 °C, reboiler 40 °C. Rejected: 3.72% overall energy imbalance despite solved() reporting true with the default disabled energy gate.
- Third trial above: one tray plus reboiler and explicit tighter temperature/energy gates. All finite-product and whole-column checks passed. The remaining unenforced MESH diagnostic is disclosed above.
