"""Correct field/network contracts and the runnable screening example."""
from pathlib import Path
import re
BOOK=Path(__file__).resolve().parents[1]
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```', re.M|re.S)
def change(number, fn):
    path=next((BOOK/'chapters').glob(f'ch{number:02d}_*/chapter.md'))
    text=path.read_text(encoding='utf-8-sig')
    for n,m in reversed(list(enumerate(PAT.finditer(text),1))):
        v=fn(n,m[1],m[3])
        if v is None: continue
        note,code=v if isinstance(v,tuple) else (m[2],v)
        text=text[:m.start()]+f'```{m[1]}{note}\n{code.rstrip()}\n```'+text[m.end():]
    path.write_text(text,encoding='utf-8')

def ch28(n, language, code):
    code=code.replace('setGORSpacing(', 'setGorSpacing(').replace('getTotalCount()', 'getTotalPoints()')
    code=code.replace('setElevation(-2800.0)', 'setAngle(90.0)')
    code=code.replace('setElevation(0.0)', 'setAngle(0.0)')
    code=code.replace('"production_vfp.inc"','"production_screening.txt"')
    code=code.replace('VFP table exported', 'Process screening diagnostics exported')
    if language=='java': return code
    if n==13:
        code=code.replace('PipeBeggsAndBrills("Export", tubing.getOutletStream())', 'PipeBeggsAndBrills("Flowline", tubing.getOutletStream())')
        code=code.replace('    process.add(flowline)\n', '    process.add(flowline)\n    process.add(Stream("Export", flowline.getOutletStream()))\n')
        code=code.replace('[5000, 10000, 20000, 30000, 50000]', '[5000.0, 10000.0, 20000.0]')
        code=code.replace('[30, 40, 50, 60]', '[30.0, 50.0]')
        code=code.replace('[0.05, 0.20, 0.40]', '[0.05]')
        code=code.replace('[300, 1000, 3000, 8000]', '[300.0, 1000.0]')
        code=code.replace('vfp_gen.setFlashGenerator(flash_gen)', 'vfp_gen.setFlashGenerator(flash_gen)\nvfp_gen.setFlowRateUnit("kg/hr")\nvfp_gen.setInletTemperature(358.15)')
        code=code.replace('vfp_gen.exportVFPEXP("production_screening.txt", 1)',
                          'from pathlib import Path\nPath("production_screening.txt").write_text(str(vfp_gen.toDiagnosticString()), encoding="utf-8")')
        code += '\nfeed = process.getUnit("Feed")\nfluid = ref_fluid\ncreate_base_process = create_process\n'
        return code
    if n==14:
        return (' pattern: requires a qualified well model and actual well-test data',code)
    if n==15:
        return (' pattern: network assembly requires field-specific nodes and verified boundary data',code)
    if n==19:
        return (' pattern: requires configured network tubing elements and water-cut data',code)
    if n==20:
        setup='''MaterialBalanceGasDrive = jneqsim.process.fielddevelopment.integrated.MaterialBalanceGasDrive
WellDeliverabilityCurve = jneqsim.process.fielddevelopment.integrated.WellDeliverabilityCurve
driveA = MaterialBalanceGasDrive(250.0, 5.0e9, 0.90)
driveB = MaterialBalanceGasDrive(220.0, 3.0e9, 0.90)
curveA = WellDeliverabilityCurve.fromVogel(2.0e6, 250.0)
curveB = WellDeliverabilityCurve.fromVogel(1.5e6, 220.0)
'''
        return setup+code
    if n==22:
        code=code.replace('flow_rates = [5000, 10000, 20000, 30000, 50000]', 'flow_rates = list(table.getFlowRates())')
        code=code.replace('thp_values = [30, 40, 50, 60]', 'thp_values = list(table.getOutletPressures())')
        code=code.replace('Flow Rate (×1000 Sm³/d)', 'Mass flow (×1000 kg/hr)').replace('THP (bara)', 'Outlet pressure (bara)').replace('BHP (bara)', 'Required inlet pressure (bara)')
        return code.replace('VFP Surface: BHP vs Rate and THP', 'Process screening: inlet pressure vs mass flow and outlet pressure')
    if n==23:
        code=code.replace('flow_rates = [5000, 10000, 20000, 30000, 50000]', 'flow_rates = list(table.getFlowRates())')
        code=code.replace('gor_values = [300, 1000, 3000, 8000]', 'gor_values = list(table.getGORs())')
        code=code.replace('gor_labels = ["GOR=300", "GOR=1000", "GOR=3000", "GOR=8000"]', 'gor_labels = [f"GOR={gor:g}" for gor in gor_values]')
        code=code.replace('table.getBHP(r_idx, 1, 1, g_idx)', 'table.getBHP(r_idx, 1, 0, g_idx)')
        code=code.replace('Flow Rate (×1000 Sm³/d)', 'Mass flow (×1000 kg/hr)').replace('Required BHP (bara)', 'Required inlet pressure (bara)')
        code=code.replace('VFP Curves at Different GOR Values', 'Process screening at different GOR values').replace('WC=20%, THP=40 bara', 'WC=5%, outlet pressure=50 bara')
        return code
    if n==24:
        return (' pattern: requires supplied well-test data and qualified interpolation routine',code)
    return code

def ch26(n, language, code):
    if n==1:
        return '''import jpype
jneqsim = jpype.JPackage("neqsim")
LoopedPipeNetwork = jneqsim.process.equipment.network.LoopedPipeNetwork
network = LoopedPipeNetwork("Production Network")
# API construction example: AOFP is kg/s here, not standard volume/day.
network.addSourceNode("Reservoir-A", 250.0, 0.0)
network.addJunctionNode("Wellbore-A")
network.addWellIPRVogel("Reservoir-A", "Wellbore-A", "Well-A", 5.0)
print(network.getNodeNames())'''
    if n==3:
        return (' pattern: requires wellstream and calibrated IPR test inputs',code)
    if n==4:
        return code.replace('aofpSm3PerDay=', '').replace('shutInPressureBara=', '')
    if n==5:
        return code.replace('rateSm3PerDay=', '').replace('flowingPressureBara=', '')
    if n==7:
        return (' pattern: requires tubing-specific valid flow envelope and rejection handling',code)
    if n==8:
        return '''# A complete source-gas gathering calculation with explicit nodes and pipe identities.
SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
fluid = SystemSrkEos(313.15, 90.0)
fluid.addComponent("methane", 0.90)
fluid.addComponent("ethane", 0.10)
fluid.setMixingRule("classic")
network = LoopedPipeNetwork("Gathering Network")
network.addSourceNode("Supply-A", 90.0, 10000.0)
network.addJunctionNode("Manifold")
network.addSinkNode("Platform", 10000.0)  # demand in kg/hr
network.setNodeFluid("Supply-A", fluid)
network.addPipe("Supply-A", "Manifold", "Flowline-A", 5000.0, 0.20)
network.addPipe("Manifold", "Platform", "Export", 10000.0, 0.25)
network.run()
assert network.isConverged()
print(network.getNetworkReport())
print("Mass balance residual:", network.getMassBalanceError())'''
    if n==9:
        return code.replace('network.getResidual()', 'network.getMaxResidual()')
    if n==10:
        return (' pattern: algorithm requires caller well identities base rates and choke adapters',code)
    if n==11:
        return code.replace('totalLiftGasSm3PerDay=', '')
    if n==13:
        return '''# Read current gathering-network results on their mass-flow basis.
for name in network.getPipeNames():
    print(name, network.getPipeFlowRate(name), "kg/s",
          network.getPipeVelocity(name), "m/s")
print("Platform pressure:", network.getNodePressure("Platform"), "bara")'''
    if n==14:
        return '''# For facility-aware network allocation, supply an explicit candidate evaluator.
# ProductionOptimizer itself takes ProcessSystem/ProcessModel, not a network constructor.
# This executable allocation example uses the supplied gas-lift response curves.
allocation = GasLiftNetworkOptimizer()
allocation.addWell("Well-A", curve_a)
allocation.addWell("Well-B", curve_b)
answer = allocation.allocate(2.5e6)
assert answer.getTotalLift() <= 2.5e6 * (1 + 1e-9)
print("Allocated oil:", answer.getTotalOil(), "Sm3/day")'''
    if n==15:
        return '''NetworkAllocationOptimizer = jneqsim.process.optimization.valuechain.NetworkAllocationOptimizer
allocation_optimizer = NetworkAllocationOptimizer(2.5e6, 3)
for leg in range(3):
    allocation_optimizer.setBounds(leg, 0.0, 1.2e6)
allocation_optimizer.setTolerance(1e-4)
# Explicit diminishing-return utility; illustrative, not simulated oil production.
def allocation_value(values):
    return sum((i + 1.0) * (max(0.0, float(value)) ** 0.5)
               for i, value in enumerate(values))
answer = allocation_optimizer.optimize(allocation_value)
print(list(answer.getAllocation()), answer.getObjective(), answer.isFeasible())'''
    if n==16:
        setup='''MaterialBalanceGasDrive = jneqsim.process.fielddevelopment.integrated.MaterialBalanceGasDrive
driveA = MaterialBalanceGasDrive(250.0, 5.0e9, 0.90)
driveB = MaterialBalanceGasDrive(220.0, 3.0e9, 0.90)
curveA = WellDeliverabilityCurve.fromVogel(2.0e6, 250.0)
curveB = WellDeliverabilityCurve.fromVogel(1.5e6, 220.0)
'''
        return setup+code

change(28,ch28)
change(26,ch26)
