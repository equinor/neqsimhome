"""Exercise book rendering: custom rights, frontmatter, numbering and backmatter."""
from pathlib import Path
import os
import re
import shutil
import sys

BOOK = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')
sys.path[:0] = [str(BOOK / '.build/python_packages'), str(BOOK.parents[1] / 'tools')]
import yaml
import pymupdf
import pypandoc
from book_render_pdf import render_book_pdf

os.environ['PATH'] = str(Path(pypandoc.get_pandoc_path()).parent) + os.pathsep + os.environ['PATH']
fixture = BOOK / '.build/renderer_fixture'
fixture.mkdir(parents=True, exist_ok=True)
cfg = {'title': 'Renderer Verification', 'authors': [{'name': 'Test Author'}], 'publisher': 'self',
       'year': 2026, 'settings': {'page_size': '170x244mm', 'font_size': 10, 'toc_depth': 2, 'chapter_hero_images': False},
       'frontmatter': ['title_page', 'copyright', 'preface'],
       'parts': [{'title': 'Methods', 'chapters': [{'dir': 'ch01', 'title': 'Alpha'}, {'dir': 'ch02', 'title': 'Beta'}]}],
       'backmatter': ['glossary'], 'nomenclature': {'file': 'nomenclature.yaml'}}
(fixture / 'book.yaml').write_text(yaml.safe_dump(cfg), encoding='utf-8')
for folder in ['frontmatter', 'backmatter', 'chapters/ch01/figures', 'chapters/ch02/figures']:
    (fixture / folder).mkdir(parents=True, exist_ok=True)
(fixture / 'frontmatter/copyright.md').write_text('# Rights\n\nCUSTOM_RIGHTS_MARKER. All rights reserved.\n', encoding='utf-8')
(fixture / 'frontmatter/preface.md').write_text('# Preface\n\nPREFACE_MARKER explains the book.\n', encoding='utf-8')
(fixture / 'backmatter/glossary.md').write_text('# Glossary\n\nGLOSSARY_MARKER: a checked definition.\n', encoding='utf-8')
(fixture / 'nomenclature.yaml').write_text('P:\n  symbol: P\n  description: Pressure\n  unit: Pa\n', encoding='utf-8')
onshore_text = (BOOK / 'chapters/ch33_onshore_processing_plants/chapter.md').read_text(encoding='utf-8')
aligned_margin = re.search(r'\\begin\{aligned\}.*?\\end\{aligned\}', onshore_text, re.S).group(0)
for number, title in [(1, 'Alpha'), (2, 'Beta')]:
    chapter = fixture / f'chapters/ch{number:02d}'
    shutil.copy2(BOOK / 'chapters/ch23_neqsim_optimization_framework/figures/optimization_evidence_loop_2026.svg', chapter / 'figures/workflow.svg')
    text = f'''# {title}

## Learning Objectives

Explain the workflow.

## {number}.1 Introduction

The introductory section has its intended number.

| Item | Cost | Interpretation |
|---|---|---|
| Steel | $5–15/kg | PRICE_ROW_MARKER |
| Capital | $5–20 billion | CAPEX_ROW_MARKER |

```python pattern: requires caller-supplied historian data
# PATTERN_COMMENT_NOT_A_CHAPTER
measurement = historian.read("pressure")
```

![A workflow.](figures/workflow.svg)

$$p = \\rho R T$$

The contribution margin uses compatible time and price bases.

$$
{aligned_margin}
$$

## Summary

The chapter ends here.
'''
    (chapter / 'chapter.md').write_text(text, encoding='utf-8')
result = render_book_pdf(fixture)
assert result is not None, 'Renderer did not produce a PDF'
doc = pymupdf.open(result)
texts = [page.get_text() for page in doc]
full = '\n'.join(texts).replace('\u00a0', ' ')
for required in ['CUSTOM_RIGHTS_MARKER', 'PREFACE_MARKER', 'GLOSSARY_MARKER', 'Nomenclature',
                 '1.1 Introduction', '2.1 Introduction', 'Figure 1.1', 'Figure 2.1']:
    assert required in full, f'Missing expected rendered content: {required}'
assert 'Creative Commons' not in full, 'Generic license replaced supplied rights'
preface_page = next(i for i, text in enumerate(texts) if 'PREFACE_MARKER' in text)
toc_page = next(i for i, text in enumerate(texts) if 'Table of Contents' in text)
assert preface_page < toc_page, 'Preface rendered after table of contents'
assert 'Learning Objectives' not in texts[toc_page], 'Pedagogic headings clutter the contents'
assert full.count('From candidate to defensible operating point') == 2, 'Numerical figures duplicated as decorative chapter openers'
assert 'Integration pattern prerequisites' in full, 'Execution prerequisites were hidden'
typst_text = (Path(result).parent / 'book.typ').read_text(encoding='utf-8')
assert '= PATTERN_COMMENT' not in typst_text, 'Code comment became a book chapter'
assert 'PRICE_ROW_MARKER' in full and 'CAPEX_ROW_MARKER' in full
assert 'PRICE_ROW_MARKER' not in '\n'.join(re.findall(r'(?<!\\)\$.*?(?<!\\)\$', typst_text, re.S)), 'Currency consumed table rows as math'
assert abs(doc[0].rect.width * 25.4 / 72 - 170) < .01
assert abs(doc[0].rect.height * 25.4 / 72 - 244) < .01
print('PASS: custom copyright, frontmatter order, stable section and figure numbering, nomenclature, backmatter, trim size.')
