"""Apply the September book metadata revision and preserve original frontmatter."""
from pathlib import Path
import json
import shutil
import sys

BOOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / '.build' / 'python_packages'))
import yaml

REVISION = '6cc8026202a5d3f9383c9abd1d97d448993813f9'
BACKUP = BOOK / '.build' / 'before_september_revision'

def save(path, text):
    backup = BACKUP / path.relative_to(BOOK)
    if path.exists() and not backup.exists():
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

config_path = BOOK / 'book.yaml'
cfg = yaml.safe_load(config_path.read_text(encoding='utf-8-sig'))
cfg['edition'] = '1st, revised'
cfg['revision_date'] = '2026-09-12'
cfg['software_basis'] = {'project': 'NeqSim', 'version': '3.20.0', 'git_revision': REVISION,
    'source_date': '2026-09-12', 'verification_report': 'verification/release_gate_report.md',
    'note': 'Source revision is authoritative; the released 3.20.0 JAR alone is not the revision baseline.'}
cfg['settings'].update({'book_type': 'textbook', 'page_size': '170x244mm',
    'font_size': 10, 'font_family': 'Libertinus Serif', 'line_spacing': 1.1,
    'margins': {'top': '19mm', 'bottom': '19mm', 'inner': '21mm', 'outer': '17mm'},
    'code_font_size': 7.2, 'table_font_size': 8.2, 'toc_depth': 2})
if 'software_revision' not in cfg['frontmatter']:
    cfg['frontmatter'].append('software_revision')
save(config_path, yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True, width=100))

