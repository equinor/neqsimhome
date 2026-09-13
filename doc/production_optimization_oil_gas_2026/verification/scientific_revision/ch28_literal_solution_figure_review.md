# Chapter 28 actual literal-figure visual review

Passed: all three actual manuscript figures were viewed by the reviewing agent and reconciled to current source and numerical evidence. This is an agent visual review, not human or field peer certification.

## ch28_verified_recombination_density.png

Equilibrium bulk density of five actual reference-phase recombinations at 80 °C and 50 bara, with 10% standard-volume water cut. GOR is standard gas volume divided by standard oil volume; standard reference is 15 °C and 1.01325 bara.

Image SHA-256: `a5d6cbf244873e2ac7377e193080f73bdabb6d49dbd95608e4a773a246bc2c72`; dimensions: [1738, 1077]; source fence 21.

- All five computed markers are visible on the logarithmic GOR axis. Density units are kg/m3; equilibrium bulk density is explicitly distinguished from pipe holdup density.
- Monotone decrease 187.2664 to 47.7679 kg/m3 reconciles to all five saved values. No fabricated intermediate points or hidden domain gaps.
- Title states 80 C, 50 bara and WC 10%; caption gives the standard reference and recipe basis. Labels and tick marks are readable with no overlap or cropping.

## ch28_verified_screening_surface.png

Six actual required-inlet-pressure samples at 5% water cut and GOR 1000 Sm³/Sm³ for the Python model: 2800 m upward tubing and 12 km horizontal flowline. Black markers identify the solved grid values; the connecting facets are a visual interpolation.

Image SHA-256: `a196e7b47b4215d947f4a449b4f0cbebb218c1fe57ca3aeda045e0beb9f1486f`; dimensions: [1496, 1516]; source fence 22.

- All six black solution markers are visible. Mass rate uses 1000 kg/hr, outlet and inlet pressure use bara. Uniform translucent shading connects samples; no misleading pressure colorbar remains.
- Height spans the actual 75.4297 to 119.9023 bara source values. The lower-middle sampled pressure and nonmonotonic rate direction are retained.
- Axes and title have room; pressure label is readable. Caption explains sparse visual interpolation and 1 bar bracketing tolerance without claiming interpolation calibration.

## ch28_verified_gor_pressure.png

Two actual GOR scenarios for the same 2800 m upward tubing and 12 km flowline, at 5% water cut and 50 bara outlet pressure. Points are accepted pressure-table solutions; lines connect the sampled cases.

Image SHA-256: `64f34efb15d9aabfa378c3d9dbb95238307dacba8da91f643b1542d3f26e5771`; dimensions: [2178, 1296]; source fence 23.

- Both GOR 300 and GOR 1000 curves have three visible markers and a readable legend. X is mixture mass rate; both y and stated outlet pressure use bara.
- GOR 1000 values 119.9023,105.0781,117.3242 bara match source arrays. GOR 300 values and 5% water cut also reconcile. No forced monotonic trend.
- Caption explains equal mixture mass-rate basis, holdup/friction competition, and limits of economic interpretation. No cropped title, axes or legend.

The 35 frozen notebooks and prior figure-review ledgers were not modified. No unresolved material image defect remains.