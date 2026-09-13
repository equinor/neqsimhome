"""Bounded prose-only cleanup after final image integration.

No code fences, image markup, captions, image order or assets may change.
"""
from pathlib import Path
import re,json,hashlib,datetime
B=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
paths=sorted((B/'chapters').glob('ch*/chapter.md'))
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha_text(s):return sha_bytes(s.encode('utf-8'))
before={p:p.read_bytes() for p in paths};texts={p:p.read_text(encoding='utf-8-sig') for p in paths};fixes=[]
def replace(n,old,new,reason):
 p=next(p for p in paths if int(p.parent.name[2:4])==n)
 assert texts[p].count(old)==1,(n,old[:100],texts[p].count(old))
 texts[p]=texts[p].replace(old,new)
 fixes.append({'chapter':n,'reason':reason,'before':old,'after':new})
replace(24,'This leads to the **capacity staircase** pattern (Figure 24.1), where each debottlenecking step unlocks capacity up to the next constraint.','This leads to the **capacity staircase** pattern, where each debottlenecking step unlocks capacity up to the next constraint.','Figure 24.1 is now the accepted/rejected pressure grid, not a capacity staircase.')
replace(24,'The CSV can be loaded into pandas for plotting convergence curves (Figure 24.2):','The CSV can be loaded into pandas for plotting convergence histories:','The local CSV plotting example is not the separately reproduced binary-search figure now numbered 24.2.')
replace(24,'This creates a **capacity staircase** (Figure 24.4):','This creates a **capacity staircase**, shown schematically below:','Figure 24.4 no longer exists; the following unnumbered text schematic remains.')
old='Thirty states satisfy the declared1ppm mass/component and10ppm enthalpy acceptance checks. The80bara feed/140bara discharge combination fails the material check at both rates: the native phase extraction loses0.407180kg/h at250t/h and0.570052kg/h at350t/h, or2.345ppm.'
new='Thirty states satisfy the declared 1 ppm mass/component and 10 ppm enthalpy acceptance checks. The 80 bara feed/140 bara discharge combination fails the material check at both rates: the native phase extraction loses 0.407180 kg/h at 250 t/h and 0.570052 kg/h at 350 t/h, or 2.345 ppm.'
replace(24,old,new,'Restore missing spaces between prose numbers, units and adjacent words; numerical values unchanged.')
replace(26,'''The curve has three important regions:

1. **Low injection rate:** Each unit of injected gas produces a significant increment of oil. The gas lift is highly efficient.
2. **Optimal injection rate:** The point of maximum economic return, balancing the value of incremental oil against the cost of compression for the lift gas.
3. **High injection rate:** Diminishing returns — additional gas produces minimal incremental oil. Beyond a critical rate, friction effects from excessive gas velocity actually reduce oil production.''','''Economic selection additionally requires the value of incremental oil and an explicit lift-gas cost or shared-supply constraint. The monotone exponential alone does not locate a finite production maximum.''','Remove the deleted gas-lift diagram\'s three-region narrative, which contradicted the explicitly monotone equation.')
replace(26,'Because the optimizer equalizes `incrementalSlope` across wells, the allocation it returns satisfies the equal-slope optimality condition derived above.','Check the returned allocation against the equal-slope conditions and bounds; the tabulated example above demonstrates why the native candidate must be checked independently.','Remove a stale unconditional optimality guarantee that contradicted the immediately preceding rejected native allocation.')
replace(33,'The diagram shows possible areas and material paths. It is a process concept, not the exact simulated flowsheet in Section 33.10. The worked model declares its narrower dry-hydrocarbon boundary and accounts for every product crossing that boundary.','Section 33.10 specifies the dry-hydrocarbon feed and the operating assumptions for this diagram\'s four-product calculation boundary.','The replacement block diagram now represents the executed dry-hydrocarbon model; old generic-diagram prose was contradictory and duplicated the new caption discussion.')
replace(33,'This conceptual diagram shows where heat recovery and fractionation can enter a plant. The worked model represents precooling as an external cooler, provides a knockout before the expander and accounts for its liquid bypass. It credits no gas-gas heat recovery or automatic shaft coupling.','The worked model represents precooling as an external cooler, provides a knockout before the expander and accounts for its liquid bypass. It credits no gas-gas heat recovery or automatic shaft coupling.','Remove the old topology description of heat recovery/fractionation absent from the replacement gas-only expansion diagram.')
code_re=re.compile(r'^```[^\n]*\n.*?^```',re.M|re.S);img_re=re.compile(r'!\[[^\n]*\]\([^\n]+\)')
proof=[];backup=B/'.build/backups/final_editorial_optimization';backup.mkdir(parents=True,exist_ok=True)
for p in paths:
 old=before[p].decode('utf-8-sig').replace('\r\n','\n');new=texts[p]
 assert code_re.findall(old)==code_re.findall(new),('code changed',p)
 assert img_re.findall(old)==img_re.findall(new),('figure markup changed',p)
 changed=old!=new
 if changed:
  saved=backup/(p.parent.name+'.md');assert not saved.exists(),saved
  saved.write_bytes(before[p]);p.write_text(new,encoding='utf-8')
 proof.append({'chapter':int(p.parent.name[2:4]),'path':str(p.relative_to(B)),'before_sha256':sha_bytes(before[p]),'after_sha256':sha_bytes(p.read_bytes()),'changed':changed,'all_code_fences_unchanged':True,'all_image_caption_markup_and_order_unchanged':True,'code_fences_sha256':sha_text('\n'.join(code_re.findall(new))),'image_markup_sha256':sha_text('\n'.join(img_re.findall(new)))})
