# Ingestion job: PDFs -> page text -> (optional) VL figure descriptions -> (optional) Nemotron embed-vl vectors -> index
FROM nvidia/cuda:12.6.2-runtime-ubuntu24.04
ENV DEBIAN_FRONTEND=noninteractive PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-venv curl git && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY packages ./packages
COPY scripts ./scripts
COPY data/manifest.yaml ./data/manifest.yaml
RUN uv sync --no-dev && uv run python scripts/install_paths.py
# Corpus is fetched at run time into the job's disk; nothing copyrighted is baked into the image.
ENTRYPOINT ["bash", "-lc", "bash scripts/fetch_corpus.sh && uv run python -m sieve_retrieval.ingest --out /output/index && cp /output/index/ingest_report.json /output/ingest_report.json"]
