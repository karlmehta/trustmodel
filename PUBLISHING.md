# Publishing `trustmodel` (PyPI) + the Python MCP server to the MCP Registry

The Python MCP server ships inside the `trustmodel` PyPI package (the `[mcp]`
extra + the `trustmodel-mcp` console script). It is listed in the official MCP
Registry under the GitHub-OAuth namespace `io.github.karlmehta/trustmodel-mcp-py`.
**No DNS / no Cloudflare.**

Ownership is proved by the `<!-- mcp-name: io.github.karlmehta/trustmodel-mcp-py -->`
comment at the top of this README (which becomes the PyPI long-description) — it
must match the `name` in `server.json`.

## 1. Publish to PyPI

Requires PyPI auth (a project API token in `~/.pypirc` or `TWINE_*`).

```bash
python -m pip install --upgrade build twine
python -m build                      # builds sdist + wheel for trustmodel 0.2.0
python -m twine upload dist/*        # publishes to PyPI
```

Verify: `pip install "trustmodel[mcp]"` then `trustmodel-mcp` starts the server;
`pip index versions trustmodel` shows `0.2.0`.

## 2. Publish to the official MCP Registry

```bash
mcp-publisher login github           # interactive GitHub OAuth → verifies io.github.karlmehta
mcp-publisher publish                # reads ./server.json
```

Verify:

```bash
curl -s "https://registry.modelcontextprotocol.io/v0/servers?search=trustmodel" | jq '.servers[].name'
# expect both io.github.karlmehta/trustmodel-mcp (npm) and .../trustmodel-mcp-py (pypi)
```

The npm/TypeScript counterpart publishes from `karlmehta/trustmodel-mcp`.
