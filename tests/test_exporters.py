"""Tests for release-notes exporters."""

import shutil
from datetime import date
from pathlib import Path

import pytest

from release_notes_agent.models.schemas import ReleaseMetadata
from release_notes_agent.tools.exporters import export_release_notes

MD = """## New Features

- A

## Bug Fixes

- B
"""

META = ReleaseMetadata(
    product_name="Demo",
    version="1.2.0",
    release_date=date(2026, 4, 17),
    audience="internal",
)


class TestExportReleaseNotes:
    def test_md(self, tmp_path):
        out = tmp_path / "r.md"
        path = export_release_notes.__wrapped__(
            markdown_text=MD,
            fmt="md",
            output_path=str(out),
            metadata=META.model_dump(mode="json"),
        )
        assert Path(path).read_text(encoding="utf-8") == MD

    def test_html_contains_title_and_sections(self, tmp_path):
        out = tmp_path / "r.html"
        export_release_notes.__wrapped__(
            markdown_text=MD,
            fmt="html",
            output_path=str(out),
            metadata=META.model_dump(mode="json"),
        )
        html = out.read_text(encoding="utf-8")
        assert "Demo 1.2.0" in html
        assert "<h2>New Features</h2>" in html
        assert "<li>A</li>" in html

    def test_docx_non_empty(self, tmp_path):
        out = tmp_path / "r.docx"
        export_release_notes.__wrapped__(
            markdown_text=MD,
            fmt="docx",
            output_path=str(out),
            metadata=META.model_dump(mode="json"),
        )
        assert out.stat().st_size > 1000
        from docx import Document

        doc = Document(str(out))
        text = "\n".join(p.text for p in doc.paragraphs)
        assert "New Features" in text
        assert "Bug Fixes" in text

    def test_pdf_non_empty(self, tmp_path):
        # WeasyPrint needs GTK on Windows; skip gracefully if unavailable.
        try:
            from weasyprint import HTML  # noqa: F401
        except OSError:
            pytest.skip("WeasyPrint system deps unavailable")
        if (
            shutil.which("gtk-launch") is None
            and not Path("/usr/lib/x86_64-linux-gnu/libgobject-2.0.so.0").exists()
        ):
            pytest.skip("WeasyPrint system deps unavailable")
        out = tmp_path / "r.pdf"
        export_release_notes.__wrapped__(
            markdown_text=MD,
            fmt="pdf",
            output_path=str(out),
            metadata=META.model_dump(mode="json"),
        )
        header = out.read_bytes()[:4]
        assert header == b"%PDF"

    def test_unknown_format_raises(self, tmp_path):
        with pytest.raises(ValueError):
            export_release_notes.__wrapped__(
                markdown_text=MD,
                fmt="rtf",
                output_path=str(tmp_path / "r.rtf"),
                metadata=META.model_dump(mode="json"),
            )
