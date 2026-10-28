.PHONY: setup test lint smoke ingest eval dev

setup:
	uv sync --extra dev
	uv run python scripts/install_paths.py

fetch-corpus:
	bash scripts/fetch_corpus.sh

test:
	uv run pytest -q

lint:
	uv run ruff check .

# One real Token Factory call per tier; prints model, tokens and cost. Requires NEBIUS_API_KEY in .env.
smoke:
	PYTHONIOENCODING=utf-8 PYTHONUTF8=1 uv run python scripts/smoke.py

ingest:
	uv run python -m sieve_retrieval.ingest --manifest data/manifest.yaml --out data/index

eval:
	PYTHONIOENCODING=utf-8 PYTHONUTF8=1 uv run python -m sieve_eval.run --out eval/results

dev:
	uv run uvicorn sieve_api.main:app --reload --port 8000

# Offline mode: 4-bit Nemotron 3 Nano on the laptop GPU via llama.cpp (see scripts/offline.ps1). Then:
#   OFFLINE_BASE_URL=http://127.0.0.1:8090/v1 make dev
offline:
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/offline.ps1

# Offline-vs-cloud delta on ten fixed cases; needs the offline server running and NEBIUS_API_KEY for the cloud column.
offline-eval:
	PYTHONIOENCODING=utf-8 PYTHONUTF8=1 OFFLINE_BASE_URL=$${OFFLINE_BASE_URL:-http://127.0.0.1:8090/v1} uv run python -c "from pathlib import Path; from sieve_eval.offline_delta import run; import json; print(json.dumps({k:{kk:vv for kk,vv in v.items() if kk!='rows'} for k,v in run(Path('eval/results/offline_delta.json')).items()}, indent=1))"
