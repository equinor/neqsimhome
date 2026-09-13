from pathlib import Path
import re
B=Path(__file__).resolve().parents[1];p=next((B/'chapters').glob('ch30_*/chapter.md'))
t=p.read_text(encoding='utf-8-sig');matches=list(re.finditer(r'^```(?:python|java)[^\n]*\n(.*?)^```',t,re.M|re.S))
for i in [19,18,9]:
 m=matches[i-1];c=m.group(1)
 if i in [9,19]:c=c.replace('compressor.setPolytropicEfficiency(0.78)',
                            'compressor.setPolytropicEfficiency(0.78)\ncompressor.setUsePolytropicCalc(True)')
 if i==18:
  c=c.replace('"deviation_pct": (','"absolute_deviation": (abs(model_val-meas_val) if not np.isnan(meas_val) else None),\n            "deviation_pct": (')
  c=c.replace('if not np.isnan(meas_val) and meas_val != 0','if not np.isnan(meas_val) and meas_val > 0 and unit != "C"')
 if i==19:
  c=c.replace('label=\'Plant (feed T)\'','label=\'Synthetic feed temperature\'')
  c=c.replace('Digital Twin Tracking — 24-Hour Period','Synthetic input propagation through the process model')
 t=t[:m.start(1)]+c+t[m.end(1):]
p.write_text(t,encoding='utf-8')
