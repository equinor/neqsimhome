"""Correct silently accepted pump units and conserve carbon in emissions accounting."""
from revise_foundations_science_phase3 import R,S
R('ch05','rod_units','rodpump.getTheoreticalDisplacement("Sm3/day")','rodpump.getTheoreticalDisplacement("m3/day")')
R('ch05','rod_actual_units','rodpump.getActualDisplacement("Sm3/day")','rodpump.getActualDisplacement("m3/day")')
R('ch05','jet_units','jet.getProducedRate("Sm3/day")','jet.getProducedRate("m3/day")')
R('ch05','rod_weight_units','rodpump.setRodWeightPerLength(35.0)         # [N/m]','rodpump.setRodWeightPerLength(35.0 / 9.80665)  # kg/m from assumed buoyant 35 N/m')
R('ch05','rod_discharge','rodpump.setDischargePressure(15.0)          # [bara]','rodpump.setDischargePressure(100.0)         # bara, above this 80 bara inlet')
R('ch05','rod_check','print("Polished rod load:", rodpump.getPolishedRodLoad(), "N")','''print("Polished rod load:", rodpump.getPolishedRodLoad(), "N")
import math
displacement_m3_day = math.pi * 0.0381**2 / 4.0 * 1.68 * 8.0 * 1440.0
assert abs(rodpump.getTheoreticalDisplacement("m3/day") / displacement_m3_day - 1.0) < 1e-12
assert abs(rodpump.getActualDisplacement("m3/day") / displacement_m3_day - 0.80) < 1e-12
assert rodpump.getPolishedRodLoad() > 0.0''')
R('ch05','jet_domain_check','print("Produced rate:", jet.getProducedRate("m3/day"))','''print("Produced rate (actual m3/day):", jet.getProducedRate("m3/day"))
assert prod_stream.getPressure("bara") < jet.getDischargePressure() < 250.0
assert 0.0 < jet.getEfficiency() < 1.0
assert jet.getProducedRate("m3/day") > 0.0''')
R('ch05','pump_scope','`getTheoreticalDisplacement` evaluates the swept-volume formula above,', '`getTheoreticalDisplacement` uses actual displacement volume, not a standard-state fluid conversion. The accepted unit strings are `m3/sec` and `m3/day`; an unsupported `Sm3/day` string silently returned m3/s in this source version. The displacement and rod-load checks are geometry/load screening; this one-stream pump object does not establish a complete reservoir-to-surface lift solution. The method evaluates the swept-volume formula above,')
R('ch18','emissions_carbon', 'co2_emission_factor = 2.75  # kg CO2 per kg fuel gas','co2_emission_factor = 44.01 / 16.043  # pure-methane combustion kg CO2/kg CH4')
R('ch18','emissions_fuel_basis','# Track CO2 emissions and carbon cost','# Pure-methane accounting scenario, separate from the mixed-fuel turbine above')
R('ch18','emissions_slip','co2_direct = fuel_rate_kg_hr * co2_emission_factor','co2_direct = fuel_rate_kg_hr * (1.0 - ch4_slip) * co2_emission_factor')
R('ch18','emissions_cost_base','total_carbon_cost_nok = annual_co2_tonnes * (','annual_direct_co2_tonnes = co2_direct * hours_per_year / 1000.0\ntotal_carbon_cost_nok = annual_direct_co2_tonnes * (')
R('ch18','production_uptime','annual_boe = production_boe_per_day * 365','annual_boe = production_boe_per_day * hours_per_year / 24.0  # same operating hours as emissions')
R('ch18','carbon_mass_check','print(f"Emissions intensity: {emissions_intensity:.1f} kg CO2/boe")','''print(f"Emissions intensity: {emissions_intensity:.1f} kg CO2-eq/boe")
# Carbon atoms in burned CO2 plus unburned CH4 equal the fuel carbon inventory.
carbon_in = fuel_rate_kg_hr * 12.011 / 16.043
carbon_out = co2_direct * 12.011 / 44.01 + fuel_rate_kg_hr * ch4_slip * 12.011 / 16.043
assert abs(carbon_in - carbon_out) / carbon_in < 1e-12
print("Carbon cost applies only to direct CO2 in this illustrative price scenario.")''')
R('ch18','HRSG_actual_water','steam.setFlowRate(hrsg.getSteamFlowRate("kg/sec"), "kg/sec")','''# Replace HRSG's internal approximate steam-enthalpy correlation with the same
# water EOS used for the turbine, so recovered heat and steam inventory agree.
steam_properties = steam_fluid.clone()
jneqsim.thermodynamicoperations.ThermodynamicOperations(steam_properties).TPflash()
steam_properties.initProperties()
feedwater_properties = steam_fluid.clone()
feedwater_properties.setTemperature(363.15)
jneqsim.thermodynamicoperations.ThermodynamicOperations(feedwater_properties).TPflash()
feedwater_properties.initProperties()
steam_enthalpy_rise = steam_properties.getEnthalpy("J/kg") - feedwater_properties.getEnthalpy("J/kg")
assert steam_enthalpy_rise > 0.0
steam.setFlowRate(hrsg.getHeatTransferred("W") / steam_enthalpy_rise, "kg/sec")''')
R('ch18','HRSG_steam_balance','print("Steam turbine power (MW):", steam_turbine.getPower("MW"))','''print("Steam turbine power (MW):", steam_turbine.getPower("MW"))
steam.getFluid().initProperties()
steam_turbine.getOutletStream().getFluid().initProperties()
recovered_heat = steam.getFlowRate("kg/sec") * steam_enthalpy_rise
assert abs(recovered_heat / hrsg.getHeatTransferred("W") - 1.0) < 1e-6
steam_work = steam.getFlowRate("kg/sec") * (
    steam.getFluid().getEnthalpy("J/kg") -
    steam_turbine.getOutletStream().getFluid().getEnthalpy("J/kg"))
assert steam_work > 0.0
assert abs(steam_work / steam_turbine.getPower("W") - 1.0) < 1e-5''')
