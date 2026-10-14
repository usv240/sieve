# OpenShell sandbox run, demonstrated 2026-10-14

Environment: Windows 11, WSL2 Ubuntu 24.04, Docker Desktop 29.5 with WSL integration, OpenShell 0.1.4 binaries in `~/.openshell/bin` (the .deb installer needs sudo; the release tarballs do not).

## What ran

1. Gateway PKI generated exactly as the packaged service unit does, with extra subject alternative names for the Docker Desktop host alias, and the gateway started with TLS (mTLS to the CLI).
2. A schema version 2 gateway config (`gateway.toml`) pointing the Docker driver's `grpc_endpoint` at `https://host.docker.internal:17670`, because Docker Desktop runs containers in its own VM while the gateway listens inside the WSL distro. Without this the sandbox supervisor cannot fetch its startup configuration.
3. Image `sieve-agent:latest` (1.2 GB) built from `Dockerfile.agent`: the repo, dependencies, the 9,458-page index, the openFDA snapshots. Workspace made writable for any uid because OpenShell runs the workload as uid 1000.
4. Sandbox created with `--no-auto-providers` and a long-lived main process, then exec'd into.
5. Two provider profiles (`profiles/nebius-token-factory.yaml`, `profiles/tavily.yaml`) linted and imported; providers created with env-lookup credentials; both attached to the sandbox.
6. A full Sieve diagnosis executed inside the sandbox.

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

Credentials inside the sandbox after attaching providers (real keys never enter the sandbox; OpenShell substitutes them at the allowed hosts only):

```
NEBIUS_API_KEY=opensh...
TAVILY_API_KEY=opensh...
```

Full pipeline run inside the sandbox:

```
INSIDE OPENSHELL SANDBOX: Philips Respironics EverFlo 19s
summary: Low oxygen purity (82%) most often indicates sieve bed exhaustion or compressor wear. First verify power and measure oxygen output with a calibrated analyzer.
steps: 3 | citations: 7 / 7 | audit: approve_with_repairs
tavily: {'parts': 'sieve bed pair (Molecular sieve bed exhaustion)'}
  trace Nemotron 3 Super synthesise.fault_tree 6131 1714 $0.0034
  trace Nemotron 3 Ultra audit.fault_tree 42474 1969 $0.0484
  trace Tavily tavily.find_parts 0 0 $0.0000
```

Three sponsor services (Nemotron 3 Super and Ultra via Nebius Token Factory, Tavily) were reached from a sandbox that holds placeholders only and can reach nothing else.

## Lessons recorded for the feedback section

- Policy `binaries` must name the resolved executable; a symlink path is accepted but never matches.
- `openshell inference set` from the hackathon brief no longer exists in 0.1.4; providers are profile based, and the gateway ships with an empty profile catalog, so a profile must be authored or imported first.
- Sandboxes exit when their initial command exits; use `-- sleep infinity` to keep one ready for `exec`.
- On Docker Desktop plus WSL2, `grpc_endpoint` is required and the server certificate must carry the host alias.
- The provider's credential placeholder appears in the sandbox environment only for processes started after attachment, which `exec` honours.

## Reproduce

```
bash infra/openshell/run.sh          # Linux, macOS or WSL2 with Docker; needs NEBIUS_API_KEY and TAVILY_API_KEY in the environment
```
