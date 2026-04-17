"""SRS extractor sub-agent — parses raw SRS text into structured SrsItems."""

import json
import logging
import re

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.models import BedrockModel

from release_notes_agent.config.aws_client import get_bedrock_session
from release_notes_agent.config.prompts import SRS_EXTRACTOR_SYSTEM_PROMPT
from release_notes_agent.config.settings import settings
from release_notes_agent.models.schemas import SrsItem

logger = logging.getLogger(__name__)

_JSON_BLOCK_RE = re.compile(r"\[[\s\S]*\]")


class SrsExtractionError(RuntimeError):
    """Raised when the extractor fails to produce valid JSON after retry."""


def create_extractor_agent() -> Agent:
    """Factory for the extractor sub-agent."""
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
        system_prompt=SRS_EXTRACTOR_SYSTEM_PROMPT,
    )


def _parse(response: str, filename: str) -> list[SrsItem]:
    text = str(response).strip()
    match = _JSON_BLOCK_RE.search(text)
    payload = match.group(0) if match else text
    data = json.loads(payload)
    items: list[SrsItem] = []
    for raw in data:
        raw.setdefault("source_file", filename)
        items.append(SrsItem.model_validate(raw))
    return items


def extract_items(raw_text: str, filename: str) -> list[SrsItem]:
    """Run the extractor sub-agent on one SRS file's raw text.

    Retries once on JSON parse failure with the error appended to the prompt.
    """
    agent = create_extractor_agent()
    user_prompt = (
        f"Filename: {filename}\n\nSRS text follows. Extract items as JSON.\n\n"
        f"{raw_text}"
    )
    try:
        response = agent(user_prompt)
        return _parse(response, filename)
    except (json.JSONDecodeError, ValueError) as first_err:
        logger.warning("extractor: first attempt failed (%s); retrying once", first_err)
        retry_prompt = (
            f"{user_prompt}\n\nYour previous output could not be parsed as JSON "
            f"({first_err}). Return a valid JSON array only."
        )
        try:
            response = agent(retry_prompt)
            return _parse(response, filename)
        except (json.JSONDecodeError, ValueError) as second_err:
            raise SrsExtractionError(
                f"extractor failed twice for {filename}: {second_err}"
            ) from second_err
