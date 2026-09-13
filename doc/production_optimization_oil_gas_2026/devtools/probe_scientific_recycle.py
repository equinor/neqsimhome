import sys,os,re,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'.build/python_packages'))
S=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim');sys.path.insert(0,str(S/'devtools'))
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=S,recompile=False,verbose=False)
p=next((B/'chapters').glob('ch31*/chapter.md'))
code=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',p.read_text(encoding='utf-8'),re.M|re.S))[2][3]
code=code.replace('assert mass_error<1e-7 and energy_error<1e-7,(mass_error,energy_error)','print("DIAGNOSTIC",h_in,h_out,cooler_loop.getDuty(),tear.getFluid().getEnthalpy(),mixer.getOutletStream().getFluid().getEnthalpy(),cooler_loop.getOutletStream().getFluid().getEnthalpy())')
code=code.replace("mass_out=sum", "for s in products+[feed,tear,mixer.getOutletStream(),cooler_loop.getOutletStream()]:s.getFluid().initProperties()\nmass_out=sum")
exec(code)
Path(B/'verification/scientific_revision/ch31_energy_probe.json').write_text(json.dumps({'hin':h_in,'hout':h_out,'Q':float(cooler_loop.getDuty()),'tearH':float(tear.getFluid().getEnthalpy()),'mixH':float(mixer.getOutletStream().getFluid().getEnthalpy()),'cooloutH':float(cooler_loop.getOutletStream().getFluid().getEnthalpy()),'flow':new_flow},indent=2))
os._exit(0)

