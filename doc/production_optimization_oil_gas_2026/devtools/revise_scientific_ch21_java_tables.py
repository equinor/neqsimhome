from pathlib import Path
import re,json,hashlib
B=Path(r'C:\Users\solbraa\OneDrive - NTNU\Documents\GitHub\neqsim\neqsim-paperlab\books\production_optimization_oil_gas_2026')
p=B/'chapters/ch21_debottlenecking/chapter.md';t=p.read_text(encoding='utf-8');before=t
backup=B/'.build/scientific_ch21_java_original';backup.mkdir(exist_ok=True,parents=True)
if not (backup/'chapter.md').exists():(backup/'chapter.md').write_text(t,encoding='utf-8')
py=lambda v:[m[1] for m in re.finditer(r'^```python\n(.*?)^```',v,re.M|re.S)]
changes=[]
def sub(a,b):
 global t
 assert a and a in t,a[:100]
 t=t.replace(a,b);changes.append(a[:120])
sub('**Hard** | Cannot be exceeded — equipment trips or fails | Equipment damage, safety hazard','**Hard** | Declared absolute model limit | A configured limit is exceeded; physical consequence requires its technical basis')
sub('**Soft** | Can be temporarily exceeded with penalty | Reduced efficiency, accelerated wear','**Soft** | Preferred model operating limit | Review predicted performance and the configured penalty policy')
sub('**Design** | Information only — original design basis | No immediate consequence','**Design** | Reference rating for capacity reporting | Reporting or optimizer impact depends on the consuming workflow')
sub('getCapacityUtilization()','getCapacityUtilizationSummary()')
sub('isOverloaded()', 'isCapacityExceeded()')
sub('The constraints are lazily initialized — they are created the first time this method is called.','Initialization is equipment-specific: separators and compressors populate native constraints during construction; several other classes initialize them when first queried.')
a=t.index('The three constraint types define different severity levels:');b=t.index('A constraint is constructed',a)
t=t[:a]+'The type records the intended treatment of a declared limit. It does not simulate a protective trip or prove that exceeding a soft limit is acceptable. `isViolated()` compares utilization with 1.0 for every type; `isHardLimitExceeded()` tests the separate maximum/minimum only for `ConstraintType.HARD`.\n\n'+t[b:]
sub('HARD,    // Cannot exceed — causes trip or equipment damage\n    SOFT,    // Can exceed temporarily — reduced efficiency or life\n    DESIGN   // Information only — original design basis','HARD,    // Declared absolute limit\n    SOFT,    // Preferred operating limit\n    DESIGN   // Reference rating')
a=t.index('Additionally, a `ConstraintSeverity`');b=t.index('### 21.2.5',a)
t=t[:a]+'''`ConstraintSeverity` is separate metadata (`CRITICAL`, `HARD`, `SOFT`, `ADVISORY`), with helper methods for critical violations and penalty calculations. Do not infer universal optimizer behavior from its name: inspect the selected optimizer, its utilization limits and penalty configuration. Setting severity does not change the constructor's `ConstraintType`; for example the optional compressor discharge-temperature constraint is constructed as SOFT even though its severity is set to HARD.

'''+t[b:]
sub('This means every one of the 144+ equipment types — from simple valves to complex distillation columns — can hold and report capacity constraints without requiring any modification to the equipment class itself.','Equipment subclasses can hold and report capacity constraints through this common interface; a populated storage object does not establish that every physically relevant limit has been implemented.')
a=t.index('| # | Strategy | Equipment | Key Constraints |');b=t.index('All 18 strategies',a)
rows=t[a:b].splitlines(); table=['| # | Registered strategy | Equipment family |','|---|---|---|']
for row in rows[2:]:
 if row.startswith('|'):
  fields=[x.strip() for x in row.split('|')[1:-1]];table.append('| '+' | '.join(fields[:3])+' |')
