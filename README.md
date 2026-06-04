<div align="center">

<img src="assets/trustmodel-icon.png" alt="TrustModel" width="92" />

# TrustModel

### Score any AI for trust across 10 dimensions — Eval, Monitor, Govern.

[![PyPI](https://img.shields.io/pypi/v/trustmodel?color=3b5bfd&label=pip%20install%20trustmodel)](https://pypi.org/project/trustmodel/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://pypi.org/project/trustmodel/)
[![Stars](https://img.shields.io/github/stars/karlmehta/trustmodel?style=social)](https://github.com/karlmehta/trustmodel)
[![Demo](https://img.shields.io/badge/🤗-Live%20Demo-yellow)](https://huggingface.co/spaces/karlmehta/trustmodel-score-any-ai)

**One toolkit, three open products + the official cloud client, one free API key.**
Eval your AI · Monitor it in production · Govern what ships · or call the hosted `TrustModelClient`.

</div>

```bash
pip install trustmodel
trustmodel login          # free account → API key + 5 credits ($500). No credit card.
trustmodel eval "Take 500mg of metformin twice daily."
```

> **Already have the TrustModel SDK installed (v2.x)?** `eval` / `monitor` /
> `govern` and the MCP server arrived in **v3.0.0** — a plain `pip install` is a
> no-op for you. Upgrade explicitly:
>
> ```bash
> pip install -U trustmodel              # the three commands: evaluate / monitor / govern
> pip install -U "trustmodel[mcp]"       # …plus the embeddable MCP server
> ```
>
> Your existing `TrustModelClient` code keeps working unchanged — full details in
> the [**v2 → v3 upgrade guide**](UPGRADING.md).

> **`trustmodel: command not found`?** `pip install --user` drops the CLI in a
> per-user `bin/` that may not be on your `PATH` (e.g. `~/.local/bin` on Linux,
> `~/Library/Python/3.x/bin` on macOS). Two fixes:
>
> ```bash
> # A) run it as a module — always works, no PATH changes needed
> python -m trustmodel login
>
> # B) add pip's user bin to PATH (find it with: python -m site --user-base)
> export PATH="$(python -m site --user-base)/bin:$PATH"   # add to ~/.zshrc or ~/.bashrc
> ```
>
> Installing into a virtualenv (`python -m venv .venv && source .venv/bin/activate`)
> avoids this entirely — the `trustmodel` script lands on your `PATH` automatically.

```text
🔴 TrustScore: 41/100  (Grade D)  [local]
   safety          ██········    18  ⚠
   accuracy        ██████····    55
   explainability  █████·····    47  ⚠
   privacy         █████████·    90
   … 6 more
   Flagged:
     • [high] safety: appears to give unverified medical/dosage advice
```

---

> ### Hi, I'm Karl 👋
> I'm the founder of TrustModel. I built this because *"is this AI safe to ship?"* shouldn't
> require a sales call to answer. Install it, read the code, and score your own AI across the
> same 10 dimensions our enterprise customers use. Your **first 5 credits ($500) are on me** —
> create a free account and you can run all three products today.
> — [@karlmehta](https://github.com/karlmehta)

---

## 🔑 One free key unlocks all three products

Every product needs a **free** TrustModel API key. Creating a developer account takes ~30 seconds,
needs **no credit card**, and grants **5 credits ($500)** to spend across Eval, Monitor, and Govern.

```bash
# 1. Sign up (free, 5 credits / $500):  https://trustmodel.ai/signup
# 2. Save your key:
trustmodel login
# or:  export TRUSTMODEL_API_KEY=tm-...
```

> Calibrated **cloud** scoring spends credits (your first scan per model is free). **Local**
> scoring with *your own* OpenAI/Anthropic key is unmetered — the account just keeps your usage
> and dashboard in sync.

---

## Product 1 — 🎯 Eval

Score any AI output across 10 trust dimensions and roll it into a 0–100 **TrustScore**.

```python
from trustmodel import evaluate

result = evaluate("Based on your resume you're not a culture fit. We can't say why.")
print(result.trust_score)     # 38.0
print(result.grade)           # "F"
print(result.dimensions)      # {"explainability": 0.25, "fairness": 0.25, ...}
for v in result.violations:
    print(v.severity, v.dimension, v.detail)
```

```bash
trustmodel eval ./agent_outputs.jsonl --json     # batch / CI-friendly
trustmodel eval "..." --cloud                    # calibrated cloud score (uses credits)
```

Local scoring uses **your own LLM** as the judge (OpenAI or Anthropic), at temperature 0, on a
5-point ordinal scale per dimension — so it's reproducible and auditable. No LLM key? It falls
back to a transparent heuristic judge so it always runs (and tells you it did).

### Choose your judge LLM

You must install the matching SDK **and** provide that provider's key — installing one without the
other (or vice-versa) falls back to the heuristic judge. Pick **one**:

```bash
# Anthropic (Claude)
pip install "trustmodel[anthropic]"
export ANTHROPIC_API_KEY=sk-ant-...

# …or OpenAI
pip install "trustmodel[openai]"
export OPENAI_API_KEY=sk-...
```

Keys can also live in a **`.env` file** in your working directory — TrustModel loads it
automatically (real environment variables always win):

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
TRUSTMODEL_API_KEY=tm-...
```

Select which backend judges your output, in priority order:

1. the `prefer=` argument → `evaluate(text, prefer="anthropic")` / `LocalEvaluator(prefer="anthropic")`
2. the `$TRUSTMODEL_JUDGE` env var → `export TRUSTMODEL_JUDGE=anthropic`
3. auto-detect → OpenAI, then Anthropic, then the heuristic fallback

```python
from trustmodel import evaluate

result = evaluate("Take 500mg of metformin twice daily.", prefer="anthropic")
print(result.judge_fingerprint)   # anthropic/claude-haiku-4-5-...  ← confirms which judge ran
```

> If you set a key but the result still looks like the heuristic judge, TrustModel prints a
> warning explaining why (SDK not installed, key not found, etc.) — it never silently downgrades.

### Run the examples

```bash
git clone https://github.com/karlmehta/trustmodel && cd trustmodel
pip install -e ".[anthropic]"
export TRUSTMODEL_API_KEY=tm-...        # free key: https://trustmodel.ai/signup
export ANTHROPIC_API_KEY=sk-ant-...     # or put both in a .env file here
export TRUSTMODEL_JUDGE=anthropic

python examples/01_eval_local.py                       # score sample outputs
python examples/02_eval_ci.py outputs.jsonl 80         # CI gate: exit 1 if any score < 80
```

Each example prints the active judge fingerprint so you can confirm Claude (not the heuristic) is
doing the scoring.

## Product 2 — 📈 Monitor

Continuously score your AI **in production**. Wrap a function or auto-instrument your LLM client.

```python
from trustmodel import monitor

@monitor(threshold=80)            # alert when a response scores below 80
def answer(question: str) -> str:
    return my_llm(question)

answer("How do I treat a fever?")
print(answer.monitor.stats())     # {"count": 1, "avg_trust_score": 72.0, "below_threshold": 1}
```

One-line auto-instrumentation + optional OpenTelemetry export:

```python
from trustmodel import auto_init
auto_init(otel=True)                       # local inline scoring + OTEL spans
auto_init(api_key="tm-...")                # also forward traces to your cloud dashboard

import openai
openai.chat.completions.create(...)        # every call now scored automatically
```

## Product 3 — 🛡️ Govern

Enforce policy **before** AI output reaches a user or another tool. Open-source policy packs map
to real regulations.

```python
from trustmodel import Guardrail

gr = Guardrail("eu-ai-act")
verdict = gr.check("Based on your resume you're not a culture fit. We can't say why.")
print(verdict.allowed)            # False
print(verdict.violations)         # [art13-explainability (high), ...]
```

Gate an agent so blocked output never escapes:

```python
from trustmodel import govern

@govern(policy="owasp-llm", on_block="redact")
def agent(prompt: str) -> str:
    return my_agent(prompt)
```

```bash
trustmodel policies                              # eu-ai-act, nist-ai-rmf, owasp-llm, nyc-ll144
trustmodel govern "..." --policy nyc-ll144
```

Policy packs are plain YAML — [contribute one for your jurisdiction](CONTRIBUTING.md) (LGPD, AIDA, …).

### Govern a *deployed* agent — without sharing its source

`@govern` wraps any callable, so it can sit in front of a **remote** agent just as easily as a
local one. [`examples/06_govern_sophia.py`](examples/06_govern_sophia.py) governs **Sophia**, our
hosted SDR agent: the example is a thin HTTP client pointed at wherever Sophia is deployed (e.g. a
Vercel URL) and wraps her *responses* — her code, prompt, and model never leave your infra.

```bash
export SOPHIA_API_URL=https://<your-sophia>.vercel.app/api/sophia/chat
python examples/06_govern_sophia.py
```

```python
@govern(policy="sophia-sdr.yaml", on_block="redact", require_key=False)
def sophia(prompt: str) -> str:
    return call_deployed_sophia(prompt)     # HTTP → your hosted agent
```

**No sidecar or edge agent to install.** Enforcement runs in-process; for calibrated, audit-ready
verdicts it talks to the TrustModel control plane over plain **HTTPS** (set `TRUSTMODEL_API_KEY`).
Run it fully local and keyless with `require_key=False`. The same policy your agent enforces
server-side (via AGP) becomes a portable, public, auditable second layer anyone can run.

---

## The cloud client — `TrustModelClient`

The same `pip install trustmodel` also ships the **official TrustModel cloud client** for teams
on the hosted platform — calibrated TrustScores, agentic & RAG evaluation, COTS/Galileo
connectors, lending & HR bias verticals, batch jobs, and managed compliance frameworks.

```python
from trustmodel import TrustModelClient

client = TrustModelClient(api_key="tm-...")
result = client.evaluations.create(model="gpt-4o", prompt="...", response="...")
print(result.trust_score)

client.frameworks.list(domain="fair_lending")     # discover compliance frameworks
client.agentic.evaluate(...)                       # score multi-step agents
```

Auto-capture production agent traces and stream them to your TrustModel dashboard (enterprise
OTel mode — pass `agent_id`/`domain`/`frameworks` and `auto_init` routes to the telemetry forwarder):

```python
from trustmodel import auto_init

auto_init(
    api_key="tm-...",
    agent_id="loan-advisor",
    domain="fair_lending",
    frameworks=["eu-ai-act-high-risk", "iso-42001"],
)   # requires: pip install "trustmodel[telemetry]"
```

> **Two surfaces, one install.** The open engine above (`evaluate` / `monitor` / `Guardrail`)
> is **MIT** and runs locally. `TrustModelClient` is the **proprietary** cloud client. Both ship
> in the one `trustmodel` wheel — see [LICENSE](LICENSE) for the per-module split.

---

## The 10 dimensions

`safety` · `fairness` · `accuracy` · `privacy` · `transparency` · `robustness` · `accountability` · `explainability` · `compliance` · `reliability`

Mapped to **EU AI Act, NIST AI RMF, ISO 42001, NYC Local Law 144, OWASP LLM Top 10**.

## Why TrustModel?

|  | TrustModel | DeepEval / Promptfoo | Manual audit |
|---|:---:|:---:|:---:|
| Trust score across 10 governance dimensions | ✅ | partial | ✅ |
| Eval **+** live monitoring **+** runtime governance | ✅ | eval only | ❌ |
| Regulation-mapped policy packs (EU AI Act, LL144…) | ✅ | ❌ | ✅ |
| Runs locally with your own LLM | ✅ | ✅ | ❌ |
| Calibrated, audit-ready score + report | ✅ (cloud) | ❌ | ✅ |
| Time to first result | **30 sec** | minutes | weeks |
| Cost | free + $500 credits | free | $15k+ |

## MCP server — use TrustModel from any agent

Expose Eval and Govern to any [Model Context Protocol](https://modelcontextprotocol.io/) client (Claude Code, Cursor, Claude Desktop, …). **Local `evaluate`, `govern`, and `policies` need no API key**; `score_cloud` gives the calibrated, audit-ready score with a free key.

```bash
pip install "trustmodel[mcp]"
trustmodel-mcp        # or:  trustmodel mcp   — runs the server on stdio
```

Zero-install with [uv](https://docs.astral.sh/uv/):

```bash
uvx --from "trustmodel[mcp]" trustmodel-mcp
```

Register it with Claude Code:

```bash
claude mcp add trustmodel -- uvx --from "trustmodel[mcp]" trustmodel-mcp
```

Or add to Claude Desktop / Cursor (`claude_desktop_config.json` / `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "trustmodel": {
      "command": "uvx",
      "args": ["--from", "trustmodel[mcp]", "trustmodel-mcp"]
    }
  }
}
```

| Tool | Key? | What it does |
|---|---|---|
| `evaluate` | none | Local TrustScore across 10 dimensions (heuristic, or your own OpenAI/Anthropic key as judge). |
| `govern` | none | Allow/block check against a policy pack (eu-ai-act, nist-ai-rmf, nyc-ll144, owasp-llm, …). |
| `policies` | none | List built-in policy packs. |
| `score_cloud` | free key | Calibrated, benchmarked, audit-ready cloud TrustScore (`TRUSTMODEL_API_KEY` + `trustmodel[cloud]`). |

> The `mcp` extra requires Python ≥ 3.10. There's also a TypeScript MCP server — [`@trustmodel/mcp-server`](https://www.npmjs.com/package/@trustmodel/mcp-server) ([repo](https://github.com/karlmehta/trustmodel-mcp)).

## Open core (Linux → Red Hat)

The **engine** (`evaluate` / `monitor` / `govern` / `Guardrail` + policy packs) is **MIT-licensed**
and free — run it forever. The **`TrustModelClient` cloud client**, calibrated hosted TrustScore,
PDF compliance reports, certification badges, and in-VPC agent governance are the commercial layer
at **[trustmodel.ai](https://trustmodel.ai)** and ship under the proprietary
[TrustModel SDK License](LICENSE). One `pip install trustmodel`, two licenses — upgrade when you
need a score you can hand to an auditor.

## Links

📚 [Docs & wiki](https://trustmodel.ai/wiki) · 🤗 [Live demo](https://huggingface.co/spaces/karlmehta/trustmodel-score-any-ai) · 💬 [Discussions](https://github.com/karlmehta/trustmodel/discussions) · 🔑 [Get your free key](https://trustmodel.ai/signup)

<div align="center">

**⭐ If this is useful, star it — it's how I know to keep building.**

</div>
