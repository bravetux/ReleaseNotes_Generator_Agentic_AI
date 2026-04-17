"""Streamlit form for the deterministic release-notes pipeline."""

from __future__ import annotations

import re
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

import streamlit as st

from release_notes_agent.config.settings import settings
from release_notes_agent.models.schemas import GenerateRequest
from release_notes_agent.pipeline import generate_release_notes

_MIME = {
    "md": "text/markdown",
    "html": "text/html",
    "docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    "pdf": "application/pdf",
}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9._-]+", "-", text.lower()).strip("-") or "release_notes"


def _save_upload(uploaded: Any, dest_dir: Path) -> str:  # noqa: ANN401
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = dest_dir / uploaded.name
    path.write_bytes(uploaded.getbuffer())
    return str(path)


def _format_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n //= 1024
    return f"{n} TB"


def _render_file_chips(files: list[Any], label: str) -> None:
    if not files:
        return
    chips = " ".join(
        f"`{f.name}` ({_format_size(f.size)})" for f in files if f is not None
    )
    st.markdown(f"**{label}:** {chips}")


def render_generate_form() -> None:
    st.markdown("### Generate release notes")
    st.caption(
        "Ingest SRS documents, match a sample style, and export to "
        "Markdown / HTML / DOCX / PDF."
    )

    # ── Section 1: Documents ────────────────────────────────────────────────
    st.markdown("#### 1. Documents")
    doc_col1, doc_col2 = st.columns(2)
    with doc_col1:
        srs_files = st.file_uploader(
            "SRS documents",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True,
            help="PDF, DOCX, TXT, or Markdown. Multiple files supported.",
        )
    with doc_col2:
        sample_file = st.file_uploader(
            "Sample release-notes (style exemplar)",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=False,
            help="The writer will mirror this file's headings and tone.",
        )

    if srs_files:
        _render_file_chips(srs_files, f"{len(srs_files)} SRS file(s)")
    if sample_file:
        _render_file_chips([sample_file], "Sample")

    st.divider()

    # ── Section 2: Metadata ─────────────────────────────────────────────────
    st.markdown("#### 2. Release metadata")
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    with meta_col1:
        product = st.text_input("Product name", value="Demo")
    with meta_col2:
        version = st.text_input("Version", value="1.0.0")
    with meta_col3:
        rel_date = st.date_input("Release date", value=date.today())

    audience = st.radio(
        "Audience",
        ["internal", "external", "both"],
        horizontal=True,
        help="`internal` preserves Bug IDs + traceability; `external` strips them.",
    )

    st.divider()

    # ── Section 3: Output ───────────────────────────────────────────────────
    st.markdown("#### 3. Output")
    out_col1, out_col2 = st.columns([1, 2])
    with out_col1:
        output_format = st.selectbox("Format", ["md", "html", "docx", "pdf"])
    with out_col2:
        default_name = f"{_slug(product)}-{_slug(version)}.{output_format}"
        out_name = st.text_input("Filename", value=default_name)

    # ── Readiness + submit ──────────────────────────────────────────────────
    ready = bool(srs_files and sample_file and product and version)
    if not ready:
        missing = [
            n
            for n, ok in [
                ("SRS files", bool(srs_files)),
                ("sample file", bool(sample_file)),
                ("product", bool(product)),
                ("version", bool(version)),
            ]
            if not ok
        ]
        st.caption(f":grey[Waiting for: {', '.join(missing)}.]")

    if st.button("Generate", type="primary", disabled=not ready):
        _run_pipeline(
            srs_files,
            sample_file,
            product,
            version,
            rel_date,
            audience,
            output_format,
            out_name,
        )


def _run_pipeline(
    srs_files: list[Any],
    sample_file: Any,  # noqa: ANN401
    product: str,
    version: str,
    rel_date: date,
    audience: str,
    output_format: str,
    out_name: str,
) -> None:
    work_dir = Path(tempfile.mkdtemp(prefix="rna_"))
    out_dir = Path(settings.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / out_name

    status = st.status("Generating release notes…", expanded=True)
    with status:
        st.write("Saving uploads…")
        srs_paths = [_save_upload(f, work_dir / "srs") for f in srs_files]
        sample_path = _save_upload(sample_file, work_dir / "sample")

        req = GenerateRequest(
            srs_paths=srs_paths,
            sample_path=sample_path,
            product_name=product,
            version=version,
            release_date=rel_date,
            audience=audience,  # type: ignore[arg-type]
            output_format=output_format,  # type: ignore[arg-type]
            output_path=str(out_path),
        )
        st.write("Running pipeline (ingest → extract → merge → write → export)…")
        result = generate_release_notes(req)
        status.update(
            label=f"Done — generated {len(result.output_paths)} file(s).",
            state="complete",
        )

    _render_result(result, output_format)


def _render_result(result: Any, output_format: str) -> None:  # noqa: ANN401
    st.success(f"Generated {len(result.output_paths)} file(s).")

    # Preview
    previews: list[tuple[str, str]] = []
    if result.internal_markdown:
        previews.append(("Internal", result.internal_markdown))
    if result.external_markdown:
        previews.append(("External", result.external_markdown))

    if previews:
        tabs = st.tabs([label for label, _ in previews])
        for tab, (label, md) in zip(tabs, previews):
            with tab:
                st.markdown(md)

    # Traceability
    if result.traceability:
        with st.expander(f"Traceability matrix ({len(result.traceability)} rows)"):
            rows = [
                {
                    "Bug ID": t.bug_id or "",
                    "FR ID": t.fr_id or "",
                    "Source": t.source_file,
                    "Section": t.release_note_section,
                }
                for t in result.traceability
            ]
            st.dataframe(rows, use_container_width=True, hide_index=True)

    # Downloads
    st.markdown("#### Downloads")
    mime = _MIME.get(output_format, "application/octet-stream")
    dl_cols = st.columns(max(1, len(result.output_paths)))
    for col, path in zip(dl_cols, result.output_paths):
        p = Path(path)
        with col:
            st.download_button(
                label=f"⬇ {p.name}",
                data=p.read_bytes(),
                file_name=p.name,
                mime=mime,
                use_container_width=True,
                key=f"dl-{p.name}",
            )
