from pathlib import Path
import sys,os,re,json
B=Path(__file__).resolve().parents[1];S=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
sys.path[:0]=[str(B/'.build/python_packages'),str(S/'devtools'),str(B/'devtools')]
os.environ['_JAVA_OPTIONS']='-Xmx512m'
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=S,recompile=False,verbose=False)
from optimization_solution_helpers import *
p=next((B/'chapters').glob('ch24_*'))/'chapter.md';matches=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',p.read_text(encoding='utf-8'),re.M|re.S))
code=matches[68].group(3).split('# ─── Step 3:')[0]
code=code.replace('separator.Separator(', 'separator.ThreePhaseSeparator(')
ns={'__name__':'__main__'};exec(code,ns)
cases=[]
for rate in (250000.,350000.):
 for a in (50.,60.,70.,80.):
  for b in (120.,140.,160.,180.):
   ns['feed'].setFlowRate(rate,'kg/hr');ns['feed'].setPressure(a,'bara');ns['comp'].setOutletPressure(b)
   ns['run_facility']()
   ko=ns['export_ko'];mi=float(ko.getInletStreams()[0].getFlowRate('kg/hr'));outs=list(ko.getOutletStreams())
   record={'q':rate,'p':a,'outp':b,'mi':mi,'outs':[float(s.getFlowRate('kg/hr')) for s in outs],
     'inphases':ko.getInletStreams()[0].getFluid().getNumberOfPhases()}
   try:record['checks']=process_checks(ns['process']);record['status']='passed'
   except Exception as ex:record['status']='failed';record['error']=str(ex)
   cases.append(record);print(record['q'],a,b,record['status'],record.get('error',''),flush=True)
   (B/'verification/scientific_revision/ch24_threephase_knockout_probe.json').write_text(json.dumps(cases,indent=2),encoding='utf-8')
sys.stdout.flush();os._exit(0 if all(c['status']=='passed' for c in cases) else 1)
