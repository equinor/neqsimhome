"""Hydraulic, separation and gas-processing science corrections."""
from revise_foundations_science_phase3 import R,S,BOOK
import re,json

R('ch06','network_accepted_assertions','    study.run();\n    logger.info("Opening', '''    study.run();
    double residualPa = study.getMaxResidual();
    double massErrorKgS = Math.abs(study.getMassBalanceError());
    double sinkKgS = study.getTotalSinkFlow();
    String chokeStatus = study.getPipe("Choke-A").getChokeModelStatus();
    if (!study.isConverged() || !Double.isFinite(residualPa)
        || residualPa > 100.0 || massErrorKgS > 1.0e-6
        || !Double.isFinite(sinkKgS) || sinkKgS <= 0.0
        || !chokeStatus.startsWith("IEC_GAS_")) {
        throw new IllegalStateException("Rejected hydraulic operating point");
    }
    double downAPa = study.getNode("Down-A").getPressure();
    double downBPa = study.getNode("Down-B").getPressure();
    if (!(40.0e5 < downAPa && downAPa < 90.0e5
        && 40.0e5 < downBPa && downBPa < 85.0e5)) {
        throw new IllegalStateException("Invalid passive-network pressure ordering");
    }
    logger.info("Accepted: residual {} Pa, mass error {} kg/s, status {}",
        residualPa, massErrorKgS, chokeStatus);
    logger.info("Opening''', 'Accepted network now requires finite positive flow,100Pa residual,1e-6kg/s balance, supported gas-choke status and pressure ordering.')
