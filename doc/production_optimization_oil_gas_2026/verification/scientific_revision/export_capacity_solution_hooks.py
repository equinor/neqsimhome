"""Supplementary checks on exact published chapter19/20/22 Python.

No input mutation. Observed loop/function state is checked before it is lost.
"""
import math
import numpy as np

TARGET_FENCES={19:list(range(1,9)),20:list(range(1,12)),22:list(range(1,10))}
ROWS={};FAILURES={};SEEN={};LINES={};RETURNS={}

def result(name,observed,tolerance=None,scope=None):
    return dict(name=name,passed=True,observed=observed,tolerance=tolerance,scope=scope)

def state(stream):
    f=stream.getFluid();f.initProperties()
    m=float(stream.getFlowRate('kg/sec')); T=float(stream.getTemperature('K')); P=float(stream.getPressure('bara'))
    assert math.isfinite(m) and m>=0 and math.isfinite(T) and T>0 and math.isfinite(P) and P>0,(m,T,P)
    M=float(f.getMolarMass()); mol=m/M
    components={str(f.getComponent(i).getComponentName()):mol*float(f.getComponent(i).getz()) for i in range(f.getNumberOfComponents())}
    assert abs(sum(components.values())-mol)<max(1e-9,abs(mol)*1e-9)
    return {'m':m,'h':m*float(f.getEnthalpy('J/kg')),'T':T,'P':P,'c':components,'phases':f.getNumberOfPhases()}

def balance(inlets,outlets,label,QW=None,tol=1e-6):
    ins=[state(s) for s in inlets];outs=[state(s) for s in outlets]
    mass=sum(s['m'] for s in ins);mr=abs(sum(s['m'] for s in outs)-mass)/max(mass,1e-9)
    names=set().union(*(set(s['c']) for s in ins+outs));scale=sum(sum(s['c'].values()) for s in ins)
    cr=max(abs(sum(s['c'].get(n,0) for s in outs)-sum(s['c'].get(n,0) for s in ins)) for n in names)/max(scale,1e-9)
    assert mr<1e-7 and cr<1e-7,(label,'mass/component',mr,cr)
    obs={'mass_relative':mr,'component_relative':cr,'inlet_kg_s':mass}
    if QW is not None:
        hin=sum(s['h'] for s in ins);hout=sum(s['h'] for s in outs)
        er=abs(hout-hin-QW)/max(abs(hin),abs(hout),abs(QW),1)
        assert er<tol,(label,'energy',er,hin,hout,QW)
        obs.update(energy_relative=er,heat_plus_work_W=QW)
    return result(label,obs,{'mass':1e-7,'components':1e-7,'energy':tol if QW is not None else None},'Steady boundary quantities; pipeline thermal duty is not inferred if unspecified.')

def compressor_check(comp,label):
    inlet=comp.getInletStream();out=comp.getOutletStream();a=state(inlet);b=state(out);W=float(comp.getPower())
    assert W>0 and b['P']>a['P'] and b['T']>a['T'] and a['phases']==1,(label,W,a,b)
    assert bool(comp.usePolytropicCalc),label+' must use the specified polytropic efficiency'
    r=balance([inlet],[out],label,W)
    r['observed'].update(power_W=W,pressure_ratio=b['P']/a['P'],temperature_rise_K=b['T']-a['T'],single_phase_inlet=True)
    return r

def separator_check(sep,label):
    return balance(list(sep.getInletStreams()),list(sep.getOutletStreams()),label,0.)

def pipeline_check(pipe,label):
    inlet=pipe.getInletStream();out=pipe.getOutletStream();p0=float(inlet.getPressure('bara'));p=float(out.getPressure('bara'))
    assert 0<p<p0,(label,p0,p)
    r=balance([inlet],[out],label)
    r['observed'].update(inlet_bara=p0,outlet_bara=p,pressure_loss_bar=p0-p)
    return r

