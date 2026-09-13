"""Render the maintained book with PaperLab and produce a portable web edition."""
from book_runtime import BOOK
import base64
import hashlib
import json
import mimetypes
import os
import re
import sys
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import pypandoc

PAPERLAB = BOOK.parents[1]
sys.path.insert(0, str(PAPERLAB / "tools"))
os.environ["PATH"] = str(Path(pypandoc.get_pandoc_path()).parent) + os.pathsep + os.environ["PATH"]


def main():
    import book_checker
    issues = book_checker.run_checks(BOOK)
    (BOOK / "verification" / "book_check.json").write_text(json.dumps(issues, indent=2), encoding="utf-8")
    print(book_checker.format_issues(issues), flush=True)
    if any(i["severity"] == "error" for i in issues):
        raise RuntimeError("Book source checks failed")
    # Freeze sources in a new candidate so a failed native build cannot replace
    # the last reviewable release or reuse stale files from an earlier attempt.
    stage = BOOK / "verification" / ("paperlab_candidate_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S"))
    stage.mkdir()
    for name in ("chapters", "frontmatter", "backmatter"):
        shutil.copytree(BOOK / name, stage / name, ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("book.yaml", "refs.bib", "nomenclature.yaml", "book.css", "cover_front.png"):
        if (BOOK / name).exists():
            shutil.copy2(BOOK / name, stage / name)
    source_hashes = {str(p.relative_to(stage)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in stage.rglob("*") if p.is_file()}
    commands = [
        ["book-check", str(stage)],
        ["book-evidence-check", str(stage), "--strict"],
        ["book-build", str(stage), "--format", "all", "--skip-notebooks", "--no-compile",
         "--no-script-notebooks", "--no-notebook-results", "--stop-on-error"],
        ["book-render", str(stage), "--format", "epub"],
    ]
    for index, args in enumerate(commands, 1):
        command = [sys.executable, "-X", "utf8", str(BOOK / "paperlab_cli.py")] + args
        print("PaperLab " + args[0], flush=True)
        run = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        (BOOK / "verification" / f"native_build_{index}.log").write_text(run.stdout + run.stderr, encoding="utf-8")
        if run.returncode or "FAILED" in run.stdout:
            raise RuntimeError("Native " + args[0] + " failed; inspect native_build log")
    assert all(hashlib.sha256((stage / p).read_bytes()).hexdigest() == h for p, h in source_hashes.items()), "Native build altered frozen sources"
    paths = []
    for name in ("book.html", "book.docx", "book.pdf", "book.odt", "book.epub"):
        candidate = stage / "submission" / name
        if not candidate.is_file() or candidate.stat().st_size == 0:
            raise RuntimeError("Missing native candidate " + name)
        target = BOOK / "submission" / name
        shutil.copy2(candidate, target)
        paths.append(target)
    if (stage / "submission/book.typ").exists():
        shutil.copy2(stage / "submission/book.typ", BOOK / "submission/book.typ")
    for asset in (stage / "submission").iterdir():
        if asset.is_dir():
            shutil.copytree(asset, BOOK / "submission" / asset.name, dirs_exist_ok=True)
        elif asset.suffix.lower() in (".png", ".svg", ".css"):
            shutil.copy2(asset, BOOK / "submission" / asset.name)
    html_path = BOOK / "submission" / "book.html"
    html = html_path.read_text(encoding="utf-8")
    def embed(match):
        value = match.group(1)
        if value.startswith(("data:","http:","https:")):
            return match.group(0)
        path = (html_path.parent / value).resolve()
        if not path.is_relative_to(BOOK.resolve()) or not path.is_file():
            raise RuntimeError("Missing or outside-book image: " + value)
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        return 'src="data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode("ascii") + '"'
    html = re.sub(r'src="([^"]+)"', lambda m: embed(m) if not m.group(1).endswith(".js") else m.group(0), html)
    standalone = BOOK / "submission" / "book_standalone.html"
    standalone.write_text(html,encoding="utf-8")
    paths.append(standalone)
    from docx import Document
    word = Document(BOOK / "submission/book.docx")
    paragraphs = word.paragraphs
    assert not any(re.search(r"\[[^\]]+\]\(https?://", p.text) for p in paragraphs), "Unrendered Word hyperlink"
    for index, paragraph in enumerate(paragraphs):
        if paragraph.text.startswith("Figure ") and index:
            previous = paragraphs[index - 1]
            if previous._p.xpath(".//w:drawing"):
                assert previous.paragraph_format.keep_with_next, "Figure separated from its caption"
    assert '&lt;a href=&quot;#ref-' not in html, "Escaped citation markup"
    supporting_assets = [
        {"path": str(Path("submission") / p.relative_to(stage / "submission")),
         "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in (stage / "submission").rglob("*") if p.is_file() and p.suffix.lower() in (".png", ".svg", ".css")]
    manifest={"python":sys.executable,"native_commands": commands,"candidate":str(stage),"source_hashes":source_hashes,
              "supporting_assets": supporting_assets,
              "outputs":[{"path":str(p.relative_to(BOOK)),"bytes":p.stat().st_size,
                "sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
              "web_note":"Images are embedded; equation rendering uses the declared KaTeX resources."}
    (BOOK / "verification" / "render_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(manifest,indent=2),flush=True)


if __name__ == "__main__": main()
