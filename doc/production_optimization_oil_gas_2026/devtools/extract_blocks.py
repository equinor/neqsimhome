"""Extract fenced code blocks from chapter.md files.

Shared by verify_python_blocks.py and verify_java_blocks.py.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

BOOK_DIR = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = BOOK_DIR / "chapters"

FENCE_RE = re.compile(r"^```([A-Za-z0-9_+-]*)[ \t]*$", re.M)


@dataclass
class Block:
    chapter: str
    path: Path
    index: int
    lang: str
    start_line: int
    code: str

    @property
    def ref(self) -> str:
        return f"{self.chapter}#{self.index} (line {self.start_line})"


def iter_blocks(path: Path, langs=None):
    """Yield Block objects for fenced code blocks in a markdown file."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    chapter = path.parent.name

    out = []
    i = 0
    idx = 0
    while i < len(lines):
        m = FENCE_RE.match(lines[i])
        if not m:
            i += 1
            continue
        lang = m.group(1).lower()
        start = i + 1
        j = i + 1
        while j < len(lines) and not lines[j].startswith("```"):
            j += 1
        code = "\n".join(lines[start:j])
        if langs is None or lang in langs:
            out.append(Block(chapter, path, idx, lang, start + 1, code))
        idx += 1
        i = j + 1
    return out


def all_chapter_files(only=None):
    files = sorted(CHAPTERS_DIR.glob("*/chapter.md"))
    if only:
        files = [f for f in files if only in f.parent.name]
    return files
