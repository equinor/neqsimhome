from pathlib import Path
import os,sys,json
BOOK=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BOOK/'.build/python_packages'))
ROOT=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
sys.path.insert(0,str(ROOT/'devtools'))
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=ROOT,recompile=False,verbose=False)
import jpype
j=jpype.JPackage('neqsim')
for mode in ['raw','init','multiphase']:
    for P in [20,70,150]:
        f=j.thermo.system.SystemSrkCPAstatoil(273.15+15,P)
        for name,z in [('methane',.90398),('ethane',.055),('propane',.018),('CO2',.015),('nitrogen',.008),('water',20e-6)]:f.addComponent(name,z)
        f.setMixingRule(10)
        if mode!='raw':f.init(0)
        op=j.thermodynamicoperations.ThermodynamicOperations(f)
        try:
            if mode=='multiphase':
                f.setMultiPhaseCheck(True)
                op.waterDewPointTemperatureMultiphaseFlash()
            else:op.waterDewPointTemperatureFlash()
            print(mode,P,f.getTemperature(),f.getNumberOfPhases(),flush=True)
            if mode=='multiphase':
                for shift in [-.2,.2]:
                    c=f.clone();c.setTemperature(f.getTemperature()+shift)
                    j.thermodynamicoperations.ThermodynamicOperations(c).TPflash();c.initProperties()
                    print('probe',shift,[(str(c.getPhase(a).getPhaseTypeName()),float(c.getPhase(a).getComponent('water').getx()),float(c.getBeta(a))) for a in range(c.getNumberOfPhases())],flush=True)
        except Exception as e:print(mode,P,str(e),flush=True)
