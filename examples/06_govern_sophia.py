"""Product 3 — Govern a DEPLOYED agent: Sophia, the TrustModel SDR.

Sophia is a real, hosted agent (closed source). This demo does NOT contain her
source, system prompt, or model — it's a thin client that points at wherever
Sophia is deployed (e.g. your Vercel URL) and wraps her *responses* with the
TrustModel SDK so unsafe output is caught before it reaches a visitor.

That's the whole point: anyone — TM employees or the public — can test the SDK
against the live agent without ever seeing Sophia's code.

    Open repo (this file)         Your infra (private)
    ┌───────────────────┐         ┌──────────────────────┐
    │ @govern(...)       │  HTTP   │ Sophia on Vercel      │
    │   → call_sophia()  │ ──────► │ /api/sophia/chat      │
    │   ← govern verdict │ ◄────── │ (AGP-governed server) │
    └───────────────────┘   SSE   └──────────────────────┘

Sophia is already governed server-side by AGP (SKU 3). This shows the *same*
policy enforced client-side with the open SDK — a portable, auditable second layer.

Run:
    export SOPHIA_API_URL=https://<your-sophia>.vercel.app/api/sophia/chat
    export SOPHIA_API_KEY=...                  # optional, if your endpoint requires it
    python examples/06_govern_sophia.py

No SOPHIA_API_URL set? Part B still runs — it shows the guardrail blocking
manipulated output, which needs no agent at all.
"""

import json
import os
import urllib.request
from pathlib import Path

from trustmodel import Guardrail, govern

# Policy pack lives next to this file — the open mirror of Sophia's AGP rules.
SOPHIA_POLICY = str(Path(__file__).parent / "sophia-sdr.yaml")

SOPHIA_API_URL = os.getenv("SOPHIA_API_URL")        # your deployed Sophia endpoint
SOPHIA_API_KEY = os.getenv("SOPHIA_API_KEY")        # optional bearer token


# Field names a reply's text might hide under, across common agent frameworks.
_TEXT_KEYS = ("text", "delta", "content", "reply", "response", "answer", "output", "message")


def _extract_text(obj) -> str:
    """Pull assistant text out of an arbitrary JSON value (recursive, best-effort)."""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return "".join(_extract_text(x) for x in obj)
    if isinstance(obj, dict):
        # OpenAI-style choices/messages first, then known text-bearing keys.
        if "choices" in obj:
            return _extract_text(obj["choices"])
        for k in _TEXT_KEYS:
            if k in obj:
                return _extract_text(obj[k])
    return ""


def call_sophia(prompt: str) -> str:
    """POST to the deployed Sophia and return her full reply text.

    Auto-detects the response shape so it works against most deployments:
      * SSE stream  (Sophia_SDR_Agent_Spec §13.1: `content_delta` → `text`)
      * plain JSON  ({"reply": "..."}, {"message": {"content": "..."}}, OpenAI-style, …)
      * raw text
    `call_sophia` is the only place that knows Sophia's wire format — tweak the
    payload / key names here if your endpoint differs.
    """
    if not SOPHIA_API_URL:
        raise RuntimeError("Set SOPHIA_API_URL to your deployed Sophia endpoint.")

    payload = {
        "visitor_id": "sdk-demo",
        "page_url": "https://trustmodel.ai/",
        "message": {"role": "user", "content": prompt},
    }
    headers = {"Content-Type": "application/json", "Accept": "text/event-stream, application/json"}
    if SOPHIA_API_KEY:
        headers["Authorization"] = f"Bearer {SOPHIA_API_KEY}"

    req = urllib.request.Request(
        SOPHIA_API_URL, data=json.dumps(payload).encode(), headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        ctype = resp.headers.get("Content-Type", "")
        body = resp.read().decode("utf-8", "replace")

    if "text/event-stream" in ctype or "\ndata:" in body or body.startswith("data:"):
        parts = []
        for line in body.splitlines():
            line = line.strip()
            if not line.startswith("data:"):
                continue
            chunk = line[len("data:"):].strip()
            if chunk in ("", "[DONE]"):
                continue
            try:
                parts.append(_extract_text(json.loads(chunk)))
            except json.JSONDecodeError:
                parts.append(chunk)               # plain-text SSE payload
        return "".join(parts).strip() or "(no content)"

    try:
        return _extract_text(json.loads(body)).strip() or "(no content)"
    except json.JSONDecodeError:
        return body.strip() or "(no content)"     # raw text response


# ── The one-line wrap: govern the deployed agent's output with the 3.0 SDK ────
# require_key=False → keyless local tier; set TRUSTMODEL_API_KEY for calibrated
# cloud scoring + your audit dashboard.
@govern(policy=SOPHIA_POLICY, on_block="redact", require_key=False)
def sophia(prompt: str) -> str:
    return call_sophia(prompt)


def main() -> None:
    guard = Guardrail(policy=SOPHIA_POLICY, require_key=False)
    print(f"Policy: {guard.pack.get('id', 'sophia-sdr')}  ·  judge: "
          f"{guard.evaluator.judge.fingerprint()}")

    print("\n── A) Live Sophia, every response governed by the SDK ──")
    if SOPHIA_API_URL:
        print(f"   → {SOPHIA_API_URL}")
        for q in [
            "What's the difference between SKU 1 and SKU 2?",
            "Can you give me a discount on the Enterprise plan?",
        ]:
            print(f"\nVisitor: {q}")
            print(f"Sophia : {sophia(q)}")     # redacted automatically if it violates
    else:
        print("   (skipped — set SOPHIA_API_URL to point at your Vercel deployment)")

    print("\n── B) The guardrail's teeth (no agent needed) ──")
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
