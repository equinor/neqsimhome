"""Extract page checks and contact sheets from final PDF and a Word PDF proof."""
from book_runtime import BOOK
import argparse
import json
import hashlib
from pathlib import Path
from PIL import Image, ImageDraw
import pdfplumber


def inspect_pdf(path, prefix, image_glob):
    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            outside = [c.get("text", "") for c in page.chars
                       if c["x0"] < -1 or c["x1"] > page.width + 1
                       or c["top"] < -1 or c["bottom"] > page.height + 1]
            pages.append({"page": i, "words": len(text.split()),
                          "first_lines": text.splitlines()[:5],
                          "outside_page_characters": outside,
                          "replacement_glyph": "\ufffd" in text})
    (BOOK / "verification" / (prefix + "_page_map.json")).write_text(
        json.dumps(pages, indent=2, ensure_ascii=False), encoding="utf-8")
    paths = sorted((BOOK / "verification").glob(image_glob))[:len(pages)]
    assert len(paths) == len(pages), "Every page needs a current raster proof"
    for offset in range(0, len(paths), 20):
        sheet = Image.new("RGB", (960, 1740), "#dbe3e8")
        draw = ImageDraw.Draw(sheet)
        for j, p in enumerate(paths[offset:offset + 20]):
            im = Image.open(p).convert("RGB")
            im.thumbnail((226, 320))
            x = (j % 4) * 240 + 7
            y = (j // 4) * 348 + 5
            sheet.paste(im, (x, y + 20))
            draw.text((x, y), str(offset+j+1), fill="#152f44")
        sheet.save(BOOK / "verification" / (prefix + "_contact_" + str(offset // 20 + 1) + ".png"))
    return {"pages": len(pages), "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "outside_page_count": sum(len(p["outside_page_characters"]) for p in pages),
            "replacement_glyph_pages": [p["page"] for p in pages if p["replacement_glyph"]]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf-rasters", default="pdf_pages_2026-09-13_final")
    parser.add_argument("--word-rasters", default="word_pages_2026-09-13_release3")
    args = parser.parse_args()
    report = {}
    for p, prefix, glob in [(BOOK / "submission/book.pdf", "pdf", args.pdf_rasters + "/page-*.png"),
                            (BOOK / "verification/book_word_proof.pdf", "word", args.word_rasters + "/page-*.png")]:
        report[prefix] = inspect_pdf(p, prefix, glob)
    (BOOK / "verification/layout_checks.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
