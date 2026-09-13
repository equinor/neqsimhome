"""Inventory and page the scientific manuscript review without changing sources."""
from pathlib import Path
import re
import json
import shutil
import hashlib
import sys
sys.stdout.reconfigure(encoding="utf-8")

BOOK = Path(__file__).resolve().parents[1]
OUT = BOOK / "verification" / "scientific_revision"
BACKUP = BOOK / ".build" / "scientific_revision_foundations_originals"
OUT.mkdir(exist_ok=True, parents=True)
BACKUP.mkdir(exist_ok=True)
chapters = sorted((BOOK / "chapters").glob("*/chapter.md"))[:18]
inventory = []
for path in chapters:
    source = path.read_text(encoding="utf-8")
    backup = BACKUP / (path.parent.name + ".md")
    if not backup.exists():
        shutil.copy2(path, backup)
    blocks = []
    def replace_block(match):
        code = match[2]
        blocks.append({"index": len(blocks) + 1, "language": match[1],
                       "line": source[:match.start()].count("\n") + 1,
                       "sha256": hashlib.sha256(code.encode()).hexdigest(), "code": code})
        return f"[CODE {len(blocks)}: {match[1]}, {len(code.splitlines())} lines; retained in inventory]"
    prose = re.sub(r"(?ms)^```([^\n]*)\n(.*?)^```", replace_block, source)
    row = {"chapter": path.parent.name, "path": str(path),
           "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
           "source_lines": len(source.splitlines()), "prose_characters": len(prose), "blocks": blocks}
    inventory.append(row)
    if len(sys.argv) > 1 and path.parent.name.startswith(sys.argv[1]):
        if len(sys.argv) > 2 and sys.argv[2] == "code":
            for block in blocks:
                print("BLOCK", block["index"], "LINE", block["line"], block["language"])
                print(block["code"])
        else:
            start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            count = int(sys.argv[3]) if len(sys.argv) > 3 else 30000
            print(prose[start:start+count])
            print(f"[Review character interval {start}:{min(start+count,len(prose))} / {len(prose)}]")
if len(sys.argv) == 1:
    print(json.dumps([{k:v for k,v in row.items() if k != "blocks"} for row in inventory], indent=2))
(OUT / "foundations_inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
