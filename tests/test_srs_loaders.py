"""Tests for SRS loader tool."""

from pathlib import Path

import pytest

from release_notes_agent.tools.srs_loaders import load_srs

FIXTURES = Path(__file__).parent / "fixtures"


class TestLoadSrs:
    def test_load_single_md(self):
        result = load_srs.__wrapped__(paths=str(FIXTURES / "srs_small.md"))
        assert len(result) == 1
        assert result[0]["format"] == "md"
        assert "BUG-101" in result[0]["raw_text"]
        assert result[0]["filename"] == "srs_small.md"

    def test_load_single_txt(self):
        result = load_srs.__wrapped__(paths=str(FIXTURES / "srs_small.txt"))
        assert result[0]["format"] == "txt"
        assert "BUG-201" in result[0]["raw_text"]

    def test_load_docx(self):
        docx_path = FIXTURES / "srs_small.docx"
        if not docx_path.exists():
            pytest.skip("docx fixture missing; run make_fixtures.py")
        result = load_srs.__wrapped__(paths=str(docx_path))
        assert result[0]["format"] == "docx"
        assert "BUG-101" in result[0]["raw_text"]

    def test_load_pdf(self):
        pdf_path = FIXTURES / "srs_small.pdf"
        if not pdf_path.exists():
            pytest.skip("pdf fixture missing; run make_fixtures.py")
        result = load_srs.__wrapped__(paths=str(pdf_path))
        assert result[0]["format"] == "pdf"
        assert "BUG-101" in result[0]["raw_text"]

    def test_load_list(self):
        paths = [
            str(FIXTURES / "srs_small.md"),
            str(FIXTURES / "srs_small.txt"),
        ]
        result = load_srs.__wrapped__(paths=paths)
        assert len(result) == 2
        names = {r["filename"] for r in result}
        assert names == {"srs_small.md", "srs_small.txt"}

    def test_load_folder(self, tmp_path):
        (tmp_path / "a.md").write_text("# A")
        (tmp_path / "b.txt").write_text("B body")
        (tmp_path / "ignore.xyz").write_text("skip me")
        result = load_srs.__wrapped__(paths=str(tmp_path))
        assert len(result) == 2
        assert {r["filename"] for r in result} == {"a.md", "b.txt"}

    def test_unreadable_file_yields_error_entry(self, tmp_path):
        bad = tmp_path / "bad.pdf"
        bad.write_bytes(b"not a pdf")
        result = load_srs.__wrapped__(paths=str(bad))
        assert len(result) == 1
        assert "error" in result[0]

    def test_truncates_huge_file(self, tmp_path, monkeypatch):
        big = tmp_path / "big.txt"
        big.write_text("x" * 10_000)
        monkeypatch.setattr("release_notes_agent.tools.srs_loaders.MAX_CHARS", 100)
        result = load_srs.__wrapped__(paths=str(big))
        assert len(result[0]["raw_text"]) == 100
        assert result[0].get("truncated") is True