def iso_check(ns,label):
    obj=ns['iso6976'];g=float(obj.getValue('SuperiorCalorificValue'))/1000;n=float(obj.getValue('InferiorCalorificValue'))/1000
    w=float(obj.getValue('SuperiorWobbeIndex'))/1000;d=float(obj.getValue('RelativeDensity'));M=float(obj.getValue('MolarMass'))
    assert all(math.isfinite(v) and v>0 for v in (g,n,w,d,M)) and g>n
    err=abs(w-g/math.sqrt(d));assert err<1e-10,(g,w,d,err)
    # Independent compositional molar-mass calculation, allowing ISO database rounding.
    f=ns['gas']; mm=sum(float(f.getComponent(i).getz())*float(f.getComponent(i).getMolarMass())*1000 for i in range(f.getNumberOfComponents()))
    assert abs(M-mm)<.02,(M,mm)
    return result(label,{'GCV_MJ_Sm3':g,'NCV_MJ_Sm3':n,'Wobbe_MJ_Sm3':w,'relative_density':d,'molar_mass_g_mol':M,'Wobbe_identity_error':err,'composition_molar_mass_g_mol':mm}, {'Wobbe_absolute':1e-10,'molar_mass_g_mol':.02},'Declared 15 C volume/25 C combustion reference; algebra/units, not custody-transfer certification.')

def before_fence(ch,fence,ns,code):
    key=(ch,fence);ROWS[key]=[];FAILURES[key]=[];SEEN[key]=set();LINES[key]=code.splitlines();RETURNS[key]=[]

def on_trace(ch,fence,frame,event,arg):
    key=(ch,fence);loc=frame.f_locals
    try:
        if ch==19 and fence==2 and event=='line' and 'print(f"{c2_frac*100' in LINES[key][frame.f_lineno-1]:
            z=loc['c2_frac']
            if z not in SEEN[key]:ROWS[key].append(iso_check(loc,f'C2+ fraction {z}'));SEEN[key].add(z)
        if ch==19 and fence==6 and event=='line' and 'diameter_results.append' in LINES[key][frame.f_lineno-1]:
            d=loc['d_inch']
            if d not in SEEN[key]:
                if loc['feasible']:ROWS[key].append(pipeline_check(loc['pipe'],f'Diameter {d} inch'))
                else:ROWS[key].append(result(f'Diameter {d} rejected pressure domain',{'outlet_bara':float(loc['P_out']),'accepted':False},scope='Invalid pressure solution retained and excluded; not claimed as a feasible pipeline.'))
                SEEN[key].add(d)
        if ch==20 and fence in (8,9) and event=='line' and ('results.append({' in LINES[key][frame.f_lineno-1]):
            v=loc['factor'] if fence==8 else loc['wc']
            if v not in SEEN[key]:
                ROWS[key]+=[separator_check(loc['sep'],f'Input {v} separator'),compressor_check(loc['comp'],f'Input {v} compressor')];SEEN[key].add(v)
        if ch==22 and event=='return' and frame.f_code.co_name in ('simulate_two_stage_separation','compressor_power','two_stage_power','facility_model','platform_production'):
            name=frame.f_code.co_name
            if arg is None:return
            RETURNS[key].append({'function':name,'value':arg,'P1':loc.get('P1'),'P2':loc.get('P2'),'P_suction':loc.get('P_suction'),'P_inter':loc.get('P_inter')})
            if name=='simulate_two_stage_separation':
                tag=f"Separation {loc['P1']}/{loc['P2']} bara"
                for var in ['hp_sep','lp_sep','st_sep']:ROWS[key].append(separator_check(loc[var],tag+' '+var))
                ROWS[key].append(balance([loc['feed']],loc['outlets'],tag+' whole boundary',0.))
            elif name=='two_stage_power':
                ROWS[key]+=[compressor_check(loc['comp1'],'Stage1'),compressor_check(loc['comp2'],'Stage2'),balance([loc['feed']],[loc['comp2'].getOutletStream()],'Two-stage whole boundary',float(loc['comp1'].getPower()+loc['comp2'].getPower()+loc['cooler'].getDuty()))]
            else:
                comp=loc['comp']; ROWS[key].append(compressor_check(comp,name+' compressor'))
                if 'sep' in loc:
                    ROWS[key].append(separator_check(loc['sep'],name+' separator'))
                    ROWS[key].append(balance([loc['feed']],[comp.getOutletStream(),loc['sep'].getOilOutStream(),loc['sep'].getWaterOutStream()],name+' whole boundary',float(comp.getPower())))
        if ch==22 and fence==7 and event=='line' and 'pareto_points.append({' in LINES[key][frame.f_lineno-1]:
            v=loc['P_sep']
            if v not in SEEN[key]:
                ROWS[key]+=[separator_check(loc['sep'],f'Pareto pressure {v} separator'),compressor_check(loc['comp'],f'Pareto pressure {v} compressor')];SEEN[key].add(v)
        if ch==22 and fence==1 and event=='return' and frame.f_code.co_name=='well_outlet' and arg is not None:
            if math.isfinite(arg) and arg>0:
                ROWS[key].append(pipeline_check(loc['wellbore'],'Forward upward tubing trial'))
            else:
                SEEN[key].add(('rejected_trial',float(loc['P_bh']),float(loc['Q_MSm3_day'])))
    except BaseException as exc:
        FAILURES[key].append(str(exc))
        raise

