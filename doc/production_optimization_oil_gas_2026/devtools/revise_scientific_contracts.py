"""Meaningful local physical/statistical contracts for solver and calibration examples."""
from pathlib import Path
import re,json
B=Path(__file__).resolve().parents[1];changes=[]
def load(n):
 global p,t,chapter
 chapter=n;p=next((B/'chapters').glob(f'ch{n:02}*/chapter.md'));t=p.read_text(encoding='utf-8-sig')
 b=B/'.build/backups/scientific_revision'/p.parent.name/'contracts_input.md';b.parent.mkdir(parents=True,exist_ok=True)
 if not b.exists():b.write_text(t,encoding='utf-8')
def r(a,b):
 global t
 assert a in t,a[:100]
 t=t.replace(a,b);changes.append({'chapter':chapter,'before':a,'after':b})
def fence(n,code,annotation=None):
 global t
 m=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',t,re.M|re.S))[n-1]
 new='```'+m[1]+(m[2] if annotation is None else annotation)+'\n'+code.rstrip()+'\n```'
 t=t[:m.start()]+new+t[m.end():];changes.append({'chapter':chapter,'fence':n,'scope':'physical/statistical contract'})
def get(n):return list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',t,re.M|re.S))[n-1][3]
def save():p.write_text(t,encoding='utf-8')
load(31)
c=get(1)
c=c.replace('# PH flash', '''# Independent phase and component checks at the TP solution.
import numpy as np
def phase_checks(system):
    z=np.array(system.getMolarComposition(),dtype=float)
    reconstructed=np.zeros(len(z))
    for phase_index in range(system.getNumberOfPhases()):
        phase=system.getPhase(phase_index)
        x=np.array([phase.getComponent(i).getx() for i in range(len(z))])
        assert abs(x.sum()-1)<1e-8 and np.all(x>=0)
        reconstructed += float(system.getBeta(phase_index))*x
    assert np.max(np.abs(z-reconstructed))<1e-7
    if system.getNumberOfPhases()==2:
        for i in range(len(z)):
            fugacity_terms=[float(system.getPhase(j).getComponent(i).getx()*
                system.getPhase(j).getComponent(i).getFugacityCoefficient())
                for j in range(2)]
            if min(fugacity_terms)>1e-12:
                assert abs(np.log(fugacity_terms[0]/fugacity_terms[1]))<1e-5
phase_checks(fluid)

# PH flash''',1)
c+='''
phase_checks(fluid)
enthalpy_residual=abs(float(fluid.getEnthalpy('J/mol'))-target_enthalpy)
assert enthalpy_residual/max(abs(target_enthalpy),1.0)<1e-7
assert fluid.getPressure('bara')==50.0
print('Accepted PH relative enthalpy residual',enthalpy_residual/max(abs(target_enthalpy),1.0))
'''
fence(1,c)
c=get(3).replace('    for unit in [mixer, cooler_loop, separator, splitter_loop]: unit.run()', '''    mixer.run();cooler_loop.run()
    # Fresh separator avoids its native 1e-6 cache masking a 1e-7 tear test.
    separator=Separator('Loop separator',cooler_loop.getOutletStream())
    separator.run()
    splitter_loop=Splitter('Gas recycle split',separator.getGasOutStream())
    splitter_loop.setSplitFactors([0.35,0.65]);splitter_loop.run()''')
