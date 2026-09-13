"""Make contact sheets using only page renders from the current PDF manifest."""
from pathlib import Path
import hashlib,json,sys
B=Path(__file__).resolve().parents[1];V=B/'verification/pdf_final'
sys.path.insert(0,str(B/'.build/python_packages'))
from PIL import Image,ImageDraw
manifest=json.loads((V/'scientific_sample_manifest.json').read_text(encoding='utf-8'))
current=hashlib.sha256((B/'.build/release_candidate/submission/book.pdf').read_bytes()).hexdigest()
assert current==manifest['pdf_sha256']
rows=manifest['rendered_images'];sheets=[]
for offset in range(0,len(rows),6):
    batch=rows[offset:offset+6];sheet=Image.new('RGB',(1000,2100),'#d7dce0');draw=ImageDraw.Draw(sheet)
    for index,row in enumerate(batch):
        path=Path(row['path']);assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
        im=Image.open(path).convert('RGB');im.thumbnail((480,650))
        x=(index%2)*500+(500-im.width)//2;y=(index//2)*700+30
        sheet.paste(im,(x,y));draw.text(((index%2)*500+12,(index//2)*700+8),'PDF page '+str(row['page']),fill='black')
    p=V/f'scientific_contact_{offset//6+1:02d}.png';sheet.save(p)
    sheets.append({'path':str(p),'pages':[r['page'] for r in batch],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(V/'scientific_contacts.json').write_text(json.dumps({'pdf_sha256':current,'sheets':sheets},indent=2),encoding='utf-8')
print(json.dumps({'pages':len(rows),'contact_sheets':len(sheets)},indent=2))
