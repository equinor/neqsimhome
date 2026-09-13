from pathlib import Path
import re,json,hashlib
B=Path(__file__).resolve().parents[1];V=B/'verification/pdf_final'
p=B/'chapters/ch18_power_production/chapter.md'
text=p.read_text(encoding='utf-8')
backup=V/'ch18_before_emissions_prose.md'
if not backup.exists():backup.write_text(text,encoding='utf-8')
fences=re.compile(r'^\x60\x60\x60[^\n]*\n.*?^\x60\x60\x60[^\n]*(?:\n|$)',re.M|re.S)
before=fences.findall(text)
replacements={
'For a typical North Sea fuel gas with ethane and propane, the composite emission factor is approximately 2.7–2.8 kg CO$_2$ per kg fuel.':
'For a mixed fuel, calculate the factor from its elemental carbon flow and the fraction oxidized to CO₂; methane, heavier hydrocarbons, inert components and unburned fuel must be accounted for explicitly.',
'For a typical offshore platform, Scope 1 emissions are 50,000–300,000 tonnes CO$_2$ per year, dominated by gas turbine exhaust (70–90% of total).':
'Quantify each source from the dated fuel, flare and emissions inventory; no generic annual total or turbine share is assumed here.',
'Typical values range from 5–15 kg CO$_2$/boe for efficient modern platforms with electrification to 50–100+ kg CO$_2$/boe for aging platforms with declining production. The global upstream industry average is approximately 15–20 kg CO$_2$/boe.':
'Comparisons require the same reporting period, emissions boundary, gas-to-boe conversion and treatment of purchased electricity. Include the relevant combustion, flare, vent and fugitive sources, and identify whether the numerator is CO₂ or CO₂-equivalent. A lower ratio may reflect a changed production denominator as well as lower emissions. The example below is a declared accounting scenario, not a measured platform or global benchmark.'}
changes=[]
for old,new in replacements.items():
 assert old in text,old
 text=text.replace(old,new)
 changes.append({'before':old,'after':new})
parts=fences.split(text)
# Chemical subscripts in prose use Unicode, avoiding ambiguous inline-dollar
# pairing around adjacent slash-unit expressions in the publishing conversion.
matches=list(fences.finditer(text));cursor=0;output=[]
for m in matches:
 output.append(text[cursor:m.start()].replace('CO$_2$','CO₂'));output.append(m[0]);cursor=m.end()
output.append(text[cursor:].replace('CO$_2$','CO₂'))
text=''.join(output)
assert fences.findall(text)==before
p.write_text(text,encoding='utf-8')
(V/'emissions_prose_fix.json').write_text(json.dumps({'status':'passed','code_unchanged':True,
 'changes':changes,'chapter_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
 'purpose':'Resolve rendered math overflow and replace unsupported generic emissions claims with an explicit accounting basis.'},indent=2),encoding='utf-8')
print('Corrected emissions prose; all code unchanged.')
