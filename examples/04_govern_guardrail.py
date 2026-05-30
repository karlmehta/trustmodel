"""Product 3 — Govern: enforce a policy pack on AI output.

Run:
    export TRUSTMODEL_API_KEY=tm-...
    python examples/04_govern_guardrail.py
"""

from trustmodel import Guardrail, available_policies

print("Available policy packs:", ", ".join(available_policies()), "\n")

gr = Guardrail("nyc-ll144")   # automated-hiring rules

for text in [
    "You were not selected. Here is the specific skills gap and how to address it: ...",
    "Based on your resume you're not a culture fit. We can't share why.",
]:
    verdict = gr.check(text)
    status = "ALLOWED ✅" if verdict.allowed else "BLOCKED ⛔"
    print(f"{status}  {text[:55]!r}")
    for v in verdict.violations:
        print(f"    • [{v.severity}] {v.rule_id}: {v.description}")
    print()
