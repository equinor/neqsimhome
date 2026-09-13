"""Verify NeqSim API usage in book chapter code blocks against the live jar.

High-signal, low-noise strategy: only check a method when the receiver's class
is statically known.

  Python : ``x = SomeNeqSimClass(...)``  then  ``x.method(...)``
  Java   : ``SomeType x = new SomeType(...)``  then  ``x.method(...)``

Also checks:
  * Python syntax of every non-fragment block
  * every ``jneqsim.a.b.C`` path and ``JClass("a.b.C")`` string resolves
  * every bare NeqSim class name used as a constructor resolves

Usage:
    python devtools/verify_api.py [--only ch23] [--json report.json]
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_blocks import all_chapter_files, iter_blocks  # noqa: E402

PROJECT_ROOT = Path(r"c:\Users\ESOL\Documents\GitHub\neqsim")

JNEQSIM_PATH_RE = re.compile(r"jneqsim\.((?:[a-z][A-Za-z0-9_]*\.)+[A-Z][A-Za-z0-9_]*)")
JCLASS_RE = re.compile(r"""JClass\(\s*["']([A-Za-z0-9_.]+)["']\s*\)""")
JAVA_DECL_RE = re.compile(
    r"\b([A-Z][A-Za-z0-9_<>, ]*?)\s+([a-z][A-Za-z0-9_]*)\s*=\s*new\s+([A-Z][A-Za-z0-9_]*)\s*\("
)
JAVA_CALL_RE = re.compile(r"\b([a-z][A-Za-z0-9_]*)\.([a-zA-Z][A-Za-z0-9_]*)\s*\(")


def build_class_index():
    """simple class name -> [fully-qualified names] from the Java source tree."""
    index = defaultdict(list)
    src = PROJECT_ROOT / "src" / "main" / "java"
    for p in src.rglob("*.java"):
        rel = p.relative_to(src).with_suffix("")
        index[p.stem].append(".".join(rel.parts))
    return index


class Checker:
    def __init__(self):
        import jpype
        from neqsim import jneqsim  # noqa: F401 boots the JVM

        self.jpype = jpype
        self.index = build_class_index()
        self._cls_cache = {}
        self._meth_cache = {}

    def load(self, fq):
        if fq in self._cls_cache:
            return self._cls_cache[fq]
        try:
            cls = self.jpype.JClass(fq)
        except Exception:
            cls = None
        self._cls_cache[fq] = cls
        return cls

    def load_simple(self, name):
        fqs = self.index.get(name)
        if not fqs:
            return None
        for fq in fqs:
            cls = self.load(fq)
            if cls is not None:
                return cls
        return None

    def methods(self, cls):
        key = str(cls.class_.getName())
        if key in self._meth_cache:
            return self._meth_cache[key]
        names = set()
        try:
            for m in cls.class_.getMethods():
                names.add(str(m.getName()))
        except Exception:
            pass
        self._meth_cache[key] = names
        return names

    def is_neqsim_name(self, name):
        return name in self.index


def is_fragment(code):
    stripped = [ln.strip() for ln in code.splitlines() if ln.strip()]
    if not stripped:
        return True
    return any(ln.startswith("...") or ln == "# ..." for ln in stripped)


def python_findings(chk, b):
    out = []
    tree = None
    if not is_fragment(b.code):
        try:
            tree = ast.parse(b.code)
        except SyntaxError as e:
            out.append(("syntax-error", "", f"line {e.lineno}: {e.msg}"))
            return out

    for fq in set(JNEQSIM_PATH_RE.findall(b.code)) | set(JCLASS_RE.findall(b.code)):
        if fq.startswith(("java.", "javax.", "org.", "com.")):
            continue
        fq_try = fq if fq.startswith("neqsim") else "neqsim." + fq
        if chk.load(fq_try) is None:
            out.append(("missing-class", fq_try, "does not resolve in the NeqSim jar"))

    if tree is None:
        return out

    binding = {}
    aliases = {}

    for node in ast.walk(tree):
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1):
            continue
        tgt, val = node.targets[0], node.value
        if not isinstance(tgt, ast.Name):
            continue
        if isinstance(val, ast.Attribute):
            src = ast.unparse(val)
            if src.startswith("jneqsim.") or src.startswith("ns."):
                aliases[tgt.id] = val.attr
        elif isinstance(val, ast.Call):
            f = val.func
            fname = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
            if fname == "JClass" and val.args and isinstance(val.args[0], ast.Constant):
                aliases[tgt.id] = str(val.args[0].value).rsplit(".", 1)[-1]
            elif fname:
                simple = aliases.get(fname, fname)
                if chk.is_neqsim_name(simple):
                    binding[tgt.id] = simple

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        recv = node.func.value
        if not isinstance(recv, ast.Name):
            continue
        simple = binding.get(recv.id)
        if simple is None:
            continue
        cls = chk.load_simple(simple)
        if cls is None:
            out.append(("missing-class", simple, "constructed but not in jar"))
            continue
        m = node.func.attr
        if m not in chk.methods(cls):
            out.append(("missing-method", f"{simple}.{m}", "not found on class"))
    return out


def java_findings(chk, b):
    out = []
    binding = {}
    for m in JAVA_DECL_RE.finditer(b.code):
        var, ctor = m.group(2), m.group(3)
        if chk.is_neqsim_name(ctor):
            binding[var] = ctor
        elif ctor not in ("String", "ArrayList", "HashMap", "LinkedHashMap"):
            continue

    for m in JAVA_CALL_RE.finditer(b.code):
        var, meth = m.group(1), m.group(2)
        simple = binding.get(var)
        if simple is None:
            continue
        cls = chk.load_simple(simple)
        if cls is None:
            out.append(("missing-class", simple, "constructed but not in jar"))
            continue
        if meth not in chk.methods(cls):
            out.append(("missing-method", f"{simple}.{meth}", "not found on class"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    chk = Checker()
    findings = []

    for md in all_chapter_files(args.only):
        for b in iter_blocks(md, langs={"python", "py", "java"}):
            fs = (python_findings if b.lang in ("python", "py") else java_findings)(chk, b)
            for kind, symbol, detail in fs:
                findings.append({
                    "chapter": b.chapter, "lang": b.lang, "block": b.index,
                    "line": b.start_line, "kind": kind, "symbol": symbol,
                    "detail": detail,
                })

    by_kind = defaultdict(int)
    by_chapter = defaultdict(int)
    for f in findings:
        by_kind[f["kind"]] += 1
        by_chapter[f["chapter"]] += 1

    print(f"Total findings: {len(findings)}")
    for k, v in sorted(by_kind.items()):
        print(f"  {k}: {v}")
    print()
    for c, v in sorted(by_chapter.items()):
        print(f"  {c}: {v}")

    if args.json:
        Path(args.json).write_text(json.dumps(findings, indent=2), encoding="utf-8")
        print(f"\nWrote {args.json}")


if __name__ == "__main__":
    main()
