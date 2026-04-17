"""Orchestrator agent — drives the chat surface with release-notes tools."""

import logging
import pathlib

from strands import Agent
from strands.agent.conversation_manager import SummarizingConversationManager
from strands.hooks import AfterToolCallEvent, BeforeToolCallEvent
from strands.models import BedrockModel
from strands_tools.think import think

from release_notes_agent.config.aws_client import get_bedrock_session
from release_notes_agent.config.prompts import ORCHESTRATOR_SYSTEM_PROMPT
from release_notes_agent.config.settings import settings
from release_notes_agent.tools.exporters import export_release_notes
from release_notes_agent.tools.item_ops import merge_srs_items
from release_notes_agent.tools.srs_loaders import load_srs
from release_notes_agent.tools.style_loader import load_sample_style

logger = logging.getLogger(__name__)

_DEFAULT_SESSION_ID = "orchestrator-default"


def get_session_manager(session_id: str = _DEFAULT_SESSION_ID):
    """Return the appropriate session manager based on SESSION_BACKEND env var."""
    try:
        from strands.session.file_session_manager import FileSessionManager

        pathlib.Path(settings.session_dir).mkdir(parents=True, exist_ok=True)
        return FileSessionManager(
            session_id=session_id, storage_dir=settings.session_dir
        )
    except (ImportError, Exception) as e:
        logger.warning(
            "FileSessionManager not available (%s), using no session manager", e
        )
        return None


def create_orchestrator(session_id: str | None = None) -> Agent:
    """Create the orchestrator agent with session persistence, conversation
    summarisation, and audit hooks.
    """
    effective_session_id = session_id or _DEFAULT_SESSION_ID

    model = BedrockModel(
        boto_session=get_bedrock_session(),
        model_id=settings.bedrock_model_id,
        temperature=settings.agent_temperature,
        top_p=settings.agent_top_p,
        max_tokens=settings.agent_max_tokens,
    )

    conversation_manager = SummarizingConversationManager(
        summary_ratio=0.4,
        summarization_system_prompt=(
            "Summarise the conversation so far. "
            "Preserve: key findings, action outcomes, and important data. "
            "Discard: raw dumps, intermediate reasoning."
        ),
    )

    tools = [
        think,
        load_srs,
        load_sample_style,
        merge_srs_items,
        export_release_notes,
    ]

    agent_kwargs: dict = {
        "model": model,
        "tools": tools,
        "conversation_manager": conversation_manager,
        "system_prompt": ORCHESTRATOR_SYSTEM_PROMPT,
    }

    session_manager = get_session_manager(effective_session_id)
    if session_manager is not None:
        agent_kwargs["session_manager"] = session_manager

    agent = Agent(**agent_kwargs)

    # Audit hooks — log tool calls for observability
    def _before_tool(event: BeforeToolCallEvent) -> None:
        tool_name = (
            event.tool_use.get("name", "unknown")
            if isinstance(event.tool_use, dict)
            else getattr(event.tool_use, "name", "unknown")
        )
        logger.info("TOOL_CALL_START tool=%s", tool_name)

    def _after_tool(event: AfterToolCallEvent) -> None:
        tool_name = (
            event.tool_use.get("name", "unknown")
            if isinstance(event.tool_use, dict)
            else getattr(event.tool_use, "name", "unknown")
        )
        logger.info("TOOL_CALL_END tool=%s", tool_name)

    try:
        agent.add_hook(_before_tool, BeforeToolCallEvent)
        agent.add_hook(_after_tool, AfterToolCallEvent)
    except (AttributeError, TypeError) as e:
        logger.warning("Hooks could not be registered: %s", e)

    return agent
