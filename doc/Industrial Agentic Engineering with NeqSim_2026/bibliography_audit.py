"""Retrieve authoritative DOI metadata for the reviewed bibliography candidates."""
from pathlib import Path
import json
import sys
import time
import urllib.parse
import urllib.request

import book_runtime

BOOK = Path(__file__).resolve().parent
sys.path.insert(0, str(BOOK.parents[1] / "tools"))
from citation_utils import parse_bibtex

entries = parse_bibtex(BOOK / "refs.enriched.bib")
dois = {key: value["doi"] for key, value in entries.items() if value.get("doi")}
dois.update({"michelsen1982b": "10.1016/0378-3812(82)85002-4",
             "sloan2008": "10.1201/9781420008494"})
output = BOOK / "verification" / "bibliography_metadata.json"
records = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
for key, doi in dois.items():
    if records.get(key, {}).get("status") == "retrieved":
        continue
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    request = urllib.request.Request(url, headers={"User-Agent": "NeqSim-PaperLab-bibliography-audit/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            metadata = json.loads(response.read().decode("utf-8"))["message"]
        records[key] = {"status": "retrieved", "url": url, "retrieved": "2026-09-12",
                        "metadata": metadata}
        print(key, metadata.get("title"), metadata.get("issued"), metadata.get("page"), flush=True)
    except Exception as exc:
        records[key] = {"status": "unavailable", "url": url, "retrieved": "2026-09-12",
                        "error": str(exc)}
        print(key, str(exc), flush=True)
    output.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    time.sleep(1)
