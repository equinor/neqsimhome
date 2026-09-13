"""Build and structurally inspect unreleased editable candidates with PaperLab."""
import argparse
import hashlib
import json
import io
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
import zipfile
import xml.etree.ElementTree as ET

BOOK = Path(__file__).resolve().parents[1]
PAPERLAB = BOOK.parents[1]
STAGE = BOOK / '.build' / 'editable_candidate'
sys.path.insert(0, str(BOOK / '.build' / 'python_packages'))
sys.path.insert(0, str(PAPERLAB / 'tools'))
import yaml
import book_builder
import book_render_word
import book_render_odf

RUNTIME = Path(r'C:\Users\solbraa\.cache\codex-runtimes\codex-primary-runtime')
NODE = RUNTIME / 'dependencies/node/bin/node.exe'
DOC_SKILL = Path(r'C:\Users\solbraa\.codex\plugins\cache\openai-primary-runtime\documents\26.904.11930\skills\documents')
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
      'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
      'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
      'draw': 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0',
      'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
      'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
      'svg': 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_metadata():
    return {
        'structural_scope': 'Chapter and supplied Markdown front/backmatter coverage, figures, tables, integration prerequisites, citations, image geometry, and source integrity. This is not visual layout approval.',
        'source_manifest_path': str(STAGE / 'source_manifest.json'),
        'configuration_coverage': {'separate_nomenclature_yaml': 'Not assembled by the canonical editable exporters; present in the primary PDF workflow.'},
        'limitations': [
            'No page images could be reviewed because the packaged render_docx command cannot find LibreOffice soffice.exe. Neither editable candidate is released.',
            'The separate nomenclature.yaml file is not assembled in these secondary candidates.',
            'ODF equations use Unicode text, not native MathML.'],
        'renderer_hashes': {name: digest(PAPERLAB / 'tools' / name) for name in ('book_render_word.py', 'book_render_odf.py')},
        'table_count_note': 'Word stores 600 code blocks as single-cell tables; 408 tables come from Markdown data tables.',
    }


def prepare_fixture():
    from PIL import Image
    root = STAGE / 'fixture'
    root.mkdir(parents=True, exist_ok=True)
    cfg = {'title': 'Editable export verification', 'authors': [{'name': 'PaperLab'}],
           'year': 2026, 'settings': {'book_type': 'textbook', 'page_size': '170x244mm',
           'font_family': 'Libertinus Serif', 'font_size': 10,
           'margins': {'top': '19mm', 'bottom': '19mm', 'inner': '21mm', 'outer': '17mm'}},
           'frontmatter': ['copyright'], 'backmatter': ['glossary'],
           'parts': [{'title': 'Fixture Part', 'chapters': [
               {'dir': 'ch01_fixture', 'title': 'First verification chapter'},
               {'dir': 'ch02_fixture', 'title': 'Second verification chapter'}]}]}
    (root / 'book.yaml').write_text(yaml.safe_dump(cfg), encoding='utf-8')
    (root / 'refs.bib').write_text('@book{FixtureReference, author={PaperLab}, title={Fixture reference}, year={2026}}', encoding='utf-8')
    (root / 'frontmatter').mkdir(exist_ok=True)
    (root / 'frontmatter/copyright.md').write_text('Copyright fixture preserved 2026.', encoding='utf-8')
    (root / 'backmatter').mkdir(exist_ok=True)
    (root / 'backmatter/glossary.md').write_text('# Glossary\n\nFixture glossary preserved.', encoding='utf-8')
    for i, name in enumerate(['First verification chapter', 'Second verification chapter'], 1):
        chapter = root / 'chapters' / f'ch{i:02d}_fixture'
        (chapter / 'figures').mkdir(parents=True, exist_ok=True)
        Image.new('RGB', (600, 200) if i == 1 else (200, 600), (40 * i, 100, 180)).save(chapter / 'figures/same_name.png')
        content = f'# Chapter {i}: {name}\n\n## {i}.1 Results\n\n'
        content += '| Parameter | Value |\n|---|---|\n| Pressure (bara) | 60 |\n\n'
        content += f'![Fixture image {i}](figures/same_name.png)\n\n'
        content += '```python\nfor i in range(2):\n    print(i)\n```\n\n$$\nQ = m C_p \\Delta T\n$$\n'
        content += '\nA price of $70/bbl and a $50 million project preserve currency; $0.8$ and $q$ / hour remain equations.\n'
        content += '\nCitation fixture \\cite{FixtureReference}. [NeqSim](https://equinor.github.io/neqsim/)\n\n```python pattern: Requires the preceding model\n# This stays code\nvalue = 2\n```\n'
        (chapter / 'chapter.md').write_text(content, encoding='utf-8')
    return root


