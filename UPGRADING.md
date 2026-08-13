# Upgrading — the local engine is now `trustmodel-local`

The open-source engine (**Eval / Monitor / Govern**) and the **embeddable MCP server** now ship
as their own package, **`trustmodel-local`** (import `trustmodel_local`). This is a deliberate
split from the hosted **`trustmodel`** cloud SDK — two packages, two APIs, no more name collision.

## TL;DR

```bash
pip install -U "trustmodel-local[mcp]"     # everything: engine + MCP server
# or, if you don't need the MCP server:
pip install -U trustmodel-local            # engine only (evaluate / monitor / govern)
```

Verify:

```bash
python -c "import trustmodel_local; print(trustmodel_local.__version__)"
```

## Migrating from the old `trustmodel` engine imports

If you were importing the local engine from `trustmodel`, change the module name:

| Old | New |
|---|---|
| `from trustmodel import evaluate` | `from trustmodel_local import evaluate` |
| `from trustmodel import monitor` | `from trustmodel_local import monitor` |
| `from trustmodel import govern, Guardrail` | `from trustmodel_local import govern, Guardrail` |
| `trustmodel-mcp` / `trustmodel mcp` (MCP server) | unchanged — CLI commands stay `trustmodel` / `trustmodel-mcp` |

The CLI command names (`trustmodel`, `trustmodel-mcp`) are unchanged; only the Python import module changed.

## The hosted cloud SDK is a SEPARATE package

`TrustModelClient` and the hosted API surface (`evaluations`, `galileo`, `cots`, `agentic`,
`frameworks`, `guardrails.decide()`, `batch_jobs`, …) live in the **separate** official SDK:

```bash
pip install trustmodel        # the hosted SDK
```
```python
from trustmodel import TrustModelClient      # cloud SDK — NOT this repo
```

Installing `trustmodel-local` does **not** give you `TrustModelClient`, and installing `trustmodel`
does **not** give you the local `evaluate`/`monitor`/`govern`/`Guardrail` engine. Pick the one you need
(or install both — they no longer collide).

## Requirements

- The MCP server (`[mcp]` extra) requires **Python 3.10+** (the `mcp` SDK does).
- The rest of the package supports **Python 3.9+**.

## Troubleshooting

- `ModuleNotFoundError: No module named 'trustmodel_local'` → `pip install -U trustmodel-local`.
- `ImportError: cannot import name 'evaluate' from 'trustmodel'` → you're importing the local engine
  from the wrong package. Use `from trustmodel_local import evaluate`.
- `ModuleNotFoundError: No module named 'mcp'` when running `trustmodel-mcp` →
  `pip install -U "trustmodel-local[mcp]"` (and use Python ≥ 3.10).

## License note

The engine (eval/monitor/govern + policy packs) is MIT — see [LICENSE](LICENSE). The hosted
`trustmodel` cloud SDK is a separate, proprietary package.
