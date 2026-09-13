"""Reproducible conceptual diagrams and plots from verified numerical results."""
from book_runtime import BOOK
import json
import math
import re
import shutil
import textwrap
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Polygon, Rectangle
import numpy as np

NAVY = "#17324d"
TEAL = "#087f8c"
GOLD = "#b7791f"
INK = "#233746"
PALE = "#eef4f5"
GRAY = "#61717e"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.labelcolor": INK, "text.color": INK,
                     "axes.edgecolor": "#b4c1c9", "grid.color": "#dce4e8",
                     "axes.titlesize": 15, "axes.labelsize": 12,
                     "legend.fontsize": 10.5, "savefig.facecolor": "white"})


def archive_legacy_assets():
    """Move the original active assets into the book's verified archive boundary."""
    root = BOOK.resolve()
    for chapter in (BOOK / "chapters").iterdir():
        if not chapter.is_dir():
            continue
        for name in ("figures", "notebooks"):
            source = (chapter / name).resolve()
            destination = (BOOK / "revision_history" / "legacy_assets" / chapter.name / name).resolve()
            if not source.is_relative_to(root) or not destination.is_relative_to(root):
                raise RuntimeError("Archive paths must stay inside the selected book")
            if source.exists() and not destination.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(destination))


def canvas(title, subtitle, height=4.6):
    fig, ax = plt.subplots(figsize=(8.6, height))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    fig.text(0.07, 0.94, title, ha="left", va="top", fontsize=18, weight="bold", color=NAVY)
    fig.text(0.07, 0.875, subtitle, ha="left", va="top", fontsize=10.5, color=GRAY)
    fig.subplots_adjust(left=0.05, right=0.97, top=0.80, bottom=0.07)
    return fig, ax


def box(ax, x, y, w, h, title, body="", color=TEAL, fill=PALE):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.11",
                              linewidth=1.2, edgecolor=color, facecolor=fill))
    ax.text(x+w/2, y+h-0.32, title, ha="center", va="top", fontsize=12.5, weight="bold", color=color)
    if body:
        ax.text(x+w/2, y+h/2-0.18, body, ha="center", va="center", fontsize=11.5, linespacing=1.4)


def arrow(ax, start, end, color=GRAY, label=None, rad=0):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=13,
                               color=color, linewidth=1.5, connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((start[0]+end[0])/2, (start[1]+end[1])/2+0.16, label,
                ha="center", fontsize=10, color=color)


def save(fig, chapter, name):
    folder = BOOK / "chapters" / chapter / "figures"
    folder.mkdir(parents=True, exist_ok=True)
    fig.savefig(folder / (name+".png"), dpi=240, bbox_inches="tight")
    fig.savefig(folder / (name+".svg"), bbox_inches="tight")
    plt.close(fig)


def flow_diagram(chapter, name, title, subtitle, items, footer):
    fig, ax = canvas(title, subtitle)
    n = len(items)
    if n <= 3:
        w, gap = 2.7, 0.65
        x0 = (10 - n*w - (n-1)*gap)/2
        for i, (head, body) in enumerate(items):
            x=x0+i*(w+gap)
            box(ax, x, 2.1, w, 2.2, head, body, NAVY if i==0 else TEAL)
            if i<n-1: arrow(ax,(x+w+0.06,3.2),(x+w+gap-0.08,3.2))
        ax.plot([8.2,8.2,1.7],[2.02,1.25,1.25],color=GRAY,lw=1.2)
        arrow(ax,(1.7,1.25),(1.7,2.02))
        ax.text(5,0.83,"Review evidence and revise the basis when needed",ha="center",fontsize=10.5,color=GRAY)
    else:
        for i,(head,body) in enumerate(items):
            col=i%3; row=i//3
            x=0.25+col*3.3; y=3.35-row*2.9
            box(ax,x,y,2.85,2.15,head,body,NAVY if i==0 else TEAL)
            if col<2 and i<n-1: arrow(ax,(x+2.93,y+1.05),(x+3.22,y+1.05))
        if n>3:
            ax.plot([9.48,9.48,1.63],[3.30,2.96,2.96],color=GRAY,lw=1.2)
            arrow(ax,(1.63,2.96),(1.63,2.62))
    ax.text(5,-0.25,footer,ha="center",va="top",fontsize=10.5,color=GRAY)
    save(fig,chapter,name)


