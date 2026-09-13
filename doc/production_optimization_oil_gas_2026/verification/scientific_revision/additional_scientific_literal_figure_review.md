# Additional scientific literal figure review

Status: passed for the three selected images.

## ch24_production_optimization

Stock-tank oil and a limited product-value screen across 28 separator pressures at 250,000 kg/h feed.

The 28 actual flashes retain all gas, oil and any aqueous products at 15 °C and 1.01325 bara. Stock-tank oil spans 2192.7–2318.8 m³/day, with its sampled maximum at 55 bara; oil density is 677.886–678.983 kg/m³. The assumed product value less compressor electricity peaks at 45 bara and 2294.38 kUSD/day. Mass/component residuals are below 3×10⁻¹¹. Conditioning cooling of 1.21–1.91 MW is recorded but not priced, and flash gas has no sales credit. The different maxima reflect liquid partition, gas value and compression work. This is a 28-point sensitivity with assumed prices and heating value; it does not establish installed capacity, product qualification or a global operating optimum.

Visual review: Full image inspected: all four panels and axes visible; actual reference-state liquid units, sampled 45.0 bara marker and limited-economic-scope labels match the saved arrays.

Image SHA256: 787726771901863aea199ba1aa60d4fc0930bdc1990eb25aee6fca58194b2633

Literal SHA256: 4aecd64d8c7e1394cfedb9dd08bd1c68a7cb18f3e936502046e4245ffb227809

## ch30_digital_twins_and_automation

A 24-hour synthetic input sequence propagated through the source-backed process model.

Feed varies from 95 to 105 t/h, with synthetic temperatures 54.26–64.74 °C and pressures 49.02–50.93 bara. The model compressor requires 3.739–4.321 MW. Separator gas temperature overlays its prescribed feed temperature because this equilibrium separator imposes no temperature change; the matching curves are not independent sensor validation. The case checks automation input propagation and process balances. Field use still requires measured observations and separate calibration.

Visual review: Full image inspected: three readable panels, 24 points, explicit synthetic-temperature legend, t/h and MW units; no plant measurements or injected 3 K offset are claimed.

Image SHA256: 9bf31e74cb64c7753d73d11b37483c994e20ec0b1018434d91efb914a572527b

Literal SHA256: 632411427db9fa32ce251592e693b3b3e9e10eac2c74fe4f0b0ca6af105b4c95

## ch32_advanced_topics

Twenty-five independently solved rate cases compared with the native weighted-search sample.

At fixed 50→150 bara compression and 40 °C suction, the independent grid spans 50,000–200,000 kg/h and 3250.84–13003.37 kW. Its monotonic linear trade-off has no unique knee or preferred throughput without a capacity or economic criterion. The native weighted search returns one endpoint near 200,000 kg/h, which agrees with the independently solved grid. Each grid point passes mass and shaft-work/enthalpy checks; this comparison establishes the sampled model trade-off, not a vendor-map or field validation.

Visual review: Full image inspected: 25 grid samples and one native endpoint are visible, legend distinguishes both sources, axes carry kg/h and kW, and title correctly says sampled non-dominated states.

Image SHA256: f5023eb47259eb22159ea0ebe8e1c4deabc0d0ddac8ea83fa8138820fd260999

Literal SHA256: 3914a8e6cc500a37eedcdf31d2609348a810549f4bdd2b140b930c6627cd2077

The existing eight-image review and all repaired legacy image bytes were preserved. Unselected native diagnostics are explicitly excluded from the publication approval. The incorrect gas-equivalent oil economic figure and prior source/report were archived as rejected evidence.