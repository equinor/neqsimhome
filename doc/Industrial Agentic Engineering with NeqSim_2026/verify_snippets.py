"""Execute the exact Python fences in the revised manuscript with stated context."""
from book_runtime import BOOK, bootstrap
from verify_examples import make_fluid
import argparse
import json
import re
import traceback


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()
    ns = bootstrap(args.project_root)
    records = []
    for path in sorted((BOOK / "chapters").glob("*/chapter.md")):
        fluid = make_fluid(ns)
        context = {"jneqsim": ns, "fluid": fluid,
                   "ops": ns.thermodynamicoperations.ThermodynamicOperations(fluid)}
        for i, code in enumerate(re.findall(r"```python\s*\n(.*?)```", path.read_text(encoding="utf-8"), re.S), 1):
            record = {"chapter": path.parent.name, "snippet": i}
            try:
                exec(compile(code, str(path) + ":snippet" + str(i), "exec"), context)
                record["status"] = "passed"
            except Exception:
                record.update(status="failed", error=traceback.format_exc())
            records.append(record)
    (BOOK / "verification/snippet_verification.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(json.dumps(records, indent=2))
    if any(r["status"] != "passed" for r in records):
        raise RuntimeError("Manuscript snippet verification failed")


if __name__ == "__main__":
    main()
