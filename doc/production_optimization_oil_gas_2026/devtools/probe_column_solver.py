"""Bounded AUTO attempt on the exact standalone manuscript deethanizer."""
from pathlib import Path
import os,sys,re,json,time
B=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(B/'.build/python_packages'),r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim\devtools']
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim',recompile=False,verbose=False)
import jpype
scope={'jneqsim':jpype.JPackage('neqsim')}
p=next((B/'chapters').glob('ch33*/chapter.md'))
blocks=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',p.read_text(encoding='utf-8-sig'),re.M|re.S))
code=blocks[3][3].replace('deethanizer.addFeedStream(ngl_feed, 15)', '''deethanizer.addFeedStream(ngl_feed, 15)
deethanizer.setSolverType(DistillationColumn.SolverType.AUTO)
deethanizer.setMaxNumberOfIterations(100, True)''')
started=time.monotonic()
exec(code,scope)
column=scope['deethanizer']
result={'solved':bool(column.solved()),'status':str(column.getLastSolveStatus()),'seconds':time.monotonic()-started,
        'overhead_temperature_C':float(scope['ethane_product'].getTemperature('C')),
        'bottoms_temperature_C':float(scope['c3plus_bottoms'].getTemperature('C'))}
(B/'verification/ch33_auto_solver_probe.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result),flush=True)
os._exit(0)