preface = '''## Preface

Production optimization connects the reservoir, wells, transport network and processing plant to a commercial objective. A useful operating recommendation must explain both the value it creates and the physical restriction that limits it. Increasing a well rate can consume compression power, reduce separation performance, change export quality or move the bottleneck to another part of the facility.

This book develops that integrated view using NeqSim. It combines the thermodynamics and equipment physics needed to build a production model with the numerical methods, capacity evidence and operating workflows needed to use the model responsibly. The intended readers are production and process engineers, graduate students, and developers building engineering applications around NeqSim.

### What Changed in This Revision

The September 2026 revision updates the book against a recorded NeqSim source checkout. It revisits the code examples, corrects chapter numbering and unit conventions, and brings current optimization, equipment-evidence and automation capabilities into the discussion. Particular attention is given to reproducing the selected operating point, distinguishing installed ratings from screening assumptions, and separating process-capacity tables from well VFP data.

Numerical plots and tables belong to the computational examples. The new cover and equipment cutaways are conceptual illustrations; their visual detail does not establish equipment geometry or performance. The verification record accompanying the book identifies what was executed, the software revision used, and any examples requiring external infrastructure.

### How This Book Is Organized

The book contains nine parts and 35 chapters.

| Part | Chapters | Engineering focus |
|---|---|---|
| I. Foundations | 1–3 | Production objectives, thermodynamics, fluid characterization and PVT |
| II. Reservoir and Wells | 4–6 | Reservoir response, inflow, tubing, well networks and artificial lift |
| III. Subsea Systems and Transport | 7–9 | Subsea production, pipeline hydraulics and flow assurance |
| IV. Topside Processing | 10–13 | Separation, stabilization, gas conditioning and produced water |
| V. Compression, Heat Transfer, and Power | 14–18 | Compression, installed maps, thermal design, valves and energy supply |
| VI. Export, Capacity, and Debottlenecking | 19–21 | Product delivery, capacity evidence and bottleneck removal |
| VII. Production Optimization | 22–28 | Search methods, NeqSim implementation, monitoring, networks and uncertainty |
| VIII. Dynamic Operations and Advanced Methods | 29–32 | Dynamics, automation, convergence and advanced optimization |
| IX. Applications and Outlook | 33–35 | Onshore plants, integrated cases and further development |

### Reading Routes

A reader new to NeqSim should begin with Chapters 1–3 and then follow the production chain. For topside capacity work, read Chapters 10–18 followed by Chapters 20–24. For compression studies, read Chapters 14–15, 18 and 20 together: the machine map, driver supply and plant operating restriction are different parts of the same decision.

For network optimization, combine Chapters 4–9 with Chapters 26–28. For digital twins and automated studies, begin with the model and evidence interfaces in Chapters 23–25, then proceed to Chapters 29–32. Chapter 34 brings these strands together.

### Working with the Examples

Use the source revision and environment described in the software-revision note. Follow the setup and prerequisite statements in each example, and retain units when transferring values between a notebook, a table and an operating specification. Synthetic fluids and ratings illustrate the method; replace them with a documented field basis before interpreting a study as a facility recommendation.

A successful calculation is only the first check. Examine convergence, mass and energy balance, phase state, enabled constraints, and the final replay of the selected point. Where an example presents a simplified correlation or conceptual diagram, its purpose is to explain a mechanism rather than qualify an installation.

### Acknowledgments

I am grateful to the NeqSim community and to colleagues at Equinor for many years of collaborative work on process modeling and production optimization. Questions from production and operations engineers, and the practical challenges of modeling offshore systems, have shaped both the software and this book.

Even Solbraa  
Stavanger, 2026
'''
save(BOOK / 'frontmatter' / 'preface.md', preface)
software = f'''## Software Basis and Reproducibility

This revision follows NeqSim source commit `{REVISION}`, dated 12 September 2026. The project version at that commit is 3.20.0. The commit identifies the implemented behavior more precisely than the version number: a packaged 3.20.0 installation may predate the changes described here.

### The Calculation Record

The companion source includes the chapter notebooks, executable-example checks, figures and verification reports. Use a full JDK and the deliberately selected Python interpreter. Notebook setup loads compiled workspace classes through `neqsim_dev_setup`; it must not silently replace the source build with an older packaged JAR. Compile the recorded source before executing the examples.

The verification record should be read with the book. It distinguishes successfully executed calculations, numerical checks, source-level API review and examples requiring a plant historian, control system or other external service. An integration pattern does not demonstrate a live plant connection.

### Current Capabilities in Context

| Capability | Where to use it in this book | Interpretation |
|---|---|---|
| PVT calibration and validation workflows | Chapter 3 | Keep regression data separate from independent validation observations |
| Explicit installed-equipment and constraint evidence | Chapters 10, 14–15, 20–21 | A calculated utilization is meaningful only with its rating basis and applicability |
| Shared-resource and common-shaft evidence | Chapters 18, 20 and 23 | Check declared participants, units, current solve and coverage |
| Final-point replay in production optimization | Chapters 23–24 and 27 | Re-solve the selected decisions before reporting an accepted result |
| Structured automation and bounded agentic search | Chapters 23, 25 and 30–32 | Inspect rejected setpoints, failed readbacks, constraints and convergence |
| Qualified VFP serialization | Chapters 26 and 28 | Supplied well BHP and standard phase-volume axes are distinct from process screening |

### Reading the Figures

Simulation figures show the stated inputs, output units and model assumptions. Sensitivity plots describe the evaluated range; a smooth curve alone does not establish a global optimum. An apparent capacity margin is conditional on the constraints actually configured and sampled.

The cover and the separator and compressor cutaways were created with OpenAI's built-in image-generation tool and selected for explanatory use. They are marked as conceptual artwork. The tool did not expose a selectable model identifier, so this edition does not claim that a specific image-model version was used. Prompts and asset provenance are retained with the source.

### Source Reference

NeqSim Project. *NeqSim source and documentation, September 2026 revision*. [Recorded source revision](https://github.com/equinor/neqsim/tree/{REVISION}). See the source documentation on optimization validation and the VFP export contract for the detailed execution and data conventions.
'''
save(BOOK / 'frontmatter' / 'software_revision.md', software)
title = (BOOK / 'frontmatter' / 'title_page.md').read_text(encoding='utf-8-sig')
save(BOOK / 'frontmatter' / 'title_page.md', title.replace('*First Edition*', '*First Edition · Revised September 2026*'))

bib = (BOOK / 'refs.bib').read_text(encoding='utf-8-sig')
if '@misc{neqsim2026update,' not in bib:
    bib += '\n@misc{neqsim2026update,\n  author = {{NeqSim Project}},\n  title = {{NeqSim Source and Documentation: September 2026 Revision}},\n  year = {2026},\n  url = {https://github.com/equinor/neqsim/tree/' + REVISION + '},\n  note = {Source commit ' + REVISION + '; accessed 12 September 2026. Project version 3.20.0; source revision is authoritative.}\n}\n'
    save(BOOK / 'refs.bib', bib)

manifest = json.loads((BOOK / 'verification' / 'illustration_manifest.json').read_text())
for asset in manifest['assets']:
    destination = BOOK / asset['filename']
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        backup = BACKUP / asset['filename']
        if not backup.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, backup)
    shutil.copy2(asset['source'], destination)
print('Revised manifest, preface, software note, bibliography and illustration assets.')
