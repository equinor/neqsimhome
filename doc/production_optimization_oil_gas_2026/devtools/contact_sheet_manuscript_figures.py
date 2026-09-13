"""Create inspection sheets for manuscript figures outside notebook execution."""
from pathlib import Path
import hashlib
import json
import re
import sys
import textwrap

BOOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / '.build/python_packages'))
from PIL import Image, ImageDraw, ImageFont
OUT = BOOK / 'verification/scientific_revision/manuscript_figures'
OUT.mkdir(exist_ok=True)
notebook_figures = {Path(row['path']).resolve() for report in json.loads((BOOK / 'verification/notebook_execution_report.json').read_text(encoding='utf-8')) for row in report['figures']}
records = []
for chapter in sorted((BOOK / 'chapters').glob('*/chapter.md')):
    for match in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', chapter.read_text(encoding='utf-8')):
        path = (chapter.parent / match[2]).resolve()
        if path in notebook_figures:
            continue
        records.append(dict(chapter=chapter.parent.name, caption=match[1], path=str(path),
                            sha256=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
                            supported=path.suffix.lower() in {'.png', '.jpg', '.jpeg'}))
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 22)
for offset in range(0, len(records), 9):
    sheet = Image.new('RGB', (2100, 2070), 'white')
    draw = ImageDraw.Draw(sheet)
    for index, row in enumerate(records[offset:offset + 9]):
        x, y = index % 3 * 700, index // 3 * 690
        path = Path(row['path'])
        if row['supported'] and path.is_file():
            picture = Image.open(path).convert('RGB')
            picture.thumbnail((680, 540))
            sheet.paste(picture, (x + (700 - picture.width) // 2, y + 5))
        else:
            draw.text((x + 15, y + 180), 'Separate inspection: ' + path.suffix, fill='red', font=font)
        label = f"{offset + index + 1}. {row['chapter'][:4]} {path.name}"
        draw.text((x + 12, y + 550), label, fill='black', font=font)
        draw.multiline_text((x + 12, y + 585), '\n'.join(textwrap.wrap(row['caption'], 52)[:4]), fill='#334455', font=font, spacing=4)
    file = OUT / f'sheet_{offset // 9 + 1:02d}.jpg'
    sheet.save(file, quality=90)
    for row in records[offset:offset + 9]:
        row['contact_sheet'] = str(file)
(OUT / 'inventory.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
print(f'{len(records)} manuscript figures in {(len(records)+8)//9} sheets.')
