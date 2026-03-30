<!-- badges -->
[![GitHub stars](https://img.shields.io/github/stars/equinor/neqsim?style=social)](https://github.com/equinor/neqsim)
[![Maven Central](https://img.shields.io/maven-central/v/com.equinor.neqsim/neqsim.svg?label=Maven%20Central)](https://search.maven.org/search?q=g:%22com.equinor.neqsim%22%20AND%20a:%22neqsim%22)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://github.com/equinor/neqsim/blob/master/LICENSE)
[![CI](https://github.com/equinor/neqsim/actions/workflows/verify_build.yml/badge.svg?branch=master)](https://github.com/equinor/neqsim/actions/workflows/verify_build.yml?query=branch%3Amaster)

## Open-source thermodynamics, process simulation, and AI-assisted engineering — in one library.

**NeqSim** calculates fluid properties, simulates process equipment, and solves engineering design problems. Use it from Python, Java, .NET, MATLAB, Jupyter notebooks, or let an AI agent drive it via natural language.

> Developed at [NTNU](https://www.ntnu.edu/employees/even.solbraa) and maintained by [Equinor](https://www.equinor.com/). Used for real-world oil & gas, carbon capture, hydrogen, and energy applications.

---

## Try it in 30 seconds

**Python** — the fastest way to start:

```bash
pip install neqsim
```

```python
from neqsim import jneqsim

fluid = jneqsim.thermo.system.SystemSrkEos(273.15 + 25.0, 60.0)
fluid.addComponent("methane", 0.85)
fluid.addComponent("ethane", 0.10)
fluid.addComponent("propane", 0.05)
fluid.setMixingRule("classic")

ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid)
ops.TPflash()
fluid.initProperties()

print(f"Gas density:   {fluid.getPhase('gas').getDensity('kg/m3'):.2f} kg/m³")
print(f"Z-factor:      {fluid.getPhase('gas').getZ():.4f}")
```

**AI agent** — describe your problem in plain English:

```
@solve.task hydrate formation temperature for wet gas at 100 bara
```

The agent builds a NeqSim simulation, validates results, and generates a report — no coding required.

[▶ Run in Google Colab](https://colab.research.google.com/github/EvenSol/NeqSim-Colab/blob/master/notebooks/examples_of_NeqSim_in_Colab.ipynb) · [▶ Python quickstart](https://github.com/equinor/neqsimpython/wiki/Getting-started-with-NeqSim-in-Python) · [▶ Java quickstart](https://github.com/equinor/neqsim/wiki/Getting-started-with-NeqSim-and-Github) · [▶ MCP server](https://github.com/equinor/neqsim/tree/master/neqsim-mcp-server)

---

## What can you do with NeqSim?

| Domain | Capabilities |
|--------|-------------|
| **Thermodynamics** | 60+ equation-of-state models (SRK, PR, CPA, GERG-2008, …), flash calculations (TP, PH, PS, dew, bubble), phase envelopes |
| **Physical properties** | Density, viscosity, thermal conductivity, surface tension, diffusion coefficients |
| **Process simulation** | 33+ equipment types — separators, compressors, heat exchangers, valves, distillation, pumps, reactors |
| **Pipeline & flow** | Steady-state and transient multiphase pipe flow, pipe networks |
| **PVT simulation** | CME, CVD, differential liberation, separator tests, swelling tests, saturation pressure |
| **Safety** | Depressurization/blowdown, PSV sizing (API 520/521), source term generation, safety envelopes |
| **Standards** | ISO 6976 (gas quality), NORSOK, DNV, API, ASME compliance checks |
| **Field development** | Production forecasting, concept screening, NPV/IRR economics, Monte Carlo uncertainty |
| **AI / MCP** | Natural-language engineering via MCP server — any LLM can run rigorous thermodynamic calculations |

---

## AI-Powered Engineering with MCP

The [NeqSim MCP Server](https://github.com/equinor/neqsim/tree/master/neqsim-mcp-server) lets **any MCP-compatible client** (VS Code Copilot, Claude Desktop, Cursor, etc.) run real calculations through natural language:

| Ask the LLM | What happens |
|---|---|
| *"Dew point of 85% methane, 10% ethane, 5% propane at 50 bara?"* | Flash calculation via NeqSim |
| *"Get density, viscosity, and thermal conductivity at 25 °C, 80 bara"* | Physical property lookup |
| *"Simulate gas through a separator then compressor to 120 bara"* | Full process simulation |

LLMs are excellent at engineering reasoning but hallucinate physics. NeqSim is exact on thermodynamics. **Together, they form a complete engineering system.**

---

## Get Started — Choose Your Path

| Path | How to start |
|------|-------------|
| **Python** | `pip install neqsim` — [quickstart guide](https://github.com/equinor/neqsimpython/wiki/Getting-started-with-NeqSim-in-Python) |
| **Google Colab** | [Open notebook now](https://colab.research.google.com/github/EvenSol/NeqSim-Colab/blob/master/notebooks/examples_of_NeqSim_in_Colab.ipynb) — zero install |
| **Java** | [Maven Central dependency](https://github.com/equinor/neqsim/wiki/Getting-started-with-NeqSim-and-Github) |
| **MATLAB** | [neqsimmatlab toolbox](https://github.com/equinor/neqsimmatlab/wiki/Getting-started-with-NeqSim-in-Matlab) |
| **.NET / Excel** | [neqsimcapeopen](https://github.com/equinor/neqsim.NET/wiki/Getting-started-with-NeqSim-in-Excel) |
| **MCP / AI agent** | [neqsim-mcp-server](https://github.com/equinor/neqsim/tree/master/neqsim-mcp-server) |
| **VS Code devcontainer** | Clone → open in VS Code → container auto-builds |

---

## Engineering Cookbook — Common Recipes

Quick copy-paste solutions for common engineering problems:

| Recipe | Description |
|--------|-------------|
| [Calculate gas dew point](https://github.com/equinor/neqsim/wiki) | Find hydrocarbon and water dew points at pipeline conditions |
| [Estimate hydrate formation temperature](https://github.com/equinor/neqsim/wiki) | Predict hydrate risk for wet gas systems |
| [Simulate separator + compressor train](https://github.com/equinor/neqsim/wiki) | Build a basic gas processing flowsheet |
| [Calculate density and viscosity](https://github.com/equinor/neqsim/wiki) | Get transport properties for natural gas or oil |
| [Perform TP/PH/PS flash](https://github.com/equinor/neqsim/wiki) | Run any standard flash calculation |
| [Estimate pipeline pressure drop](https://github.com/equinor/neqsim/wiki) | Multiphase flow with Beggs & Brill |
| [TEG dehydration process](https://github.com/equinor/neqsim/wiki) | Full absorption/regeneration loop |
| [Gas quality — ISO 6976](https://github.com/equinor/neqsim/wiki) | Calorific value, Wobbe index, density compliance |

See 30+ Jupyter notebooks in the [examples collection](https://github.com/EvenSol/NeqSim-Colab).

---

## Showcase — End-to-End Case Studies

Real engineering workflows solved with NeqSim:

**Gas Compression Train Sizing** — Define feed gas, separate liquids, compress in stages with intercooling, calculate power and outlet conditions.

**TEG Dehydration Workflow** — Model absorber, flash drum, regenerator, and recycle. Check water dew point spec at outlet.

**PVT Lab Matching** — Import lab data (CME, CVD, separator tests), tune EOS parameters, predict reservoir fluid behavior.

**Blowdown / Depressurization Study** — Simulate vessel blowdown, track minimum metal temperature, size PSV per API 520/521.

**Sales Gas Quality Check** — Verify ISO 6976 compliance: calorific value, Wobbe index, hydrocarbon dew point, H₂S/CO₂ limits.

**Offshore Field Process Model** — Wellhead → manifold → separator train → export pipeline, with production forecasting and economics.

All examples are available as runnable notebooks in [NeqSim-Colab](https://github.com/EvenSol/NeqSim-Colab) and [examples/notebooks](https://github.com/equinor/neqsim/tree/master/examples/notebooks).

---

## How NeqSim Compares

| Feature | NeqSim | Aspen HYSYS / UniSim | DWSIM | CoolProp |
|---------|--------|---------------------|-------|----------|
| **Open source** | ✅ Apache-2.0 | ❌ Commercial | ✅ GPL | ✅ MIT |
| **Thermodynamic depth** | 60+ EOS, CPA, electrolytes | Extensive | Moderate | Pure fluids only |
| **Process simulation** | 33+ unit ops, dynamic | Full-featured | Full-featured | ❌ Properties only |
| **Scriptable / automatable** | ✅ Java, Python, .NET, MATLAB | Limited COM/scripting | Python | Python, C++ |
| **AI / MCP ready** | ✅ MCP server, AI agents | ❌ | ❌ | ❌ |
| **Notebook-friendly** | ✅ Jupyter / Colab | ❌ GUI-based | Partial | ✅ |
| **PVT simulation** | ✅ Full suite | ✅ Full suite | Partial | ❌ |
| **Safety / standards** | ✅ API, ISO, NORSOK | ✅ Built-in | Limited | ❌ |
| **Multiphase flow** | ✅ Beggs & Brill, two-fluid | Via extensions | ❌ | ❌ |
| **Cost** | Free | $10k–$100k+/year | Free | Free |

**Where NeqSim excels:** Scriptability, AI integration, open-source flexibility, combined thermo + process + safety in one library.
**Where it is maturing:** GUI/visual flowsheet editor, real-time training solver, graphic reports.

---

## Documentation & Resources

| Resource | Link |
|----------|------|
| **User documentation** | [equinor.github.io/neqsim](https://equinor.github.io/neqsim/) |
| **Reference manual** | [350+ page reference](https://equinor.github.io/neqsim/manual/neqsim_reference_manual.html) |
| **JavaDoc API** | [API reference](javadoc/site/apidocs/index.html) |
| **Jupyter notebooks** | [30+ examples](https://github.com/EvenSol/NeqSim-Colab) |
| **WebApp** | [neqsim.streamlit.app](https://neqsim.streamlit.app/) |
| **Discussion forum** | [GitHub Discussions](https://github.com/equinor/neqsim/discussions) |

---

## NeqSim on GitHub

The NeqSim library is written in Java. Source code and releases are on GitHub:

* [**NeqSim Java** (core library)](https://github.com/equinor/neqsim) — 104 ⭐ · 40 forks · 120+ releases
* [NeqSim Python](https://github.com/equinor/neqsimpython) — `pip install neqsim`
* [NeqSim MATLAB](https://github.com/equinor/neqsimmatlab)
* [NeqSim .NET / Excel / CAPE-OPEN](https://github.com/equinor/neqsimcapeopen)
* [NeqSim native (GraalVM)](https://github.com/equinor/neqsim-native)
* [NeqSim process models](https://github.com/equinor/neqsimprocess)
* [NeqSim-Colab notebooks](https://github.com/EvenSol/NeqSim-Colab)
* [Parameter fitting project](https://github.com/equinor/neqsimParameterFittingProject)

---

## Contribute

We welcome contributions — bug fixes, new models, examples, documentation, and notebook recipes.

| Contribution type | Where to start |
|-------------------|---------------|
| **Bug fixes & features** | [CONTRIBUTING.md](https://github.com/equinor/neqsim/blob/master/CONTRIBUTING.md) |
| **Documentation** | [docs/](https://github.com/equinor/neqsim/tree/master/docs) — improve guides and tutorials |
| **Notebook recipes** | [examples/notebooks/](https://github.com/equinor/neqsim/tree/master/examples/notebooks) — add engineering examples |
| **Validation & benchmarks** | Compare NeqSim vs. reference data and publish results |
| **MCP / AI tools** | [neqsim-mcp-server/](https://github.com/equinor/neqsim/tree/master/neqsim-mcp-server) — add tool schemas |
| **Good first issues** | [Browse issues](https://github.com/equinor/neqsim/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) |

---

## Examples

### Java
* [Thermodynamic calculations](https://github.com/equinor/neqsim/tree/master/src/test/java/neqsim/thermo/util/example)
* [Physical properties](https://github.com/equinor/neqsim/tree/master/src/test/java/neqsim/physicalProperties/util/examples)
* [Process simulation](https://github.com/equinor/neqsim/tree/master/src/test/java/neqsim/processSimulation/util/example)

### Python
* [Python examples](https://github.com/equinor/neqsimpython/tree/master/examples)
* [Jupyter / Google Colab notebooks](https://github.com/EvenSol/NeqSim-Colab)
* [NeqSim process project](https://github.com/equinor/neqsimprocess)

### Other
* [MATLAB examples](https://github.com/equinor/neqsimmatlab/tree/master/example)
* [.NET examples](https://github.com/equinor/neqsimNET/tree/master/examples)
* [Excel / CAPE-OPEN](https://github.com/equinor/neqsim.NET/wiki/Getting-started-with-NeqSim-in-Excel)
* [Java & Python API development](https://github.com/EvenSol/NeqSim-Colab/tree/master/API)

---

## NeqSimLive
NeqSimLive is a collection of container-based APIs used for simulation and performance monitoring of process plants. NeqSimLive APIs are typically consumed by company-specific tools for scheduling calculations, visualization, and data writing.

Support for developing digital twin components for flow assurance, process, and transport can be requested from the [Energy and Process Technology group](https://www.ntnu.no/ansatte/even.solbraa) at NTNU.

* [NeqSimLive Process Digital Twin API template](https://github.com/equinor/NeqSimLive-api-template)  
* [NeqSimLive API components](https://github.com/equinor/NeqSimAPI)

---

## NeqSim Web Applications
A web application has been developed to run calculations using NeqSim via a web interface. Calculations such as TPflash, dew points, phase envelopes, and hydrate equilibrium calculations can be performed in the web application. An alternative web interface is available via Google Colab (Python).

* [NeqSim Streamlit Web application](https://github.com/equinor/neqsimweb2)  
* [NeqSim Web on GitHub](https://github.com/equinor/neqsimweb)

---

## NeqSim AI
NeqSim Process Reinforcement Learning Agents is an open-source project that leverages multi-agent reinforcement learning (RL) to optimize oil and gas processes simulated using the NeqSim package. The framework allows intelligent agents to control different process components — compressors, valves, pumps, and heat exchangers — to minimize emissions, CO₂ footprint, power consumption, and heat input while maintaining product quality and operational stability.

* [NeqSim-Process-RL-Agents](https://github.com/equinor/NeqSim-Process-RL-Agents)

---

## Benchmark
See the [NeqSim benchmark project](https://github.com/equinor/neqsim-benchmark).

A benchmark of computational speed is published on the [benchmark page](/benchmark.html).
