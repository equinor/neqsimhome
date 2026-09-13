"""Apply reviewed illustration captions and retire unsupported legacy plots.

Run only after chapter-author freeze. Code fences are preserved byte-for-byte.
The original files remain in the pre-review backup; removals affect placement,
not historical evidence. Any changed asset is withheld from automatic removal.
"""
from pathlib import Path
import hashlib,json,re
BOOK=Path(__file__).resolve().parents[1]
OUT=BOOK/'verification/scientific_revision'
initial=json.loads((OUT/'manuscript_figures/inventory.json').read_text(encoding='utf-8'))
old={(r['chapter'],Path(r['path']).name):r for r in initial}
repairs=json.loads((OUT/'illustration_repairs.json').read_text(encoding='utf-8'))
# A later companion record can add physically traced envelope assets.
envelopes=OUT/'legacy_phase_envelopes/phase_envelope_replacements.json'
if envelopes.exists():
    value=json.loads(envelopes.read_text(encoding='utf-8'))
    for row in value['records']:
        row=dict(row)
        amounts=', '.join(f'{name} {amount:g}' for name,amount in row['components'])
        row['discussion']=(f"Input relative molar amounts are {amounts}, normalized to mole fractions. "
            'Fresh TP flashes bracketed each saturation branch at three sampled pressures; phase amounts and density continuity determined physical branch assignment. '
            'Component closure and fugacity equality verify these computed states, but do not establish agreement with measured mixture saturation data. '
            + ('This illustration uses a different defined-compound surrogate because the original TBP-fluid trace did not pass the branch checks; it does not validate that original trace. ' if row['chapter'].startswith('ch03') else '')
            + ('The unresolved continuation interval is deliberately left open; the plotted points do not establish a complete saturation locus. ' if row['chapter'].startswith('ch12') else ''))
        row['basis']='source-backed VLE continuation with fresh TP branch checks; declared mixture and domain'
        repairs.append(row)
