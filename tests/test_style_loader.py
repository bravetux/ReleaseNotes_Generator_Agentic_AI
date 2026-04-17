"""Tests for sample release-notes style loader."""

from pathlib import Path

from release_notes_agent.tools.style_loader import load_sample_style

FIXTURES = Path(__file__).parent / "fixtures"


class TestLoadSampleStyle:
    def test_headings_extracted(self):
        result = load_sample_style.__wrapped__(
            path=str(FIXTURES / "sample_release_notes.md")
        )
        assert "New Features" in result["headings"]
        assert "Enhancements" in result["headings"]
        assert "Bug Fixes" in result["headings"]

    def test_section_order_preserved(self):
        result = load_sample_style.__wrapped__(
            path=str(FIXTURES / "sample_release_notes.md")
        )
        order = result["section_order"]
        assert order.index("New Features") < order.index("Enhancements")
        assert order.index("Enhancements") < order.index("Bug Fixes")

    def test_bullet_style(self):
        result = load_sample_style.__wrapped__(
            path=str(FIXTURES / "sample_release_notes.md")
        )
        assert result["list_style"] == "bullet"

    def test_numbered_style(self, tmp_path):
        p = tmp_path / "numbered.md"
        p.write_text("# Title\n\n## Section\n\n1. one\n2. two\n3. three\n")
        result = load_sample_style.__wrapped__(path=str(p))
        assert result["list_style"] == "numbered"

    def test_raw_excerpt_truncated(self, tmp_path):
        p = tmp_path / "big.md"
        p.write_text("# T\n\n" + "word " * 1000)
        result = load_sample_style.__wrapped__(path=str(p))
        assert len(result["raw_excerpt"]) <= 2000
