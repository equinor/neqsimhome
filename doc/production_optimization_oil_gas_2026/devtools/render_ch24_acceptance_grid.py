"""Plot every attempted state from the exact-source pressure-grid solution record."""
from pathlib import Path
import sys,hashlib,json
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'.build/python_packages'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
source=next((B/'.build/solution_runs').glob('ch24_*/ch24_pressure_grid_acceptance.json'))
rows=json.loads(source.read_text());assert len(rows)==32
out=B/'verification/scientific_revision/figures/ch24_pressure_grid_acceptance.png';out.parent.mkdir(exist_ok=True)
fig,axes=plt.subplots(1,2,figsize=(11.5,4.5),layout='constrained')
vmin=min(r['power_MW'] for r in rows if r['accepted']);vmax=max(r['power_MW'] for r in rows if r['accepted'])
cmap=plt.get_cmap('YlGnBu').copy();cmap.set_bad('#e7e7e7')
for ax,rate in zip(axes,[250000.,350000.]):
 data=np.full((4,4),np.nan)
 for row in rows:
  if row['rate_kg_hr']!=rate:continue
  y=[50.,60.,70.,80.].index(row['sep_P']);x=[120.,140.,160.,180.].index(row['comp_P'])
  if row['accepted']:data[y,x]=row['power_MW']
  if row['accepted']:
   ax.text(x,y,f"{row['power_MW']:.2f}",ha='center',va='center',color='white' if row['power_MW']>(vmin+vmax)/2 else '#163246',fontsize=10)
  else:
   ax.text(x,y,f"Rejected\nΔm={row['knockout_mass_deficit_kg_hr']:.3f} kg/h",ha='center',va='center',color='#9c1b29',fontsize=8,fontweight='bold')
 mesh=ax.imshow(np.ma.masked_invalid(data),origin='lower',cmap=cmap,vmin=vmin,vmax=vmax,aspect='auto')
 ax.set_xticks(range(4),[120,140,160,180]);ax.set_yticks(range(4),[50,60,70,80])
 ax.set_xlabel('Compressor discharge pressure (bara)');ax.set_ylabel('Feed / HP separator pressure (bara)')
 ax.set_title(f'Fixed feed {rate/1000:.0f} t/h: 15 accepted, 1 rejected')
fig.colorbar(mesh,ax=axes,label='Compressor shaft power (MW)',shrink=.85)
fig.suptitle('All 32 attempted pressure states; strict 1 ppm material acceptance gate',fontsize=13)
fig.savefig(out,dpi=160,bbox_inches='tight');plt.close(fig)
manifest={'source':str(source.relative_to(B)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'figure':str(out.relative_to(B)),'figure_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'attempted':32,'accepted':30,'rejected':2,'interpretation':'Native numerical phase-extraction failures are retained; no complete-grid or global optimum claim.'}
(B/'verification/scientific_revision/ch24_acceptance_figure.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
