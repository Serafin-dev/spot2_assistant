"""
Session state management.

Handles initialization and management of the Streamlit session state.
"""
import logging
import os
import sys

# Configure path before any imports that depend on it
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st

from app.main import assistant

LOG = logging.getLogger(__name__)


def initialize_session():
    """
    Initializes the Streamlit session state with required variables.

    Sets up user ID, session ID, chat history, and initializes the assistant session.
    """
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 'streamlit_user'
    if 'session_id' not in st.session_state:
        st.session_state.session_id = 'streamlit_session'
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'session_initialized' not in st.session_state:
        st.session_state.session_initialized = False
    if 'message_to_process' not in st.session_state:
        st.session_state.message_to_process = None

    if not st.session_state.session_initialized:
        try:
            LOG.debug('Initializing assistant session')
            assistant.create_session(
                user_id=st.session_state.user_id,
                session_id=st.session_state.session_id
            )
            st.session_state.session_initialized = True
            LOG.info('Assistant session initialized successfully')
        except (ConnectionError, ValueError, RuntimeError) as e:
            LOG.error('Error initializing session: %s', e)
            st.error(f'Error initializing session: {e}')
