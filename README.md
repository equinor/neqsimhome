## NeqSim - an open source process simulation software

[![GitHub license](https://img.shields.io/github/license/equinor/neqsim)](https://github.com/equinor/neqsim/blob/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/equinor/neqsim)](https://github.com/equinor/neqsim/stargazers)
[![Maven Central](https://img.shields.io/maven-central/v/com.equinor.neqsim/neqsim)](https://search.maven.org/artifact/com.equinor.neqsim/neqsim)

NeqSim is a library for calculation of fluid behavior, phase equilibrium and process simulation. NeqSim can be used via various toolboxes or the web interface. It is integrated in computer programs via available interfaces in Java, Python, .NET, Matlab or in process simulators via the Cape Open interface. The basis for NeqSim is fundamental mathematical models related to unit operations, phase behaviour and physical properties of fluids. NeqSim is used for fluids such as oil and gas, carbon dioxide, refrigerants, hydrogen, ammonia, water and chemicals. 

Support related to use and development of NeqSim is provided by [Department of Energy and Process Engineering at NTNU](https://www.ntnu.edu/employees/even.solbraa).

## NeqSim — Key Capabilities

- **Advanced Thermodynamics**  
  Multiple EOS and activity-based models for accurate multiphase equilibrium and PVT calculations.

- **Integrated Process Simulation**  
  Steady-state and dynamic simulation with compressors, separators, heat exchangers, and full process flowsheets.

- **Flow Assurance & Production Chemistry**  
  Hydrate, wax, dehydration, and gas treatment modeling for real-field operating conditions.

- **Open, Scriptable & Extensible**  
  Fully accessible via Python and Java APIs—ideal for automation, customization, and research.

- **Built for Digital Twins & AI**  
  Designed for real-time integration, optimization, and machine-learning-driven workflows.
  
## NeqSim project in GitHub
The NeqSim library is written in the Java programming language. The source code and libraries are hosted in GitHub.

* [NeqSim Java](https://github.com/equinor/neqsim)

Also see the [experimental data and parameter fitting project](https://github.com/equinor/neqsimParameterFittingProject)

## NeqSim toolboxes in GitHub
NeqSim toolboxes are available via GitHub for alternative programming languages.

* [NeqSim Matlab](https://github.com/equinor/neqsimmatlab)
* [NeqSim Python](https://github.com/equinor/neqsimpython)
* [NeqSim .NET](https://github.com/equinor/neqsimNET)
* [NeqSim Excel/Cape-Open](https://github.com/equinor/neqsimcapeopen)
* [NeqSim native compilation using GraalVM](https://github.com/equinor/neqsim-native)

## NeqSim User Manual
A comprehensive user manual is available for NeqSim, covering thermodynamic models, methods, and usage examples.

* <a href="doc/neqsim_reference_manual.html" target="_blank">NeqSim User Manual (HTML)</a>
* <a href="javadoc/site/apidocs/index.html" target="_blank">API Documentation (JavaDoc)</a>

## Getting started
NeqSim is integrated in computer programs via interfaces in java, python, .NET and Matlab.

* [Getting started using NeqSim in Java](https://github.com/equinor/neqsim/wiki/Getting-started-with-NeqSim-and-Github)
* [Getting started using NeqSim in Matlab](https://github.com/equinor/neqsimmatlab/wiki/Getting-started-with-NeqSim-in-Matlab)
* [Getting started using NeqSim in Python](https://github.com/equinor/neqsimpython/wiki/Getting-started-with-NeqSim-in-Python)
* [Getting started using NeqSim in Excel](https://github.com/equinor/neqsim.NET/wiki/Getting-started-with-NeqSim-in-Excel)
* [Demo of NeqSim in Colab (Python)](https://colab.research.google.com/github/EvenSol/NeqSim-Colab/blob/master/notebooks/examples_of_NeqSim_in_Colab.ipynb)
* [Getting started as a NeqSim developer](https://github.com/equinor/neqsim/wiki/Getting-started-as-a-NeqSim-developer)

## NeqSim discussion
Questions related to use and development are asked on the [NeqSim github discussions](https://github.com/equinor/neqsim/discussions) page.

## Examples
#### Java:
* [Thermodynamic calculations](https://github.com/equinor/neqsim/tree/master/src/test/java/neqsim/thermo/util/example)
* [Calculation of physical properties](https://github.com/equinor/neqsim/tree/master/src/test/java/neqsim/physicalProperties/util/examples)
* [Process simulation](https://github.com/equinor/neqsim/tree/master/src/test/java/neqsim/processSimulation/util/example)

#### Matlab:
* [Thermodynamic and process calculations](https://github.com/equinor/neqsimmatlab/tree/master/example)

#### Python
* [Python examples](https://github.com/equinor/neqsimpython/tree/master/examples) 
* [Notebook examples (Jupyter/Google Colab)](https://github.com/EvenSol/NeqSim-Colab)
* [NeqSim process project](https://github.com/equinor/neqsimprocess) A project to build up a library of prebuilt process models

#### NeqSim.NET
* [NeqSim .NET](https://github.com/equinor/neqsimNET/tree/master/examples)

#### Excel/Cape Open
* [NeqSim Excel user interface](https://github.com/equinor/neqsim.NET/wiki/Getting-started-with-NeqSim-in-Excel)

## NeqSim API
NeqSim is well suited for being the basis for developing APIs for thermodynamic and process calculations.
* API development in [Java API](https://github.com/EvenSol/NeqSim-Colab/tree/master/API/java) and [Python API](https://github.com/EvenSol/NeqSim-Colab/tree/master/API/python)
* [Example of use of API from Python](https://github.com/EvenSol/NeqSim-Colab/blob/master/API/java/example/TEGprocess.ipynb)

## NeqSimLive 
NeqSimLive is a collection of container-based APIs used for simulation and performance monitoring of process plants. NeqSimLive APIs are typically consumed by company-specific tools for scheduling calculations, visualization and writing of data. Support on developing digital twin components for flow assurance, process and transport can be requested from the [Energy and Process Technology group](https://www.ntnu.no/ansatte/even.solbraa) at NTNU.
* API template for [NeqSimLive Process Digital Twin](https://github.com/equinor/NeqSimLive-api-template)
* [NeqSimLive API](https://github.com/equinor/NeqSimAPI) components

## NeqSim web application
A  web application has been developed to run calculation using neqsim via a web interface. Calculations such as TPflash, dew points, phase envelopes and hydrate equilibrium calculations can be run in the web application. An alternative web application is via Google Colab (Python).
* [NeqSim Streamlit Web application](https://github.com/equinor/neqsimweb2)
* [NeqSim Web on Github](https://github.com/equinor/neqsimweb)

## NeqSim AI
NeqSim Process Reinforcement Learning Agents is an open-source project that leverages multi-agent reinforcement learning (RL) to optimize oil and gas processes simulated using the NeqSim package. This project provides a framework where intelligent agents control different process components, such as compressors, valves, pumps, and heat exchangers, to minimize emissions, CO2 footprint, power and heat input while maintaining product quality and operational stability.
* [NeqSim-Process-RL-Agents](https://github.com/equinor/NeqSim-Process-RL-Agents)

## Benchmark
See [NeqSim-benchmark project](https://github.com/equinor/neqsim-benchmark). 

A benchmark of computational speed of the frameworks is published in the [benchmark page](/benchmark.html)
