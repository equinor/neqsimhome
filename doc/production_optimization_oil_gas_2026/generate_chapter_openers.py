#!/usr/bin/env python3
"""Generate decorative *topic* illustrations for each chapter opener.

Problem this solves
-------------------
The HTML/PDF renderers pick a chapter "hero" image by taking the first figure
(alphabetically) that matches a hint regex. Data plots such as
``fig01_density_vs_pressure.png`` win that contest because ``fig01_`` sorts
first and matches the ``01_`` hint — so a data plot ends up at the top of the
chapter instead of an illustration of the chapter's topic. The plot itself
still belongs in the body where its calculation is discussed.

This script generates a dedicated conceptual illustration (a radial concept
map of the chapter's topic) named ``00_<chNN>_opener.png`` (e.g.
``00_ch01_opener.png``). The ``00_`` prefix sorts before every ``fig*`` /
schematic file *and* the name matches the ``opener`` hero hint, so both
renderers select it as the chapter hero. The ``<chNN>`` segment keeps the
filename unique per chapter — essential because the HTML renderer flattens all
chapter figures into a single ``submission/figures/`` directory, where a shared
name would collide and leave every chapter showing the same image. The original
data plots remain in each chapter's ``## Figures`` section, untouched.

No API keys, GPU, or subscriptions — uses only Pillow via
``tools/chapter_illustrations.concept_diagram``.

Run from anywhere::

    python generate_chapter_openers.py
"""
import os
import re
import sys
from pathlib import Path

# Locate the paperlab root so we can import tools/chapter_illustrations.py
BOOK_DIR = Path(__file__).resolve().parent
PAPERLAB_ROOT = BOOK_DIR.parents[1]  # books/<book>/ -> paperlab root
sys.path.insert(0, str(PAPERLAB_ROOT))

from tools.chapter_illustrations import concept_diagram  # noqa: E402

# Legacy shared name (collides in the flat submission/figures dir). Removed
# before writing the new per-chapter unique openers.
LEGACY_OPENER_NAME = "00_chapter_opener.png"

