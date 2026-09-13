"""Capture actual line arrays from unchanged accepted literal plot producers."""
from pathlib import Path
import sys,os,json,hashlib,runpy
B=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
n=int(sys.argv[1]);sys.path.insert(0,str(B/'.build/python_packages'));sys.path.insert(0,str(B/'devtools'))
os.environ['MPLBACKEND']='Agg'
import matplotlib;matplotlib.use('Agg')
from matplotlib.figure import Figure
import numpy as np
original=Figure.savefig;records=[]
def values(x):
 a=np.asarray(x)
 if a.dtype.kind not in 'iufb':return a.astype(str).tolist()
 return [None if not np.isfinite(v) else float(v) for v in a.reshape(-1)]
def savefig(fig,filename,*args,**kwargs):
 result=original(fig,filename,*args,**kwargs)
 p=Path(filename).resolve()
 row={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'axes':[]}
 for ax in fig.axes:
  item={'title':ax.get_title(),'xlabel':ax.get_xlabel(),'ylabel':ax.get_ylabel(),'xlim':list(ax.get_xlim()),'ylim':list(ax.get_ylim()),'lines':[]}
  for line in ax.lines:
   item['lines'].append({'label':line.get_label(),'x':values(line.get_xdata()),'y':values(line.get_ydata())})
  row['axes'].append(item)
 records.append(row)
 return result
Figure.savefig=savefig
sys.argv=[str(B/'devtools/foundations_manuscript_physics.py'),'--chapter',f'ch{n:02d}']
runpy.run_path(sys.argv[0],run_name='__main__')
report=OUT/f'ch{n:02d}_manuscript_physics.json';evidence=json.loads(report.read_text(encoding='utf-8'))
assert all(r['execution']=='pass' for r in evidence['literal_blocks'])
assert all(r.get('pass',False) for r in evidence['physical_checks'])
for row in records:row.update(physics_report=str(report.relative_to(B)),physics_report_sha256=hashlib.sha256(report.read_bytes()).hexdigest())
(OUT/f'final_original_ch{n:02d}_plot_arrays.json').write_text(json.dumps({'chapter':n,'plots':records,'python':sys.executable},indent=2),encoding='utf-8')
print('ARRAY_CAPTURE',n,len(records),'accepted plots',flush=True)
os._exit(0)
