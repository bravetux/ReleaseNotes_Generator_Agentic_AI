# SRS-004 — CLI Enhancements

**Product:** release-notes-agent
**Module:** `cli/app.py`
**Target release:** 1.3.0
**Author:** DevEx
**Date:** 2026-04-12

## 1. Overview

The CLI has feature parity with the UI but lacks ergonomics for CI usage
and batch generation. This SRS tracks the fixes and improvements required
to make it first-class for automation.

## 2. Bugs

- **BUG-4001** — `--date` rejects ISO-8601 strings that include a time
  component (e.g. `2026-04-17T00:00:00`), breaking integrations with
  Jira where dates are serialised with timestamps.

- **BUG-4002** — Repeating `--srs` with a folder path does not de-duplicate
  files already listed individually; the same file is processed twice
  and produces duplicate items (the merge step catches it but the
  extractor LLM is called twice, doubling cost).

- **BUG-4003** — `main.py chat` crashes on Windows when the user hits
  Ctrl+Z (EOF on Windows) because only `EOFError` for POSIX was handled.

## 3. Functional Requirements

- **FR-4001** — `--date` must accept any value `date.fromisoformat` would
  accept, plus any full ISO-8601 datetime (truncate to the date portion).

- **FR-4002** — Before running the pipeline, the CLI must canonicalise
  all `--srs` paths (resolve symlinks, expand folders to files) and
  deduplicate by absolute path.

- **FR-4003** — Add `--dry-run` that loads SRS files, extracts items,
  prints a summary table (count per file, total bugs, total FRs) and
  exits without calling the writer or exporter. Intended for CI lint
  jobs.

- **FR-4004** — Add `--log-level` (`debug|info|warning|error`) flag
  mapped to Python logging. Default `info`.

## 4. Acceptance

`uv run python main.py generate --dry-run ...` must complete in under
5 seconds on the 10-file sample corpus and print a non-empty summary.
