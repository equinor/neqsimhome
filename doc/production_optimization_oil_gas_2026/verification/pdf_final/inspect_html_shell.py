from pathlib import Path
import sys,json,hashlib
B=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(B/'devtools'))
import check_html_renderer as checker
checker.MEASURE_SCRIPT=r'''<script>
window.addEventListener('load',function(){setTimeout(function(){
 const width=window.innerWidth;
 function widths(){return {document:document.documentElement.scrollWidth,body:document.body.scrollWidth,rootClient:document.documentElement.clientWidth,bodyClient:document.body.clientWidth,scrollX:window.scrollX};}
 function desc(el){let c=el.className;return el.tagName+(el.id?'#'+el.id:'')+(typeof c==='string'&&c?'.'+c.trim().replace(/\s+/g,'.'):'');}
 function parents(el){const a=[];for(let p=el.parentElement;p&&a.length<8;p=p.parentElement){const c=getComputedStyle(p);const r=p.getBoundingClientRect();a.push({node:desc(p),overflowX:c.overflowX,position:c.position,left:r.left,right:r.right});}return a;}
 const baseline=widths(),outside=[];
 for(const el of document.querySelectorAll('*')){
  if(['STYLE','SCRIPT','HEAD','META','LINK','TITLE'].includes(el.tagName))continue;
  const cs=getComputedStyle(el);if(cs.display==='none'||cs.visibility==='hidden')continue;
  const r=el.getBoundingClientRect();if(r.width<1||r.height<1)continue;
  if(r.left< -1||r.right>width+1)outside.push({node:desc(el),left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height,position:cs.position,overflowX:cs.overflowX,text:el.textContent.trim().slice(0,160),ancestors:parents(el)});
 }
 window.scrollTo(10000,0);const forcedScroll=widths();window.scrollTo(0,0);
 const experiments=[];
 for(const selector of ['.katex-mathml','.katex svg','.book-cover-page','nav.sidebar','.katex','.title-page']){
  const style=document.createElement('style');style.textContent=selector+'{display:none!important}';document.head.appendChild(style);experiments.push({selector,widths:widths()});style.remove();
 }
 const data={width,baseline,forcedScroll,experiments,outsideCount:outside.length,
  rightBoundary:outside.filter(r=>r.right<=baseline.document+2).sort((a,b)=>b.right-a.right).slice(0,60),
  greatestRight:outside.sort((a,b)=>b.right-a.right).slice(0,12),
  shell:[...document.body.children].map(el=>({node:desc(el),rect:el.getBoundingClientRect().toJSON(),scrollWidth:el.scrollWidth,css:getComputedStyle(el).overflowX})),
  katexAvailable:!!window.katex,mathCount:document.querySelectorAll('.katex').length};
 const report=document.createElement('script');report.type='application/json';report.id='renderer-measurements';report.textContent=JSON.stringify(data);document.body.appendChild(report);
},1000)});
</script>'''
source=json.loads((B/'verification/full_book_html_check.json').read_text(encoding='utf-8'))['html']
path=Path(source);sha=hashlib.sha256(path.read_bytes()).hexdigest()
result=checker.browser_check(path,B/'verification/pdf_final/html_shell_probe',Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe'),[500])
(B/'verification/pdf_final/html_shell_probe.json').write_text(json.dumps({'source':source,'source_sha256':sha,'measurements':result},indent=2),encoding='utf-8')
print(json.dumps({'baseline':result[0].get('baseline'),'forcedScroll':result[0].get('forcedScroll'),'experiments':result[0].get('experiments'),'error':result[0].get('error'),'outsideCount':result[0].get('outsideCount')},indent=2))
