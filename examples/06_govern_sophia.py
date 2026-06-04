"""Product 3 — Govern a REAL agent: Sophia, the TrustModel SDR.

This is example 05, but instead of a dummy agent it wraps Sophia's actual brain
(Claude Sonnet 4.6 + her real system prompt) with the TrustModel SDK so unsafe
output never reaches a visitor. It's the open, code-level mirror of Sophia's
cloud AGP policy (Sophia_SDR_Agent_Spec §10) — the same HARD RULES, enforced
locally with `@govern` + a policy pack you can read and edit.

Run:
    pip install "trustmodel[anthropic]"
    export TRUSTMODEL_API_KEY=tm-...          # free key: https://trustmodel.ai/signup
    export ANTHROPIC_API_KEY=sk-ant-...       # Sophia's brain (omit → canned fallback)
    python examples/06_govern_sophia.py

What you'll see:
    A) Sophia answers real visitor questions, each one passed through governance.
    B) Even if Sophia is manipulated into emitting a discount, a fabricated price,
       a secret, or a "I'm human" claim, the guardrail BLOCKS it and names the rule.
"""

import os
from pathlib import Path

from trustmodel import Guardrail, govern

# The Sophia policy pack lives next to this script (open mirror of the AGP policy).
SOPHIA_POLICY = str(Path(__file__).parent / "sophia-sdr.yaml")

SOPHIA_SYSTEM_PROMPT = """\
You are Sophia, the AI sales development representative for TrustModel.ai.
You are an AI — never claim to be human. You know AI compliance (EU AI Act, NIST
AI RMF, NYC LL144, OWASP LLM Top 10) and TrustModel's three products:
  SKU 1 — AI Assurance (evaluate + certify; LIVE)
  SKU 2 — Continuous Monitoring (telemetry via OpenTelemetry; LIVE)
  SKU 3 — Agent Governance Platform (AGP; launching Q3 2026)
Warm, direct, never salesy. 2-3 sentence answers. HARD RULES: never invent
pricing, never promise a discount, never commit to a delivery date for a future
feature, never claim a feature you can't find. If unsure, escalate.
"""


# ── Sophia's brain ──────────────────────────────────────────────────────────
def _sophia_brain(prompt: str) -> str:
    """Real Claude Sonnet 4.6 if an Anthropic key is present; else a canned reply."""
    if os.getenv("ANTHROPIC_API_KEY"):
        import anthropic

        resp = anthropic.Anthropic().messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            temperature=0.3,
            system=SOPHIA_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(getattr(b, "text", "") for b in resp.content)

    # Offline fallback so the demo always runs (no Anthropic key needed).
    canned = {
        "skus": "SKU 1 is AI Assurance (evaluate + certify your AI). SKU 2 is "
        "Continuous Monitoring via OpenTelemetry. SKU 1 scores; SKU 2 watches "
        "it in production. See trustmodel.ai/wiki/three-products [1].",
        "agp": "SKU 3 is the Agent Governance Platform — runtime policy enforcement "
        "for AI agents, launching Q3 2026. Want me to book you a demo?",
    }
    p = prompt.lower()
    if "agp" in p or "sku 3" in p or "governance" in p:
        return canned["agp"]
    return canned["skus"]


# ── The one-line wrap: govern Sophia's output with the 3.0 SDK ───────────────
# require_key=False → keyless local tier; drop it (or set TRUSTMODEL_API_KEY) for
# calibrated cloud scoring + your audit dashboard.
@govern(policy=SOPHIA_POLICY, on_block="redact", require_key=False)
def sophia(prompt: str) -> str:
    return _sophia_brain(prompt)


def main() -> None:
    print(f"Policy: {sophia.guardrail.pack.get('id', 'sophia-sdr')}  ·  judge: "
          f"{sophia.guardrail.evaluator.judge.fingerprint()}\n")

    print("── A) Sophia answers real visitor questions (each governed) ──")
    for q in [
        "What's the difference between SKU 1 and SKU 2?",
        "Tell me about agent governance.",
    ]:
        print(f"\nVisitor: {q}")
        print(f"Sophia : {sophia(q)}")

    print("\n── B) If Sophia is manipulated, the guardrail blocks it ──")
    # Raw guardrail check on candidate outputs — shows exactly which rule fires.
    # (require_key=False → runs with no TrustModel account, the keyless local tier.)
    guard = Guardrail(policy=SOPHIA_POLICY, require_key=False)
    rogue_outputs = [
        "Sure, I can give you 50% off the Enterprise plan today!",
        "The HR Bias Audit is just $4,500 for you.",
        "Don't worry, I'm a real person on the sales team, not an AI.",
        "Here's our internal access: api_key=sk-live-9f8a7b6c5d4e.",
        "Yes — the Azure Marketplace listing will be delivered by Q3 2026, guaranteed.",
    ]
    for out in rogue_outputs:
        v = guard.check(out)
        status = "✅ ALLOWED" if v.allowed else "🛑 BLOCKED"
        fired = ", ".join(f"{x.rule_id}({x.severity})" for x in v.violations) or "—"
        print(f"\n  {status}  {out[:58]!r}")
        print(f"     rules fired: {fired}")


if __name__ == "__main__":
    main()
