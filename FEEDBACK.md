# Feedback on Nebius Token Factory, Nebius AI Cloud, and NVIDIA tools

A running log kept from day one. The hackathon requires this section; we keep it honest and specific.

## Onboarding
- 2026-10-13: Credits: promo code route and Builders Program route both documented on Devpost resources; balance confirmation pending.
- Time from zero to first successful Token Factory call: (fill in after `make smoke`).

## What worked

## What needs work
- Model catalog metadata shows 0 parameters for Super and Ultra in the markdown catalog; NVIDIA figures used instead.
- Nemotron models do not carry the JSON-mode tag; we used tool calling for structured output. A documented guarantee for `response_format=json_schema` on Nemotron would remove a workaround.
- No official Nebius doc page covers `chat_template_kwargs.enable_thinking` for Nemotron; we found it in NVIDIA docs and community repos.
- Vision Nemotron (Nano Omni, Nano VL) is not on shared serverless endpoints since the Aug 31 2026 deprecation; teams must self-host on a Serverless Endpoint or use a non-NVIDIA image2text model.

## Would we build with it again

## Tavily

## NVIDIA models

## Tavily (2026-10-14)
- Signup to first successful search with `tavily-python`: under five minutes, no card. `include_domains` worked well for restricting parts searches to suppliers and manual searches to known mirrors.
- The agent-setup SKILL.md on tavily.com pushes CLI install, browser login and global skill installation; for an application that only needs the SDK and an env var, the Path B section was the only part needed. A shorter "I just want the SDK" entry point would save time.
- What worked: a brand-name query for a pesticide returned regulator and supplier pages with the active ingredient in the title on the first try.

## Hermes Agent (2026-10-14)
- Installed on native Windows via `uv tool install hermes-agent --with "mcp>=1.2"`; the PyPI release (0.19.0) does not include the mcp SDK, so MCP servers fail with a clear message until the extra is added.
- 0.19.0 predates the built-in `nebius-token-factory` provider documented on the site; `provider: custom` with the US base URL and `key_env: NEBIUS_API_KEY` works for Nemotron 3 Super.
- Config lives in `%LOCALAPPDATA%\hermes` on Windows, not `~/.hermes`; `hermes config path` tells you.
- `hermes mcp test sieve` discovered all six Sieve tools; a one-shot `hermes -z` diagnosis on Nemotron 3 Super called identify_device and analyze_fault correctly.
- Cron `--script` runs under Hermes's own interpreter and home directory; a two-line wrapper that calls the repo's venv was needed. Worth documenting.

## NVIDIA OpenShell and NemoClaw (2026-10-14)
- Needs Linux, macOS or WSL2 with Docker. Docker Desktop was running but WSL integration for the Ubuntu distro was off, so the sandbox could not reach a Docker socket from WSL. Policy file and run script were written against the current docs (network_policies with endpoints and binaries; `openshell policy update --add-endpoint host:port:access:protocol:enforcement`; `openshell sandbox exec`).
- The docs moved from `openshell inference set` to provider profiles between the hackathon brief and today; the brief still names the old flow.
- Later the same day, with Docker WSL integration on, the full run worked. What cost time: the gateway ships with an empty profile catalog (a profile for any OpenAI-compatible endpoint would help every hackathon team); the Docker driver needs `grpc_endpoint` plus a cert SAN on Docker Desktop, which is undocumented for WSL2; policy `binaries` silently never match a symlink path. What impressed: kernel-level EACCES denials, live policy reload with no restart, and credential placeholders that let the pipeline run unchanged with real keys never entering the sandbox.
