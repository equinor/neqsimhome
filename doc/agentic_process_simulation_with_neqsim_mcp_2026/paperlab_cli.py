"""Run native PaperLab using the selected Python and existing publishing packages.

No installation is attempted. PAPERLAB_BUILD_DEPS can point to another already
provisioned package directory when this book is moved to another machine.
"""
from pathlib import Path
import os
import runpy
import sys

BOOK = Path(__file__).resolve().parent
PAPERLAB = BOOK.parents[1]
DEFAULT_DEPS = BOOK.parent / "Industrial Agentic Engineering with NeqSim_2026" / "revision_history" / "build_dependencies"
DEPS = Path(os.environ.get("PAPERLAB_BUILD_DEPS", str(DEFAULT_DEPS))).resolve()
if not DEPS.is_dir():
    raise RuntimeError("Existing publishing packages unavailable: " + str(DEPS))
sys.path.insert(0, str(DEPS))
sys.path.insert(0, str(PAPERLAB))
sys.path.insert(0, str(PAPERLAB / "tools"))
os.environ["PYTHONPATH"] = str(DEPS) + os.pathsep + os.environ.get("PYTHONPATH", "")
os.environ["PYTHONUTF8"] = "1"
os.environ["PAPERLAB_AUTO_INSTALL"] = "0"
import pypandoc
os.environ["PATH"] = str(Path(pypandoc.get_pandoc_path()).parent) + os.pathsep + os.environ["PATH"]
if __name__ == "__main__":
    os.chdir(PAPERLAB)
    sys.argv[0] = str(PAPERLAB / "paperflow.py")
    runpy.run_path(str(PAPERLAB / "paperflow.py"), run_name="__main__")

