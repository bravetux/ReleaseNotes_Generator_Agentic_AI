"""Streamlit chat interface for release-notes-agent."""

import uuid

import streamlit as st

from release_notes_agent.agents.orchestrator import create_orchestrator
from release_notes_agent.ui.components import render_message, render_sidebar

st.set_page_config(
    page_title="release-notes-agent",
    page_icon="🤖",
    layout="wide",
)


def main() -> None:
    st.title("release-notes-agent")
    st.caption("Powered by Strands Agents + AWS Bedrock")

    render_sidebar()

    # Initialise session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # Display chat history
    for msg in st.session_state.messages:
        render_message(msg["role"], msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        render_message("user", prompt)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                agent = create_orchestrator(session_id=st.session_state.session_id)
                response = agent(prompt)
                response_text = str(response)

            st.markdown(response_text)

        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )


if __name__ == "__main__":
    main()
