# Deploying the hosted demo

Both halves run on Vercel's free Hobby plan. Nothing here costs money.

Live: web https://sieve-kappa.vercel.app, API https://sieve-api.vercel.app (OpenAPI at https://sieve-api.vercel.app/docs).

## API as a Vercel Python function

The FastAPI app is served by Vercel's Python runtime (Fluid compute, 300 second max duration, 2 GB memory), which is enough for the Nemotron 3 Ultra audit step (about 15 to 25 seconds end to end).

Files that make this work, all at the repo root:

- `index.py`: the entrypoint Vercel looks for. The function must ship with the index; `GET /health` reports how many pages it has, so check that number after every API deploy. It puts `apps/api` and `packages/*` on `sys.path` and exposes `app`.
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

- **Web**: `git push origin main` deploys the `sieve` project, which builds `apps/web`.
- **API**: deploy only from the CLI at the repo root: `vercel deploy --prod --yes`. The search index in `data/index/` is gitignored because it is built from copyrighted manuals, so a git build would ship an API with an empty index. The `sieve-api` project therefore has an Ignored Build Step of `exit 0`, which skips every git-triggered build, and the CLI upload carries the local index through `includeFiles` in `vercel.json`.

Do not run `vercel deploy` from `apps/web`, and keep the web project's Root Directory at `apps/web`.

After any deploy, check both hosts: `curl -I https://sieve-api.vercel.app/health` should be 200 and `https://sieve-kappa.vercel.app/` should return the landing page.

Locally `apps/web/.env.local` keeps `NEXT_PUBLIC_API_BASE=http://localhost:8000`.

## Keeping it warm

Vercel functions cold-start in one to two seconds and need no keep-alive. If the API ever moves to a host that sleeps, a Hermes cron job (`hermes cron create "*/10 * * * *" --no-agent --script ping_api.py`) or any uptime monitor pointed at `/health` keeps it awake.

## Alternative: Docker

`apps/api/Dockerfile` also builds the API as a container for any Docker host (verified image build).
