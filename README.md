## What is NeqSim?
[NeqSim](https://equinor.github.io/neqsimhome/) (Non-Equilibrium Simulator) is a library for estimation of fluid properties and process simulation. NeqSim can be used as a stand-alone tool via Excel or a web interface. It is integrated in computer programs via available interfaces in Java, Python, .NET and Matlab. The basis for NeqSim is fundamental mathematical models related to phase behaviour and physical properties of oil and gas.

The original NeqSim web page is hosted at [NTNU](http://folk.ntnu.no/solbraa/neqsim/NeqSim.htm)

## NeqSim project in GitHub
The NeqSim library is written in the Java programming language. The source code and libraries are hosted in GitHub

* [NeqSim Java](https://github.com/equinor/neqsim)

## NeqSim toolboxes in GitHub
NeqSim toolboxes are avalable via GitHub for alternative programming languages.

* [NeqSim Matlab](https://github.com/equinor/neqsimmatlab)
* [NeqSim Python](https://github.com/equinor/neqsimpython)
* [NeqSim .NET](https://github.com/equinor/neqsimNET)
* [NeqSim Cape Open](https://github.com/equinor/neqsimcapeopen)

## Getting started
NeqSim is integrated in computer programs via interfaces in java, python, .NET and Matlab.

* [Getting started using NeqSim in Java](https://github.com/equinor/neqsim/wiki/Getting-started-with-NeqSim-and-Github)
* [Getting started using NeqSim in Matlab](https://github.com/equinor/neqsimmatlab/wiki/Getting-started-with-NeqSim-in-Matlab)
* [Getting started using NeqSim in Python](https://github.com/equinor/neqsimpython/wiki/Getting-started-with-NeqSim-in-Python)
* [Demo of NeqSim in Colab (Python)](https://colab.research.google.com/github/EvenSol/NeqSim-Colab/blob/master/notebooks/examples_of_NeqSim_in_Colab.ipynb#scrollTo=9VqtmS_MpS6M)
* [Getting started as a NeqSim developer](https://github.com/equinor/neqsim/wiki/Getting-started-as-a-NeqSim-developer)

## NeqSim discussion
Questions related to use and development are asked on the [NeqSim github discussions](https://github.com/equinor/neqsim/discussions) page.

## Examples
#### Java:
* [Thermodynamic calculations](https://github.com/equinor/neqsim/tree/master/src/main/java/neqsim/thermo/util/example)
* [Calculation of physical properties](https://github.com/equinor/neqsim/tree/master/src/main/java/neqsim/physicalProperties/util/examples)
* [Process simulation](https://github.com/equinor/neqsim/tree/master/src/main/java/neqsim/processSimulation/util/example)

#### Matlab:
* [Thermodynamic and process calculations](https://github.com/equinor/neqsimmatlab/tree/master/example)

#### Python
* [Python examples](https://github.com/equinor/neqsimpython/tree/master/examples) 
* [Notebook examples (Jupyter/Google Colab)](https://github.com/EvenSol/NeqSim-Colab)
* [NeqSim process project](https://github.com/equinor/neqsimprocess) A project to build up a library of prebuilt process models

#### NeqSim.NET
* [NeqSim .NET](https://github.com/equinor/neqsimNET/tree/master/examples)

#### Excel/Cape Open (restricted access)
* NeqSim Excel user interface
* Cape-Open plugin to process simulators

## NeqSim API
The NeqSim API project uses NeqSim as basis for developing an API based on containers, making fluid properties and process calculations available via a client-server connection. The NeqSim API is based on the [Quarkus](https://quarkus.io/) framework (a cloud native container first framework).
* NeqSim API
* Examples of how to use the NeqSim API

## NeqSim web application
A  web application has been developed to run calculation using neqsim via a web interface. Calculations such as TPflash, dew points, phase envelopes and hydrate equilibrium calculations can be run in the web application. An alternative web application is via Google Colab (Python).
* [NeqSim Web on Github](https://github.com/equinor/neqsimweb)
* [NeqSim Web application](http://129.241.62.72:8080/NeqSimServer3/faces/Login.jsp) hosted at NTNU
* [NeqSim Colab](https://github.com/EvenSol/NeqSim-Colab)

## Benchmark
A benchmark of computational speed of the frameworks is published in the [benchmark page](/benchmark.html)
