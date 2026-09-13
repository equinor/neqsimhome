"""Read-only check of calculation evidence independent of final page placement."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1];O=B/'verification/scientific_revision'
def read(n):return json.loads((O/n).read_text(encoding='utf-8'))
physics=read('notebook_physics_review.json');bench=read('benchmark_results.json')
for names in (physics['validation_helper_sha256'],bench['hashes']):
 for name,digest in names.items():
  assert hashlib.sha256((O/name).read_bytes()).hexdigest()==digest,name
assert physics['notebooks_passed']==35 and physics['benchmark_failures']==0
assert len(bench['comparisons'])==89 and all(r['passed'] for r in bench['comparisons'])
opt=read('optimization_review.json');foundation=read('foundations_review.json')
for r in (opt,foundation):
 assert r['numerical_coverage_complete'] and not r['unresolved_solution_verification']
print('Current calculation evidence:35 notebooks,89 benchmark comparisons,complete scoped manuscript coverage; all checked helper/reference hashes match.')
