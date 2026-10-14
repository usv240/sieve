# OpenShell sandbox run, demonstrated 2026-10-14

Environment: Windows 11, WSL2 Ubuntu 24.04, Docker Desktop 29.5 with WSL integration, OpenShell 0.1.4 binaries in `~/.openshell/bin` (the .deb installer needs sudo; the release tarballs do not).

## What ran

1. Gateway PKI generated exactly as the packaged service unit does, with extra subject alternative names for the Docker Desktop host alias, and the gateway started with TLS (mTLS to the CLI).
2. A schema version 2 gateway config pointing the Docker driver's `grpc_endpoint` at `https://host.docker.internal:17670`, because Docker Desktop runs containers in its own VM while the gateway listens inside the WSL distro. Without this the sandbox supervisor cannot fetch its startup configuration.
3. Image `sieve-agent:latest` (1.2 GB) built from `Dockerfile.agent`: the repo, dependencies, the 9,458-page index, the openFDA snapshots. Workspace made writable for any uid because OpenShell runs the workload as uid 1000.
4. Sandbox created with `--no-auto-providers` and a long-lived main process, then exec'd into.

## Observed

Before any policy (deny by default):

```
api.fda.gov -> blocked: ConnectError [Errno 13] Permission denied
example.com -> blocked: ConnectError [Errno 13] Permission denied
```

After four `openshell policy update` rules (binary `/usr/local/bin/python3.12`, the resolved interpreter, not the venv symlink):

```
api.fda.gov    -> 200
api.tavily.com -> 200
example.com    -> blocked: ConnectError [Errno 13] Permission denied
```

The denial is at the kernel (Landlock and seccomp), not at an HTTP proxy, which is why it surfaces as EACCES on connect.

## Lessons recorded for the feedback section

- Policy `binaries` must name the resolved executable; a symlink path is accepted but never matches.
- `openshell inference set` from the hackathon brief no longer exists in 0.1.4; providers are profile based.
- Sandboxes exit when their initial command exits; use `-- sleep infinity` to keep one ready for `exec`.
- On Docker Desktop plus WSL2, `grpc_endpoint` is required and the server certificate must carry the host alias.

## Still to do

Attach a provider so the sandboxed pipeline gets brokered Nebius and Tavily credentials (placeholders inside, real keys injected only at the allowed hosts), then run a full diagnosis inside the sandbox and record the Trace.
