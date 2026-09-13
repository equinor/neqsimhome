"""Place the inspected pressure-grid figure and bind its review evidence."""
from pathlib import Path
import hashlib,json,shutil
BOOK=Path(__file__).resolve().parents[1]
OUT=BOOK/'verification/scientific_revision'
record=json.loads((OUT/'ch24_acceptance_figure.json').read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=BOOK/record['source']
image=BOOK/record['figure']
assert sha(source)==record['source_sha256']
assert sha(image)==record['figure_sha256']
target=BOOK/'chapters/ch24_production_optimization/figures/ch24_pressure_grid_acceptance.png'
shutil.copy2(image,target)
review={'status':'passed','source':str(source),'source_sha256':sha(source),
        'images':[{'path':str(target),'sha256':sha(target)}],
        'inspection':'Full-resolution image inspected: all 32 states shown, 30 numerical power values, two visibly rejected cells, distinct fixed-feed panels, units and shared power scale readable; rejected mass deficits shown. No complete-grid optimum claim.',
        'unresolved_material_findings':0}
(OUT/'ch24_figure_review.json').write_text(json.dumps(review,indent=2),encoding='utf-8')
print('Copied and recorded inspected Chapter 24 acceptance figure.')
