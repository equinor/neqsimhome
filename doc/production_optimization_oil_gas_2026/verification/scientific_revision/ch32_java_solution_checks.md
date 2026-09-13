# Chapter32 Java numerical verification

**PASS**: 12 literal Java fences executed with 363 successful checks and zero compile/runtime diagnostics. One explicitly marked external integration pattern (fence23) remains excluded.

The fresh source fixture now explicitly enables polytropic mode. The evaluator retains the rejected100,000kg/hr candidate above its5MW constraint and accepts80,000kg/hr with direct power and returned-feasibility checks.

Checks cover:

- Compressor/separator component, mass and energy closure and fresh objective replays for sampled Pareto states.
- Convex quadratic SQP solution `(3,2)`, objective0, equality/inequality/bounds; finite-difference gradient `(-1,0)`.
- Constant-signal mean60, zero deviation and the declared R-statistic convention.
- Analytic weighted reconciliation `[101600,69100,27600,4900]kg/hr, residual0, chi-square1.2 and normalized residual magnitudes.
- Synthetic efficiency recovery from0.78 with fresh130/150/170bara temperature and compressor-energy checks.
- All12 batch cases replayed on fresh processes, sampled Pareto non-dominance, lower-pressure selection at each flow and independent summary arithmetic.
- JSON serialization with explicit null encoding for unbounded limits.

Pareto fresh objective replay uses1e-6 relative tolerance; initial absolute1e-5kW bound was below thermodynamic solver repeatability (largest7.45W at10.411MW,7.15e-7 relative). Initial report is retained; mass/component/energy tolerances remain1e-6/1e-6/1e-5.

The successful12fences comprise11 numerical cases and one serialization contract. These checks verify the stated algorithms and model balances; they do not constitute plant calibration or prove a complete continuous Pareto front. Exact code hashes and all measurements are retained in the JSON companion.
