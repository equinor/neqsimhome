#!/usr/bin/env python3
"""Generate all figures for chapters 23-30 (17 figures)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from generate_figures_style import apply_style, savefig, C, PALETTE, add_watermark

apply_style()

# ═══════════════════════════════════════════════════════════════════
# Chapter 23: Case Studies (4 figures)
# ═══════════════════════════════════════════════════════════════════

def ch23_case1_platform_schematic():
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.set_xlim(0, 14); ax.set_ylim(0, 6); ax.axis("off")
    # Platform with 3-stage separation + compression
    units = [
        (0.5, 3, "Well\nFluids", C["ltgreen"]),
        (3.0, 3, "HP Sep\n(70 bara)", C["ltblue"]),
        (5.5, 3, "MP Sep\n(20 bara)", C["ltblue"]),
        (8.0, 3, "LP Sep\n(3 bara)", C["ltblue"]),
        (3.0, 5, "1st Stage\nComp", C["ltorange"]),
        (5.5, 5, "2nd Stage\nComp", C["ltorange"]),
        (8.0, 5, "Export\nComp", C["ltorange"]),
        (11, 5, "Gas\nExport", C["ltorange"]),
        (11, 3, "Oil\nExport", C["ltgreen"]),
    ]
    for x, y, label, color in units:
        ax.add_patch(FancyBboxPatch((x, y), 2.2, 1.2, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor=C["gray"]))
        ax.text(x+1.1, y+0.6, label, ha="center", va="center", fontsize=7, fontweight="bold")
    # Oil flow
    for i in range(3):
        ax.annotate("", xy=(units[i+1][0], 3.6), xytext=(units[i][0]+2.2, 3.6),
                    arrowprops=dict(arrowstyle="->", color=C["green"], lw=1.5))
    ax.annotate("", xy=(11, 3.6), xytext=(10.2, 3.6),
                arrowprops=dict(arrowstyle="->", color=C["green"], lw=1.5))
    # Gas flow
    for i in [1, 2, 3]:
        ax.annotate("", xy=(units[i][0]+1.1, 5), xytext=(units[i][0]+1.1, 4.2),
                    arrowprops=dict(arrowstyle="->", color=C["orange"], lw=1.2))
    for i in range(4, 7):
        ax.annotate("", xy=(units[i+1][0], 5.6), xytext=(units[i][0]+2.2, 5.6),
                    arrowprops=dict(arrowstyle="->", color=C["orange"], lw=1.5))
    ax.set_title("Case Study 1 — Offshore Platform Process Schematic", fontsize=10, fontweight="bold", pad=5)
    savefig("ch23_case_studies", "ch23_case1_platform_schematic.png", fig)


def ch23_case1_hp_optimization():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    P_hp = np.linspace(40, 100, 100)
    oil_rec = -0.003*(P_hp-65)**2 + 97
    comp_power = 8 + 0.05*P_hp + 0.001*(100-P_hp)**2
    revenue = oil_rec * 0.5  # simplified
    cost = comp_power * 0.1
    profit = revenue - cost
    ax.plot(P_hp, oil_rec, color=C["blue"], linewidth=2, label="Oil Recovery (%)")
    ax2 = ax.twinx()
    ax2.plot(P_hp, profit, color=C["green"], linewidth=2.5, linestyle="--", label="Net Revenue (arb.)")
    ax2.set_ylabel("Net Revenue", color=C["green"])
    ax.axvline(x=65, color=C["red"], linestyle=":", linewidth=1.5)
    ax.text(67, 92, "Optimal\nHP Pressure", fontsize=8, color=C["red"])
    ax.set_xlabel("HP Separator Pressure (bara)")
    ax.set_ylabel("Oil Recovery (%)", color=C["blue"])
    ax.set_title("Case Study 1 — HP Separator Optimization", fontweight="bold")
    lines1, l1 = ax.get_legend_handles_labels()
    lines2, l2 = ax2.get_legend_handles_labels()
    ax.legend(lines1+lines2, l1+l2, loc="lower left", fontsize=8)
    add_watermark(ax)
    savefig("ch23_case_studies", "ch23_case1_hp_optimization.png", fig)


def ch23_case2_water_cut_sensitivity():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    wc = np.linspace(0, 95, 100)  # water cut %
    oil_rate = 15000 * (1 - wc/100)
    sep_util = 40 + 0.6*wc
    pump_power = 2 + 0.08*wc
    ax.plot(wc, oil_rate/1000, color=C["blue"], linewidth=2.5, label="Oil Rate (kSm³/d)")
    ax2 = ax.twinx()
    ax2.plot(wc, sep_util, color=C["red"], linewidth=2, linestyle="--", label="Separator Util. (%)")
    ax2.axhline(y=90, color=C["orange"], linestyle=":", alpha=0.5)
    ax2.set_ylabel("Separator Utilization (%)", color=C["red"])
    ax.set_xlabel("Water Cut (%)")
    ax.set_ylabel("Oil Rate (kSm³/d)", color=C["blue"])
    ax.set_title("Case Study 2 — Water Cut Impact on Production", fontweight="bold")
    lines1, l1 = ax.get_legend_handles_labels()
    lines2, l2 = ax2.get_legend_handles_labels()
    ax.legend(lines1+lines2, l1+l2, loc="center right", fontsize=8)
    add_watermark(ax)
    savefig("ch23_case_studies", "ch23_case2_water_cut_sensitivity.png", fig)


def ch23_case3_debottleneck_analysis():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    scenarios = ["Base Case", "New Scrubber\n+ Demister", "Comp. Speed\nUpgrade", "Full\nDebottleneck"]
    production = [85, 95, 98, 112]
    capex = [0, 25, 40, 80]
    colors_list = [C["blue"], C["green"], C["orange"], C["red"]]
    bars = ax.bar(scenarios, production, color=colors_list, edgecolor=C["gray"], alpha=0.8, width=0.6)
    ax.axhline(y=100, color=C["gray"], linewidth=2, linestyle="--", label="Design capacity")
    ax2 = ax.twinx()
    ax2.plot(scenarios, capex, "D-", color=C["purple"], linewidth=2, markersize=8, label="CAPEX (MNOK)")
    ax2.set_ylabel("CAPEX (MNOK)", color=C["purple"])
    ax.set_ylabel("Production (% of design)")
    ax.set_title("Case Study 3 — Debottlenecking Scenarios", fontweight="bold")
    lines1, l1 = ax.get_legend_handles_labels()
    lines2, l2 = ax2.get_legend_handles_labels()
    ax.legend(lines1+lines2, l1+l2, loc="upper left", fontsize=8)
    ax.set_ylim(0, 130)
    add_watermark(ax)
    savefig("ch23_case_studies", "ch23_case3_debottleneck_analysis.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 25: NeqSim Optimization Framework (2 figures)
# ═══════════════════════════════════════════════════════════════════

def ch25_fig25_1_architecture():
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis("off")
    layers = [
        (0.5, 6.5, 9, 1.0, "User Interface / API Layer", C["ltblue"]),
        (0.5, 4.8, 9, 1.2, "Optimization Engine\n(SciPy, Genetic Algorithms, Gradient-Free)", C["ltorange"]),
        (0.5, 3.0, 9, 1.3, "NeqSim Process Simulation Core\n(Thermo + Equipment + Flash)", C["ltgreen"]),
        (0.5, 1.2, 9, 1.3, "Thermodynamic Models\n(SRK, PR, CPA, Electrolyte)", C["ltblue"]),
    ]
    for x, y, w, h, label, color in layers:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor=C["gray"], alpha=0.7))
        ax.text(x + w/2, y + h/2, label, ha="center", va="center", fontsize=9, fontweight="bold")
    # Vertical arrows
    for y in [6.5, 4.8, 3.0]:
        ax.annotate("", xy=(5, y), xytext=(5, y+0.5),
                    arrowprops=dict(arrowstyle="<->", color=C["gray"], lw=1.5))
    ax.set_title("NeqSim Optimization Framework Architecture", fontsize=11, fontweight="bold", pad=10)
    savefig("ch25_neqsim_optimization_framework", "fig25_1_architecture.png", fig)


def ch25_fig25_2_component_diagram():
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis("off")
    components = [
        (1, 5, "ProcessSystem", C["ltblue"]),
        (5, 5, "FluidStream", C["ltgreen"]),
        (1, 3, "Equipment\n(Sep, Comp, HX)", C["ltorange"]),
        (5, 3, "ThermodynamicOps\n(Flash, Phase Eq)", C["ltblue"]),
        (8, 5, "Optimization\nDriver", C["ltred"]),
        (8, 3, "Objective\nFunction", C["ltorange"]),
        (3, 1, "Automation API\n(String-based Access)", C["ltgreen"]),
        (7, 1, "Results\nExporter", C["ltblue"]),
    ]
    for x, y, label, color in components:
        ax.add_patch(FancyBboxPatch((x-0.9, y-0.4), 1.8, 0.8, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor=C["gray"]))
        ax.text(x, y, label, ha="center", va="center", fontsize=7.5, fontweight="bold")
    connections = [(0,1), (0,2), (1,3), (4,5), (4,0), (5,3), (2,6), (5,7)]
    for i, j in connections:
        ax.plot([components[i][0], components[j][0]], [components[i][1], components[j][1]],
                color=C["gray"], linewidth=1, linestyle="--")
    ax.set_title("NeqSim Component Diagram", fontsize=11, fontweight="bold", pad=10)
    savefig("ch25_neqsim_optimization_framework", "fig25_2_component_diagram.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 26: Utilization Monitoring (3 figures)
# ═══════════════════════════════════════════════════════════════════

def ch26_fig26_1_utilization_profiles():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    years = np.arange(2025, 2050)
    n = len(years)
    sep = 60 + 35*(1 - np.exp(-0.2*(years-2025))) - 20*(1-np.exp(-0.05*(years-2035)))*np.where(years>2035, 1, 0)
    comp = 50 + 40*(1 - np.exp(-0.15*(years-2025))) - 15*(1-np.exp(-0.05*(years-2035)))*np.where(years>2035, 1, 0)
    dehy = 55 + 30*(1 - np.exp(-0.18*(years-2025))) - 10*(1-np.exp(-0.05*(years-2035)))*np.where(years>2035, 1, 0)
    ax.plot(years, sep, color=C["blue"], linewidth=2, marker="o", markersize=3, label="Separator")
    ax.plot(years, comp, color=C["red"], linewidth=2, marker="s", markersize=3, label="Compressor")
    ax.plot(years, dehy, color=C["green"], linewidth=2, marker="^", markersize=3, label="Dehydration")
    ax.axhline(y=90, color=C["orange"], linestyle="--", linewidth=1.5, label="Warning (90%)")
    ax.axhline(y=100, color=C["red"], linestyle=":", linewidth=1.5, label="Max capacity")
    ax.fill_between(years, 90, 100, color=C["ltorange"], alpha=0.2)
    ax.set_xlabel("Year")
    ax.set_ylabel("Utilization (%)")
    ax.set_title("Equipment Utilization Profiles Over Field Life", fontweight="bold")
    ax.legend(loc="lower right", fontsize=7, ncol=2)
    ax.set_xlim(2025, 2049)
    add_watermark(ax)
    savefig("ch26_utilization_monitoring", "fig26_1_utilization_profiles.png", fig)


def ch26_fig26_2_monitoring_architecture():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.set_xlim(0, 12); ax.set_ylim(0, 5); ax.axis("off")
    boxes = [
        (1, 3.5, "Plant\nHistorian", C["ltblue"]),
        (4, 3.5, "NeqSim\nDigital Twin", C["ltgreen"]),
        (7, 3.5, "Utilization\nCalculator", C["ltorange"]),
        (10, 3.5, "Dashboard\n& Alerts", C["ltred"]),
        (4, 1, "Equipment\nModels", C["ltblue"]),
        (7, 1, "Capacity\nDatabase", C["ltgreen"]),
    ]
    for x, y, label, color in boxes:
        ax.add_patch(FancyBboxPatch((x-0.9, y), 1.8, 1.0, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor=C["gray"]))
        ax.text(x, y+0.5, label, ha="center", va="center", fontsize=8, fontweight="bold")
    # Horizontal flow
    for i in range(3):
        ax.annotate("", xy=(boxes[i+1][0]-0.9, 4), xytext=(boxes[i][0]+0.9, 4),
                    arrowprops=dict(arrowstyle="->", color=C["blue"], lw=2))
    # Vertical
    ax.annotate("", xy=(4, 3.5), xytext=(4, 2), arrowprops=dict(arrowstyle="<->", color=C["gray"], lw=1.2))
    ax.annotate("", xy=(7, 3.5), xytext=(7, 2), arrowprops=dict(arrowstyle="<->", color=C["gray"], lw=1.2))
    ax.set_title("Utilization Monitoring Architecture", fontsize=11, fontweight="bold", pad=5)
    savefig("ch26_utilization_monitoring", "fig26_2_monitoring_architecture.png", fig)


def ch26_fig26_3_utilization_heatmap():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    equipment = ["HP Sep", "MP Sep", "LP Sep", "Comp 1", "Comp 2", "TEG", "Export"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    np.random.seed(42)
    data = 60 + 30*np.random.rand(len(equipment), 12)
    data[3, 5:8] = 95 + 5*np.random.rand(3)  # Comp 1 high in summer
    data[4, 5:8] = 92 + 5*np.random.rand(3)  # Comp 2 high in summer
    im = ax.imshow(data, cmap="RdYlGn_r", aspect="auto", vmin=50, vmax=105)
    ax.set_xticks(range(12)); ax.set_xticklabels(months, fontsize=8)
    ax.set_yticks(range(len(equipment))); ax.set_yticklabels(equipment, fontsize=9)
    plt.colorbar(im, ax=ax, label="Utilization (%)", shrink=0.8)
    ax.set_title("Equipment Utilization Heatmap — Monthly", fontweight="bold")
    savefig("ch26_utilization_monitoring", "fig26_3_utilization_heatmap.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 27: Well Network Optimization (3 figures)
# ═══════════════════════════════════════════════════════════════════

def ch27_fig27_1_ipr_curves():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Pwf = np.linspace(0, 300, 200)
    Pr = 300
    for well, Jv, color in [("Well A", 3200, C["blue"]), ("Well B", 2800, C["red"]), ("Well C", 1500, C["green"])]:
        Q = Jv * (1 - 0.2*(Pwf/Pr) - 0.8*(Pwf/Pr)**2)
        Q = np.clip(Q, 0, None)
        ax.plot(Q, Pwf, color=color, linewidth=2.5, label=well)
    ax.set_xlabel("Flow Rate (Sm³/d)")
    ax.set_ylabel("Flowing Bottom-hole Pressure (bara)")
    ax.set_title("IPR Curves — Multi-Well Comparison", fontweight="bold")
    ax.legend(loc="upper right")
    add_watermark(ax)
    savefig("ch27_well_network_optimization", "fig27_1_ipr_curves.png", fig)


def ch27_fig27_2_vfp_curve():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Q = np.linspace(200, 6000, 200)
    for WHP, color, label in [(15, C["blue"], "15 bara"), (30, C["red"], "30 bara"), (50, C["green"], "50 bara")]:
        Pwf = WHP + 80 + 0.018*Q + 1.5e-6*Q**2
        ax.plot(Q, Pwf, color=color, linewidth=2, label=f"WHP = {label}")
    # IPR overlay
    Pr = 280
    Pwf_ipr = Pr * np.sqrt(np.clip(1 - (Q/5500)**2, 0, None))
    ax.plot(Q, Pwf_ipr, "k-", linewidth=2.5, label="IPR")
    ax.set_xlabel("Flow Rate (Sm³/d)")
    ax.set_ylabel("Flowing BHP (bara)")
    ax.set_title("VFP Curves with IPR Overlay", fontweight="bold")
    ax.legend(loc="lower right", fontsize=8)
    add_watermark(ax)
    savefig("ch27_well_network_optimization", "fig27_2_vfp_curve.png", fig)


def ch27_fig27_3_gaslift_curve():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Q_gl = np.linspace(0, 300, 200)
    for well, Q_max, color in [("Well A", 2800, C["blue"]), ("Well B", 2200, C["red"]), ("Well C", 1200, C["green"])]:
        Q_oil = Q_max * (1 - np.exp(-0.02*Q_gl))
        ax.plot(Q_gl, Q_oil, color=color, linewidth=2.5, label=well)
    # Total
    total = 2800*(1-np.exp(-0.02*Q_gl)) + 2200*(1-np.exp(-0.02*Q_gl)) + 1200*(1-np.exp(-0.02*Q_gl))
    ax.plot(Q_gl, total, "k--", linewidth=2, label="Total field")
    ax.axvline(x=150, color=C["gray"], linestyle=":", alpha=0.5)
    ax.text(155, 1000, "Available\ngas lift", fontsize=8, color=C["gray"])
    ax.set_xlabel("Gas Lift Rate per Well (kSm³/d)")
    ax.set_ylabel("Oil Rate (Sm³/d)")
    ax.set_title("Gas Lift Allocation Optimization", fontweight="bold")
    ax.legend(loc="lower right", fontsize=8)
    add_watermark(ax)
    savefig("ch27_well_network_optimization", "fig27_3_gaslift_curve.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 28: Multi-Scenario Optimization (2 figures)
# ═══════════════════════════════════════════════════════════════════

def ch28_fig28_tornado():
    fig, ax = plt.subplots(figsize=(6.5, 5))
    params = [
        "Oil Price",
        "Gas Price",
        "CAPEX",
        "OPEX",
        "Recovery Factor",
        "Discount Rate",
        "Water Cut",
        "Production Rate",
    ]
    low = np.array([-350, -180, 150, 80, -200, 120, 50, -250])
    high = np.array([400, 220, -120, -60, 250, -100, -40, 300])
    # Sort by swing
    swing = np.abs(high - low)
    order = np.argsort(swing)[::-1]
    params = [params[i] for i in order]
    low = low[order]; high = high[order]
    y_pos = np.arange(len(params))
    ax.barh(y_pos, high, color=C["green"], alpha=0.7, label="High case")
    ax.barh(y_pos, low, color=C["red"], alpha=0.7, label="Low case")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(params)
    ax.axvline(x=0, color=C["black"], linewidth=1)
    ax.set_xlabel("ΔNPV from Base Case (MNOK)")
    ax.set_title("Tornado Diagram — NPV Sensitivity", fontweight="bold")
    ax.legend(loc="lower right", fontsize=8)
    add_watermark(ax)
    savefig("ch28_multi_scenario_optimization", "fig28_tornado.png", fig)


def ch28_fig28_npv_comparison():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    scenarios = ["Conservative", "Base Case", "Optimistic", "High Oil\nPrice", "Low CAPEX", "Debottleneck"]
    npv = [1200, 2500, 4100, 3800, 3200, 3500]
    colors_list = [C["blue"], C["green"], C["orange"], C["red"], C["purple"], C["teal"]]
    bars = ax.bar(scenarios, npv, color=colors_list, edgecolor=C["gray"], alpha=0.85, width=0.6)
    ax.axhline(y=0, color=C["black"], linewidth=0.8)
    for bar, v in zip(bars, npv):
        ax.text(bar.get_x() + bar.get_width()/2, v + 80, f"{v}", ha="center", fontsize=8, fontweight="bold")
    ax.set_ylabel("NPV (MNOK)")
    ax.set_title("NPV Comparison Across Scenarios", fontweight="bold")
    ax.set_ylim(0, 5000)
    add_watermark(ax)
    savefig("ch28_multi_scenario_optimization", "fig28_npv_comparison.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 30: Power Production (3 figures)
# ═══════════════════════════════════════════════════════════════════

def ch30_brayton_cycle_ts():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    # Simplified Brayton cycle T-s diagram
    s1, T1 = 6.0, 300    # Compressor inlet
    s2, T2 = 6.05, 700   # Compressor outlet
    s3, T3 = 7.0, 1500   # Turbine inlet
    s4, T4 = 7.05, 850   # Turbine outlet
    # Isentropic compression
    s_comp = np.linspace(s1, s1, 50)
    T_comp = np.linspace(T1, T2, 50)
    ax.plot(s_comp, T_comp, color=C["blue"], linewidth=2.5)
    # Heat addition (constant pressure)
    s_heat = np.linspace(s1, s3-0.05, 50)
    T_heat = T2 + (T3-T2)*((s_heat-s1)/(s3-0.05-s1))**0.8
    ax.plot(s_heat, T_heat, color=C["red"], linewidth=2.5)
    # Isentropic expansion
    s_exp = np.linspace(s3-0.05, s3-0.05, 50)
    T_exp = np.linspace(T3, T4, 50)
    ax.plot(s_exp, T_exp, color=C["green"], linewidth=2.5)
    # Heat rejection
    s_rej = np.linspace(s3-0.05, s1, 50)
    T_rej = T4 + (T1-T4)*((s_rej-(s3-0.05))/(s1-(s3-0.05)))**1.2
    ax.plot(s_rej, T_rej, color=C["orange"], linewidth=2.5)
    # Labels
    ax.plot(s1, T1, "ko", markersize=8)
    ax.text(s1-0.15, T1, "1", fontsize=10, fontweight="bold")
    ax.plot(s1, T2, "ko", markersize=8)
    ax.text(s1-0.15, T2, "2", fontsize=10, fontweight="bold")
    ax.plot(s3-0.05, T3, "ko", markersize=8)
    ax.text(s3, T3, "3", fontsize=10, fontweight="bold")
    ax.plot(s3-0.05, T4, "ko", markersize=8)
    ax.text(s3, T4, "4", fontsize=10, fontweight="bold")
    ax.text(5.85, 500, "Compression", fontsize=8, color=C["blue"], rotation=90)
    ax.text(6.3, 1200, "Combustion", fontsize=8, color=C["red"])
    ax.text(7.1, 1200, "Expansion", fontsize=8, color=C["green"], rotation=-90)
    ax.text(6.3, 400, "Heat rejection", fontsize=8, color=C["orange"])
    ax.set_xlabel("Specific Entropy, s (kJ/kg·K)")
    ax.set_ylabel("Temperature, T (K)")
    ax.set_title("Brayton Cycle — T-s Diagram", fontweight="bold")
    add_watermark(ax)
    savefig("ch30_power_production", "brayton_cycle_ts.png", fig)


def ch30_gt_ambient_performance():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    T_amb = np.linspace(-20, 45, 100)
    # Power output decreases with temperature
    P_out = 30 * (1 - 0.008*(T_amb - 15))
    eff = 37 - 0.05*(T_amb - 15) - 0.001*(T_amb-15)**2
    ax.plot(T_amb, P_out, color=C["blue"], linewidth=2.5, label="Power Output (MW)")
    ax2 = ax.twinx()
    ax2.plot(T_amb, eff, color=C["red"], linewidth=2, linestyle="--", label="Thermal Efficiency (%)")
    ax2.set_ylabel("Thermal Efficiency (%)", color=C["red"])
    ax.axvline(x=15, color=C["gray"], linestyle=":", alpha=0.5)
    ax.text(17, 28, "ISO\nconditions", fontsize=8, color=C["gray"])
    ax.set_xlabel("Ambient Temperature (°C)")
    ax.set_ylabel("Power Output (MW)", color=C["blue"])
    ax.set_title("Gas Turbine Performance vs Ambient Temperature", fontweight="bold")
    lines1, l1 = ax.get_legend_handles_labels()
    lines2, l2 = ax2.get_legend_handles_labels()
    ax.legend(lines1+lines2, l1+l2, loc="upper right", fontsize=8)
    add_watermark(ax)
    savefig("ch30_power_production", "gt_ambient_performance.png", fig)


def ch30_power_demand_profile():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    years = np.arange(2025, 2050)
    n = len(years)
    # Power demands
    comp_power = np.zeros(n)
    pump_power = np.zeros(n)
    util_power = np.full(n, 5.0)
    for i, yr in enumerate(years):
        t = yr - 2025
        if t < 3:
            comp_power[i] = 5 + 8*t
        elif t < 12:
            comp_power[i] = 30
        else:
            comp_power[i] = 30 - 1.5*(t-12)
        comp_power[i] = max(5, comp_power[i])
        pump_power[i] = 3 + 0.3*t  # water injection increasing
    total = comp_power + pump_power + util_power
    ax.fill_between(years, 0, comp_power, color=C["blue"], alpha=0.7, label="Compression")
    ax.fill_between(years, comp_power, comp_power+pump_power, color=C["green"], alpha=0.7, label="Pumping")
    ax.fill_between(years, comp_power+pump_power, total, color=C["orange"], alpha=0.7, label="Utilities")
    ax.axhline(y=42, color=C["red"], linewidth=2, linestyle="--", label="GT capacity (42 MW)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Power Demand (MW)")
    ax.set_title("Platform Power Demand Profile", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_xlim(2025, 2049)
    add_watermark(ax)
    savefig("ch30_power_production", "power_demand_profile.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating figures for chapters 23-30...")
    funcs = [v for k, v in sorted(globals().items()) if k.startswith("ch") and callable(v)]
    for fn in funcs:
        try:
            fn()
        except Exception as e:
            print(f"  [FAIL] {fn.__name__}: {e}")
    print(f"Done. Generated {len(funcs)} figures.")
