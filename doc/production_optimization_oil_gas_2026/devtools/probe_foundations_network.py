from pathlib import Path
import sys,os,json
BOOK=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BOOK/'.build/python_packages'))
SRC=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
sys.path.insert(0,str(SRC/'devtools'))
os.environ['JAVA_TOOL_OPTIONS']='-Xmx512m'
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=SRC,recompile=False,verbose=False)
import jpype
j=jpype.JPackage('neqsim')
out=[]
for mode in [True,False]:
 for relax in [1.0,0.5]:
  net=j.process.equipment.network.LoopedPipeNetwork('accepted choke test')
  f=j.thermo.system.SystemSrkEos(303.15,90)
  f.addComponent('methane',.95);f.addComponent('ethane',.05);f.setMixingRule('classic')
  net.setFluidTemplate(f)
  net.addSourceNode('SourceA',90.0,0.0);net.addSourceNode('SourceB',85.0,0.0)
  net.addJunctionNode('DownA');net.addJunctionNode('DownB')
  net.addSinkNode('Plant',0.0);net.getNode('Plant').setPressure(40e5);net.getNode('Plant').setPressureFixed(True)
  net.addChoke('SourceA','DownA','Choke-A',20,80);net.addChoke('SourceB','DownB','Choke-B',15,80)
  net.addPipe('DownA','Plant','Line-A',5000,.2032);net.addPipe('DownB','Plant','Line-B',4000,.2032)
  net.getPipe('Choke-A').setChokeUseValveModel(mode);net.getPipe('Choke-B').setChokeUseValveModel(mode)
  net.setSolverType(j.process.equipment.network.LoopedPipeNetwork.SolverType.NEWTON_RAPHSON)
  net.setMaxIterations(200);net.setTolerance(100);net.setRelaxationFactor(relax)
  for opening in [40,60,80,100]:
   net.getPipe('Choke-A').setChokeOpening(opening);net.run()
   row=dict(mode=mode,relaxation=relax,opening=opening,converged=bool(net.isConverged()),residual_Pa=net.getMaxResidual(),mass_error_kg_s=net.getMassBalanceError(),flow_kg_s=net.getTotalSinkFlow(),pA_Pa=net.getNode('DownA').getPressure(),pB_Pa=net.getNode('DownB').getPressure(),statusA=str(net.getPipe('Choke-A').getChokeModelStatus()))
   out.append(row);print(json.dumps(row),flush=True)
(BOOK/'verification/scientific_revision/network_probe.json').write_text(json.dumps(out,indent=2))
