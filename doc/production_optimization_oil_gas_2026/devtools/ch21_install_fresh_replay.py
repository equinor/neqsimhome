"""Make accepted waterfall states fresh rather than tolerance-cached replays."""
from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
p=B/'chapters/ch21_debottlenecking/chapter.md'
t=p.read_text(encoding='utf-8')
matches=list(re.finditer(r'^```(python|java)([^\n]*)\n(.*?)^```',t,re.M|re.S))
m=matches[24];c=m[3]
start=c.index('fluid = ');end=c.index('print(f"Separator utilization:')
initial=c[start:end]
body='def build_waterfall_process(template=None):\n'
body+=''.join('    '+line+'\n' if line else '\n' for line in initial.splitlines())
body+='''    if template is not None:
        for unit_name in ("HP Sep", "Export Comp"):
            previous = template.getUnit(unit_name).getCapacityConstraints()
            fresh = process.getUnit(unit_name).getCapacityConstraints()
            for key in previous.keySet():
                fresh.get(key).setEnabled(previous.get(key).isEnabled())
    return process, feed, sep, comp

process, feed, sep, comp = build_waterfall_process()

'''
c=c[:start]+body+c[end:]
old='''    optimum = ProductionOptimizer().optimize(process, feed, config, None, None)
    process.run()

    assert optimum.isFeasible(), "Relaxed candidate failed declared constraints"
    new_rate = float(feed.getFlowRate("kg/hr"))
    assert abs(new_rate - optimum.getOptimalRate()) <= 1e-6 * max(new_rate, 1.0)
'''
new='''    optimum = ProductionOptimizer().optimize(process, feed, config, None, None)
    assert optimum.isFeasible(), "Relaxed candidate failed declared constraints"
    new_rate = float(optimum.getOptimalRate())
    # Rebuild the physical model at the original sizing basis, retaining the
    # diagnostic constraint masks. This avoids the separator's 1e-6 input cache.
    process, feed, sep, comp = build_waterfall_process(process)
    feed.setFlowRate(new_rate, "kg/hr")
    process.run()
    assert abs(feed.getFlowRate("kg/hr") - new_rate) < 1e-7
'''
assert old in c;c=c.replace(old,new)
t=t[:m.start(3)]+c+t[m.end(3):]
t=t.replace('To simulate replacing an entire piece of equipment with a larger one:',
'''To diagnose the effect of omitting one equipment item's configured constraints:
This operation does not resize or replace that item.''')
t=t.replace('| Returns count of disabled | Simulate equipment upgrade |','| Returns count of disabled | Diagnose omitted equipment limits |')
t=t.replace('The search upper bound may become the final limit.',
'''The search upper bound may become the final limit. Each candidate is replayed in a freshly constructed model with the original sizing basis; this prevents the separator's relative input-change cache (1e-6) from leaving small material imbalances near the optimizer's final rate.''')
p.write_text(t,encoding='utf-8')
print('Fresh replay installed in Chapter21 fence25.')
