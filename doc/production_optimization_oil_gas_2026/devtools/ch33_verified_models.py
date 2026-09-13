"""Source for the physically checked Chapter 33 examples; inserted literally into the book."""
import jpype
import math
import json

jneqsim = jpype.JPackage("neqsim")
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
Cooler = jneqsim.process.equipment.heatexchanger.Cooler
Heater = jneqsim.process.equipment.heatexchanger.Heater
Expander = jneqsim.process.equipment.expander.Expander
Compressor = jneqsim.process.equipment.compressor.Compressor
Valve = jneqsim.process.equipment.valve.ThrottlingValve
Mixer = jneqsim.process.equipment.mixer.Mixer
DistillationColumn = jneqsim.process.equipment.distillation.DistillationColumn
ProcessSystem = jneqsim.process.processmodel.ProcessSystem
ProcessModel = jneqsim.process.processmodel.ProcessModel
ThermodynamicOperations = jneqsim.thermodynamicoperations.ThermodynamicOperations

engineering_checks = []

def check_balance(name, inlets, outlets, energy_input_W=0.0, tolerance=1e-5):
    """Steady state, no reaction, negligible kinetic/potential energy change.

    Positive energy_input_W means heat or shaft work enters the control volume.
    NeqSim stream getEnthalpy() is a flow enthalpy in W for these process streams.
    """
    mass_in = sum(s.getFlowRate("kg/sec") for s in inlets)
    mass_out = sum(s.getFlowRate("kg/sec") for s in outlets)
    assert mass_in > 0.0
    mass_error = abs(mass_in - mass_out) / mass_in
    def amounts(streams):
        totals = {}
        for stream in streams:
            fluid = stream.getFluid()
            for i in range(fluid.getNumberOfComponents()):
                comp = fluid.getComponent(i)
                key = str(comp.getComponentName())
                totals[key] = totals.get(key, 0.0) + comp.getNumberOfmoles()
        return totals
    ni, no = amounts(inlets), amounts(outlets)
    scale = sum(ni.values())
    component_error = max(abs(ni.get(k, 0.0)-no.get(k, 0.0)) /
        max(abs(ni.get(k, 0.0)), 1e-8*scale) for k in set(ni) | set(no))
    hi = sum(s.getFluid().getEnthalpy() for s in inlets)
    ho = sum(s.getFluid().getEnthalpy() for s in outlets)
    energy_error = abs(hi + energy_input_W - ho) / max(abs(hi), abs(ho),
        abs(energy_input_W), 1.0)
    values = (mass_error, component_error, energy_error)
    assert all(math.isfinite(v) and v < tolerance for v in values), (name, values)
    result = dict(name=name, mass_relative=mass_error,
        component_relative=component_error, energy_relative=energy_error,
        tolerance=tolerance)
    engineering_checks.append(result)
    print(name, {k: f"{v:.2e}" for k, v in result.items() if isinstance(v, float)})
    return result

