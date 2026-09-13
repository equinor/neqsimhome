# Editable export candidates

These Word and ODF files are internal candidates, not reviewed publication
deliverables. The primary book release is the independently checked PDF.

`source/` contains a frozen copy of the source files used for each render.
`source_manifest.json` records their SHA-256 hashes. The current build status,
output hashes, chapter/figure/table checks, equation conversion counts, image
bounds and aspect-ratio checks are in
`../../verification/editable_export_report.json` relative to this directory.

The prescribed documents renderer was attempted with the selected bundled
Python runtime. It cannot render pages because LibreOffice `soffice.exe` is
not available in this runtime. No page-by-page visual review has been possible.
Do not promote the candidates to the book's `submission/` directory until that
review is complete. ODF equations use editable Unicode text rather than native
MathML; Word equations use native OMML where the report confirms conversion.

The two-chapter `fixture/` exercises trim, source copyright, separate images
with repeated filenames, tables, code line breaks, currency, inline equations,
integration prerequisites, and citations. Its report is `fixture_report.json`.