def repository_map():
    fig,ax=canvas("One ecosystem, several owners", "Canonical sources remain separate from installed and exported copies",5.5)
    items=[(0.2,3.55,"NeqSim core","Java models and tests\nWorkspace agents / skills",NAVY),
           (3.55,3.55,"Community","Public agents + skills\nVersioned catalogs",TEAL),
           (6.9,3.55,"Enterprise","Private policy + data access\nInternal catalogs",GOLD)]
    for x,y,h,b,c in items: box(ax,x,y,2.85,1.9,h,b,c)
    box(ax,1.1,0.95,3.35,1.7,"Canonical installation","~/.neqsim/agents\n~/.neqsim/skills",NAVY)
    box(ax,5.55,0.95,3.35,1.7,"Host discovery","VS Code personal export\nGeneric export + host setup",TEAL)
    for x in (1.62,4.97,8.32): arrow(ax,(x,3.45),(2.75,2.74),color=GRAY)
    arrow(ax,(4.57,1.8),(5.43,1.8),label="export")
    ax.text(5,0.1,"PaperLab keeps its publishing library in its own agents/ and skills/ folders.",ha="center",fontsize=10.5,color=GRAY)
    save(fig,"ch05","repository_map")


def process_diagram():
    fig,ax=canvas("A small process with explicit boundaries", "Synthetic gas  |  10,000 kg/h  |  60 bara  |  30 °C",4.8)
    ax.plot([0.3,2.4],[3.0,3.0],color=TEAL,lw=2)
    ax.text(0.35,3.4,"Feed",fontsize=13,weight="bold")
    vessel=FancyBboxPatch((2.4,1.65),1.35,2.7,boxstyle="round,pad=0,rounding_size=0.6",ec=NAVY,fc=PALE,lw=2)
    ax.add_patch(vessel)
    ax.plot([2.45,3.7],[2.4,2.4],color=TEAL,lw=1.4)
    ax.text(3.08,4.75,"Inlet separator",ha="center",fontsize=12,weight="bold")
    arrow(ax,(3.78,3.55),(5.05,3.55),color=TEAL)
    ax.text(4.4,3.88,"Gas",ha="center",fontsize=11)
    ax.add_patch(Polygon([[5.1,2.85],[5.1,4.25],[6.3,3.95],[6.3,3.15]],closed=True,fc=PALE,ec=NAVY,lw=2))
    ax.text(5.7,4.75,"Compressor",ha="center",fontsize=12,weight="bold")
    arrow(ax,(5.65,1.7),(5.65,2.8),color=GOLD)
    ax.text(5.65,1.3,"Shaft power in",ha="center",fontsize=11,color=GOLD)
    arrow(ax,(6.4,3.55),(7.45,3.55),color=TEAL)
    ax.add_patch(Circle((8.05,3.55),0.57,ec=NAVY,fc=PALE,lw=2))
    ax.plot([7.7,7.88,8.08,8.26,8.4],[3.25,3.83,3.26,3.83,3.3],color=TEAL,lw=1.5)
    ax.text(8.05,4.75,"Aftercooler",ha="center",fontsize=12,weight="bold")
    arrow(ax,(8.68,3.55),(9.8,3.55),color=TEAL)
    ax.text(9.45,2.8,"120 bara\n35 °C",ha="center",fontsize=11)
    arrow(ax,(8.05,2.91),(8.05,1.7),color=GOLD)
    ax.text(8.05,1.3,"Heat removed",ha="center",fontsize=11,color=GOLD)
    arrow(ax,(3.08,1.57),(3.08,0.6),color=TEAL)
    ax.text(3.08,0.15,"Any inlet liquid",ha="center",fontsize=11)
    save(fig,"ch10","gas_process")


