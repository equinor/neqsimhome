"""Rebase a chapter freeze only after a targeted scientific correction is rerun."""
from pathlib import Path
import argparse,datetime,hashlib,json,re
B=Path(__file__).resolve().parents[1];O=B/'verification/scientific_revision'
parser=argparse.ArgumentParser()
parser.add_argument('--chapter',required=True)
parser.add_argument('--reason',required=True)
args=parser.parse_args()
p=B/'chapters'/args.chapter/'chapter.md'
ledger=json.loads((O/'optimization_review.json').read_text(encoding='utf-8'))
assert ledger['numerical_coverage_complete'] and not ledger['unresolved_solution_verification']
entry=next(r for r in ledger['chapters'] if r['chapter']==args.chapter)
assert entry['full_text_review']
text=p.read_text(encoding='utf-8')
codes=[hashlib.sha256(m[3].encode()).hexdigest() for m in re.finditer(r'^\x60\x60\x60(python|java)([^\n]*)\n(.*?)^\x60\x60\x60',text,re.M|re.S)]
checked={r.get('code_sha256',r.get('sha256')) for r in entry['entries']}
assert all(h in checked for h in codes),'Amended source lacks current per-fence verification'
snapshot_path=O/'pre_integration_source.json'
snapshot=json.loads(snapshot_path.read_text(encoding='utf-8'))
old=snapshot[args.chapter]
assert old['code_sha256']!=codes,'No numerical code amendment to record'
new={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'code_sha256':codes}
record={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'chapter':args.chapter,'reason':args.reason,'previous_freeze':old,
        'amended_verified_freeze':new,
        'scientific_ledger_sha256':hashlib.sha256((O/'optimization_review.json').read_bytes()).hexdigest(),
        'interpretation':'The prior freeze is preserved. This numerical amendment was corrected and rerun before the final source snapshot; subsequent editorial integration must leave its newly verified code unchanged.'}
target=O/(args.chapter+'_integration_scientific_amendment.json')
assert not target.exists(),'Do not overwrite historical amendment'
target.write_text(json.dumps(record,indent=2),encoding='utf-8')
snapshot[args.chapter]=new
snapshot_path.write_text(json.dumps(snapshot,indent=2),encoding='utf-8')
print('Recorded verified scientific amendment:',args.chapter)
