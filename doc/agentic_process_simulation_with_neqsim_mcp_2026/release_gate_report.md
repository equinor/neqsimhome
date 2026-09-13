# Release review — 13 September 2026

The reader editions are `submission/book.pdf`, `submission/book.docx` and
`submission/book_standalone.html`. Native HTML with separate assets is also
available as `submission/book.html`. Diagnostic fixture files are not reader
editions.

## Typesetting release review

| Format | Result | Evidence and scope |
|---|---|---|
| HTML | Pass | All 13 images loaded, no math errors, no page-wide overflow at 500, 768, 1024 and 1280 pixels. Portable edition embeds all 13 images. Early reading-path explanation checked in the browser. |
| PDF | Pass | Final 189-page PDF independently reviewed across all 12 contact sheets and 15 full-size pages. Long tables, captions, apparatus headers and corrected prompt/reference formatting passed. The reviewed SHA256 is recorded in the final PDF visual review. |
| DOCX | Pass | Final 172-page native Word proof; all page contacts and full-size figure, code, numbering and pagination checks passed. |
| OpenDocument | Warn | Package/XML integrity checked; 12 chapter illustrations embedded. This supplementary format does not include the front cover and has no independent native ODF page proof. |

No blocking issues remain in the primary reader formats.
See the final page reviews for observed minor whitespace and
proof limits. Nineteen native renderer fixtures and twelve focused Word checks
passed; four Word checks overlap with the native suite.

## Content and calculations

The configured ten-chapter source check and strict evidence check passed with
zero reported errors or warnings. All cited bibliography keys resolve. The
bibliography audit retained one uncited legacy entry rather than deleting a
reference solely to silence a warning; uncited entries do not appear in the
reader bibliography.

An independent content review's three findings were corrected and signed off.
Five source-backed Java regression checks passed, with zero failures, errors or
skips; the full repository formatting check passed. The numerical record also
contains native runner and modular-model execution checks. Rejected phase-boundary
roots and the limits of those checks are retained. The fictional field study is
explicitly distinguished from these calculated examples and from plant validation.

## Traceable records

- [Revision and calculation summary](revision_support/revision_report.md)
- [Final content review and resolutions](revision_support/final_content_review.md)
- [Numerical verification](revision_support/calculation_verification.json)
- [Java regression results](revision_support/junit_verification.json)
- [PDF pagination and caption proof](revision_support/renderer_pagination_verification.json)
- [Final PDF visual review](revision_support/pdf_visual_review.md)
- [Final Word visual review](revision_support/word_visual_review.md)
- [Final browser visual review](revision_support/browser_visual_review.json)
- [Output hashes and package checks](revision_support/release_structure.json)
- [Portable HTML image manifest](revision_support/reader_package.json)

Earlier 193-page, 187-page and uncorrected 189-page PDF proofs and earlier Word hashes are superseded
by these final records. The companion foundations book also now introduces this
volume early as the follow-up for industrial multi-agent and tool workflows; its
separate follow-up release addendum records that limited change and rebuild.
