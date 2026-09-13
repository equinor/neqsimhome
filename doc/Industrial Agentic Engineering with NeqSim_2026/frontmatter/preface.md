# Preface

Engineering calculations become useful when someone can explain their assumptions, reproduce their results, and judge whether they answer the right question. This book shows how to build that chain with NeqSim and AI agents.

For the next step into industrial practice, the follow-up book *Agentic
Engineering for Oil and Gas Facility Operations: Connecting Data, Tools and
NeqSim in Engineering Workflows* explains how to work with multiple specialist
agents and tools across an oil and gas company \cite{AgenticFacilityOperations2026}.
It connects document systems, historians, laboratory and production databases,
maintenance records, process simulation and engineering review. Read this book
for the foundations and reproducible calculations, then use the follow-up for
industrial data handoffs, coordinated multi-agent studies and practical playbooks.

NeqSim supplies thermodynamic models and process equipment calculations. An agent can help define the work, find relevant knowledge, prepare code, run tools, investigate failures, and assemble the evidence. Skills preserve reusable methods and practical lessons. The engineer supplies the operating context, chooses acceptable assumptions, and takes responsibility for the decision.

The combination is useful because engineering work extends well beyond solving equations. A calculation may require a fluid analysis from one document, equipment information from another, a model with explicit units, and an independent check before its result can be used. Agents can assist with those connections. Their fluency does not establish physical accuracy, and a successful simulation does not establish design approval. Learning to distinguish these claims is a central purpose of the book.

## Who should read this book

Process, petroleum, and energy engineers can use the book to understand the software and build reproducible calculations. Software developers can learn how to connect language models to an engineering engine without hiding assumptions inside prompts. Technical leaders can use the later chapters to assess evidence, deployment boundaries, and the practical work needed to introduce agents into an organisation.

The technical chapters assume basic thermodynamics and some familiarity with Python. You do not need to be a Java developer to follow the main examples. The opening chapters explain the vocabulary before introducing repository layouts, tool contracts, and workflow orchestration.

## Reading paths

| Your immediate goal | Suggested path |
|---|---|
| Understand the idea | Chapters 1, 2, 4, then 12 and 13 |
| Run and inspect calculations | Chapters 1, 3, 9, 10 and 11 |
| Organise agents and skills | Chapters 4, 5, 6 and 7 |
| See how a task is solved and its answer checked | Section 1.10, Chapter 7, then the worked examples in Chapters 9–11 |
| Deploy a governed service | Chapters 7, 8, 12 and 13 |

A synthetic gas-processing example connects the worked chapters. Its inputs are teaching assumptions, not measurements from an operating asset. Other industrial examples explain the evidence and model structure a study requires; they do not claim confidential field validation.

## About this revision

This edition was revised on 13 September 2026. The public release baseline is NeqSim 3.20.0. Source-level discussion also uses commit `9a95440e194a6fdc2890e4efafff647711beedce`, which is newer than the release tag. A class present in that checkout should not automatically be assumed to exist in every packaged distribution bearing the same project version.

The opening chapter restores a command-by-command start, from the selected Python and source build to a first agent request and an inspectable methane calculation. The task root, recursive source-document library and Word template are configured separately. The workflow chapters cover document intake, current report naming and the portable work record. A matching set of AI-generated conceptual illustrations accompanies the chapters; these images explain ideas and are not scientific measurements or as-built drawings.

The revision expands the explanation of core, community, enterprise, and personal skills; distinguishes canonical packages from editor exports; and introduces current automation, lifecycle, engineering information exchange, and PVT workflows. It replaces speculative performance percentages with questions that can be tested. The final chapter presents possible future developments as proposals, with the evidence required to make them useful.

Code and numerical illustrations have a separate execution record in the book project. The reproducibility appendix explains the runtime, source revision, scripts, and checks. It distinguishes source inspection, numerical sanity checks, regression checks, and independent validation. Readers should retain those distinctions when adapting an example.

The book is designed to remain useful as individual language models change. Learn the division of responsibilities, the input and output contracts, and the evidence required for a decision. Then consult the current repositories for the available tools and their exact interfaces.

*Even Solbraa — Trondheim, September 2026*