def plots(chapter):
    r=json.loads((BOOK/"results.json").read_text())
    if chapter=="ch09":
        rows=r["methane_properties"]; p=[x["pressure_bara"] for x in rows]
        fig,ax=plt.subplots(figsize=(8,4.8),layout="constrained")
        for model,c,marker in [("SRK",TEAL,"o"),("PR",GOLD,"s")]:
            ax.plot(p,[x[model+"_density_kg_m3"] for x in rows],label=model,color=c,marker=marker,lw=2)
        ax.scatter(p,[x["NIST_density_kg_m3"] for x in rows],label="NIST reference",color=NAVY,marker="x",s=65,zorder=4)
        ax.set(xlabel="Pressure (bara)",ylabel="Density (kg/m³)",title="Methane at 298.15 K")
        ax.grid(alpha=.7); ax.legend(); save(fig,chapter,"methane_density")
        fig,ax=plt.subplots(figsize=(8,4.4),layout="constrained")
        for model,c,marker in [("SRK",TEAL,"o"),("PR",GOLD,"s")]:
            ax.plot(p,[x[model+"_deviation_pct"] for x in rows],label=model,color=c,marker=marker,lw=2)
        ax.axhline(0,color=GRAY,lw=1)
        ax.set(xlabel="Pressure (bara)",ylabel="Density deviation from NIST (%)",title="Agreement changes with pressure")
        ax.grid(alpha=.7); ax.legend(); save(fig,chapter,"methane_deviation")
    if chapter=="ch10":
        rows=r["compression_sensitivity"]; p=[x["outlet_pressure_bara"] for x in rows]
        fig,axes=plt.subplots(1,2,figsize=(9.0,4.2),layout="constrained")
        for ax,key,c,label in [(axes[0],"power_kW",TEAL,"Compressor power (kW)"),(axes[1],"discharge_temperature_C",GOLD,"Discharge temperature (°C)")]:
            ax.plot(p,[x[key] for x in rows],"o-",color=c,lw=2)
            ax.set(xlabel="Discharge pressure (bara)",ylabel=label)
            ax.grid(alpha=.7)
        fig.suptitle("One changed specification, two consequences",fontsize=15)
        save(fig,chapter,"compressor_sensitivity")
        fig,ax=plt.subplots(figsize=(8,4.6),layout="constrained")
        values=[x["power_kW"] for x in r["uncertainty"]["cases"]]
        ax.hist(values,bins=17,color=TEAL,edgecolor="white",alpha=.85)
        for key,c in [("q10",NAVY),("q50",GOLD),("q90",NAVY)]:
            q=r["uncertainty"]["power_kW_quantiles"][key]
            ax.axvline(q,color=c,lw=1.6,ls="--",label=f"{key[1:]}th percentile: {q:.1f} kW")
        ax.set(xlabel="Compressor power (kW)",ylabel="Number of realisations",title="200 full NeqSim process runs")
        ax.grid(axis="y",alpha=.5); ax.legend(loc="upper right",fontsize=9.5)
        save(fig,chapter,"compressor_uncertainty")
    if chapter=="ch11":
        fig,ax=plt.subplots(figsize=(8,4.6),layout="constrained")
        for row,c in zip(r["pipeline_sensitivity"],[NAVY,TEAL,GOLD,"#926b99"]):
            vals=row["pressure_profile_bara"]
            ax.plot(np.linspace(0,5,len(vals)),vals,color=c,lw=2,label=f"D = {row['diameter_m']:.2f} m")
        ax.set(xlabel="Distance (km)",ylabel="Pressure (bara)",title="Horizontal, isothermal pipe at 30 °C")
        ax.grid(alpha=.6);ax.legend();save(fig,chapter,"pipeline_profiles")
        rows=r["hydrate_screening"]
        assert len(rows)==4, "Do not draw a completed curve from failed hydrate cases"
        fig,ax=plt.subplots(figsize=(8,4.4),layout="constrained")
        ax.plot([x["pressure_bara"] for x in rows],[x["hydrate_temperature_C"] for x in rows],"o-",color=TEAL,lw=2)
        ax.set(xlabel="Pressure (bara)",ylabel="Equilibrium temperature (°C)",title="Wet-gas model demonstration")
        ax.grid(alpha=.6)
        save(fig,chapter,"hydrate_boundary")


