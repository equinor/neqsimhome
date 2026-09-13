# Bibliographic and source review

Reviewed 12 September 2026. This record distinguishes bibliographic identity checks from verification of an engineering claim. A correct title or standards catalogue entry does not establish that a calculation implements a publication or complies with a standard.

## Master bibliography corrections

| Legacy key | Correction | Primary evidence |
|---|---|---|
| campbell2014 | This entry describes the GPSA Engineering Data Book, thirteenth edition, issued in 2012. Corrected the year; the legacy key is retained to avoid breaking citations. | [GPSA edition and errata records](https://www.gpamidstream.org/errata-sheets/) |
| hankinson1979 | Corrected publication type to journal article and added DOI 10.1002/aic.690250412. | [AIChE Journal record](https://aiche.onlinelibrary.wiley.com/doi/abs/10.1002/aic.690250412) |
| schultz1962 | Corrected publication type to journal article and added DOI 10.1115/1.3673381. Engineering equations were separately reviewed in Chapter 14. | [ASME DOI](https://doi.org/10.1115/1.3673381) |
| api617 | Updated edition metadata to ninth edition, April 2022. Catalogue identity is not clause-level compliance evidence. | [API publication catalogue](https://www.api.org/-/media/files/publications/2023_catalog/refining-2023.pdf) |
| norsok_p002 | Corrected to P-002:2023+AC:2024, second edition. Removed the obsolete edition claim. | [Standards Norway process catalogue](https://standard.no/en/sectors/petroleum/norsok-standards/p-process/) |
| stewart2019 | Corrected Volume III copyright/publication metadata to 2016 and ISBN 9781856178082; retained the legacy key. | [Elsevier book record](https://www.sciencedirect.com/book/monograph/9781856178082/surface-production-operations) |
| faria2022rl | Corrected authors' names, including Ruan de Rezende Faria and Maurício B. de Souza Jr.; added DOI. | [Published article](https://www.mdpi.com/2227-9717/10/11/2311) |
| nasir2024rl | Confirmed 2024 issue year, distinguished online 2023 date and added DOI. | [Stanford author publication record](https://cap.stanford.edu/profiles/viewCV?facultyId=9109&name=Louis_Durlofsky) |
| gal2016dropout | Corrected publication type to conference paper and added the official proceedings link. | [PMLR proceedings](https://proceedings.mlr.press/v48/gal16.html) |
| ng2022survey | Corrected issue year to 2023, volume 170, article 108107. DOI's 2022 component and online date are not the issue year. | [Publisher DOI](https://doi.org/10.1016/j.compchemeng.2022.108107) |
| schweidtmann2021ml | Corrected journal to Chemie Ingenieur Technik, 93(12), 2029–2039 and author Asja Fischer; added DOI. | [Authors' research-group record](https://www.pi-research.org/publication/j_031_schweidtman-et-al-2021-cit-perspective-paper-ml/) |
| schweidtmann2019 | Added DOI 10.1016/j.compchemeng.2018.10.007. | [TU Delft publication record](https://research.tudelft.nl/en/publications/deterministic-global-process-optimization-accurate-single-species/) |
| hourfar2019rl | Corrected the second author's name to Hamed Jalaly Bidgoly and added DOI 10.1016/j.engappai.2018.09.019. | [British Library legal-deposit catalogue](https://eld.bl.uk/?f%5Ball_names_ssim%5D%5B%5D=Bidgoly%2C+Hamed+Jalaly&f%5Barticle_issue_title_ssi%5D%5B%5D=Volume+77%282019%29&f%5Bjournal_title_ssi%5D%5B%5D=Engineering+applications+of+artificial+intelligence&per_page=10&sort=article+page) |

The unused entries `dimoplon1978`, `dale2013`, and `norsok_p001` could not be substantiated as written. They were removed from the active bibliography and retained in `unverified_unused_references.bib`, with reasons. No cited entry was silently discarded.

## Chapter 33 claim sources

- NIOSH gives a hydrogen-sulfide IDLH value of 100 ppm. The book uses that precise value and does not infer a universal fatal exposure time: [NIOSH IDLH](https://www.cdc.gov/niosh/idlh/7783064.html).
- NIST ethane phase-change data support the stated boiling and critical properties and the correction to ambient-temperature storage claims: [NIST Chemistry WebBook](https://webbook.nist.gov/cgi/cbook.cgi?ID=C74840&Mask=4). A low-temperature Antoine fit is not extrapolated to ambient conditions.
- The University of Waterloo distillation notes support the Fenske/Underwood shortcut scope and feed-quality convention: [design equations](https://chemengvirtual.uwaterloo.ca/distillation-lab/design.html). The binary saturated-liquid equation was also solved and checked independently.
- Honeywell UOP identifies water and mercury removal as relevant pretreatment for cryogenic gas processing: [UOP technical brochure](https://uop.honeywell.com/content/dam/uop/en-us/documents/industry-solutions/gas-processing/gas-treating/mercury-removal/uop-mercury-removal-natural-gas-production-brochure.pdf). The synthetic numerical feed is explicitly dry and acid-gas-free.
- Twu et al. (2005), DOI 10.1016/j.fluid.2004.09.031, and Neagu and Cursaru (2017), DOI 10.1016/j.jngse.2016.11.052, provide TEG/water thermodynamic and process context. The book does not claim that these publications independently validate the particular NeqSim approximate absorber example.
- EPA AP-42 Section 5.3 supports process-boundary context: [natural-gas processing chapter](https://www.epa.gov/sites/default/files/2020-09/documents/5.3_natural_gas_processing.pdf). Its 1995 process description is not presented as a current emissions permit requirement.

## Review limits and retained evidence

`bibliographic_metadata_audit.json` records a machine metadata lookup attempt. Most Crossref queries received HTTP 429 and therefore did not verify the entries. Successful raw responses are retained under `references/crossref/`. Those failures were not converted to passes. Publisher, author, standards-body and official data sources above were consulted separately for the corrections.

The chapter reviewers also checked manual in-chapter reference lists, including references absent from the master bibliography. Their detailed corrections and remaining scopes are recorded in `foundations_review.*`, `optimization_review.*`, and `onshore_review.*`. This review does not claim full-text access to every cited book or standard.

## Final manual-reference reconciliation

The publisher's [2014–2015 PetroSkills catalogue](https://www.jmcampbell.com/2014-15_PetroSkills_Facilities_Training_Guide.pdf) explicitly identifies January2014 first printings of the ninth-edition Gas Conditioning and Processing volumes1 and2. Those manual Campbell references are valid and remain distinct from the GPSA book under the legacy master key `campbell2014`.

The [API catalogue](https://www.api.org/~/media/files/publications/2018_catalog/2018_pubs_catalog_final_sm.pdf) identifies RP14E fifth edition1991; incorrect2007 manual dates were corrected. Manual NORSOKP002 metadata were aligned with the verified2023+AC2024 master record. This does not establish clause-level compliance.

[McGraw-Hill](https://www.mheducation.com/highered/mhp/product/process-equipment-malfunctions-techniques-identify-correct-plant-problems.html) identifies Lieberman's Process Equipment Malfunctions as published2011,copyright2012. [Wiley](https://onlinelibrary.wiley.com/doi/book/10.1002/9780470432259) is the publisher of Troubleshooting Process Plant Control,copyright2009. The manuscript's wrong date/publisher were corrected. The unspecific Ludwig1999Vols1–3 reading-list record was quarantined in `manual_bibliography_alignment.json` because its shared volume/year identity was not verified; no numerical result relies on that entry. Full-text access to these books is not claimed.
