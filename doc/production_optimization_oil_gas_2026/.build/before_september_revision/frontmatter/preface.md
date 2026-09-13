## Preface

Production optimization is at the heart of the oil and gas industry. The ability to extract maximum value from a hydrocarbon asset — safely, efficiently, and sustainably — depends on a deep understanding of every link in the production chain: the reservoir, the wells, the subsea infrastructure, the flowlines, the topside processing facilities, the gas compression and treatment systems, and the export and metering infrastructure. Each of these elements imposes constraints, and true optimization requires modeling and understanding them as an integrated system.

This book grew from more than two decades of practical experience developing and applying the NeqSim thermodynamic and process simulation library to real production optimization challenges on the Norwegian Continental Shelf and beyond. NeqSim is an open-source Java toolkit that provides rigorous thermodynamic calculations, steady-state and dynamic process simulation, equipment rating, and capacity analysis — the fundamental building blocks needed for production optimization.

### Who This Book Is For

This book is intended for three audiences:

1. **Production engineers and operations engineers** in oil and gas who want to understand the theory behind production optimization and learn how to apply computational tools to their daily work — from capacity checks and bottleneck analysis to compressor performance evaluation and separator sizing.

2. **Graduate students** in petroleum engineering, chemical engineering, and process engineering who need a comprehensive reference covering the full production system from reservoir to market, with a strong emphasis on practical thermodynamic and process simulation.

3. **Software developers and data scientists** working on digital twins, model-based optimization, and AI-assisted production management who need to understand the physical models that underpin the digital representations.

### How This Book Is Organized

The book is divided into six parts spanning 24 chapters:

**Part I: Foundations (Chapters 1–3)** introduces production optimization as a discipline, establishes the thermodynamic foundations needed for process simulation, and covers fluid characterization and PVT modeling — the essential input to every production model.

**Part II: From Reservoir to Topside (Chapters 4–8)** traces the hydrocarbon journey from the reservoir through the wells, subsea production systems, flowlines, and risers. It covers inflow performance, multiphase flow, artificial lift, and flow assurance — the threats (hydrates, wax, corrosion, slugging) that production optimization must manage.

**Part III: Separation and Oil Processing (Chapters 9–11)** covers the core of topside oil processing: separation technology (two-phase and three-phase separators, scrubbers, cyclones), oil stabilization and crude treatment, and produced water handling.

**Part IV: Gas Processing and Compression (Chapters 12–16)** is the largest part, reflecting the critical importance of gas handling in modern production facilities. It covers gas processing (dehydration, dew point control, NGL recovery, acid gas removal), gas compression systems, compressor characteristics and performance curves (a major topic in production optimization), heat exchanger thermal design, and valve and pressure relief systems.

**Part V: Export, Metering, and Optimization (Chapters 17–21)** covers the downstream end of production facilities — export systems, fiscal metering, and gas quality — then presents the theoretical framework for production optimization itself, including capacity checks and equipment utilization calculations, optimization algorithms, dynamic simulation and control, and digital twin architectures.

**Part VI: Applications and Case Studies (Chapters 22–24)** applies everything to real-world scenarios: onshore gas processing plants, integrated offshore case studies that exercise the full production chain, and future directions including the energy transition and carbon-conscious production.

### How to Read This Book

Readers with a petroleum or process engineering background can start at Chapter 1 and read sequentially. The thermodynamic foundations in Chapters 2–3 can be skimmed by those already comfortable with equations of state and flash calculations.

Production engineers focused on topside optimization may wish to start with Part III (separation) or Part IV (gas compression) and refer back to earlier chapters as needed.

Those specifically interested in compressor performance and capacity analysis should read Chapters 12–13 and 18 as a unit — these cover compression fundamentals, performance curve generation and interpretation, and equipment utilization calculations.

For digital twin and automation practitioners, Chapters 20–21 provide the framework, but they depend on the process models developed in Parts III and IV.

### Software and Reproducibility

Every figure, table, and calculation in this book can be reproduced using the NeqSim Python package. Each chapter includes Jupyter notebooks that generate the figures and results presented. Install NeqSim with:

```bash
pip install neqsim
```

The NeqSim source code and documentation are available at https://github.com/equinor/neqsim.

All figures are generated from Jupyter notebooks included with the book source, ensuring full reproducibility. The notebooks use NeqSim's Java API via jpype, giving access to the complete thermodynamic and process simulation engine from Python.

### Acknowledgments

I am grateful to the NeqSim community and to colleagues at Equinor for many years of collaborative work on process modeling and production optimization. The experience gained from modeling production systems on the Norwegian Continental Shelf — from small subsea tiebacks to large platform complexes — forms the practical foundation of this book.

Special thanks to the operations and production technology teams who provided real-world insights into what matters most when optimizing a producing asset, and to the many engineers whose questions and challenges motivated the development of NeqSim's production optimization capabilities.

Even Solbraa
Stavanger, 2026
