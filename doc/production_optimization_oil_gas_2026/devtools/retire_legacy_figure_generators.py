"""Archive the superseded hand-drawn numerical generators with their provenance."""
from pathlib import Path
import hashlib,json,shutil
BOOK=Path(__file__).resolve().parents[1]
OUT=BOOK/'verification/scientific_revision/legacy_generators'
OUT.mkdir(exist_ok=True)
records=[]
for name in ['generate_figures_style.py']+[f'generate_figures_batch{i}.py' for i in range(1,5)]:
    source=BOOK/name;target=OUT/name
    if source.exists():
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
        else:shutil.copy2(source,target)
        # Retire only the exact copied file inside this existing book.
        assert source.resolve().parent==BOOK.resolve()
        assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
        source.unlink()
    if target.exists():records.append(dict(file=name,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
(OUT/'README.md').write_text('''# Superseded synthetic figure generators

These five files are retained as historical evidence, not as the book's current
figure-generation workflow. Some numerical curves were manually constructed;
one plot labeled generated points as experimental. Their model, citation and
physical limitations were not adequately disclosed in the previous manuscript.

The scientific revision replaces incorrect figures with checked analytical
illustrations, actually traced NeqSim envelopes, or independent NIST comparisons.
It removes unsupported result plots and explicitly identifies retained
conceptual scenarios. Current simulation figures come from the executed chapter
notebooks and literal examples. See `../manuscript_figure_review.json`,
`../illustration_repairs.json`, and `../figure_visual_review.json`.

Do not use these historical generators to overwrite reviewed publication assets.
''',encoding='utf-8')
(OUT/'archive_manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print(f'Archived {len(records)} superseded generators with content hashes.')
