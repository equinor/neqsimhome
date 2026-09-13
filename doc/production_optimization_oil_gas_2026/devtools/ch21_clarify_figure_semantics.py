from pathlib import Path
import re
B=Path(__file__).resolve().parents[1];p=B/'chapters/ch21_debottlenecking/chapter.md'
t=p.read_text(encoding='utf-8');P=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
for i,m in reversed(list(enumerate(P.finditer(t),1))):
    c=m[3]
    if i==25:
        c=c.replace("[b['equipment'] for b in bottlenecks]", "[b['equipment'] + '\\n' + b['constraint'] for b in bottlenecks]")
        c=c.replace("ax.set_ylabel('Production Rate (kg/hr)')", "ax.set_ylabel('Feed mass rate (kg/hr)')")
        c=c.replace("ax.set_xlabel('Debottlenecking Step')", "ax.set_xlabel('Configured constraint omitted at each step')")
        c=c.replace('plt.tight_layout()', '''for index, b in enumerate(bottlenecks, start=1):
    ax.text(index, b['cumulative'] + 1500, f"+{b['gain']:.0f}",
            ha='center', va='bottom', fontsize=9)
plt.tight_layout()''')
    if i==32:
        old="ax1.plot(flow_rates / 1000, bottleneck_utils, 'b-o', linewidth=2)"
        new='''# 999% is the native outside-map penalty, not a measured 9.99-fold demand.
outside_map = np.asarray(bottleneck_utils) >= 999.0 - 1e-8
plotted_utilization = np.where(outside_map, np.nan, bottleneck_utils)
assert np.any(~outside_map)
ax1.plot(flow_rates / 1000, plotted_utilization, 'b-o', linewidth=2,
         label='Numerical constraint utilization')
flag_height = max(150.0, float(np.nanmax(plotted_utilization)) * 1.12)
ax1.scatter(flow_rates[outside_map] / 1000,
            np.full(np.count_nonzero(outside_map), flag_height),
            color='darkred', marker='x', s=45,
            label='Outside template map (999% penalty; marker height arbitrary)')'''
        assert old in c;c=c.replace(old,new)
    if c!=m[3]:t=t[:m.start(3)]+c+t[m.end(3):]
t=t.replace('The sweep identifies the largest configured utilization at each imposed feed rate.',
'''The sweep identifies the largest configured utilization at each imposed feed rate. A reported 999% is the native penalty for an invalid operating region of the generated template compressor map, not a physical demand measured at 9.99 times capacity. The plot retains these rejected cases as red crosses in a labeled display strip and leaves the numerical curve open across them.''')
p.write_text(t,encoding='utf-8')
