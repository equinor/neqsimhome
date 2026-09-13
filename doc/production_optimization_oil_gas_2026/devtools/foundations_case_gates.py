"""Independent arithmetic/physical-domain checks for named manuscript cases."""
import ast,math,re

def case_gates(chapter,index,code,s):
 rows=[]
 def row(name,scope):
  r={'block':index,'equipment':name,'class':'CaseAcceptance','scope':scope,'checks':[]};rows.append(r)
  return r
 def ck(r,name,value,tolerance):
  value=float(value);r['checks'].append({'name':name,'error':value if math.isfinite(value) else str(value),'tolerance':tolerance,'pass':math.isfinite(value) and value<=tolerance})
 def boolean(r,name,value):ck(r,name,0 if value else 1,0)
 if '.addHotStream(' in code and 'pinch.run()' in code:
  hot=[];cold=[];delta=None
  for node in ast.walk(ast.parse(code)):
   if isinstance(node,ast.Call):
    if isinstance(node.func,ast.Name) and node.func.id=='PinchAnalysis':delta=float(ast.literal_eval(node.args[0]))
    if isinstance(node.func,ast.Attribute) and node.func.attr in ['addHotStream','addColdStream']:
     vals=[float(ast.literal_eval(v)) for v in node.args[1:]]
     (hot if node.func.attr=='addHotStream' else cold).append(vals)
  if hot and cold and delta is not None:
   r=row('Pinch heat cascade','Independent constant-heat-capacity shifted-temperature interval cascade; validates specified stream targets, not plant stream data')
   shifted=[(a-delta/2,b-delta/2,c) for a,b,c in hot]+[(b+delta/2,a+delta/2,-c) for a,b,c in cold]
   levels=sorted(set(v for a,b,c in shifted for v in [a,b]),reverse=True)
   cascade=[0.0]
   for upper,lower in zip(levels,levels[1:]):
    mid=(upper+lower)/2;cp=sum(c for a,b,c in shifted if b<mid<a)
    cascade.append(cascade[-1]+cp*(upper-lower))
   qh=max(0,-min(cascade));qc=cascade[-1]+qh
   ck(r,'minimum_hot_utility_kW',abs(s['pinch'].getMinimumHeatingUtility()-qh),1e-7)
   ck(r,'minimum_cold_utility_kW',abs(s['pinch'].getMinimumCoolingUtility()-qc),1e-7)
   r['independent_result']={'hot_utility_kW':qh,'cold_utility_kW':qc,'minimum_shifted_cascade_kW':min(cascade)}
 if 'hydrateFormationTemperature' in code:
  r=row('Hydrate result domain','Finite hydrate temperatures and inhibitor-direction check only; no independent hydrate reference data')
  vals=[]
  for key in ['T_hyd','T_hyd_with_MEG','T_hyd_no_MEG']:
   if key in s and (key in code):vals.append(float(s[key]))
  if 'hydrate_temps' in code:vals.extend(float(t) for t in s.get('hydrate_temps',[]) if t is not None)
  if 'fluid_hyd' in code:vals.append(float(s['fluid_hyd'].getTemperature('C')))
  boolean(r,'nonempty_finite_temperature_in_exercised_230_to_330_K_domain',bool(vals) and all(math.isfinite(t) and -43.15<t<56.85 for t in vals))
  if 'T_hyd_with_MEG' in code and 'T_hyd_no_MEG' in code:boolean(r,'MEG_lowers_equilibrium_temperature',s['T_hyd_with_MEG']<s['T_hyd_no_MEG'])
  r['temperature_C']=vals
 if 'SimpleAmineAbsorber' in code:
  r=row('Amine loading and material allocation','Literal component/mass assertions and explicit net-loading screen; inferred isothermal heat is not an independent energy-closure test')
  ck(r,'relative_mass_closure',abs(s['mass_in']-s['mass_out'])/s['mass_in'],1e-6)
  boolean(r,'net_loading_within_stated_limit',0<s['net_loading']<=s['assumed_net_loading_limit'])
  boolean(r,'original_5_tph_rejected',s['original_5_tph_loading']>s['assumed_net_loading_limit'])
  r['values']={'net_loading_mol_mol':s['net_loading'],'isothermal_heat_input_W':s['isothermal_heat_W']}
 if 'GasTurbineUnit' in code or ('gas_turbine.run()' in code and 'available_mw' in code):
  r=row('Turbine performance bookkeeping','Package heat-rate/efficiency, positive fuel and power-domain identities only; synthetic map and exhaust composition are not a combustor or OEM validation')
  unit=s.get('gt') if 'gt.run()' in code else s.get('gas_turbine')
  eta=float(unit.getThermalEfficiency());hr=float(unit.getEffectiveHeatRateKJPerKWh())
  boolean(r,'efficiency_domain',0<eta<1);ck(r,'heat_rate_efficiency_identity',abs(eta*hr/3600-1),1e-10)
  boolean(r,'nonnegative_fuel_and_available_power',unit.getFuelMassFlowKgPerS()>=0 and unit.getAvailablePowerW()>0)
  if 'available_mw' in code:
   boolean(r,'finite_ambient_sweep',all(math.isfinite(v) and v>0 for v in s['available_mw']+s['fuel_kg_hr']))
   boolean(r,'higher_ambient_derates_power',s['available_mw'][-1]<s['available_mw'][0])
 if 'carbon_in =' in code:
  r=row('Carbon accounting','Carbon-atom closure for explicit pure-methane fuel/slip scenario; GWP and prices are assumptions')
  ck(r,'relative_carbon_closure',abs(s['carbon_in']-s['carbon_out'])/s['carbon_in'],1e-12)
 if 'displacement_m3_day =' in code:
  r=row('Rod pump displacement','Geometric swept-volume and volumetric-efficiency check; no whole-well hydraulic validation')
  ck(r,'swept_volume_relative_error',abs(s['rodpump'].getTheoreticalDisplacement('m3/day')/s['displacement_m3_day']-1),1e-12)
  ck(r,'volumetric_efficiency',abs(s['rodpump'].getActualDisplacement('m3/day')/s['displacement_m3_day']-.8),1e-12)
 if 'jet.getProducedRate' in code:
  r=row('Jet pump declared operating domain','Head-ratio screening model; one-stream implementation does not model a full power-fluid material/energy boundary')
  boolean(r,'pressure_between_suction_and_motive',s['prod_stream'].getPressure('bara')<s['jet'].getDischargePressure()<250)
  boolean(r,'positive_rate_efficiency_domain',s['jet'].getProducedRate('m3/day')>0 and 0<s['jet'].getEfficiency()<1)
 if 'steam_enthalpy_rise =' in code:
  r=row('HRSG and steam turbine','Same-EOS feedwater-to-steam duty consistency and turbine shaft-work balance; SRK water is not validated here against steam-table reference data')
  ck(r,'steam_duty_relative_error',abs(s['recovered_heat']/s['hrsg'].getHeatTransferred('W')-1),1e-6)
  ck(r,'steam_turbine_work_relative_error',abs(s['steam_work']/s['steam_turbine'].getPower('W')-1),1e-5)
 if 'optimizeThroughput(' in code and 'result' in s:
  r=row('Throughput optimizer acceptance','Returned numerical feasibility and declared active upper/lower constraints; objective global optimality is not inferred')
  boolean(r,'optimizer_feasible',bool(s['result'].isFeasible()))
  boolean(r,'finite_positive_rate',math.isfinite(s['result'].getOptimalRate()) and s['result'].getOptimalRate()>0)
 if 'getUnmetDemand() - 6.0e6' in code:
  r=row('Electrical energy bus','Supply plus unserved demand equals requested load; allocation accounting only')
  served=sum(float(x.getPowerMagnitude()) for x in s['loads']);unmet=float(s['report'].getUnmetDemand())
  ck(r,'served_plus_unmet_minus_request_W',abs(served+unmet-16e6),1)
  ck(r,'served_minus_supply_W',abs(served-10e6),1)
 for r in rows:r['pass']=all(x['pass'] for x in r['checks'])
 return rows
