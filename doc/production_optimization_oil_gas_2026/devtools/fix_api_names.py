"""One-shot mechanical corrections of wrong NeqSim API names in chapter.md files.

Each entry is (regex, replacement, reason). Applied to chapters/*/chapter.md.
Safe to re-run: patterns no longer match once fixed.

Usage:
    python devtools/fix_api_names.py --dry-run
    python devtools/fix_api_names.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_blocks import all_chapter_files  # noqa: E402

RULES = [
    # PipeBeggsAndBrills / Pipeline
    (r"\.setOuterTemperature\(", ".setConstantSurfaceTemperature(",
     "no setOuterTemperature; constant ambient surface temperature is the right call"),
    (r"\.setPipeLength\(", ".setLength(", "PipeBeggsAndBrills.setLength"),
    (r"\.setInsideDiameter\(", ".setDiameter(", "PipeBeggsAndBrills.setDiameter"),

    # ThermodynamicOperations package
    (r"neqsim\.thermo\.ThermodynamicOperations",
     "neqsim.thermodynamicoperations.ThermodynamicOperations",
     "class lives in neqsim.thermodynamicoperations"),
    (r"jneqsim\.thermo\.ThermodynamicOperations",
     "jneqsim.thermodynamicoperations.ThermodynamicOperations",
     "class lives in neqsim.thermodynamicoperations"),

    # PinchAnalysis
    (r"\.getPinchTemperature\(\)", ".getPinchTemperatureC()", "PinchAnalysis.getPinchTemperatureC"),
    (r"\.getMinHotUtility\(\)", ".getMinimumHeatingUtility()", "PinchAnalysis"),
    (r"\.getMinColdUtility\(\)", ".getMinimumCoolingUtility()", "PinchAnalysis"),
    (r"\.getMinHeatingUtility\(\)", ".getMinimumHeatingUtility()", "PinchAnalysis"),
    (r"\.getMinCoolingUtility\(\)", ".getMinimumCoolingUtility()", "PinchAnalysis"),
    (r"\.getMaxHeatRecovery\(\)", ".getMaximumHeatRecovery()", "PinchAnalysis"),

    # LoopedPipeNetwork
    (r"\bnetwork\.addSource\(", "network.addSourceNode(", "LoopedPipeNetwork.addSourceNode"),
    (r"\bnetwork\.addSink\(", "network.addSinkNode(", "LoopedPipeNetwork.addSinkNode"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default=None)
    args = ap.parse_args()

    total = 0
    for md in all_chapter_files(args.only):
        text = md.read_text(encoding="utf-8")
        orig = text
        hits = []
        for pat, repl, reason in RULES:
            text, n = re.subn(pat, repl, text)
            if n:
                hits.append(f"{n}x {pat} -> {repl}")
                total += n
        if text != orig:
            print(f"{md.parent.name}")
            for h in hits:
                print(f"    {h}")
            if not args.dry_run:
                md.write_text(text, encoding="utf-8")

    print(f"\nTotal replacements: {total}{' (dry run)' if args.dry_run else ''}")


if __name__ == "__main__":
    main()
