exec(open(__file__.replace('probe_ch24_phase_extraction.py','probe_ch24_knockout.py'),encoding='utf-8').read().split('code=matches[68]')[0])
code=matches[68].group(3).split('# Check axial discretization')[0]
ns={'__name__':'__main__'};exec(code,ns)
ns['feed'].setFlowRate(250000.,'kg/hr');ns['feed'].setPressure(80.,'bara');ns['comp'].setOutletPressure(140.)
ns['run_facility']();original=ns['cooler'].getOutletStream().getFluid()
import jpype
j=jpype.JPackage('neqsim');rows=[]
for mode in ['original','repeat_flash','init0_flash','init0_multiphase_false_then_true']:
 f=original.clone()
 if mode.startswith('init0'):f.init(0)
 if mode=='init0_multiphase_false_then_true':
  f.setMultiPhaseCheck(False);j.thermodynamicoperations.ThermodynamicOperations(f).TPflash();f.setMultiPhaseCheck(True)
 if mode!='original':j.thermodynamicoperations.ThermodynamicOperations(f).TPflash()
 f.initProperties();st=j.process.equipment.stream.Stream('Probe',f)
 sep=j.process.equipment.separator.ThreePhaseSeparator('Probe knockout',st);sep.run()
 mi=float(st.getFlowRate('kg/hr'));mo=sum(float(o.getFlowRate('kg/hr')) for o in sep.getOutletStreams())
 r={'mode':mode,'mi':mi,'mo':mo,'residual':(mo-mi)/mi,'total_moles':float(f.getTotalNumberOfMoles()),
    'phase_moles':[float(f.getPhase(k).getNumberOfMolesInPhase()) for k in range(f.getNumberOfPhases())]}
 try:r['checks']=unit_checks(sep);r['status']='passed'
 except Exception as e:r['status']='failed';r['error']=str(e)
 rows.append(r);print(r,flush=True)
(B/'verification/scientific_revision/ch24_phase_extraction_probe.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
sys.stdout.flush();os._exit(0)
