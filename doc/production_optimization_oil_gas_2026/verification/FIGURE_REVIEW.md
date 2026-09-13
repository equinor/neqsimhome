# Numerical figure review

The final notebook release contains 104 regenerated figures from 35 chapter
notebooks. All plots have explicit labels and units; numerical plots are exported
at 220 dpi with CSV coordinates and per-figure provenance. The release gate
verified all notebook, code-cell and PNG hashes after the final editorial update.

The figure review checked the physical meaning of the plotted output in addition
to successful execution. Corrections included active polytropic compressor
efficiency, a finite water-dew-point calculation, material-consistent oil formation
volume factors, explicit upward-production VFP boundaries, independent valve
sizing, heat-exchanger energy closure, and feasible optimizer endpoints. Display
coordinates from horizontal bars are now exported from bar width rather than
the decorative bar height.

Representative final PNGs were viewed directly for legible axes, titles, legends,
units, visible variation, and unclipped annotations:

- Chapter 1: actual volumetric equipment load at fixed mass flow.
- Chapter 3: same-sample oil formation volume factor.
- Chapter 8: bracketed pipeline capacity versus diameter.
- Chapter 9: MEG inhibition and 50 ppmv water-dew-point calculations.
- Chapter 14: distinct active-efficiency compressor power curves.
- Chapter 17: increasing required Cv and constant JT cooling on an engineering scale.
- Chapter 24: matched search results and independently checked utilization.
- Chapter 28: upward-production VFP curves.
- Chapter 29: correctly acting illustrative level controller.
- Chapter 32: separate seasonal KPI panels with individual physical units.
- Chapter 33: CPA TEG circulation sensitivity and the limiting plateau.

The chapter discussion sections explicitly identify assumed maps, analytical
relationships, prescribed pressure and temperature paths, illustrative Python
control dynamics, and synthetic sensor measurements. These illustrations are not
represented as independent experimental or field validation. Additional figures
generated from manuscript code fences are tracked by the manuscript verification
workflow, separately from the 104 notebook figures.

Ready-to-insert discussions and compact numerical tables are in
`figure_sections/ch01.md` through `figure_sections/ch35.md`. Their machine-readable
equivalent is `notebook_figure_updates.json`.
