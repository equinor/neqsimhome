"""Initialize the pipeline design read by the optimizer capacity strategy."""
import json
from pathlib import Path
BOOK=Path(__file__).resolve().parents[1]
p=next((BOOK/'chapters').glob('ch24*/notebooks/*.ipynb'))
nb=json.loads(p.read_text(encoding='utf-8'))
for c in nb['cells']:
    s=''.join(c['source'])
    if 'pipeline.autoSize(1.15)' in s:
        s=s.replace('pipeline.autoSize(1.15)', '''pipeline.autoSize(1.15)
pipeline.initMechanicalDesign()
# Both search implementations use the same 100 percent power boundary.
power_constraint = compressor.getCapacityConstraints().get("power")
power_constraint.setMaxValue(power_constraint.getDesignValue())''')
    s=s.replace('assert result.isConverged(), "Optimization did not converge"', 'assert result.isConverged(), str(result.getErrorMessage())')
    c['source']=s.splitlines(True)
p.write_text(json.dumps(nb,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
