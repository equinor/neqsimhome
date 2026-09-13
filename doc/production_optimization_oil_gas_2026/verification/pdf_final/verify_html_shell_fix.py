"""Compare canonical CSS on the identical full rendered book body in Chrome."""
from pathlib import Path
import hashlib,json,re,sys
B=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(B/'devtools'))
import check_html_renderer as checker
import book_render_html
OUT=B/'verification/pdf_final'
prior=json.loads((OUT/'html_shell_probe.json').read_text(encoding='utf-8'))
path=Path(prior['source']);source=path.read_text(encoding='utf-8')
assert hashlib.sha256(path.read_bytes()).hexdigest()==prior['source_sha256']
canonical_head=book_render_html._html_head('CSS regression')
css=re.findall(r'<style>(.*?)</style>',canonical_head,re.S)[-1]
old_css=re.findall(r'<style>(.*?)</style>',source,re.S)[-1]
assert 'main .katex {\n  position: relative;' in css
assert 'main .katex {\n  position: relative;' not in old_css
patched=source.replace('<style>'+old_css+'</style>','<style>'+css+'</style>',1)
assert source.split('</head>',1)[1]==patched.split('</head>',1)[1]
class PatchedDocument:
 def read_text(self,encoding):return patched
 def as_uri(self):return path.as_uri()
measurements=checker.browser_check(PatchedDocument(),OUT/'html_shell_fixed',Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe'),[500,1024])
checks=[]
for r in measurements:
 width=r.get('requestedWidth',r.get('width'))
 checks.append({'name':f'{width}px measurement','passed':'error' not in r})
 if 'error' in r:continue
 checks.extend([
  {'name':f'{width}px exact viewport','passed':r['width']==width},
  {'name':f'{width}px document has no horizontal overflow','passed':r['documentScrollWidth']<=width+1 and r['bodyScrollWidth']<=width+1 and r['maximumPageScrollX']<=1,
   'documentScrollWidth':r['documentScrollWidth'],'bodyScrollWidth':r['bodyScrollWidth'],'maximumPageScrollX':r['maximumPageScrollX']},
  {'name':f'{width}px visible shell/content inside viewport or local scroller','passed':not r['overflow'],'outliers':r['overflow']},
  {'name':f'{width}px all4356 formulas rendered with accessible MathML retained','passed':r['renderedMathCount']==4356 and r['accessibleMathCount']==4356 and not r['katexErrors']},
  {'name':f'{width}px all images load','passed':not r['missingImages'],'missing':r['missingImages']}])
passed=all(r['passed'] for r in checks)
report={'status':'passed' if passed else 'failed','source_html':str(path),'source_html_sha256':prior['source_sha256'],
 'canonical_renderer':str(Path(book_render_html.__file__)),'canonical_renderer_sha256':hashlib.sha256(Path(book_render_html.__file__).read_bytes()).hexdigest(),
 'diagnosis':'Real62px horizontal root scrolling originated from the absolutely positioned visually hidden KaTeX MathML layer. Hiding only that layer reduced562px document width to500px; hiding cover, navigation or SVG did not. Relative positioning of each math wrapper supplies its containing block without removing accessible MathML.',
 'before':prior['measurements'],'after':measurements,'checks':checks,
 'regression_scope':'Same entire35-chapter HTML body,202 images and4356 math boxes; replace only CSS with the current canonical _html_head output. No manuscript changes or full-book rebuild. Shared checker now inspects body*, root width and actual maximum horizontal page scroll.',
 'page_body_byte_identical':True,
 'original_release_html_unchanged':hashlib.sha256(path.read_bytes()).hexdigest()==prior['source_sha256']}
(OUT/'html_shell_review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':checks},indent=2))
raise SystemExit(not passed)
