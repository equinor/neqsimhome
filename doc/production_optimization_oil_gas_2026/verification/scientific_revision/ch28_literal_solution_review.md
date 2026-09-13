# Chapter 28 literal engineering solution review

Passed: 8 Python and 11 Java runnable fences, 118 Python and 1261 Java check records. All 96 table cells have current-source solution checks. Five external-input patterns remain explicitly scoped. Three new figures were inspected by the reviewing agent.

## Material corrections

- Third recombination argument mislabeled as mass kg/hr; inherited helper expected 10000 kg/hr. Current primary Java contract uses 10000 Sm3/hr total standard liquid. Validate liquid volume and resulting mass separately. Original mass mismatch retained; tolerance was not relaxed to pass a wrong unit.
- Published export example invented VFPEXP deck text contradicting the actual diagnostic API. Replaced with actual diagnostic column/unit/feasibility contract; exact written UTF-8 output checked against native diagnostic text.
- Initial supplementary reference-phase component lookup assumed every separated phase had every mixture component. Absent components contribute zero to the independent inventory, as the actual phase composition specifies. No manuscript or model inputs changed.
- Initial reference-state hook interpreted unflashed input phase fields as equilibrium. A cloned reference receives an explicit verification TP flash before phase component-balance checking. Input configuration is not misrepresented as a solved equilibrium.
- 3D polygon colors used average facet values with an ambiguous pressure colorbar. Final literal plot uses uniform shading, six explicit black solution markers and a pressure height axis. Numeric arrays remain unchanged.
- Route alternatives named a booster/FPSO/riser without those equipment changes; economic pattern multiplied total mass by volumetric water cut. Routes now describe changed horizontal lengths with unchanged upward tubing. The external-data economic pattern uses standard oil-plus-water liquid volume and volumetric water cut on a common reference.

## Numerical result and engineering interpretation

The reduced allocation gives 39,923.9833 Sm³/day and revenue 119,771.9499 per day. The independent feasible 40,000 Sm³/day witness establishes revenue 120,000 per day as a reachable upper bound: the reported candidate is 0.190% below it. The five density states decrease from 187.2664 to 47.7679 kg/m³ over GOR 200–5000 at 80 °C and 50 bara. Nonmonotonic required inlet pressures are retained and physically bracketed.

## Exact scope and limits

- These literal hydraulic replays verify the solutions of the supplied correlations; they are not an independent field calibration. Book benchmark evidence remains a separately scoped artifact.
- No pipe heat-transfer boundary is specified in these cases; an energy-conservation claim for an adiabatic pipe is not made.
- Vogel-shaped wellhead curves and default quadratic line resistances are illustrative reduced surrogates. Chokes are mathematical deliverability multipliers, not calibrated valve positions.
- The optimizer returns a feasible near-optimum 0.190% below the independently reachable revenue upper bound. Constant energy and emissions intensities do not constitute a thermodynamic facility or lifecycle assessment.
- Route-length alternatives do not include a subsea booster or FPSO processing model. Standard liquid mixing rates and total mixture mass rates remain separate dimensions.
- No field data is supplied for the five explicitly annotated integration patterns; no execution or solution validation is claimed for those external-data workflows.

## Source freshness

Chapter SHA-256: `192c05f73e68ae91434ddcbd25aec4e407904e13a347845ed0147d9aa40808e2`. The JSON ledger records every current literal hash, ordinary execution status, primary source and verifier hash, tolerances and evidence-file hashes. The 35 notebooks and their existing reports were not changed.
