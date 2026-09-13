from pathlib import Path
import re
BOOK=Path(__file__).resolve().parents[1]
for n in (3,6,9,14,18):
    p=next((BOOK/'chapters').glob(f'ch{n:02}*/chapter.md'))
    t=p.read_text(encoding='utf-8')
    if n==3:
        start=t.index('# Bisection search\n')
        end=t.index('\n```',start)
        t=t[:start]+'''# A synthetic target generated from a known parameter tests the search.
# Replace this with a laboratory target only after checking the bracket.
target_pb = calc_bubble_point(0.035)
kij_low, kij_high = -0.02, 0.10
f_low = calc_bubble_point(kij_low) - target_pb
f_high = calc_bubble_point(kij_high) - target_pb
assert f_low * f_high <= 0.0, "Target not bracketed by admissible BIP range"
for iteration in range(30):
    kij_mid = (kij_low + kij_high) / 2.0
    pb_calc = calc_bubble_point(kij_mid)
    residual = pb_calc - target_pb
    if abs(residual) < 0.05:
        print(f"Synthetic fit: kij={kij_mid:.5f}; Pb={pb_calc:.2f} bara; "
              f"residual={residual:.3f} bar")
        break
    if f_low * residual <= 0.0:
        kij_high = kij_mid
    else:
        kij_low, f_low = kij_mid, residual
else:
    raise RuntimeError("Bubble-point regression did not meet tolerance")
'''+t[end:]
        t=t.replace('target_pb = 245.0  # Target bubble point (bara)\n','')
        t=t.replace('# Plus fraction: specify mole fraction, molecular weight, and density', '# Explicit TBP pseudo-components: amounts in a common mole basis, MW and density')
        t=t.replace('# Characterize the plus fractions\nfluid.getCharacterization().setLumpingModel("no lumping")\nfluid.getCharacterization().characterisePlusFraction()', '# These TBP pseudo-components are already defined; no automatic plus split is requested.')
    if n==6:
        t=t.replace('### 6.2.1 API units and model scope in the 2026 release', '**API units and model scope in the 2026 release**')
        lines=t.splitlines(); inside=False
        for i,line in enumerate(lines):
            if line.startswith('```'):
                if not inside and line=='```': lines[i]='```text'
                inside=not inside
        t='\n'.join(lines)+'\n'
    if n==9:
        t=t.replace('// The pipeline now carries constraint metadata', 'pipeline.initMechanicalDesign();\n// The pipeline now carries constraint metadata')
    if n in (14,18):
        # This metadata setter is kW and initializes a default overload allowance.
        pos=t.find('```python')
        note=('The current compressor constraint API is `updatePowerConstraint(ratingKW)`. '
              'Its argument is kW even though `getPower()` returns W. The generated capacity '
              'constraint includes the default overload allowance; a study requiring a strict '
              'driver limit must explicitly set its maximum and verify the selected operating point.\n\n')
        if note not in t: t=t[:pos]+note+t[pos:]
    if n==18:
        t=t.replace('### 18.15 Typed energy allocation:', '### 18.13.1 Typed energy allocation:')
    p.write_text(t,encoding='utf-8')
