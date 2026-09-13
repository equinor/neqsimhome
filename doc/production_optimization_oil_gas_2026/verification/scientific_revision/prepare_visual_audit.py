from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parent;BOOK=ROOT.parents[1]
sys.path.insert(0,str(BOOK/'.build/python_packages'))
from PIL import Image,ImageOps,ImageDraw,ImageFont
dest=ROOT/'figure_visual_review';dest.mkdir(exist_ok=True)
records=[]
for p in sorted((BOOK/'verification/notebooks').glob('*.json')):
    report=json.loads(p.read_text(encoding='utf-8'))
    for f in report['figures']:
        path=Path(f['path']);actual=hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual==f['sha256'],str(path)
        im=Image.open(path)
        records.append({'chapter':p.stem,'path':str(path),'sha256':actual,'size_px':list(im.size),
                        'dpi':f['dpi'],'series':f['series']})
p=ROOT/'figures/nist_methane_density_validation.png'
records.append({'chapter':'36_benchmark','path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                'size_px':list(Image.open(p).size),'dpi':220,'series':[]})
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
label_font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
for start in range(0,len(records),6):
    page=Image.new('RGB',(2048,2100),'#e6e9ec');draw=ImageDraw.Draw(page)
    for slot,rec in enumerate(records[start:start+6]):
        x=(slot%2)*1024;y=(slot//2)*700
        draw.text((x+18,y+9),f"{start+slot+1:03d}  {rec['chapter']}",fill='#18324a',font=font)
        draw.text((x+18,y+41),Path(rec['path']).name,fill='#223344',font=label_font)
        thumb=ImageOps.contain(Image.open(rec['path']).convert('RGB'),(994,620),method=Image.Resampling.LANCZOS)
        page.paste(thumb,(x+(1024-thumb.width)//2,y+75+(620-thumb.height)//2))
        rec['contact_sheet']=str(dest/f'contact_{start//6+1:02d}.jpg');rec['contact_index']=start+slot+1
    page.save(dest/f'contact_{start//6+1:02d}.jpg',quality=94)
(dest/'inspection_inventory.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print(len(records),'plots;',len(list(dest.glob('contact_*.jpg'))),'contact sheets')
