"""Tests for the release writer sub-agent wrapper."""

from datetime import date
from unittest.mock import MagicMock, patch

from release_notes_agent.agents.release_writer import write_release_notes
from release_notes_agent.models.schemas import ReleaseMetadata, SampleStyle, SrsItem

ITEM = SrsItem(
    bug_id="B1",
    fr_id="FR-1",
    item_type="bug",
    description="crash",
    functional_requirement=None,
    severity=None,
    source_file="a.md",
)
STYLE = SampleStyle(
    headings=["New Features", "Bug Fixes"],
    section_order=["New Features", "Bug Fixes"],
    list_style="bullet",
    raw_excerpt="# Sample",
)
META = ReleaseMetadata(
    product_name="Demo",
    version="1.0.0",
    release_date=date(2026, 4, 17),
    audience="both",
)


class TestWriteReleaseNotes:
    def test_internal_returns_markdown(self):
        mock_agent = MagicMock(return_value="## Bug Fixes\n\n- Fixed B1 crash.\n")
        with patch(
            "release_notes_agent.agents.release_writer.create_writer_agent",
            return_value=mock_agent,
        ):
            md = write_release_notes(
                items=[ITEM],
                style=STYLE,
                metadata=META,
                audience="internal",
            )
        assert "Bug Fixes" in md
        mock_agent.assert_called_once()

    def test_external_includes_ids_in_prompt(self):
        captured = {}

        def fake_agent(prompt):
            captured["prompt"] = prompt
            return "- Fixed a crash."

        with patch(
            "release_notes_agent.agents.release_writer.create_writer_agent",
            return_value=fake_agent,
        ):
            write_release_notes(
                items=[ITEM],
                style=STYLE,
                metadata=META,
                audience="external",
            )
        # User prompt still contains IDs — it's the system prompt that tells
        # the model to strip them.
        assert "B1" in captured["prompt"]
