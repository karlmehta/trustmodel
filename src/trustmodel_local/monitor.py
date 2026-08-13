"""Product 2 — MONITOR.

Continuously score your AI in production. Wrap a function or an LLM client and
every response is scored inline across the 10 dimensions, with rolling stats,
threshold alerts, and an optional OpenTelemetry export.

Local-first (no account):

    from trustmodel_local import monitor

    @monitor(threshold=80)            # alert if a response scores below 80
    def answer(q: str) -> str:
        return my_llm(q)

Or instrument an OpenAI client in one line:

    from trustmodel_local import auto_init
    auto_init()                       # local inline scoring; auto_init(api_key=...) forwards to cloud
"""

from __future__ import annotations

import functools
import sys
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from .auth import require_api_key
from .eval import LocalEvaluator, TrustResult


@dataclass
class TraceEvent:
    output: str
    trust_score: float
    grade: str
    dimensions: dict
    below_threshold: bool


@dataclass
class Monitor:
    """Scores text events inline and keeps rolling telemetry."""
    threshold: Optional[float] = None        # 0–100; alert/flag below this
    prefer: Optional[str] = None             # judge backend preference
    otel: bool = False                       # emit OpenTelemetry spans if available
    on_alert: Optional[Callable[[TraceEvent], None]] = None
    events: List[TraceEvent] = field(default_factory=list)
    _evaluator: LocalEvaluator = field(default=None, repr=False)
    _tracer: object = field(default=None, repr=False)

    def __post_init__(self):
        # Monitor requires a free TrustModel account/API key (grants 5 credits / $500).
        require_api_key()
        self._evaluator = LocalEvaluator(prefer=self.prefer)
        if self.otel:
            self._tracer = _try_get_otel_tracer()

    def record(self, output: str, context: Optional[str] = None) -> TraceEvent:
        result: TrustResult = self._evaluator.evaluate(output, context=context)
        below = self.threshold is not None and result.trust_score < self.threshold
        ev = TraceEvent(output, result.trust_score, result.grade, result.dimensions, below)
        self.events.append(ev)
        self._emit_otel(ev, result)
        if below:
            (self.on_alert or _default_alert)(ev)
        return ev

    # --- telemetry ---------------------------------------------------------
    def _emit_otel(self, ev: TraceEvent, result: TrustResult):
        if not self._tracer:
            return
        with self._tracer.start_as_current_span("trustmodel.eval") as span:
            span.set_attribute("trustmodel.trust_score", ev.trust_score)
            span.set_attribute("trustmodel.grade", ev.grade)
            for k, v in ev.dimensions.items():
                span.set_attribute(f"trustmodel.dim.{k}", round(v, 3))
            if ev.below_threshold:
                span.set_attribute("trustmodel.alert", True)

    def stats(self) -> dict:
        if not self.events:
            return {"count": 0}
        scores = [e.trust_score for e in self.events]
        return {
            "count": len(scores),
            "avg_trust_score": round(sum(scores) / len(scores), 1),
            "min": min(scores),
            "below_threshold": sum(1 for e in self.events if e.below_threshold),
        }


def monitor(threshold: Optional[float] = None, prefer: Optional[str] = None,
            otel: bool = False, on_alert: Optional[Callable] = None):
    """Decorator: score the (string) return value of a function on every call.

    The wrapped function's return value is passed through unchanged; the score is
    attached as `result.__trustmodel__` and surfaced via alerts/telemetry.
    """
    mon = Monitor(threshold=threshold, prefer=prefer, otel=otel, on_alert=on_alert)

    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            out = fn(*args, **kwargs)
            text = out if isinstance(out, str) else _extract_text(out)
            if text:
                mon.record(text)
            return out
        wrapper.monitor = mon  # expose the Monitor for .stats()/.events
        return wrapper
    return deco


# Global monitor wired by auto_init() so instrumented clients can find it.
_GLOBAL: Optional[Monitor] = None


def auto_init(api_key: Optional[str] = None, threshold: Optional[float] = None,
              otel: bool = False, prefer: Optional[str] = None) -> Monitor:
    """Zero-config entry point.

    * Local mode (no api_key): enables inline scoring + optional OpenTelemetry.
    * Cloud mode (api_key set): also forwards scored traces to TrustModel cloud
      for calibrated scoring and dashboards (see trustmodel.cloud).
    """
    global _GLOBAL
    _GLOBAL = Monitor(threshold=threshold, prefer=prefer, otel=otel)
    if api_key:
        from .cloud import attach_forwarder
        attach_forwarder(_GLOBAL, api_key)
    _instrument_openai(_GLOBAL)
    return _GLOBAL


def get_global_monitor() -> Optional[Monitor]:
    return _GLOBAL


# --- helpers ---------------------------------------------------------------
def _extract_text(obj) -> str:
    """Best-effort text extraction from common LLM response objects."""
    try:
        if hasattr(obj, "choices"):            # OpenAI chat completion
            return obj.choices[0].message.content or ""
        if hasattr(obj, "content"):            # Anthropic message
            return "".join(getattr(b, "text", "") for b in obj.content)
    except Exception:  # noqa: BLE001
        pass
    return str(obj) if obj is not None else ""


def _instrument_openai(mon: Monitor) -> bool:
    """Monkeypatch openai chat completions to score each response. No-op if openai absent."""
    try:
        from openai.resources.chat import completions as _c
    except Exception:  # noqa: BLE001
        return False
    if getattr(_c.Completions.create, "__trustmodel_wrapped__", False):
        return True
    original = _c.Completions.create

    @functools.wraps(original)
    def create(self, *args, **kwargs):
        resp = original(self, *args, **kwargs)
        try:
            mon.record(_extract_text(resp))
        except Exception:  # noqa: BLE001 - monitoring must never break the call
            pass
        return resp

    create.__trustmodel_wrapped__ = True
    _c.Completions.create = create
    return True


def _try_get_otel_tracer():
    try:
        from opentelemetry import trace
        return trace.get_tracer("trustmodel")
    except Exception:  # noqa: BLE001
        return None


def _default_alert(ev: TraceEvent):
    print(
        f"⚠  TrustModel alert: response scored {ev.trust_score:.0f}/100 "
        f"(grade {ev.grade}) — below threshold.",
        file=sys.stderr,
    )
