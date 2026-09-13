from pathlib import Path
import re,json,hashlib,datetime
BOOK=Path(__file__).resolve().parents[1]
folder=BOOK/'verification/scientific_revision'
for p in sorted((BOOK/'chapters').glob('ch*/chapter.md'))[:18]:
 t=p.read_text(encoding='utf-8').replace('foundationMichelsen1982','michelsen1982').replace('foundationFisher2023','emerson2023valves')
 p.write_text(t,encoding='utf-8')
extra=folder/'foundations_refs.bib'
t=extra.read_text(encoding='utf-8').replace('foundationMichelsen1982','michelsen1982')
records=[
('article','kunz2012',{'author':'Kunz, Oliver and Wagner, Wolfgang','title':'The GERG-2008 Wide-Range Equation of State for Natural Gases and Other Mixtures: An Expansion of GERG-2004','journal':'Journal of Chemical \& Engineering Data','year':'2012','volume':'57','number':'11','pages':'3032--3091','doi':'10.1021/je300655b'}),
('article','foundationPeneloux1982',{'author':"P{\\'e}neloux, Andr{\\'e} and Rauzy, Evelyne and Fr{\\'e}ze, Richard",'title':'A consistent correction for Redlich-Kwong-Soave volumes','journal':'Fluid Phase Equilibria','year':'1982','volume':'8','number':'1','pages':'7--23','doi':'10.1016/0378-3812(82)80002-2'}),
('manual','foundationPRMS2018',{'author':'{Society of Petroleum Engineers and co-sponsors}','title':'Petroleum Resources Management System','year':'2018','url':'https://www.spe.org/en/industry/petroleum-resources-management-system-2018/','note':'Resources and reserves classification; no commercial reserve assignment follows solely from tank material balance'}),
('article','turner1969',{'author':'Turner, R. G. and Hubbard, M. G. and Dukler, A. E.','title':'Analysis and Prediction of Minimum Flow Rate for the Continuous Removal of Liquids from Gas Wells','journal':'Journal of Petroleum Technology','year':'1969','volume':'21','number':'11','pages':'1475--1482','doi':'10.2118/2198-PA','url':'https://www.ipt.ntnu.no/~curtis/courses/PhD-PVT/PVT-HOT-Vienna-May-2016x/e-course/Papers/misc/Turner-Minimum-Rate-to-Lift.pdf'}),
('misc','foundationIADCtree',{'author':'{International Association of Drilling Contractors}','title':'Horizontal tree','url':'https://iadclexicon.org/horizontal-tree/','note':'IADC Lexicon; accessed 12 September 2026'}),
('misc','foundationVigdis2021',{'author':'{Equinor}','title':'Giving Vigdis a boost','year':'2021','url':'https://www.equinor.com/news/archive/20210806-giving-vigdis-boost'}),
('misc','foundationGullfaks2015',{'author':'{Statoil}','title':'Gullfaks subsea compression starts up','year':'2015','url':'https://www.equinor.com/news/archive/2015/10/12/12OctGullfakssubseacompression'}),
('misc','foundationAsgard2015',{'author':'{Statoil}','title':'Asgard subsea compression starts up','year':'2015','url':'https://www.equinor.com/news/archive/2015/09/17/17SepAasgardsubsea'}),
('misc','foundationAsgard2025',{'author':'{Equinor}','title':'Phase 2 of Asgard subsea compression','year':'2025','url':'https://www.equinor.com/news/20250926-phase-2-asgard-subsea-compression'}),
('manual','foundationGPSAerrata',{'author':'{Gas Processors Suppliers Association}','title':'GPSA Engineering Data Book, 13th edition: SI Errata, July 2013','year':'2013','url':'https://www.gpamidstream.org/wp-content/uploads/2025/08/Errata-SI_07-13.pdf','note':'Corrected Hammerschmidt constant: 1297 for methanol and ethylene glycol in the SI equation; errata are not a new edition'}),
('article','deboer1995',{'author':'de Boer, R. B. and Leerlooyer, K. and Eigner, M. R. P. and van Bergen, A. R. D.','title':'Screening of Crude Oils for Asphalt Precipitation: Theory, Practice, and the Selection of Inhibitors','journal':'SPE Production \& Facilities','year':'1995','volume':'10','number':'1','pages':'55--61','doi':'10.2118/24987-PA'}),
('manual','foundationOSPARmethod',{'author':'{OSPAR Commission}','title':'OSPAR reference method of analysis for dispersed oil in produced water','year':'2005','url':'https://www.ospar.org/documents?v=32591','note':'Agreement 2005-15, modified ISO 9377-2; use current permit and applicable amendments'}),
('misc','foundationCCPmethods',{'author':'{CCP Project}','title':'Performance functions: polytropic head methods','url':'https://ccp-centrifugal-compressor-performance.readthedocs.io/en/stable/references/performance_functions.html','note':'Implementation documentation for Schultz and related compressor methods; accessed 12 September 2026'}),
('misc','foundationSiemensA65',{'author':'{Siemens}','title':'Floating power plants support New York City energy strategy','year':'2019','url':'https://press.siemens.com/global/de/pressemitteilung/schwimmende-kraftwerke-von-siemens-unterstuetzen-new-york-citys-energiestrategie','note':'Manufacturer terminology for SGT-A65, formerly Industrial Trent 60; not an offshore installation performance guarantee'}),
('misc','foundationNorwayTax2026',{'author':'{Norwegian Ministry of Finance}','title':'Avgiftssatser 2026','year':'2026','url':'https://www.regjeringen.no/no/tema/okonomi-og-budsjett/skatter-og-avgifter/skatte-og-avgiftssatser/avgiftssatser-2026/id3121982/','note':'Dated tax schedule; offshore natural-gas CO2 tax distinguished from ETS and other fuels'}),
('manual','foundationASTMD3232026',{'author':'{ASTM International}','title':'ASTM D323-26: Standard Test Method for Vapor Pressure of Petroleum Products (Reid Method)','year':'2026','url':'https://store.astm.org/standards/d323','note':'Publisher scope: Reid absolute pressure at 37.8 degrees C; method distinct from bubble-point TVP'})]
existing=set(re.findall(r'@\w+\s*\{\s*([^,]+)',t))
for typ,key,fields in records:
 if key not in existing:t+='\n@'+typ+'{'+key+',\n'+',\n'.join('  '+k+' = {'+v+'}' for k,v in fields.items())+'\n}\n'
extra.write_text(t,encoding='utf-8')
refdir=folder/'references';items=[]
for p in refdir.rglob('*.pdf'):
 items.append({'path':str(p.relative_to(refdir)), 'source':'Emerson Control Valve Handbook' if 'emerson' in str(p).lower() else p.stem, 'url':'https://www.emerson.com/documents/automation/control-valve-handbook-en-3661206.pdf' if 'emerson' in str(p).lower() else '', 'retrieved':'2026-09-12','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'review_status':'reviewed','relevance':'Primary manufacturer flow-sizing constants and unit conventions; not a valve selection guarantee'})
# The release orchestrator owns the shared references index. Supply only our
# addition, and require it to load/merge the existing collection rather than
# overwrite evidence from other agents.
(folder/'foundations_reference_additions.json').write_text(json.dumps([x for x in items if 'emerson' in x['path'].lower()],indent=2),encoding='utf-8')