def generate_chapter(chapter):
    from install_generated_illustrations import chapter_art
    generated_art = chapter_art(chapter)
    replaced = {item["name"] for item in generated_art if item.get("mode") == "replace"}
    specs={
      "ch01_getting_started":("engineering_loop","From question to reviewed result","Roles are connected by explicit inputs and evidence",[("Engineer","Question, basis\nand acceptance"),("Agent + skills","Method, tools\nand investigation"),("NeqSim","Numerical model\nand observations")],"Return results, checks and limitations to the engineer."),
      "ch02":("evidence_ladder","What does the evidence establish?","A completed run is the beginning of the review",[("1  Execution","The operation\ncompleted"),("2  Verification","The implementation\npassed its checks"),("3  Physics","Balances and trends\nare plausible"),("4  Validation","Independent data\nmatch the application"),("5  Decision","The accepted basis\nsupports the conclusion")],"Each level answers a different question; none replaces the next."),
      "ch03":("physics_stack","The numerical foundation","Data and model choices propagate into every process result",[("Component data","Identities, properties\nand interactions"),("Thermodynamics","EOS, mixing rules\nand phase stability"),("Flash + properties","Equilibrium state\nand transport data"),("Equipment","Material and energy\nrelationships"),("Automation","Variables, units\nand model revisions"),("Deliverables","Cases, exchanges\nand evidence")],"Source presence, regression evidence and physical validation are distinct."),
      "ch04":("tool_use_cycle","An observable agent workflow","Retain the actions and observations needed for review",[("Scope","Accepted basis\nand constraints"),("Load","Relevant skills\nand tool contracts"),("Act","Run a bounded\noperation"),("Observe","Result, diagnostics\nand failed cases"),("Evaluate","Continue, investigate\nor revise explicitly"),("Record","Artifacts, decisions\nand open issues")],"Persistent artifacts carry the study across interruptions and handoffs."),
      "ch06":("skill_lifecycle","Maintain a method, not just a prompt","A reusable improvement starts with an observed need",[("Observe","Preserve the case\nand failure"),("Specify","Scope, inputs\nand applicability"),("Implement","Focused instructions\nand executable example"),("Verify","Nominal, boundary\nand invalid cases"),("Review","Owner, version\nand compatibility"),("Refresh","Update dependants\nand repeat checks")],"Public methods, company policy and confidential study data have separate owners."),
      "ch07":("study_workflow","The study and its evidence","Resolve one task folder and preserve the accepted basis",[("Scope + research","Specification, sources\nand capability plan"),("Analysis + checks","Models, benchmarks\nand uncertainty"),("Report + review","Supported conclusions\nand open issues")],"Revisit the basis when evidence requires a change; retain its revision history."),
      "ch08":("mcp_layers","MCP connects a host to calculations","Protocol correctness and engineering validity need separate checks",[("Host + client","User intent, permissions\nand tool discovery"),("Server wrapper","Transport, schemas\nand deployment profile"),("Core runners","Typed requests\nand diagnostics"),("NeqSim engine","Fluid and process\ncalculations"),("Evidence store","Exact inputs, outputs\nand revisions"),("Reviewer","Applicability\nand decision")],"Runtime controls surround execution; tool annotations alone do not enforce policy."),
      "ch12":("digital_twin_loop","A model connected to operating evidence","Begin with read-only comparison and controlled updates",[("Measurements","Timestamps, tags\nand uncertainty"),("Data quality","Units, regime\nand missing values"),("Model comparison","Predictions, residuals\nand competing causes"),("Proposed update","Parameters, bounds\nand fit changes"),("Review","Check identification\nand operating context"),("Accepted revision","Preserve before/after\nevidence and status")],"A smaller residual can hide a sensor error; preserve the pre-update discrepancy."),
      "ch13":("autonomy_progression","Autonomy is specific to the action","Proposed evaluation stages, not a product maturity score",[("Assisted calculation","Explicit basis\nand checked output"),("Repeatable study","Durable execution\nand regression cases"),("Advisory monitoring","Validated comparisons\nand supervised updates"),("Bounded action","Qualified limits\nand enforceable controls"),("Accountable review","Authority follows\nconsequence")],"Advance only when the evidence supports the intended operation."),
    }
    if chapter in specs and specs[chapter][0] not in replaced:
        flow_diagram(chapter,*specs[chapter])
    if chapter=="ch05" and "repository_map" not in replaced: repository_map()
    if chapter=="ch10": process_diagram()
    if chapter in ("ch09","ch10","ch11"): plots(chapter)
    if chapter=="ch12":
        flow_diagram(chapter,"engineering_handover","An exchange file is one stage of handover","Select the information model and recipient before exporting",[("Reviewed model","Identity, topology\nand case basis"),("Exchange package","Graph, XML\nand evidence"),("Internal checks","Schema and supported\nsemantics"),("Recipient test","Named product\nand version"),("Acceptance","Review differences\nand intended use")],"Internal conformance is not recipient-tool qualification or construction release.")


