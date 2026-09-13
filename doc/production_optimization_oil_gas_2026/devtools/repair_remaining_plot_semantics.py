"""One-time editorial corrections with engineering assertions."""
import json
from pathlib import Path
BOOK = Path(__file__).resolve().parents[1]
def apply(number, transform):
    p = next((BOOK/'chapters').glob('ch%02d*/notebooks/*.ipynb' % number))
    nb = json.loads(p.read_text(encoding='utf-8'))
    for c in nb['cells']:
        c['source'] = transform(''.join(c['source']), c['cell_type']).splitlines(True)
    p.write_text(json.dumps(nb, indent=1, ensure_ascii=False)+'\n', encoding='utf-8')

def fluid(s, kind):
    s = s.replace('Liquid Dropout Curve at 90°C (CVD-like)', 'Constant-composition liquid fraction at 90 °C')
    s = s.replace('Maximum liquid dropout:', 'Maximum equilibrium liquid fraction:')
    if 'pressures_bo = ' in s:
        a = s.index('    if fluid.hasPhaseType("oil"):')
        b = s.index('\nvalid_bo =', a)
        s = s[:a] + '''    if not fluid.hasPhaseType("oil"):
        bo_values.append(float('nan'))
        continue
    # Flash the SAME reservoir liquid sample to stock-tank conditions.
    reservoir_oil_volume = float(fluid.getPhase("oil").getVolume("m3"))
    sample = fluid.phaseToSystem("oil")
    sample.setTemperature(288.15)
    sample.setPressure(1.01325)
    ThermodynamicOperations(sample).TPflash()
    sample.initProperties()
    assert sample.hasPhaseType("oil"), "Stock-tank oil phase is required to define Bo"
    stock_oil_volume = float(sample.getPhase("oil").getVolume("m3"))
    bo_values.append(reservoir_oil_volume / stock_oil_volume)
''' + s[b:]
        s = s.replace('ThermodynamicOperations(sample)', 'jneqsim.thermodynamicoperations.ThermodynamicOperations(sample)')
    return s
apply(3, fluid)
apply(5, lambda s,k: s.replace('Gas Lift Optimization - Injection Rate vs Production', 'Illustrative gas-lift response model'))

def capacity(s, kind):
    if 'max_flows = []' in s:
        s = s.replace('5000.0, 300000.0', '5000.0, 1500000.0')
        s = s.replace('    max_flows.append', '    assert best_flow < 1499000.0, "Increase search upper bound; no capacity boundary found"\n    max_flows.append')
    return s
apply(8, capacity)

def quality(s, kind):
    if '# Component heating values' in s:
        a = s.index('# Component heating values')
        b = s.index('print("=== Gas Quality', a)
        s = s[:a] + '''# ISO 6976: 15 C combustion and metering temperatures, volume basis.
iso = jneqsim.standards.gasquality.Standard_ISO6976(gas_std, 15.0, 15.0, "volume")
iso.calculate()
ghv = float(iso.getValue("SuperiorCalorificValue")) / 1000.0
wobbe_index = float(iso.getValue("SuperiorWobbeIndex")) / 1000.0
relative_density = float(iso.getValue("RelativeDensity"))

''' + s[b:]
        s = s.replace('Typical sales gas specification:', 'Illustrative gas-quality screening limits (not a contract):')
    return s
apply(19, quality)

def opt_theory(s, kind):
    s = s.replace('print(f"Engine iterations:     {result_engine.getOptimalValue()}")', 'assert result_engine.isConverged(), "Optimization engine did not converge"')
    if 'gs_max_rate = a' in s:
        s = s.replace('gs_max_rate = a', 'gs_max_rate = a\nassert is_feasible(gs_max_rate), "Search lower bound must be feasible"')
    if 'def find_max_rate_binary' in s:
        s = s.replace('    for _ in range(30):', '    assert is_feasible(low), "Binary-search lower bound is infeasible"\n    assert not is_feasible(high), "Increase binary-search upper bound"\n    for _ in range(30):')
        # The baseline1.2 factor needs0.96/1.44 for exact±20% changes.
        s = s.replace('("- 20%", 1.0)', '("- 20%", 0.96)')
    return s
apply(22, opt_theory)

def opt(s, kind):
    if '# Manual binary search' in s:
        s = s.replace('iteration_log = []', '''iteration_log = []
feed.setFlowRate(low, "kg/hr")
process.run()
assert not process.isAnyEquipmentOverloaded(), "Lower search bound must be feasible"
feed.setFlowRate(high, "kg/hr")
process.run()
assert process.isAnyEquipmentOverloaded(), "Upper search bound must be infeasible"''')
    if 'opt_iters = ' in s:
        s = s.replace('opt_iters = [result_binary.getOptimalValue(), result_golden.getOptimalValue()]', '''# OptimizationResult has no iteration count. Compare independently rerun utilization.
opt_utils = []
for result in (result_binary, result_golden):
    assert result.isConverged(), "Optimization did not converge"
    feed.setFlowRate(float(result.getOptimalValue()), "kg/hr")
    process.run()
    utilization = float(process.findBottleneck().getUtilizationPercent())
    assert utilization <= 100.2, f"Returned optimum is infeasible: {utilization}%"
    opt_utils.append(utilization)
feed.setFlowRate(design_rate, "kg/hr")
process.run()''')
        s = s.replace('opt_iters', 'opt_utils').replace('Iteration count comparison', 'Independently checked utilization')
        s = s.replace("ax2.set_ylabel('Iterations'", "ax2.set_ylabel('Maximum equipment utilization (%)'")
        s = s.replace("ax2.set_title('Convergence Speed'", "ax2.set_title('Feasibility at returned optimum'")
        s = s.replace('str(val), ha=', "f'{val:.2f}%', ha=")
    return s
apply(24, opt)
print('Updated chapters03,05,08,19,22,24; execute affected notebooks.')
