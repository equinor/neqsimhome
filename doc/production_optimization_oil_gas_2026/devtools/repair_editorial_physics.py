"""One-time corrections found while reviewing the physical meaning of plot data."""
import json
import re
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]

def edit(number, transform):
    path = next((BOOK / 'chapters').glob('ch%02d*/notebooks/*.ipynb' % number))
    nb = json.loads(path.read_text(encoding='utf-8'))
    for cell in nb['cells']:
        cell['source'] = transform(''.join(cell['source']), cell['cell_type']).splitlines(True)
    path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')

def dewpoint(s, kind):
    if 'wdp_pressures =' not in s:
        return s
    s = s.replace('fluid.addComponent("methane", 0.85)', 'fluid.addComponent("methane", 0.88995)')
    s = s.replace('fluid.addComponent("water", 0.04)', 'fluid.addComponent("water", 50.0e-6)  # 50 ppmv water in total gas')
    s = s.replace('    fluid.setHydrateCheck(True)\n', '')
    start = s.index('    try:\n')
    end = s.index('\n# Plot', start)
    s = s[:start] + '''    ops.waterDewPointTemperatureMultiphaseFlash()
    wdp_T = float(fluid.getTemperature("C"))
    assert -100.0 < wdp_T < 80.0, f"Invalid water dew point at {P} bara: {wdp_T} C"
    water_dew_temps.append(wdp_T)
print("Water dew point for 50 ppmv water:")
for pressure, temperature in zip(wdp_pressures, water_dew_temps):
    print(f"  {pressure:.0f} bara: {temperature:.3f} C")
''' + s[end:]
    return s.replace('Water Dew Point Temperature vs Pressure', 'Water dew point at 50 ppmv water').replace('Typical export gas spec (−18 °C)', 'Illustrative water-dew-point target (−18 °C)')

edit(9, dewpoint)

def oil(s, kind):
    return (s.replace('Reid Vapor Pressure', 'True Vapor Pressure at 37.8 °C')
            .replace('RVP vs Stabilizer Temperature', 'True vapor pressure vs stabilizer temperature')
            .replace('Typical RVP spec (~1 bara)', 'Illustrative TVP target (1 bara)')
            .replace('RVP range:', 'TVP range:').replace('flash at RVP conditions (37.8°C)', 'calculate bubble pressure at 37.8°C (TVP, not ASTM Reid vapor pressure)')
            .replace('273.15 + 15.6', '288.7056').replace('rho / 999.0', 'rho / 999.016'))
edit(11, oil)

def poly(s, kind):
    if kind == 'code' and 'setPolytropicEfficiency' in s and 'setUsePolytropicCalc' not in s:
        s = re.sub(r'(?m)^(\s*)(\w+)\.setPolytropicEfficiency\(([^\n]+)\)$', r'\1\2.setUsePolytropicCalc(True)\n\1\2.setPolytropicEfficiency(\3)', s)
    if 'powers_75.append' in s:
        s = s.replace('fig, ax =', 'assert np.all(np.array(powers_75) > np.array(powers_85)), "Higher efficiency must lower power"\n\nfig, ax =')
        s = s.replace('powers_75[5]', 'powers_75[4]').replace('powers_85[5]', 'powers_85[4]')
    if 'discharge_temps_65.append' in s:
        s = s.replace('fig, ax =', 'assert np.all(np.array(discharge_temps_65) > np.array(discharge_temps_75)), "Lower efficiency must raise discharge temperature"\n\nfig, ax =')
    s = s.replace('Typical limit (150°C)', 'Illustrative design limit (150°C)').replace('Absolute max (200°C)', 'Illustrative review threshold (200°C)').replace('Material Limit (150°C)', 'Illustrative design limit (150°C)')
    s = s.replace('head_curve = design_head * (1.15 - 0.0015 * (flow_pct - 70)**2 / 100)', 'head_curve = design_head * (1.0 + 0.15 * (1.0 - (flow_pct / 100.0)**2))')
    s = s.replace('Compressor Performance Map (Centrifugal)', 'Illustrative centrifugal compressor map')
    return s
for chapter in (12, 14, 34):
    edit(chapter, poly)

