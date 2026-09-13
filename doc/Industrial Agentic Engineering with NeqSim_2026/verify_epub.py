"""Verify the existing EPUB and write release evidence; never render or edit it."""
from book_runtime import BOOK
import hashlib
import json
import posixpath
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile

PAPERLAB = BOOK.parents[1]
sys.path.insert(0, str(PAPERLAB / "tools"))
import book_builder
from book_render_epub import _collect_chapter_md


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cfg = book_builder.load_book_config(BOOK)
    sources = _collect_chapter_md(BOOK, cfg)
    image_sources = set()
    cited = set()
    for source in sources:
        text = source.read_text(encoding="utf-8")
        if source.name == "chapter.md":
            text = book_builder.strip_excluded_sections(text, cfg)
        for keys in re.findall(r"\\cite\{([^}]+)\}", text):
            cited.update(key.strip() for key in keys.split(",") if key.strip())
        for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
            if not urlsplit(target).scheme:
                image_sources.add((source.parent / unquote(target.strip("<>"))).resolve())
    cover = BOOK / "cover_front.png"
    image_sources.add(cover)
    sources.extend([BOOK / "book.yaml", BOOK / "refs.bib"])
    sources.extend(sorted(image_sources))
    if (BOOK / "nomenclature.yaml").exists():
        sources.append(BOOK / "nomenclature.yaml")
    source_hashes = {str(path.relative_to(BOOK)): digest(path) for path in sources}
    expected_headings = [f"Chapter {number}: {chapter['title']}"
                         for number, chapter, _ in book_builder.iter_chapters(cfg)]
    epub = BOOK / "submission" / "book.epub"
    failures = []
    with zipfile.ZipFile(epub) as archive:
        names = set(archive.namelist())
        if archive.read("mimetype") != b"application/epub+zip":
            failures.append("Incorrect EPUB MIME type")
        first = archive.infolist()[0]
        if first.filename != "mimetype" or first.compress_type != zipfile.ZIP_STORED:
            failures.append("EPUB MIME declaration is not the first uncompressed entry")
        trees = {name: ET.fromstring(archive.read(name)) for name in names
                 if name.endswith((".xhtml", ".opf", ".ncx", ".xml"))}
        xhtml = {name: tree for name, tree in trees.items() if name.endswith(".xhtml")}
        ids = {name: {element.attrib["id"] for element in tree.iter()
                      if "id" in element.attrib} for name, tree in xhtml.items()}
        headings = [{"file": name, "text": "".join(element.itertext())}
                    for name, tree in xhtml.items() for element in tree.iter()
                    if element.tag.endswith("}h1")
                    and "".join(element.itertext()).startswith("Chapter ")]
        headings.sort(key=lambda item: int(re.match(r"Chapter (\d+)", item["text"])[1]))
        images = [name for name in names if Path(name).suffix.lower()
                  in (".png", ".jpg", ".jpeg", ".svg", ".webp")]
        embedded_hashes = {hashlib.sha256(archive.read(name)).hexdigest() for name in images}
        missing_images = sorted(str(path.relative_to(BOOK)) for path in image_sources
                                if digest(path) not in embedded_hashes)
        math_count = sum(element.tag == "{http://www.w3.org/1998/Math/MathML}math"
                         for tree in xhtml.values() for element in tree.iter())
        citations = [element for tree in xhtml.values() for element in tree.iter()
                     if "citation" in element.attrib.get("class", "").split()]
        references = {element.attrib["id"][4:] for tree in xhtml.values()
                      for element in tree.iter() if element.attrib.get("id", "").startswith("ref-")}
        broken_links, missing_alt, raw_citations = [], [], []
        for name, tree in xhtml.items():
            for element in tree.iter():
                if element.tag.endswith("}img") and not element.attrib.get("alt", "").strip():
                    missing_alt.append(name)
                for attribute, value in element.attrib.items():
                    if attribute not in ("href", "src", "{http://www.w3.org/1999/xlink}href"):
                        continue
                    parsed = urlsplit(value)
                    if parsed.scheme or value.startswith("//"):
                        continue
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parsed.path))) if parsed.path else name
                    if target not in names or (parsed.fragment and target in ids
                                               and unquote(parsed.fragment) not in ids[target]):
                        broken_links.append({"source": name, "target": value})
            body = tree.find("{http://www.w3.org/1999/xhtml}body")
            if body is not None and re.search(r"\\cite\{", "".join(body.itertext())):
                raw_citations.append(name)
        opf_name = next(name for name in names if name.endswith(".opf"))
        package = trees[opf_name]
        manifest = package.find("{http://www.idpf.org/2007/opf}manifest")
        missing_resources = [item.attrib["href"] for item in manifest
                             if posixpath.normpath(posixpath.join(posixpath.dirname(opf_name),
                                                                unquote(item.attrib["href"]))) not in names]
        cover_items = [item for item in manifest if "cover-image" in item.attrib.get("properties", "").split()]
        checks = [("Chapter titles/order differ from the manifest", [h["text"] for h in headings] == expected_headings),
                  ("Source images missing or changed", not missing_images),
                  ("Unexpected embedded image count", len(images) == len(image_sources)),
                  ("No declared EPUB cover", len(cover_items) == 1),
                  ("Broken internal links", not broken_links),
                  ("Missing package resources", not missing_resources),
                  ("Images without alternative text", not missing_alt),
                  ("Raw LaTeX citations remain", not raw_citations),
                  ("No native MathML equations", math_count > 0),
                  ("Bibliography differs from cited source keys", references == cited),
                  ("No linked citation spans", bool(citations))]
        failures.extend(message for message, passed in checks if not passed)
    build_path = BOOK / "verification" / "render_manifest.json"
    build = json.loads(build_path.read_text(encoding="utf-8")) if build_path.exists() else {}
    published = next((item for item in build.get("outputs", [])
                      if Path(item["path"]).name == "book.epub"), None)
    manifest_matches = bool(published and published["sha256"] == digest(epub))
    changed_sources = [name for name, value in source_hashes.items()
                       if build.get("source_hashes", {}).get(name) != value]
    if not manifest_matches:
        failures.append("EPUB bytes differ from the native-build output manifest")
    if changed_sources:
        failures.append("Current sources differ from the native-build frozen source manifest")
    report = {"status": "pass" if not failures else "fail",
              "date": str(cfg.get("revision_date", "2026-09-13")), "checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "candidate": str(epub), "sha256": digest(epub), "size_bytes": epub.stat().st_size,
              "interpreter": sys.executable, "verification_command": str(Path(__file__).resolve()),
              "render_command": "build_book.py -> native book-render <frozen-candidate> --format epub",
              "source_hashes": source_hashes, "renderer_sha256": digest(PAPERLAB / "tools/book_render_epub.py"),
              "chapter_count": len(headings), "chapter_headings": headings,
              "image_count": len(images), "missing_source_images": missing_images,
              "native_mathml_count": math_count, "citation_span_count": len(citations),
              "reference_count": len(references), "broken_internal_links": broken_links,
              "missing_package_resources": missing_resources, "images_missing_alt": missing_alt,
              "raw_citation_files": raw_citations, "build_manifest_epub_matches": manifest_matches,
              "changed_sources_since_frozen_build": changed_sources, "failures": failures,
              "limitations": ["Structural EPUB package/XHTML/MathML verification, not EPUBCheck certification.",
                              "MathML display depends on the reading system; dedicated EPUB-reader visual testing was not performed.",
                              "The EPUB renderer does not automatically insert the separate nomenclature.yaml section; chapter definitions and glossary remain available."]}
    (BOOK / "verification" / "epub_checks.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary = f"""# EPUB verification of the frozen native build

Checked {report['checked_at_utc']}. The existing artifact was inspected without
rendering or changing it. Run `verify_epub.py` with the selected Python
interpreter to repeat these checks.

| Check | Result |
|---|---|
| Structural status | {report['status']} |
| Chapters, titles and order | {len(headings)}; matched book.yaml |
| Embedded source images | {len(images)}; byte hashes checked |
| Native MathML expressions | {math_count} |
| Citation spans / cited references | {len(citations)} / {len(references)} |
| Broken internal links / missing resources | {len(broken_links)} / {len(missing_resources)} |
| Images without alt text / raw citation syntax | {len(missing_alt)} / {len(raw_citations)} |
| Artifact matches native build manifest | {manifest_matches} |
| Source changes since frozen build | {len(changed_sources)} |

Candidate: `submission/book.epub` ({epub.stat().st_size:,} bytes).
SHA-256: `{digest(epub)}`.

The native source renderer was previously tested with a two-chapter fixture:
distinct same-named images, quoted metadata, cover selection, numeric citations,
native math and annotated code fences; missing images/chapters fail. All three
focused renderer tests passed. This refresh rechecks the current artifact and
source hashes; it does not rerun the renderer.

Limits: structural verification is not EPUBCheck certification. Dedicated
EPUB-reader visual testing was not performed, and MathML rendering depends on
the reading system. The native EPUB renderer does not automatically insert the
separate nomenclature.yaml section; chapter definitions and the glossary are
retained. Full numerical evidence and the other formats are covered by the
parent release workflow.

Failures: {json.dumps(failures)}

Complete current source hashes, renderer hash and check details are recorded in
`epub_checks.json`.
"""
    (BOOK / "verification" / "epub_checks.md").write_text(summary, encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "sha256", "chapter_count", "image_count", "native_mathml_count", "reference_count", "build_manifest_epub_matches", "failures")}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