def prepare_source():
    root = STAGE / 'source'
    root.mkdir(parents=True, exist_ok=True)
    paths = [BOOK / name for name in ('book.yaml', 'refs.bib', 'nomenclature.yaml') if (BOOK / name).exists()]
    for area in ('frontmatter', 'backmatter'):
        paths.extend(p for p in (BOOK / area).rglob('*') if p.is_file())
    for _, ch, _ in book_builder.iter_chapters(book_builder.load_book_config(BOOK)):
        directory = book_builder.resolve_chapter_dir(BOOK, ch)
        paths.append(directory / 'chapter.md')
        paths.extend(p for p in (directory / 'figures').rglob('*') if p.is_file())
    manifest = {}
    for source in paths:
        rel = source.relative_to(BOOK)
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        manifest[rel.as_posix()] = digest(source)
    (STAGE / 'source_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    # Word requires a raster fallback for SVG; add it only to this disposable stage.
    for svg in root.rglob('*.svg'):
        code = "const sharp = require(process.argv[1]); sharp(process.argv[2], {density: 220}).png().toFile(process.argv[3]);"
        sharp = RUNTIME / 'dependencies/node/node_modules/sharp'
        subprocess.run([str(NODE), '-e', code, str(sharp), str(svg), str(svg.with_suffix('.png'))], check=True)
    return root, manifest


def inspect(root, docx, odt):
    from PIL import Image
    cfg = book_builder.load_book_config(root)
    chapters = list(book_builder.iter_chapters(cfg))
    expected_figures = 0
    expected_tables = 0
    expected_patterns = 0
    chapter_titles = []
    sources = []
    errors = []
    image_errors = []
    for area in ('frontmatter', 'backmatter'):
        for name in cfg.get(area, []):
            path = root / area / (name + '.md')
            if path.exists():
                sources.append(path)
    for n, ch, _ in chapters:
        path = book_builder.resolve_chapter_dir(root, ch) / 'chapter.md'
        sources.append(path)
        md = path.read_text(encoding='utf-8')
        title = re.search(r'^#\s+(.+)', md, re.M).group(1)
        title = re.sub(r'^Chapter\s+\d+\s*:\s*', '', title)
        chapter_titles.append(f'{n} {title}')
    for path in sources:
        md = book_builder.strip_excluded_sections(book_builder._strip_html_comments(path.read_text(encoding='utf-8')), cfg) if hasattr(book_builder, '_strip_html_comments') else path.read_text(encoding='utf-8')
        expected_patterns += len(re.findall(r'^```\w+\s+pattern:', md, re.M))
        md = re.sub(r'```.*?```', '', md, flags=re.S)
        expected_figures += len(re.findall(r'^\s*!\[[^\]]*\]\([^)]+\)', md, re.M))
        expected_tables += len(re.findall(r'^\s*\|\s*:?-{3,}', md, re.M))
    with zipfile.ZipFile(docx) as z:
        xml = ET.fromstring(z.read('word/document.xml'))
        strings = [''.join(p.itertext()) for p in xml.findall('.//w:p', NS)]
        drawings = len(xml.findall('.//a:blip', NS))
        page_sizes = [p.attrib for p in xml.findall('.//w:pgSz', NS)]
        section = xml.find('.//w:sectPr', NS)
        size, margins = section.find('w:pgSz', NS), section.find('w:pgMar', NS)
        available_width = (int(size.get('{'+NS['w']+'}w')) - sum(int(margins.get('{'+NS['w']+'}'+side)) for side in ('left', 'right'))) * 635
        available_height = (int(size.get('{'+NS['w']+'}h')) - sum(int(margins.get('{'+NS['w']+'}'+side)) for side in ('top', 'bottom'))) * 635
        relationships = ET.fromstring(z.read('word/_rels/document.xml.rels'))
        targets = {r.get('Id'): r.get('Target') for r in relationships}
        for inline in xml.findall('.//wp:inline', NS):
            extent, blip = inline.find('wp:extent', NS), inline.find('.//a:blip', NS)
            if extent is None or blip is None:
                continue
            width, height = int(extent.get('cx')), int(extent.get('cy'))
            if width > available_width + 1000 or height > available_height + 1000:
                image_errors.append('Word image exceeds text block')
            rid = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            with Image.open(io.BytesIO(z.read('word/' + targets[rid]))) as im:
                if abs((width / height) / (im.width / im.height) - 1) > 0.002:
                    image_errors.append('Word image aspect ratio changed')
        word = {'image_placements': drawings,
                'media_files': len([x for x in z.namelist() if x.startswith('word/media/')]),
                'tables': len(xml.findall('.//w:tbl', NS)),
                'native_math_elements': len(xml.findall('.//m:oMath', NS)),
                'equation_rendering': dict(book_render_word._EQ_STATS),
                'page_sizes_twips': page_sizes,
                'chapter_titles_found': sum(title in strings for title in chapter_titles),
                'title_style_found': any(p.find('w:pPr/w:pStyle', NS) is not None and p.find('w:pPr/w:pStyle', NS).get('{'+NS['w']+'}val') == 'Title' for p in xml.findall('.//w:p', NS)),
                'placeholder_figures': sum('[Figure:' in s for s in strings),
                'numbered_figure_captions': sum(bool(re.match(r'^Figure\s+\d+\.\d+', s)) for s in strings),
                'unresolved_citation_commands': sum(s.count('\\cite{') for s in strings),
                'integration_prerequisite_paragraphs': sum('Integration pattern prerequisites:' in s for s in strings),
                'copyright_present': any('Copyright' in s or 'copyright' in s for s in strings)}
    with zipfile.ZipFile(odt) as z:
        xml = ET.fromstring(z.read('content.xml'))
        style_xml = ET.fromstring(z.read('styles.xml'))
        text = ''.join(xml.itertext())
        props = style_xml.findall('.//style:page-layout-properties', NS) + xml.findall('.//style:page-layout-properties', NS)
        layout = props[0]
        def cm(prop):
            return float(layout.get('{'+NS['fo']+'}'+prop).removesuffix('cm'))
        page_width = cm('page-width') - cm('margin-left') - cm('margin-right')
        page_height = cm('page-height') - cm('margin-top') - cm('margin-bottom')
        for frame in xml.findall('.//draw:frame', NS):
            width = float(frame.get('{'+NS['svg']+'}width').removesuffix('cm'))
            height = float(frame.get('{'+NS['svg']+'}height').removesuffix('cm'))
            if width > page_width + 0.001 or height > page_height + 0.001:
                image_errors.append('ODF image exceeds text block')
            image = frame.find('draw:image', NS)
            href = image.get('{http://www.w3.org/1999/xlink}href')
            data = z.read(href)
            if href.lower().endswith('.svg'):
                view_box = [float(x) for x in ET.fromstring(data).get('viewBox').split()]
                aspect = view_box[2] / view_box[3]
            else:
                with Image.open(io.BytesIO(data)) as im:
                    aspect = im.width / im.height
            if abs((width / height) / aspect - 1) > 0.002:
                image_errors.append('ODF image aspect ratio changed')
        odf = {'image_placements': len(xml.findall('.//draw:image', NS)),
               'media_files': len([x for x in z.namelist() if x.startswith('Pictures/')]),
               'tables': len(xml.findall('.//table:table', NS)),
               'page_layouts': [p.attrib for p in props],
               'chapter_titles_found': sum(title in text for title in chapter_titles),
               'code_line_breaks': len(xml.findall('.//text:line-break', NS)),
               'placeholder_figures': text.count('[Figure:'),
               'unresolved_citation_commands': text.count('\\cite{'),
               'integration_prerequisite_paragraphs': text.count('Integration pattern prerequisites:'),
               'copyright_present': 'Copyright' in text or 'copyright' in text,
               'math_representation': 'Unicode text from LaTeX; editable equations are not native MathML.'}
    errors.extend(image_errors)
    for label, result in [('docx', word), ('odf', odf)]:
        for k, expected in [('chapter_titles_found', len(chapters)), ('image_placements', expected_figures), ('tables', expected_tables)]:
            if result[k] < expected:
                errors.append(f'{label} {k}: {result[k]} < {expected}')
        if result['placeholder_figures']:
            errors.append(f'{label} contains missing-figure placeholders')
        if result['unresolved_citation_commands']:
            errors.append(f'{label} contains unresolved citation commands')
        if result['integration_prerequisite_paragraphs'] != expected_patterns:
            errors.append(f'{label} integration prerequisites differ from source')
    return {'expected': {'chapters': len(chapters), 'figure_placements': expected_figures, 'tables': expected_tables,
                         'integration_prerequisites': expected_patterns},
            'docx': word, 'odf': odf, 'image_bounds_and_aspect_ratio_errors': image_errors,
            'errors': errors, 'structural_status': 'pass' if not errors else 'fail'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixture', action='store_true')
    parser.add_argument('--source-final', action='store_true')
    args = parser.parse_args()
    if not args.fixture and not args.source_final:
        parser.error('Require --fixture or explicit --source-final after parent signals final source.')
    STAGE.mkdir(parents=True, exist_ok=True)
    for split in (book_render_word._split_inline_math, book_render_odf._split_inline_math_odf):
        cases = [('A price of $70/bbl and $50 million with $q$ / hour.', ['q']),
                 ('$0.8$ and $10^6$ and $50–200/tCO2.', ['0.8', '10^6'])]
        for text, expected_math in cases:
            assert [part for part, math in split(text) if math] == expected_math
    manifest = {}
    root = prepare_fixture() if args.fixture else None
    if root is None:
        root, manifest = prepare_source()
    docx = book_render_word.render_book_word(root)
    odt = book_render_odf.render_book_odf(root)
    report = inspect(root, docx, odt)
    if not args.fixture:
        report.update(candidate_metadata())
    report.update({'created_utc': datetime.now(timezone.utc).isoformat(), 'python': sys.executable,
                   'source_stage': str(root), 'paths': {'docx': str(docx), 'odf': str(odt)},
                   'artifact_hashes': {p.name: digest(p) for p in (docx, odt)},
                   'source_files': len(manifest),
                   'source_changed_during_build': [name for name, sha in manifest.items() if digest(BOOK / name) != sha],
                   'release_status': 'not_released_pending_visual_review'})
    env = dict(os.environ, PYTHONPATH=str(BOOK / '.build/python_packages'))
    command = [sys.executable, str(DOC_SKILL / 'render_docx.py'), str(docx), '--output_dir', str(root / 'visual_qa')]
    try:
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=90)
        log = result.stdout + '\n' + result.stderr
        report['visual_qa'] = {'command': command, 'returncode': result.returncode,
                               'status': 'renderer_failed' if result.returncode else 'images_pending_review',
                               'message': log[-6500:]}
    except subprocess.TimeoutExpired:
        report['visual_qa'] = {'command': command, 'status': 'renderer_timeout'}
    destination = STAGE / 'fixture_report.json' if args.fixture else BOOK / 'verification/editable_export_report.json'
    destination.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    if report['errors'] or report['source_changed_during_build']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
