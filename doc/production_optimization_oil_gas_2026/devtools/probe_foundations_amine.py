from pathlib import Path
import sys, os, re, json, math
BOOK=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BOOK/'.build/python_packages'))
SRC=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim')
os.environ['JAVA_TOOL_OPTIONS']='-Xmx512m'
sys.path.insert(0,str(SRC/'devtools'))
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=SRC,recompile=False,verbose=False)
import jpype
text=next((BOOK/'chapters').glob('ch12*/chapter.md')).read_text(encoding='utf-8')
code=re.findall(r'^```python\s*\n(.*?)^```',text,re.M|re.S)[0]
code=code.replace('sour_gas.addComponent("water", 4.5)','sour_gas.addComponent("water", 0.005)  # pretreated gas, about 52 ppmv water')
code=code.replace('lean_amine.setMixingRule(10)', 'lean_amine.addComponent("CO2", 0.0)\nlean_amine.addComponent("H2S", 0.0)\nlean_amine.setMixingRule(10)')
code=code.replace('setFlowRate(5000.0, "kg/hr")','setFlowRate(300000.0, "kg/hr")')
code=code.replace('absorber.setNumberOfStages(15)','absorber.setNumberOfStages(15)  # metadata; removal remains prescribed\nabsorber.setH2SRemovalEfficiency(0.99)')
code+= '''
# This prescribed-removal model is isothermal; calculate its required heat exchange.
rich_amine = absorber.getRichAmineOutStream()
def amine_state(stream):
    fluid = stream.getFluid()
    fluid.initProperties()
    return {"mass": stream.getFlowRate("kg/sec"),
            "H": stream.getFlowRate("kg/sec") * fluid.getEnthalpy("J/kg"),
            "moles": {str(fluid.getComponent(i).getComponentName()):
                      fluid.getComponent(i).getNumberOfmoles()
                      for i in range(fluid.getNumberOfComponents())}}
in_states = [amine_state(gas_feed), amine_state(amine_feed)]
out_states = [amine_state(sweet_gas), amine_state(rich_amine)]
mass_in = sum(s["mass"] for s in in_states)
mass_out = sum(s["mass"] for s in out_states)
assert abs(mass_in - mass_out) / mass_in < 1e-6
components = set(k for s in in_states + out_states for k in s["moles"])
total_moles = sum(sum(s["moles"].values()) for s in in_states)
for name in components:
    ni = sum(s["moles"].get(name, 0.0) for s in in_states)
    no = sum(s["moles"].get(name, 0.0) for s in out_states)
    assert abs(ni - no) / total_moles < 1e-6, name
acid_pickup = sum(in_states[0]["moles"].get(k, 0.0) -
                  out_states[0]["moles"].get(k, 0.0) for k in ["CO2", "H2S"])
amine_moles = in_states[1]["moles"]["MDEA"]
net_loading = acid_pickup / amine_moles
assumed_net_loading_limit = 0.50  # explicit screening assumption, needs solvent data
assert 0.0 < net_loading <= assumed_net_loading_limit
original_5_tph_loading = net_loading * 300000.0 / 5000.0
assert original_5_tph_loading > assumed_net_loading_limit
isothermal_heat_W = sum(s["H"] for s in out_states) - sum(s["H"] for s in in_states)
assert math.isfinite(isothermal_heat_W)
print(f"Net acid pickup: {net_loading:.3f} mol/mol MDEA")
print(f"Rejected 5 t/hr solvent case: {original_5_tph_loading:.2f} mol/mol MDEA")
print(f"Required isothermal heat input: {isothermal_heat_W / 1000:.1f} kW")
'''
scope={'math':math}
exec(code,scope)
out=BOOK/'verification/scientific_revision/amine_probe.json'
out.write_text(json.dumps({'status':'pass','code':code,'net_loading':scope['net_loading'],'rejected_loading_5_tph':scope['original_5_tph_loading'],'heat_input_W':scope['isothermal_heat_W'],'mass_relative_error':abs(scope['mass_in']-scope['mass_out'])/scope['mass_in'],'scope':'prescribed-removal isothermal material allocation and solvent-loading screen; not reactive absorption or stage prediction'},indent=2),encoding='utf-8')
