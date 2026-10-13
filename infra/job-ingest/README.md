# Ingestion as a Nebius Serverless Job

Builds the page index from the corpus manifest. The lexical index needs no GPU; the figure-description and embedding enrichment steps use the GPU.

```
docker build -t ghcr.io/usv240/sieve-ingest:latest -f infra/job-ingest/Dockerfile .
docker push ghcr.io/usv240/sieve-ingest:latest

nebius ai job create \
  --name sieve-ingest \
  --image ghcr.io/usv240/sieve-ingest:latest \
  --platform gpu-l40s-a --preset 1gpu-8vcpu-32gb \
  --timeout 3h --disk-size 100Gi

nebius ai job logs <job-id>
```

The job writes `ingest_report.json` (documents, pages, low-text pages, seconds, GPU minutes). That report is shown on the Evals page under Ingestion.

Fallback without Nebius AI Cloud: `make fetch-corpus && make ingest` runs the same code on a laptop. Observed locally on 2026-10-13: 168 PDFs, 9,806 pages, 32.7 seconds for the lexical index.
