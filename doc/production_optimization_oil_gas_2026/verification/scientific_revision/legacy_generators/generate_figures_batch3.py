#!/usr/bin/env python3
"""Generate all figures for chapters 16-22 (24 figures)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from generate_figures_style import apply_style, savefig, C, PALETTE, add_watermark

apply_style()

# ═══════════════════════════════════════════════════════════════════
# Chapter 16: Produced Water Treatment (1 figure)
# ═══════════════════════════════════════════════════════════════════

def ch16_water_lifecycle_profile():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    years = np.arange(2024, 2050)
    n = len(years)
    # Production profiles
    Q_oil = 20000 * np.exp(-0.06*(years-2024)) * np.minimum(1, 0.5*(years-2024))
    Q_oil = np.clip(Q_oil, 0, None)
    Q_water = 500 + 30000*(1 - np.exp(-0.08*(years-2024)))
    water_cut = Q_water / (Q_oil + Q_water) * 100
    ax2 = ax.twinx()
    ax.bar(years-0.2, Q_oil/1000, 0.4, color=C["green"], alpha=0.7, label="Oil")
    ax.bar(years+0.2, Q_water/1000, 0.4, color=C["ltblue"], alpha=0.7, label="Water")
    ax2.plot(years, water_cut, color=C["red"], linewidth=2.5, linestyle="--", label="Water Cut")
    ax.set_xlabel("Year")
    ax.set_ylabel("Production Rate (kSm³/d)")
    ax2.set_ylabel("Water Cut (%)", color=C["red"])
    ax2.tick_params(axis="y", labelcolor=C["red"])
    ax.set_title("Water Production Lifecycle Profile", fontweight="bold")
    lines1, l1 = ax.get_legend_handles_labels()
    lines2, l2 = ax2.get_legend_handles_labels()
    ax.legend(lines1+lines2, l1+l2, loc="center left", fontsize=8)
    ax.set_xlim(2023, 2049)
    add_watermark(ax)
    savefig("ch16_produced_water_treatment", "water_lifecycle_profile.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 17: Export and Metering (4 figures)
# ═══════════════════════════════════════════════════════════════════

def ch17_gas_quality_envelope():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    # Wobbe index vs GCV plot with spec window
    gcv = np.linspace(34, 44, 100)
    wobbe_hi = 52 + 0.3*(gcv - 39)
    wobbe_lo = 47 + 0.3*(gcv - 39)
    ax.fill_between(gcv, wobbe_lo, wobbe_hi, color=C["ltgreen"], alpha=0.3, label="Spec window")
    ax.plot(gcv, wobbe_hi, color=C["green"], linewidth=1.5)
    ax.plot(gcv, wobbe_lo, color=C["green"], linewidth=1.5)
    # Operating points
    np.random.seed(42)
    gcv_ops = 38 + 2*np.random.randn(50)
    wobbe_ops = 49.5 + 1.5*np.random.randn(50)
    in_spec = (wobbe_ops > 47 + 0.3*(gcv_ops-39)) & (wobbe_ops < 52 + 0.3*(gcv_ops-39))
    ax.scatter(gcv_ops[in_spec], wobbe_ops[in_spec], c=C["blue"], s=20, label="In-spec", zorder=5)
    ax.scatter(gcv_ops[~in_spec], wobbe_ops[~in_spec], c=C["red"], s=30, marker="x", label="Off-spec", zorder=5)
    ax.set_xlabel("Gross Calorific Value (MJ/Sm³)")
    ax.set_ylabel("Wobbe Index (MJ/Sm³)")
    ax.set_title("Gas Quality Envelope (ISO 6976)", fontweight="bold")
    ax.legend(loc="upper left", fontsize=8)
    add_watermark(ax)
    savefig("ch17_export_and_metering", "gas_quality_envelope.png", fig)


def ch17_gcv_wobbe_vs_ngl():
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 4))
    C2_frac = np.linspace(0, 0.10, 100)
    # GCV increases with heavier components
    gcv = 37.5 + 40*C2_frac + 80*C2_frac**2
    wobbe = 49 + 25*C2_frac + 50*C2_frac**2
    axes[0].plot(C2_frac*100, gcv, color=C["blue"], linewidth=2.5)
    axes[0].axhline(y=42.3, color=C["red"], linestyle="--", label="Max spec (42.3)")
    axes[0].axhline(y=36.0, color=C["green"], linestyle="--", label="Min spec (36.0)")
    axes[0].set_xlabel("C2+ Content (mol%)")
    axes[0].set_ylabel("GCV (MJ/Sm³)")
    axes[0].set_title("GCV vs NGL Content", fontweight="bold")
    axes[0].legend(fontsize=7)
    axes[1].plot(C2_frac*100, wobbe, color=C["red"], linewidth=2.5)
    axes[1].axhline(y=52.0, color=C["red"], linestyle="--", label="Max (52.0)")
    axes[1].axhline(y=47.0, color=C["green"], linestyle="--", label="Min (47.0)")
    axes[1].set_xlabel("C2+ Content (mol%)")
    axes[1].set_ylabel("Wobbe Index (MJ/Sm³)")
    axes[1].set_title("Wobbe Index vs NGL Content", fontweight="bold")
    axes[1].legend(fontsize=7)
    fig.tight_layout()
    savefig("ch17_export_and_metering", "gcv_wobbe_vs_ngl.png", fig)


def ch17_phase_envelope_export_gas():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    theta = np.linspace(0, 2*np.pi, 300)
    r = 0.6 + 0.3*np.cos(theta)
    T = -30 + 60*r*np.cos(theta - 0.2)
    P = 60 + 50*r*np.sin(theta)
    ax.plot(T, P, color=C["blue"], linewidth=2.5, label="Phase envelope")
    # Cricondenbar
    max_p_idx = np.argmax(P)
    ax.plot(T[max_p_idx], P[max_p_idx], "ko", markersize=8)
    ax.annotate("Cricondenbar", xy=(T[max_p_idx], P[max_p_idx]), xytext=(T[max_p_idx]-30, P[max_p_idx]+10),
                fontsize=8, arrowprops=dict(arrowstyle="->"))
    # Export pipeline conditions
    ax.plot(5, 120, "D", color=C["green"], markersize=10, label="Pipeline inlet")
    ax.plot(-2, 90, "s", color=C["orange"], markersize=10, label="Pipeline outlet")
    ax.plot([5, -2], [120, 90], "--", color=C["gray"], linewidth=1.5)
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Pressure (bara)")
    ax.set_title("Export Gas Phase Envelope with Pipeline Conditions", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    add_watermark(ax)
    savefig("ch17_export_and_metering", "phase_envelope_export_gas.png", fig)


def ch17_pipeline_sizing_dp_vs_diameter():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    D = np.linspace(8, 36, 100)  # inches
    for Q, color, label in [(5, C["blue"], "5 MSm³/d"), (10, C["red"], "10 MSm³/d"), (15, C["green"], "15 MSm³/d")]:
        dp_per_km = 500 * Q**1.8 / (D**4.8)
        ax.semilogy(D, dp_per_km, color=color, linewidth=2.5, label=label)
    ax.axhline(y=0.5, color=C["gray"], linestyle=":", label="Max ΔP/km = 0.5 bar/km")
    ax.set_xlabel("Pipeline Diameter (inches)")
    ax.set_ylabel("Pressure Drop (bar/km)")
    ax.set_title("Pipeline Sizing: Pressure Drop vs Diameter", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_xlim(8, 36); ax.set_ylim(0.01, 100)
    add_watermark(ax)
    savefig("ch17_export_and_metering", "pipeline_sizing_dp_vs_diameter.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 18cap: Capacity Checks and Utilization (5 figures)
# ═══════════════════════════════════════════════════════════════════

def ch18cap_separator_capacity_diagram():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Q_gas = np.linspace(0, 15, 100)  # MSm3/d
    Q_liq_max = 25 - 1.2*Q_gas - 0.05*Q_gas**2
    Q_liq_max = np.clip(Q_liq_max, 0, None)
    ax.plot(Q_gas, Q_liq_max, color=C["blue"], linewidth=2.5, label="Max liquid capacity")
    ax.fill_between(Q_gas, 0, Q_liq_max, color=C["ltgreen"], alpha=0.3)
    ax.text(5, 8, "Operating\nRegion", fontsize=11, color=C["green"], ha="center", fontweight="bold")
    # Operating points
    ax.plot(8, 10, "D", color=C["green"], markersize=10, label="Design point")
    ax.plot(10, 12, "*", color=C["orange"], markersize=14, label="Current operation")
    ax.set_xlabel("Gas Rate (MSm³/d)")
    ax.set_ylabel("Liquid Rate (kSm³/d)")
    ax.set_title("Separator Capacity Diagram", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    add_watermark(ax)
    savefig("ch18_capacity_checks_and_utilization", "separator_capacity_diagram.png", fig)


def ch18cap_compressor_capacity_map():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Q = np.linspace(2000, 14000, 200)
    # Max and min head envelopes
    H_max = 100 - 0.5e-6*(Q-7000)**2
    H_min = 30 - 0.2e-6*(Q-7000)**2
    H_max = np.clip(H_max, 0, None)
    H_min = np.clip(H_min, 0, None)
    ax.fill_between(Q, H_min, H_max, color=C["ltblue"], alpha=0.3, label="Operating range")
    ax.plot(Q, H_max, color=C["blue"], linewidth=2)
    ax.plot(Q, H_min, color=C["blue"], linewidth=2, linestyle="--")
    # Surge line
    Q_s = np.array([3000, 3500, 4000, 5000])
    H_s = np.array([40, 55, 70, 95])
    ax.plot(Q_s, H_s, color=C["red"], linewidth=2.5, label="Surge line")
    # Design and operating
    ax.plot(8000, 75, "D", color=C["green"], markersize=12, label="Design")
    ax.plot(6000, 80, "*", color=C["orange"], markersize=14, label="Current")
    ax.set_xlabel("Volume Flow (Am³/h)")
    ax.set_ylabel("Polytropic Head (kJ/kg)")
    ax.set_title("Compressor Capacity Map", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    add_watermark(ax)
    savefig("ch18_capacity_checks_and_utilization", "compressor_capacity_map.png", fig)


def ch18cap_capacity_staircase():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    equipment = ["Inlet\nSep", "HP\nSep", "1st Stage\nComp", "2nd Stage\nComp", "Gas\nDehy", "Export\nComp", "Export\nPipe"]
    capacity = [120, 105, 95, 110, 100, 88, 115]
    colors_list = [C["blue"] if c >= 100 else C["red"] for c in capacity]
    bars = ax.bar(equipment, capacity, color=colors_list, edgecolor=C["gray"], alpha=0.8)
    ax.axhline(y=100, color=C["green"], linewidth=2, linestyle="--", label="Production target")
    ax.set_ylabel("Capacity (% of target)")
    ax.set_title("Capacity Staircase — Bottleneck Identification", fontweight="bold")
    # Annotate bottleneck
    min_idx = np.argmin(capacity)
    ax.annotate("Bottleneck!", xy=(min_idx, capacity[min_idx]), xytext=(min_idx+0.5, capacity[min_idx]+10),
                fontsize=10, color=C["red"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C["red"], lw=2))
    ax.legend(loc="upper right")
    ax.set_ylim(0, 140)
    add_watermark(ax)
    savefig("ch18_capacity_checks_and_utilization", "capacity_staircase.png", fig)


def ch18cap_utilization_vs_production():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Q_prod = np.linspace(50, 120, 100)
    util_sep = np.clip(Q_prod / 110 * 100, 0, 100)
    util_comp = np.clip(Q_prod / 95 * 100, 0, 100)
    util_dehy = np.clip(Q_prod / 100 * 100, 0, 100)
    ax.plot(Q_prod, util_sep, color=C["blue"], linewidth=2, label="Separator")
    ax.plot(Q_prod, util_comp, color=C["red"], linewidth=2, linestyle="--", label="Compressor")
    ax.plot(Q_prod, util_dehy, color=C["green"], linewidth=2, linestyle="-.", label="Dehydration")
    ax.axhline(y=100, color=C["gray"], linewidth=1.5, linestyle=":")
    ax.axhline(y=90, color=C["orange"], linewidth=1, linestyle=":", alpha=0.5)
    ax.text(55, 92, "90% warning level", fontsize=8, color=C["orange"])
    ax.set_xlabel("Production Rate (% of plateau)")
    ax.set_ylabel("Equipment Utilization (%)")
    ax.set_title("Equipment Utilization vs Production Rate", fontweight="bold")
    ax.legend(loc="upper left", fontsize=8)
    add_watermark(ax)
    savefig("ch18_capacity_checks_and_utilization", "utilization_vs_production.png", fig)


def ch18cap_utilization_trend_field_life():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    years = np.arange(2024, 2048)
    n = len(years)
    # Production ramp-up, plateau, decline
    prod = np.zeros(n)
    for i in range(n):
        yr = i
        if yr < 3:
            prod[i] = 30 + 30*yr
        elif yr < 10:
            prod[i] = 100
        else:
            prod[i] = 100 * np.exp(-0.08*(yr-10))
    # Equipment utilizations
    util_sep = prod * 0.95
    util_comp = prod * 1.05
    util_comp = np.clip(util_comp, 0, 100)
    ax.plot(years, util_sep, color=C["blue"], linewidth=2, label="Separator utilization")
    ax.plot(years, util_comp, color=C["red"], linewidth=2, linestyle="--", label="Compressor utilization")
    ax.fill_between(years, 90, 100, color=C["ltorange"], alpha=0.3)
    ax.text(2030, 95, "Caution zone", fontsize=8, color=C["orange"], ha="center")
    ax.axhline(y=100, color=C["red"], linewidth=1.5, linestyle=":")
    ax.set_xlabel("Year")
    ax.set_ylabel("Utilization (%)")
    ax.set_title("Equipment Utilization Over Field Life", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_xlim(2024, 2047)
    add_watermark(ax)
    savefig("ch18_capacity_checks_and_utilization", "utilization_trend_field_life.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 19po: Production Optimization Theory (5 figures)
# ═══════════════════════════════════════════════════════════════════

def ch19po_nodal_analysis_operating_point():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Q = np.linspace(100, 5000, 200)
    Pr = 300
    Pwf_ipr = Pr * (1 - 0.2*(Q/5000) - 0.8*(Q/5000)**2)
    Pwf_ipr = np.clip(Pwf_ipr, 0, None)
    Pwf_vlp = 30 + 0.03*Q + 2e-6*Q**2
    ax.plot(Q, Pwf_ipr, color=C["blue"], linewidth=2.5, label="IPR")
    ax.plot(Q, Pwf_vlp, color=C["red"], linewidth=2.5, linestyle="--", label="VLP")
    # Operating point
    diff = np.abs(Pwf_ipr - Pwf_vlp)
    idx = np.argmin(diff)
    ax.plot(Q[idx], Pwf_ipr[idx], "ko", markersize=12, zorder=5)
    ax.annotate(f"Operating Point\nQ = {Q[idx]:.0f} Sm³/d\nPwf = {Pwf_ipr[idx]:.0f} bara",
                xy=(Q[idx], Pwf_ipr[idx]), xytext=(Q[idx]+600, Pwf_ipr[idx]+30),
                fontsize=9, arrowprops=dict(arrowstyle="->", color=C["black"], lw=1.5),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.8))
    ax.set_xlabel("Flow Rate (Sm³/d)")
    ax.set_ylabel("Flowing Bottom-hole Pressure (bara)")
    ax.set_title("Nodal Analysis — Operating Point", fontweight="bold")
    ax.legend(loc="upper right")
    add_watermark(ax)
    savefig("ch19_production_optimization_theory", "nodal_analysis_operating_point.png", fig)


def ch19po_separator_pressure_contour():
    fig, ax = plt.subplots(figsize=(6.5, 5))
    P_hp = np.linspace(30, 90, 100)
    P_mp = np.linspace(5, 30, 100)
    PHP, PMP = np.meshgrid(P_hp, P_mp)
    # Oil recovery objective (simplified)
    Z = 95 - 0.002*(PHP-60)**2 - 0.01*(PMP-15)**2 - 0.001*(PHP-60)*(PMP-15)
    cs = ax.contourf(PHP, PMP, Z, levels=15, cmap="RdYlGn")
    plt.colorbar(cs, ax=ax, label="Oil Recovery (%)")
    ax.contour(PHP, PMP, Z, levels=15, colors="k", linewidths=0.5, alpha=0.3)
    ax.plot(60, 15, "w*", markersize=15, markeredgecolor="k", markeredgewidth=1.5, label="Optimum")
    ax.set_xlabel("HP Separator Pressure (bara)")
    ax.set_ylabel("MP Separator Pressure (bara)")
    ax.set_title("Separator Pressure Optimization Contour", fontweight="bold")
    ax.legend(loc="upper right")
    savefig("ch19_production_optimization_theory", "separator_pressure_contour.png", fig)


def ch19po_gas_lift_performance_curves():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Q_gl = np.linspace(0, 250, 200)
    for Pr, color, label in [(350, C["blue"], "Pr=350 bara"), (280, C["red"], "Pr=280 bara"), (200, C["green"], "Pr=200 bara")]:
        Q_oil = (Pr/350) * 3000 * (1 - np.exp(-0.025*Q_gl)) + 200
        ax.plot(Q_gl, Q_oil, color=color, linewidth=2, label=label)
    ax.axvline(x=80, color=C["gray"], linestyle=":", alpha=0.5)
    ax.text(85, 500, "Economic\nlimit", fontsize=8, color=C["gray"])
    ax.set_xlabel("Gas Lift Injection Rate (kSm³/d)")
    ax.set_ylabel("Oil Production Rate (Sm³/d)")
    ax.set_title("Gas Lift Performance at Different Reservoir Pressures", fontweight="bold")
    ax.legend(loc="lower right")
    add_watermark(ax)
    savefig("ch19_production_optimization_theory", "gas_lift_performance_curves.png", fig)


def ch19po_interstage_pressure_optimization():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    P2 = np.linspace(5, 60, 200)
    # Total compression power for 3-stage
    P1 = 3  # suction
    P3 = 150  # discharge
    W_total = 2.5*((P2/P1)**0.28 - 1) + 2.5*((P3/P2)**0.28 - 1)
    ax.plot(P2, W_total, color=C["blue"], linewidth=2.5)
    idx_min = np.argmin(W_total)
    ax.plot(P2[idx_min], W_total[idx_min], "ro", markersize=10, zorder=5)
    ax.annotate(f"Minimum Power\nP₂ = {P2[idx_min]:.0f} bara",
                xy=(P2[idx_min], W_total[idx_min]), xytext=(P2[idx_min]+15, W_total[idx_min]+0.3),
                fontsize=9, arrowprops=dict(arrowstyle="->", color=C["red"]))
    ax.set_xlabel("Interstage Pressure, P₂ (bara)")
    ax.set_ylabel("Specific Power (kW per kg/s)")
    ax.set_title("Interstage Pressure Optimization — 2-Stage Compression", fontweight="bold")
    add_watermark(ax)
    savefig("ch19_production_optimization_theory", "interstage_pressure_optimization.png", fig)


def ch19po_pareto_front_oil_vs_power():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    np.random.seed(42)
    n = 200
    # Random feasible solutions
    oil = 3000 + 2000*np.random.rand(n)
    power = 15 + 10*np.random.rand(n) + 0.002*(oil-4000)**2/1000
    ax.scatter(oil, power, c=C["ltblue"], s=15, alpha=0.5, label="Feasible solutions")
    # Pareto front
    oil_pareto = np.linspace(3200, 5000, 30)
    power_pareto = 14 + 0.003*(oil_pareto-3200)**1.3/100
    ax.plot(oil_pareto, power_pareto, "o-", color=C["red"], linewidth=2.5, markersize=5, label="Pareto front")
    # Selected solution
    ax.plot(4200, 16.5, "*", color=C["green"], markersize=18, zorder=5, label="Selected solution")
    ax.set_xlabel("Oil Production (Sm³/d)")
    ax.set_ylabel("Power Consumption (MW)")
    ax.set_title("Pareto Front: Oil Production vs Power", fontweight="bold")
    ax.legend(loc="upper left", fontsize=8)
    add_watermark(ax)
    savefig("ch19_production_optimization_theory", "pareto_front_oil_vs_power.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 20: Dynamic Simulation and Control (5 figures)
# ═══════════════════════════════════════════════════════════════════

def ch20_feedback_control_loop():
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_xlim(0, 12); ax.set_ylim(0, 5); ax.axis("off")
    boxes = [
        (1, 2.5, "Set\nPoint", C["ltgreen"]),
        (3.5, 2.5, "Controller\n(PID)", C["ltorange"]),
        (6.5, 2.5, "Final\nElement\n(Valve)", C["ltblue"]),
        (9.5, 2.5, "Process", C["ltblue"]),
        (9.5, 0.5, "Sensor/\nTransmitter", C["ltorange"]),
    ]
    for x, y, label, color in boxes:
        ax.add_patch(FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.8, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor=C["gray"]))
        ax.text(x, y, label, ha="center", va="center", fontsize=7.5, fontweight="bold")
    # Forward path
    for i in range(3):
        ax.annotate("", xy=(boxes[i+1][0]-0.8, boxes[i+1][1]), xytext=(boxes[i][0]+0.8, boxes[i][1]),
                    arrowprops=dict(arrowstyle="->", color=C["blue"], lw=2))
    # Feedback
    ax.annotate("", xy=(boxes[4][0], boxes[4][1]+0.4), xytext=(boxes[3][0], boxes[3][1]-0.4),
                arrowprops=dict(arrowstyle="->", color=C["red"], lw=1.5))
    ax.plot([9.5, 3.5], [0.9, 0.9], color=C["red"], linewidth=1.5)
    ax.annotate("", xy=(3.5, 2.1), xytext=(3.5, 0.9),
                arrowprops=dict(arrowstyle="->", color=C["red"], lw=1.5))
    ax.text(6, 0.6, "Feedback (PV)", fontsize=8, color=C["red"], ha="center")
    ax.text(5, 3.6, "Forward Path", fontsize=8, color=C["blue"], ha="center")
    ax.set_title("Feedback Control Loop", fontsize=11, fontweight="bold", pad=5)
    savefig("ch20_dynamic_simulation_and_control", "feedback_control_loop.png", fig)


def ch20_separator_dynamic_response():
    fig, axes = plt.subplots(2, 1, figsize=(6.5, 5.5), sharex=True)
    t = np.linspace(0, 60, 500)  # minutes
    # Level response to flow disturbance
    level_sp = 50 * np.ones_like(t)
    level = 50 + 8*np.exp(-0.05*t)*np.sin(0.3*t) + np.where(t>10, 5*(1-np.exp(-0.08*(t-10))), 0)
    level = level - 3*(1 - np.exp(-0.03*t))
    axes[0].plot(t, level_sp, "k--", linewidth=1, label="Setpoint")
    axes[0].plot(t, level, color=C["blue"], linewidth=2, label="Level (PV)")
    axes[0].set_ylabel("Level (%)")
    axes[0].set_title("Separator Level — Dynamic Response", fontweight="bold")
    axes[0].legend(fontsize=8)
    axes[0].set_ylim(30, 70)
    # Valve position
    valve = 50 - 10*np.exp(-0.05*t)*np.cos(0.3*t) + np.where(t>10, -8*(1-np.exp(-0.06*(t-10))), 0)
    axes[1].plot(t, valve, color=C["red"], linewidth=2)
    axes[1].set_xlabel("Time (minutes)")
    axes[1].set_ylabel("Valve Opening (%)")
    axes[1].set_title("Control Valve Response", fontweight="bold")
    fig.tight_layout()
    savefig("ch20_dynamic_simulation_and_control", "ch20_separator_dynamic_response.png", fig)


def ch20_compressor_map_antisurge():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Q = np.linspace(2000, 14000, 200)
    # Speed lines
    for N, alpha_val in [(9000, 0.4), (10000, 0.6), (11000, 0.8), (12000, 1.0)]:
        H = (N/10000)**2 * 90 * (1 - 0.4*((Q*10000/N/7500)-1)**2)
        H = np.clip(H, 5, None)
        mask = (H > 5) & (Q < N*1.2)
        ax.plot(Q[mask], H[mask], color=C["blue"], linewidth=1.5, alpha=alpha_val)
    # Surge line
    Q_s = np.array([2500, 3200, 4000, 5000, 6000])
    H_s = np.array([25, 40, 55, 75, 92])
    ax.plot(Q_s, H_s, color=C["red"], linewidth=3, label="Surge limit")
    # Control line
    Q_c = Q_s * 1.1
    ax.plot(Q_c, H_s, color=C["orange"], linewidth=2, linestyle="--", label="Control line (10% margin)")
    ax.fill_betweenx([0, 100], 0, 4000, color=C["ltred"], alpha=0.15)
    ax.text(2500, 60, "SURGE\nZONE", fontsize=12, color=C["red"], fontweight="bold", ha="center")
    # Operating trajectory
    ax.annotate("", xy=(4500, 65), xytext=(7000, 50),
                arrowprops=dict(arrowstyle="-|>", color=C["green"], lw=2.5))
    ax.text(7500, 48, "Recycle opens", fontsize=8, color=C["green"])
    ax.set_xlabel("Volume Flow (Am³/h)")
    ax.set_ylabel("Polytropic Head (kJ/kg)")
    ax.set_title("Anti-Surge Control on Compressor Map", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_xlim(1500, 14000); ax.set_ylim(0, 100)
    add_watermark(ax)
    savefig("ch20_dynamic_simulation_and_control", "ch20_compressor_map_antisurge.png", fig)


def ch20_blowdown_curves():
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 4))
    t = np.linspace(0, 30, 200)  # minutes
    # Pressure
    P = 85 * np.exp(-0.12*t) + 1
    axes[0].plot(t, P, color=C["blue"], linewidth=2.5)
    axes[0].axhline(y=6.9, color=C["red"], linestyle="--", label="API 521 target (15 min)")
    axes[0].axvline(x=15, color=C["gray"], linestyle=":", alpha=0.5)
    axes[0].set_xlabel("Time (minutes)")
    axes[0].set_ylabel("Pressure (bara)")
    axes[0].set_title("Blowdown Pressure", fontweight="bold")
    axes[0].legend(fontsize=8)
    # Temperature
    T = 80 - 70*(1-np.exp(-0.08*t))
    T_wall = 80 - 50*(1-np.exp(-0.05*t))
    axes[1].plot(t, T, color=C["blue"], linewidth=2, label="Gas temperature")
    axes[1].plot(t, T_wall, color=C["red"], linewidth=2, linestyle="--", label="Wall temperature")
    axes[1].axhline(y=-46, color=C["purple"], linestyle=":", label="MDMT (-46°C)")
    axes[1].set_xlabel("Time (minutes)")
    axes[1].set_ylabel("Temperature (°C)")
    axes[1].set_title("Blowdown Temperature", fontweight="bold")
    axes[1].legend(fontsize=7)
    fig.tight_layout()
    savefig("ch20_dynamic_simulation_and_control", "ch20_blowdown_curves.png", fig)


def ch20_slug_response():
    fig, axes = plt.subplots(2, 1, figsize=(6.5, 5.5), sharex=True)
    t = np.linspace(0, 120, 1000)  # minutes
    # Slug arrival - periodic liquid surges
    flow = 5000 + 3000*np.sin(0.15*t)**2 * np.where(np.sin(0.15*t) > 0.7, 1, 0.1)
    flow += 200*np.random.randn(len(t))
    level = 50 + 15*np.sin(0.15*t) + 5*np.random.randn(len(t))*0.3
    axes[0].plot(t, flow, color=C["blue"], linewidth=1, alpha=0.8)
    axes[0].set_ylabel("Inlet Flow (Sm³/d)")
    axes[0].set_title("Slug Flow — Separator Response", fontweight="bold")
    axes[0].axhline(y=5000, color=C["gray"], linestyle=":", alpha=0.5)
    axes[1].plot(t, level, color=C["red"], linewidth=1.5)
    axes[1].axhline(y=50, color=C["gray"], linestyle="--", label="SP", linewidth=1)
    axes[1].axhline(y=70, color=C["orange"], linestyle=":", label="HH alarm")
    axes[1].axhline(y=30, color=C["orange"], linestyle=":", label="LL alarm")
    axes[1].set_xlabel("Time (minutes)")
    axes[1].set_ylabel("Level (%)")
    axes[1].legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    savefig("ch20_dynamic_simulation_and_control", "ch20_slug_response.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 21dt: Digital Twins and Automation (4 figures)
# ═══════════════════════════════════════════════════════════════════

def ch21dt_digital_twin_architecture():
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis("off")
    # Physical layer
    ax.add_patch(FancyBboxPatch((0.5, 0.5), 11, 2, boxstyle="round,pad=0.1",
                 facecolor=C["ltgreen"], edgecolor=C["green"], alpha=0.3))
    ax.text(6, 1.5, "Physical Plant", fontsize=11, ha="center", fontweight="bold", color=C["green"])
    ax.text(2, 0.9, "Sensors", fontsize=8); ax.text(5, 0.9, "Actuators", fontsize=8)
    ax.text(8.5, 0.9, "DCS/SCADA", fontsize=8)
    # Data layer
    ax.add_patch(FancyBboxPatch((0.5, 3), 11, 1.3, boxstyle="round,pad=0.1",
                 facecolor=C["ltblue"], edgecolor=C["blue"], alpha=0.3))
    ax.text(6, 3.6, "Data Infrastructure (Historian / Streaming)", fontsize=10, ha="center", fontweight="bold", color=C["blue"])
    # Digital twin
    ax.add_patch(FancyBboxPatch((0.5, 4.8), 11, 2.5, boxstyle="round,pad=0.1",
                 facecolor=C["ltorange"], edgecolor=C["orange"], alpha=0.3))
    ax.text(6, 6.8, "Digital Twin Layer", fontsize=11, ha="center", fontweight="bold", color=C["orange"])
    twin_boxes = [
        (2, 5.3, "NeqSim\nProcess Model"),
        (5.5, 5.3, "State\nEstimation"),
        (9, 5.3, "Optimization\nEngine"),
    ]
    for x, y, label in twin_boxes:
        ax.add_patch(FancyBboxPatch((x-0.9, y), 1.8, 1.0, boxstyle="round,pad=0.08",
                     facecolor="white", edgecolor=C["orange"]))
        ax.text(x, y+0.5, label, ha="center", va="center", fontsize=8)
    # Arrows
    ax.annotate("", xy=(6, 3), xytext=(6, 2.5), arrowprops=dict(arrowstyle="<->", color=C["gray"], lw=2))
    ax.annotate("", xy=(6, 4.8), xytext=(6, 4.3), arrowprops=dict(arrowstyle="<->", color=C["gray"], lw=2))
    ax.set_title("Digital Twin Architecture", fontsize=12, fontweight="bold", pad=10)
    savefig("ch21_digital_twins_and_automation", "ch21_digital_twin_architecture.png", fig)


def ch21dt_rto_cycle():
    fig, ax = plt.subplots(figsize=(6, 5.5))
    ax.set_xlim(0, 8); ax.set_ylim(0, 8); ax.axis("off")
    steps = [
        (4, 7, "Data\nAcquisition", C["blue"]),
        (7, 5, "Model\nUpdate", C["green"]),
        (7, 2.5, "Optimization", C["orange"]),
        (4, 0.8, "Implementation", C["red"]),
        (1, 2.5, "Validation", C["purple"]),
        (1, 5, "Monitoring", C["teal"]),
    ]
    for x, y, label, color in steps:
        ax.add_patch(FancyBboxPatch((x-1, y-0.4), 2, 0.8, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor="white", alpha=0.85))
        ax.text(x, y, label, ha="center", va="center", fontsize=8.5, fontweight="bold", color="white")
    # Circular arrows
    for i in range(len(steps)):
        j = (i+1) % len(steps)
        ax.annotate("", xy=(steps[j][0], steps[j][1]), xytext=(steps[i][0], steps[i][1]),
                    arrowprops=dict(arrowstyle="-|>", color=C["gray"], lw=1.5,
                                   connectionstyle="arc3,rad=0.2"))
    ax.text(4, 4, "RTO\nCycle", fontsize=14, ha="center", va="center", fontweight="bold", color=C["gray"])
    ax.set_title("Real-Time Optimization Cycle", fontsize=11, fontweight="bold", pad=5)
    savefig("ch21_digital_twins_and_automation", "ch21_rto_cycle.png", fig)


def ch21dt_digital_twin_tracking():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    t = np.linspace(0, 48, 500)  # hours
    np.random.seed(123)
    # Measured data with noise
    T_meas = 65 + 5*np.sin(0.3*t) + 2*np.random.randn(len(t))
    # Model prediction (initially good, then drifts, then corrected)
    T_model = 65 + 5*np.sin(0.3*t)
    T_model[200:] += 3*(t[200:]-t[200])/20  # drift
    T_model[350:] = 65 + 5*np.sin(0.3*t[350:]) + 0.5  # recalibrated
    ax.plot(t, T_meas, color=C["blue"], linewidth=1, alpha=0.6, label="Measured")
    ax.plot(t, T_model, color=C["red"], linewidth=2, label="Digital Twin")
    ax.axvspan(t[200], t[350], color=C["ltred"], alpha=0.2)
    ax.text(30, 73, "Model drift\ndetected", fontsize=8, color=C["red"], ha="center")
    ax.axvline(x=t[350], color=C["green"], linestyle="--", linewidth=1.5)
    ax.text(t[355], 58, "Recalibrated", fontsize=8, color=C["green"])
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Temperature (°C)")
    ax.set_title("Digital Twin Tracking Performance", fontweight="bold")
    ax.legend(loc="upper left", fontsize=8)
    add_watermark(ax)
    savefig("ch21_digital_twins_and_automation", "ch21_digital_twin_tracking.png", fig)


def ch21dt_domain_architecture():
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis("off")
    # Layers
    layers = [
        (0.5, 5.5, 9, 1.0, "Presentation Layer\n(Dashboards, Reports, APIs)", C["ltblue"]),
        (0.5, 3.8, 9, 1.2, "Application Layer\n(RTO, Advisory, What-If)", C["ltorange"]),
        (0.5, 2.0, 9, 1.3, "Domain Layer\n(NeqSim Thermo + Process Models)", C["ltgreen"]),
        (0.5, 0.5, 9, 1.0, "Infrastructure Layer\n(Data, Historian, Messaging)", C["ltred"]),
    ]
    for x, y, w, h, label, color in layers:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor=C["gray"], alpha=0.7))
        ax.text(x + w/2, y + h/2, label, ha="center", va="center", fontsize=9, fontweight="bold")
    ax.set_title("Domain-Driven Digital Twin Architecture", fontsize=11, fontweight="bold", pad=10)
    savefig("ch21_digital_twins_and_automation", "ch21_domain_architecture.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 22o: Onshore Processing Plants (4 figures)
# ═══════════════════════════════════════════════════════════════════

def ch22o_onshore_plant_block_diagram():
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_xlim(0, 14); ax.set_ylim(0, 5.5); ax.axis("off")
    units = [
        (0.3, 2.5, "Inlet\nReceiving", C["ltblue"]),
        (2.8, 2.5, "Slug\nCatcher", C["ltblue"]),
        (5.3, 3.8, "Amine\nUnit", C["ltorange"]),
        (5.3, 1.2, "Condensate\nStab.", C["ltgreen"]),
        (8, 3.8, "Dehydration\n(TEG)", C["ltorange"]),
        (8, 1.2, "NGL\nRecovery", C["ltgreen"]),
        (10.8, 2.5, "Sales Gas\nCompression", C["ltorange"]),
    ]
    for x, y, label, color in units:
        ax.add_patch(FancyBboxPatch((x, y), 2.2, 1.0, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor=C["gray"]))
        ax.text(x+1.1, y+0.5, label, ha="center", va="center", fontsize=7.5, fontweight="bold")
    # Connect
    arrows_list = [(0,1), (1,2), (1,3), (2,4), (3,5), (4,6), (5,6)]
    for i, j in arrows_list:
        x1 = units[i][0]+2.2; y1 = units[i][1]+0.5
        x2 = units[j][0]; y2 = units[j][1]+0.5
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=C["gray"], lw=1.2))
    ax.set_title("Onshore Gas Processing Plant — Block Diagram", fontsize=11, fontweight="bold", pad=5)
    savefig("ch22_onshore_processing_plants", "ch22_onshore_plant_block_diagram.png", fig)


def ch22o_amine_unit_pfd():
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7); ax.axis("off")
    units = [
        (1, 3, "Absorber\nColumn", C["ltblue"]),
        (4.5, 3, "Flash\nDrum", C["ltblue"]),
        (4.5, 0.5, "Lean/Rich\nExchanger", C["ltorange"]),
        (8, 3, "Regenerator\nColumn", C["ltblue"]),
        (8, 0.5, "Reboiler", C["ltred"]),
        (1, 0.5, "Lean Amine\nPump", C["ltgreen"]),
    ]
    for x, y, label, color in units:
        ax.add_patch(FancyBboxPatch((x, y), 2.2, 1.5, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor=C["gray"]))
        ax.text(x+1.1, y+0.75, label, ha="center", va="center", fontsize=8, fontweight="bold")
    # Gas path
    ax.annotate("Sour gas →", xy=(1, 3.75), xytext=(-0.5, 3.75), fontsize=8, color=C["blue"],
                arrowprops=dict(arrowstyle="->", color=C["blue"]))
    ax.text(1.5, 5, "Sweet gas ↑", fontsize=8, color=C["green"])
    # Rich amine path
    ax.plot([3.2, 4.5], [3.75, 3.75], color=C["red"], linewidth=1.5)
    ax.plot([6.7, 8], [3.75, 3.75], color=C["red"], linewidth=1.5)
    # Lean return
    ax.plot([8, 8], [3, 2], color=C["green"], linewidth=1.5, linestyle="--")
    ax.plot([8, 1], [0.5, 0.5], color=C["green"], linewidth=1.5, linestyle="--")
    ax.plot([1, 1], [2, 3], color=C["green"], linewidth=1.5, linestyle="--")
    ax.text(5, 5.5, "Rich amine →", fontsize=8, color=C["red"])
    ax.text(5, 6.2, "← Lean amine", fontsize=8, color=C["green"])
    ax.set_title("Amine Unit Process Flow Diagram", fontsize=11, fontweight="bold", pad=10)
    savefig("ch22_onshore_processing_plants", "ch22_amine_unit_pfd.png", fig)


def ch22o_turboexpander_pfd():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.set_xlim(0, 12); ax.set_ylim(0, 5); ax.axis("off")
    units = [
        (0.5, 2, "Inlet\nCooler", C["ltblue"]),
        (3.0, 2, "Cold\nSeparator", C["ltblue"]),
        (5.5, 3, "Turbo-\nExpander", C["ltorange"]),
        (5.5, 1, "J-T\nValve", C["ltgreen"]),
        (8.5, 2, "Demethanizer\nColumn", C["ltblue"]),
        (8.5, 4, "Recompressor", C["ltorange"]),
    ]
    for x, y, label, color in units:
        ax.add_patch(FancyBboxPatch((x, y), 2, 1.0, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor=C["gray"]))
        ax.text(x+1, y+0.5, label, ha="center", va="center", fontsize=7.5, fontweight="bold")
    connections = [(0,1), (1,2), (1,3), (2,4), (3,4)]
    for i,j in connections:
        x1 = units[i][0]+2; y1 = units[i][1]+0.5
        x2 = units[j][0]; y2 = units[j][1]+0.5
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=C["blue"], lw=1.2))
    # Shaft connection expander-recompressor
    ax.plot([6.5, 9.5], [4, 4], color=C["orange"], linewidth=2, linestyle="-.")
    ax.text(8, 4.5, "Shaft", fontsize=8, color=C["orange"])
    ax.set_title("Turboexpander NGL Recovery Process", fontsize=11, fontweight="bold", pad=5)
    savefig("ch22_onshore_processing_plants", "ch22_turboexpander_pfd.png", fig)


def ch22o_ngl_sensitivity():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    T_exp = np.linspace(-60, -10, 100)  # expander outlet temp
    C2_recovery = 100 / (1 + np.exp(0.15*(T_exp + 30)))
    C3_recovery = 100 / (1 + np.exp(0.2*(T_exp + 15)))
    ax.plot(T_exp, C2_recovery, color=C["blue"], linewidth=2.5, label="C2 Recovery")
    ax.plot(T_exp, C3_recovery, color=C["red"], linewidth=2.5, linestyle="--", label="C3 Recovery")
    ax.axvline(x=-35, color=C["green"], linestyle=":", label="Design T = -35°C")
    ax.set_xlabel("Expander Outlet Temperature (°C)")
    ax.set_ylabel("Recovery (%)")
    ax.set_title("NGL Recovery Sensitivity to Expander Temperature", fontweight="bold")
    ax.legend(loc="center right", fontsize=8)
    add_watermark(ax)
    savefig("ch22_onshore_processing_plants", "ch22_ngl_sensitivity.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating figures for chapters 16-22...")
    funcs = [v for k, v in sorted(globals().items()) if k.startswith("ch") and callable(v)]
    for fn in funcs:
        try:
            fn()
        except Exception as e:
            print(f"  [FAIL] {fn.__name__}: {e}")
    print(f"Done. Generated {len(funcs)} figures.")