def cover():
    from install_generated_illustrations import chapter_art
    if chapter_art("cover"):
        return
    fig=plt.figure(figsize=(7.04,10),facecolor=NAVY)
    ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,1),ylim=(0,1));ax.axis("off")
    ax.add_patch(Rectangle((0,.0),1,.04,color=TEAL))
    ax.text(.085,.915,"INDUSTRIAL",fontsize=26,color="white",weight="bold")
    ax.text(.085,.850,"AGENTIC",fontsize=39,color="white",weight="bold")
    ax.text(.085,.785,"ENGINEERING",fontsize=29,color="white",weight="bold")
    ax.text(.085,.723,"with NeqSim",fontsize=26,color="#68d2d5")
    ax.plot([.085,.88],[.67,.67],color="#66b9c5",lw=1)
    ax.text(.085,.628,"Physics, Agents, Skills and\nReproducible Engineering Workflows",fontsize=16,color="white",va="top",linespacing=1.5)
    nodes=[(.14,.29),(.30,.42),(.43,.28),(.60,.44),(.77,.31),(.88,.46)]
    for i in range(len(nodes)-1):
        x,y=nodes[i];xx,yy=nodes[i+1]
        ax.plot([x,xx],[y,yy],color="#69bdc7",lw=2,alpha=.9)
    for i,(x,y) in enumerate(nodes):
        ax.add_patch(Circle((x,y),.022 if i not in (1,3) else .032,facecolor=TEAL if i%2 else "#d8ad60",edgecolor="#ffffff",lw=.7))
    ax.text(.085,.145,"EVEN SOLBRAA",fontsize=17,color="white",weight="bold")
    ax.text(.085,.094,"REVISED SEPTEMBER 2026",fontsize=11,color="#9ad9df")
    fig.savefig(BOOK/"cover_front.png",dpi=240,facecolor=NAVY)
    fig.savefig(BOOK/"cover_front.svg",facecolor=NAVY)
    plt.close(fig)


def replace_block(chapter,label,content):
    path=BOOK/"chapters"/chapter/"chapter.md"
    text=path.read_text(encoding="utf-8-sig")
    pattern=rf"<!-- BEGIN GENERATED {label} -->.*?<!-- END GENERATED {label} -->"
    value=f"<!-- BEGIN GENERATED {label} -->\n\n{content}\n\n<!-- END GENERATED {label} -->"
    text,count=re.subn(pattern,lambda _:value,text,flags=re.S)
    assert count==1,(chapter,label,count)
    path.write_text(text,encoding="utf-8")


