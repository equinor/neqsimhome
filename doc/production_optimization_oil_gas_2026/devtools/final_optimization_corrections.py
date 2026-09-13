from pathlib import Path
import re,json
B=Path(__file__).resolve().parents[1]
changes=[]
def chapter(n):return next((B/'chapters').glob(f'ch{n:02d}_*/chapter.md'))
def replace(n,old,new):
 p=chapter(n);t=p.read_text(encoding='utf-8-sig')
 assert old in t,(n,old[:100])
 p.write_text(t.replace(old,new),encoding='utf-8');changes.append({'chapter':n,'old':old,'new':new})
def fence(n,i,file):
 p=chapter(n);t=p.read_text(encoding='utf-8-sig');m=list(re.finditer(r'^```(?:python|java)[^\n]*\n(.*?)^```',t,re.M|re.S))[i-1]
 code=(B/'devtools'/file).read_text(encoding='utf-8')
 p.write_text(t[:m.start(1)]+code+t[m.end(1):],encoding='utf-8');changes.append({'chapter':n,'fence':i,'new_source':file})
fence(27,4,'scientific_ch27_surface.py');fence(27,5,'scientific_ch27_tornado.py')
replace(19,'| **Combined (RSS)** | | | **0.519** |','| **Combined (RSS)** | | | **0.520** |')
bad='Nwachukwu, A. and Jeong, H. (2018). "Surrogate-Based Optimization for Production Forecasting and Optimization." *SPE Journal*, 23(4), pp. 1242–1263.'
good='Nwachukwu, A., Jeong, H., Pyrcz, M., and Lake, L.W. (2018). "Fast evaluation of well placements in heterogeneous reservoir models using machine learning." *Journal of Petroleum Science and Engineering*, 163, pp. 463–475. DOI: [10.1016/j.petrol.2018.01.019](https://doi.org/10.1016/j.petrol.2018.01.019).'
for n in [22,30]:replace(n,bad,good)
replace(30,'Willersrud, A., Bjarne, A., and Imsland, L. (2015). "Short-Term Production Optimization of Offshore Oil and Gas Production Using Nonlinear Model Predictive Control." *Journal of Process Control*, 25, pp. 108–122.',
 'Willersrud, A., Imsland, L., Hauger, S.O., and Kittilsen, P. (2011). "Short-term Production Optimization of Offshore Oil and Gas Production Using Nonlinear Model Predictive Control." *IFAC Proceedings Volumes*, 44(1), pp. 10851–10856. DOI: [10.3182/20110828-6-IT-1002.01216](https://doi.org/10.3182/20110828-6-IT-1002.01216).')
replace(30,'von Rueden, L., Mayer, S., Beckh, K., et al. (2021).','von Rueden, L., Mayer, S., Beckh, K., et al. (2023).')
replace(32,'Schweidtmann, A.M., et al. (2019). Deterministic global process optimization via neural networks. *Computers & Chemical Engineering*, 121, 67–84.',
 'Schweidtmann, A.M., Huster, W.R., Lüthje, J.T., and Mitsos, A. (2019). Deterministic global process optimization: Accurate (single-species) properties via artificial neural networks. *Computers & Chemical Engineering*, 121, 67–74. DOI: [10.1016/j.compchemeng.2018.10.007](https://doi.org/10.1016/j.compchemeng.2018.10.007).')
replace(24,'The detection algorithm uses a sliding window to check that:\n1. The coefficient of variation (CV = σ/μ) is below a threshold for each measurement\n2. No significant trends are present (linear regression slope test)\n3. No autocorrelation structure suggests oscillatory behavior\n\nTypical steady-state criteria:\n- Temperature: CV < 0.5% over 30 minutes\n- Pressure: CV < 1% over 30 minutes\n- Flow rate: CV < 3% over 30 minutes',
 'The current implementation computes window variance, the successive-difference variance ratio and a regression slope in units per sample. Independent stationary noise gives a ratio near one; drift may give a small ratio. It does not establish an absence of oscillations with a general autocorrelation test. Set limits from signal noise and the process settling time, and use a declared regular sampling interval. A coefficient of variation is unsuitable for Celsius temperature or a near-zero mean because it depends on the arbitrary zero of the scale; use an absolute temperature variability limit instead. Chapter 32 checks the native ratio against an independent calculation, while Chapter 30 demonstrates explicit drift, oscillation and missing-data rejection.')
for n in [34]:
 p=chapter(n);t=p.read_text(encoding='utf-8-sig')
 t=t.replace('FPSO Heavy Oil','FPSO Water-Handling Surrogate').replace('FPSO heavy oil','FPSO water-handling surrogate')
 p.write_text(t,encoding='utf-8')
 changes.append({'chapter':n,'correction':'FPSO case title matches defined light-ended CPA surrogate; no heavy-oil calibration claim.'})
p=chapter(27);t=p.read_text(encoding='utf-8-sig')
marker='### 27.7.2'
pos=t.find(marker)
assert pos>=0
t=t[:pos]+('The following surface-process screen uses CPA and a three-phase separator. Its water input is the **overall water mole fraction**, not standard liquid water cut. Each sample starts from a fresh model; every separator, compressor and complete process boundary must close mass and component flow to $10^{-7}$ relative and energy to $10^{-5}$. The prescribed feed rate has no compressor feedback, so efficiency changes power but leaves the upstream gas rate unchanged. A failed case stops the calculation; it is not silently dropped from the distribution. Low/high bars identify input endpoints. Their span includes the base and is not a confidence interval or a proof of global extremes.\n\n')+t[pos:]
p.write_text(t,encoding='utf-8')
(B/'verification/scientific_revision/final_optimization_corrections.json').write_text(json.dumps(changes,indent=2,ensure_ascii=False),encoding='utf-8')
print(len(changes),'final corrections')
