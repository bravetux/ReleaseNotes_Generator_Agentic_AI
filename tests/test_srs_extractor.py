"""Tests for the SRS extractor sub-agent wrapper."""

import json
from unittest.mock import MagicMock, patch

import pytest

from release_notes_agent.agents.srs_extractor import (
    SrsExtractionError,
    extract_items,
)


class TestExtractItems:
    def test_parses_valid_json(self):
        payload = [
            {
                "bug_id": "B1",
                "fr_id": None,
                "item_type": "bug",
                "description": "crash",
                "functional_requirement": None,
                "severity": None,
                "source_file": "a.md",
            }
        ]
        mock_agent = MagicMock(return_value=json.dumps(payload))
        with patch(
            "release_notes_agent.agents.srs_extractor.create_extractor_agent",
            return_value=mock_agent,
        ):
            items = extract_items(raw_text="BUG-1 crash", filename="a.md")
        assert len(items) == 1
        assert items[0].bug_id == "B1"

    def test_retries_once_on_bad_json(self):
        mock_agent = MagicMock(
            side_effect=[
                "not json at all",
                json.dumps(
                    [
                        {
                            "bug_id": None,
                            "fr_id": None,
                            "item_type": "feature",
                            "description": "x",
                            "functional_requirement": None,
                            "severity": None,
                            "source_file": "a.md",
                        }
                    ]
                ),
            ]
        )
        with patch(
            "release_notes_agent.agents.srs_extractor.create_extractor_agent",
            return_value=mock_agent,
        ):
            items = extract_items(raw_text="...", filename="a.md")
        assert mock_agent.call_count == 2
        assert len(items) == 1

    def test_raises_after_two_failures(self):
        mock_agent = MagicMock(return_value="still not json")
        with patch(
            "release_notes_agent.agents.srs_extractor.create_extractor_agent",
            return_value=mock_agent,
        ):
            with pytest.raises(SrsExtractionError):
                extract_items(raw_text="...", filename="a.md")
