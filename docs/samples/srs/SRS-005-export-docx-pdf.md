# SRS-005 — DOCX & PDF Export

**Product:** release-notes-agent
**Module:** `tools/exporters.py`, `ui/templates/`
**Target release:** 1.3.0
**Author:** Release Mgmt
**Date:** 2026-04-12

## 1. Overview

Customers embed the exported DOCX in corporate templates and the PDF in
their support portal. Current output is functional but visually plain
and does not match the style exemplar passed to the writer.

## 2. Bugs

- **BUG-5001** — DOCX export loses all heading levels; `htmldocx` emits
  every `<h1>`/`<h2>` as `Normal` paragraphs, breaking the client's
  automatic TOC generation.

- **BUG-5002** — PDF export fails silently on Windows when GTK is missing:
  the WeasyPrint `ImportError` is caught at module load, so the user's
  pipeline run succeeds but `result.output_paths` is empty with no error.

- **BUG-5003** — The traceability table at the bottom of the internal
  document renders without table borders in the DOCX export; in HTML
  and PDF the borders are present.

## 3. Functional Requirements

- **FR-5001** — Replace `htmldocx` heading handling with a post-processing
  pass that maps `<h1>`..`<h4>` to the corresponding `Heading 1..4`
  Word styles.

- **FR-5002** — If PDF export is requested and WeasyPrint is unavailable,
  raise an explicit `ExportError("PDF export requires WeasyPrint/GTK: <url>")`
  rather than producing zero output paths.

- **FR-5003** — Add inline `border="1"` attributes on generated
  `<table>` elements so `htmldocx` preserves table borders in DOCX.

- **FR-5004** — Accept an optional `--logo <path.png>` CLI flag and
  `logo_path` field on `GenerateRequest`; embed the logo at the top
  of the first page in HTML/PDF and as an inline image in DOCX.

## 4. Acceptance

All three export paths (MD, HTML, DOCX) must round-trip the sample
release-notes in `tests/fixtures/sample_release_notes.md` while
preserving heading structure, lists, and table borders.
