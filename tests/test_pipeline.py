"""End-to-end pipeline test with sub-agents mocked."""

from datetime import date
from pathlib import Path
from unittest.mock import patch

from release_notes_agent.models.schemas import GenerateRequest, SrsItem
from release_notes_agent.pipeline import generate_release_notes

FIXTURES = Path(__file__).parent / "fixtures"


def _mock_extract(raw_text, filename):
    return [
        SrsItem(
            bug_id="BUG-101",
            fr_id="FR-12",
            item_type="bug",
            description="crash on long filename",
            functional_requirement="save validation",
            severity="Major",
            source_file=filename,
        ),
    ]


def _mock_write(items, style, metadata, audience):
    if audience == "internal":
        return "## Bug Fixes\n\n- (BUG-101, FR-12) crash on long filename.\n"
    return "## Bug Fixes\n\n- Fixed a save issue with long file names.\n"


class TestGenerateReleaseNotes:
    def test_both_audiences_writes_two_files(self, tmp_path):
        req = GenerateRequest(
            srs_paths=[str(FIXTURES / "srs_small.md")],
            sample_path=str(FIXTURES / "sample_release_notes.md"),
            product_name="Demo",
            version="1.2.0",
            release_date=date(2026, 4, 17),
            audience="both",
            output_format="md",
            output_path=str(tmp_path / "out.md"),
        )
        with (
            patch(
                "release_notes_agent.pipeline.extract_items",
                side_effect=_mock_extract,
            ),
            patch(
                "release_notes_agent.pipeline.write_release_notes",
                side_effect=_mock_write,
            ),
        ):
            result = generate_release_notes(req)
        assert result.internal_markdown is not None
        assert result.external_markdown is not None
        assert len(result.output_paths) == 2
        assert (tmp_path / "out.md").exists()
        assert (tmp_path / "out.external.md").exists()

    def test_internal_only_writes_one_file_with_traceability(self, tmp_path):
        req = GenerateRequest(
            srs_paths=[str(FIXTURES / "srs_small.md")],
            sample_path=str(FIXTURES / "sample_release_notes.md"),
            product_name="Demo",
            version="1.2.0",
            release_date=date(2026, 4, 17),
            audience="internal",
            output_format="md",
            output_path=str(tmp_path / "out.md"),
        )
        with (
            patch(
                "release_notes_agent.pipeline.extract_items",
                side_effect=_mock_extract,
            ),
            patch(
                "release_notes_agent.pipeline.write_release_notes",
                side_effect=_mock_write,
            ),
        ):
            result = generate_release_notes(req)
        assert result.external_markdown is None
        assert len(result.output_paths) == 1
        content = (tmp_path / "out.md").read_text(encoding="utf-8")
        assert "Traceability" in content
        assert "BUG-101" in content

    def test_external_only_no_traceability(self, tmp_path):
        req = GenerateRequest(
            srs_paths=[str(FIXTURES / "srs_small.md")],
            sample_path=str(FIXTURES / "sample_release_notes.md"),
            product_name="Demo",
            version="1.2.0",
            release_date=date(2026, 4, 17),
            audience="external",
            output_format="md",
            output_path=str(tmp_path / "out.md"),
        )
        with (
            patch(
                "release_notes_agent.pipeline.extract_items",
                side_effect=_mock_extract,
            ),
            patch(
                "release_notes_agent.pipeline.write_release_notes",
                side_effect=_mock_write,
            ),
        ):
            generate_release_notes(req)
        content = (tmp_path / "out.md").read_text(encoding="utf-8")
        assert "Traceability" not in content
