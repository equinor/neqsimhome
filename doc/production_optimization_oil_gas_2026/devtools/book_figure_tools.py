"""Book-local figure provenance and numerical export utilities.

Figures remain products of the notebook's NeqSim calculations. Each save also
exports plotted numerical series so readers can inspect the published curves.
"""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.container import BarContainer
from matplotlib.collections import PathCollection

FIGURE_RECORDS = []
_original_savefig = Figure.savefig


def configure_figures():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.titlesize": 13, "axes.labelsize": 11,
        "legend.fontsize": 9, "xtick.labelsize": 10, "ytick.labelsize": 10,
        "figure.dpi": 110, "savefig.dpi": 220,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titleweight": "bold", "axes.titlepad": 12,
        "axes.labelpad": 8, "grid.alpha": 0.23,
        "lines.linewidth": 2.0, "figure.facecolor": "white",
        "axes.prop_cycle": plt.cycler(color=["#146B8B", "#DF7B29", "#218A75", "#765692", "#B54157", "#686C70"]),
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })
    Figure.savefig = _save_with_data


def _save_with_data(figure, filename, *args, **kwargs):
    """Save the requested plot plus a CSV and compact evidence manifest."""
    if not isinstance(filename, (str, Path)):
        return _original_savefig(figure, filename, *args, **kwargs)
    path = Path(filename).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    kwargs["dpi"] = max(220, float(kwargs.get("dpi", 220)))
    kwargs.setdefault("bbox_inches", "tight")
    _original_savefig(figure, path, *args, **kwargs)
    rows, series = [], []
    for panel, axis in enumerate(figure.axes, 1):
        candidates = []
        for idx, line in enumerate(axis.lines, 1):
            try:
                x, y = np.asarray(line.get_xdata(), dtype=float), np.asarray(line.get_ydata(), dtype=float)
            except (ValueError, TypeError):
                continue
            label = line.get_label()
            if label.startswith("_"):
                label = "Curve {}".format(idx)
            candidates.append((label, x, y, "y"))
        for idx, container in enumerate(axis.containers, 1):
            if isinstance(container, BarContainer):
                horizontal = container.orientation == "horizontal"
                if horizontal:
                    x = np.asarray([bar.get_width() for bar in container], dtype=float)
                    y = np.asarray([bar.get_y() + bar.get_height() / 2 for bar in container], dtype=float)
                else:
                    x = np.asarray([bar.get_x() + bar.get_width() / 2 for bar in container], dtype=float)
                    y = np.asarray([bar.get_height() for bar in container], dtype=float)
                label = container.get_label()
                candidates.append((label if not label.startswith("_") else "Bars {}".format(idx), x, y, "x" if horizontal else "y"))
        for idx, collection in enumerate(axis.collections, 1):
            if isinstance(collection, PathCollection):
                offsets = np.asarray(collection.get_offsets(), dtype=float)
                if offsets.ndim == 2 and offsets.shape[1] == 2 and len(offsets) > 1:
                    label = collection.get_label()
                    candidates.append((label if not label.startswith("_") else "Points {}".format(idx), offsets[:, 0], offsets[:, 1], "y"))
        for label, x, y, value_axis in candidates:
            if x.size != y.size or y.size == 0:
                continue
            finite = np.isfinite(x) & np.isfinite(y)
            for point, (xvalue, yvalue) in enumerate(zip(x, y)):
                rows.append({"panel": panel, "series": label, "point": point,
                             "x_label": axis.get_xlabel(), "y_label": axis.get_ylabel(),
                             "x": float(xvalue), "y": float(yvalue), "finite": bool(finite[point])})
            series.append({"panel": panel, "title": axis.get_title(), "series": label, "value_axis": value_axis,
                           "x_label": axis.get_xlabel(), "y_label": axis.get_ylabel(),
                           "n_points": int(y.size), "n_nonfinite": int((~finite).sum()),
                           "x_min": float(x[finite].min()) if finite.any() else None,
                           "x_max": float(x[finite].max()) if finite.any() else None,
                           "y_min": float(y[finite].min()) if finite.any() else None,
                           "y_max": float(y[finite].max()) if finite.any() else None,
                           "x_at_y_max": float(x[finite][np.argmax(y[finite])]) if finite.any() else None})
    if rows:
        with path.with_suffix(".csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    record = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "dpi": kwargs["dpi"], "series": series}
    FIGURE_RECORDS.append(record)
    path.with_suffix(".data.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")


def export_figure_summary(notebook_path):
    """Return a table of actual curve extrema and persist chapter evidence."""
    import pandas as pd
    notebook_path = Path(notebook_path)
    chapter = notebook_path.parent.parent
    rows = []
    for record in FIGURE_RECORDS:
        for item in record["series"]:
            value_axis = item.get("value_axis", "y")
            rows.append({"Figure": Path(record["path"]).name, "Panel": item["panel"],
                         "Series": item["series"], "Output / unit": item[value_axis + "_label"],
                         "Minimum": item[value_axis + "_min"], "Maximum": item[value_axis + "_max"],
                         "Finite points": item["n_points"] - item["n_nonfinite"],
                         "Missing points": item["n_nonfinite"]})
    table = pd.DataFrame(rows)
    table.to_csv(chapter / "figures" / (notebook_path.stem + "_results.csv"), index=False)
    (chapter / "figures" / (notebook_path.stem + "_manifest.json")).write_text(
        json.dumps({"notebook": notebook_path.name, "figures": FIGURE_RECORDS}, indent=2, ensure_ascii=False), encoding="utf-8")
    return table
