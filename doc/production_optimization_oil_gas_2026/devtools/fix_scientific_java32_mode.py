from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1]
p=B/'chapters/ch32_advanced_topics/chapter.md';t=p.read_text(encoding='utf-8')
backup=B/'.build/scientific_java32_original';backup.mkdir(exist_ok=True)
if not (backup/'chapter.md').exists():(backup/'chapter.md').write_text(t,encoding='utf-8')
old='compressor.setPolytropicEfficiency(0.78);\nProcessSystem process = new ProcessSystem();'
new='compressor.setPolytropicEfficiency(0.78);\ncompressor.setUsePolytropicCalc(true);\nProcessSystem process = new ProcessSystem();'
if old in t:p.write_text(t.replace(old,new,1),encoding='utf-8')
(B/'verification/scientific_revision/ch32_java_corrections.json').write_text(json.dumps([{'issue':'Java Pareto fixture set polytropic efficiency without activating polytropic mode, unlike corresponding Python case.','correction':'Set usePolytropicCalc true explicitly before process run.','source':'Compressor.java usePolytropicCalc defaults false; fixed source6cc8026','before':old,'after':new}],indent=2),encoding='utf-8')
