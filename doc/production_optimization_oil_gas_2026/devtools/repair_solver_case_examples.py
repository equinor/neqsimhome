"""Reuse executed solver artifacts and fix case-study topology/API errors."""
import json
from pathlib import Path
import re
BOOK=Path(__file__).resolve().parents[1]
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
def edit(n, fn):
    p=next((BOOK/'chapters').glob(f'ch{n:02d}_*/chapter.md'))
    text=p.read_text(encoding='utf-8-sig')
    for i,m in reversed(list(enumerate(PAT.finditer(text),1))):
        ans=fn(i,m[1],m[3])
        if ans is None: continue
        note,code=ans if isinstance(ans,tuple) else (m[2],ans)
        text=text[:m.start()]+f'```{m[1]}{note}\n{code.rstrip()}\n```'+text[m.end():]
    p.write_text(text,encoding='utf-8')

notebook=json.loads(next((BOOK/'chapters').glob('ch31*/notebooks/ch29_solver_methods.ipynb')).read_text(encoding='utf-8'))
imports='''import jpype
import numpy as np
jneqsim = jpype.JPackage("neqsim")
SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
Stream = jneqsim.process.equipment.stream.Stream
Mixer = jneqsim.process.equipment.mixer.Mixer
Cooler = jneqsim.process.equipment.heatexchanger.Cooler
Separator = jneqsim.process.equipment.separator.Separator
Splitter = jneqsim.process.equipment.splitter.Splitter
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
ThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve
'''
def ch31(i,language,code):
    if i==3: return imports+''.join(notebook['cells'][9]['source'])
    if i==4:
        return '''# Inspect the actual, normalized tear residuals recorded above.
for name, values in [("flow", flow_errors), ("temperature", temp_errors),
                     ("composition", comp_errors)]:
    print(name, "iterations:", len(values), "final normalized residual:", values[-1])
assert max(flow_errors[-1], temp_errors[-1], comp_errors[-1]) < 1e-7'''
    if i==5:
        return imports+''.join(notebook['cells'][13]['source']).replace(
            'ns.Adjuster(', 'jneqsim.process.equipment.util.Adjuster(').replace('= 20 C','= 40 C')
    if i==6:
        return (' pattern: requires a fully specified column feed pressures and operating specifications',code)
    if i==7:
        return (' pattern: requires initialized dynamic equipment inventories and controller setup',code.replace('process.setDynamic(True)','sep.setCalculateSteadyState(False)'))

def ch33(i,language,code):
    code=code.replace('deethanizer.setCondenser("TOTAL_CONDENSER")','deethanizer.getCondenser().setTotalCondenser(True)\n    deethanizer.getCondenser().setRefluxRatio(2.0)' if i==5 else 'deethanizer.getCondenser().setTotalCondenser(True)\ndeethanizer.getCondenser().setRefluxRatio(2.0)')
    code=code.replace('deethanizer.getCondenser().getOutletStream()','deethanizer.getCondenser().getProductOutStream()')
    code=code.replace("jneqsim.process.equipment.expander.Expander.cast(ngl_sys.getUnit('Turboexpander'))","ngl_sys.getUnit('Turboexpander')")
    code=code.replace('recomp.getPower() + residue_comp.getPower()', 'ngl_sys.getUnit("Shaft Recompressor").getPower() + residue_comp.getPower()')
    code=code.replace('NGL Recovery::Gas-Gas HX.outTemperature','NGL Recovery::Gas-Gas HX.outletTemperature')
    return code

def ch34(i,language,code):
    code=code.replace('    system.add(lp_gas_stream)','    # Cross-area source streams are already solved by their owning area.').replace(
        '    system.add(hp_gas_stream)','    # HP gas belongs to the separation area.')
    code=code.replace('    comp_system.add(sep2.getGasOutStream())','    # Gas streams are owned by the separation area.').replace(
        '    comp_system.add(sep3.getGasOutStream())','').replace('    comp_system.add(sep1.getGasOutStream())','')
    if i==6: return (' pattern: requires calibrated well_models and reservoir/network boundary data',code)
    return code

edit(31,ch31)
edit(33,ch33)
edit(34,ch34)

# Explain fixture-dependent fragments visibly, not only in a machine-readable fence tag.
for chapter in (BOOK/'chapters').glob('ch*'):
    if not 19<=int(chapter.name[2:4])<=35: continue
    p=chapter/'chapter.md'; text=p.read_text(encoding='utf-8-sig')
    text=re.sub(r'(?m)^```python pattern: ([^\n]+)',
        lambda m: '**Execution scope:** This integration pattern '+m[1]+'. It is not a standalone validated process calculation.\n\n'+m[0],text)
    p.write_text(text,encoding='utf-8')
