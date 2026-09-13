#!/usr/bin/env python3
"""Patch all book notebooks to fix the dual-boot cell.

Problem: When neqsim_dev_setup is installed, the dual-boot cell activates
devtools mode, but classes are on `ns.SystemSrkEos` not bare `SystemSrkEos`.
Later cells that reference bare class names or `jneqsim.xxx` fail.

Fix: Replace the dual-boot cell with one that always ensures `jneqsim` is
available AND extracts common bare class names from jneqsim. This makes
all subsequent cells work regardless of which mode activated.

Also fixes conditional import cells (if NEQSIM_MODE == ...) by replacing
them with unconditional imports from jneqsim.
"""

import json
import glob
import os
import sys
from pathlib import Path

BOOK_DIR = Path(__file__).resolve().parent
CHAPTERS_DIR = BOOK_DIR / "chapters"

# The new dual-boot cell that always ensures jneqsim is available
NEW_DUALBOOT = '''import importlib, subprocess, sys

try:
    from neqsim_dev_setup import neqsim_init, neqsim_classes
    ns = neqsim_init(recompile=False)
    ns = neqsim_classes(ns)
    NEQSIM_MODE = "devtools"
    print("NeqSim loaded via devtools (local dev mode)")
except Exception:
    NEQSIM_MODE = "pip"

# Always ensure jneqsim is available (works in both modes)
try:
    import neqsim
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "neqsim"])

from neqsim import jneqsim
print(f"NeqSim ready (mode: {NEQSIM_MODE})")

# Common class shortcuts for convenience
SystemSrkEos = jneqsim.thermo.system.SystemSrkEos
SystemPrEos = jneqsim.thermo.system.SystemPrEos
SystemSrkCPAstatoil = jneqsim.thermo.system.SystemSrkCPAstatoil
ThermodynamicOperations = jneqsim.thermodynamicoperations.ThermodynamicOperations

# Process equipment
Stream = jneqsim.process.equipment.stream.Stream
Separator = jneqsim.process.equipment.separator.Separator
ThreePhaseSeparator = jneqsim.process.equipment.separator.ThreePhaseSeparator
Compressor = jneqsim.process.equipment.compressor.Compressor
Cooler = jneqsim.process.equipment.heatexchanger.Cooler
Heater = jneqsim.process.equipment.heatexchanger.Heater
HeatExchanger = jneqsim.process.equipment.heatexchanger.HeatExchanger
Mixer = jneqsim.process.equipment.mixer.Mixer
Splitter = jneqsim.process.equipment.splitter.Splitter
ThrottlingValve = jneqsim.process.equipment.valve.ThrottlingValve
Pump = jneqsim.process.equipment.pump.Pump
Expander = jneqsim.process.equipment.expander.Expander
Recycle = jneqsim.process.equipment.util.Recycle
ProcessSystem = jneqsim.process.processmodel.ProcessSystem'''


def find_all_notebooks():
    """Return sorted list of all .ipynb files under chapters/."""
    return sorted(CHAPTERS_DIR.rglob("*.ipynb"))


def is_dualboot_cell(source):
    """Check if a cell is the dual-boot setup cell."""
    return ("neqsim_dev_setup" in source and "neqsim_init" in source)


def is_conditional_import_cell(source):
    """Check if a cell has conditional NEQSIM_MODE imports."""
    return ("NEQSIM_MODE" in source and ("if NEQSIM_MODE" in source or
            "SystemSrkEos = jneqsim" in source or
            "SystemSrkEos = ns." in source))


def is_import_cell_after_dualboot(source):
    """Check if a cell is the import cell immediately after dual-boot.
    These cells typically import matplotlib, numpy, and optionally jneqsim classes."""
    lines = source.strip().split('\n')
    has_mpl = any('matplotlib' in l for l in lines)
    has_np = any('numpy' in l for l in lines)
    has_jneqsim_import = any('from neqsim import jneqsim' in l for l in lines)
    has_class_import = any('= jneqsim.' in l for l in lines)
    return (has_mpl or has_np) and (has_jneqsim_import or has_class_import or
                                     any('NEQSIM_MODE' in l for l in lines))


def patch_notebook(nb_path, dry_run=False):
    """Patch a notebook's dual-boot and import cells.
    Returns True if changes were made."""
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    cells = nb.get('cells', [])
    changed = False

    for i, cell in enumerate(cells):
        if cell['cell_type'] != 'code':
            continue
        source = ''.join(cell.get('source', []))

        # Replace dual-boot cell
        if is_dualboot_cell(source):
            if source.strip() != NEW_DUALBOOT.strip():
                if not dry_run:
                    cell['source'] = [NEW_DUALBOOT]
                    # Clear old outputs
                    cell['outputs'] = []
                    cell['execution_count'] = None
                changed = True
                print(f"  Patched dual-boot cell (cell {i+1})")

        # Remove or simplify conditional import cells
        elif is_conditional_import_cell(source):
            # Strip out the NEQSIM_MODE conditional, keep other imports
            new_lines = []
            skip_block = False
            for line in source.split('\n'):
                if 'if NEQSIM_MODE' in line:
                    skip_block = True
                    continue
                if skip_block:
                    if line.startswith('    ') or line.startswith('\t'):
                        # Keep the actual imports but de-indent
                        stripped = line.lstrip()
                        if stripped and not stripped.startswith('pass'):
                            new_lines.append(stripped)
                        continue
                    elif line.startswith('else:'):
                        continue
                    else:
                        skip_block = False
                new_lines.append(line)

            # Also remove redundant imports already in dual-boot
            final_lines = []
            for line in new_lines:
                # Skip lines that import things already in dual-boot cell
                if line.strip().startswith('from neqsim import jneqsim'):
                    continue
                if '= jneqsim.thermo.system.SystemSrkEos' in line:
                    continue
                if '= jneqsim.thermo.system.SystemPrEos' in line:
                    continue
                if '= jneqsim.thermodynamicoperations.ThermodynamicOperations' in line:
                    continue
                final_lines.append(line)

            new_source = '\n'.join(final_lines)
            if new_source.strip() != source.strip():
                if not dry_run:
                    cell['source'] = [new_source]
                    cell['outputs'] = []
                    cell['execution_count'] = None
                changed = True
                print(f"  Cleaned conditional import cell (cell {i+1})")

    if changed and not dry_run:
        with open(nb_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)

    return changed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Patch book notebooks")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    notebooks = find_all_notebooks()
    print(f"Found {len(notebooks)} notebooks\n")

    patched = 0
    for nb_path in notebooks:
        rel = nb_path.relative_to(CHAPTERS_DIR)
        print(f"{rel}:")
        if patch_notebook(nb_path, dry_run=args.dry_run):
            patched += 1
        else:
            print("  No changes needed")

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Patched {patched}/{len(notebooks)} notebooks")


if __name__ == "__main__":
    main()
