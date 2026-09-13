"""Bounded current-source physical checks for the scientific revision."""
import os
import sys
import json
from pathlib import Path
BOOK = Path(__file__).resolve().parents[1]
SOURCE = Path(r"C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim")
sys.path[:0] = [str(BOOK / ".build/python_packages"), str(SOURCE / "devtools")]
os.environ["MPLBACKEND"] = "Agg"
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=SOURCE, recompile=False, verbose=False)
import jpype
import numpy as np
jneqsim = jpype.JPackage("neqsim")
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
Compressor = jneqsim.process.equipment.compressor.Compressor
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
OUT = BOOK / "verification/scientific_revision"
OUT.mkdir(parents=True, exist_ok=True)


def dynamic_case(dt, slug=False):
    fluid = jneqsim.thermo.system.SystemSrkEos(313.15, 30.0)
    fluid.addComponent("methane", 0.5)
    fluid.addComponent("n-heptane", 0.5)
    fluid.setMixingRule("classic")
    inlet = Stream("Dynamic feed", fluid)
    inlet.setFlowRate(2.0, "kg/sec")
    inlet.run()
    vessel = Separator("Inventory vessel", inlet)
    vessel.setInternalDiameter(1.0)
    vessel.setSeparatorLength(3.0)
    vessel.setLiquidLevel(0.5)
    vessel.run()
    vessel.setCalculateSteadyState(False)
    vessel.initializeTransientCalculation()
    gasout = vessel.getGasOutStream()
    liquidout = vessel.getLiquidOutStream()
    basegas = float(gasout.getFlowRate("kg/sec"))
    baseliquid = float(liquidout.getFlowRate("kg/sec"))
    LT = jneqsim.process.measurementdevice.LevelTransmitter("LT", vessel)
    controller = jneqsim.process.controllerdevice.ControllerDeviceBaseClass()
    controller.setTransmitter(LT)
    setpoint = float(vessel.getLiquidLevel())
    controller.setControllerSetPoint(setpoint)
    controller.setReverseActing(False)
    controller.setControllerParameters(0.10, 30.0, 0.0)
    controller.setOutputLimits(0.0, 6.0)
    command = baseliquid
    identity = jpype.java.util.UUID.randomUUID()
    inventory = vessel.getThermoSystem()
    mass0 = float(inventory.getTotalNumberOfMoles()*inventory.getMolarMass())
    energy0 = float(inventory.getInternalEnergy())
    balance_mass = balance_energy = 0.0
    max_mass = max_energy = 0.0
    series = []
    for step in range(round(120.0/dt)):
        t = step*dt
        identity = jpype.java.util.UUID.randomUUID()
        pulse = 3.0 if slug else 2.4
        inlet.setFlowRate(pulse if 20.0 <= t < 40.0 else 2.0, "kg/sec")
        inlet.run()
        controller.runTransient(command, dt, identity)
        command = min(6.0, max(0.0, float(controller.getResponse())))
        gasout.setFlowRate(basegas, "kg/sec")
        liquidout.setFlowRate(command, "kg/sec")
        gasout.run()
        liquidout.run()
        net_mass = float(inlet.getFlowRate("kg/sec")-gasout.getFlowRate("kg/sec")-liquidout.getFlowRate("kg/sec"))
        net_energy = float(inlet.getFluid().getEnthalpy()-gasout.getFluid().getEnthalpy()-liquidout.getFluid().getEnthalpy())
        balance_mass += dt*net_mass
        balance_energy += dt*net_energy
        vessel.runTransient(dt, identity)
        inventory = vessel.getThermoSystem()
        mass = float(inventory.getTotalNumberOfMoles()*inventory.getMolarMass())
        energy = float(inventory.getInternalEnergy())
        mass_error = abs(mass-mass0-balance_mass)/mass0
        energy_error = abs(energy-energy0-balance_energy)/max(abs(energy0),1.0)
        max_mass = max(max_mass, mass_error)
        max_energy = max(max_energy, energy_error)
        row = [t+dt, float(vessel.getLiquidLevel()), float(inventory.getPressure("bara")), float(inventory.getTemperature("C")), mass, command]
        assert all(np.isfinite(row)) and 0.0 < row[1] < 1.0
        series.append(row)
    assert max_mass < 1e-10 and max_energy < 1e-5
    globals()["sep"] = vessel  # inspected by the later instrumentation examples
    return dict(dt=dt, mass0_kg=mass0, energy0_J=energy0,
                setpoint_fraction=setpoint, base_liquid_kg_s=baseliquid,
                max_mass_relative_residual=max_mass, max_energy_relative_residual=max_energy,
                series=series)


