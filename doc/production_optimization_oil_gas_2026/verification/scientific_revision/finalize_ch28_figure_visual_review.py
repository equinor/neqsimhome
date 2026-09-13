"""Record completed actual-image inspection; fail on stale source/image evidence.

The reviewing agent viewed all three actual images and re-viewed the final uniform
surface after removing the misleading facet-mean colorbar. Running this script
does not itself perform visual inspection of changed images.
"""
from pathlib import Path
import hashlib,json,sys,re,datetime
B=Path(__file__).resolve().parents[2];sys.path.insert(0,str(B/'.build/python_packages'))
from PIL import Image
OUT=Path(__file__).resolve().parent
manifest=OUT/'ch28_literal_solution_figure_data.json';d=json.loads(manifest.read_text(encoding='utf-8'))
report=OUT/'ch28_solution_checks.json';r=json.loads(report.read_text(encoding='utf-8'));assert r['all_targeted_checks_passed']
C=next((B/'chapters').glob('ch28_*/chapter.md'));text=C.read_text(encoding='utf-8-sig')
fences=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',text,re.M|re.S))
notes={21:['All five computed markers are visible on the logarithmic GOR axis. Density units are kg/m3; equilibrium bulk density is explicitly distinguished from pipe holdup density.','Monotone decrease 187.2664 to 47.7679 kg/m3 reconciles to all five saved values. No fabricated intermediate points or hidden domain gaps.','Title states 80 C, 50 bara and WC 10%; caption gives the standard reference and recipe basis. Labels and tick marks are readable with no overlap or cropping.'],22:['All six black solution markers are visible. Mass rate uses 1000 kg/hr, outlet and inlet pressure use bara. Uniform translucent shading connects samples; no misleading pressure colorbar remains.','Height spans the actual 75.4297 to 119.9023 bara source values. The lower-middle sampled pressure and nonmonotonic rate direction are retained.','Axes and title have room; pressure label is readable. Caption explains sparse visual interpolation and 1 bar bracketing tolerance without claiming interpolation calibration.'],23:['Both GOR 300 and GOR 1000 curves have three visible markers and a readable legend. X is mixture mass rate; both y and stated outlet pressure use bara.','GOR 1000 values 119.9023,105.0781,117.3242 bara match source arrays. GOR 300 values and 5% water cut also reconcile. No forced monotonic trend.','Caption explains equal mixture mass-rate basis, holdup/friction competition, and limits of economic interpretation. No cropped title, axes or legend.']}
for row in d['figures']:
 p=B/row['path'];digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest==row['sha256']
 assert hashlib.sha256(fences[row['fence']-1][3].encode()).hexdigest()==row['literal_code_sha256']
 assert hashlib.sha256(report.read_bytes()).hexdigest()==row['source_array_evidence_sha256']
 assert row['caption'] in text and row['discussion'] in text
 with Image.open(p) as im:size=list(im.size);dpi=im.info.get('dpi')
 row.update(visual_review_status='passed',dimensions_px=size,dpi=dpi,inspection='Actual image viewed by reviewing agent at full available resolution',findings=notes[row['fence']],unresolved_material_defects=[])
summary={'status':'passed','review_method':'Visual inspection by the reviewing agent, with exact literal-code/source-array/image hash reconciliation; no human peer certification implied.','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'images_inspected':3,'repaired_material_defects':['Removed ambiguous 3D facet-mean colorbar; retained explicit six solution markers and pressure-height axis.'],'chapter_sha256':hashlib.sha256(C.read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'figures':d['figures']}
(OUT/'ch28_literal_solution_figure_review.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
md=['# Chapter 28 actual literal-figure visual review','','Passed: all three actual manuscript figures were viewed by the reviewing agent and reconciled to current source and numerical evidence. This is an agent visual review, not human or field peer certification.','']
for row in d['figures']:
 md+=['## '+row['filename'],'',row['caption'],'',f"Image SHA-256: `{row['sha256']}`; dimensions: {row['dimensions_px']}; source fence {row['fence']}.",'']+['- '+n for n in row['findings']]+['']
md+=['The 35 frozen notebooks and prior figure-review ledgers were not modified. No unresolved material image defect remains.']
(OUT/'ch28_literal_solution_figure_review.md').write_text('\n'.join(md),encoding='utf-8')
print('3 actual figures: visual and data review passed')
