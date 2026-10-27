# Verification as a Nebius Serverless Job

`verify.sh` runs on a fresh Nebius Serverless machine with nothing of ours on it. It clones both public repositories,
installs them, runs every test and the published safety checks that need no model key, then calls both hosted APIs
end to end. The job fails if anything a judge would rely on is broken.

```
nebius ai job create --parent-id <project> --name both-entries-verify \
  --image python:3.12-slim --platform gpu-l40s-a --preset 1gpu-8vcpu-32gb --disk-size 40Gi --timeout 45m \
  --inject-file "infra/job-verify/verify.sh:/verify.sh" --container-command bash --args "/verify.sh"
nebius ai job logs <job-id>
```

The job needs no GPU, but this account's CPU-only quota is zero, so it runs on the smallest L40S preset (about
$1.55 an hour, a few minutes). Logs of the run are in `RUN.md`.
