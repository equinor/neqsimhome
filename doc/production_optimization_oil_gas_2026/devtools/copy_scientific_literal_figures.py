"""Publish the exact plots retained by accepted current literal chapter runs."""
from pathlib import Path
import json
import hashlib
import shutil

BOOK=Path(__file__).resolve().parents[1]
selected={27:['fig28_tornado.png','ch27_verified_resource_npv.png'],
          29:['ch29_verified_level_inventory.png','ch29_verified_blowdown.png','ch29_verified_feed_pulse.png'],
          34:['ch23_case1_hp_optimization.png','ch23_case2_water_cut_sensitivity.png','ch23_case3_debottleneck_analysis.png']}
records=[]
for number,names in selected.items():
    chapter=next((BOOK/'chapters').glob(f'ch{number:02d}_*'))
    for name in names:
        source=BOOK/'.build/fence_runs'/chapter.name/'figures'/name
        target=chapter/'figures'/name
        assert source.is_file(),source
        shutil.copy2(source,target)
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
        records.append({'chapter':chapter.name,'source':str(source),'path':str(target),'sha256':digest})
(BOOK/'verification/scientific_revision/literal_figure_copies.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print(f'Copied {len(records)} figures from their executed literal-source runs.')
