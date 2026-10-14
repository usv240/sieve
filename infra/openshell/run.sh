#!/usr/bin/env bash
# Run the Sieve agent inside an NVIDIA OpenShell sandbox with a deny-by-default network policy and brokered
# credentials. Verified on WSL2 + Docker Desktop on 2026-10-14 (see DEMONSTRATED.md).
# Requires: openshell + openshell-gateway 0.1.4 on PATH, Docker reachable, NEBIUS_API_KEY and TAVILY_API_KEY exported.
set -euo pipefail
NAME=${SANDBOX_NAME:-sieve}
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
TLS_DIR=${OPENSHELL_LOCAL_TLS_DIR:-$HOME/.local/state/openshell/tls}
CFG=${OPENSHELL_GATEWAY_CONFIG:-$HOME/.config/openshell/gateway.toml}
PY=/usr/local/bin/python3.12   # resolved interpreter inside the image; policy binaries must not be symlinks

# 0. Gateway (skip if one is already registered and connected)
if ! openshell status >/dev/null 2>&1; then
  mkdir -p "$TLS_DIR" "$(dirname "$CFG")"
  [ -f "$TLS_DIR/ca.crt" ] || openshell-gateway generate-certs --output-dir "$TLS_DIR" --server-san host.openshell.internal --server-san host.docker.internal --server-san 127.0.0.1
  [ -f "$CFG" ] || cp "$HERE/gateway.toml" "$CFG"
  (OPENSHELL_LOCAL_TLS_DIR="$TLS_DIR" OPENSHELL_GATEWAY_CONFIG="$CFG" nohup openshell-gateway >"$HOME/.openshell-gateway.log" 2>&1 &)
  sleep 5
  openshell gateway add https://127.0.0.1:17670 --local --name openshell >/dev/null
fi
openshell status | grep -E "Status|Authentication"

# 1. Agent image: repo + deps + index, workspace writable for the sandbox uid
docker build -q -t sieve-agent:latest -f "$HERE/Dockerfile.agent" "$REPO"

# 2. Provider profiles and providers (credentials looked up from the environment, never written to disk)
for p in nebius-token-factory tavily; do openshell profile lint -f "$HERE/profiles/$p.yaml" >/dev/null && openshell profile import -f "$HERE/profiles/$p.yaml" 2>/dev/null || true; done
openshell provider create --name nebius --type nebius-token-factory --credential NEBIUS_API_KEY 2>/dev/null || true
openshell provider create --name tavily --type tavily --credential TAVILY_API_KEY 2>/dev/null || true

# 3. Sandbox with a long-lived main process, deny-all network by default
openshell sandbox delete "$NAME" >/dev/null 2>&1 || true; sleep 2
(openshell sandbox create --name "$NAME" --from sieve-agent:latest --no-auto-providers -- sleep infinity >/dev/null 2>&1 &)
for _ in $(seq 1 30); do openshell sandbox list 2>/dev/null | grep -q "^$NAME .*Ready" && break; sleep 2; done

# 4. Prove deny-by-default, then allow exactly four hosts
openshell sandbox exec --name "$NAME" -- $PY -c "import httpx
try: httpx.get('https://example.com', timeout=8); print('example.com: ALLOWED (unexpected)')
except Exception as e: print('example.com before policy: blocked ->', type(e).__name__)"
openshell policy update "$NAME" --rule-name openfda --binary $PY --add-endpoint api.fda.gov:443:read-only:rest:enforce --wait
openshell sandbox provider attach "$NAME" nebius --wait --timeout 60
openshell sandbox provider attach "$NAME" tavily --wait --timeout 60
openshell sandbox exec --name "$NAME" -- sh -c 'env | grep -E "^(NEBIUS|TAVILY)_API_KEY=" | sed -E "s/=(.{6}).*/=\1... (placeholder)/"'

# 5. Full diagnosis inside the sandbox: Nemotron 3 Super, Nemotron 3 Ultra audit, Tavily parts lookup
openshell sandbox exec --name "$NAME" -- $PY -c "
import sys
sys.path[:0] = ['/workspace/packages/core','/workspace/packages/llm','/workspace/packages/retrieval','/workspace/packages/rules','/workspace/packages/vision']
from sieve_llm import Ledger, TokenFactoryClient
from sieve_retrieval import PageStore
from sieve_core.pipeline import SievePipeline
p = SievePipeline(TokenFactoryClient(ledger=Ledger('/tmp/ledger.db')), PageStore('/workspace/data/index/sieve.db'))
r = p.analyze(device_id='philips-everflo', indicator_ids=['everflo-yellow-solid-silent'], answers={'in_use':'no','warmup':'yes','analyser':'yes'}, audit=True)
print('INSIDE OPENSHELL SANDBOX:', r.device_label, '| steps', len(r.tree.steps), '| citations', r.citation_report['verified'], '/', r.citation_report['total'], '| audit', r.audit.overall if r.audit else None)
for row in p.client.ledger.trace(r.trace_id): print('  trace', row['model'], row['purpose'], f\"\${row['usd']:.4f}\")"
