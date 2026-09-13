from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
def path(n):return next((B/'chapters').glob(f'ch{n:02d}_*/chapter.md'))
p=path(20);t=p.read_text(encoding='utf-8-sig')
t=t.replace('cold_fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 20.0, 5.0)',
            'cold_fluid = jneqsim.thermo.system.SystemSrkCPAstatoil(273.15 + 20.0, 5.0)')
t=t.replace('cold_fluid.setMixingRule("classic")','cold_fluid.setMixingRule(10)')
start=t.index('# Capacity assessment\nUA_design = 50000.0')
end=t.index('\n```',start)
t=t[:start]+'''# Two solved conductances; no arbitrary assumed 50 K driving force.
import numpy as np
UA_design = 50000.0
DT_min_limit = 5.0  # K, assumed screening limit
hx_checks = []
for UA in [UA_design, .8*UA_design]:
    hx.setUAvalue(UA); hx.run()
    streams = [hot_stream,cold_stream,hx.getOutStream(0),hx.getOutStream(1)]
    for stream in streams: stream.getFluid().initProperties()
    for inlet,outlet in [(streams[0],streams[2]),(streams[1],streams[3])]:
        assert abs(outlet.getFlowRate('kg/hr')/inlet.getFlowRate('kg/hr')-1) < 1e-8
    hot_change = float(streams[2].getFluid().getEnthalpy()-streams[0].getFluid().getEnthalpy())
    cold_change = float(streams[3].getFluid().getEnthalpy()-streams[1].getFluid().getEnthalpy())
    energy_error = abs(hot_change+cold_change)/max(abs(hot_change),abs(cold_change),1.)
    assert energy_error < 1e-5 and hot_change < 0 and cold_change > 0, energy_error
    terminals = [hot_stream.getTemperature('K')-streams[3].getTemperature('K'),
                 streams[2].getTemperature('K')-cold_stream.getTemperature('K')]
    assert min(terminals)>0 and all(np.isfinite(v) for v in terminals)
    hx_checks.append({'UA_W_K':UA,'duty_kW':-hot_change/1000.,
                      'minimum_approach_K':min(terminals),'energy_relative':energy_error})
assert hx_checks[1]['duty_kW'] < hx_checks[0]['duty_kW']
print(hx_checks)
print('Fouled approach screen:',hx_checks[1]['minimum_approach_K'] >= DT_min_limit)
''' + t[end:]
p.write_text(t,encoding='utf-8')
p=path(27);t=p.read_text(encoding='utf-8-sig')
matches=list(re.finditer(r'^```python[^\n]*\n(.*?)^```',t,re.M|re.S));m=matches[0];code=m.group(1)
code=code.replace('water_cut','water_mole_fraction').replace('SystemSrkEos(temperature + 273.15, pressure)',
 'jneqsim.thermo.system.SystemSrkCPAstatoil(temperature + 273.15, pressure)')
for old,new in [('0.70 *','(0.70/.95) *'),('0.10 *','(0.10/.95) *'),('0.05 *','(0.05/.95) *')]:code=code.replace(old,new)
code=code.replace('fluid.setMixingRule("classic")','fluid.setMixingRule(10)')
code=code.replace('separator = Separator("HP separator", feed)',
 'separator = jneqsim.process.equipment.separator.ThreePhaseSeparator("HP separator", feed)')
code=code.replace('low WC','low water mole fraction').replace('High water cut','High water mole fraction')
t=t[:m.start(1)]+code+t[m.end(1):]
t=t.replace('uncertain feed rate, feed pressure, and water cut:',
 'uncertain feed rate, pressure, temperature, overall water mole fraction and isentropic efficiency:')
t=t.replace('Feed rate and water cut dominate the sensitivity, while compressor efficiency has relatively minor impact.',
 'Bars show low/high input endpoints relative to the base. Compressor efficiency has zero gas-yield effect in this prescribed upstream-feed model.')
p.write_text(t,encoding='utf-8')
p=path(30);t=p.read_text(encoding='utf-8-sig')
t=t.replace(r'\text{anomaly score} = \|x - \hat{x}\|^2',
 r'\text{anomaly score} = (x-\hat{x})^T S^{-1}(x-\hat{x})')
t=t.replace('When the anomaly score exceeds a threshold, the system generates an alert. The physics-based digital twin provides a natural baseline for anomaly detection: if the model-vs-plant discrepancy exceeds the expected measurement uncertainty, something has changed.',
 'Here $S$ is a positive-definite residual covariance matrix estimated from representative nominal data, including measurement noise and model discrepancy. For an autoencoder, standardized residuals with a held-out empirical threshold are also possible. Raw squared differences cannot be added across pressure, temperature and flow units. An alert means that the calibrated residual distribution was exceeded; it does not by itself identify a fault or distinguish sensor bias, model error and an unrepresented operating regime.')
p.write_text(t,encoding='utf-8')
p=path(34);t=p.read_text(encoding='utf-8-sig')
t=t.replace('Model a heavy oil FPSO production system with gas lift, multi-stage separation, crude stabilization, and produced water treatment, and analyze the effects of rising water cut on system performance',
 'Model an illustrative FPSO separation and compression system with a defined CPA hydrocarbon/water recipe, analyze reference water-cut sensitivity, and identify the extra models needed for gas lift and water treatment')
t=t.replace('Heavy oil reservoir fluid composition (mole fractions).','Illustrative hydrocarbon recipe (mole fractions); not a calibrated heavy-oil assay.')
t=t.replace('fixed200m³/hr','fixed 200 m³/hr').replace('gives149.069m³/hr','gives 149.069 m³/hr').replace('at2.5bara,61.996m³/hr','at 2.5 bara, 61.996 m³/hr').replace('at35bara/70°C','at 35 bara/70°C').replace('and0.306854MW','and 0.306854 MW').replace('same35bara/70°C totals223.752m³/hr, or55.94%','same 35 bara/70°C totals 223.752 m³/hr, or 55.94%').replace('assumed400m³/hr','assumed 400 m³/hr').replace('Across10–80%','Across 10–80%').replace('decreases57.18→52.85%','decreases from 57.18% to 52.85%')
p.write_text(t,encoding='utf-8')
print('Final physical boundaries installed')