def optimize_case():
    from scipy.optimize import minimize
    def build():
        fluid = jneqsim.thermo.system.SystemSrkEos(313.15, 50.0)
        fluid.addComponent("methane",0.9)
        fluid.addComponent("ethane",0.1)
        fluid.setMixingRule("classic")
        feed = Stream("Feed",fluid)
        comp = Compressor("Compressor",feed)
        comp.setOutletPressure(150.0,"bara")
        comp.setPolytropicEfficiency(0.78)
        comp.setUsePolytropicCalc(True)
        process = ProcessSystem()
        process.add(feed)
        process.add(comp)
        return feed,comp,process
    feed,comp,process=build()
    def evaluate(x, objects=None):
        f,c,p=objects or (feed,comp,process)
        f.setFlowRate(float(x[0])*100000.0,"kg/hr")
        f.setPressure(float(x[1])*50.0,"bara")
        p.run()
        power=float(c.getPower("kW"))
        mass_error=abs(float(c.getOutletStream().getFlowRate("kg/hr")-f.getFlowRate("kg/hr")))/float(f.getFlowRate("kg/hr"))
        duty=float(c.getOutletStream().getFluid().getEnthalpy()-f.getFluid().getEnthalpy())/1000.0
        assert np.isfinite(power) and mass_error < 1e-10
        assert abs(duty-power) < 1e-5*max(power,1.0)
        return power
    cap=3500.0
    result=minimize(lambda x:-float(x[0]), [0.6,1.0],method="SLSQP",
                    bounds=[(0.5,2.0),(0.8,1.6)],
                    constraints={"type":"ineq","fun":lambda x:(cap-evaluate(x))/cap},
                    options={"ftol":1e-10,"eps":1e-5,"maxiter":100})
    replay=evaluate(result.x,build())
    grid=[]
    for suction in np.linspace(0.8,1.6,21):
        for rate in np.linspace(0.5,2.0,101):
            power=evaluate([rate,suction])
            if power <= cap+1e-7:
                grid.append((rate,suction,power))
    best=max(grid,key=lambda row:row[0])
    return dict(success=bool(result.success),message=str(result.message),iterations=int(result.nit),
                x=result.x.tolist(),replayed_power_kW=replay,grid_best=best,
                grid_flow_spacing_kg_hr=1500.0,grid_evaluations=2121)


def blowdown_case(dt):
    fluid=jneqsim.thermo.system.SystemSrkEos(313.15,80.0)
    fluid.addComponent("methane",0.95)
    fluid.addComponent("ethane",0.05)
    fluid.setMixingRule("classic")
    inlet=Stream("Isolated inlet",fluid)
    inlet.setFlowRate(1000.0,"kg/hr")
    inlet.run()
    vessel=Separator("Blowdown vessel",inlet)
    vessel.setInternalDiameter(1.0)
    vessel.setSeparatorLength(3.0)
    vessel.setLiquidLevel(0.0)
    vessel.run()
    gasout=vessel.getGasOutStream()
    liquidout=vessel.getLiquidOutStream()
    valve=jneqsim.process.equipment.valve.ThrottlingValve("BDV",gasout)
    valve.setOutletPressure(1.01325,"bara")
    valve.setCv(1.0)
    valve.run()
    vessel.setCalculateSteadyState(False)
    vessel.initializeTransientCalculation()
    valve.setCalculateSteadyState(False)
    inlet.setFlowRate(1.0e-6,"kg/sec")
    inlet.run()
    inventory=vessel.getThermoSystem()
    mass0=float(inventory.getTotalNumberOfMoles()*inventory.getMolarMass())
    energy0=float(inventory.getInternalEnergy())
    mass_out=energy_out=0.0
    max_mass=max_energy=0.0
    series=[]
    for step in range(round(120.0/dt)):
        identity=jpype.java.util.UUID.randomUUID()
        valve.runTransient(dt,identity)
        liquidout.setFlowRate(0.0,"kg/sec")
        gasout.run()
        flow=float(gasout.getFlowRate("kg/sec"))
        mass_out+=dt*(flow-float(inlet.getFlowRate("kg/sec")))
        energy_out+=dt*float(gasout.getFluid().getEnthalpy()-inlet.getFluid().getEnthalpy())
        vessel.runTransient(dt,identity)
        inventory=vessel.getThermoSystem()
        mass=float(inventory.getTotalNumberOfMoles()*inventory.getMolarMass())
        energy=float(inventory.getInternalEnergy())
        max_mass=max(max_mass,abs(mass-mass0+mass_out)/mass0)
        max_energy=max(max_energy,abs(energy-energy0+energy_out)/abs(energy0))
        series.append([(step+1)*dt,float(inventory.getPressure("bara")),float(inventory.getTemperature("C")),mass,flow])
    return dict(dt=dt,mass0_kg=mass0,max_mass_relative_residual=max_mass,
                max_energy_relative_residual=max_energy,series=series)


if __name__ == "__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else "dynamic"
    if mode=="dynamic":
        answer={str(dt):dynamic_case(dt) for dt in (0.5,0.25)}
        (OUT/"ch29_dynamic_probe.json").write_text(json.dumps(answer,indent=2),encoding="utf-8")
        for dt, row in answer.items():
            print(dt,{k:v for k,v in row.items() if k!="series"},"end",row["series"][-1],flush=True)
    elif mode=="blowdown":
        answer={str(dt):blowdown_case(dt) for dt in (0.5,0.25)}
        (OUT/"ch29_blowdown_probe.json").write_text(json.dumps(answer,indent=2),encoding="utf-8")
        for dt,row in answer.items():
            print(dt,{k:v for k,v in row.items() if k!="series"},"end",row["series"][-1],flush=True)
    else:
        answer=optimize_case()
        (OUT/"ch32_optimum_probe.json").write_text(json.dumps(answer,indent=2),encoding="utf-8")
        print(json.dumps(answer,indent=2),flush=True)
    sys.stdout.flush()
    os._exit(0)
