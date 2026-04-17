# SRS-003 — Streamlit UI

**Product:** release-notes-agent
**Module:** `ui/generate_form.py`, `app.py`
**Target release:** 1.3.0
**Author:** UX
**Date:** 2026-04-11

## 1. Overview

Close the gap between the Generate tab and the Chat tab, and improve the
first-run experience when the user has no AWS credentials configured.

## 2. Bugs

- **BUG-3001** — Uploading a 30 MB DOCX file freezes the UI for ~15 s
  with no spinner; users click Generate twice, producing two parallel
  pipeline runs that race on the same output path.

- **BUG-3002** — When `audience="both"` the Streamlit preview only renders
  the internal markdown; the external markdown is generated and saved
  but never shown in the browser.

- **BUG-3003** — The download button for the DOCX export sets
  `mime="application/octet-stream"`, causing Chrome to save the file as
  `.bin` instead of `.docx`.

## 3. Functional Requirements

- **FR-3001** — The Generate button must be disabled while a run is in
  flight (use `st.session_state["generating"]`). Show an
  `st.spinner("Generating…")` over the whole form.

- **FR-3002** — When `audience="both"`, the UI must render two side-by-side
  expanders ("Internal preview", "External preview") with independent
  download buttons.

- **FR-3003** — The download button must use the correct MIME type per
  format (`text/markdown`, `text/html`,
  `application/vnd.openxmlformats-officedocument.wordprocessingml.document`,
  `application/pdf`).

- **FR-3004** — On startup, if `settings.aws_access_key_id` is empty,
  render an `st.error` banner on both tabs with a link to the
  `.env.example` setup instructions.

## 4. Non-goals

Full SSO login flow inside the UI (users still edit `.env`).
