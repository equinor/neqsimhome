"""Retain primary publisher metadata; merge rather than replace shared sources."""
from pathlib import Path
import datetime,hashlib,json,urllib.request
B=Path(__file__).resolve().parents[1];O=B/'verification/scientific_revision';R=O/'references';D=R/'publisher';D.mkdir(exist_ok=True)
items=[
('api_2018_publications_catalog.pdf','API publication catalogue','https://www.api.org/~/media/files/publications/2018_catalog/2018_pubs_catalog_final_sm.pdf','Identifies RP14E fifth edition1991; not a current applicability or compliance assessment.'),
('petroskills_2014_2015_catalog.pdf','PetroSkills/John M. Campbell','https://www.jmcampbell.com/2014-15_PetroSkills_Facilities_Training_Guide.pdf','Confirms Gas Conditioning and Processing volumes1 and2 ninth edition first printing January2014; preserves valid manual references.'),
('lieberman_malfunctions_publisher.html','McGraw-Hill','https://www.mheducation.com/highered/mhp/product/process-equipment-malfunctions-techniques-identify-correct-plant-problems.html','Process Equipment Malfunctions publication July2011,copyright2012,ISBN9780071770200.'),
('lieberman_control_publisher.html','Wiley','https://onlinelibrary.wiley.com/doi/book/10.1002/9780470432259','Troubleshooting Process Plant Control publisherWiley,copyright2009; notPennWell.')]
manifest=json.loads((R/'collection_manifest.json').read_text(encoding='utf-8'));attempts=[]
for name,source,url,purpose in items:
    path=D/name;row={'url':url,'source':source,'purpose':purpose}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=30) as response:payload=response.read()
        if name.endswith('.pdf'):assert payload.startswith(b'%PDF'), 'Not aPDF'
        path.write_bytes(payload)
        row.update(status='archived',file=str(path.relative_to(O)),sha256=hashlib.sha256(payload).hexdigest(),retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),data_type='Primary publisher bibliographic metadata',review_status='reviewed for metadata only')
        manifest=[r for r in manifest if r['file'].replace('\\','/')!=row['file'].replace('\\','/')]+[row]
    except Exception as exc:row.update(status='download_failed',error=str(exc),interpretation='Web primary-source metadata was consulted; failed download is not represented as an archive.')
    attempts.append(row)
(R/'collection_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(O/'final_reference_retrievals.json').write_text(json.dumps(attempts,indent=2),encoding='utf-8')
print(json.dumps([{'source':r['source'],'status':r['status']} for r in attempts],indent=2))
