"""Pydantic data models for the release-notes pipeline."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class SrsItem(BaseModel):
    bug_id: str | None = None
    fr_id: str | None = None
    item_type: Literal["bug", "feature", "enhancement"]
    description: str
    functional_requirement: str | None = None
    severity: str | None = None
    source_file: str


class ReleaseMetadata(BaseModel):
    product_name: str
    version: str
    release_date: date
    audience: Literal["internal", "external", "both"]


class SampleStyle(BaseModel):
    headings: list[str] = Field(default_factory=list)
    list_style: Literal["bullet", "numbered"] = "bullet"
    section_order: list[str] = Field(default_factory=list)
    raw_excerpt: str = ""


class TraceabilityEntry(BaseModel):
    bug_id: str | None = None
    fr_id: str | None = None
    source_file: str
    release_note_section: str


class GenerationResult(BaseModel):
    metadata: ReleaseMetadata
    internal_markdown: str | None = None
    external_markdown: str | None = None
    traceability: list[TraceabilityEntry] = Field(default_factory=list)
    output_paths: list[str] = Field(default_factory=list)


class GenerateRequest(BaseModel):
    srs_paths: list[str]
    sample_path: str
    product_name: str
    version: str
    release_date: date
    audience: Literal["internal", "external", "both"]
    output_format: Literal["md", "html", "docx", "pdf"]
    output_path: str
