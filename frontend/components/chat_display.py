"""
Chat history display component.

Handles the display of the conversation history between user and assistant.
"""
import logging
import streamlit as st

LOG = logging.getLogger(__name__)


def render_chat_history():
    """
    Renders the chat history in the Streamlit interface.

    Displays all messages from the session state's chat history.
    """
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Assistant:** {message['content']}")
