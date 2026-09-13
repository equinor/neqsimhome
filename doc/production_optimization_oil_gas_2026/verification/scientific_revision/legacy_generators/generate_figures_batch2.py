#!/usr/bin/env python3
"""Generate all figures for chapters 9-15 (17 figures)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from generate_figures_style import apply_style, savefig, C, PALETTE, add_watermark

apply_style()

# ═══════════════════════════════════════════════════════════════════
# Chapter 9: Separation Technology (4 figures)
# ═══════════════════════════════════════════════════════════════════

def ch09_three_stage_separation():
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.set_xlim(0, 14); ax.set_ylim(0, 5); ax.axis("off")
    stages = [
        (0.5, 2.0, "HP Sep\n70 bara", C["ltblue"]),
        (4.0, 2.0, "MP Sep\n20 bara", C["ltblue"]),
        (7.5, 2.0, "LP Sep\n3 bara", C["ltblue"]),
        (11.0, 3.5, "Gas\nCompression", C["ltorange"]),
        (11.0, 0.5, "Oil\nExport", C["ltgreen"]),
    ]
    for x, y, label, color in stages:
        ax.add_patch(FancyBboxPatch((x, y), 2.3, 1.2, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor=C["gray"]))
        ax.text(x+1.15, y+0.6, label, ha="center", va="center", fontsize=8, fontweight="bold")
    # Gas lines (top)
    for i in range(3):
        x = stages[i][0] + 1.15
        ax.annotate("", xy=(11, 4.1), xytext=(x, 3.2),
                    arrowprops=dict(arrowstyle="->", color=C["orange"], lw=1.2))
    # Oil lines (bottom)
    for i in range(2):
        ax.annotate("", xy=(stages[i+1][0], 2.6), xytext=(stages[i][0]+2.3, 2.6),
                    arrowprops=dict(arrowstyle="->", color=C["green"], lw=1.5))
    ax.annotate("", xy=(11, 1.1), xytext=(9.8, 2.6),
                arrowprops=dict(arrowstyle="->", color=C["green"], lw=1.5))
    ax.text(6, 4.3, "Gas", fontsize=9, color=C["orange"], fontweight="bold")
    ax.text(6, 1.2, "Oil", fontsize=9, color=C["green"], fontweight="bold")
    ax.set_title("Three-Stage Separation System", fontsize=11, fontweight="bold", pad=10)
    savefig("ch09_separation_technology", "three_stage_separation.png", fig)


def ch09_horizontal_two_phase_separator():
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
    # Vessel body
    from matplotlib.patches import Ellipse
    ax.add_patch(plt.Rectangle((1, 1.5), 7, 2.5, facecolor=C["ltblue"], edgecolor=C["blue"], linewidth=2))
    ax.add_patch(Ellipse((1, 2.75), 0.6, 2.5, facecolor=C["ltblue"], edgecolor=C["blue"], linewidth=2))
    ax.add_patch(Ellipse((8, 2.75), 0.6, 2.5, facecolor=C["ltblue"], edgecolor=C["blue"], linewidth=2))
    # Liquid level
    ax.fill_between([1, 8], 1.5, 2.8, color=C["ltgreen"], alpha=0.5)
    ax.axhline(y=2.8, xmin=0.1, xmax=0.8, color=C["green"], linewidth=1.5, linestyle="--")
    # Labels
    ax.text(4.5, 3.4, "Gas Phase", fontsize=9, ha="center", color=C["orange"])
    ax.text(4.5, 2.2, "Liquid Phase", fontsize=9, ha="center", color=C["green"])
    # Inlet
    ax.annotate("Inlet", xy=(1.5, 3.3), xytext=(0, 4.2),
                fontsize=8, arrowprops=dict(arrowstyle="->", color=C["blue"]))
    # Outlets
    ax.annotate("Gas Out", xy=(7.5, 4.0), xytext=(8.5, 4.5),
                fontsize=8, arrowprops=dict(arrowstyle="->", color=C["orange"]))
    ax.annotate("Liquid Out", xy=(7, 1.5), xytext=(8.5, 0.8),
                fontsize=8, arrowprops=dict(arrowstyle="->", color=C["green"]))
    # Demister
    ax.add_patch(plt.Rectangle((5.5, 2.9), 0.15, 1.0, facecolor=C["gray"], alpha=0.5))
    ax.text(5.8, 3.4, "Demister", fontsize=7, rotation=90, va="center")
    # Weir
    ax.add_patch(plt.Rectangle((6.5, 1.5), 0.1, 1.3, facecolor=C["black"]))
    ax.text(6.3, 1.3, "Weir", fontsize=7, ha="center")
    ax.set_title("Horizontal Two-Phase Separator", fontsize=11, fontweight="bold", pad=10)
    savefig("ch09_separation_technology", "horizontal_two_phase_separator.png", fig)


def ch09_separator_pressure_optimization():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    P_hp = np.linspace(30, 100, 100)
    # Oil recovery vs HP separator pressure
    recovery = -0.002*(P_hp - 60)**2 + 95
    GOR = 80 + 0.5*P_hp + 0.01*P_hp**2
    ax.plot(P_hp, recovery, color=C["blue"], linewidth=2.5, label="Oil Recovery (%)")
    ax2 = ax.twinx()
    ax2.plot(P_hp, GOR, color=C["red"], linewidth=2, linestyle="--", label="GOR (Sm³/Sm³)")
    ax2.set_ylabel("GOR (Sm³/Sm³)", color=C["red"])
    ax2.tick_params(axis="y", labelcolor=C["red"])
    ax.axvline(x=60, color=C["green"], linestyle=":", linewidth=1.5)
    ax.text(62, 88, "Optimal\nPressure", fontsize=8, color=C["green"])
    ax.set_xlabel("HP Separator Pressure (bara)")
    ax.set_ylabel("Oil Recovery (%)", color=C["blue"])
    ax.tick_params(axis="y", labelcolor=C["blue"])
    ax.set_title("Separator Pressure Optimization", fontweight="bold")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1+lines2, labels1+labels2, loc="lower left", fontsize=8)
    add_watermark(ax)
    savefig("ch09_separation_technology", "separator_pressure_optimization.png", fig)


def ch09_separator_utilization_profile():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    years = np.arange(2024, 2045)
    # Simulated production profile
    Q_oil = 25000 * np.exp(-0.08*(years-2024)) * (1 - np.exp(-0.5*(years-2024)))
    Q_water = 5000 * (1 - np.exp(-0.15*(years-2024)))
    Q_total = Q_oil + Q_water
    capacity = 30000
    util = Q_total / capacity * 100
    ax.fill_between(years, 0, Q_oil/1000, color=C["green"], alpha=0.6, label="Oil")
    ax.fill_between(years, Q_oil/1000, Q_total/1000, color=C["ltblue"], alpha=0.6, label="Water")
    ax.axhline(y=capacity/1000, color=C["red"], linewidth=2, linestyle="--", label="Separator capacity")
    ax.set_xlabel("Year")
    ax.set_ylabel("Liquid Rate (kSm³/d)")
    ax.set_title("Separator Utilization Over Field Life", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_xlim(2024, 2044)
    add_watermark(ax)
    savefig("ch09_separation_technology", "separator_utilization_profile.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 10: Oil Processing (2 figures)
# ═══════════════════════════════════════════════════════════════════

def ch10_oil_processing_train_overview():
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.set_xlim(0, 14); ax.set_ylim(0, 5); ax.axis("off")
    units = [
        (0.3, 2, "HP Sep\n(70 bara)", C["ltblue"]),
        (3.0, 2, "MP Sep\n(20 bara)", C["ltblue"]),
        (5.7, 2, "LP Sep\n(3 bara)", C["ltblue"]),
        (8.4, 2, "Electrostatic\nCoalescer", C["ltorange"]),
        (11.1, 2, "Export\nPump", C["ltgreen"]),
    ]
    for x, y, label, color in units:
        ax.add_patch(FancyBboxPatch((x, y), 2.3, 1.2, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor=C["gray"]))
        ax.text(x+1.15, y+0.6, label, ha="center", va="center", fontsize=7.5, fontweight="bold")
    for i in range(len(units)-1):
        ax.annotate("", xy=(units[i+1][0], 2.6), xytext=(units[i][0]+2.3, 2.6),
                    arrowprops=dict(arrowstyle="->", color=C["blue"], lw=1.5))
    # Labels
    ax.text(0.3, 4.2, "From\nWell", fontsize=8, color=C["gray"])
    ax.annotate("", xy=(0.3, 2.6), xytext=(0.3, 3.8),
                arrowprops=dict(arrowstyle="->", color=C["gray"], lw=1.2))
    ax.set_title("Oil Processing Train", fontsize=11, fontweight="bold", pad=10)
    savefig("ch10_oil_processing", "oil_processing_train_overview.png", fig)


def ch10_mp_pressure_optimization():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    P_mp = np.linspace(5, 40, 100)
    oil_recovery = -0.005*(P_mp - 18)**2 + 96.5
    compression_power = 2.0 + 0.08*P_mp + 0.003*(40-P_mp)**1.5
    ax.plot(P_mp, oil_recovery, color=C["blue"], linewidth=2.5, label="Oil Recovery (%)")
    ax2 = ax.twinx()
    ax2.plot(P_mp, compression_power, color=C["red"], linewidth=2, linestyle="--", label="Compression Power (MW)")
    ax2.set_ylabel("Compression Power (MW)", color=C["red"])
    ax.axvline(x=18, color=C["green"], linestyle=":", linewidth=1.5)
    ax.text(20, 94, "Optimal P_MP", fontsize=8, color=C["green"])
    ax.set_xlabel("MP Separator Pressure (bara)")
    ax.set_ylabel("Oil Recovery (%)", color=C["blue"])
    ax.set_title("MP Stage Pressure Optimization", fontweight="bold")
    lines1, l1 = ax.get_legend_handles_labels()
    lines2, l2 = ax2.get_legend_handles_labels()
    ax.legend(lines1+lines2, l1+l2, loc="center right", fontsize=8)
    add_watermark(ax)
    savefig("ch10_oil_processing", "mp_pressure_optimization.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 11: Gas Processing (2 figures)
# ═══════════════════════════════════════════════════════════════════

def ch11_gas_processing_overview():
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.set_xlim(0, 14); ax.set_ylim(0, 5); ax.axis("off")
    units = [
        (0.3, 2, "Inlet\nScrubber", C["ltblue"]),
        (3.0, 2, "Gas\nDehydration\n(TEG)", C["ltorange"]),
        (5.7, 2, "NGL\nRecovery", C["ltgreen"]),
        (8.4, 2, "Gas\nSweetening", C["ltblue"]),
        (11.1, 2, "Sales Gas\nCompression", C["ltorange"]),
    ]
    for x, y, label, color in units:
        ax.add_patch(FancyBboxPatch((x, y), 2.3, 1.2, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor=C["gray"]))
        ax.text(x+1.15, y+0.6, label, ha="center", va="center", fontsize=7.5, fontweight="bold")
    for i in range(len(units)-1):
        ax.annotate("", xy=(units[i+1][0], 2.6), xytext=(units[i][0]+2.3, 2.6),
                    arrowprops=dict(arrowstyle="->", color=C["blue"], lw=1.5))
    ax.set_title("Gas Processing Plant Overview", fontsize=11, fontweight="bold", pad=10)
    savefig("ch11_gas_processing", "gas_processing_overview.png", fig)


def ch11_phase_envelope_gas():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    # Lean gas phase envelope (narrow)
    theta = np.linspace(0, 2*np.pi, 300)
    r = 0.7 + 0.3*np.cos(theta)
    T = -40 + 80*r*np.cos(theta-0.3)
    P = 50 + 40*r*np.sin(theta)
    ax.plot(T, P, color=C["blue"], linewidth=2.5, label="Lean gas")
    # Rich gas (wider)
    r2 = 1.0 + 0.4*np.cos(theta)
    T2 = -20 + 100*r2*np.cos(theta-0.2)
    P2 = 55 + 50*r2*np.sin(theta)
    ax.plot(T2, P2, color=C["red"], linewidth=2, linestyle="--", label="Rich gas")
    # Export spec point
    ax.plot(-10, 70, "D", color=C["green"], markersize=10, label="Export condition")
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Pressure (bara)")
    ax.set_title("Phase Envelopes: Lean vs Rich Gas", fontweight="bold")
    ax.legend(loc="upper right")
    add_watermark(ax)
    savefig("ch11_gas_processing", "phase_envelope_gas.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 12: Gas Compression (3 figures)
# ═══════════════════════════════════════════════════════════════════

def ch12_compression_pr_sensitivity():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    n_stages = np.array([1, 2, 3, 4, 5])
    PR_total = 10  # overall ratio
    for PR, color, label in [(5, C["blue"], "PR=5"), (10, C["red"], "PR=10"), (20, C["green"], "PR=20")]:
        PR_per_stage = PR**(1.0/n_stages)
        T_discharge = 40 + 100*(PR_per_stage**0.3 - 1)  # simplified polytropic
        power = n_stages * 2.5 * (PR_per_stage**0.28 - 1)
        ax.plot(n_stages, power, "o-", color=color, linewidth=2, markersize=7, label=f"Total PR = {PR}")
    ax.set_xlabel("Number of Compression Stages")
    ax.set_ylabel("Specific Power (kW per kg/s)")
    ax.set_title("Compression Power vs Number of Stages", fontweight="bold")
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.legend(loc="upper right")
    add_watermark(ax)
    savefig("ch12_gas_compression", "compression_pr_sensitivity.png", fig)


def ch12_compressor_performance_map():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Q = np.linspace(2000, 12000, 200)
    # Speed lines
    for N, color in [(9000, C["blue"]), (10000, C["teal"]), (11000, C["green"]), (12000, C["orange"]), (13000, C["red"])]:
        PR = 0.5 + (N/10000)**2 * (3.5 - 0.00003*(Q - 7000*N/10000)**2/1e6)
        PR = np.clip(PR, 1.0, 5.0)
        valid = (PR > 1.05) & (Q < N*1.1)
        ax.plot(Q[valid], PR[valid], color=color, linewidth=1.5, label=f"{N} rpm")
    # Surge line
    Q_surge = np.array([2500, 3000, 3500, 4200, 5000])
    PR_surge = np.array([1.5, 2.0, 2.5, 3.2, 4.0])
    ax.plot(Q_surge, PR_surge, "k--", linewidth=2, label="Surge line")
    ax.fill_betweenx([1, 5], 0, 3500, color=C["ltred"], alpha=0.2)
    ax.text(2000, 3.5, "Surge\nRegion", fontsize=9, color=C["red"], fontweight="bold")
    # Efficiency contours
    ax.set_xlabel("Volume Flow (Am³/h)")
    ax.set_ylabel("Pressure Ratio")
    ax.set_title("Centrifugal Compressor Performance Map", fontweight="bold")
    ax.legend(loc="upper right", fontsize=7, ncol=2)
    ax.set_xlim(1500, 13000); ax.set_ylim(1.0, 4.5)
    add_watermark(ax)
    savefig("ch12_gas_compression", "compressor_performance_map.png", fig)


def ch12_compressor_speed_sensitivity():
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 4))
    speeds = [0.85, 0.90, 0.95, 1.00, 1.05]
    Q_base = 8000
    # Head vs flow
    for s, color in zip(speeds, PALETTE):
        Q = np.linspace(3000*s, 12000*s, 100)
        H = 80*s**2 * (1 - 0.3*((Q/(Q_base*s))-1)**2)
        H = np.clip(H, 0, None)
        axes[0].plot(Q, H, color=color, linewidth=1.5, label=f"N/N₀ = {s:.2f}")
    axes[0].set_xlabel("Volume Flow (Am³/h)")
    axes[0].set_ylabel("Polytropic Head (kJ/kg)")
    axes[0].set_title("Head vs Flow", fontweight="bold")
    axes[0].legend(fontsize=7)
    # Efficiency vs flow
    for s, color in zip(speeds, PALETTE):
        Q = np.linspace(3000*s, 12000*s, 100)
        eta = 0.82 * (1 - 2*((Q/(Q_base*s))-1)**2)
        eta = np.clip(eta, 0.5, None)
        axes[1].plot(Q, eta*100, color=color, linewidth=1.5)
    axes[1].set_xlabel("Volume Flow (Am³/h)")
    axes[1].set_ylabel("Polytropic Efficiency (%)")
    axes[1].set_title("Efficiency vs Flow", fontweight="bold")
    fig.tight_layout()
    savefig("ch12_gas_compression", "compressor_speed_sensitivity.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 13: Compressor Characteristics (3 figures)
# ═══════════════════════════════════════════════════════════════════

def ch13_compressor_map_overview():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Q = np.linspace(2000, 14000, 300)
    for N, color in [(8500, C["blue"]), (10000, C["green"]), (11500, C["orange"]), (13000, C["red"])]:
        Qn = Q * 10000/N
        H = (N/10000)**2 * 90 * (1 - 0.5*((Qn/8000)-1)**2)
        H = np.clip(H, 0, None)
        mask = H > 5
        ax.plot(Q[mask], H[mask], color=color, linewidth=2, label=f"{N} rpm")
    # Surge and stonewall
    ax.axvline(x=3000, color=C["gray"], linewidth=1.5, linestyle=":", label="Surge limit")
    ax.axvline(x=13500, color=C["gray"], linewidth=1.5, linestyle="--")
    ax.text(13200, 70, "Stonewall", fontsize=8, rotation=90, color=C["gray"])
    ax.set_xlabel("Volume Flow (Am³/h)")
    ax.set_ylabel("Polytropic Head (kJ/kg)")
    ax.set_title("Compressor Characteristic Map", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    add_watermark(ax)
    savefig("ch13_compressor_characteristics", "compressor_map_overview.png", fig)


def ch13_operating_envelope():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    # Operating envelope
    Q_min = np.array([3000, 3500, 4000, 4500, 5200])
    Q_max = np.array([10000, 11000, 12000, 12500, 12800])
    P_ratio = np.array([1.5, 2.0, 2.5, 3.0, 3.5])
    ax.fill_betweenx(P_ratio, Q_min, Q_max, color=C["ltgreen"], alpha=0.4, label="Operating envelope")
    ax.plot(Q_min, P_ratio, color=C["red"], linewidth=2.5, label="Surge line")
    ax.plot(Q_max, P_ratio, color=C["blue"], linewidth=2, linestyle="--", label="Choke/stonewall")
    # Design point
    ax.plot(7500, 2.5, "D", color=C["green"], markersize=12, zorder=5, label="Design point")
    # Current operating point
    ax.plot(6000, 2.8, "*", color=C["orange"], markersize=14, zorder=5, label="Current operation")
    ax.set_xlabel("Volume Flow (Am³/h)")
    ax.set_ylabel("Pressure Ratio")
    ax.set_title("Compressor Operating Envelope", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    add_watermark(ax)
    savefig("ch13_compressor_characteristics", "operating_envelope.png", fig)


def ch13_compressor_map_complete():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5))
    Q = np.linspace(3000, 13000, 200)
    # Left: Head-flow with efficiency contours
    for N, color in [(9000, C["blue"]), (10500, C["green"]), (12000, C["red"])]:
        Qn = Q * 10000/N
        H = (N/10000)**2 * 85 * (1 - 0.4*((Qn/7500)-1)**2)
        H = np.clip(H, 5, None)
        mask = H > 5
        ax1.plot(Q[mask], H[mask], color=color, linewidth=2, label=f"{N} rpm")
    ax1.set_xlabel("Volume Flow (Am³/h)")
    ax1.set_ylabel("Polytropic Head (kJ/kg)")
    ax1.set_title("Head-Flow Curves", fontweight="bold")
    ax1.legend(fontsize=7)
    # Right: Power-flow
    for N, color in [(9000, C["blue"]), (10500, C["green"]), (12000, C["red"])]:
        Qn = Q * 10000/N
        P_kw = (N/10000)**3 * 5000 * (0.3 + 0.7*Q/10000)
        ax2.plot(Q, P_kw/1000, color=color, linewidth=2, label=f"{N} rpm")
    ax2.set_xlabel("Volume Flow (Am³/h)")
    ax2.set_ylabel("Shaft Power (MW)")
    ax2.set_title("Power-Flow Curves", fontweight="bold")
    ax2.legend(fontsize=7)
    fig.tight_layout()
    savefig("ch13_compressor_characteristics", "compressor_map_complete.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 14: Heat Exchangers (2 figures)
# ═══════════════════════════════════════════════════════════════════

def ch14_shell_tube_hx_cross_section():
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_aspect("equal"); ax.axis("off")
    # Shell
    shell = plt.Circle((0, 0), 2.5, fill=False, edgecolor=C["blue"], linewidth=3)
    ax.add_patch(shell)
    ax.text(0, 2.8, "Shell", fontsize=9, ha="center", color=C["blue"], fontweight="bold")
    # Tubes
    tube_positions = []
    for row in range(-2, 3):
        n_tubes = 5 - abs(row)
        for col in range(n_tubes):
            x = (col - (n_tubes-1)/2) * 0.7
            y = row * 0.6
            if x**2 + y**2 < 4.5:
                tube = plt.Circle((x, y), 0.15, facecolor=C["ltorange"], edgecolor=C["orange"], linewidth=0.8)
                ax.add_patch(tube)
                tube_positions.append((x, y))
    # Baffles
    for bx in [-1.5, 0, 1.5]:
        ax.plot([bx, bx], [-2, 1.5], color=C["gray"], linewidth=2, alpha=0.5)
    ax.text(0, -2.8, f"{len(tube_positions)} tubes shown", fontsize=8, ha="center", color=C["gray"])
    ax.annotate("Baffle", xy=(0, 1.2), xytext=(2, 1.8), fontsize=8,
                arrowprops=dict(arrowstyle="->", color=C["gray"]))
    ax.set_title("Shell-and-Tube Heat Exchanger Cross Section", fontsize=11, fontweight="bold", pad=10)
    savefig("ch14_heat_exchangers", "shell_tube_hx_cross_section.png", fig)


def ch14_composite_curves():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    # Hot composite curve
    Q_hot = np.array([0, 2, 4, 6, 8, 10, 12])
    T_hot = np.array([200, 180, 150, 130, 100, 80, 60])
    # Cold composite curve
    Q_cold = np.array([0, 2, 4, 6, 8, 10, 12])
    T_cold = np.array([30, 55, 80, 105, 120, 140, 160])
    ax.plot(Q_hot, T_hot, color=C["red"], linewidth=2.5, marker="o", markersize=5, label="Hot composite")
    ax.plot(Q_cold, T_cold, color=C["blue"], linewidth=2.5, marker="s", markersize=5, label="Cold composite")
    # Pinch point
    idx_pinch = 3
    ax.annotate("Pinch Point\nΔT_min = 25°C", xy=(Q_hot[idx_pinch], T_hot[idx_pinch]),
                xytext=(8, 145), fontsize=9, arrowprops=dict(arrowstyle="->", color=C["green"]))
    ax.fill_between(Q_hot, T_cold, T_hot, color=C["ltorange"], alpha=0.2)
    ax.set_xlabel("Heat Duty (MW)")
    ax.set_ylabel("Temperature (°C)")
    ax.set_title("Composite Curves — Heat Integration", fontweight="bold")
    ax.legend(loc="lower right")
    add_watermark(ax)
    savefig("ch14_heat_exchangers", "composite_curves.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 15: Valves and Flow Control (1 figure)
# ═══════════════════════════════════════════════════════════════════

def ch15_valve_characteristics_curves():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    travel = np.linspace(0, 100, 200)
    # Linear
    Cv_linear = travel / 100
    # Equal percentage
    R = 50
    Cv_eq = R**((travel/100) - 1)
    # Quick opening
    Cv_quick = np.sqrt(travel/100)
    ax.plot(travel, Cv_linear*100, color=C["blue"], linewidth=2.5, label="Linear")
    ax.plot(travel, Cv_eq*100, color=C["red"], linewidth=2.5, linestyle="--", label="Equal Percentage (R=50)")
    ax.plot(travel, Cv_quick*100, color=C["green"], linewidth=2.5, linestyle="-.", label="Quick Opening")
    ax.set_xlabel("Valve Travel (%)")
    ax.set_ylabel("Flow Capacity, Cv/Cv_max (%)")
    ax.set_title("Valve Inherent Characteristics", fontweight="bold")
    ax.legend(loc="upper left")
    ax.set_xlim(0, 100); ax.set_ylim(0, 105)
    add_watermark(ax)
    savefig("ch15_valves_and_flow_control", "valve_characteristics_curves.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating figures for chapters 9-15...")
    funcs = [v for k, v in sorted(globals().items()) if k.startswith("ch") and callable(v)]
    for fn in funcs:
        try:
            fn()
        except Exception as e:
            print(f"  [FAIL] {fn.__name__}: {e}")
    print(f"Done. Generated {len(funcs)} figures.")
