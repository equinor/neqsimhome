# Bibliography audit — PaperLab book workflow

Reviewed 12 September 2026. The active route was PaperLab's `book-author` agent
instructions, `book_creation` skill and the literature-reuse steps they require.
The companion `neqsim_in_writing` skill supplied the boundary between citation
metadata and executed computational evidence.

## Commands and preserved evidence

The exact selected interpreter was
`C:\Users\solbraa\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
`book_runtime.py` exposed the existing book-local dependencies. No runtime or
package changes were made during this audit.

1. Ran native `paperflow.py book-enrich-bib <book_dir>` **without** `--in-place`.
   `refs.enriched.bib` preserves the machine-proposed result, and
   `refs.enrichment_report.json` preserves the complete first-pass report.
2. Reviewed all 12 proposed DOIs through direct Crossref work records. Queried
   two additional known candidates from the paper/publisher trail. All 14 DOI
   work records were retrieved and are preserved in
   `verification/bibliography_metadata.json` with exact URLs and retrieval date.
3. Merged the verified proposals into `refs.bib`, then made the four metadata
   corrections listed below. `refs.bib` is the curated release input;
   `refs.enriched.bib` is review evidence and is deliberately not its replacement.
4. Ran native `paperflow.py validate-bib <book_dir>` using the repaired book
   route, which reads the complete configured manuscript. The result was
   **0 failures**, **17 unused-entry warnings** and 19 informational messages
   at this audit's checkpoint. No citation key was missing from `refs.bib`.
   The machine-readable checkpoint is
   `verification/bibliography_validation.json`; later chapter edits may change
   the unused-entry count.

## Accepted DOI metadata

All keys below retain their original title, year and authors unless separately
listed in the correction table. Crossref titles and publication years matched
the cited works. Direct work records provide publisher-deposited bibliographic
metadata; they do not validate the scientific conclusions of the papers.

| Book key | Verified DOI | Disposition |
|---|---|---|
| `soave1972` | `10.1016/0009-2509(72)80096-4` | Added; also found in the TP-flash paper bibliography |
| `peng1976` | `10.1021/i160057a011` | Added; also found in the TP-flash paper bibliography |
| `michelsen1982a` | `10.1016/0378-3812(82)85001-2` | Added; existing paper candidate verified |
| `michelsen1982b` | `10.1016/0378-3812(82)85002-4` | Added after direct lookup; first search was rate-limited |
| `rachford1952` | `10.2118/952327-G` | Added; unusual publisher-deposited pagination retained |
| `kontogeorgis1996` | `10.1021/ie9600203` | Added; publisher record supports existing author spelling |
| `kunz2012` | `10.1021/je300655b` | Added |
| `wei2022chain` | `10.52202/068431-1800` | Added; retained as an uncited reading candidate |
| `liu2023lost` | `10.1162/tacl_a_00638` | Added; publication year remains 2024 despite historical key name |
| `sloan2008` | `10.1201/9781420008494` | Added; third-edition year corrected to 2007 |
| `coutinho2006` | `10.1081/lft-200035541` | Added; publication year remains 2005 despite historical key name |
| `speight2014` | `10.1201/b16559` | Added; corrected book entry type |
| `nyborg2002` | `10.5006/c2002-02233` | Added; corrected conference-publication metadata |
| `beggs1973` | `10.2118/4007-PA` | Added |

DOIs are case-insensitive. Lowercase values inserted by the native enricher are
equivalent to the capitalized forms shown in some publisher records.

## Verified corrections and deliberately retained details

| Key | Correction or reviewed decision | Evidence |
|---|---|---|
| `sloan2008` | Year 2008 → 2007; added Sloan's `Jr.` suffix in valid BibTeX name order. Kept the historical key so chapter citations remain stable. | [CRC Press third-edition page](https://www.routledge.com/Clathrate-Hydrates-of-Natural-Gases/Koh-SloanJr/p/book/9780849390784) and [Crossref DOI record](https://api.crossref.org/works/10.1201%2F9781420008494) both identify 2007. Crossref repeats Koh in its author array; that duplicate was not imported. |
| `speight2014` | `@article` → `@book`; existing edition, publisher and year retained. | [Crossref record](https://api.crossref.org/works/10.1201%2Fb16559) identifies a book; the [publisher's Chemical Industries catalog](https://www.routledge.com/Chemical-Industries/book-series/CRCCHEMINDUS?a=1&pg=2) identifies fifth edition, February 2014. |
| `coutinho2006` | Issue 9 → combined issue 9–10. | [Crossref record](https://api.crossref.org/works/10.1081%2Flft-200035541) identifies volume 23, issue 9–10, pages 1113–1128, 2005. |
| `nyborg2002` | `@article` → `@inproceedings`; conference title `CORROSION 2002`, publisher NACE International, pages 1–16. | [Crossref record](https://api.crossref.org/works/10.5006%2Fc2002-02233) identifies the conference publication. |
| `rachford1952` | Retained `19--3` pagination after review instead of guessing a replacement. | [Crossref record](https://api.crossref.org/works/10.2118%2F952327-G) itself deposits `19-3`. The local paper uses `19`; these records disagree, so the publisher-deposited value was preserved. |
| `kontogeorgis1996` | Retained `Iakovos V. Yakoumis`; did not import the existing paper's `Ioannis` spelling. | [Crossref record](https://api.crossref.org/works/10.1021%2Fie9600203) supports the book's existing name. |

## Enrichment limitations

The first native pass reported 12 DOI additions, 5 non-confident matches,
3 no-match results and 23 entries skipped because the type normally has no
DOI. Three search requests received HTTP 429: `michelsen1982b`, `poling2001`
and `brown2020`. The first was subsequently resolved by direct lookup; the
others remain without newly assigned DOIs. This is not a finding that the
works do not exist.

Non-confident candidates were `smith2005`, `yao2022react`, `wooldridge2009`,
`sloan2008` and `ahmed2019`. Sloan/Koh was resolved using its publisher page
and direct DOI record. The others were left unchanged. A different edition,
similarly titled work, or search result with an inconsistent year must not
replace the intended reference solely to make enrichment pass.

The master bibliography intentionally retains relevant reading candidates
from the previous book; 17 were not cited at the audit checkpoint. These are
visible warnings, not unresolved citations. No unused reference was inserted
into unrelated prose or deleted merely to suppress a warning. Uncited generic
standards-family entries such as `iso20765` require a part and edition check
before future normative use. No claim of current compliance follows from
their presence in the master bibliography.

## Native workflow repair

`validate-bib` previously read only `paper.md`, silently omitting book chapter
citations. It now detects `book.yaml` and checks all configured chapters and
front/backmatter together, respecting the configured bibliography filename.
It excludes archived drafts and fails when a configured source is missing.
The validator now handles bibtexparser 1.x and 2.x; its fallback also checks
citations, including hyphenated keys. Focused regression cases cover manifest
coverage, exclusion of archived citations, missing sources, unchanged paper
validation, fallback citation checking and duplicate entries.

The reusable instructions were updated in `skills/book_creation/SKILL.md`,
linking the book-author literature handoff and scientific traceability audit.
The paper reuse assessment is in `paper_to_chapter_mapping.md`.
