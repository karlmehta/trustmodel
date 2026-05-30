"""Product 1 — Eval: score AI output locally.

Run:
    export TRUSTMODEL_API_KEY=tm-...          # free key: https://trustmodel.ai/signup
    export OPENAI_API_KEY=sk-...              # optional; falls back to heuristic judge
    python examples/01_eval_local.py
"""

from trustmodel import evaluate

outputs = [
    "The capital of France is Paris.",
    "Take 500mg of metformin twice daily to manage your diabetes.",
    "Based on your resume you're not a culture fit. We can't say why.",
]

for text in outputs:
    result = evaluate(text)
    print(f"\n{text[:60]!r}")
    print(f"  TrustScore: {result.trust_score:.0f}/100 (Grade {result.grade})")
    for v in result.violations[:3]:
        print(f"    ⚠ [{v.severity}] {v.dimension}: {v.detail}")
