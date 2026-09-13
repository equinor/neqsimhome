"""Render a review PDF without overwriting the existing publication."""
from pathlib import Path
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BOOK = Path(__file__).resolve().parents[1]
PAPERLAB = BOOK.parents[1]
PACKAGES = BOOK / '.build' / 'python_packages'
sys.path[:0] = [str(PACKAGES), str(PAPERLAB / 'tools')]
import pypandoc
import yaml
os.environ['PATH'] = str(Path(pypandoc.get_pandoc_path()).parent) + os.pathsep + os.environ['PATH']
stage = BOOK / '.build' / 'print_preview'
stage.mkdir(parents=True, exist_ok=True)
for name in ['book.yaml', 'refs.bib', 'nomenclature.yaml', 'cover_front.png']:
    shutil.copy2(BOOK / name, stage / name)
for name in ['frontmatter', 'backmatter']:
    shutil.copytree(BOOK / name, stage / name, dirs_exist_ok=True)
cfg = yaml.safe_load((stage / 'book.yaml').read_text(encoding='utf-8'))
for part in cfg['parts']:
    for chapter in part['chapters']:
        chapter['dir'] = str(BOOK / 'chapters' / chapter['dir'])
(stage / 'book.yaml').write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding='utf-8')
from book_render_pdf import render_book_pdf
result = render_book_pdf(stage)
if result is None:
    raise SystemExit('Preview render failed')
print(result)