def build_dry_plant(precooling_C=-30.0, flow_kg_hr=350000.0):
    """Hydrocarbon-only boundary after acid gas removal and deep dehydration.

    Pretreatment, mercury removal and solid deposition are outside this model.
    Fractions sum to one; they are not a water-saturated raw gas specification.
    """
    fluid = jneqsim.thermo.system.SystemSrkEos(298.15, 70.0)
    recipe = {"nitrogen": .005, "methane": .800, "ethane": .085,
        "propane": .045, "i-butane": .010, "n-butane": .015,
        "i-pentane": .008, "n-pentane": .007, "n-hexane": .010,
        "n-heptane": .010, "n-octane": .005}
    assert abs(sum(recipe.values())-1.0) < 1e-12
    for name, fraction in recipe.items():
        fluid.addComponent(name, fraction)
    fluid.setMixingRule("classic")
    feed = Stream("Plant Inlet Feed", fluid)
    feed.setFlowRate(flow_kg_hr, "kg/hr")
    inlet_sep = Separator("Inlet Separator", feed)
    inlet_sys = ProcessSystem()
    inlet_sys.add(feed)
    inlet_sys.add(inlet_sep)
    inlet_sys.run()

    # External cooling: no heat recovery is credited without a second exchanger side.
    precooler = Cooler("Precooler", inlet_sep.getGasOutStream())
    precooler.setOutTemperature(precooling_C, "C")
    feed_knockout = Separator("Expander Feed Knockout", precooler.getOutletStream())
    expander = Expander("Turboexpander", feed_knockout.getGasOutStream())
    expander.setOutletPressure(20.0)
    expander.setIsentropicEfficiency(.85)
    liquid_valve = Valve("Cold Liquid Letdown", feed_knockout.getLiquidOutStream())
    liquid_valve.setOutletPressure(20.0, "bara")
    cold_mixer = Mixer("Cold Streams Mixer")
    cold_mixer.addStream(expander.getOutletStream())
    cold_mixer.addStream(liquid_valve.getOutletStream())
    cold_sep = Separator("Cold Separator", cold_mixer.getOutletStream())
    recomp = Compressor("Recompressor", cold_sep.getGasOutStream())
    recomp.setOutletPressure(35.0, "bara")
    recomp.setUsePolytropicCalc(True)
    recomp.setPolytropicEfficiency(.78)
    intercooler = Cooler("Intercooler", recomp.getOutletStream())
    intercooler.setOutTemperature(30.0, "C")
    residue_comp = Compressor("Residue Gas Compressor", intercooler.getOutletStream())
    residue_comp.setOutletPressure(70.0, "bara")
    residue_comp.setUsePolytropicCalc(True)
    residue_comp.setPolytropicEfficiency(.78)
    aftercooler = Cooler("Export Aftercooler", residue_comp.getOutletStream())
    aftercooler.setOutTemperature(30.0, "C")
    ngl_units = [precooler, feed_knockout, expander, liquid_valve, cold_mixer,
        cold_sep, recomp, intercooler, residue_comp, aftercooler]
    ngl_sys = ProcessSystem()
    for unit in ngl_units:
        ngl_sys.add(unit)
    ngl_sys.run()
    # A gas-only expander inlet is necessary for the present turbine assumption.
    assert feed_knockout.getGasOutStream().getFluid().getNumberOfPhases() == 1
    for gas_stream in (intercooler.getOutletStream(), aftercooler.getOutletStream()):
        assert gas_stream.getFluid().getNumberOfPhases() == 1
        assert str(gas_stream.getFluid().getPhase(0).getType()) == "GAS"

    # One contacting tray plus an equilibrium reboiler: a small stabilization case.
    # The specified heat input is part of the stage energy equations.
    heater = Heater("Stabilizer Feed Heater", cold_sep.getLiquidOutStream())
    heater.setOutTemperature(-30.0, "C")
    column = DistillationColumn("NGL Stabilizer", 1, True, False)
    column.addFeedStream(heater.getOutletStream(), 1)
    column.setTopPressure(19.5)
    column.setBottomPressure(20.0)
    column.getReboiler().setHeatInput(4.5e6)
    column.setSolverType(DistillationColumn.SolverType.DIRECT_SUBSTITUTION)
    column.setMaxNumberOfIterations(100, True)
    column.setTemperatureTolerance(1e-7)
    column.setMassBalanceTolerance(1e-6)
    column.setEnthalpyBalanceTolerance(1e-5)
    column.setEnforceEnergyBalanceTolerance(True)
    column.setMeshResidualTolerance(1e-5)
    column.setEnforceMeshResidualTolerance(True)
    frac_sys = ProcessSystem()
    frac_sys.add(heater)
    frac_sys.add(column)
    frac_sys.run()
    plant = ProcessModel()
    plant.add("Inlet Receiving", inlet_sys)
    plant.add("NGL Recovery", ngl_sys)
    plant.add("Stabilization", frac_sys)
    # Areas are already solved sequentially; a repeat verifies the assembled model.
    plant.run()
    assert column.solved() and str(column.getLastSolveStatus()) == "RIGOROUS_CONVERGED"
    assert column.getLastMeshResidualNorm() < 1e-5
    assert column.getGasOutStream().getFlowRate("kg/hr") > 0
    assert column.getReboiler().getLiquidOutStream().getFlowRate("kg/hr") > 0
    return locals()

