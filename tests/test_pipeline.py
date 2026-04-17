"""End-to-end pipeline test with sub-agents mocked."""

from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

from release_notes_agent.models.schemas import GenerateRequest, SrsItem
from release_notes_agent.pipeline import _timestamped_path, generate_release_notes

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
        internal_files = list(tmp_path.glob("Generated_ReleaseNotes_*.md"))
        external_files = list(tmp_path.glob("Generated_ReleaseNotes_*.external.md"))
        assert len(internal_files) == 2  # glob matches both internal and external
        assert len(external_files) == 1

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
        written = Path(result.output_paths[0])
        assert written.parent == tmp_path
        assert written.name.startswith("Generated_ReleaseNotes_")
        assert written.suffix == ".md"
        content = written.read_text(encoding="utf-8")
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
            result = generate_release_notes(req)
        written = Path(result.output_paths[0])
        assert written.name.startswith("Generated_ReleaseNotes_")
        content = written.read_text(encoding="utf-8")
        assert "Traceability" not in content


class TestTimestampedPath:
    def test_replaces_stem_and_keeps_dir_and_ext(self):
        now = datetime(2026, 4, 17, 15, 30, 45)
        result = _timestamped_path("/tmp/release/notes.docx", now=now)
        assert result == str(
            Path("/tmp/release/Generated_ReleaseNotes_04172026_153045.docx")
        )

    def test_zero_pads_single_digit_components(self):
        now = datetime(2026, 1, 2, 3, 4, 5)
        result = _timestamped_path("out.md", now=now)
        assert Path(result).name == "Generated_ReleaseNotes_01022026_030405.md"
