# PaperLab paper-to-chapter reuse assessment

Reviewed 12 September 2026 through `agents/book_author.paperlab.md` and
`skills/book_creation/SKILL.md`. This is a source and reuse map for the existing
book revision. The three paper projects under `../../papers/` were inspected at
their `paper.md`, `refs.bib` and project metadata. Their own abstracts and draft
labels are not evidence that all claims have been reproduced on this book's
source snapshot.

| Existing PaperLab project | Relevant book chapters | Reuse decision and rationale |
|---|---|---|
| `tpflash_algorithms_2026` — *Systematic Characterization of a Hybrid Successive-Substitution–Newton Flash Algorithm for Multicomponent Natural Gas Systems* | 3: The NeqSim Physics Engine; 9: Thermodynamic Property Calculations | Reused the foundational bibliography candidates for Soave, Peng–Robinson, Michelsen Parts I/II, and Rachford–Rice. They match the book's existing keys and are now DOI-linked after Crossref verification. Retained the book's own notation and executable methane example. The paper's reported 1,664-case convergence coverage and CPU timings were not imported: they have a distinct mixture suite, runtime, implementation basis and performance question, none re-run as part of this book release. |
| `implicit_cpa_performance_2026` — *Evaluation of a Fully Implicit CPA Algorithm for Industrially Relevant Associating Fluid Systems* | 3: The NeqSim Physics Engine; possible advanced follow-up to 9 | Reused the DOI for the existing `kontogeorgis1996` entry, with author metadata independently checked. Did not copy its `Ioannis V. Yakoumis` spelling: publisher-deposited metadata for the 1996 article gives `Iakovos V. Yakoumis`, already used by the book. CPA algorithm papers and association-theory references remain future reading candidates; detailed implicit-solver derivations are outside this introduction. No draft speedup plots, 2–33× claims, or “zero accuracy loss” conclusion were imported. Such claims need versioned benchmark execution and stated tolerances before reuse. |
| `gibbs_minimization_2026` — *Robust Gibbs Free Energy Minimization for Chemical Equilibrium Calculations with Cubic Equations of State* | 3: numerical stability and physical constraints; 7: verification workflow; 13: evaluation of new capabilities | Confirmed overlap with `smith2005`, `michelsen1982a` and the NeqSim software source, retaining existing book keys instead of adding duplicate entries. White et al., NASA CEA, constrained minimization and numerical-optimization references would be appropriate for a future reactive-equilibrium chapter, not the current non-reactive worked examples. The draft's iteration-reduction and equilibrium-composition tables were not imported because the reactive species set, algorithms and validation suite differ from this book. |

## Asset-level decision

No paper figures, benchmark tables or numerical results were copied into the
book. The revised book already has original explanatory diagrams and executed
chapter-specific calculations. Importing paper plots merely to satisfy an asset
count would weaken the connection between the chapter's question and its
evidence. The existing papers were used to locate relevant methods and reliable
bibliographic identifiers, with independent metadata checks before acceptance.

## Bibliographic key mapping

| Paper key | Retained book key | Action |
|---|---|---|
| `Soave1972` | `soave1972` | Matched DOI and publication metadata; no duplicate entry |
| `PengRobinson1976` | `peng1976` | Matched DOI and publication metadata; no duplicate entry |
| `Michelsen1982a` | `michelsen1982a` | Matched DOI and publication metadata; no duplicate entry |
| `Michelsen1982b` | `michelsen1982b` | Direct DOI lookup resolved an initial rate-limited enrichment search |
| `RachfordRice1952` | `rachford1952` | Matched DOI; preserved publisher-deposited page range `19–3` despite the paper's shorter `19` field |
| `Kontogeorgis1996` | `kontogeorgis1996` | Matched DOI; retained publisher-verified given name |
| `SmithVanNess2005` | `smith2005` | Same seventh-edition textbook; no unverified DOI assigned |
| `neqsim2024` | `neqsim2026`, `neqsim_release_320` | Existing release/source references are more appropriate for this revision |

Metadata evidence is in `verification/bibliography_metadata.json`. The complete
enrichment outcomes, accepted changes and limitations are in
`bibliography_audit.md` and `refs.enrichment_report.json`.
