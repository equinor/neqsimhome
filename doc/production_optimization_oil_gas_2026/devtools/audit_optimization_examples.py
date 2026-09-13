"""Execute manuscript Python fences using the explicitly selected source build.

Each chapter is a fresh process/JVM; sequential examples share chapter state.
Results are checkpointed after each fence and preserve exact source hashes.
No published neqsim package, substitute physics, or silent runtime fallback.
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback

BOOK = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get("NEQSIM_PROJECT_ROOT", r"C:\Users\solbraa\OneDrive - NTNU\Documents\ChatGPT\NeqSim"))
PACKAGES = BOOK / ".build" / "python_packages"
sys.path.insert(0, str(PACKAGES))
FENCES = re.compile(r"^```(python|java)([^\n]*)\n(.*?)^```", re.M | re.S)


def child(chapter, only=None):
    sys.path.insert(0, str(SOURCE / "devtools"))
    import jpype
    from neqsim_dev_setup import neqsim_init
    neqsim_init(project_root=SOURCE, recompile=False, verbose=False)
    work = BOOK / ".build" / "fence_runs" / chapter.name
    work.mkdir(parents=True, exist_ok=True)
    os.chdir(work)
    os.environ["MPLBACKEND"] = "Agg"
    namespace = {"__name__": "__main__", "__file__": str(chapter / "chapter.md")}
    result = {"chapter": chapter.name, "source_root": str(SOURCE), "python": sys.executable,
              "execution_model": "sequential Python fences, fresh JVM per chapter", "examples": []}
    output = BOOK / "verification" / (chapter.name + "_fences.json")
    text = (chapter / "chapter.md").read_text(encoding="utf-8-sig")
    for number, match in enumerate(FENCES.finditer(text), 1):
        language, annotation, code = match.groups()
        row = {"number": number, "language": language,
               "line": text.count("\n", 0, match.start()) + 1,
               "sha256": hashlib.sha256(code.encode()).hexdigest()}
        if only and number not in only:
            continue
        if language == "java":
            row["status"] = "pending_java_harness"
        elif "pattern" in annotation:
            row.update(status="integration_pattern", reason=annotation.strip())
        else:
            capture = io.StringIO()
            started = time.monotonic()
            try:
                with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
                    exec(compile(code, f"{chapter.name}:fence{number}", "exec"), namespace)
                row["status"] = "passed"
            except BaseException as exc:
                row.update(status="failed", error=f"{type(exc).__name__}: {exc}", traceback=traceback.format_exc())
            row["seconds"] = round(time.monotonic() - started, 3)
            row["output"] = capture.getvalue()
        result["examples"].append(row)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{chapter.name} {number} {row['status']} {row.get('error','')[:160]}", flush=True)
    # Some optimizer examples own non-daemon executor pools. A chapter worker
    # is disposable; all artifacts are flushed before terminating its JVM.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", type=int)
    parser.add_argument("--only")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--start", type=int, default=19)
    parser.add_argument("--chapters")
    args = parser.parse_args()
    if args.chapter:
        chapter = next((BOOK / "chapters").glob(f"ch{args.chapter:02d}_*"))
        child(chapter, set(map(int, args.only.split(","))) if args.only else None)
    else:
        numbers=list(map(int,args.chapters.split(','))) if args.chapters else range(args.start,36)
        for number in numbers:
            env = dict(os.environ, PYTHONIOENCODING="utf-8", MPLBACKEND="Agg",
                       PYTHONPATH=str(PACKAGES), NEQSIM_PROJECT_ROOT=str(SOURCE), _JAVA_OPTIONS="-Xmx512m")
            log = BOOK / "verification" / f"ch{number:02d}_fence_run.log"
            with log.open("w", encoding="utf-8") as handle:
                try:
                    run = subprocess.run([sys.executable, __file__, "--chapter", str(number)],
                                         stdout=handle, stderr=subprocess.STDOUT, env=env,
                                         timeout=900)
                    print(number, run.returncode, flush=True)
                except subprocess.TimeoutExpired:
                    print(number, "TIMEOUT", flush=True)


if __name__ == "__main__":
    main()
