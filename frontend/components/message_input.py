"""
Message input component.

Handles the user input field and submission logic.
"""
import logging
import streamlit as st

LOG = logging.getLogger(__name__)


def on_message_submit():
    """
    Handles the submission of a new user message.

    Adds the message to chat history and queues it for processing.
    """
    user_input = st.session_state.user_message
    if user_input and user_input.strip():
        st.session_state.user_message = ''
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        st.session_state.message_to_process = user_input

        LOG.debug('User message submitted: %s...', user_input[:30])

def render_message_input():
    """
    Renders the message input component in the Streamlit interface.

    Includes text input field and send button.
    """
    with st.container():
        st.text_input(
            'Type your message here:',
            key='user_message',
            on_change=on_message_submit
        )
        send_col, _ = st.columns([1, 5])
        with send_col:
            if st.button('Send'):
                on_message_submit()
