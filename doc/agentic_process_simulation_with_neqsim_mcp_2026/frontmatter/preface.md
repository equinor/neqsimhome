## Preface

This book is the industrial-workflow follow-up to *Industrial Agentic Engineering
with NeqSim* \cite{OnlineBook2026}. The first book introduces the physics engine,
agents, skills and reproducible calculations. This volume shows how to work with
multiple specialist agents and engineering tools in an industrial context:
connecting documents, historians, laboratory and production databases,
maintenance records and process models in one reviewable workflow. Readers
looking for that practical cooperation should begin with Chapters 1–3, then
follow the data handoffs and worked study in Chapters 4–10.

An engineering question at an oil and gas facility rarely belongs to one tool.
Explaining a compressor's rising power demand may require a historian interval,
a laboratory composition, an approved vendor curve, a maintenance record and
a thermodynamic model. Each provides a different part of the answer. This book
shows how an agent can coordinate those contributions into a study that an
engineer can inspect, challenge and reuse.

The central workflow is straightforward: define the decision, retrieve
evidence, reconcile its meaning, run the appropriate models, compare alternatives,
review the findings and retain the result. The chapters explain what moves
between those steps: records, units, timestamps, source revisions, model inputs,
diagnostics and unresolved questions. Tool cooperation is useful when those
handoffs remain visible.

### Industry scope

The examples span offshore and onshore production, gas processing, pipeline
systems and LNG interfaces. The same integration principles support other
process facilities. The book uses public commercial products and open standards
as examples of system categories; it does not describe an operator's internal
tools, databases or facilities. A document-management system, a historian,
a laboratory information system, an enterprise asset-management platform and
a production database each have a distinct role.

Naming a product does not mean a connector is installed, licensed or available
to NeqSim. Every deployment must establish its approved interface and verify the
data contract. NeqSim supplies physical calculations where its models apply.
Other tools supply data access, document interpretation, specialist calculations,
visualization, engineering review and the existing process for implementing an
approved action.

### How to read the book

Chapters 1–3 explain the workbench: the engineering question, MCP interfaces,
agents, skills and shared study context. Chapters 4–5 connect industrial records
to process and equipment models. Chapters 6–8 cover safety studies, operational
workflows and governance. Chapters 9–10 bring the tools together in a worked
study and reusable playbooks.

The two books can be read in sequence or used together: consult the first for
calculation and platform foundations, and this follow-up for industrial data,
multi-agent cooperation and tool handoffs.

### Calculations and illustrations

The worked scenarios are teaching cases with invented assets and inputs.
Numerical results described as calculated are linked to a retained verification
record that identifies the model and source revision. Other example numbers
remain explicitly hypothetical. Reproducing a software result is distinct from
validating a model against independent measurements, and neither establishes
plant-specific design acceptance.

The diagrams show conceptual tool handoffs. The industrial scene and cover are
AI-generated editorial illustrations. They represent no real facility, measured
performance or approved engineering drawing. Each diagram is followed by an
explanation of its engineering purpose.

### Prerequisites and acknowledgements

Readers should understand basic process engineering and operating data.
Configuration and code examples are explained in the context of the decision
they support. This edition was developed with NeqSim PaperLab's book-authoring,
case-continuity, traceability and typesetting workflows, with specialist review
and calculation checks.
