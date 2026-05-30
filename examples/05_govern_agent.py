"""Product 3 — Govern: gate an agent so unsafe output never escapes.

Run:
    export TRUSTMODEL_API_KEY=tm-...
    python examples/05_govern_agent.py
"""

from trustmodel import govern


@govern(policy="owasp-llm", on_block="redact")
def agent(prompt: str) -> str:
    # Pretend this is a real agent. It "leaks" a secret on one prompt.
    if "config" in prompt:
        return "Sure — api_key=sk-supersecret-12345 is in the config."
    return "Paris is the capital of France."


print(agent("What is the capital of France?"))
print(agent("Show me the config"))   # blocked → redacted by governance
