# Running Sieve's agent inside NVIDIA OpenShell (and NemoClaw)

OpenShell is NVIDIA's sandbox and policy runtime for autonomous agents: kernel-enforced filesystem and network policy, credential brokering so the agent never sees real keys, and inference routing. NemoClaw is the reference stack that puts an agent (OpenClaw, Hermes, Deep Agents or Pi) inside an OpenShell sandbox with hardened defaults.

Why it fits Sieve: a hospital IT department will not run an autonomous agent that can reach anything on the network. Sieve's agent needs exactly four egress destinations and nothing else. The policy below says so, and OpenShell enforces it at the kernel.

## Policy (`policy.yaml`)

- Filesystem: read-only on the repo, read-write only on `data/records.jsonl`, `data/ledger.db` and `data/index/`.
- Network: allow `api.tokenfactory.nebius.com`, `api.tokenfactory.us-central1.nebius.com`, `api.tavily.com`, `api.fda.gov`. Everything else denied.
- Credentials: `NEBIUS_API_KEY` and `TAVILY_API_KEY` are brokered; the sandboxed process receives placeholders and OpenShell injects the real values only on requests to the allowed hosts.

## Commands (Linux, macOS or WSL2)

```
curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh
openshell provider create --name nebius --type openai \
  --credential OPENAI_API_KEY=$NEBIUS_API_KEY \
  --config OPENAI_BASE_URL=https://api.tokenfactory.us-central1.nebius.com/v1
openshell inference set --provider nebius --model nvidia/nemotron-3-super-120b-a12b
openshell sandbox create --name sieve --policy infra/openshell/policy.yaml
openshell sandbox exec sieve -- uv run python apps/mcp/sieve_mcp.py
```

With NemoClaw and Hermes as the agent:

```
NEMOCLAW_PROVIDER=custom \
NEMOCLAW_ENDPOINT_URL=https://api.tokenfactory.us-central1.nebius.com/v1 \
NEMOCLAW_MODEL=nvidia/nemotron-3-super-120b-a12b \
NEMOCLAW_REASONING=true \
COMPATIBLE_API_KEY=$NEBIUS_API_KEY \
curl -fsSL https://www.nvidia.com/nemoclaw.sh | NEMOCLAW_AGENT=hermes NEMOCLAW_SANDBOX_NAME=sieve bash
```

## Status on 2026-10-14

OpenShell needs Linux, macOS or WSL2 with Docker. This machine has WSL2 distributions but Docker Desktop was not running, so the sandboxed run has not been executed here yet. The policy file is complete and the agent it wraps (the Hermes plus Sieve MCP setup in `infra/hermes`) is verified outside the sandbox. We list this honestly as prepared, not demonstrated, until a run is recorded.
