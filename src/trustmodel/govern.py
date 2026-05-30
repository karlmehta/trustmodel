"""Product 3 — GOVERN.

Enforce policy on AI output before it reaches a user or another tool. A Guardrail
loads a policy pack (open-source YAML mapped to a regulation) and evaluates the
output against its rules — both fast pattern rules and dimension-threshold rules
backed by the eval engine.

    from trustmodel import Guardrail
    gr = Guardrail("eu-ai-act")
    verdict = gr.check("Based on your resume you're not a culture fit. We can't say why.")
    print(verdict.allowed, verdict.violations)

Or gate an agent so blocked output never escapes:

    from trustmodel import govern

    @govern(policy="owasp-llm", on_block="redact")
    def agent(prompt: str) -> str:
        return my_agent(prompt)
"""

from __future__ import annotations

import functools
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml

from .auth import require_api_key
from .eval import LocalEvaluator

_PACKS_DIR = Path(__file__).parent / "policy_packs"


@dataclass
class RuleViolation:
    rule_id: str
    description: str
    severity: str
    kind: str  # "pattern" | "dimension"


@dataclass
class GuardrailVerdict:
    allowed: bool
    violations: List[RuleViolation] = field(default_factory=list)
    policy: str = ""

    @property
    def blocked(self) -> bool:
        return not self.allowed


def available_policies() -> List[str]:
    return sorted(p.stem for p in _PACKS_DIR.glob("*.yaml"))


def load_policy(policy: str) -> dict:
    """Load a built-in policy pack by id, or a path to a custom YAML pack."""
    path = Path(policy)
    if not path.exists():
        path = _PACKS_DIR / f"{policy}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"Unknown policy '{policy}'. Built-in packs: {', '.join(available_policies())}, "
            f"or pass a path to a custom .yaml pack."
        )
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class Guardrail:
    """Evaluate output against a policy pack and decide allow/block."""

    def __init__(self, policy: str = "eu-ai-act", evaluator: Optional[LocalEvaluator] = None,
                 block_severity: str = "high"):
        # Govern requires a free TrustModel account/API key (grants 5 credits / $500).
        self.api_key = require_api_key()
        self.policy_id = policy
        self.pack = load_policy(policy)
        self.rules = self.pack.get("rules", [])
        self._evaluator = evaluator
        self.block_severity = block_severity  # block when a violation >= this severity
        self._needs_eval = any(r.get("type") == "dimension" for r in self.rules)

    @property
    def evaluator(self) -> LocalEvaluator:
        if self._evaluator is None:
            self._evaluator = LocalEvaluator()
        return self._evaluator

    def check(self, output: str, context: Optional[str] = None) -> GuardrailVerdict:
        violations: List[RuleViolation] = []

        # Run the eval engine once only if a dimension rule needs it.
        dim_scores = {}
        if self._needs_eval:
            dim_scores = self.evaluator.evaluate(output, context=context).dimensions

        for rule in self.rules:
            rid = rule.get("id", "rule")
            sev = rule.get("severity", "medium")
            rtype = rule.get("type", "pattern")
            desc = rule.get("description", rid)

            if rtype == "pattern":
                # "should_not" semantics: a match is a violation (score inversion).
                pat = rule.get("must_not_match")
                if pat and re.search(pat, output or "", re.IGNORECASE):
                    violations.append(RuleViolation(rid, desc, sev, "pattern"))
                must = rule.get("must_match")
                if must and not re.search(must, output or "", re.IGNORECASE):
                    violations.append(RuleViolation(rid, desc, sev, "pattern"))

            elif rtype == "dimension":
                dim = rule["dimension"]
                min_score = float(rule.get("min_score", 0.65))
                if dim_scores.get(dim, 1.0) < min_score:
                    violations.append(RuleViolation(rid, desc, sev, "dimension"))

        order = {"high": 0, "medium": 1, "low": 2}
        violations.sort(key=lambda v: order.get(v.severity, 1))
        allowed = not any(order.get(v.severity, 1) <= order[self.block_severity] for v in violations)
        return GuardrailVerdict(allowed=allowed, violations=violations, policy=self.policy_id)


_REDACTION = "[blocked by TrustModel governance: policy violation]"


def govern(policy: str = "eu-ai-act", on_block: str = "raise", block_severity: str = "high"):
    """Decorator that gates a function's string output through a Guardrail.

    on_block:
      * "raise"  -> raise GovernanceError (default)
      * "redact" -> return a safe placeholder instead of the violating output
      * "flag"   -> return the output unchanged but attach the verdict
    """
    gr = Guardrail(policy=policy, block_severity=block_severity)

    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            out = fn(*args, **kwargs)
            text = out if isinstance(out, str) else str(out)
            verdict = gr.check(text)
            if verdict.blocked:
                if on_block == "redact":
                    return _REDACTION
                if on_block == "flag":
                    return out
                raise GovernanceError(verdict)
            return out
        wrapper.guardrail = gr
        return wrapper
    return deco


class GovernanceError(Exception):
    def __init__(self, verdict: GuardrailVerdict):
        self.verdict = verdict
        details = "; ".join(f"{v.rule_id} ({v.severity})" for v in verdict.violations)
        super().__init__(f"Output blocked by policy '{verdict.policy}': {details}")
