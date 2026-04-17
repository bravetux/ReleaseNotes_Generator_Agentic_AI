"""Example specialist sub-agent — demonstrates the sub-agent factory pattern."""

import logging

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.models import BedrockModel
from strands_tools.think import think

from release_notes_agent.config.aws_client import get_bedrock_session
from release_notes_agent.config.prompts import EXAMPLE_AGENT_SYSTEM_PROMPT
from release_notes_agent.config.settings import settings
from release_notes_agent.tools.example_tools import add_numbers, greet

logger = logging.getLogger(__name__)


def create_example_agent() -> Agent:
    """Create a specialist sub-agent with its own tools and conversation window.

    Sub-agents use SlidingWindowConversationManager (not summarising) because
    they handle short-lived, focused tasks delegated by the orchestrator.
    """
    model = BedrockModel(
        boto_session=get_bedrock_session(),
        model_id=settings.bedrock_model_id,
        temperature=settings.agent_temperature,
        top_p=settings.agent_top_p,
        max_tokens=settings.agent_max_tokens,
    )

    return Agent(
        model=model,
        tools=[think, greet, add_numbers],
        conversation_manager=SlidingWindowConversationManager(window_size=10),
        system_prompt=EXAMPLE_AGENT_SYSTEM_PROMPT,
    )