t=t[:a]+'\n'.join(table)+'\n\nThe registry identifies handlers, not a guaranteed list of physical constraints. A strategy can delegate to the equipment\'s native constraint map or use a limited fallback metric. Query that map, its enabled flags, measurement availability and units at the solved operating point; the native cases below show the actual keys.\n\n'+t[b:]
sub('Constraints are **disabled by default** until explicitly enabled. This prevents unexpected capacity violations in existing simulations.','The equipment-level analysis flag defaults to enabled. Individual constraint defaults differ by class: separator checks start disabled; compressor power checks are enabled and chart-dependent checks are enabled only with an active chart. `autoSize()` can change both the model and the enabled set. Inspect the result explicitly.') if 'Constraints are **disabled by default** until explicitly enabled. This prevents unexpected capacity violations in existing simulations.' in t else None
sub('The shadow price is zero until populated by an economic tool. The `DebottleneckingAdvisor` (Section 21.9.5) writes shadow prices back onto the binding constraints so that the same constraint objects used for capacity checking also rank the value of the production each bottleneck withholds.','The shadow-price field stores a supplied scalar without a unit schema or derivative calculation. The example assumes NOK per RPM. `DebottleneckingAdvisor.applyShadowPrices()` instead copies each candidate\'s assumed annual incremental value into that field; it neither divides by a capacity increment nor verifies that the attached constraint is binding. Preserve the economic basis separately before interpreting this value.')
sub('The separator\'s `autoSize` creates constraints for:\n\n| Constraint | Unit | Type | Basis |\n|-----------|------|------|-------|\n| `gasLoadFactor` | m/s | SOFT | Souders-Brown K-factor |\n| `liquidRetentionTime` | s | SOFT | Minimum residence time |\n| `liquidLevel` | % | DESIGN | Normal operating level |', '''`Separator` and `ThreePhaseSeparator` share the following native keys. `autoSize` enables `gasLoadFactor` and preserves checks previously enabled; the other keys are present but remain disabled unless selected.

| Constraint | Unit | Type | Basis |
|---|---|---|---|
| `gasLoadFactor` | m/s | SOFT | Gas velocity multiplied by the gas/liquid density correction |
| `kValue` | m/s | SOFT | K-value at the assumed high liquid level |
| `dropletCutSize` | µm | SOFT | Calculated gas-side droplet cut-size screen |
| `inletMomentum` | Pa | SOFT | Inlet mixture momentum flux |
| `oilRetentionTime` | min | SOFT | Minimum oil inventory/outlet volume-rate ratio |
| `waterRetentionTime` | min | SOFT | Minimum water inventory/outlet volume-rate ratio |

There is no native `liquidRetentionTime` or `liquidLevel` constraint in this implementation. The minimum-retention utilization is minimum/current; the default warning threshold of 1.2 therefore warns only after the minimum has already been violated. Change that warning policy deliberately if advance warning is required. An absent liquid phase can return the 999-minute sentinel; phase availability must accompany the number. A two-outlet `Separator` is suitable for this dry gas/oil fixture; use `ThreePhaseSeparator` for separately conserved oil and water outlets.''')
a=t.index("The compressor's `autoSize` creates constraints for:");b=t.index('The surge margin constraint',a)
t=t[:a]+'''Compressor `autoSize` generates a scaled template chart, enables chart use and speed solving, and assigns a power rating from current kW multiplied by the requested factor. Rerun after sizing because the generated chart changes the operating model. These are synthetic screening curves, not a vendor performance map.

| Constraint | Unit | Type | Availability and basis |
|---|---|---|---|
| `speed` | RPM | HARD | Active chart maximum or mechanical speed limit |
| `minSpeed` | RPM | HARD | Minimum/current speed; present if a positive minimum exists |
| `power` | % | HARD | Current shaft kW relative to available driver/design kW; design 100%, hard maximum 110% |
| `ratedPower` | % | DESIGN | Current kW relative to driver rating or mechanical design rating |
| `surgeMargin` | % | HARD | Minimum/current flow margin; active chart required |
| `stonewallMargin` | % | SOFT | Minimum/current distance to stonewall; active chart required |
| `dischargeTemperature` | C | SOFT type, HARD severity | Added only after an explicit maximum-temperature setting |

There is no native `polytropicHead` constraint. Chartless models disable speed and surge/stonewall checks because those quantities lack a physical chart basis. The optional temperature utilization divides Celsius values, so it is a library reporting convention, not a thermodynamic ratio; use the actual temperature difference to the declared limit for engineering decisions. A missing power rating can produce zero reported utilization and must be treated as unavailable rating evidence.

'''+t[b:]
sub('A compressor operating with less than 10% surge margin is dangerously close to surge and requires immediate attention.','The library uses a 10% minimum surge margin in this flow-based definition. Treat it as a configured screening input. The acceptable operating region and anti-surge control line require the vendor map, gas basis and control-system design; there is no universal margin established by this example.')
sub('| `cvUtilization` | - | HARD | Ratio of required Cv to installed Cv |','| `cvUtilization` | Cv convention | HARD | Stored valve Cv divided by mechanical-design maximum Cv |')
sub('The valve opening constraint warns when the valve is nearly fully open (limited control authority) or nearly closed (poor rangeability):','The native opening utilization tests opening divided by its configured maximum; it does not enforce a lower-opening bound. The following is a separately assumed teaching control range:')
sub('\\text{Valve OK if:}', '\\text{Assumed control range:}')
sub('### 21.4.5 Pipeline autoSize','The Cv constraint compares stored values; it does not recompute the required Cv for each trial state. Confirm the sizing mode and opening characteristic separately. Auto-sizing recreates these valve constraints disabled. The AIV result is a screening metric, not a fatigue or acoustic qualification.\n\n### 21.4.5 Pipeline autoSize')
a=t.index('Pump constraints include:');b=t.index('### 21.4.7',a)
t=t[:a]+'''The native pump map always contains disabled `power` (kW, HARD) and `flowRate` (m³/hr, DESIGN) constraints. `autoSize(1.20)` sets design volume flow to 1.20 times actual inlet flow; its power rule uses the current shaft work times 1.20². That latter rule is an implementation sizing heuristic, not a general pump affinity law or driver rating. No native `differentialHead` constraint is created.

When `setCheckNPSH(true)` is configured, a disabled SOFT `npshMargin` key is also added. Its API unit says metres, but its supplier returns a dimensionless ratio of NPSH available to a multiple of NPSH required; the generic utilization direction is unsuitable as a standalone cavitation acceptance check. Do not enable it and infer cavitation safety from the resulting utilization.

For a physical check, obtain the suction total-head and vapor-pressure basis and the vendor's NPSH requirement, then evaluate explicitly:

$$
\\mathrm{NPSH}_A-\\mathrm{NPSH}_R\\geq\\Delta H_{\\mathrm{required}},
$$

with a project-defined positive head margin in metres. A negative difference fails the specified NPSH requirement; a positive difference alone does not demonstrate absence of cavitation or damage. The pump example below checks material and shaft-energy closure, liquid inlet, positive head and finite design flow/power; it does not supply a vendor NPSH curve.

'''+t[b:]
sub('`evaluate()` returns the recommendations sorted by descending NPV. Each `Recommendation` exposes `getNpvNok()`, `getPvBenefitsNok()`, `getBenefitCostRatio()`, `getPaybackYears()`, and `isAttractive()` (NPV > 0). Calling `applyShadowPrices()` then propagates the marginal value of each binding constraint back to the corresponding `CapacityConstraint` object (Section 21.2.3), so that a later utilization report shows not only *how loaded* each equipment item is but *how much production value* its limit is currently withholding. The full result set is available as JSON via `toJson()` for inclusion in a debottlenecking study.','`evaluate()` sorts by descending NPV and supplies discounted benefits, benefit/cost ratio, simple payback and the NPV > 0 flag. In this API, CAPEX is discounted to `firstYear`, and benefits are paid from `firstYear` through `lastYear` inclusive; with firstYear = 1, this differs from the initial-outlay-at-year-zero equation above. `applyShadowPrices()` copies the assumed annual incremental value onto each supplied constraint, without solving a capacity sensitivity or checking binding status. The result can be exported with `toJson()`.')
# Only mutate Java fences; root owns Python.
i=0
def java(m):
 global i
 i+=1;c=m[1]
 if i==1:c=c.replace('        compressor.enableAllConstraints();','        compressor.enableAllConstraints();\n        process.run();  // Solve the chart model activated by autoSize')
 if i==8:c=c.replace('entry.getValue() * 100','entry.getValue()')
 if i==10:c=c.replace('> 0.80','> 80.0')
 if i==11:c=c.replace('// Any HARD constraint violated (trip/safety condition)?','// Any declared HARD maximum/minimum exceeded?')
 if i in [16,20,31]:
  marker={16:'comp.autoSize(1.15);  // Multiplicative factor: 15% design margin',20:'comp.autoSize(1.15);',31:'hpComp.autoSize(1.15);'}[i]
  c=c.replace(marker,marker+'\n'+('topside' if i==31 else 'process')+'.run();  // Recompute after activating the generated chart')
 if i==25:c=c.replace('> 1.0','> 100.0').replace('> 0.90','> 90.0').replace('> 0.75','> 75.0').replace('u * 100','u')
 if i==26:c=c.replace('> 0.95','> 95.0').replace('> 0.85','> 85.0').replace('> 0.75','> 75.0')
 return '```java\n'+c+'```'
t=re.sub(r'^```java\n(.*?)^```',java,t,flags=re.M|re.S)
# Insert dimensional/API note once outside shared §21.5.
anchor='### 21.3.3 Equipment Utilization Summary'
if anchor not in t:anchor='## 21.6 Utilization Summary Dashboard'
t=t.replace(anchor,'`getCapacityUtilizationSummary()` returns **percent** (100.0 = 100%); `BottleneckResult.getUtilization()` and equipment `getMaxUtilization()` return fractions (1.0 = 100%). Use thresholds of 80.0/90.0 in the summary map, and 0.80/0.90 in the fractional APIs. The legacy `getBottleneck()` path does not apply the equipment-level exclusion flag; use `findBottleneck()` when that flag matters.\n\n'+anchor)
assert py(t)==py(before),'Python source changed'
p.write_text(t,encoding='utf-8')
(B/'verification/scientific_revision/ch21_table_java_corrections.json').write_text(json.dumps({'changes':changes,'python_fences_unchanged':True,'java_fences':i},indent=2),encoding='utf-8')
print('Updated',i,'Java fences; preserved all Python')
