"""Streamlit interface for release-notes-agent."""

import uuid

import streamlit as st

from release_notes_agent.agents.orchestrator import create_orchestrator
from release_notes_agent.ui.components import render_message, render_sidebar
from release_notes_agent.ui.generate_form import render_generate_form

st.set_page_config(
    page_title="release-notes-agent",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

_EXAMPLE_PROMPTS = [
    "Load SRS files from docs/samples/srs/ and tell me how many bugs you found.",
    "Using docs/samples/ReleaseNotev1.txt as the sample style, generate "
    "external release notes for Demo v1.2.0 dated 2026-04-17.",
    "Merge the items from the last load and export the result as DOCX "
    "to .releases/demo.docx.",
]


def _run_agent_turn(prompt: str) -> None:
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_message("user", prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            agent = create_orchestrator(session_id=st.session_state.session_id)
            response = agent(prompt)
            response_text = str(response)
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})


def _render_chat() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if not st.session_state.messages:
        st.markdown("### 💬 Chat with the release-notes agent")
        st.caption(
            "Ask the agent to load SRS files, merge items, and export release notes."
        )
        st.markdown("**Try one of these:**")
        cols = st.columns(len(_EXAMPLE_PROMPTS))
        for col, example in zip(cols, _EXAMPLE_PROMPTS):
            with col:
                if st.button(
                    example, use_container_width=True, key=f"ex-{hash(example)}"
                ):
                    _run_agent_turn(example)
                    st.rerun()
    else:
        for msg in st.session_state.messages:
            render_message(msg["role"], msg["content"])

    if prompt := st.chat_input("Ask the agent…"):
        _run_agent_turn(prompt)


def main() -> None:
    render_sidebar()
    st.title("📝 release-notes-agent")
    st.caption("Turn SRS documents into polished release notes.")
    tab_gen, tab_chat = st.tabs(["🛠 Generate", "💬 Chat"])
    with tab_gen:
        render_generate_form()
    with tab_chat:
        _render_chat()


if __name__ == "__main__":
    main()
