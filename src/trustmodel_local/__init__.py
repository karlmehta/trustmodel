"""TrustModel — score any AI for trust across 10 dimensions.

Three products, one free API key (5 credits / $500 on signup → https://trustmodel.ai/signup):

    Product 1 — EVAL     score AI output / models / agents
    Product 2 — MONITOR  continuously score live LLM calls
    Product 3 — GOVERN   enforce policy packs before output ships

Quick start:

    from trustmodel_local import evaluate
    print(evaluate("Take 500mg of metformin twice daily.").trust_score)
"""

from ._env import load_dotenv_once

# Pick up keys from a local .env (ANTHROPIC_API_KEY / OPENAI_API_KEY / TRUSTMODEL_API_KEY)
# before anything reads the environment. Real env vars always win.
load_dotenv_once()

from .auth import AuthError, get_api_key, require_api_key, save_api_key
from .dimensions import DIMENSION_KEYS, DIMENSIONS

# Product 1 — Eval
from .eval import LocalEvaluator, TrustResult, Violation, evaluate

# Product 3 — Govern
from .govern import (
    GovernanceError,
    Guardrail,
    GuardrailVerdict,
    RuleViolation,
    available_policies,
    govern,
    load_policy,
)

# Product 2 — Monitor
from .monitor import Monitor, TraceEvent, auto_init, get_global_monitor, monitor

__version__ = "3.0.0"

__all__ = [
    "__version__",
    # auth
    "AuthError", "get_api_key", "require_api_key", "save_api_key",
    # eval
    "evaluate", "LocalEvaluator", "TrustResult", "Violation",
    # monitor
    "monitor", "Monitor", "TraceEvent", "auto_init", "get_global_monitor",
    # govern
    "Guardrail", "GuardrailVerdict", "GovernanceError", "RuleViolation",
    "govern", "available_policies", "load_policy",
    # dimensions
    "DIMENSIONS", "DIMENSION_KEYS",
]
