"""Place three inspected exact-run figures with numerical discussion and evidence."""
from pathlib import Path
import datetime,hashlib,json,re,shutil
B=Path(__file__).resolve().parents[1];O=B/'verification/scientific_revision'
chapter=B/'chapters/ch21_debottlenecking';p=chapter/'chapter.md'
data=json.loads((O/'ch21_plot_data.json').read_text(encoding='utf-8'))
proof=json.loads((O/'ch21_solution_checks.json').read_text(encoding='utf-8'))
assert proof['all_targeted_checks_passed']
names={25:'waterfall_debottleneck',31:'utilization_dashboard',32:'bottleneck_sensitivity'}
captions={
25:('Conditional rate changes from three declared constraint relaxations',
    '**Observation.** The screened rate changes from 200,000 to 219,128 kg/hr when the speed limit is omitted. Omitting the duplicate power check alone adds zero; omitting ratedPower then reaches 227,772 kg/hr, a conditional 13.9% increase.\n\n**Mechanism.** Different enabled checks bind as the candidate rate rises; the two driver-power constraints describe overlapping restrictions. Every selected state was rebuilt at the original sizing basis and compared with a 51-point rate grid.\n\n**Engineering implication and recommendation.** The scan stops before removing the separator’s last active constraint. These rates rank assumed omissions; they are not installed-capacity or retrofit guarantees. Obtain actual ratings, implement a physical modification and restore all applicable limits before accepting a production increase.'),
31:('Capacity percentages after solving the generated screening compressor map',
    '**Observation.** At the imposed 150,000 kg/hr feed, the separator reports 83.3% and the compressor 99.3% utilization.\n\n**Mechanism.** The displayed values are the maximum configured utilization for each unit. The summary API already returns percentages; multiplying them by 100 again would introduce a hundredfold reporting error.\n\n**Engineering implication and recommendation.** The compressor is close to the assumed design boundary, but its auto-generated map is a teaching input. Replace the template with the appropriate vendor map and operating envelope before treating this dashboard as an installed-equipment capacity assessment.'),
32:('Rate sweep with numerical overloads and rejected compressor-map states shown separately',
    '**Observation.** Of 20 imposed rates from 50 to 250 t/hr, 12 return the native 999% outside-map penalty. The eight numerical points span 96.1–319.5%; only the sampled 123.7–144.7 t/hr points are below 100%. Red crosses retain rejected map states at an arbitrary labeled height.\n\n**Mechanism.** A generated compressor map has a bounded operating region. Moving away from that region can violate surge, speed or stonewall limits; the penalty is a diagnostic flag rather than a measured utilization.\n\n**Engineering implication and recommendation.** Do not join invalid states into a physical performance curve or select an overloaded point. Refine any candidate interval, verify the actual active constraints and replay the state using a characterized map. This sweep does not by itself determine a feasible field rate.')}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=p.read_text(encoding='utf-8');P=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
fences=list(P.finditer(t));images=[]
for i in sorted(names,reverse=True):
    name=names[i];src=B/'.build/solution_runs/ch21_debottlenecking/figures'/(name+'.png')
    dest=chapter/'figures'/('ch21_verified_'+name+'.png');shutil.copy2(src,dest)
    caption,discussion=captions[i];m=fences[i-1]
    row=next(e for e in proof['entries'] if e['number']==i)
    assert hashlib.sha256(m[3].encode()).hexdigest()==row['code_sha256']
    placement=f'\n\n![{caption}](figures/{dest.name})\n\n{discussion}\n'
    assert dest.name not in t
    t=t[:m.end()]+placement+t[m.end():]
    images.append({'path':str(dest),'sha256':sha(dest),'source_path':str(src),'source_sha256':sha(src),
                   'literal_fence':i,'literal_code_sha256':row['code_sha256'],'caption':caption,
                   'data':data[name],'visual_inspection':'Full resolution inspected by root reviewing agent; readable labels/units, no clipping/overlap, numerical arrays and diagnostic semantics checked.'})
assert [m[3] for m in P.finditer(t)]==[m[3] for m in fences]
p.write_text(t,encoding='utf-8')
report={'status':'passed','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'method':'Exact-run assets, source-array and unit checks, full-resolution visual inspection by reviewing agent; not human peer review.',
        'check_report_sha256':sha(O/'ch21_solution_checks.json'),'plot_data_sha256':sha(O/'ch21_plot_data.json'),
        'unresolved_findings':[],'images':images}
(O/'ch21_figure_review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('Three inspected Chapter21 figures placed; code preserved.')
