"""Repair the liquid/gas standard-volume basis found by full-view figure review."""
from pathlib import Path
import hashlib,json,re,shutil
B=Path(__file__).resolve().parents[1]
C=next((B/'chapters').glob('ch24*'))/'chapter.md'
P=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
text=C.read_text(encoding='utf-8-sig');fences=list(P.finditer(text))
archive=B/'verification/scientific_revision/rejected_gas_equivalent_oil_basis'
archive.mkdir(exist_ok=True)
for source in [C,B/'verification/scientific_revision/ch24_solution_checks.json',B/'.build/solution_runs/ch24_production_optimization/figures/sep_pressure_optimization.png']:
 data=source.read_bytes();(archive/(hashlib.sha256(data).hexdigest()+'_'+source.name)).write_bytes(data)
helper='''# Fixed-inventory flash of the separated oil at the declared reference state.
# Phase actual volume = phase mass / density; Sm3/day is gas-equivalent here.
def stock_tank_flash(oil_stream):
    source = oil_stream.getFluid()
    source.initProperties()
    liquid = source.clone()
    mass_in = float(oil_stream.getFlowRate("kg/hr"))
    moles_in = [float(source.getComponent(k).getNumberOfmoles())
                for k in range(source.getNumberOfComponents())]
    liquid.setTemperature(288.15)
    liquid.setPressure(1.01325)
    liquid.setMultiPhaseCheck(True)
    jneqsim.thermodynamicoperations.ThermodynamicOperations(liquid).TPflash()
    liquid.initProperties()
    phases = []
    for k in range(liquid.getNumberOfPhases()):
        phase = liquid.getPhase(k)
        mass = float(phase.getFlowRate("kg/hr"))
        density = float(phase.getDensity("kg/m3"))
        volume = float(phase.getFlowRate("m3/hr"))
        assert mass >= 0.0 and density > 0.0 and np.isfinite(volume)
        assert abs(volume*density-mass) < 1e-8*max(mass, 1.0)
        phases.append({"phase": str(phase.getType()), "mass_kg_hr": mass,
                       "density_kg_m3": density, "actual_m3_hr": volume,
                       "enthalpy_W": float(phase.getEnthalpy())})
    mass_error = abs(sum(r["mass_kg_hr"] for r in phases)-mass_in)/mass_in
    scale = max(sum(moles_in), 1e-12)
    component_error = max(abs(sum(float(liquid.getPhase(k).getComponent(j)
        .getNumberOfMolesInPhase()) for k in range(liquid.getNumberOfPhases()))
        - amount)/scale for j, amount in enumerate(moles_in))
    assert mass_error < 1e-6 and component_error < 1e-6
    oil = next(r for r in phases if r["phase"] == "oil")
    assert 450.0 < oil["density_kg_m3"] < 1000.0  # light condensate domain
    # An isothermal flash requires conditioning heat; it is not adiabatic.
    duty = float(liquid.getEnthalpy()-source.getEnthalpy())
    energy_error = abs(sum(r["enthalpy_W"] for r in phases)
        - float(source.getEnthalpy())-duty)/max(abs(duty),abs(float(liquid.getEnthalpy())),1.0)
    assert energy_error < 1e-5
    return {"temperature_K": 288.15, "pressure_bara": 1.01325,
            "feed_mass_kg_hr": mass_in, "products": phases,
            "oil_m3_day": 24.0*oil["actual_m3_hr"],
            "mass_relative_error": mass_error,
            "component_relative_error": component_error,
            "energy_relative_error": energy_error,
            "conditioning_duty_W": duty}

'''
replacements={}
code=fences[41][3]
code=code.replace('new OptimizationObjective("oil_rate", proc -> ((ThreePhaseSeparator) proc.getUnit("HP Sep")).getOilOutStream().getFlowRate("Sm3/day"), 1.0, ObjectiveType.MAXIMIZE),',
'''new OptimizationObjective("oil_mass_kg_hr", proc ->
        ((ThreePhaseSeparator) proc.getUnit("HP Sep"))
            .getOilOutStream().getFlowRate("kg/hr"),
        1.0, ObjectiveType.MAXIMIZE),''')
