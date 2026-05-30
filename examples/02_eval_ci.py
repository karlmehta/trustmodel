"""Product 1 — Eval as a CI gate: fail the build if any output scores below a threshold.

Run:
    export TRUSTMODEL_API_KEY=tm-...
    python examples/02_eval_ci.py outputs.jsonl 80
Exit code 1 if any line scores below the threshold (use it as a pipeline gate).
"""

import json
import sys

from trustmodel import LocalEvaluator

path = sys.argv[1] if len(sys.argv) > 1 else "outputs.jsonl"
threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 80.0

evaluator = LocalEvaluator()
failures = 0
with open(path, encoding="utf-8") as fh:
    for i, line in enumerate(fh, 1):
        line = line.strip()
        if not line:
            continue
        text = json.loads(line)["output"] if line.startswith("{") else line
        result = evaluator.evaluate(text)
        status = "PASS" if result.trust_score >= threshold else "FAIL"
        if status == "FAIL":
            failures += 1
        print(f"[{status}] line {i}: {result.trust_score:.0f}/100")

print(f"\n{failures} output(s) below {threshold:.0f}.")
sys.exit(1 if failures else 0)
