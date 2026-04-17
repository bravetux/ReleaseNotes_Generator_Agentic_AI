# SRS-007 — Release Writer Agent

**Product:** release-notes-agent
**Module:** `agents/release_writer.py`, `config/prompts.py`
**Target release:** 1.3.0
**Author:** ML Platform
**Date:** 2026-04-13

## 1. Overview

The writer produces the customer-visible text. Two audiences are
supported, and the current output is technically correct but stylistically
generic — it does not reliably mirror the sample exemplar.

## 2. Bugs

- **BUG-7001** — External audience output sometimes leaks internal
  Bug-IDs inside the prose (e.g. "Fixed an issue (BUG-1023) where…").
  The prompt forbids it, but the model regresses on ~5% of runs.

- **BUG-7002** — Section ordering ignores `SampleStyle.section_order`.
  The writer always emits `## New Features` then `## Bug Fixes`, even
  when the sample uses the opposite order.

- **BUG-7003** — When the input contains zero bugs, the writer still
  emits an empty `## Bug Fixes` heading with the placeholder text
  "No bugs in this release.", which two customers have flagged as
  embarrassing.

## 3. Functional Requirements

- **FR-7001** — After writer output, run a deterministic post-check:
  for `audience="external"`, reject any line containing `BUG-\d+` or
  `FR-\d+` and re-prompt the model up to twice to rewrite that line.

- **FR-7002** — The writer prompt must include the verbatim
  `SampleStyle.section_order` list and an explicit instruction:
  "Emit sections in this exact order; omit any with no items."

- **FR-7003** — If a category (bugs / features / enhancements) has zero
  items, the writer must omit the heading entirely rather than emitting
  a placeholder.

- **FR-7004** — Expose a `tone` parameter (`neutral|enthusiastic|formal`)
  on `GenerateRequest` that is injected into the writer system prompt.

## 4. Acceptance

Running the pipeline with `tests/fixtures/sample_release_notes.md` as
the exemplar must produce output whose first H2 matches the first H2
in the sample for 20 consecutive runs (style stability test).
