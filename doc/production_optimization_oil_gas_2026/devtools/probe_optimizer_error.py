"""Diagnostic for the legacy engine's process-container detection."""
import json, os, sys
from pathlib import Path
BOOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK/'.build/python_packages'))
path=next((BOOK/'chapters').glob('ch24*/notebooks/*.ipynb'))
namespace={'__file__':str(path), '__vsc_ipynb_file__':str(path)}
os.chdir(path.parent)
for c in json.loads(path.read_text(encoding='utf-8'))['cells']:
    source=''.join(c['source'])
    if c['cell_type']=='code':
        if 'algorithms = ' in source:
            break
        exec(source, namespace)
for name in ('result_binary','result_golden'):
    result=namespace[name]
    print(name, result.isConverged(), result.getErrorMessage())
os._exit(0)
