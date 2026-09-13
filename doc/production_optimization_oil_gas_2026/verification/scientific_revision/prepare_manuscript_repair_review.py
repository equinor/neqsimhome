from pathlib import Path
import hashlib
import json
import sys
HERE=Path(__file__).resolve().parent
BOOK=HERE.parents[1]
sys.path.insert(0,str(BOOK/'.build/python_packages'))
from PIL import Image,ImageDraw,ImageFont
records=json.loads((HERE/'illustration_repairs.json').read_text(encoding='utf-8'))
OUT=HERE/'manuscript_repair_visual_review'
OUT.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
inventory=[]
for start in range(0,len(records),6):
    sheet=Image.new('RGB',(2000,1950),'#eeeeee')
    draw=ImageDraw.Draw(sheet)
    for offset,r in enumerate(records[start:start+6]):
        index=start+offset+1
        p=BOOK/r['path']
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        assert digest==r['sha256'],p
        im=Image.open(p).convert('RGB')
        original=im.size
        im.thumbnail((970,585))
        x=(offset%2)*1000;y=(offset//2)*650
        sheet.paste(im,(x+(1000-im.width)//2,y+58+(585-im.height)//2))
        draw.text((x+15,y+8),f'{index:02d}  {r["chapter"][:4]}  {r["file"]}',fill='#202020',font=font)
        draw.text((x+15,y+34),r['basis'],fill='#505050',font=small)
        inventory.append({'index':index,'path':str(p),'sha256':digest,'size_px':original,'contact_sheet':str(OUT/f'contact_{start//6+1:02d}.jpg')})
    sheet.save(OUT/f'contact_{start//6+1:02d}.jpg',quality=93)
(OUT/'inspection_inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
print('Prepared',len(records),'images on four contact sheets')
