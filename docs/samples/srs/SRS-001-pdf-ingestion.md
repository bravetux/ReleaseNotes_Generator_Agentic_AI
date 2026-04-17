# SRS-001 — PDF Ingestion

**Product:** release-notes-agent
**Module:** `tools/srs_loaders.py`
**Target release:** 1.3.0
**Author:** Platform Eng
**Date:** 2026-04-10

## 1. Overview

Hardening the PDF ingestion path after field reports of silent failures on
scanned and multi-column SRS PDFs. Scope covers both bug fixes and two new
capabilities on the PDF loader.

## 2. Bugs

- **BUG-1001** — Scanned/image-only PDFs return empty text without warning.
  `pypdf.PdfReader.extract_text()` silently yields `""`, which passes through
  to the extractor and produces zero items. The user sees a successful run
  with an empty release-notes file.

- **BUG-1002** — PDFs containing form fields raise
  `PyPdfError: Unknown PDF Form Field type` and crash the whole pipeline
  instead of the single file being flagged as unreadable.

- **BUG-1003** — Multi-column page layout interleaves lines from both
  columns, corrupting Bug-ID/description pairs passed to the extractor LLM.
  Root cause: text extraction follows coordinate order, not reading order.

## 3. Functional Requirements

- **FR-1001** — When `extract_text()` returns fewer than 20 non-whitespace
  characters across the whole document, `load_srs` must emit a structured
  error entry (`{"error": "empty_or_scanned_pdf", "path": ...}`) rather
  than returning empty content.

- **FR-1002** — All `pypdf` exceptions must be caught per-file and converted
  to an error entry; the loader must continue with the remaining files.

- **FR-1003** — The loader must accept an optional `layout="columns"` hint
  and, when set, sort text blocks by column bounding box before concatenating.

- **FR-1004** — Add unit tests for each of the three bugs using tiny
  fixture PDFs under `tests/fixtures/pdf_edge_cases/`.

## 4. Out of scope

OCR for scanned PDFs (deferred to Phase 3), encrypted PDFs.
