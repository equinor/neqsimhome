"""Focused real-glossary evidence using the canonical PDF renderer."""
from pathlib import Path
import sys
import json
import re
import hashlib

BOOK = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "glossary_fixture"
PAPERLAB = BOOK.parents[1]
sys.path[:0] = [str(BOOK / ".build/python_packages"), str(PAPERLAB / "tools")]
import yaml
import pypandoc
import typst
import pymupdf
import book_render_pdf

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

config = yaml.safe_load((BOOK / "book.yaml").read_text(encoding="utf-8"))
preamble = book_render_pdf.build_book_typst_preamble(config).split("// ── Title Page ──")[0]
glossary = BOOK / "backmatter/glossary.md"
markdown = glossary.read_text(encoding="utf-8")
fragment = book_render_pdf.postprocess_typst(pypandoc.convert_text(
    markdown, "typst", format="md", extra_args=["--wrap=none"]))
intro = "#set heading(numbering: none)\n= Before Glossary\nA preceding section with substantive text.\n#pagebreak()\n"
source = OUT / "canonical_fixed.typ"
source.write_text(preamble + intro + fragment, encoding="utf-8")
pdf = OUT / "canonical_fixed.pdf"
pdf.write_bytes(typst.compile(str(source)))
doc = pymupdf.open(pdf)
checks = []
pages = []

def check(name, condition, details=None):
    checks.append({"check": name, "passed": bool(condition), "details": details})

check("glossary spans several pages", len(doc) > 3, len(doc))
check("heading shares first glossary page with actual first row",
      "Glossary" in doc[1].get_text() and "AGA" in doc[1].get_text())
terms = re.findall(r"^\| \*\*(.*?)\*\* \|", markdown, re.M)
term_locations = []
for term in terms:
    matches = []
    for number, page in enumerate(doc, 1):
        for rect in page.search_for(term):
            # Terms occupy the first column; definitions may mention them too.
            if rect.x0 < 190:
                matches.append({"page": number, "rect": list(rect)})
    check("term visible: " + term, bool(matches), matches)
    term_locations.append({"term": term, "locations": matches})

for i, page in enumerate(doc):
    lines = [(line["bbox"], "".join(s["text"] for s in line["spans"]))
             for block in page.get_text("dict")["blocks"] if block["type"] == 0
             for line in block["lines"]]
    body = [(box, text) for box, text in lines
            if box[1] > 48 and not text.strip().isdigit()]
    image = OUT / ("canonical_fixed_%02d.png" % (i + 1))
    page.get_pixmap(matrix=pymupdf.Matrix(1.7, 1.7)).save(image)
    if i:
        check("page %d has substantive rows" % (i + 1), sum(len(t) for _, t in body) > 500)
        check("page %d repeats column headings" % (i + 1), "Term\nDefinition\n" in page.get_text())
        check("page %d body remains within bottom margin" % (i + 1),
              all(box[3] < page.rect.height - 35 for box, _ in body))
        # Same-column line boxes cannot overlap vertically; paired columns can.
        definitions = [(box, text) for box, text in body if box[0] >= 185]
        overlapping = [(a[1], b[1]) for a, b in zip(definitions, definitions[1:])
                       if b[0][1] < a[0][3] - 0.1]
        check("page %d definition lines do not overlap" % (i + 1), not overlapping, overlapping)
    pages.append({"page": i + 1, "characters": len(page.get_text()),
                  "image": str(image), "image_sha256": sha(image)})
check("final definition complete", "complete burner-compatibility test" in
      doc[-1].get_text().replace("\u00ad\n", "").replace("\n", " "))
report = {"passed": all(c["passed"] for c in checks), "python": sys.executable,
          "renderer": str(PAPERLAB / "tools/book_render_pdf.py"),
          "renderer_sha256": sha(PAPERLAB / "tools/book_render_pdf.py"),
          "source_glossary_sha256": sha(glossary), "glossary_terms": len(terms),
          "fixed_pdf": str(pdf), "fixed_pdf_sha256": sha(pdf),
          "baseline_pdf_sha256": sha(OUT / "baseline.pdf"),
          "page_count": len(doc), "checks": checks, "term_locations": term_locations,
          "pages": pages, "manual_visual_review": "pending",
          "cause": "Native figure wrapper remained unbreakable despite a breakable custom inner block.",
          "fix": "Show-set table figure's native block to breakable.",
          "documentation": "https://typst.app/docs/reference/model/figure/#breaking-figures-across-pages"}
destination = OUT.parent / "glossary_pagination_fix.json"
destination.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({"passed": report["passed"], "checks": len(checks),
                  "failed": [c for c in checks if not c["passed"]],
                  "renderer_sha256": report["renderer_sha256"]}, indent=2))
assert report["passed"]
