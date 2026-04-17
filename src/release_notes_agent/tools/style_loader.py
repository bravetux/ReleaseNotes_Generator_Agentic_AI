"""Sample release-notes style extractor."""

import re
from pathlib import Path

from strands import tool

from release_notes_agent.tools.srs_loaders import _READERS, SUPPORTED_EXTS

_EXCERPT_CHARS = 2000
_BULLET_RE = re.compile(r"^\s*[-*]\s+", re.MULTILINE)
_NUMBERED_RE = re.compile(r"^\s*\d+\.\s+", re.MULTILINE)
_MD_HEADING_RE = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


def _extract_headings(path: Path, raw_text: str, ext: str) -> list[str]:
    if ext == ".docx":
        from docx import Document

        doc = Document(str(path))
        return [
            p.text.strip()
            for p in doc.paragraphs
            if p.style and p.style.name.startswith("Heading") and p.text.strip()
        ]
    return [m.group(2).strip() for m in _MD_HEADING_RE.finditer(raw_text)]


@tool
def load_sample_style(path: str) -> dict:
    """Parse a sample release-notes file and return style metadata.

    Args:
        path: Path to a .md/.txt/.docx/.pdf sample release-notes document.

    Returns:
        A dict with ``headings``, ``section_order``, ``list_style``
        ("bullet"|"numbered"), and ``raw_excerpt`` (first 2000 chars).
    """
    p = Path(path)
    ext = p.suffix.lower()
    if ext not in SUPPORTED_EXTS:
        return {
            "headings": [],
            "section_order": [],
            "list_style": "bullet",
            "raw_excerpt": "",
            "error": f"unsupported extension {ext}",
        }

    raw_text = _READERS[ext](p)
    headings = _extract_headings(p, raw_text, ext)

    bullets = len(_BULLET_RE.findall(raw_text))
    numbered = len(_NUMBERED_RE.findall(raw_text))
    list_style = "numbered" if numbered > bullets else "bullet"

    # Section order: sub-headings (skip the document title, which is the first
    # heading when present). Preserve first-occurrence order, dedup.
    body_headings = headings[1:] if len(headings) > 1 else headings
    seen: list[str] = []
    for h in body_headings:
        if h not in seen:
            seen.append(h)

    return {
        "headings": headings,
        "section_order": seen,
        "list_style": list_style,
        "raw_excerpt": raw_text[:_EXCERPT_CHARS],
    }
