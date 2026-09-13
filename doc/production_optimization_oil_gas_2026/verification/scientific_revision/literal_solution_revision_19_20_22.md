# Chapters 19, 20 and 22 solution verification

PASS: all 28 literal Python fences execute and match current source hashes, with 530 scoped solution-check records. Three new actual figures passed visual and array review. The 35 chapter notebooks were not modified.

- Initialized mole fractions before ISO6976; the former zero GCV/NaN Wobbe output is rejected. Checked positive GCV>NCV, Wobbe=GCV/sqrt(relative density), compositional molar mass, reference units and all declared quality-screen predicates.

- Replaced the failing direct water-dew-point call with a normalized exactly 20 mol-ppm CPA recipe and a multiphase VLE calculation. Eight pressure states each have aqueous liquid below and no aqueous liquid above their onset. Ice/hydrate scope is explicit.

- Retained finite contiguous hydrocarbon envelope data and documented the undefined terminal continuation slot. The reported quantity is a sampled dew-curve maximum, with no invented critical point.

- Export pipelines and diameter alternatives have positive pressure, material/component balance and accepted/rejected-domain checks; coupled compressor and cooler boundaries have first-law checks.

- Corrected the facility pipeline length from 80 m to 80,000 m. Replaced claims of a complete LP/two-stage/UA facility with the actual HP/single-stage/specified-temperature-cooler boundary.

- Explicitly enabled polytropic calculation wherever a polytropic efficiency was specified. Compressor checks include single-phase inlets, positive work, rising pressure/temperature and first-law closure.

- Verified half-full separator geometry, retention and Souders–Brown arithmetic, UA clean/fouled heat balance, isenthalpic valve behavior, erosional-unit conversion and fixed-rating utilization arithmetic. A linear extrapolation is explicitly not a solved facility capacity.

- Replaced the unexecuted water-cut placeholder and assumed trend with eight actual CPA methane/heptane/water cases using fixed 200 m3/h liquid at 15 C/1.01325 bara and a specified associated-gas/oil ratio. Each separation and compression boundary is checked.

- Replaced the dimensionally invalid API-area expression with a clearly scoped SI ideal-gas sonic-nozzle limit. An independent sonic-state density×velocity×area check reproduces its mass rate. Real-fluid Z and pressure convention are explicit; no PSV rating is claimed.

- Replaced reverse 3 m wellbore integration with a forward 3000 m upward tubing solve coupled to the declared IPR. Nonphysical trial states are excluded and diagnosed; accepted TPR and operating-point residuals are checked.

- Verified every separation and compressor sample and all objective selections. Actual two-objective samples have one nondominated point. Gas-lift allocation is checked by analytical KKT conditions and an independent exhaustive grid.

- Replaced three stale adjacent Chapter22 illustrations with actual accepted nodal, interstage-power and sampled-objective plots, with connected quantitative discussions.

Exact code/report/image hashes, tolerances and observed values are retained in the JSON records. These checks establish the stated numerical/physical scopes and do not provide field or standards certification.
