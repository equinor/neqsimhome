"""One-time transparent repair of literal cases diagnosed by solution checks."""
from pathlib import Path
import re, shutil, json, hashlib
B=Path(__file__).resolve().parents[2]
backup=B/'.build/backups/literal_solution_revision'
backup.mkdir(parents=True,exist_ok=True)
P=re.compile(r'^```python([^\n]*)\n(.*?)^```',re.M|re.S)
path=next((B/'chapters').glob('ch19_*/chapter.md'))
if not (backup/path.parent.name).exists():
    (backup/path.parent.name).mkdir()
    shutil.copy2(path,backup/path.parent.name/'chapter.md')
text=path.read_text(encoding='utf-8-sig'); blocks=list(P.finditer(text)); changes={}
for n in [1,2,8]:
    code=blocks[n-1].group(2)
    # Initialize overall composition before the standard reads component z.
    code=code.replace('gas.setMixingRule("classic")','gas.setMixingRule("classic")\n'+('    ' if n==2 else '')+'gas.init(0)  # Initialize mole fractions before ISO 6976 reads them.')
    changes[n]=code
changes[3]='''import jpype
import numpy as np
jneqsim = jpype.JPackage("neqsim")

# Exactly 20 mol-ppm water; methane balances the specified dry components.
# VLE water dew point: below 0 C this excludes stable ice and hydrate phases.
def export_water_dew_point(P_bara):
    gas = jneqsim.thermo.system.SystemSrkCPAstatoil(288.15, P_bara)
    for name, fraction in [("methane", .90398), ("ethane", .055),
                           ("propane", .018), ("CO2", .015),
                           ("nitrogen", .008), ("water", 20e-6)]:
        gas.addComponent(name, fraction)
    gas.setMixingRule(10)
    gas.setMultiPhaseCheck(True)
    gas.init(0)
    ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(gas)
    ops.waterDewPointTemperatureMultiphaseFlash()
    dew_K = float(gas.getTemperature())
    assert np.isfinite(dew_K) and 180.0 < dew_K < 320.0
    phase_checks = []
    for offset_K in [-0.2, 0.2]:
        check = gas.clone()
        check.setTemperature(dew_K + offset_K)
        jneqsim.thermodynamicoperations.ThermodynamicOperations(check).TPflash()
        check.initProperties()
        aqueous = check.hasPhaseType("aqueous")
        phase_checks.append(bool(aqueous))
    assert phase_checks == [True, False], (P_bara, dew_K, phase_checks)
    return {"pressure_bara": P_bara, "water_dew_C": dew_K-273.15,
            "aqueous_below_above": phase_checks}

water_dew_results = [export_water_dew_point(P) for P in
                     [20.0, 40.0, 60.0, 70.0, 80.0, 100.0, 120.0, 150.0]]
print("Water VLE dew point; ice/hydrate phases are outside this calculation")
for row in water_dew_results:
    print(f"{row['pressure_bara']:6.1f} bara: {row['water_dew_C']:7.2f} C")
'''
changes[4]=blocks[3].group(2).replace('Cricondentherm: {max_T_C','Sampled dew-curve maximum: {max_T_C')
code=blocks[5].group(2)
code=code.replace('for d_inch in diameters_inch:', 'diameter_results = []\nfor d_inch in diameters_inch:')
code=code.replace('area = 3.14159 * (d_m / 2) ** 2','area = math.pi * (d_m / 2) ** 2')
code=code.replace('import jpype','import math\nimport jpype',1)
needle='    print(f"{d_inch:>10d} {d_m:>10.4f} {dP:>10.1f} "\n          f"{v_gas:>10.1f} {P_out:>12.1f}")'
replacement='''    feasible = math.isfinite(P_out) and 0.0 < P_out <= 150.0
    diameter_results.append({"diameter_inch": d_inch, "outlet_bara": P_out,
                             "inlet_velocity_m_s": v_gas,
                             "physical_pressure_domain": feasible})
    if feasible:
        print(f"{d_inch:>10d} {d_m:>10.4f} {dP:>10.1f} "
              f"{v_gas:>10.1f} {P_out:>12.1f}")
    else:
        print(f"{d_inch:>10d}: infeasible pressure solution at specified rate")'''
assert needle in code;changes[6]=code.replace(needle,replacement)
for n,m in reversed(list(enumerate(blocks,1))):
    if n in changes:text=text[:m.start(2)]+changes[n].rstrip()+'\n'+text[m.end(2):]
text=text.replace('## 19.','## 19.')
path.write_text(text,encoding='utf-8')
print('Repaired chapter19 initialization, water VLE boundary validation, sampled envelope terminology and pipeline-domain reporting.')
