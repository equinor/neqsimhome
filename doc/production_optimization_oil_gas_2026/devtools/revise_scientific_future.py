"""Energy, emissions, thermodynamics and research-capability scientific corrections."""
import re,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];p=next((B/'chapters').glob('ch35*/chapter.md'))
t=p.read_text(encoding='utf-8-sig');backup=B/'.build/backups/scientific_revision'/p.parent.name/'future_input.md';backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():backup.write_text(t,encoding='utf-8')
changes=[];missed=[]
markers=re.findall(r'<!-- reviewed-notebook-results:start -->.*?<!-- reviewed-notebook-results:end -->',t,re.S)
for i,m in enumerate(markers):t=t.replace(m,f'PROTECTED_RESULTS_{i}')
def r(a,b):
 global t
 if a not in t:missed.append(a[:120]);return
 t=t.replace(a,b);changes.append({'before':a,'after':b})
def sub(a,b):
 global t
 t2,n=re.subn(a,lambda m:b,t,flags=re.S)
 if not n:missed.append(a[:120]);return
 changes.append({'pattern':a,'after':b});t=t2
def get(n):return list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',t,re.M|re.S))[n-1][3]
def fence(n,c):
 global t
 m=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',t,re.M|re.S))[n-1]
 t=t[:m.start(3)]+c.rstrip()+'\n'+t[m.end(3):]
 changes.append({'fence':n,'scope':'physical checks and corrected calculation basis'})