# (chapter_dir, central topic, [branch subtopics])
CHAPTERS = [
    ("ch01_introduction", "Production\nOptimization",
     ["Reservoir & Wells", "Subsea Transport", "Topside Processing",
      "Compression & Power", "Export & Metering", "Optimization Workflow"]),
    ("ch02_thermodynamic_foundations", "Thermodynamic\nFoundations",
     ["Equations of State", "Phase Equilibrium", "Flash Calculations",
      "Fugacity & K-values", "Mixing Rules", "Property Models"]),
    ("ch03_fluid_characterization", "Fluid\nCharacterization",
     ["PVT Analysis", "TBP / Plus Fractions", "Component Lumping",
      "EOS Tuning", "Black-Oil vs Compositional", "Lab Data Matching"]),
    ("ch04_reservoir_engineering", "Reservoir &\nInflow",
     ["Inflow Performance", "Material Balance", "Drive Mechanisms",
      "Reservoir Pressure", "Voidage Replacement", "Decline Behaviour"]),
    ("ch05_well_performance", "Well\nPerformance",
     ["Tubing Performance", "Inflow (IPR)", "Nodal Analysis",
      "Operating Point", "Multiphase Flow", "Tubing Sizing"]),
    ("ch06_wells_artificial_lift", "Artificial\nLift",
     ["Gas Lift", "Electric Submersible Pumps", "Well Networks",
      "Lift-Gas Allocation", "Lift Optimization", "Well Routing"]),
    ("ch07_subsea_production_systems", "Subsea\nSystems",
     ["Subsea Trees", "Manifolds", "Boosting Pumps",
      "Umbilicals", "Tieback Design", "Subsea Control"]),
    ("ch08_flowlines_and_risers", "Flowlines\n& Risers",
     ["Pressure Drop", "Multiphase Hydraulics", "Liquid Holdup",
      "Riser Dynamics", "Thermal Profile", "Slug Flow"]),
    ("ch09_flow_assurance", "Flow\nAssurance",
     ["Hydrates", "Wax Deposition", "Asphaltenes",
      "Corrosion", "Inhibitor Injection", "Slug Management"]),
    ("ch10_separation_technology", "Separation\nTechnology",
     ["Gravity Separation", "HP / MP / LP Stages", "Demisters & Internals",
      "Retention Time", "Vessel Sizing", "Carry-Over Control"]),
    ("ch11_oil_processing", "Oil\nStabilization",
     ["Multi-Stage Flash", "RVP / TVP Control", "Stabilization Column",
      "Recycle Streams", "Export Spec", "Vapour Recovery"]),
    ("ch12_gas_processing", "Gas\nConditioning",
     ["Dehydration (TEG)", "Dew-Point Control", "Acid Gas Removal",
      "NGL Recovery", "Gas Compression", "Sales-Gas Spec"]),
    ("ch13_produced_water_treatment", "Produced Water\nTreatment",
     ["Oil-in-Water", "Hydrocyclones", "Flotation",
      "Degassing", "Discharge Limits", "Re-Injection"]),
    ("ch14_gas_compression", "Gas\nCompression",
     ["Compression Stages", "Intercooling", "Power Demand",
      "Anti-Surge Control", "Recompression", "Export Compression"]),
    ("ch15_compressor_characteristics", "Compressor\nCharacteristics",
     ["Head vs Flow", "Surge Line", "Stonewall Limit",
      "Speed Lines", "Efficiency Map", "Operating Point"]),
    ("ch16_heat_exchangers", "Heat\nTransfer",
     ["Duty & UA", "Shell-and-Tube", "Plate / Compact",
      "LMTD & Approach", "Coolers & Heaters", "Thermal Design"]),
    ("ch17_valves_and_flow_control", "Flow\nControl",
     ["Control Valves (Cv)", "Choke Modeling", "Pressure Letdown",
      "Relief & Blowdown", "Joule-Thomson", "Flow Splitting"]),
    ("ch18_power_production", "Power\nProduction",
     ["Gas Turbines", "Steam Turbines / HRSG", "Combined Cycle",
      "Fuel Gas Demand", "Heat Integration", "Emissions"]),
    ("ch19_export_and_metering", "Export &\nMetering",
     ["Sales-Gas Spec", "Fiscal Metering", "Wobbe / Heating Value",
      "Oil Export Spec", "Custody Transfer", "Pipeline Delivery"]),
    ("ch20_capacity_checks_and_utilization", "Capacity &\nUtilization",
     ["Capacity Constraints", "Utilization Snapshot", "Bottleneck ID",
      "Design vs Actual", "Hard Limits", "Operating Margins"]),
    ("ch21_debottlenecking", "Systematic\nDebottlenecking",
     ["Bottleneck Analysis", "Utilization Ranking", "Constraint Removal",
      "Throughput Gains", "Cost vs Benefit", "Iterative Study"]),
    ("ch22_production_optimization_theory", "Optimization\nTheory",
     ["Objective Function", "Constraints", "Decision Variables",
      "Gradient-Free Search", "Local vs Global", "Feasibility"]),
    ("ch23_neqsim_optimization_framework", "NeqSim\nFramework",
     ["ProcessAutomation", "evaluate() Loop", "Adjustable Parameters",
      "Feasibility Gating", "Trajectory Logging", "Agentic Optimizer"]),
    ("ch24_production_optimization", "Production\nOptimization",
     ["Rate Allocation", "Setpoint Tuning", "Constraint Handling",
      "Objective: Value", "Solver Loop", "Result Extraction"]),
    ("ch25_utilization_monitoring", "Utilization\nMonitoring",
     ["Real-Time Snapshot", "Constraint Tracking", "Bottleneck Alerts",
      "KPI Dashboards", "Plant Historian", "Trend Analysis"]),
    ("ch26_well_network_optimization", "Network\nOptimization",
     ["Well Allocation", "Shared Manifolds", "Back-Pressure Coupling",
      "Lift-Gas Split", "Routing Decisions", "System Optimum"]),
    ("ch27_multi_scenario_optimization", "Multi-Scenario\nOptimization",
     ["Uncertainty", "Monte Carlo", "Scenario Trees",
      "Stochastic Objective", "P10 / P50 / P90", "Robust Setpoints"]),
    ("ch28_field_development", "Field\nDevelopment",
     ["Concept Selection", "VFP Tables", "Production Forecast",
      "CAPEX / OPEX", "NPV & Economics", "Capacity Planning"]),
    ("ch29_dynamic_simulation_and_control", "Dynamic\n& Control",
     ["Transient Simulation", "PID Controllers", "Level & Pressure",
      "Startup / Shutdown", "Anti-Surge", "Loop Tuning"]),
    ("ch30_digital_twins_and_automation", "Digital Twins\n& Automation",
     ["Model Calibration", "Plant Data Bridge", "Automation API",
      "Continuous Tuning", "AI-Assisted Loops", "State Snapshots"]),
    ("ch31_solver_methods", "Numerical\nMethods",
     ["Recycle Convergence", "Flash Solvers", "Newton Methods",
      "Damping & Relaxation", "Tolerance Gating", "Robustness"]),
    ("ch32_advanced_topics", "Advanced\nMethods",
     ["Surrogate Models", "Bayesian Optimization", "Reinforcement Learning",
      "Gradient-Free Search", "Multi-Objective", "Hybrid Methods"]),
    ("ch33_onshore_processing_plants", "Onshore\nProcessing",
     ["Gas Plant Trains", "NGL Fractionation", "LNG Pre-Treatment",
      "Utilities", "Multi-Area Models", "Energy Integration"]),
    ("ch34_case_studies", "Integrated\nCase Studies",
     ["Full-Plant Models", "Reservoir-to-Market", "Optimization Studies",
      "Model Calibration", "Debottlenecking", "Lessons Learned"]),
    ("ch35_future_directions", "Future\nDirections",
     ["Autonomous Operations", "AI Agents", "Electrification",
      "Decarbonization", "Digital Integration", "Real-Time Optimization"]),
]


def main():
    chapters_root = BOOK_DIR / "chapters"
    generated = 0
    for ch_dir, center, branches in CHAPTERS:
        fig_dir = chapters_root / ch_dir / "figures"
        if not fig_dir.is_dir():
            print(f"  SKIP (no figures dir): {ch_dir}")
            continue
        # Remove the legacy shared-name opener so it cannot collide in the
        # flat submission/figures directory during rendering.
        legacy = fig_dir / LEGACY_OPENER_NAME
        if legacy.exists():
            legacy.unlink()
        # Unique per-chapter name: 00_<chNN>_opener.png (e.g. 00_ch01_opener.png)
        m = re.match(r"(ch\d+)", ch_dir)
        prefix = m.group(1) if m else ch_dir
        opener_name = f"00_{prefix}_opener.png"
        out = fig_dir / opener_name
        concept_diagram(
            center=center,
            branches=branches,
            output_path=str(out),
            width=1600,
            height=920,
        )
        print(f"  OK  {ch_dir}/figures/{opener_name}")
        generated += 1
    print(f"\nGenerated {generated} chapter-opener illustrations.")


if __name__ == "__main__":
    main()
