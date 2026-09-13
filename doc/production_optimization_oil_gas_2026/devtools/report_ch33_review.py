"""Summarize the scientific read-through and exact executed chapter evidence."""
from pathlib import Path
import hashlib
import json
import re

BOOK = Path(__file__).resolve().parents[1]
OUT = BOOK / 'verification/scientific_revision'
chapter = BOOK / 'chapters/ch33_onshore_processing_plants/chapter.md'
text = chapter.read_text(encoding='utf-8')
execution = json.loads((OUT / 'ch33_physical_execution.json').read_text(encoding='utf-8'))
blocks = list(re.finditer(r'^```python\s*\n(.*?)^```', text, re.M | re.S))
assert execution['literal'] and len(blocks) == len(execution['executions']) == 9
purposes = [
    ('bindings and conservation helper', 'Reusable mass, each-component and enthalpy/work/heat residual calculations are exercised by all subsequent process cases.'),
    ('surge inventory', 'Independent dimensional arithmetic: 60 m3 of accumulated liquid from flow imbalance and duration.'),
    ('amine circulation', 'Independent dimensional arithmetic: 67.8974 kg/s of lean solution including solvent molar mass, weight fraction and loading change.'),
    ('TEG contactor', 'Mass, each component and explicit corrected energy boundary; raw energy residual retained. Positive heat capacities/densities, single retained phase and bounded temperature correction.'),
    ('ideal-gas expansion limit', 'Analytical temperature/efficiency relation, correct sign of work and temperature drop.'),
    ('binary shortcut distillation', 'Independent Fenske/Underwood/Gilliland assumptions; saturated-liquid binary Underwood root 4/3 and minimum reflux 1.7.'),
    ('complete dry-gas plant', 'Unit and whole-plant mass/component/energy balances, rigorous column status and MESH residual, independent fugacity equality and reconstructed expander efficiency.'),
    ('automation and saved input record', 'Pressure readback matches the accepted process; fresh model rebuild from the serialized input specification reproduces export/product/energy results.'),
    ('seven-case temperature sweep and scientific figure', 'Fresh whole-plant rebuild at each temperature; all physical acceptance checks, component recovery plus every loss path sums to one; plot uses executed data and separate heat/shaft-power quantities.'),
]
entries = []
for match, run, (purpose, evidence) in zip(blocks, execution['executions'], purposes):
    digest = hashlib.sha256(match[1].encode()).hexdigest()
    assert run['passed'] and digest == run['sha256']
    entries.append(dict(block=run['block'], line=text[:match.start()].count('\n') + 1,
                        code_sha256=digest, status='passed', purpose=purpose,
                        engineering_evidence=evidence,
                        classification='executed verification helper' if run['block'] == 1 else 'calculation/derived output'))