def inject_results():
    r=json.loads((BOOK/"results.json").read_text())
    assert not r["failures"],r["failures"]
    rows=r["methane_properties"]
    table="| Pressure (bara) | NIST (kg/m3) | SRK (kg/m3) | PR (kg/m3) |\n|---|---|---|---|\n"
    table+="\n".join(f"| {x['pressure_bara']:.0f} | {x['NIST_density_kg_m3']:.4f} | {x['SRK_density_kg_m3']:.4f} | {x['PR_density_kg_m3']:.4f} |" for x in rows)
    replace_block("ch09","METHANE TABLE",table)
    x=rows[-1]
    replace_block("ch09","METHANE DISCUSSION",f"At 201 bara, NIST gives {x['NIST_density_kg_m3']:.2f} kg/m3; SRK gives {x['SRK_density_kg_m3']:.2f} kg/m3 and PR gives {x['PR_density_kg_m3']:.2f} kg/m3. Their deviations are {x['SRK_deviation_pct']:.2f}% and {x['PR_deviation_pct']:.2f}%, respectively. The near-ideal low-pressure agreement therefore does not persist unchanged as density rises. For an application requiring tighter density accuracy, extend the validation over its operating envelope and consider a more suitable model or justified calibration.")
    base=r["compression_base"]
    fields=[("Compressor power","power_kW","kW"),("Discharge temperature","discharge_temperature_C","degrees C"),("Aftercooler temperature","cooled_temperature_C","degrees C"),("Aftercooler duty","cooler_duty_kW","kW"),("Separator gas flow","gas_mass_flow_kg_h","kg/h"),("Separator liquid flow","liquid_mass_flow_kg_h","kg/h")]
    table="| Output | Calculated value | Unit |\n|---|---|---|\n"+"\n".join(f"| {title} | {base[key]:.3f} | {unit} |" for title,key,unit in fields)
    table+=f"\n\nThe separator relative mass-balance residual is {base['mass_balance_relative_error']:.2e}. The numerical liquid outlet is negligible for this case. Values are model predictions for the declared synthetic basis."
    replace_block("ch10","PROCESS TABLE",table)
    energy = (f"The inlet enthalpy rate is {base['inlet_enthalpy_rate_kW']:.3f} kW; the cooled outlet carries "
              f"{base['cooled_outlet_enthalpy_rate_kW']:.3f} kW and the separate liquid outlet carries "
              f"{base['liquid_outlet_enthalpy_rate_kW']:.3f} kW on the same enthalpy reference. Thus the material-stream "
              f"enthalpy change is {base['enthalpy_change_kW']:.3f} kW. Work into the process is "
              f"+{base['power_kW']:.3f} kW and heat into it is {base['cooler_duty_kW']:.3f} kW. "
              f"The unrounded balance residual is {base['energy_balance_residual_kW']:.2e} kW.")
    replace_block("ch10", "ENERGY BALANCE", energy)
    low,high=r["compression_sensitivity"][0],r["compression_sensitivity"][-1]
    replace_block("ch10","PROCESS DISCUSSION",f"Increasing discharge pressure from 80 to 160 bara raises calculated duty from {low['power_kW']:.1f} to {high['power_kW']:.1f} kW and discharge temperature from {low['discharge_temperature_C']:.1f} to {high['discharge_temperature_C']:.1f} degrees C. The greater pressure ratio requires more work and raises the gas temperature. Check driver and temperature constraints before accepting a higher-pressure case; obtain vendor-map evidence before claiming an operating margin.")
    q=r["uncertainty"]["power_kW_quantiles"]
    replace_block("ch10","UNCERTAINTY DISCUSSION",f"All {r['uncertainty']['completed']} requested cases completed. The non-exceedance 10th, 50th and 90th percentiles are {q['q10']:.1f}, {q['q50']:.1f} and {q['q90']:.1f} kW. Higher flow and lower efficiency increase the required duty, broadening the distribution around the base result. Use this as a demonstration of uncertainty propagation, then replace the teaching ranges with justified application data and check statistical convergence.")
    table="| Internal diameter (m) | Outlet pressure (bara) | Pressure drop (bar) |\n|---|---|---|\n"+"\n".join(f"| {x['diameter_m']:.2f} | {x['outlet_pressure_bara']:.4f} | {x['pressure_drop_bar']:.4f} |" for x in r["pipeline_sensitivity"])
    replace_block("ch11","PIPE TABLE",table)
    replace_block("ch11","PIPE DISCUSSION","Increasing internal diameter from 0.15 to 0.30 m reduces the calculated pressure drop from 0.9705 to 0.0305 bar in this case. A larger flow area lowers velocity and frictional loss. The small losses also explain why the profiles are nearly linear. Use these results to understand hydraulic sensitivity, then introduce the actual route, thermal conditions and design constraints before selecting a diameter.")
    table="| Increments | Pressure drop (bar) | Outlet temperature (degrees C) |\n|---|---|---|\n"+"\n".join(f"| {x['increments']} | {x['pressure_drop_bar']:.7f} | {x['outlet_temperature_C']:.2f} |" for x in r["pipeline_refinement"])
    replace_block("ch11","REFINEMENT TABLE",table)
    rows=r["hydrate_screening"]
    table="| Pressure (bara) | Calculated equilibrium temperature (degrees C) |\n|---|---|\n"+"\n".join(f"| {x['pressure_bara']:.0f} | {x['hydrate_temperature_C']:.2f} |" for x in rows)
    replace_block("ch11","HYDRATE TABLE",table)
    replace_block("ch11","HYDRATE DISCUSSION",f"The calculated boundary rises from {rows[0]['hydrate_temperature_C']:.2f} degrees C at 40 bara to {rows[-1]['hydrate_temperature_C']:.2f} degrees C at 100 bara. This is consistent with pressure favouring hydrate stability over the selected range. The engineering implication is that a pressure change can alter the required thermal or inhibition strategy. Validate the selected wet-fluid model and establish water and inhibitor conditions before applying an operating-margin policy; this curve has not been independently validated.")


