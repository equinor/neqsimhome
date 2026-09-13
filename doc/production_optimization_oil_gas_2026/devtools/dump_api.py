"""Dump the real public API of NeqSim classes referenced by the book.

Usage:
    python devtools/dump_api.py neqsim.process.util.optimizer.ProductionOptimizer ...
    python devtools/dump_api.py --simple ProductionOptimizer BatchStudy
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(r"c:\Users\ESOL\Documents\GitHub\neqsim")


def build_index():
    index = defaultdict(list)
    src = PROJECT_ROOT / "src" / "main" / "java"
    for p in src.rglob("*.java"):
        rel = p.relative_to(src).with_suffix("")
        index[p.stem].append(".".join(rel.parts))
    return index


def sig(m):
    params = ", ".join(str(p.getSimpleName()) for p in m.getParameterTypes())
    ret = str(m.getReturnType().getSimpleName())
    return f"{ret} {m.getName()}({params})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="+")
    ap.add_argument("--simple", action="store_true", help="names are simple class names")
    ap.add_argument("--filter", default=None)
    ap.add_argument("--ctors", action="store_true", help="show constructors only")
    args = ap.parse_args()

    import jpype
    from neqsim import jneqsim  # noqa: F401

    index = build_index() if args.simple else None

    for name in args.names:
        fqs = index.get(name, []) if args.simple else [name]
        if not fqs:
            print(f"=== {name}: NO SOURCE FILE FOUND")
            continue
        for fq in fqs:
            try:
                c = jpype.JClass(fq)
            except Exception as e:
                print(f"=== {fq}: LOAD FAILED ({str(e)[:100]})")
                continue
            print(f"=== {fq}")
            for ctor in c.class_.getConstructors():
                params = ", ".join(str(p.getSimpleName()) for p in ctor.getParameterTypes())
                print(f"    ctor({params})")
            if args.ctors:
                continue
            own = {str(m.getDeclaringClass().getName()): None for m in c.class_.getMethods()}
            sigs = sorted({sig(m) for m in c.class_.getMethods()
                           if not str(m.getDeclaringClass().getName()).startswith("java.lang.Object")})
            if args.filter:
                sigs = [s for s in sigs if args.filter.lower() in s.lower()]
            for s in sigs:
                print(f"    {s}")
            print()


if __name__ == "__main__":
    main()
