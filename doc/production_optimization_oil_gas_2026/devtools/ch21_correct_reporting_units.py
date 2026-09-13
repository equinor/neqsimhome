from pathlib import Path
import re
B=Path(__file__).resolve().parents[1];p=B/'chapters/ch21_debottlenecking/chapter.md'
t=p.read_text(encoding='utf-8');P=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
for i,m in reversed(list(enumerate(P.finditer(t),1))):
    c=m[3]
    if m[1]!='python':continue
    c=c.replace('{u * 100:6.1f}%', '{u:6.1f}%')
    c=c.replace('float(utilization.get(k)) * 100','float(utilization.get(k))')
    c=c.replace('float(utilization.get(name)) * 100','float(utilization.get(name))')
    c=c.replace('Total potential gain:', 'Conditional screened gain:')
    if i==36:
        c=c.replace('# Debottlenecking options from capacity analysis','# Assumed independent economic examples; these gains are not outputs\n# from the mixed-fluid capacity model above. No incremental OPEX or tax.')
        for old,new in [(8000,80),(4500,45),(3000,30),(6000,60),(2000,20)]:
            c=c.replace('"delta_q_bpd": '+str(old), '"delta_q_bpd": '+str(new))
        c=c.replace('for opt in options:', 'economic_rows = []\nfor opt in options:')
        c=c.replace('    print(f"  {opt[\'name\']', '    economic_rows.append({**opt, "annual_revenue_mnok": annual_revenue_mnok,\n                          "npv_mnok": npv, "PI": pi})\n    print(f"  {opt[\'name\']')
    if c!=m[3]:t=t[:m.start(3)]+c+t[m.end(3):]
t=t.replace('Debottlenecking options should be ranked by the ratio of NPV to CAPEX (profitability index):',
'''The profitability index compares the present value of incremental net cash flows with the initial investment:''')
t=t.replace('### 21.9.4 Screening with Python\n', '''### 21.9.4 Screening with Python

The five independent cases below assume constant extra saleable oil of 20–80 bbl/day for ten years, 93% uptime, a fixed illustrative price of 70 USD/bbl and exchange rate of 10.5 NOK/USD. They demonstrate pretax discounted cash-flow arithmetic; the extra oil, reserves, costs and constant-rate life are assumptions, not results from the preceding mixed-fluid flow model. Zero incremental OPEX, no shutdown loss and no tax are simplifying assumptions. Replace them with project evidence before investment use.
''')
p.write_text(t,encoding='utf-8')
