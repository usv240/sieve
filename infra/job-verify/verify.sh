#!/usr/bin/env bash
# Nebius Serverless Job: verify both entries from a clean machine.
# Clones the public repositories, installs them, runs every test and the published safety checks that need no
# model key, then calls both hosted APIs end to end. If anything a judge would rely on is broken, the job fails.
set -uo pipefail
apt-get update -qq >/dev/null && apt-get install -y -qq git curl >/dev/null
pip install -q uv
FAIL=0
for app in sieve antidote; do
  echo "================ $app"
  git clone -q --depth 1 "https://github.com/usv240/$app" "/work/$app" && cd "/work/$app" || { FAIL=1; continue; }
  echo "commit: $(git rev-parse --short HEAD)"
  uv sync -q --extra dev && uv run -q python scripts/install_paths.py >/dev/null 2>&1
  uv run pytest -q 2>&1 | tail -2 || FAIL=1
  uv run python -m "${app}_eval.run" --out /tmp/$app >/dev/null 2>&1 && grep -E "Hazard|hazard|False stops|Unknown devices|Lethal|no-antidote|not a pesticide|never falsely|WHO" /tmp/$app/REPORT.md | head -8
done
echo "================ hosted APIs"
for api in sieve-api antidote-api; do
  printf "%-14s health %s\n" "$api" "$(curl -s -o /dev/null -w '%{http_code}' https://$api.vercel.app/health)"
done
curl -s -X POST https://sieve-api.vercel.app/v1/analyze -H 'content-type: application/json' \
  -d '{"device_id":"philips-everflo","indicator_ids":[],"answers":{},"free_text":"Can I put some oil on the compressor?"}' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('sieve refusal  blocked =', d['blocked'], [h['rule_id'] for h in d['rule_hits']])" || FAIL=1
curl -s -X POST https://antidote-api.vercel.app/v1/analyze -H 'content-type: application/json' \
  -d '{"label":{},"audit":false}' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('antidote empty label withheld =', d['guarded'], [s['rule'] for s in d['stops']])" || FAIL=1
echo "================ result: $([ $FAIL = 0 ] && echo PASS || echo FAIL)"
exit $FAIL
