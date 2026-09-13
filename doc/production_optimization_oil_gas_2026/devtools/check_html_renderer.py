"""Render the two-chapter regression fixture and inspect its actual HTML output.

Run with the user-selected Python; dependencies remain in .build/python_packages.
Only fixture submission files and verification/html_renderer_check.* are written.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

BOOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / ".build" / "python_packages"))
sys.path.insert(0, str(BOOK.parents[1] / "tools"))
from bs4 import BeautifulSoup
import book_render_html


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


MEASURE_SCRIPT = r"""
<script>
window.addEventListener('load', function () {
  setTimeout(function () {
    const width = window.innerWidth;
    const out = [];
    for (const el of document.querySelectorAll('body *')) {
      if (el.closest('script, style, .katex-mathml')) continue;
      // KaTeX SVG paths extend beyond their clipped SVG viewport by design.
      // The surrounding visible math boxes are still measured below.
      if (el instanceof SVGElement) continue;
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      const r = el.getBoundingClientRect();
      if (r.width < 1 || r.height < 1) continue;
      let scrollAncestor = null;
      for (let p = el.parentElement; p && p.tagName !== 'BODY'; p = p.parentElement) {
        if (['auto', 'scroll'].includes(getComputedStyle(p).overflowX)) {
          scrollAncestor = p; break;
        }
      }
      if (!scrollAncestor && (r.left < -1 || r.right > width + 1)) {
        out.push({tag:el.tagName, id:el.id, class:el.className,
          left:r.left, right:r.right, text:el.textContent.trim().slice(0,140)});
      }
    }
    const missingImages = [...document.images]
      .filter(el => !el.complete || !el.naturalWidth).map(el => el.getAttribute('src'));
    const initialY = window.scrollY;
    window.scrollTo(100000, initialY);
    const maximumPageScrollX = window.scrollX;
    window.scrollTo(0, initialY);
    const data = {width, viewportHeight:window.innerHeight,
      bodyScrollWidth:document.body.scrollWidth,
      documentScrollWidth:document.documentElement.scrollWidth,
      maximumPageScrollX,
      mainWidth:document.querySelector('main').getBoundingClientRect().width,
      sidebarDisplay:getComputedStyle(document.querySelector('nav.sidebar')).display,
      overflow:out, missingImages,
      katexAvailable:!!window.katex,
      renderedMathCount:document.querySelectorAll('.katex').length,
      accessibleMathCount:document.querySelectorAll('.katex-mathml math').length,
      katexErrors:[...document.querySelectorAll('.katex-error')].map(el=>el.textContent)};
    const report = document.createElement('script');
    report.type = 'application/json'; report.id = 'renderer-measurements';
    report.textContent = JSON.stringify(data); document.body.appendChild(report);
  }, 1000);
});
</script>
"""


def browser_check(html_path, output_prefix, chrome, widths):
    """Measure layout using Chrome without changing the renderer-produced HTML."""
    source = html_path.read_text(encoding="utf-8")
    source = source.replace("<head>", '<head><base href="' + html_path.as_uri() + '">', 1)
    source = source.replace("</body>", MEASURE_SCRIPT + "</body>", 1)
    probe_path = Path(str(output_prefix) + ".browser.html")
    probe_path.write_text(source, encoding="utf-8")
    measurements = []
    for width in widths:
        with tempfile.TemporaryDirectory(prefix="paperlab_html_check_") as profile:
            screenshot = Path(str(output_prefix) + f".{width}.png")
            command = [str(chrome), "--headless=new", "--disable-gpu",
                       "--no-first-run", "--no-default-browser-check", "--disable-extensions",
                       "--disable-background-networking", "--disable-sync", "--hide-scrollbars",
                       "--allow-file-access-from-files", "--force-device-scale-factor=1",
                       "--run-all-compositor-stages-before-draw",
                       "--user-data-dir=" + profile, f"--window-size={width + 22},900",
                       "--virtual-time-budget=5000", "--dump-dom",
                       "--screenshot=" + str(screenshot), probe_path.as_uri()]
            try:
                result = subprocess.run(command, capture_output=True, timeout=55)
                html = result.stdout.decode("utf-8", errors="replace")
                dom_path = Path(str(output_prefix) + f".{width}.dom.html")
                dom_path.write_text(html, encoding="utf-8")
                Path(str(output_prefix) + f".{width}.browser.log").write_bytes(result.stderr)
                # A full textbook can expand to hundreds of thousands of math
                # DOM nodes. Read the injected JSON record without rebuilding
                # that entire tree in Python.
                marker = re.search(r'<script\b[^>]*\bid="renderer-measurements"[^>]*>(.*?)</script>', html, re.S)
                if marker is None:
                    measurements.append({"width": width, "error": "Chrome produced no measurement marker",
                                         "returncode": result.returncode})
                else:
                    measured = json.loads(marker[1])
                    measured["requestedWidth"] = width
                    measured["screenshot"] = str(screenshot)
                    measurements.append(measured)
            except subprocess.TimeoutExpired:
                measurements.append({"width": width, "error": "Chrome exceeded 55-second limit"})
    return measurements


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=BOOK / ".build" / "renderer_fixture")
    parser.add_argument("--chrome", type=Path,
                        default=Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"))
    parser.add_argument("--skip-browser", action="store_true")
    args = parser.parse_args()
    prefix = BOOK / "verification" / "html_renderer_check"
    prefix.parent.mkdir(exist_ok=True)
    log = io.StringIO()
    renderer_path = Path(book_render_html.__file__)
    renderer_sha = digest(renderer_path)
    with contextlib.redirect_stdout(log):
        output = book_render_html.render_book_html(args.fixture)
    Path(str(prefix) + ".render.log").write_text(log.getvalue(), encoding="utf-8")
    html = Path(output).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    checks = []

    def check(name, passed, detail):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    chapters = soup.select("section.chapter")
    check("two_chapters", len(chapters) == 2, f"Found {len(chapters)}")
    paths = []
    for number, chapter in enumerate(chapters, 1):
        imgs = chapter.select("img")
        captions = [node.get_text(" ", strip=True) for node in chapter.select("figcaption")]
        headings = [node.get_text(" ", strip=True) for node in chapter.select("h2")]
        check(f"chapter_{number}_single_image_no_hero", len(imgs) == 1 and not chapter.select(".ch-hero"),
              f"Images={len(imgs)}, heroes={len(chapter.select('.ch-hero'))}")
        check(f"chapter_{number}_caption", captions == [f"Figure {number}.1: A workflow."], captions)
        check(f"chapter_{number}_manual_heading", headings == ["Learning Objectives", f"{number}.1 Introduction", "Summary"], headings)
        check(f"chapter_{number}_single_title", len(chapter.select("h1")) == 1,
              [node.get_text(" ", strip=True) for node in chapter.select("h1")])
        if imgs:
            image_path = imgs[0].get("src")
            paths.append(image_path)
            expected = f"figures_ch{number:02d}/workflow.svg"
            check(f"chapter_{number}_namespace", image_path == expected, image_path)
            copied = Path(output).parent / expected
            original = args.fixture / "chapters" / f"ch{number:02d}" / "figures" / "workflow.svg"
            check(f"chapter_{number}_image_bytes", copied.is_file() and digest(copied) == digest(original), str(copied))
    check("figure_namespaces_unique", len(paths) == len(set(paths)) == 2, paths)
    check("custom_copyright", soup.get_text().count("CUSTOM_RIGHTS_MARKER") == 1, "Custom rights marker occurs once")
    check("no_default_creative_commons", "Creative Commons" not in soup.get_text(), "No generated Creative Commons license")
    ids = [node["id"] for node in soup.select("[id]")]
    duplicates = sorted({identifier for identifier in ids if ids.count(identifier) > 1})
    check("unique_html_ids", not duplicates, duplicates)
    unresolved = sorted({node.get("href") for node in soup.select('a[href^="#"]')
                         if node.get("href")[1:] not in ids})
    check("navigation_targets_exist", not unresolved, unresolved)
    measurements = []
    if not args.skip_browser:
        if args.chrome.is_file():
            measurements = browser_check(Path(output), prefix, args.chrome, [500, 768, 1024])
            for item in measurements:
                width = item.get("requestedWidth", item["width"])
                check(f"browser_{width}_measurement", "error" not in item, item.get("error", "Measured"))
                if "error" not in item:
                    check(f"browser_{width}_exact_viewport", item["width"] == width, item["width"])
                    check(f"browser_{width}_no_overflow", not item["overflow"], item["overflow"])
                    check(f"browser_{width}_no_page_horizontal_scroll",
                          item["documentScrollWidth"] <= width + 1 and
                          item["bodyScrollWidth"] <= width + 1 and
                          item["maximumPageScrollX"] <= 1,
                          {key: item[key] for key in ["documentScrollWidth", "bodyScrollWidth", "maximumPageScrollX"]})
                    check(f"browser_{width}_images_loaded", not item["missingImages"], item["missingImages"])
                    check(f"browser_{width}_math_rendered", item["renderedMathCount"] == 2 and not item["katexErrors"],
                          {key: item[key] for key in ["katexAvailable", "renderedMathCount", "katexErrors"]})
        else:
            check("browser_available", False, str(args.chrome))
    check("renderer_unchanged_during_check", renderer_sha == digest(renderer_path), renderer_sha)
    report = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "python": sys.executable,
              "renderer": str(renderer_path), "renderer_sha256": renderer_sha,
              "fixture": str(args.fixture), "html": str(output), "html_sha256": digest(output),
              "checks": checks, "browser_measurements": measurements,
              "passed": sum(item["passed"] for item in checks),
              "failed": sum(not item["passed"] for item in checks)}
    Path(str(prefix) + ".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    failed = [item for item in checks if not item["passed"]]
    lines = ["# HTML renderer verification", "", f"{report['passed']} passed; {report['failed']} failed.", "",
             f"Fixture: `{args.fixture}`", f"Renderer SHA-256: `{renderer_sha}`", "",
             "Checks use the rendered output and actual Chrome layout at 500, 768, and 1024 px.",
             "DOM measurements include the entire fixture. Screenshots show the initial viewport.", ""]
    for item in failed:
        lines.append(f"- **{item['name']}**: {item['detail']}")
    if not failed:
        lines.append("No concrete failures found in the two-chapter fixture.")
    lines += ["", "The fixture covers repeated filenames, chapter captions, custom copyright, existing section numbering,",
              "navigation IDs, and disabled chapter hero images. It does not establish full-book layout coverage.", ""]
    Path(str(prefix) + ".md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "failed": report["failed"], "failures": failed}, indent=2))
    return bool(failed)


if __name__ == "__main__":
    raise SystemExit(main())
