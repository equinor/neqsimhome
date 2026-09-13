"""Use the selected interpreter with optional book-local publishing dependencies."""
from pathlib import Path
import os
import sys

BOOK = Path(__file__).resolve().parent
LOCAL_DEPS = BOOK / "revision_history" / "build_dependencies"
if LOCAL_DEPS.is_dir():
    sys.path.insert(0, str(LOCAL_DEPS))
    os.environ["PYTHONPATH"] = str(LOCAL_DEPS) + os.pathsep + os.environ.get("PYTHONPATH", "")


def bootstrap(project_root):
    project_root = Path(project_root).resolve()
    if not (project_root / "devtools" / "neqsim_dev_setup.py").is_file():
        raise RuntimeError("Select an explicit NeqSim source checkout")
    os.environ["NEQSIM_PROJECT_ROOT"] = str(project_root)
    sys.path.insert(0, str(project_root / "devtools"))
    from neqsim_dev_setup import neqsim_init
    neqsim_init(project_root=project_root, recompile=False, verbose=True)
    import jpype
    return jpype.JPackage("neqsim")
