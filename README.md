# Setu — Sarvam MCP Server

> Open-source **Model Context Protocol** server that exposes Sarvam AI's API surface as
> typed tools, so any MCP-capable agent (Claude Desktop, Cursor, Claude Code, or a custom
> LangGraph agent) can use Sarvam speech / translation / chat / document tools in minutes.

**Live demo & write-up:** https://aquamarine-buttercream-058e45.netlify.app/setu

---

## Status — Milestone 1 (skeleton)

This repo currently ships the **milestone 1 skeleton**: a working FastMCP server over
**stdio** with one health-check tool (`setu_ping`), full config + logging scaffolding, and
tests. The Sarvam tool surface and reliability/telemetry middleware land in later milestones.

| Milestone | Scope | State |
|---|---|---|
| **1** | Scaffold, config, structlog, FastMCP `setu_ping` over stdio | ✅ this repo |
| 2 | `sarvam_speak` + `sarvam_transcribe` end-to-end (live) | ⬜ |
| 3 | Retry, rate-limit, cost/latency OTel telemetry middleware | ⬜ |
| 4 | `translate`, `chat`, `transliterate`, `identify_language`, `parse_document` | ⬜ |
| 5 | Mock mode + fixtures, unit tests, CI | ⬜ |
| 6 | streamable-HTTP transport, Dockerfile, docs | ⬜ |
| 7 | 60-sec demo, tag → PyPI | ⬜ |

## Quickstart

```bash
# 1. Create a virtualenv and install (editable, with dev extras)
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'

# 2. Copy the env template (defaults to mock mode — no key needed)
cp .env.example .env

# 3. Run the server over stdio
setu            # or: python -m setu.server

# 4. Run the tests
pytest
```

`setu` speaks the MCP protocol on **stdout**, so it looks like it "hangs" — that's correct;
it's waiting for an MCP client. Logs go to **stderr** as JSON. Press Ctrl-C to stop.

## Configuration

All config is environment-driven (`pydantic-settings`); secrets never get hardcoded.

| Variable | Default | Meaning |
|---|---|---|
| `SETU_MODE` | `mock` | `mock` serves fixtures (no credits); `live` calls Sarvam (milestone 2+). |
| `SETU_SERVER_NAME` | `setu` | Name advertised to MCP clients. |
| `SETU_LOG_LEVEL` | `INFO` | structlog level. |
| `SETU_RATE_LIMIT_PER_MINUTE` | `60` | Reserved for the token-bucket limiter (milestone 3). |
| `SARVAM_API_KEY` | — | Sarvam key; only needed in `live` mode. Get one at dashboard.sarvam.ai. |

## Connect to Claude Desktop

1. Find the absolute path to the `setu` entrypoint inside your venv:

   ```bash
   source .venv/bin/activate
   which setu      # e.g. /Users/you/setu-mcp/.venv/bin/setu
   ```

2. Open Claude Desktop → **Settings → Developer → Edit Config**. This opens
   `claude_desktop_config.json`. Add Setu under `mcpServers`:

   ```json
   {
     "mcpServers": {
       "setu": {
         "command": "/ABSOLUTE/PATH/TO/setu-mcp/.venv/bin/setu",
         "env": { "SETU_MODE": "mock" }
       }
     }
   }
   ```

   (On Windows the path ends in `\.venv\Scripts\setu.exe`.)

3. **Fully quit and reopen** Claude Desktop. Click the tools/🔌 icon in the chat box —
   you should see **setu** listed with the `setu_ping` tool.

4. Ask Claude: *"Use the setu_ping tool with message 'it works'."* You should get back a
   typed result showing `ok: true`, the server name, version, and `mode: mock`.

If the server doesn't appear, check Claude Desktop's MCP logs
(`~/Library/Logs/Claude/mcp*.log` on macOS) — Setu's JSON logs on stderr are captured there.

## Layout

```
setu-mcp/
├─ pyproject.toml          # package + tooling (ruff, mypy, pytest)
├─ .env.example            # config template (mock by default)
├─ src/setu/
│  ├─ config.py            # SetuSettings + SarvamSettings (pydantic-settings)
│  ├─ logging.py           # structlog → stderr, JSON, request ids
│  └─ server.py            # FastMCP app + setu_ping + stdio entrypoint
└─ tests/
   └─ test_ping.py         # imports, registration, and mock-default smoke tests
```

## License

MIT © 2026 Manasa SB
