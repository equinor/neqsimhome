"""
Shared Wiley-quality figure styling for all book figures.
Import this module in each batch script.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Wiley book style: clean, serif fonts, publication quality
WILEY_STYLE = {
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif", "Georgia"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linewidth": 0.5,
    "axes.linewidth": 0.8,
    "lines.linewidth": 1.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.figsize": (6.5, 4.5),
}

# Color palette – professional, colorblind-safe
C = {
    "blue":    "#2166ac",
    "red":     "#b2182b",
    "green":   "#1b7837",
    "orange":  "#e08214",
    "purple":  "#6a3d9a",
    "teal":    "#17becf",
    "gray":    "#636363",
    "black":   "#1a1a1a",
    "ltblue":  "#92c5de",
    "ltred":   "#fddbc7",
    "ltgreen": "#a6dba0",
    "ltorange":"#fee0b6",
}
PALETTE = [C["blue"], C["red"], C["green"], C["orange"], C["purple"], C["teal"], C["gray"]]

BOOK_DIR = Path(__file__).parent
CHAPTERS_DIR = BOOK_DIR / "chapters"


def apply_style():
    """Apply Wiley style globally."""
    plt.rcParams.update(WILEY_STYLE)


def savefig(chapter_dir_name: str, filename: str, fig=None):
    """Save figure to the chapter's figures/ directory."""
    out = CHAPTERS_DIR / chapter_dir_name / "figures" / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    if fig is None:
        fig = plt.gcf()
    fig.savefig(str(out), dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] {chapter_dir_name}/figures/{filename}")


def add_watermark(ax, text="NeqSim"):
    """Subtle watermark in bottom-right."""
    ax.text(0.98, 0.02, text, transform=ax.transAxes, fontsize=7,
            color="#cccccc", ha="right", va="bottom", style="italic")
