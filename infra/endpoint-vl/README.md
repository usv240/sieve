# Vision endpoint: NVIDIA Nemotron Nano VL on a Nebius Serverless Endpoint

Serves `nvidia/NVIDIA-Nemotron-Nano-12B-v2-VL` with vLLM behind an OpenAI-compatible API. Started before demo and judging windows, stopped otherwise. The API falls back to a Token Factory image2text model, then manual entry, when this endpoint is down.

## Create

```
export HF_TOKEN=...            # Hugging Face token with access to the model
export VISION_TOKEN=$(openssl rand -hex 24)

nebius ai endpoint create \
  --name sieve-vision \
  --image vllm/vllm-openai:latest \
  --platform gpu-l40s-a --preset 1gpu-8vcpu-32gb \
  --container-port 8000/http --auth token --token "$VISION_TOKEN" \
  --disk-size 120Gi --shm-size 16Gi --public=false \
  --env HF_TOKEN="$HF_TOKEN" \
  --container-command python3 \
  --args "-m vllm.entrypoints.openai.api_server --model nvidia/NVIDIA-Nemotron-Nano-12B-v2-VL --trust-remote-code --max-model-len 16384 --gpu-memory-utilization 0.92 --port 8000"
```

Then read the URL from `.status.public_endpoints[]` and set in `.env`:

```
VISION_ENDPOINT_URL=https://<endpoint-host>/v1
VISION_ENDPOINT_TOKEN=<VISION_TOKEN>
VISION_MODEL=nvidia/NVIDIA-Nemotron-Nano-12B-v2-VL
```

## Stop and start

```
nebius ai endpoint stop  --id <id>
nebius ai endpoint start --id <id>
```

## Cost

L40S at about $1.35 per GPU-hour plus CPU and RAM. Budget: roughly 25 hours across development, video and judging.

## Fallback if Nebius AI Cloud is unavailable

Run the same vLLM command locally on a 24 GB class GPU with `--quantization fp8`, or on an RTX 4070 laptop GPU use the FP8 or NVFP4 checkpoint with reduced `--max-model-len`. The API reads the same two environment variables.
