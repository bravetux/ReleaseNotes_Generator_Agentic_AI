"""Release writer sub-agent — produces markdown release notes."""

import json
import logging
from typing import Literal

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.models import BedrockModel

from release_notes_agent.config.aws_client import get_bedrock_session
from release_notes_agent.config.prompts import (
    RELEASE_WRITER_EXTERNAL_SYSTEM_PROMPT,
    RELEASE_WRITER_INTERNAL_SYSTEM_PROMPT,
)
from release_notes_agent.config.settings import settings
from release_notes_agent.models.schemas import ReleaseMetadata, SampleStyle, SrsItem

logger = logging.getLogger(__name__)

_PROMPTS = {
    "internal": RELEASE_WRITER_INTERNAL_SYSTEM_PROMPT,
    "external": RELEASE_WRITER_EXTERNAL_SYSTEM_PROMPT,
}


def create_writer_agent(audience: Literal["internal", "external"]) -> Agent:
    """Factory — audience selects the system prompt."""
    model = BedrockModel(
        boto_session=get_bedrock_session(),
        model_id=settings.bedrock_model_id,
        temperature=settings.agent_temperature,
        top_p=settings.agent_top_p,
        max_tokens=settings.agent_max_tokens,
    )
    return Agent(
        model=model,
        tools=[],
        conversation_manager=SlidingWindowConversationManager(window_size=4),
        system_prompt=_PROMPTS[audience],
    )


def write_release_notes(
    items: list[SrsItem],
    style: SampleStyle,
    metadata: ReleaseMetadata,
    audience: Literal["internal", "external"],
) -> str:
    """Produce a markdown release notes string for the given audience."""
    agent = create_writer_agent(audience)
    payload = {
        "items": [i.model_dump(mode="json") for i in items],
        "style": style.model_dump(mode="json"),
        "metadata": metadata.model_dump(mode="json"),
    }
    prompt = (
        "Write release notes in Markdown based on the following JSON payload.\n\n"
        f"{json.dumps(payload, indent=2)}"
    )
    return str(agent(prompt)).strip()
