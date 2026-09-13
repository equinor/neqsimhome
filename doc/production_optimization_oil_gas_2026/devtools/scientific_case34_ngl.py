"""Reduced NGL pressure/capacity screen with explicit external refrigeration."""
def build_gas_plant(feed_rate_kghr):
    # Fresh fluid and equipment for every point.
    fluid=jneqsim.thermo.system.SystemSrkEos(303.15,70.0)
    recipe={'nitrogen':.004,'CO2':.030,'methane':.800,'ethane':.070,
            'propane':.040,'i-butane':.010,'n-butane':.015,
            'i-pentane':.008,'n-pentane':.006,'n-hexane':.008,
            'n-heptane':.005,'n-octane':.004}
    for name,fraction in recipe.items():fluid.addComponent(name,fraction)
    fluid.setMixingRule('classic')
    ps=ProcessSystem()
    def run_add(unit):ps.add(unit);unit.run();return unit
    feed=Stream('Plant Feed',fluid)
    feed.setFlowRate(feed_rate_kghr,'kg/hr');run_add(feed)
    inlet_sep=run_add(Separator('Inlet Separator',feed))
    precooler=Cooler('External Refrigeration',inlet_sep.getGasOutStream())
    precooler.setOutTemperature(243.15);run_add(precooler)
    pre_ko=run_add(Separator('Expander Inlet KO',precooler.getOutletStream()))
    expander=jneqsim.process.equipment.expander.Expander('Turboexpander',pre_ko.getGasOutStream())
    expander.setIsentropicEfficiency(.85);expander.setOutletPressure(22.0);run_add(expander)
    cold_sep=run_add(Separator('Cold Separator',expander.getOutletStream()))
    recomp=Compressor('First Residue Stage',cold_sep.getGasOutStream())
    recomp.setUsePolytropicCalc(True);recomp.setPolytropicEfficiency(.78)
    recomp.setOutletPressure(35.0,'bara');run_add(recomp)
    residue_comp=Compressor('Residue Compressor',recomp.getOutletStream())
    residue_comp.setUsePolytropicCalc(True);residue_comp.setPolytropicEfficiency(.78)
    residue_comp.setOutletPressure(70.0,'bara');run_add(residue_comp)
    ps.run()
    liquids=[inlet_sep.getLiquidOutStream(),pre_ko.getLiquidOutStream(),cold_sep.getLiquidOutStream()]
    products=liquids+[residue_comp.getOutletStream()]
    for stream in products+[feed]:stream.getFluid().initProperties()
    duties=[float(precooler.getDuty()),float(expander.getPower()),
            float(recomp.getPower()),float(residue_comp.getPower())]
    checks=process_boundary_check(feed,products,duties)
    assert expander.getPower()<0 and recomp.getPower()>0 and residue_comp.getPower()>0
    assert pre_ko.getGasOutStream().getFluid().getNumberOfPhases()==1
    assert cold_sep.getGasOutStream().getFluid().getNumberOfPhases()==1
    row=dict(feed_kghr=feed_rate_kghr,
             feed_MSm3day=float(feed.getFlowRate('MSm3/day')),
             inlet_gas_MSm3day=float(inlet_sep.getGasOutStream().getFlowRate('MSm3/day')),
             expander_MW=-float(expander.getPower())/1e6,
             residue_comp_MW=float(residue_comp.getPower())/1e6,
             first_residue_stage_MW=float(recomp.getPower())/1e6,
             refrigeration_MW=-float(precooler.getDuty())/1e6,
             liquid_kghr=sum(float(s.getFlowRate('kg/hr')) for s in liquids),
             checks=checks)
    return ps,row

# Explicit mass-throughput basis; no universal MMscfd/kg conversion is assumed.
design_rate=290000.0
plant_design,ngl_base=build_gas_plant(design_rate)
plant_new,ngl_increased=build_gas_plant(1.2*design_rate)
ngl_limits={'inlet_gas_MSm3day':10.5,'expander_MW':4.5,'residue_comp_MW':18.0}
for row in [ngl_base,ngl_increased]:
    row['screen_utilization']={k:row[k]/v for k,v in ngl_limits.items()}
    row['screen_feasible']=all(v<=1 for v in row['screen_utilization'].values())
Path('ch34_ngl_base_increased.json').write_text(json.dumps([ngl_base,ngl_increased],indent=2))
print(json.dumps([ngl_base,ngl_increased],indent=2))
