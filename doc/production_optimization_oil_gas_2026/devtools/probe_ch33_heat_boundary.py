"""Bounded NGL stabilizer probe on Chapter 33's actual upstream liquid."""
import os
import sys
from pathlib import Path
import re
import json
import time
import argparse
import hashlib

BOOK = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim")
os.environ["JAVA_TOOL_OPTIONS"] = "-Xmx512m"
os.environ["NEQSIM_PROJECT_ROOT"] = str(SRC)
sys.path.insert(0, str(BOOK / ".build" / "python_packages"))
sys.path.insert(0, str(SRC / "devtools"))
from neqsim_dev_setup import neqsim_init
neqsim_init(project_root=SRC, recompile=False, verbose=False)
import jpype

parser = argparse.ArgumentParser()
parser.add_argument("--feed-c", type=float, default=50.0)
parser.add_argument("--reboiler-c", type=float, default=105.0)
parser.add_argument("--top-bar", type=float, default=8.0)
parser.add_argument("--stages", type=int, default=5)
args = parser.parse_args()

chapter = BOOK / "chapters" / "ch33_onshore_processing_plants" / "chapter.md"
source = chapter.read_text(encoding="utf-8")
block = next(m[1] for m in re.finditer(r"^```python\s*\n(.*?)^```", source, re.M | re.S)
             if "def build_inlet_receiving" in m[1])
upstream = block.split("def build_fractionation", 1)[0]
namespace = {}
exec(upstream, namespace)
inlet_sys, inlet_sep = namespace["build_inlet_receiving"]()
inlet_sys.run()
dehy_sys, absorber = namespace["build_dehydration"](inlet_sep.getGasOutStream())
dehy_sys.run()
ngl_sys, cold_sep, residue_comp = namespace["build_ngl_recovery"](absorber.getGasOutStream())
ngl_sys.run()

jneqsim = jpype.JPackage("neqsim")
Stream = jneqsim.process.equipment.stream.Stream
Valve = jneqsim.process.equipment.valve.ThrottlingValve
Heater = jneqsim.process.equipment.heatexchanger.Heater
DistillationColumn = jneqsim.process.equipment.distillation.DistillationColumn

def state(stream):
    fluid = stream.getFluid()
    return {"flow_kg_hr": stream.getFlowRate("kg/hr"), "temperature_C": stream.getTemperature("C"),
            "pressure_bara": stream.getPressure("bara"), "enthalpy_W": fluid.getEnthalpy(),
            "phase_mole_fractions": {str(fluid.getPhase(i).getType()): fluid.getPhase(i).getBeta()
                                     for i in range(fluid.getNumberOfPhases())},
            "composition": {str(fluid.getComponent(i).getComponentName()): fluid.getComponent(i).getz()
                            for i in range(fluid.getNumberOfComponents())}}

cold_liquid = cold_sep.getLiquidOutStream()
report = {"python": sys.executable, "heap_limit_MB": 512,
          "java_max_memory_MB": jpype.JClass("java.lang.Runtime").getRuntime().maxMemory() / 1024**2,
          "chapter_sha256": hashlib.sha256(source.encode()).hexdigest(),
          "upstream_code_sha256": hashlib.sha256(upstream.encode()).hexdigest(),
          "settings": vars(args), "cold_separator_liquid": state(cold_liquid)}
suffix = f"{args.stages}stage_{args.top_bar:g}bar_{args.feed_c:g}C_{args.reboiler_c:g}C"
output = BOOK / "verification" / ("ch33_heat_boundary_probe_" + suffix + ".json")
output.write_text(json.dumps(report, indent=2), encoding="utf-8")
print("COLD_FEED", report["cold_separator_liquid"], flush=True)

feed = Stream("NGL Stabilizer Feed", cold_liquid.getFluid().clone())
feed.run()
valve = Valve("Stabilizer Feed Letdown", feed)
valve.setOutletPressure(args.top_bar + 0.5, "bara")
valve.run()
heater = Heater("Stabilizer Feed Heater", valve.getOutletStream())
heater.setOutTemperature(args.feed_c, "C")
heater.run()
report["column_feed"] = state(heater.getOutletStream())
report["feed_heater_duty_kW"] = heater.getDuty() / 1000.0
print("CONDITIONED_FEED", report["column_feed"], flush=True)
column = DistillationColumn("NGL Stabilizer", args.stages, True, False)
column.addFeedStream(heater.getOutletStream(), args.stages)
column.setTopPressure(args.top_bar)
column.setBottomPressure(args.top_bar + 0.5)
column.getReboiler().setHeatInput(4.5e6)
column.setSolverType(DistillationColumn.SolverType.DIRECT_SUBSTITUTION)
column.setMaxNumberOfIterations(80, True)
column.setTemperatureTolerance(1e-7)
column.setMassBalanceTolerance(1e-6)
column.setMeshResidualTolerance(1e-5)
column.setEnforceMeshResidualTolerance(True)
column.setEnthalpyBalanceTolerance(1e-4)
column.setEnforceEnergyBalanceTolerance(True)
start = time.monotonic()
column.run()
report.update(seconds=time.monotonic() - start, solved=bool(column.solved()),
              solve_status=str(column.getLastSolveStatus()), diagnostics=str(column.getConvergenceDiagnostics()),
              overhead=state(column.getGasOutStream()),
              bottoms=state(column.getReboiler().getLiquidOutStream()),
              reboiler_duty_kW=column.getReboiler().getDuty() / 1000.0)
report["mass_closure_relative"] = abs(report["column_feed"]["flow_kg_hr"] -
    report["overhead"]["flow_kg_hr"] - report["bottoms"]["flow_kg_hr"]) / report["column_feed"]["flow_kg_hr"]
report["energy_closure_relative"] = abs(report["column_feed"]["enthalpy_W"] + report["reboiler_duty_kW"] * 1000.0 -
    report["overhead"]["enthalpy_W"] - report["bottoms"]["enthalpy_W"]) / max(abs(report["reboiler_duty_kW"] * 1000.0), 1.0)
output.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2), flush=True)
assert report["solved"], "Column failed rigorous convergence gates"
assert report["solve_status"] == "RIGOROUS_CONVERGED", "Products were reconciled or fallback values"
assert report["mass_closure_relative"] < 0.001
assert report["energy_closure_relative"] < 0.001

