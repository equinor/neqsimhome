"""Replace the erroneous reverse wellbore example and false Pareto claim."""
from pathlib import Path
import re,shutil
B=Path(__file__).resolve().parents[2];P=re.compile(r'^```python([^\n]*)\n(.*?)^```',re.M|re.S)
path=next((B/'chapters').glob('ch22_*/chapter.md'));backup=B/'.build/backups/literal_solution_revision'/path.parent.name
backup.mkdir(parents=True,exist_ok=True)
if not (backup/'chapter.md').exists():shutil.copy2(path,backup/'chapter.md')
text=path.read_text(encoding='utf-8');blocks=list(P.finditer(text));changes={}
changes[1]='''import jpype
import numpy as np
jneqsim = jpype.JPackage("neqsim")

# Gas backpressure IPR and forward upward tubing calculation.
P_res, C_ipr, n_ipr = 250.0, 0.0035, 0.85
P_wh_target = 80.0
def well_outlet(P_bh, Q_MSm3_day):
    gas=jneqsim.thermo.system.SystemSrkEos(363.15,P_bh)
    for name,z in [("methane",.88),("ethane",.06),("propane",.03),
                   ("CO2",.02),("nitrogen",.01)]:gas.addComponent(name,z)
    gas.setMixingRule("classic")
    stream=jneqsim.process.equipment.stream.Stream("Bottomhole inlet",gas)
    stream.setFlowRate(Q_MSm3_day,"MSm3/day")
    wellbore=jneqsim.process.equipment.pipeline.PipeBeggsAndBrills("Upward tubing",stream)
    wellbore.setPipeWallRoughness(2.5e-5)
    wellbore.setLength(3000.0)  # metres, 3000 m vertical rise
    wellbore.setDiameter(.1016)
    wellbore.setAngle(90.0)    # positive outlet-minus-inlet elevation
    wellbore.setNumberOfIncrements(30)
    ps=jneqsim.process.processmodel.ProcessSystem()
    ps.add(stream);ps.add(wellbore);ps.run()
    arrival=float(wellbore.getOutletStream().getPressure("bara"))
    return arrival

# Bisection rejects nonpositive/undefined trial outlet pressures instead of
# reporting them as physical well states. Only accepted final states are used.
def required_bottomhole(Q):
    lo,hi=P_wh_target,P_res
    upper=well_outlet(hi,Q)
    if not np.isfinite(upper) or upper<P_wh_target:return None
    for _ in range(28):
        mid=.5*(lo+hi);arrival=well_outlet(mid,Q)
        if np.isfinite(arrival) and arrival>=P_wh_target:hi=mid
        else:lo=mid
    arrival=well_outlet(hi,Q)
    assert abs(arrival-P_wh_target)<.002
    return hi

Q_tpr=[.5,1.0,1.5,2.0,2.5,3.0,3.5]
P_wf_tpr=[required_bottomhole(q) for q in Q_tpr]
print("Required BHP for 80 bara wellhead; None means unavailable below reservoir pressure")
print(list(zip(Q_tpr,P_wf_tpr)))

def ipr_bottomhole(Q):
    square=P_res**2-(Q/C_ipr)**(1/n_ipr)
    assert square>0
    return float(np.sqrt(square))
lo,hi=.05,5.0
assert well_outlet(ipr_bottomhole(lo),lo)>P_wh_target
hi_arrival=well_outlet(ipr_bottomhole(hi),hi)
assert not np.isfinite(hi_arrival) or hi_arrival<P_wh_target
for _ in range(30):
    mid=.5*(lo+hi);arrival=well_outlet(ipr_bottomhole(mid),mid)
    if np.isfinite(arrival) and arrival>=P_wh_target:lo=mid
    else:hi=mid
operating_rate_MSm3_day=lo
operating_BHP_bara=ipr_bottomhole(lo)
operating_WHP_bara=well_outlet(operating_BHP_bara,lo)
assert abs(operating_WHP_bara-P_wh_target)<.002
assert abs(C_ipr*(P_res**2-operating_BHP_bara**2)**n_ipr-lo)<1e-8
print(f"Coupled solution: {lo:.5f} MSm3/day; BHP {operating_BHP_bara:.3f} bara; WHP {operating_WHP_bara:.3f} bara")
print("Specified IPR plus a steady forward pipe model; no calibrated thermal wellbore or field deliverability claim.")
'''
code=blocks[6].group(2)
code=code.replace('print("\\nLower separator pressure → more oil recovery but more compressor power.")\nprint("The Pareto front represents the trade-off frontier.")','''assert len(pareto_points) == len(P_sep_range), "A failed case cannot silently enter a complete frontier"
pareto_front = [point for point in pareto_points if not any(
    other["oil_rate"] >= point["oil_rate"] and other["power"] <= point["power"]
    and (other["oil_rate"] > point["oil_rate"] or other["power"] < point["power"])
    for other in pareto_points)]
print("Nondominated sampled points:", pareto_front)
print("Oil is liquid mass at separator conditions; compare actual trends, not an assumed pressure/recovery direction.")''')
changes[7]=code
for n,m in reversed(list(enumerate(blocks,1))):
    if n in changes:text=text[:m.start(2)]+changes[n].rstrip()+'\n'+text[m.end(2):]
path.write_text(text,encoding='utf-8');print('Repaired 3000 m upward nodal solve and explicit Pareto enumeration.')
