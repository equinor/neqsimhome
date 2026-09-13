from pathlib import Path
import re,ast
B=Path(__file__).resolve().parents[1]
for n in list(range(19,33))+[34,35]:
 p=next((B/'chapters').glob(f'ch{n:02d}_*/chapter.md'));t=p.read_text(encoding='utf-8-sig')
 print('\nCHAPTER',n)
 for i,m in enumerate(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',t,re.M|re.S),1):
  lang,ann,c=m.groups()
  h=list(re.finditer(r'^#{2,4} (.*)',t[:m.start()],re.M))[-1].group(1)
  assertions=[]
  if lang=='python':
   assertions=[ast.unparse(node.test) for node in ast.walk(ast.parse(c)) if isinstance(node,ast.Assert)]
  print(i,lang,'pattern' if 'pattern' in ann else '',h,'CHECKS',len(assertions),'; '.join(assertions)[:450])
