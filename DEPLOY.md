# Deploying the hosted demo

Both halves run on Vercel's free Hobby plan. Nothing here costs money.

Live: web https://sieve-kappa.vercel.app, API https://sieve-api.vercel.app (OpenAPI at https://sieve-api.vercel.app/docs).

## API as a Vercel Python function

The FastAPI app is served by Vercel's Python runtime (Fluid compute, 300 second max duration, 2 GB memory), which is enough for the Nemotron 3 Ultra audit step (about 15 to 25 seconds end to end).

Files that make this work, all at the repo root:

- `index.py`: the entrypoint Vercel looks for. It puts `apps/api` and `packages/*` on `sys.path` and exposes `app`.
- `vercel.json`: declares the single FastAPI service and its entrypoint, and routes every path to it.
- `requirements.txt`: the runtime-only dependency list (the full `pyproject.toml` and `uv.lock` are excluded by `.vercelignore` so the bundle stays small).
- `.vercelignore`: keeps the web app, corpus PDFs, docs, tests and local databases out of the upload.
- `packages/core/sieve_core/paths.py`: on Vercel the bundle is read-only, so the index and seed records are copied to `/tmp` on first request. The ledger, API keys, register rows and uploads live there for the life of the instance. Set `SIEVE_DATA_DIR` to point at persistent storage if you need durability.

Deploy from the repo root:

```
vercel link --yes --project sieve-api
grep '^NEBIUS_API_KEY=' ../.env | cut -d= -f2- | vercel env add NEBIUS_API_KEY production
grep '^TAVILY_API_KEY=' ../.env | cut -d= -f2- | vercel env add TAVILY_API_KEY production
echo 30 | vercel env add SIEVE_RATE_LIMIT_PER_MIN production
vercel deploy --prod --yes
```

Set `SIEVE_REQUIRE_KEY=1` as well if you want every `/v1/*` call to carry an `X-API-Key` minted by `POST /v1/keys`.

## Web on Vercel (Next.js)

The web app is its own Vercel project (`sieve`, Root Directory `apps/web`, env `NEXT_PUBLIC_API_BASE=https://sieve-api.vercel.app`).

## How deploys happen

All four projects are connected to GitHub, so `git push origin main` deploys everything: the `sieve` project builds `apps/web`, the `sieve-api` project builds the FastAPI service from the repo root. No CLI step is needed.

If you deploy by CLI, run it only from the repo root with the API project linked there (`.vercel/project.json` names `sieve-api`). Do not run `vercel deploy` from `apps/web` and do not change the web project's Root Directory back to `.`: with Root Directory `.` a git push built the API onto the web domain (this happened on 2026-10-14 and was fixed by setting Root Directory to `apps/web`).

After any deploy, check both hosts: `curl -I https://sieve-api.vercel.app/health` should be 200 and `https://sieve-kappa.vercel.app/` should return the landing page.

Locally `apps/web/.env.local` keeps `NEXT_PUBLIC_API_BASE=http://localhost:8000`.

## Keeping it warm during judging

Vercel functions cold-start in one to two seconds and need no keep-alive. If the API ever moves to a host that sleeps, a Hermes cron job (`hermes cron create "*/10 * * * *" --no-agent --script ping_api.py`) or any uptime monitor pointed at `/health` keeps it awake.

## Alternative: Docker on Render

`render.yaml` and `apps/api/Dockerfile` still describe the API as a Docker web service for Render's free tier (verified image build). Free Render services sleep after 15 minutes idle and cold-start in about 30 seconds.
