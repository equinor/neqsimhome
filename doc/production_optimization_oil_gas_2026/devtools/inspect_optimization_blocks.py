from pathlib import Path
import re,sys
B=Path(__file__).resolve().parents[1]
for spec in sys.argv[1:]:
 n,nums=spec.split(':'); p=next((B/'chapters').glob(f'ch{int(n):02d}*/chapter.md'))
 blocks=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',p.read_text(encoding='utf-8-sig'),re.M|re.S))
 for i in map(int,nums.split(',')):
  print(f'CHAPTER {n} FENCE {i}\n{blocks[i-1][0]}\n')
