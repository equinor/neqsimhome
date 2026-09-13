"""Explicit conservation and applicability checks for the book calculations.

These are verification of the computed cases, not field calibration. Independent
reference comparisons are in benchmark_results.json and use separate expected data.
"""
import atexit
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import numpy as np


class PhysicsViolation(AssertionError):
    pass


class PhysicsChecks:
    def __init__(self, notebook):
        self.notebook = Path(notebook)
        self.chapter = self.notebook.parent.parent.name
        self.book = self.notebook.parents[3]
        self.records = {}
        self.rejected_candidates = []
        self.failures = []
        self.uncovered = set()
        self.finished = False
        self._candidate = False
        self.output = self.book / 'verification/scientific_revision/notebooks' / (self.chapter + '.json')
        self.output.parent.mkdir(parents=True, exist_ok=True)
        atexit.register(self.save)

    def require(self, label, condition, actual, expected, unit='1', tolerance=None, category='physical_domain'):
        key = category + ':' + label
        entry = self.records.setdefault(key, {'label': label, 'category': category, 'unit': unit,
            'expected': expected, 'tolerance': tolerance, 'evaluations': 0, 'passed': 0, 'failed': 0,
            'minimum_actual': None, 'maximum_actual': None})
        entry['evaluations'] += 1
        entry['passed' if bool(condition) else 'failed'] += 1
        if isinstance(actual, (int, float, np.number)) and math.isfinite(float(actual)):
            entry['minimum_actual'] = float(actual) if entry['minimum_actual'] is None else min(entry['minimum_actual'], float(actual))
            entry['maximum_actual'] = float(actual) if entry['maximum_actual'] is None else max(entry['maximum_actual'], float(actual))
        if not condition:
            failure = {'label': label, 'actual': str(actual), 'expected': expected,
                       'unit': unit, 'tolerance': tolerance, 'candidate_rejection': self._candidate}
            (self.rejected_candidates if self._candidate else self.failures).append(failure)
            raise PhysicsViolation(f'{label}: actual={actual}; expected={expected}; tolerance={tolerance} {unit}')
        return True

    def close(self, label, actual, expected, atol=0.0, rtol=0.0, unit='1', category='analytic_identity'):
        actual, expected = float(actual), float(expected)
        tolerance = float(atol + rtol * abs(expected))
        error = abs(actual - expected)
        return self.require(label, math.isfinite(actual) and error <= tolerance,
                            error, f'absolute error <= {tolerance:g}', unit,
                            {'absolute': atol, 'relative': rtol, 'reference': expected}, category)

    def array(self, label, values, lower=None, upper=None, allow_missing=False, min_finite=1, unit='1'):
        values = np.asarray(values, dtype=float).ravel()
        valid = values[np.isfinite(values)]
        self.require(label + ' finite coverage', len(valid) >= min_finite and (allow_missing or len(valid) == len(values)),
                     len(valid), f'>={min_finite} finite values; missing allowed={allow_missing}; total={len(values)}', 'points')
        if lower is not None:
            self.require(label + ' lower bound', np.all(valid >= lower), float(valid.min()), f'>={lower}', unit)
        if upper is not None:
            self.require(label + ' upper bound', np.all(valid <= upper), float(valid.max()), f'<={upper}', unit)
        return True

    def monotonic(self, label, values, direction, atol=1e-8, unit='1'):
        values = np.asarray(values, dtype=float)
        self.array(label, values, unit=unit)
        delta = np.diff(values)
        worst = float(np.min(delta * direction)) if len(delta) else 0.0
        return self.require(label, worst >= -atol, worst, f'signed consecutive change >= {-atol}', unit,
                            {'absolute': atol}, 'justified_sensitivity')

    def _state(self, fluid, label):
        # Equipment may leave transport/phase density caches uninitialized.
        # Initialize properties without a new equilibrium flash or changing the state.
        fluid.initProperties()
        T, P = float(fluid.getTemperature('K')), float(fluid.getPressure('bara'))
        self.require(label + ' absolute temperature', math.isfinite(T) and T > 0, T, '>0 K', 'K')
        self.require(label + ' absolute pressure', math.isfinite(P) and P > 0, P, '>0 bara', 'bara')
        z = np.asarray(fluid.getMolarComposition(), dtype=float)
        self.array(label + ' overall mole fractions', z, 0.0, 1.0 + 1e-10)
        self.close(label + ' overall composition sum', z.sum(), 1.0, atol=1e-8, category='composition_balance')
        phase_z = np.zeros(len(z))
        beta_total = 0.0
        for i in range(int(fluid.getNumberOfPhases())):
            phase = fluid.getPhase(i)
            beta = float(fluid.getBeta(i))
            self.require(label + ' phase amount bound', math.isfinite(beta) and -1e-12 <= beta <= 1 + 1e-10,
                         beta, '[0,1]', tolerance={'absolute': 1e-10}, category='composition_balance')
            beta_total += beta
            if beta <= 1e-12:
                continue
            x = np.array([float(phase.getComponent(k).getx()) for k in range(len(z))])
            self.array(label + ' phase mole fractions', x, -1e-12, 1.0 + 1e-8)
            self.close(label + ' phase composition sum', x.sum(), 1.0, atol=1e-7, category='composition_balance')
            phase_z += beta * x
            rho = float(phase.getDensity('kg/m3'))
            self.require(label + ' phase density', math.isfinite(rho) and rho > 0, rho, '>0', 'kg/m3')
        self.close(label + ' phase fractions sum', beta_total, 1.0, atol=1e-7, category='composition_balance')
        self.close(label + ' flash component reconstruction', np.max(np.abs(phase_z - z)), 0.0,
                   atol=1e-7, category='component_balance')

    def state(self, fluid, label, candidate=False):
        previous = self._candidate
        self._candidate = candidate
        try:
            self._state(fluid, label)
            return True
        finally:
            self._candidate = previous

    @staticmethod
    def _stream_totals(streams):
        mass, enthalpy = 0.0, 0.0
        components = defaultdict(float)
        for stream in streams:
            flow = float(stream.getFlowRate('kg/sec'))
            fluid = stream.getFluid()
            mass += flow
            if abs(flow) < 1e-16:
                continue
            enthalpy += flow * float(fluid.getEnthalpy('J/kg'))
            molar_rate = flow / float(fluid.getMolarMass())
            for i, z in enumerate(fluid.getMolarComposition()):
                components[str(fluid.getComponent(i).getComponentName())] += molar_rate * float(z)
        return mass, enthalpy, components

    def _equipment(self, equipment, label):
        kind = str(equipment.getClass().getSimpleName())
        if kind == 'ProcessSystem':
            for item in equipment.getUnitOperations():
                self._equipment(item, label + '/' + str(item.getName()))
            return
        if kind == 'Stream':
            flow = float(equipment.getFlowRate('kg/sec'))
            self.require(label + ' nonnegative flow', math.isfinite(flow) and flow >= -1e-12, flow, '>=0', 'kg/s')
            if flow > 1e-14:
                self._state(equipment.getFluid(), label)
            return
        known = {'Separator', 'ThreePhaseSeparator', 'Mixer', 'StaticMixer', 'Splitter', 'ThrottlingValve',
                 'Compressor', 'Pump', 'Expander', 'Cooler', 'Heater', 'HeatExchanger', 'PipeBeggsAndBrills', 'SimpleTEGAbsorber'}
        if kind not in known:
            self.uncovered.add(kind + ': requires a domain-specific check rather than the generic steady-state balance')
            return
        inlets, outlets = list(equipment.getInletStreams()), list(equipment.getOutletStreams())
        if kind == 'SimpleTEGAbsorber':
            inlets = [equipment.getGasInStream(), equipment.getSolventInStream()]
            outlets = [equipment.getGasOutStream(), equipment.getSolventOutStream()]
        if not inlets or not outlets:
            self.uncovered.add(kind + ': stream introspection incomplete')
            return
        for side, streams in [('in', inlets), ('out', outlets)]:
            for i, stream in enumerate(streams):
                if abs(float(stream.getFlowRate('kg/sec'))) > 1e-14:
                    self._state(stream.getFluid(), f'{label}/{side}{i}')
        mi, hi, ci = self._stream_totals(inlets)
        mo, ho, co = self._stream_totals(outlets)
        if abs(mo-mi) > 1e-8 + 1e-7*abs(mi):
            print('MASS DIAGNOSTIC', label, kind, mi, mo, dict(ci), dict(co))
        self.close(label + ' total mass', mo, mi, atol=1e-8, rtol=1e-7, unit='kg/s', category='mass_balance')
        scale = max(sum(abs(v) for v in ci.values()), 1.0)
        error = max([abs(co[k] - ci[k]) for k in set(ci) | set(co)] or [0.0])
        self.close(label + ' component molar flow', error, 0.0, atol=1e-7 * scale,
                   unit='mol/s', category='component_balance')
        duty = None
        if kind in {'Separator', 'ThreePhaseSeparator', 'Mixer', 'StaticMixer', 'Splitter', 'ThrottlingValve', 'HeatExchanger', 'SimpleTEGAbsorber'}:
            duty = 0.0
        elif kind in {'Compressor', 'Pump', 'Expander'}:
            duty = float(equipment.getPower('kW')) * 1000.0
        elif kind in {'Cooler', 'Heater'}:
            duty = float(equipment.getDuty())
        if duty is not None:
            energy_scale = max(abs(hi), abs(ho), abs(duty), 1.0)
            if abs(ho - hi - duty) > 1e-5 * energy_scale:
                print('ENERGY DIAGNOSTIC', label, kind, 'Hin W', hi, 'Hout W', ho, 'duty W', duty,
                      'inlets', [(str(s.getName()), float(s.getFlowRate('kg/hr'))) for s in inlets],
                      'outlets', [(str(s.getName()), float(s.getFlowRate('kg/hr'))) for s in outlets])
            self.close(label + ' first law', ho - hi, duty, atol=1e-5 * energy_scale,
                       unit='W', category='energy_balance')
        if kind in {'ThrottlingValve', 'Compressor', 'Pump', 'Expander'}:
            pin, pout = float(inlets[0].getPressure('bara')), float(outlets[0].getPressure('bara'))
            sign = 1 if kind in {'Compressor', 'Pump'} else -1
            self.require(label + ' pressure direction', sign * (pout - pin) >= -1e-7,
                         pout - pin, 'nonnegative rise' if sign == 1 else 'nonpositive drop', 'bar')
        if kind == 'Compressor':
            self.require(label + ' gas at suction', bool(inlets[0].getFluid().hasPhaseType('gas')),
                         str(inlets[0].getFluid().getPhase(0).getType()), 'gas phase present')

    def run(self, equipment, label, candidate=False):
        previous = self._candidate
        self._candidate = candidate
        try:
            self._equipment(equipment, label)
            return True
        finally:
            self._candidate = previous

    def check_published_figures(self):
        from book_figure_tools import FIGURE_RECORDS
        for record in FIGURE_RECORDS:
            filename = Path(record['path']).name
            for index, series in enumerate(record['series']):
                label = f'{filename} panel {series["panel"]} curve {index+1}'
                self.require(label + ' plotted finite coverage', series['n_points'] > series['n_nonfinite'],
                             series['n_points'] - series['n_nonfinite'], '>0 finite plotted values', 'points', category='figure_domain')
                for axis in ('x', 'y'):
                    unit = series[axis + '_label'].lower()
                    low = series[axis + '_min']
                    if low is None:
                        continue
                    # Only absolute-pressure labels qualify; differences and gauge readings may be negative.
                    if '(bara)' in unit and 'drop' not in unit and 'difference' not in unit:
                        self.require(label + f' {axis} absolute pressure', low >= 0.0, low, '>=0', 'bara', category='figure_domain')
                    if 'density' in unit and 'change' not in unit and 'difference' not in unit:
                        self.require(label + f' {axis} density', low >= 0.0, low, '>=0', unit, category='figure_domain')

    def finish(self):
        self.check_published_figures()
        self.finished = True
        self.save()
        assert not self.failures, f'{len(self.failures)} physical verification failures'
        print(f'Physics verification: {len(self.records)} distinct checks, '
              f'{sum(r["evaluations"] for r in self.records.values())} evaluations; '
              f'{len(self.rejected_candidates)} rejected nonphysical candidates.')
        return True

    def save(self):
        result = {'chapter': self.chapter, 'notebook': str(self.notebook.relative_to(self.book)),
                  'status': 'passed' if self.finished and not self.failures else 'incomplete_or_failed',
                  'checked_at': datetime.now(timezone.utc).isoformat(), 'checks': list(self.records.values()),
                  'failures': self.failures, 'rejected_candidates': self.rejected_candidates,
                  'uncovered_equipment': sorted(self.uncovered), 'finished': self.finished,
                  'scope': 'Computed-case physical verification. Does not establish independent model accuracy or field calibration.'}
        result['domain_scope'] = getattr(self, 'domain_scope', None)
        result['case_evidence'] = getattr(self, 'case_evidence', None)
        self.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
