"""Install reviewed image-generator art without replacing numerical plots."""
from book_runtime import BOOK
from pathlib import Path
import hashlib
import json
import shutil

MANIFEST = BOOK / "illustrations" / "imagegen_manifest_2026-09-13.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def install():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    archive = BOOK / "revision_history" / "illustrations_before_2026-09-13"
    for item in data["assets"]:
        source = Path(item["generated_source"])
        master = BOOK / item["master"]
        active = BOOK / item["active"]
        for target in (master, active):
            if not target.resolve().is_relative_to(BOOK.resolve()):
                raise ValueError("Asset destinations must stay inside this book")
            target.parent.mkdir(parents=True, exist_ok=True)
        if not master.exists():
            shutil.copy2(source, master)
        for previous in (active, active.with_suffix(".svg")):
            saved = archive / previous.relative_to(BOOK)
            if previous.exists() and not saved.exists():
                saved.parent.mkdir(parents=True, exist_ok=True)
                if not saved.resolve().is_relative_to(BOOK.resolve()):
                    raise ValueError("Archive must remain inside the book")
                shutil.copy2(previous, saved)
            # An older SVG must not take precedence over the new raster in Word.
            if previous.suffix == ".svg" and previous.exists():
                if not previous.resolve().is_relative_to(BOOK.resolve()):
                    raise ValueError("Previous asset outside book")
                moved = archive / (previous.stem + "_retired.svg")
                if not moved.exists():
                    shutil.move(str(previous), str(moved))
        shutil.copy2(master, active)
        item["sha256"] = sha(master)
        item["status"] = "generated_and_visually_reviewed"
    MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Installed {len(data['assets'])} reviewed cover/chapter assets")


def chapter_art(chapter):
    if not MANIFEST.exists():
        return []
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = [i for i in data["assets"] if i.get("chapter") == chapter]
    for item in items:
        master = BOOK / item["master"]
        assert sha(master) == item["sha256"], "Reviewed image master changed"
        active = BOOK / item["active"]
        active.parent.mkdir(parents=True, exist_ok=True)
        if not active.exists() or sha(active) != item["sha256"]:
            shutil.copy2(master, active)
    return items


if __name__ == "__main__":
    install()
