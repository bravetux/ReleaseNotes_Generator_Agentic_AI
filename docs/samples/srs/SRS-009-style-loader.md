# SRS-009 — Sample Style Loader

**Product:** release-notes-agent
**Module:** `tools/style_loader.py`
**Target release:** 1.3.0
**Author:** Platform Eng
**Date:** 2026-04-14

## 1. Overview

The style loader parses a user-supplied sample release-notes file and
extracts headings, list style, and section order. It is the only
mechanism by which the writer matches the customer's voice — weaknesses
here cascade into poor output.

## 2. Bugs

- **BUG-9001** — When the sample document uses setext-style headings
  (`===` or `---` underline) instead of ATX (`#`), no headings are
  extracted and `section_order` is empty.

- **BUG-9002** — DOCX samples with nested lists report
  `list_style="bullet"` even when the top level is numbered, because
  the loader looks at the last list item in the document, not the
  dominant style.

- **BUG-9003** — The 2000-character `raw_excerpt` truncation cuts
  mid-word, producing an unnatural trailing fragment that the writer
  treats as meaningful input.

## 3. Functional Requirements

- **FR-9001** — Support setext-style headings in Markdown samples by
  pre-converting them to ATX (`# Heading`) before regex extraction.

- **FR-9002** — `list_style` must be determined by counting bullet vs
  numbered items at the top level of the first list and taking the
  majority; tie-break to `bullet`.

- **FR-9003** — `raw_excerpt` truncation must round down to the nearest
  paragraph break (`\n\n`) to avoid mid-word cuts.

- **FR-9004** — Add a `warnings: list[str]` field on `SampleStyle` and
  populate it when the sample is too short (< 200 chars) or contains
  no headings; the writer prompt must surface these to the user via
  the CLI and UI.

## 4. Acceptance

Unit tests over 6 synthetic samples (ATX, setext, nested lists,
heading-free, very-short, mixed) must all pass.
