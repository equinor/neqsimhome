"""Re-render the frozen Word candidate after a Word-only publisher correction."""
from book_runtime import BOOK
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from docx import Document


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    record = BOOK / "verification/render_manifest.json"
    manifest = json.loads(record.read_text(encoding="utf-8"))
    previous_stage = Path(manifest["candidate"])
    for name, digest in manifest["source_hashes"].items():
        assert sha(BOOK / name) == sha(previous_stage / name) == digest, name
    for item in manifest["outputs"]:
        assert sha(BOOK / item["path"]) == item["sha256"], item["path"]
    stage = BOOK / "verification" / ("word_candidate_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S"))
    stage.mkdir()
    for name in manifest["source_hashes"]:
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BOOK / name, target)
    args = ["book-render", str(stage), "--format", "docx"]
    run = subprocess.run([sys.executable, "-X", "utf8", str(BOOK / "paperlab_cli.py")] + args,
        capture_output=True, text=True, encoding="utf-8")
    (BOOK / "verification/word_final_refresh_2026-09-13.log").write_text(run.stdout + run.stderr, encoding="utf-8")
    if run.returncode:
        raise RuntimeError("Word refresh failed; previous release was preserved")
    candidate = stage / "submission/book.docx"
    word = Document(candidate)
    math = word.element.xpath(".//m:oMath")
    assert len(math) == 36, "Expected the same 36 mathematical expressions as the reviewed web edition"
    assert all("PythonExe" not in "".join(e.itertext()) for e in math), "Shell variable parsed as mathematics"
    for name, digest in manifest["source_hashes"].items():
        assert sha(stage / name) == digest, name
    shutil.copy2(candidate, BOOK / "submission/book.docx")
    for item in manifest["outputs"]:
        if item["path"].replace("\\", "/") == "submission/book.docx":
            item.update(sha256=sha(BOOK / item["path"]), bytes=(BOOK / item["path"]).stat().st_size)
    manifest["native_commands"].append(args)
    manifest["word_candidate"] = str(stage)
    record.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Frozen Word refreshed; 36 native mathematical expressions and no shell variables in mathematics. A new Word page proof is required.")


if __name__ == "__main__":
    main()
