import json
log = json.load(open("notebook_execution_log.json"))
for r in log:
    print(f"{r['status']}: {r['notebook']}")
