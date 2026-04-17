"""Reusable Streamlit UI components."""

import streamlit as st

from release_notes_agent.config.settings import settings


def render_sidebar() -> None:
    """Render a minimal sidebar: environment status + actions."""
    with st.sidebar:
        st.title("release-notes-agent")
        st.caption("Strands Agents + AWS Bedrock")

        st.divider()

        st.markdown("**Environment**")
        creds_ok = bool(settings.aws_access_key_id)
        status_icon = "🟢" if creds_ok else "🔴"
        status_text = "credentials present" if creds_ok else "credentials missing"
        st.markdown(f"{status_icon} {status_text}")
        st.markdown(f"**Region:** `{settings.aws_region}`")
        st.markdown(f"**Model:** `{settings.bedrock_model_id}`")

        st.divider()

        session_id = st.session_state.get("session_id")
        if session_id:
            st.caption(f"Session: `{session_id[:8]}…`")

        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pop("session_id", None)
            st.rerun()


def render_message(role: str, content: str) -> None:
    """Render a single chat message."""
    with st.chat_message(role):
        st.markdown(content)