def verify_dry_plant(case):
    feed, sep = case["feed"], case["inlet_sep"]
    check_balance("inlet separator", [feed], [sep.getGasOutStream(), sep.getLiquidOutStream()])
    for key in ("precooler", "intercooler", "aftercooler", "heater"):
        unit = case[key]
        check_balance(key, list(unit.getInletStreams()), [unit.getOutletStream()], unit.getDuty())
    for key in ("feed_knockout", "cold_sep"):
        unit = case[key]
        check_balance(key, list(unit.getInletStreams()),
            [unit.getGasOutStream(), unit.getLiquidOutStream()])
    for key in ("expander", "recomp", "residue_comp"):
        unit = case[key]
        check_balance(key, list(unit.getInletStreams()), [unit.getOutletStream()], unit.getPower())
    valve, mixer = case["liquid_valve"], case["cold_mixer"]
    check_balance("JT liquid letdown", list(valve.getInletStreams()), [valve.getOutletStream()])
    check_balance("cold mixer", list(mixer.getInletStreams()), [mixer.getOutletStream()])
    column = case["column"]
    bottoms = column.getReboiler().getLiquidOutStream()
    overhead = column.getGasOutStream()
    check_balance("stabilizer specified duty", [case["heater"].getOutletStream()],
        [overhead, bottoms], 4.5e6)
    # Independently reconstruct each stage balance and phase fugacity equality.
    equilibrium_errors = []
    for index in range(column.getNumberOfTrays()):
        tray = column.getTray(index)
        qstage = 4.5e6 if index == 0 else 0.0
        check_balance(f"stabilizer stage {index}", list(tray.getInletStreams()),
            [tray.getGasOutStream(), tray.getLiquidOutStream()], qstage)
        stage_fluid = tray.getThermoSystem().clone()
        stage_fluid.init(3)
        assert stage_fluid.getNumberOfPhases() == 2
        for p in range(2):
            phase = stage_fluid.getPhase(p)
            assert abs(sum(phase.getComponent(i).getx() for i in range(
                stage_fluid.getNumberOfComponents()))-1.0) < 1e-8
        for i in range(stage_fluid.getNumberOfComponents()):
            a, b = (stage_fluid.getPhase(p).getComponent(i) for p in range(2))
            fa, fb = a.getx()*a.getFugacityCoefficient(), b.getx()*b.getFugacityCoefficient()
            if min(fa, fb) > 1e-14:
                equilibrium_errors.append(abs(math.log(fa/fb)))
    assert max(equilibrium_errors) < 1e-5
    # Independent whole-control-volume balance excludes internal area crossings.
    heat = sum(case[k].getDuty() for k in ("precooler", "intercooler", "aftercooler", "heater")) + 4.5e6
    shaft = sum(case[k].getPower() for k in ("expander", "recomp", "residue_comp"))
    products = [sep.getLiquidOutStream(), case["aftercooler"].getOutletStream(), overhead, bottoms]
    check_balance("whole dry plant", [feed], products, heat + shaft)
    # Independent PS-flash reconstructs the expander isentropic reference.
    ein = case["feed_knockout"].getGasOutStream().getFluid()
    ideal = ein.clone()
    ideal.setPressure(20.0)
    ThermodynamicOperations(ideal).PSflash(ein.getEntropy())
    eta = (ein.getEnthalpy()-case["expander"].getOutletStream().getFluid().getEnthalpy()) / (ein.getEnthalpy()-ideal.getEnthalpy())
    assert abs(eta-.85) < 1e-5
    gas = case["aftercooler"].getOutletStream()
    return dict(feed_kg_hr=feed.getFlowRate("kg/hr"),
        export_kg_hr=gas.getFlowRate("kg/hr"), export_pressure_bara=gas.getPressure("bara"),
        inlet_condensate_kg_hr=sep.getLiquidOutStream().getFlowRate("kg/hr"),
        cold_liquid_kg_hr=case["cold_sep"].getLiquidOutStream().getFlowRate("kg/hr"),
        stabilizer_overhead_kg_hr=overhead.getFlowRate("kg/hr"),
        stabilizer_bottoms_kg_hr=bottoms.getFlowRate("kg/hr"),
        stabilizer_bottoms_methane_mol_pct=100*bottoms.getFluid().getComponent("methane").getz(),
        gross_compression_MW=(case["recomp"].getPower()+case["residue_comp"].getPower())/1e6,
        recovered_expander_MW=-case["expander"].getPower()/1e6,
        precooler_duty_MW=case["precooler"].getDuty()/1e6,
        reboiler_duty_MW=column.getReboiler().getDuty()/1e6,
        mesh_residual=column.getLastMeshResidualNorm(),
        independent_log_fugacity_error=max(equilibrium_errors), expander_efficiency=eta)

case = build_dry_plant()
plant_results = verify_dry_plant(case)
print(json.dumps(plant_results, indent=2))
