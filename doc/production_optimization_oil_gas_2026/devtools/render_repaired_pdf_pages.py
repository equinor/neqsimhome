from pathlib import Path
import sys,json,hashlib
B=Path(__file__).resolve().parents[1];V=B/'verification/pdf_final'
sys.path.insert(0,str(B/'.build/python_packages'))
import pymupdf
p=B/'.build/release_candidate/submission/book.pdf';doc=pymupdf.open(p);rows=[]
for number in (461,664,1257,1337):
 image=V/f'qa_repaired_{number:04d}.png'
 doc[number-1].get_pixmap(matrix=pymupdf.Matrix(1.8,1.8)).save(image)
 rows.append({'page':number,'path':str(image),'sha256':hashlib.sha256(image.read_bytes()).hexdigest()})
(V/'repaired_page_manifest.json').write_text(json.dumps({'pdf_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pages':rows},indent=2),encoding='utf-8')
