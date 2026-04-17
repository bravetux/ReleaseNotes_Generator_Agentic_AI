"""Tests for typer CLI."""

from datetime import date
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from release_notes_agent.cli.app import app
from release_notes_agent.models.schemas import GenerationResult, ReleaseMetadata

FIXTURES = Path(__file__).parent / "fixtures"
runner = CliRunner()


def _fake_result(paths, audience="internal"):
    meta = ReleaseMetadata(
        product_name="Demo",
        version="1.2.0",
        release_date=date(2026, 4, 17),
        audience=audience,
    )
    return GenerationResult(metadata=meta, output_paths=paths)


class TestCliGenerate:
    def test_basic_invocation(self, tmp_path):
        out = tmp_path / "out.md"
        with patch(
            "release_notes_agent.cli.app.generate_release_notes",
            return_value=_fake_result([str(out)]),
        ) as mock:
            result = runner.invoke(
                app,
                [
                    "generate",
                    "--srs",
                    str(FIXTURES / "srs_small.md"),
                    "--sample",
                    str(FIXTURES / "sample_release_notes.md"),
                    "--product",
                    "Demo",
                    "--version",
                    "1.2.0",
                    "--date",
                    "2026-04-17",
                    "--audience",
                    "internal",
                    "--format",
                    "md",
                    "--out",
                    str(out),
                ],
            )
        assert result.exit_code == 0, result.output
        mock.assert_called_once()
        req = mock.call_args.args[0]
        assert req.srs_paths == [str(FIXTURES / "srs_small.md")]
        assert req.audience == "internal"
        assert req.output_format == "md"

    def test_multiple_srs(self, tmp_path):
        out = tmp_path / "out.md"
        with patch(
            "release_notes_agent.cli.app.generate_release_notes",
            return_value=_fake_result([str(out)]),
        ) as mock:
            runner.invoke(
                app,
                [
                    "generate",
                    "--srs",
                    str(FIXTURES / "srs_small.md"),
                    "--srs",
                    str(FIXTURES / "srs_small.txt"),
                    "--sample",
                    str(FIXTURES / "sample_release_notes.md"),
                    "--product",
                    "Demo",
                    "--version",
                    "1.2.0",
                    "--date",
                    "2026-04-17",
                    "--audience",
                    "external",
                    "--format",
                    "md",
                    "--out",
                    str(out),
                ],
            )
        req = mock.call_args.args[0]
        assert len(req.srs_paths) == 2
