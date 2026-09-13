"""Inspect the actual full HTML book at desktop and narrow browser widths."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

BOOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / '.build/python_packages'))
from bs4 import BeautifulSoup
from check_html_renderer import browser_check

parser = argparse.ArgumentParser()
parser.add_argument('--widths', default='1024,500')
args = parser.parse_args()
path = BOOK / '.build/release_candidate/submission/book.html'
sha = hashlib.sha256(path.read_bytes()).hexdigest()
soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
chapters = soup.select('section.chapter')
ids = [node['id'] for node in soup.select('[id]')]
missing = [node.get('src') for node in soup.select('img[src]')
           if not node['src'].startswith(('http:', 'https:', 'data:'))
           and not (path.parent / node['src']).is_file()]
report = {'html': str(path), 'sha256': sha, 'chapters': len(chapters),
          'images': len(soup.select('img')), 'figures': len(soup.select('figcaption')),
          'missing_images': missing, 'duplicate_ids': sorted({x for x in ids if ids.count(x) > 1})}
report['browser'] = browser_check(path, BOOK / 'verification/full_book_html',
    Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe'),
    [int(x) for x in args.widths.split(',')])
report['source_unchanged'] = hashlib.sha256(path.read_bytes()).hexdigest() == sha
report['passed'] = (len(chapters) == 35 and not missing and not report['duplicate_ids']
    and report['source_unchanged'] and all(not item.get('error') and not item.get('overflow')
    and not item.get('missingImages') and not item.get('katexErrors')
    and item.get('documentScrollWidth', float('inf')) <= item.get('width', 0) + 1
    and item.get('bodyScrollWidth', float('inf')) <= item.get('width', 0) + 1
    and item.get('maximumPageScrollX', float('inf')) <= 1
    and item.get('accessibleMathCount', 0) == item.get('renderedMathCount', 0)
    and item.get('renderedMathCount', 0) > 0 for item in report['browser']))
(BOOK / 'verification/full_book_html_check.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
raise SystemExit(0 if report['passed'] else 1)
