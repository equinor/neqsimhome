"""Explicit energy-closed reconstruction of SimpleTEGAbsorber outlets.

The native Kremser approximation transfers water after its combined-feed PH
flash. Preserve that predicted component inventory, and solve a common outlet
temperature satisfying the specified adiabatic boundary. This reconstruction
does not establish stage equilibrium or predictive mass-transfer accuracy.
"""
import numpy as np
from scipy.optimize import brentq


def close_teg_energy(absorber, checks):
    incoming = [absorber.getGasInStream(), absorber.getSolventInStream()]
    outgoing = [absorber.getGasOutStream(), absorber.getSolventOutStream()]
    _, h_in, _ = checks._stream_totals(incoming)
    _, h_raw, _ = checks._stream_totals(outgoing)
    raw_temperature = float(outgoing[0].getTemperature('K'))
    originals = [stream.getFluid().clone() for stream in outgoing]
    z_original = [np.asarray(fluid.getMolarComposition(), dtype=float) for fluid in originals]
    flow_original = [float(stream.getFlowRate('kg/sec')) for stream in outgoing]

    def residual(temperature):
        total = 0.0
        for fluid, mass in zip(originals, flow_original):
            fluid.setTemperature(float(temperature))
            fluid.init(3)  # Fixed inventories; deliberately no TPflash.
            total += mass * float(fluid.getEnthalpy('J/kg'))
        return total - h_in

    low, high = raw_temperature - 5.0, raw_temperature + 5.0
    checks.require('TEG energy root is locally bracketed', residual(low) * residual(high) <= 0,
                   residual(low) * residual(high), '<=0 within native temperature +/-5 K', 'W2')
    corrected_temperature = float(brentq(residual, low, high, xtol=1e-9))
    residual(corrected_temperature)
    for i, (stream, fluid) in enumerate(zip(outgoing, originals)):
        fluid.initProperties()
        checks.close('TEG reconstruction preserves composition',
                     np.max(np.abs(np.asarray(fluid.getMolarComposition()) - z_original[i])),
                     0.0, atol=1e-12, category='component_balance')
        checks.require('TEG reconstructed outlet remains single phase', int(fluid.getNumberOfPhases()) == 1,
                       int(fluid.getNumberOfPhases()), 'one retained gas or liquid phase', 'phases')
        stream.setThermoSystem(fluid)
        checks.close('TEG reconstruction preserves mass flow', stream.getFlowRate('kg/sec'),
                     flow_original[i], atol=1e-10, rtol=1e-10, unit='kg/s', category='mass_balance')
    _, h_closed, _ = checks._stream_totals(outgoing)
    checks.close('TEG reconstructed adiabatic first law', h_closed, h_in,
                 atol=0.1, rtol=1e-8, unit='W', category='energy_balance')
    result = {'raw_energy_residual_W': h_raw - h_in,
              'raw_relative_energy_residual': (h_raw - h_in) / max(abs(h_in), abs(h_raw), 1.0),
              'native_temperature_K': raw_temperature, 'reconstructed_temperature_K': corrected_temperature,
              'temperature_shift_K': corrected_temperature - raw_temperature,
              'corrected_energy_residual_W': h_closed - h_in,
              'limitation': 'Fixed-inventory energy closure of a Kremser approximation; no multistage equilibrium validation.'}
    print('TEG energy reconstruction:', result)
    return result
