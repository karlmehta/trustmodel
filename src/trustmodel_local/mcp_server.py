"""TrustModel MCP server.

Exposes the TrustModel engine to any Model Context Protocol client (Claude Code,
Cursor, Claude Desktop, …) as agent tools — built on the official MCP Python SDK
(FastMCP). Wraps the existing local engine; no scoring is reimplemented here.

Tools:
  * evaluate(output, context)        — local TrustScore across 10 dimensions. NO key.
  * govern(text, policy, context)    — policy-pack allow/block check. NO key.
  * policies()                       — list built-in policy packs. NO key.
  * score_cloud(output, context)     — calibrated, audit-ready cloud TrustScore.
                                       Needs a free TRUSTMODEL_API_KEY; degrades
                                       gracefully (never crashes) if absent.

Run:
    pip install "trustmodel[mcp]"
    trustmodel-mcp                 # or:  trustmodel mcp
    uvx --from "trustmodel[mcp]" trustmodel-mcp
"""

from __future__ import annotations

from typing import Optional

from mcp.server.fastmcp import FastMCP

from .eval import LocalEvaluator
from .govern import Guardrail, available_policies

mcp = FastMCP("trustmodel")

_LOCAL_NOTE = (
    "local score — uncalibrated (heuristic, or your own OpenAI/Anthropic key as judge). "
    "For a calibrated, benchmarked, audit-ready TrustScore call score_cloud with a free "
    "TRUSTMODEL_API_KEY (https://trustmodel.ai/signup)."
)


@mcp.tool()
def evaluate(output: str, context: Optional[str] = None) -> dict:
    """Score AI output locally across the 10 TrustModel dimensions (safety, fairness,
    accuracy, privacy, transparency, robustness, accountability, explainability,
    compliance, reliability) and roll it into a 0-100 TrustScore.

    No API key required — runs on your machine. Uses your OPENAI_API_KEY /
    ANTHROPIC_API_KEY as the judge if available, otherwise a transparent heuristic
    fallback. Returns trust_score, grade, per-dimension scores, and violations."""
    result = LocalEvaluator(require_key=False).evaluate(output, context=context)
    data = result.to_dict()
    data["note"] = _LOCAL_NOTE
    return data


@mcp.tool()
def govern(text: str, policy: str = "eu-ai-act", context: Optional[str] = None) -> dict:
    """Check text against a governance policy pack and decide allow/block.

    No API key required. `policy` is a built-in pack id (e.g. eu-ai-act, nist-ai-rmf,
    nyc-ll144, owasp-llm — call policies() to list them) or a path to a custom .yaml
    pack. Returns allowed/blocked, the policy id, and the list of rule violations."""
    gr = Guardrail(policy=policy, require_key=False)
    verdict = gr.check(text, context=context)
    return {
        "allowed": verdict.allowed,
        "blocked": verdict.blocked,
        "policy": verdict.policy,
        "violations": [v.__dict__ for v in verdict.violations],
        "note": _LOCAL_NOTE,
    }


@mcp.tool()
def policies() -> dict:
    """List the built-in governance policy packs available to govern()."""
    return {"available_policies": available_policies()}


@mcp.tool()
def score_cloud(output: str, context: Optional[str] = None) -> dict:
    """Calibrated, benchmarked, audit-ready cloud TrustScore.

    Requires a free TRUSTMODEL_API_KEY (5 free credits / $500) and the cloud extra
    (pip install "trustmodel[cloud]"). If either is missing this returns a clear
    upgrade message instead of raising — local evaluate/govern always work with no key."""
    try:
        from .cloud import CloudClient
    except ImportError:
        return _cloud_unavailable("the TrustModel cloud client could not be imported")

    try:
        client = CloudClient()
    except Exception as e:  # AuthError when no key is set
        return _cloud_unavailable(str(e))

    try:
        data = client.evaluate(output, context=context)
        if isinstance(data, dict):
            data.setdefault("calibrated", True)
            return data
        return {"calibrated": True, "result": data}
    except Exception as e:  # CloudUnavailable, network/HTTP errors, missing requests extra
        return _cloud_unavailable(str(e))


def _cloud_unavailable(reason: str) -> dict:
    return {
        "calibrated": False,
        "error": "calibrated cloud scoring is unavailable",
        "reason": reason,
        "hint": (
            "Set TRUSTMODEL_API_KEY (free, 5 credits) — get one at "
            "https://trustmodel.ai/signup — and install the cloud extra: "
            'pip install "trustmodel[cloud]". Local evaluate/govern need no key.'
        ),
    }


def run() -> None:
    """Start the MCP server on stdio (the default MCP transport)."""
    mcp.run()


def main() -> None:
    """Console-script entry point (`trustmodel-mcp`)."""
    run()


if __name__ == "__main__":
    main()
