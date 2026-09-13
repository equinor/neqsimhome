from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import subprocess
import sys

BOOK = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--project-root', required=True)
p.add_argument('--chapters', nargs='*', default=['ch09','ch10','ch14','ch16','ch17'])
a = p.parse_args()
def run(ch):
    result = subprocess.run([sys.executable,str(BOOK/'devtools/verify_foundations_java.py'),
                             '--project-root',a.project_root,'--chapter',ch], capture_output=True,text=True)
    return result.stdout
with ThreadPoolExecutor(max_workers=2) as pool:
    for future in as_completed([pool.submit(run,ch) for ch in a.chapters]):
        print(future.result(),flush=True)
