# Serverless Endpoint run, 2026-10-27

Endpoint `aiendpoint-e00sqzn5h17f0f32v3` in eu-north1: image `vllm/vllm-openai:latest`, one NVIDIA L40S
(`gpu-l40s-a`, `1gpu-8vcpu-32gb`), model `nvidia/NVIDIA-Nemotron-Nano-12B-v2-VL-FP8`, token auth. About 37 minutes from
create to stop, roughly $1 at $1.55 per GPU-hour. Stopped after use; a stopped endpoint is not billed.

Both photo benchmarks were rerun with this endpoint as the only reader (no second read, no cross-check):

| Benchmark | Result with Nemotron Nano 12B VL alone |
|---|---|
| Sieve, 57 real concentrator photos | 73.2% of covered devices identified, 88.5% when the model name is legible, 16/16 look-alikes refused, 0 wrong devices |
| Antidote, 68 real pesticide labels | 57 correct (92.9% when the chemical is legible), the rest held for confirmation |

The production path adds two safeguards on top of any single reader: two independent reads must agree, and the brand is
checked on the web. With both, the same 68 labels gave 0 unsafe cards.

Restart for a demo: `nebius ai endpoint start aiendpoint-e00sqzn5h17f0f32v3`, then set `VISION_ENDPOINT_URL` to its
`/v1` URL and `VISION_ENDPOINT_TOKEN`; Sieve then reads photos with it first.
