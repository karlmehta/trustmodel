"""TrustModel, live, on a real agent — Sophia, the TrustModel SDR.

Sophia runs in production (on Vercel) and is evaluated, monitored, and governed by
TrustModel's own three products. This script prints her **real** results in your
terminal — the exact same numbers published at https://trustmodel.ai/sophia.

It's read-only: it fetches the public TrustScore endpoint, so anyone can run it
with zero setup and no keys. This is the "see it yourself" companion to the live
page — and proof TrustModel eats its own dog food.

Run:
    python examples/00_sophia_live.py                 # tenant=trustmodel
    python examples/00_sophia_live.py acme            # any tenant slug

Then govern a live Sophia response yourself with examples/06_govern_sophia.py.
"""

import json
import sys
import urllib.request

try:
    from trustmodel.dimensions import grade as _grade   # reuse the SDK's 0-100 → letter
except Exception:  # noqa: BLE001 - keep runnable even if the package isn't importable
    def _grade(score: float) -> str:
        return "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else \
               "D" if score >= 60 else "F"

TENANT = sys.argv[1] if len(sys.argv) > 1 else "trustmodel"
ENDPOINT = (
    "https://hfycechaipqausrrbmiq.supabase.co/functions/v1/"
    f"sophia-trust-score?tenant_slug={TENANT}"
)
PAGE = "https://trustmodel.ai/sophia"


def bar(score, width=10):
    if score is None:
        return "·" * width
    filled = round((score / 100) * width)
    return "█" * filled + "·" * (width - filled)


def main():
    with urllib.request.urlopen(ENDPOINT, timeout=20) as r:
        data = json.load(r)

    tenant = data.get("tenant", {}).get("display_name", TENANT)
    print(f"\nTrustModel · Sophia — live results for {tenant}")
    print(f"(the same numbers published at {PAGE})\n")

    # ── SKU 1 · EVAL ─────────────────────────────────────────────────────────
    score = data.get("score") or {}
    if score.get("status") == "evaluated":
        overall = score["overall"]
        print(f"SKU 1 · EVAL     TrustScore {overall}/100  (Grade {_grade(overall)})")
        print(f"                 {score.get('source','?')} · "
              f"evaluated {str(score.get('evaluated_at',''))[:10]}")
        for key, val in (score.get("dimensions") or {}).items():
            print(f"    {key:<15} {bar(val)}  {val}")
        if score.get("probes_run"):
            print(f"    red-team probes: {score['probes_passed']}/{score['probes_run']} passed")
    else:
        print("SKU 1 · EVAL     pending — no evaluation has run yet")

    # ── SKU 2 · MONITOR ──────────────────────────────────────────────────────
    # Populated once the live runtime is instrumented; forward-compatible here.
    mon = data.get("monitor")
    print()
    if mon:
        print(f"SKU 2 · MONITOR  {mon.get('calls_30d', 0)} live calls (30d) · "
              f"avg TrustScore {mon.get('avg_score', '—')} · "
              f"{mon.get('below_threshold', 0)} below threshold")
    else:
        print("SKU 2 · MONITOR  pending — live-call telemetry coming online")

    # ── SKU 3 · GOVERN ───────────────────────────────────────────────────────
    audit = data.get("audit") or {}
    print()
    gov = audit.get("decisions")  # optional richer breakdown
    if gov:
        print(f"SKU 3 · GOVERN   {audit.get('events_30d', 0)} governed events (30d) · "
              f"{gov.get('allowed', 0)} allowed · {gov.get('blocked', 0)} blocked · "
              f"{gov.get('redacted', 0)} redacted")
    else:
        print(f"SKU 3 · GOVERN   {audit.get('events_30d', 0)} governed events (30d) · "
              f"policy: {audit.get('policy_id') or 'pending'}")

    print(f"\nSee it live → {PAGE}")
    print("Govern a live Sophia reply yourself → examples/06_govern_sophia.py\n")


if __name__ == "__main__":
    main()
