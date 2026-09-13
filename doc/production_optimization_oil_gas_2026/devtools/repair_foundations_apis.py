from pathlib import Path
import re

BOOK = Path(__file__).resolve().parents[1]
for path in sorted((BOOK / 'chapters').glob('*/chapter.md'))[:18]:
    text = path.read_text(encoding='utf-8')
    number = int(path.parent.name[2:4])
    text = text.replace('v.getUnit()', 'v.getDefaultUnit()')
    text = text.replace('hydrateEquilibriumTemperature()', 'hydrateFormationTemperature()')
    text = text.replace("getJouleThomsonCoefficient('C/bara')", "getJouleThomsonCoefficient('K/bar')")
    text = text.replace('.setCharacterizeMethod("Pedersen")', '.setPlusFractionModel("Pedersen")')
    text = text.replace('.setInteractionParameter(', '.setBinaryInteractionParameter(')
    text = text.replace('"am3/', '"Am3/').replace("'am3/", "'Am3/")
    text = text.replace('.setReBoilerDuty(', '.setHeatInput(')
    text = re.sub(r'^.*getCompressorChart\(\)\.setChartType\("interpolate and extrapolate"\).*\n', '# Generated charts already use interpolation and extrapolation.\n', text, flags=re.M)
    if number in (5, 7, 8, 9):
        text = text.replace('negative = upward flow', 'positive = outlet above inlet')
        text = re.sub(r'\.setElevation\(-([0-9.]+)\)', r'.setElevation(\1)', text)
        if number in (7, 8):
            text = re.sub(r'(\w+\.setLength\()([0-9.]+)(\))', lambda m: m[1] + (str(float(m[2]) * 1000.0) if float(m[2]) < 100.0 else m[2]) + m[3], text)
            text = text.replace('setLength(float(dist))', 'setLength(float(dist) * 1000.0)')
            text = text.replace('setLength(pipe_length_km)', 'setLength(pipe_length_km * 1000.0)')
            text = text.replace('# km\n', '# m (15 km)\n')
    if number == 2:
        text = text.replace('fluid_hyd.setMixingRule(10)', 'fluid_hyd.setMixingRule(10)\nfluid_hyd.setHydrateCheck(True)')
        text = text.replace('SystemGERG2004Eos(273.15 + 15.0, 50.0)', 'SystemSrkEos(273.15 + 15.0, 50.0)')
        text = text.replace("fluid_gerg.getPhase('gas').getDensity('kg/m3')", "fluid_gerg.getPhase('gas').getDensity_GERG2008()")
        text = text.replace('# GERG-2008 for custody transfer quality calculations', '# Flash with SRK, then evaluate single-phase gas density with Java GERG-2008.\n# The legacy SystemGERG2004Eos requires a separate native library.')
    if number == 4:
        text = text.replace('reservoir.setReservoirFluid(fluid)\nreservoir.setGasOilContact(200.0)  # OGOC depth in meters', '# Initial in-situ gas, oil and water pore volumes in m3 (illustrative).\nreservoir.setReservoirFluid(fluid, 1.0e7, 2.0e7, 5.0e6)')
        text = text.replace('reservoir.addWell("Producer-1")', 'producer = reservoir.addOilProducer("Producer-1")\nproducer.setFlowRate(10000.0, "kg/hr")')
        text = text.replace('drive = MaterialBalanceGasDrive(initialPressureBara, gasInPlaceSm3)', 'initialPressureBara, gasInPlaceSm3, averageZ = 250.0, 1.0e9, 0.90\ndrive = MaterialBalanceGasDrive(initialPressureBara, gasInPlaceSm3, averageZ)')
    if number == 5:
        text = text.replace('SuckerRodPump("rod pump", wellStream)', 'SuckerRodPump("rod pump", well_stream)')
        text = text.replace('JetPump("jet pump", producedStream)', 'JetPump("jet pump", prod_stream)')
    if number == 6:
        text = text.replace('well = WellFlow("Well-A", reservoirStream)', '''# Standalone oil IPR example, separate from the Java network.
oil_fluid = jneqsim.thermo.system.SystemSrkEos(353.15, 250.0)
oil_fluid.addComponent("methane", 0.20)
oil_fluid.addComponent("n-decane", 0.80)
oil_fluid.setMixingRule("classic")
reservoirStream = jneqsim.process.equipment.stream.Stream("Reservoir", oil_fluid)
reservoirStream.setFlowRate(200.0, "Sm3/day")
reservoirStream.run()
qTest, pwfTest, reservoirP = 200.0, 180.0, 250.0
well = WellFlow("Well-A", reservoirStream)''')
        text = text.replace('w["Pr"] * 1e5, w["PI"])', 'w["PI"] * 800.0 / 86400.0 / 1e5, False)')
        text = text.replace('result.getObjectiveValue()', 'result.objectiveValue').replace('result.getOptimalValues()', 'result.optimalValues')
        text = text.replace('point.getObjectiveValue()', 'point.objectiveValue').replace('point.getSecondaryObjective()', 'point.objectives[1]')
        text = text.replace('get("totalSinkFlow")', 'get("totalFlowRate")').replace("get('totalSinkFlow')", "get('totalFlowRate')")
        text = text.replace('target_oil_rate', 'target_total_mass_rate').replace('# kg/s total oil', '# kg/s total mixture; phase allocation is a separate calculation')
        text = text.replace('    # Constrained optimization: minimize total water while meeting oil target\n    pass', '    print("Total-mixture target exceeded; a phase-aware allocation constraint is required.")')
    if number == 9:
        text = text.replace('fluid_with_MEG.setMultiPhaseCheck(True)', 'fluid_with_MEG.setMultiPhaseCheck(True)\nfluid_with_MEG.setHydrateCheck(True)')
        text = text.replace('fluid_no_MEG.setMultiPhaseCheck(True)', 'fluid_no_MEG.setMultiPhaseCheck(True)\nfluid_no_MEG.setHydrateCheck(True)')
        for old, new in [('n-C11','nC11'),('n-C17','nC17'),('n-C20','nC20')]:
            text = text.replace('"'+old+'"', '"'+new+'"')
        text = text.replace('# Flash at decreasing temperatures to find WAT', '# Liquid-property cooling screen only: TPflash without a wax model cannot determine WAT.')
    if number == 10:
        text = re.sub(r'(get(?:Gas|Liquid|Oil|Water)OutStream\(\))\.getDensity', r'\1.getFluid().getDensity', text)
        for name in ('gas_density = gas','rho_gas = gas','rho_liq = liq','rho_G = gas','rho_L = oil'):
            text = text.replace(name+'.getDensity', name+'.getFluid().getDensity')
        for name in ('oil_out','water_out','gas_out','liq_out'):
            text = text.replace(name+'.getDensity', name+'.getFluid().getDensity')
    path.write_text(text, encoding='utf-8')

# Audit harness: JShell rejects non-JAR Maven descriptor files on its classpath.
path = BOOK / 'devtools/verify_foundations_java.py'
text = path.read_text()
text = text.replace("(args.project_root / 'target/neqsim-dev-classpath.txt').read_text().strip()", "os.pathsep.join(p for p in (args.project_root / 'target/neqsim-dev-classpath.txt').read_text().strip().split(os.pathsep) if p.endswith('.jar'))")
path.write_text(text)
