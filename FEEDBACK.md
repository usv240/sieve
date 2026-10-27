# Feedback on Nebius Token Factory, Nebius AI Cloud, and NVIDIA tools

A running log kept from day one. The hackathon requires this section; we keep it honest and specific.

## Onboarding
- 2026-10-13: Credits: promo code route and Builders Program route both documented on Devpost resources. The $25 promo arrived by email and applied cleanly through Top up, With promo code.
- Time from a fresh API key to the first successful Nemotron call across all three tiers: under five minutes, using the OpenAI SDK with the two documented base URLs.

## What worked
- One OpenAI-compatible client covers four Nemotron models; swapping tiers is one string. Tool calling worked first time on Nano, Super and Ultra.
- Ultra with a 60 to 200 page manual in context as an auditor was the single most useful capability we touched: the whole-document check is what made the citation integrity number possible. 44,000 input tokens for about five cents.
- Nemotron 3.5 Lightning read 140,000 tokens of fleet log plus FDA reports in one call for under a cent.
- Qwen3-Embedding-8B embedded 2,994 pages in six minutes with no rate-limit trouble.
- The image models in the catalog (MiniCPM-V-4_5 in 2.6 s) made photo identification possible without GPU hosting.
- Rate limits (60 RPM) were never hit during a 300-question benchmark with three systems and two judges.

## What needs work
- Model catalog metadata shows 0 parameters for Super and Ultra in the markdown catalog; NVIDIA figures used instead.
- Nemotron models do not carry the JSON-mode tag; we used tool calling for structured output. A documented guarantee for `response_format=json_schema` on Nemotron would remove a workaround.
- No official Nebius doc page covers `chat_template_kwargs.enable_thinking` for Nemotron; we found it in NVIDIA docs and community repos.
- Vision Nemotron (Nano Omni, Nano VL) is not on shared serverless endpoints since the Aug 31 2026 deprecation; teams must self-host on a Serverless Endpoint or use a non-NVIDIA image2text model.

## Would we build with it again
Yes. Token Factory was the fastest path from idea to a measured result we have used: open weights, one API, a model for every tier, and prices low enough to run a 300-question benchmark three times for about a dollar each. Two things would make the next team faster: a documented Nemotron reasoning toggle, and one NVIDIA vision model on the shared endpoints.

## NVIDIA models
- Nemotron 3 Nano: reliable structured extraction with thinking off; occasionally ignores an enumerated allowed-values list (fault ids) until the list is repeated in the user message.
- Nemotron 3 Super: good step-by-step synthesis under a strict schema; quotes are usually verbatim but PDF artefacts (dashes, table cells) cost 10 to 15 percent of exact matches, hence our tiered verifier.
- Nemotron 3 Ultra: excellent as an auditor; strict, specific reasons, and it catches wrong-page citations. Its cost dominates a session (about 90 percent), so we audit once, not per step.
- Nemotron Nano 12B v2 VL via llama.cpp on an RTX 4070 laptop: correct nameplate reading at 59 seconds per image; fine for a technician, too slow for a live demo, so Token Factory image models carry the demo.
- Nemotron Nano 9B v2 Q4 as the offline model: 32 tokens per second fully on an 8 GB GPU; the 30B-A3B at Q4 spilled to CPU and was impractical there.

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

## Nemotron 3.5 Super VL on Token Factory (2026-10-27)
- It appeared in the Token Factory catalog during the hackathon. It is the first NVIDIA vision model we could call there, and it replaced a third-party image model as our first reader.
- With reasoning on, a 600 or 1,500 token budget returned empty content: the budget went to thinking. `chat_template_kwargs: {"enable_thinking": false}` fixed it. A note on the model card would save others an hour.
- On 68 real Indian pesticide labels it read the chemical better than MiniCPM-V; on a Gramoxone bottle it read paraquat where MiniCPM-V invented two organophosphates.
- It can still invent plausible small print. On a real DeVilbiss 1025DS rating label it returned "REF 525DS" with a made-up serial number and current rating. A per-field confidence, or a flag when text is reconstructed rather than read, would let applications decide when to ask a person.
- It returns `null` for fields it cannot see, which is right, but a client expecting strings fails validation; worth one line in the docs.
- Under bursts, image calls returned 429 or 5xx without a Retry-After header. We added backoff; a documented per-model rate limit would help.

## Local inference on an 8 GB laptop GPU (2026-10-27)
- Nemotron Nano 9B v2 at Q4_K_M through llama.cpp b11617 ran well on 2026-10-14. On 2026-10-27 the server stopped three times with "ggml-cuda.cu:109: CUDA error" a few minutes into generation, with GPU memory at about 7.6 of 8 GB. A smaller context and flash attention did not prevent it. A recommended configuration for 8 GB cards would help the offline story Nemotron Nano is well suited to.
