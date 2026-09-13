"""Run the canonical PaperLab CLI with the book's explicitly selected packages."""
from pathlib import Path
import os
import runpy
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BOOK = Path(__file__).resolve().parents[1]
PAPERLAB = BOOK.parents[1]
PACKAGES = BOOK / '.build' / 'python_packages'
sys.path.insert(0, str(PACKAGES))
sys.path.insert(0, str(PAPERLAB))
sys.path.insert(0, str(PAPERLAB / 'tools'))
os.environ['PYTHONPATH'] = os.pathsep.join([str(PACKAGES), str(PAPERLAB / 'tools'), os.environ.get('PYTHONPATH', '')])
os.environ['PYTHONIOENCODING'] = 'utf-8'
import pypandoc
os.environ['PATH'] = str(Path(pypandoc.get_pandoc_path()).parent) + os.pathsep + os.environ['PATH']
sys.argv = [str(PAPERLAB / 'paperflow.py')] + sys.argv[1:]
os.chdir(PAPERLAB)
runpy.run_path(str(PAPERLAB / 'paperflow.py'), run_name='__main__')
