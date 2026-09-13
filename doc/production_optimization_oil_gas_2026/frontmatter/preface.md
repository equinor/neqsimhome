## Preface

Production optimization connects the reservoir, wells, transport network and processing plant to a commercial objective. A useful operating recommendation must explain both the value it creates and the physical restriction that limits it. Increasing a well rate can consume compression power, reduce separation performance, change export quality or move the bottleneck to another part of the facility.

This book develops that integrated view using NeqSim. It combines the thermodynamics and equipment physics needed to build a production model with the numerical methods, capacity evidence and operating workflows needed to use the model responsibly. The intended readers are production and process engineers, graduate students, and developers building engineering applications around NeqSim.

### What Changed in This Revision

The September 2026 revision updates the book against a recorded NeqSim source checkout. It revisits the code examples, corrects chapter numbering and unit conventions, and brings current optimization, equipment-evidence and automation capabilities into the discussion. Particular attention is given to reproducing the selected operating point, distinguishing installed ratings from screening assumptions, and separating process-capacity tables from well VFP data.

Numerical plots and tables belong to the computational examples. The new cover and equipment cutaways are conceptual illustrations; their visual detail does not establish equipment geometry or performance. The verification record accompanying the book identifies what was executed, the software revision used, and any examples requiring external infrastructure.

A further scientific review checks the equations, units, reference conditions and reasoning throughout the text. The worked calculations now include explicit physical acceptance tests, and a separate benchmark notebook compares selected properties with NIST reference data and tests analytical limits. This review corrects misleading results as well as code errors: a solver may terminate while a material balance, energy boundary or operating constraint is still wrong. The companion evidence record distinguishes those solution checks from independent validation of predictive model accuracy.

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
