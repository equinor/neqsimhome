"""Correct scientific definitions and explicit units in the reference sections."""
from pathlib import Path
import json
import re
import sys

BOOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / '.build/python_packages'))
import yaml

definitions = {
    'Anti-surge control': 'Control that maintains margin from compressor surge, commonly by recycling gas; its effectiveness depends on the map, sensors, valve dynamics and implemented logic.',
    'API gravity': 'Petroleum-liquid density scale: 141.5/SG(60/60 °F) − 131.5. The reference temperatures are part of the definition.',
    'Automatic differentiation (AD)': 'Chain-rule differentiation of implemented elementary operations, accurate to floating-point arithmetic for the differentiable executed path; branches and numerical solvers need appropriate derivative treatment.',
    'BHP': 'Bottomhole pressure at a stated well datum; flowing BHP differs from average reservoir pressure and from shut-in pressure.',
    'BOE': 'Barrel of oil equivalent; an energy-equivalent reporting quantity whose conversion factor and heating-value basis must be stated.',
    'Bubble point': 'For a specified mixture and temperature, the pressure at which an infinitesimal vapor phase first coexists with the liquid; a bubble-point temperature can instead be defined at fixed pressure.',
    'Capacity check': 'Comparison of operating demands with explicitly configured equipment limits, subject to the rating basis, model applicability and completeness of the checked constraints.',
    'CCR': 'Cricondenbar: maximum pressure of vapor–liquid coexistence for a specified mixture; not necessarily the mixture critical pressure.',
    'CCT': 'Cricondentherm: maximum temperature of vapor–liquid coexistence for a specified mixture; not a standard or necessarily the critical temperature.',
    'Compressor surge': 'Low-flow system instability involving pressure and flow oscillations, potentially including flow reversal; the boundary depends on the compressor and connected system.',
    'Conformal prediction': 'Prediction-set calibration with finite-sample marginal coverage under the method\'s assumptions, commonly exchangeability; it does not guarantee conditional coverage or remain valid under arbitrary distribution shift.',
    'Cv value': 'Valve flow coefficient based on US gallons per minute of water at about 60 °F producing a 1 psi pressure drop. Gas, cavitation and choked-flow calculations require the appropriate sizing relations.',
    'DeepONet': 'Deep Operator Network: a learned mapping between function spaces, used as a surrogate for solution operators within a demonstrated training and validation domain.',
    'Digital twin': 'A computational representation connected to observations of a physical asset, with defined update, synchronization and validation procedures; connection alone does not establish accuracy.',
    'Flash calculation': 'Equilibrium phase amounts and compositions at specified constraints, such as temperature/pressure or enthalpy/pressure; more than two phases may be present.',
    'HYSYS': 'Aspen HYSYS, an AspenTech process simulator. Honeywell UniSim Design is a separate product.',
    'JT cooling': 'Cooling during approximately isenthalpic throttling when the Joule–Thomson coefficient is positive. Throttling can instead heat a fluid when that coefficient is negative.',
    'K-factor': 'Here, the Souders–Brown separator capacity factor, with velocity units; distinguish it from the dimensionless phase-equilibrium ratio K_i = y_i/x_i.',
    'Monte Carlo dropout': 'Approximate uncertainty estimation from repeated stochastic network evaluations with dropout; prediction spread needs calibration and is not automatically a reliable physical-error bound.',
    'Multiphase flow': 'Simultaneous transport of two or more phases, for example gas–liquid, oil–water or gas–oil–water.',
    'NPV': 'Net present value: the sum of cash flows, including initial investment, discounted to a specified valuation date using a stated discount-rate convention.',
    'OPR': 'Outflow performance relationship: pressure required to transport a specified rate through tubing and downstream equipment for stated outlet and thermal conditions.',
    'PI': 'Productivity index: production rate divided by pressure drawdown on a stated flow/pressure basis; the linear relation has an applicability range.',
    'Polytropic efficiency': 'For compression, the ratio of differential ideal pressure work to differential actual enthalpy rise along the compression path; real-gas evaluation requires thermodynamic properties and a defined method.',
    'Utilization': 'Dimensionless operating demand divided by the relevant declared limit; separate limits may apply to power, actual volume, gas load, liquid retention or other quantities.',
    'Affinity laws': 'Approximate centrifugal-machine similarity relations: flow scales with speed, head with speed squared and power with density times speed cubed, for fixed geometry and comparable operating conditions.',
    'Carbon intensity': 'Emissions divided by a declared production or energy measure, with system boundary, gas coverage and CO2-equivalent convention stated.',
    'Decline curve': 'Empirical production-rate trend, such as an Arps model; fitted coefficients and flow-regime applicability do not by themselves establish recoverable reserves.',
    'IRR': 'Discount rate at which project NPV is zero; cash-flow patterns can produce multiple IRRs or no economically useful root.',
    'Latin Hypercube Sampling': 'Stratified sampling that covers each marginal probability interval once; it does not guarantee uniform coverage of all joint combinations.',
    'P10/P50/P90': 'Quantile labels requiring an explicit convention. Under non-exceedance, P10 is the 10th percentile; petroleum resource exceedance notation commonly uses P10 for the high case and P90 for the low case.',
    'PINN': 'Physics-informed neural network: includes equation residuals or physical constraints in training. Soft penalty terms encourage, but do not guarantee, conservation or an accurate solution.',
    'Recycle': 'NeqSim recycle-stream convergence equipment supporting direct substitution and optional acceleration; acceptance still requires residual and conservation checks.',
    'Robust optimization': 'Optimization imposing feasibility or performance requirements over a specified uncertainty set; coverage is limited to that set and the chosen formulation.',
    'Scope 1/2 emissions': 'Scope 1 covers direct emissions from owned or controlled sources; Scope 2 covers indirect emissions from purchased electricity, steam, heat and cooling.',
    'Stochastic optimization': 'Optimization using probability models for uncertain inputs, through sampling, probability-weighted scenarios or other stochastic formulations.',
    'Tornado diagram': 'Ranked one-at-a-time sensitivity ranges for a declared input variation and baseline; the bars are not generally a variance decomposition or probability distribution.',
    'UQ': 'Uncertainty quantification: identifying, propagating and assessing uncertainties in inputs, observations, parameters and models with explicit assumptions and calibration evidence.',
    'Wobbe index': 'Calorific value divided by the square root of gas relative density to air, using consistent reference conditions and gross/net basis; this is an interchangeability indicator, not a complete burner-compatibility test.',
}
path = BOOK / 'backmatter/glossary.md'
source = path.read_text(encoding='utf-8')
changes = []
for term, definition in definitions.items():
    pattern = re.compile(r'^\| \*\*' + re.escape(term) + r'\*\* \| (.*?) \|$', re.M)
    match = pattern.search(source)
    assert match, term
    changes.append(dict(section='glossary', term=term, before=match[1], after=definition))
    source = source[:match.start()] + f'| **{term}** | {definition} |' + source[match.end():]
