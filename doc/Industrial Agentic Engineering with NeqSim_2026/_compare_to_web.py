"""Compare rendered book.html vs. the published web version."""
import re, urllib.request, pathlib

WEB_URL = "https://equinor.github.io/neqsimhome/doc/agentic%20engineering/book.html"
LOCAL   = pathlib.Path("submission/book.html")

web   = urllib.request.urlopen(WEB_URL, timeout=30).read().decode("utf-8", "ignore")
local = LOCAL.read_text(encoding="utf-8")

def strip_html(s: str) -> str:
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<style.*?</style>",   " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s)

wt, lt = strip_html(web), strip_html(local)
print(f"Web    text: {len(wt):>8} chars   {len(wt.split()):>6} words")
print(f"Local  text: {len(lt):>8} chars   {len(lt.split()):>6} words")

print(f"Web    <img> tags: {len(re.findall(r'<img\b', web, re.I))}")
print(f"Local  <img> tags: {len(re.findall(r'<img\b', local, re.I))}")

def heads(s):
    return [re.sub(r"<[^>]+>", " ", h).strip()
            for h in re.findall(r"<h[12][^>]*>(.*?)</h[12]>", s, re.I | re.S)]

wh, lh = heads(web), heads(local)
print(f"Web    H1/H2: {len(wh)}")
print(f"Local  H1/H2: {len(lh)}")

ws = {h.lower() for h in wh}
ls = {h.lower() for h in lh}
only_web = [h for h in wh if h.lower() not in ls]
only_loc = [h for h in lh if h.lower() not in ws]

print(f"\nOnly on web (count={len(only_web)}, first 15):")
for h in only_web[:15]:
    print("  W>", h[:90])

print(f"\nOnly local (count={len(only_loc)}, first 15):")
for h in only_loc[:15]:
    print("  L>", h[:90])
