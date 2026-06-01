"""Smoke tests for the MCP server tool handlers.

These exercise the FastMCP tool functions directly (no transport) and prove the
no-key local tier works: evaluate/govern/policies need no API key, and score_cloud
degrades gracefully when no key is set. Skipped if the optional `mcp` extra
(pip install "trustmodel[mcp]") is not installed.
"""

import pytest

pytest.importorskip("mcp", reason="requires the 'mcp' extra: pip install \"trustmodel[mcp]\"")

from trustmodel import mcp_server  # noqa: E402


@pytest.fixture(autouse=True)
def _no_key(monkeypatch):
    """Run every test as if no TrustModel API key is available anywhere."""
    monkeypatch.delenv("TRUSTMODEL_API_KEY", raising=False)
    import trustmodel.auth as auth
    monkeypatch.setattr(auth, "_read_saved", lambda: None)


def test_evaluate_works_with_no_key():
    data = mcp_server.evaluate("The capital of France is Paris.")
    assert 0 <= data["trust_score"] <= 100
    assert data["grade"] in {"A", "B", "C", "D", "F"}
    assert len(data["dimensions"]) == 10
    assert data["calibrated"] is False
    assert "note" in data


def test_govern_works_with_no_key():
    data = mcp_server.govern(
        "Based on your resume you're not a culture fit. We can't share why.",
        policy="nyc-ll144",
    )
    assert data["blocked"] is True
    assert data["policy"] == "nyc-ll144"
    assert any(v["severity"] == "high" for v in data["violations"])


def test_policies_lists_packs():
    data = mcp_server.policies()
    for expected in ("eu-ai-act", "owasp-llm", "nist-ai-rmf", "nyc-ll144"):
        assert expected in data["available_policies"]


def test_score_cloud_degrades_without_key():
    data = mcp_server.score_cloud("The capital of France is Paris.")
    assert data["calibrated"] is False
    assert "error" in data
    assert "hint" in data  # never crashes — returns guidance instead
