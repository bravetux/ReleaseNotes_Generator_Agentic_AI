"""Reusable Streamlit UI components."""

import streamlit as st

from release_notes_agent.config.settings import settings


def render_sidebar() -> None:
    """Render the sidebar with project info and settings."""
    with st.sidebar:
        st.title("release-notes-agent")
        st.markdown("---")

        st.subheader("Settings")
        st.text_input("Model", value=settings.bedrock_model_id, disabled=True)
        st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=settings.agent_temperature,
            disabled=True,
        )
        st.number_input(
            "Max Tokens",
            value=settings.agent_max_tokens,
            disabled=True,
        )

        st.markdown("---")
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pop("session_id", None)
            st.rerun()


def render_message(role: str, content: str) -> None:
    """Render a single chat message."""
    with st.chat_message(role):
        st.markdown(content)
