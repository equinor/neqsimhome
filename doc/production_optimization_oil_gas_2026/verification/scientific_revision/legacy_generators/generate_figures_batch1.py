#!/usr/bin/env python3
"""Generate all figures for chapters 1-8 (31 figures)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from generate_figures_style import apply_style, savefig, C, PALETTE, add_watermark

apply_style()

# ═══════════════════════════════════════════════════════════════════
# Chapter 1: Introduction (3 figures)
# ═══════════════════════════════════════════════════════════════════

def ch01_production_system_schematic():
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5)
    ax.set_aspect("equal"); ax.axis("off")
    boxes = [
        (0.3, 2.0, "Reservoir"),
        (2.2, 2.0, "Wells"),
        (4.0, 2.0, "Subsea\nFlowlines"),
        (5.8, 2.0, "Risers"),
        (7.6, 2.0, "Topside\nProcessing"),
        (7.6, 0.3, "Export\nPipeline"),
    ]
    for x, y, label in boxes:
        ax.add_patch(FancyBboxPatch((x, y), 1.5, 1.0, boxstyle="round,pad=0.1",
                     facecolor=C["ltblue"], edgecolor=C["blue"], linewidth=1.2))
        ax.text(x + 0.75, y + 0.5, label, ha="center", va="center", fontsize=8, fontweight="bold")
    for i in range(4):
        x1 = boxes[i][0] + 1.5; x2 = boxes[i+1][0]
        ax.annotate("", xy=(x2, 2.5), xytext=(x1, 2.5),
                    arrowprops=dict(arrowstyle="->", color=C["blue"], lw=1.5))
    ax.annotate("", xy=(8.35, 1.3), xytext=(8.35, 2.0),
                arrowprops=dict(arrowstyle="->", color=C["green"], lw=1.5))
    ax.set_title("Integrated Production System Overview", fontsize=11, fontweight="bold", pad=10)
    add_watermark(ax)
    savefig("ch01_introduction", "production_system_schematic.png", fig)


def ch01_topside_process_schematic():
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.set_xlim(0, 12); ax.set_ylim(0, 6)
    ax.set_aspect("equal"); ax.axis("off")
    units = [
        (0.5, 3.0, "Inlet\nSeparator", C["ltblue"]),
        (2.8, 4.2, "HP\nSeparator", C["ltblue"]),
        (2.8, 1.8, "LP\nSeparator", C["ltblue"]),
        (5.5, 4.2, "Gas\nCompression", C["ltorange"]),
        (5.5, 1.8, "Oil\nStabilization", C["ltgreen"]),
        (8.2, 4.2, "Gas\nDehydration", C["ltorange"]),
        (8.2, 1.8, "Oil Export\nPumping", C["ltgreen"]),
        (10.5, 4.2, "Gas\nExport", C["ltorange"]),
        (10.5, 1.8, "Oil\nExport", C["ltgreen"]),
    ]
    for x, y, label, color in units:
        ax.add_patch(FancyBboxPatch((x, y), 1.8, 1.0, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor=C["gray"], linewidth=1.0))
        ax.text(x + 0.9, y + 0.5, label, ha="center", va="center", fontsize=7, fontweight="bold")
    connections = [
        (0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6), (5, 7), (6, 8)
    ]
    for i, j in connections:
        x1 = units[i][0] + 1.8; y1 = units[i][1] + 0.5
        x2 = units[j][0]; y2 = units[j][1] + 0.5
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=C["gray"], lw=1.0))
    ax.set_title("Topside Process Schematic", fontsize=11, fontweight="bold", pad=10)
    add_watermark(ax)
    savefig("ch01_introduction", "topside_process_schematic.png", fig)


def ch01_optimization_workflow():
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.set_xlim(0, 8); ax.set_ylim(0, 8)
    ax.axis("off")
    steps = [
        (4, 7.0, "Define Objective\nFunction", C["blue"]),
        (4, 5.5, "Build Process\nModel (NeqSim)", C["green"]),
        (4, 4.0, "Identify Decision\nVariables", C["orange"]),
        (4, 2.5, "Run Optimization\nAlgorithm", C["purple"]),
        (4, 1.0, "Validate &\nImplement", C["red"]),
    ]
    for x, y, label, color in steps:
        ax.add_patch(FancyBboxPatch((x-1.2, y-0.45), 2.4, 0.9, boxstyle="round,pad=0.12",
                     facecolor=color, edgecolor="white", alpha=0.85, linewidth=1.5))
        ax.text(x, y, label, ha="center", va="center", fontsize=9, fontweight="bold", color="white")
    for i in range(len(steps)-1):
        ax.annotate("", xy=(4, steps[i+1][1]+0.45), xytext=(4, steps[i][1]-0.45),
                    arrowprops=dict(arrowstyle="-|>", color=C["gray"], lw=1.8))
    ax.annotate("", xy=(6.5, steps[0][1]), xytext=(6.5, steps[-1][1]),
                arrowprops=dict(arrowstyle="-|>", color=C["teal"], lw=1.2, linestyle="--"))
    ax.text(6.7, 4.0, "Iterate", fontsize=8, color=C["teal"], rotation=90, va="center")
    ax.set_title("Production Optimization Workflow", fontsize=11, fontweight="bold", pad=10)
    savefig("ch01_introduction", "optimization_workflow.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 2: Thermodynamic Foundations (2 figures)
# ═══════════════════════════════════════════════════════════════════

def ch02_phase_envelope():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    # Typical gas-condensate phase envelope
    T_bp = np.array([-80, -60, -40, -20, 0, 20, 40, 60, 80, 100, 120, 130])
    P_bp = np.array([5, 15, 30, 52, 78, 108, 140, 170, 192, 200, 180, 150])
    T_dp = np.array([130, 140, 155, 170, 185, 200, 210, 218, 220, 218, 210, 195, 170, 150, 130])
    P_dp = np.array([150, 170, 200, 240, 280, 310, 335, 350, 355, 350, 335, 310, 280, 240, 150])
    ax.plot(T_bp, P_bp, color=C["blue"], linewidth=2, label="Bubble point")
    ax.plot(T_dp, P_dp, color=C["red"], linewidth=2, label="Dew point")
    # Cricondentherm and cricondenbar
    ax.plot(220, 355, "ko", markersize=8)
    ax.annotate("Cricondenbar", xy=(220, 355), xytext=(160, 380),
                fontsize=8, arrowprops=dict(arrowstyle="->", color=C["black"]))
    ax.plot(220, 355, "ko", markersize=8)
    # Critical point
    ax.plot(130, 150, "s", color=C["purple"], markersize=8, zorder=5)
    ax.annotate("Critical\nPoint", xy=(130, 150), xytext=(80, 180),
                fontsize=8, arrowprops=dict(arrowstyle="->", color=C["purple"]))
    # Regions
    ax.text(20, 50, "Liquid\nRegion", fontsize=9, color=C["blue"], ha="center", style="italic")
    ax.text(200, 150, "Gas\nRegion", fontsize=9, color=C["red"], ha="center", style="italic")
    ax.text(150, 250, "Two-Phase\nRegion", fontsize=9, color=C["gray"], ha="center", style="italic")
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Pressure (bara)")
    ax.set_title("Phase Envelope for a Gas-Condensate System", fontweight="bold")
    ax.legend(loc="upper left", framealpha=0.9)
    ax.set_xlim(-100, 250); ax.set_ylim(0, 420)
    add_watermark(ax)
    savefig("ch02_thermodynamic_foundations", "phase_envelope.png", fig)


def ch02_eos_comparison():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    P = np.linspace(1, 300, 100)
    # Simulated compressibility factor curves
    Z_srk = 1 - 0.003*P + 8e-6*P**2
    Z_pr = 1 - 0.0028*P + 7.5e-6*P**2
    Z_cpa = 1 - 0.0032*P + 8.5e-6*P**2
    Z_exp = 1 - 0.0029*P + 7.8e-6*P**2 + np.random.normal(0, 0.005, len(P))
    ax.plot(P, Z_srk, color=C["blue"], linewidth=2, label="SRK EOS")
    ax.plot(P, Z_pr, color=C["red"], linewidth=2, linestyle="--", label="PR EOS")
    ax.plot(P, Z_cpa, color=C["green"], linewidth=2, linestyle="-.", label="CPA EOS")
    ax.scatter(P[::10], Z_exp[::10], color=C["orange"], s=25, zorder=5, label="Experimental", marker="o", edgecolors=C["black"], linewidth=0.5)
    ax.set_xlabel("Pressure (bara)")
    ax.set_ylabel("Compressibility Factor, Z")
    ax.set_title("Equation of State Comparison — Natural Gas", fontweight="bold")
    ax.legend(loc="lower right", framealpha=0.9)
    ax.set_ylim(0.6, 1.05)
    add_watermark(ax)
    savefig("ch02_thermodynamic_foundations", "eos_comparison.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 3: Fluid Characterization (4 figures)
# ═══════════════════════════════════════════════════════════════════

def ch03_fluid_characterization_workflow():
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis("off")
    steps = [
        (5, 7.0, "PVT Lab\nSampling", C["blue"]),
        (2, 5.2, "Compositional\nAnalysis", C["green"]),
        (8, 5.2, "C7+ Fraction\nCharacterization", C["green"]),
        (5, 3.5, "EOS Model\nSelection & Tuning", C["orange"]),
        (2, 1.7, "Property\nPrediction", C["purple"]),
        (8, 1.7, "Validation vs\nLab Data", C["red"]),
    ]
    for x, y, label, color in steps:
        ax.add_patch(FancyBboxPatch((x-1.3, y-0.5), 2.6, 1.0, boxstyle="round,pad=0.12",
                     facecolor=color, edgecolor="white", alpha=0.85, linewidth=1.5))
        ax.text(x, y, label, ha="center", va="center", fontsize=8.5, fontweight="bold", color="white")
    arrows = [(0,1), (0,2), (1,3), (2,3), (3,4), (3,5), (5,3)]
    for i,j in arrows:
        ls = "--" if (i,j)==(5,3) else "-"
        ax.annotate("", xy=(steps[j][0], steps[j][1]+0.5), xytext=(steps[i][0], steps[i][1]-0.5),
                    arrowprops=dict(arrowstyle="-|>", color=C["gray"], lw=1.2, linestyle=ls))
    ax.set_title("Fluid Characterization Workflow", fontsize=11, fontweight="bold")
    savefig("ch03_fluid_characterization", "fluid_characterization_workflow.png", fig)


def ch03_fluid_type_phase_envelopes():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    t = np.linspace(0, 1, 200)
    fluids = {
        "Dry Gas":       (t*300-100, 200*np.sin(np.pi*t)**0.8, C["blue"]),
        "Gas Condensate": (t*350-80,  350*np.sin(np.pi*t)**0.7, C["teal"]),
        "Volatile Oil":  (t*400-40,   380*np.sin(np.pi*t)**0.6, C["orange"]),
        "Black Oil":     (t*500+0,    300*np.sin(np.pi*t)**0.5, C["red"]),
    }
    for name, (T, P, color) in fluids.items():
        ax.plot(T, P, color=color, linewidth=2, label=name)
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Pressure (bara)")
    ax.set_title("Phase Envelopes by Fluid Type", fontweight="bold")
    ax.legend(loc="upper right", framealpha=0.9)
    ax.set_xlim(-120, 500); ax.set_ylim(0, 420)
    add_watermark(ax)
    savefig("ch03_fluid_characterization", "fluid_type_phase_envelopes.png", fig)


def ch03_gas_condensate_phase_envelope():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    theta = np.linspace(0, 2*np.pi, 200)
    # Asymmetric envelope for gas condensate
    r = 1 + 0.6*np.cos(theta)
    T = 100 + 100*r*np.cos(theta)
    P = 200 + 180*r*np.sin(theta)
    ax.plot(T, P, color=C["blue"], linewidth=2)
    # Quality lines
    for q, alpha_val in zip([0.9, 0.7, 0.5], [0.3, 0.5, 0.7]):
        T_q = 100 + (100*r*np.cos(theta))*q
        P_q = 200 + (180*r*np.sin(theta))*q
        ax.plot(T_q, P_q, color=C["gray"], linewidth=0.8, alpha=alpha_val)
        idx = len(T_q)//4
        ax.text(T_q[idx], P_q[idx], f"{int(q*100)}%", fontsize=7, color=C["gray"])
    # Operating path
    T_op = np.linspace(80, 40, 20)
    P_op = np.linspace(350, 100, 20)
    ax.plot(T_op, P_op, "k--", linewidth=1.5, label="Depletion path")
    ax.plot(T_op[0], P_op[0], "ko", markersize=6)
    ax.text(T_op[0]+5, P_op[0]+10, "Initial\nconditions", fontsize=7)
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Pressure (bara)")
    ax.set_title("Gas-Condensate Phase Envelope with Quality Lines", fontweight="bold")
    ax.legend(loc="upper left")
    add_watermark(ax)
    savefig("ch03_fluid_characterization", "gas_condensate_phase_envelope.png", fig)


def ch03_separator_test():
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 4))
    # Left: GOR vs separator pressure
    P_sep = np.array([10, 20, 30, 40, 50, 60, 70, 80])
    GOR = np.array([250, 195, 165, 145, 135, 130, 132, 138])
    Bo = np.array([1.22, 1.25, 1.27, 1.29, 1.30, 1.31, 1.30, 1.29])
    ax1 = axes[0]
    ax1.plot(P_sep, GOR, "o-", color=C["blue"], linewidth=2, markersize=5)
    ax1.set_xlabel("1st Stage Pressure (bara)")
    ax1.set_ylabel("GOR (Sm³/Sm³)", color=C["blue"])
    ax1.tick_params(axis="y", labelcolor=C["blue"])
    ax1b = ax1.twinx()
    ax1b.plot(P_sep, Bo, "s--", color=C["red"], linewidth=2, markersize=5)
    ax1b.set_ylabel("$B_o$ (Rm³/Sm³)", color=C["red"])
    ax1b.tick_params(axis="y", labelcolor=C["red"])
    ax1.set_title("Separator Test: GOR and $B_o$", fontweight="bold")
    ax1.axvline(x=50, color=C["green"], linestyle=":", alpha=0.5, label="Optimum")
    ax1.legend(loc="upper right", fontsize=8)
    # Right: API gravity vs pressure
    ax2 = axes[1]
    API = np.array([32.5, 33.8, 34.5, 35.0, 35.3, 35.5, 35.4, 35.2])
    ax2.plot(P_sep, API, "D-", color=C["green"], linewidth=2, markersize=5)
    ax2.set_xlabel("1st Stage Pressure (bara)")
    ax2.set_ylabel("API Gravity (°API)")
    ax2.set_title("Oil API Gravity vs Separator Pressure", fontweight="bold")
    ax2.axvline(x=50, color=C["green"], linestyle=":", alpha=0.5)
    fig.tight_layout()
    savefig("ch03_fluid_characterization", "separator_test.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 4: Reservoir Engineering (5 figures)
# ═══════════════════════════════════════════════════════════════════

def ch04_horner_plot():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    horner_ratio = np.logspace(0, 4, 100)
    p_ws = 280 + 12*np.log10(horner_ratio)
    ax.semilogx(horner_ratio, p_ws, color=C["blue"], linewidth=2)
    # Straight line portion
    mask = (horner_ratio > 10) & (horner_ratio < 500)
    ax.semilogx(horner_ratio[mask], p_ws[mask], color=C["red"], linewidth=3, alpha=0.5, label="Semilog straight line")
    ax.set_xlabel("Horner Time Ratio, $(t_p + \\Delta t)/\\Delta t$")
    ax.set_ylabel("Shut-in Pressure (bara)")
    ax.set_title("Horner Plot — Pressure Build-Up Test", fontweight="bold")
    ax.invert_xaxis()
    ax.legend(); add_watermark(ax)
    savefig("ch04_reservoir_engineering", "horner_plot.png", fig)


def ch04_ipr_curves():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Pr = 300; Pwf = np.linspace(0, 300, 200)
    # Productivity Index (straight line)
    J = 15  # m3/d/bar
    Q_pi = J * (Pr - Pwf)
    Q_pi = np.clip(Q_pi, 0, None)
    # Vogel IPR
    Q_max_v = 3500
    Q_vogel = Q_max_v * (1 - 0.2*(Pwf/Pr) - 0.8*(Pwf/Pr)**2)
    Q_vogel = np.clip(Q_vogel, 0, None)
    # Fetkovich
    C_f, n = 0.5, 0.85
    Q_fet = C_f * (Pr**2 - Pwf**2)**n
    Q_fet = np.clip(Q_fet, 0, None)
    ax.plot(Q_pi, Pwf, color=C["blue"], linewidth=2, label="PI (linear)")
    ax.plot(Q_vogel, Pwf, color=C["red"], linewidth=2, linestyle="--", label="Vogel")
    ax.plot(Q_fet, Pwf, color=C["green"], linewidth=2, linestyle="-.", label="Fetkovich")
    ax.set_xlabel("Flow Rate (Sm³/d)")
    ax.set_ylabel("Flowing Bottom-hole Pressure (bara)")
    ax.set_title("Inflow Performance Relationships (IPR)", fontweight="bold")
    ax.legend(loc="upper right"); ax.set_xlim(0, 5000)
    add_watermark(ax)
    savefig("ch04_reservoir_engineering", "ipr_curves.png", fig)


def ch04_pz_plot():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Gp = np.linspace(0, 80, 50)  # BCM
    p_z_initial = 350
    p_z = p_z_initial * (1 - Gp/100)
    ax.plot(Gp, p_z, "o-", color=C["blue"], linewidth=2, markersize=4, label="p/Z data")
    # Straight line fit
    ax.plot([0, 100], [p_z_initial, 0], "--", color=C["red"], linewidth=1.5, label="Linear extrapolation")
    ax.axhline(y=50, color=C["gray"], linestyle=":", alpha=0.5)
    ax.text(85, 55, "Abandonment\np/Z", fontsize=8, color=C["gray"])
    ax.plot(85.7, 50, "v", color=C["green"], markersize=10)
    ax.annotate("EUR = 85.7 BCM", xy=(85.7, 50), xytext=(65, 100),
                fontsize=9, arrowprops=dict(arrowstyle="->", color=C["green"]))
    ax.set_xlabel("Cumulative Gas Production, $G_p$ (BCM)")
    ax.set_ylabel("p/Z (bara)")
    ax.set_title("Material Balance: p/Z Plot", fontweight="bold")
    ax.legend(); ax.set_xlim(0, 110); ax.set_ylim(0, 400)
    add_watermark(ax)
    savefig("ch04_reservoir_engineering", "pz_plot.png", fig)


def ch04_nodal_analysis():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Q = np.linspace(100, 5000, 200)
    # IPR curve
    Pr = 300
    Pwf_ipr = Pr * (1 - (Q/5500)**0.5)
    Pwf_ipr = np.clip(Pwf_ipr, 0, None)
    # VLP curves for different tubing sizes
    for d, label, color in [(3.5, '3.5"', C["blue"]), (4.5, '4.5"', C["red"]), (5.5, '5.5"', C["green"])]:
        Pwf_vlp = 50 + 0.015*d*Q + 2e-6*Q**2/d
        ax.plot(Q, Pwf_vlp, color=color, linewidth=2, linestyle="--", label=f"VLP {label} tubing")
    ax.plot(Q, Pwf_ipr, color=C["black"], linewidth=2.5, label="IPR")
    ax.set_xlabel("Flow Rate (Sm³/d)")
    ax.set_ylabel("Flowing Bottom-hole Pressure (bara)")
    ax.set_title("Nodal Analysis: IPR vs VLP", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8); ax.set_xlim(0, 5000); ax.set_ylim(0, 350)
    # Mark operating points
    for d, color in [(3.5, C["blue"]), (4.5, C["red"]), (5.5, C["green"])]:
        Pwf_vlp = 50 + 0.015*d*Q + 2e-6*Q**2/d
        diff = np.abs(Pwf_ipr - Pwf_vlp)
        valid = Pwf_ipr > 0
        if np.any(valid):
            idx = np.argmin(diff[valid])
            ax.plot(Q[valid][idx], Pwf_ipr[valid][idx], "o", color=color, markersize=8, zorder=5)
    add_watermark(ax)
    savefig("ch04_reservoir_engineering", "nodal_analysis.png", fig)


def ch04_decline_curve():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    t = np.linspace(0, 20, 200)  # years
    qi = 5000
    # Exponential
    D_exp = 0.15
    q_exp = qi * np.exp(-D_exp * t)
    # Hyperbolic
    b, Di = 0.5, 0.2
    q_hyp = qi / (1 + b*Di*t)**(1/b)
    # Harmonic
    q_harm = qi / (1 + 0.15*t)
    ax.semilogy(t, q_exp, color=C["blue"], linewidth=2, label="Exponential (D=0.15)")
    ax.semilogy(t, q_hyp, color=C["red"], linewidth=2, linestyle="--", label=f"Hyperbolic (b={b})")
    ax.semilogy(t, q_harm, color=C["green"], linewidth=2, linestyle="-.", label="Harmonic (b=1)")
    ax.axhline(y=500, color=C["gray"], linestyle=":", alpha=0.5)
    ax.text(15, 550, "Economic limit", fontsize=8, color=C["gray"])
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Production Rate (Sm³/d)")
    ax.set_title("Arps Decline Curve Models", fontweight="bold")
    ax.legend(loc="upper right"); ax.set_xlim(0, 20); ax.set_ylim(100, 7000)
    add_watermark(ax)
    savefig("ch04_reservoir_engineering", "decline_curve.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 5: Well Performance (6 figures)
# ═══════════════════════════════════════════════════════════════════

def ch05_flow_patterns_vertical():
    fig, ax = plt.subplots(figsize=(4, 6))
    ax.set_xlim(0, 4); ax.set_ylim(0, 10); ax.axis("off")
    patterns = [
        (0.5, "Bubble\nFlow", C["ltblue"]),
        (2.5, "Slug\nFlow", C["ltorange"]),
        (4.5, "Churn\nFlow", C["ltgreen"]),
        (6.5, "Annular\nFlow", C["ltred"]),
        (8.5, "Mist\nFlow", C["gray"]),
    ]
    for y, label, color in patterns:
        ax.add_patch(plt.Rectangle((0.5, y), 3, 1.5, facecolor=color, edgecolor=C["black"], linewidth=0.8))
        ax.text(2, y+0.75, label, ha="center", va="center", fontsize=9, fontweight="bold")
    ax.annotate("", xy=(0.2, 9.5), xytext=(0.2, 0.5),
                arrowprops=dict(arrowstyle="-|>", color=C["blue"], lw=2))
    ax.text(0.15, 5, "Increasing\nGas Velocity", fontsize=8, rotation=90, va="center", ha="right", color=C["blue"])
    ax.set_title("Vertical Flow Patterns", fontsize=11, fontweight="bold", pad=10)
    savefig("ch05_well_performance", "flow_patterns_vertical.png", fig)


def ch05_pressure_traverse():
    fig, ax = plt.subplots(figsize=(5, 5.5))
    depth = np.linspace(0, 3000, 200)
    # Different flow rates
    for Q, color, label in [(1000, C["blue"], "1000 Sm³/d"), (2500, C["red"], "2500 Sm³/d"), (4000, C["green"], "4000 Sm³/d")]:
        P = 20 + 0.08*depth + 5e-8*Q*depth - 2e-5*depth*np.log1p(Q/1000)
        ax.plot(P, depth, color=color, linewidth=2, label=label)
    ax.set_xlabel("Pressure (bara)")
    ax.set_ylabel("Measured Depth (m)")
    ax.set_title("Pressure Traverse Curves", fontweight="bold")
    ax.invert_yaxis()
    ax.legend(loc="lower right")
    add_watermark(ax)
    savefig("ch05_well_performance", "pressure_traverse.png", fig)


def ch05_gas_lift_performance():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Q_gl = np.linspace(0, 200, 200)  # kSm3/d gas lift rate
    Q_oil = 2000 * (1 - np.exp(-0.03*Q_gl)) + 500
    ax.plot(Q_gl, Q_oil, color=C["blue"], linewidth=2.5)
    # Optimal point
    idx_opt = 80
    ax.plot(Q_gl[idx_opt], Q_oil[idx_opt], "o", color=C["red"], markersize=10, zorder=5)
    ax.annotate("Economic\nOptimum", xy=(Q_gl[idx_opt], Q_oil[idx_opt]), xytext=(120, 2000),
                fontsize=9, arrowprops=dict(arrowstyle="->", color=C["red"]))
    ax.axvline(x=Q_gl[idx_opt], color=C["red"], linestyle=":", alpha=0.3)
    ax.set_xlabel("Gas Lift Rate (kSm³/d)")
    ax.set_ylabel("Oil Production Rate (Sm³/d)")
    ax.set_title("Gas Lift Performance Curve", fontweight="bold")
    ax.set_xlim(0, 200); ax.set_ylim(0, 3000)
    add_watermark(ax)
    savefig("ch05_well_performance", "gas_lift_performance.png", fig)


def ch05_log_log_diagnostic():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    dt = np.logspace(-2, 3, 200)
    dp = 5 * dt**0.5 * (1 + 0.1*np.log(dt))
    dp_der = 0.5 * dp / dt * dt  # Bourdet derivative approximation
    dp_der = np.gradient(dp, np.log(dt))
    ax.loglog(dt, dp, color=C["blue"], linewidth=2, label="Pressure change, Δp")
    ax.loglog(dt, np.abs(dp_der), color=C["red"], linewidth=2, linestyle="--", label="Bourdet derivative")
    ax.axhline(y=20, color=C["gray"], linestyle=":", alpha=0.5)
    ax.text(0.5, 22, "Radial flow stabilization", fontsize=8, color=C["gray"])
    ax.set_xlabel("Elapsed Time, Δt (hours)")
    ax.set_ylabel("Δp and Derivative (bar)")
    ax.set_title("Log-Log Diagnostic Plot", fontweight="bold")
    ax.legend(loc="lower right")
    add_watermark(ax)
    savefig("ch05_well_performance", "log_log_diagnostic.png", fig)


def ch05_vfp_curves():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Q = np.linspace(500, 6000, 200)
    for WHP, color, label in [(20, C["blue"], "20 bara"), (40, C["red"], "40 bara"), (60, C["green"], "60 bara"), (80, C["orange"], "80 bara")]:
        Pwf = WHP + 100 + 0.02*Q - 5e-7*Q**2 + 8e-4*WHP*Q**0.5
        ax.plot(Q, Pwf, color=color, linewidth=2, label=f"WHP = {label}")
    ax.set_xlabel("Flow Rate (Sm³/d)")
    ax.set_ylabel("Flowing Bottom-hole Pressure (bara)")
    ax.set_title("Vertical Flow Performance (VFP) Curves", fontweight="bold")
    ax.legend(loc="lower right")
    add_watermark(ax)
    savefig("ch05_well_performance", "vfp_curves.png", fig)


def ch05_nodal_analysis():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    Q = np.linspace(100, 5000, 200)
    Pr = 280
    Pwf_ipr = Pr * np.sqrt(1 - (Q/6000)**2)
    Pwf_ipr = np.clip(Pwf_ipr, 0, None)
    Pwf_vlp = 30 + 0.02*Q + 3e-6*Q**2
    ax.plot(Q, Pwf_ipr, color=C["blue"], linewidth=2.5, label="IPR (Reservoir)")
    ax.plot(Q, Pwf_vlp, color=C["red"], linewidth=2.5, linestyle="--", label="VLP (Tubing)")
    diff = np.abs(Pwf_ipr - Pwf_vlp)
    valid = (Pwf_ipr > 0) & (Pwf_vlp < 300)
    idx = np.argmin(diff[valid])
    ax.plot(Q[valid][idx], Pwf_ipr[valid][idx], "ko", markersize=10, zorder=5)
    ax.annotate(f"Operating Point\nQ={Q[valid][idx]:.0f} Sm³/d",
                xy=(Q[valid][idx], Pwf_ipr[valid][idx]), xytext=(Q[valid][idx]+800, Pwf_ipr[valid][idx]+30),
                fontsize=9, arrowprops=dict(arrowstyle="->", color=C["black"]))
    ax.set_xlabel("Flow Rate (Sm³/d)")
    ax.set_ylabel("Flowing Bottom-hole Pressure (bara)")
    ax.set_title("Nodal Analysis — Operating Point Determination", fontweight="bold")
    ax.legend(loc="upper right")
    add_watermark(ax)
    savefig("ch05_well_performance", "nodal_analysis.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 6: Subsea Production Systems (4 figures)
# ═══════════════════════════════════════════════════════════════════

def ch06_subsea_system_overview():
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis("off")
    # Sea surface
    ax.axhline(y=5.5, color=C["blue"], linewidth=2, linestyle="-")
    ax.fill_between([0, 12], 5.5, 8, color=C["ltblue"], alpha=0.15)
    ax.text(10, 7.2, "Platform", fontsize=10, fontweight="bold", ha="center")
    ax.add_patch(FancyBboxPatch((8.5, 5.8), 3, 1.5, boxstyle="round,pad=0.1",
                 facecolor=C["ltorange"], edgecolor=C["orange"]))
    # Seabed
    ax.fill_between([0, 12], 0, 2, color="#e8dcc8", alpha=0.4)
    ax.axhline(y=2, color="#8B7355", linewidth=1.5)
    # Equipment
    subsea = [
        (1.5, 2.3, "Xmas\nTree", C["ltgreen"]),
        (4, 2.3, "Manifold", C["ltgreen"]),
        (7, 3.5, "Riser\nBase", C["ltblue"]),
    ]
    for x, y, label, color in subsea:
        ax.add_patch(FancyBboxPatch((x-0.6, y), 1.2, 0.9, boxstyle="round,pad=0.08",
                     facecolor=color, edgecolor=C["green"]))
        ax.text(x, y+0.45, label, ha="center", va="center", fontsize=7.5, fontweight="bold")
    # Flowline
    ax.plot([2.1, 3.4], [2.75, 2.75], color=C["blue"], linewidth=3)
    ax.plot([4.6, 6.4], [2.75, 3.95], color=C["blue"], linewidth=3)
    # Riser
    ax.plot([7, 9], [4.4, 5.8], color=C["red"], linewidth=3)
    # Well
    ax.plot([1.5, 1.5], [0.5, 2.3], color=C["black"], linewidth=2)
    ax.text(1.5, 0.3, "Well", fontsize=8, ha="center")
    ax.text(3, 2.4, "Flowline", fontsize=8, color=C["blue"], rotation=0)
    ax.text(7.8, 5, "Riser", fontsize=8, color=C["red"], rotation=50)
    ax.set_title("Subsea Production System Overview", fontsize=11, fontweight="bold", pad=10)
    savefig("ch06_subsea_production_systems", "subsea_system_overview.png", fig)


def ch06_subsea_field_layout():
    fig, ax = plt.subplots(figsize=(7, 5.5))
    ax.set_xlim(-5, 25); ax.set_ylim(-5, 20); ax.axis("off")
    # Platform
    ax.plot(20, 15, "^", color=C["orange"], markersize=20, zorder=5)
    ax.text(20, 16.5, "Host\nPlatform", ha="center", fontsize=8, fontweight="bold")
    # Wells
    wells = [(2, 3), (5, 5), (3, 8), (8, 2), (10, 7)]
    for i, (x, y) in enumerate(wells):
        ax.plot(x, y, "o", color=C["blue"], markersize=8)
        ax.text(x, y-1, f"W{i+1}", ha="center", fontsize=7)
    # Manifold
    ax.plot(8, 10, "s", color=C["green"], markersize=15, zorder=5)
    ax.text(8, 11.5, "Manifold", ha="center", fontsize=8, fontweight="bold")
    # Flowlines
    for x, y in wells:
        ax.plot([x, 8], [y, 10], color=C["ltblue"], linewidth=1.5, linestyle="--")
    ax.plot([8, 20], [10, 15], color=C["blue"], linewidth=3, label="Trunk flowline")
    # Umbilical
    ax.plot([20, 8], [14, 9.5], color=C["purple"], linewidth=1.5, linestyle="-.", label="Umbilical")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title("Subsea Field Layout — Daisy-Chain Tieback", fontsize=11, fontweight="bold")
    savefig("ch06_subsea_production_systems", "subsea_field_layout.png", fig)


def ch06_tieback_distance_analysis():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    dist = np.linspace(5, 80, 100)
    # Arrival temperature
    T_arr = 80 * np.exp(-0.02*dist) + 5
    ax2 = ax.twinx()
    ax.plot(dist, T_arr, color=C["red"], linewidth=2, label="Arrival temperature")
    ax.axhline(y=25, color=C["red"], linestyle=":", alpha=0.5)
    ax.text(60, 27, "Hydrate risk threshold", fontsize=8, color=C["red"])
    # Arrival pressure
    P_arr = 100 - 0.8*dist - 0.003*dist**2
    ax2.plot(dist, P_arr, color=C["blue"], linewidth=2, linestyle="--", label="Arrival pressure")
    ax2.axhline(y=40, color=C["blue"], linestyle=":", alpha=0.5)
    ax2.text(10, 42, "Min arrival pressure", fontsize=8, color=C["blue"])
    ax.set_xlabel("Tieback Distance (km)")
    ax.set_ylabel("Temperature (°C)", color=C["red"])
    ax2.set_ylabel("Pressure (bara)", color=C["blue"])
    ax.set_title("Tieback Distance Feasibility Analysis", fontweight="bold")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1+lines2, labels1+labels2, loc="center right", fontsize=8)
    add_watermark(ax)
    savefig("ch06_subsea_production_systems", "tieback_distance_analysis.png", fig)


def ch06_surf_cost_breakdown():
    fig, ax = plt.subplots(figsize=(6, 4.5))
    categories = ["Flowlines", "Umbilicals", "Risers", "Manifold", "Xmas Trees", "Installation"]
    costs = [180, 95, 120, 65, 110, 150]
    colors_list = [C["blue"], C["purple"], C["red"], C["green"], C["teal"], C["orange"]]
    wedges, texts, autotexts = ax.pie(costs, labels=categories, autopct="%1.0f%%",
                                       colors=colors_list, startangle=90, pctdistance=0.8)
    for t in autotexts:
        t.set_fontsize(8); t.set_fontweight("bold")
    for t in texts:
        t.set_fontsize(8)
    ax.set_title("SURF Cost Breakdown (Total: 720 MNOK)", fontweight="bold")
    savefig("ch06_subsea_production_systems", "surf_cost_breakdown.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 7: Flowlines and Risers (4 figures)
# ═══════════════════════════════════════════════════════════════════

def ch07_pipeline_system_overview():
    fig, ax = plt.subplots(figsize=(7.5, 3.5))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4); ax.axis("off")
    components = [
        (0.5, 1.5, "Wellhead\n(80 bara)", C["ltgreen"]),
        (3, 1.5, "Flowline\n(50 km)", C["ltblue"]),
        (5.5, 1.5, "Riser\n(350 m)", C["ltorange"]),
        (8, 1.5, "Slug\nCatcher", C["ltblue"]),
        (10.5, 1.5, "Topside\nSeparation", C["ltgreen"]),
    ]
    for x, y, label, color in components:
        ax.add_patch(FancyBboxPatch((x, y), 2, 1.2, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor=C["gray"]))
        ax.text(x+1, y+0.6, label, ha="center", va="center", fontsize=8, fontweight="bold")
    for i in range(len(components)-1):
        x1 = components[i][0]+2; x2 = components[i+1][0]
        ax.annotate("", xy=(x2, 2.1), xytext=(x1, 2.1),
                    arrowprops=dict(arrowstyle="->", color=C["blue"], lw=2))
    ax.set_title("Pipeline Transport System", fontsize=11, fontweight="bold", pad=10)
    savefig("ch07_flowlines_and_risers", "pipeline_system_overview.png", fig)


def ch07_flow_regimes():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    # Baker flow regime map (simplified)
    Vsg = np.logspace(-2, 2, 300)
    Vsl = np.logspace(-3, 1, 300)
    Vsg_g, Vsl_g = np.meshgrid(Vsg, Vsl)
    # Regime boundaries (simplified)
    ax.fill_between([0.01, 0.3], 0.001, 10, color=C["ltblue"], alpha=0.4)
    ax.fill_between([0.3, 3], 0.01, 10, color=C["ltorange"], alpha=0.4)
    ax.fill_between([3, 100], 0.001, 0.01, color=C["ltgreen"], alpha=0.4)
    ax.fill_between([3, 100], 0.01, 10, color=C["ltred"], alpha=0.4)
    ax.text(0.08, 1, "Bubble", fontsize=9, fontweight="bold", color=C["blue"])
    ax.text(0.7, 0.3, "Slug", fontsize=9, fontweight="bold", color=C["orange"])
    ax.text(15, 0.003, "Stratified", fontsize=9, fontweight="bold", color=C["green"])
    ax.text(15, 0.3, "Annular", fontsize=9, fontweight="bold", color=C["red"])
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Superficial Gas Velocity (m/s)")
    ax.set_ylabel("Superficial Liquid Velocity (m/s)")
    ax.set_title("Horizontal Flow Regime Map", fontweight="bold")
    ax.set_xlim(0.01, 100); ax.set_ylim(0.001, 10)
    add_watermark(ax)
    savefig("ch07_flowlines_and_risers", "flow_regimes.png", fig)


def ch07_pipeline_pt_profiles():
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 4))
    L = np.linspace(0, 50, 200)
    # Pressure profile
    P = 80 - 0.8*L - 0.005*L**2
    axes[0].plot(L, P, color=C["blue"], linewidth=2)
    axes[0].set_xlabel("Distance (km)"); axes[0].set_ylabel("Pressure (bara)")
    axes[0].set_title("Pressure Profile", fontweight="bold")
    axes[0].set_ylim(0, 100)
    # Temperature profile
    T_amb = 4
    T = T_amb + (80-T_amb)*np.exp(-0.04*L)
    axes[1].plot(L, T, color=C["red"], linewidth=2)
    axes[1].axhline(y=20, color=C["green"], linestyle=":", label="Hydrate T")
    axes[1].set_xlabel("Distance (km)"); axes[1].set_ylabel("Temperature (°C)")
    axes[1].set_title("Temperature Profile", fontweight="bold")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    savefig("ch07_flowlines_and_risers", "pipeline_pt_profiles.png", fig)


def ch07_flowline_riser_profile():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    # Horizontal distance vs depth
    x = np.concatenate([np.linspace(0, 45, 100), np.linspace(45, 50, 50)])
    depth = np.concatenate([
        np.full(100, -350) + 10*np.sin(np.linspace(0, 4*np.pi, 100)),  # seabed undulation
        -350 + 350*np.linspace(0, 1, 50)**0.8  # riser
    ])
    ax.plot(x, depth, color=C["blue"], linewidth=2.5)
    ax.fill_between(x[:100], depth[:100]-20, -400, color="#e8dcc8", alpha=0.3)
    ax.axhline(y=0, color=C["black"], linewidth=1)
    ax.text(25, -280, "Seabed Flowline", fontsize=9, color=C["blue"], ha="center")
    ax.text(48, -150, "Riser", fontsize=9, color=C["blue"], rotation=70)
    ax.text(2, -320, "Wellhead", fontsize=8)
    ax.text(49, 10, "Platform", fontsize=8)
    ax.set_xlabel("Horizontal Distance (km)")
    ax.set_ylabel("Depth (m)")
    ax.set_title("Flowline-Riser Profile", fontweight="bold")
    add_watermark(ax)
    savefig("ch07_flowlines_and_risers", "flowline_riser_profile.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Chapter 8: Flow Assurance (3 figures)
# ═══════════════════════════════════════════════════════════════════

def ch08_flow_assurance_threats():
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis("off")
    threats = [
        (5, 6.5, "Flow Assurance\nThreats", C["black"], 14),
        (1.5, 4.5, "Hydrates", C["blue"], 10),
        (4, 4.5, "Wax", C["orange"], 10),
        (6.5, 4.5, "Asphaltenes", C["purple"], 10),
        (9, 4.5, "Corrosion", C["red"], 10),
        (1.5, 2.5, "Slugging", C["green"], 10),
        (4, 2.5, "Scale", C["teal"], 10),
        (6.5, 2.5, "Erosion", C["gray"], 10),
        (9, 2.5, "Emulsions", C["orange"], 10),
    ]
    for x, y, label, color, fs in threats:
        ax.add_patch(FancyBboxPatch((x-1.1, y-0.4), 2.2, 0.8, boxstyle="round,pad=0.1",
                     facecolor=color, edgecolor="white", alpha=0.85))
        ax.text(x, y, label, ha="center", va="center", fontsize=fs-2, fontweight="bold", color="white")
    for i in range(1, 5):
        ax.plot([5, threats[i][0]], [6.1, threats[i][1]+0.4], color=C["gray"], linewidth=1)
    for i in range(5, 9):
        ax.plot([5, threats[i][0]], [6.1, threats[i][1]+0.4], color=C["gray"], linewidth=1, linestyle="--")
    ax.set_title("Flow Assurance Threat Matrix", fontsize=12, fontweight="bold", pad=15)
    savefig("ch08_flow_assurance", "flow_assurance_threats.png", fig)


def ch08_hydrate_phase_envelope():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    T = np.linspace(-5, 30, 200)
    P_hyd = 10 * np.exp(0.12 * (T + 5))
    P_hyd_inh = 10 * np.exp(0.12 * (T - 2))  # With inhibitor
    ax.semilogy(T, P_hyd, color=C["blue"], linewidth=2.5, label="No inhibitor")
    ax.semilogy(T, P_hyd_inh, color=C["green"], linewidth=2.5, linestyle="--", label="With MEG (30 wt%)")
    ax.fill_betweenx([1, 1000], -5, 15, color=C["ltblue"], alpha=0.2)
    ax.text(5, 300, "Hydrate\nRegion", fontsize=10, color=C["blue"], ha="center", style="italic")
    ax.text(22, 50, "No Hydrate\nRegion", fontsize=10, color=C["green"], ha="center", style="italic")
    # Operating path
    T_op = np.array([25, 18, 12, 8, 5])
    P_op = np.array([80, 75, 70, 65, 60])
    ax.plot(T_op, P_op, "ro-", linewidth=1.5, markersize=6, label="Operating path")
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Pressure (bara)")
    ax.set_title("Hydrate Phase Envelope", fontweight="bold")
    ax.legend(loc="lower right"); ax.set_xlim(-5, 30); ax.set_ylim(5, 500)
    add_watermark(ax)
    savefig("ch08_flow_assurance", "hydrate_phase_envelope.png", fig)


def ch08_flow_assurance_envelope():
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    T = np.linspace(-10, 100, 300)
    # Various constraints
    P_hyd = 8 * np.exp(0.12*(T+5))
    P_wax = np.where(T < 35, 1000, np.nan)  # WAT at 35°C
    ax.semilogy(T, P_hyd, color=C["blue"], linewidth=2, label="Hydrate curve")
    ax.axvline(x=35, color=C["orange"], linewidth=2, linestyle="--", label="WAT = 35°C")
    ax.axhline(y=150, color=C["gray"], linewidth=1.5, linestyle=":", label="Design pressure (150 bara)")
    # Safe operating window
    ax.fill_between([35, 100], 1, 150, color=C["ltgreen"], alpha=0.3)
    ax.text(60, 50, "Safe Operating\nWindow", fontsize=10, color=C["green"], ha="center", fontweight="bold")
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Pressure (bara)")
    ax.set_title("Flow Assurance Operating Envelope", fontweight="bold")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_xlim(-10, 100); ax.set_ylim(1, 500)
    add_watermark(ax)
    savefig("ch08_flow_assurance", "flow_assurance_envelope.png", fig)


# ═══════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating figures for chapters 1-8...")
    funcs = [v for k, v in sorted(globals().items()) if k.startswith("ch0") and callable(v)]
    for fn in funcs:
        try:
            fn()
        except Exception as e:
            print(f"  [FAIL] {fn.__name__}: {e}")
    print(f"Done. Generated {len(funcs)} figures.")
