"""Apply source-verified manual bibliography fixes after author freeze."""
from pathlib import Path
import json,re
B=Path(__file__).resolve().parents[1];O=B/'verification/scientific_revision'
P=re.compile(r'^```[^\n]*\n.*?^```[^\n]*(?:\n|$)',re.M|re.S);records=[]
for p in sorted((B/'chapters').glob('*/chapter.md')):
    t=p.read_text(encoding='utf-8');before=P.findall(t);lines=t.splitlines(keepends=True);updated=[]
    for line in lines:
        new=line;url=None
        if re.match(r'^\d+\. .*API.*14E \(2007\)',line):
            new=line.replace('14E (2007)','14E (1991)');url='https://www.api.org/~/media/files/publications/2018_catalog/2018_pubs_catalog_final_sm.pdf'
        if re.match(r'^\d+\. NORSOK P-002 \(2014\)',line):
            new=line.replace('P-002 (2014)','P-002:2023+AC:2024 (2023)');url='https://standard.no/en/sectors/petroleum/norsok-standards/p-process/'
        if 'Lieberman, N. (2009). *Process Equipment Malfunctions:' in line:
            new=line.replace('Lieberman, N. (2009)','Lieberman, N.P. (2011; copyright 2012)');url='https://www.mheducation.com/highered/mhp/product/process-equipment-malfunctions-techniques-identify-correct-plant-problems.html'
        if 'Lieberman, N.P. (2009). *Troubleshooting Process Plant Control*' in line:
            new=line.replace('Tulsa, OK: PennWell.','Wiley. DOI: 10.1002/9780470432259.');url='https://onlinelibrary.wiley.com/doi/book/10.1002/9780470432259'
        if 'Ludwig, E.E. (1999).' in line and 'Vol. 1–3' in line:
            new='';url='Unverified volume/year combination: retained in review archive; no quantitative claim relies on this unspecific reading-list entry.'
        if new!=line:records.append({'chapter':p.parent.name,'original':line.strip(),'replacement':new.strip(),'evidence':url})
        updated.append(new)
    t=''.join(updated)
    if p.parent.name=='ch21_debottlenecking':
        # Only the final two entries shift after quarantining the unspecific series reference.
        t=t.replace('5. Lieberman, N.P. (2011; copyright 2012)','4. Lieberman, N.P. (2011; copyright 2012)').replace('6. Smith, R. (2016).','5. Smith, R. (2016).')
    assert P.findall(t)==before,p
    p.write_text(t,encoding='utf-8')
(O/'manual_bibliography_alignment.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
note='''
## Final manual-reference reconciliation

The publisher's [2014–2015 PetroSkills catalogue](https://www.jmcampbell.com/2014-15_PetroSkills_Facilities_Training_Guide.pdf) explicitly identifies January2014 first printings of the ninth-edition Gas Conditioning and Processing volumes1 and2. Those manual Campbell references are valid and remain distinct from the GPSA book under the legacy master key `campbell2014`.

The [API catalogue](https://www.api.org/~/media/files/publications/2018_catalog/2018_pubs_catalog_final_sm.pdf) identifies RP14E fifth edition1991; incorrect2007 manual dates were corrected. Manual NORSOKP002 metadata were aligned with the verified2023+AC2024 master record. This does not establish clause-level compliance.

[McGraw-Hill](https://www.mheducation.com/highered/mhp/product/process-equipment-malfunctions-techniques-identify-correct-plant-problems.html) identifies Lieberman's Process Equipment Malfunctions as published2011,copyright2012. [Wiley](https://onlinelibrary.wiley.com/doi/book/10.1002/9780470432259) is the publisher of Troubleshooting Process Plant Control,copyright2009. The manuscript's wrong date/publisher were corrected. The unspecific Ludwig1999Vols1–3 reading-list record was quarantined in `manual_bibliography_alignment.json` because its shared volume/year identity was not verified; no numerical result relies on that entry. Full-text access to these books is not claimed.
'''
with (O/'bibliographic_review.md').open('a',encoding='utf-8') as f:f.write(note)
print('Manual reference corrections:',len(records))
