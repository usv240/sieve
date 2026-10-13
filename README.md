# Sieve

Offline-capable repair copilot for biomedical equipment technicians in low-resource hospitals. Oxygen-concentrator-first.

Built for the Nebius x NVIDIA Global AI Hackathon on Nebius Token Factory with NVIDIA Nemotron 3 Nano, Super and Ultra. Apache-2.0.

Status: scaffold. See `docs/IDEA.md`, `docs/PLAN.md`, `docs/TECHNICAL-DESIGN.md`, `docs/UX-DESIGN.md`.

## Quick start

```
cp .env.example .env   # add NEBIUS_API_KEY and TAVILY_API_KEY
make setup
make test
make smoke             # one real call per Nemotron tier, prints the cost ledger
```
