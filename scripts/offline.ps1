# Offline mode: serve a 4-bit NVIDIA Nemotron 3 Nano with llama.cpp on the laptop GPU, OpenAI-compatible on :8080.
# Usage (PowerShell):  .\scripts\offline.ps1
# Then set OFFLINE_BASE_URL=http://127.0.0.1:8080/v1 in .env (or export it) and start the API; the router sends
# the fast and mid tiers to the local model and disables the Ultra audit. No internet needed after the download.
$root  = Split-Path -Parent $PSScriptRoot
$bin   = Join-Path (Split-Path -Parent $root) "tools\llama.cpp\llama-server.exe"
$model = Join-Path (Split-Path -Parent $root) "models\Nemotron-3-Nano-30B-A3B-Q4_K_M.gguf"
if (-not (Test-Path $bin))   { Write-Error "llama-server not found at $bin (download a llama.cpp CUDA build into tools\llama.cpp)"; exit 1 }
if (-not (Test-Path $model)) { Write-Error "model not found at $model (download Nemotron-3-Nano-30B-A3B-Q4_K_M.gguf from unsloth/Nemotron-3-Nano-30B-A3B-GGUF)"; exit 1 }
# 30B total, 3.5B active: offload as many layers as the 8 GB GPU holds, the rest stays on CPU RAM.
& $bin --model $model --alias nemotron-3-nano --host 127.0.0.1 --port 8080 --ctx-size 32768 --n-gpu-layers 20 --threads 8 --jinja --reasoning-format none
