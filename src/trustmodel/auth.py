"""Authentication for TrustModel's three products.

Eval, Monitor, and Govern all require a **free** TrustModel API key. Creating a
developer account takes ~30 seconds (no credit card) and grants **5 credits
($500)** to use across all three products.

    1. Sign up:  https://trustmodel.ai/signup   ->  copy your tm-... key
    2. Run:      trustmodel login                (paste the key)
       or set:   export TRUSTMODEL_API_KEY=tm-...

The key identifies you, meters your free credits for calibrated cloud scoring,
and unlocks the dashboard. (Local "bring-your-own-LLM" scoring doesn't spend
credits, but an account/key is still required so your usage and dashboard stay
in sync.)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

SIGNUP_URL = "https://trustmodel.ai/signup"
KEYS_URL = "https://trustmodel.ai/developers"
SIGNUP_CREDITS = 5          # free credits granted on signup
CREDIT_VALUE_USD = 100      # 1 credit = $100
_CRED_PATH = Path.home() / ".trustmodel" / "credentials.json"


class AuthError(Exception):
    """Raised when no API key is available."""


def _read_saved() -> Optional[str]:
    try:
        with open(_CRED_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh).get("api_key")
    except Exception:  # noqa: BLE001
        return None


def get_api_key() -> Optional[str]:
    """Return the API key from $TRUSTMODEL_API_KEY or the saved credentials file."""
    return os.getenv("TRUSTMODEL_API_KEY") or _read_saved()


def save_api_key(api_key: str) -> Path:
    """Persist the API key to ~/.trustmodel/credentials.json (used by `trustmodel login`)."""
    _CRED_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_CRED_PATH, "w", encoding="utf-8") as fh:
        json.dump({"api_key": api_key}, fh)
    try:
        _CRED_PATH.chmod(0o600)
    except Exception:  # noqa: BLE001
        pass
    return _CRED_PATH


_SIGNUP_MESSAGE = (
    "A free TrustModel API key is required to use Eval, Monitor, and Govern.\n\n"
    f"  Create a free developer account (no credit card) and get your key plus\n"
    f"  {SIGNUP_CREDITS} credits (${SIGNUP_CREDITS * CREDIT_VALUE_USD}) to use across all three products:\n\n"
    f"    1. Sign up:   {SIGNUP_URL}\n"
    f"    2. Run:       trustmodel login            (paste your tm-... key)\n"
    f"       or set:    export TRUSTMODEL_API_KEY=tm-...\n\n"
    f"  Manage keys & credits at {KEYS_URL}"
)


def require_api_key() -> str:
    """Return the API key, or raise AuthError with a friendly signup CTA."""
    key = get_api_key()
    if not key:
        raise AuthError(_SIGNUP_MESSAGE)
    return key
