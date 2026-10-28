# Evidence

Every number on the site and in the submission, where its raw output lives, and how to run it again. Nothing here is summarised from memory: each row points at a file in this repository.

## Results

| Claim | Number | Raw output | Rerun |
|---|---|---|---|
| Benchmark A: closest prior work's own 300 questions (INGENZI), blind judge | Sieve 69.7, chunk-RAG 62.0, zero-shot 17.0 | `eval/results/bench_a_300.json` | `python -m sieve_eval.bench_a` |
| Same answers, second judge from another company | 66.0, 52.4, 2.5; kappa 0.94 to 1.0 | `eval/results/bench_a_300.json` | `python -m sieve_eval.cross_judge` |
| Benchmark B: 74 real FDA malfunction reports, pre-registered | fire and heat reports taken out of service: 62 of 62 | `eval/results/bench_b_v2.json` | `eval/PREREG-benchmark-b.md`, `python -m sieve_eval.bench_b` |
| Real-world photos, two vision reads | 82.9 percent identified, 100 percent when legible, 16 of 16 look-alikes refused, 0 wrong auto-selections | `eval/results/photo_bench.json` | `python -m sieve_eval.photo_bench` |
| Same photos, NVIDIA Nemotron Nano 12B VL alone on a Nebius Serverless Endpoint | 73.2 percent | `eval/results/photo_bench_nano_vl.json`, `infra/endpoint-vl/RUN.md` | `python -m sieve_eval.photo_bench --single` |
| Citations by sentence id vs copied quotes | 100 vs 88.8 percent resolve | `eval/results/cite_ab.json` | `python -m sieve_eval.cite_ab` |
| Negative controls: hazards gated, false stops, unknown devices refused, retrieval | 20 of 20, 0 of 10, 10 of 10, 10 of 10 | `eval/results/latest.json` | `make eval` |
| Offline on a laptop GPU, no cloud keys | full cited diagnosis in 61 s with every safety rule intact | `eval/results/offline_delta.json` | `scripts/offline.ps1`, `make offline-eval` |
| Clean-machine verification on Nebius AI Cloud | PASS | `infra/job-verify/RUN.md` | `infra/job-verify/README.md` |
| Cost of every run | from the call ledger | `eval/results/latest.json` (`cost_usd`) | printed by every eval |

## Safety stops, as code

The stops are rules in `packages/rules/sieve_rules/sieve.yaml`, checked before any model sees the request and again on every model output. Tests that prove each one fires: `tests/test_rules.py`, `tests/test_published_controls.py`. Run `make test` (37 tests).

## Build timeline

Every commit is dated after 2026-10-13, inside the submission period (which opened 2026-08-26). `git log --reverse` shows each step, including the runs that found problems.
