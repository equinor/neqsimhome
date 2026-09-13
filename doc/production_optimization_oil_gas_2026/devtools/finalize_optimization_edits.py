"""Finish mathematical typography and source-confirmed API corrections."""
from pathlib import Path
import re
BOOK=Path(__file__).resolve().parents[1]
def chapter(n): return next((BOOK/'chapters').glob(f'ch{n:02d}*/chapter.md'))
p=chapter(19); s=p.read_text(encoding='utf-8-sig')
s=re.sub(r'C_d = 0\.5961[^\n]+',r'''\\begin{aligned}
C_d ={}& 0.5961 + 0.0261\\beta^2 - 0.216\\beta^8 \\\\
&+ 0.000521\\left(\\frac{10^6\\beta}{\\mathrm{Re}_D}\\right)^{0.7} \\\\
&+ (0.0188+0.0063A)\\beta^{3.5}\\left(\\frac{10^6}{\\mathrm{Re}_D}\\right)^{0.3}
+ \\Delta C_{\\mathrm{up}} + \\Delta C_{\\mathrm{down}}
\\end{aligned}''',s)
p.write_text(s,encoding='utf-8')
p=chapter(24); s=p.read_text(encoding='utf-8-sig')
a=s.index('The optimizer evaluates candidates using a composite score:')
b=s.index('\n---',a)
s=s[:a]+r'''A penalty score combines normalized objectives and violation measures. Define

$$
\begin{aligned}
F(x) &= \sum_j w_j\hat f_j(x), \\
P(x) &= \sum_m\lambda_m\max(0,g_m(x)), \\
V(x) &= \sum_i\max(0,U_i(x)-U_{i,\mathrm{limit}}).
\end{aligned}
$$

A schematic conditional score is then

$$
S(x)=\begin{cases}
F(x), & \text{feasible}, \\
F(x)-P(x)-\Lambda V(x), & \text{infeasible}.
\end{cases}
$$

Here feasibility means that every enabled hard constraint and equipment utilization limit is satisfied. Soft-constraint treatment depends on the chosen scoring configuration; the expression illustrates the penalty concept rather than every implementation branch.

A finite penalty weight $\Lambda$ does **not** generally ensure that every feasible candidate outranks every infeasible candidate: such a guarantee requires additional objective and violation bounds. Acceptance therefore uses explicit feasibility checks and the final full-model replay, with a recorded failure when a valid final state cannot be established. A favorable scalar score alone is insufficient.
''' + s[b:]
p.write_text(s,encoding='utf-8')
