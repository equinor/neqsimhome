import re
from pathlib import Path

new_path = Path(r"C:\Users\ESOL\Documents\GitHub\neqsim\neqsim-paperlab\books\production_optimization_oil_gas_2026\submission\book.html")
ref_path = Path(r"C:\Users\ESOL\Documents\GitHub\neqsimhome\doc\production optimization\book.html")

new = new_path.read_text(encoding="utf-8", errors="ignore")
ref = ref_path.read_text(encoding="utf-8", errors="ignore")

def strip(html):
    t = re.sub(r"<script[\s\S]*?</script>", " ", html)
    t = re.sub(r"<style[\s\S]*?</style>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()

new_text = strip(new)
ref_text = strip(ref)

print(f"New text chars : {len(new_text):>10,}")
print(f"Ref text chars : {len(ref_text):>10,}")
print(f"New words      : {len(new_text.split()):>10,}")
print(f"Ref words      : {len(ref_text.split()):>10,}")

# Count equations (MathJax/KaTeX display and inline)
for name, pat in [
    ("inline $...$",  r"\$[^$\n]+?\$"),
    ("display $$...$$", r"\$\$[\s\S]+?\$\$"),
    ("\\(...\\)",     r"\\\([\s\S]+?\\\)"),
    ("\\[...\\]",     r"\\\[[\s\S]+?\\\]"),
    ("<math",         r"<math"),
    ("class=\"katex", r"class=\"katex"),
]:
    n = len(re.findall(pat, new))
    r = len(re.findall(pat, ref))
    print(f"{name:20s}  new={n:5d}  ref={r:5d}")

# Per-chapter text length (split by h1 with chapter number)
def split_chapters(html):
    # split at each <h1 ...>N Title</h1> where N is a digit
    parts = re.split(r'<h1[^>]*>(?:Chapter\s+)?(\d+)[^<]*</h1>', html)
    # parts[0] = preamble, then pairs (num, content)
    chaps = {}
    for i in range(1, len(parts)-1, 2):
        num = int(parts[i])
        content_text = strip(parts[i+1])
        chaps[num] = len(content_text.split())
    return chaps

nc = split_chapters(new)
rc = split_chapters(ref)
print("\n{:>4}  {:>10}  {:>10}  {:>10}".format("Ch", "new words", "ref words", "diff"))
for i in range(1, 36):
    n = nc.get(i, 0)
    r = rc.get(i, 0)
    diff = n - r
    flag = " !!" if n < r * 0.5 else ""
    print(f"{i:>4}  {n:>10,}  {r:>10,}  {diff:>+10,}{flag}")
