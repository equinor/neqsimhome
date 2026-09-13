"""Integrate conceptual artwork while preserving numerical figure references."""
from book_runtime import BOOK
import json
import re

DESCRIPTIONS = {
    "engineering_loop": ("From a defined question through workspace preparation and calculation to reviewed evidence", "The return arrow connects review to a revised question. Keep the input basis, selected tools, executed calculation and review record together so an unexpected result can be investigated."),
    "evidence_ladder": ("Different checks connect execution, verification, physical reasoning, independent validation and an engineering decision", "Each area answers a different question. A completed computation does not establish agreement with independent data, and a reference comparison does not by itself establish that the result answers the intended engineering question."),
    "physics_stack": ("Fluid data and thermodynamic models feed flash calculations, properties and process equipment", "The connected areas share a model basis. Incorrect composition or an unsuitable thermodynamic model can affect every downstream equipment result. The molecular and equipment forms are symbolic, not chemical structures or a process design."),
    "tool_use_cycle": ("An agent workflow connects scope, reading, action, observation, evaluation and recording", "The return path makes investigation explicit. A result is inspected before another action is selected; the evidence folder preserves the context needed when a different agent or a later session resumes the work."),
    "repository_map": ("Core, community and enterprise sources retain separate ownership while packages are installed and discovered by an agent host", "Public reusable methods and private organisational content have different owners. The picture is an ownership and discovery overview; the paths and commands in the text define the actual installation and export mechanisms."),
    "skill_lifecycle": ("A reusable skill develops through method description, implementation, testing, review and maintenance", "The return path represents maintenance after evidence reveals a gap. Preserve the failing example, update the method and its tests, and review the effect on dependent agents before treating the revised package as accepted practice."),
    "study_workflow": ("A study carries source evidence from scope and research through modelling to report and review", "Input documents feed a scoped model, while the study folder retains calculations, checks and the report. Changes to the basis should be recorded and propagated through that chain rather than edited only in the final document."),
    "mcp_layers": ("An agent host exchanges requests and results with a service and the NeqSim engine, with evidence retained for review", "The service boundary and numerical engine have different responsibilities. Transport, schemas and access controls need their own checks; numerical outputs still require physical interpretation and application-specific evidence."),
    "property_workbench": ("A property study specifies the state, selects a model, calculates properties and compares an independent reference", "The reference comparison must use the same composition, temperature, pressure, phase meaning and property units as the model. The small decorative curves have no numerical meaning; the specified-state labels and calculated values appear in the actual comparison below."),
    "process_workspace": ("A conceptual feed, separator, compressor and aftercooler arrangement connects material streams with work and heat", "The bottom separator outlet and the energy arrows draw attention to the control-volume boundary. The depicted liquid is illustrative and does not predict a liquid inventory for the dry-gas case. The exact model schematic and balance table below define the calculation."),
    "pipeline_workspace": ("A pipeline study combines route geometry, fluid and flow data, thermal conditions and an operating envelope", "These input groups determine which questions a model can answer. The illustrated coastal route, insulation and envelope are conceptual. The numerical example below is deliberately horizontal and isothermal, so its pressure results do not predict cooldown or arrival temperature."),
    "digital_twin_loop": ("Operating evidence supports model comparison, a proposed update and engineering review", "A discrepancy is investigated before a model revision is accepted. Check sensor quality, operating regime and competing physical causes; a smaller residual alone can conceal a wrong explanation. The return path represents controlled learning, not automatic actuation of a plant."),
    "autonomy_progression": ("Five cooperating capabilities surround human review: calculations, repeatable studies, monitoring, bounded actions and accountability", "The connected areas are a proposed way to organise capabilities, not a maturity scale or a promise of autonomous operation. Evidence, authority and controls must be appropriate to each action and its consequences."),
}


def main():
    manifest = json.loads((BOOK / "illustrations/imagegen_manifest_2026-09-13.json").read_text(encoding="utf-8"))
    for item in manifest["assets"]:
        chapter, name = item["chapter"], item["name"]
        if chapter == "cover":
            continue
        path = BOOK / "chapters" / chapter / "chapter.md"
        text = path.read_text(encoding="utf-8")
        num = int(chapter[2:4])
        target = "figures/" + name + ".png"
        if item["mode"] == "addition" and target not in text:
            text = re.sub(r"\bFigure " + str(num) + r"\.(\d+)", lambda m: f"Figure {num}.{int(m.group(1))+1}", text)
            at = re.search(r"^## " + str(num) + r"\.1\b", text, re.M).start()
            text = text[:at] + f"![Figure {num}.1: Conceptual illustration.]({target})\n\n*Observation.* Figure {num}.1 introduces the chapter.\n\n" + text[at:]
        pattern = re.compile(r"!\[[^\]]*\]\(" + re.escape(target) + r"\)")
        match = pattern.search(text)
        assert match, (chapter, name)
        ordinal = len(re.findall(r"!\[[^\]]*\]\(figures/[^)]+\)", text[:match.start()])) + 1
        number = f"{num}.{ordinal}"
        caption, observation = DESCRIPTIONS[name]
        replacement = f"![Figure {number}: {caption}. AI-generated conceptual illustration.]({target})"
        rest = text[match.end():]
        rest = re.sub(r"^\s*<!-- @neqsim:figure.*?-->\s*", "\n\n", rest, count=1, flags=re.S)
        rest = re.sub(r"^\s*<!-- @imagegen:.*?-->\s*", "\n\n", rest, count=1, flags=re.S)
        rest = re.sub(r"^\s*\*Observation\.\*.*?(?=\n\s*\n|\Z)", f"\n\n*Observation.* Figure {number} connects the chapter's main ideas. {observation}", rest, count=1, flags=re.S)
        text = text[:match.start()] + replacement + f"\n<!-- @imagegen: manifest=../../illustrations/imagegen_manifest_2026-09-13.json asset={name} -->" + rest
        path.write_text(text, encoding="utf-8")
    print("Integrated one image-generator illustration in each of 13 chapters; preserved scientific charts and exact schematic.")


if __name__ == "__main__":
    main()
