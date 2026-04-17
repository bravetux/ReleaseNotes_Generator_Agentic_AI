"""Tests for Pydantic schemas."""

from datetime import date

import pytest
from pydantic import ValidationError

from release_notes_agent.models.schemas import (
    GenerateRequest,
    GenerationResult,
    ReleaseMetadata,
    SampleStyle,
    SrsItem,
    TraceabilityEntry,
)


class TestSrsItem:
    def test_minimal(self):
        item = SrsItem(
            item_type="bug", description="Crash on save", source_file="srs.pdf"
        )
        assert item.bug_id is None
        assert item.item_type == "bug"

    def test_rejects_bad_type(self):
        with pytest.raises(ValidationError):
            SrsItem(item_type="nope", description="x", source_file="srs.pdf")

    def test_roundtrip_json(self):
        item = SrsItem(
            bug_id="BUG-1",
            fr_id="FR-2",
            item_type="feature",
            description="d",
            functional_requirement="fr",
            severity="major",
            source_file="srs.pdf",
        )
        assert SrsItem.model_validate_json(item.model_dump_json()) == item


class TestReleaseMetadata:
    def test_audience_values(self):
        meta = ReleaseMetadata(
            product_name="X",
            version="1.0.0",
            release_date=date(2026, 4, 17),
            audience="both",
        )
        assert meta.audience == "both"

    def test_rejects_bad_audience(self):
        with pytest.raises(ValidationError):
            ReleaseMetadata(
                product_name="X",
                version="1",
                release_date=date(2026, 4, 17),
                audience="foo",
            )


class TestSampleStyle:
    def test_defaults(self):
        s = SampleStyle(raw_excerpt="# Title")
        assert s.headings == []
        assert s.list_style == "bullet"
        assert s.section_order == []


class TestTraceabilityEntry:
    def test_minimal(self):
        t = TraceabilityEntry(source_file="srs.pdf", release_note_section="Bug Fixes")
        assert t.bug_id is None


class TestGenerationResult:
    def test_minimal(self):
        meta = ReleaseMetadata(
            product_name="X",
            version="1.0.0",
            release_date=date(2026, 4, 17),
            audience="internal",
        )
        r = GenerationResult(metadata=meta)
        assert r.internal_markdown is None
        assert r.traceability == []


class TestGenerateRequest:
    def test_minimal(self):
        req = GenerateRequest(
            srs_paths=["a.pdf"],
            sample_path="sample.md",
            product_name="X",
            version="1.0.0",
            release_date=date(2026, 4, 17),
            audience="internal",
            output_format="md",
            output_path="out.md",
        )
        assert req.output_format == "md"
