from pathlib import Path
import re,sys
B=Path(__file__).resolve().parents[1];sys.stdout.reconfigure(encoding='utf-8')
t=(B/'chapters/ch32_advanced_topics/chapter.md').read_text(encoding='utf-8')
selected=set(map(int,sys.argv[1:]))
for i,m in enumerate(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',t,re.M|re.S),1):
 if m[1]=='java' and (not selected or i in selected):print('FENCE',i,m[2],'\n',m[3])