r('two primary routes for hydrogen production from natural gas — blue hydrogen (SMR/ATR with CCS) and green hydrogen (electrolysis powered by renewables)', 'two hydrogen pathways — natural-gas reforming with CCS, and water electrolysis powered by renewable electricity')
r('Traditional production optimization minimizes a single objective — often maximizing', 'A conventional production optimization may maximize a scalar objective such as')
r('where $w_i$ are weighting factors reflecting corporate strategy and regulatory requirements,', 'Use a common currency, valuation date and discounted time basis for every cost/revenue term; exclude energy and carbon costs from the production NPV term if they are subtracted separately. Here $w_i$ are explicitly declared preference factors,')
sub(r'\| Carbon Price .*?\*Table 35\.1:.*?\*', 'A carbon price changes economics through the emissions difference between alternatives. There is no universal price at which electrification, CCS or hydrogen becomes profitable: utility price, plant scale, load factor, capture boundary, transport/storage costs and financing all matter. Use a discounted cash-flow comparison with explicit uncertainty, rather than the former unsupported technology-threshold table.')
r('The major sources of CO$_2$ emissions from oil and gas production are:', 'Major greenhouse-gas sources include combustion CO₂, methane releases and separated reservoir CO₂. Report chemical species and conversion to CO₂-equivalent separately:')
r('Redesign processes to avoid emissions (e.g., replace gas turbines with electric motors)', 'Avoid on-site combustion where appropriate; include the electricity supply’s emissions in a consistent system boundary')
r('Compression is the largest energy consumer on most production platforms, accounting for 60–80% of total power demand.', 'Compression can dominate platform shaft-power demand, but its share must be calculated for the defined plant and operating state.')
r('typically 2.75 kg CO$_2$/kg natural gas for methane', 'approximately 2.744 kg CO$_2$/kg pure methane for complete combustion; calculate the actual mixture carbon content')
sub(r'\Delta \\dot\{m\}_\{\\text\{CO\}_2\} =.*?\n\$\$', r'''\Delta \dot m_{\mathrm{CO_2}}=
\dot m_{\mathrm{CO_2,GT}}-
\frac{W_{\mathrm{shaft}}}{\eta_{\mathrm{motor}}\eta_{\mathrm{delivery}}}
\,EF_{\mathrm{electricity}}
$$''')
r('For Norwegian power-from-shore (essentially zero-carbon hydroelectric grid), the reduction is nearly 100% of turbine emissions.', 'Here the electricity factor must use units consistent with electrical power (for example kg CO₂e/kWh with kW gives kg CO₂e/hr). Include motor and delivery losses, the stated grid factor and allocation method; low-carbon supply can greatly reduce emissions but is not automatically zero-carbon. On-site Scope 1 reduction and full-system reduction are different quantities.')
r('Global flaring burned approximately 140 billion cubic meters of gas in 2023, equivalent to 270 million tonnes of CO$_2$ emissions.', 'The World Bank reports 148 billion m³ flared in 2023 and approximately 381 million tonnes CO₂-equivalent including unburned methane. Its June 2026 data release reports 167 billion m³ for 2025. Keep the year and CO₂-versus-CO₂e basis attached to each number \\cite{worldbankflaring2024,worldbankflaring2026}.')
r('NeqSim can model the flare header system and predict when the gas handling system will be overwhelmed:', 'The following steady-state example imposes an 80/20 compressor/flare split and checks the diverted mass and complete-combustion carbon accounting with the native `Flare` class. It is not a calculated transient surge, header hydraulic limit or radiation/dispersion assessment:')
r('Methane pyrolysis is particularly attractive as it produces solid carbon (no CO$_2$):', 'Methane pyrolysis produces solid carbon rather than CO₂ in the reaction itself. Lifecycle emissions still depend on energy supply, methane leakage and the fate of the solid carbon:')
r('Electrification of compression using renewable power can reduce platform CO$_2$ emissions by 50–80%.', 'Calculate the emissions change from time-resolved power dispatch, efficiency and energy-source emission factors; no universal reduction percentage is implied.')
r('gas sweetening process described in Chapter 22','gas sweetening process described in Chapter 33')
r('The energy penalty for CO$_2$ capture is significant — typically 15–25% of the gas turbine power output is consumed by the capture plant\'s reboiler duty and compression.', 'Capture requires both heat and electrical/shaft work. A reboiler duty is thermal energy, so it cannot simply be deducted from turbine electrical output; model steam extraction, waste-heat recovery, heat pumps or other utility conversion explicitly.')
r('The CO$_2$ is compressed to supercritical conditions (typically >80 bara) for pipeline transport in dense phase.', 'Dense transport can be liquid-like below the critical temperature or supercritical above it. Pressure above 80 bara alone does not establish a supercritical or qualified single-phase state, especially for mixtures.')
r('31.1°C and 73.8 bar','approximately 30.98°C and 73.77 bara \\cite{nistco2properties}')
r('The CO$_2$ is miscible with crude oil above a minimum miscibility pressure (MMP),', 'For a specified oil, injection composition, temperature and multicontact displacement process, a minimum miscibility pressure (MMP) may be established; above it, multicontact miscibility can develop,')
r('or, more accurately, from slim-tube simulations using equation of state calculations.', 'or from a calibrated multicontact/slim-tube calculation compared with independent displacement data. Greater model detail alone does not ensure greater accuracy.')
r('ATR produces a higher-concentration CO$_2$ stream than SMR, making CCS more efficient.', 'The displayed partial-oxidation reaction is one contribution to ATR, which combines oxidation, reforming and shift chemistry. Oxygen-blown ATR places much of the carbon in a pressurized syngas stream; capture performance depends on the full flowsheet and capture boundary, including furnace emissions for SMR.')
r('where $W_{\\text{CCS}}$ is the energy consumed by the CCS system (compression, capture). Typical values are 60–70% for SMR+CCS and 65–75% for ATR+CCS.', 'All denominator terms must be powers on the same energy basis. Include total methane feed **and fuel**, externally supplied heat, oxygen production, compression and auxiliary electricity without double counting. Report LHV versus HHV explicitly. The abbreviated formula is a boundary definition, not an efficiency prediction; lifecycle emissions also include uncaptured carbon and upstream methane.')
r('### 35.4.2 Blue Hydrogen Model in NeqSim','### 35.4.2 Syngas Conditioning Submodel')
r('The following example demonstrates a simplified blue hydrogen production model using NeqSim\'s thermodynamic capabilities:', 'The following model conditions a prescribed wet syngas and compresses it. It does not simulate reforming, shift, CO₂ capture or hydrogen purification. The total stream rate is therefore a mixed-syngas rate, not a hydrogen product rate. Native reactor classes such as `CatalyticTubeReformer` and `AutothermalReformer` provide separate reaction-model capabilities requiring their own feed, heat/oxygen and reaction acceptance checks \\cite{neqsim2026update}.')
r(r'2\text{H}_2\text{O} \rightarrow 2\text{H}_2 + \text{O}_2 \quad \Delta H = +286 \text{ kJ/mol}',r'\text{H}_2\text{O}_{(l)} \rightarrow \text{H}_2 + \tfrac12\text{O}_2 \quad \Delta H_{298}^{\circ}\approx+285.83\ \text{kJ/mol H}_2')
sub(r'\| Technology \| Operating Temp.*?\*Table 35\.3:.*?\*', 'Alkaline, proton-exchange-membrane and solid-oxide electrolyzers have different temperature, materials and heat-supply requirements. Compare efficiency only at a shared HHV/LHV and stack/system boundary. High-temperature electrolysis can use supplied heat to reduce electrical work; ignoring that heat would overstate total-energy efficiency.')
sub(r'E_\{\\text\{specific\}\} =.*?where \$F\$ is Faraday\'s constant and \$\\eta\$ is the cell efficiency\.', r'''E_{\mathrm{specific,DC}}=
\frac{2F V_{\mathrm{cell}}}{\eta_F M_{\mathrm{H_2}}\,3.6\times10^6}
\quad[\mathrm{kWh/kg}]
$$

Here $F$ is C/mol, $V_{\mathrm{cell}}$ is volts, $\eta_F$ is Faradaic efficiency and $M_{\mathrm{H_2}}$ is kg/mol. Add rectifier, auxiliaries and compression at the system boundary. Alternatively an HHV efficiency gives $E_{\mathrm{specific}}\approx39.4/\eta_{\mathrm{HHV}}$ kWh/kg. The thermoneutral energy is distinct from reversible electrical work because heat can enter the electrolyzer \cite{ivy2004electrolysis}.''')
r('up to 5–20 vol% depending on jurisdiction','at a blend limit qualified for the specific network and end users')
r('It is a pure Java library with no native dependencies','Its core simulation is Java; optional ONNX and Python integration can introduce native runtime dependencies')
r('from Chapter 21','from Chapter 30');r('(Chapter 21)','(Chapter 30)');r('in Chapter 21','in Chapter 30');r('Chapter 19.','Chapter 22.')
r('(adapted from SAE J3016 for automotive)', '(illustrative analogy only; SAE J3016 does not classify process-plant safety or operational assurance)')
r('Most production facilities currently operate at Level 0–1, with some advanced installations at Level 2.', 'No survey of current installation maturity is supplied here.')
r('This architecture ensures that predictions respect physical laws even when the ML component is uncertain, and significantly reduces the training data requirements compared to pure ML approaches.', 'Adding an unconstrained residual does not preserve conservation or thermodynamic consistency. Enforce admissible variables and recompute dependent balances; then test prediction error and physical residuals independently. Reduced training-data requirements are a hypothesis to benchmark, not a guarantee.')
r('BIPs change slowly (monthly recalibration), while fouling factors may change weekly.', 'EOS binary interaction parameters are model parameters for a specified fluid description, not equipment aging indicators. Retune them against suitable phase/property data only when justified; do not fit composition errors or sensor drift into arbitrary monthly BIP changes. Equipment degradation has a different time scale and evidence basis.')
r('exact gradients of any output with respect to any input', 'derivatives of the implemented smooth numerical model with respect to its inputs')
r('provides exact gradients at $O(1)$ cost relative to the forward pass', 'can compute a scalar-objective reverse derivative at a modest multiple of forward cost, with memory/checkpointing and solver costs accounted for')
r('In adjoint mode, the cost of computing $dL/d\\mathbf{x}$ is independent of the dimension of $\\mathbf{x}$ — it requires roughly the same computational effort as a single forward simulation, regardless of whether there are 10 or 10,000 input parameters.', 'Reverse differentiation can avoid one full solve per input for a scalar objective. Its absolute cost still scales with model size and the number of operations, and memory/checkpointing can be substantial. A full many-output Jacobian needs additional reverse seeds. For implicit process equations the adjoint also requires a transposed linear solve.')
r('This approach avoids the numerical instabilities of differentiating through iteration histories and is applicable to any iterative solver', 'This expression requires a sufficiently converged smooth residual and nonsingular state Jacobian. At phase appearance, active-set changes or critical singularities, derivatives may be discontinuous or undefined. It can be applied to eligible implicit models')
r('with confidence that the physical constraints (thermodynamic equilibrium, conservation laws, equipment capacity) are respected.', 'provided each candidate is independently checked for model convergence, balance closure and the declared equipment limits.')
sub(r'Proprietary simulators, however capable, cannot serve as RL training environments.*?An open-source simulator like NeqSim enables researchers to:', 'Some proprietary simulators support scripted/RL integration subject to their APIs and licenses. Source availability improves inspectability, modification and redistribution. An open-source simulator like NeqSim enables researchers to:')
r('The simulator serves as a "ground truth" check on the AI\'s proposals.', 'The simulator provides a numerical reference under its assumptions; independent data and balance/constraint checks are still required. It is not universal ground truth.')
r('Such models are not yet available, but the trajectory of foundation model development — from text to images to code to scientific domains — suggests that domain-specific process engineering models will emerge within the coming decade.', 'These are research directions rather than a verified ten-year delivery forecast. Evaluate any claimed process foundation model against reproducible domain-specific benchmarks and uncertainty tests.')
r('a physics-based model degrades gracefully because the underlying physical laws remain valid.', 'a physics-based model also can fail abruptly at omitted phase transitions, invalid constitutive ranges or numerical failures. Conservation laws remain valid, but equilibrium, transport closures and equipment assumptions are approximations.')
r('The uncertainty in a physics-based model is primarily parametric (uncertainty in model parameters) rather than structural (uncertainty in the form of the model), making it amenable to systematic treatment.', 'Both parameter uncertainty and structural discrepancy can dominate. Separate input uncertainty, parameter uncertainty, numerical error and model-form inadequacy; simulation alone does not bound missing physics.')
r(r'C_v \sim \mathcal{N}(C_{v,\text{design}}, 0.05 C_{v,\text{design}})',r'\ln C_v \sim \mathcal{N}(\ln C_{v,\text{design}},0.05^2)')
r('Feed composition: individual component mole fractions perturbed by $\\pm5\\%$', 'Feed composition: sample on the nonnegative simplex with declared correlations and renormalization')
r('When deployed on the real plant, the actual parameter values fall somewhere within the training distribution, and the agent\'s policy generalizes.', 'Real operating states may fall outside this assumed distribution. Hold-out scenarios, distribution-shift tests and constraint checks are needed; randomization by itself provides no robust-feasibility or transfer guarantee.')
r('As more data is collected, the posterior distribution narrows, reducing uncertainty and improving the fidelity of the simulation.', 'Posterior concentration requires informative, sufficiently independent data, identifiable parameters and a suitable likelihood/model. Additional biased data or changing equipment can shift or broaden uncertainty instead.')
r('The system should match or improve upon historical performance.', 'Historical replay can test predictive consistency and decisions, but unobserved counterfactual outcomes cannot be proven from recorded operator actions alone; use a defensible causal or prospective evaluation.')
sub(r'Industry experience from pilot implementations of integrated optimization on NCS fields suggests:.*?\*\*The role of data and collaboration\.\*\*', 'No field pilot dataset is supplied, so no 2–5% uplift, 5–10% energy saving or 1–3-year intervention deferral is claimed. As an **assumed gross-revenue sensitivity**, 50,000 bbl/day × 3% × USD 75/bbl × 365 days gives USD 41.06 million/year before decline, downtime, costs and tax. Energy and emissions benefits require separate balances.\n\n**The role of data and collaboration.**')
r('The Norwegian Petroleum Directorate maintains', 'The Norwegian Offshore Directorate maintains')
r('demonstrates genuine understanding of the underlying physics.', 'provides stronger evidence of transfer performance within the tested domains.')
r('| CPA (SRK) | Cubic + association (in NeqSim) | Water, glycol, amines, methanol |','| CPA (related association approach) | Cubic reference plus association; not a SAFT variant | Water, glycol and methanol; reactive amines need electrolyte chemistry |')
r('| SAFT-$\\gamma$ Mie | Group contribution SAFT | Predictive, no binary parameter fitting |','| SAFT-$\\gamma$ Mie | Group-contribution parameters and unlike-group interactions | Prediction only within the validated parameter set |')
r('Future integration of full SAFT variants (PC-SAFT, SAFT-$\\gamma$ Mie) into NeqSim would enable:', 'PC-SAFT is already implemented in the pinned source (`SystemPCSAFT`); broader parameterization and other SAFT variants remain separate development/validation work. Candidate applications include:')
r('This approach preserves thermodynamic consistency (the ML correction is added to a thermodynamically consistent base model) while improving accuracy for systems where the standard EOS is inadequate.', 'An additive pressure correction alone does **not** preserve thermodynamic consistency. A differentiable Helmholtz/Gibbs energy correction with consistently derived pressure, chemical potentials and caloric derivatives is one route; stability, limits and experimental agreement still require checks.')
r('This pipeline would enable truly predictive process simulation without requiring any fluid-specific experimental data — a transformational capability for early-stage field development and screening of novel processes.', 'This pipeline can reduce dependence on fitted data, but quantum and coarse-grained models introduce approximations and parameter-transfer error. Independent fluid-specific validation remains necessary before consequential engineering decisions.')
r('reduces operating costs and eliminates personnel exposure to hazards.', 'can reduce staffing costs and routine personnel exposure; inspection, maintenance and emergency visits still create exposure.')
r('with wider operating envelopes and better exception handling.', 'within explicitly qualified operating envelopes and with tested exception handling.')
r('| Cubic EOS (SRK, PR, GERG-2008) | Mature |','| Cubic EOS (SRK, PR) and multiparameter Helmholtz GERG-2008 | Implemented; distinct model families and validity domains |')
r('| Standards compliance | Growing |','| Standards-related calculation methods | Implemented methods require edition, scope and independent compliance review |')
r('The NeqSim project roadmap includes several areas aligned with the trends discussed in this chapter:', 'The following research priorities are editorial suggestions, not a project delivery commitment. Current implemented optimizer, agent, dynamic and MCP capabilities are distinguished from research below:')
r('**Near-term (1–2 years)**','**Near-term research priorities (no delivery commitment)**');r('**Medium-term (3–5 years)**','**Additional research priorities**');r('**Long-term (5+ years)**','**Longer-range research topics**')
r('Built-in multi-objective optimization with constraint handling','Extend the already implemented multi-objective optimization and explicit constraint/evidence handling')
r('Simulation results can be exactly reproduced by anyone with access to the code','Reproduction also requires the exact source revision, dependencies, inputs, numerical settings and external resources')
r('Identify the safe operating window.', 'Identify the modeled phase window and separately assess water, corrosion, fracture and transient limits before calling any window safe.')
r('Plot the phase envelopes and identify the safe operating window.', 'Plot the phase envelopes and distinguish the thermodynamic phase window from qualified transport limits.')
r('the typical pipeline specification of 45–55 MJ/Sm$^3$', 'an assumed teaching interval of 45–55 MJ/Sm$^3$ at the declared reference conditions')
r('Given a wind profile that provides 5 MW for 60% of the time and 0 MW for 40%, calculate:', 'A duration percentage alone is insufficient to size storage. First construct and disclose a chronological wind profile with low-wind spell lengths, battery efficiency, power limits and initial/final state of charge; then calculate:')
r('Case Study 1 (Chapter 23)','Case Study 1 (Chapter 34)')
# Literal scientific checks and truthful stream labels.
c=get(1).replace('comp.setPolytropicEfficiency(0.75)','comp.setPolytropicEfficiency(0.75)\ncomp.setUsePolytropicCalc(True)')
c=c.replace('print(f"CO2 from flaring:  {flare_rate * 1e6 * 0.72 * 2.75:.1f} kg/day")','''flare_stream=splitter.getSplitStream(1)
flare_stream.getFluid().initProperties()
flare=jneqsim.process.equipment.flare.Flare('Complete-combustion accounting',flare_stream)
flare.run()
carbon_moles_s=sum(float(flare_stream.getFluid().getComponent(name).getNumberOfmoles())*nC
                   for name,nC in [('methane',1),('ethane',2),('propane',3)])
co2_kgday=carbon_moles_s*.04401*86400
assert abs(flare.getCO2Emission('kg/day')-co2_kgday)<1e-6
assert abs(flare_stream.getFlowRate('kg/hr')-10000.0)<1e-6
assert abs(comp.getOutletStream().getFlowRate('kg/hr')+flare_stream.getFlowRate('kg/hr')-50000.0)<1e-6
for s in [comp.getInletStream(),comp.getOutletStream()]:s.getFluid().initProperties()
assert abs(comp.getOutletStream().getFluid().getEnthalpy()-comp.getInletStream().getFluid().getEnthalpy()-comp.getPower())/comp.getPower()<1e-5
print(f'Complete-combustion CO2 accounting: {co2_kgday:.1f} kg/day')
# Methane slip, incomplete combustion and radiation are separate assessments.''')
fence(1,c)
c=get(2)
c=c.replace('co2_fluid.addComponent("water", 0.005)','').replace('co2_fluid.addComponent("methane", 0.005)','co2_fluid.addComponent("methane", 0.010)')
c=c.replace('# CO2 with impurities', '# Dry teaching CO2 mixture with impurities').replace('# Flash at pipeline conditions to verify single-phase transport','# TP flash gives a phase-model result, not transport qualification')
c=re.sub(r'print\(f"Phase:.*?\n', 'print("Calculated phase count:",co2_fluid.getNumberOfPhases())\n',c)
c=c[:c.index('# Phase envelope')]+'''# Check composition reconstruction over five fresh pressure states.
import numpy as np
for pressure in [40.0,60.0,80.0,100.0,120.0]:
    state=co2_fluid.clone();state.setPressure(pressure)
    jneqsim.thermodynamicoperations.ThermodynamicOperations(state).TPflash()
    state.initProperties()
    reconstructed=np.zeros(state.getNumberOfComponents())
    for j in range(state.getNumberOfPhases()):
        x=np.array([state.getPhase(j).getComponent(i).getx()
                    for i in range(state.getNumberOfComponents())])
        assert abs(x.sum()-1)<1e-8
        reconstructed+=state.getBeta(j)*x
    assert np.max(np.abs(reconstructed-np.array(state.getMolarComposition())))<1e-7
    assert np.isfinite(state.getDensity('kg/m3')) and state.getDensity('kg/m3')>0
    print(pressure,state.getNumberOfPhases(),state.getDensity('kg/m3'))
# This dry SRK screening does not model water dropout, hydrate or corrosion.
'''
fence(2,c)
c=get(3)+'''
assert oil_co2.getDensity('kg/m3')>0
assert abs(sum(oil_co2.getMolarComposition())-1.0)<1e-8
''';fence(3,c)
c=get(4).replace('SystemSrkEos','SystemSrkCPAstatoil').replace('syngas.setMixingRule("classic")','syngas.setMixingRule(10)\nsyngas.setMultiPhaseCheck(True)')
c=c.replace('h2_comp.setPolytropicEfficiency(0.80)','h2_comp.setPolytropicEfficiency(0.80)\nh2_comp.setUsePolytropicCalc(True)')
c=c.replace('Blue Hydrogen Production Results','Prescribed Syngas Conditioning Results').replace('H2 product rate:','Mixed syngas rate:').replace('H2 pressure:','Syngas pressure:').replace('H2 temperature:','Syngas temperature:')
c+='''
products=[water_ko.getLiquidOutStream(),h2_product]
for s in products+[syngas_stream]:s.getFluid().initProperties()
assert abs(sum(s.getFlowRate('kg/hr') for s in products)-100000.0)/100000.0<1e-7
hin=float(syngas_stream.getFluid().getEnthalpy())
hout=sum(float(s.getFluid().getEnthalpy()) for s in products)
power=float(h2_comp.getPower());cooling=float(h2_cooler.getDuty())
assert power>0 and abs(hout-hin-power-cooling)/max(abs(hin),abs(hout),power,1.0)<1e-5
h2_component=h2_product.getFluid().getComponent('hydrogen')
h2_mass_kghr=float(h2_component.getNumberOfmoles()*h2_component.getMolarMass()*3600)
print('Hydrogen component within mixed syngas (kg/hr):',h2_mass_kghr)
assert 0<h2_mass_kghr<h2_product.getFlowRate('kg/hr')
assert h2_molfrac<0.99 # No PSA or membrane purification in this flowsheet.
''';fence(4,c)
c=get(5)+'''
assert len(properties['h2_pct'])==11
assert all(np.isfinite(properties[k]).all() for k in properties)
assert all(v>0 for v in properties['wobbe_MJm3'])
assert properties['density_kgm3'][-1]<properties['density_kgm3'][0]
''';fence(5,c)
# Additional genuinely executed native electrolysis model.
needle='### 35.4.4 Hydrogen Blending in Natural Gas Pipelines'
electrolysis='''The native `Electrolyzer` can also be checked directly. This deliberately simple water-feed case uses unit Faradaic efficiency, 2.0 V and a 25°C thermoneutral heat approximation. It checks atom stoichiometry, electrical work and heat accounting. It excludes stack kinetics, gas crossover, auxiliaries and downstream compression; non-unit Faradaic-efficiency cases require accounting for unreacted water and side reactions rather than assuming a closed two-product balance.

```python
import jpype
jneqsim=jpype.JPackage('neqsim')
water=jneqsim.thermo.Fluid().create('water')
water_feed=jneqsim.process.equipment.stream.Stream('Electrolysis water',water)
water_feed.setTemperature(298.15,'K');water_feed.setPressure(1.0,'bara')
water_feed.setFlowRate(2.0,'mole/sec');water_feed.run()
electrolyzer=jneqsim.process.equipment.electrolyzer.Electrolyzer('Teaching stack',water_feed)
electrolyzer.setCellVoltage(2.0);electrolyzer.setFaradaicEfficiency(1.0)
electrolyzer.run()
h2=electrolyzer.getHydrogenOutStream();o2=electrolyzer.getOxygenOutStream()
n_h2=float(h2.getFlowRate('mole/sec'));n_o2=float(o2.getFlowRate('mole/sec'))
assert abs(n_h2-2.0)<1e-9 and abs(n_o2-1.0)<1e-9
assert abs(2*n_h2-2*water_feed.getFlowRate('mole/sec'))<1e-9
assert abs(2*n_o2-water_feed.getFlowRate('mole/sec'))<1e-9
power=float(electrolyzer.getStackPower());heat=float(electrolyzer.getWasteHeat())
expected_power=n_h2*2*96485.3329*2.0
assert abs(power-expected_power)<1e-6
reaction_power=n_h2*285830.0 # J/mol H2, liquid water at25C
assert abs(power-reaction_power-heat)/power<1e-3
specific_kWhkg=power/1000/float(h2.getFlowRate('kg/hr'))
assert 52.0<specific_kWhkg<54.0
print('H2 mol/s, O2 mol/s, stack kW, rejected heat kW, DC kWh/kg:',
      n_h2,n_o2,power/1000,heat/1000,specific_kWhkg)
```

'''
r(needle,electrolysis+needle)
for i,m in enumerate(markers):t=t.replace(f'PROTECTED_RESULTS_{i}',m)
p.write_text(t,encoding='utf-8')
(B/'verification/scientific_revision/future_corrections.json').write_text(json.dumps({'changes':changes,'unmatched':missed},indent=2),encoding='utf-8')
print(len(changes),'future edits; unmatched',json.dumps(missed))
