# Sieve inside Hermes Agent

Hermes Agent (Nous Research, MIT) gives technicians a chat surface for Sieve on WhatsApp, Telegram, Slack or the terminal, with Nemotron 3 Super on Nebius Token Factory as the model and Sieve exposed as MCP tools.

## Setup (verified on Windows, Hermes 0.19, 2026-10-14)

```
uv tool install hermes-agent --with "mcp>=1.2"
hermes config path          # shows where config.yaml lives (Windows: %LOCALAPPDATA%\hermes)
```

Copy `config.example.yaml` to that path, replace `<path-to-sieve>` with your clone path, and put the keys in the `.env` file next to it:

```
NEBIUS_API_KEY=...
TAVILY_API_KEY=...
```

Then:

```
hermes mcp test sieve       # expect: Connected, Tools discovered: 6
hermes chat                 # or: hermes -z "DeVilbiss 525, red light beeping. Use the sieve tools."
```

Hermes 0.19 on PyPI predates the built-in `nebius-token-factory` provider, so Token Factory is configured as a custom OpenAI-compatible endpoint. Newer Hermes builds can use `provider: nebius-token-factory` directly.

## Messaging

`hermes whatsapp` or `hermes gateway` wires the same agent to WhatsApp or Telegram, which is how field technicians in India actually communicate. Sieve's tools, rules and citations are unchanged; only the surface changes.
