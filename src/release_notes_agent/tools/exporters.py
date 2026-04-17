"""Release-notes exporter: md -> html -> {md, html, docx, pdf}."""

import tempfile
from pathlib import Path
from typing import Literal

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown import markdown as md_to_html
from strands import tool

from release_notes_agent.models.schemas import ReleaseMetadata

_TEMPLATES_DIR = Path(__file__).parent.parent / "ui" / "templates"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "htm", "xml"]),
)


def _render_html(markdown_text: str, metadata: ReleaseMetadata) -> str:
    body_html = md_to_html(markdown_text, extensions=["tables", "fenced_code"])
    css = (_TEMPLATES_DIR / "release_notes.css").read_text(encoding="utf-8")
    template = _env.get_template("release_notes.html.j2")
    return template.render(metadata=metadata, body_html=body_html, css=css)


def _write_atomic(path: Path, writer) -> None:
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=path.suffix)
    import os

    os.close(fd)
    tmp = Path(tmp_name)
    try:
        writer(tmp)
        tmp.replace(path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


@tool
def export_release_notes(
    markdown_text: str,
    fmt: Literal["md", "html", "docx", "pdf"],
    output_path: str,
    metadata: dict,
) -> str:
    """Export release notes to a file in the requested format.

    Args:
        markdown_text: The release-notes body as Markdown.
        fmt: Output format.
        output_path: Absolute or relative path where the file is written.
        metadata: Serialised ReleaseMetadata (dict).

    Returns:
        The absolute path of the written file.
    """
    meta = ReleaseMetadata.model_validate(metadata)
    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "md":
        _write_atomic(out, lambda p: p.write_text(markdown_text, encoding="utf-8"))
    elif fmt == "html":
        html = _render_html(markdown_text, meta)
        _write_atomic(out, lambda p: p.write_text(html, encoding="utf-8"))
    elif fmt == "docx":
        from docx import Document
        from htmldocx import HtmlToDocx

        html = _render_html(markdown_text, meta)
        doc = Document()
        HtmlToDocx().add_html_to_document(html, doc)

        def _save(p: Path) -> None:
            doc.save(str(p))

        _write_atomic(out, _save)
    elif fmt == "pdf":
        from weasyprint import HTML

        html = _render_html(markdown_text, meta)
        _write_atomic(out, lambda p: HTML(string=html).write_pdf(str(p)))
    else:
        raise ValueError(f"unsupported format: {fmt}")

    return str(out)
