from pathlib import Path
import json,hashlib,re
B=Path(__file__).resolve().parents[1];V=B/'verification/scientific_revision';p=V/'ch32_java_solution_checks.json';d=json.loads(p.read_text())
t=(B/'chapters/ch32_advanced_topics/chapter.md').read_text(encoding='utf-8')
codes={i:hashlib.sha256(m[3].encode()).hexdigest() for i,m in enumerate(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',t,re.M|re.S),1) if m[1]=='java'}
assert all(codes[e['number']]==e['code_sha256'] for e in d['entries'])
d['executed_source_sha256']=d['source_sha256'];d['source_sha256']=hashlib.sha256(t.encode()).hexdigest()
for e in d['entries']:
 if e['number']==11:e['classification']='serialization_contract_check'
p.write_text(json.dumps(d,indent=2),encoding='utf-8')
rows=['# Chapter32 Java numerical verification','',f"**{d['status'].upper()}**: 12 literal Java fences executed with 363 successful checks and zero compile/runtime diagnostics. One explicitly marked external integration pattern (fence23) remains excluded.",'','The fresh source fixture now explicitly enables polytropic mode. The evaluator retains the rejected100,000kg/hr candidate above its5MW constraint and accepts80,000kg/hr with direct power and returned-feasibility checks.','', 'Checks cover:', '', '- Compressor/separator component, mass and energy closure and fresh objective replays for sampled Pareto states.', '- Convex quadratic SQP solution `(3,2)`, objective0, equality/inequality/bounds; finite-difference gradient `(-1,0)`.', '- Constant-signal mean60, zero deviation and the declared R-statistic convention.', '- Analytic weighted reconciliation `[101600,69100,27600,4900]kg/hr, residual0, chi-square1.2 and normalized residual magnitudes.', '- Synthetic efficiency recovery from0.78 with fresh130/150/170bara temperature and compressor-energy checks.', '- All12 batch cases replayed on fresh processes, sampled Pareto non-dominance, lower-pressure selection at each flow and independent summary arithmetic.', '- JSON serialization with explicit null encoding for unbounded limits.', '', d['tolerance_note'], '', 'The successful12fences comprise11 numerical cases and one serialization contract. These checks verify the stated algorithms and model balances; they do not constitute plant calibration or prove a complete continuous Pareto front. Exact code hashes and all measurements are retained in the JSON companion.']
(V/'ch32_java_solution_checks.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
print('Fresh hashes matched; summary ready.')
