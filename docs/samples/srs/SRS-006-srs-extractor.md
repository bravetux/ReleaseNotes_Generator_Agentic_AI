# SRS-006 — SRS Extractor Agent

**Product:** release-notes-agent
**Module:** `agents/srs_extractor.py`
**Target release:** 1.3.0
**Author:** ML Platform
**Date:** 2026-04-13

## 1. Overview

The extractor converts raw SRS text into a `list[SrsItem]` via a Bedrock
call. Field reports show (a) brittle JSON parsing, (b) wrong item types
for "enhancement" items, and (c) dropped Bug-IDs when the SRS uses
non-English punctuation.

## 2. Bugs

- **BUG-6001** — When the LLM response wraps the JSON array in a code
  fence (` ```json ... ``` `), the current regex `_JSON_BLOCK_RE`
  matches the whole fenced block and `json.loads` fails on the backticks.

- **BUG-6002** — Any item whose description starts with the word
  "Enhance…" is classified as `item_type="feature"` instead of
  `"enhancement"`, because the prompt does not list enhancement as a
  category.

- **BUG-6003** — Bug-IDs written with full-width digits (common in
  CJK documents, e.g. `BUG-１２３４`) are stripped by the extractor's
  ASCII-only regex in post-processing.

## 3. Functional Requirements

- **FR-6001** — `_JSON_BLOCK_RE` must strip surrounding ``` fences
  before parsing. Add a retry that asks the model to return JSON only
  (no fences) on the first parse failure.

- **FR-6002** — The system prompt must explicitly enumerate three
  `item_type` values (`bug`, `feature`, `enhancement`) and include an
  example of each.

- **FR-6003** — The Bug-ID normalizer must unicode-normalize
  (NFKC) the text before regex matching to fold full-width digits.

- **FR-6004** — Add a structured log line
  `EXTRACTOR_RESULT file=... items=... bugs=... features=...`
  so downstream monitoring can alert on zero-item files.

## 4. Acceptance

Running the extractor over `docs/samples/srs/SRS-00*.md` must yield
≥ 2 items per file with correct `item_type` classification.
