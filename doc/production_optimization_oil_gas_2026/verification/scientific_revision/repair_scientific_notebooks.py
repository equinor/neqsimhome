import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BOOK=ROOT.parents[1]
for path in (BOOK/'chapters').glob('*/notebooks/*.ipynb'):
    notebook=json.loads(path.read_text(encoding='utf-8'))
    chapter=int(path.parent.parent.name[2:4])
    for cell in notebook['cells']:
        source=''.join(cell.get('source',[]))
        if chapter==4:
            source=source.replace('hydrostatic_gradient = 0.1', 'hydrostatic_gradient = 0.1')
            source=source.replace('# bar/m (approximate for light hydrocarbon)', '# bar/m; imposed pressure path, not a solved hydrostatic gradient')
        if chapter==33 and cell['cell_type']=='code':
            if 'process_teg = ProcessSystem()' in source and 'teg_energy_corrections = []' not in source:
                source=source.replace('process_teg = ProcessSystem()',
                    'from teg_energy_reconstruction import close_teg_energy\nteg_energy_corrections = []\nprocess_teg = ProcessSystem()')
            lines=source.splitlines()
            for i in reversed(range(len(lines))):
                if lines[i].strip()=='process_teg.run()':
                    indent=lines[i][:len(lines[i])-len(lines[i].lstrip())]
                    if i+1>=len(lines) or 'close_teg_energy' not in lines[i+1]:
                        lines.insert(i+1,indent+'teg_energy_corrections.append(close_teg_energy(absorber, _physics))')
            source='\n'.join(lines)+'\n'
        if chapter==31 and cell['cell_type']=='code':
            old="""    for unit in [mixer, cooler_loop, separator, splitter_loop]:
        unit.run()
        assert _physics.run(unit, 'calculation_cell_9:unit', candidate=False)
"""
            new="""    for unit in [mixer, cooler_loop]:
        unit.run()
        assert _physics.run(unit, 'calculation_cell_9:unit', candidate=False)
    # Separator caches changes below 1e-6; this demonstration resolves a tighter
    # 1e-7 recycle residual. Fresh phase allocation avoids reusing stale outlets.
    separator = Separator("Loop separator", cooler_loop.getOutletStream())
    separator.run()
    assert _physics.run(separator, 'recycle fresh separator')
    splitter_loop.setInletStream(separator.getGasOutStream())
    splitter_loop.run()
    assert _physics.run(splitter_loop, 'recycle gas split')
"""
            source=source.replace(old,new)
        cell['source']=source.splitlines(keepends=True)
    path.write_text(json.dumps(notebook,ensure_ascii=False,indent=1),encoding='utf-8')