def exchanger(s, kind):
    if '# Create heat exchanger' in s:
        s = s.replace('# Results', '''def hot_side_heat_removed_kW(exchanger):
    hot_loss = (exchanger.getInStream(0).getFluid().getEnthalpy()
                - exchanger.getOutStream(0).getFluid().getEnthalpy()) / 1000.0
    cold_gain = (exchanger.getOutStream(1).getFluid().getEnthalpy()
                 - exchanger.getInStream(1).getFluid().getEnthalpy()) / 1000.0
    assert hot_loss > 0.0 and cold_gain > 0.0, "Heat must flow from hot stream to cold stream"
    assert abs(hot_loss - cold_gain) / hot_loss < 0.001, "Exchanger energy balance does not close"
    return hot_loss

# Results''')
    s = s.replace('hx.getDuty() / 1000.0', 'hot_side_heat_removed_kW(hx)')
    s = s.replace('Position Along Exchanger [% length]', 'Fraction of total heat transferred [%]')
    s = s.replace('Counterflow Heat Exchanger — Temperature Profile', 'Counterflow temperatures on a heat-transfer coordinate')
    s = s.replace('Duty [kW]', 'Heat transferred [kW]')
    return s
edit(16, exchanger)

def valves(s, kind):
    if 'cv_values = []' in s:
        s = s.replace('    process.run()\n    cv_values.append(valve.getCv("US"))', '''    feed.run()
    sized_valve = ThrottlingValve("Independently sized valve", feed)
    sized_valve.setOutletPressure(80.0, "bara")
    sized_valve.run()
    cv_values.append(sized_valve.getCv("US"))''')
        s = s.replace('T_out_i = valve.getOutletStream()', 'T_out_i = sized_valve.getOutletStream()')
        s = s.replace('# Reset', 'assert cv_values[-1] > 7.9 * cv_values[0], "Required Cv must scale with rate at fixed states"\n\n# Reset')
    if '# Set a known Cv' in s:
        s = s.replace('openings = np.linspace(10, 100, 10)', 'valve.setIsCalcOutPressure(True)\nopenings = np.linspace(20, 100, 9)')
        s = s.replace('    outlet_P.append(valve.getOutletStream().getPressure("bara"))', '''    pressure = float(valve.getOutletStream().getPressure("bara"))
    assert 0.0 < pressure <= P_in, "Valve cannot increase pressure"
    outlet_P.append(pressure)''')
        s = s.replace('# Reset', '# Reset\nvalve.setIsCalcOutPressure(False)')
    return s
edit(17, valves)

def fixed_pressure_capacity(s, kind):
    if kind != 'code':
        return s
    # Auto-sizing produces synthetic maps. This exercise uses its power rating only.
    pattern = r'(?m)^(\s*)(compressor|comp|equip_obj)\.autoSize\(([^\n]+)\)$'
    def configure(match):
        indent, obj, arg = match.groups()
        base = match.group(0)
        conditional = obj == 'equip_obj'
        prefix = indent + ('    ' if conditional else '')
        code = ('\n' + indent + 'if equip_name == "Compressor":') if conditional else ''
        for line in [f'{obj}.getCompressorChart().setUseCompressorChart(False)',
                     f'{obj}.setSolveSpeed(False)',
                     f'{obj}.setUsePolytropicCalc(True)',
                     f'for constraint_entry in {obj}.getCapacityConstraints().entrySet():',
                     '    constraint_entry.getValue().setEnabled(str(constraint_entry.getKey()) == "power")']:
            code += '\n' + prefix + line
        return base + code
    s = re.sub(pattern, configure, s)
    if 'compressor.setOutletPressure' in s:
        s = s.replace('compressor.setOutletPressure', 'compressor.setUsePolytropicCalc(True)\ncompressor.setOutletPressure', 1)
    if 'comp.setOutletPressure' in s:
        s = s.replace('comp.setOutletPressure', 'comp.setUsePolytropicCalc(True)\ncomp.setOutletPressure', 1)
    return s
for chapter in (20,22,24):
    edit(chapter, fixed_pressure_capacity)
print('Updated chapters09,11,12,14,16,17,20,22,24,34. Execute affected notebooks next.')
