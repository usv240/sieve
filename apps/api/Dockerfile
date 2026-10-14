# Sieve API for hosting (Render, Fly, Railway or any Docker host). Includes the prebuilt index and the CC0 data.
FROM python:3.12-slim
ENV PYTHONIOENCODING=utf-8 PIP_NO_CACHE_DIR=1 PORT=8000
RUN pip install uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen
COPY packages ./packages
COPY apps/api ./apps/api
COPY apps/mcp ./apps/mcp
COPY scripts/install_paths.py ./scripts/install_paths.py
RUN uv run python scripts/install_paths.py
COPY data/index ./data/index
COPY data/external ./data/external
COPY data/samples ./data/samples
COPY data/records.jsonl ./data/records.jsonl
COPY eval/results ./eval/results
EXPOSE 8000
CMD ["sh", "-c", "uv run uvicorn sieve_api.main:app --host 0.0.0.0 --port ${PORT}"]
