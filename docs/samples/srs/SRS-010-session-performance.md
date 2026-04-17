# SRS-010 — Session Persistence & Performance

**Product:** release-notes-agent
**Module:** `agents/orchestrator.py`, `pipeline.py`
**Target release:** 1.3.0
**Author:** SRE
**Date:** 2026-04-15

## 1. Overview

Long-running workflows (20+ SRS files in a single run) and multi-user
Streamlit deployments expose performance and session issues. This SRS
scopes the hardening work for production use behind an internal SSO
proxy.

## 2. Bugs

- **BUG-10001** — Sessions under `.sessions/` grow unbounded; one
  customer has 4.2 GB after six months, and orchestrator startup now
  takes > 3 s because the FileSessionManager loads the full history
  on construction.

- **BUG-10002** — `generate_release_notes(req)` serialises the two
  writer invocations when `audience="both"`, even though the plan
  claims parallelism — the `ThreadPoolExecutor` wait blocks on the
  first future before submitting the second.

- **BUG-10003** — On Windows, pipeline runs lock the output file
  exclusively during DOCX export; concurrent runs targeting the same
  `--out` path crash with `PermissionError: [WinError 32]` instead
  of failing with a clear "output path in use" message.

## 3. Functional Requirements

- **FR-10001** — Add a `MAX_SESSION_AGE_DAYS` setting (default 14);
  at orchestrator startup, purge session files older than this value.
  Log one summary line per purge run.

- **FR-10002** — The writer fan-out for `audience="both"` must submit
  both futures first, then `concurrent.futures.wait`; both invocations
  must overlap in time (asserted via timestamps in a unit test).

- **FR-10003** — Wrap the atomic write with a retry-on-`PermissionError`
  loop (max 3 attempts, 250 ms back-off). After final failure, raise
  `ExportError("Output path locked by another process: <path>")`.

- **FR-10004** — Expose a `/healthz` endpoint from the Streamlit
  sidebar: it renders the orchestrator session dir size, the last
  five tool calls, and the configured Bedrock model ID.

## 4. Non-functional

- p95 orchestrator startup < 500 ms on a freshly purged session dir.
- Peak memory during a 20-file run must stay under 1 GB on a t3.medium.
