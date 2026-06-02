# Upgrading to TrustModel v3.0.0

v3.0.0 unifies the open-source engine (**Eval / Monitor / Govern**) and the
**embeddable MCP server** into the same `trustmodel` package that previously
shipped only the cloud SDK. If you're on **v2.x**, here's how to move up.

## TL;DR

```bash
pip install -U "trustmodel[mcp]"     # everything: engine + MCP server
# or, if you don't need the MCP server:
pip install -U trustmodel            # engine only (evaluate / monitor / govern)
```

> ⚠️ A plain `pip install trustmodel` will **not** upgrade an existing install —
> pip treats the requirement as already satisfied and does nothing. The `-U`
> (`--upgrade`) flag is required.

Verify:

```bash
python -c "import trustmodel; print(trustmodel.__version__)"   # → 3.0.0
```

## What you get

| Import | New in 3.0.0 | Needs |
|---|---|---|
| `from trustmodel import evaluate` | ✅ | base install |
| `from trustmodel import monitor` | ✅ | base install |
| `from trustmodel import govern, Guardrail` | ✅ | base install |
| `trustmodel-mcp` / `trustmodel mcp` (MCP server) | ✅ | `trustmodel[mcp]`, Python ≥ 3.10 |
| `from trustmodel import TrustModelClient` | unchanged | base install |

## What stays the same

- **`TrustModelClient` and all exceptions are preserved** — existing cloud SDK
  code runs unchanged after the upgrade.
- The cloud API surface (`evaluations`, `galileo`, `cots`, `agentic`,
  `frameworks`, `batch_jobs`, …) is untouched.

## The one behavior change

`auto_init` is now a dispatcher:

- `auto_init(api_key="tm-...", agent_id=..., domain=..., frameworks=[...])`
  → routes to the OTel trace-forwarder, **exactly as in v2.x** (also reachable
  explicitly at `trustmodel.telemetry.auto_init`).
- `auto_init()` with no enterprise args → enables local inline scoring + optional
  OpenTelemetry.

Existing `auto_init(...)` calls that pass `agent_id`/`domain`/`frameworks` are
unaffected.

## Requirements

- The MCP server (`[mcp]` extra) requires **Python 3.10+** (the `mcp` SDK does).
- The rest of the package still supports **Python 3.7+**.

## Troubleshooting

- `ImportError: cannot import name 'evaluate' from 'trustmodel'` → you're still
  on v2.x. Run `pip install -U trustmodel`.
- `ModuleNotFoundError: No module named 'mcp'` when running `trustmodel-mcp` →
  install the extra: `pip install -U "trustmodel[mcp]"` (and use Python ≥ 3.10).
- `trustmodel: command not found` → pip installed the CLI to a per-user `bin/`
  not on your `PATH`; run `python -m trustmodel ...` or add
  `"$(python -m site --user-base)/bin"` to `PATH`.

## License note

The engine (eval/monitor/govern + policy packs) is MIT. `TrustModelClient` is
the proprietary cloud client. Both ship in the one wheel — see [LICENSE](LICENSE).
