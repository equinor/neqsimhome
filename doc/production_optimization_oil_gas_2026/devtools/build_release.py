"""Build review candidates through canonical PaperLab renderers; preserve published files."""
from pathlib import Path
import argparse
import base64
import datetime
import hashlib
import importlib
import json
import mimetypes
import os
import re
import shutil
import sys

BOOK = Path(__file__).resolve().parents[1]
PAPERLAB = BOOK.parents[1]
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path[:0] = [str(BOOK / '.build/python_packages'), str(PAPERLAB / 'tools')]
import pypandoc
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('--formats', default='html,pdf,docx,odf')
parser.add_argument('--promote', action='store_true')
args = parser.parse_args()
stage = BOOK / '.build/release_candidate'
stage.mkdir(parents=True, exist_ok=True)
os.environ['PATH'] = str(Path(pypandoc.get_pandoc_path()).parent) + os.pathsep + os.environ['PATH']

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source_snapshot():
    files = [BOOK / name for name in ('book.yaml', 'refs.bib', 'nomenclature.yaml', 'cover_front.png')]
    files += list((BOOK / 'frontmatter').glob('*.md')) + list((BOOK / 'backmatter').glob('*.md'))
    files += list((BOOK / 'chapters').glob('*/chapter.md'))
    files += [p for p in (BOOK / 'chapters').glob('*/figures/*') if p.suffix.lower() in ('.png', '.jpg', '.svg', '.jpeg')]
    return {str(p.relative_to(BOOK)): digest(p) for p in files if p.is_file()}

snapshot = source_snapshot()
renderer_snapshot = {str(PAPERLAB / 'tools' / name): digest(PAPERLAB / 'tools' / name)
    for name in ('book_builder.py', 'book_render_pdf.py', 'book_render_html.py',
                 'render_pdf.py', 'citation_utils.py', 'katex_head.py')}
for name in ('book.yaml', 'refs.bib', 'nomenclature.yaml', 'cover_front.png'):
    shutil.copy2(BOOK / name, stage / name)
for name in ('frontmatter', 'backmatter'):
    shutil.copytree(BOOK / name, stage / name, dirs_exist_ok=True)
cfg = yaml.safe_load((stage / 'book.yaml').read_text(encoding='utf-8'))
for part in cfg['parts']:
    for chapter in part['chapters']:
        chapter['dir'] = str(BOOK / 'chapters' / chapter['dir'])
(stage / 'book.yaml').write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding='utf-8')

renderers = {'html': ('book_render_html', 'render_book_html'), 'pdf': ('book_render_pdf', 'render_book_pdf'),
             'docx': ('book_render_word', 'render_book_word'), 'odf': ('book_render_odf', 'render_book_odf')}
outputs = []
for format in args.formats.split(','):
    module, function = renderers[format]
    print('Rendering', format, flush=True)
    result = getattr(importlib.import_module(module), function)(stage)
    if result is None:
        raise RuntimeError(f'{format} did not produce an artifact')
    outputs.append(Path(result))
    if format == 'html':
        html_path = Path(result)
        html_text = html_path.read_text(encoding='utf-8')
        def embed(match):
            url = match[1]
            if url.startswith(('http:', 'https:', 'data:')):
                return match[0]
            file = (html_path.parent / url).resolve()
            if not file.is_file():
                raise FileNotFoundError(f'Missing HTML image: {url}')
            mime = mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
            return 'src="data:' + mime + ';base64,' + base64.b64encode(file.read_bytes()).decode() + '"'
        standalone = re.sub(r'src="([^\"]+)"', embed, html_text)
        embedded = html_path.with_name('book_standalone.html')
        embedded.write_text(standalone, encoding='utf-8')
        outputs.append(embedded)

changed = [name for name, sha in snapshot.items() if not (BOOK / name).exists() or digest(BOOK / name) != sha]
changed_renderers = [name for name, sha in renderer_snapshot.items() if digest(Path(name)) != sha]
report = {'built_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'python': sys.executable,
          'source_sha256': snapshot, 'changed_during_render': changed,
          'renderer_sha256': renderer_snapshot, 'renderers_changed_during_render': changed_renderers,
          'artifacts': [{'path': str(p), 'bytes': p.stat().st_size, 'sha256': digest(p)} for p in outputs]}
(BOOK / 'verification/render_manifest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
if changed:
    raise RuntimeError('Source changed during rendering; regenerate before promotion: ' + ', '.join(changed))
if changed_renderers:
    raise RuntimeError('Renderer changed during rendering; regenerate before promotion: ' + ', '.join(changed_renderers))
if args.promote:
    # Promotion is explicit so visual review can finish on the staged PDF first.
    destination = BOOK / 'submission'
    backup = BOOK / '.build/previous_publication'
    destination.mkdir(exist_ok=True)
    backup.mkdir(exist_ok=True)
    for name in ('book.pdf', 'book.html', 'book_standalone.html', 'book.docx', 'book.odt'):
        old = destination / name
        if old.exists() and not (backup / name).exists():
            shutil.copy2(old, backup / name)
    shutil.copytree(stage / 'submission', destination, dirs_exist_ok=True)
    print('Updated publication files in', destination)
print('Build manifest:', BOOK / 'verification/render_manifest.json')
