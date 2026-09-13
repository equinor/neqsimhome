from pathlib import Path
from collections import Counter
import json
BOOK=Path(__file__).resolve().parents[1]
report=json.loads((BOOK/'verification/scientific_revision/optimization_review.json').read_text(encoding='utf-8'))
for chapter in report['chapters']:
    unqualified=[e for e in chapter['entries'] if e['classification']=='executed_numerical_or_api_demonstration_unqualified']
    print(chapter['chapter'],len(unqualified))
    for e in unqualified:print(e['number'],e['language'],e['heading'])
