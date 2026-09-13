"""Independent conservation/domain checks for the declared simple equipment models."""
import math

def check(name,observed,expected=True,tolerance=None,scope=None):
    ok=(abs(float(observed)-float(expected))<=tolerance) if tolerance is not None else bool(observed==expected)
    row={'name':name,'passed':bool(ok),'observed':observed,'expected':expected}
    if tolerance is not None:row['tolerance']=tolerance
    if scope:row['scope']=scope
    assert ok,row
    return row

def stream_state(stream):
    fluid=stream.getFluid();mass=float(stream.getFlowRate('kg/sec'))
    assert math.isfinite(mass) and mass>=-1e-10
    if mass>1e-12:fluid.initProperties()
    pressure=float(stream.getPressure('bara'));temperature=float(stream.getTemperature('K'))
    assert math.isfinite(pressure) and pressure>0 and math.isfinite(temperature) and temperature>0
    enthalpy=float(fluid.getEnthalpy()) if mass>1e-12 else 0.
    assert math.isfinite(enthalpy)
    components={str(fluid.getComponent(i).getComponentName()):float(fluid.getComponent(i).getNumberOfmoles())
                for i in range(fluid.getNumberOfComponents())}
    return {'mass':mass,'enthalpy':enthalpy,'components':components,'pressure':pressure,'temperature':temperature}

def boundary(name,inlets,outlets,energy_W=0.,energy_tol=1e-5,include_energy=True):
    a=[stream_state(s) for s in inlets];b=[stream_state(s) for s in outlets]
    mi=sum(s['mass'] for s in a);mo=sum(s['mass'] for s in b)
    if mi<1e-10:return [check(name+' zero-flow boundary',abs(mo)<1e-10)]
    mass_error=abs(mo-mi)/mi
    names=set(k for s in a+b for k in s['components'])
    mol_scale=max(sum(sum(s['components'].values()) for s in a),1e-12)
    comp_error=max(abs(sum(s['components'].get(k,0.) for s in b)-sum(s['components'].get(k,0.) for s in a))/mol_scale for k in names)
    # Native equipment caching is1e-6 in these interface demonstrations.
    # Stricter central cases use fresh factories and their own tighter gates.
    rows=[check(name+' mass relative',mass_error,0.,1e-6),
          check(name+' component relative',comp_error,0.,1e-6),
          check(name+' finite positive p/T and nonnegative flows',True)]
    if include_energy:
        hi=sum(s['enthalpy'] for s in a);ho=sum(s['enthalpy'] for s in b)
        energy_error=abs(ho-hi-energy_W)/max(abs(hi),abs(ho),abs(energy_W),1.)
        rows.append(check(name+' energy relative',energy_error,0.,energy_tol))
    return rows

def unit_checks(unit):
    kind=str(unit.getClass().getSimpleName());name=str(unit.getName())
    if kind=='Stream':return []
    inlets=list(unit.getInletStreams());outlets=list(unit.getOutletStreams())
    if not inlets or not outlets:return []
    power=0.
    if kind in ['Compressor','Expander','Pump']:power=float(unit.getPower())
    elif kind in ['Cooler','Heater','HeatExchanger']:power=float(unit.getDuty())
    rows=boundary(name,inlets,outlets,power,include_energy=kind not in ['PipeBeggsAndBrills','AdiabaticPipe'])
    if kind=='Compressor':
        rows.append(check(name+' single-phase compressor inlet',inlets[0].getFluid().getNumberOfPhases()==1))
        rows.append(check(name+' compression pressure ratio',outlets[0].getPressure('bara')>inlets[0].getPressure('bara')))
        rows.append(check(name+' positive shaft work',power>0))
    if kind=='PipeBeggsAndBrills':
        rows.append(check(name+' horizontal passive pressure decline',
                          0<outlets[0].getPressure('bara')<=inlets[0].getPressure('bara')))
    return rows

def process_checks(process):
    rows=[]
    for unit in process.getUnitOperations():rows.extend(unit_checks(unit))
    assert rows,'No physical equipment boundary found'
    return rows

def utilization_checks(process):
    rows=[];values=[]
    for unit in process.getConstrainedEquipment():
        value=float(unit.getMaxUtilization());values.append(value)
        rows.append(check(str(unit.getName())+' utilization finite/nonnegative',math.isfinite(value) and value>=0))
    if values:
        rows.append(check('bottleneck maximum aggregation',float(process.getBottleneckUtilization()),max(values),1e-9))
    return rows
