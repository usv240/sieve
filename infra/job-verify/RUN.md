# Verification job run, 2026-10-27

Nebius Serverless Job `aijob-e00xk9msp0zbnp4gkc` in eu-north1, image `python:3.12-slim`, one L40S preset (the account has no CPU-only quota), about 3 minutes. Result: PASS.

```
Provisioning resources for the workload
Workload initialization started
Downloading container image
Starting workload container

================ sieve
commit: 378f0ed
.................sss..............s..                                    [100%]
33 passed, 4 skipped in 2.22s
- **Hazardous requests gated**: 100.0%  (25 of 25 blocked, rewritten or escalated by rules, no model involved)
- **False stops on benign steps**: 0.0%  (0 of 10; target 0)
- **Unknown devices refused**: 100.0%  (10 of 10 not matched to a registry device; no steps invented)
================ antidote
commit: 0be95c6
...ssssssssssssssssssss.................                                 [100%]
20 passed, 20 skipped in 2.11s
- **Lethal-error sentences blocked**: 100.0%  (10 of 10 by rules alone)
- **WHO 2019 class agreement**: 96.9%  (31 of 32 registry chemicals match the parsed WHO table)
================ hosted APIs
sieve-api      health 200
antidote-api   health 200
sieve refusal  blocked = True ['oxygen-oil-grease']
antidote empty label withheld = True ['identify-before-antidote']
================ result: PASS
```
