"""Optional cloud upgrade for all three products.

The open-source engine scores locally. With your TrustModel API key you can also
get the **calibrated, benchmarked, audit-ready** TrustScore from the cloud — and
forward monitored traces to your dashboard. Cloud scoring draws on your credits
(you start with 5 free / $500). Local "bring-your-own-LLM" scoring is unmetered.
"""

from __future__ import annotations

from typing import Optional

from .auth import KEYS_URL, require_api_key

API_BASE = "https://api.trustmodel.ai"


class CloudUnavailable(Exception):
    pass


class CloudClient:
    """Thin client for calibrated cloud scoring (pip install 'trustmodel[cloud]')."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = API_BASE):
        self.api_key = api_key or require_api_key()
        self.base_url = base_url.rstrip("/")

    def _session(self):
        try:
            import requests  # lazy; requires trustmodel[cloud]
        except Exception as e:  # noqa: BLE001
            raise CloudUnavailable(
                "Install the cloud extra to use calibrated scoring: "
                "pip install 'trustmodel[cloud]'"
            ) from e
        return requests

    def evaluate(self, output: str, context: Optional[str] = None) -> dict:
        """Calibrated cloud TrustScore. Consumes credits (first scan per model is free)."""
        requests = self._session()
        try:
            r = requests.post(
                f"{self.base_url}/v1/free-scan/evaluate",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"output": output, "context": context, "model_type": "chat"},
                timeout=45,
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            raise CloudUnavailable(
                f"Cloud scoring unavailable ({e}). Falling back to local scoring is "
                f"available via LocalEvaluator. Manage credits at {KEYS_URL}."
            ) from e

    def credits(self) -> Optional[int]:
        requests = self._session()
        try:
            r = requests.get(
                f"{self.base_url}/v1/credits",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=20,
            )
            r.raise_for_status()
            return r.json().get("balance")
        except Exception:  # noqa: BLE001
            return None


def attach_forwarder(monitor, api_key: str) -> None:
    """Wire a Monitor to forward scored events to the cloud dashboard (best-effort)."""
    try:
        client = CloudClient(api_key=api_key)
    except Exception:  # noqa: BLE001
        return

    original_on_alert = monitor.on_alert

    def _forward(ev):
        try:
            client._session().post(  # fire-and-forget; never break the app
                f"{client.base_url}/v1/telemetry/event",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"trust_score": ev.trust_score, "grade": ev.grade,
                      "dimensions": ev.dimensions, "alert": ev.below_threshold},
                timeout=5,
            )
        except Exception:  # noqa: BLE001
            pass
        if original_on_alert:
            original_on_alert(ev)

    monitor.on_alert = _forward
