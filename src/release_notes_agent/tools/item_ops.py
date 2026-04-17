"""Merge and deduplicate SRS items collected from multiple files."""

import logging

from strands import tool

from release_notes_agent.models.schemas import SrsItem

logger = logging.getLogger(__name__)


@tool
def merge_srs_items(items: list[dict]) -> list[dict]:
    """Deduplicate SRS items by ``bug_id`` (last occurrence wins).

    Items with ``bug_id is None`` are never deduped. When a duplicate has a
    different ``description`` than the previous occurrence, a warning is logged.

    Args:
        items: list of SrsItem dicts.

    Returns:
        Deduplicated list of SrsItem dicts in first-seen order (but values from
        the last duplicate).
    """
    parsed = [SrsItem.model_validate(i) for i in items]

    by_id: dict[str, SrsItem] = {}
    order: list[str] = []
    loose: list[SrsItem] = []

    for item in parsed:
        if item.bug_id is None:
            loose.append(item)
            continue
        prior = by_id.get(item.bug_id)
        if prior is None:
            order.append(item.bug_id)
        elif prior.description != item.description:
            logger.warning(
                "duplicate bug_id %s with differing description; last-wins "
                "(%s overrides %s)",
                item.bug_id,
                item.source_file,
                prior.source_file,
            )
        by_id[item.bug_id] = item

    deduped: list[SrsItem] = [by_id[k] for k in order] + loose
    return [i.model_dump() for i in deduped]
