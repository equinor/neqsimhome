from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
p=next((B/'chapters').glob('ch33*/chapter.md'));text=p.read_text(encoding='utf-8-sig')
PAT=re.compile(r'^```(python|java)([^\n]*)\n(.*?)^```',re.M|re.S)
m=list(PAT.finditer(text))[6];code=m[3]
code=code.replace('    plant.run()', '    # Only this downstream-independent area determines the reported outputs.\n    ngl_sys.run()')
code=code.replace('ax1.set_ylabel(\'NGL Recovery (m³/hr)\', color=\'b\')', 'ax1.set_ylabel("Cold-separator liquid (m³/hr)", color="b")')
code+='''
print("Precooling C | cold-separator liquid m3/hr | compression MW")
for temperature, liquid_rate, power in zip(temperatures, ngl_recovery, compression_power):
    print(f"{temperature:12.1f} | {liquid_rate:27.3f} | {power:14.4f}")
assert all(np.isfinite(ngl_recovery)) and all(np.isfinite(compression_power))
'''
text=text[:m.start()]+'```python\n'+code.rstrip()+'\n```'+text[m.end():]
text+='''

![Specified precooling sensitivity of the illustrative NGL train: simulated liquid volume and gas-compressor shaft power](figures/ch33_ngl_temperature_sensitivity.png)

The plotted liquid volume is evaluated at the cold separator's operating conditions, so it is not a stock-tank NGL sales volume. Lower precooling temperature changes the equilibrium split before expansion and separation; the resulting gas rate and inlet state also change the recompression duty. Read both curves together and include the cooling and fractionation duties before comparing total plant energy or economics. The seven points come from the executed temperature-sweep example above; its values and source hash are preserved in `verification/ch33_onshore_processing_plants_fences.json`.
'''
p.write_text(text,encoding='utf-8')
