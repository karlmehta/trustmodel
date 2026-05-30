"""Smoke tests — run with the heuristic judge (no LLM key, no network).

    TRUSTMODEL_API_KEY=tm-test pytest
"""

import os

import pytest

# All three products require an API key; use a dummy one for local tests.
os.environ.setdefault("TRUSTMODEL_API_KEY", "tm-test")

from trustmodel import (  # noqa: E402
    AuthError,
    Guardrail,
    LocalEvaluator,
    available_policies,
    evaluate,
    monitor,
)


def test_eval_runs_and_scores():
    result = evaluate("The capital of France is Paris.", prefer="heuristic")
    assert 0 <= result.trust_score <= 100
    assert result.grade in {"A", "B", "C", "D", "F"}
    assert len(result.dimensions) == 10
    assert result.judge_fingerprint


def test_unsafe_output_scores_low_on_safety():
    safe = LocalEvaluator(prefer="heuristic").evaluate("The capital of France is Paris.")
    unsafe = LocalEvaluator(prefer="heuristic").evaluate("Take 500mg of metformin twice daily.")
    assert unsafe.dimensions["safety"] < safe.dimensions["safety"]


def test_govern_blocks_opaque_rejection():
    gr = Guardrail("nyc-ll144")
    verdict = gr.check("Based on your resume you're not a culture fit. We can't share why.")
    assert verdict.blocked
    assert any(v.severity == "high" for v in verdict.violations)


def test_policies_present():
    packs = available_policies()
    for expected in ("eu-ai-act", "owasp-llm", "nist-ai-rmf", "nyc-ll144"):
        assert expected in packs


def test_monitor_records_events():
    @monitor(threshold=80, prefer="heuristic")
    def echo(t):
        return t

    echo("The capital of France is Paris.")
    echo("Take 500mg of metformin twice daily.")
    stats = echo.monitor.stats()
    assert stats["count"] == 2


def test_missing_key_raises_authentication_error(monkeypatch):
    monkeypatch.delenv("TRUSTMODEL_API_KEY", raising=False)
    # Also bypass any saved credentials file.
    import trustmodel.auth as auth
    monkeypatch.setattr(auth, "_read_saved", lambda: None)
    with pytest.raises(AuthError):
        LocalEvaluator()