issues = [
    ('Inventory sizing', 'Separated transient surge accumulation from residence-time inventory and defined standard/actual volume bases.'),
    ('Amine circulation', 'Restored solvent molar mass in the solution mass-flow relation; separated loadings, weight fraction and circulation.'),
    ('Hydrogen sulfide', 'Replaced unsupported concentration/consequence claims with the NIOSH 100 ppm IDLH value and a primary citation.'),
    ('TEG composition', 'Converted 99.5 mass% lean solution to molar amounts; the old molar recipe did not represent the stated concentration.'),
    ('TEG energy conservation', 'Exposed the native approximate absorber residual and solved an explicit fixed-composition outlet-temperature energy reconstruction; retained the raw residual.'),
    ('Cryogenic pretreatment', 'Defined the numerical feed as dry and acid-gas-free; distinguished TEG dew-point reduction from molecular-sieve cryogenic pretreatment.'),
    ('Heat exchange boundary', 'Replaced unsupported one-sided heat-recovery credit with a cooler having an explicit external thermal duty.'),
    ('Expander inlet', 'Added a knockout separator, gas-only expansion and separate liquid letdown/remixing to avoid expanding a wet two-phase feed as turbine gas.'),
    ('Expander efficiency', 'Corrected the efficiency/temperature relation; lower efficiency produces less cooling at fixed pressure ratio.'),
    ('Refrigeration', 'Used enthalpy duty without adding latent heat twice; stated the Carnot COP upper bound and utility-model requirement.'),
    ('Recovery basis', 'Computed recovery by component molar flow rather than mixed-phase volume ratios, accounting for all loss paths.'),
    ('Distillation shortcuts', 'Corrected the saturated-liquid Underwood formulation and its root interval, with an independently checked binary example.'),
    ('Column acceptance', 'Replaced a failed large column with a converged equilibrium-stage stabilizer and explicit stage heat input, stage energy and MESH gates.'),
    ('Column duty accounting', 'Matched reboiler heatInput to the stage-energy boundary; rejected a fixed-temperature result that appeared solved while failing rigorous energy residuals.'),
    ('Sulfur recovery', 'Corrected sulfur atom accounting and removed an ambiguous reaction-enthalpy value without a specified sulfur reference state.'),
    ('Ethane storage', 'Used NIST boiling/critical properties and removed an unsupported ambient-pressure liquid-storage guarantee near the critical temperature.'),
    ('Plant scope', 'Replaced the claimed complete raw-gas plant with an explicit three-area dry-gas teaching flowsheet; standalone TEG is a separate model.'),
    ('Product specification', 'Reported 2.2246 mol% methane in stabilizer bottoms as a calculated composition, without claiming an untested storage/product specification.'),
    ('Export constraint', 'Made 70 bara export pressure an explicit requirement rather than treating low-pressure gas as sales-ready production.'),
    ('Energy objective', 'Reported gross compression, recovered expansion and thermal cooling separately; no shaft coupling or utility conversion is silently assumed.'),
    ('Persistence', 'Rebuilt from a checked input specification rather than claiming an unverified whole-state archive proves reproducibility.'),
    ('Sensitivity', 'Rebuilt every plant for seven temperatures and retained the nonmonotonic recovery maximum under fixed stabilizer heat input.'),
    ('Design numbers', 'Removed universal cost, recovery, life and capacity claims without a documented basis.'),
    ('Exercises and standards', 'Labeled design assignments and standards scope explicitly; no unsolved exercise or catalogue citation is represented as an executed design or compliance proof.'),
]
balances = execution['balances']
assert balances and all(max(row[k] for k in ('mass_relative', 'component_relative', 'energy_relative')) <= row['tolerance'] for row in balances)
report = dict(chapter='ch33_onshore_processing_plants', status='reviewed_and_verified_with_stated_model_limits',
              full_text_review=True, chapter_sha256=hashlib.sha256(chapter.read_bytes()).hexdigest(),
              source_revision='6cc8026202a5d3f9383c9abd1d97d448993813f9',
              issue_families=[dict(topic=a, correction=b) for a, b in issues],
              entries=entries, balance_evaluations=len(balances),
              maximum_relative_residuals={k: max(row[k] for row in balances) for k in ('mass_relative', 'component_relative', 'energy_relative')},
              execution_record='verification/scientific_revision/ch33_physical_execution.json',
              independent_references=['nioshH2S2026', 'nistEthanePhase2026', 'waterlooDistillation2026', 'uopMercuryRemoval2026', 'twuTEG2005', 'neaguTEG2017', 'epaGasProcessing1995'],
              limitations=[
                  'Conservation, equilibrium and reconstructed efficiency are solution verification; the same EOS is not an independent experimental reference.',
                  'No measured performance data were available for this synthetic plant or TEG case; no field calibration is claimed.',
                  'SimpleTEGAbsorber water transfer remains an approximate stage-efficiency model; the explicit energy reconstruction does not make it a rigorous rate-based contactor.',
                  'The small stabilizer is a converged teaching calculation, not a sized or validated commercial fractionation train.',
                  'Only the specified dry feed, pressure, temperature and duty range is covered by the executed plant checks.',
                  'References to safety values and standards do not establish a facility safety assessment or regulatory compliance.'
              ])
(OUT / 'onshore_review.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
lines = ['# Chapter 33 scientific review', '',
         'The complete chapter was rewritten after a scientific read-through. All nine current literal Python blocks executed successfully, including the explicit thermodynamic and engineering acceptance assertions.', '',
         f"The retained run includes {len(balances)} unit/stage/whole-plant balance evaluations, a rebuilt input round trip and seven independently rebuilt temperature cases. Every checked mass, component and energy residual is below its declared tolerance.", '',
         '## Corrected issues', '']
lines += [f'- **{a}:** {b}' for a, b in issues]
lines += ['', '## Exact published-code evidence', '']
lines += [f"- Block {e['block']} — {e['purpose']}: {e['engineering_evidence']}" for e in entries]
lines += ['', '## Scope of the evidence', ''] + ['- ' + s for s in report['limitations']]
lines += ['', 'The machine-readable ledger records every current code-block hash and points to the complete numerical execution record.']
(OUT / 'onshore_review.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(json.dumps({k: report[k] for k in ('status', 'balance_evaluations', 'maximum_relative_residuals')}, indent=2))