c+='''
products=[separator.getLiquidOutStream(),splitter_loop.getSplitStream(1)]
mass_out=sum(float(s.getFlowRate('kg/hr')) for s in products)
mass_error=abs(mass_out-50000.0)/50000.0
h_in=float(feed.getFluid().getEnthalpy())
h_out=sum(float(s.getFluid().getEnthalpy()) for s in products)
energy_error=abs(h_out-h_in-float(cooler_loop.getDuty()))/max(abs(h_in),abs(h_out),1.0)
assert mass_error<1e-7 and energy_error<1e-7,(mass_error,energy_error)
for i in range(feed.getFluid().getNumberOfComponents()):
    ni=float(feed.getFluid().getComponent(i).getNumberOfmoles())
    no=sum(float(s.getFluid().getComponent(i).getNumberOfmoles()) for s in products)
    assert abs(no-ni)/float(feed.getFluid().getTotalNumberOfMoles())<1e-7
print('Accepted recycle boundary',mass_error,energy_error)
'''
fence(3,c)
c=get(5)+'''
assert 5.0<=outlet_P<=95.0 and abs(outlet_T-40.0)<1e-4
assert abs(valve.getOutletStream().getFlowRate('kg/hr')-50000.0)<1e-5
assert abs(valve.getOutletStream().getFluid().getEnthalpy()-feed2.getFluid().getEnthalpy())/max(abs(feed2.getFluid().getEnthalpy()),1.0)<1e-6
# Final independent valve replay at the accepted pressure.
replay_valve=ThrottlingValve('Independent JT replay',feed2)
replay_valve.setOutletPressure(outlet_P);replay_valve.run()
assert abs(replay_valve.getOutletStream().getTemperature('C')-40.0)<1e-4
'''
fence(5,c)
c=get(6)
c=re.sub(r'# Select solver type.*?column.setSolverType', '# Select a current solver enum; compare enabled physical residual gates.\ncolumn.setSolverType',c,flags=re.S)
fence(6,c)
save()
load(32)
r('| `getKneePoint()` | A normalized geometric compromise among sampled points; not an economic decision |','| Application decision rule | Select among sampled non-dominated points using declared economics or preferences; no `getKneePoint()` API is supplied |')
r('Reconciling transient data produces meaningless results.', 'Steady-state balance reconciliation is inappropriate when unmodeled accumulation is significant; dynamic reconciliation is a different formulation.')
r(r'R = \frac{1}{N-1} \sum_{k=1}^{N-1} \frac{(y_k - \bar{y})(y_{k+1} - \bar{y})}{s_y^2}',r'R = \frac{\sum_{k=1}^{N-1}(y_{k+1}-y_k)^2}{2(N-1)s_y^2}')
r('For a truly random (steady-state) process, $R \\approx 0$. For a process with trends (transient), $R \\rightarrow 1$.', 'For independent, stationary finite-variance noise, $R$ is near one; slow trends often reduce it. The native implementation handles negligible sample variance separately. Autocorrelation, oscillation and sensor freeze require additional checks; this ratio alone does not prove steady state.')
r(r'z_i = \frac{y_i - \hat{y}_i}{\sigma_i \sqrt{1 - r_{ii}}}',r'z_i = \frac{\hat{y}_i-y_i}{\sqrt{V_{ii}-V^{\mathrm{adj}}_{ii}}}')
r('where $r_{ii}$ is the diagonal element of the residual projection matrix. If $|z_i| > z_{\\alpha/2}$ (typically 1.96 for 95% confidence), the measurement is flagged as having a gross error — indicating a sensor fault, calibration drift, or data entry error.', r'For full-row-rank linear constraints, $V^{\mathrm{adj}}=V-VA^T(AVA^T)^{-1}AV$. This is the reconciled covariance, so the denominator is the standard deviation of the **adjustment**. The native method uses this expression. A two-sided Gaussian screen uses $z_{1-\alpha/2}$ (1.96 for an individual 95% test). Multiple tests, correlated errors and uncertain model constraints affect false-alarm rates; a flag is evidence for investigation, not proof of a faulty sensor. A zero adjustment variance provides no identifiable residual test.')
for old,new in [('`runFullFactorial()`','`.vary(...).build().run()`'),('`runOneAtATime()`','Application-built parameter cases'),('`runLatinHypercube(N)`','External LHS sampling and explicit cases'),('`runRandom(N)`','External seeded sampling and explicit cases')]:r(old,new)
r('A complete model calibration workflow:\n\n**Execution scope:** requires measured time series, reconciler constraints and calibration data.', 'The following self-contained local fixture checks native steady-state statistics against the explicit equation, reconciled flows against an independent linear-algebra solution, and recovery of a known compressor efficiency from three synthetic temperature observations. It uses native kelvin observation values because this estimator path does not convert the declared unit string. Synthetic recovery is a contract test, not field calibration or independent EOS validation. Site use still requires time alignment, quality flags, realistic covariance and identifiable parameters.')
fence(16,'''import jpype
import numpy as np
import json
from pathlib import Path
jneqsim=jpype.JPackage('neqsim')
SteadyStateVariable=jneqsim.process.util.reconciliation.SteadyStateVariable
DataReconciliationEngine=jneqsim.process.util.reconciliation.DataReconciliationEngine
ReconciliationVariable=jneqsim.process.util.reconciliation.ReconciliationVariable
BatchParameterEstimator=jneqsim.process.calibration.BatchParameterEstimator
values=60.0+np.random.default_rng(42).normal(0,0.02,60)
signal=SteadyStateVariable('Synthetic pressure')
signal.setWindowSize(60)
for value in values:signal.addValue(float(value))
expected_r=float(np.sum(np.diff(values)**2)/(2*59*np.var(values,ddof=1)))
assert abs(signal.getRStatistic()-expected_r)<1e-10

measured=np.array([100000.0,70000.0,28000.0,5000.0])
sigma=np.array([2000.0,1500.0,1000.0,500.0])
A=np.array([[1.0,-1.0,-1.0,-1.0]])
V=np.diag(sigma**2)
expected=measured-V@A.T@np.linalg.solve(A@V@A.T,A@measured)
engine=DataReconciliationEngine()
names=['Feed','Gas','Oil','Water']
for name,value,sd in zip(names,measured,sigma):
    engine.addVariable(ReconciliationVariable(name,float(value),float(sd)))
engine.addConstraint(jpype.JArray(jpype.JDouble)(A[0].tolist()),'Mass balance')
reconciliation=engine.reconcile()
actual=np.array([engine.getVariable(n).getReconciledValue() for n in names])
assert reconciliation.isConverged()
assert np.max(np.abs(actual-expected))<1e-6 and abs(float(A@actual))<1e-6

def calibration_fixture(eta,discharge):
    fluid=jneqsim.thermo.system.SystemSrkEos(313.15,60.0)
    fluid.addComponent('methane',.9);fluid.addComponent('ethane',.1)
    fluid.setMixingRule('classic')
    feed=jneqsim.process.equipment.stream.Stream('Feed',fluid)
    feed.setFlowRate(100000.0,'kg/hr')
    comp=jneqsim.process.equipment.compressor.Compressor('Compressor',feed)
    comp.setUsePolytropicCalc(True);comp.setPolytropicEfficiency(eta)
    comp.setOutletPressure(discharge,'bara')
    process=jneqsim.process.processmodel.ProcessSystem()
    process.add(feed);process.add(comp);process.run()
    hout=float(comp.getOutletStream().getFluid().getEnthalpy())
    hin=float(feed.getFluid().getEnthalpy());power=float(comp.getPower())
    assert power>0 and abs(hout-hin-power)/power<1e-5
    assert abs(comp.getOutletStream().getFlowRate('kg/hr')-100000.0)<1e-5
    return process,comp

true_eta=.78;observations=[]
for discharge in [130.0,150.0,170.0]:
    _,comp=calibration_fixture(true_eta,discharge)
    observations.append((discharge,float(comp.getOutletStream().getTemperature('K'))))
process,comp=calibration_fixture(.72,150.0)
estimator=BatchParameterEstimator(process)
estimator.addTunableParameter('Compressor.polytropicEfficiency','-',.60,.90,.72)
estimator.addMeasuredVariable('Compressor.outletStream.temperature','K',1.0)
HashMap=jpype.JClass('java.util.HashMap')
for discharge,temperature in observations:
    conditions=HashMap();conditions.put('Compressor.outletPressure',jpype.JDouble(discharge))
    observed=HashMap();observed.put('Compressor.outletStream.temperature',jpype.JDouble(temperature))
    estimator.addDataPoint(conditions,observed)
estimator.setMaxIterations(40);fit=estimator.solve()
estimate=float(fit.getEstimate(0))
assert fit.isConverged() and .60<=estimate<=.90
assert abs(estimate-true_eta)<.002
replay_errors=[]
for discharge,temperature in observations:
    _,independent=calibration_fixture(estimate,discharge)
    replay_errors.append(abs(independent.getOutletStream().getTemperature('K')-temperature))
assert max(replay_errors)<.02
contract=dict(R=expected_r,reconciliation_max_error=float(np.max(np.abs(actual-expected))),
              estimated_efficiency=estimate,maximum_replay_error_K=max(replay_errors),
              native_fit_converged=bool(fit.isConverged()))
Path('ch32_local_calibration_contract.json').write_text(json.dumps(contract,indent=2))
print(json.dumps(contract,indent=2))
''',annotation='')
save()
(B/'verification/scientific_revision/contracts_corrections.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
print(len(changes),'contract edits')
