"""Copy source-executed Chapter 28 figures, bind numeric arrays, add discussions.

Does not regenerate or touch the frozen notebook images or their visual reports.
Visual acceptance is a separate explicit reviewing-agent step.
"""
from pathlib import Path
import hashlib,json,shutil,re
B=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
C=next((B/'chapters').glob('ch28_*'));report=OUT/'ch28_solution_checks.json'
d=json.loads(report.read_text(encoding='utf-8'));assert d['all_targeted_checks_passed']
entries={e['number']:e for e in d['entries']}
base=next(c['observed'] for c in entries[13]['checks'] if 'all 12 pressure roots' in c['name'])
density=next(c['observed'] for c in entries[21]['checks'] if c['name'].startswith('Five actual density'))
curves={gor:[p['required_inlet_bara'] for p in base if p['GOR_input']==gor and p['outlet_target_bara']==50] for gor in (300.,1000.)}
surface=[[next(p['required_inlet_bara'] for p in base if p['rate_kg_hr']==r and p['outlet_target_bara']==t and p['GOR_input']==1000.) for t in (30.,50.)] for r in (5000.,10000.,20000.)]
rows=[
 {'filename':'ch28_verified_recombination_density.png','fence':21,'caption':'Equilibrium bulk density of five actual reference-phase recombinations at 80 °C and 50 bara, with 10% standard-volume water cut. GOR is standard gas volume divided by standard oil volume; standard reference is 15 °C and 1.01325 bara.',
  'discussion':f"Density decreases from {density['density_kg_m3'][0]:.2f} to {density['density_kg_m3'][-1]:.2f} kg/m³ as the GOR mixing input rises from 200 to 5000 Sm³/Sm³. Increasing the proportion of reference gas lowers the equilibrium bulk density for this recipe. A pipe calculation still needs slip-dependent liquid holdup; substituting this bulk density for the flowing hydrostatic density would omit that effect. The independently reconstructed component inventory and a fresh standard flash confirm the requested liquid-rate, GOR and water-cut basis for all five samples.",
  'data':density,'insert_before':'### 28.9.2 Plotting VFP Surfaces'},
 {'filename':'ch28_verified_screening_surface.png','fence':22,'caption':'Six actual required-inlet-pressure samples at 5% water cut and GOR 1000 Sm³/Sm³ for the Python model: 2800 m upward tubing and 12 km horizontal flowline. Black markers identify the solved grid values; the connecting facets are a visual interpolation.',
  'discussion':f"The six required inlet pressures range from {min(v for r in surface for v in r):.2f} to {max(v for r in surface for v in r):.2f} bara over 5000–20,000 kg/hr and 30–50 bara outlet pressure. Every marker meets its outlet target in a fresh process replay, while reducing its inlet pressure by the declared 1 bar search width drops below the target. Height represents pressure; the uniform surface shade only connects the samples. A surface drawn through six points does not establish interpolation accuracy between them; refine the grid and compare measured pressure losses before reservoir coupling.",
  'data':{'flow_kg_hr':[5000.,10000.,20000.],'outlet_bara':[30.,50.],'required_inlet_bara':surface,'watercut':.05,'GOR_Sm3_Sm3':1000.},'insert_before':'### 28.9.3 Multi-Scenario Comparison'},
 {'filename':'ch28_verified_gor_pressure.png','fence':23,'caption':'Two actual GOR scenarios for the same 2800 m upward tubing and 12 km flowline, at 5% water cut and 50 bara outlet pressure. Points are accepted pressure-table solutions; lines connect the sampled cases.',
  'discussion':f"At GOR 1000, required inlet pressure changes from {curves[1000.][0]:.2f} to {curves[1000.][1]:.2f} and then {curves[1000.][2]:.2f} bara as mass rate rises from 5000 to 10,000 and 20,000 kg/hr. The nonmonotonic response is retained: multiphase lift balances changing liquid holdup against friction, so increasing rate need not always increase the required pressure. GOR 300 requires {min(curves[300.]):.2f}–{max(curves[300.]):.2f} bara in these samples. This is a comparison at equal mixture mass rate, not equal stock-tank oil or gas production; use a common economic production basis before selecting an operating strategy.",
  'data':{'flow_kg_hr':[5000.,10000.,20000.],'GOR_300_inlet_bara':curves[300.],'GOR_1000_inlet_bara':curves[1000.],'outlet_bara':50.,'watercut':.05},'insert_before':'## 28.10 Quality Assurance and Validation of VFP Tables'}]
s=(C/'chapter.md').read_text(encoding='utf-8')
for row in rows:
 src=B/'.build/solution_runs'/C.name/'figures'/row['filename'];dst=C/'figures'/row['filename'];assert src.exists()
 shutil.copy2(src,dst)
 row.update(path=str(dst.relative_to(B)),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),literal_code_sha256=entries[row['fence']]['code_sha256'],source_array_evidence=str(report.relative_to(B)),source_array_evidence_sha256=hashlib.sha256(report.read_bytes()).hexdigest(),visual_review_status='pending_reviewing_agent_inspection')
 marker='<!-- ch28-literal-'+str(row['fence'])+' -->'
 content=marker+'\n\n!['+row['caption']+'](figures/'+row['filename']+')\n\n'+row['discussion']+'\n\n'
 if marker not in s:s=s.replace(row['insert_before'],content+row['insert_before'])
 else:s=re.sub(re.escape(marker)+r'.*?(?='+re.escape(row['insert_before'])+')',lambda m:content,s,flags=re.S)
(C/'chapter.md').write_text(s,encoding='utf-8')
(OUT/'ch28_literal_solution_figure_data.json').write_text(json.dumps({'figures':rows,'source':'Exact manuscript Python output, not frozen chapter notebook output'},indent=2,ensure_ascii=False),encoding='utf-8')
print('Copied and placed',len(rows),'actual literal figures; visual inspection pending')
