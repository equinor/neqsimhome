"""Dimensional and limiting-case tests of corrected printed equations.

These independent calculations verify algebra and units, not empirical model
accuracy or measured field behavior. No NeqSim model is replaced by these tests.
"""
from pathlib import Path
import math,json,hashlib
BOOK=Path(__file__).resolve().parents[1]
rows=[]
def check(ch,name,actual,expected,tolerance,definition):
 error=abs(actual-expected)
 rows.append({'chapter':ch,'name':name,'actual':actual,'expected':expected,'absolute_error':error,'tolerance':tolerance,'definition':definition,'pass':math.isfinite(actual) and error<=tolerance})
g=9.80665
check('ch01','Freshwater gradient psi/ft',1000*g*.3048/6894.757293,.4335275,1e-6,'rho*g; SI to psi per foot')
check('ch01','3000m freshwater pressure bara',1.01325+1000*g*3000/1e5,295.21275,1e-8,'absolute datum pressure plus hydrostatic head')
check('ch05','Turner field coefficient converted to SI',1.91*.3048*(1000/16.018463)**.25*16.018463**.5,6.55503,.01,'1.91 ft/s, surface tension dyn/cm and density lb/ft3 converted to m/s, N/m, kg/m3')
check('ch07','API14E C100 SI coefficient',100*.3048*math.sqrt(16.018463),121.990324,1e-6,'field velocity ft/s, density lb/ft3 to SI')
check('ch08','Thermal characteristic length km',50*2000/(5*math.pi*.52)/1000,12.242688,.01,'m*cp/(U*pi*D), stated fixed-property cooling limit')
for w in [10.,20.,30.]:
 dT=1297*w/(62.07*(100-w));inverted=100*62.07*dT/(1297+62.07*dT)
 check('ch09','Hammerschmidt inverse at %.0f wt%%'%w,inverted,w,1e-12,'same SI constant1297 for MEG, valid only within correlation concentration/domain')
check('ch09','10K depression MEG wt%',100*62.07*10/(1297+62.07*10),32.36638,.001,'KH1297 and MEG molecular mass62.07 g/mol')
check('ch09','10K depression methanol wt%',100*32.04*10/(1297+32.04*10),19.80957,.001,'KH1297 and methanol molecular mass32.04 g/mol')
check('ch10','100micron Stokes settling mm/s',g*(100e-6)**2*200/(18*.001)*1000,1.089628,1e-6,'rigid sphere, low-Reynolds-number limit')
check('ch10','10micron Stokes settling mm/s',g*(10e-6)**2*200/(18*.001)*1000,.01089628,1e-8,'diameter-squared scaling')
check('ch13','100000mg/L brine salt mass fraction',100000*.001/1070,.0934579439,1e-10,'C_s/rho, 1mg/L=.001kg/m3')
# Gas IPR q=C*(Pr^2-Pwf^2)^n; verify inverse derivative against central difference.
Pr,C,n,q=250.,.05,.8,80.
def inverse(q):return math.sqrt(Pr**2-(q/C)**(1/n))
d=-((q/C)**(1/n-1))/(2*n*C*inverse(q))
h=q*1e-5
check('ch06','Inverse gas-IPR derivative',d,(inverse(q+h)-inverse(q-h))/(2*h),1e-7,'dp/dq=-1/(2*n*C*p)*(q/C)^(1/n-1)')
# Hyperbolic cumulative production must differentiate to the rate.
qi,Di,b,t=5000.,.001,.5,750.
def np(t):return qi/(Di*(1-b))*(1-(1+b*Di*t)**((b-1)/b))
rate=qi/(1+b*Di*t)**(1/b)
check('ch04','Arps cumulative derivative Sm3/day',(np(t+.001)-np(t-.001))/.002,rate,1e-5,'analytic material accumulation derivative for b=.5')
# Equal ideal-gas stage pressure ratios minimize work at perfect intercooling.
r_total=30.;a=(1.3-1)/(1.3*.8);opt=math.sqrt(r_total)
def w(r1):return r1**a+(r_total/r1)**a-2
check('ch14','Equal-ratio stationary point',(w(opt+.0001)-w(opt-.0001))/.0002,0.,1e-8,'fixed inlet T/composition, equal stage efficiency, no pressure losses')
check('ch14','Equal-ratio minimum versus unequal split',0 if w(opt)<w(2.) and w(opt)<w(15.) else 1,0,0,'convex ideal-gas work in logarithmic pressure ratio')
check('ch16','Counterflow NTU equal-capacity limit',2/(1+2),2/3,1e-12,'epsilon=NTU/(1+NTU) when Cr=1; avoids0/0 formula')
check('ch18','80C source and25C sink Carnot bound',1-298.15/353.15,.15574118646,1e-9,'upper bound even before finite-temperature heat transfer and parasitic losses')
report={'status':'pass' if all(r['pass'] for r in rows) else 'fail','scope':'Independent algebra, dimensional conversions and limiting cases of selected printed equations; not empirical calibration','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':rows}
(BOOK/'verification/scientific_revision/foundations_analytical_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(report['status'],len(rows),'checks')
for r in rows:
 if not r['pass']:print(r)
raise SystemExit(0 if report['status']=='pass' else 1)
