"""Chapter-specific identities and engineering limits; expanded during review."""


"""Case-specific physical and analytical checks, beyond successful execution.

Bounds apply to the stated teaching cases. Empirical correlations, assumed
maps, synthetic measurements and economics are explicitly scoped in SCOPES.
"""
import numpy as np

SCOPES = {
1: ('Natural-gas PVT and actual volume', 'SRK/PR methane NIST density benchmark is contextual; mixture data are not independently calibrated.'),
2: ('EOS comparisons, heat capacity, enthalpy and transport', 'Methane density and dilute limits benchmark EOS; no independent mixture viscosity or JT dataset.'),
3: ('CCE liquid dropout, phase volumes and sample-specific Bo', 'CCE is not CVD. TBP characterization and reservoir PVT need laboratory calibration.'),
4: ('PI/Vogel endpoints and Corey saturation bounds', 'Inflow and relative-permeability curves are specified correlations; imposed depth gradients are not a coupled hydrostatic solution.'),
5: ('Nodal pressure residual and production bounds', 'Gas-lift response is an illustrative correlation. No measured well test or lift calibration.'),
6: ('Well, choke and manifold conservation', 'Fixed-rate manifold example is not a pressure-coupled field network validation.'),
7: ('Segmented flowline state and pressure budget', 'Flow-regime map and waterfall allocations are conceptual; hydrate boundary lacks external validation.'),
8: ('Hydraulic domains, holdup and diameter conversion', 'Hydrostatic and no-flow limits do not validate Beggs-Brill against multiphase field data.'),
9: ('Hydrate/inhibitor/dew-point domains and monotonic sensitivities', 'No measured hydrate or inhibited-water dataset; composition and inhibitor basis must match the application.'),
10: ('Phase mass splits and Souders-Brown identity', 'K factor and residence criteria are assumed screening inputs, not separator vendor performance.'),
11: ('TVP, reference-density API gravity and staged material release', '37.8 C bubble pressure is TVP, not ASTM RVP. No crude assay benchmark.'),
12: ('Water-content bounds, JT first law and heavy-component nesting', 'No independent gas-conditioning recovery or dew-point dataset.'),
13: ('Three-phase material conservation', 'Equilibrium phase split does not predict emulsions, droplet separation or water-treatment removal efficiency.'),
14: ('Compressor first law and efficiency sensitivity', 'Independent dilute-argon limit supports equations; assumed efficiencies and temperature limits are not vendor guarantees.'),
15: ('Assumed compressor-map affinity scaling', 'Map curves are pedagogical, not measured machine curves; no surge or choke certification.'),
16: ('Two-stream energy closure, driving forces and effectiveness', 'Linear temperature profiles interpolate endpoints; exchanger UA and fouling need design data.'),
17: ('Valve mass and enthalpy conservation', 'Fixed-state Cv sizing and opening sweeps do not validate cavitation, noise or vendor trim performance.'),
18: ('Fuel-energy and annual-emissions unit identities', 'Gas-turbine part-load curve, carbon factor and annual hours are assumptions; no emissions certification.'),
19: ('Export hydraulics and calorific-value unit basis', 'ISO calculator execution is not custody-transfer certification or metering uncertainty validation.'),
20: ('Equipment utilization domains and fixed-rating capacity sweep', 'Autosizing establishes teaching ratings, not installed equipment capacity.'),
21: ('Dimensionless utilization and debottleneck arithmetic', 'Capacity changes are assigned scenarios; no CAPEX or production optimum is independently validated.'),
22: ('Feasible throughput bracket and search agreement', 'Search checks use the same process model. Monotone feasibility is case-specific.'),
23: ('Power-limited optimizer feasibility and independent grid search', 'Independent search algorithm comparison uses the same EOS; unspecified mechanical constraints remain outside scope.'),
24: ('Manual and engine throughput feasibility', 'Screening constraints are not a complete installed facility envelope.'),
25: ('Power utilization ratios', 'Overloads are deliberately plotted; a positive value is not an acceptance decision.'),
26: ('Network stream conservation and bounded rate response', 'No independent multiwell production history; well response and boundary conditions are illustrative.'),
27: ('Selected scenario constraint satisfaction', 'Discrete scenario comparison is not a probability model or an uncertainty quantile.'),
28: ('VFP inverse-solution pressure residuals', 'Measured VFP and thermal profiles are required for well prediction; analytic hydrostatics covers only a limit.'),
29: ('Lumped controller discrete inventory equation and actuator bounds', 'Python lumped dynamics illustrate control; these are not NeqSim equipment transients or a calibrated plant response.'),
30: ('Synthetic measurement residual and normalization identities', 'Noise-generated observations are not independent field validation or calibration.'),
31: ('Recycle residuals and achieved adjuster target', 'Timing is machine-dependent. Convergence does not establish model accuracy.'),
32: ('Enumerated Pareto nondominance', 'Efficiency is an assumed scenario/design input; tradeoffs are not an implementable optimal controller.'),
33: ('TEG material balance, explicit energy reconstruction and compression', 'Native SimpleTEGAbsorber has an energy residual after water transfer; reconstructed outlets close energy without validating stage mass transfer.'),
34: ('Integrated process material/energy accounting', 'Illustrative facility inputs lack plant calibration, operability and full equipment design evidence.'),
35: ('CO2 PVT domains and hydrogen-mixture calorific trends', 'Single-phase CO2 is not miscibility evidence; H2 Wobbe trends do not establish material compatibility or burner interchangeability.')
}