images=[];refs=[];label_set=set()
for p in paths:
 n=int(p.parent.name[2:4]);text=texts[p];plain=code_re.sub(lambda m:'\n'*m[0].count('\n'),text)
 for index,m in enumerate(re.finditer(r'!\[([^\n]*)\]\(([^\n]+)\)',plain),1):
  caption,path=m.groups();number=re.match(r'Figure (\d+\.\d+):',caption)
  assert number and number[1]==f'{n}.{index}' and number[1] not in label_set
  label_set.add(number[1]);target=(p.parent/path).resolve();assert target.is_file()
  images.append({'chapter':n,'label':number[1],'path':str(target.relative_to(B)),'caption':caption,'image_sha256':sha_bytes(target.read_bytes())})
 for line_no,line in enumerate(plain.splitlines(),1):
  if line.lstrip().startswith('!['):continue
  for m in re.finditer(r'\b(?:Figure|Fig\.)\s+(\d+\.\d+)\b',line):refs.append({'chapter':n,'line':line_no,'label':m[1],'text':line})
for row in refs:assert row['label'] in label_set,row
notebooks=json.loads((B/'verification/notebook_figure_updates.json').read_text(encoding='utf-8'))
for row in notebooks:
 p=B/'chapters'/row['chapter']/'chapter.md'
 assert sum(Path(im['path']).name==row['figure'] and im['chapter']==row['chapter_number'] for im in images)==1,row['figure']
result={'status':'passed','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':{'detailed_figure_adjacent_prose_review_chapters':list(range(19,36)),'caption_placement_and_reference_check_chapters':list(range(1,36)),'placed_figures':len(images),'notebook_figures_placed_exactly_once':len(notebooks),'changes_allowed':'Only necessary prose; no code, image, caption, label or ordering changes.'},'fixes':fixes,'source_hashes_and_preservation_proof':proof,'final_figure_placements':images,'all_prose_numbered_figure_references':refs,'retained_intentional_repetition':['Chapter 30 repeats external historian prerequisites immediately before separately scoped integration patterns; these are necessary local prerequisites, not duplicated figure captions.'],'removed_asset_checks':{'ch19_gas_quality_envelope':'No remaining source placement or dangling image-specific discussion.','ch26_gaslift_curve':'Removed image remains unplaced; obsolete three-region narrative corrected.'},'limitations':['This pass checks editorial placement and consistency, not a new execution or visual-physics review of the already verified images.','Figure numbers inside frozen code-generated titles are not changed; manuscript prose no longer points at their obsolete numbering.'],'unresolved_editorial_placement_defects':[]}
(OUT/'final_editorial_optimization.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'fixes':len(fixes),'changed_chapters':[r['chapter'] for r in proof if r['changed']],'figures':len(images),'notebook_figures':len(notebooks),'all_code_and_caption_markup_unchanged':True}))
