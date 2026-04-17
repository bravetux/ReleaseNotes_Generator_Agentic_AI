"""Tests for item_ops (merge/dedup)."""

import logging

from release_notes_agent.models.schemas import SrsItem
from release_notes_agent.tools.item_ops import merge_srs_items


def _item(bug_id=None, fr_id=None, desc="x", src="a.md", kind="bug"):
    return SrsItem(
        bug_id=bug_id,
        fr_id=fr_id,
        item_type=kind,
        description=desc,
        source_file=src,
    )


class TestMergeSrsItems:
    def test_keeps_unique(self):
        items = [_item(bug_id="B1"), _item(bug_id="B2")]
        result = merge_srs_items.__wrapped__(items=[i.model_dump() for i in items])
        assert len(result) == 2

    def test_dedups_same_bug_id_last_wins(self):
        items = [
            _item(bug_id="B1", desc="first", src="a.md"),
            _item(bug_id="B1", desc="second", src="b.md"),
        ]
        result = merge_srs_items.__wrapped__(items=[i.model_dump() for i in items])
        assert len(result) == 1
        assert result[0]["description"] == "second"
        assert result[0]["source_file"] == "b.md"

    def test_logs_warning_on_conflict(self, caplog):
        items = [
            _item(bug_id="B1", desc="first"),
            _item(bug_id="B1", desc="second"),
        ]
        with caplog.at_level(logging.WARNING):
            merge_srs_items.__wrapped__(items=[i.model_dump() for i in items])
        assert any("B1" in r.message for r in caplog.records)

    def test_none_bug_id_never_deduped(self):
        items = [_item(desc="a"), _item(desc="b")]
        result = merge_srs_items.__wrapped__(items=[i.model_dump() for i in items])
        assert len(result) == 2
