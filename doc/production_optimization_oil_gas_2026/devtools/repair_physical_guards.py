from pathlib import Path
BOOK=Path(__file__).resolve().parents[1]
p=next((BOOK/'chapters').glob('ch07*/chapter.md'))
t=p.read_text(encoding='utf-8')
t=t.replace('choke.setOutletPressure(150.0)     # choke outlet pressure', 'choke.setOutletPressure(110.0)     # below the calculated upstream wellhead pressure')
t=t.replace('T_topside = riser.getOutletStream().getTemperature("C")', 'T_topside = riser.getOutletStream().getTemperature("C")\nassert 0.0 < P_choke_out <= P_wh, "A passive choke cannot add pressure"')
t=t.replace('booster.setOutletPressure(100.0)  # boost back up to 100 bara', 'booster.setOutletPressure(150.0)  # pressure increase above the flowline inlet\nbooster.setPolytropicEfficiency(0.75)\nbooster.setUsePolytropicCalc(True)')
t=t.replace('booster_power = booster.getPower("kW")', 'booster_power = booster.getPower("kW")\nassert booster_power > 0.0, "A booster must consume positive shaft power"')
t=t.replace('The effect of subsea boosting on production can be modeled by inserting a pressure increase between the flowline and riser:', 'A screening estimate of subsea boosting can insert a pressure increase between the flowline and riser. This example uses a compressor as a thermodynamic pressure-raising proxy for the defined multiphase fluid. It is not a qualified wet-gas compressor or multiphase-pump performance model; detailed design needs phase handling, vendor maps, and an appropriate machine model:')
t=t.replace(r'\frac{\Delta P_{available} \cdot D^5}{\lambda \cdot \rho_{mix} \cdot v^2 / 2}',r'\frac{2\Delta P_{available}D}{\lambda\rho_{mix}v^2}')
t=t.replace('This simplified form illustrates the strong dependence on diameter (fifth power) — doubling the pipe diameter increases the pressure-limited tieback distance by a factor of 32.', 'At fixed velocity this relation is linear in diameter. At fixed volumetric rate, substitution of $v=4Q/(\\pi D^2)$ gives a $D^5$ dependence if density and friction factor remain constant. Multiphase holdup, friction-factor changes, acceleration and elevation invalidate treating the resulting factor of 32 as a general design rule.')
t=t.replace('Industry experience provides benchmarks for achievable tieback distances:', 'The following broad ranges are orientation examples, not demonstrated capability or acceptance limits. A particular tieback requires a field-specific thermal, hydraulic and shutdown assessment:')
# Avoid treating unfilled mechanical metadata as measured or certified data.
needle='print(design.toJson())'
if needle in t: t=t.replace(needle, needle+'\nprint("Unspecified design fields are not validated limits; complete the design basis before use.")')
p.write_text(t,encoding='utf-8')
p=next((BOOK/'chapters').glob('ch10*/chapter.md'))
t=p.read_text(encoding='utf-8')
t=t.replace('design.setMaxOperationPressure(85.0)', 'design.setMaxOperationPressure(85.0)\ndesign.setMaxOperationTemperature(100.0, "C")\ndesign.setMinOperationTemperature(0.0, "C")')
# Repair Python-only insertion in Java occurrences using their semicolon style.
t=t.replace('design.setMaxOperationPressure(85.0)\ndesign.setMaxOperationTemperature(100.0, "C")\ndesign.setMinOperationTemperature(0.0, "C");', 'design.setMaxOperationPressure(85.0);\ndesign.setMaxOperationTemperature(100.0, "C");\ndesign.setMinOperationTemperature(0.0, "C");')
t=t.replace('Stock tank oil:', 'LP separator liquid:')
t=t.replace('Stock Tank Oil (m3/hr)', 'LP liquid (m3/hr)')
t=t.replace('`SeparatorMechanicalDesign`: operating-pressure envelope, K-factor, retention', '`SeparatorMechanicalDesign`: operating-pressure envelope, explicit temperature units, K-factor, retention')
needle='A process flash determines'
if 'Null or non-finite fields' not in t:
    t=t.replace('## 10.1', 'Null or non-finite fields in a mechanical-design JSON record indicate unconfigured data, not a completed mechanical design. A calculated vessel diameter does not establish material selection, design-temperature limits, corrosion allowance, nozzle adequacy or code compliance.\n\n## 10.1',1)
p.write_text(t,encoding='utf-8')
