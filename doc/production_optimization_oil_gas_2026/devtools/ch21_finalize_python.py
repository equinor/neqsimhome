from pathlib import Path
B=Path(__file__).resolve().parents[1];p=B/'chapters/ch21_debottlenecking/chapter.md'
t=p.read_text(encoding='utf-8')
old='compressor.autoSize(1.15)   # Multiplicative factor: 15% margin\n'
assert old in t
t=t.replace(old,old+'process.run()              # Solve the generated screening chart before reading it\n')
p.write_text(t,encoding='utf-8')
