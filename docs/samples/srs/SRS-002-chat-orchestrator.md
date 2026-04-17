# SRS-002 — Chat Orchestrator

**Product:** release-notes-agent
**Module:** `agents/orchestrator.py`
**Target release:** 1.3.0
**Author:** Agent Platform
**Date:** 2026-04-11

## 1. Overview

Improve reliability and observability of the chat orchestrator so that
non-technical users can drive the release-notes pipeline end-to-end from
natural language without hitting dead-ends.

## 2. Bugs

- **BUG-2001** — `SummarizingConversationManager` occasionally drops the
  most recent tool result when summarisation fires mid-turn, causing the
  orchestrator to re-invoke `load_srs` on the same paths.

- **BUG-2002** — `FileSessionManager` writes are not atomic on Windows;
  concurrent tabs in Streamlit corrupt the session JSON, and the next
  turn fails with `json.JSONDecodeError`.

- **BUG-2003** — When `AWS_SESSION_TOKEN` expires mid-conversation the
  Bedrock call raises `ExpiredTokenException` and the full traceback is
  surfaced to the chat UI instead of a clean "please re-authenticate"
  message.

## 3. Functional Requirements

- **FR-2001** — Summarisation must never discard the immediately preceding
  tool result in the same turn; audit hook logs must show the full
  `TOOL_CALL_START` / `TOOL_CALL_END` pair.

- **FR-2002** — Session writes must go through a temp-file + rename to
  guarantee atomic replace on Windows. Corrupted session files must be
  quarantined to `.sessions/.quarantine/` and a fresh session started.

- **FR-2003** — Bedrock credential errors must be caught at the
  orchestrator boundary and returned as a user-facing message asking for
  re-authentication, without the stack trace.

- **FR-2004** — Add an `audit_log_path` setting so tool-call logs can be
  tailed from a file (for the Streamlit sidebar to render live).

## 4. Acceptance

A scripted multi-turn chat that runs `load_srs`, `merge_srs_items`,
`export_release_notes` must complete without duplicate tool calls and
without losing any result across summarisation boundaries.