def integrate_figure_references():
    """Keep PaperLab evidence syntax and meaningful discussion through regeneration."""
    starts = {
        "engineering_loop": ("Read the loop", "Read the loop in Figure 1.1"),
        "evidence_ladder": ("The diagram", "Figure 2.1"),
        "physics_stack": ("The layers", "The layers in Figure 3.1"),
        "tool_use_cycle": ("In the gas case,", "Following the observation step in Figure 4.1,"),
        "repository_map": ("The diagram", "Figure 5.1"),
        "skill_lifecycle": ("The return arrow", "The return arrow in Figure 6.1"),
        "study_workflow": ("**Scope and research**", "In Figure 7.1, **scope and research**"),
        "mcp_layers": ("This separation", "The separation in Figure 8.1"),
        "methane_density": ("At 201 bara,", "At 201 bara in Figure 9.2,"),
        "methane_deviation": ("The deviation plot", "The deviation plot in Figure 9.3"),
        "gas_process": ("Follow both material outlets", "Follow both material outlets in Figure 10.2"),
        "compressor_sensitivity": ("Increasing discharge pressure", "In Figure 10.3, increasing discharge pressure"),
        "compressor_uncertainty": ("All ", "In the results plotted in Figure 10.4, all "),
        "pipeline_profiles": ("Increasing internal diameter", "In Figure 11.2, increasing internal diameter"),
        "hydrate_boundary": ("The calculated boundary", "The calculated boundary in Figure 11.3"),
        "digital_twin_loop": ("The first stage", "The first stage in Figure 12.1"),
        "engineering_handover": ("Internal checks", "The internal checks in Figure 12.2"),
        "autonomy_progression": ("The progression", "The progression in Figure 13.1"),
    }
    for path in sorted((BOOK / "chapters").glob("*/chapter.md")):
        chapter_number = int(re.match(r"ch(\d+)", path.parent.name).group(1))
        source = path.read_text(encoding="utf-8")
        matches = list(re.finditer(r"!\[(.*?)\]\((figures/[^)]+)\)", source))
        for index, match in reversed(list(enumerate(matches, 1))):
            number = f"{chapter_number}.{index}"
            alt = re.sub(r"^Figure \d+\.\d+:\s*", "", match.group(1))
            caption = f"![Figure {number}: {alt}]({match.group(2)})"
            rest = source[match.end():]
            prefix = re.match(r"\s*(?:<!--.*?-->\s*)*", rest, re.S).group(0)
            discussion = rest[len(prefix):]
            if not discussion.startswith("*Observation.*"):
                stem = Path(match.group(2)).stem
                if stem not in starts:
                    raise ValueError("Add a substantive observation for the new figure: " + stem)
                old, new = starts[stem]
                assert discussion.startswith(old), (path, number, discussion[:100])
                discussion = "*Observation.* " + new + discussion[len(old):]
            source = source[:match.start()] + caption + prefix + discussion
        path.write_text(source, encoding="utf-8")


def main():
    archive_legacy_assets()
    chapters=["ch01_getting_started"]+[f"ch{i:02d}" for i in range(2,14)]
    for chapter in chapters: generate_chapter(chapter)
    cover()
    inject_results()
    integrate_figure_references()
    print("Verified 14 retained AI assets, regenerated scientific charts and code-native diagrams, and refreshed result tables.")


if __name__=="__main__": main()