def after_fence(ch,fence,ns,code):
    key=(ch,fence);assert not FAILURES[key],FAILURES[key]
    rows=ROWS[key]
    if ch==19:
        if fence in (1,8):rows.append(iso_check(ns,'Export gas quality'))
        elif fence==2:
            assert len(rows)==7
            g=[r['observed']['GCV_MJ_Sm3'] for r in rows]
            assert np.all(np.diff(g)>0)
            rows.append(result('Declared enrichment increases volumetric GCV',g))
        elif fence==3:
            vals=ns['water_dew_results'];assert len(vals)==8
            assert all(v['aqueous_below_above']==[True,False] and -93.15<v['water_dew_C']<46.85 for v in vals)
            rows.append(result('Eight water VLE onset states bracketed by independent TP flashes',vals,.2,'Metastable aqueous VLE below freezing; ice and hydrates excluded.'))
        elif fence==4:
            t=np.array(ns['dew_temps']);p=np.array(ns['dew_press']);assert len(t)==len(p)>20 and np.isfinite(t).all() and np.isfinite(p).all() and min(t)>0 and min(p)>0
            assert abs(max(t)-ns['max_T_K'])<1e-10
            rows.append(result('Finite positive envelope and sampled maximum',{'points':len(t),'maximum_C':float(max(t)-273.15),'pressure_at_max_bara':float(p[np.argmax(t)])},1e-10,'Same literal composition also has a separately retained four-envelope boundary-probe report; no critical point inferred.'))
        elif fence==5:rows.append(pipeline_check(ns['pipeline'],'200 km export pipeline'))
        elif fence==6:
            vals=ns['diameter_results'];assert len(vals)==len(rows)==7 and any(v['physical_pressure_domain'] for v in vals)
            valid=[v for v in vals if v['physical_pressure_domain']];assert np.all(np.diff([v['outlet_bara'] for v in valid])>0)
            rows.append(result('Diameter sweep domain ledger',vals,scope='Positive-pressure accepted cases only; monotonic loss reduction checked within valid branch.'))
        elif fence==7:
            rows+=[compressor_check(ns['compressor'],'Export compressor'),balance([ns['comp_out']],[ns['cool_out']],'Export cooler',float(ns['cooler'].getDuty())),pipeline_check(ns['pipeline'],'250 km export pipeline')]
        if fence==8:
            assert ns['gcv_status']==('PASS' if ns['gcv_min']<=ns['gcv']<=ns['gcv_max'] else 'FAIL')
            assert ns['wi_status']==('PASS' if ns['wi_min']<=ns['wobbe']<=ns['wi_max'] else 'FAIL')
            rows.append(result('Declared quality-screen predicates match their numbers',{'GCV':ns['gcv_status'],'Wobbe':ns['wi_status'],'CO2':ns['co2_status']},scope='Illustrative thresholds, not verified current contractual limits.'))
        return rows
    if ch==20:
        if fence==1:
            rows.append(separator_check(ns['separator'],'Three-phase separation'))
            assert ns['rho_oil']>ns['rho_gas']>0 and ns['rho_water']>0 and ns['Q_liq_total']>0
            volume=math.pi*ns['D_sep']**2/4*ns['L_sep']*.5
            assert abs(ns['V_liquid']-volume)<1e-12
            assert abs(ns['t_ret_actual']*ns['Q_liq_total']-volume)<1e-10
            assert abs(ns['U_gas']-ns['v_gas_actual']/ns['v_gas_max'])<1e-12
            assert ns['U_sep']==max(ns['U_gas'],ns['U_liq'])
            rows.append(result('Half-full circular geometry, retention and gas-load identities',{'gas_utilization':ns['U_gas'],'liquid_utilization':ns['U_liq'],'retention_s':ns['t_ret_actual'],'liquid_volume_m3':volume},1e-10,'Exactly half-diameter level makes half-area exact; fixed K-factor and retention target are declared assumptions.'))
        elif fence==2:
            rows.append(compressor_check(ns['compressor'],'Compressor duty'))
            assert abs(ns['W_driver_derated']-14.1)<1e-10 and abs(ns['U_power']-ns['power_actual']/14.1)<1e-12
            assert abs(ns['SM']-100*(ns['Q_actual']-ns['Q_surge'])/ns['Q_actual'])<1e-12
            rows.append(result('Declared driver derating and flow-margin arithmetic',{'derated_driver_MW':ns['W_driver_derated'],'power_utilization':ns['U_power'],'assumed_surge_margin_pct':ns['SM']},1e-10,'The assumed surge fraction is not an installed compressor map; discharge-temperature acceptability remains a separate constraint.'))
        elif fence==3:
            hx=ns['hx'];rows.append(balance([ns['hot_stream'],ns['cold_stream']],[hx.getOutStream(0),hx.getOutStream(1)],'Two-stream exchanger boundary',0.))
            assert len(ns['hx_checks'])==2 and ns['hx_checks'][1]['duty_kW']<ns['hx_checks'][0]['duty_kW']
            rows.append(result('Clean/fouled duty, thermal approach and energy checks',ns['hx_checks'],1e-5,'Two-stream UA model, positive terminal approaches; no arbitrary driving-temperature assumption.'))
        elif fence==4:
            valve=ns['valve'];rows.append(balance([ns['feed']],[valve.getOutletStream()],'Throttling valve isenthalpic balance',0.))
            assert 0<ns['ratio']<1 and abs(ns['ratio']-25/65)<1e-12
            rows.append(result('Valve pressure boundary and ratio',{'ratio':ns['ratio'],'pressure_out_bara':ns['P_out']},1e-12,'A 0.55 heuristic flag is not a Cv/xT valve-capacity or choking calculation.'))
        elif fence==5:
            rows.append(pipeline_check(ns['pipe'],'Multiphase pipeline'))
            independent=150*0.3048/math.sqrt(ns['rho_mix']/16.01846337)
            assert abs(independent-ns['v_eros'])<1e-10
            assert abs(ns['U_dP']-ns['dP']/(80-40))<1e-12
            rows.append(result('Unit-converted screening velocities and pressure budget',{'mixture_velocity_m_s':ns['v_actual'],'screening_velocity_m_s':independent,'velocity_utilization':ns['U_vel'],'pressure_utilization':ns['U_dP'],'MAOP_utilization':ns['U_MAOP']},1e-10,'Specified erosional constant and pressure limits; a screening calculation, not erosion prediction.'))
        elif fence==6:
            rows += [separator_check(ns['hp_sep'],'Facility HP separator'),compressor_check(ns['compressor'],'Facility compressor'),balance([ns['compressor'].getOutletStream()],[ns['cooler'].getOutletStream()],'Facility cooler',float(ns['cooler'].getDuty())),pipeline_check(ns['pipeline'],'80 km facility pipeline')]
        elif fence==7:
            vals=ns['utilization_report'];assert len(vals)==4 and all(math.isfinite(v['utilization']) and v['utilization']>=0 for v in vals)
            assert all(abs(v['spare_capacity']-(1-v['utilization']))<1e-12 for v in vals)
            assert ns['bottleneck']==max(vals,key=lambda r:r['utilization'])
            assert abs(ns['max_production']*ns['bottleneck']['utilization']-350000)<1e-6
            rows.append(result('Utilization arithmetic and explicit extrapolation scope',vals,1e-6,'The cooler approach ratio is a feasibility indicator. Current-rate division is a linear screening extrapolation, not a solved throughput limit.'))
        elif fence==8:
            assert len(rows)==18 and len(ns['results'])==9
            vals=ns['results'];ref=next(r for r in vals if r['factor']==1.)
            errors=[abs(r[k]/r['factor']-ref[k]) for r in vals for k in ('U_separator','U_compressor')]
            assert max(errors)<1e-7
            rows.append(result('Fixed-composition rate sweep scaling',{'cases':9,'maximum_normalized_utilization_error':max(errors)},1e-7,'Linear proportionality is justified only for this fixed T/P/composition separation/compression boundary.'))
        elif fence==9:
            assert len(rows)==16 and len(ns['water_cut_results'])==8
            vals=ns['water_cut_results'];assert np.all(np.diff([v['gas_kg_hr'] for v in vals])<0)
            assert all(abs(v['liquid_screen_utilization_pct']-v['first_separator_liquid_m3_hr']/4)<1e-10 for v in vals)
            rows.append(result('Executed volume-reference water-cut sweep',vals,1e-10,'Fixed reference liquid, specified associated-gas/oil ratio, three named compounds; no prescribed field trend.'))
        elif fence==10:
            assert abs(ns['fluid'].getPressure('bara')-ns['P_relief'])<1e-10
            assert ns['rho_gas_relief']>0 and ns['MW_gas']>0 and ns['Z_relief']>0 and ns['k']>1
            k=ns['gamma_ideal']; R=ns['R_specific']; T0=ns['T_relief']; P0=ns['P_stagnation_Pa']; A=ns['A_required']
            Tstar=T0*2/(k+1);Pstar=P0*(2/(k+1))**(k/(k-1));rho=Pstar/(R*Tstar);a=math.sqrt(k*R*Tstar)
            mass=rho*a*A;expected=ns['W_relief']/3600.;error=abs(mass/expected-1)
            assert error<1e-12 and A>0
            rows.append(result('Independent sonic-state continuity reproduces SI ideal nozzle area',{'ideal_area_m2':A,'mass_rate_kg_s':mass,'sonic_pressure_Pa':Pstar,'sonic_temperature_K':Tstar,'relative_mass_error':error,'real_fluid_Z':ns['Z_relief'],'relieving_pressure_bara':ns['P_relief']},1e-12,'Independent rho_star*a_star*A calculation using calorically perfect ideal gas; deliberately not an API PSV or real-gas rating.'))
        elif fence==11:
            assert not ns['coverage'].isComplete() and any('MISSING_EQUIPMENT' in s for s in ns['diagnostics'])
            rows.append(result('Missing equipment prevents a complete capacity coverage claim',ns['diagnostics'],scope='Software coverage behavior only.'))
        return rows
    if ch==22:
        samples=RETURNS[key]
        if fence==1:
            q=ns['operating_rate_MSm3_day'];bh=ns['operating_BHP_bara'];wh=ns['operating_WHP_bara']
            assert 0<q<5 and ns['P_wh_target']<bh<ns['P_res'] and abs(wh-ns['P_wh_target'])<.002
            err=abs(ns['C_ipr']*(ns['P_res']**2-bh**2)**ns['n_ipr']-q);assert err<1e-8
            valid=[p for p in ns['P_wf_tpr'] if p is not None];assert len(valid)>2 and np.all(np.diff(valid)>0)
            lower=ns['well_outlet'](ns['ipr_bottomhole'](q*.9999),q*.9999)
            upper=ns['well_outlet'](ns['ipr_bottomhole'](q*1.0001),q*1.0001)
            assert lower>ns['P_wh_target']>upper
            rows.append(result('Coupled IPR/forward-pipe root and accepted TPR ordering',{'rate_MSm3_day':q,'BHP_bara':bh,'WHP_bara':wh,'IPR_rate_residual':err,'bracketing_WHP_bara':[lower,upper],'TPR_required_BHP_bara':ns['P_wf_tpr'],'rejected_pressure_trials':len(SEEN[key]),'rejected_solver_diagnostics':ns['well_trial_failures']},{'WHP_bar':.002,'IPR_rate_MSm3_day':1e-8},'3000 m positive elevation in the physical flow direction; invalid trial pressures are excluded, not reported as required BHP.'))
        elif fence in (2,3):
            assert len(samples)==(11 if fence==2 else 36),(fence,len(samples))
            peak=max(samples,key=lambda s:s['value'])
            reported=ns['best_oil'] if fence==2 else ns['best_result']['oil']
            assert abs(peak['value']-reported)<1e-8
            rows.append(result('All specified separation cases checked; sampled maximum reconciled',{'cases':len(samples),'max_oil_kg_hr':peak['value'],'P1_bara':peak['P1'],'P2_bara':peak['P2']},1e-8,'Grid optimum only, with each separator and whole material/energy boundary checked; no extrapolated continuous optimum.'))
        elif fence==4:
            assert abs(sum(ns['rates'].values())-ns['budget'])<.1
            assert ns['replayed_oil']>=ns['grid_best']-1e-5 and ns['replayed_oil']-ns['grid_best']<1
            assert max(ns['slopes'])-min(ns['slopes'])<1e-7
            rows.append(result('Native gas-lift allocation satisfies concave KKT and independent exhaustive grid certificate',{'lift_rates_Sm3_day':ns['rates'],'total_oil_Sm3_day':ns['replayed_oil'],'grid_best_Sm3_day':ns['grid_best'],'marginal_spread':max(ns['slopes'])-min(ns['slopes'])},{'budget_Sm3_day':.1,'KKT':1e-7,'grid_gap_Sm3_day':1},'Declared separable lift curves, no calibrated well physics claim.'))
        elif fence==5:
            assert len(samples)==9
            vals=[s['value'] for s in samples];assert np.all(np.diff(vals)<0)
            rows.append(result('Every fixed-flow suction-pressure case verified',{'cases':9,'power_MW':vals},scope='Increasing suction pressure reduces duty for the specified gas, flow and fixed discharge; no production uplift inferred.'))
        elif fence==6:
            assert len(samples)==12
            assert all(abs(s['value'][0]-s['value'][1]-s['value'][2])<1e-10 for s in samples)
            best=min(samples,key=lambda s:s['value'][0]);assert abs(best['value'][0]-ns['best_W'])<1e-10 and best['P_inter']==ns['best_P']
            rows.append(result('Two-stage component balances and sampled power minimum',{'cases':12,'best_interstage_bara':ns['best_P'],'best_power_MW':ns['best_W'],'geometric_mean_reference_bara':ns['P_inter_opt_theory'],'sampled_results':samples},1e-10,'Unequal efficiencies/intercooling and real-fluid properties mean the ideal geometric mean is only a reference.'))
        elif fence==7:
            vals=ns['pareto_points'];assert len(vals)==11
            front=[p for p in vals if not any(other['oil_rate']>=p['oil_rate'] and other['power']<=p['power'] and (other['oil_rate']>p['oil_rate'] or other['power']<p['power']) for other in vals)]
            assert ns['pareto_front']==front
            rows.append(result('Exhaustive sampled dominance check',{'sample_count':11,'nondominated_count':len(front),'nondominated_points':front,'all_points':vals},scope='Separator liquid mass, not stock-tank oil; all points need not form a trade-off frontier.'))
        elif fence==8:
            assert len(samples)==1;out=ns['output'];mass=out['gas_export_kghr']+out['oil_rate_kghr']+out['water_rate_kghr']
            assert abs(mass/ns['wc'][0]['flow_kghr']-1)<1e-7 and abs(out['export_pressure_bara']-120)<1e-8
            rows.append(result('Single-well facility API outputs reconcile to executed boundary',out,1e-7,'Exactly one input well is handled in this reduced coupling example.'))
        elif fence==9:
            assert len(samples)==11
            vals=[s['value'] for s in samples];assert all(v['power_ok']==(v['power_MW']<=40) for v in vals)
            eligible=[v for v in vals if v['power_ok']];best=max(eligible,key=lambda v:v['oil_kghr']);assert best==ns['best']
            assert all(abs((v['oil_kghr']+v['gas_kghr']+v['water_kghr'])/400000-1)<1e-7 for v in vals)
            rows.append(result('Constrained sampled maximum and all phase products reconcile',{'cases':11,'best':best},1e-7,'One declared 40 MW power screen; no comprehensive installed capacity rating or stock-tank reference.'))
        return rows
    raise NotImplementedError((ch,fence))
