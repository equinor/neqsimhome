from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
for ch in (21,24,32):
 p=next((B/'chapters').glob(f'ch{ch:02d}*/chapter.md'));text=p.read_text(encoding='utf-8-sig')
 for n,m in reversed(list(enumerate(PAT.finditer(text),1))):
  code=m[3];old=code;annotation=m[2]
  if ch==21 and n==25:
   code='import jpype\njneqsim = jpype.JPackage("neqsim")\nProductionOptimizer = jneqsim.process.util.optimizer.ProductionOptimizer\n'+code
  if ch==24 and n==64:
   annotation=''
   code='''import neqsim.process.util.reconciliation.*;
DataReconciliationEngine reconciler = new DataReconciliationEngine();
// Synthetic readings with standard-deviation uncertainties, all kg/hr.
reconciler.addVariable(new ReconciliationVariable("feed",200000.0,2000.0));
reconciler.addVariable(new ReconciliationVariable("gas",150000.0,1500.0));
reconciler.addVariable(new ReconciliationVariable("oil",48000.0,1000.0));
reconciler.addVariable(new ReconciliationVariable("water",5000.0,500.0));
reconciler.addConstraint(new double[]{1.0,-1.0,-1.0,-1.0},"Mass balance");
ReconciliationResult reconciliation = reconciler.reconcile();
if (!reconciliation.isConverged()) { throw new IllegalStateException(reconciliation.getErrorMessage()); }
logger.info("Chi-square {}, global test passed {}",reconciliation.getChiSquareStatistic(),reconciliation.isGlobalTestPassed());
logger.info("Mass-balance residuals kg/hr: {}",Arrays.toString(reconciliation.getConstraintResidualsAfter()));'''
  if ch==24 and n==65:
   annotation=''
   code='''for (ReconciliationVariable suspect : reconciliation.getGrossErrors()) {
    logger.warn("Suspect {} normalized residual {}",suspect.getName(),suspect.getNormalizedResidual());
}'''
  if ch==32 and n==14:
   annotation=''
   code='''import neqsim.process.calibration.BatchParameterEstimator;
import neqsim.process.calibration.BatchResult;
// Recovery experiment using synthetic observations generated at known efficiency.
compressor.setUsePolytropicCalc(true);
compressor.setPolytropicEfficiency(0.78);
feed.setFlowRate(100000.0,"kg/hr");
feed.setPressure(60.0,"bara");
BatchParameterEstimator estimator = new BatchParameterEstimator(process);
estimator.addTunableParameter("Compressor.polytropicEfficiency","-",0.60,0.90,0.72);
estimator.addMeasuredVariable("Compressor.outletStream.temperature","C",1.0);
for (double discharge : new double[]{130.0,150.0,170.0}) {
    compressor.setOutletPressure(discharge,"bara");
    process.run();
    Map<String,Double> conditions = new HashMap<String,Double>();
    conditions.put("Compressor.outletPressure",discharge);
    Map<String,Double> observations = new HashMap<String,Double>();
    observations.put("Compressor.outletStream.temperature",compressor.getOutletStream().getTemperature("C"));
    estimator.addDataPoint(conditions,observations);
}
compressor.setPolytropicEfficiency(0.72);
estimator.setMaxIterations(40);
BatchResult fit = estimator.solve();
logger.info("Converged {}, estimated efficiency {}, RMSE {}",fit.isConverged(),fit.getEstimate(0),fit.getRMSE());
if (!Double.isFinite(fit.getEstimate(0))) { throw new IllegalStateException("Non-finite fitted efficiency"); }
// Synthetic recovery tests exercise the estimator; independent plant data are still required.
// Separator diameter is not identified by equilibrium outlet temperature in this model.'''
  if ch==32 and n==15:
   code=code.replace('"Compressor.polytropicEfficiency", "-", 0.6, 0.9)', '"Compressor.polytropicEfficiency", "-", 0.6, 0.9, 0.75)')
   code=code.replace('estimator.estimate()', 'fit = estimator.solve()').replace('estimator.getEstimatedParameters().get(', 'fit.getEstimate(')
   code=code.replace('engine.getReconciledValue(', 'engine.getVariable(').replace('"Compressor Outlet Temperature"))))', '"Compressor Outlet Temperature").getReconciledValue())))')
  if code!=old or annotation!=m[2]:text=text[:m.start()]+'```'+m[1]+annotation+'\n'+code.rstrip()+'\n```'+text[m.end():]
 text=text.replace('**Execution scope:** requires a measured-variable reconciliation model and statistical acceptance policy.\n\n','')
 text=text.replace('**Execution scope:** requires calibration observations, current estimator adapters and an identifiability study.\n\n','')
 p.write_text(text,encoding='utf-8')
