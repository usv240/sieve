# Serverless Endpoint run, 2026-10-27

Endpoint `aiendpoint-e00sqzn5h17f0f32v3` in eu-north1: image `vllm/vllm-openai:latest`, one NVIDIA L40S
(`gpu-l40s-a`, `1gpu-8vcpu-32gb`), model `nvidia/NVIDIA-Nemotron-Nano-12B-v2-VL-FP8`, token auth. About 37 minutes from
create to stop, roughly $1 at $1.55 per GPU-hour. Stopped after use; a stopped endpoint is not billed.

Both photo benchmarks were rerun with this endpoint as the only reader (no second read, no cross-check):

| Benchmark | Result with Nemotron Nano 12B VL alone |
|---|---|
| Sieve, 57 real concentrator photos | 73.2% of covered devices identified, 88.5% when the model name is legible, 16/16 look-alikes refused, 0 wrong devices |
| Antidote, 68 real pesticide labels | 57 correct (92.9% when the chemical is legible), 10 withheld, 1 unsafe |

The unsafe card: a chlorpyriphos (organophosphate) label read as deltamethrin (a pyrethroid). This is exactly the failure
the production path guards against: it requires two independent reads to agree and checks the brand on the web, and
with those checks the same 68 labels gave 0 unsafe cards. A single vision model, however good, is not enough on its own.

Restart for a demo: `nebius ai endpoint start aiendpoint-e00sqzn5h17f0f32v3`, then set `VISION_ENDPOINT_URL` to its
`/v1` URL and `VISION_ENDPOINT_TOKEN`; Sieve then reads photos with it first.
