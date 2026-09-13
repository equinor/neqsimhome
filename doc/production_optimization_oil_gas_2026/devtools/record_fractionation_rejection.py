from pathlib import Path
import json
B=Path(__file__).resolve().parents[1]
p=next((B/'chapters').glob('ch33*/chapter.md'));text=p.read_text(encoding='utf-8-sig')
text=text.replace('For fractionation, report `deethanizer.solved()` with the product flows and verify composition and energy balances.',
'''In the verified execution, both included fractionation cases returned `deethanizer.solved() == False`. Their product values are diagnostic outputs and are excluded from accepted plant predictions. A bounded AUTO-solver probe also failed within the 512 MB worker memory limit; no converged replacement is claimed. The upstream NGL sensitivity uses only the independent NGL area and remains separate from that rejected fractionation calculation.

For fractionation, report `deethanizer.solved()` with the product flows and verify composition and energy balances.''')
p.write_text(text,encoding='utf-8')
(B/'verification/ch33_auto_solver_probe.json').write_text(json.dumps({
 'solver':'AUTO','maximum_iterations':100,'hard_iteration_cap':True,'java_heap_limit_mb':512,
 'status':'failed','failure':'java.lang.OutOfMemoryError: Java heap space',
 'scope':'Standalone30-tray manuscript deethanizer; no model acceptance or converged replacement',
 'manuscript_decision':'Retain explicit rejected/unqualified fractionation status; independently evaluate upstream NGL area'
},indent=2),encoding='utf-8')
