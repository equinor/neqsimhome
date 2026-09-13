"""Run the native PaperLab CLI with this book's selected dependency context."""
from book_runtime import BOOK
import os
from pathlib import Path
import runpy
import sys

PAPERLAB = BOOK.parents[1]
sys.path.insert(0, str(PAPERLAB))
sys.path.insert(0, str(PAPERLAB / "tools"))
os.environ["PYTHONUTF8"] = "1"
os.environ["PAPERLAB_AUTO_INSTALL"] = "0"
try:
    import pypandoc
    os.environ["PATH"] = str(Path(pypandoc.get_pandoc_path()).parent) + os.pathsep + os.environ["PATH"]
except ImportError:
    pass
os.chdir(PAPERLAB)
sys.argv[0] = str(PAPERLAB / "paperflow.py")
runpy.run_path(str(PAPERLAB / "paperflow.py"), run_name="__main__")
