#!/usr/bin/env bash
# Run the Sieve MCP agent inside an NVIDIA OpenShell sandbox with a deny-by-default network policy.
# Requires: Linux, macOS, or WSL2 with Docker reachable; NEBIUS_API_KEY and TAVILY_API_KEY in the environment.
# Verified commands follow the OpenShell docs as of 2026-10-14; the policy reloads live, no restart needed.
set -euo pipefail
NAME=${SANDBOX_NAME:-sieve}
REPO=${REPO_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}

if ! command -v openshell >/dev/null; then
  echo "Install OpenShell first: curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh"; exit 1
fi

# 1. Sandbox from a minimal Python image with the repo mounted at /workspace, no auto providers.
openshell sandbox create --name "$NAME" --from python:3.12-slim --no-auto-providers \
  --env OPENAI_BASE_URL=https://api.tokenfactory.us-central1.nebius.com/v1 \
  --env PYTHONIOENCODING=utf-8 \
  --mount "$REPO:/workspace" -- sleep infinity

# 2. Deny-by-default network: allow only the four hosts Sieve needs.
PY=/workspace/.venv/bin/python
openshell policy update "$NAME" --rule-name nebius_eu --binary "$PY" --add-endpoint api.tokenfactory.nebius.com:443:read-write:rest:enforce --wait
openshell policy update "$NAME" --rule-name nebius_us --binary "$PY" --add-endpoint api.tokenfactory.us-central1.nebius.com:443:read-write:rest:enforce --wait
openshell policy update "$NAME" --rule-name tavily    --binary "$PY" --add-endpoint api.tavily.com:443:read-write:rest:enforce --wait
openshell policy update "$NAME" --rule-name openfda   --binary "$PY" --add-endpoint api.fda.gov:443:read-only:rest:enforce --wait

# 3. Prove the policy: an allowed host answers, a disallowed host is refused by the proxy.
openshell sandbox exec --name "$NAME" -- /workspace/.venv/bin/python -c "import httpx; print('fda:', httpx.get('https://api.fda.gov/device/recall.json?limit=1', timeout=20).status_code)"
openshell sandbox exec --name "$NAME" -- /workspace/.venv/bin/python -c "import httpx
try:
    httpx.get('https://example.com', timeout=10); print('example.com: ALLOWED (unexpected)')
except Exception as e:
    print('example.com: blocked by policy ->', type(e).__name__)"
openshell logs "$NAME" --since 2m --source sandbox | tail -5

# 4. Run a real Sieve diagnosis inside the sandbox through the MCP server's pipeline.
openshell sandbox exec --name "$NAME" -- /workspace/.venv/bin/python -c "
import sys; sys.path[:0]=['/workspace/packages/core','/workspace/packages/llm','/workspace/packages/retrieval','/workspace/packages/rules','/workspace/packages/vision']
from sieve_llm import Ledger, TokenFactoryClient
from sieve_retrieval import PageStore
from sieve_core.pipeline import SievePipeline
p = SievePipeline(TokenFactoryClient(ledger=Ledger('/workspace/data/ledger.db')), PageStore('/workspace/data/index/sieve.db'))
r = p.analyze(device_id='devilbiss-525', indicator_ids=['dv525-yellow'], answers={'in_use':'no','warmup':'yes'}, audit=False)
print('steps', len(r.tree.steps), 'citations', r.citation_report['verified'], '/', r.citation_report['total'])"
