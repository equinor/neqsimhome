from pathlib import Path
import os,sys
ROOT=Path(__file__).resolve().parent;BOOK=ROOT.parents[1]
sys.path.insert(0,str(BOOK/'.build/python_packages'));sys.path.insert(0,str(Path(os.environ['NEQSIM_PROJECT_ROOT'])/'devtools'))
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=Path(os.environ['NEQSIM_PROJECT_ROOT']),recompile=False,verbose=False)
import jpype
j=jpype.JPackage('neqsim')
for T in [25,50,100]:
    for P in [120,125,130,200]:
        f=j.thermo.system.SystemSrkEos(T+273.15,float(P))
        for c,z in [('methane',.7),('ethane',.10),('propane',.08),('n-butane',.05),('n-pentane',.04),('n-hexane',.03)]:f.addComponent(c,z)
        f.setMixingRule('classic');j.thermodynamicoperations.ThermodynamicOperations(f).TPflash();f.initProperties()
        print(T,P,'default beta',f.getBeta(),[(str(f.getPhase(i).getType()),float(f.getBeta(i))) for i in range(f.getNumberOfPhases())])
