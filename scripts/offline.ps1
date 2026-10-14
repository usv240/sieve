# Offline mode: serve an open NVIDIA Nemotron model with llama.cpp on the laptop GPU, OpenAI-compatible on :8080.
# Usage (PowerShell):  .\scripts\offline.ps1
# Then set OFFLINE_BASE_URL=http://127.0.0.1:8080/v1 (and OFFLINE_MODEL=nemotron-nano) and start the API; the router
# sends the fast and mid tiers to the local model and disables the Ultra audit. No internet needed after the download.
$root  = Split-Path -Parent $PSScriptRoot
$bin   = Join-Path (Split-Path -Parent $root) "tools\llama.cpp\llama-server.exe"
# Default: NVIDIA Nemotron Nano 9B v2 at 4-bit (about 5.5 GB) fits entirely in an 8 GB laptop GPU and runs at usable speed.
# Set $env:SIEVE_OFFLINE_MODEL to the 30B-A3B GGUF to try the larger model; on 8 GB it spills to CPU and runs far slower.
$model = if ($env:SIEVE_OFFLINE_MODEL) { $env:SIEVE_OFFLINE_MODEL } else { Join-Path (Split-Path -Parent $root) "models\nvidia_NVIDIA-Nemotron-Nano-9B-v2-Q4_K_M.gguf" }
if (-not (Test-Path $bin))   { Write-Error "llama-server not found at $bin (download a llama.cpp CUDA build into tools\llama.cpp)"; exit 1 }
if (-not (Test-Path $model)) { Write-Error "model not found at $model (download from bartowski/nvidia_NVIDIA-Nemotron-Nano-9B-v2-GGUF)"; exit 1 }
& $bin --model $model --alias nemotron-nano --host 127.0.0.1 --port 8080 --ctx-size 32768 --n-gpu-layers 99 --threads 8 --jinja --reasoning-format none
