from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
p=next((B/'chapters').glob('ch30*/chapter.md'));text=p.read_text(encoding='utf-8-sig')
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
for n,m in reversed(list(enumerate(PAT.finditer(text),1))):
 code=m[3];old=code
 if n==18:
  code+='''

# Exercise the update function with clearly labelled synthetic observations.
tags = {name: name for name in ["feed_rate", "feed_temperature", "feed_pressure",
    "hp_sep_pressure", "hp_sep_temperature", "compressor_power"]}
observations = {"feed_rate": 100000.0, "feed_temperature": 60.0, "feed_pressure": 50.0,
    "hp_sep_pressure": 50.2, "hp_sep_temperature": 59.8, "compressor_power": 6.0}
comparison = digital_twin_update(process, observations, tags)
print(json.dumps(comparison, indent=2))
# These declared observations test data plumbing; they are not an independent plant validation.
'''
 if n==20:code=code.replace('"Feed.pressure"','"Feed Gas.pressure"')
 if n==21:code='''# Optimize the explicitly built single process using writable input addresses.
opt = auto.newOptimizer()
opt.addVariable("Feed Gas.pressure", 30.0, 70.0, "bara")
opt.addVariable("Export Compressor.outletPressure", 80.0, 200.0, "bara")
opt.maximize("HP Separator.liquidOutStream.flowRate", "kg/hr")
opt.addConstraintLessOrEqual("Export Compressor.power", 8000.0, "kW", 1.0e4)
opt.setSeed(42).setMaxEvaluations(30)
result = opt.optimize()
print("Feasible:", result.isFeasible(), "objective:", result.getBestObjective())
print("Best setpoints:", dict(result.getBestSetpoints()))
# A process oil-outlet pressure is not RVP. Add a separately computed quality specification
# only when its physical test method and callable evaluator have been supplied.
if not result.isFeasible():
    print("No accepted operating recommendation; inspect the optimizer diagnostics")'''
 if code!=old:text=text[:m.start()]+'```'+m[1]+m[2]+'\n'+code.rstrip()+'\n```'+text[m.end():]
p.write_text(text,encoding='utf-8')
