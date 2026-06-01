<div align="center">

<img src="assets/trustmodel-icon.png" alt="TrustModel" width="92" />

# TrustModel

### Score any AI for trust across 10 dimensions — Eval, Monitor, Govern.

[![PyPI](https://img.shields.io/pypi/v/trustmodel?color=3b5bfd&label=pip%20install%20trustmodel)](https://pypi.org/project/trustmodel/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://pypi.org/project/trustmodel/)
[![Stars](https://img.shields.io/github/stars/karlmehta/trustmodel?style=social)](https://github.com/karlmehta/trustmodel)
[![Demo](https://img.shields.io/badge/🤗-Live%20Demo-yellow)](https://huggingface.co/spaces/karlmehta/trustmodel-score-any-ai)

**One toolkit, three products, one free API key.**
Eval your AI · Monitor it in production · Govern what ships.

</div>

```bash
pip install trustmodel
trustmodel login          # free account → API key + 5 credits ($500). No credit card.
trustmodel eval "Take 500mg of metformin twice daily."
```

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
back to a transparent heuristic judge so it always runs.

```bash
pip install "trustmodel[openai]"      # or [anthropic]
export OPENAI_API_KEY=sk-...
```

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

## Open core (Linux → Red Hat)

This toolkit is **MIT-licensed** and free. The **calibrated hosted TrustScore**, PDF compliance
reports, certification badges, and in-VPC agent governance are the commercial layer at
**[trustmodel.ai](https://trustmodel.ai)**. Run the open source forever; upgrade when you need a
score you can hand to an auditor.

## Links

📚 [Docs & wiki](https://trustmodel.ai/wiki) · 🤗 [Live demo](https://huggingface.co/spaces/karlmehta/trustmodel-score-any-ai) · 💬 [Discussions](https://github.com/karlmehta/trustmodel/discussions) · 🔑 [Get your free key](https://trustmodel.ai/signup)

<div align="center">

**⭐ If this is useful, star it — it's how I know to keep building.**

</div>