replacements[42]=code
code=fences[58][3].replace('Minimize negative oil rate (maximize oil) subject to constraints.',
    'Maximize separator oil mass flow (kg/hr), before stock-tank flashing.')
code=code.replace('oil_rate = hp_sep.getOilOutStream().getFlowRate("Sm3/day")','oil_rate = hp_sep.getOilOutStream().getFlowRate("kg/hr")')
replacements[59]=code
code=fences[61][3]
code=code.replace('# Build process model\n# ... (as shown earlier)\n',helper)
code=code.replace('# Sweep separator pressure', '# Sweep at a fixed feed rate, independent of the prior optimizer state.\nfeed.setFlowRate(250000.0, "kg/hr")\nstock_tank_results = []\n# Sweep separator pressure')
code=code.replace('    oil_rates.append(hp_sep.getOilOutStream().getFlowRate("Sm3/day"))',
'''    tank = stock_tank_flash(hp_sep.getOilOutStream())
    stock_tank_results.append(tank)  # gas and any aqueous product retained
    oil_rates.append(tank["oil_m3_day"])''')
code=code.replace('# Calculate total revenue', '# Hypothetical product value less compressor electricity only.\n# Flash gas has zero sales credit; conditioning heat, losses, CAPEX, tax and\n# other operating costs are outside this deliberately limited screen.')
code=code.replace('oil_rev = oil_rates[i] * 6.29 * oil_price / 1000', 'oil_rev = oil_rates[i] / 0.158987294928 * oil_price / 1000')
code=code.replace('# Find optimal pressure', '# Highest value among the 28 evaluated pressures; no global optimum claim.')
code=code.replace('Optimal separator pressure:', 'Highest sampled value at separator pressure:')
code=code.replace('At optimum: Oil=', 'At this grid point: stock-tank oil=').replace(':.0f} Sm3/d, ', ':.1f} m3/day, ')
code=code.replace('Net revenue:', 'Product value less compressor electricity:')
code=code.replace('Oil Rate (Sm3/day)', 'Stock-tank oil (m3/day at 15 C, 1.01325 bara)')
code=code.replace('Oil Rate vs Separator Pressure','Flashed stock-tank liquid oil')
code=code.replace("label=f'Optimal: {pressures[idx_opt]:.0f} bara'", "label=f'Highest sampled: {pressures[idx_opt]:.1f} bara'")
code=code.replace('Net Revenue (kUSD/day)', 'Product value less electricity (kUSD/day)')
code=code.replace('Net Revenue vs Separator Pressure', 'Limited economic screen')
code=code.replace('Figure 24.6: Separator Pressure Optimization', 'Separator pressure sensitivity at 250,000 kg/h feed')
code+='''\nimport json
with open("stock_tank_pressure_sweep.json", "w") as output:
    json.dump({"pressure_bara": pressures.tolist(), "oil_m3_day": oil_rates,
               "gas_MSm3_day": gas_rates, "compressor_MW": comp_powers,
               "limited_value_kUSD_day": revenues, "stock_tank_flashes": stock_tank_results,
               "best_grid_index": int(idx_opt)}, output, indent=2)
'''
replacements[62]=code
for i,code in sorted(replacements.items(),reverse=True):
 m=fences[i-1];text=text[:m.start(3)]+code+text[m.end(3):]
C.write_text(text,encoding='utf-8')
(archive/'rejection.json').write_text(json.dumps({'status':'rejected_basis',
 'reason':'Gas-equivalent standard volume on a liquid stream was incorrectly priced as liquid oil; old arithmetic and figure were not valid stock-tank calculations.',
 'source_path':'src/main/java/neqsim/thermo/phase/Phase.java#getFlowRate',
 'repaired_fences':[42,59,62]},indent=2),encoding='utf-8')
print('Installed Chapter24 liquid basis corrections')
