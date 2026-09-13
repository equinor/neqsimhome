"""One-time targeted editorial repairs, preserving original literal source/evidence."""
from pathlib import Path
import shutil,re
B=Path(__file__).resolve().parents[2]
C=next((B/'chapters').glob('ch28_*/chapter.md'))
backup=B/'.build/backups/ch28_literal_solution_revision';backup.mkdir(parents=True,exist_ok=True)
if not (backup/'chapter.md').exists():shutil.copy2(C,backup/'chapter.md')
for p in [B/'verification/scientific_revision/ch28_java_solution_checks.json',B/'verification/scientific_revision/ch28_java_solution_checks.log',B/'verification/ch28_field_development_fences.json']:
    if p.exists() and not (backup/p.name).exists():shutil.copy2(p,backup/p.name)
s=C.read_text(encoding='utf-8-sig')
s=s.replace('mass-flow normalization [kg/hr]; this is not a stock-tank liquid rate','total standard oil + water rate [Sm3/hr], at 15 C and 1.01325 bara')
s=s.replace('// WC index 0, GOR index 3','// WC index 0, GOR index 1')
start=s.index('The exported file contains:')
end=s.index('\n---',start)
s=s[:start]+'''The diagnostic text records the rate unit (`kg/hr` here), outlet-pressure, water-cut and GOR axes, and one required inlet pressure with an explicit feasibility flag for each sampled combination. An unavailable pressure remains `NaN`. The output is not a `VFPPROD` or `VFPEXP` reservoir deck; converting it requires a separate, verified reservoir-simulator contract and pressure datum.
'''+s[end:]
s=s.replace('# Process factory: 30 km flowline + riser','# Process factory: existing 2800 m upward tubing + 30 km horizontal flowline')
s=s.replace('# Process factory: subsea booster + 8 km flowline','# Process factory: existing 2800 m upward tubing + 8 km horizontal flowline')
s=s.replace('# Process factory: short riser only','# Process factory: existing 2800 m upward tubing + 0.5 km horizontal flowline')
for i in range(1,4):
 s=s.replace(f'feasible_{i} = vfp_concept{i}.generateVFPTable().getFeasibleCount()',f'table_concept{i} = vfp_concept{i}.generateVFPTable()\nfeasible_{i} = table_concept{i}.getFeasibleCount()')
s=s.replace('list(result.getChokeSettings())','dict(result.getChokeSettings())')
s=s.replace('# Assume VFP table has been generated (table object from Section 28.6.2)','# Use the actual Python table generated in Section 28.7')
s=s.replace('# THP index=1 (40 bara), WC index=1','# Outlet-pressure index 1 (50 bara), WC index 0 (5%)')
s=s.replace('The larger tubing will have more feasible points (lower friction), but the smaller tubing may be preferred for low rates (avoid liquid loading).','Compare the accepted pressures and unavailable cells for each diameter. A larger diameter usually reduces friction, but it need not increase the number of feasible points in a coarse grid, and the steady correlation does not establish a liquid-loading limit.')
s=s.replace('The `RecombinationFlashGenerator` caches fluids — repeated (GOR, WC) pairs are free','The `RecombinationFlashGenerator` caches composition; repeated (GOR, WC) pairs still require rate normalization and flashes')
s=s.replace('The VFP table enables accurate production forecasting by the reservoir simulator:','A qualified and calibrated VFP table can support reservoir forecasts through the following coupling:')
s=s.replace('Without multi-scenario VFP, the simulator uses a single VFP curve that becomes increasingly wrong — leading to optimistic production forecasts in the early years and pessimistic forecasts later.','A fixed-composition table can become unrepresentative as composition changes. The direction and size of forecast bias require a case-specific sensitivity study.')
s=s.replace('**Concept 2: Subsea processing hub (8 km tieback)**','**Concept 2: Shorter horizontal route (8 km)**')
s=s.replace('**Concept 3: Local processing (minimal subsea infrastructure)**','**Concept 3: Short horizontal route (0.5 km)**')
# These are scenario blend labels, not evidence of a field production history.
needle='### 28.9.2 Plotting VFP Surfaces'
s=s.replace(needle,'The density plot uses the total equilibrium fluid volume at 80 °C and 50 bara. It is not the pipe mixture density based on slip-dependent liquid holdup. `generateFluid` takes total standard liquid **Sm³/hr** as its third argument; the pressure-table generator subsequently sets its separately configured feed mass rate in **kg/hr**. GOR and water cut define mixing ratios of separated reference phases. Verify and report the equilibrated standard ratios when exact sales or production ratios matter.\n\n'+needle)
C.write_text(s,encoding='utf-8')
print(C)
