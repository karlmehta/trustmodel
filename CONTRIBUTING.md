# Contributing to TrustModel

Thanks for helping make AI more trustworthy. 🛡️

## Dev setup

```bash
git clone https://github.com/karlmehta/trustmodel
cd trustmodel
pip install -e ".[dev,all]"
TRUSTMODEL_API_KEY=tm-test pytest        # tests run offline with the heuristic judge
```

## Good first issues

Look for the [`good first issue`](https://github.com/karlmehta/trustmodel/labels/good%20first%20issue)
label. Great starters:
- Add a PII pattern (e.g. UK/EU phone formats) to the heuristic judge.
- Improve a dimension rubric prompt in `dimensions.py`.
- Add a runnable example under `examples/`.

## Contributing a policy pack ⭐

Policy packs are plain YAML in `src/trustmodel/policy_packs/`. To add one (e.g. Brazil's LGPD,
Canada's AIDA, your company's internal policy):

1. Copy an existing pack (e.g. `eu-ai-act.yaml`) to `<your-id>.yaml`.
2. Fill in `id`, `name`, `references`, and `rules`. Two rule types:
   - `pattern` — `must_not_match` / `must_match` regex (fast, deterministic).
   - `dimension` — `dimension` + `min_score` (uses the eval engine).
3. Add a test asserting it blocks a clearly-violating string.
4. Open a PR. Community packs are very welcome and get credited in the README.

## Guidelines

- Keep the core dependency-light (`pyyaml` only; LLM/OTel/cloud are optional extras).
- Local mode must never call TrustModel servers.
- Run `ruff check .` and `pytest` before pushing.
- Be kind — see `CODE_OF_CONDUCT.md`.
