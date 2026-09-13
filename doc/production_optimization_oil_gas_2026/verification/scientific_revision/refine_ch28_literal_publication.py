"""Targeted, repeatable Chapter 28 publication corrections."""
from pathlib import Path
import re
B=Path(__file__).resolve().parents[2];C=next((B/'chapters').glob('ch28_*/chapter.md'))
s=C.read_text(encoding='utf-8-sig')
s=s.replace('**Concept 2: Short tieback with subsea boosting (8 km)**','**Concept 2: Shorter horizontal route (8 km)**').replace('**Concept 3: Standalone FPSO (minimal pipeline)**','**Concept 3: Short horizontal route (0.5 km)**')
s=s.replace('Creates physically consistent fluids at any GOR','Creates recombined fluids at specified GOR')
s=s.replace('**RecombinationFlashGenerator** creates physically consistent fluids at any GOR and water cut by recombining separated gas, oil, and water phases — mimicking actual reservoir behavior.','**RecombinationFlashGenerator** recombines separated reference gas, oil and water phases at specified mixing ratios. It does not predict reservoir depletion, and extreme ratios require equilibrium and phase-applicability checks.')
s=s.replace('**Concept screening** with multi-scenario VFP tables allows rapid comparison of development alternatives (tieback distance, subsea boosting, standalone FPSO).','**Concept screening** here compares horizontal route lengths at unchanged tubing geometry. Subsea boosting and FPSO processing require additional equipment models and economics.')
s=s.replace('**Quality assurance** — check for monotonicity, validate against well tests, and refresh tables when the reservoir model is updated.','**Quality assurance** — check phase and pressure domains, conservation and outlet-pressure brackets; interpret any nonmonotonic lift requirement through holdup and friction. Validate against well tests and refresh tables when the reservoir model changes.')
s=s.replace('**At what GOR does the compressor become the bottleneck?** — The VFP table shows the maximum rate achievable at each GOR','**At what GOR might compression constrain production?** — Include a compressor with an explicit installed capacity model; the tubing-and-flowline table shown here has no compressor.')
s=s.replace('**When should the choke setting change?** — VFP curves at different WC/GOR show the optimal pressure split','**When should the choke setting change?** — Couple the pressure table to inflow and explicit choke/facility constraints before optimizing a pressure split.')
s=s.replace('**How does water cut affect export pipeline capacity?** — Higher WC means more liquid holdup and higher friction','**How does water cut affect export pipeline capacity?** — Recalculate holdup, density and friction for the declared flow basis; their combined direction is case dependent.')
s=s.replace('**Low GOR, low WC:** Nearly linear VFP curve. BHP increases smoothly with rate.','**Low GOR, low WC:** Friction can dominate at high rates; the actual low-rate branch depends on liquid holdup and elevation.')
s=s.replace('**Low GOR, high WC:** Steeper curve (heavy emulsion). Higher BHP needed at all rates.','**Low GOR, high WC:** A denser liquid phase may increase static head. Emulsion effects require a separate calibrated rheology and cannot be inferred from water cut alone.')
s=s.replace('**High water cut** — When water cut exceeds 80–90%, the well may not be economic:','**High water cut** — Water handling and disposal costs can reduce the economic oil rate. Use standard oil and water volumes on the same reference basis:')
old='''# Check if well is economic at current water cut
for well_name in wells:
    tubing = network.getPipe(f"Tubing-{well_name}")
    wc = tubing.getWaterCut()
    flow = network.getPipeFlowRate(f"Tubing-{well_name}")
    oil_flow = flow * (1.0 - wc)

    if oil_flow < min_economic_oil_rate:
        print(f"Well {well_name}: WC={wc:.0%}, "
              f"Oil={oil_flow:.1f} kg/s — UNECONOMIC")'''
new='''# Supplied standard liquid rate and volumetric water cut, at the same reference.
for well_name in wells:
    wc = well_standard_water_cut[well_name]
    liquid = well_standard_liquid_rate_Sm3_day[well_name]
    assert 0.0 <= wc <= 1.0 and liquid >= 0.0
    oil_rate = liquid * (1.0 - wc)
    if oil_rate < min_economic_oil_rate_Sm3_day:
        print(f"Well {well_name}: WC={wc:.0%}, "
              f"Oil={oil_rate:.1f} Sm3/day — below assumed economic threshold")'''
s=s.replace(old,new).replace('requires configured network tubing elements and water-cut data','requires supplied standard liquid rates, volumetric water cuts, and economic threshold')
s=s.replace('This integration pattern requires configured network tubing elements and water-cut data.','This integration pattern requires supplied standard liquid rates, volumetric water cuts and a declared economic threshold.')
old='surf = ax.plot_surface(Q / 1000, P, bhp_data, cmap=\'viridis\', alpha=0.8)'
new='''surf = ax.plot_surface(Q / 1000, P, bhp_data, cmap='viridis', alpha=0.85,
                       vmin=np.nanmin(bhp_data), vmax=np.nanmax(bhp_data))
ax.scatter(Q / 1000, P, bhp_data, c='black', s=22, depthshade=False)'''
s=s.replace(old,new)
for old,new in [('density_vs_gor.png','ch28_verified_recombination_density.png'),('vfp_surface.png','ch28_verified_screening_surface.png'),('vfp_gor_comparison.png','ch28_verified_gor_pressure.png')]:
 s=s.replace('"figures/'+old+'"','"figures/'+new+'"')
s=s.replace('dpi=150, bbox_inches="tight"','dpi=220, bbox_inches="tight"')
s=s.replace('ax.set_ylabel("Mixture Density (kg/m³)")','ax.set_ylabel("Equilibrium bulk density (kg/m³)")')
old='The optimizer\'s `OptimizationResult` reports'
addition='''The reduced model returns 39,923.98 Sm³/day: 3,208.21 from Well A and 36,715.77 from Well B. Revenue is 119,771.95 currency units/day at the assumed common price of 3 per Sm³. The capacity gives an upper bound of 120,000 currency units/day; an independent solution of the stated Vogel interpolation and quadratic flowline equations confirms that 40,000 Sm³/day is reachable. The native coordinate search is therefore 0.190% below this bound for the teaching case, rather than an exact global optimum. The two chokes are dimensionless deliverability multipliers, not valve openings calibrated to a Cv curve. Energy and emissions use the stated fixed intensities; no thermodynamic processing plant is solved in this reduced example.

'''
if addition not in s:s=s.replace(old,addition+old)
C.write_text(s,encoding='utf-8');print(C)
