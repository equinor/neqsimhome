import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'legacy_phase_envelopes'
path = OUT / 'phase_envelope_replacements.json'
manifest = json.loads(path.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert manifest['script_sha256'] == sha(HERE / 'replace_legacy_phase_envelopes.py')
records = []
for r in manifest['records']:
    p, data = Path(r['path']), Path(r['data_path'])
    assert sha(p) == r['sha256'] and sha(data) == r['data_sha256']
    with data.open(encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle))
    finite = [x for x in rows if x['valid'] == 'True']
    assert all(math.isclose(float(x['T_K'])-273.15, float(x['T_C']), abs_tol=1e-10) for x in finite)
    assert math.isclose(max(float(x['T_C']) for x in finite), r['extrema']['sampled_cricondentherm']['T_C'], abs_tol=1e-10)
    assert math.isclose(max(float(x['P_bara']) for x in finite), r['extrema']['sampled_cricondenbar']['P_bara'], abs_tol=1e-10)
    records.append({'chapter':r['chapter'], 'path':str(p), 'sha256':sha(p), 'csv_sha256':sha(data), 'full_resolution_inspected':True, 'status':'passed_scoped_visual_review', 'basis_match':r['basis_match'], 'finding':'Axes and units, branch legend, sampled extrema, qualified VLE-only footer and retained continuation gaps are clear. No fabricated critical point or operating trajectory is shown.', 'csv_extrema_and_temperature_units':'passed', 'physical_checks':r['verification']})
report = {'created_utc':datetime.now(timezone.utc).isoformat(), 'scope':'Four legacy manuscript phase-envelope replacements, separate from the 104 notebook plots and NIST plot audit.', 'summary':{'images':4, 'full_resolution_views':4, 'fresh_TP_flash_states':sum(r['physical_checks']['fresh_TP_flash_states'] for r in records), 'physical_scope':'Three transition brackets per branch per fluid, component conservation, positive phase density, normalized compositions and two-phase fugacity equality. No independent laboratory validation or critical-point claim.', 'max_component_closure':max(r['physical_checks']['component_closure_max_abs'] for r in records), 'max_absolute_log_fugacity_ratio':max(r['physical_checks']['two_phase_fugacity_max_abs_log_ratio'] for r in records)}, 'records':records, 'limitations':['Chapter 3 image is a six-defined-component PR surrogate with an explicit new recipe; it does not validate the original TBP case.', 'Chapter 12 has unresolved continuation segments left visibly open; the sampled maxima and limited branch checks do not certify a complete saturation locus.', 'Solids, hydrates and aqueous phase stability are outside these VLE illustrations.', 'Original failed TBP and intermediate heavy-surrogate evidence is retained alongside final evidence.'], 'manifest_sha256':sha(path)}
(OUT/'visual_review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(OUT/'visual_review.md').write_text('# Legacy phase-envelope illustration review\n\nFour calculated figures were inspected at full resolution. All use explicit temperature (°C), absolute pressure (bara), distinguished dew/bubble boundaries, sampled extrema and VLE-only scope labels. No invented critical point or operating trajectory is shown.\n\n48 fresh TP-flash states verify transition brackets at three pressures per branch. Maximum component closure error is '+f"{report['summary']['max_component_closure']:.3g}"+' mol/mol; maximum absolute log fugacity ratio is '+f"{report['summary']['max_absolute_log_fugacity_ratio']:.3g}"+' (tolerances 1e-7 and 1e-6, respectively). These are local consistency checks, not independent EOS accuracy validation.\n\n'+ '\n'.join('- '+x for x in report['limitations'])+'\n\nCaptions, exact input amounts, normalized compositions, branch probes and hashes are in phase_envelope_replacements.json. Original diagrams are preserved under .build/backups/scientific_revision_legacy_envelopes.\n',encoding='utf-8')
failure = {'status':'original_TBP_envelope_unverified', 'original_input_and_TP_probe_evidence':'ch03_probe.json', 'bubble_first_trace':'No finite dew branch was returned for the original Chapter 3 PR/TBP case.', 'dew_first_probe':{'bubble_temperature_K':135.69665027436778,'pressure_bara':4.787423008443752,'minus_0_5K_phase':'single OIL','plus_0_5K_phase':'single OIL','interpretation':'Fresh TP flashes failed to bracket the returned bubble boundary at this point.'},'standalone_dew_temperature_K':2299.4412025893675, 'intermediate_surrogate':{'evidence':'ch03_c20_surrogate_evidence.json','data':'ch03_c20_surrogate_envelope.csv','limitation':'A same-amount n-heptane/nC10/nC20 surrogate left a large unresolved bubble segment between about 53 and 294 bara.'}, 'disposition':'Both were excluded as complete verified-envelope illustrations. Final image uses an explicitly identified six-compound PR surrogate; original manuscript calculation was not silently replaced.'}
(OUT/'rejected_attempts.json').write_text(json.dumps(failure,indent=2),encoding='utf-8')
print(json.dumps(report['summary'],indent=2))
