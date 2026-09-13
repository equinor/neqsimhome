from pathlib import Path
import sys,os,re,json,traceback
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'.build/python_packages'))
S=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim');sys.path.insert(0,str(S/'devtools'));os.environ['JAVA_TOOL_OPTIONS']='-Xmx512m'
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=S,recompile=False,verbose=False)
import jpype,matplotlib;matplotlib.use('Agg')
codes=re.findall(r'^```python\s*\n(.*?)^```',next((B/'chapters').glob('ch18*/chapter.md')).read_text(encoding='utf-8'),re.M|re.S)
ns={'jneqsim':jpype.JPackage('neqsim')}
exec(codes[0],ns)
try:exec(codes[2].replace('steam.run()','steam.run()\nsteam.getFluid().initProperties()').replace('setOutletPressure(0.08, "bara")','setOutletPressure(10.0, "bara")'),ns)
except:traceback.print_exc()
vals={k:float(ns[k]) for k in ['steam_enthalpy_rise','steam_work','recovered_heat'] if k in ns}
unit=ns['steam_turbine'];steam=ns['steam'];hrsg=ns['hrsg']
vals['power_W']=float(unit.getPower());vals['duty_W']=float(hrsg.getHeatTransferred('W'))
vals['mass_in']=float(steam.getFlowRate('kg/sec'));vals['mass_out']=float(unit.getOutletStream().getFlowRate('kg/sec'))
vals['Hin_W']=float(steam.getFluid().getEnthalpy());vals['Hout_W']=float(unit.getOutletStream().getFluid().getEnthalpy());vals['Tsteam']=float(steam.getTemperature('K'))
print(vals)
(B/'verification/scientific_revision/hrsg_probe.json').write_text(json.dumps(vals,indent=2))
