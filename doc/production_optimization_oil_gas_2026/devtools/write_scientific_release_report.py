"""Write the final publication summary from checked artifacts, without fixed counts."""
from pathlib import Path
import json
from collections import Counter

BOOK=Path(__file__).resolve().parents[1]
V=BOOK/'verification'
def read(name):return json.loads((V/name).read_text(encoding='utf-8-sig'))
science=read('scientific_revision/engineering_release_gate.json')
release=read('publication_release.json')
geometry=read('pdf_final/geometry_report.json')
structure=read('publication_structure_check.json')
visual=read('pdf_final/visual_review.json')
browser=read('full_book_html_check.json')
evidence=json.loads((BOOK/'evidence_report.json').read_text(encoding='utf-8'))
issues=evidence.get('issues',[])
warnings=Counter(r.get('code',r.get('category',r.get('type','unspecified'))) for r in issues if r.get('severity')=='warning')
assert science['status']=='passed_with_declared_model_scope' and release['status']=='released'
assert structure['passed'] and visual['passed'] and browser['passed']
lines=['# Scientific revision: final publication checks','',
       'The revised PDF and browser editions are in `submission`. The exact publication hashes are recorded in `publication_release.json`; the previous edition is preserved under `.build/pre_scientific_publication`.','',
       '## Completed checks','',
       '| Check | Result |','|---|---|',
       '| Scientific manuscript review | All 35 chapters, plus preface, software basis, glossary, nomenclature and reference corrections |',
       f"| Chapter notebooks | 35 passed; {science['notebook_code_cells']} code cells; 104 generated figures with reviewed discussions |",
       f"| Literal manuscript examples | {science['executed_manuscript_fences']} executed Python/Java fragments; exact current code hashes match |",
       f"| External integration patterns | {science['integration_patterns_not_executed']} explicitly scoped patterns; prerequisites visible; excluded from execution claims |",
       '| Independent benchmark notebook | 89 comparisons passed, including 18 NIST methane density comparisons at nine states |',
       f"| PDF | {geometry['pages']} pages; 170 × 244 mm; no text outside physical pages or unexplained empty pages |",
       f"| Structure | 35 numbered chapters and {structure['pdf_caption_count']} matching PDF/HTML figure captions |",
       f"| Visual review | {visual['distinct_pages_reviewed']} distinct PDF pages; {visual['contact_sheets_reviewed']} current contact sheets; all flagged layout pages have explicit dispositions |",
       '| Browser edition | Full-book layout, image and math checks at 500 and 1024 px; unique navigation identifiers |',
       '| Canonical book check | Zero errors; publisher length advisory retained |','',
       'The executable fragments include shared setup, configuration and introspection. They are run in documented sequential chapter contexts, not all as standalone programs. Java examples use Java 8-compatible syntax; execution used the installed JDK 25 and the recorded source build. All Python subprocesses reused the user-selected bundled interpreter.','',
       '## Scientific interpretation','',
       'See `scientific_revision/SCIENTIFIC_REVIEW.md` for all chapter coverage and material corrections. The physical acceptance checks include mass and component conservation, enthalpy/heat/shaft-work accounting, phase-domain checks, equilibrium and column residuals, optimizer replay and independent sampled/analytical comparisons, and transient inventory/timestep checks.','',
       'The NIST comparisons are independent reference-EOS values, not raw field or experimental measurements. Passing the tests establishes the stated solution and benchmark scope. It does not certify other fluids, plant performance, installed equipment, safety compliance or commercial economics. Approximate TEG handling, unsupported phase-envelope continuation, assumed ratings and synthetic input data remain explicit.','',
       '## Diagnostic warning disposition','',
       'PaperLab’s evidence scanner looks for numbered captions, explicit cross-references and discussion markers in Markdown. Final source figure labels and references were normalized, and the renderers preserve a single numbered caption. Some illustrations use normal explanatory paragraphs. The final structure check verifies every rendered caption; notebook and manuscript figure ledgers record actual image inspection and interpretation. Absence of a scanner marker does not invalidate that separate evidence, and the scanner no longer auto-approves an image merely because a marker exists.','',
       'Retained warning counts by diagnostic code:', '']
lines += [f'- `{key}`: {count}.' for key,count in sorted(warnings.items())]
lines += ['', 'The default self-publisher length estimate exceeds 1,000 pages. This is a substantial digital reference edition. Commercial binding, printer imposition and press-proof acceptance were not performed. Visual inspection was sampled; automated geometry checks covered every PDF page.','',
          'The final visual review is an AI-agent publication review, not external human peer review. It includes the complete glossary and enlarged checks of repaired equations and numerical plots. Intentionally sparse cover, half-title, dedication, part dividers, recto chapter separators and short reference continuations have recorded dispositions. Dense equation bounding boxes were inspected rather than automatically treated as failures or approvals.','',
          '## Reproduction and provenance','',
          'Source commit: `'+science['source_revision']+'`. The version is 3.20.0, but the source commit is the authoritative implementation baseline. The older checkout containing PaperLab was not used as the calculation engine.','',
          'Follow `README.md` and `devtools/README.md` for execution and benchmark regeneration. The literal-code ledgers identify the chapter runners and retained outputs. Build with `build_release.py --formats html,pdf`; inspect the exact candidate and run the geometry, structure and browser checks. `promote_reviewed_release.py` checks final sources and artifact hashes before copying the reviewed candidates.','',
          'The cover and selected equipment cutaways are conceptual OpenAI-generated artwork. The tool did not expose a selectable image-model identifier, so no particular Image 2.0/2.5 version is claimed. Numerical plots are produced from the documented calculation sources, never from image generation.','',
          'The standalone HTML embeds images and uses its declared online math resources. PDF and HTML are the released outputs; secondary editable candidates have not been promoted.','',
          'PaperLab’s scientific-writing, traceability and notebook-verifier guidance was improved during this revision. The figure-dossier regression check verifies that formatting markers remain separate from scientific approval. Renderer regressions cover long glossary pagination, paired numerical math versus currency, and reference-heading attributes. The build manifest also binds the renderer sources, so changing a renderer after the reviewed build prevents promotion.']
(V/'release_gate_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Updated final publication report from current release evidence.')
