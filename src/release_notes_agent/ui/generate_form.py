"""Streamlit form for the deterministic release-notes pipeline."""

from __future__ import annotations

import tempfile
from datetime import date
from pathlib import Path
from typing import Any

import streamlit as st

from release_notes_agent.config.settings import settings
from release_notes_agent.models.schemas import GenerateRequest
from release_notes_agent.pipeline import generate_release_notes


def _save_upload(uploaded: Any, dest_dir: Path) -> str:  # noqa: ANN401
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = dest_dir / uploaded.name
    path.write_bytes(uploaded.getbuffer())
    return str(path)


def render_generate_form() -> None:
    st.header("Generate release notes")

    srs_files = st.file_uploader(
        "SRS documents (PDF / DOCX / TXT / MD)",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
    )
    sample_file = st.file_uploader(
        "Sample release-notes document",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=False,
    )

    col1, col2 = st.columns(2)
    with col1:
        product = st.text_input("Product name", value="Demo")
        version = st.text_input("Version", value="1.0.0")
    with col2:
        rel_date = st.date_input("Release date", value=date.today())
        audience = st.radio(
            "Audience", ["internal", "external", "both"], horizontal=True
        )

    output_format = st.selectbox("Output format", ["md", "html", "docx", "pdf"])
    out_name = st.text_input("Output filename", value=f"release_notes.{output_format}")

    if st.button("Generate", type="primary", disabled=not (srs_files and sample_file)):
        work_dir = Path(tempfile.mkdtemp(prefix="rna_"))
        srs_paths = [_save_upload(f, work_dir / "srs") for f in srs_files]
        sample_path = _save_upload(sample_file, work_dir / "sample")
        out_dir = Path(settings.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / out_name

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
        with st.spinner("Generating…"):
            result = generate_release_notes(req)

        st.success(f"Generated {len(result.output_paths)} file(s).")

        if result.internal_markdown:
            st.subheader("Internal preview")
            st.markdown(result.internal_markdown)
        if result.external_markdown:
            st.subheader("External preview")
            st.markdown(result.external_markdown)

        for path in result.output_paths:
            p = Path(path)
            st.download_button(
                label=f"Download {p.name}",
                data=p.read_bytes(),
                file_name=p.name,
                mime="application/octet-stream",
                key=f"dl-{p.name}",
            )
