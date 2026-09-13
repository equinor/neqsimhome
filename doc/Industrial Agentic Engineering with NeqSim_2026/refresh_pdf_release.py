"""Re-render only the frozen PDF candidate after a PDF-only publisher correction."""
from book_runtime import BOOK
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone


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
    # A fresh candidate avoids trying to remove an output directory locked by
    # sync software and never replaces the last reviewable release on failure.
    stage = BOOK / "verification" / ("pdf_candidate_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S"))
    stage.mkdir()
    for name in manifest["source_hashes"]:
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BOOK / name, target)
    args = ["book-render", str(stage), "--format", "pdf"]
    run = subprocess.run([sys.executable, "-X", "utf8", str(BOOK / "paperlab_cli.py")] + args,
        capture_output=True, text=True, encoding="utf-8")
    (BOOK / "verification/pdf_final_refresh_2026-09-13.log").write_text(run.stdout + run.stderr, encoding="utf-8")
    if run.returncode:
        raise RuntimeError("PDF refresh failed; previous release was preserved")
    for name in ("book.pdf", "book.typ"):
        shutil.copy2(stage / "submission" / name, BOOK / "submission" / name)
    for item in manifest["outputs"]:
        if item["path"].replace("\\", "/") == "submission/book.pdf":
            item.update(sha256=sha(BOOK / item["path"]), bytes=(BOOK / item["path"]).stat().st_size)
    manifest["native_commands"].append(args)
    manifest["pdf_candidate"] = str(stage)
    record.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Frozen PDF refreshed. Other editions are byte-identical; a new PDF page proof is required.")


if __name__ == "__main__":
    main()
