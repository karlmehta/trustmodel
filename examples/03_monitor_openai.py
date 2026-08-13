"""Product 2 — Monitor: auto-score every OpenAI call in production.

Run:
    export TRUSTMODEL_API_KEY=tm-...
    export OPENAI_API_KEY=sk-...
    pip install "trustmodel[openai]"
    python examples/03_monitor_openai.py
"""

from trustmodel_local import auto_init, get_global_monitor

# One line: instruments openai so every chat completion is scored inline.
auto_init(threshold=80)

import openai

openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "How should I treat a high fever at home?"}],
)

mon = get_global_monitor()
print("Monitored calls:", mon.stats())
for ev in mon.events:
    print(f"  {ev.trust_score:.0f}/100 (grade {ev.grade}){'  ⚠ alert' if ev.below_threshold else ''}")
