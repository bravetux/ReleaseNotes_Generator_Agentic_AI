"""Deterministic release-notes generation pipeline.

This orchestrates the tools and sub-agents in a fixed order. It is called
directly by the UI and CLI — it does NOT go through the chat Agent.
"""

from __future__ import annotations

import concurrent.futures
import logging
from pathlib import Path

from release_notes_agent.agents.release_writer import write_release_notes
from release_notes_agent.agents.srs_extractor import extract_items
from release_notes_agent.models.schemas import (
    GenerateRequest,
    GenerationResult,
    ReleaseMetadata,
    SampleStyle,
    SrsItem,
    TraceabilityEntry,
)
from release_notes_agent.tools.exporters import export_release_notes
from release_notes_agent.tools.item_ops import merge_srs_items
from release_notes_agent.tools.srs_loaders import load_srs
from release_notes_agent.tools.style_loader import load_sample_style

logger = logging.getLogger(__name__)

_SECTION_BY_TYPE = {
    "bug": "Bug Fixes",
    "feature": "New Features",
    "enhancement": "Enhancements",
}


def _build_traceability(items: list[SrsItem]) -> list[TraceabilityEntry]:
    return [
        TraceabilityEntry(
            bug_id=i.bug_id,
            fr_id=i.fr_id,
            source_file=i.source_file,
            release_note_section=_SECTION_BY_TYPE.get(i.item_type, "Other"),
        )
        for i in items
    ]


def _traceability_markdown(entries: list[TraceabilityEntry]) -> str:
    lines = [
        "",
        "## Traceability",
        "",
        "| Bug ID | FR ID | Source File | Section |",
        "|---|---|---|---|",
    ]
    for e in entries:
        lines.append(
            f"| {e.bug_id or ''} | {e.fr_id or ''} | {e.source_file} "
            f"| {e.release_note_section} |"
        )
    return "\n".join(lines) + "\n"


def _variant_path(base: str, suffix: str) -> str:
    p = Path(base)
    return str(p.with_name(f"{p.stem}.{suffix}{p.suffix}"))


def generate_release_notes(req: GenerateRequest) -> GenerationResult:
    """Run the full pipeline deterministically and return a GenerationResult."""
    loaded = load_srs.__wrapped__(paths=req.srs_paths)
    all_items: list[SrsItem] = []
    for doc in loaded:
        if "error" in doc:
            logger.warning("skipping %s: %s", doc["filename"], doc["error"])
            continue
        all_items.extend(
            extract_items(raw_text=doc["raw_text"], filename=doc["filename"])
        )

    merged_dicts = merge_srs_items.__wrapped__(
        items=[i.model_dump() for i in all_items]
    )
    merged = [SrsItem.model_validate(d) for d in merged_dicts]

    style = SampleStyle.model_validate(
        load_sample_style.__wrapped__(path=req.sample_path)
    )
    metadata = ReleaseMetadata(
        product_name=req.product_name,
        version=req.version,
        release_date=req.release_date,
        audience=req.audience,
    )

    internal_md: str | None = None
    external_md: str | None = None

    if req.audience == "both":
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            f_int = ex.submit(write_release_notes, merged, style, metadata, "internal")
            f_ext = ex.submit(write_release_notes, merged, style, metadata, "external")
            internal_md = f_int.result()
            external_md = f_ext.result()
    elif req.audience == "internal":
        internal_md = write_release_notes(merged, style, metadata, "internal")
    else:  # external
        external_md = write_release_notes(merged, style, metadata, "external")

    traceability = _build_traceability(merged)
    output_paths: list[str] = []

    if internal_md is not None:
        body = internal_md + _traceability_markdown(traceability)
        path = export_release_notes.__wrapped__(
            markdown_text=body,
            fmt=req.output_format,
            output_path=req.output_path,
            metadata=metadata.model_dump(mode="json"),
        )
        output_paths.append(path)

    if external_md is not None:
        ext_out = (
            _variant_path(req.output_path, "external")
            if internal_md is not None
            else req.output_path
        )
        path = export_release_notes.__wrapped__(
            markdown_text=external_md,
            fmt=req.output_format,
            output_path=ext_out,
            metadata=metadata.model_dump(mode="json"),
        )
        output_paths.append(path)

    return GenerationResult(
        metadata=metadata,
        internal_markdown=internal_md,
        external_markdown=external_md,
        traceability=traceability,
        output_paths=output_paths,
    )
