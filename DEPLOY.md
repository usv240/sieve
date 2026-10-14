# Deploying the hosted demo

Two free-tier services, both deploy from this repository with no code changes.

## API on Render (Docker)

1. In Render, New, Blueprint, pick `usv240/sieve`. The `render.yaml` at the root defines the service.
2. Add two environment variables in the dashboard: `NEBIUS_API_KEY`, `TAVILY_API_KEY`.
3. Deploy. The image includes the 9,458-page index, the openFDA snapshots and the published eval results, so the service is self-contained. Health check at `/health`.
4. Copy the public URL, for example `https://sieve-api.onrender.com`.

Free-tier note: Render sleeps idle services and cold-starts in about 30 seconds. The web app's status strip shows "API offline: showing replay samples only" until it wakes, then switches to live.

## Web on Vercel (Next.js)

1. In Vercel, Add New Project, import `usv240/sieve`, set the Root Directory to `apps/web`.
2. Add the environment variable `NEXT_PUBLIC_API_BASE` with the Render URL from above.
3. Deploy. Vercel builds with `npm run build`; the app is static plus client-side fetches, so it costs nothing to host.

## Keeping both awake for judging

Render free services sleep after 15 minutes idle. A Hermes cron job (`hermes cron create "*/10 * * * *" --no-agent --script ping_api.py`) or any uptime pinger keeps the API warm through the judging window (December 1 to 15).

## Local equivalent

```
make dev                      # API on :8000
cd apps/web && npm run dev    # web on :3000
```
