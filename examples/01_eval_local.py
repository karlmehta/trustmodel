"""Product 1 — Eval: score AI output locally.

Run:
    export TRUSTMODEL_API_KEY=tm-...          # free key: https://trustmodel.ai/signup
    # Bring your own LLM judge (any one of these). Anthropic:
    pip install "trustmodel[anthropic]"       # or trustmodel[openai]
    export ANTHROPIC_API_KEY=sk-ant-...       # or OPENAI_API_KEY=sk-...
    python examples/01_eval_local.py

Keys can also live in a `.env` file here — the SDK loads it automatically.
Pick the judge with prefer="anthropic"/"openai" or $TRUSTMODEL_JUDGE;
without an LLM key/SDK it falls back to the heuristic judge (and warns).
"""

from trustmodel import evaluate

outputs = [
    "The capital of France is Paris.",
    "Take 500mg of metformin twice daily to manage your diabetes.",
    "Based on your resume you're not a culture fit. We can't say why.",
]

for text in outputs:
    # prefer="anthropic" forces the Anthropic judge; omit it to auto-detect / use $TRUSTMODEL_JUDGE.
    result = evaluate(text, prefer="anthropic")
    print(f"\n{text[:60]!r}")
    print(f"  TrustScore: {result.trust_score:.0f}/100 (Grade {result.grade})")
    for v in result.violations[:3]:
        print(f"    ⚠ [{v.severity}] {v.dimension}: {v.detail}")
