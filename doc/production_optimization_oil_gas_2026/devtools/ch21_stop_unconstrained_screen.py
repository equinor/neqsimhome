from pathlib import Path
B=Path(__file__).resolve().parents[1]
p=B/'chapters/ch21_debottlenecking/chapter.md';t=p.read_text(encoding='utf-8')
old='''    # Disable it
    result.getConstraint().setEnabled(False)
    config ='''
new='''    # Stop before omitting the last active limit on either equipment item.
    # A fallback liquid-level metric is not a separator throughput rating.
    remaining = sum(c.isEnabled() for c in
                    process.getUnit(name).getCapacityConstraints().values())
    if remaining <= 1:
        print(f"Stopped: {name} would have no active capacity constraint")
        break
    result.getConstraint().setEnabled(False)
    config ='''
assert old in t;t=t.replace(old,new)
t=t.replace("+ ['Maximum']", "+ ['Screened']")
t=t.replace('The search upper bound may become the final limit.',
'''The search upper bound may become the final limit. The calculation stops before disabling an equipment item's last enabled constraint: a fallback liquid-level metric or an absent compressor limit cannot establish its throughput capacity. The final bar is the screened rate reached before that stop, not an unconstrained plant maximum.''')
p.write_text(t,encoding='utf-8')
