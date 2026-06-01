"""TrustModel command-line interface.

    trustmodel login                       # save your free API key (5 credits / $500)
    trustmodel eval "some AI output"        # Product 1: score 10 dimensions
    trustmodel eval ./outputs.txt --json
    trustmodel govern "..." --policy eu-ai-act   # Product 3: policy gate
    trustmodel monitor --demo               # Product 2: inline scoring demo
    trustmodel policies                     # list built-in policy packs
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .auth import AuthError, SIGNUP_URL, require_api_key, save_api_key


def _read_input(arg: str) -> str:
    p = Path(arg)
    if p.exists() and p.is_file():
        return p.read_text(encoding="utf-8")
    return arg


def _print_result(result, as_json: bool):
    if as_json:
        print(json.dumps(result.to_dict(), indent=2))
        return
    badge = "🟢" if result.trust_score >= 80 else "🟡" if result.trust_score >= 65 else "🔴"
    cal = "calibrated" if result.calibrated else "local"
    print(f"\n{badge} TrustScore: {result.trust_score:.0f}/100  (Grade {result.grade})  [{cal}]")
    print(f"   judge: {result.judge_fingerprint}\n")
    for s in result.scores:
        bar = "█" * int(round(s.value * 10)) + "·" * (10 - int(round(s.value * 10)))
        flag = "  ⚠" if s.value < 0.65 else ""
        print(f"   {s.key:<15} {bar} {s.value*100:5.0f}{flag}")
    if result.violations:
        print("\n   Flagged:")
        for v in result.violations[:8]:
            print(f"     • [{v.severity}] {v.dimension}: {v.detail}")
    print()


def _cmd_login(args):
    token = args.token
    if not token:
        print(f"Get a free API key (5 credits / $500) at {SIGNUP_URL}")
        try:
            token = input("Paste your tm-... API key: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return 1
    if not token:
        print("No key provided.")
        return 1
    path = save_api_key(token)
    print(f"✓ Saved. Credentials at {path}")
    return 0


def _cmd_eval(args):
    from .eval import LocalEvaluator
    text = _read_input(args.input)
    if args.cloud:
        from .cloud import CloudClient, CloudUnavailable
        try:
            data = CloudClient().evaluate(text, context=args.context)
            print(json.dumps(data, indent=2) if args.json else data)
            return 0
        except CloudUnavailable as e:
            print(f"(cloud) {e}\nFalling back to local scoring.\n", file=sys.stderr)
    result = LocalEvaluator(prefer=args.judge).evaluate(text, context=args.context)
    _print_result(result, args.json)
    return 0


def _cmd_govern(args):
    from .govern import Guardrail
    text = _read_input(args.input)
    gr = Guardrail(policy=args.policy)
    verdict = gr.check(text, context=args.context)
    if args.json:
        print(json.dumps({
            "allowed": verdict.allowed, "policy": verdict.policy,
            "violations": [v.__dict__ for v in verdict.violations],
        }, indent=2))
        return 0 if verdict.allowed else 3
    status = "✅ ALLOWED" if verdict.allowed else "⛔ BLOCKED"
    print(f"\n{status}  (policy: {verdict.policy})")
    for v in verdict.violations:
        print(f"   • [{v.severity}] {v.rule_id}: {v.description}")
    print()
    return 0 if verdict.allowed else 3


def _cmd_monitor(args):
    from .monitor import monitor
    require_api_key()
    if not args.demo:
        print("Monitor is an SDK feature. Wrap your LLM calls:\n")
        print("    from trustmodel import monitor\n")
        print("    @monitor(threshold=80)")
        print("    def answer(q): return my_llm(q)\n")
        print("Run `trustmodel monitor --demo` to see it score sample responses.")
        return 0

    @monitor(threshold=80)
    def sample(text):
        return text

    for t in ["The capital of France is Paris.",
              "Take 500mg of metformin twice daily for your diabetes."]:
        sample(t)
    print(json.dumps(sample.monitor.stats(), indent=2))
    return 0


def _cmd_mcp(args):
    try:
        from .mcp_server import run
    except ImportError:
        print(
            "The MCP server needs the 'mcp' extra:\n\n"
            '    pip install "trustmodel[mcp]"\n\n'
            "Then run `trustmodel mcp` (or `trustmodel-mcp`) and point your MCP client at it.",
            file=sys.stderr,
        )
        return 2
    run()
    return 0


def _cmd_policies(args):
    from .govern import available_policies
    print("Built-in policy packs:")
    for p in available_policies():
        print(f"   • {p}")
    print("\nUse with:  trustmodel govern \"...\" --policy <id>")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="trustmodel",
        description="Score any AI for trust — Eval, Monitor, Govern. "
                    f"Free API key + 5 credits ($500): {SIGNUP_URL}",
    )
    parser.add_argument("--version", action="version", version=f"trustmodel {__version__}")
    sub = parser.add_subparsers(dest="command")

    p_login = sub.add_parser("login", help="save your free API key")
    p_login.add_argument("--token", help="tm-... API key (prompts if omitted)")
    p_login.set_defaults(func=_cmd_login)

    p_eval = sub.add_parser("eval", help="Product 1: score 10 trust dimensions")
    p_eval.add_argument("input", help="text to score, or a path to a file")
    p_eval.add_argument("--context", help="context the output was produced in")
    p_eval.add_argument("--judge", choices=["openai", "anthropic", "heuristic"],
                        help="local judge backend (auto-detected by default)")
    p_eval.add_argument("--cloud", action="store_true", help="use calibrated cloud scoring (uses credits)")
    p_eval.add_argument("--json", action="store_true", help="machine-readable output")
    p_eval.set_defaults(func=_cmd_eval)

    p_gov = sub.add_parser("govern", help="Product 3: enforce a policy pack")
    p_gov.add_argument("input", help="text to check, or a path to a file")
    p_gov.add_argument("--policy", default="eu-ai-act", help="policy pack id or path")
    p_gov.add_argument("--context", help="context the output was produced in")
    p_gov.add_argument("--json", action="store_true", help="machine-readable output")
    p_gov.set_defaults(func=_cmd_govern)

    p_mon = sub.add_parser("monitor", help="Product 2: inline scoring for live LLM calls")
    p_mon.add_argument("--demo", action="store_true", help="run a small scoring demo")
    p_mon.set_defaults(func=_cmd_monitor)

    p_pol = sub.add_parser("policies", help="list built-in policy packs")
    p_pol.set_defaults(func=_cmd_policies)

    p_mcp = sub.add_parser("mcp", help="run the MCP server (stdio) for MCP clients")
    p_mcp.set_defaults(func=_cmd_mcp)

    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    try:
        return args.func(args)
    except AuthError as e:
        print(f"\n{e}\n", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