R('ch06','accepted_curve_meaning','This produces a characteristic curve showing diminishing returns as the choke opens — the well transitions from choke-limited to reservoir-limited or tubing-limited flow.', 'For this fixed-source-pressure example, the gas chokes remain in the supported critical-flow regime. Total plant flow at40%,60%,80% and100% opening is6.11035,7.37624,8.64213 and9.90802kg/s. The largest hydraulic residual is11.45Pa and the mass residual is below1e-6kg/s. The approximately linear increase is the expected critical-capacity response; this model contains no reservoir IPR and cannot demonstrate a reservoir-limited plateau. The opt-in forward gas-capacity model is essential: the legacy head-loss choke approximation can report hydraulic convergence while flagging unsupported critical flow.')
S('ch06','gaslift_proxy_body',r'Gas lift reduces the hydrostatic head in the tubing.*?The gas lift rate is specified in kg/hr of injection gas:',r'''Physical gas lift mixes injected gas with production, changing density, friction, temperature and total mass. In this network's legacy gas-lift switch, however, the pressure benefit is only a capped loss proxy:

$$\Delta P_{\mathrm{boost}}=|\Delta P_{\mathrm{base}}|\min\!\left(0.5,\frac{2\dot m_{\mathrm{lift}}}{\dot m_{\mathrm{produced}}}\right).$$

It does not add injection gas to the material balance. Use Chapter5's explicit gas mixer/tubing calculation for injection sizing or an economic gas-lift optimum. The API accepts its screening lift-rate input in kg/hr:''')
S('ch06','gaslift_gain',r'The effect on wellhead pressure \(and hence production rate\) is dramatic.*?natural energy\.', 'A physical production gain must be established from the coupled IPR, tubing, injection pressure and downstream constraints. Do not interpret a gain from this capped proxy as an empirical50–200% recovery prediction.')
R('ch10','threephase_train','Separator = jneqsim.process.equipment.separator.Separator\nThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve\nProcessSystem = jneqsim.process.processmodel.ProcessSystem\n\n# Three-stage separation:', 'Separator = jneqsim.process.equipment.separator.ThreePhaseSeparator\nThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve\nProcessSystem = jneqsim.process.processmodel.ProcessSystem\n\n# Withdraw oil and free water separately; the liquid outlet feeds oil forward.\n# Three-stage separation:', 'Three-phase feed requires separate aqueous withdrawal; prior two-phase LP separator failed18.54%energy closure.')
R('ch10','stage_ratio',r'r = \left(\frac{P_1}{P_{final}}\right)^{1/n}',r'r = \left(\frac{P_1}{P_{final}}\right)^{1/(n-1)}', 'n separator pressure levels contain n−1 pressure intervals.')
R('ch10','asme_pressure','- $P$ is the design pressure [MPa]','- $P$ is the internal-minus-external design pressure [MPa]; do not insert bara as gauge pressure')
R('ch10','asme_radius','- $R$ is the inside radius [mm]','- $R$ is the corroded-condition inside radius [mm]')
R('ch10','asme_stress','- $S$ is the maximum allowable stress [MPa]','- $S$ is the allowable stress for the material, product form and design temperature from the applicable code edition [MPa]')
R('ch10','head_weight','each approximately $0.4D$ in projected length','an approximate equivalent shell-area contribution, not a physical projected head depth')
S('ch10','autosize_true',r'The `autoSize\(.*?method.*?(?=### 10\.|\n```)', lambda: '') if False else None
R('ch11','salt_chemistry',r'\text{CaCl}_2 + \text{H}_2\text{O}',r'\text{CaCl}_2 + 2\text{H}_2\text{O}', 'Balanced hydrolysis reaction water stoichiometry.')
R('ch11','column_scope','The following example demonstrates a complete stabilizer with reboiler and condenser:', 'The following example represents an unrefluxed stripping section with a reboiler and no condenser; it illustrates component and energy conservation, not a complete refluxed-column design.')
S('ch11','RVP_definition',r'Reid Vapor Pressure is the vapor pressure.*?vapor space dilution effect\.', 'Reid vapor pressure is defined by the ASTM D323 apparatus and conditioning procedure at37.8°C. ASTM D5191 is a separate mini-method with a specified conversion/reporting basis, not simply automated D323. A bubble-pressure flash predicts equilibrium true vapor pressure at its specified temperature; it is not a Reid test. Finite vapor/liquid ratio, air saturation and sample preparation prevent a universal conversion from a bubble-point calculation to measured RVP.', sources=['https://www.astm.org/d0323-20a.html','https://www.astm.org/d5191-22.html'])
R('ch12','acid_chemistry','forms carbonic acid and sulfuric acid','forms aqueous carbonic-acid and hydrogen-sulfide species; H2S dissolution does not itself form sulfuric acid')
R('ch12','hcdp_table','| HC dew point | < −2°C (cricondentherm) | Prevent liquid dropout |','| HC dew point | Illustrative target < −2°C over the contract pressure range | Prevent hydrocarbon liquid dropout |')
S('ch12','cricondentherm_contract',r'The cricondentherm — the maximum temperature.*?\$\$T_\{\\text\{HCDP,spec\}\}.*?\$\$',r'''Cricondentherm is the maximum saturation temperature of the specified composition. A gas contract may instead limit dew point at one pressure or over a specified interval:

$$\max_{P\in[P_{min},P_{max}]}T_{dew}(P,\mathbf z)\leq T_{spec}.$$

An all-pressure cricondentherm limit is a different, generally stronger condition; specify which is required.''')
R('ch12','stahl','**Stahl column (azeotropic regeneration)**','**Stahl column (stripping-gas regeneration)**')
R('ch12','TEG_decomposition','above 204°C, TEG decomposes to form acidic products that cause corrosion and foaming.', '204°C is a common practical reboiler limit rather than an abrupt chemical threshold; degradation depends on temperature, residence time, oxygen and contaminants. Apply the solvent supplier\'s limits.')
R('ch12','JT_integral',r'T_2 = T_1 - \int_{P_1}^{P_2}',r'T_2 = T_1 + \int_{P_1}^{P_2}', 'Correct signed integration of dT=muJT dP.')
S('ch12','expander_percent',r'A turboexpander with 80% isentropic efficiency typically produces 30–50% more cooling than a JT valve for the same pressure drop\.', 'The actual temperature difference must be calculated for the same inlet composition/state and outlet pressure; there is no universal percentage cooling advantage.')
R('ch12','expander_T_domain','the isentropic outlet temperature is always lower than the isenthalpic outlet temperature for the same pressure ratio.', 'the expander outlet has lower enthalpy than the JT outlet at the same pressure. For a stable single phase this normally gives a lower temperature; within a pure-fluid two-phase region it can instead change vapor quality at the same saturation temperature.')
S('ch12','retrograde_peak',r'\*\*Retrograde condensation behavior\*\* adds complexity.*?dew point curve\.', 'For a gas-condensate mixture, liquid dropout along an isothermal depletion or expansion path can be nonmonotonic. The cricondenbar is the maximum pressure of the saturation envelope, where a phase is incipient; it does not identify maximum bulk liquid recovery. Optimize actual flashed liquid yield along the specified energy path, including recompression and final product quality constraints.')
R('ch12','henry_sign','which decreases with temperature (favoring absorption at lower temperatures).','defined here by $x=P/H$. When cooling favors absorption, this pressure-over-mole-fraction Henry constant decreases on cooling (increases with temperature); its convention must be stated.')
R('ch12','TEG_typo','TEG circulation rate','amine circulation rate') if False else None
R('ch17','N8_units','The expansion factor:',r'For $W$ in kg/hr, $p_1$ in bara, $T_1$ in K and $M$ in g/mol, $N_8=94.8$. For the density form above, $N_6=27.3$ with $\rho_1$ in kg/m³. Cap the sizing ratio at $x_{sizing}=\min(x,F_kx_T)$; attached fittings require the adjusted $x_{TP}$.\cite{foundationFisher2023}'+'\n\nThe expansion factor:', sources=['https://www.emerson.com/documents/automation/control-valve-handbook-en-3661206.pdf'])
R('ch17','mode_enable','valve.setPercentValveOpening(70.0)\n```','valve.setPercentValveOpening(70.0)\nvalve.setIsCalcOutPressure(True)\n```') if False else None
S('ch18','carbon_current',r'1\. \*\*Norwegian CO\$_2\$ tax\*\*.*?This substantial cost directly incentivizes:',r'''1. **Norwegian CO₂ tax** — the adopted2026 offshore petroleum rate for combusted natural gas is2.57NOK/Sm³. Convert it to NOK/tonneCO₂ using the actual fuel composition and reporting basis.\cite{foundationNorwayTax2026}
2. **EU ETS** — add the applicable allowance price and NOK/EUR exchange rate for the valuation date; it is a market input, not a fixed statutory NOK/tonne amount.

For an explicitly assumed combined cost of1,500NOK/tonne and150,000tonnes/year, the annual cost is225millionNOK. This sensitivity input is not a claim about the current ETS price. Carbon cost incentivizes:''', sources=['https://www.regjeringen.no/no/tema/okonomi-og-budsjett/skatter-og-avgifter/skatte-og-avgiftssatser/avgiftssatser-2026/id3121982/'])
S('ch18','carbon_payback',r'At Norwegian CO\$_2\$ tax rates \(currently.*?3–5 years\.', 'Calculate payback from the project\'s dated fuel, carbon and electricity prices, recoverable heat, installed cost and remaining operating life; no universal offshore payback period follows from thermal efficiency alone.')
R('ch18','carbon_summary','combined Norwegian CO$_2$ tax and EU ETS carbon cost of ~900 NOK/tonne','dated Norwegian CO$_2$ tax and EU ETS allowance-price assumptions')
R('ch18','carbon_exercise','Norwegian rate: 600 NOK/tonne + EU ETS at 70 EUR/tonne','use the2026 gas tax2.57NOK/Sm³, actual fuel emission factor, and an explicitly assumed70EUR/tonne allowance price with stated exchange rate')
S('ch18','turbine_catalog',r'Common offshore gas turbine models and their characteristics:.*?(?=### Ambient Temperature)',r'''Package selection must use the OEM's current model variant, ISO/site rating, shaft-versus-generator basis and guaranteed ambient curve. Engine-core weight is not installed-package weight. The Siemens SGT-A65 derives from the Industrial Trent60; it is not an Avon16–22MW machine. Historical catalog names and mixed core/package masses are therefore unsuitable for a comparison table.\cite{foundationSiemensA65}

''', sources=['https://press.siemens.com/global/de/pressemitteilung/schwimmende-kraftwerke-von-siemens-unterstuetzen-new-york-citys-energiestrategie'])
