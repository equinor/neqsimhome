from pathlib import Path
code_path = Path(__file__).with_name('replace_legacy_phase_envelopes.py')
exec(code_path.read_text(encoding='utf-8').split('records = []')[0])
case = json.loads((OUT/'ch03_probe.json').read_text(encoding='utf-8'))['case']
out = {'case': case, 'probes': []}
for T in [130,135,136,140,145,150,160,180,200,250,300,350,400,450]:
    try:
        out['probes'].append(flash_probe(case,T,4.787423008443752))
    except Exception as exc:
        out['probes'].append({'T_K':T,'error':repr(exc)})
for method in ['bubblePointTemperatureFlash','dewPointTemperatureFlash']:
    f=new_fluid(case);f.setPressure(4.787423008443752)
    f.setTemperature(140. if method.startswith('bubble') else 450.)
    try:
        getattr(j.thermodynamicoperations.ThermodynamicOperations(f),method)()
        out[method]={'T_K':float(f.getTemperature()),'P_bara':float(f.getPressure())}
    except Exception as exc:
        out[method]={'error':str(exc)}
(OUT/'ch03_probe_replay.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
