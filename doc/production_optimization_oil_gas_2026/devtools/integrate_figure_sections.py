"""Integrate reviewed notebook results without touching executable source blocks."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

BOOK = Path(__file__).resolve().parents[1]
records = json.loads((BOOK / 'verification/notebook_figure_updates.json').read_text(encoding='utf-8'))
parser=argparse.ArgumentParser()
parser.add_argument('--chapters',help='Comma-separated chapter prefixes; omitted integrates all.')
args=parser.parse_args()
if args.chapters:
    prefixes=tuple(args.chapters.split(','))
    records=[r for r in records if r['chapter'].startswith(prefixes)]
    assert records,'No requested chapter result sections found'
FENCES = re.compile(r'(?ms)(^```[^\n]*\n.*?^```[^\n]*(?:\n|$))')
fig_heading = re.compile(r'^##\s+(?:\d+(?:\.\d+)*\s+)?Figures\s*$', re.M)
summary_heading = re.compile(r'^##\s+(?:\d+(?:\.\d+)*\s+)?Summary\b', re.M)
report = []
for chapter in sorted({r['chapter'] for r in records}):
    number = int(chapter[2:4])
    path = BOOK / 'chapters' / chapter / 'chapter.md'
    section_path = BOOK / 'verification/figure_sections' / f'ch{number:02d}.md'
    if not section_path.exists():
        raise FileNotFoundError(section_path)
    original = path.read_text(encoding='utf-8-sig')
    before_code = FENCES.findall(original)
    text = re.sub(r'(?ms)\n<!-- reviewed-notebook-results:start -->.*?<!-- reviewed-notebook-results:end -->\n', '\n', original)
    old = fig_heading.search(text)
    if old:
        next_heading = re.search(r'^##\s', text[old.end():], re.M)
        end = old.end() + next_heading.start() if next_heading else len(text)
        text = text[:old.start()] + text[end:]
    for row in (r for r in records if r['chapter'] == chapter):
        if row['figure_path'] in text:
            raise RuntimeError(f'Figure already placed in the body; review insertion manually: {chapter}/{row["figure"]}')
    reviewed = section_path.read_text(encoding='utf-8')
    # Standardize the chapter-level heading, while preserving reviewed content.
    reviewed = re.sub(r'^#{1,2}\s+[^\n]+\n', '## Reproduced Calculation Results\n', reviewed, count=1)
    section = '\n<!-- reviewed-notebook-results:start -->\n' + reviewed.strip() + '\n<!-- reviewed-notebook-results:end -->\n\n'
    position = summary_heading.search(text)
    insert_at = position.start() if position else len(text)
    text = text[:insert_at].rstrip() + '\n\n' + section + text[insert_at:]

    parts = FENCES.split(text)
    for index in range(0, len(parts), 2):
        prose = parts[index]
        prose = re.sub(r'(!\[)Figure\s+\d+(?:[.-]\d+)*\s*[:.]\s*', r'\1', prose, flags=re.I)
        # Old generated sections sometimes duplicated an image's alt caption
        # as an italic paragraph. Keep genuine discussion but remove its stale number.
        def caption(match):
            image, alt, explanation = match[1], match[2], match[3].strip()
            return image if alt.strip().casefold() == explanation.casefold() else image + '\n\n' + explanation
        prose = re.sub(r'(!\[([^\]]*)\]\([^\n]+\))\s*\n\*Figure\s+\d+(?:[.-]\d+)*\s*:\s*([^\n]+)\*', caption, prose, flags=re.I)
        prose = re.sub(r'^\*Figure\s+\d+(?:[.-]\d+)*\s*:\s*(.*?)\*\s*$', r'\1', prose, flags=re.M | re.I)
        def merge_repeated_title(match):
            alt, destination, caption = match[1], match[2], match[3]
            if caption.casefold().startswith(alt.rstrip('.').casefold()):
                return '![' + caption.rstrip('.') + '](' + destination + ')'
            return match[0]
        prose = re.sub(r'!\[([^\]]+)\]\(([^\n]+)\)\s*\n\*([^\n]+)\*', merge_repeated_title, prose)
        parts[index] = prose
    text = ''.join(parts)
    assert before_code == FENCES.findall(text), f'Executable content changed in {chapter}'
    backup = BOOK / '.build/before_figure_integration' / chapter / 'chapter.md'
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        backup.write_text(original, encoding='utf-8')
    path.write_text(text, encoding='utf-8')
    report.append({'chapter': chapter, 'figures': sum(r['chapter'] == chapter for r in records),
                   'sha256': hashlib.sha256(text.encode()).hexdigest(), 'code_unchanged': True})
report_path=BOOK / 'verification/figure_integration_report.json'
updated_chapters=len(report)
if args.chapters and report_path.exists():
    prior=json.loads(report_path.read_text(encoding='utf-8'))
    replaced={r['chapter'] for r in report}
    report=sorted([r for r in prior if r['chapter'] not in replaced]+report,key=lambda r:r['chapter'])
report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(f'Integrated reviewed results for {updated_chapters} chapters and {len(records)} figures; retained {len(report)} chapter records.')
