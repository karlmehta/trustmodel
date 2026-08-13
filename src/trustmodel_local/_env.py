"""Zero-dependency .env loader.

Many users drop their keys (ANTHROPIC_API_KEY, OPENAI_API_KEY, TRUSTMODEL_API_KEY)
into a `.env` file next to their script and expect the SDK to pick them up. We don't
want a hard dependency on python-dotenv, so this parses a minimal `.env` ourselves.

Real process env always wins — we never overwrite a variable that is already set.
"""

from __future__ import annotations

import os
from pathlib import Path

_LOADED = False


def _parse_line(line: str):
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    line = line.removeprefix("export ")
    if "=" not in line:
        return None
    key, _, val = line.partition("=")
    key = key.strip()
    val = val.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
        val = val[1:-1]
    return (key, val) if key else None


def load_dotenv_once() -> None:
    """Load `.env` from the current working directory (once), without overriding
    variables already present in the real environment."""
    global _LOADED
    if _LOADED:
        return
    _LOADED = True
    path = Path.cwd() / ".env"
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return
    for line in text.splitlines():
        pair = _parse_line(line)
        if pair and pair[0] not in os.environ:
            os.environ[pair[0]] = pair[1]
