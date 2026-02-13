## NeqSim — an Open-Source Process Simulation Software

NeqSim is a library for the calculation of fluid behavior, phase equilibrium, and process simulation. NeqSim can be used via various toolboxes or through a web interface. It can be integrated into computer programs via available interfaces in Java, Python, .NET, and MATLAB, or into process simulators via the CAPE-OPEN interface.

The basis for NeqSim is fundamental mathematical models related to unit operations, phase behavior, and physical properties of fluids. NeqSim is used for fluids such as oil and gas, carbon dioxide, refrigerants, hydrogen, ammonia, water, and chemicals.

Support related to the use and development of NeqSim is provided by the [Department of Energy and Process Engineering at NTNU](https://www.ntnu.edu/employees/even.solbraa).

---

## NeqSim — Key Capabilities
- Advanced thermodynamics and property models  
- Integrated process simulation  
- PVT simulation  
- Flow assurance & production chemistry  
- Fluid flow & pipeline simulation  
- Production optimization & calibration  
- Risk-based process safety analysis  
- Sustainability & emissions tracking  
- Field development & concept screening  
- Open, scriptable & extensible  
- Digital process twins & AI integration  

---

## NeqSim Project on GitHub
The NeqSim library is written in the Java programming language. The source code and libraries are hosted on GitHub.

* [NeqSim Java](https://github.com/equinor/neqsim)

Also see the [experimental data and parameter fitting project](https://github.com/equinor/neqsimParameterFittingProject).

---

## NeqSim Toolboxes on GitHub
NeqSim toolboxes are available on GitHub for alternative programming languages.

* [NeqSim MATLAB](https://github.com/equinor/neqsimmatlab)  
* [NeqSim Python](https://github.com/equinor/neqsimpython)  
* [NeqSim .NET](https://github.com/equinor/neqsimNET)  
* [NeqSim Excel/CAPE-OPEN](https://github.com/equinor/neqsimcapeopen)  
* [NeqSim native compilation using GraalVM](https://github.com/equinor/neqsim-native)

---

## NeqSim User Documentation
A comprehensive user manual is available for NeqSim, covering thermodynamic models, methods, and usage examples.

* [NeqSim Documentation Page](https://equinor.github.io/neqsim/)  
* [NeqSim User Manual (HTML)](https://equinor.github.io/neqsim/manual/neqsim_reference_manual.html)  
* [API Documentation (Javadoc)](javadoc/site/apidocs/index.html)

---

## Getting Started
NeqSim can be integrated into computer programs via interfaces in Java, Python, .NET, and MATLAB.

* [Getting started using NeqSim in Java](https://github.com/equinor/neqsim/wiki/Getting-started-with-NeqSim-and-Github)  
* [Getting started using NeqSim in MATLAB](https://github.com/equinor/neqsimmatlab/wiki/Getting-started-with-NeqSim-in-Matlab)  
* [Getting started using NeqSim in Python](https://github.com/equinor/neqsimpython/wiki/Getting-started-with-NeqSim-in-Python)  
* [Getting started using NeqSim in Excel](https://github.com/equinor/neqsim.NET/wiki/Getting-started-with-NeqSim-in-Excel)  
* [Demo of NeqSim in Colab (Python)](https://colab.research.google.com/github/EvenSol/NeqSim-Colab/blob/master/notebooks/examples_of_NeqSim_in_Colab.ipynb)  
* [Getting started as a NeqSim developer](https://github.com/equinor/neqsim/wiki/Getting-started-as-a-NeqSim-developer)

---

## NeqSim Discussions
Questions related to use and development can be asked on the [NeqSim GitHub Discussions](https://github.com/equinor/neqsim/discussions) page.

---

## Examples

### Java
* [Thermodynamic calculations](https://github.com/equinor/neqsim/tree/master/src/test/java/neqsim/thermo/util/example)  
* [Calculation of physical properties](https://github.com/equinor/neqsim/tree/master/src/test/java/neqsim/physicalProperties/util/examples)  
* [Process simulation](https://github.com/equinor/neqsim/tree/master/src/test/java/neqsim/processSimulation/util/example)

### MATLAB
* [Thermodynamic and process calculations](https://github.com/equinor/neqsimmatlab/tree/master/example)

### Python
* [Python examples](https://github.com/equinor/neqsimpython/tree/master/examples)  
* [Notebook examples (Jupyter/Google Colab)](https://github.com/EvenSol/NeqSim-Colab)  
* [NeqSim process project](https://github.com/equinor/neqsimprocess) — A project to build a library of prebuilt process models

### NeqSim.NET
* [NeqSim .NET examples](https://github.com/equinor/neqsimNET/tree/master/examples)

### Excel/CAPE-OPEN
* [NeqSim Excel user interface](https://github.com/equinor/neqsim.NET/wiki/Getting-started-with-NeqSim-in-Excel)

---

## NeqSim API
NeqSim is well suited as a basis for developing APIs for thermodynamic and process calculations.

* API development in [Java API](https://github.com/EvenSol/NeqSim-Colab/tree/master/API/java) and [Python API](https://github.com/EvenSol/NeqSim-Colab/tree/master/API/python)  
* [Example of API usage from Python](https://github.com/EvenSol/NeqSim-Colab/blob/master/API/java/example/TEGprocess.ipynb)

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