repair_by_key={(r['chapter'],r.get('file',Path(r['path']).name)):r for r in repairs}
remove={
 (3,'fluid_type_phase_envelopes.png'):'Hand-drawn envelopes do not establish thermodynamic fluid classifications or critical loci. The chapter has a checked, explicitly defined illustrative envelope and executed PVT results.',
 (3,'separator_test.png'):'Invented separator-test points and an unsupported optimum are not laboratory evidence; the executed chapter calculations provide the numerical results.',
 (5,'pressure_traverse.png'):'Identical manufactured pressure traces were presented as flow-dependent well solutions; use the executed nodal/hydraulic results.',
 (7,'tieback_distance_analysis.png'):'Manufactured pressure/temperature curves and an unsupported fixed hydrate threshold do not define tieback feasibility.',
 (8,'flow_regimes.png'):'Rectangular region boundaries are not a valid multiphase flow-regime correlation.',
 (8,'pipeline_pt_profiles.png'):'Manufactured profiles conflict with the caption distance and do not match the executed hydraulic case.',
 (9,'hydrate_phase_envelope.png'):'The drawn inhibitor curve shifts in the physically wrong direction. Retain the executed inhibitor calculations and their stated limitations.',
 (9,'flow_assurance_envelope.png'):'Unsupported fixed hydrate/wax boundaries and a universal safe-window label are replaced by case-specific computed results and separate risk discussion.',
 (19,'gas_quality_envelope.png'):'Invented acceptance envelope incorrectly implies ISO6976 establishes a gas-quality contract.',
 (26,'fig27_3_gaslift_curve.png'):'Equal per-well injection curves and their sum were falsely labeled an allocation optimum.',
}
caption_updates={
 (1,'topside_process_schematic.png'):('Conceptual gas and liquid processing paths after inlet separation','This overview groups equipment functions. A detailed staged separation model must account for every gas and liquid outlet and for pressure matching before mixing streams.'),
 (1,'optimization_workflow.png'):('Conceptual sequence from objective and model definition to search and result verification','Calibration data and independent validation evidence are separate inputs to the modeling work. A proposed operating point still requires the physical and constraint acceptance checks developed later in the book.'),
 (3,'fluid_characterization_workflow.png'):('Conceptual fluid-characterization workflow linking samples, composition, EOS parameters and validation','Keep data used for parameter fitting separate from holdout or independent validation data. Characterization is an inference from the stated sample and assay; this workflow diagram is not evidence that a particular fluid has been calibrated.'),
 (4,'ipr_curves.png'):('Illustrative inflow-correlation shapes with separately assigned parameters','These curves illustrate alternative inflow functional forms. Their parameter choices are synthetic and do not represent three calibrated models for the same well.'),
 (4,'pz_plot.png'):('Analytical straight-line p/Z material-balance illustration for a specified volumetric gas reservoir','The straight line is an assumed idealized material-balance relation. Its intercept and abandonment cut-off illustrate how resource and recovery estimates differ; real interpretation needs consistent standard-volume data, reservoir-average pressure, Z and the reservoir drive assumptions.'),
 (4,'decline_curve.png'):('Illustrative exponential, hyperbolic and harmonic rate histories over 20 years','The curves compare specified Arps forms and an assumed economic cut-off. They show rate, not cumulative production, and are not history-matched resource or reserve estimates.'),
 (5,'gas_lift_performance.png'):('Illustrative saturating gas-lift response with an assumed screening point','The response is a specified teaching correlation. The marked point requires an explicit gas-cost or constraint basis before it can be interpreted as an economic optimum; use the checked allocation examples for an actual optimization calculation.'),
 (5,'vfp_curves.png'):('Illustrative pressure-rate curves at four assumed wellhead pressures','The parallel curves illustrate an imposed boundary-pressure shift. They are not calculated or measured VFP tables; the executed well examples include hydraulic solution checks and an explicit operating domain.'),
 (5,'nodal_analysis.png'):('Illustrative nodal intersection for specified inflow and outflow curves','The plotted intersection illustrates the common-node pressure condition. It is not a measured well test or a calibrated production forecast; the chapter notebook solves the declared hydraulic case separately.'),
 (7,'subsea_field_layout.png'):('Conceptual manifold-centered subsea tieback layout','The wells connect to a common manifold and a trunk line to the host. This is a hub layout, not a daisy-chain topology; line lengths, elevations and pressure-loss models are needed for hydraulic analysis.'),
 (7,'surf_cost_breakdown.png'):('Illustrative allocation of an assumed 720 MNOK SURF budget','The slices are assigned teaching inputs, not vendor quotations or a cost estimate for a specified development. Use a dated quantity and cost basis, installation scope and uncertainty model for investment analysis.'),
 (8,'pipeline_system_overview.png'):('Conceptual sequence of wellhead, flowline, riser, receiving and separation functions','The printed dimensions and inlet pressure are schematic inputs. This block diagram is not a cross-section or an accepted hydraulic sizing result.'),
 (8,'flowline_riser_profile.png'):('Illustrative seabed and riser elevation profile relative to sea level','The negative vertical coordinate denotes elevation below sea level. This is a geometric sketch, not a pressure/temperature profile; it must be supplied to a hydraulic and thermal calculation.'),
 (15,'compressor_map_overview.png'):('Specified speed-curve family illustrating centrifugal-compressor map terminology','The curves and vertical boundary markers are schematic. They are not vendor data or a qualified operating envelope; installed-map limits vary with speed and gas conditions.'),
 (15,'operating_envelope.png'):('Illustrative pressure-flow bounds and two assumed operating points','The shaded region is a conceptual constraint window. No speed lines or constant-efficiency contours are shown, and the figure does not establish installed-machine limits.'),
 (16,'shell_tube_hx_cross_section.png'):('Schematic circular shell cross-section with an illustrative tube arrangement','The drawing identifies a shell, tubes and baffle concepts. It does not specify a complete TEMA construction, dimensions, tube count for a design, or a calculated heat-transfer area.'),
 (18,'power_demand_profile.png'):('Specified power-demand scenario with an assumed 50 MW supply limit','Compression, injection and utility loads are assigned scenario components on the plotted production axis. The crossing illustrates a shared-resource constraint; no driver sizing or validated facility energy forecast follows from these assumed curves.'),
 (20,'separator_capacity_diagram.png'):('Conceptual gas/liquid capacity trade-off and assumed operating points','The boundary is an illustrative constraint shape, not a computed gas-velocity field or liquid-retention design. A real envelope needs phase densities, vessel geometry, internals, level and both gas and liquid performance limits.'),
 (20,'capacity_staircase.png'):('Assumed individual equipment capacities on one common production basis','Bars compare independent equipment ceilings at the same reference production basis. They do not represent a sequential series of completed debottlenecking projects.'),
 (20,'utilization_trend_field_life.png'):('Specified utilization scenario over a hypothetical field lifecycle','The plateau and decline are assigned teaching trajectories. They illustrate time-dependent capacity demand and are not forecasts from a calibrated reservoir or facility model.'),
 (22,'nodal_analysis_operating_point.png'):('Illustrative common-node intersection of specified inflow and outflow functions','The point solves the pressure equality for the plotted synthetic curves. Physical well prediction needs calibrated inflow, tubing and boundary conditions; do not interpret this sketch as a field optimization result.'),
 (23,'fig25_1_architecture.png'):('Conceptual layering of interfaces, optimization, process simulation and thermodynamic models','The drawing groups software responsibilities. Class-level interfaces and accepted evidence checks are specified in the text; this schematic is not an exhaustive dependency or deployment diagram.'),
 (23,'fig25_2_component_diagram.png'):('Conceptual interaction among process, fluid, equipment, objective, automation and result roles','Boxes denote software roles, and some labels are abstractions rather than exact class names. Use the executable API examples and recorded source revision for concrete class and method contracts.'),
 (25,'fig26_1_utilization_profiles.png'):('Assumed separator, compressor and dehydration utilization profiles','The plotted lifecycle trajectories are synthetic inputs used to explain monitoring displays. The actual rate-sweep examples calculate utilization from declared model demands and ratings.'),
 (25,'fig26_3_utilization_heatmap.png'):('Synthetic monthly equipment-utilization matrix for illustrating a monitoring display','The colors show an assigned example matrix, including overloads. No historian records or observed seasonal facility behavior are represented.'),
 (26,'fig27_1_ipr_curves.png'):('Illustrative inflow curves for three separately parameterized wells','Each curve uses assumed reservoir/inflow parameters. Their shape is not evidence of a well test, a history match or calibrated field deliverability.'),
 (26,'fig27_2_vfp_curve.png'):('Illustrative required bottomhole-pressure curves and an inflow overlay','The vertical axis is flowing BHP, not tubing-head pressure. The figure explains nodal coupling with specified synthetic curves; it is not a validated 3000 m well model.'),
 (30,'ch21_domain_architecture.png'):('Conceptual software layers for presentation, application, domain and infrastructure services','The layers separate software responsibilities. They do not replace the physical reservoir, transport and facility model boundaries or establish that every plant interface is implemented.'),
}
changes=[]
fences=re.compile(r'^```[^\n]*\n.*?^```[^\n]*(?:\n|$)',re.M|re.S)
for path in sorted((BOOK/'chapters').glob('*/chapter.md')):
    source=path.read_text(encoding='utf-8');before=fences.findall(source);n=int(path.parent.name[2:4])
    def replace(match):
        caption,target=match[1],match[2];name=Path(target).name;key=(path.parent.name,name)
        asset=(path.parent/target).resolve();digest=hashlib.sha256(asset.read_bytes()).hexdigest() if asset.is_file() else None
        if (n,name) in remove:
            prior=old.get(key)
            if prior and prior['sha256']==digest:
                changes.append(dict(chapter=path.parent.name,file=name,action='removed_unsupported_legacy_placement',reason=remove[n,name],old_sha256=digest))
                return ''
            changes.append(dict(chapter=path.parent.name,file=name,action='changed_asset_requires_manual_review',sha256=digest))
            return match[0]
        row=repair_by_key.get(key)
        if row:
            assert digest==row['sha256'], f'Asset changed after repair: {asset}'
            new_caption=row['caption'];discussion=row['discussion'];basis=row.get('basis','recorded scientific illustration')
        elif (n,name) in caption_updates:
            new_caption,discussion=caption_updates[n,name];basis='explicitly scoped conceptual illustration'
        else:return match[0]
        marker=f'<!-- scientific-illustration:{name} -->'
        # Idempotent integration; an existing block is stripped before this pass.
        changes.append(dict(chapter=path.parent.name,file=name,action='reviewed_caption_and_discussion',basis=basis,sha256=digest))
        return f'![{new_caption}]({target})\n\n{marker}\n{discussion}\n<!-- /scientific-illustration -->'
    source=re.sub(r'\n\n<!-- scientific-illustration:[^>]+-->.*?<!-- /scientific-illustration -->','',source,flags=re.S)
    source=re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',replace,source)
    assert fences.findall(source)==before, f'Code modified in {path}'
    path.write_text(source,encoding='utf-8')
(OUT/'manuscript_figure_review.json').write_text(json.dumps(dict(initial_figures=len(initial),all_initial_contact_sheets_visually_inspected=True,changes=changes),indent=2),encoding='utf-8')
print(f'Integrated {len(changes)} caption, discussion and removal decisions; code preserved.')
