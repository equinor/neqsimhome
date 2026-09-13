"""Repair gas-treatment material allocation and state a physically bounded process boundary."""
from revise_foundations_science_phase3 import R,S,BOOK
import json,re
ledger_path=BOOK/'verification/scientific_revision/foundations_text_changes.json'
entries=json.loads(ledger_path.read_text(encoding='utf-8'))
bad=[x for x in entries if x['id']=='ch12_amine_boundary_note' and not x['original']]
if bad:
    p=next((BOOK/'chapters').glob('ch12*/chapter.md'))
    t=p.read_text(encoding='utf-8').replace(bad[0]['correction'],'')
    p.write_text(t,encoding='utf-8')
    entries=[x for x in entries if x not in bad]
    ledger_path.write_text(json.dumps(entries,indent=2),encoding='utf-8')
    from revise_foundations_science_phase3 import ledger
    ledger[:]=entries
path=next((BOOK/'chapters').glob('ch12*/chapter.md'))
source=path.read_text(encoding='utf-8')
old=re.findall(r'^```python\s*\n(.*?)^```',source,re.M|re.S)[0]
new=json.loads((BOOK/'verification/scientific_revision/amine_probe.json').read_text())['code']
new='import math\n'+new
R('ch12','amine_material_capacity',old,new,'The original 5 t/hr solvent case demanded 21.96 mol acid gas/mol MDEA; missing zero-amount CO2/H2S in the lean fluid caused acid gas to disappear rather than enter the rich outlet. Verified 300 t/hr case has 0.366 mol/mol loading and material closure. Heat exchange is an inferred isothermal duty, not an adiabatic prediction.',['NeqSim SimpleAmineAbsorber.java run(UUID), fixed source commit6cc8026','verification/scientific_revision/amine_probe.json'])
R('ch12','amine_boundary_note', '```python\nimport math\nimport jpype', '''The next calculation is a **prescribed-removal, isothermal material-allocation example**. Its 90% CO₂ and 99% H₂S removals are input assumptions, not equilibrium or rate-based absorber predictions; the stage count is metadata in this simple model. The feed is already dry and the 50 wt% MDEA stream contains explicit zero-amount acid-gas components so transferred material is retained. A 300 t/hr solvent rate gives net loading 0.366 mol acid gas/mol MDEA, below the explicitly assumed 0.50 screening limit. The original 5 t/hr rate would require 21.96 mol/mol and is rejected. The resulting 467.9 kW heat removal maintains the isothermal boundary; solvent-specific loading, reaction heat, mass transfer, regenerator duty and outlet specifications still require a reactive process design. Sweet gas retains about 5,524 ppmv CO₂, so no universal sales-gas compliance is claimed.

```python
import math
import jpype''')
R('ch12','dry_JT_feed','gas.addComponent("water", 1.0)','gas.addComponent("water", 0.0)  # dry pretreated hydrocarbon boundary')
R('ch12','dry_integrated_feed','raw_gas.addComponent("water", 2.1)','raw_gas.addComponent("water", 0.0)  # upstream dehydration is outside this boundary')
R('ch12','integrated_feed_label','# Step 1: Define the raw gas','# Step 1: Define dry pretreated rich gas; acid-gas treating and dehydration are upstream')
R('ch12','JT_cooler_label','# Gas-gas heat exchanger (inlet cooling)','# Specified-temperature cooler; its heat sink is external to this flowsheet')
R('ch12','integrated_cooler_scope','# Step 3: Gas cooling and dew point control','# Step 3: Dry-gas cooling and hydrocarbon liquid recovery')
R('ch12','envelope_candidates','print("Phase envelope calculated successfully")\nprint(f"Number of dew points: {len(list(dew_temps))}")\nprint(f"Number of bubble points: {len(list(bub_temps))}")', '''import math
def finite_pairs(temperatures, pressures):
    return [(float(t), float(p)) for t, p in zip(temperatures, pressures)
            if math.isfinite(t) and math.isfinite(p) and t > 0.0 and p > 0.0]
candidate_A = finite_pairs(dew_temps, dew_pres)
candidate_B = finite_pairs(bub_temps, bub_pres)
assert candidate_A or candidate_B, "No finite saturation-trace candidates"
print(f"Finite trace candidates A/B: {len(candidate_A)}/{len(candidate_B)}")
print("Branch identity and full-envelope completeness require independent TP transition brackets.")''')