path.write_text(source, encoding='utf-8')

path = BOOK / 'nomenclature.yaml'
data = yaml.safe_load(path.read_text(encoding='utf-8'))
updates = {
    'Cp': ('$C_p$', 'Molar heat capacity at constant pressure', 'J/(mol·K)'),
    'Cv': ('$C_v$', 'Molar heat capacity at constant volume', 'J/(mol·K)'),
    'Cv_valve': ('$C_{v,\\mathrm{valve}}$', 'Valve coefficient: water flow at 60 °F and 1 psi differential', 'US gpm on the stated reference basis'),
    'cp_mass': ('$c_p$', 'Mass-specific heat capacity at constant pressure', 'J/(kg·K)'),
    'f': ('$f_i$', 'Component fugacity', 'Pa'),
    'f_D': ('$f_D$', 'Darcy friction factor; four times the Fanning factor', 'dimensionless'),
    'G': ('$G$', 'Molar Gibbs free energy in molar thermodynamic equations', 'J/mol'),
    'H': ('$H$', 'Enthalpy on the stated molar, mass or extensive basis', 'J/mol, J/kg or J; defined locally'),
    'H_dot': ('$\\dot{H}$', 'Enthalpy flow rate', 'W'),
    'H_head': ('$H_p$', 'Polytropic compressor head as specific work', 'J/kg; sometimes kJ/kg'),
    'h_head': ('$h_{\\mathrm{head}}$', 'Hydraulic head as energy per unit weight', 'm'),
    'K': ('$K_i$', 'Phase-equilibrium ratio y_i/x_i', 'dimensionless'),
    'K_SB': ('$K_{SB}$', 'Souders–Brown separator gas-capacity factor', 'm/s'),
    'M': ('$M$', 'Molar mass; convert g/mol to kg/mol in SI mass balances', 'kg/mol'),
    'P': ('$P$', 'Absolute pressure unless explicitly marked gauge', 'Pa or bara; 1 bar = 100000 Pa'),
    'Q': ('$Q$', 'Heat or volumetric flow, distinguished by local definition', 'J or m³/s; defined locally'),
    'Q_dot': ('$\\dot{Q}$', 'Heat-transfer rate, positive into the stated control volume', 'W'),
    'q_volume': ('$q$', 'Volumetric flow at stated actual or reference conditions', 'm³/s'),
    'R': ('$R$', 'Universal gas constant, approximately 8.314462618', 'J/(mol·K)'),
    'T': ('$T$', 'Absolute temperature in thermodynamic ratios; Celsius may label reported states', 'K; °C only where stated'),
    'W': ('$W$', 'Work crossing a stated system boundary', 'J'),
    'W_dot': ('$\\dot{W}$', 'Shaft power, with sign convention defined locally', 'W'),
    'beta': ('$\\beta$', 'Vapor mole fraction in the two-phase flash equations', 'dimensionless'),
}
for key, (symbol, description, unit) in updates.items():
    replacement = dict(symbol=symbol, description=description, unit=unit)
    changes.append(dict(section='nomenclature', key=key, before=data.get(key), after=replacement))
    data[key] = replacement
path.write_text('# Symbols may be reused across disciplines; local definitions and stated units govern.\n' + yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100), encoding='utf-8')
(BOOK / 'verification/scientific_revision/reference_section_review.json').write_text(
    json.dumps(dict(full_text_review=['glossary', 'nomenclature', 'preface', 'software_revision'],
                    corrections=changes,
                    sources={'HYSYS':'https://www.aspentech.com/en/products/engineering/aspen-hysys',
                             'UniSim':'https://process.honeywell.com/us/en/products/industrial-software/process-optimization/unisim-design-suite',
                             'NeqSim':'source commit 6cc8026202a5d3f9383c9abd1d97d448993813f9',
                             'technical_definitions':'Corresponding reviewed textbook chapters and their cited primary sources'}), indent=2), encoding='utf-8')
print(f'Corrected {len(definitions)} glossary definitions and {len(updates)} nomenclature entries.')
