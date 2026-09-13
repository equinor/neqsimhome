"""Correct hydraulic, hydrate and subsea scientific statements and units."""
from revise_foundations_science_phase3 import R,S,BOOK
R('ch02','HV_sign',r'\sum_i x_i \frac{a_i}{b_i} + \frac{g_{\text{E},\infty}}{C^*}',r'\sum_i x_i \frac{a_i}{b_i} - \frac{g_{\text{E},\infty}}{C^*}')
R('ch02','HV_constant','and $C^*$ is a constant that depends on the EOS.',r'and $C^*$ is positive in this convention: $\ln 2$ for SRK and $\ln[(2+\sqrt 2)/(2-\sqrt 2)]/(2\sqrt 2)$ for PR. Defining a negative constant instead reverses the displayed sign; do not mix conventions.')
R('ch02','GERG_table','| GERG-2008 | `SystemGERG2004Eos` | Custody transfer natural gas |','| GERG-2008 | Java gas-phase GERG property methods after a supported flash | Natural-gas reference properties within its composition/state domain |')
S('ch02','GERG_uncertainty',r'For custody transfer and fiscal metering.*?However, it is limited to defined natural gas components \(21 species\) and is not suitable for reservoir fluid modeling with heavy fractions\.',r'''GERG-2008 is a Helmholtz-energy mixture model covering21 defined natural-gas components, including gas, liquid and supercritical states in its published domain. Its uncertainty varies with property, composition and temperature/pressure region; the primary paper supplies the applicable ranges. It does not accept arbitrary petroleum pseudo-components. A density property call after an SRK flash does not turn that flash into a GERG phase-equilibrium calculation or establish fiscal compliance.\cite{kunz2012}''')
S('ch02','GERG_selection',r'For the highest possible accuracy.*?cannot handle C\$_7\$\+ pseudo-components\.', 'Check the contractually specified property method and composition/state range. The example uses the Java GERG-2008 gas-property calculation; the legacy `SystemGERG2004Eos` has separate native-library requirements. Agreement with a gas-density reference is not automatic ISO conformity of a complete metering system.')
R('ch05','Turner_SI',r'v_{cr} = 1.593',r'v_{cr} = 6.56')
S('ch05','Turner_scope',r'For water in natural gas at typical conditions.*?depending on pressure\.',r'''The coefficient6.56 is the SI conversion of the commonly used1.91 field-unit droplet-screening form, including its approximate20% empirical uplift; without that uplift the coefficient is about5.46. The field expression uses ft/s, dyn/cm and lb/ft³ and must not be paired with the SI definitions above. For $\sigma=0.06$N/m, $\rho_l=1000$kg/m³ and $\rho_g=50$kg/m³, the uplifted SI expression gives2.55m/s. This is a vertical droplet-screening model, not a general criterion for film reversal, deviated wells or transient unloading.\cite{turner1969}''')
R('ch05','gravel_skin',r'S_{gp} = \frac{k}{k_{gp}} \ln\frac{r_{gp}}{r_w}',r'S_{gp} = \left(\frac{k}{k_{gp}}-1\right)\ln\frac{r_{gp}}{r_w}')
R('ch05','gravel_interpretation','**Gravel pack (GP):**','For an annulus replacing formation material, the incremental skin relative to the original formation is $(k/k_{gp}-1)\ln(r_{gp}/r_w)$. If the pack is an additional serial resistance, use the full pack resistance instead; perforation/convergence damage is a separate contribution.\n\n**Gravel pack (GP):**')
S('ch07','tree_geometry',r'\| Feature \| Vertical Tree \| Horizontal Tree \|.*?simplifying intervention operations\.',r'''| Feature | Conventional vertical tree | Conventional horizontal tree |
|---------|----------------------------|------------------------------|
| Production master valves | In the vertical production bore | In lateral production bores |
| Tubing hanger | In the wellhead below the tree | In the tree body |
| Installation sequence | Hanger/tubing before tree | Tree before hanger/tubing |
| Tree retrieval | Tree can normally be removed above the landed hanger | Normally requires tubing/hanger retrieval first |
| Tubing intervention | Requires the configured vertical access/barrier arrangement | Tubing can be retrieved through the tree without first removing it |

These are conventional configurations; vendor variants and barrier requirements determine the actual installation and intervention sequence. Water depth, cost and pressure rating alone do not select a tree type.\cite{foundationIADCtree}''',sources=['https://iadclexicon.org/horizontal-tree/','https://www.onesubsea.slb.com/products-and-services/subsea-field-development/subsea-production-systems/subsea-trees'])
R('ch07','distance_economics','Satellite wells are uneconomic beyond ~15 km due to per-well flowline costs; cluster manifolds become advantageous for longer tiebacks','Compare the extra flowlines, shared-capacity limits and intervention strategy; there is no universal15km economic cutoff')
R('ch08','annular_fourthroot',r'3.1 \sqrt{\frac{\sigma g (\rho_L - \rho_G)}{\rho_G^2}}^{0.25}',r'3.1 \left[\frac{\sigma g (\rho_L - \rho_G)}{\rho_G^2}\right]^{1/4}')
R('ch08','BB_whole_numerator',r'\frac{dP}{dL} = \frac{f_{tp} \, \rho_n \, v_m^2 / (2D)}{1 - \rho_s \, v_m \, v_{SG} / P} + \rho_s \, g \sin\theta',r'-\frac{dP}{dL} = \frac{f_{tp}\rho_n v_m^2/(2D)+\rho_s g\sin\theta}{1-\rho_s v_m v_{SG}/P}')
R('ch08','riser_pressure_sign','a substantial pressure increase from the riser base to the topside','a substantial pressure decrease from the riser base to the topside in upward flow')
S('ch08','thermal_length',r'This exponential decay means.*?\$\\tau \\approx 31\$ km\.',r'''For the stated constant-property model, the characteristic cooling length is $L_T=\dot m c_p/(\pi DU)$, not a time constant. With $\dot m=80000/3600$kg/s, $c_p=2200$J/(kgK), $D=0.254$m and $U=5$W/(m²K), $L_T=12.25$km. Use the same diameter/area basis for $U$. This temperature law neglects pressure-work/JT effects, phase changes and axial conduction.''')
S('ch08','JT_range',r'\\mu_\{JT\} = \\left\(\\frac\{\\partial T\}\{\\partial P\}\\right\)_H \\approx .*?for natural gas\}',r'\mu_{JT}=\left(\frac{\partial T}{\partial P}\right)_h')
S('ch08','slug_criterion',r'The Pots criterion for severe slugging:.*?(?=### 8\.9\.4)',r'''A severe-slugging boundary compares the rate of gas-pressure buildup in the upstream volume with the rate at which a liquid plug raises hydrostatic head in the riser. It therefore requires phase flow rates, compressible gas inventory, pipe/riser geometry, downstream pressure and a closure for liquid holdup. A dimensionless ratio of static pressure to hydrostatic head alone cannot distinguish a stable high-rate case from a low-rate oscillation.

Use a documented transient or linear-stability model and state its closure and boundary conditions. A steady Beggs–Brill profile can supply a base state, but cannot establish slug amplitude, period or a universal stable gas-lift rate.

''')
R('ch08','slug_lift_criterion','The minimum gas lift rate required to prevent severe slugging can be estimated from the Pots stability criterion: sufficient gas must be supplied to ensure $\Pi_{SS} > 1$ at all times.','Determine the stabilizing gas-lift range with the selected transient/stability model and check the extra friction and compression duty. Confirm the operating range against measured riser behavior; no universal static-pressure ratio guarantees stability.')
R('ch08','actual_gas_flow','Q_actual = Q / (24 * 3600) * (1.01325 / 120.0) * (273.15 + 25.0) / 273.15  # actual m3/s','''# NeqSim Sm3 uses 15 C and 1.01325 bara. Convert through the EOS, including Z.
reference = gas.clone()
reference.setTemperature(288.15)
reference.setPressure(1.01325)
ThermodynamicOperations(reference).TPflash()
reference.initProperties()
assert reference.getNumberOfPhases() == gas.getNumberOfPhases() == 1
mass_rate = Q / 86400.0 * reference.getDensity("kg/m3")
Q_actual = mass_rate / rho''')
R('ch08','pipeline_linear_limit','print(f"Pressure drop: {dP_bar:.1f} bar over {L/1000:.0f} km")','''print(f"Inlet-property screening drop: {dP_bar:.1f} bar over {L/1000:.0f} km")
assert rho > 0 and mu > 0 and Re > 4000 and 0 < f < 0.1
assert 0 < dP_bar < gas.getPressure("bara")
# Finite pressure changes require distributed compressible-flow integration.
print(f"Screening drop/inlet pressure: {dP_bar / 120.0:.3f}")''')
R('ch09','hammerschmidt_units','(1,297 for MEG; 2,335 for methanol)','(1,297 for both MEG and methanol with depression in °C;2,335 belongs to the °F convention)')
S('ch09','hammerschmidt_table',r'This gives approximate required concentrations:.*?(?=### 9\.3\.3)',r'''Rearranging gives $w=100\Delta T M_i/(1297+\Delta T M_i)$. For an illustrative10°C depression it gives32.4wt%MEG and19.8wt%methanol. The GPSA SI erratum explicitly specifies1297 for both compounds.\cite{foundationGPSAerrata} This low-order aqueous-phase estimate does not include vapor/hydrocarbon partitioning, salinity, inhibitor concentration limits or freeze/viscosity constraints. The injected concentration and flow must satisfy an overall inhibitor/water balance; use a suitable equilibrium model and data before extrapolating to concentrated solutions.

''',sources=['https://www.gpamidstream.org/wp-content/uploads/2025/08/Errata-SI_07-13.pdf'])
R('ch09','methanol_recovery','Cannot be practically recovered (consumed)','Can be recovered by appropriate separation/distillation, but losses and recovery economics often favor once-through injection')
R('ch09','vdWP_reference',r'- $\nu_i$ is the number of type $i$ cages per water molecule',r'- $\Delta\mu_w^H=\mu_w^{empty}-\mu_w^{hydrate}$ is the positive empty-lattice minus occupied-lattice reference difference in this equation'+'\n'+r'- $\nu_i$ is the number of type $i$ cages per water molecule')
R('ch09','asphalt_path','**Pressure decreases** below the bubble point (loss of light ends that are good asphaltene solvents)','**Pressure depletion** above the bubble point can reduce asphaltene solubility; below the bubble point, gas liberation changes the liquid composition and can promote redissolution')
S('ch09','deboer_reverse',r'\| \$\\Delta P\$ \(bar\).*?Fields above the empirical trend line are more susceptible to asphaltene problems\.',r'''The original screening trend associates greater susceptibility with light, low-density oils that are strongly undersaturated with gas; heavier oils near their bubble point can be less susceptible despite higher asphaltene content. A rectangular low/medium/high table reverses and oversimplifies that trend. Use the original chart and measured live-oil density, saturation pressure and precipitation-onset data; pressure undersaturation alone is not a precipitation criterion.\cite{deboer1995}''',sources=['https://doi.org/10.2118/24987-PA'])
R('ch09','erosion_mass_ratio',r'E = K \cdot F(\alpha) \cdot v_p^n \cdot m_p',r'E=K F(\alpha)v_p^n')
R('ch09','erosion_def','- $E$ is the erosion rate [kg/kg]','- $E$ is the eroded-target mass per impacting-sand mass [kg/kg], not a rate')
R('ch09','erosion_mass_rate','- $m_p$ is the particle mass [kg]','- $\dot m_p$ is the impacting-sand mass rate [kg/s] used below')
R('ch09','erosion_wallrate',r'v_p^n \cdot m_p \cdot G',r'v_p^n \cdot \dot m_p \cdot G')