def validate_chapter(c, n):
    chapter = int(c.chapter[2:4])
    c.domain_scope = {'checked': SCOPES[chapter][0], 'limitations': SCOPES[chapter][1]}
    a = lambda name: np.asarray(n[name], dtype=float)
    def bounded(name, low=None, high=None, missing=False, unit='1', minimum=1):
        return c.array(name, n[name], low, high, missing, minimum, unit)
    def identity(name, actual, expected, atol=1e-9, rtol=1e-9, unit='1'):
        actual, expected = np.asarray(actual), np.asarray(expected)
        error = float(np.max(np.abs(actual - expected)))
        return c.close(name, error, 0, atol=atol + rtol * float(np.max(np.abs(expected))), unit=unit)
    def order(label, condition, actual='ordered'):
        return c.require(label, bool(np.all(condition)), actual, 'stated case ordering', category='justified_sensitivity')

    if chapter == 1:
        bounded('densities', 0, unit='kg/m3'); bounded('z_factors', 0)
        bounded('actual_volume_m3_hr', 0, unit='m3/hr')
        for pressure, volume in zip(n['whp_pressures'], n['actual_volume_m3_hr']):
            fluid = n['create_natural_gas'](313.15, float(pressure))
            n['ThermodynamicOperations'](fluid).TPflash(); fluid.initProperties()
            c.close('actual volume times density equals fixed mass flow', volume * fluid.getDensity('kg/m3'),
                    n['mass_flow_kg_hr'], atol=1e-6, rtol=1e-8, unit='kg/hr')
    elif chapter == 2:
        for key in ['density_srk','density_pr','cp_values','viscosities']: bounded(key, 0)
        c.monotonic('fixed-pressure mixture enthalpy rises with temperature', n['enthalpy_values'], 1, unit='J/mol')
    elif chapter == 3:
        bounded('liquid_vol_pct', 0, 100, missing=True, unit='volume %', minimum=3)
        bounded('gor_values', 0, missing=True, minimum=3); bounded('bo_values', 0, missing=True, minimum=3)
        c.close('characterization mole fractions sum', sum(n['mole_fracs']), 1, atol=1e-7)
    elif chapter == 4:
        identity('PI inflow law', a('q_pi'), n['PI']*(n['P_res']-a('Pwf')))
        identity('Vogel closed-reservoir endpoint', n['q_max_vogel']*(1-.2-.8), 0)
        identity('Vogel tangent agrees with PI at reservoir pressure', 1.8*n['q_max_vogel']/n['P_res'], n['PI'])
        bounded('Se',0,1); bounded('kr_w',0,n['kr_w_max']); bounded('kr_o',0,n['kr_o_max'])
        c.monotonic('Corey water mobility increases with saturation',n['kr_w'],1)
        c.monotonic('Corey oil mobility decreases with saturation',n['kr_o'],-1)
    elif chapter == 5:
        c.close('nodal achieved wellhead pressure', n['achieved_pwh'],n['P_wh_target'],atol=.05,unit='bara')
        c.close('nodal IPR pressure',n['p_op'],n['P_res']-n['q_op']/n['PI'],atol=1e-8,unit='bara')
        bounded('q_oil',0,unit='stb/day')
        c.close('illustrative gas-lift sampled maximum',n['q_opt_oil'],max(n['q_oil']),atol=1e-8)
    elif chapter == 6:
        bounded('choke_outlet_pressures',0,missing=True,unit='bara',minimum=3)
        bounded('manifold_pressures',0,missing=True,unit='bara',minimum=3)
        order('fixed-rate branches lose pressure',a('arrival_pressures')<=a('inlet_pressures')+1e-7)
        c.close('three specified branch mass rates',sum(n['flow_rates']),100000,atol=1e-4,unit='kg/hr')
    elif chapter == 7:
        c.close('segmented length',n['seg_length']*n['n_segments'],n['total_length'],atol=1e-8,unit='m')
        bounded('pressures',0,unit='bara'); c.monotonic('horizontal flowline pressure decreases',n['pressures'],-1,unit='bar')
        c.close('assigned pressure budget closes',n['P_reservoir']-sum(n[k] for k in ['dP_reservoir_drawdown','dP_wellbore','dP_xmas_tree','dP_flowline','dP_riser','dP_topsides']),n['P_separator'],atol=1e-8,unit='bar')
    elif chapter == 8:
        identity('inches to metres',a('diameters_m'),a('diameters_inch')*.0254)
        bounded('pressure_drops',0,80,missing=True,unit='bar',minimum=3)
        bounded('holdups',0,1,missing=True,minimum=3); bounded('gas_velocities',0,missing=True,minimum=3)
        bounded('max_flows',0,unit='kg/hr')
    elif chapter == 9:
        bounded('hydrate_temps_C',-273.15,100,missing=True,unit='C',minimum=3)
        bounded('hydrate_T_with_meg',-273.15,100,missing=True,unit='C',minimum=3)
        bounded('water_dew_temps',-273.15,100,unit='C',minimum=3)
        c.monotonic('fixed-fluid hydrate boundary rises with pressure',n['hydrate_temps_C'],1,atol=.05,unit='K')
        c.monotonic('specified MEG addition depresses hydrate boundary',n['hydrate_T_with_meg'],-1,atol=.05,unit='K')
        bounded('meg_wt_fractions',0,1)
    elif chapter == 10:
        identity('separator mass percentages sum to 100',a('gas_fracs')+a('oil_fracs')+a('water_fracs'),100,atol=1e-5)
        for key in ['gas_fracs','oil_fracs','water_fracs']: bounded(key,0,100,unit='mass %')
        identity('Souders-Brown velocity',a('max_velocities'),n['K_factor']*np.sqrt((a('oil_densities')-a('gas_densities'))/a('gas_densities')),unit='m/s')
        c.close('sampled oil-yield optimum',n['opt_y'],np.nanmax(n['oil_yields']),atol=1e-5,unit='kg/hr')
    elif chapter == 11:
        bounded('rvp_values',0,missing=True,unit='bara')
        identity('API gravity reference-density definition',a('api_gravities'),141.5/(a('oil_densities')/999.016)-131.5,atol=1e-7)
        bounded('gas_pct',0,100,unit='mol %'); bounded('cum_pct',0,100+1e-6,unit='mol %')
        identity('cumulative released gas',a('cum_pct'),np.cumsum(a('gas_pct')),atol=1e-6)
    elif chapter == 12:
        bounded('c2plus_in_gas',0,100); bounded('c3plus_in_gas',0,100)
        order('C3+ is a subset of C2+',a('c3plus_in_gas')<=a('c2plus_in_gas')+1e-10)
        bounded('jt_outlet_temps',-273.15,missing=True,unit='C',minimum=3)
    elif chapter == 13:
        for key in ['gas_flows','oil_flows','water_flows']: bounded(key,0,unit='kg/hr')
        identity('total liquid is oil plus aqueous product',a('total_liquid_flows'),a('oil_flows')+a('water_flows'),atol=1e-5)
    elif chapter == 14:
        identity('absolute compressor pressure ratio',a('compression_ratios'),a('outlet_pressures')/n['inlet_pressure'])
        bounded('powers_75',0,unit='MW'); bounded('powers_85',0,unit='MW')
        order('higher specified efficiency reduces fixed-duty power',a('powers_85')<=a('powers_75')+1e-5)
        bounded('max_discharge_temps',-273.15,unit='C')
        c.require('temperature-limit screening explicitly includes violating designs',np.any(a('max_discharge_temps')>150),float(max(n['max_discharge_temps'])),'at least one evaluated design exceeds stated 150 C limit','C',category='constraint_screening')
    elif chapter == 15:
        for i,sr in enumerate(n['speed_ratios']):
            identity('assumed map flow affinity',np.asarray(n['curves_flow'][i]),n['ref_flow']*sr*a('flow_fracs'),unit='m3/hr')
            identity('assumed map head affinity',np.asarray(n['curves_head'][i]),n['ref_head']*sr**2*a('head_fracs'),unit='kJ/kg')
        bounded('curves_eff',0,100,unit='%')
    elif chapter == 16:
        for key in ['dT1','dT2','LMTD']: bounded(key,0,unit='K')
        bounded('ua_effectiveness',0,1); bounded('effectiveness',0,1)
        c.require('LMTD lies between terminal driving forces',min(n['dT1'],n['dT2'])<=n['LMTD']<=max(n['dT1'],n['dT2']),n['LMTD'],'between terminal differences','K')
    elif chapter == 17:
        bounded('cv_values',0); bounded('effective_cv',0)
        c.close('fixed inlet/outlet state JT is independent of mass rate',np.ptp(a('outlet_temps')),0,atol=1e-5,unit='K')
        c.close('valve pressure-drop definition',n['dP'],n['P_in']-n['P_out'],atol=1e-8,unit='bar')
    elif chapter == 18:
        bounded('efficiencies',0,1)
        identity('fuel lower-heating-value energy balance',a('fuel_rate_kg_hr')*n['LHV_MJ_per_kg']/3600,a('heat_input_MW'),unit='MW')
        identity('annual CO2 conversion',n['co2_rate_tonnes_yr'],n['co2_rate_kg_hr']*8760/1000,unit='tonne/year')
        identity('reserve margin definition',n['reserve_margin'],100*(n['total_available']-n['total_demand'])/n['total_available'])
    elif chapter == 19:
        bounded('arrival_pressures',0,missing=True,unit='bara'); bounded('ghv',0,unit='MJ/Sm3'); bounded('wobbe_index',0,unit='MJ/Sm3')
        identity('ISO Wobbe and calorific value use the same real-gas relative density',n['wobbe_index'],n['ghv']/np.sqrt(n['relative_density']),atol=1e-7,unit='MJ/Sm3')
        identity('export diameter conversion',a('diameters_m'),a('diameters_inch')*.0254,unit='m')
    elif chapter == 20:
        bounded('utils',0,unit='%'); c.require('capacity sweep has at least three evaluations',n['n_points']>=3,n['n_points'],'>=3','points')
        for key,values in n['results'].items(): c.array('utilization '+key,values,0,unit='%')
        c.require('capacity sweep keeps chart disabled for fixed-pressure compressor',not n['compressor'].getCompressorChart().isUseCompressorChart(),False,'chart disabled; power constraint applies')
    elif chapter == 21:
        identity('utilization uses like-unit load/capacity per row',a('utilizations'),a('actual_loads')/a('design_capacities')*100,unit='%')
        bounded('design_capacities',0)
        for i,(capacity,utilization) in enumerate(zip(n['capacities_history'],n['util_history'])):
            identity('debottleneck step includes stated 5 percent load growth',np.asarray(utilization),
                     a('actual_loads')*1.05**i/np.asarray(capacity)*100,atol=1e-7,unit='%')
    elif chapter == 22:
        bounded('comp_powers',0,unit='kW'); bounded('export_rates',0,unit='kg/hr')
        c.close('two manual throughput searches agree within bracket resolution',n['gs_max_rate'],n['base_max'],atol=700,unit='kg/hr',category='search_verification')
        saved=float(n['feed'].getFlowRate('kg/hr'))
        c.require('reported base throughput is feasible',n['is_feasible'](n['base_max']),n['base_max'],'no enabled capacity overload','kg/hr',category='constraint_satisfaction')
        n['feed'].setFlowRate(saved,'kg/hr'); n['process'].run(); c.run(n['process'],'post-validation restored process')
    elif chapter == 23:
        bounded('opt_rate',20000,200000,unit='kg/hr')
        saved=float(n['feed'].getFlowRate('kg/hr')); n['feed'].setFlowRate(float(n['opt_rate']),'kg/hr'); n['process'].run()
        power=float(n['compressor'].getPower('kW')) if 'compressor' in n else float(n['comp'].getPower('kW'))
        c.require('optimizer replay satisfies 4750 kW bound',power<=4751,power,'<=4751 (1 kW numerical allowance)','kW',category='constraint_satisfaction')
        n['feed'].setFlowRate(saved,'kg/hr'); n['process'].run()
    elif chapter == 24:
        bounded('max_rate',10000,120000,unit='kg/hr'); bounded('opt_rates',10000,120000,unit='kg/hr')
        bounded('opt_utils',0,100.2,unit='%')
        c.require('manual throughput bracket meets resolution',n['high']-n['low']<=n['tol'],n['high']-n['low'],'<=configured flow tolerance','kg/hr',category='search_verification')
    elif chapter == 25:
        bounded('utilization_matrix',0); bounded('max_powers',0,unit='kW')
        bounded('comp1_util',0); bounded('comp2_util',0)
        c.require('heatmap covers both compressor ratings',a('utilization_matrix').shape[0]==len(n['max_powers']),a('utilization_matrix').shape[0],'one row per compressor','rows')
    elif chapter == 26:
        bounded('total_rates',0,unit='kg/hr'); bounded('rates_total',0,unit='kg/hr')
        c.monotonic('fixed inflow model loses rate with greater manifold pressure',n['total_rates'],-1,atol=.01,unit='kg/hr')
    elif chapter == 27:
        bounded('optimal_rates',0,unit='tonne/hr')
        bounded('optimal_utils',0,n['utilization_limit']*100+1e-8,unit='%')
        for label,result in n['results'].items():
            c.require('scenario '+label+' selected utilization feasible',result['optimal_utilization']<=n['utilization_limit']+1e-10,result['optimal_utilization'],'<=specified utilization',category='constraint_satisfaction')
    elif chapter == 28:
        bounded('BHP_grid',0,missing=True,unit='bara',minimum=3)
        c.close('inverse VFP arrival pressure residual',np.max(np.abs(a('arrival_errors'))),0,atol=.05,unit='bar',category='boundary_condition')
    elif chapter == 29:
        bounded('level',0,1); bounded('valve_pos',0,100,unit='%')
        rhs=(-n['K_process']*(a('valve_pos')[1:]-50)/100+a('feed_disturbance')[1:])/n['tau_process']
        expected=np.clip(a('level')[:-1]+n['dt']*rhs,0,1)
        identity('lumped controller discrete inventory equation',a('level')[1:],expected,atol=1e-12)
        c.require('initial equilibrium level',abs(n['level'][0]-n['level_setpoint'])<1e-12,n['level'][0],'setpoint before disturbance')
    elif chapter == 30:
        bounded('sim_vals'); bounded('measured_vals')
        c.require('normalization references are nonzero',np.all(a('sim_vals')!=0),float(np.min(np.abs(a('sim_vals')))),'nonzero per-variable denominators')
        identity('synthetic residual percentage definition',a('deviations'),100*(a('measured_vals')-a('sim_vals'))/a('sim_vals'),atol=1e-9,unit='%')
        identity('normalized comparison retains residuals',a('meas_norm')-a('sim_norm'),a('deviations'),atol=1e-9,unit='%')
    elif chapter == 31:
        for key in ['flow_errors','temp_errors','comp_errors']:
            bounded(key,0); c.require(key+' converged',n[key][-1]<1e-7,n[key][-1],'<1e-7',category='solver_residual')
        c.close('adjuster achieved temperature target',n['outlet_T'],40,atol=.05,unit='C',category='boundary_condition')
    elif chapter == 32:
        bounded('candidate_power',0,unit='kW'); bounded('candidate_production',0,unit='kg/hr'); bounded('candidate_eta',0,1)
        production,power=a('candidate_production'),a('candidate_power')
        for i in np.flatnonzero(n['is_pareto']):
            dominates=(production>=production[i])&(power<=power[i])&((production>production[i])|(power<power[i]))
            c.require('selected Pareto point is nondominated',not np.any(dominates),int(np.sum(dominates)),'zero dominating sampled candidates','points',category='search_verification')
    elif chapter == 33:
        bounded('water_content',0,1e6,unit='ppmv'); bounded('total_powers',0,unit='kW')
        # Solvent enters warmer than the gas. A monotonic water decrease is not
        # a thermodynamic requirement: sensible heat competes with absorption.
        wet_ppmv=float(n['inlet_separator'].getGasOutStream().getFluid().getPhase('gas').getComponent('water').getx())*1e6
        bounded('water_content',0,wet_ppmv,unit='ppmv')
        c.monotonic('fixed-feed two-stage power rises with export pressure',n['total_powers'],1,atol=.001,unit='kW')
        c.require('TEG energy reconstruction evidence retained',len(n['teg_energy_corrections'])==len(n['teg_rates'])+1,len(n['teg_energy_corrections']),'baseline plus every circulation point','cases',category='energy_balance')
        c.case_evidence={'teg_energy_reconstruction':n['teg_energy_corrections'],
                         'circulation_kg_hr':list(n['teg_rates']), 'water_ppmv':list(n['water_content'])}
    elif chapter == 34:
        identity('total compression shaft power',n['total_power_kW'],n['lp_power_kW']+n['export_power_kW'],unit='kW')
        identity('total separated aqueous flow',n['total_water'],n['water_hp']+n['water_mp']+n['water_lp'],unit='kg/hr')
        for key in ['gas_rate_kg_hr','oil_rate_kg_hr','total_water']: bounded(key,0,unit='kg/hr')
    elif chapter == 35:
        bounded('densities',0,unit='kg/m3'); bounded('z_factors',0); bounded('h2_fractions',0,1)
        bounded('wobbe_indices',0,unit='MJ/Sm3')
        c.monotonic('methane replacement by hydrogen lowers molar mass',n['molar_masses'],-1)
        # Mixture molar mass is affine in composition regardless of the EOS.
        h=a('h2_fractions'); m=a('molar_masses')
        identity('hydrogen blend molar mass is affine',m,m[0]+(m[-1]-m[0])*(h-h[0])/(h[-1]-h[0]),atol=1e-9)
    return True
